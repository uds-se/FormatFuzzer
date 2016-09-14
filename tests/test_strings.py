#!/usr/bin/env python
# encoding: utf-8

import binascii
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


class TestStrings(utils.PfpTestCase):
    def setUp(self):
        pfp.fields.NumberBase.endian = pfp.fields.BIG_ENDIAN
    
    def tearDown(self):
        pass

    def test_unicode_const(self):
        dom = self._test_parse_build(
            "\n",
            """
                        char newline;
                        if(newline == \'\\n\') {
                           Warning("Found newline!");
                        }
                        """
                        )
        self.assertEqual(dom.newline, ord('\n'))

    def test_basic_string(self):
        dom = self._test_parse_build(
            "hello there\x00good byte\x00",
            """
                struct {
                    string hello;
                    string goodbye;
                } greetings;
            """
        )
        self.assertEqual(dom.greetings.hello, pfp.utils.binary("hello there"))
        self.assertEqual(dom.greetings.goodbye, pfp.utils.binary("good byte"))
    
    def test_basic_wstring(self):
        dom = self._test_parse_build(
            "h\x00e\x00l\x00l\x00o\x00 \x00t\x00h\x00e\x00r\x00e\x00\x00\x00g\x00o\x00o\x00d\x00 \x00b\x00y\x00t\x00e\x00\x00\x00",
            """
                struct {
                    wstring hello;
                    wstring goodbye;
                } greetings;
            """
        )
        self.assertEqual(dom.greetings.hello, pfp.utils.binary("hello there"))
        self.assertEqual(dom.greetings.goodbye, pfp.utils.binary("good byte"))
    
    def test_unterminated_string(self):
        with self.assertRaises(pfp.errors.PfpError):
            dom = self._test_parse_build(
                "unterminated string",
                """
                    struct {
                        string something;
                    } data;
                """
            )
    
    def test_string_indexing(self):
        dom = self._test_parse_build(
            "abcd\x00",
            """
                string alpha;
                local char a = alpha[0];
                Printf(a);
            """,
            stdout="a"
        )

        self.assertEqual(dom.alpha[0], ord("a"))
        self.assertEqual(dom.alpha[1], ord("b"))
        self.assertEqual(dom.alpha[2], ord("c"))
        self.assertEqual(dom.alpha[3], ord("d"))

        dom.alpha[2] = ord("C")

        self.assertEqual(dom.alpha[0], ord("a"))
        self.assertEqual(dom.alpha[1], ord("b"))
        self.assertEqual(dom.alpha[2], ord("C"))
        self.assertEqual(dom.alpha[3], ord("d"))
    
    def test_string_declaration_with_chars(self):
        dom = self._test_parse_build(
            "",
            r"""
                local string RarSignature = "Rar!" + '\x1A' + '\x07';
                Printf("%s", RarSignature);
            """,
            stdout="Rar!\x1a\x07"
        )

    # temp_char ends up being of class Bytes in python 3 - but not on python 2
    # This test ensures we can handle adding both a String and byte together
    def test_add_strings(self):
        dom = self._test_parse_build(
            "\x01\x02\x03\x04\x05",
            """
                             local string temp_expected, temp_char;
                             local int i;
                             for(i = 0; i < 5; i++) {
                                 SPrintf(temp_char, "%.2X", ReadUByte(FTell()+i));
                                 temp_expected += temp_char;
                             }
                             Printf("%s", temp_expected);
                     """,
            stdout="0102030405",
            verify=False
        )

    def test_add_strings_simple(self):
        dom = self._test_parse_build(
            "\x01",
            """
                             local string test;
                                 local int i;
                                 for(i = 0; i < 5; i++) {
                                     test += "test";
                                 }
                                 Printf("%s", test);
                         """,
            stdout="testtesttesttesttest",
            verify=False
         )

if __name__ == "__main__":
    unittest.main()
