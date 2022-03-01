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


def set_up_logger(level):
    consoleLog = log.StreamHandler()
    logfile = log.FileHandler("testbench.log", mode='w')
    logfile.setLevel(level)
    log.basicConfig(format='%(asctime)s::%(levelname)s:%(message)s',
                    level=level,
                    handlers=[consoleLog, logfile],
                    datefmt="%Y-%m-%d %H:%M:%S")
    return log.getLogger('root')


def create_fmt_folder(formatName):
    if not os.path.exists(TESTFOLDER + formatName):
        os.makedirs(TESTFOLDER + formatName)
        os.makedirs(TESTFOLDER + formatName + "/build")
        os.makedirs(TESTFOLDER + formatName + "/output")
        os.makedirs(TESTFOLDER + formatName + "/input")
    return TESTFOLDER + formatName


class TestRunException(Exception):
    """thrown if any part of a test run fails"""
    def __init__(self, logger, msg, cause: Exception = None):
        self.msg = msg
        self.cause = cause
        self.logger = logger

    def print(self):
        self.logger.error(self.msg)
        if isinstance(self.cause, subprocess.CalledProcessError):
            self.logger.error(self.cause.cmd)
            self.logger.error(self.cause.returncode)
            self.logger.error(f"Stderr: {self.cause.stderr.decode()}")
            linefinder = r"(Compile|Parse)Error.*:(\d+):(\d+):"
            lines = re.finditer(linefinder, self.cause.stderr.decode())
            for _, ma in enumerate(lines, 1):
                _, ln, cl = ma.groups()
                self.logger.error("Error occurred on line: %s, column: %s", ln,
                                  cl)
            self.logger.error(f"Stdout: {self.cause.output.decode()}")
        elif (self.cause is not None):
            self.logger.error(self.cause)
            self.logger.error(self.cause.args)


# should return file path or false in not found
def findFileRecursively(base_path, name, ext, logger, maxDepth=3):
    cmd = [
        'find',
        path.normpath(base_path), '-maxdepth', f'{maxDepth}', '-name',
        f'{name}.{ext}'
    ]
    found_file = subprocess.run(cmd, stdout=subprocess.PIPE)
    if (found_file.returncode != 0):
        logger.error(f"Error ret: {found_file.stderr}")
        return False
    if (len(found_file.stdout) == 0):
        logger.error(f"Error: {found_file.stderr}")
        return False

    logger.debug(f"Debug: find output {found_file.stdout.decode()}")
    splitOut = found_file.stdout.decode().split("\n")
    if (len(splitOut) > 2):
        #some default behavior, maybe make this a user ask
        logger.warning(f"multiple results found. using the first one.")
    return splitOut[0]


def runSingleFormatParseTest(formatName, resolveTestInput, logger):
    logger_fmt = logger.getChild(formatName)
    basePath = create_fmt_folder(formatName)
    logfileName = f'{basePath}/output/test-{formatName}-fuzzer.output'
    logger.handlers = [
        log.StreamHandler(),
        log.FileHandler(logfileName, mode='w')
    ]
    try:
        convertedFile = callConverter(
            formatName, basePath,
            logger_fmt)  # contains path to converted file

        logfileName = f'{TESTFOLDER}{formatName}/output/test-{formatName}-fuzzer.output'
        logger.handlers = [log.StreamHandler(), log.FileHandler(logfileName)]
        parserUnderTest = compileParser(convertedFile,
                                        test=True,
                                        basePath=basePath,
                                        logger=logger_fmt)
        # contains path to reference template
        referenceTemplate = findFileRecursively(BT_TEMPLATE_BASE_PATH,
                                                formatName, 'bt', logger_fmt)
        if not referenceTemplate:
            raise TestRunException(logger_fmt,
                                   "Reference template file not found")
        referenceParser = compileParser(referenceTemplate,
                                        basePath=basePath,
                                        logger=logger_fmt)
        testInput = resolveTestInput(formatName, referenceParser)
        referencePT = runParserOnInput(referenceParser, testInput, basePath,
                                       logger)
        PTunderTest = runParserOnInput(parserUnderTest, testInput, basePath,
                                       logger)
        return diffParseTrees(referencePT, PTunderTest, logger_fmt)
    except TestRunException as e:
        e.print()
        return False


def callConverter(formatName, basePath, logger):
    # resolve kaitai struct path and feed to our converter
    if (not path.isdir(KAITAI_BASE_PATH)):
        raise Exception("kaitai base path is no directory")

    filePath = findFileRecursively(KAITAI_BASE_PATH, formatName, "ksy", logger)
    if (not filePath):
        raise TestRunException(
            logger,
            f"Kaitai struct file not found, path: {path.join(KAITAI_BASE_PATH, formatName)}.ksy"
        )
    WORKING_DIR = basePath + "/build"

    logger.info(f"found file to convert: {filePath}. converting...")
    try:
        convert = subprocess.run(
            ["python3", CONVERTER, filePath, f"{WORKING_DIR}/{formatName}.bt"],
            check=True,
            capture_output=True)
        logger.info(convert.stdout.decode())
    except Exception as err:
        raise TestRunException(logger, "Conversion Failed", err)
    if (convert.returncode != 0):
        raise TestRunException(logger, f"Error: {convert.stderr}")
    logger.info(
        f"Converted file successfully. Result saved in Converter/test/{formatName}/build/{formatName}.bt"
    )
    return f"{WORKING_DIR}/{formatName}.bt"


def runMultiFromatParseTest(formats, testInputResolver, logger):
    passed = []
    for fmt in formats:
        logger.info("Current format: %s", fmt)
        passed.append(
            (fmt, runSingleFormatParseTest(fmt, testInputResolver, logger)))

    logger.info("Passed status of formats: \n")
    for (fmt, status) in passed:
        logger.info(
            f"Format: {fmt}, Status: { 'Passed' if status else 'Failed'}")


def diffParseTrees(expected, actual, logger):
    if expected == actual:
        return True
    diff = "\n".join(
        difflib.unified_diff(expected.split("\n"),
                             actual.split("\n"),
                             fromfile="expected-parse-tree",
                             tofile="actual-parse-tree",
                             n=4))
    logger.warning(diff)
    return False


def compileParser(templatePath, basePath, logger, test=False):
    try:
        #./ffcompile templates/gif.bt gif.cpp
        #g++ -c -I . -std=c++17 -g -O3 -Wall fuzzer.cpp
        #g++ -c -I . -std=c++17 -g -O3 -Wall gif.cpp
        # g++ -O3 gif.o fuzzer.o -o gif-fuzzer -lz
        flavor = ""
        if test:
            logger.info("Compiling parser under test")
            flavor = "test_"
        else:
            logger.info("Compiling reference parser")
            flavor = "reference_"
        logger.info("Compiling template...")
        fmtName = path.basename(templatePath).split('.')[0]
        ffCompCmd = [
            FFCOMPILE, templatePath, f"{basePath}/build/{flavor}{fmtName}.cpp"
        ]
        subprocess.run(ffCompCmd, capture_output=True, check=True)
        logger.info("Compiled template")
        logger.info("Compiling general fuzzer api...")
        fuzzerCppCmd = [
            'g++', '-c', '-I',
            path.normpath(FFROOT) + "/", '-std=c++17', '-g', '-O3', '-Wall',
            path.normpath(f'{FFROOT}fuzzer.cpp'), '-o',
            f'{basePath}/build/fuzzer.o'
        ]
        subprocess.run(fuzzerCppCmd, capture_output=True, check=True)
        logger.info("Compiled general fuzzer api")
        logger.info("Compiling format code...")
        compFuzzerCmd = [
            'g++', '-c', '-I',
            path.normpath(FFROOT), '-std=c++17', '-g', '-O3', '-Wall',
            f'{basePath}/build/{flavor}{fmtName}.cpp', '-o',
            f'{basePath}/build/{flavor}{fmtName}.o'
        ]
        subprocess.run(compFuzzerCmd, capture_output=True, check=True)
        logger.info("Compiled format code")
        logger.info("Compiling fuzzer binary...")
        binName = f'test-{fmtName}-fuzzer' if test else f'{fmtName}-fuzzer'
        linkCmd = [
            'g++', '-O3', f'{basePath}/build/{flavor}{fmtName}.o',
            f'{basePath}/build/fuzzer.o', '-o',
            f'{basePath}/build/{binName}', '-lz'
        ]
        subprocess.run(linkCmd, capture_output=True, check=True)
        logger.info("Compiled fuzzer binary")
        return binName
    except Exception as err:
        raise TestRunException(logger, f"failed to compile", err)


def runParserOnInput(parser, testInput, basePath, logger):
    try:
        cmd = [f"{basePath}/build/{parser}", "parse", testInput]
        parseTree = subprocess.run(cmd, check=True, capture_output=True)
        if (parseTree.returncode != 0):
            raise TestRunException(logger, f"Error ret: {parseTree.stderr}")
        if (len(parseTree.stdout) == 0):
            raise TestRunException(logger, f"Error : {parseTree.stderr}")
        #print(parseTree.stderr.decode())
        with open(f"{basePath}/output/{parser}.output", "w") as file:
            file.write(parseTree.stdout.decode())

        return parseTree.stdout.decode()
    except Exception as err:
        raise TestRunException(logger, f"failed to run parser", err)


def resolveTestInputByFormat(formatName, generator, basePath):
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
        return f"{basePath}/input/testinput.{formatName}"
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
    numeric_level = getattr(log, parsedArgs.log_lvl.upper(), log.INFO)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % numeric_level)
    logger = set_up_logger(numeric_level)
    logger.info("===Starting test bench run===")
    if (len(parsedArgs.formats) == 1):
        logger.info("Running test for single format %s", parsedArgs.formats[0])
        testInputResolver = lambda fmt, parser: parsedArgs.testInput if parsedArgs.testInput else resolveTestInputByFormat(
            fmt, parser, create_fmt_folder(fmt))
        runSingleFormatParseTest(parsedArgs.formats[0], testInputResolver,
                                 logger)
        return
    logger.info("Runing test for multiple formats")
    runMultiFromatParseTest(parsedArgs.formats, resolveTestInputByFormat,
                            logger)


if __name__ == "__main__":
    main()
