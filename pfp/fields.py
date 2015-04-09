
import struct

from . import errors

BIG_ENDIAN = ">"
LITTLE_ENDIAN = "<"

class Field(object):
	"""Core class for all fields used in the Pfp DOM.
	
	All methods use the _pfp__XXX naming convention to
	avoid conflicting names used in templates, since
	struct fields will implement ``__getattr__`` and 
	``__setattr__`` to directly access child fields"""

	def __init__(self, name):
		super(Field, self).__init__()
		self._pfp__name = name
	
	def _pfp__build(self, output_stream):
		"""Pack this field into the output stream

		:output_stream: TODO
		:returns: TODO

		"""
		raise NotImplemented("Inheriting classes must implement the _pfp__build function")
	
	def _pfp__parse(self, stream):
		"""Parse this field from the ``stream``

		:stream: An IO stream that can be read from
		:returns: None
		"""
		raise NotImplemented("Inheriting classes must implement the _pfp__parse function")

class Struct(Field):
	"""The struct field"""
	def __init__(self):
		super(Struct, self).__init__()
		
		# ordered list of children
		super(Struct, self).__setattr__("_pfp__children", [])
		# for quick child access
		super(Struct, self).__setattr__("_pfp__children_map", [])
	
	def _pfp__add_child(self, child):
		"""Add a child to the Struct field

		:child: A :class:`.Field` instance
		:returns: None
		"""
		self._pfp__children.append(child)
		self._pfp__children_map[child._pfp__name] = child
	
	def __getattr__(self, name):
		"""Custom __getattr__ for quick access to the children"""
		children_map = super(Struct, self).__getattribute__("_pfp__children_map")
		if name in children_map:
			return children_map[name]
		else:
			# default getattr instead
			return super(Struct, self).__getattr__(name)
	
	def __setattr__(self, name, value):
		"""Custom __setattr__ for quick setting of children values"""
		children_map = super(Struct, self).__getattribute__("_pfp__children_map")
		if name in children_map:
			children_map[name] = value
			return children_map[name]
		else:
			# default getattr instead
			return super(Struct, self).__setattr__(name, value)

class DOM(Struct):
	"""The result of an interpreted template"""

class NumberBase(Field):
	"""The base field for all numeric fields"""

	# can be set on individual fields, for all numbers (NumberBase.endian = ...),
	# or specific number classes (Int.endian = ...)
	endian = BIG_ENDIAN		# default endianness is BIG_ENDIAN

	width = 4 				# number of bytes
	format = "i"			# default signed int

	def _pfp__parse(self, stream):
		"""Parse the IO stream for this numeric field

		:stream: An IO stream that can be read from
		:returns: None
		"""
		data = stream.read(self.width)

		if len(data) < self.width:
			raise errors.PrematureEOF()

		self._pfp__data = data
		self._pfp__value = struct.unpack(
			"{}{}".format(self.endian, self.format),
			data
		)[0]
	
	def _pfp__build(self, stream):
		"""Build the field and write the result into the stream

		:stream: An IO stream that can be written to
		:returns: None

		"""
		data = struct.pack(
			"{}{}".format(self.endian, self.format),
			[self._pfp__value]
		)
		stream.write(data)
	
	def __cmp__(self, other):
		"""Custom comparison function so code like below will work: ::
		
			field = Int()
			field._pfp__parse(StringIO.StringIO("\\x00\\x00\\x00\\x01"))
			field == 1 # should be True"""
		if isinstance(other, NumberBase):
			other = other._pfp__value
		return cmp(self._pfp__value, other)

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
