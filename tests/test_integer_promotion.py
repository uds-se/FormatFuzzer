#!/usr/bin/env python
# encoding: utf-8

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pfp
import pfp.fields
from pfp.fields import PYVAL, PYSTR
import pfp.interp
import pfp.utils

import utils


class TestIntegerPromotion(utils.PfpTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_eq(self):
        dom = self._test_parse_build(
            "",
            """
                local int DEFA = 0xfaded006;
                if (DEFA == 0xFADED006) {
                    Printf("true1");
                }
                if (DEFA == -86061050) {
                    Printf("true2");
                }
                if (DEFA != 0xFADED005) {
                    Printf("true1");
                }
                if (DEFA != -86061051) {
                    Printf("true2");
                }
            """,
            stdout="true1true2true1true2",
        )

    def test_cmp(self):
        dom = self._test_parse_build(
            "",
            """
                local int DEFA = 0xfaded006;
                if (DEFA > 0xFADED005) {
                    Printf("true1");
                }
                if (DEFA < -86061049) {
                    Printf("true2");
                }
                if (DEFA >= 0xFADED005) {
                    Printf("true1");
                }
                if (DEFA <= -86061049) {
                    Printf("true2");
                }
            """,
            stdout="true1true2true1true2",
        )

    def test_iadd(self):
        dom = self._test_parse_build(
            "",
            """
                local int DEFA = 0;
                DEFA += 0xFADED006;
                Printf("DEFA: %d", DEFA);
            """,
            stdout="DEFA: -86061050",
        )

    def test_add(self):
        dom = self._test_parse_build(
            "",
            """
                local int DEFA = 0;
                local unsigned int U = DEFA + 0xFADED006;
                local signed int X = DEFA + 0xFADED006;
                Printf("U: %u,", U);
                Printf("X: %d", X);
            """,
            stdout="U: 4208906246,X: -86061050",
        )
