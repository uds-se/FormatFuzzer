#!/usr/bin/env python
# encoding: utf-8

import six
import sys
import pfp
import pfp.utils

class UtilsMixin(object):
	def _test_parse_build(self, data, template, stdout=None, debug=False, predefines=False):
		if stdout is not None:
			fake_stdout = sys.stdout = six.StringIO()

		dom = pfp.parse(six.StringIO(data), template, debug=debug, predefines=predefines)

		if stdout is not None:
			sys.stdout = sys.__stdout__
			output = fake_stdout.getvalue()
			self.assertEqual(output, stdout)

		self.assertEqual(dom._pfp__build(), pfp.utils.binary(data))

		return dom
