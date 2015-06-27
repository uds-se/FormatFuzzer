#!/usr/bin/env python
# encoding: utf-8

import os
import six
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
		self._start_endian = pfp.fields.NumberBase.endian
	
	def tearDown(self):
		pfp.fields.NumberBase.endian = self._start_endian
	
	def test_big_endian(self):
		# just something different so that we know it changed
		pfp.fields.NumberBase.endian = pfp.fields.LITTLE_ENDIAN
		dom = self._test_parse_build(
			"",
			"""
				BigEndian();
			"""
		)
		self.assertEqual(pfp.fields.NumberBase.endian, pfp.fields.BIG_ENDIAN)

	def test_little_endian(self):
		# just something different so that we know it changed
		pfp.fields.NumberBase.endian = pfp.fields.BIG_ENDIAN
		dom = self._test_parse_build(
			"",
			"""
				LittleEndian();
			"""
		)
		self.assertEqual(pfp.fields.NumberBase.endian, pfp.fields.LITTLE_ENDIAN)
	
	def test_file_size(self):
		input_ = six.StringIO("ABCDE")
		output_ = six.StringIO()
		sys.stdout = output_
		dom = pfp.parse(
			input_,
			"""
			Printf("%d", FileSize());
			""",
		)
		sys.stdout = sys.__stdout__

		self.assertEqual(output_.getvalue(), "5")

if __name__ == "__main__":
	unittest.main()
