#!/usr/bin/env python
# encoding: utf-8

import os
try:
	from StringIO import StringIO

# StringIO does not exist in python3
except ImportError as e:
	from io import StringIO
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pfp
import pfp.fields
import pfp.interp
import pfp.utils

import utils

class TestCompat(unittest.TestCase, utils.UtilsMixin):
	def setUp(self):
		pass
	
	def tearDown(self):
		pass
	
	def test_big_endian(self):
		# just something different so that we know it changed
		pfp.fields.NumberBase.endian = "BLAH"
		dom = self._test_parse_build(
			"",
			"""
				BigEndian();
			"""
		)
		self.assertEqual(pfp.fields.NumberBase.endian, pfp.fields.BIG_ENDIAN)

	def test_little_endian(self):
		# just something different so that we know it changed
		pfp.fields.NumberBase.endian = "BLAH"
		dom = self._test_parse_build(
			"",
			"""
				LittleEndian();
			"""
		)
		self.assertEqual(pfp.fields.NumberBase.endian, pfp.fields.LITTLE_ENDIAN)

if __name__ == "__main__":
	unittest.main()
