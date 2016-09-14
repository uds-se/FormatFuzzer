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
import pfp.interp as interp
import pfp.errors
from pfp.fields import *
import pfp.utils

import utils

class TestBitfields(utils.PfpTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    def test_bitfield_basic(self):
        dom = self._test_parse_build(
            "\xab",
            """
                struct {
                    uchar test:8;
                } blah;
            """
        )
    
    def test_bitfield_enable_padding_left_right(self):
        dom = self._test_parse_build(
            "\x3f\x03",
            """
                LittleEndian();
                BitfieldEnablePadding();
                BitfieldLeftToRight();
                struct {
                    ushort test1: 10;
                    ushort test2: 6;
                } blah;
            """,
        )
        self.assertEqual(dom.blah.test1, 0xc)
        self.assertEqual(dom.blah.test2, 0x3f)
    
    def test_bitfield_enable_padding_right_left(self):
        dom = self._test_parse_build(
            "\x3f\x03",
            """
                LittleEndian();
                BitfieldEnablePadding();
                BitfieldRightToLeft();
                struct {
                    ushort test1: 10;
                    ushort test2: 6;
                } blah;
            """,
        )
        self.assertEqual(dom.blah.test1, 0x33f)
        self.assertEqual(dom.blah.test2, 0x0)
    
    def test_bitfield_basic_big_endian(self):
        b = lambda x: chr(int(x,2))

        dom = self._test_parse_build(
            b("10011011") + b("10011111") + b("10000001"),
            """
                BigEndian();
                struct {
                    uchar test : 4;
                    uchar test1 : 2;
                    uchar test2 : 2;
                    ushort test3 : 16;
                } blah;
            """
        )
        self.assertEqual(dom.blah.test, int("1001",2))
        self.assertEqual(dom.blah.test1, int("10", 2))
        self.assertEqual(dom.blah.test2, int("11", 2))
        self.assertEqual(dom.blah.test3, int("1001111110000001",2))
    
    def test_bitfield_basic_little_endian(self):
        b = lambda x: chr(int(x,2))

        dom = self._test_parse_build(
             b("10011111") + b("10000001") + b("10011011"),
            """
                LittleEndian();
                struct {
                    uchar test : 4;
                    uchar test1 : 2;
                    uchar test2 : 2;
                    ushort test3 : 16;
                } blah;
            """
        )
        self.assertEqual(dom.blah.test, int("1111", 2))
        self.assertEqual(dom.blah.test1, int("01", 2))
        self.assertEqual(dom.blah.test2, int("10", 2))
        self.assertEqual(dom.blah.test3, int("1001101110000001",2))
    
    def test_bitfield_basic_padded_little_endian(self):
        b = lambda x: chr(int(x,2))
        
        dom = self._test_parse_build(
            b("00000111") + b("00000000") + b("10000000"),
            """
                LittleEndian();
                BitfieldEnablePadding();
                struct {
                    uchar test : 3;
                    ushort big;
                } blah;
            """,
            predefines=False,
        )
        self.assertEqual(dom.blah.test, int("111", 2))
        self.assertEqual(dom.blah.big, int("1000000000000000", 2))

    def test_bitfield_basic_unpadded_little_endian(self):
        b = lambda x: chr(int(x,2))
        
        dom = self._test_parse_build(
            b("11110000") + b("00000000") + b("00000000"),
            """
                LittleEndian();
                BitfieldDisablePadding();
                struct {
                    uchar test : 3;
                    ushort big;
                } blah;
            """,
            predefines=False
        )
        self.assertEqual(dom.blah.test, int("111", 2))
        self.assertEqual(dom.blah.big, int("10000000", 2))

    def test_bitfield_basic_unpadded_big_endian(self):
        b = lambda x: chr(int(x,2))
        
        dom = self._test_parse_build(
            b("11110000") + b("00000000") + b("00000000"),
            """
                BigEndian();
                BitfieldDisablePadding();
                struct {
                    uchar test : 3;
                    ushort big;
                } blah;
            """,
            predefines=False
        )
        self.assertEqual(dom.blah.test, int("111", 2))
        self.assertEqual(dom.blah.big, int("1000000000000000", 2))
    
    def test_bitfield_in_if(self):
        dom = self._test_parse_build(
            "\xf0",
            """
                LittleEndian();
                struct {
                    if(1) {
                        // bitfields are padded by default
                        uchar bitfield_1:4;
                        uchar bitfield_2:4;
                    }
                } blah;
            """
        )
    
    def test_bitfield_again(self):
        dom = self._test_parse_build(
            "\x00AB",
            """
            struct QuanTable {
                uchar Pq : 4;
                uchar Tq : 4;
                if (Pq == 0)
                    byte qTable[2];
            } qtable;
            """
        )
    
    def test_bitfield_no_padding(self):
        dom = self._test_parse_build(
            "\x78\x00\x05\x5f\x00\x00\x0f\xa0\x00\x00\x0c",
            """
            LittleEndian();
            BitfieldLeftToRight();
            typedef struct {
                ubyte Nbits         : 5;
                BitfieldDisablePadding();
                int Xmin            : Nbits;
                int Xmax            : Nbits;
                int Ymin            : Nbits;
                int Ymax            : Nbits;
                BitfieldEnablePadding();
            } RECT;
            RECT rect;

            // should snap back to padded mode
            short test;
            """,
        )
        self.assertEqual(dom.rect.Nbits, 15)
        self.assertEqual(dom.rect.Xmin, 0)
        self.assertEqual(dom.rect.Xmax, 11000)
        self.assertEqual(dom.rect.Ymin, 0)
        self.assertEqual(dom.rect.Ymax, 8000)
        self.assertEqual(dom.test, 0x0c00)
    
    def test_bitfield_with_mixed_types_and_enum(self):
        b = lambda x: chr(int(x,2))

        dom = self._test_parse_build(
            b("11011110"),
            """
                enum <uchar> BLAHS {
                    BLAH1=1,
                    BLAH2,
                    BLAH3,
                    BLAH4
                };

                // this should work in padded mode
                uchar test1: 2;
                uchar test2: 2;
                BLAHS test3: 2;
                byte test4: 2;
            """
        )
        self.assertEqual(dom.test1, 2)
        self.assertEqual(dom.test2, 3)
        self.assertEqual(dom.test3, 1)
        self.assertEqual(dom.test3.enum_name, "BLAH1")
        self.assertEqual(dom.test4, 3)

if __name__ == "__main__":
    unittest.main()
