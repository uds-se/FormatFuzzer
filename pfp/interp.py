#!/usr/bin/env python

"""
Python format parser
"""

import sys
import os

import py010parser

class PfpInterp(object):
    """
    """

    def __init__(self):
        """
        """
        pass

    def parse(self, stream, template):
        """Parse the data stream using the template

        :stream: TODO
        :template: TODO
        :returns: TODO

        """
        self._stream = stream
        self._template = template
        self._010_ast = py010parser.parse_string(template)
