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
        pass

    def tearDown(self):
        pass
    
    def _do_parse(self, field, data):
        field._pfp__parse(StringIO(data.decode("ISO-8859-1")))
    
    def _do_endian_tests(self, field, format):
        field.endian = pfp.fields.BIG_ENDIAN
        self._do_parse(field, struct.pack(">" + format, 1))
        self.assertEqual(field, 1)

        field.endian = pfp.fields.LITTLE_ENDIAN
        self._do_parse(field, struct.pack("<" + format, 1))
        self.assertEqual(field, 1)
    
    def test_char(self):
        field = Char()
        self._do_endian_tests(field, "b")
    
    def test_uchar(self):
        field = UChar()
        self._do_endian_tests(field, "b")
    
    def test_short(self):
        field = Short()
        self._do_endian_tests(field, "h")
    
    def test_ushort(self):
        field = UShort()
        self._do_endian_tests(field, "H")

    def test_int(self):
        field = Int()
        self._do_endian_tests(field, "i")
    
    def test_uint(self):
        field = UInt()
        self._do_endian_tests(field, "I")

    def test_int64(self):
        field = Int64()
        self._do_endian_tests(field, "q")

    def test_int64(self):
        field = UInt64()
        self._do_endian_tests(field, "Q")
    
    def test_const_int64(self):
        dom = self._test_parse_build(
            "",
            """
                const uint64 PNGMAGIC = 0x89504E470D0A1A0AL;
                Printf("%d", PNGMAGIC);
            """,
            stdout="9894494448401390090"
        )
    
if __name__ == "__main__":
    unittest.main()
