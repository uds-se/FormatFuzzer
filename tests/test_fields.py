#!/usr/bin/env python
# encoding: utf-8

import os

try:
    from StringIO import StringIO
# StringIO does not exist in python3
except ImportError as e:
    from io import StringIO
import struct
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pfp
import pfp.errors
from pfp.fields import *
import pfp.utils

import utils


class TestNumericFields(utils.PfpTestCase):
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

    def _do_parse(self, field, data):
        """
        Parse the field.

        Args:
            self: (todo): write your description
            field: (todo): write your description
            data: (todo): write your description
        """
        field._pfp__parse(StringIO(data.decode("ISO-8859-1")))

    def _do_endian_tests(self, field, format):
        """
        Endian - endian struct.

        Args:
            self: (todo): write your description
            field: (todo): write your description
            format: (str): write your description
        """
        field.endian = pfp.fields.BIG_ENDIAN
        self._do_parse(field, struct.pack(">" + format, 1))
        self.assertEqual(field, 1)

        field.endian = pfp.fields.LITTLE_ENDIAN
        self._do_parse(field, struct.pack("<" + format, 1))
        self.assertEqual(field, 1)

    def test_char(self):
        """
        U move the character.

        Args:
            self: (todo): write your description
        """
        field = Char()
        self._do_endian_tests(field, "b")

    def test_uchar(self):
        """
        Perform the sanar.

        Args:
            self: (todo): write your description
        """
        field = UChar()
        self._do_endian_tests(field, "b")

    def test_short(self):
        """
        !

        Args:
            self: (todo): write your description
        """
        field = Short()
        self._do_endian_tests(field, "h")

    def test_ushort(self):
        """
        !

        Args:
            self: (todo): write your description
        """
        field = UShort()
        self._do_endian_tests(field, "H")

    def test_int(self):
        """
        Test for the test.

        Args:
            self: (todo): write your description
        """
        field = Int()
        self._do_endian_tests(field, "i")

    def test_uint(self):
        """
        !

        Args:
            self: (todo): write your description
        """
        field = UInt()
        self._do_endian_tests(field, "I")

    def test_int64(self):
        """
        !

        Args:
            self: (todo): write your description
        """
        field = Int64()
        self._do_endian_tests(field, "q")

    def test_int64(self):
        """
        Test for 64 bit64 is 8 bits.

        Args:
            self: (todo): write your description
        """
        field = UInt64()
        self._do_endian_tests(field, "Q")

    def test_const_int64(self):
        """
        The test test test test test test timestamp.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                const uint64 PNGMAGIC = 0x89504E470D0A1A0AL;
                Printf("%d", PNGMAGIC);
            """,
            stdout="9894494448401390090",
        )


if __name__ == "__main__":
    unittest.main()
