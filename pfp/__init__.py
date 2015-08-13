#!/usr/bin/env python

import os
import sys

import py010parser.c_parser

import pfp.interp
from pfp.bitwrap import BitwrappedStream

PARSER = py010parser.c_parser.CParser()

def parse(data=None, template=None, data_file=None, template_file=None, interp=None, debug=False, predefines=True, int3=True, cpp_path="cpp", cpp_args="-xc++"):
	"""Parse the data stream using the supplied template. The data stream
	WILL NOT be automatically closed.

	:data: Input stream (yes, a STREAM, not str)
	:template: template contents (str)
	:data_file: path to the data to be used as the input stream
	:template_file: template file path
	:interp: the interpretor to be used (a default one will be created if ``None``)
	:debug: if debug information should be printed while interpreting the template (false)
	:predefines: if built-in type information should be inserted (true)
	:int3: if debugger breaks are allowed while interpreting the template (true)
	:cpp_path: the path to the ``cpp`` binary, used to strip comments ("cpp")
	:cpp_args: the args to the ``cpp`` binary to strip comments. Defaults to "", but "-xc++" might be useful on macs.
	:returns: pfp DOM
	"""
	if data is None and data_file is None:
		raise Exception("No input data was specified")
	
	if data is not None and data_file is not None:
		raise Exception("Only one input data may be specified")
	
	if data_file is not None:
		data = open(os.path.expanduser(data_file), "rb")

	if template is None and template_file is None:
		raise Exception("No template specified!")
	
	if template is not None and template_file is not None:
		raise Exception("Only one template may be specified!")
	
	orig_filename = "string"
	if template_file is not None:
		orig_filename = template_file
		try:
			with open(os.path.expanduser(template_file), "r") as f:
				template = f.read()
		except Exception as e:
			raise Exception("Could not open template file '{}'".format(template_file))

	# the user may specify their own instance of PfpInterp to be
	# used
	if interp is None:
		interp = pfp.interp.PfpInterp(debug=debug, parser=PARSER, int3=int3, cpp_path=cpp_path, cpp_args=cpp_args)
	
	# so we can consume single bits at a time
	data = BitwrappedStream(data)

	dom = interp.parse(data, template, predefines=predefines, orig_filename=orig_filename)

	# close the data stream if a data_file was specified
	if data_file is not None:
		data.close()

	return dom
