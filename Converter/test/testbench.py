#!/usr/bin/env python
import os.path as path
import subprocess
import logging as log
import difflib
import sys
import argparse

#NOTE change these as needed
KAITAI_BASE_PATH = "kaitai_formats/"
BT_TEMPLATE_BASE_PATH = "../templates/"
FFCOMPILE = "../ffcompile"
CONVERTER = "Converter.py"


class TestRunException(Exception):
    """thrown if any part of a test run fails"""
    def __init__(self, msg, cause: Exception):
        self.msg = msg
        self.cause = cause

    def print(self):
        log.error(self.msg)
        if isinstance(self.cause, subprocess.CalledProcessError):
            log.error(self.cause.cmd)
            log.error(self.cause.returncode)
            log.error(self.cause.stderr)
            log.error(self.cause.output)


# should return file path or false in not found
def findFileRecursively(name, ext, maxDepth=3):
    cmd = [
        'find',
        path.normpath(KAITAI_BASE_PATH), '-maxdepth', f'{maxDepth}', '-name',
        f'{name}.{ext}'
    ]
    #cmd = f"find {path.normpath(KAITAI_BASE_PATH)} -maxdepth {maxDepth} -name \"{name}.{ext}\""
    found_file = subprocess.run(cmd, shell=False, stdout=subprocess.PIPE)
    if (found_file.returncode != 0):
        log.error(f"Error ret: {found_file.stderr}")
        return False
    if (len(found_file.stdout) == 0):
        log.error(f"Error: {found_file.stderr}")
        return False

    # print(f"Debug: find output {found_file.stdout.decode()}")
    splitOut = found_file.stdout.decode().split("\n")
    if (len(splitOut) > 2):
        #some default behavior, maybe make this a user ask
        log.warn(f"multiple results found. using the first one.")
    return splitOut[0]


def runSingleFormatParseTest(formatName, resolveTestInput):
    try:
        convertedFile = callConverter(
            formatName)  #contains path to converted file
        parserUnderTest = compileParser(convertedFile)
        #contains path to reference template
        referenceTemplate = findFileRecursively(formatName, 'bt')
        if not referenceTemplate:
            raise TestRunException("Reference template file not found")
        referenceParser = compileParser(referenceTemplate)
        testInput = resolveTestInput(formatName, referenceParser)
        PTunderTest = runParserOnInput(parserUnderTest, testInput)
        referencePT = runParserOnInput(referenceParser, testInput)
        return diffParseTrees(referencePT, PTunderTest)
    except TestRunException as e:
        e.print()
        return False


def callConverter(formatName):
    # resolve kaitai struct path and feed to our converter
    if (not path.isdir(KAITAI_BASE_PATH)):
        raise Exception("kaitai base path is no directory")

    #kaitai_ext = f"{0}.ksy".format(formatName)
    filePath = findFileRecursively(formatName, "ksy")
    if (not filePath):
        raise TestRunException(
            f"Kaitai struct file not found, path: {path.join(KAITAI_BASE_PATH,formatName)}.ksy"
        )
    log.info(f"found file to convert: {filePath}. converting...")
    convert = subprocess.run(
        ["python3", CONVERTER, filePath, f"{formatName}.bt"], check=True)
    if (convert.returncode != 0):
        raise TestRunException(f"Error: {convert.stderr}")
    log.info(f"Converted file successfully. Result saved in {formatName}.bt")
    return f"{formatName}.bt"


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
    for line in difflib.unified_diff(expected,
                                     actual,
                                     fromfile="expected-parse-tree",
                                     tofile="actual-parse-tree"):
        log.warn(line)
    return False


def compileParser(templatePath, test=False):
    try:
        #./ffcompile templates/gif.bt gif.cpp
        #g++ -c -I . -std=c++17 -g -O3 -Wall fuzzer.cpp
        #g++ -c -I . -std=c++17 -g -O3 -Wall gif.cpp
        # g++ -O3 gif.o fuzzer.o -o gif-fuzzer -lz
        fmtName = path.basename(templatePath).split('.')[0]
        ffCompCmd = [FFCOMPILE, templatePath, f"{fmtName}.cpp"]
        result = subprocess.check_call(ffCompCmd)
        fuzzerCppCmd = "g++ -c -I . -std=c++17 -g -O3 -Wall fuzzer.cpp"
        subprocess.check_call(ffCompCmd, shell=True)
        compFuzzerCmd = [
            'g++', '-c', '-I', '.', '-std=c++17', '-g', '-O3', '-Wall',
            f'{fmtName}.cpp'
        ]
        subprocess.check_call(compFuzzerCmd)
        binName = f'test-{fmtName}-fuzzer' if test else f'{fmtName}-fuzzer'
        linkCmd = [
            'g++', '-O3', f'{fmtName}.o', 'fuzzer.o', '-o', binName, '-lz'
        ]
        subprocess.check_call(linkCmd)
        return binName
    except subprocess.CalledProcessError as err:
        raise TestRunException(f"failed to compile", err)


def runParserOnInput(parser, testInput):
    cmd = [parser, testInput]
    parseTree = subprocess.run(cmd, stdout=subprocess.PIPE)
    if (parseTree.returncode != 0):
        raise TestRunException(f"Error ret: {found_file.stderr}")
    if (len(parseTree.stdout) == 0):
        raise TestRunException(f"Error : {found_file.stderr}")
    return parseTree.stdout.decode()


def resolveTestInputByFormat(formatName, generator):
    try:
        cmd = [parser, "fuzz", f"testinput.{formatName}"]
        out = subprocess.run(cmd,
                             check=True,
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as err:
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
    numeric_level = getattr(log, parsedArgs.log_lvl.upper(), None)

    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    consoleLog = log.StreamHandler()
    logfile = log.FileHandler("testbench.log")
    log.basicConfig(format='%(asctime)s::%(levelname)s:%(message)s',
                    level=numeric_level,
                    handlers=[consoleLog, logfile],
                    datefmt="%Y-%m-%d %H:%M:%S")
    log.info("===Statring test bench run===")
    if (len(parsedArgs.formats) == 1):
        log.info("Running test for single format %s", parsedArgs.formats[0])
        testInputResolver = lambda fmt: parsedArgs.testInput if parsedArgs.testInput else resolveTestInputByFormat
        runSingleFormatParseTest(parsedArgs.formats[0], testInputResolver)
        return
    log.info("Runing test for multiple formats")
    runMultiFromatParseTest(parsedArgs.formats, resolveTestInputByFormat)


if __name__ == "__main__":
    main()
