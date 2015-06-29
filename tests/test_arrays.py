#!/usr/bin/env python
# encoding: utf-8

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pfp
import pfp.errors
from pfp.fields import *
import pfp.utils

import utils


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

	def test_array_initialization(self):
		# was having problems with array decls _always_ parsing the
		# input stream
		dom = self._test_parse_build(
			"",
			"""
				local uchar blah[2] = { 'a', 'b' };
				Printf("%s", blah);
			""",
		)
	
	def test_struct_array_decl(self):
		dom = self._test_parse_build(
			"abcd",
			"""
				struct {
					uchar blah;
				} structs[4];
			""",
		)

if __name__ == "__main__":
	unittest.main()
