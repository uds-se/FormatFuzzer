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

    def test_basic_enum(self):
        """
        Evaluate a test variable.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "\x00\x00\x00\x01",
            """
                BigEndian();
                enum TEST_ENUM {
                    BLAH1,
                    BLAH2,
                    BLAH3,
                    BLAH4,
                    BLAH5,
                    BLAH6
                } var1;
            """,
        )
        self.assertEqual(dom.var1.enum_cls, Int)
        self.assertEqual(dom.var1.enum_name, "BLAH2")

    def test_basic_enum2(self):
        """
        Equal of enum enum.

        Args:
            self: (todo): write your description
        """
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
            stdout="3",
        )
        self.assertEqual(dom.var1.enum_cls, UChar)
        self.assertEqual(dom.var1.enum_name, "BLAH2")

    def test_basic_enum_unnamed(self):
        """
        Test that is a type.

        Args:
            self: (todo): write your description
        """
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
        """
        Test for enum enum enum.

        Args:
            self: (todo): write your description
        """
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
        """
        Check that the test test types.

        Args:
            self: (todo): write your description
        """
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
            stdout="5",
        )

    def test_enum_name_as_type(self):
        """
        Test for enum name.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "\x01",
            """
                enum <uchar> BLAHS {
                    BLAH1,
                    BLAH2,
                    BLAH3
                };
                BLAHS test;
            """,
        )
        self.assertEqual(dom.test, 1)
        self.assertEqual(dom.test.enum_name, "BLAH2")

    def test_enum_word_type(self):
        """
        Test for enum type.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                enum <WORD> tagID {
                    M_TAG0, // should be 0
                    M_TAG1 = 0xff01,
                    M_TAG2,
                    M_TAG3,
                };
            """,
        )
        self.assertEqual(dom.M_TAG0, 0)
        self.assertEqual(dom.M_TAG1, 0xff01)
        self.assertEqual(dom.M_TAG2, 0xff02)
        self.assertEqual(dom.M_TAG3, 0xff03)

        self.assertTrue(isinstance(dom.M_TAG0, UShort))
        self.assertTrue(isinstance(dom.M_TAG1, UShort))
        self.assertTrue(isinstance(dom.M_TAG2, UShort))
        self.assertTrue(isinstance(dom.M_TAG3, UShort))

    def test_enum_with_bitfield(self):
        """
        Parse the testfield.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "\x31",
            """
                BigEndian();
                enum <uchar> BLAHS {
                    BLAH1,
                    BLAH2,
                    BLAH3,
                    BLAH4
                };

                BLAHS test1: 4;
                BLAHS test2: 4;
            """,
        )
        self.assertEqual(dom.test1, 3)
        self.assertEqual(dom.test1.enum_name, "BLAH4")
        self.assertEqual(dom.test2, 1)
        self.assertEqual(dom.test2.enum_name, "BLAH2")

    def test_enum_with_bitfield_typedef(self):
        """
        Test for enum type to make it is_ty.

        Args:
            self: (todo): write your description
        """
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
            """,
        )
        self.assertEqual(dom.test1, 3)
        self.assertEqual(dom.test1.enum_name, "BLAH4")
        self.assertEqual(dom.test2, 1)
        self.assertEqual(dom.test2.enum_name, "BLAH2")

    def test_enum_with_bitfield_inline(self):
        """
        Test for enum enum enum in - style.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "\x31",
            """
                BigEndian();
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
            """,
        )
        self.assertEqual(dom.test1, 3)
        self.assertEqual(dom.test1.enum_name, "BLAH4")
        self.assertEqual(dom.test2, 1)
        self.assertEqual(dom.test2.enum_name, "BLAH2")

    def test_enum_compared_to_enum(self):
        """
        Convert enum enum enum to enum

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "\x00\x00\x00\x01",
            """
                BigEndian();
                enum <uchar> TEST_ENUM {
                    BLAH1,
                };

                do {
                    TEST_ENUM test = BLAH1;
                } while (test == BLAH1);
            """,
        )
        self.assertEqual(len(dom.test), 4)


if __name__ == "__main__":
    unittest.main()
