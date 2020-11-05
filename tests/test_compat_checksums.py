#!/usr/bin/env python
# encoding: utf-8

import unittest
import os
import sys
import utils

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestCompat(utils.PfpTestCase):
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

    def test_adler32(self):
        """
        Run test test test test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "test\x00",
            """
                string test;
                Printf("%X", Checksum(CHECKSUM_ADLER32, 0, 1, -1, -1));
            """,
            stdout="750075",
            # Required for CHECKSUM_ADLER32 to be found
            predefines=True,
        )
