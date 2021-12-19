#!/usr/bin/env python
import os.path as path
import os

KAITAI_BASE_PATH="" #todo fill
BT_TEMPLATE_BASE_PATH="" #todo fill

def runSingleFormatParseTest(formatName="png"):
    pass

def callConverter(formatName):
    # resolve kaitai struct path and feed to our converter
    if(not path.isdir(KAITAI_BASE_PATH)) :
        raise "kaitai base path is no directory"
    if(os.listdir(KAITAI_BASE_PATH).)
    pass

def runMultiFromatParseTest(formats=[]):
    pass

def diffParseTrees(expected, actual):
    pass

def compileParser(templatePath):
    pass

def runParserOnInput(parser, testInput):
    pass

def resolveTestInputByFormat(formatName):
    pass
