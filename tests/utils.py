#!/usr/bin/env python
# encoding: utf-8

import sys
try:
	from StringIO import StringIO

# StringIO does not exist in python3
except ImportError as e:
	from io import StringIO

import pfp
import pfp.six as six

class UtilsMixin(object):
	def _test_parse_build(self, data, template, stdout=None):
		if stdout is not None:
			fake_stdout = sys.stdout = StringIO()

		dom = pfp.parse(StringIO(data), template)

		if stdout is not None:
			sys.stdout = sys.__stdout__
			output = fake_stdout.getvalue()
			self.assertEqual(output, stdout)

		self.assertEqual(dom._pfp__build(), six.binary(data))

		return dom
