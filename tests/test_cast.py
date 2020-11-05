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


class TestArrays(utils.PfpTestCase):
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

    def test_cast_basic(self):
        """
        Cast test test test to test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                local int a = 0x61;
                local uchar b = (char)a;
                Printf(b);
            """,
            stdout="a",
        )

    def test_cast_from_dex(self):
        """
        Cast test test test to test test test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                local ubyte cur = 7;
                local uint test1 = (uint)(10);
                local uint test2 = (uint)((cur & 0x7f) << 7);
                Printf("%u,%u", test1, test2);
            """,
            stdout="10,896",
        )


if __name__ == "__main__":
    unittest.main()
