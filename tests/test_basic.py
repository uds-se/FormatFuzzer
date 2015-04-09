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

	def test_basic_parse(self):
		data = "\x00\x01\x02\x03"
		template = """
			struct DATA {
				char a;
				char b;
				char c;
				char d;
			} data;
		"""
		stream = StringIO.StringIO(data)
		dom = pfp.parse(data, template)

if __name__ == "__main__":
	unittest.main()
