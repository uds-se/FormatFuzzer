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

class TestTypeCreation(utils.PfpTestCase):
    def setUp(self):
        pfp.fields.NumberBase.endian = pfp.fields.LITTLE_ENDIAN

    def tearDown(self):
        pass
    
    def test_atomic(self):
        dom = self._test_parse_build(
            "",
            """
                typedef unsigned int BLAH;
            """
        )
        res = dom.BLAH()
        self.assertTrue(isinstance(res, pfp.fields.UInt))
        self.assertEqual(res, 0)
    
    def test_struct(self):
        dom = self._test_parse_build(
            "",
            """
                LittleEndian();
                typedef struct {
                    char a;
                    char b;
                    uint c;
                } TEST_STRUCT;
            """
        )
        res = dom.TEST_STRUCT()

        self.assertTrue(isinstance(res, pfp.fields.Struct))
        self.assertEqual(res.a, 0)
        self.assertEqual(res.b, 0)
        self.assertEqual(res.c, 0)

        res.a = 0x30
        res.b = 0x40
        res.c = 0x1000
        self.assertEqual(res.a, 0x30)
        self.assertEqual(res.b, 0x40)
        self.assertEqual(res.c, 0x1000)

        output = res._pfp__build()
        self.assertEqual(output, pfp.utils.binary("\x30\x40\x00\x10\x00\x00"))


if __name__ == "__main__":
    unittest.main()
