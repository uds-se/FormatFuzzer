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

    def test_isub(self):
        dom = self._test_parse_build(
            "",
            """
                local int DEFA = 0;
                DEFA -= 0xFADED006;
                Printf("DEFA: %d", DEFA);
            """,
            stdout="DEFA: 86061050",
        )

    def test_sub(self):
        dom = self._test_parse_build(
            "",
            """
                local int DEFA = 0;
                local unsigned int U = DEFA - 0xFADED006;
                local signed int X = DEFA - 0xFADED006;
                Printf("U: %u,", U);
                Printf("X: %d", X);
            """,
            stdout="U: 86061050,X: 86061050",
        )

    def test_imul(self):
        dom = self._test_parse_build(
            "",
            """
                local int DEFA = 1;
                DEFA *= 0xFADED006;
                Printf("DEFA: %d", DEFA);
            """,
            stdout="DEFA: -86061050",
        )

    def test_mul(self):
        dom = self._test_parse_build(
            "",
            """
                local int DEFA = 1;
                local unsigned int U = DEFA * 0xFADED006;
                local signed int X = DEFA * 0xFADED006;
                Printf("U: %u,", U);
                Printf("X: %d", X);
            """,
            stdout="U: 4208906246,X: -86061050",
        )

    def test_idiv(self):
        # NOTE: 010 editor differs from C's integer promotion
        # and handling here. C will output "DEFA: 0", since 0xFADED006 * 10
        # wraps and does not end up being an even multiple of 0xFADED006:
        #
        #     #include <stdio.h>
        #
        #     int main(int argc, char *argv[])
        #     {
        #         int DEFA = 0xFADED006 * 10;
        #         DEFA /= 0xFADED006;
        #         printf("DEFA: %d", DEFA);
        #         return 0;
        #     }
        #
        # It appears that 010 editor, on the other hand, does not promote
        # constants to be greater than four bytes (defaults to Int). Pfp
        # also defaults to Int, and, since it mirrors 010's behavior, pfp
        # will keep this even though it doesn't match C's integer promotion.
        dom = self._test_parse_build(
            "",
            """
                local int DEFA = 0xFADED006 * 10;
                DEFA /= 0xFADED006;
                Printf("DEFA: %d", DEFA);
            """,
            stdout="DEFA: 10",
        )

    def test_div(self):
        # as with the test_imul test case, 010 editor has differing behavior 
        # from C's integer promotion:
        #
        #       U: 10,X: 10
        #
        # Whereas the C program below outputs: U: 0, X: 0
        #
        #       #include <stdio.h>
        #       
        #       int main(int argc, char *argv[])
        #       {
        #           int DEFA = 0xFADED006 * 10;
        #           unsigned int U = DEFA / 0xFADED006;
        #           signed int X = DEFA / 0xFADED006;
        #           printf("U: %u,", U);
        #           printf("X: %d", X);
        #       }
        #
        # For now pfp will adhere mirror 010 editor's behavior.

        dom = self._test_parse_build(
            "",
            """
                local int DEFA = 0xFADED006 * 10;
                local unsigned int U = DEFA / 0xFADED006;
                local signed int X = DEFA / 0xFADED006;
                Printf("U: %u,", U);
                Printf("X: %d", X);
            """,
            stdout="U: 10,X: 10",
        )

    def test_iand(self):
        dom = self._test_parse_build(
            "",
            """
                local int DEFA = 0xffffffff;
                DEFA &= 0xFADED006;
                Printf("DEFA: %d", DEFA);
            """,
            stdout="DEFA: -86061050",
        )

    def test_and(self):
        dom = self._test_parse_build(
            "",
            """
                local int DEFA = 0xffffffff;
                local unsigned int U = DEFA & 0xFADED006;
                local signed int X = DEFA & 0xFADED006;
                Printf("U: %u,", U);
                Printf("X: %d", X);
            """,
            stdout="U: 4208906246,X: -86061050",
        )

    def test_ixor(self):
        dom = self._test_parse_build(
            "",
            """
                local int DEFA = 0xffffffff;
                DEFA ^= 0xFADED006;
                Printf("DEFA: %d", DEFA);
            """,
            stdout="DEFA: 86061049",
        )

    def test_xor(self):
        dom = self._test_parse_build(
            "",
            """
                local int DEFA = 0xffffffff;
                local unsigned int U = DEFA ^ 0xFADED006;
                local signed int X = DEFA ^ 0xFADED006;
                Printf("U: %u,", U);
                Printf("X: %d", X);
            """,
            stdout="U: 86061049,X: 86061049",
        )

    def test_ior(self):
        dom = self._test_parse_build(
            "",
            """
                local int DEFA = 0x33333333;
                DEFA |= 0xFADED006;
                Printf("DEFA: %d", DEFA);
            """,
            stdout="DEFA: -67112137",
        )

    def test_or(self):
        dom = self._test_parse_build(
            "",
            """
                local int DEFA = 0x33333333;
                local unsigned int U = DEFA | 0xFADED006;
                local signed int X = DEFA | 0xFADED006;
                Printf("U: %u,", U);
                Printf("X: %d", X);
            """,
            stdout="U: 4227855159,X: -67112137",
        )

    def test_imod(self):
        # C differs from 010 editor here:
        #
        #          #include <stdio.h>
        #          
        #          int main(int argc, char *argv[])
        #          {
        #              int DEFA = 0x33333333;
        #              DEFA %= 0xFADED006;
        #              printf("DEFA: %d", DEFA);
        #          }
        #
        # prints DEFA: 858993459, which is what pfp currently produces
        #
        # 010 editor on the other hand produces DEFA: 84444009. I am not
        # sure where that number comes from.
        #
        # In this case, pfp adheres to C's behavior instead of 010 editor
        dom = self._test_parse_build(
            "",
            """
                local int DEFA = 0x33333333;
                DEFA %= 0xFADED006;
                Printf("DEFA: %d", DEFA);
            """,
            stdout="DEFA: 858993459",
        )

    def test_mod(self):
        # oddly enough, 010 editor's behavior on direct mod *DOES* match C's
        # behavior
        dom = self._test_parse_build(
            "",
            """
                local int DEFA = 0x33333333;
                local unsigned int U = DEFA % 0xFADED006;
                local signed int X = DEFA % 0xFADED006;
                Printf("U: %u,", U);
                Printf("X: %d", X);
            """,
            stdout="U: 858993459,X: 858993459",
        )
