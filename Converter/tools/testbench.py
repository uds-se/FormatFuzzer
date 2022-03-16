#!/usr/bin/env python3
import os.path as path
from os import listdir
import os
import subprocess as sub
import logging as log
import difflib
import sys
import argparse as parse
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


class TestRunException(Exception):
    """thrown if any part of a test run fails"""

    def __init__(self, logger, msg, cause: Exception = None):
        self.msg = msg
        self.cause = cause
        self.logger = logger

    def print(self):
        self.logger.error(self.msg)
        if isinstance(self.cause, sub.CalledProcessError):
            self.logger.error(self.cause.cmd)
            self.logger.error(self.cause.returncode)
            self.logger.error(f"Stderr: {self.cause.stderr.decode()}")
            linefinder = r"(Compile|Parse)Error.*:(\d+):(\d+):"
            lines = re.finditer(linefinder, self.cause.stderr.decode())
            for _, ma in enumerate(lines, 1):
                _, ln, cl = ma.groups()
                self.logger.error("Error occurred on line: %s, column: %s", ln, cl)
            self.logger.error(f"Stdout: {self.cause.output.decode()}")
        elif self.cause is not None:
            self.logger.error(self.cause)
            self.logger.error(self.cause.args)


def set_up_logger(level):
    console_log = log.StreamHandler()
    logfile = log.FileHandler("testbench.log", mode='w')
    logfile.setLevel(level)
    console_log.setLevel(level)
    log.basicConfig(format='%(asctime)s::%(levelname)s:%(message)s',
                    level=level,
                    handlers=[console_log, logfile],
                    datefmt="%Y-%m-%d %H:%M:%S")
    return log.getLogger()


def reset_logger(logger: log.Logger, file_path="testbench.log", mode="w", console_stream=sys.stderr):
    formatter = logger.handlers[0].formatter
    level = logger.handlers[0].level
    [logger.removeHandler(h) for h in logger.handlers[:]]
    console_log = log.StreamHandler(console_stream)
    console_log.setFormatter(formatter)
    console_log.setLevel(level)
    log_file = log.FileHandler(file_path, mode=mode)
    log_file.setFormatter(formatter)
    log_file.setLevel(level)
    logger.addHandler(console_log)
    logger.addHandler(log_file)


def create_fmt_folder(format_name):
    if not os.path.exists(TEST_FOLDER + format_name):
        os.makedirs(TEST_FOLDER + format_name)
        os.makedirs(TEST_FOLDER + format_name + "/build")
        os.makedirs(TEST_FOLDER + format_name + "/output")
        os.makedirs(TEST_FOLDER + format_name + "/input")
    return TEST_FOLDER + format_name


def has_wanted_ext(file: str, ext: str) -> bool:
    with open(file, 'r') as kt_file:
        input_stream = kt_file.read()
    kt_structure = yaml.full_load(input_stream)
    if "file-extension" in kt_structure["meta"].keys():
        alt_file_ext = kt_structure["meta"]["file-extension"]
    else:
        return False
    return ext in alt_file_ext


def has_no_ext_header(file: str) -> bool:
    with open(file, 'r') as kt_file:
        input_stream = kt_file.read()
    kt_structure = yaml.full_load(input_stream)
    return "file-extension" not in kt_structure["meta"].keys() or len(kt_structure["meta"]["file-extension"]) == 0


# should return file path or false in not found
# 1. name match + header nonext / empty -> MATCH
# 2. name match + ext in header -> MATCH
# 3. name match + header exists but ext not int header -> NO MATCH
# 4. no name mach + ext in header -> MATCH
# 5. no match at all -> NO MATCH
def find_templates(base_path, name, template_ext):
    matching = []
    for (root, dirs, files) in os.walk(base_path):
        for file in filter(lambda fn: fn.endswith(template_ext), files):
            if template_ext == "ksy":
                file_path = path.join(root, file)
                if file == f"{name}.{template_ext}":
                    return [(file_path, file.rsplit(".", 0)[0])]
                name_match = name in file
                has_no_header = has_no_ext_header(file_path)
                ext_in_header = has_wanted_ext(file_path, name)
                if (name_match and ext_in_header) or (name_match and has_no_header) or (
                        not name_match and ext_in_header):
                    matching.append((file_path, file.rsplit(".", 0)[0]))
            else:
                if name in file and 'orig' not in file:
                    matching.append((path.join(root, f"{name}.{template_ext}"), name))
    return matching


def call_converter(template, name, base_path, logger):
    # resolve kaitai struct path and feed to our converter
    name = name if "." not in name else name.split(".")[0]
    if not template:
        raise TestRunException(
            logger, f"Kaitai struct file not found, path: {path.join(KAITAI_BASE_PATH, template)}.ksy"
        )
    working_dir = base_path + "/build"

    logger.info(f"found file to convert: {template}. converting...")
    try:
        convert = sub.run(
            ["python3", CONVERTER, template, f"{working_dir}/{name}.bt"],
            check=True,
            capture_output=True)
        logger.info(convert.stdout.decode())
    except Exception as err:
        raise TestRunException(logger, "Conversion Failed", err)
    if convert.returncode != 0:
        raise TestRunException(logger, f"Error: {convert.stderr}")
    logger.info(f"Converted file successfully. Result saved in {working_dir}/{name}.bt")
    return f"{working_dir}/{name}.bt"


def compile_parser(template_path, base_path, logger, test=False):
    try:
        # ./ffcompile templates/gif.bt gif.cpp
        # g++ -c -I . -std=c++17 -g -O3 -Wall fuzzer.cpp
        # g++ -c -I . -std=c++17 -g -O3 -Wall gif.cpp
        # g++ -O3 gif.o fuzzer.o -o gif-fuzzer -lz
        if test:
            logger.info("Compiling parser under test")
            flavor = "test_"
        else:
            logger.info("Compiling reference parser")
            flavor = "reference_"
        logger.info("Compiling template...")
        fmt_name = path.basename(template_path).split('.')[0]
        ff_comp_cmd = [
            FFCOMPILE, template_path, f"{base_path}/build/{flavor}{fmt_name}.cpp"
        ]
        sub.run(ff_comp_cmd, capture_output=True, check=True)
        logger.info("Compiled template")
        logger.info("Compiling general fuzzer api...")
        fuzzer_cpp_cmd = [
            'g++', '-c', '-I',
            path.normpath(FF_ROOT) + "/", '-std=c++17', '-g', '-O3', '-Wall',
            path.normpath(f'{FF_ROOT}fuzzer.cpp'), '-o',
            f'{base_path}/build/fuzzer.o'
        ]
        sub.run(fuzzer_cpp_cmd, capture_output=True, check=True)
        logger.info("Compiled general fuzzer api")
        logger.info("Compiling format code...")
        comp_fuzzer_cmd = [
            'g++', '-c', '-I',
            path.normpath(FF_ROOT), '-std=c++17', '-g', '-O3', '-Wall',
            f'{base_path}/build/{flavor}{fmt_name}.cpp', '-o',
            f'{base_path}/build/{flavor}{fmt_name}.o'
        ]
        sub.run(comp_fuzzer_cmd, capture_output=True, check=True)
        logger.info("Compiled format code")
        logger.info("Compiling fuzzer binary...")
        bin_name = f'test-{fmt_name}-fuzzer' if test else f'{fmt_name}-fuzzer'
        link_cmd = [
            'g++', '-O3', f'{base_path}/build/{flavor}{fmt_name}.o',
            f'{base_path}/build/fuzzer.o', '-o', f'{base_path}/build/{bin_name}',
            '-lz'
        ]
        sub.run(link_cmd, capture_output=True, check=True)
        logger.info("Compiled fuzzer binary")
        return bin_name
    except Exception as err:
        raise TestRunException(logger, f"failed to compile", err)


# TODO  logfile:  <inputname without .format>.log i will keep this at one log file for now
def run_parser_on_input(parser, test_input, base_path, logger):
    try:
        cmd = [f"{base_path}/build/{parser}", "parse", test_input]
        parse_tree = sub.run(cmd, capture_output=True)
        parser_version = "reference" if "test" not in parser else "converted"
        with open(
                f"{base_path}/output/{path.basename(test_input).rsplit('.', 1)[0]}-{parser_version}.output",
                "w") as file:
            file.write(parse_tree.stdout.decode())

        return parser, path.basename(
            test_input), parse_tree.returncode, parse_tree.stdout.decode(), parse_tree.stderr.decode()
    except Exception as err:
        raise TestRunException(logger, f"failed to run parser", err)


def diff_parse_trees(expected: str, actual: str, logger) -> str:
    # if expected == actual:
    #    return True
    diff = "\n".join(
        difflib.context_diff(expected.split("\n"),
                             actual.split("\n"),
                             fromfile="expected-parse-tree",
                             tofile="actual-parse-tree",
                             n=4))
    logger.debug(diff)
    return diff


def generate_test_results_for_test_files(ref_parse_trees, test_parse_trees, format_name, logger):
    garbage_overwrite = True  # if True : status = passed if garbage in both trees

    if len(ref_parse_trees) != len(test_parse_trees):
        logger.error(f"ERROR: count of parse trees do not match REF {len(ref_parse_trees)} TEST {len(test_parse_trees)}")

    runs = len(ref_parse_trees)
    logger.info(f"Format: {format_name}:")
    for run_index in range(runs):
        error_msg = []
        (ref_name, ref_fn, ref_ret_code, ref_tree, ref_stderr) = ref_parse_trees[run_index]
        (test_name, test_fn, test_ret_code, test_tree, test_stderr) = test_parse_trees[run_index]
        ref_last_lines = ref_tree.split("\n")[-10:-2]
        test_last_lines = test_tree.split("\n")[-10:-2]
        ref_largest_offset = max([int(i.split(",")[1]) for i in ref_last_lines])
        test_largest_offset = max([int(i.split(",")[1]) for i in test_last_lines])
        file_size = int(test_tree.split('\n')[0].split("SIZE ")[1]) - 1
        correct_parsed_sizes = ref_largest_offset == test_largest_offset == file_size
        ret_codes_good = ref_ret_code == test_ret_code == 0
        garbage_in_test = "garbage_after_end_of_parsed_file_CONVERTER" in "".join(test_last_lines)
        garbage_in_ref = "garbage" in "".join(ref_last_lines)
        garbage_flag = not (garbage_in_ref and garbage_overwrite)
        test_err_msg = test_stderr.split("\n")
        ref_err_msg = ref_stderr.split("\n")
        if garbage_in_test and ret_codes_good and garbage_flag:
            error_msg.append(f'    Found potential Garbage-Data at end of {test_fn}')
            error_msg.append(f'    Check in Ref-Parse-Tree!')
            status = "TBD"
        elif correct_parsed_sizes and ret_codes_good:
            status = "PASSED"
        else:
            status = "FAILED"
            error_msg.append(f"    Test_ret {test_ret_code} Ref_ret {ref_ret_code}\n")
            error_msg.append(f"++++Test Parser Log:\n")
            error_msg.extend(["    " + s for s in test_err_msg[0:-2]])
            error_msg.append(f"\n----Reference Parser Log:\n")
            error_msg.extend(["    " + s for s in ref_err_msg[0:-2]])

        error_msg = "\n".join(error_msg)
        logger.info(f"\n\n====Result for Testfile {test_fn}:\n"
                    f'\n    Status: {status}\n{error_msg}\n')


def run_single_format_parse_test(format_name, resolve_test_input, logger):
    base_path = create_fmt_folder(format_name)
    logfile = f'{base_path}/output/test-{format_name}-fuzzer.log'
    reset_logger(logger, file_path=logfile)

    try:
        if not path.isdir(KAITAI_BASE_PATH):
            raise Exception("kaitai base path is no directory")
        ksy_files = find_templates(KAITAI_BASE_PATH, format_name, "ksy")
        ff_templates = find_templates(BT_TEMPLATE_BASE_PATH, format_name, "bt")
        test_inputs = resolve_test_input(format_name, logger)
        if not ff_templates:
            logger.error(f"Either template set empty ( FF: {len(ff_templates)})")
            raise FileNotFoundError()
        if not test_inputs:
            logger.error(f"Either template set empty (TEST: {len(test_inputs)})")
            raise FileNotFoundError()

        test_parse_trees = []
        ref_parse_trees = []

        # run reference parser on test inputs
        for (file_path, name) in ff_templates:
            logger.info(f"Compiling reference template {name} at location {file_path}")
            parser = compile_parser(file_path, base_path, logger)
            for ti in test_inputs:
                logger.info(f"running Reference-Parser on test file {path.basename(ti)}")
                ref_parse_trees.append(run_parser_on_input(parser, ti, base_path, logger))

        # run parsers under test on test inputs
        for (file_path, name) in ksy_files:
            logger.info(f"Converting template {name} at location {file_path}")
            converted_file = call_converter(file_path, name, base_path, logger)
            parser = compile_parser(converted_file, base_path, logger, True)
            for ti in test_inputs:
                logger.info(f"running Test-Parser on test file {path.basename(ti)}")
                test_parse_trees.append(run_parser_on_input(parser, ti, base_path, logger))

            # compare outputs
            generate_test_results_for_test_files(ref_parse_trees, test_parse_trees, format_name, logger)

        reset_logger(logger)
    except FileNotFoundError:
        log.error(f"No test files for {format_name} found, skipping!!")
    except TestRunException as e:
        e.print()
        reset_logger(logger)


def run_multi_format_parse_test(formats, test_input_resolver, logger):
    passed = []
    for fmt in formats:
        logger.info("Current format: %s", fmt)
        passed.append((fmt, run_single_format_parse_test(fmt, test_input_resolver, logger)))


def provide_wild_files(file_root):
    def load_wild_files(format_name, logger, multiple=True):
        format_path = path.join(file_root, format_name)
        files = [
            path.join(format_path, f) for f in listdir(format_path)
            if path.isfile(path.join(format_path, f))
        ]
        if len(files) == 0:
            raise TestRunException(logger, "No test files found")
        if multiple:
            return files
        else:
            return files[1:1]

    return load_wild_files


def main():
    parser = parse.ArgumentParser(description="Run tests on converted templates")
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
    parser.add_argument('--test-folder',
                        metavar='folder',
                        dest='test_folder',
                        nargs='?',
                        type=str,
                        default=TEST_FILE_ROOT)
    parser.add_argument('--filter-diffs', action='store_true', dest="filter_diffs",
                        help='filter "useless" diffs')
    parser.add_argument('--no-filter-diffs', action='store_false', dest="filter_diffs",
                        help='do not filter "useless" diffs')
    parser.set_defaults(filter_diffs=True)
    parsed_args = parser.parse_args(sys.argv[1::])
    numeric_level = getattr(log, parsed_args.log_lvl.upper(), log.INFO)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % numeric_level)
    logger = set_up_logger(numeric_level)
    logger.info("===Starting test bench run===")
    provide_files = provide_wild_files(parsed_args.test_folder)
    if len(parsed_args.formats) == 1:
        logger.info("Running test for single format %s", parsed_args.formats[0])
        run_single_format_parse_test(
            parsed_args.formats[0],
            lambda fmt, curr_log: parsed_args.testInput if parsed_args.testInput else provide_files(fmt, curr_log),
            logger)
    else:
        logger.info("Running test for multiple formats")
        run_multi_format_parse_test(parsed_args.formats, provide_files, logger)


if __name__ == "__main__":
    main()
