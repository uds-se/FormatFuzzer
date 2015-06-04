#!/usr/bin/env python

import os
import sys

def parse(stream, template, interp=None):
	"""Parse the stream using the supplied template

	:stream: Input stream
	:template: template contents (str)
	:interp: the interpretor to be used (a default one will be created if ``None``)
	:returns: pfp DOM
	"""
	import pfp.interp

	if interp is None:
		interp = pfp.interp.PfpInterp()
	dom = interp.parse(stream, template)
	return dom
