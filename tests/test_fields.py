#!/usr/bin/env python
# encoding: utf-8

import os
try:
	from StringIO import StringIO
# StringIO does not exist in python3
except ImportError as e:
	from io import StringIO
import struct
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pfp
import pfp.errors
from pfp.fields import *
import pfp.utils

import utils

class TestNumericFields(unittest.TestCase, utils.UtilsMixin):
	def setUp(self):
		pass

	def tearDown(self):
		pass
	
	def _do_parse(self, field, data):
		field._pfp__parse(StringIO(data.decode("ISO-8859-1")))
	
	def _do_endian_tests(self, field, format):
		field.endian = pfp.fields.BIG_ENDIAN
		self._do_parse(field, struct.pack(">" + format, 1))
		self.assertEqual(field, 1)

		field.endian = pfp.fields.LITTLE_ENDIAN
		self._do_parse(field, struct.pack("<" + format, 1))
		self.assertEqual(field, 1)
	
	def test_char(self):
		field = Char()
		self._do_endian_tests(field, "b")
	
	def test_uchar(self):
		field = UChar()
		self._do_endian_tests(field, "b")
	
	def test_short(self):
		field = Short()
		self._do_endian_tests(field, "h")
	
	def test_ushort(self):
		field = UShort()
		self._do_endian_tests(field, "H")

	def test_int(self):
		field = Int()
		self._do_endian_tests(field, "i")
	
	def test_uint(self):
		field = UInt()
		self._do_endian_tests(field, "I")

	def test_int64(self):
		field = Int64()
		self._do_endian_tests(field, "q")

	def test_int64(self):
		field = UInt64()
		self._do_endian_tests(field, "Q")
	
	def test_const_int64(self):
		dom = self._test_parse_build(
			"",
			"""
				const uint64 PNGMAGIC = 0x89504E470D0A1A0AL;
				Printf("%d", PNGMAGIC);
			""",
			stdout="9894494448401390090"
		)

class TestStrings(unittest.TestCase, utils.UtilsMixin):
	def setUp(self):
		pass
	
	def tearDown(self):
		pass
	
class TestBitFields(unittest.TestCase, utils.UtilsMixin):
	def setUp(self):
		pass

	def tearDown(self):
		pass
	
	def test_bitfield_basic(self):
		dom = self._test_parse_build(
			"\xab",
			"""
				struct {
					uchar test:16;
				} blah;
			"""
		)
	
	def test_bitfield_basic_big_endian(self):
		b = lambda x: chr(int(x,2))

		dom = self._test_parse_build(
			b("10011011") + b("10011111") + b("10000001"),
			"""
				BigEndian();
				struct {
					uchar test : 4;
					uchar test1 : 2;
					uchar test2 : 2;
					ushort test3 : 16;
				} blah;
			"""
		)
		self.assertEqual(dom.blah.test, int("1001",2))
		self.assertEqual(dom.blah.test1, int("10", 2))
		self.assertEqual(dom.blah.test2, int("11", 2))
		self.assertEqual(dom.blah.test3, int("1001111110000001",2))
	
	def test_bitfield_basic_little_endian(self):
		b = lambda x: chr(int(x,2))

		dom = self._test_parse_build(
			b("10011011") + b("10011111") + b("10000001"),
			"""
				LittleEndian();
				struct {
					uchar test : 4;
					uchar test1 : 2;
					uchar test2 : 2;
					ushort test3 : 16;
				} blah;
			"""
		)
		self.assertEqual(dom.blah.test, int("1001", 2))
		self.assertEqual(dom.blah.test1, int("10", 2))
		self.assertEqual(dom.blah.test2, int("11", 2))
		self.assertEqual(dom.blah.test3, int("1000000110011111",2))
	
	def test_bitfield_basic_padded_little_endian(self):
		b = lambda x: chr(int(x,2))
		
		dom = self._test_parse_build(
			b("11100000") + b("00000000") + b("10000000"),
			"""
				LittleEndian();
				BitfieldEnablePadding();
				struct {
					uchar test : 3;
					ushort big;
				} blah;
			""",
			predefines=False
		)
		self.assertEqual(dom.blah.test, int("111", 2))
		self.assertEqual(dom.blah.big, int("1000000000000000", 2))

	def test_bitfield_basic_unpadded_little_endian(self):
		b = lambda x: chr(int(x,2))
		
		dom = self._test_parse_build(
			b("11110000") + b("00000000") + b("00000000"),
			"""
				LittleEndian();
				BitfieldDisablePadding();
				struct {
					uchar test : 3;
					ushort big;
				} blah;
			""",
			predefines=False
		)
		self.assertEqual(dom.blah.test, int("111", 2))
		self.assertEqual(dom.blah.big, int("10000000", 2))

	def test_bitfield_basic_unpadded_big_endian(self):
		b = lambda x: chr(int(x,2))
		
		dom = self._test_parse_build(
			b("11110000") + b("00000000") + b("00000000"),
			"""
				BigEndian();
				BitfieldDisablePadding();
				struct {
					uchar test : 3;
					ushort big;
				} blah;
			""",
			predefines=False
		)
		self.assertEqual(dom.blah.test, int("111", 2))
		self.assertEqual(dom.blah.big, int("1000000000000000", 2))
	
	def test_bitfield_in_if(self):
		dom = self._test_parse_build(
			"\xf0",
			"""
				LittleEndian();
				struct {
					if(1) {
						int bitfield_1:4;
						int bitfield_2:4;
					}
				} blah;
			"""
		)
	
	def test_bitfield_again(self):
		dom = self._test_parse_build(
			"\x00AB",
			"""
			struct QuanTable {
				uchar Pq : 4;
				uchar Tq : 4;
				if (Pq == 0)
					byte qTable[2];
			} qtable;
			"""
		)

if __name__ == "__main__":
	unittest.main()
