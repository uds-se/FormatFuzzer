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
        pass

    def tearDown(self):
        pass
    
    def _do_parse(self, field, data):
        field._pfp__parse(StringIO(data))
    
    def _do_endian_tests(self, field, format):
        field.endian = pfp.fields.BIG_ENDIAN
        self._do_parse(field, struct.pack(">" + format, 1))
        self.assertEqual(field, 1)

        field.endian = pfp.fields.LITTLE_ENDIAN
        self._do_parse(field, struct.pack("<" + format, 1))
        self.assertEqual(field, 1)

    def test_char_array(self):
        dom = self._test_parse_build(
            "AABBCC",
            """
                char blah[6];
            """
        )
        self.assertEqual(dom.blah[0], ord("A"))
        self.assertEqual(dom.blah[1], ord("A"))
        self.assertEqual(dom.blah[2], ord("B"))
        self.assertEqual(dom.blah[3], ord("B"))
        self.assertEqual(dom.blah[4], ord("C"))
        self.assertEqual(dom.blah[5], ord("C"))

        with self.assertRaises(IndexError):
            dom.blah[6]

        with self.assertRaises(TypeError):
            dom.blah["hello"]

        dom.blah[5] = 10
        self.assertEqual(dom.blah[5], 10)
    
    def test_char_array_string_compare(self):
        dom = self._test_parse_build(
            "AABBCC",
            """
                char blah[6];
                if(blah == "AABBCC") {
                    Printf("true");
                }
            """,
            stdout="true"
        )

    def test_implicit_array_basic(self):
        dom = self._test_parse_build(
            "ABCD",
            """
                while(!FEof()) {
                    char chars;
                }
            """
        )
        self.assertEqual(len(dom.chars), 4)
        self.assertEqual(dom.chars[0], ord("A"))
        self.assertEqual(dom.chars[1], ord("B"))
        self.assertEqual(dom.chars[2], ord("C"))
        self.assertEqual(dom.chars[3], ord("D"))
    
    def test_array_length1(self):
        dom = self._test_parse_build(
            "abcd",
            """
                char chars[4];
            """
        )
        self.assertEqual(dom.chars[0], ord("a"))
        self.assertEqual(dom.chars[1], ord("b"))
        self.assertEqual(dom.chars[2], ord("c"))
        self.assertEqual(dom.chars[3], ord("d"))
        # this broke because of the Array.raw_data optimization
        self.assertEqual(len(dom.chars), 4)
    
    def test_implicit_array_complex(self):
        dom = self._test_parse_build(
            "\x01A\x02B\x03C",
            """
                typedef struct {
                    uchar some_val;
                    char some_char;
                } some_struct;

                local int i = 0;
                for(i = 0; i < 3; i++) {
                    some_struct structs;
                }
            """,
        )
        self.assertEqual(len(dom.structs), 3)
        self.assertEqual(dom.structs[0].some_val, 0x01)
        self.assertEqual(dom.structs[1].some_val, 0x02)
        self.assertEqual(dom.structs[2].some_val, 0x03)
        self.assertEqual(dom.structs[0].some_char, 0x41)
        self.assertEqual(dom.structs[1].some_char, 0x42)
        self.assertEqual(dom.structs[2].some_char, 0x43)
    
    def test_array_ref(self):
        dom = self._test_parse_build(
            "abcd",
            """
                char bytes[4];
                Printf("%02x", bytes[0]);
            """,
            stdout="61"
        )

    def test_array_initialization(self):
        # was having problems with array decls _always_ parsing the
        # input stream
        dom = self._test_parse_build(
            "",
            """
                local uchar blah[2] = { 'a', 'b' };
                Printf("%s", blah);
            """,
            stdout="ab"
        )
    
    def test_struct_array_decl(self):
        dom = self._test_parse_build(
            "abcd",
            """
                struct {
                    uchar blah;
                } structs[4];
            """,
        )
    
    def test_typedefd_array(self):
        dom = self._test_parse_build(
            "abcd",
            """
                typedef uchar BLAH[2];

                BLAH blah1;
                BLAH blah2;
            """,
            predefines=False
        )

        self.assertEqual(PYSTR(dom.blah1), "ab")
        self.assertEqual(PYSTR(dom.blah2), "cd")
    
    def test_struct_raw_data_optmization1(self):
        dom = self._test_parse_build(
            "abcd",
            """
                struct {
                    uchar blah;
                } structs[4];
            """,
        )
        self.assertEqual(dom.structs.raw_data, None)
    
    def test_struct_raw_data_optmization2(self):
        dom = self._test_parse_build(
            "abcd",
            """
                uchar chars[4];
            """,
        )
        self.assertNotEqual(dom.chars.raw_data, None)
        self.assertEqual(dom.chars.raw_data, pfp.utils.binary("abcd"))
        self.assertEqual(dom.chars._array_to_str(), pfp.utils.binary("abcd"))
        self.assertEqual(dom.chars[0], ord("a"))
        self.assertEqual(dom.chars[1], ord("b"))
        self.assertEqual(dom.chars[2], ord("c"))
        self.assertEqual(dom.chars[3], ord("d"))

        dom.chars[0] = ord("A")
        self.assertEqual(dom.chars.raw_data, pfp.utils.binary("Abcd"))
        self.assertEqual(dom.chars._array_to_str(), pfp.utils.binary("Abcd"))
        self.assertEqual(dom.chars[0], ord("A"))
        self.assertEqual(dom.chars[1], ord("b"))
        self.assertEqual(dom.chars[2], ord("c"))
        self.assertEqual(dom.chars[3], ord("d"))

        dom.chars[1] = ord("B")
        self.assertEqual(dom.chars.raw_data, pfp.utils.binary("ABcd"))
        self.assertEqual(dom.chars._array_to_str(), pfp.utils.binary("ABcd"))
        self.assertEqual(dom.chars[0], ord("A"))
        self.assertEqual(dom.chars[1], ord("B"))
        self.assertEqual(dom.chars[2], ord("c"))
        self.assertEqual(dom.chars[3], ord("d"))

        dom.chars[2] = ord("C")
        self.assertEqual(dom.chars.raw_data, pfp.utils.binary("ABCd"))
        self.assertEqual(dom.chars._array_to_str(), pfp.utils.binary("ABCd"))
        self.assertEqual(dom.chars[0], ord("A"))
        self.assertEqual(dom.chars[1], ord("B"))
        self.assertEqual(dom.chars[2], ord("C"))
        self.assertEqual(dom.chars[3], ord("d"))

        dom.chars[3] = ord("D")
        self.assertEqual(dom.chars.raw_data, pfp.utils.binary("ABCD"))
        self.assertEqual(dom.chars._array_to_str(), pfp.utils.binary("ABCD"))
        self.assertEqual(dom.chars[0], ord("A"))
        self.assertEqual(dom.chars[1], ord("B"))
        self.assertEqual(dom.chars[2], ord("C"))
        self.assertEqual(dom.chars[3], ord("D"))
    
    def test_implicit_single_item_array1(self):
        dom = self._test_parse_build(
            "\x01",
            """
                uchar blah;
                local uchar a = blah[0];
            """,
        )
        self.assertEqual(dom.blah, 1)
        self.assertEqual(dom.a, 1)
    
    def test_implicit_single_item_array2(self):
        dom = self._test_parse_build(
            "aaaa",
            """
                int blah;
                local int a = blah[0];
            """,
        )
        self.assertEqual(dom.blah, 0x61616161)
        self.assertEqual(dom.a, 0x61616161)
    
    def test_implicit_single_item_array3(self):
        dom = self._test_parse_build(
            "aaaa",
            """
                struct {
                    int blah;
                } test;
                local int a = test[0].blah;
            """,
        )
        self.assertEqual(dom.test.blah, 0x61616161)
        self.assertEqual(dom.a, 0x61616161)

if __name__ == "__main__":
    unittest.main()
