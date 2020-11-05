#!/usr/bin/env python
# encoding: utf-8

import os
import six
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pfp
import pfp.fields
import pfp.interp
import pfp.utils

import utils


class TestCompatStrings(utils.PfpTestCase):
    def setUp(self):
        """
        Set the re - of - fields fields.

        Args:
            self: (todo): write your description
        """
        pfp.fields.NumberBase.endian = pfp.fields.BIG_ENDIAN

    def tearDown(self):
        """
        Tear down the next callable.

        Args:
            self: (todo): write your description
        """
        pass

    def test_strlen(self):
        """
        Returns the test test test test test test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                Printf("%d.%d.%d", Strlen("HELLO"), Strlen("abcd"), Strlen("abc"));
            """,
            stdout="5.4.3",
        )

    def test_substr(self):
        """
        Run test test test test files.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                Printf("%s\\n", SubStr("Hello there", 0, 5));

                string local someString = "abcdefg";
                Printf("%s", SubStr(someString, 3));
            """,
            stdout="Hello\ndefg",
        )


if __name__ == "__main__":
    unittest.main()
