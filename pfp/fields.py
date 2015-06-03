
import struct

import pfp.errors as errors
import pfp.six as six

BIG_ENDIAN = ">"
LITTLE_ENDIAN = "<"

def get_value(field):
	if isinstance(field, Field):
		return field._pfp__value
	else:
		return field
PYVAL = get_value

class Field(object):
	"""Core class for all fields used in the Pfp DOM.
	
	All methods use the _pfp__XXX naming convention to
	avoid conflicting names used in templates, since
	struct fields will implement ``__getattr__`` and 
	``__setattr__`` to directly access child fields"""

	def __init__(self, stream=None):
		super(Field, self).__init__()
		self._pfp__name = None
		
		if stream is not None:
			self._pfp__parse(stream)
	
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
	
	def __le__(self, other):
		val = get_value(other)
		return self._pfp__value >= val
	
	def __ne__(self, other):
		val = get_value(other)
		return self._pfp__value >= val
	
	def __eq__(self, other):
		"""See if the two items are equal (True/False)

		:other: 
		:returns: 
		"""
		val = get_value(other)
		return self._pfp__value == val
	
	def __repr__(self):
		return "{}({!r})".format(self.__class__.__name__, self._pfp__value)

class Void(Field):
	"""The void field - used for return value of a function"""
	pass

class Struct(Field):
	"""The struct field"""
	def __init__(self, name=None):
		# ordered list of children
		super(Struct, self).__setattr__("_pfp__children", [])
		# for quick child access
		super(Struct, self).__setattr__("_pfp__children_map", {})

		super(Struct, self).__init__(name)
	
	def _pfp__add_child(self, name, child):
		"""Add a child to the Struct field

		:child: A :class:`.Field` instance
		:returns: None
		"""
		self._pfp__children.append(child)
		child._pfp__name = name
		self._pfp__children_map[name] = child
	
	def _pfp__parse(self, stream):
		"""Parse the incoming stream

		:stream: Input stream to be parsed
		:returns: Nothing

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
		res = six.binary("") if stream is None else 0

		# iterate IN ORDER
		for child in self._pfp__children:
			res += child._pfp__build(stream)

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

class Dom(Struct):
	"""The result of an interpreted template"""

class NumberBase(Field):
	"""The base field for all numeric fields"""

	# can be set on individual fields, for all numbers (NumberBase.endian = ...),
	# or specific number classes (Int.endian = ...)
	endian = BIG_ENDIAN		# default endianness is BIG_ENDIAN

	width = 4 				# number of bytes
	format = "i"			# default signed int

	_pfp__value = 0			# default value

	def _pfp__parse(self, stream):
		"""Parse the IO stream for this numeric field

		:stream: An IO stream that can be read from
		:returns: The number of bytes parsed
		"""
		raw_data = stream.read(self.width)
		data = six.binary(raw_data)

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
		if stream is not None:
			return stream.write(data)
		else:
			return data
	
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
	
	def __getattr__(self, val):
		if val.startswith("__") and attr.endswith("__"):
			return getattr(self._pfp__value, val)
		raise AttributeError()

class Char(NumberBase):
	width = 1
	format = "b"

class UChar(Char):
	format = "B"

class Short(NumberBase):
	width = 2
	format = "h"

class UShort(Short):
	format = "H"

class Int(NumberBase):
	width = 4
	format = "i"

class UInt(Int):
	format = "I"

class Int64(NumberBase):
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

	def _pfp__parse(self, stream):
		# optimizations... should reuse existing fields??
		self.items = []
		for x in range(PYVAL(self.width)):
			field = self.field_cls()
			field._pfp__name = "{}[{}]".format(
				self._pfp__name,
				x
			)
			field._pfp__parse(stream)
			self.items.append(field)
	
	def _pfp__build(self, stream=None):
		res = 0 if stream is not None else six.binary("")
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

# http://www.sweetscape.com/010editor/manual/ArraysStrings.htm
class String(Field):
	"""A null-terminated string. String fields should be interchangeable
	with char arrays"""

	# if the width is -1 when parse is called, read until null
	# termination.
	width = -1
	read_size = 1
	terminator = six.binary("\x00")

	def _pfp__parse(self, stream):
		"""Read from the stream until the string is null-terminated

		:stream: The input stream
		:returns: None

		"""
		res = six.binary("")
		while True:
			byte = six.binary(stream.read(self.read_size))
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
		if stream is None:
			return self._pfp__value + six.binary("\x00")
		else:
			return stream.write(self._pfp__value + six.binary("\x00"))
	
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
	terminator = six.binary("\x00\x00")

	def _pfp__parse(self, stream):
		String._pfp__parse(self, stream)
		self._pfp__value = six.binary(self._pfp__value.decode("utf-16le"))
	
	def _pfp__build(self, stream=None):
		val = self._pfp__value.decode("ISO-8859-1").encode("utf-16le") + b"\x00\x00"
		if stream is None:
			return val
		else:
			return stream.write(val)
