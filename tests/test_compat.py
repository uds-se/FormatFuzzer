#!/usr/bin/env python
# encoding: utf-8

import os
import six
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pfp
import pfp.fields
import pfp.interp
import pfp.utils

import utils


class TestCompat(utils.PfpTestCase):
    def setUp(self):
        """
        Set the start and end numbers.

        Args:
            self: (todo): write your description
        """
        self._start_endian = pfp.fields.NumberBase.endian

    def tearDown(self):
        """
        Tear down the start of the file.

        Args:
            self: (todo): write your description
        """
        pfp.fields.NumberBase.endian = self._start_endian

    def test_big_endian(self):
        """
        A big - big endian field.

        Args:
            self: (todo): write your description
        """
        # just something different so that we know it changed
        pfp.fields.NumberBase.endian = pfp.fields.LITTLE_ENDIAN
        dom = self._test_parse_build(
            "",
            """
                BigEndian();
            """,
        )
        self.assertEqual(pfp.fields.NumberBase.endian, pfp.fields.BIG_ENDIAN)

    def test_little_endian(self):
        """
        Write the fields that fields

        Args:
            self: (todo): write your description
        """
        # just something different so that we know it changed
        pfp.fields.NumberBase.endian = pfp.fields.BIG_ENDIAN
        dom = self._test_parse_build(
            "",
            """
                LittleEndian();
            """,
        )
        self.assertEqual(
            pfp.fields.NumberBase.endian, pfp.fields.LITTLE_ENDIAN
        )

    def test_file_size(self):
        """
        Test if the test test.

        Args:
            self: (todo): write your description
        """
        input_ = six.StringIO("ABCDE")
        output_ = six.StringIO()
        sys.stdout = output_
        dom = pfp.parse(
            input_,
            """
            Printf("%d", FileSize());
            """,
        )
        sys.stdout = sys.__stdout__

        self.assertEqual(output_.getvalue(), "5")


class TestCompatInterface(utils.PfpTestCase):
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

    def test_boolean_constants(self):
        """
        Parse the test constants.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
            local int bool_val;
            bool_val = true;
            bool_val = True;
            bool_val = TRUE;

            bool_val = false;
            bool_val = False;
            bool_val = FALSE;
            """,
            predefines=True,
        )

    def test_color_constants(self):
        """
        Finds the test case.

        Args:
            self: (todo): write your description
        """
        # shouldn't error
        dom = self._test_parse_build(
            "",
            """
            local int color;
            color = cBlack;
            color = cRed;
            color = cDkRed;
            color = cLtRed;
            color = cGreen;
            color = cDkGreen;
            color = cLtGreen;
            color = cBlue;
            color = cDkBlue;
            color = cLtBlue;
            color = cPurple;
            color = cDkPurple;
            color = cLtPurple;
            color = cAqua;
            color = cDkAqua;
            color = cLtAqua;
            color = cYellow;
            color = cDkYellow;
            color = cLtYellow;
            color = cDkGray;
            color = cGray;
            color = cSilver;
            color = cLtGray;
            color = cWhite;
            color = cNone;
            """,
            predefines=True,
        )


class TestCompatIO(utils.PfpTestCase):
    def setUp(self):
        """
        Set the re - of - fields fields.

        Args:
            self: (todo): write your description
        """
        pfp.fields.NumberBase.endian = pfp.fields.BIG_ENDIAN

    def tearDown(self):
        """
        Tear down the next callable.

        Args:
            self: (todo): write your description
        """
        pass

    def test_read_ushort(self):
        """
        Run test test test test test test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "\x80\x01",
            """
                BigEndian();
                local ushort blah = ReadUShort();
                Printf("%d|", blah);
                Printf("%d", FTell());
            """,
            stdout="32769|0",
        )

    def test_read_bytes_uchar(self):
        """
        Read test test test test test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "ab\x00\x01",
            """
                local uchar data[2];
                ReadBytes(data, FTell(), 2);
                Printf(data);

                uchar a;
                uchar b;
                Printf("%d%d", a, b);
            """,
            stdout="ab9798",
        )

    def test_seek1(self):
        """
        Test to the dom of the specified in the dom.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "\x01\x02ABCD\x03\x04",
            """
                uchar a;
                uchar b;
                FSeek(FTell() + 4);
                uchar c;
                uchar d;
            """,
        )

        self.assertEqual(dom.a, 1)
        self.assertEqual(dom.b, 2)
        self.assertEqual(dom._skipped, "ABCD")
        self.assertEqual(dom.c, 3)
        self.assertEqual(dom.d, 4)

    def test_seek2(self):
        """
        Test for tests in - specific dom.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "\x01\x02ABCD\x03EF\x04",
            """
                uchar a;
                uchar b;
                FSeek(FTell() + 2);
                FSeek(FTell() + 2);
                uchar c;
                FSeek(FTell() + 2);
                uchar d;
            """,
        )

        self.assertEqual(dom.a, 1)
        self.assertEqual(dom.b, 2)
        # should be merged into one _skipped array
        self.assertEqual(dom._skipped_0, "ABCD")
        self.assertEqual(dom.c, 3)
        self.assertEqual(dom._skipped_1, "EF")
        self.assertEqual(dom.d, 4)

    def test_seek3(self):
        """
        Test to test test test test test test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "ABCD",
            """
                Printf("%d", FSeek(FTell() + 4));
                Printf("%d", FSeek(FTell() + 2));
            """,
            stdout="0-1",
        )

    def test_seek4(self):
        """
        Test if the dom position.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "ABCD",
            """
                local int pos1 = FTell();
                local int rv1 = FSeek(1);
                local int pos2 = FTell();
                local int rv2 = FSeek(2);
                local int pos3 = FTell();
                local int rv3 = FSeek(0x1000);
                local int pos4 = FTell();
                local int rv4 = FSeek(FileSize());
                local int pos5 = FTell();
                local int rv5 = FSeek(-0x1000);
                local int pos6 = FTell();
                local int rv6 = FSeek(0);
                local int pos7 = FTell();
            """,
        )
        self.assertEqual(dom.pos1, 0)
        self.assertEqual(dom.rv1, 0)
        self.assertEqual(dom.pos2, 1)
        self.assertEqual(dom.rv2, 0)
        self.assertEqual(dom.pos3, 2)
        self.assertEqual(dom.rv3, -1)
        self.assertEqual(dom.pos4, 4)
        self.assertEqual(dom.rv4, 0)
        self.assertEqual(dom.pos5, 4)
        self.assertEqual(dom.rv5, -1)
        self.assertEqual(dom.pos6, 0)
        self.assertEqual(dom.rv6, 0)
        self.assertEqual(dom.pos7, 0)

    def test_skip1(self):
        """
        Compute cross - section.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "\x01\x02ABCD\x03\x04",
            """
                uchar a;
                uchar b;
                FSkip(4);
                uchar c;
                uchar d;
            """,
        )

        self.assertEqual(dom.a, 1)
        self.assertEqual(dom.b, 2)
        self.assertEqual(dom._skipped, "ABCD")
        self.assertEqual(dom.c, 3)
        self.assertEqual(dom.d, 4)

    def test_skip2(self):
        """
        Determine the cross validation.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "\x01\x02ABCD\x03EF\x04",
            """
                uchar a;
                uchar b;
                FSkip(2);
                FSkip(2);
                uchar c;
                FSkip(2);
                uchar d;
            """,
        )

        self.assertEqual(dom.a, 1)
        self.assertEqual(dom.b, 2)
        # should be merged into one _skipped array
        self.assertEqual(dom._skipped_0, "ABCD")
        self.assertEqual(dom.c, 3)
        self.assertEqual(dom._skipped_1, "EF")
        self.assertEqual(dom.d, 4)

    def test_skip3(self):
        """
        Compute the dom.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "ABCD",
            """
                local int fskip_rv1 = FSkip(1);
                local int pos1 = FTell();
                uchar b;
                uchar c;
                local int fskip_rv2 = FSkip(3);
                local int pos2 = FTell();
            """,
        )
        self.assertEqual(dom.fskip_rv1, 0)
        self.assertEqual(dom.pos1, 1)
        self.assertEqual(dom.b, ord("B"))
        self.assertEqual(dom.c, ord("C"))
        self.assertEqual(dom.fskip_rv2, -1)
        self.assertEqual(dom.pos2, 4)


class TestCompatString(utils.PfpTestCase):
    def setup(self):
        """
        Set up a new setup.

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

    def test_memcpy1(self):
        """
        Perform test test test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "abcd",
            """
            uchar bytes[4];
            local uchar local_bytes[4];
            Memcpy(local_bytes, bytes, 4);

            Printf(local_bytes);
            """,
            stdout="abcd",
        )

    def test_memcpy2(self):
        """
        Computes test test test test test test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "abcd",
            """
            uchar bytes[4];
            local uchar local_bytes[4];
            Memcpy(local_bytes, bytes, 4);

            local uint i;
            for(i = 0; i < 4; i++) {
                local_bytes[3 - i] = local_bytes[i];
            }
            Printf(local_bytes);
            Printf(bytes);
            """,
            stdout="abbaabcd",
        )

    def test_strchr1(self):
        """
        Test the test test test test test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
            local char b[30] = "hellogoodbyte";
            Printf("%d", Strchr(b, 'g'));
            """,
            stdout="5",
        )

    def test_strchr2(self):
        """
        Generate test test test test test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
            local char b[30] = "hellogoodbyte";
            Printf("%d", Strchr(b, 'X'));
            """,
            stdout="-1",
        )

    def test_strcpy(self):
        """
        Parse the test test test test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
            local char a[0];
            Printf("%s", a);

            local char b[30] = "hellogoodbyte";
            Printf("%s", b);

            Strcpy(a, b);
            Printf("%s", a);
            """,
            stdout="hellogoodbyte\x00hellogoodbyte\x00",
        )

    def test_strncpy(self):
        """
        Parse test test test test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
            local char a[0];
            Printf("%s", a);

            local char b[30] = "hellogoodbyte";
            Printf("%s", b);

            Strncpy(a, b, 5);
            Printf("%s", a);
            """,
            stdout="hellogoodbyte\x00hello",
        )

    def test_strcmp1(self):
        """
        Test for test test test files.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
            local string a = "hellothere";
            local string b = "hellogoodbyte";
            Printf("%d", Strcmp(a, b));
            """,
            stdout="1",
        )

    def test_strcmp2(self):
        """
        Test if test test test files.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
            local string a = "hello";
            local string b = "hello";
            Printf("%d", Strcmp(a, b));
            """,
            stdout="0",
        )

    def test_stricmp1(self):
        """
        Build test test test test test test test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
            local string a = "helLotherE";
            local string b = "hEllogoOdbyte";
            Printf("%d", Stricmp(a, b));
            """,
            stdout="1",
        )

    def test_stricmp2(self):
        """
        Test for test test test test test test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
            local string a = "hElLo";
            local string b = "HeLlo";
            Printf("%d", Stricmp(a, b));
            """,
            stdout="0",
        )

    def test_strncmp1(self):
        """
        Test for test test test files

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
            local string a = "hellothere";
            local string b = "hellogoodbyte";
            Printf("%d", Strncmp(a, b, 5));
            """,
            stdout="0",
        )

    def test_strncmp2(self):
        """
        Test for test test test test test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
            local string a = "hellothere";
            local string b = "hellogoodbyte";
            Printf("%d", Strncmp(a, b, 6));
            """,
            stdout="1",
        )

    def test_strnicmp1(self):
        """
        Test test test test test test test test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
            local string a = "hElLothere";
            local string b = "HeLlOgoodbyte";
            Printf("%d", Strnicmp(a, b, 5));
            """,
            stdout="0",
        )

    def test_strnicmp2(self):
        """
        Test for test test test test test

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
            local string a = "hElLOthere";
            local string b = "helLogoOdbyte";
            Printf("%d", Strnicmp(a, b, 6));
            """,
            stdout="1",
        )

    def test_strstr1(self):
        """
        Generate test test test test test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
            local string a = "hellothere";
            Printf("%d", Strstr(a, "llo"));
            """,
            stdout="2",
        )

    def test_strstr2(self):
        """
        Convert test - test test test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            """
            local string a = "hellothere";
            Printf("%d", Strstr(a, "lloZ"));
            """,
            stdout="-1",
        )

    def test_memcmp(self):
        """
        Called when the test tests.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "",
            r"""
            local string a = "hellothere";
            local string b = "helloblah";
            Printf("%d\n", Memcmp(a, b, 1));
            Printf("%d\n", Memcmp(a, b, 2));
            Printf("%d\n", Memcmp(a, b, 3));
            Printf("%d\n", Memcmp(a, b, 4));
            Printf("%d\n", Memcmp(a, b, 5));
            Printf("%d\n", Memcmp(a, b, 6));
            Printf("%d\n", Memcmp(b, a, 6));
            """,
            stdout="0\n0\n0\n0\n0\n1\n-1\n",
        )


class TestCompatTools(utils.PfpTestCase):
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

    def test_find_all1(self):
        """
        Searches for test test test test results.

        Args:
            self: (todo): write your description
        """
        # TODO maybe we should just expose all defined fields/locals/types/vars/etc
        # to the user? then could just directly test dom.results...
        #
        # I like having it a bit cleaner though and not cluttered with
        # all of the locals.
        dom = self._test_parse_build(
            "abcd HELLO THERE HELLO blah HELLO blkajsdf",
            """
                local TFindResults results = FindAll("HELLO");
                Printf("count:%d", results.count);
                for(local int i = 0 ; i < results.count; i++) {
                    Printf("start-size:%d-%d", results.start[i], results.size[i]);
                }
            """,
            stdout="count:3start-size:5-5start-size:17-5start-size:28-5",
            predefines=True,
        )

    def test_find_all2(self):
        """
        Searches for test test test test test test test test

        Args:
            self: (todo): write your description
        """
        # TODO maybe we should just expose all defined fields/locals/types/vars/etc
        # to the user? then could just directly test dom.results...
        #
        # I like having it a bit cleaner though and not cluttered with
        # all of the locals.
        dom = self._test_parse_build(
            "abcd HELLO THERE HELLO blah HELLO blkajsdf",
            """
                local TFindResults results = FindAll("HELLO");
                Printf("count:%d", results.count);
                for(local int i = 0 ; i < results.count; i++) {
                    Printf("start-size:%d-%d", results.start[i], results.size[i]);
                }
            """,
            stdout="count:3start-size:5-5start-size:17-5start-size:28-5",
            predefines=True,
        )

    def test_find_all_no_match_case(self):
        """
        Find all test case case - test case - match.

        Args:
            self: (todo): write your description
        """
        # TODO maybe we should just expose all defined fields/locals/types/vars/etc
        # to the user? then could just directly test dom.results...
        #
        # I like having it a bit cleaner though and not cluttered with
        # all of the locals.
        dom = self._test_parse_build(
            "abcd HELLO THERE HELLO blah HellO blkajsdf",
            """
                local TFindResults results = FindAll("HELLO", 0/*match case*/);
                Printf("count:%d", results.count);
                for(local int i = 0 ; i < results.count; i++) {
                    Printf("start-size:%d-%d", results.start[i], results.size[i]);
                }
            """,
            stdout="count:3start-size:5-5start-size:17-5start-size:28-5",
            predefines=True,
        )

    def test_find_all_whole_words_only(self):
        """
        Finds all the test terms.

        Args:
            self: (todo): write your description
        """
        # TODO maybe we should just expose all defined fields/locals/types/vars/etc
        # to the user? then could just directly test dom.results...
        #
        # I like having it a bit cleaner though and not cluttered with
        # all of the locals.
        dom = self._test_parse_build(
            "abcd HELLO THHELLOERE HELLO blah HELLO blkajsdf",
            """
                local TFindResults results = FindAll("HELLO", 1/*match case*/, 1/*whole words only*/);
                Printf("count:%d", results.count);
                for(local int i = 0 ; i < results.count; i++) {
                    Printf("start-size:%d-%d", results.start[i], results.size[i]);
                }
            """,
            stdout="count:3start-size:5-5start-size:22-5start-size:33-5",
            predefines=True,
        )

    def test_find_all_wildcards(self):
        """
        Find all wildcard wildcards.

        Args:
            self: (todo): write your description
        """
        # TODO maybe we should just expose all defined fields/locals/types/vars/etc
        # to the user? then could just directly test dom.results...
        #
        # I like having it a bit cleaner though and not cluttered with
        # all of the locals.
        dom = self._test_parse_build(
            "abcd HELLO THHELLOERE HELLO blah HELLO blkajsdf",
            """
                local TFindResults results = FindAll(
                    "HE??O",
                    1/*match case*/,
                    1/*whole words only*/,
                    FINDMETHOD_WILDCARDS
                );
                Printf("count:%d", results.count);
                for(local int i = 0 ; i < results.count; i++) {
                    Printf("start-size:%d-%d", results.start[i], results.size[i]);
                }
            """,
            stdout="count:3start-size:5-5start-size:22-5start-size:33-5",
            predefines=True,
        )

    def test_find_all_wildcards2(self):
        """
        Find all wildcards for all test tests.

        Args:
            self: (todo): write your description
        """
        # TODO maybe we should just expose all defined fields/locals/types/vars/etc
        # to the user? then could just directly test dom.results...
        #
        # I like having it a bit cleaner though and not cluttered with
        # all of the locals.
        dom = self._test_parse_build(
            "abcd HELLO abcd HELLO abcd HELLO abcd",
            """
                local TFindResults results = FindAll(
                    "H*O",
                    1/*match case*/,
                    1/*whole words only*/,
                    FINDMETHOD_WILDCARDS
                );
                Printf("count:%d", results.count);
                for(local int i = 0 ; i < results.count; i++) {
                    Printf("start-size:%d-%d", results.start[i], results.size[i]);
                }
            """,
            stdout="count:3start-size:5-5start-size:16-5start-size:27-5",
            predefines=True,
        )

    def test_find_all_with_size(self):
        """
        Find all test test test test test test results.

        Args:
            self: (todo): write your description
        """
        # TODO maybe we should just expose all defined fields/locals/types/vars/etc
        # to the user? then could just directly test dom.results...
        #
        # I like having it a bit cleaner though and not cluttered with
        # all of the locals.
        dom = self._test_parse_build(
            "abcd HELLO abcd HELLO abcd HELLO abcd",
            """
                local TFindResults results = FindAll(
                    "H*O",
                    1/*match case*/,
                    1/*whole words only*/,
                    FINDMETHOD_WILDCARDS,
                    0.0/*tolerance*/,
                    1/*dir*/,
                    4,/*start*/
                    17/*size*/
                );
                Printf("count:%d", results.count);
                for(local int i = 0 ; i < results.count; i++) {
                    Printf("start-size:%d-%d", results.start[i], results.size[i]);
                }
            """,
            stdout="count:2start-size:5-5start-size:16-5",
            predefines=True,
        )

    def test_find_first_next(self):
        """
        Searches for next test.

        Args:
            self: (todo): write your description
        """
        dom = self._test_parse_build(
            "abcd HELLO defg HELLO hijk HELLO",
            """
                local uint index = FindFirst("HELLO");
                Printf("%d,", index);
                index = FindNext();
                Printf("%d,", index);
                index = FindNext();
                Printf("%d", index);
            """,
            stdout="5,16,27",
        )


if __name__ == "__main__":
    unittest.main()
