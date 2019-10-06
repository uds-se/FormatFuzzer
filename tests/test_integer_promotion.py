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

    def test_if4(self):
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
            """,
            stdout="true1true2",
        )
