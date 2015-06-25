#!/usr/bin/env python
# encoding: utf-8

import json
import math
import six
import struct

import pfp.errors as errors
import pfp.utils as utils
import pfp.bitwrap as bitwrap

BIG_ENDIAN = ">"
LITTLE_ENDIAN = "<"

def get_value(field):
	if isinstance(field, Field):
		return field._pfp__value
	else:
		return field

def get_str(field):
	if isinstance(field, Array):
		return field._array_to_str()
	else:
		return get_value(field)

PYVAL = get_value
PYSTR = get_str

class Field(object):
	"""Core class for all fields used in the Pfp DOM.
	
	All methods use the _pfp__XXX naming convention to
	avoid conflicting names used in templates, since
	struct fields will implement ``__getattr__`` and 
	``__setattr__`` to directly access child fields"""

	_pfp__interp = None

	def __init__(self, stream=None):
		super(Field, self).__init__()
		self._pfp__name = None
		self._pfp__frozen = False
		
		if stream is not None:
			self._pfp__parse(stream)
	
	def _pfp__freeze(self):
		"""Freeze the field so that it cannot be modified (const)
		"""
		self._pfp__frozen = True
	
	def _pfp__get_root_value(self, val):
		"""helper function to fetch the root value of an object"""
		if isinstance(val, Field):
			return val._pfp__value
		else:
			return val
	
	def _pfp__set_value(self, new_val):
		"""Set the new value if type checking is passes, potentially
		(TODO? reevaluate this) casting the value to something else

		:new_val: The new value
		:returns: TODO

		"""
		if self._pfp__frozen:
			raise errors.UnmodifiableConst()
		self._pfp__value = self._pfp__get_root_value(new_val)
	
	def _pfp__build(self, output_stream=None):
		"""Pack this field into a string. If output_stream is specified,
		write the output into the output stream

		:output_stream: Optional output stream to write the results to
		:returns: Resulting string if ``output_stream`` is not specified. Else the number of bytes writtern.

		"""
		raise NotImplemented("Inheriting classes must implement the _pfp__build function")
	
	def _pfp__parse(self, stream):
		"""Parse this field from the ``stream``

		:stream: An IO stream that can be read from
		:returns: None
		"""
		raise NotImplemented("Inheriting classes must implement the _pfp__parse function")

	def __cmp__(self, other):
		"""Compare the Field to something else, either another
		Field or something else

		:other: Another Field instance or something else
		:returns: result of cmp()

		"""
		val = get_value(other)
		return cmp(self._pfp__value, val)
	
	def __lt__(self, other):
		"""Compare the Field to something else, either another
		Field or something else

		:other: The other field
		:returns: True if equal
		"""
		val = get_value(other)
		return self._pfp__value < val
	
	def __le__(self, other):
		val = get_value(other)
		return self._pfp__value <= val
	
	def __gt__(self, other):
		"""Compare the Field to something else, either another
		Field or something else

		:other: The other field
		:returns: True if equal
		"""
		val = get_value(other)
		return self._pfp__value > val
	
	def __ge__(self, other):
		val = get_value(other)
		return self._pfp__value >= val
	
	def __ne__(self, other):
		val = get_value(other)
		return self._pfp__value != val
	
	def __eq__(self, other):
		"""See if the two items are equal (True/False)

		:other: 
		:returns: 
		"""
		val = get_value(other)
		return self._pfp__value == val
	
	def __repr__(self):
		return "{}({!r})".format(self.__class__.__name__, self._pfp__value)
	
	def _pfp__show(self, level=0):
		return repr(self)

class Void(Field):
	"""The void field - used for return value of a function"""
	pass

class Struct(Field):
	"""The struct field"""

	_pfp__show_name = "struct"

	def __init__(self, stream=None):
		# ordered list of children
		super(Struct, self).__setattr__("_pfp__children", [])
		# for quick child access
		super(Struct, self).__setattr__("_pfp__children_map", {})

		super(Struct, self).__init__()
	
	def _pfp__set_value(self, value):
		"""Initialize the struct. Value should be an array of
		fields, one each for each struct member.

		:value: An array of fields to initialize the struct with
		:returns: None
		"""
		if self._pfp__frozen:
			raise errors.UnmodifiableConst()
		if len(value) != len(self._pfp__children):
			raise errors.PfpError("struct initialization has wrong number of members")

		for x in six.moves.range(len(self._pfp__children)):
			self._pfp__children[x]._pfp__set_value(value[x])
	
	def _pfp__add_child(self, name, child):
		"""Add a child to the Struct field

		:name: The name of the child
		:child: A :class:`.Field` instance
		:returns: None
		"""
		if name in self._pfp__children_map:
			return self._pfp__handle_implicit_array(name, child)
		else:
			self._pfp__children.append(child)
			child._pfp__name = name
			self._pfp__children_map[name] = child
			return child
	
	def _pfp__handle_implicit_array(self, name, child):
		"""Handle inserting implicit array elements
		"""
		existing_child = self._pfp__children_map[name]
		if isinstance(existing_child, Array):
			if existing_child.field_cls != child.__class__:
				raise errors.PfpError("implicit arrays must be sequential!")
			existing_child.append(child)
			return existing_child
		else:
			if self._pfp__children[-1].__class__ != child.__class__:
				raise errors.PfpError("implicit arrays must be sequential!")

			cls = child._pfp__class if hasattr(child, "_pfp__class") else child.__class__
			ary = Array(0, cls)
			ary._pfp__name = name
			ary.append(existing_child)
			ary.append(child)

			exist_idx = -1
			for idx,child in enumerate(self._pfp__children):
				if child is existing_child:
					exist_idx = idx
					break

			self._pfp__children[exist_idx] = ary
			self._pfp__children_map[name] = ary
			return ary
	
	def _pfp__parse(self, stream):
		"""Parse the incoming stream

		:stream: Input stream to be parsed
		:returns: Number of bytes parsed

		"""
		res = 0
		for child in self._pfp__children:
			res += child._pfp__parse(stream)
		return res
	
	def _pfp__build(self, stream=None):
		"""Build the field and write the result into the stream

		:stream: An IO stream that can be written to
		:returns: None

		"""
		# returns either num bytes written or total data
		res = utils.binary("") if stream is None else 0

		# iterate IN ORDER
		for child in self._pfp__children:
			child_res = child._pfp__build(stream)
			res += child_res

		return res
	
	def __getattr__(self, name):
		"""Custom __getattr__ for quick access to the children"""
		children_map = super(Struct, self).__getattribute__("_pfp__children_map")
		if name in children_map:
			return children_map[name]
		else:
			# default getattr instead
			return super(Struct, self).__getattribute__(name)
	
	def __setattr__(self, name, value):
		"""Custom __setattr__ for quick setting of children values
		
		If value is not an instance of ``Field``, assume it is the
		value for the field and that the field itself should not
		be overridden"""
		children_map = super(Struct, self).__getattribute__("_pfp__children_map")
		if name in children_map:
			if not isinstance(value, Field):
				children_map[name]._pfp__value = value
			else:
				children_map[name] = value
			return children_map[name]
		else:
			# default getattr instead
			return super(Struct, self).__setattr__(name, value)
	
	def __repr__(self):
		return object.__repr__(self)
	
	def _pfp__show(self, level=0):
		"""Show the contents of the struct
		"""
		res = []
		res.append("{} {{".format(
			self._pfp__show_name
		))
		for child in self._pfp__children:
			res.append("{}{:10s} = {}".format(
				"    "*(level+1),
				child._pfp__name,
				child._pfp__show(level+1)
			))
		res.append("{}}}".format("    "*level))
		return "\n".join(res)

class Union(Struct):
	"""A union field, where each member is an alternate
	view of the data"""

	_pfp__buff = None
	_pfp__size = 0
	_pfp__show_name = "union"

	def __init__(self, name=None):
		"""Init the union and its buff stream
		"""
		super(Union, self).__init__(name)
		self._pfp__buff = six.BytesIO()

	def _pfp__add_child(self, name, child):
		"""Add a child to the Union field

		:name: The name of the child
		:child: A :class:`.Field` instance
		:returns: None
		"""
		res = super(Union, self)._pfp__add_child(name, child)
		self._pfp__buff.seek(0, 0)
		child._pfp__build(stream=self._pfp__buff)
		self._pfp__buff.seek(0, 0)

		return res
	
	def _pfp__parse(self, stream):
		"""Parse the incoming stream

		:stream: Input stream to be parsed
		:returns: Number of bytes parsed
		"""
		max_res = 0
		for child in self._pfp__children:
			child_res = child._pfp__parse(stream)
			if child_res > max_res:
				max_res = child_res

			# rewind the stream
			stream.seek(child_res, -1)
		self._pfp__size = max_res

		self._pfp__buff = six.BytesIO(stream.read(self._pfp__size))
		return max_res
	
	def _pfp__build(self, stream=None):
		"""Build the union and write the result into the stream.

		:stream: None
		:returns: None
		"""
		val = self._pfp__buff.getvalue()
		if stream is None:
			return val
		else:
			stream.write(self._pfp__buff.getvalue())
			return len(val)
	
	def __setattr__(self, name, value):
		"""Custom __setattr__ to keep track of the order things
		are writen (to mimic writing to memory)
		"""
		res = super(Union, self).__setattr__(name, value)
		children_map = super(Struct, self).__getattribute__("_pfp__children_map")

		if name in children_map:
			field = getattr(self, name)
			# back to the start of the buffer
			self._pfp__buff.seek(0, 0)
			field._pfp__build(stream=self._pfp__buff)

		return res

class Dom(Struct):
	"""The result of an interpreted template"""
	def _pfp__build(self, stream=None):
		if stream is None:
			io_stream = six.BytesIO()
			tmp_stream = bitwrap.BitwrappedStream(io_stream)
			tmp_stream.padded = self._pfp__interp.get_bitfield_padded()
			super(Dom, self)._pfp__build(tmp_stream)

			# flush out any unaligned bitfields, etc
			tmp_stream.flush()
			res = io_stream.getvalue()
			return res
		else:
			return super(Dom, self)._pfp__build(stream)

class NumberBase(Field):
	"""The base field for all numeric fields"""

	# can be set on individual fields, for all numbers (NumberBase.endian = ...),
	# or specific number classes (Int.endian = ...)
	endian = BIG_ENDIAN		# default endianness is BIG_ENDIAN

	width = 4 				# number of bytes
	format = "i"			# default signed int
	bitsize = None			# for IntBase

	_pfp__value = 0			# default value
	
	def __init__(self, stream=None, bitsize=None):
		"""Special init for the bitsize
		"""
		self.bitsize = get_value(bitsize)
		super(NumberBase, self).__init__(stream)

	def __nonzero__(self):
		"""Used for the not operator"""
		return self._pfp__value != 0
	
	def __bool__(self):
		"""Used for the not operator"""
		return self._pfp__value != 0

	def _pfp__parse(self, stream):
		"""Parse the IO stream for this numeric field

		:stream: An IO stream that can be read from
		:returns: The number of bytes parsed
		"""
		if self.bitsize is None:
			raw_data = stream.read(self.width)
			data = utils.binary(raw_data)

		else:
			bits = stream.read_bits(self.bitsize)
			width_diff = self.width  - (len(bits)//8) - 1
			bits_diff = 8 - (len(bits) % 8)
			padding = [0] * (width_diff * 8 + bits_diff)

			bits = padding + bits

			data = bitwrap.bits_to_bytes(bits)

		if len(data) < self.width:
			raise errors.PrematureEOF()

		self._pfp__data = data
		self._pfp__value = struct.unpack(
			"{}{}".format(self.endian, self.format),
			data
		)[0]

		return self.width
	
	def _pfp__build(self, stream=None):
		"""Build the field and write the result into the stream

		:stream: An IO stream that can be written to
		:returns: None

		"""
		data = struct.pack(
			"{}{}".format(self.endian, self.format),
			self._pfp__value
		)
		if self.bitsize is None:
			if stream is not None:
				stream.write(data)
				return len(data)
			else:
				return data
		else:
			num_bytes = int(math.ceil(self.bitsize / 8.0))
			if self.endian == BIG_ENDIAN:
				bit_data = data[:num_bytes]
			else:
				bit_data = data[-num_bytes:]

			raw_bits = bitwrap.bytes_to_bits(bit_data)
			bits = raw_bits[-self.bitsize:]

			if stream is not None:
				stream.write_bits(bits)
				return len(bits) // 8
			else:
				# TODO this can't be right....
				return bits
	
	def _dom_class(self, obj1, obj2):
		"""Return the dominating numeric class between the two

		:obj1: TODO
		:obj2: TODO
		:returns: TODO

		"""
		if isinstance(obj1, Double) or isinstance(obj2, Double):
			return Double
		if isinstance(obj1, Float) or isinstance(obj2, Float):
			return Float
	
	def __iadd__(self, other):
		self._pfp__value += self._pfp__get_root_value(other)
	def __isub__(self, other):
		self._pfp__value -= self._pfp__get_root_value(other)
	def __imul__(self, other):
		self._pfp__value *= self._pfp__get_root_value(other)
	def __idiv__(self, other):
		self._pfp__value /= self._pfp__get_root_value(other)
	def __iand__(self, other):
		self._pfp__value &= self._pfp__get_root_value(other)
	def __ixor__(self, other):
		self._pfp__value ^= self._pfp__get_root_value(other)
	def __ior__(self, other):
		self._pfp__value |= self._pfp__get_root_value(other)
	def __ifloordiv__(self, other):
		self._pfp__value //= self._pfp__get_root_value(other)
	def __imod__(self, other):
		self._pfp__value %= self._pfp__get_root_value(other)
	def __ipow__(self, other):
		self._pfp__value **= self._pfp__get_root_value(other)
	def __ilshift__(self, other):
		self._pfp__value <<= self._pfp__get_root_value(other)
	def __irshift__(self, other):
		self._pfp__value >>= self._pfp__get_root_value(other)
	
	def __add__(self, other):
		res = self.__class__()
		res._pfp__set_value(self._pfp__value + self._pfp__get_root_value(other))
		return res
	
	def __sub__(self, other):
		res = self.__class__()
		res._pfp__set_value(self._pfp__value - self._pfp__get_root_value(other))
		return res
	
	def __mul__(self, other):
		res = self.__class__()
		res._pfp__set_value(self._pfp__value * self._pfp__get_root_value(other))
		return res
	
	def __truediv__(self, other):
		res = self.__class__()
		# if truediv is being called, then / should also behave like
		# truediv (2/3 == 0.6666 instead of 0 [classic division])
		# the default in python 3 is truediv
		res._pfp__set_value(self._pfp__value / self._pfp__get_root_value(other))
		return res
	
	def __div__(self, other):
		res = self.__class__()
		res._pfp__set_value(self._pfp__value / self._pfp__get_root_value(other))
		return res
	
	def __and__(self, other):
		res = self.__class__()
		res._pfp__set_value(self._pfp__value & self._pfp__get_root_value(other))
		return res
	
	def __xor__(self, other):
		res = self.__class__()
		res._pfp__set_value(self._pfp__value ^ self._pfp__get_root_value(other))
		return res
	
	def __or__(self, other):
		res = self.__class__()
		res._pfp__set_value(self._pfp__value | self._pfp__get_root_value(other))
		return res
	
	def __floordiv__(self, other):
		res = self.__class__()
		res._pfp__set_value(self._pfp__value // self._pfp__get_root_value(other))
		return res
	
	def __mod__(self, other):
		res = self.__class__()
		res._pfp__set_value(self._pfp__value % self._pfp__get_root_value(other))
		return res
	
	def __pow__(self, other):
		res = self.__class__()
		res._pfp__set_value(self._pfp__value ** self._pfp__get_root_value(other))
		return res

	def __lshift__(self, other):
		res = self.__class__()
		res._pfp__set_value(self._pfp__value << self._pfp__get_root_value(other))
		return res

	def __rshift__(self, other):
		res = self.__class__()
		res._pfp__set_value(self._pfp__value >> self._pfp__get_root_value(other))
		return res

	def __invert__(self):
		return ~self._pfp__value
	
	def __neg__(self):
		return -self._pfp__value
	
	def __getattr__(self, val):
		if val.startswith("__") and attr.endswith("__"):
			return getattr(self._pfp__value, val)
		raise AttributeError(val)

class IntBase(NumberBase):
	signed = True

	def _pfp__set_value(self, new_val):
		"""Set the value, potentially converting an unsigned
		value to a signed one (and visa versa)"""
		if self._pfp__frozen:
			raise errors.UnmodifiableConst()
		if isinstance(new_val, IntBase):
			# will automatically convert correctly between ints of
			# different sizes, unsigned/signed, etc
			raw = new_val._pfp__build()
			while len(raw) < self.width:
				if self.endian == BIG_ENDIAN:
					raw += "\x00"
				else:
					raw = "\x00" + raw
			while len(raw) > self.width:
				if self.endian == BIG_ENDIAN:
					raw = raw[1:]
				else:
					raw = raw[:-1]
			self._pfp__parse(six.BytesIO(raw))
		else:
			self._pfp__value = new_val

	def __repr__(self):
		f = ":0{}x".format(self.width*2)
		return ("{}({!r} [{" + f + "}])").format(
			self.__class__.__name__,
			self._pfp__value,
			self._pfp__value
		)
	
	def __truediv__(self, other):
		"""dividing ints should not return a float (python 3
		true div behavior). So force floordiv
		"""
		return self // other

class Char(IntBase):
	width = 1
	format = "b"

class UChar(Char):
	format = "B"

class Short(IntBase):
	width = 2
	format = "h"

class UShort(Short):
	format = "H"

class WChar(Short):
	pass

class WUChar(UShort):
	pass

class Int(IntBase):
	width = 4
	format = "i"

class UInt(Int):
	format = "I"

class Int64(IntBase):
	width = 8
	format = "q"

class UInt64(Int64):
	format = "Q"

class Float(NumberBase):
	width = 4
	format = "f"

class Double(NumberBase):
	width = 8
	format = "d"

# --------------------------------

class Array(Field):
	width = -1

	def __init__(self, width, field_cls, stream=None):
		""" Create an array field of size "width" from the stream
		"""
		self.width = width
		self.field_cls = field_cls
		self.items = []

		if stream is not None:
			self._pfp__parse(stream)
	
	def append(self, item):
		# TODO check for consistent type
		self.items.append(item)
		self.width = len(self.items)
	
	def _is_stringable(self):
		# TODO WChar
		return self.field_cls in [Char, UChar]
	
	def _array_to_str(self, max_len=-1):
		if not self._is_stringable():
			return None
		res = ""
		for item in self.items:
			if max_len != -1 and len(res) >= max_len:
				break
			# TODO WChar
			res += chr(PYVAL(item))
		return res
	
	def __eq__(self, other):
		if self._is_stringable() and other.__class__ in [String, WString]:
			res = self._array_to_str()
			return res == other
		else:
			raise Exception("TODO")
	
	def __ne__(self, other):
		return not self.__eq__(other)

	def _pfp__parse(self, stream):
		# optimizations... should reuse existing fields??
		self.items = []
		for x in six.moves.range(PYVAL(self.width)):
			field = self.field_cls()
			field._pfp__name = "{}[{}]".format(
				self._pfp__name,
				x
			)
			field._pfp__parse(stream)
			self.items.append(field)
	
	def _pfp__build(self, stream=None):
		res = 0 if stream is not None else utils.binary("")
		for item in self.items:
			res += item._pfp__build(stream=stream)
		return res
	
	def __getitem__(self, idx):
		return self.items[idx]
	
	def __setitem__(self, idx, value):
		if isinstance(value, Field):
			self.items[idx] = value
		else:
			self.items[idx]._pfp__set_value(value)
	
	def __repr__(self):
		other = ""
		if self._is_stringable():
			res = self._array_to_str(20)
			other = " ({!r})".format(res)

		return "{}[{}]{}".format(
			self.field_cls.__name__ if type(self.field_cls) is type else self.field_cls._typedef_name,
			PYVAL(self.width),
			other
		)
	
	def __len__(self):
		return len(self.items)

# http://www.sweetscape.com/010editor/manual/ArraysStrings.htm
class String(Field):
	"""A null-terminated string. String fields should be interchangeable
	with char arrays"""

	# if the width is -1 when parse is called, read until null
	# termination.
	width = -1
	read_size = 1
	terminator = utils.binary("\x00")

	def _pfp__set_value(self, new_val):
		"""Set the value of the String, taking into account
		escaping and such as well
		"""
		if not isinstance(new_val, Field):
			new_val = json.loads('"' + new_val + '"')
		super(String, self)._pfp__set_value(new_val)

	def _pfp__parse(self, stream):
		"""Read from the stream until the string is null-terminated

		:stream: The input stream
		:returns: None

		"""
		res = utils.binary("")
		while True:
			byte = utils.binary(stream.read(self.read_size))
			if len(byte) < self.read_size:
				raise errors.PrematureEOF()
			# note that the null terminator must be added back when
			# built again!
			if byte == self.terminator:
				break
			res += byte
		self._pfp__value = res
	
	def _pfp__build(self, stream=None):
		"""Build the String field

		:stream: TODO
		:returns: TODO

		"""
		data = self._pfp__value + utils.binary("\x00")
		if stream is None:
			return data
		else:
			stream.write(data)
			return len(data)
	
	def __add__(self, other):
		"""Add two strings together. If other is not a String instance,
		a fields.String instance will still be returned

		:other: TODO
		:returns: TODO

		"""
		res_field = String()
		res = ""
		if isinstance(other, String):
			res = self._pfp__value + other._pfp__value
		else:
			res = self._pfp__value + other
		res_field._pfp__set_value(res)
		return res_field
	
	def __iadd__(self, other):
		"""In-place addition to this String field

		:other: TODO
		:returns: TODO

		"""
		if isinstance(other, String):
			self._pfp__value += other._pfp__value
		else:
			self._pfp__value += other

class WString(String):
	width = -1
	read_size = 2
	terminator = utils.binary("\x00\x00")

	def _pfp__parse(self, stream):
		String._pfp__parse(self, stream)
		self._pfp__value = utils.binary(self._pfp__value.decode("utf-16le"))
	
	def _pfp__build(self, stream=None):
		val = self._pfp__value.decode("ISO-8859-1").encode("utf-16le") + b"\x00\x00"
		if stream is None:
			return val
		else:
			stream.write(val)
			return len(val)
