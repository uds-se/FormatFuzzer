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

class TestEnums(utils.PfpTestCase):
    def setUp(self):
        pfp.fields.NumberBase.endian = pfp.fields.BIG_ENDIAN
    
    def tearDown(self):
        pass
    
    def test_basic_enum(self):
        dom = self._test_parse_build(
            "\x00\x00\x00\x01",
            """
                enum TEST_ENUM {
                    BLAH1,
                    BLAH2,
                    BLAH3,
                    BLAH4,
                    BLAH5,
                    BLAH6
                } var1;
            """
        )
        self.assertEqual(dom.var1.enum_cls, Int)
        self.assertEqual(dom.var1.enum_name, "BLAH2")
    
    def test_basic_enum2(self):
        dom = self._test_parse_build(
            "\x01",
            """
                enum <uchar> TEST_ENUM {
                    BLAH1,
                    BLAH2,
                    BLAH3,
                    BLAH4,
                    BLAH5,
                    BLAH6
                } var1;

                local uchar blah = BLAH4;
                Printf("%d", blah);
            """,
            stdout="3"
        )
        self.assertEqual(dom.var1.enum_cls, UChar)
        self.assertEqual(dom.var1.enum_name, "BLAH2")
    
    def test_basic_enum_unnamed(self):
        dom = self._test_parse_build(
            "\x01",
            """
                enum <uchar> {
                    BLAH1,
                    BLAH2,
                    BLAH3,
                    BLAH4,
                    BLAH5,
                    BLAH6
                } var1;
            """,
        )
        self.assertEqual(dom.var1.enum_cls, UChar)
        self.assertEqual(dom.var1.enum_name, "BLAH2")
    
    def test_basic_enum_typedef(self):
        dom = self._test_parse_build(
            "\x01",
            """
                typedef enum <uchar> blahs {
                    BLAH1,
                    BLAH2,
                    BLAH3,
                    BLAH4,
                    BLAH5,
                    BLAH6
                } ENUM_TYPE;

                ENUM_TYPE hello;
            """,
        )
        self.assertEqual(dom.hello.enum_cls, UChar)
        self.assertEqual(dom.hello.enum_name, "BLAH2")
        self.assertEqual(dom.hello, 1)
    
    def test_basic_enum_types(self):
        dom = self._test_parse_build(
            "",
            """
                enum <uchar> blahs {
                    BLAH1,
                    BLAH2,
                    BLAH3,
                    BLAH4,
                    BLAH5,
                    BLAH6
                };

                local uchar blah = BLAH6;
                Printf("%d", blah);
            """,
            stdout="5"
        )
    
    def test_enum_name_as_type(self):
        dom = self._test_parse_build(
            "\x01",
            """
                enum <uchar> BLAHS {
                    BLAH1,
                    BLAH2,
                    BLAH3
                };
                BLAHS test;
            """
        )
        self.assertEqual(dom.test, 1)
        self.assertEqual(dom.test.enum_name, "BLAH2")
    
    def test_enum_with_bitfield(self):
        dom = self._test_parse_build(
            "\x31",
            """
                enum <uchar> BLAHS {
                    BLAH1,
                    BLAH2,
                    BLAH3,
                    BLAH4
                };

                BLAHS test1: 4;
                BLAHS test2: 4;
            """
        )
        self.assertEqual(dom.test1, 3)
        self.assertEqual(dom.test1.enum_name, "BLAH4")
        self.assertEqual(dom.test2, 1)
        self.assertEqual(dom.test2.enum_name, "BLAH2")

    def test_enum_with_bitfield_typedef(self):
        dom = self._test_parse_build(
            "\x31",
            """
                typedef enum <uchar> blahs {
                    BLAH1,
                    BLAH2,
                    BLAH3,
                    BLAH4
                } BLAHS;

                BLAHS test1: 4;
                BLAHS test2: 4;
            """
        )
        self.assertEqual(dom.test1, 3)
        self.assertEqual(dom.test1.enum_name, "BLAH4")
        self.assertEqual(dom.test2, 1)
        self.assertEqual(dom.test2.enum_name, "BLAH2")

    def test_enum_with_bitfield_inline(self):
        dom = self._test_parse_build(
            "\x31",
            """
                enum <uchar> {
                    BLAH1,
                    BLAH2,
                    BLAH3,
                    BLAH4
                } test1: 4;

                enum <uchar> {
                    BLAH1,
                    BLAH2,
                    BLAH3,
                    BLAH4
                } test2: 4;
            """
        )
        self.assertEqual(dom.test1, 3)
        self.assertEqual(dom.test1.enum_name, "BLAH4")
        self.assertEqual(dom.test2, 1)
        self.assertEqual(dom.test2.enum_name, "BLAH2")

if __name__ == "__main__":
    unittest.main()
