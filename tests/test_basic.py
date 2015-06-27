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

	def test_struct(self):
		dom = self._test_parse_build(
			"abcddcba",
			"""
				typedef struct {
					int some_int;
				} blah;

				blah some_struct;
				blah some_struct2;
			""",
		)
	
	def test_struct_initialization(self):
		dom = self._test_parse_build(
			"",
			"""
				typedef struct {
					char a;
					char b;
					char c;
					char d;
				} blah;

				local blah some_struct = { 'a', 'b', 'c', 'd'};
			"""
		)
	
	def test_union(self):
		dom = self._test_parse_build(
			"abcd",
			"""
				typedef union {
					int some_int;
					struct {
						char a;
						char b;
						char c;
						char d;
					} some_chars;
				} blah;

				blah some_union;
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

class TestControlFlow(unittest.TestCase, utils.UtilsMixin):
	def setUp(self):
		pass

	def tearDown(self):
		pass
	
	def test_if1(self):
		dom = self._test_parse_build(
			"",
			"""
				local int b = 10;
				if(b == 10) {
					Printf("true");
				} else if(b == 11) {
					Printf("false");
				} else {
					Printf("false");
				}
			""",
			stdout="true"
		)

	def test_if2(self):
		dom = self._test_parse_build(
			"",
			"""
				local int b = 10;
				if(b == 11) {
					Printf("false");
				} else if(b == 10) {
					Printf("true");
				} else {
					Printf("false");
				}
			""",
			stdout="true"
		)

	def test_if3(self):
		dom = self._test_parse_build(
			"",
			"""
				local int b = 10;
				if(b == 11) {
					Printf("false");
				} else if(b == 12) {
					Printf("false");
				} else {
					Printf("true");
				}
			""",
			stdout="true"
		)
	
	def test_for1(self):
		dom = self._test_parse_build(
			"",
			"""
				local int j = 0;
				for(local int j = 0; j < 10; j++ ) {
					Printf("a");
				}
			""",
			stdout="a"*10
		)

	def test_for2(self):
		dom = self._test_parse_build(
			"",
			"""
				local int j = 0;
				for(; j < 10; j++ ) {
					Printf("a");
				}
			""",
			stdout="a"*10
		)

	def test_for3(self):
		dom = self._test_parse_build(
			"",
			"""
				local int j = 0;
				for(; j < 10; j++ ) {
					Printf("a");
					break;
				}
			""",
			stdout="a"
		)

	def test_for4(self):
		dom = self._test_parse_build(
			"",
			"""
				local int j = 0;
				for(; j < 10; j++ ) {
					if(j % 2 == 0) {
						continue;
					}
					Printf("a");
				}
			""",
			stdout="aaaaa"
		)

	def test_for5(self):
		dom = self._test_parse_build(
			"",
			"""
				local int j = 0;
				for(;; j++ ) {
					Printf("a");
					if(j == 3) {
						break;
					}
				}
			""",
			stdout="aaaa"
		)
	
	def test_while1(self):
		dom = self._test_parse_build(
			"",
			"""
				local int j = 0;
				while(j < 3) {
					j++;
					Printf("a");
				}
			""",
			stdout="aaa"
		)
	
	def test_while2(self):
		dom = self._test_parse_build(
			"",
			"""
				local int j = 0;
				while(1) {
					Printf("a");
					j++;
					if(j == 3) {
						break;
					}
				}
			""",
			stdout="aaa"
		)
	
	def test_while3(self):
		dom = self._test_parse_build(
			"",
			"""
				local int j = 0;
				while(1) {
					Printf("a");
					j++;
					if(j != 3) {
						continue;
					}
					break;
				}
			""",
			stdout="aaa"
		)

if __name__ == "__main__":
	unittest.main()
