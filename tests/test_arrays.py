#!/usr/bin/env python
# encoding: utf-8

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


class TestArrays(utils.PfpTestCase):
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

    def _do_parse(self, field, data):
        """
        Parse the field.

        Args:
            self: (todo): write your description
            field: (todo): write your description
            data: (todo): write your description
        """
        field._pfp__parse(StringIO(data))

    def _do_endian_tests(self, field, format):
        """
        Endian - endian struct.

        Args:
            self: (todo): write your description
            field: (todo): write your description
            format: (str): write your description
        """
        field.endian = pfp.fields.BIG_ENDIAN
        self._do_parse(field, struct.pack(">" + format, 1))
        self.assertEqual(field, 1)

        field.endian = pfp.fields.LITTLE_ENDIAN
        self._do_parse(field, struct.pack("<" + format, 1))
        self.assertEqual(field, 1)

    def test_char_array(self):
        """
        Parse array.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "AABBCC",
            """
                char blah[6];
            """,
        )
        self.assertEqual(dom.blah[0], ord("A"))
        self.assertEqual(dom.blah[1], ord("A"))
        self.assertEqual(dom.blah[2], ord("B"))
        self.assertEqual(dom.blah[3], ord("B"))
        self.assertEqual(dom.blah[4], ord("C"))
        self.assertEqual(dom.blah[5], ord("C"))

        with self.assertRaises(IndexError):
            dom.blah[6]

        with self.assertRaises(TypeError):
            dom.blah["hello"]

        dom.blah[5] = 10
        self.assertEqual(dom.blah[5], 10)

    def test_char_array_string_compare(self):
        """
        Compares the test string.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "AABBCC",
            """
                char blah[6];
                if(blah == "AABBCC") {
                    Printf("true");
                }
            """,
            stdout="true",
        )

    def test_implicit_array_basic(self):
        """
        Equalizes the cross validation.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "ABCD",
            """
                while(!FEof()) {
                    char chars;
                }
            """,
        )
        self.assertEqual(len(dom.chars), 4)
        self.assertEqual(dom.chars[0], ord("A"))
        self.assertEqual(dom.chars[1], ord("B"))
        self.assertEqual(dom.chars[2], ord("C"))
        self.assertEqual(dom.chars[3], ord("D"))

    def test_implicit_array_same_behavior_as_010(self):
        """
        Test if the element - wise cross - cross - validation.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "ABCD",
            """
                while(!FEof()) {
                    char x;
                    Printf("%c", x);
                }
            """,
            stdout="ABCD",
        )
        self.assertIsInstance(dom.x, Array)
        self.assertEqual(dom.x, b"ABCD")

    def test_array_length1(self):
        """
        Compute the length of the element - wise length.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "abcd",
            """
                char chars[4];
            """,
        )
        self.assertEqual(dom.chars[0], ord("a"))
        self.assertEqual(dom.chars[1], ord("b"))
        self.assertEqual(dom.chars[2], ord("c"))
        self.assertEqual(dom.chars[3], ord("d"))
        # this broke because of the Array.raw_data optimization
        self.assertEqual(len(dom.chars), 4)

    def test_implicit_array_complex(self):
        """
        Equalizes the element - like.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "\x01A\x02B\x03C",
            """
                typedef struct {
                    uchar some_val;
                    char some_char;
                } some_struct;

                local int i = 0;
                for(i = 0; i < 3; i++) {
                    some_struct structs;
                }
            """,
        )
        self.assertEqual(len(dom.structs), 3)
        self.assertEqual(dom.structs[0].some_val, 0x01)
        self.assertEqual(dom.structs[1].some_val, 0x02)
        self.assertEqual(dom.structs[2].some_val, 0x03)
        self.assertEqual(dom.structs[0].some_char, 0x41)
        self.assertEqual(dom.structs[1].some_char, 0x42)
        self.assertEqual(dom.structs[2].some_char, 0x43)

    def test_array_ref(self):
        """
        The test test test test test test test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "abcd",
            """
                char bytes[4];
                Printf("%02x", bytes[0]);
            """,
            stdout="61",
        )

    def test_array_initialization(self):
        """
        Sets the initial test data.

        Args:
            self: (todo): write your description
        """
        # was having problems with array decls _always_ parsing the
        # input stream
        dom = self._test_parse_build(
            "",
            """
                local uchar blah[2] = { 'a', 'b' };
                Printf("%s", blah);
            """,
            stdout="ab",
        )

    def test_struct_array_decl(self):
        """
        Declare struct struct struct struct structs

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "abcd",
            """
                struct {
                    uchar blah;
                } structs[4];
            """,
        )

    def test_typedefd_array(self):
        """
        Create an array data array for an array.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "abcd",
            """
                typedef uchar BLAH[2];

                BLAH blah1;
                BLAH blah2;
            """,
            predefines=False,
        )

        self.assertEqual(PYSTR(dom.blah1), "ab")
        self.assertEqual(PYSTR(dom.blah2), "cd")

    def test_struct_raw_data_optmization1(self):
        """
        Run test test test test test test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "abcd",
            """
                struct {
                    uchar blah;
                } structs[4];
            """,
        )
        self.assertEqual(dom.structs.raw_data, None)

    def test_struct_raw_data_optmization2(self):
        """
        Compute the static data.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "abcd",
            """
                uchar chars[4];
            """,
        )
        self.assertNotEqual(dom.chars.raw_data, None)
        self.assertEqual(dom.chars.raw_data, pfp.utils.binary("abcd"))
        self.assertEqual(dom.chars._array_to_str(), pfp.utils.binary("abcd"))
        self.assertEqual(dom.chars[0], ord("a"))
        self.assertEqual(dom.chars[1], ord("b"))
        self.assertEqual(dom.chars[2], ord("c"))
        self.assertEqual(dom.chars[3], ord("d"))

        dom.chars[0] = ord("A")
        self.assertEqual(dom.chars.raw_data, pfp.utils.binary("Abcd"))
        self.assertEqual(dom.chars._array_to_str(), pfp.utils.binary("Abcd"))
        self.assertEqual(dom.chars[0], ord("A"))
        self.assertEqual(dom.chars[1], ord("b"))
        self.assertEqual(dom.chars[2], ord("c"))
        self.assertEqual(dom.chars[3], ord("d"))

        dom.chars[1] = ord("B")
        self.assertEqual(dom.chars.raw_data, pfp.utils.binary("ABcd"))
        self.assertEqual(dom.chars._array_to_str(), pfp.utils.binary("ABcd"))
        self.assertEqual(dom.chars[0], ord("A"))
        self.assertEqual(dom.chars[1], ord("B"))
        self.assertEqual(dom.chars[2], ord("c"))
        self.assertEqual(dom.chars[3], ord("d"))

        dom.chars[2] = ord("C")
        self.assertEqual(dom.chars.raw_data, pfp.utils.binary("ABCd"))
        self.assertEqual(dom.chars._array_to_str(), pfp.utils.binary("ABCd"))
        self.assertEqual(dom.chars[0], ord("A"))
        self.assertEqual(dom.chars[1], ord("B"))
        self.assertEqual(dom.chars[2], ord("C"))
        self.assertEqual(dom.chars[3], ord("d"))

        dom.chars[3] = ord("D")
        self.assertEqual(dom.chars.raw_data, pfp.utils.binary("ABCD"))
        self.assertEqual(dom.chars._array_to_str(), pfp.utils.binary("ABCD"))
        self.assertEqual(dom.chars[0], ord("A"))
        self.assertEqual(dom.chars[1], ord("B"))
        self.assertEqual(dom.chars[2], ord("C"))
        self.assertEqual(dom.chars[3], ord("D"))

    def test_implicit_single_item_array1(self):
        """
        Equal a cross - element.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "\x01",
            """
                uchar blah;
                local uchar a = blah[0];
            """,
        )
        self.assertEqual(dom.blah, 1)
        self.assertEqual(dom.a, 1)

    def test_implicit_single_item_array2(self):
        """
        Equalizes a cross - wise array.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "aaaa",
            """
                int blah;
                local int a = blah[0];
            """,
        )
        self.assertEqual(dom.blah, 0x61616161)
        self.assertEqual(dom.a, 0x61616161)

    def test_implicit_single_item_array3(self):
        """
        Test for an element in - wise.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "aaaa",
            """
                struct {
                    int blah;
                } test;
                local int a = test[0].blah;
            """,
        )
        self.assertEqual(dom.test.blah, 0x61616161)
        self.assertEqual(dom.a, 0x61616161)

    # see #54 - after overwriting all items in an array with a new
    # list, fetching individual items does not work (attemps to pull
    # the "current" item data its raw data, instead of from the items)
    def test_array_overwrite_fetch(self):
        """
        Overwrite the test array.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
                typedef struct {
                    uint array[1];
                } TestStruct;
            """,
        )
        struct = dom.TestStruct()
        struct.array = [0xFFFF]
        self.assertEqual(struct.array[0], 0xFFFF)

    def test_array_iter(self):
        """Test array item iteration.
        """
        dom = self._test_parse_build(
            "ABCDEFGHI",
            """
                typedef struct {
                    char first;
                    char second;
                    char third;
                } three_bytes;

                three_bytes three_three_bytes[3];
            """,
        )
        items = [x for x in dom.three_three_bytes]
        self.assertEqual(items[0].first, 0x41)
        self.assertEqual(items[0].second, 0x42)
        self.assertEqual(items[0].third, 0x43)
        self.assertEqual(items[1].first, 0x44)
        self.assertEqual(items[1].second, 0x45)
        self.assertEqual(items[1].third, 0x46)
        self.assertEqual(items[2].first, 0x47)
        self.assertEqual(items[2].second, 0x48)
        self.assertEqual(items[2].third, 0x49)

    def test_array_with_root_scope(self):
        """
        Sets the test test scope.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "\x00\x01\x02\x03",
            """
                typedef struct {
                    char a_byte;
                    Printf("%02x|", item[0].a_byte);
                } simple_struct;

                while (!FEof()) {
                    simple_struct item;
                }
            """,
            stdout="00|00|00|00|",
        )


if __name__ == "__main__":
    unittest.main()
