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

class TestStrings(unittest.TestCase, utils.UtilsMixin):
	def setUp(self):
		pass
	
	def tearDown(self):
		pass
	
	def test_basic_string(self):
		dom = self._test_parse_build(
			"hello there\x00good byte\x00",
			"""
				struct {
					string hello;
					string goodbye;
				} greetings;
			"""
		)
		self.assertEqual(dom.greetings.hello, pfp.utils.binary("hello there"))
		self.assertEqual(dom.greetings.goodbye, pfp.utils.binary("good byte"))
	
	def test_basic_wstring(self):
		dom = self._test_parse_build(
			"h\x00e\x00l\x00l\x00o\x00 \x00t\x00h\x00e\x00r\x00e\x00\x00\x00g\x00o\x00o\x00d\x00 \x00b\x00y\x00t\x00e\x00\x00\x00",
			"""
				struct {
					wstring hello;
					wstring goodbye;
				} greetings;
			"""
		)
		self.assertEqual(dom.greetings.hello, pfp.utils.binary("hello there"))
		self.assertEqual(dom.greetings.goodbye, pfp.utils.binary("good byte"))
	
	def test_unterminated_string(self):
		with self.assertRaises(pfp.errors.PrematureEOF):
			dom = self._test_parse_build(
				"unterminated string",
				"""
					struct {
						string something;
					} data;
				"""
			)

class TestArrays(unittest.TestCase, utils.UtilsMixin):
	def setUp(self):
		pass

	def tearDown(self):
		pass
	
	def _do_parse(self, field, data):
		field._pfp__parse(StringIO(data))
	
	def _do_endian_tests(self, field, format):
		field.endian = pfp.fields.BIG_ENDIAN
		self._do_parse(field, struct.pack(">" + format, 1))
		self.assertEqual(field, 1)

		field.endian = pfp.fields.LITTLE_ENDIAN
		self._do_parse(field, struct.pack("<" + format, 1))
		self.assertEqual(field, 1)

	def test_char_array(self):
		dom = self._test_parse_build(
			"AABBCC",
			"""
				char blah[6];
			"""
		)
		self.assertEqual(dom.blah[0], ord("A"))
		self.assertEqual(dom.blah[1], ord("A"))
		self.assertEqual(dom.blah[2], ord("B"))
		self.assertEqual(dom.blah[3], ord("B"))
		self.assertEqual(dom.blah[4], ord("C"))
		self.assertEqual(dom.blah[5], ord("C"))

		with self.assertRaises(IndexError):
			dom.blah[6]

		with self.assertRaises(TypeError):
			dom.blah["hello"]

		dom.blah[5] = 10
		self.assertEqual(dom.blah[5], 10)
	
	def test_char_array_string_compare(self):
		dom = self._test_parse_build(
			"AABBCC",
			"""
				char blah[6];
				if(blah == "AABBCC") {
					Printf("true");
				}
			""",
		)

	def test_implicit_array_basic(self):
		dom = self._test_parse_build(
			"ABCD",
			"""
				while(!FEof()) {
					char chars;
				}
			"""
		)
		self.assertEqual(len(dom.chars), 4)
	
	def test_implicit_array_complex(self):
		dom = self._test_parse_build(
			"\x01A\x02B\x03C",
			"""
				typedef struct {
					uchar some_val;
					char some_char;
				} some_struct;

				local int i = 0;
				for(i = 0; i < 3; i++) {
					some_struct structs;
				}
			""",
		)
		self.assertEqual(len(dom.structs), 3)
		self.assertEqual(dom.structs[0].some_val, 0x01)
		self.assertEqual(dom.structs[1].some_val, 0x02)
		self.assertEqual(dom.structs[2].some_val, 0x03)
		self.assertEqual(dom.structs[0].some_char, 0x41)
		self.assertEqual(dom.structs[1].some_char, 0x42)
		self.assertEqual(dom.structs[2].some_char, 0x43)
	
	def test_array_ref(self):
		dom = self._test_parse_build(
			"abcd",
			"""
				char bytes[4];
				Printf("%02x", bytes[0]);
			""",
			stdout="61"
		)

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
					uchar test : 16;
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

if __name__ == "__main__":
	unittest.main()
