#!/usr/bin/env python
# encoding: utf-8

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pfp
import pfp.fields
from pfp.fields import PYVAL,PYSTR
import pfp.interp
import pfp.utils

import utils

class TestControlFlow(utils.PfpTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    def test_ternary1(self):
        dom = self._test_parse_build(
            "",
            """
                local int b = 10;
                local int a = (b == 10 ? 5 : 6);
            """,
        )
        self.assertEqual(dom.a, 5)
    
    def test_ternary2(self):
        dom = self._test_parse_build(
            "",
            """
                local int b = 9;
                local int a = (b == 10 ? 5 : 6);
            """,
        )
        self.assertEqual(dom.a, 6)
    
    def test_if1(self):
        dom = self._test_parse_build(
            "",
            """
                local int b = 10;
                if(b == 10) {
                    Printf("true");
                } else if(b == 11) {
                    Printf("false");
                } else {
                    Printf("false");
                }
            """,
            stdout="true"
        )

    def test_if2(self):
        dom = self._test_parse_build(
            "",
            """
                local int b = 10;
                if(b == 11) {
                    Printf("false");
                } else if(b == 10) {
                    Printf("true");
                } else {
                    Printf("false");
                }
            """,
            stdout="true"
        )

    def test_if3(self):
        dom = self._test_parse_build(
            "",
            """
                local int b = 10;
                if(b == 11) {
                    Printf("false");
                } else if(b == 12) {
                    Printf("false");
                } else {
                    Printf("true");
                }
            """,
            stdout="true"
        )
    
    def test_for1(self):
        dom = self._test_parse_build(
            "",
            """
                local int j = 0;
                for(local int j = 0; j < 10; j++ ) {
                    Printf("a");
                }
            """,
            stdout="a"*10
        )

    def test_for2(self):
        dom = self._test_parse_build(
            "",
            """
                local int j = 0;
                for(; j < 10; j++ ) {
                    Printf("a");
                }
            """,
            stdout="a"*10
        )

    def test_for3(self):
        dom = self._test_parse_build(
            "",
            """
                local int j = 0;
                for(; j < 10; j++ ) {
                    Printf("a");
                    break;
                }
            """,
            stdout="a"
        )

    def test_for4(self):
        dom = self._test_parse_build(
            "",
            """
                local int j = 0;
                for(; j < 10; j++ ) {
                    if(j % 2 == 0) {
                        continue;
                    }
                    Printf("a");
                }
            """,
            stdout="aaaaa"
        )

    def test_for5(self):
        dom = self._test_parse_build(
            "",
            """
                local int j = 0;
                for(;; j++ ) {
                    Printf("a");
                    if(j == 3) {
                        break;
                    }
                }
            """,
            stdout="aaaa"
        )
    
    def test_while1(self):
        dom = self._test_parse_build(
            "",
            """
                local int j = 0;
                while(j < 3) {
                    j++;
                    Printf("a");
                }
            """,
            stdout="aaa"
        )
    
    def test_while2(self):
        dom = self._test_parse_build(
            "",
            """
                local int j = 0;
                while(1) {
                    Printf("a");
                    j++;
                    if(j == 3) {
                        break;
                    }
                }
            """,
            stdout="aaa"
        )
    
    def test_while3(self):
        dom = self._test_parse_build(
            "",
            """
                local int j = 0;
                while(1) {
                    Printf("a");
                    j++;
                    if(j != 3) {
                        continue;
                    }
                    break;
                }
            """,
            stdout="aaa"
        )
    
    def test_do_while(self):
        dom = self._test_parse_build(
            "abcd\x00",
            """
                do {
                    string str;
                } while(0);
            """,
        )
        self.assertEqual(dom.str, b"abcd")
        self.assertEqual(dom.str[0], ord("a"))
        self.assertEqual(dom.str[1], ord("b"))
        self.assertEqual(dom.str[2], ord("c"))
        self.assertEqual(dom.str[3], ord("d"))

    def test_switch(self):
        dom = self._test_parse_build(
            "\x00\x00\x00\x01\x00\x00\x00\x02",
            """
                local int a = 5;
                switch(a) {
                    case 0:
                        Printf("false");
                        Printf("false");
                        Printf("false");
                        break;
                    case 5:
                        int case_5;
                    default:
                        int case_default;
                        break;
                };
            """,
        )
        self.assertEqual(dom.case_5, 1)
        self.assertEqual(dom.case_default, 2)
    
    def test_fall_through_no_case_body(self):
        dom = self._test_parse_build(
            "\x00\x01\x00\x02\x00\x03",
            """
            BigEndian();
            local int a = 1;
            switch(a) {
                case 0:
                case 1:
                case 2:
                    ushort a;
                    ushort b;
                    ushort c;
                    break;
                case 3:
                case 4:
                case 5:
                default:
                    uchar a;
                    uchar b;
                    uchar c;
                    break;
            };
            """
        )
        self.assertEqual(dom.a, 1)
        self.assertEqual(dom.b, 2)
        self.assertEqual(dom.c, 3)

    def test_fall_through_no_case_body2(self):
        dom = self._test_parse_build(
            "",
            """
            BigEndian();
            local int a = 3;
            switch(a) {
                case 0:
                case 1:
                    break;
                case 3:
                case 4:
                    break;
                case 5:
                    uchar a;
                    uchar b;
                    uchar c;
                    break;
                default:
                    break;
            };
            """
        )

    def test_fall_through_no_case_body3(self):
        dom = self._test_parse_build(
            "AAABBBCCCDDD",
            """
            BigEndian();
            local int val = 3;
            while(!FEof()) {
                switch(val) {
                    case 0:
                    case 1:
                        break;
                    case 3:
                    case 4:
                        uchar a;
                        break;
                    case 5:
                        uchar a;
                        uchar b;
                        uchar c;
                        break;
                    default:
                        break;
                };
            }
            """
        )

if __name__ == "__main__":
    unittest.main()
