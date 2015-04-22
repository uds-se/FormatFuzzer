#!/usr/bin/env python

import os
import sys

def parse(stream, template):
	"""Parse the stream using the supplied template

	:stream: Input stream
	:template: template contents (str)
	:returns: pfp DOM

	"""
	import pfp.interp

	interpretor = pfp.interp.PfpInterp()
	dom = interpretor.parse(stream, template)
	return dom
