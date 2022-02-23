#!/usr/bin/env python3
import os.path as path
import subprocess
import logging as log
import difflib
import sys
import argparse
import re
import os

# NOTE change these as needed
TestBenchLoc = os.path.dirname(os.path.abspath(__file__))
KAITAI_BASE_PATH = TestBenchLoc + "/../kaitai_struct_formats/"
BT_TEMPLATE_BASE_PATH = TestBenchLoc + "/../../templates/"
FFCOMPILE = TestBenchLoc + "/../../ffcompile"
FFROOT = TestBenchLoc + "/../../"
CONVERTER = TestBenchLoc + "/Converter.py"
TESTFOLDER = TestBenchLoc + "/../test/"
WORKING_DIR = ""

# TODO save generated Files in test folder and adjust code to using that

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
    try:
        convertedFile = callConverter(
            formatName)  #contains path to converted file
        parserUnderTest = compileParser(convertedFile, True)
        #contains path to reference template
        referenceTemplate = findFileRecursively(BT_TEMPLATE_BASE_PATH,
                                                formatName, 'bt')
        if not referenceTemplate:
            raise TestRunException("Reference template file not found")
        referenceParser = compileParser(referenceTemplate)
        testInput = resolveTestInput(formatName, referenceParser)
        referencePT = runParserOnInput(referenceParser, testInput)
        PTunderTest = runParserOnInput(parserUnderTest, testInput)
        return diffParseTrees(referencePT, PTunderTest)
    except TestRunException as e:
        e.print()
        return False


def callConverter(formatName):
    # resolve kaitai struct path and feed to our converter
    if (not path.isdir(KAITAI_BASE_PATH)):
        raise Exception("kaitai base path is no directory")

    filePath = findFileRecursively(KAITAI_BASE_PATH, formatName, "ksy")
    if (not filePath):
        raise TestRunException(
            f"Kaitai struct file not found, path: {path.join(KAITAI_BASE_PATH, formatName)}.ksy"
        )
    if not os.path.exists(TESTFOLDER + formatName):
        os.makedirs(TESTFOLDER + formatName)
        os.makedirs(TESTFOLDER + formatName + "/build")
        os.makedirs(TESTFOLDER + formatName + "/output")
        os.makedirs(TESTFOLDER + formatName + "/input")
    global WORKING_DIR
    WORKING_DIR = TESTFOLDER + formatName + "/build"

    log.info(f"found file to convert: {filePath}. converting...")
    try:
        convert = subprocess.run(
            ["python3", CONVERTER, filePath, f"{WORKING_DIR}/{formatName}.bt"],
            check=True, capture_output=True)
    except Exception as err:
        raise TestRunException("Conversion Failed", err)
    if (convert.returncode != 0):
        raise TestRunException(f"Error: {convert.stderr}")
    log.info(f"Converted file successfully. Result saved in Converter/test/{formatName}/build/{formatName}.bt")
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
    if expected == actual:
        return True
    diff = "\n".join(
        difflib.unified_diff(expected.split("\n"),
                             actual.split("\n"),
                             fromfile="expected-parse-tree",
                             tofile="actual-parse-tree",
                             n=4))
    log.warning(diff)
    return False


def compileParser(templatePath, test=False):
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
        ffCompCmd = [FFCOMPILE, templatePath, f"{WORKING_DIR}/{flavor}{fmtName}.cpp"]
        subprocess.run(ffCompCmd, capture_output=True, check=True)
        log.info("Compiled template")
        log.info("Compiling general fuzzer api...")
        fuzzerCppCmd = [
            'g++', '-c', '-I',
            path.normpath(FFROOT) + "/", '-std=c++17', '-g', '-O3', '-Wall',
            path.normpath(f'{FFROOT}fuzzer.cpp'), '-o',
            f'{WORKING_DIR}/fuzzer.o'
        ]
        subprocess.run(fuzzerCppCmd, capture_output=True, check=True)
        log.info("Compiled general fuzzer api")
        log.info("Compiling format code...")
        compFuzzerCmd = [
            'g++', '-c', '-I',
            path.normpath(FFROOT), '-std=c++17', '-g', '-O3', '-Wall',
            f'{WORKING_DIR}/{flavor}{fmtName}.cpp', '-o',
            f'{WORKING_DIR}/{flavor}{fmtName}.o'
        ]
        subprocess.run(compFuzzerCmd, capture_output=True, check=True)
        log.info("Compiled format code")
        log.info("Compiling fuzzer binary...")
        binName = f'test-{fmtName}-fuzzer' if test else f'{fmtName}-fuzzer'
        linkCmd = [
            'g++', '-O3', f'{WORKING_DIR}/{flavor}{fmtName}.o', f'{WORKING_DIR}/fuzzer.o', '-o',
            f'{WORKING_DIR}/{binName}', '-lz'
        ]
        subprocess.run(linkCmd, capture_output=True, check=True)
        log.info("Compiled fuzzer binary")
        return binName
    except Exception as err:
        raise TestRunException(f"failed to compile", err)


def runParserOnInput(parser, testInput):
    try:
        cmd = [f"{WORKING_DIR}/{parser}", "parse", testInput]
        parseTree = subprocess.run(cmd, check=True, capture_output=True)
        if (parseTree.returncode != 0):
            raise TestRunException(f"Error ret: {parseTree.stderr}")
        if (len(parseTree.stdout) == 0):
            raise TestRunException(f"Error : {parseTree.stderr}")
        #print(parseTree.stderr.decode())
        with open(f"{WORKING_DIR}/../output/{parser}.output", "w") as file:
            file.write(parseTree.stdout.decode())

        return parseTree.stdout.decode()
    except Exception as err:
        raise TestRunException(f"failed to run parser", err)


def resolveTestInputByFormat(formatName, generator):
    try:
        cmd = [
            f'{WORKING_DIR}/{generator}', "fuzz",
            f"{WORKING_DIR}/../input/testinput.{formatName}"
        ]
        subprocess.run(cmd,
                       check=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
        return f"{WORKING_DIR}/../input/testinput.{formatName}"
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
    parsedArgs = parser.parse_args(sys.argv[1::])
    numeric_level = getattr(log, parsedArgs.log_lvl.upper(), 'INFO')

    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % numeric_level)
    consoleLog = log.StreamHandler()
    logfile = log.FileHandler("testbench.log")
    logfile.setLevel(numeric_level)
    log.basicConfig(format='%(asctime)s::%(levelname)s:%(message)s',
                    level=numeric_level,
                    handlers=[consoleLog, logfile],
                    datefmt="%Y-%m-%d %H:%M:%S")
    log.info("===Statring test bench run===")
    if (len(parsedArgs.formats) == 1):
        log.info("Running test for single format %s", parsedArgs.formats[0])
        testInputResolver = lambda fmt, parser: parsedArgs.testInput if parsedArgs.testInput else resolveTestInputByFormat(
            fmt, parser)
        runSingleFormatParseTest(parsedArgs.formats[0], testInputResolver)
        return
    log.info("Runing test for multiple formats")
    runMultiFromatParseTest(parsedArgs.formats, resolveTestInputByFormat)


if __name__ == "__main__":
    main()
