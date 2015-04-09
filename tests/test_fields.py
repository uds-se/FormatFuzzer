#!/usr/bin/env python
# encoding: utf-8

import os
import StringIO
import struct
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pfp
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

class TestStructField(unittest.TestCase):
	def setUp(self):
		pass
	
	def tearDown(self):
		pass
	
	def test_struct_subfields(self):
		data = "abc"
	
if __name__ == "__main__":
	unittest.main()
