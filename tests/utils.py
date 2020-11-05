#!/usr/bin/env python
# encoding: utf-8

import six
import sys
import pfp
import pfp.utils
import unittest
import contextlib


class PfpTestMeta(type):
    def __init__(cls, name, bases, dict_):
        """
        Initialize a new class.

        Args:
            cls: (todo): write your description
            name: (str): write your description
            bases: (float): write your description
            dict_: (todo): write your description
        """
        for attr_name, attr_val in six.iteritems(dict_):
            if not attr_name.startswith("test_"):
                continue

            if not hasattr(attr_val, "__call__"):
                continue

            new_func_name = attr_name + "_with_string_data"
            new_func = cls._create_string_data_test(attr_val)
            setattr(cls, new_func_name, new_func)

        return super(PfpTestMeta, cls).__init__(name, bases, dict_)

    def _create_string_data_test(cls, method):
        """Wrap the test method in a new function that causes _test_parse_build
        to use _stream=False as the default in order to test string data
        as input to pfp.parse
        """

        @contextlib.wraps(method)
        def new_method(self, *args, **kwargs):
            """
            Returns a new method that will be called method.

            Args:
                self: (todo): write your description
            """
            self._test_parse_build = self._test_parse_build_with_string
            try:
                res = method(self, *args, **kwargs)
            finally:
                self._test_parse_build = cls._test_parse_build_orig

        return new_method


@six.add_metaclass(PfpTestMeta)
class PfpTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        """
        Initialize this component.

        Args:
            self: (todo): write your description
        """
        # create two versions of each test

        unittest.TestCase.__init__(self, *args, **kwargs)

    def _test_parse_build_with_string(self, *args, **kwargs):
        """
        Parse test string and return the test string.

        Args:
            self: (todo): write your description
        """
        kwargs["_stream"] = False
        return self._test_parse_build_orig(*args, **kwargs)

    def _test_parse_build(
        self,
        data,
        template,
        stdout=None,
        debug=False,
        predefines=False,
        _stream=True,
        printf=True,
    ):
        """
        Parse test data to produce a dom. dom.

        Args:
            self: (todo): write your description
            data: (str): write your description
            template: (str): write your description
            stdout: (todo): write your description
            debug: (bool): write your description
            predefines: (todo): write your description
            _stream: (todo): write your description
            printf: (str): write your description
        """
        if stdout is not None:
            fake_stdout = sys.stdout = six.StringIO()

        if _stream:
            data = six.StringIO(data)

        # defaults to LittleEndian
        template = "LittleEndian();" + template

        dom = pfp.parse(
            data, template, debug=debug, predefines=predefines, printf=printf
        )

        if stdout is not None:
            sys.stdout = sys.__stdout__
            output = fake_stdout.getvalue()
            self.assertEqual(output, stdout)

        return dom

    _test_parse_build_orig = _test_parse_build
