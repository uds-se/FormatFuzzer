#!/usr/bin/env python
# encoding: utf-8

from intervaltree import IntervalTree,Interval
import json
import math
import six
import struct

import pfp.errors as errors
import pfp.utils as utils
import pfp.bitwrap as bitwrap
import pfp.functions as functions

BIG_ENDIAN = ">"
LITTLE_ENDIAN = "<"

def true():
	res = Int()
	res._pfp__value = 1
	return res

def false():
	res = Int()
	res._pfp__value = 0
	return res

def get_value(field):
	if isinstance(field, Field):
		return field._pfp__value
	else:
		return field

def get_str(field):
	if isinstance(field, Array):
		res = field._array_to_str()
	elif isinstance(field, Char):
		res = chr(PYVAL(field))
	else:
		res = get_value(field)
	
	return utils.string(res)

PYVAL = get_value
PYSTR = get_str

class Field(object):
	"""Core class for all fields used in the Pfp DOM.
	
	All methods use the _pfp__XXX naming convention to
	avoid conflicting names used in templates, since
	struct fields will implement ``__getattr__`` and 
	``__setattr__`` to directly access child fields"""

	_pfp__interp = None

	def __init__(self, stream=None, metadata_processor=None):
		super(Field, self).__init__()
		self._pfp__name = None
		self._pfp__frozen = False

		self._pfp__offset = -1

		# watchers to update when something changes
		self._pfp__watchers = []
		self._pfp__parent = None
		self._pfp__watch_fields = []
		self._pfp__no_notify = False

		self._pfp__packer = None
		self._pfp__unpack = None
		self._pfp__pack = None
		self._pfp__pack_type = None
		self._pfp__no_unpack = False
		self._pfp__parsed_packed = None
		self._pfp__metadata_processor = metadata_processor
		self._ = None

		self._pfp__array_idx = None
		
		if stream is not None:
			self._pfp__parse(stream, save_offset=True)
	
	def _pfp__process_metadata(self):
		"""Process the metadata once the entire struct has been
		declared.
		"""
		if self._pfp__metadata_processor is None:
			return

		metadata_info = self._pfp__metadata_processor()
		if isinstance(metadata_info, list):
			for metadata in metadata_info:
				if metadata["type"] == "watch":
					self._pfp__set_watch(
						metadata["watch_fields"],
						metadata["update_func"],
						*metadata["func_call_info"]
					)

				elif metadata["type"] == "packed":
					del metadata["type"]
					self._pfp__set_packer(**metadata)
					if self._pfp__can_unpack():
						self._pfp__unpack_data(self.raw_data)
	
	def _pfp__watch(self, watcher):
		"""Add the watcher to the list of fields that
		are watching this field
		"""
		if self._pfp__parent is not None and isinstance(self._pfp__parent, Union):
			self._pfp__parent._pfp__watch(watcher)
		else:
			self._pfp__watchers.append(watcher)
	
	def _pfp__set_watch(self, watch_fields, update_func, *func_call_info):
		"""Subscribe to update events on each field in ``watch_fields``, using
		``update_func`` to update self's value when ``watch_field``
		changes"""
		self._pfp__watch_fields = watch_fields

		for watch_field in watch_fields:
			watch_field._pfp__watch(self)
		self._pfp__update_func = update_func
		self._pfp__update_func_call_info = func_call_info
	
	def _pfp__set_packer(self, pack_type, packer=None, pack=None, unpack=None, func_call_info=None):
		"""Set the packer/pack/unpack functions for this field, as
		well as the pack type.

		:pack_type: The data type of the packed data
		:packer: A function that can handle packing and unpacking. First
				 arg is true/false (to pack or unpack). Second arg is the stream.
				 Must return an array of chars.
		:pack: A function that packs data. It must accept an array of chars and return an
				array of chars that is a packed form of the input.
		:unpack: A function that unpacks data. It must accept an array of chars and
				return an array of chars
		"""
		self._pfp__pack_type = pack_type
		self._pfp__unpack = unpack
		self._pfp__pack = pack
		self._pfp__packer = packer
		self._pfp__pack_func_call_info = func_call_info
	
	def _pfp__pack_data(self):
		"""Pack the nested field
		"""
		if self._pfp__pack_type is None:
			return

		tmp_stream = six.BytesIO()
		self._._pfp__build(bitwrap.BitwrappedStream(tmp_stream))
		raw_data = tmp_stream.getvalue()

		unpack_func = self._pfp__packer
		unpack_args = []
		if self._pfp__packer is not None:
			unpack_func = self._pfp__packer
			unpack_args = [true(), raw_data]
		elif self._pfp__pack is not None:
			unpack_func = self._pfp__pack
			unpack_args = [raw_data]

		# does not need to be converted to a char array
		if not isinstance(unpack_func, functions.NativeFunction):
			io_stream = bitwrap.BitwrappedStream(six.BytesIO(raw_data))
			unpack_args[-1] = Array(len(raw_data), Char, io_stream)

		res = unpack_func.call(unpack_args, *self._pfp__pack_func_call_info, no_cast=True)
		if isinstance(res, Array):
			res = res._pfp__build()

		io_stream = six.BytesIO(res)
		tmp_stream = bitwrap.BitwrappedStream(io_stream)

		self._pfp__no_unpack = True
		self._pfp__parse(tmp_stream)
		self._pfp__no_unpack = False
	
	def _pfp__can_unpack(self):
		"""Return if this field has a packer/pack/unpack methods
		set as well as a pack type
		"""
		return self._pfp__pack_type is not None
	
	def _pfp__unpack_data(self, raw_data):
		"""Means that the field has already been parsed normally,
		and that it now needs to be unpacked.

		:raw_data: A string of the data that the field consumed while parsing
		"""
		if self._pfp__pack_type is None:
			return
		if self._pfp__no_unpack:
			return

		unpack_func = self._pfp__packer
		unpack_args = []
		if self._pfp__packer is not None:
			unpack_func = self._pfp__packer
			unpack_args = [false(), raw_data]

		elif self._pfp__unpack is not None:
			unpack_func = self._pfp__unpack
			unpack_args = [raw_data]

		# does not need to be converted to a char array
		if not isinstance(unpack_func, functions.NativeFunction):
			io_stream = bitwrap.BitwrappedStream(six.BytesIO(raw_data))
			unpack_args[-1] = Array(len(raw_data), Char, io_stream)

		res = unpack_func.call(unpack_args, *self._pfp__pack_func_call_info, no_cast=True)
		if isinstance(res, Array):
			res = res._pfp__build()

		io_stream = six.BytesIO(res)
		tmp_stream = bitwrap.BitwrappedStream(io_stream)

		# TODO
		#tmp_stream.padded = self._pfp__interp.get_bitfield_padded()

		self._ = self._pfp__parsed_packed = self._pfp__pack_type(tmp_stream)

		self._._pfp__watch(self)

	def _pfp__offset(self):
		"""Get the offset of the field into the stream
		"""
		if self._pfp__parent is not None:
			self._pfp__parent
	
	def _pfp__handle_updated(self, watched_field):
		"""Handle the watched field that was updated
		"""
		self._pfp__no_notify = True

		# nested data has been changed, so rebuild the
		# nested data to update the field
		# TODO a global setting to determine this behavior?
		# could slow things down a bit for large nested structures

		# notice the use of _is_ here - 'is' != '=='. '==' uses
		# the __eq__ operator, while is compares id(object) results
		if watched_field is self._:
			self._pfp__pack_data()
		else:
			self._pfp__update_func.call(
				[self] + self._pfp__watch_fields,
				*self._pfp__update_func_call_info
			)

		self._pfp__no_notify = False
	
	def _pfp__notify_update(self, child=None):
		for watcher in self._pfp__watchers:
			watcher._pfp__handle_updated(self)
		if self._pfp__parent is not None:
			self._pfp__parent._pfp__notify_update(self)
	
	def _pfp__width(self):
		"""Return the width of the field (sizeof)
		"""
		raw_output = six.BytesIO()
		output = bitwrap.BitwrappedStream(raw_output)
		self._pfp__build(output)
		output.flush()
		return len(raw_output.getvalue())
	
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
		self._pfp__notify_parent()
	
	def _pfp__notify_parent(self):
		if self._pfp__no_notify:
			return

		for watcher in self._pfp__watchers:
			watcher._pfp__handle_updated(self)
		if self._pfp__parent is not None:
			self._pfp__parent._pfp__notify_update(self)
	
	def _pfp__build(self, output_stream=None, save_offset=False):
		"""Pack this field into a string. If output_stream is specified,
		write the output into the output stream

		:output_stream: Optional output stream to write the results to
		:save_offset: If true, the current offset into the stream will be saved in the field
		:returns: Resulting string if ``output_stream`` is not specified. Else the number of bytes writtern.

		"""
		raise NotImplemented("Inheriting classes must implement the _pfp__build function")
	
	def _pfp__parse(self, stream, save_offset=False):
		"""Parse this field from the ``stream``

		:stream: An IO stream that can be read from
		:save_offset: Save the offset into the stream
		:returns: None
		"""
		raise NotImplemented("Inheriting classes must implement the _pfp__parse function")
	
	def _pfp__maybe_unpack(self):
		"""Should be called after initial parsing to unpack any
		nested data types
		"""
		if self._pfp__pack_type is None or (self._pfp__pack is not None and self._pfp__packer is not None):
			return
		pass
	
	def _pfp__pack(self):
		"""Should be called after initial parsing
		"""
		pass

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
	
	def _pfp__show(self, level=0, include_offset=False):
		return repr(self)

class Void(Field):
	"""The void field - used for return value of a function"""
	pass

class Struct(Field):
	"""The struct field"""

	_pfp__show_name = "struct"

	def __init__(self, stream=None, metadata_processor=None):
		# ordered list of children
		super(Struct, self).__setattr__("_pfp__children", [])
		# for quick child access
		super(Struct, self).__setattr__("_pfp__children_map", {})

		super(Struct, self).__init__(metadata_processor=metadata_processor)

		if stream is not None:
			self._pfp__offset = stream.tell()
	
	def _pfp__process_fields_metadata(self):
		"""Tell each child to process its metadata
		"""
		for child in self._pfp__children:
			child._pfp__process_metadata()
	
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
	
	def _pfp__add_child(self, name, child, stream=None, overwrite=False):
		"""Add a child to the Struct field

		:name: The name of the child
		:child: A :class:`.Field` instance
		:returns: None
		"""
		if not overwrite and name in self._pfp__children_map:
			return self._pfp__handle_implicit_array(name, child)
		else:
			child._pfp__parent = self
			self._pfp__children.append(child)
			child._pfp__name = name
			self._pfp__children_map[name] = child
			return child
	
	def _pfp__handle_implicit_array(self, name, child):
		"""Handle inserting implicit array elements
		"""
		existing_child = self._pfp__children_map[name]
		if isinstance(existing_child, Array):
			# I don't think we should check this
			#
			#if existing_child.field_cls != child.__class__:
			#	raise errors.PfpError("implicit arrays must be sequential!")
			existing_child.append(child)
			return existing_child
		else:
			# I don't think we should check this
			#
			#if self._pfp__children[-1].__class__ != child.__class__:
			#	raise errors.PfpError("implicit arrays must be sequential!")

			cls = child._pfp__class if hasattr(child, "_pfp__class") else child.__class__
			ary = Array(0, cls)
			# since the array starts with the first item
			ary._pfp__offset = existing_child._pfp__offset
			ary._pfp__parent = self
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
	
	def _pfp__parse(self, stream, save_offset=False):
		"""Parse the incoming stream

		:stream: Input stream to be parsed
		:returns: Number of bytes parsed

		"""
		if save_offset:
			self._pfp__offset = stream.tell()

		res = 0
		for child in self._pfp__children:
			res += child._pfp__parse(stream, save_offset)
		return res
	
	def _pfp__build(self, stream=None, save_offset=False):
		"""Build the field and write the result into the stream

		:stream: An IO stream that can be written to
		:returns: None

		"""
		if save_offset and stream is not None:
			self._pfp__offset = stream.tell()

		# returns either num bytes written or total data
		res = utils.binary("") if stream is None else 0

		# iterate IN ORDER
		for child in self._pfp__children:
			child_res = child._pfp__build(stream, save_offset)
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
				children_map[name]._pfp__set_value(value)
			else:
				children_map[name] = value
				self._pfp__notify_parent()
			return children_map[name]
		else:
			# default getattr instead
			return super(Struct, self).__setattr__(name, value)
	
	def __repr__(self):
		return object.__repr__(self)
	
	def _pfp__show(self, level=0, include_offset=False):
		"""Show the contents of the struct
		"""
		res = []
		res.append("{}{} {{".format(
			"{:04x} ".format(self._pfp__offset) if include_offset else "",
			self._pfp__show_name
		))
		for child in self._pfp__children:
			res.append("{}{}{:10s} = {}".format(
				"    "*(level+1),
				"{:04x} ".format(child._pfp__offset) if include_offset else "",
				child._pfp__name,
				child._pfp__show(level+1, include_offset)
			))
		res.append("{}}}".format("    "*level))
		return "\n".join(res)

class Union(Struct):
	"""A union field, where each member is an alternate
	view of the data"""

	_pfp__buff = None
	_pfp__size = 0
	_pfp__show_name = "union"

	def __init__(self, stream=None, metadata_processor=None):
		"""Init the union and its buff stream
		"""
		super(Union, self).__init__(metadata_processor=metadata_processor)
		self._pfp__buff = six.BytesIO()

	def _pfp__add_child(self, name, child, stream=None):
		"""Add a child to the Union field

		:name: The name of the child
		:child: A :class:`.Field` instance
		:returns: None
		"""
		res = super(Union, self)._pfp__add_child(name, child)
		self._pfp__buff.seek(0, 0)
		child._pfp__build(stream=self._pfp__buff)
		size = len(self._pfp__buff.getvalue())
		self._pfp__buff.seek(0, 0)

		if stream is not None:
			curr_pos = stream.tell()
			stream.seek(curr_pos-size, 0)

		return res
	
	def _rebuild_internal_buff(self):
		"""rebuild the internal buffer for the union
		"""
		self._pfp__buff = six.BytesIO()
		for child in self._pfp__children:
			child._pfp__build(self._pfp__buff, save_offset=True)
			self._pfp__buff.seek(0, 0)
	
	def _pfp__parse(self, stream, save_offset=False):
		"""Parse the incoming stream

		:stream: Input stream to be parsed
		:returns: Number of bytes parsed
		"""
		if save_offset:
			self._pfp__offset = stream.tell()

		max_res = 0
		for child in self._pfp__children:
			child_res = child._pfp__parse(stream, save_offset)
			if child_res > max_res:
				max_res = child_res

			# rewind the stream
			stream.seek(child_res, -1)
		self._pfp__size = max_res

		self._pfp__buff = six.BytesIO(stream.read(self._pfp__size))
		return max_res
	
	def _pfp__build(self, stream=None, save_offset=False):
		"""Build the union and write the result into the stream.

		:stream: None
		:returns: None
		"""
		max_size = -1
		if stream is not None:
			for child in self._pfp__children:
				curr_pos = stream.tell()
				child._pfp__build(stream, save_offset)
				size = stream.tell() - curr_pos
				stream.seek(-size, 1)

				if size > max_size:
					max_size = size

			stream.seek(max_size, 1)

			return max_size
		else:
			self._rebuild_internal_buff()
			val = self._pfp__buff.getvalue()
			return val
	
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
	def _pfp__build(self, stream=None, save_offset=False):
		if stream is None:
			io_stream = six.BytesIO()
			tmp_stream = bitwrap.BitwrappedStream(io_stream)
			tmp_stream.padded = self._pfp__interp.get_bitfield_padded()
			super(Dom, self)._pfp__build(tmp_stream, save_offset=save_offset)

			# flush out any unaligned bitfields, etc
			tmp_stream.flush()
			res = io_stream.getvalue()
			return res
		else:
			if not isinstance(stream, bitwrap.BitwrappedStream):
				stream = bitwrap.BitwrappedStream(stream)
			return super(Dom, self)._pfp__build(stream, save_offset=save_offset)

class NumberBase(Field):
	"""The base field for all numeric fields"""

	# can be set on individual fields, for all numbers (NumberBase.endian = ...),
	# or specific number classes (Int.endian = ...)
	endian = BIG_ENDIAN		# default endianness is BIG_ENDIAN

	width = 4 				# number of bytes
	format = "i"			# default signed int
	bitsize = None			# for IntBase

	_pfp__value = 0			# default value
	
	def __init__(self, stream=None, bitsize=None, metadata_processor=None):
		"""Special init for the bitsize
		"""
		self.bitsize = get_value(bitsize)
		super(NumberBase, self).__init__(stream, metadata_processor=metadata_processor)

	def __nonzero__(self):
		"""Used for the not operator"""
		return self._pfp__value != 0
	
	def __bool__(self):
		"""Used for the not operator"""
		return self._pfp__value != 0

	def _pfp__parse(self, stream, save_offset=False):
		"""Parse the IO stream for this numeric field

		:stream: An IO stream that can be read from
		:returns: The number of bytes parsed
		"""
		if save_offset:
			self._pfp__offset = stream.tell()

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
	
	def _pfp__build(self, stream=None, save_offset=False):
		"""Build the field and write the result into the stream

		:stream: An IO stream that can be written to
		:returns: None

		"""
		if stream is not None and save_offset:
			self._pfp__offset = stream.tell()

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
		return self
	def __isub__(self, other):
		self._pfp__value -= self._pfp__get_root_value(other)
		return self
	def __imul__(self, other):
		self._pfp__value *= self._pfp__get_root_value(other)
		return self
	def __idiv__(self, other):
		self._pfp__value /= self._pfp__get_root_value(other)
		return self
	def __iand__(self, other):
		self._pfp__value &= self._pfp__get_root_value(other)
		return self
	def __ixor__(self, other):
		self._pfp__value ^= self._pfp__get_root_value(other)
		return self
	def __ior__(self, other):
		self._pfp__value |= self._pfp__get_root_value(other)
		return self
	def __ifloordiv__(self, other):
		self._pfp__value //= self._pfp__get_root_value(other)
		return self
	def __imod__(self, other):
		self._pfp__value %= self._pfp__get_root_value(other)
		return self
	def __ipow__(self, other):
		self._pfp__value **= self._pfp__get_root_value(other)
		return self
	def __ilshift__(self, other):
		self._pfp__value <<= self._pfp__get_root_value(other)
		return self
	def __irshift__(self, other):
		self._pfp__value >>= self._pfp__get_root_value(other)
		return self
	
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
		res = self.__class__()
		res._pfp__set_value(~self._pfp__value)
		return res
	
	def __neg__(self):
		res = self.__class__()
		res._pfp__set_value(-self._pfp__value)
		return res
	
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
				raw = b"\x00" + raw
			while len(raw) > self.width:
				raw = raw[1:]
			self._pfp__parse(six.BytesIO(raw))
		else:
			self._pfp__value = new_val

		self._pfp__notify_parent()

	def __repr__(self):
		f = ":0{}x".format(self.width*2)
		return ("{}({!r} [{" + f + "}]){}").format(
			self._pfp__cls_name(),
			self._pfp__value,
			self._pfp__value,
			":{}".format(self.bitsize) if self.bitsize is not None else ""
		)
	
	def _pfp__cls_name(self):
		"""
		"""
		return self.__class__.__name__
	
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

class Enum(IntBase):
	"""For teh enums"""

	enum_vals = None
	enum_cls = None
	enum_name = None

	def __init__(self, stream=None, enum_cls=None, enum_vals=None, bitsize=None, metadata_processor=None):
		"""Init the enum
		"""
		# discard the bitsize value
		self.enum_name = None

		if enum_vals is not None:
			self.enum_vals = enum_vals

		if enum_cls is not None:
			self.enum_cls = enum_cls
			self.endian = enum_cls.endian
			self.width = enum_cls.width
			self.format = enum_cls.format

		super(Enum, self).__init__(stream, metadata_processor=metadata_processor)
	
	def _pfp__parse(self, stream, save_offset=False):
		"""Parse the IO stream for this enum

		:stream: An IO stream that can be read from
		:returns: The number of bytes parsed
		"""
		res = super(Enum, self)._pfp__parse(stream, save_offset)

		if self._pfp__value in self.enum_vals:
			self.enum_name = self.enum_vals[self._pfp__value]
		else:
			self.enum_name = "?? UNK_ENUM ??"

		return res
	
	def __repr__(self):
		"""Add the enum name to the int representation
		"""
		res = super(Enum, self).__repr__()
		res += "({})".format(self.enum_name)
		return res
	
	def _pfp__cls_name(self):
		"""
		"""
		return "Enum<{}>".format(
			self.enum_cls.__name__
		)

# --------------------------------

class Array(Field):
	width = -1

	def __init__(self, width, field_cls, stream=None, metadata_processor=None):
		""" Create an array field of size "width" from the stream
		"""
		super(Array, self).__init__(stream=None, metadata_processor=metadata_processor)

		self.width = width
		self.field_cls = field_cls
		self.items = []
		self.raw_data = None

		if stream is not None:
			self._pfp__parse(stream, save_offset=True)
		else:
			for x in six.moves.range(self.width):
				self.items.append(self.field_cls())
	
	def append(self, item):
		# TODO check for consistent type
		item._pfp__parent = self
		self.items.append(item)
		self.width = len(self.items)
	
	def _is_stringable(self):
		# TODO WChar
		return self.field_cls in [Char, UChar]
	
	def _array_to_str(self, max_len=-1):
		if not self._is_stringable():
			return None

		if self.raw_data is not None:
			if max_len != -1:
				return PYSTR(self.raw_data)[:max_len]
			return self.raw_data

		res = ""
		for item in self.items:
			if max_len != -1 and len(res) >= max_len:
				break
			
			# null-terminate string
			if PYVAL(item) == 0:
				break

			# TODO WChar
			res += chr(PYVAL(item))
		return res
	
	def __eq__(self, other):
		if self._is_stringable() and other.__class__ in [String, WString, str]:
			res = self._array_to_str()
			return utils.binary(res) == utils.binary(PYSTR(other))
		else:
			raise Exception("TODO")
	
	def __ne__(self, other):
		return not self.__eq__(other)
	
	def _pfp__set_value(self, value):
		if value.__class__ not in [list, tuple]:
			raise Exception("Error, invalid value for array")

		# this shouldn't be enforced
		# e.g.
		# local uchar[16] = {0};
		# where the first item should be 0
		#
		#if len(value) != PYVAL(self.width):
		#	raise Exception("Array was declared as having {} items, not {} items".format(
		#		PYVAL(self.width),
		#		len(value)
		#	))

		if len(value) > PYVAL(self.width):
			raise Exception("This is not actual C, memory corruption is not allowed!")

		for idx,item in enumerate(value):
			self.items[idx] = item

		self._pfp__notify_parent()

	def _pfp__parse(self, stream, save_offset=False):
		start_offset = stream.tell()
		if save_offset:
			self._pfp__offset = start_offset

		# will always be known widths for these field types
		if issubclass(self.field_cls, NumberBase):
			length = self.field_cls.width * PYVAL(self.width)
			self.raw_data = stream.read(length)

			if self._pfp__can_unpack():
				self._pfp__unpack_data(self.raw_data)

		else:
			# optimizations... should reuse existing fields??
			self.items = []
			for x in six.moves.range(PYVAL(self.width)):
				field = self.field_cls(stream)
				field._pfp__name = "{}[{}]".format(
					self._pfp__name,
					x
				)
				#field._pfp__parse(stream, save_offset)
				self.items.append(field)

			if self._pfp__can_unpack():
				curr_offset = stream.tell()
				stream.seek(start_offset, 0)
				data = stream.read(curr_offset - start_offset)

				# this shouldn't be necessary....
				# stream.seek(curr_offset, 0)

				self._pfp__unpack_data(data)
	
	def _pfp__build(self, stream=None, save_offset=False):
		if stream is not None and save_offset:
			self._pfp__offset = stream.tell()

		if self.raw_data is None:
			res = 0 if stream is not None else utils.binary("")
			for item in self.items:
				res += item._pfp__build(stream=stream, save_offset=save_offset)
		else:
			if stream is None:
				return self.raw_data
			else:
				stream.write(self.raw_data)
				return len(self.raw_data)
		return res
	
	def _pfp__handle_updated(self, watched_field):
		if self.raw_data is not None and \
				watched_field._pfp__name is not None and \
				watched_field._pfp__name.startswith(self._pfp__name) and \
				watched_field._pfp__array_idx is not None:
			data = watched_field._pfp__build()
			offset = watched_field.width * watched_field._pfp__array_idx
			self.raw_data = self.raw_data[0:offset] + data + self.raw_data[offset + len(data):]
		else:
			super(Array, self)._pfp__handle_updated(watched_field)
	
	def __getitem__(self, idx):
		if self.raw_data is None:
			return self.items[idx]
		else:
			if self.width < 0 or idx+1 > self.width:
				raise IndexError(idx)
			width = self.field_cls.width
			offset = width * idx
			data = self.raw_data[offset:offset+width]

			stream = bitwrap.BitwrappedStream(six.BytesIO(data))
			res = self.field_cls(stream)
			res._pfp__watch(self)
			res._pfp__parent = self
			res._pfp__array_idx = idx
			res._pfp__name = "{}[{}]".format(
				self._pfp__name, idx
			)
			return res
	
	def __setitem__(self, idx, value):
		if isinstance(value, Field):
			if self.raw_data is None:
				self.items[idx] = value
			else:
				if self.width < 0 or idx+1 > self.width:
					raise IndexError(idx)
				data = value._pfp__build()
				offset = self.field_cls.width * idx
				self.raw_data = self.raw_data[0:offset] + data + self.raw_data[offset+self.field_cls.width:]
		else:
			self[idx]._pfp__set_value(value)

		self._pfp__notify_update(self)
	
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
	
	def _pfp__show(self, level=0, include_offset=False):
		if self._is_stringable():
			res = self.__repr__()
			if self._ is not None:
				packed_show = self._._pfp__show(level=level+1, include_offset=False)
				res += "\n" + ("    "*(level+1)) + "_ = " + packed_show
			return res

		res = [self.__repr__()]
		for idx,item in enumerate(self.items):
			item_res = "{}{}{}[{}] = {}".format(
				"    " * (level+1),
				"{:04x} ".format(item._pfp__offset) if include_offset else "",
				self._pfp__name,
				idx,
				item._pfp__show(level+2, include_offset)
			)
			res.append(item_res)

		return "\n".join(res)
	
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
			new_val = utils.string_escape(new_val)
		super(String, self)._pfp__set_value(new_val)

	def _pfp__parse(self, stream, save_offset=False):
		"""Read from the stream until the string is null-terminated

		:stream: The input stream
		:returns: None

		"""
		if save_offset:
			self._pfp__offset = stream.tell()

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
	
	def _pfp__build(self, stream=None, save_offset=False):
		"""Build the String field

		:stream: TODO
		:returns: TODO

		"""
		if stream is not None and save_offset:
			self._pfp__offset = stream.tell()

		data = self._pfp__value + utils.binary("\x00")
		if stream is None:
			return data
		else:
			stream.write(data)
			return len(data)
	
	def __getitem__(self, idx):
		if idx < 0 or idx+1 > len(self._pfp__value):
			raise IndexError(idx)
		
		val = self._pfp__value[idx:idx+1]
		stream = six.BytesIO(val)
		res = Char(stream)
		return res
	
	def __setitem__(self, idx, val):
		if idx < 0 or idx+1 > len(self._pfp__value):
			raise IndexError(idx)
		
		if isinstance(val, Field):
			val = val._pfp__build()[-1:]
		elif isinstance(val, int):
			val = utils.binary(chr(val))

		self._pfp__value = self._pfp__value[0:idx] + val + self._pfp__value[idx+1:]
	
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
			res = self._pfp__value + PYSTR(other)
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
			self._pfp__value += PYSTR(other)
		return self

class WString(String):
	width = -1
	read_size = 2
	terminator = utils.binary("\x00\x00")

	def _pfp__parse(self, stream, save_offset=False):
		String._pfp__parse(self, stream, save_offset)
		self._pfp__value = utils.binary(self._pfp__value.decode("utf-16le"))
	
	def _pfp__build(self, stream=None, save_offset=False):
		if stream is not None and save_offset:
			self._pfp__offset = stream.tell()

		val = self._pfp__value.decode("ISO-8859-1").encode("utf-16le") + b"\x00\x00"
		if stream is None:
			return val
		else:
			stream.write(val)
			return len(val)
