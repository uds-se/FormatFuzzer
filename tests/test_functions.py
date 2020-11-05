#!/usr/bin/env python
# encoding: utf-8

import os

try:
    from StringIO import StringIO

# StringIO does not exist in python3
except ImportError as e:
    from io import StringIO
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pfp
import pfp.fields
import pfp.interp
import pfp.utils

import utils


class TestFunctions(utils.PfpTestCase):
    def setUp(self):
        """
        Set the endian fields.

        Args:
            self: (todo): write your description
        """
        pfp.fields.NumberBase.endian = pfp.fields.LITTLE_ENDIAN

    def tearDown(self):
        """
        Tear down the next callable.

        Args:
            self: (todo): write your description
        """
        pass

    def test_function(self):
        """
        Run the test test function.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                void func(int a, int b) {
                    local int c = a + b;
                }

                func(10, 20);
            """,
        )

    def test_declaration_order(self):
        """
        Æł¥è¯¢é¢ĺçº¿

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            # this has been tested in 010 to work
            """
                hello();
                void hello() {
                    Printf("Hello World");
                }
            """,
            stdout="Hello World",
        )

    def test_declaration_order2(self):
        """
        Æľ´æĸ°æį¢åįķ®

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            # this has been tested in 010 to work
            r"""
                hello(10);
                typedef unsigned short custom_ushort;
                void hello(custom_ushort test) {
                    Printf("Hello World %d", test);
                }
            """,
            stdout="Hello World 10",
        )

    def test_builtin(self):
        """
        Called when builtin builtinspect.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                Printf("hello there");
                Printf("%d", 10);
            """,
            stdout="hello there10",
        )

    def test_custom_func(self):
        """
        Test for test test test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                int add(int n1, int n2) {
                    return n1 + n2;
                }

                Printf("%d", add(5, 8));
            """,
            stdout="13",
        )

    def test_custom_func2(self):
        """
        Add test test test test test test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                string prepend(string orig) {
                    return "blah: " + orig;
                }

                Printf(prepend("hello"));
            """,
            stdout="blah: hello",
        )

    def test_native_func(self):
        """
        Decorator for native python native python native native native native native native native python datatypes

        Args:
            self: (todo): write your description
        """
        func_called = False

        def func(params, ctxt, scope, stream, coord):
            """
            Decor for the function.

            Args:
                params: (dict): write your description
                ctxt: (todo): write your description
                scope: (todo): write your description
                stream: (todo): write your description
                coord: (todo): write your description
            """
            func_called = True
            return 555

        interp = pfp.interp.PfpInterp()
        interp.add_native(name="func", func=func, ret=pfp.fields.Int)

        dom = self._test_parse_build(
            "",
            """
            Printf("%d", func());
            """,
            stdout="555",
        )

    def test_lazy_type_checking(self):
        """
        Check if the test test tests.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "\x0a",
            """
                void lazy_type_checking_function(LazyType &blah) {
                    Printf("blah.var1 = %d", blah.var1);
                }

                typedef struct LazyType {
                    uchar var1;
                } LAZY_TYPE_TYPE;

                LAZY_TYPE_TYPE a;
                lazy_type_checking_function(a);
            """,
            stdout="blah.var1 = 10",
        )

    def test_function_string_return(self):
        """
        Returns the test test string.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "abcd\x00",
            """
                string ReadStringN(int64 pos, int n) {
                    local uchar s[n];
                    ReadBytes(s, pos, n);
                    return s;
                }
                if(ReadStringN(FTell(), 5) == "abcd") {
                    Printf("true");
                } else {
                    Printf("false");
                }
            """,
            stdout="true",
        )

    # see https://github.com/d0c-s4vage/pfp/issues/27 - thanks @vit9696!
    def test_void_return(self):
        """
        The test test test test test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            r"""
                void func() {
                    #ifndef DEBUG
                        return;
                    #endif
                    Printf("Hello\n");
                }
                func();
            """,
        )

    def test_array_as_param(self):
        """
        Convert the test test test test results

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "".join(
                [
                    "\x00\x00\x00\x01",
                    "\x00\x00\x00\x02",
                    "\x00\x00\x00\x03",
                    "\x00\x00\x00\x04",
                    "\x00\x00\x00\x05",
                ]
            ),
            r"""
                LittleEndian();
                int me[5];
                void passMe(int value[]) {
                    Printf("%08x", value[0]);
                }
                passMe(me);
            """,
            stdout="01000000",
        )


if __name__ == "__main__":
    unittest.main()
