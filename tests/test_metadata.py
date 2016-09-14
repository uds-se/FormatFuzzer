#!/usr/bin/env python
# encoding: utf-8

import binascii
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


class TestMetadata(utils.PfpTestCase):
    def setUp(self):
        pfp.fields.NumberBase.endian = pfp.fields.BIG_ENDIAN
    
    def tearDown(self):
        pass
    
#< format=hex|decimal|octal|binary,
#     fgcolor=<color>,
#     bgcolor=<color>,
#     comment="<string>"|<function_name>,
#     name="<string>"|<function_name>,
#     open=true|false|suppress,
#     hidden=true|false,
#     read=<function_name>,
#     write=<function_name>
#     size=<number>|<function_name> >
    def test_metadata_watch_interpd(self):
        dom = self._test_parse_build(
            "\x05\x07",
            """
                void PlusTwo(int &to_update, int watched) {
                    to_update = watched + 2;
                }

                uchar hello;
                uchar blah<watch=hello,update=PlusTwo>;
            """
        )
        self.assertEqual(dom.hello, 5)
        self.assertEqual(dom.blah, 7)

        dom.hello = 20

        self.assertEqual(dom.hello, 20)
        self.assertEqual(dom.blah, 22)

    def test_metadata_watch_native(self):
        def plus_two(params, ctxt, scope, stream, coord):
            params[0]._pfp__set_value(params[1] + 2)

        interp = pfp.interp.PfpInterp()
        interp.add_native(name="PlusTwo", func=plus_two, ret=pfp.fields.Void)

        dom = self._test_parse_build(
            "\x05\x07",
            """
                uchar hello;
                uchar blah<watch=hello,update=PlusTwo>;
            """
        )
        self.assertEqual(dom.hello, 5)
        self.assertEqual(dom.blah, 7)

        dom.hello = 20

        self.assertEqual(dom.hello, 20)
        self.assertEqual(dom.blah, 22)
    
    def test_metadata_watch_struct(self):
        dom = self._test_parse_build(
            "\x02\x03\xff\x05",
            """
                void TwoFieldsPlusTwo(char &to_update, some_type &watched) {
                    to_update = watched.a + watched.b;
                }

                typedef struct {
                    uchar a;
                    uchar b;
                    uchar c;
                } some_type;
                some_type a_struct;

                char sum_a_b<watch=a_struct,update=TwoFieldsPlusTwo>;
            """
        )
        self.assertEqual(dom.a_struct.a, 2)
        self.assertEqual(dom.a_struct.b, 3)
        self.assertEqual(dom.a_struct.c, 0xff)
        self.assertEqual(dom.sum_a_b, 5)

        dom.a_struct.a = 10;

        self.assertEqual(dom.a_struct.a, 10)
        self.assertEqual(dom.a_struct.b, 3)
        self.assertEqual(dom.a_struct.c, 0xff)
        self.assertEqual(dom.sum_a_b, 13)
    
    def test_metadata_watch_this(self):
        dom = self._test_parse_build(
            "\x05\x06\x0b",
            """
                void PlusTwo(char &to_update, void &watched) {
                    to_update = watched.a + watched.b;
                }

                struct {
                    char a;
                    char b;
                    char c<watch=this,update=PlusTwo>;
                } main_struct;
            """
        )
        self.assertEqual(dom.main_struct.a, 5)
        self.assertEqual(dom.main_struct.b, 6)
        self.assertEqual(dom.main_struct.c, 11)

        dom.main_struct.b = 50

        self.assertEqual(dom.main_struct.a, 5)
        self.assertEqual(dom.main_struct.b, 50)
        self.assertEqual(dom.main_struct.c, 55)

    def test_metadata_complex(self):
        def crc32(params, ctxt, scope, stream, coord):
            data = pfp.utils.binary("").join([x._pfp__build() for x in params[1:]])
            val = binascii.crc32(data)
            params[0]._pfp__set_value(val)

        interp = pfp.interp.PfpInterp()
        interp.add_native(name="Crc32", func=crc32, ret=pfp.fields.Void)

        dom = self._test_parse_build(
            "TYPA\x41\x410000TYPB\x42\x420000",
            """
                typedef struct {
                    uchar a;
                    uchar b;
                } TYPE_A;

                typedef struct {
                    ushort hello;
                } TYPE_B;

                while(!FEof()) {
                    struct {
                        uchar cname[4];

                        union {
                            if(cname == "TYPA") {
                                TYPE_A type_a;
                                uchar raw[sizeof(type_a)];
                            } else if(cname == "TYPB") {
                                TYPE_B type_b;
                                uchar raw[sizeof(type_b)];
                            }
                        } data;
                        uint crc<watch=data.raw,update=Crc32>;
                    } chunks;
                }
            """,
        )
        self.assertEqual(len(dom.chunks), 2)
        self.assertEqual(dom.chunks[0].data.raw, "AA")
        self.assertEqual(dom.chunks[0].data.type_a.a, ord("A"))
        self.assertEqual(dom.chunks[0].data.type_a.b, ord("A"))
        self.assertEqual(dom.chunks[1].data.raw, "BB")
        self.assertEqual(dom.chunks[1].data.type_b.hello, 0x4242)

        dom.chunks[1].data.type_b.hello = 0xff01

        self.assertEqual(dom.chunks[1].crc, 0xa5fadf1b)
        
    
    def test_metadata_packer(self):
        dom = self._test_parse_build(
            "yoyoyo\x00\x10x\x9cc```d```\x02\x00\x00\x0f\x00\x04",
            """
                typedef struct {
                    int a;
                    int b;
                } PACKED_DATA;

                struct {
                    string type;
                    uchar length;
                    char data[length] <packtype=PACKED_DATA, packer=PackerGZip>;
                } main_struct;
            """,
        )

        self.assertEqual(dom.main_struct.data._.a, 1)
        self.assertEqual(dom.main_struct.data._.b, 2)

        dom.main_struct.data._.a = 5

        self.assertEqual(dom.main_struct.data._pfp__build(), b"x\x9cc```e```\x02\x00\x00#\x00\x08")
    
    #def test_metadata_packer_interpd(self):
        #dom = self._test_parse_build(
            #"\x08AaAbAcAd",
            #r"""
                #string CustomPacker(int pack, string data) {
                    #Int3();
                    #local string res = "";
                    #local int size = sizeof(data);
#
                    #if(pack) {
                        #for(local int i = 0; i < size; i++) {
                            #res += "A" + data[i];
                        #}
                    #} else {
                        #for(local int i = 0; i < size; i += 2) {
                            #res += data[i];
                        #}
                    #}
#
                    #return res;
                #}
#
                #typedef struct {
                    #char a;
                    #char b;
                    #char c;
                    #char d;
                #} PACKED_DATA;
#
                #struct {
                    #uchar length;
                    #char data[length] <packtype=PACKED_DATA, packer=CustomPacker>;
                #} main_struct;
            #""",
        #)

if __name__ == "__main__":
    unittest.main()
