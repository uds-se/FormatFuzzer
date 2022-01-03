#!/usr/bin/env python
import os.path as path
import subprocess
import difflib

#NOTE change these as needed
KAITAI_BASE_PATH = "kaitai_formats/"
BT_TEMPLATE_BASE_PATH = "../templates/"
FFCOMPILE = "../ffcompile"

#TODO add better prints


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
        print(f"Error ret: {found_file.stderr}")
        return False
    if (len(found_file.stdout) == 0):
        print(f"Error: {found_file.stderr}")
        return False

    # print(f"Debug: find output {found_file.stdout.decode()}")
    splitOut = found_file.stdout.decode().split("\n")
    if (len(splitOut) > 2):
        #some default behavior, maybe make this a user ask
        print(f"multiple results found. using the first one.")
    return splitOut[0]


def runSingleFormatParseTest(formatName, testInput):
    convertedFile = callConverter(formatName)  #contains path to converted file
    parserUnderTest = compileParser(convertedFile)
    #contains path to reference template
    referenceTemplate = findFileRecursively(formatName, 'bt')
    referenceParser = compileParser(referenceTemplate)
    # testInput = resolveTestInputByFormat(formatName)
    PTunderTest = runParserOnInput(parserUnderTest, testInput)
    referencePT = runParserOnInput(referenceParser, testInput)
    return diffParseTrees(referencePT, PTunderTest)


def callConverter(formatName):
    # resolve kaitai struct path and feed to our converter
    if (not path.isdir(KAITAI_BASE_PATH)):
        raise Exception("kaitai base path is no directory")

    #kaitai_ext = f"{0}.ksy".format(formatName)
    filePath = findFileRecursively(formatName, "ksy")
    if (not filePath):
        return False
    print(f"found file to convert: {filePath}. converting...")
    convert = subprocess.run(
        ["python3", "../Converter.py", filePath, f"{formatName}.bt"])
    if (convert.returncode != 0):
        print(convert.stderr)
        return False
    print(f"Converted file successfully. Result saved in {formatName}.bt")
    return f"{formatName}.bt"


def runMultiFromatParseTest(formats=[]):
    passed = []
    for fmt in formats:
        passed.append((fmt, runSingleFormatParseTest(fmt)))

    print("Passed status of formats: \n")
    print(passed)


def diffParseTrees(expected, actual):
    if expected == actual:
        return True
    for line in difflib.unified_diff(expected,
                                     actual,
                                     fromfile="expected-parse-tree",
                                     tofile="actual-parse-tree"):
        print(line)
    return False


def compileParser(templatePath, test=False):
    #./ffcompile templates/gif.bt gif.cpp
    #g++ -c -I . -std=c++17 -g -O3 -Wall fuzzer.cpp
    #g++ -c -I . -std=c++17 -g -O3 -Wall gif.cpp
    # g++ -O3 gif.o fuzzer.o -o gif-fuzzer -lz
    fmtName = path.basename(templatePath).split('.')[0]
    ffCompCmd = [FFCOMPILE, templatePath, f"{fmtName}.cpp"]
    result = subprocess.call(ffCompCmd, check=True)
    fuzzerCppCmd = "g++ -c -I . -std=c++17 -g -O3 -Wall fuzzer.cpp"
    subprocess.call(ffCompCmd, check=True, shell=True)
    compFuzzerCmd = [
        'g++', '-c', '-I', '.', '-std=c++17', '-g', '-O3', '-Wall',
        f'{fmtName}.cpp'
    ]
    subprocess.call(compFuzzerCmd, check=True)
    binName = f'test-{fmtName}-fuzzer' if test else f'{fmtName}-fuzzer'
    linkCmd = ['g++', '-O3', f'{fmtName}.o', 'fuzzer.o', '-o', binName, '-lz']
    subprocess.call(linkCmd, check=True)
    return binName


def runParserOnInput(parser, testInput):
    cmd = [parser, testInput]
    parseTree = subprocess.run(cmd, stdout=subprocess.PIPE)
    if (parseTree.returncode != 0):
        print(f"Error ret: {found_file.stderr}")
        return False
    if (len(parseTree.stdout) == 0):
        print(f"Error: {found_file.stderr}")
        return False
    return parseTree.stdout.decode()


#maybe scrap this.
def resolveTestInputByFormat(formatName):  #TODO talk with daniel on this
    pass


print(findFileRecursively("png", "ksy", 5))
