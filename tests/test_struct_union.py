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


class TestStructUnion(utils.PfpTestCase):
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

    def test_struct_vit9696_1(self):
        """
        The test test test test files.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "\x00\x01\x02\x03\x00\x01\x02\x03",
            """
                typedef struct MY_STRUCT_S {
                    char magic[4];
                    unsigned int filesize;
                } MY_STRUCT;
                LittleEndian();
                MY_STRUCT s;
            """
        )
        assert dom.s.magic == "\x00\x01\x02\x03"
        assert dom.s.filesize == 0x03020100

    def test_struct_vit9696_2(self):
        """
        Build test test test test test test files.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "\x00\x01\x02\x03\x00\x01\x02\x03",
            """
                struct MY_STRUCT {
                    char magic[4];
                    unsigned int filesize;
                };
                LittleEndian();
                MY_STRUCT s;
            """
        )
        assert dom.s.magic == "\x00\x01\x02\x03"
        assert dom.s.filesize == 0x03020100

    def test_struct_vit9696_3(self):
        """
        Test for test test test files.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "\x00\x01\x02\x03\x00\x01\x02\x03",
            """
                typedef struct MY_STRUCT {
                    char magic[4];
                    unsigned int filesize;
                };
                LittleEndian();
                MY_STRUCT s;
            """
        )
        assert dom.s.magic == "\x00\x01\x02\x03"
        assert dom.s.filesize == 0x03020100

    def test_struct_vit9696_4(self):
        """
        The test test test test test test test files.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "\x00\x01\x02\x03\x00\x01\x02\x03",
            """
                struct MY_STRUCT {
                    char magic[4];
                    unsigned int filesize;
                };
                LittleEndian();
                struct MY_STRUCT s;
            """
        )
        assert dom.s.magic == "\x00\x01\x02\x03"
        assert dom.s.filesize == 0x03020100

    def test_struct_vit9696_5(self):
        """
        Test for test test test test test files

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "\x00\x01\x02\x03\x00\x01\x02\x03",
            """
                struct MY_STRUCT {
                    char magic[4];
                    unsigned int filesize;
                };
                typedef struct MY_STRUCT ME;
                LittleEndian();
                ME s;
            """,
            debug=False,
        )
        assert dom.s.magic == "\x00\x01\x02\x03"
        assert dom.s.filesize == 0x03020100
    
    def test_basic_struct(self):
        """
        Deter struct struct.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "\x00\x01\x02\x03",
            """
                struct SomeStruct {
                    byte a;
                    byte b;
                    byte c;
                    byte d;
                };
                struct SomeStruct test;
            """
        )
        assert dom.test.a == 0
        assert dom.test.b == 1
        assert dom.test.c == 2
        assert dom.test.d == 3

    def test_field_path(self):
        """
        Test for the field path

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "Abbbb4141414142424242",
            """
                struct {
                    struct {
                        struct {
                            char inner;
                            char array[4];
                        } nested2;
                        int some_int;
                    } nested1;
                    int some_int2;
                } root;
            """,
        )
        self.assertEqual(dom.root._pfp__path(), "root")
        self.assertEqual(dom.root.some_int2._pfp__path(), "root.some_int2")
        self.assertEqual(dom.root.nested1._pfp__path(), "root.nested1")
        self.assertEqual(dom.root.nested1.some_int._pfp__path(), "root.nested1.some_int")
        self.assertEqual(dom.root.nested1.nested2._pfp__path(), "root.nested1.nested2")
        self.assertEqual(dom.root.nested1.nested2.inner._pfp__path(), "root.nested1.nested2.inner")
        self.assertEqual(dom.root.nested1.nested2.array._pfp__path(), "root.nested1.nested2.array")
        self.assertEqual(dom.root.nested1.nested2.array[0]._pfp__path(), "root.nested1.nested2.array[0]")
        self.assertEqual(dom.root.nested1.nested2.array[1]._pfp__path(), "root.nested1.nested2.array[1]")
        self.assertEqual(dom.root.nested1.nested2.array[2]._pfp__path(), "root.nested1.nested2.array[2]")
        self.assertEqual(dom.root.nested1.nested2.array[3]._pfp__path(), "root.nested1.nested2.array[3]")
    
    def test_struct(self):
        """
        The test test test test test test test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "abcddcba",
            """
                typedef struct {
                    int some_int;
                } blah;

                blah some_struct;
                blah some_struct2;
            """,
        )
    
    def test_forward_declared_struct(self):
        """
        Forward test test test test test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "\x00\x01",
            """
                struct fp16;
                void ReadFP16(fp16& f)
                {
                    Printf("%d", f.value);
                }
                typedef struct
                {
                    int16 value;
                } fp16;
                fp16 preferred_volume;
                ReadFP16(preferred_volume);
            """,
            stdout="256",
        )

    def test_struct_with_parameters(self):
        """
        Equal of test test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "aabbb",
            """
                typedef struct (int a, int b) {
                    char chars1[a];
                    char chars2[b];
                } blah;

                blah test(2, 3);
            """,
        )
        self.assertEqual(dom.test.chars1, "aa")
        self.assertEqual(dom.test.chars2, "bbb")

    def test_struct_with_parameters2(self):
        """
        This function to see if the values in the same order.

        Args:
            self: (todo): write your description
        """
        # ``descr_length l(bytes)`` is being treated as a function
        # declaration!
        dom = self._test_parse_build(
            "\x01\x02\x03\x04",
            """
                typedef struct (int arraySize)
                {
                    uchar b[arraySize];
                } descr_length <read=descr_format>;

                local int bytes = 4;
                descr_length l(bytes);
            """,
        )
        self.assertEqual(len(dom.l.b), 4)
        self.assertEqual(dom.l.b[0], 1)
        self.assertEqual(dom.l.b[1], 2)
        self.assertEqual(dom.l.b[2], 3)
        self.assertEqual(dom.l.b[3], 4)

    def test_struct_with_parameters3(self):
        """
        Equalize the values of the structure.

        Args:
            self: (todo): write your description
        """
        # ``descr_length l(bytes)`` is being treated as a function
        # declaration!
        dom = self._test_parse_build(
            "\x01\x02\x03\x04\x01\x02\x03",
            """
                typedef struct (int arraySize, int arraySize2)
                {
                    uchar b[arraySize];
                    uchar c[arraySize2];
                } descr_length <read=descr_format>;

                local int bytes = 4;
                descr_length l(bytes, 3);
            """,
        )
        self.assertEqual(len(dom.l.b), 4)
        self.assertEqual(dom.l.b[0], 1)
        self.assertEqual(dom.l.b[1], 2)
        self.assertEqual(dom.l.b[2], 3)
        self.assertEqual(dom.l.b[3], 4)
        self.assertEqual(len(dom.l.c), 3)
        self.assertEqual(dom.l.c[0], 1)
        self.assertEqual(dom.l.c[1], 2)
        self.assertEqual(dom.l.c[2], 3)

    def test_typedefd_struct_with_parameters(self):
        """
        This function for checking of the superclass.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "\x01\x02\x03\x04\x01\x02\x03",
            """
                struct TEST_STRUCT(int arraySize, int arraySize2)
                {
                    uchar b[arraySize];
                    uchar c[arraySize2];
                };
                local int bytes = 4;
                typedef struct TEST_STRUCT NEW_STRUCT;
                NEW_STRUCT l(bytes, 3);
            """,
        )
        self.assertEqual(len(dom.l.b), 4)
        self.assertEqual(dom.l.b[0], 1)
        self.assertEqual(dom.l.b[1], 2)
        self.assertEqual(dom.l.b[2], 3)
        self.assertEqual(dom.l.b[3], 4)
        self.assertEqual(len(dom.l.c), 3)
        self.assertEqual(dom.l.c[0], 1)
        self.assertEqual(dom.l.c[1], 2)
        self.assertEqual(dom.l.c[2], 3)

    def test_struct_decl_with_struct_keyword(self):
        """
        Returns a struct struct struct_decl_keyword.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "ABCD",
            """
                typedef struct {
                    char a;
                    char b;
                    char c;
                    char d;
                } BLAH;

                struct BLAH decldStruct;
            """,
        )

        self.assertEqual(dom.decldStruct.a, ord("A"))
        self.assertEqual(dom.decldStruct.b, ord("B"))
        self.assertEqual(dom.decldStruct.c, ord("C"))
        self.assertEqual(dom.decldStruct.d, ord("D"))

    def test_struct_initialization(self):
        """
        Returns the test_structization of the test.

        Args:
            self: (todo): write your description
        """
        # local structs aren't allowed!!!
        return

    #        dom = self._test_parse_build(
    #            "",
    #            """
    #                typedef struct {
    #                    char a;
    #                    char b;
    #                    char c;
    #                    char d;
    #                } blah;
    #
    #                local blah some_struct = { 'a', 'b', 'c', 'd'};
    #            """
    #        )

    def test_union(self):
        """
        Compile the union of the test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "abcd",
            """
                typedef union {
                    int some_int;
                    struct {
                        char a;
                        char b;
                        char c;
                        char d;
                    } some_chars;
                } blah;

                blah some_union;
            """,
        )

    def test_union_complex(self):
        """
        Compute the union of the union.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "\x00abcd",
            """
                typedef struct {
                    uchar a;
                    uchar b;
                    uchar c;
                    uchar d;
                } TEST;

                struct {
                    uchar blah;
                    union {
                        TEST chars;
                        uchar raw[sizeof(chars)];
                    } onion;
                } test;
            """,
        )
        self.assertEqual(dom.test.onion.raw, "abcd")
        self.assertEqual(dom.test.onion.chars.a, ord("a"))
        self.assertEqual(dom.test.onion.chars.b, ord("b"))
        self.assertEqual(dom.test.onion.chars.c, ord("c"))
        self.assertEqual(dom.test.onion.chars.d, ord("d"))

    def test_union_offset1(self):
        """
        Compute the union of two union.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "abcd",
            """
                struct {
                    char a;
                    char b;
                    union {
                        char c;
                        uchar uc;
                    } union_test;
                    char d;
                } test;
            """,
        )
        self.assertEqual(dom.test.union_test._pfp__offset, 2)

    def test_union_offset2(self):
        """
        Compute the union of two union of union offset.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "abcd",
            """
                typedef union {
                    char c;
                    uchar uc;
                } CHAR_UNION;

                struct {
                    char a;
                    char b;
                    CHAR_UNION union_test;
                    char d;
                } test;
            """,
        )
        self.assertEqual(dom.test.union_test._pfp__offset, 2)

    def test_auto_increment_field_names(self):
        """
        Test for auto - scaling names of the fields.

        Args:
            self: (todo): write your description
        """
        # when a field is declared multiple times with the same name, but
        # not consecutively, the fields should get a sequential number assigned
        # to them and NOT be stored in an implicit array
        dom = self._test_parse_build(
            "a\x00\x010\x00\x02",
            """
                BigEndian();
                while(!FEof()) {
                    char header;
                    short val;
                }
            """,
        )

        self.assertEqual(dom.header_0, ord("a"))
        self.assertEqual(dom.val_0, 1)

        self.assertEqual(dom.header_1, ord("0"))
        self.assertEqual(dom.val_1, 2)

    def test_auto_increment_but_still_reference_last_decl_normal(self):
        """
        Increment the auto auto auto auto auto auto auto auto auto auto auto auto auto auto auto auto auto auto auto auto auto auto auto auto auto auto auto

        Args:
            self: (todo): write your description
        """
        # this is an interesting behavior of 010 scripts. When a field
        # is repeatedly declared, 010 scripts do not append a suffix to
        # the field names. However, since our goal is manipulation and being
        # able to access these fields individually, we do add a suffix.
        # the problem is that the script still needs to be able to access
        # the last declared field by the original name and not the
        # suffixed one.
        dom = self._test_parse_build(
            "\x01a\x01b\x01c",
            """
                while(!FEof()) {
                    char length;
                    char str[length];
                    Printf("%s|", str);
                }
            """,
            stdout="a|b|c|",
        )

    def test_implicit_array_dot_notation_for_last(self):
        """
        Test if the test cross - product.

        Args:
            self: (todo): write your description
        """
        # I BELIEVE scripts are able to access implicit array items
        # by index OR directly access the last one without an index
        dom = self._test_parse_build(
            "\x01a\x01b\x01c",
            """
                typedef struct {
                    uchar length;
                    char str[length];
                } STR;

                local int total_length = 0;
                while(!FEof()) {
                    STR str;
                    total_length += str.length;
                }
                Printf("%d", total_length);
            """,
            stdout="3",
        )

    def test_struct_iter(self):
        """Test struct children iteration.
        """
        dom = self._test_parse_build(
            "ABC",
            """
                typedef struct {
                    char first;
                    char second;
                    char third;
                } three_bytes;

                three_bytes bytes;
            """,
        )
        chars = [x for x in dom.bytes]
        self.assertEquals(chars[0], 0x41)
        self.assertEquals(chars[1], 0x42)
        self.assertEquals(chars[2], 0x43)


if __name__ == "__main__":
    unittest.main()
