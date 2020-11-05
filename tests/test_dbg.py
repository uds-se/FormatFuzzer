#!/usr/bin/env python
# encoding: utf-8

import os
import sys
import unittest

try:
    from StringIO import StringIO

# StringIO does not exist in python3
except ImportError as e:
    from io import StringIO

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pfp
import pfp.dbg

import utils


class TestDebug(utils.PfpTestCase):
    def setUp(self):
        """
        Sets the result of this thread.

        Args:
            self: (todo): write your description
        """
        pass

    def tearDown(self):
        """
        Tear down the next callable.

        Args:
            self: (todo): write your description
        """
        pass

    def test_debug_prompt(self):
        """
        Test for debugging.

        Args:
            self: (todo): write your description
        """
        return
        dom = pfp.parse(
            StringIO("aaaabbbbcccchello there\x00\x05abcdf"),
            """
            Int3();
            int a;
            int b;
            int c;
            string greeting;
            unsigned char length;
            char str[length];
            """,
        )


if __name__ == "__main__":
    unittest.main()
