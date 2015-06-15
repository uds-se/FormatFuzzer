#!/usr/bin/env python
# encoding: utf-8

import sys

# Useful for very coarse version differentiation.
PY3 = sys.version_info[0] == 3

if PY3:
	def binary(s):
		if type(s) is bytes:
			return s
		return s.encode("ISO-8859-1")
else:
	def binary(s):
		return s
