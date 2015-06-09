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

class TestBasic(unittest.TestCase, utils.UtilsMixin):
	def setUp(self):
		pass

	def tearDown(self):
		pass
	
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
		self.assertEqual(dom.a, 0xff00)
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
				~i;
				!i;
			"""
		)
	
	def test_comparisons(self):
		dom = self._test_parse_build(
			"",
			"""
				local int i;
				i > 10;
				i >= 10;
				i < 10;
				i <= 10;
				i != 10;
				i == 10;
			"""
		)
	
	# is this even what you call this?
	def test_binary_assignment(self):
		dom = self._test_parse_build(
			"",
			"""
				local int i;
				i += 10;
				i -= 10;
				i *= 10;
				i /= 10;
				i %= 10;
				i ^= 10;
				i &= 10;
				i <<= 10;
				i >>= 10;
			"""
		)
	
	def test_function(self):
		dom = self._test_parse_build(
			"",
			"""
				void func(int a, int b) {
					local int c = a + b;
				}

				func(10, 20);
			"""
		)
	
	def test_builtin(self):
		dom = self._test_parse_build(
			"",
			"""
				Printf("hello there");
				Printf("%d", 10);
			""",
			stdout="hello there10"
		)
	
	def test_custom_func(self):
		dom = self._test_parse_build(
			"",
			"""
				int add(int n1, int n2) {
					return n1 + n2;
				}

				Printf("%d", add(5, 8));
			""",
			stdout="13"
		)
	
	def test_custom_func2(self):
		dom = self._test_parse_build(
			"",
			"""
				string prepend(string orig) {
					return "blah: " + orig;
				}

				Printf(prepend("hello"));
			""",
			stdout="blah: hello"
		)
	
	def test_native_func(self):
		func_called = False
		def func(params, ctxt, scope, stream, coord):
			func_called = True
			return 555

		interp = pfp.interp.PfpInterp()
		interp.add_native(name="func", func=func, ret=pfp.fields.Int)

		dom = self._test_parse_build(
			"",
			"""
			Printf("%d", func());
			""",
			stdout="555"
		)

if __name__ == "__main__":
	unittest.main()
