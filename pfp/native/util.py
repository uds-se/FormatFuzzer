#!/usr/bin/env python
# encoding: utf-8

import sys

from pfp.native import native
import pfp.fields

@native(name="Printf", ret=pfp.fields.Int)
def printf(params, ctxt, scope, stream):
	"""Prints format string to stdout

	:params: TODO
	:returns: TODO

	"""
	if len(params) == 1:
		sys.stdout.write(PYVAL(params[0]))
		return

	to_print = PYVAL(params[0]) % tuple(PYVAL(x) for x in params[1:])
	res = len(to_print)
	sys.stdout.write(to_print)
	sys.stdout.flush()
	return res
