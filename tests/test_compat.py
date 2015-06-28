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

class TestCompatIO(unittest.TestCase, utils.UtilsMixin):
	def setUp(self):
		pass
	
	def tearDown(self):
		pass
	
	def test_read_ushort(self):
		dom = self._test_parse_build(
			"\x80\x01",
			"""
				local ushort blah = ReadUShort();
				Printf("%d|", blah);
				Printf("%d", FTell());
			""",
			verify=False
		)
	
	def test_read_bytes_uchar(self):
		dom = self._test_parse_build(
			"ab\x00\x01",
			"""
				local uchar data[2];
				ReadBytes(data, FTell(), 2);
				Printf(data);

				uchar a;
				uchar b;
				Printf("%d%d", a, b);
			""",
			verify=False,
			stdout="ab9798"
		)

if __name__ == "__main__":
	unittest.main()
