#!/usr/bin/env python3
import os.path as path
from os import listdir
import os
import subprocess
import logging as log
import difflib
import sys
import argparse
import re
import yaml

# NOTE change these as needed
TestBenchLoc = os.path.dirname(os.path.abspath(__file__))
KAITAI_BASE_PATH = TestBenchLoc + "/../kaitai_struct_formats/"
BT_TEMPLATE_BASE_PATH = TestBenchLoc + "/../../templates/"
FFCOMPILE = TestBenchLoc + "/../../ffcompile"
FF_ROOT = TestBenchLoc + "/../../"
CONVERTER = TestBenchLoc + "/Converter.py"
TEST_FOLDER = TestBenchLoc + "/../test/"
TEST_FILE_ROOT = TestBenchLoc + "/../test-files"


def find_alt_format_names(fmt):
    kaitiai_file = find_file_recursively(KAITAI_BASE_PATH, fmt, "ksy")
    with open(kaitiai_file, 'r') as kt_file:
        input_stream = kt_file.read()
    kt_structure = yaml.safe_load(input_stream)
    if "file-extension" in kt_structure["meta"].keys():
        alt_file_ext = kt_structure["meta"]["file-extension"]
    else:
        alt_file_ext = [fmt]
    return alt_file_ext


def set_up_logger(level, reset=False):
    if not reset:
        console_log = log.StreamHandler()
        logfile = log.FileHandler("testbench.log", mode='w')
        logfile.setLevel(level)
        log.basicConfig(format='%(asctime)s::%(levelname)s:%(message)s',
                        level=level,
                        handlers=[console_log, logfile],
                        datefmt="%Y-%m-%d %H:%M:%S")
    else:
        console_log = log.StreamHandler()
        logfile = log.FileHandler("testbench.log", mode='w')
        log.handlers = [console_log, logfile]


def create_fmt_folder(format_name):
    if not os.path.exists(TEST_FOLDER + format_name):
        os.makedirs(TEST_FOLDER + format_name)
        os.makedirs(TEST_FOLDER + format_name + "/build")
        os.makedirs(TEST_FOLDER + format_name + "/output")
        os.makedirs(TEST_FOLDER + format_name + "/input")
    return TEST_FOLDER + format_name


class TestRunException(Exception):
    """thrown if any part of a test run fails"""

    def __init__(self, msg, cause: Exception = None):
        self.msg = msg
        self.cause = cause

    def print(self):
        log.error(self.msg)
        if isinstance(self.cause, subprocess.CalledProcessError):
            log.error(self.cause.cmd)
            log.error(self.cause.returncode)
            log.error(f"Stderr: {self.cause.stderr.decode()}")
            linefinder = r"(Compile|Parse)Error.*:(\d+):(\d+):"
            lines = re.finditer(linefinder, self.cause.stderr.decode())
            for _, ma in enumerate(lines, 1):
                _, ln, cl = ma.groups()
                log.error("Error occurred on line: %s, column: %s", ln, cl)
            log.error(f"Stdout: {self.cause.output.decode()}")
        elif self.cause is not None:
            log.error(self.cause)
            log.error(self.cause.args)


def try_file_extensions(base_path, names, ext, max_depth=3):
    log.info(f'Names {names}')
    if type(names) is not list:
        names = [names]
    for name in names:
        temp_path = find_file_recursively(base_path, name, ext, max_depth)
        if temp_path:
            return temp_path, name
    return False, None


# should return file path or false in not found
def find_file_recursively(base_path, name, ext, max_depth=3):
    cmd = [
        'find',
        path.normpath(base_path), '-maxdepth', f'{max_depth}', '-name',
        f'{name}.{ext}'
    ]
    found_file = subprocess.run(cmd, stdout=subprocess.PIPE)
    if found_file.returncode != 0:
        log.error(f"Error ret: {found_file.stderr}")
        return False
    if len(found_file.stdout) == 0:
        log.error(f"Error: {found_file.stderr}")
        return False

    log.debug(f"Debug: find output {found_file.stdout.decode()}")
    split_out = found_file.stdout.decode().split("\n")
    if len(split_out) > 2:
        # some default behavior, maybe make this a user ask
        log.warning(f"multiple results found. using the first one.")
    return split_out[0]


def run_single_format_parse_test(format_name, resolve_test_input):
    base_path = create_fmt_folder(format_name)
    logfile = f'{base_path}/output/test-{format_name}-fuzzer.log-output'
    log.handlers = [
        log.StreamHandler(),
        log.FileHandler(logfile, mode='w')
    ]
    try:
        extensions = find_alt_format_names(format_name)
        # contains path to converted file
        converted_file = call_converter(extensions, base_path)
        parser_under_test = compile_parser(converted_file,
                                           test=True,
                                           base_path=base_path)
        # contains path to reference template
        (referenceTemplate,
         format_name) = try_file_extensions(BT_TEMPLATE_BASE_PATH, extensions, "bt")
        if not referenceTemplate:
            raise TestRunException("Reference template file not found")
        reference_parser = compile_parser(referenceTemplate, base_path=base_path)
        test_inputs = resolve_test_input(format_name, reference_parser, base_path)
        diff = ""
        for ti in test_inputs:
            log.info(f"running test on input {path.basename(ti)}")
            reference_pt = run_parser_on_input(reference_parser, ti, base_path)
            pt_under_test = run_parser_on_input(parser_under_test, ti, base_path)
            if (isinstance(reference_pt, int) and isinstance(pt_under_test, int)
                    and reference_pt == pt_under_test):
                return True
            elif (isinstance(reference_pt, int)
                  or isinstance(pt_under_test, int)):
                return False
            log.info(f"diff of parse trees for {path.basename(ti)}")
            diff = + diff_parse_trees(reference_pt, pt_under_test)
        set_up_logger(None, True)
        return diff
    except TestRunException as e:
        e.print()
        set_up_logger(None, True)
        return False


def call_converter(format_names, base_path):
    # resolve kaitai struct path and feed to our converter
    if not path.isdir(KAITAI_BASE_PATH):
        raise Exception("kaitai base path is no directory")

    (filePath, formatName) = try_file_extensions(KAITAI_BASE_PATH, format_names, "ksy")
    if not filePath:
        raise TestRunException(
            f"Kaitai struct file not found, path: {path.join(KAITAI_BASE_PATH, formatName)}.ksy"
        )
    working_dir = base_path + "/build"

    log.info(f"found file to convert: {filePath}. converting...")
    try:
        convert = subprocess.run(
            ["python3", CONVERTER, filePath, f"{working_dir}/{formatName}.bt"],
            check=True,
            capture_output=True)
        log.info(convert.stdout.decode())
    except Exception as err:
        raise TestRunException("Conversion Failed", err)
    if convert.returncode != 0:
        raise TestRunException(f"Error: {convert.stderr}")
    log.info(
        f"Converted file successfully. Result saved in Converter/test/{formatName}/build/{formatName}.bt"
    )
    return f"{working_dir}/{formatName}.bt"


def run_multi_format_parse_test(formats, test_input_resolver):
    passed = []
    for fmt in formats:
        log.info("Current format: %s", fmt)
        passed.append((fmt, run_single_format_parse_test(fmt, test_input_resolver)))

    log.info("Passed status of formats: \n")
    for (fmt, status) in passed:
        log.info(f"Format: {fmt}, Status: {'Passed' if status else 'Failed'}")


def diff_parse_trees(expected, actual):
    # if expected == actual:
    #    return True
    diff = "\n".join(
        difflib.context_diff(expected.split("\n"),
                             actual.split("\n"),
                             fromfile="expected-parse-tree",
                             tofile="actual-parse-tree",
                             n=4))
    log.debug(diff)
    return True


def compile_parser(template_path, base_path, test=False):
    try:
        # ./ffcompile templates/gif.bt gif.cpp
        # g++ -c -I . -std=c++17 -g -O3 -Wall fuzzer.cpp
        # g++ -c -I . -std=c++17 -g -O3 -Wall gif.cpp
        # g++ -O3 gif.o fuzzer.o -o gif-fuzzer -lz
        if test:
            log.info("Compiling parser under test")
            flavor = "test_"
        else:
            log.info("Compiling reference parser")
            flavor = "reference_"
        log.info("Compiling template...")
        fmt_name = path.basename(template_path).split('.')[0]
        ff_comp_cmd = [
            FFCOMPILE, template_path, f"{base_path}/build/{flavor}{fmt_name}.cpp"
        ]
        subprocess.run(ff_comp_cmd, capture_output=True, check=True)
        log.info("Compiled template")
        log.info("Compiling general fuzzer api...")
        fuzzer_cpp_cmd = [
            'g++', '-c', '-I',
            path.normpath(FF_ROOT) + "/", '-std=c++17', '-g', '-O3', '-Wall',
            path.normpath(f'{FF_ROOT}fuzzer.cpp'), '-o',
            f'{base_path}/build/fuzzer.o'
        ]
        subprocess.run(fuzzer_cpp_cmd, capture_output=True, check=True)
        log.info("Compiled general fuzzer api")
        log.info("Compiling format code...")
        comp_fuzzer_cmd = [
            'g++', '-c', '-I',
            path.normpath(FF_ROOT), '-std=c++17', '-g', '-O3', '-Wall',
            f'{base_path}/build/{flavor}{fmt_name}.cpp', '-o',
            f'{base_path}/build/{flavor}{fmt_name}.o'
        ]
        subprocess.run(comp_fuzzer_cmd, capture_output=True, check=True)
        log.info("Compiled format code")
        log.info("Compiling fuzzer binary...")
        bin_name = f'test-{fmt_name}-fuzzer' if test else f'{fmt_name}-fuzzer'
        link_cmd = [
            'g++', '-O3', f'{base_path}/build/{flavor}{fmt_name}.o',
            f'{base_path}/build/fuzzer.o', '-o', f'{base_path}/build/{bin_name}',
            '-lz'
        ]
        subprocess.run(link_cmd, capture_output=True, check=True)
        log.info("Compiled fuzzer binary")
        return bin_name
    except Exception as err:
        raise TestRunException(f"failed to compile", err)


def run_parser_on_input(parser, test_input, base_path):
    try:
        cmd = [f"{base_path}/build/{parser}", "parse", test_input]
        parse_tree = subprocess.run(cmd, capture_output=True)

        if parse_tree.returncode != 0:
            with open(
                    f"{base_path}/output/{parser}-{path.basename(test_input)}.output",
                    "w") as file:
                file.write(parse_tree.stdout.decode())
            log.error(parse_tree.stderr)
            return parse_tree.returncode
        if len(parse_tree.stdout) == 0:
            raise TestRunException(f"Error : {parse_tree.stderr}")
        with open(
                f"{base_path}/output/{parser}-{path.basename(test_input)}.output",
                "w") as file:
            file.write(parse_tree.stdout.decode())

        return parse_tree.stdout.decode()
    except Exception as err:
        raise TestRunException(f"failed to run parser", err)


def provide_wild_files(format_name, generator, base_path, multiple=True):
    format_path = path.join(TEST_FILE_ROOT, format_name)
    files = [
        path.join(format_path, f) for f in listdir(format_path)
        if path.isfile(path.join(format_path, ))
    ]
    if multiple:
        return files
    else:
        return files[1:1]


def resolve_test_input_by_format(format_name, generator, base_path, multiple=False):
    file_path = f"{base_path}/input/test-input.{format_name}"
    try:
        cmd = [
            f'{base_path}/build/{generator}', "fuzz",
            file_path
        ]
        subprocess.run(cmd,
                       check=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE,
                       env={"DONT_BE_EVIL": "1"})
        return [file_path]
    except Exception as err:
        raise TestRunException("Creating input failed!", err)


def main():
    parser = argparse.ArgumentParser(
        description="Run tests on converted templates")
    parser.add_argument('formats',
                        metavar='fmt',
                        type=str,
                        nargs='+',
                        help='The formats to run tests on')
    parser.add_argument('--test-input',
                        metavar='testIn',
                        dest='testInput',
                        nargs='?',
                        type=str)
    parser.add_argument('--log',
                        metavar='loglevel',
                        dest='log_lvl',
                        default='INFO',
                        nargs='?',
                        type=str)
    parser.add_argument('--use-test-files',
                        dest='resolver',
                        action='store',
                        nargs='?',
                        const=provide_wild_files,
                        default=resolve_test_input_by_format,
                        help="use real world files")
    parsed_args = parser.parse_args(sys.argv[1::])
    numeric_level = getattr(log, parsed_args.log_lvl.upper(), log.INFO)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % numeric_level)
    set_up_logger(numeric_level)
    log.info("===Starting test bench run===")
    if len(parsed_args.formats) == 1:
        log.info("Running test for single format %s", parsed_args.formats[0])
        run_single_format_parse_test(
            parsed_args.formats[0],
            lambda fmt, bt_parser, base_path: parsed_args.testInput if parsed_args.testInput else parsed_args.resolver(
                fmt, bt_parser, create_fmt_folder(fmt))
        )
    else:
        log.info("Running test for multiple formats")
        run_multi_format_parse_test(parsed_args.formats, parsed_args.resolver)


if __name__ == "__main__":
    main()
