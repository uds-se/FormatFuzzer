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


class TestBasic(utils.PfpTestCase):
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

    def test_printf(self):
        """
        Run the test test. test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                Printf("hello");
            """,
            stdout="hello",
            printf=True,
        )

        dom = self._test_parse_build(
            "",
            """
                Printf("hello");
            """,
            stdout="",
            printf=False,
        )

    def test_single_decl_parse(self):
        """
        Implementation of single declaration declaration

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "\x41",
            """
                char a;
            """,
        )

    def test_basic_parse_with_comments(self):
        """
        Run test test comments.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "\x00\x01\x02\x03",
            """
                // This should be removed
                struct DATA {
                    /* so should this */
                    char a; // yo yoyo
                    char b;
                    char c;
                    char d;
                } data; /*haha*/
            """,
        )

    def test_basic_parse(self):
        """
        Test for test test test test test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "\x00\x01\x02\x03",
            """
                struct DATA {
                    char a;
                    char b;
                    char c;
                    char d;
                } data;
            """,
        )

    def test_nested_basic_parse(self):
        """
        Evaluate test test test test test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "\x00\x01\x02\x03",
            """
                struct DATA {
                    char a;
                    char b;

                    struct {
                        char a;
                        char b;
                    } nested;
                } data;
            """,
        )

    def test_typedef_basic_parse(self):
        """
        Check that the element.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "\xff\x00\x00\xff",
            """
                BigEndian();

                typedef unsigned short BLAH;
                BLAH a;
                short b;
            """,
        )
        self.assertEqual(dom.a, 0xFF00)
        self.assertEqual(dom.b, 0xFF)

    def test_local(self):
        """
        Test for test test files.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                local int i;
            """,
        )

    def test_local_field_precedence1(self):
        """
        Precedence of test files.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "\x01",
            """
                local int size = 0;
                struct {
                    uchar size;
                    Printf("%d", size);
                } test;
            """,
            stdout="1",
        )

    def test_local_field_precedence2(self):
        """
        Test for test test files.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "\x01",
            """
                uchar size;

                struct {
                    local int size = 0;
                    Printf("%d", size);
                } test;
            """,
            stdout="0",
        )

    def test_local_assignment_int(self):
        """
        Test for local assignment assignment.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                local int i = 10;
            """,
        )

    def test_local_assignment_char(self):
        """
        Test for local assignment assignment.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                local char i = 'A';
            """,
        )

    def test_local_assignment_float(self):
        """
        Test for local assignment assignment.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                local float i = 0.5f;
            """,
        )

    def test_local_assignment_double(self):
        """
        Test for assignment assignment assignment.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                local double i = 0.5;
            """,
        )

    def test_local_assignment_long(self):
        """
        Test if the local test test test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                local long i = 555l;
            """,
        )

    def test_local_assignment_string(self):
        """
        Test for assignment assignment assignment assignment.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                local string i = "hello";
            """,
        )

    def test_local_binary_arithmetic(self):
        """
        Sets the binary of the binary.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                local int i = 0;
                local int j = 10;
                local int k;
                k = i + j;
                k = i - j;
                k = i * j;
                k = i / j;
                k = i % j;
                k = i ^ j;
                k = i & j;
                k = i | j;
                k = i || j;
                k = i && j;
                k = i << j;
                k = i >> j;
            """,
        )

    def test_add_operator(self):
        """
        Adds the test operator to the test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                local int i = 2;
                local int j = 3;
                local int k = i + j;
                Printf("%d", k);
            """,
            stdout="5",
        )

    def test_minus_operator(self):
        """
        Sets the test operator

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                local int i = 2;
                local int j = 3;
                local int k = i - j;
                Printf("%d", k);
            """,
            stdout="-1",
        )

    def test_mul_operator(self):
        """
        Sets the test operator

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                local int i = 2;
                local int j = 3;
                local int k = i * j;
                Printf("%d", k);
            """,
            stdout="6",
        )

    def test_div_operator(self):
        """
        Divide test test operator

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                local int i = 2;
                local int j = 6;
                local int k = j / i;
                Printf("%d", k);
            """,
            stdout="3",
        )

    def test_mod_operator(self):
        """
        Test if the test operations

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                local int i = 5;
                local int j = 7;
                local int k = j % i;
                Printf("%d", k);
            """,
            stdout="2",
        )

    def test_xor_operator(self):
        """
        Evaluate xor test for xor

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                local int i = 6;
                local int j = 3;
                local int k = j ^ i;
                Printf("%d", k);
            """,
            stdout="5",
        )

    def test_and_operator(self):
        """
        Test for test operator

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                local int i = 56; // 0b111000
                local int j = 25; // 0b011001
                local int k = j & i;
                Printf("%d", k);
            """,
            stdout=str(int("011000", 2)),
        )

    def test_or_operator(self):
        """
        Check if the test is enabled

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                local int i = 56; // 0b111000
                local int j = 25; // 0b011001
                local int k = j | i;
                Printf("%d", k);
            """,
            stdout=str(int("111001", 2)),
        )

    def test_logical_or_operator(self):
        """
        Evaluate test or not *

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                local int i = 0;
                local int j = 25;
                local int k = j || i;
                Printf("%d", k);
            """,
            stdout="1",
        )

    def test_logical_or_operator2(self):
        """
        * test test * test *

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                Printf(
                    "%d,%d,%d,%d",
                    0 || 0,
                    0 || 1,
                    1 || 0,
                    1 || 1
                );
            """,
            stdout="0,1,1,1",
        )

    def test_logical_or_operator_lazy_resolve(self):
        """Test that logic or operations are lazily resolved
        """
        dom = self._test_parse_build(
            "",
            """
                local int a = 1;
                if (a || DOES_NOT_EXIST) {
                    Printf("Short circuit power!");
                }
            """,
            stdout="Short circuit power!",
        )

    def test_logical_and_operator(self):
        """
        Evaluate test test test test test *.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                local int i = 0;
                local int j = 25;
                local int k = j && i;
                Printf("%d", k);
            """,
            stdout="0",
        )

    def test_logical_and_operator2(self):
        """
        * test test operator to test test *

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                Printf(
                    "%d,%d,%d,%d",
                    0 && 0,
                    0 && 1,
                    1 && 0,
                    1 && 1
                );
            """,
            stdout="0,0,0,1",
        )

    def test_logical_shl_operator(self):
        """
        * test test for test for test test

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                local int i = 3;
                local int j = 4;
                local int k = i << j;
                Printf("%d", k);
            """,
            stdout="48",
        )

    def test_logical_shr_operator(self):
        """
        Evaluate test test test test results *

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                local int i = 0x17000;
                local int j = 4;
                local int k = i >> j;
                Printf("%d", k);
            """,
            stdout="5888",
        )

    def test_local_accessible_via_this(self):
        """
        Test to test test files.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "\x01\x02\x03\x04",
            """
                struct {
                    local uint test = ReadUInt();
                    Printf("%d,", this.test);
                    Printf("%d", test);
                } blah;
            """,
            stdout="{a},{a}".format(a=str(0x04030201)),
        )

    def test_struct_field_declared_in_function(self):
        """
        Test for struct struct struct struct struct struct struct.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "\x01\x02\x03\x04",
            """
                void DeclareField() {
                    uint test;
                }

                struct {
                    DeclareField();
                    Printf("%d,", this.test);
                    Printf("%d", test);
                } blah;
            """,
            stdout="{a},{a}".format(a=str(0x04030201)),
        )

    def test_add(self):
        """
        Add test test test test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "ab",
            """
                char a;
                char b;
                local int i;
                local int j = 3;
                i = FTell() + j;
                Printf("%d", i);
            """,
            stdout="5",
        )

    def test_unary_arithmetic(self):
        """
        Test for unary.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                local int i = 0;
                i++;
                i--;
                ~i;
                !i;
            """,
        )

    def test_unary_double_plus_minus1(self):
        """
        R evaluate the cross - validation.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                local int a = 0;
                local int b = ++a; // 1
                local int c = a++; // 1
                local int d = a; // 2
            """,
        )
        # also, locals are now accessible via structs! easier testing FTW!
        # TODO stop checking stdout and check the actual local values in
        # tests
        self.assertEqual(dom.a, 2)
        self.assertEqual(dom.b, 1)
        self.assertEqual(dom.c, 1)
        self.assertEqual(dom.d, 2)

    def test_unary_sizeof_basic(self):
        """
        Test test test test test test test test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "abcd",
            """
                int some_int;
                Printf("%d", sizeof(some_int));
            """,
            stdout="4",
        )

    def test_unary_sizeof_struct(self):
        """
        Unary test test test test test test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "abcde",
            """
                struct {
                    int a;
                    char b;
                } blah;
                Printf("%d", sizeof(blah));
            """,
            stdout="5",
        )

    def test_unary_sizeof_atomic_type(self):
        """
        The test test test test size.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                Printf("%d", sizeof(int));
            """,
            stdout="4",
        )

    def test_unary_sizeof_atomic_type2(self):
        """
        The test test test test test test type.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                typedef unsigned int NEW_TYPE;
                Printf("%d", sizeof(NEW_TYPE));
            """,
            stdout="4",
        )

    def test_unary_exists(self):
        """
        Check if the test test exists.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "\x00",
            """
                if(exists(this.size)) {
                    Printf("True");
                } else {
                    Printf("False");
                    uchar size;
                }

                if(exists(this.size)) {
                    Printf("True");
                } else {
                    Printf("False");
                }
            """,
            # 010 verified output: FalseFalse
            # this output will change when #87 is fixed
            stdout="FalseTrue",
        )

    def test_unary_function_exists(self):
        """
        Determine if the test test exists.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                if(function_exists(Func1)) {
                    Printf("True");
                } else {
                    Printf("False");
                }

                void Func1() {
                    
                }

                if(function_exists(Func1)) {
                    Printf("True");
                } else {
                    Printf("False");
                }
            """,
            # 010 verified output: TrueTrue
            # this output will change when #87 is fixed
            stdout="TrueTrue",
        )

    def test_unary_startof(self):
        """
        Test for test test test test test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "\x01\x02\x03",
            """
                uchar a;
                uchar b;
                uchar c;

                Printf("%d,", startof(a));
                Printf("%d,", startof(b));
                Printf("%d,", startof(c));
                Printf("%d,", startof(this.a));
                Printf("%d,", startof(this.b));
                Printf("%d", startof(this.c));
            """,
            stdout="0,1,2,0,1,2",
        )

    def test_unary_parentof(self):
        """
        Test for unary test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "\x01\x02\x03",
            """
                struct {
                    uchar a;
                    struct {
                        uchar a;
                        Printf("%d", (parentof(this)).a);
                        struct {
                            uchar a;
                            Printf("%d", (parentof(this)).a);
                        } b;
                    } b;
                } b;

                Printf("%d", (parentof(b.b.b.a)).a); // 3
                Printf("%d", (parentof b.b.b.a).a); // 3

                Printf("%d", (parentof(parentof(b.b.b.a))).a); // 2
                Printf("%d", (parentof (parentof b.b.b.a)).a); // 2

                Printf("%d", (parentof(parentof(parentof(b.b.b.a)))).a); // 1
                Printf("%d", (parentof (parentof (parentof b.b.b.a))).a); // 1
            """,
            stdout="12332211",
        )

    def test_comparisons(self):
        """
        Run test test test test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                local int i;
                i > 10;
                i >= 10;
                i < 10;
                i <= 10;
                i != 10;
                i == 10;
            """,
        )

    # is this even what you call this?
    def test_binary_assignment(self):
        """
        Gets the binary assignment.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                local int i;
                i += 10;
                i -= 10;
                i *= 10;
                i /= 10;
                i %= 10;
                i ^= 10;
                i &= 10;
                i <<= 10;
                i >>= 10;
            """,
        )


class TestByRef(utils.PfpTestCase):
    def setUp(self):
        """
        Sets the result of this thread.

        Args:
            self: (todo): write your description
        """
        pass

    def tearDown(self):
        """
        Tear down the next callable.

        Args:
            self: (todo): write your description
        """
        pass

    def test_non_byref_native_type(self):
        """
        Sets the test type for the test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                void test_func(local int value) {
                    value = 20;
                }
                local int blah = 10;
                test_func(blah);
                Printf("%d", blah);
            """,
            stdout="10",
        )

    def test_non_byref_complex(self):
        """
        Test for test to test tests. test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "abcd",
            """
                typedef struct {
                    char a;
                    char b;
                    char c;
                    char d;
                } some_struct_t;

                void test_func(some_struct_t &var) {
                    Printf("a: %d", var.a);
                    Printf("b: %d", var.b);
                    Printf("c: %d", var.c);
                    Printf("d: %d", var.d);
                }

                some_struct_t blah;
                test_func(blah);
            """,
            stdout="a: 97b: 98c: 99d: 100",
        )


if __name__ == "__main__":
    unittest.main()
