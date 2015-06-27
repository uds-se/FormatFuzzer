#!/usr/bin/env python
# encoding: utf-8

import collections
import os
import six
import sys

import pfp.utils as utils

BIT_DIR_LEFT_RIGHT = 1
BIT_DIR_RIGHT_LEFT = -1

class EOFError(Exception): pass

def bits_to_bytes(bits):
	"""Convert the bit list into bytes. (Assumes bits is a list
	whose length is a multiple of 8)
	"""
	if len(bits) % 8 != 0:
		raise Exception("num bits must be multiple of 8")

	res = ""

	for x in six.moves.range(0, len(bits), 8):
		byte_bits = bits[x:x+8]
		byte_val = int(''.join(map(str, byte_bits)), 2)
		res += chr(byte_val)

	return utils.binary(res)

def bytes_to_bits(bytes_):
	"""Convert bytes to a list of bits
	"""
	res = []
	for x in bytes_:
		if not isinstance(x, int):
			x = ord(x)
		res += byte_to_bits(x)
	return res

def byte_to_bits(b):
	"""Convert a byte into bits
	"""
	return [(b >> x) & 1 for x in six.moves.range(7, -1, -1)]

class BitwrappedStream(object):

	"""A stream that wraps other streams to provide bit-level
	access"""

	closed = True

	def __init__(self, stream):
		"""Init the bit-wrapped stream

		:stream: The normal byte stream
		"""
		self._stream = stream
		self._bits = collections.deque()

		self.closed = False
		
		# assume that bitfields end on an even boundary,
		# otherwise the entire stream will be treated as
		# a bit stream with no padding
		self.padded = True

		# packed left-to-right
		self.direction = BIT_DIR_LEFT_RIGHT
	
	def is_eof(self):
		"""Return if the stream has reached EOF or not
		without discarding any unflushed bits

		:returns: True/False
		"""
		pos = self._stream.tell()
		byte = self._stream.read(1)
		self._stream.seek(pos, 0)

		return utils.binary(byte) == utils.binary("")
		
	def close(self):
		"""Close the stream
		"""
		self.closed = True
		self._flush_bits_to_stream()
		self._stream.close()
	
	def flush(self):
		"""Flush the stream
		"""
		self._flush_bits_to_stream()
		self._stream.flush()
	
	def isatty(self):
		"""Return if the stream is a tty
		"""
		return self._stream.isatty()
	
	def read(self, num):
		"""Read ``num`` number of bytes from the stream. Note that this will
		automatically resets/ends the current bit-reading if it does not
		end on an even byte AND ``self.padded`` is True. If ``self.padded`` is
		True, then the entire stream is treated as a bitstream.

		:num: number of bytes to read
		:returns: the read bytes, or empty string if EOF has been reached
		"""
		if self.padded:
			# we toss out any uneven bytes
			self._bits.clear()
			return utils.binary(self._stream.read(num))
		else:
			bits = self.read_bits(num * 8)
			res = bits_to_bytes(bits)
			return utils.binary(res)
	
	def read_bits(self, num):
		"""Read ``num`` number of bits from the stream

		:num: number of bits to read
		:returns: a list of ``num`` bits, or an empty list if EOF has been reached
		"""
		if num > len(self._bits):
			needed = num - len(self._bits)
			num_bytes = (needed // 8) + 1
			read_bytes = self._stream.read(num_bytes)

			for bit in bytes_to_bits(read_bytes):
				self._bits.append(bit)

		res = []
		while len(res) < num and len(self._bits) > 0:
			res.append(self._bits.popleft())

		return res
	
	def write(self, data):
		"""Write data to the stream

		:data: the data to write to the stream
		:returns: None
		"""
		if self.padded:
			# flush out any remaining bits first
			if len(self._bits) > 0:
				self._flush_bits_to_stream()
			self._stream.write(data)
		else:
			# nothing to do here
			if len(data) == 0:
				return

			bits = bytes_to_bits(data)
			self.write_bits(bits)
	
	def write_bits(self, bits):
		"""Write the bits to the stream.

		Add the bits to the existing unflushed bits and write
		complete bytes to the stream.
		"""
		for bit in bits:
			self._bits.append(bit)

		while len(self._bits) >= 8:
			byte_bits = [self._bits.popleft() for x in six.moves.range(8)]
			byte = bits_to_bytes(byte_bits)
			self._stream.write(byte)
		
		# there may be unflushed bits leftover and THAT'S OKAY
	
	def tell(self):
		"""Return the current position in the stream (ignoring bit
		position)

		:returns: int for the position in the stream
		"""
		return self._stream.tell()
	
	def seek(self, pos, seek_type):
		"""Seed to the specified position in the stream with seek_type.
		Unflushed bits will be discarded in the case of a seek.

		:pos: offset
		:seek_type: direction
		:returns: TODO

		"""
		self._bits.clear()
		return self._stream.seek(pos, seek_type)
	
	def size(self):
		"""Return the size of the stream, or -1 if it cannot
		be determined.
		"""
		pos = self._stream.tell()
		# seek to the end of the stream
		self._stream.seek(0,2)
		size = self._stream.tell()
		self._stream.seek(pos, 0)

		return size
	
	# -----------------------------
	# PRIVATE FUNCTIONS
	# -----------------------------
	
	def _flush_bits_to_stream(self):
		"""Flush the bits to the stream. This is used when
		a few bits have been read and ``self._bits`` contains unconsumed/
		flushed bits when data is to be written to the stream
		"""
		if len(self._bits) == 0:
			return 0

		bits = list(self._bits)

		diff = 8 - (len(bits) % 8)
		padding = [0] * diff

		bits = bits + padding

		self._stream.write(bits_to_bytes(bits))

		self._bits.clear()
