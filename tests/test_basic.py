#!/usr/bin/env python
# encoding: utf-8

import os
import StringIO
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pfp

class TestBasic(unittest.TestCase):
	def setUp(self):
		pass

	def tearDown(self):
		pass
	
	def _test_parse_build(self, data, template):
		dom = pfp.parse(StringIO.StringIO(data), template)
		self.assertEqual(dom._pfp__build(), data)
		return dom
	
	def test_single_decl_parse(self):
		dom = self._test_parse_build(
			"\x41",
			"""
				char a;
			"""
		)

	def test_basic_parse(self):
		dom = self._test_parse_build(
			"\x00\x01\x02\x03",
			"""
				struct DATA {
					char a;
					char b;
					char c;
					char d;
				} data;
			"""
		)
	
	def test_nested_basic_parse(self):
		dom = self._test_parse_build(
			"\x00\x01\x02\x03",
			"""
				struct DATA {
					char a;
					char b;

					struct {
						char a;
						char b;
					} nested;
				} data;
			"""
		)
	
	def test_typedef_basic_parse(self):
		dom = self._test_parse_build(
			"\xff\x00\x00\xff",
			"""
				typedef unsigned short BLAH;
				BLAH a;
				short b;
			"""
		)
		self.assertTrue(dom.a, 0xff00)
		self.assertEqual(dom.b, 0xff)
	
	def test_local(self):
		dom = self._test_parse_build(
			"",
			"""
				local int i;
			"""
		)
	
	def test_local_assignment_int(self):
		dom = self._test_parse_build(
			"",
			"""
				local int i = 10;
			"""
		)

	def test_local_assignment_char(self):
		dom = self._test_parse_build(
			"",
			"""
				local char i = 'A';
			"""
		)

	def test_local_assignment_float(self):
		dom = self._test_parse_build(
			"",
			"""
				local float i = 0.5f;
			"""
		)

	def test_local_assignment_double(self):
		dom = self._test_parse_build(
			"",
			"""
				local double i = 0.5;
			"""
		)

	def test_local_assignment_long(self):
		dom = self._test_parse_build(
			"",
			"""
				local long i = 555l;
			"""
		)

	def test_local_assignment_string(self):
		dom = self._test_parse_build(
			"",
			"""
				local string i = "hello";
			"""
		)

	def test_local_binary_arithmetic(self):
		dom = self._test_parse_build(
			"",
			"""
				local int i = 0;
				local int j = 10;
				local int k;
				k = i + j;
				k = i - j;
				k = i * j;
				k = i / j;
				k = i % j;
				k = i ^ j;
				k = i & j;
				k = i | j;
			"""
		)

	def test_unary_arithmetic(self):
		dom = self._test_parse_build(
			"",
			"""
				local int i = 0;
				i++;
				i--;
			"""
		)

if __name__ == "__main__":
	unittest.main()
