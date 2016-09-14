#!/usr/bin/env python
# encoding: utf-8

import os
import six
import struct
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pfp
import pfp.errors
from pfp.fields import *
import pfp.utils
from pfp.bitwrap import BitwrappedStream

import utils

class TestBitwrap(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_bytes_read(self):
        stream = six.BytesIO(pfp.utils.binary("abcd"))
        bitwrapped = BitwrappedStream(stream)
        res = bitwrapped.read(4)
        self.assertEqual(pfp.utils.binary("abcd"), res)
    
    def test_bits_read1(self):
        stream = six.BytesIO(pfp.utils.binary(chr(int("01010101", 2))))
        bitwrapped = BitwrappedStream(stream)
        res = bitwrapped.read_bits(8)
        self.assertEqual([0,1,0,1,0,1,0,1], res)
    
    def test_bits_read2_padded1(self):
        stream = six.BytesIO(pfp.utils.binary(chr(int("11110000",2)) + chr(int("10101010", 2))))
        bitwrapped = BitwrappedStream(stream)
        bitwrapped.padded = True

        res = bitwrapped.read_bits(4)
        self.assertEqual([1,1,1,1], res)

        res = bitwrapped.read_bits(3)
        self.assertEqual([0,0,0], res)

        res = bitwrapped.read_bits(4)
        self.assertEqual([0,1,0,1], res)

        res = bitwrapped.read_bits(5)
        self.assertEqual([0,1,0,1,0], res)

    def test_bits_read2_padded2(self):
        stream = six.BytesIO(pfp.utils.binary(chr(int("11110000",2)) + chr(int("10101010", 2))))
        bitwrapped = BitwrappedStream(stream)
        bitwrapped.padded = True

        res = bitwrapped.read_bits(4)
        self.assertEqual([1,1,1,1], res)

        next_byte = bitwrapped.read(1)
        self.assertEqual(pfp.utils.binary(chr(int("10101010", 2))), next_byte)
    
    def test_bits_read_unpadded(self):
        stream = six.BytesIO(pfp.utils.binary(chr(int("11110000",2)) + chr(int("10101010", 2))))
        bitwrapped = BitwrappedStream(stream)
        bitwrapped.padded = False

        res = bitwrapped.read_bits(4)
        self.assertEqual([1,1,1,1], res)

        res = bitwrapped.read(1)
        self.assertEqual(pfp.utils.binary(chr(int("00001010", 2))), res)

        res = bitwrapped.read_bits(4)
        self.assertEqual([1,0,1,0], res)
    
    def test_bits_read_unpadded(self):
        stream = six.BytesIO(pfp.utils.binary(chr(int("11110000",2)) + chr(int("10101010", 2))))
        bitwrapped = BitwrappedStream(stream)
        bitwrapped.padded = False

        res = bitwrapped.read_bits(4)
        self.assertEqual([1,1,1,1], res)

        res = bitwrapped.read(1)
        self.assertEqual(pfp.utils.binary(chr(int("00001010", 2))), res)

        res = bitwrapped.read_bits(4)
        self.assertEqual([1,0,1,0], res)
    
    def test_bits_write_padded(self):
        stream = six.BytesIO()
        bitwrapped = BitwrappedStream(stream)
        bitwrapped.padded = True

        bitwrapped.write_bits([1,1,0,1])
        # should go to a new byte now, zero padded after the
        # 1101 bits
        bitwrapped.write(pfp.utils.binary("hello"))

        self.assertEqual(stream.getvalue(), pfp.utils.binary(chr(int("11010000", 2)) + "hello"))
    
    def test_unconsumed_ranges1(self):
        stream = six.BytesIO(pfp.utils.binary("A" * 100))
        bitwrapped = BitwrappedStream(stream)

        bitwrapped.read(10)
        bitwrapped.seek(bitwrapped.tell()+10)
        bitwrapped.read(10)
        bitwrapped.seek(bitwrapped.tell()+10)
        bitwrapped.read(10)

        uranges = bitwrapped.unconsumed_ranges()

        # test (11,20]
        self.assertEqual(len(uranges[11]), 1)
        self.assertEqual(len(uranges[10]), 0)
        self.assertEqual(len(uranges[19]), 1)
        self.assertEqual(len(uranges[20]), 0)

        # test (31,40]
        self.assertEqual(len(uranges[31]), 1)
        self.assertEqual(len(uranges[30]), 0)
        self.assertEqual(len(uranges[39]), 1)
        self.assertEqual(len(uranges[40]), 0)

    def test_unconsumed_ranges2(self):
        stream = six.BytesIO(pfp.utils.binary("A" * 100))
        bitwrapped = BitwrappedStream(stream)

        bitwrapped.read(10)
        bitwrapped.seek(bitwrapped.tell()+10)

        # it should not need a second read to add the
        # unconsumed range
        uranges = bitwrapped.unconsumed_ranges()

        self.assertEqual(len(uranges), 1)

        # test (11,20]
        self.assertEqual(len(uranges[11]), 1)
        self.assertEqual(len(uranges[10]), 0)
        self.assertEqual(len(uranges[19]), 1)
        self.assertEqual(len(uranges[20]), 0)

    def test_unconsumed_ranges3(self):
        stream = six.BytesIO(pfp.utils.binary("A" * 100))
        bitwrapped = BitwrappedStream(stream)

        bitwrapped.read(10)

        # it should not need a second read to add the
        # unconsumed range
        uranges = bitwrapped.unconsumed_ranges()

        self.assertEqual(len(uranges), 0)

if __name__ == "__main__":
    unittest.main()
