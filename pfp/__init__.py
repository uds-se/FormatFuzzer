#!/usr/bin/env python

import os
import sys

import pfp.interp
import py010parser.c_parser

PARSER = py010parser.c_parser.CParser()

def parse(data=None, template=None, data_file=None, template_file=None, interp=None, debug=False):
	"""Parse the data stream using the supplied template. The data stream
	WILL NOT be automatically closed.

	:data: Input stream (yes, a STREAM, not str)
	:template: template contents (str)
	:data_file: path to the data to be used as the input stream
	:template_file: template file path
	:interp: the interpretor to be used (a default one will be created if ``None``)
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
	
	if template_file is not None:
		try:
			with open(os.path.expanduser(template_file), "r") as f:
				template = f.read()
		except Exception as e:
			raise Exception("Could not open template file '{}'".format(template_file))

	# the user may specify their own instance of PfpInterp to be
	# used
	if interp is None:
		interp = pfp.interp.PfpInterp(debug=debug, parser=PARSER)

	dom = interp.parse(data, template)

	# close the data stream if a data_file was specified
	if data_file is not None:
		data.close()

	return dom
