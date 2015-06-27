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

	def test_switch(self):
		dom = self._test_parse_build(
			"\x00\x00\x00\x01\x00\x00\x00\x02",
			"""
				local int a = 5;
				switch(a) {
					case 0:
						Printf("false");
						Printf("false");
						Printf("false");
						break;
					case 5:
						int case_5;
					default:
						int case_default;
						break;
				};
			""",
		)
		self.assertEqual(dom.case_5, 1)
		self.assertEqual(dom.case_default, 2)

if __name__ == "__main__":
	unittest.main()
