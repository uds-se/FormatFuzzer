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
			verify=False,
			stdout="32769|0"
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
	
	def test_seek1(self):
		dom = self._test_parse_build(
			"\x01\x02ABCD\x03\x04",
			"""
				uchar a;
				uchar b;
				FSeek(FTell() + 4);
				uchar c;
				uchar d;
			""",
		)

		self.assertEqual(dom.a, 1)
		self.assertEqual(dom.b, 2)
		self.assertEqual(dom._skipped_0, "ABCD")
		self.assertEqual(dom.c, 3)
		self.assertEqual(dom.d, 4)
	
	def test_seek2(self):
		dom = self._test_parse_build(
			"\x01\x02ABCD\x03EF\x04",
			"""
				uchar a;
				uchar b;
				FSeek(FTell() + 2);
				FSeek(FTell() + 2);
				uchar c;
				FSeek(FTell() + 2);
				uchar d;
			""",
		)

		self.assertEqual(dom.a, 1)
		self.assertEqual(dom.b, 2)
		# should be merged into one _skipped array
		self.assertEqual(dom._skipped_0, "ABCD")
		self.assertEqual(dom.c, 3)
		self.assertEqual(dom._skipped_1, "EF")
		self.assertEqual(dom.d, 4)
	
	def test_seek3(self):
		dom = self._test_parse_build(
			"ABCD",
			"""
				Printf("%d", FSeek(FTell() + 4));
				Printf("%d", FSeek(FTell() + 2));
			""",
			verify=False,
			stdout="0-1"
		)
	
	def test_skip1(self):
		dom = self._test_parse_build(
			"\x01\x02ABCD\x03\x04",
			"""
				uchar a;
				uchar b;
				FSkip(4);
				uchar c;
				uchar d;
			""",
		)

		self.assertEqual(dom.a, 1)
		self.assertEqual(dom.b, 2)
		self.assertEqual(dom._skipped_0, "ABCD")
		self.assertEqual(dom.c, 3)
		self.assertEqual(dom.d, 4)
	
	def test_seek2(self):
		dom = self._test_parse_build(
			"\x01\x02ABCD\x03EF\x04",
			"""
				uchar a;
				uchar b;
				FSkip(2);
				FSkip(2);
				uchar c;
				FSkip(2);
				uchar d;
			""",
		)

		self.assertEqual(dom.a, 1)
		self.assertEqual(dom.b, 2)
		# should be merged into one _skipped array
		self.assertEqual(dom._skipped_0, "ABCD")
		self.assertEqual(dom.c, 3)
		self.assertEqual(dom._skipped_1, "EF")
		self.assertEqual(dom.d, 4)
	
	def test_skip3(self):
		dom = self._test_parse_build(
			"ABCD",
			"""
				Printf("%d", FSkip(4));
				Printf("%d", FSkip(2));
			""",
			verify=False,
			stdout="0-1"
		)

class TestCompatString(unittest.TestCase, utils.UtilsMixin):
	def setup(self):
		pass
	
	def tearDown(self):
		pass
	
	def test_memcpy1(self):
		dom = self._test_parse_build(
			"abcd",
			"""
			uchar bytes[4];
			local uchar local_bytes[4];
			Memcpy(local_bytes, bytes, 4);

			Printf(local_bytes);
			""",
			stdout="abcd"
		)
	
	def test_memcpy2(self):
		dom = self._test_parse_build(
			"abcd",
			"""
			uchar bytes[4];
			local uchar local_bytes[4];
			Memcpy(local_bytes, bytes, 4);

			local uint i;
			for(i = 0; i < 4; i++) {
				local_bytes[3 - i] = local_bytes[i];
			}
			Printf(local_bytes);
			Printf(bytes);
			""",
			stdout="abbaabcd"
		)

if __name__ == "__main__":
	unittest.main()
