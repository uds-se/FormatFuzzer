#!/usr/bin/env python
# encoding: utf-8

import os
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

	def test_basic_parse_with_comments(self):
		dom = self._test_parse_build(
			"\x00\x01\x02\x03",
			"""
				// This should be removed
				struct DATA {
					/* so should this */
					char a; // yo yoyo
					char b;
					char c;
					char d;
				} data; /*haha*/
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
				BigEndian();

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
	
	def test_local_field_precedence1(self):
		dom = self._test_parse_build(
			"\x01",
			"""
				local int size = 0;
				struct {
					uchar size;
					Printf("%d", size);
				} test;
			""",
			stdout="1"
		)

	def test_local_field_precedence2(self):
		dom = self._test_parse_build(
			"\x01",
			"""
				uchar size;

				struct {
					local int size = 0;
					Printf("%d", size);
				} test;
			""",
			stdout="0"
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
				k = i || j;
				k = i && j;
				k = i << j;
				k = i >> j;
			"""
		)
	
	def test_add(self):
		dom = self._test_parse_build(
			"ab",
			"""
				char a;
				char b;
				local int i;
				local int j = 3;
				i = FTell() + j;
				Printf("%d", i);
			""",
			stdout="5"
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
	
	def test_unary_sizeof_basic(self):
		dom = self._test_parse_build(
			"abcd",
			"""
				int some_int;
				Printf("%d", sizeof(some_int));
			""",
			stdout="4"
		)
	
	def test_unary_sizeof_struct(self):
		dom = self._test_parse_build(
			"abcde",
			"""
				struct {
					int a;
					char b;
				} blah;
				Printf("%d", sizeof(blah));
			""",
			stdout="5"
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

class TestByRef(unittest.TestCase, utils.UtilsMixin):
	def setUp(self):
		pass

	def tearDown(self):
		pass
	
	def test_non_byref_native_type(self):
		dom = self._test_parse_build(
			"",
			"""
				void test_func(local int value) {
					value = 20;
				}
				local int blah = 10;
				test_func(blah);
				Printf("%d", blah);
			""",
			stdout="10"
		)
	
	def test_non_byref_complex(self):
		dom = self._test_parse_build(
			"abcd",
			"""
				typedef struct {
					char a;
					char b;
					char c;
					char d;
				} some_struct_t;

				void test_func(some_struct_t &var) {
					Printf("a: %d", var.a);
					Printf("b: %d", var.b);
					Printf("c: %d", var.c);
					Printf("d: %d", var.d);
				}

				some_struct_t blah;
				test_func(blah);
			""",
			stdout="a: 97b: 98c: 99d: 100"
		)

if __name__ == "__main__":
	unittest.main()
