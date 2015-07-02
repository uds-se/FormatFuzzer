#!/usr/bin/env python
# encoding: utf-8

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


class TestMetadata(unittest.TestCase, utils.UtilsMixin):
	def setUp(self):
		pass
	
	def tearDown(self):
		pass
	
#< format=hex|decimal|octal|binary,
#     fgcolor=<color>,
#     bgcolor=<color>,
#     comment="<string>"|<function_name>,
#     name="<string>"|<function_name>,
#     open=true|false|suppress,
#     hidden=true|false,
#     read=<function_name>,
#     write=<function_name>
#     size=<number>|<function_name> >
	def test_metadata_watch_interpd(self):
		dom = self._test_parse_build(
			"\x05\x07",
			"""
				int PlusTwo(int val) {
					return val + 2;
				}

				uchar hello;
				uchar blah<watch=hello,update=PlusTwo>;
			"""
		)
		self.assertEqual(dom.hello, 5)
		self.assertEqual(dom.blah, 7)

		dom.hello = 20

		self.assertEqual(dom.hello, 20)
		self.assertEqual(dom.blah, 22)

if __name__ == "__main__":
	unittest.main()
