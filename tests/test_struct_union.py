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

class TestStructUnion(unittest.TestCase, utils.UtilsMixin):
	def setUp(self):
		pass

	def tearDown(self):
		pass
	
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
	
	def test_struct_decl_with_struct_keyword(self):
		dom = self._test_parse_build(
			"ABCD",
			"""
				typedef struct {
					char a;
					char b;
					char c;
					char d;
				} BLAH;

				struct BLAH decldStruct;
			"""
		)

		self.assertEqual(dom.decldStruct.a, ord("A"))
		self.assertEqual(dom.decldStruct.b, ord("B"))
		self.assertEqual(dom.decldStruct.c, ord("C"))
		self.assertEqual(dom.decldStruct.d, ord("D"))
	
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
	
	def test_union_complex(self):
		dom = self._test_parse_build(
			"\x00abcd",
			"""
				typedef struct {
					uchar a;
					uchar b;
					uchar c;
					uchar d;
				} TEST;

				struct {
					uchar blah;
					union {
						TEST chars;
						uchar raw[sizeof(chars)];
					} onion;
				} test;
			"""
		)
		self.assertEqual(dom.test.onion.raw, "abcd")
		self.assertEqual(dom.test.onion.chars.a, ord("a"))
		self.assertEqual(dom.test.onion.chars.b, ord("b"))
		self.assertEqual(dom.test.onion.chars.c, ord("c"))
		self.assertEqual(dom.test.onion.chars.d, ord("d"))
	
	def test_union_offset1(self):
		dom = self._test_parse_build(
			"abcd",
			"""
				struct {
					char a;
					char b;
					union {
						char c;
						uchar uc;
					} union_test;
					char d;
				} test;
			"""
		)
		self.assertEqual(dom.test.union_test._pfp__offset, 2)
	
	def test_union_offset2(self):
		dom = self._test_parse_build(
			"abcd",
			"""
				typedef union {
					char c;
					uchar uc;
				} CHAR_UNION;

				struct {
					char a;
					char b;
					CHAR_UNION union_test;
					char d;
				} test;
			"""
		)
		self.assertEqual(dom.test.union_test._pfp__offset, 2)

if __name__ == "__main__":
	unittest.main()
