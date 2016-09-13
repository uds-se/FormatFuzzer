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
        self._start_endian = pfp.fields.NumberBase.endian
    
    def tearDown(self):
        pfp.fields.NumberBase.endian = self._start_endian
    
    def test_big_endian(self):
        # just something different so that we know it changed
        pfp.fields.NumberBase.endian = pfp.fields.LITTLE_ENDIAN
        dom = self._test_parse_build(
            "",
            """
                BigEndian();
            """
        )
        self.assertEqual(pfp.fields.NumberBase.endian, pfp.fields.BIG_ENDIAN)

    def test_little_endian(self):
        # just something different so that we know it changed
        pfp.fields.NumberBase.endian = pfp.fields.BIG_ENDIAN
        dom = self._test_parse_build(
            "",
            """
                LittleEndian();
            """
        )
        self.assertEqual(pfp.fields.NumberBase.endian, pfp.fields.LITTLE_ENDIAN)
    
    def test_file_size(self):
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
        pass
    
    def tearDown(self):
        pass
    
    def test_color_constants(self):
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
            predefines=True
        )

class TestCompatIO(utils.PfpTestCase):
    def setUp(self):
        pfp.fields.NumberBase.endian = pfp.fields.BIG_ENDIAN
    
    def tearDown(self):
        pass
    
    def test_read_ushort(self):
        dom = self._test_parse_build(
            "\x80\x01",
            """
                local ushort blah = ReadUShort();
                Printf("%d|", blah);
                Printf("%d", FTell());
            """,
            verify=False,
            stdout="32769|0"
        )
    
    def test_read_bytes_uchar(self):
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
            verify=False,
            stdout="ab9798"
        )
    
    def test_seek1(self):
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
        dom = self._test_parse_build(
            "ABCD",
            """
                Printf("%d", FSeek(FTell() + 4));
                Printf("%d", FSeek(FTell() + 2));
            """,
            verify=False,
            stdout="0-1"
        )
    
    def test_seek4(self):
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
            verify=False
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
            verify=False,
        )
        self.assertEqual(dom.fskip_rv1, 0)
        self.assertEqual(dom.pos1, 1)
        self.assertEqual(dom.b, ord("B"))
        self.assertEqual(dom.c, ord("C"))
        self.assertEqual(dom.fskip_rv2, -1)
        self.assertEqual(dom.pos2, 4)

class TestCompatString(utils.PfpTestCase):
    def setup(self):
        pass
    
    def tearDown(self):
        pass
    
    def test_memcpy1(self):
        dom = self._test_parse_build(
            "abcd",
            """
            uchar bytes[4];
            local uchar local_bytes[4];
            Memcpy(local_bytes, bytes, 4);

            Printf(local_bytes);
            """,
            stdout="abcd"
        )
    
    def test_memcpy2(self):
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
            stdout="abbaabcd"
        )
    
    def test_strchr1(self):
        dom = self._test_parse_build(
            "",
            """
            local char b[30] = "hellogoodbyte";
            Printf("%d", Strchr(b, 'g'));
            """,
            stdout="5"
        )
    
    def test_strchr2(self):
        dom = self._test_parse_build(
            "",
            """
            local char b[30] = "hellogoodbyte";
            Printf("%d", Strchr(b, 'X'));
            """,
            stdout="-1"
        )
    
    def test_strcpy(self):
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
            stdout="hellogoodbyte\x00hellogoodbyte\x00"
        )
    
    def test_strncpy(self):
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
            stdout="hellogoodbyte\x00hello"
        )
    
    def test_strcmp1(self):
        dom = self._test_parse_build(
            "",
            """
            local string a = "hellothere";
            local string b = "hellogoodbyte";
            Printf("%d", Strcmp(a, b));
            """,
            stdout="1"
        )
    
    def test_strcmp2(self):
        dom = self._test_parse_build(
            "",
            """
            local string a = "hello";
            local string b = "hello";
            Printf("%d", Strcmp(a, b));
            """,
            stdout="0"
        )

    def test_stricmp1(self):
        dom = self._test_parse_build(
            "",
            """
            local string a = "helLotherE";
            local string b = "hEllogoOdbyte";
            Printf("%d", Stricmp(a, b));
            """,
            stdout="1"
        )
    
    def test_stricmp2(self):
        dom = self._test_parse_build(
            "",
            """
            local string a = "hElLo";
            local string b = "HeLlo";
            Printf("%d", Stricmp(a, b));
            """,
            stdout="0"
        )
    
    def test_strncmp1(self):
        dom = self._test_parse_build(
            "",
            """
            local string a = "hellothere";
            local string b = "hellogoodbyte";
            Printf("%d", Strncmp(a, b, 5));
            """,
            stdout="0"
        )
    
    def test_strncmp2(self):
        dom = self._test_parse_build(
            "",
            """
            local string a = "hellothere";
            local string b = "hellogoodbyte";
            Printf("%d", Strncmp(a, b, 6));
            """,
            stdout="1"
        )
    
    
    def test_strnicmp1(self):
        dom = self._test_parse_build(
            "",
            """
            local string a = "hElLothere";
            local string b = "HeLlOgoodbyte";
            Printf("%d", Strnicmp(a, b, 5));
            """,
            stdout="0"
        )
    
    def test_strnicmp2(self):
        dom = self._test_parse_build(
            "",
            """
            local string a = "hElLOthere";
            local string b = "helLogoOdbyte";
            Printf("%d", Strnicmp(a, b, 6));
            """,
            stdout="1"
        )
    
    def test_strstr1(self):
        dom = self._test_parse_build(
            "",
            """
            local string a = "hellothere";
            Printf("%d", Strstr(a, "llo"));
            """,
            stdout="2"
        )
    
    def test_strstr2(self):
        dom = self._test_parse_build(
            "",
            """
            local string a = "hellothere";
            Printf("%d", Strstr(a, "lloZ"));
            """,
            stdout="-1"
        )

class TestCompatTools(utils.PfpTestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def test_find_all1(self):
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
            verify=False,
            predefines=True
        )
    
    def test_find_all2(self):
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
            verify=False,
            predefines=True
        )
    
    def test_find_all_no_match_case(self):
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
            verify=False,
            predefines=True
        )
    
    def test_find_all_whole_words_only(self):
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
            verify=False,
            predefines=True
        )

    def test_find_all_wildcards(self):
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
            verify=False,
            predefines=True
        )

    def test_find_all_wildcards2(self):
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
            verify=False,
            predefines=True
        )

    def test_find_all_with_size(self):
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
            verify=False,
            predefines=True
        )
    
    
    def test_find_first_next(self):
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
            verify=False,
            stdout="5,16,27"
        )

if __name__ == "__main__":
    unittest.main()
