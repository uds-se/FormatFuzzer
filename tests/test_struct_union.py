#!/usr/bin/env python
# encoding: utf-8

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pfp
import pfp.fields
import pfp.interp
import pfp.utils

import utils

class TestStructUnion(utils.PfpTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    def test_struct(self):
        dom = self._test_parse_build(
            "abcddcba",
            """
                typedef struct {
                    int some_int;
                } blah;

                blah some_struct;
                blah some_struct2;
            """,
        )
    
    def test_struct_with_parameters(self):
        dom = self._test_parse_build(
            "aabbb",
            """
                typedef struct (int a, int b) {
                    char chars1[a];
                    char chars2[b];
                } blah;

                blah test(2, 3);
            """,
        )
        self.assertEqual(dom.test.chars1, "aa")
        self.assertEqual(dom.test.chars2, "bbb")
    
    def test_struct_with_parameters2(self):
        # ``descr_length l(bytes)`` is being treated as a function
        # declaration!
        dom = self._test_parse_build(
            "\x01\x02\x03\x04",
            """
                typedef struct (int arraySize)
                {
                    uchar b[arraySize];
                } descr_length <read=descr_format>;

                local int bytes = 4;
                descr_length l(bytes);
            """
        )
        self.assertEqual(len(dom.l.b), 4)
        self.assertEqual(dom.l.b[0], 1)
        self.assertEqual(dom.l.b[1], 2)
        self.assertEqual(dom.l.b[2], 3)
        self.assertEqual(dom.l.b[3], 4)
    
    def test_struct_with_parameters3(self):
        # ``descr_length l(bytes)`` is being treated as a function
        # declaration!
        dom = self._test_parse_build(
            "\x01\x02\x03\x04\x01\x02\x03",
            """
                typedef struct (int arraySize, int arraySize2)
                {
                    uchar b[arraySize];
                    uchar c[arraySize2];
                } descr_length <read=descr_format>;

                local int bytes = 4;
                descr_length l(bytes, 3);
            """
        )
        self.assertEqual(len(dom.l.b), 4)
        self.assertEqual(dom.l.b[0], 1)
        self.assertEqual(dom.l.b[1], 2)
        self.assertEqual(dom.l.b[2], 3)
        self.assertEqual(dom.l.b[3], 4)
        self.assertEqual(len(dom.l.c), 3)
        self.assertEqual(dom.l.c[0], 1)
        self.assertEqual(dom.l.c[1], 2)
        self.assertEqual(dom.l.c[2], 3)
    
    def test_struct_decl_with_struct_keyword(self):
        dom = self._test_parse_build(
            "ABCD",
            """
                typedef struct {
                    char a;
                    char b;
                    char c;
                    char d;
                } BLAH;

                struct BLAH decldStruct;
            """
        )

        self.assertEqual(dom.decldStruct.a, ord("A"))
        self.assertEqual(dom.decldStruct.b, ord("B"))
        self.assertEqual(dom.decldStruct.c, ord("C"))
        self.assertEqual(dom.decldStruct.d, ord("D"))
    
    def test_struct_initialization(self):
        # local structs aren't allowed!!!
        return
#        dom = self._test_parse_build(
#            "",
#            """
#                typedef struct {
#                    char a;
#                    char b;
#                    char c;
#                    char d;
#                } blah;
#
#                local blah some_struct = { 'a', 'b', 'c', 'd'};
#            """
#        )
    
    def test_union(self):
        dom = self._test_parse_build(
            "abcd",
            """
                typedef union {
                    int some_int;
                    struct {
                        char a;
                        char b;
                        char c;
                        char d;
                    } some_chars;
                } blah;

                blah some_union;
            """
        )
    
    def test_union_complex(self):
        dom = self._test_parse_build(
            "\x00abcd",
            """
                typedef struct {
                    uchar a;
                    uchar b;
                    uchar c;
                    uchar d;
                } TEST;

                struct {
                    uchar blah;
                    union {
                        TEST chars;
                        uchar raw[sizeof(chars)];
                    } onion;
                } test;
            """
        )
        self.assertEqual(dom.test.onion.raw, "abcd")
        self.assertEqual(dom.test.onion.chars.a, ord("a"))
        self.assertEqual(dom.test.onion.chars.b, ord("b"))
        self.assertEqual(dom.test.onion.chars.c, ord("c"))
        self.assertEqual(dom.test.onion.chars.d, ord("d"))
    
    def test_union_offset1(self):
        dom = self._test_parse_build(
            "abcd",
            """
                struct {
                    char a;
                    char b;
                    union {
                        char c;
                        uchar uc;
                    } union_test;
                    char d;
                } test;
            """
        )
        self.assertEqual(dom.test.union_test._pfp__offset, 2)
    
    def test_union_offset2(self):
        dom = self._test_parse_build(
            "abcd",
            """
                typedef union {
                    char c;
                    uchar uc;
                } CHAR_UNION;

                struct {
                    char a;
                    char b;
                    CHAR_UNION union_test;
                    char d;
                } test;
            """
        )
        self.assertEqual(dom.test.union_test._pfp__offset, 2)
    
    def test_auto_increment_field_names(self):
        # when a field is declared multiple times with the same name, but
        # not consecutively, the fields should get a sequential number assigned
        # to them and NOT be stored in an implicit array
        dom = self._test_parse_build(
            "a\x00\x010\x00\x02",
            """
                BigEndian();
                while(!FEof()) {
                    char header;
                    short val;
                }
            """
        )

        self.assertEqual(dom.header_0, ord("a"))
        self.assertEqual(dom.val_0, 1)

        self.assertEqual(dom.header_1, ord("0"))
        self.assertEqual(dom.val_1, 2)
    
    def test_auto_increment_but_still_reference_last_decl_normal(self):
        # this is an interesting behavior of 010 scripts. When a field
        # is repeatedly declared, 010 scripts do not append a suffix to
        # the field names. However, since our goal is manipulation and being
        # able to access these fields individually, we do add a suffix.
        # the problem is that the script still needs to be able to access
        # the last declared field by the original name and not the
        # suffixed one.
        dom = self._test_parse_build(
            "\x01a\x01b\x01c",
            """
                while(!FEof()) {
                    char length;
                    char str[length];
                    Printf("%s|", str);
                }
            """,
            stdout="a|b|c|"
        )

    def test_implicit_array_dot_notation_for_last(self):
        # I BELIEVE scripts are able to access implicit array items
        # by index OR directly access the last one without an index
        dom = self._test_parse_build(
            "\x01a\x01b\x01c",
            """
                typedef struct {
                    uchar length;
                    char str[length];
                } STR;

                local int total_length = 0;
                while(!FEof()) {
                    STR str;
                    total_length += str.length;
                }
                Printf("%d", total_length);
            """,
            stdout="3"
        )

if __name__ == "__main__":
    unittest.main()
