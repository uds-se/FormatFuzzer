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
FFROOT = TestBenchLoc + "/../../"
CONVERTER = TestBenchLoc + "/Converter.py"
TESTFOLDER = TestBenchLoc + "/../test/"
TESTFILEROOT = TestBenchLoc + "/../test-files"


def find_alt_format_names(fmt):
    kaitiai_file = findFileRecursively(KAITAI_BASE_PATH, fmt, "ksy")
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
        consoleLog = log.StreamHandler()
        logfile = log.FileHandler("testbench.log", mode='w')
        logfile.setLevel(level)
        log.basicConfig(format='%(asctime)s::%(levelname)s:%(message)s',
                        level=level,
                        handlers=[consoleLog, logfile],
                        datefmt="%Y-%m-%d %H:%M:%S")
    else:
        consoleLog = log.StreamHandler()
        logfile = log.FileHandler("testbench.log", mode='w')
        log.handlers = [consoleLog, logfile]


def create_fmt_folder(formatName):
    if not os.path.exists(TESTFOLDER + formatName):
        os.makedirs(TESTFOLDER + formatName)
        os.makedirs(TESTFOLDER + formatName + "/build")
        os.makedirs(TESTFOLDER + formatName + "/output")
        os.makedirs(TESTFOLDER + formatName + "/input")
    return TESTFOLDER + formatName


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
        elif (self.cause is not None):
            log.error(self.cause)
            log.error(self.cause.args)


def try_file_exts(base_path, names, ext, max_depth=3):
    log.info(f'Names {names}')
    if type(names) is not list:
        names = [names]
    for name in names:
        temp_path = findFileRecursively(base_path, name, ext, max_depth)
        if temp_path:
            return temp_path, name
    return False, None


# should return file path or false in not found
def findFileRecursively(base_path, name, ext, maxDepth=3):
    cmd = [
        'find',
        path.normpath(base_path), '-maxdepth', f'{maxDepth}', '-name',
        f'{name}.{ext}'
    ]
    found_file = subprocess.run(cmd, stdout=subprocess.PIPE)
    if (found_file.returncode != 0):
        log.error(f"Error ret: {found_file.stderr}")
        return False
    if (len(found_file.stdout) == 0):
        log.error(f"Error: {found_file.stderr}")
        return False

    log.debug(f"Debug: find output {found_file.stdout.decode()}")
    splitOut = found_file.stdout.decode().split("\n")
    if (len(splitOut) > 2):
        #some default behavior, maybe make this a user ask
        log.warning(f"multiple results found. using the first one.")
    return splitOut[0]


def runSingleFormatParseTest(formatName, resolveTestInput):
    basePath = create_fmt_folder(formatName)
    logfileName = f'{basePath}/output/test-{formatName}-fuzzer.log-output'
    log.handlers = [
        log.StreamHandler(),
        log.FileHandler(logfileName, mode='w')
    ]
    try:
        exts = find_alt_format_names(formatName)
        # contains path to converted file
        convertedFile = callConverter(exts, basePath)
        parserUnderTest = compileParser(convertedFile,
                                        test=True,
                                        basePath=basePath)
        # contains path to reference template
        (referenceTemplate,
         formatName) = try_file_exts(BT_TEMPLATE_BASE_PATH, exts, "bt")
        if not referenceTemplate:
            raise TestRunException("Reference template file not found")
        referenceParser = compileParser(referenceTemplate, basePath=basePath)
        testInputs = resolveTestInput(formatName, referenceParser, basePath)
        for ti in testInputs:
            log.info(f"running test on input {path.basename(ti)}")
            referencePT = runParserOnInput(referenceParser, ti, basePath)
            PTunderTest = runParserOnInput(parserUnderTest, ti, basePath)
            if (isinstance(referencePT, int) and isinstance(PTunderTest, int)
                    and referencePT == PTunderTest):
                return True
            elif (isinstance(referencePT, int)
                  or isinstance(PTunderTest, int)):
                return False
            log.info(f"diff of parse trees for {path.basename(ti)}")
            diff = diffParseTrees(referencePT, PTunderTest)
        set_up_logger(None, True)
        return diff
    except TestRunException as e:
        e.print()
        set_up_logger(None, True)
        return False


def callConverter(formatNames, basePath):
    # resolve kaitai struct path and feed to our converter
    if (not path.isdir(KAITAI_BASE_PATH)):
        raise Exception("kaitai base path is no directory")

    (filePath, formatName) = try_file_exts(KAITAI_BASE_PATH, formatNames,
                                           "ksy")
    if (not filePath):
        raise TestRunException(
            f"Kaitai struct file not found, path: {path.join(KAITAI_BASE_PATH, formatName)}.ksy"
        )
    WORKING_DIR = basePath + "/build"

    log.info(f"found file to convert: {filePath}. converting...")
    try:
        convert = subprocess.run(
            ["python3", CONVERTER, filePath, f"{WORKING_DIR}/{formatName}.bt"],
            check=True,
            capture_output=True)
        log.info(convert.stdout.decode())
    except Exception as err:
        raise TestRunException("Conversion Failed", err)
    if (convert.returncode != 0):
        raise TestRunException(f"Error: {convert.stderr}")
    log.info(
        f"Converted file successfully. Result saved in Converter/test/{formatName}/build/{formatName}.bt"
    )
    return f"{WORKING_DIR}/{formatName}.bt"


def runMultiFromatParseTest(formats, testInputResolver):
    passed = []
    for fmt in formats:
        log.info("Current format: %s", fmt)
        passed.append((fmt, runSingleFormatParseTest(fmt, testInputResolver)))

    log.info("Passed status of formats: \n")
    for (fmt, status) in passed:
        log.info(f"Format: {fmt}, Status: { 'Passed' if status else 'Failed'}")


def diffParseTrees(expected, actual):
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


def compileParser(templatePath, basePath, test=False):
    try:
        #./ffcompile templates/gif.bt gif.cpp
        #g++ -c -I . -std=c++17 -g -O3 -Wall fuzzer.cpp
        #g++ -c -I . -std=c++17 -g -O3 -Wall gif.cpp
        # g++ -O3 gif.o fuzzer.o -o gif-fuzzer -lz
        flavor = ""
        if test:
            log.info("Compiling parser under test")
            flavor = "test_"
        else:
            log.info("Compiling reference parser")
            flavor = "reference_"
        log.info("Compiling template...")
        fmtName = path.basename(templatePath).split('.')[0]
        ffCompCmd = [
            FFCOMPILE, templatePath, f"{basePath}/build/{flavor}{fmtName}.cpp"
        ]
        subprocess.run(ffCompCmd, capture_output=True, check=True)
        log.info("Compiled template")
        log.info("Compiling general fuzzer api...")
        fuzzerCppCmd = [
            'g++', '-c', '-I',
            path.normpath(FFROOT) + "/", '-std=c++17', '-g', '-O3', '-Wall',
            path.normpath(f'{FFROOT}fuzzer.cpp'), '-o',
            f'{basePath}/build/fuzzer.o'
        ]
        subprocess.run(fuzzerCppCmd, capture_output=True, check=True)
        log.info("Compiled general fuzzer api")
        log.info("Compiling format code...")
        compFuzzerCmd = [
            'g++', '-c', '-I',
            path.normpath(FFROOT), '-std=c++17', '-g', '-O3', '-Wall',
            f'{basePath}/build/{flavor}{fmtName}.cpp', '-o',
            f'{basePath}/build/{flavor}{fmtName}.o'
        ]
        subprocess.run(compFuzzerCmd, capture_output=True, check=True)
        log.info("Compiled format code")
        log.info("Compiling fuzzer binary...")
        binName = f'test-{fmtName}-fuzzer' if test else f'{fmtName}-fuzzer'
        linkCmd = [
            'g++', '-O3', f'{basePath}/build/{flavor}{fmtName}.o',
            f'{basePath}/build/fuzzer.o', '-o', f'{basePath}/build/{binName}',
            '-lz'
        ]
        subprocess.run(linkCmd, capture_output=True, check=True)
        log.info("Compiled fuzzer binary")
        return binName
    except Exception as err:
        raise TestRunException(f"failed to compile", err)


def runParserOnInput(parser, testInput, basePath):
    try:
        cmd = [f"{basePath}/build/{parser}", "parse", testInput]
        parseTree = subprocess.run(cmd, capture_output=True)

        if (parseTree.returncode != 0):
            with open(
                    f"{basePath}/output/{parser}-{path.basename(testInput)}.output",
                    "w") as file:
                file.write(parseTree.stdout.decode())
            log.error(parseTree.stderr)
            return parseTree.returncode
        if (len(parseTree.stdout) == 0):
            raise TestRunException(f"Error : {parseTree.stderr}")
        with open(
                f"{basePath}/output/{parser}-{path.basename(testInput)}.output",
                "w") as file:
            file.write(parseTree.stdout.decode())

        return parseTree.stdout.decode()
    except Exception as err:
        raise TestRunException(f"failed to run parser", err)


def provideWildFiles(formatName, generator, basePath, multiple=True):
    formatPath = path.join(TESTFILEROOT, formatName)
    files = [
        path.join(formatPath, f) for f in listdir(formatPath)
        if path.isfile(path.join(formatPath, ))
    ]
    if multiple:
        return files
    else:
        return files[1:1]


def resolveTestInputByFormat(formatName, generator, basePath, multiple=False):
    try:
        cmd = [
            f'{basePath}/build/{generator}', "fuzz",
            f"{basePath}/input/testinput.{formatName}"
        ]
        subprocess.run(cmd,
                       check=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE,
                       env={"DONT_BE_EVIL": "1"})
        return [f"{basePath}/input/testinput.{formatName}"]
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
                        const=provideWildFiles,
                        default=resolveTestInputByFormat,
                        help="use real world files")
    parsedArgs = parser.parse_args(sys.argv[1::])
    numeric_level = getattr(log, parsedArgs.log_lvl.upper(), log.INFO)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % numeric_level)
    set_up_logger(numeric_level)
    log.info("===Starting test bench run===")
    if (len(parsedArgs.formats) == 1):
        log.info("Running test for single format %s", parsedArgs.formats[0])
        testInputResolver = lambda fmt, parser, basePath: parsedArgs.testInput if parsedArgs.testInput else parsedArgs.resolver(
            fmt, parser, create_fmt_folder(fmt))
        runSingleFormatParseTest(parsedArgs.formats[0], testInputResolver)
        return
    log.info("Runing test for multiple formats")
    runMultiFromatParseTest(parsedArgs.formats, parsedArgs.resolver)


if __name__ == "__main__":
    main()
