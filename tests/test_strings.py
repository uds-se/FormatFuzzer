#!/usr/bin/env python
# encoding: utf-8

import binascii
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


class TestStrings(unittest.TestCase, utils.UtilsMixin):
	def setUp(self):
		pfp.fields.NumberBase.endian = pfp.fields.BIG_ENDIAN
	
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
		with self.assertRaises(pfp.errors.PfpError):
			dom = self._test_parse_build(
				"unterminated string",
				"""
					struct {
						string something;
					} data;
				"""
			)
	
	def test_string_indexing(self):
		dom = self._test_parse_build(
			"abcd\x00",
			"""
				string alpha;
				local char a = alpha[0];
				Printf(a);
			""",
			stdout="a"
		)

		self.assertEqual(dom.alpha[0], ord("a"))
		self.assertEqual(dom.alpha[1], ord("b"))
		self.assertEqual(dom.alpha[2], ord("c"))
		self.assertEqual(dom.alpha[3], ord("d"))

		dom.alpha[2] = ord("C")

		self.assertEqual(dom.alpha[0], ord("a"))
		self.assertEqual(dom.alpha[1], ord("b"))
		self.assertEqual(dom.alpha[2], ord("C"))
		self.assertEqual(dom.alpha[3], ord("d"))

if __name__ == "__main__":
	unittest.main()
