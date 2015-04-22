#!/usr/bin/env python
# encoding: utf-8

import os
import StringIO
import struct
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pfp
import pfp.errors
from pfp.fields import *

class TestNumericFields(unittest.TestCase):
	def setUp(self):
		pass

	def tearDown(self):
		pass
	
	def _do_parse(self, field, data):
		field._pfp__parse(StringIO.StringIO(data))
	
	def _do_endian_tests(self, field, format):
		field.endian = pfp.fields.BIG_ENDIAN
		self._do_parse(field, struct.pack(">" + format, 1))
		self.assertEqual(field, 1)

		field.endian = pfp.fields.LITTLE_ENDIAN
		self._do_parse(field, struct.pack("<" + format, 1))
		self.assertEquals(field, 1)
	
	def test_default_endian(self):
		self.assertEquals(pfp.fields.NumberBase.endian, pfp.fields.BIG_ENDIAN)
	
	def test_char(self):
		field = Char()
		self._do_endian_tests(field, "b")
	
	def test_uchar(self):
		field = Char()
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

class TestStrings(unittest.TestCase):
	def setUp(self):
		pass
	
	def tearDown(self):
		pass

	def _test_parse_build(self, data, template):
		dom = pfp.parse(StringIO.StringIO(data), template)
		self.assertEqual(dom._pfp__build(), data)
		return dom
	
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
		self.assertEqual(dom.greetings.hello, "hello there")
		self.assertEqual(dom.greetings.goodbye, "good byte")
	
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
		self.assertEqual(dom.greetings.hello, "hello there")
		self.assertEqual(dom.greetings.goodbye, "good byte")
	
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

class TestArrays(unittest.TestCase):
	def setUp(self):
		pass

	def tearDown(self):
		pass
	
	def _do_parse(self, field, data):
		field._pfp__parse(StringIO.StringIO(data))
	
	def _do_endian_tests(self, field, format):
		field.endian = pfp.fields.BIG_ENDIAN
		self._do_parse(field, struct.pack(">" + format, 1))
		self.assertEqual(field, 1)

		field.endian = pfp.fields.LITTLE_ENDIAN
		self._do_parse(field, struct.pack("<" + format, 1))
		self.assertEquals(field, 1)

	def _test_parse_build(self, data, template):
		dom = pfp.parse(StringIO.StringIO(data), template)
		self.assertEqual(dom._pfp__build(), data)
		return dom
	
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

if __name__ == "__main__":
	unittest.main()
