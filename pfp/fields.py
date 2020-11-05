#!/usr/bin/env python
# encoding: utf-8

import contextlib
from intervaltree import IntervalTree, Interval
import json
import math
import re
import six
import struct

import pfp.errors as errors
import pfp.utils as utils
import pfp.bitwrap as bitwrap
import pfp.functions as functions


BIG_ENDIAN = ">"
LITTLE_ENDIAN = "<"


def true():
    """
    Return the number of the boolean.

    Args:
    """
    res = Int()
    res._pfp__value = 1
    return res


def false():
    """
    Returns an unsigned int that will be used as a number.

    Args:
    """
    res = Int()
    res._pfp__value = 0
    return res


def get_value(field):
    """
    Convert field value from field to string.

    Args:
        field: (str): write your description
    """
    if isinstance(field, Field):
        if isinstance(field, Array):
            return field._array_to_str()
        return field._pfp__value
    else:
        return field


def get_width(field):
    """
    Returns the width of a field.

    Args:
        field: (todo): write your description
    """
    if isinstance(field, Field):
        return field.width
    elif isinstance(field, int):
        if field == 0:
            return 1
        if field > 0:
            return int(math.ceil(field.bit_length() / 8.0))
        else:
            return int(math.ceil(((~field).bit_length() + 1) / 8.0))
    else:
        raise Exception("Unexpected type: {}".format(field))


def get_str(field):
    """
    Get string representation of field

    Args:
        field: (str): write your description
    """
    if isinstance(field, Array):
        res = field._array_to_str()
    elif isinstance(field, Char):
        res = chr(PYVAL(field))
    else:
        res = get_value(field)

    return utils.string(res)


def inherit_hash(cls):
    """
    Returns a hash of - > hash

    Args:
        cls: (todo): write your description
    """
    cls.__hash__ = Field.__hash__
    return cls


PYVAL = get_value
PYSTR = get_str


class BitfieldRW(object):
    """Handles reading and writing the total bits for the bitfield
    data type from the input stream, and correctly applying
    endian and bit direction settings.
    """

    def __init__(self, interp, cls):
        """Set the interpreter and stream for BitFieldReader

        :param pfp.interp.PfpInterp interp: The interpreter being used
        :param pfp.bitwrap.BitwrappedStream stream: The bitwrapped stream
        :param pfp.fields.Field cls: The class (a subclass of :any:`pfp.fields.Field`) - used to determine total size of bitfield (if padded).
        """
        self.interp = interp
        self.cls = cls
        self.max_bits = self.cls.width * 8
        self.reserved_bits = 0

        self.offset = None
        self.total_bits_read = 0

        # only used with padding is enabled
        self._cls_bits = None

        # used to write to the stream
        self._write_bits = []

    def reserve_bits(self, num_bits, stream):
        """Used to "reserve" ``num_bits`` amount of bits in order to keep track
        of consecutive bitfields (or are the called bitfield groups?).

        E.g. ::

            struct {
                char a:8, b:8;
                char c:4, d:4, e:8;
            }

        :param int num_bits: The number of bits to claim
        :param pfp.bitwrap.BitwrappedStream stream: The stream to reserve bits on
        :returns: If room existed for the reservation
        """
        padded = self.interp.get_bitfield_padded()
        num_bits = PYVAL(num_bits)

        if padded:
            num_bits = PYVAL(num_bits)
            if num_bits + self.reserved_bits > self.max_bits:
                return False

        # if unpadded, always allow it
        if not padded:
            if self._cls_bits is None:
                self._cls_bits = []

            # reserve bits will only be called just prior to reading the bits,
            # so check to see if we have enough bits in self._cls_bits, else
            # read what's missing
            diff = len(self._cls_bits) - num_bits
            if diff < 0:
                self._cls_bits += self._do_read_bits(stream, -diff)

        self.reserved_bits += num_bits
        return True

    def tell(self, stream):
        """
        Return the number of bytes in the stream.

        Args:
            self: (todo): write your description
            stream: (todo): write your description
        """
        if self.offset is None:
            return stream.tell()
        else:
            bytes_offset = self.total_bits_read // 8
            return self.offset + bytes_offset

    def tell_bits(self):
        """
        The number of the bits in bytes.

        Args:
            self: (todo): write your description
        """
        return 8 - (self.total_bits_read % 8)

    def read_bits(self, stream, num_bits, padded, left_right, endian):
        """Return ``num_bits`` bits, taking into account endianness and 
        left-right bit directions
        """
        if self._cls_bits is None and padded:
            raw_bits = self._do_read_bits(stream, self.cls.width * 8)
            self._cls_bits = self._endian_transform(raw_bits, endian)

        if self._cls_bits is not None:
            if num_bits > len(self._cls_bits):
                raise errors.PfpError("BitfieldRW reached invalid state")

            if left_right:
                res = self._cls_bits[:num_bits]
                self._cls_bits = self._cls_bits[num_bits:]
            else:
                res = self._cls_bits[-num_bits:]
                self._cls_bits = self._cls_bits[:-num_bits]
        else:
            res = self._do_read_bits(stream, num_bits)

        self.total_bits_read += len(res)
        return res

    def write_bits(self, stream, raw_bits, padded, left_right, endian):
        """Write the bits. Once the size of the written bits is equal
        to the number of the reserved bits, flush it to the stream
        """
        if padded:
            if left_right:
                self._write_bits += raw_bits
            else:
                self._write_bits = raw_bits + self._write_bits

            if len(self._write_bits) == self.reserved_bits:
                bits = self._endian_transform(self._write_bits, endian)

                # if it's padded, and all of the bits in the field weren't used,
                # we need to flush out the unused bits
                # TODO should we save the value of the unused bits so the data that
                # is written out matches exactly what was read?
                if self.reserved_bits < self.cls.width * 8:
                    filler = [0] * ((self.cls.width * 8) - self.reserved_bits)
                    if left_right:
                        bits += filler
                    else:
                        bits = filler + bits

                stream.write_bits(bits)
                self._write_bits = []

        else:
            # if an unpadded field ended up using the same BitfieldRW and
            # as a previous padded field, there will be unwritten bits left in
            # self._write_bits. These need to be flushed out as well
            if len(self._write_bits) > 0:
                stream.write_bits(self._write_bits)
                self._write_bits = []

            stream.write_bits(raw_bits)

    def _endian_transform(self, bits, endian):
        """
        Return the endian string representation of the string.

        Args:
            self: (todo): write your description
            bits: (int): write your description
            endian: (todo): write your description
        """
        res = []

        # perform endianness transformation
        for x in six.moves.range(self.cls.width):
            if endian == BIG_ENDIAN:
                curr_byte_idx = x
            else:
                curr_byte_idx = self.cls.width - x - 1
            res += bits[curr_byte_idx * 8 : (curr_byte_idx + 1) * 8]

        return res
    
    def _do_read_bits(self, stream, num):
        """Read ``num`` number of bits from the stream
        """
        if self.offset is None:
            self.offset = stream.tell()
        return stream.read_bits(num)


class Field(object):
    """Core class for all fields used in the Pfp DOM.
    
    All methods use the _pfp__XXX naming convention to
    avoid conflicting names used in templates, since
    struct fields will implement ``__getattr__`` and 
    ``__setattr__`` to directly access child fields"""

    _pfp__interp = None

    _pfp__name = None
    """The name of the Field"""

    _pfp__parent = None
    """The parent of the field"""

    _pfp__prev_sibling = None
    """The previous field in this scope"""

    _pfp__next_sibling = None
    """The next field in this scope"""

    _pfp__watchers = []
    """All fields that are watching this field"""

    _pfp__watch_fields = []
    """All fields that this field is watching"""

    def __init__(self, stream=None, metadata_processor=None):
        """
        Initialize the metadata

        Args:
            self: (todo): write your description
            stream: (todo): write your description
            metadata_processor: (str): write your description
        """
        super(Field, self).__init__()
        self._pfp__name = None
        self._pfp__frozen = False

        self._pfp__offset = -1
        self._pfp__offset_bits = None

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

        self._pfp__snapshot_stack = []

        if stream is not None:
            self._pfp__parse(stream, save_offset=True)

    def _pfp__get_class(self):
        """Return the class for this field. This would be used for things like
        integer promotion and type casting.
        """
        return self.__class__

    # see #51 - fields should have a method of returning the full path of its name
    def _pfp__path(self):
        """Return the full pathname of this field. E.g. given
        the template below, the ``a`` field would have a full
        path of ``root.nested.a``

        .. code-block:: c

            struct {
                struct {
                    char a;
                } nested;
            } root;
        """
        curr = self
        res = []
        while curr is not None:
            # don't show the meta __root name in the path
            if curr._pfp__name == "__root" and curr._pfp__parent is None:
                break

            if curr._pfp__name is not None:
                res.append(curr._pfp__name)

            if isinstance(curr._pfp__parent, Array):
                curr = curr._pfp__parent._pfp__parent
            else:
                curr = curr._pfp__parent

        return ".".join(reversed(res))

    def _pfp__snapshot(self, recurse=True):
        """Save off the current value of the field
        """
        if hasattr(self, "_pfp__value"):
            self._pfp__snapshot_stack.append(self._pfp__value)

    def _pfp__restore_snapshot(self, recurse=True):
        """Restore a saved value snapshot
        """
        if hasattr(self, "_pfp__value"):
            self._pfp__value = self._pfp__snapshot_stack.pop()

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
        if self._pfp__parent is not None and isinstance(
            self._pfp__parent, Union
        ):
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

    def _pfp__set_packer(
        self,
        pack_type,
        packer=None,
        pack=None,
        unpack=None,
        func_call_info=None,
    ):
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

        res = unpack_func.call(
            unpack_args, *self._pfp__pack_func_call_info, no_cast=True
        )
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

        res = unpack_func.call(
            unpack_args, *self._pfp__pack_func_call_info, no_cast=True
        )
        if isinstance(res, Array):
            res = res._pfp__build()

        io_stream = six.BytesIO(res)
        tmp_stream = bitwrap.BitwrappedStream(io_stream)

        tmp_stream.padded = self._pfp__interp.get_bitfield_padded()

        self._ = self._pfp__parsed_packed = self._pfp__pack_type(tmp_stream)

        self._._pfp__watch(self)

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
        elif self._pfp__update_func is not None:
            self._pfp__update_func.call(
                [self] + self._pfp__watch_fields,
                *self._pfp__update_func_call_info
            )

        self._pfp__no_notify = False

    def _pfp__notify_update(self, child=None):
        """
        Notify that the changes.

        Args:
            self: (todo): write your description
            child: (str): write your description
        """
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
        self._pfp__value = get_value(new_val)
        return self._pfp__notify_parent()

    def _pfp__notify_parent(self):
        """
        Notify the parent of the parent.

        Args:
            self: (todo): write your description
        """
        if self._pfp__no_notify:
            return []

        notified_watchers = []
        for watcher in self._pfp__watchers:
            watcher._pfp__handle_updated(self)
            notified_watchers.append(watcher)

        if self._pfp__parent is not None:
            self._pfp__parent._pfp__notify_update(self)
        return notified_watchers

    def _pfp__build(self, output_stream=None, save_offset=False):
        """Pack this field into a string. If output_stream is specified,
        write the output into the output stream

        :output_stream: Optional output stream to write the results to
        :save_offset: If true, the current offset into the stream will be saved in the field
        :returns: Resulting string if ``output_stream`` is not specified. Else the number of bytes writtern.

        """
        raise NotImplemented(
            "Inheriting classes must implement the _pfp__build function"
        )

    def _pfp__parse(self, stream, save_offset=False):
        """Parse this field from the ``stream``

        :stream: An IO stream that can be read from
        :save_offset: Save the offset into the stream
        :returns: None
        """
        raise NotImplemented(
            "Inheriting classes must implement the _pfp__parse function"
        )

    def _pfp__maybe_unpack(self):
        """Should be called after initial parsing to unpack any
        nested data types
        """
        if self._pfp__pack_type is None or (
            self._pfp__pack is not None and self._pfp__packer is not None
        ):
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
        """
        Returns a < = self.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
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
        """
        Returns the geometries of other.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        val = get_value(other)
        return self._pfp__value >= val

    def __ne__(self, other):
        """
        Returns true if self is not in self.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        val = get_value(other)
        return self._pfp__value != val

    def __eq__(self, other):
        """See if the two items are equal (True/False)

        :other: 
        :returns: 
        """
        val = get_value(other)
        return self._pfp__value == other

    # see #49 - needed for some fuzzing functionality changes (python3
    # was complaining about Fields not being hashable)
    #
    # Also note - this is not inheritable in python3 and MUST be explicitly
    # set: https://stackoverflow.com/a/1608907
    def __hash__(self):
        """
        Return a hash of the list.

        Args:
            self: (todo): write your description
        """
        #return self._pfp__value.__hash__()
        res = self._pfp__build()
        # bit fields return an array, not bytes
        if isinstance(res, list):
            return str(res).__hash__()
        return res.__hash__()

    def __repr__(self):
        """
        Return a human - readable representation of this object.

        Args:
            self: (todo): write your description
        """
        return "{}({!r})".format(self.__class__.__name__, self._pfp__value)

    def __getitem__(self, idx):
        """
        Return the item at indexx.

        Args:
            self: (todo): write your description
            idx: (list): write your description
        """
        if idx != 0:
            raise IndexError(idx)
        return self

    def _pfp__show(self, level=0, include_offset=False):
        """Return a representation of this field

        :param int level: The indent level of the output
        :param bool include_offset: Include the parsed offsets of this field
        """
        return repr(self)
    
    def _pfp__promote(self, other):
        """Noop promotion on the base NumberBase class
        """
        return other


@inherit_hash
class Void(Field):
    """The void field - used for return value of a function"""
    pass


@inherit_hash
class ImplicitArrayWrapper(Field):
    """
    """

    last_field = None
    implicit_array = None

    def __init__(self, last_field, implicit_array):
        """Redirect all attribute accesses to the ``last_field``, except for
        array indexing. Array indexing is forwarded on to the
        ``implicit_array``.
        """
        super(Field, self).__setattr__("last_field", last_field)
        super(Field, self).__setattr__("implicit_array", implicit_array)

    def _pfp__get_class(self):
        """Return the last field class type and not the array type. Overrides
        :any:`Field._pfp__get_class`.
        """
        return self.last_field._pfp__get_class()

    def __setattr__(self, name, value):
        """Custom setattr that forwards all sets to the last_field
        """
        return setattr(self.last_field, name, value)

    def __getattr__(self, name):
        """Custom getattr that forwards all gets to last_field.
        """
        return getattr(self.last_field, name)
    
    def __getitem__(self, key):
        """Let this ImplicitArrayWrapper act like an array
        """
        return self.implicit_array[key]


@inherit_hash
class Struct(Field):
    """The struct field"""

    _pfp__show_name = "struct"

    _pfp__children = []
    """All children of the struct, in order added"""

    _pfp__implicit_arrays = {}
    """Mapping of all implicit arrays in this struct. All implicit arrays will
    be resolved to a concrete array after parsing is complete"""

    _pfp__name_collisions = {}
    """Counters for any naming collisions"""

    _pfp__scope = None

    def __init__(self, stream=None, metadata_processor=None):
        """
        Initialize the metadata.

        Args:
            self: (todo): write your description
            stream: (todo): write your description
            metadata_processor: (str): write your description
        """
        # ordered list of children
        super(Struct, self).__setattr__("_pfp__children", [])
        # initialize implicit arrays for this struct instance
        super(Struct, self).__setattr__("_pfp__implicit_arrays", {})
        # for quick child access
        super(Struct, self).__setattr__("_pfp__children_map", {})

        # reinit it here just for this instance...
        self._pfp__name_collisions = {}

        super(Struct, self).__init__(metadata_processor=metadata_processor)

        if stream is not None:
            self._pfp__offset = stream.tell()

    def _pfp__finalize(self):
        """Finalize the results of parsing the data. Currently this involves:

          * resolving implicit arrays to concrete arrays
        """
        to_swap = []
        for child_name, child in six.iteritems(self._pfp__children_map):
            if isinstance(child, Struct):
                child._pfp__finalize()
                continue
            if child_name not in self._pfp__implicit_arrays:
                continue
            to_swap.append((child_name, child))

        for child_name, child in to_swap:
            implicit_array = self._pfp__implicit_arrays[child_name]
            self._pfp__children_map[child_name] = implicit_array
            self._pfp__scope.add_var(child_name, implicit_array)
            
    def _pfp__snapshot(self, recurse=True):
        """Save off the current value of the field
        """
        super(Struct, self)._pfp__snapshot(recurse=recurse)

        if recurse:
            for child in self._pfp__children:
                child._pfp__snapshot(recurse=recurse)

    def _pfp__restore_snapshot(self, recurse=True):
        """Restore the snapshotted value without triggering any events
        """
        super(Struct, self)._pfp__restore_snapshot(recurse=recurse)

        if recurse:
            for child in self._pfp__children:
                child._pfp__restore_snapshot(recurse=recurse)

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
            raise errors.PfpError(
                "struct initialization has wrong number of members"
            )

        modified_watchers = []
        for x in six.moves.range(len(self._pfp__children)):
            modified_watchers += self._pfp__children[x]._pfp__set_value(value[x])
        return modified_watches

    def _pfp__add_child(self, name, child, stream=None, overwrite=False):
        """Add a child to the Struct field. If multiple consecutive fields are
        added with the same name, an implicit array will be created to store
        all fields of that name.

        :param str name: The name of the child
        :param pfp.fields.Field child: The field to add
        :param bool overwrite: Overwrite existing fields (False)
        :param pfp.bitwrap.BitwrappedStream stream: unused, but her for compatability with Union._pfp__add_child
        :returns: The resulting field added
        """
        res = None
        if not overwrite and self._pfp__is_non_consecutive_duplicate(
            name, child
        ):
            res = self._pfp__handle_non_consecutive_duplicate(name, child)
        elif not overwrite and name in self._pfp__children_map:
            implicit_array = self._pfp__handle_implicit_array(name, child)

            # see #110 (https://github.com/d0c-s4vage/pfp/issues/110)
            # during parsing, duplicate (implicit) arrays should always
            # reference the last parsed variable of ``name``. However, if the
            # variable ``name`` is indexed, then the nth duplicate array item
            # should be returned.
            #
            # E.g.
            #
            #    int x;
            #    int x;
            #    int x;
            #    Printf("%d\n", x);    // prints the latest x value
            #    Printf("%d\n", x[0]); // prints the first x value
            #
            self._pfp__implicit_arrays[name] = implicit_array
            wrapper = self._pfp__children_map[name] = ImplicitArrayWrapper(child, implicit_array)
            res = wrapper
        else:
            child._pfp__parent = self
            self._pfp__children.append(child)
            child._pfp__name = name
            self._pfp__children_map[name] = child
            res = child

        if len(self._pfp__children) > 1:
            res._pfp__prev_sibling = self._pfp__children[-2]
            self._pfp__children[-2]._pfp__next_sibling = res

        return res

    def _pfp__handle_non_consecutive_duplicate(self, name, child, insert=True):
        """This new child, and potentially one already existing child, need to
        have a numeric suffix appended to their name.
        
        An entry will be made for this name in ``self._pfp__name_collisions`` to keep
        track of the next available suffix number"""
        if name in self._pfp__children_map:
            previous_child = self._pfp__children_map[name]

            # DO NOT cause __eq__ to be called, we want to test actual objects, not comparison
            # operators
            if previous_child is not child:
                self._pfp__handle_non_consecutive_duplicate(
                    name, previous_child, insert=False
                )
                del self._pfp__children_map[name]

        next_suffix = self._pfp__name_collisions.setdefault(name, 0)
        new_name = "{}_{}".format(name, next_suffix)
        child._pfp__name = new_name
        self._pfp__name_collisions[name] = next_suffix + 1
        self._pfp__children_map[new_name] = child
        child._pfp__parent = self

        if insert:
            self._pfp__children.append(child)

        return child

    def _pfp__is_non_consecutive_duplicate(self, name, child):
        """Return True/False if the child is a non-consecutive duplicately named
        field. Consecutive duplicately-named fields are stored in an implicit array,
        non-consecutive duplicately named fields have a numeric suffix appended to their name"""

        if len(self._pfp__children) == 0:
            return False

        # it should be an implicit array
        if self._pfp__children[-1]._pfp__name == name:
            return False

        # if it's elsewhere in the children name map OR a collision sequence has already been
        # started for this name, it should have a numeric suffix
        # appended
        elif (
            name in self._pfp__children_map
            or name in self._pfp__name_collisions
        ):
            return True

        # else, no collision
        return False

    def _pfp__handle_implicit_array(self, name, child):
        """Handle inserting implicit array elements
        """
        existing_child = self._pfp__children_map[name]
        existing_implicit_array = self._pfp__implicit_arrays.get(name, None)
        if isinstance(existing_implicit_array, Array):
            # I don't think we should check this
            #
            # if existing_child.field_cls != child.__class__:
            #    raise errors.PfpError("implicit arrays must be sequential!")
            existing_implicit_array.append(child)
            return existing_implicit_array
        else:
            cls = (
                child._pfp__class
                if hasattr(child, "_pfp__class")
                else child.__class__
            )
            ary = Array(0, cls)
            # since the array starts with the first item
            ary._pfp__offset = existing_child._pfp__offset
            ary._pfp__parent = self
            ary._pfp__name = name
            ary.implicit = True
            ary.append(existing_child)
            ary.append(child)

            exist_idx = -1
            for idx, child in enumerate(self._pfp__children):
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
        children_map = super(Struct, self).__getattribute__(
            "_pfp__children_map"
        )
        if name in children_map:
            return children_map[name]
        else:
            res = None
            if self._pfp__scope is not None:
                res = self._pfp__scope.get_var(name, recurse=False)
            if res is not None:
                return res

            # default getattr instead
            return super(Struct, self).__getattribute__(name)

    def __setattr__(self, name, value):
        """Custom __setattr__ for quick setting of children values
        
        If value is not an instance of ``Field``, assume it is the
        value for the field and that the field itself should not
        be overridden"""
        children_map = super(Struct, self).__getattribute__(
            "_pfp__children_map"
        )
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
        """
        Return a repr representation of the object.

        Args:
            self: (todo): write your description
        """
        return object.__repr__(self)

    def __eq__(self, other):
        """
        Determine if two values are equal.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        return self is other

    def _pfp__show(self, level=0, include_offset=False):
        """Show the contents of the struct
        """
        res = []
        res.append(
            "{}{} {{".format(
                "{:04x} ".format(self._pfp__offset) if include_offset else "",
                self._pfp__show_name,
            )
        )
        for child in self._pfp__children:
            res.append(
                "{}{}{:10s} = {}".format(
                    "    " * (level + 1),
                    "{:04x} ".format(child._pfp__offset)
                    if include_offset
                    else "",
                    child._pfp__name,
                    child._pfp__show(level + 1, include_offset),
                )
            )
        res.append("{}}}".format("    " * level))
        return "\n".join(res)
    
    def __iter__(self):
        """Iterate over this struct's children
        """
        return self._pfp__children.__iter__()


@inherit_hash
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

        if stream is not None:
            self._pfp__offset = stream.tell()
        self._pfp__buff = six.BytesIO()

    def _pfp__add_child(self, name, child, stream=None):
        """Add a child to the Union field

        :name: The name of the child
        :child: A :class:`.Field` instance
        :returns: The resulting field
        """
        res = super(Union, self)._pfp__add_child(name, child)
        self._pfp__buff.seek(0, 0)
        child._pfp__build(stream=self._pfp__buff)
        size = len(self._pfp__buff.getvalue())
        self._pfp__buff.seek(0, 0)

        if stream is not None:
            curr_pos = stream.tell()
            stream.seek(curr_pos - size, 0)

        return res

    def _pfp__notify_update(self, child=None):
        """Handle a child with an updated value
        """
        if getattr(self, "_pfp__union_update_other_children", True):
            self._pfp__union_update_other_children = False

            new_data = child._pfp__build()
            new_stream = bitwrap.BitwrappedStream(six.BytesIO(new_data))
            for other_child in self._pfp__children:
                if other_child is child:
                    continue

                if (
                    isinstance(other_child, Array)
                    and other_child.is_stringable()
                ):
                    other_child._pfp__set_value(new_data)
                else:
                    other_child._pfp__parse(new_stream)
                new_stream.seek(0)

            self._pfp__no_update_other_children = True

        super(Union, self)._pfp__notify_update(child=child)

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
        if stream is None:
            core_stream = six.BytesIO()
            new_stream = bitwrap.BitwrappedStream(core_stream)
        else:
            new_stream = stream

        for child in self._pfp__children:
            curr_pos = new_stream.tell()
            child._pfp__build(new_stream, save_offset)
            size = new_stream.tell() - curr_pos
            new_stream.seek(-size, 1)

            if size > max_size:
                max_size = size

        new_stream.seek(max_size, 1)

        if stream is None:
            return core_stream.getvalue()
        else:
            return max_size

    def __setattr__(self, name, value):
        """Custom __setattr__ to keep track of the order things
        are writen (to mimic writing to memory)
        """
        res = super(Union, self).__setattr__(name, value)
        children_map = super(Struct, self).__getattribute__(
            "_pfp__children_map"
        )

        if name in children_map:
            field = getattr(self, name)
            # back to the start of the buffer
            self._pfp__buff.seek(0, 0)
            field._pfp__build(stream=self._pfp__buff)

        return res


@inherit_hash
class Dom(Struct):
    """The main container struct for a template"""

    def __init__(self, *args, **kwargs):
        """
        Initialize the pfp type.

        Args:
            self: (todo): write your description
        """
        super(self.__class__, self).__init__(*args, **kwargs)

        # see keep_successful notes on pfp.parse and pfp.interp.PfpInterp.parse
        self._pfp__error = None
        self._pfp__types = None

    def __getattr__(self, attr_name):
        """Custom getattr for Dom class so types can also be
        accessed"""
        if self._pfp__types is not None and hasattr(
            self._pfp__types, attr_name
        ):
            return getattr(self._pfp__types, attr_name)
        else:
            return super(self.__class__, self).__getattr__(attr_name)

    """The result of an interpreted template"""

    def _pfp__build(self, stream=None, save_offset=False):
        """
        Builds the field

        Args:
            self: (todo): write your description
            stream: (todo): write your description
            save_offset: (bool): write your description
        """
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
            return super(Dom, self)._pfp__build(
                stream, save_offset=save_offset
            )


@inherit_hash
class NumberBase(Field):
    """The base field for all numeric fields"""

    # can be set on individual fields, for all numbers (NumberBase.endian = ...),
    # or specific number classes (Int.endian = ...)
    endian = (
        LITTLE_ENDIAN
    )  # default endianness is LITTLE_ENDIAN apparently..?? wtf

    width = 4  # number of bytes
    format = "i"  # default signed int
    bitsize = None  # for IntBase

    _pfp__value = 0  # default value

    @classmethod
    def _pfp__width(self):
        """Return the width of the current atomic type
        """
        return self.width

    def __init__(
        self,
        stream=None,
        bitsize=None,
        metadata_processor=None,
        bitfield_rw=None,
        bitfield_padded=False,
        bitfield_left_right=False,
    ):
        """Special init for the bitsize
        """
        self.bitsize = get_value(bitsize)
        self.bitfield_rw = bitfield_rw

        # fields need to remember if they were parsed with padded bits or not
        self.bitfield_padded = bitfield_padded
        self.bitfield_left_right = bitfield_left_right

        super(NumberBase, self).__init__(
            stream, metadata_processor=metadata_processor
        )

    def __nonzero__(self):
        """Used for the not operator"""
        return self._pfp__value != 0

    def __bool__(self):
        """Used for the not operator"""
        return self._pfp__value != 0

    def _pfp__parse(self, stream, save_offset=False, set_val=True):
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
            self._pfp__offset = self.bitfield_rw.tell(stream)
            self._pfp__offset_bits = self.bitfield_rw.tell_bits()

            bits = self.bitfield_rw.read_bits(
                stream,
                self.bitsize,
                self.bitfield_padded,
                self.bitfield_left_right,
                self.endian,
            )

            width_diff = self.width - (len(bits) // 8) - 1
            bits_diff = 8 - (len(bits) % 8)

            padding = [0] * (width_diff * 8 + bits_diff)

            bits = padding + bits

            data = bitwrap.bits_to_bytes(bits)
            if self.endian == LITTLE_ENDIAN:
                # reverse the data
                data = data[::-1]

        if len(data) < self.width:
            raise errors.PrematureEOF()

        val = struct.unpack(
            "{}{}".format(self.endian, self.format), data
        )[0]

        if set_val:
            self._pfp__data = data
            self._pfp__value = val
            return self.width
        else:
            return val

    def _pfp__build(
            self, stream=None, save_offset=False, ignore_bitfields=False,
        ):
        """Build the field and write the result into the stream

        :stream: An IO stream that can be written to
        :returns: None

        """
        if stream is not None and save_offset:
            self._pfp__offset = stream.tell()

        if ignore_bitfields or self.bitsize is None:
            data = struct.pack(
                "{}{}".format(self.endian, self.format), self._pfp__value
            )
            if stream is not None:
                stream.write(data)
                return len(data)
            else:
                return data
        else:
            data = struct.pack(
                "{}{}".format(BIG_ENDIAN, self.format), self._pfp__value
            )

            num_bytes = int(math.ceil(self.bitsize / 8.0))
            bit_data = data[-num_bytes:]

            raw_bits = bitwrap.bytes_to_bits(bit_data)
            bits = raw_bits[-self.bitsize :]

            if stream is not None:
                self.bitfield_rw.write_bits(
                    stream,
                    bits,
                    self.bitfield_padded,
                    self.bitfield_left_right,
                    self.endian,
                )
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
        """
        Add this set i { self.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        root = get_value(other)
        self._pfp__set_value(self._pfp__value + root)
        return self

    def __isub__(self, other):
        """
        Determine if this set objects are the same.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        root = get_value(other)
        self._pfp__set_value(self._pfp__value - root)
        return self

    def __imul__(self, other):
        """
        Return the result of - placeholders.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        self._pfp__value *= get_value(other)
        return self

    def __idiv__(self, other):
        """
        Return the unique idiv idivative identifier.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        self._pfp__value /= get_value(other)
        return self

    def __iand__(self, other):
        """
        Returns the i { self } objects.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        self._pfp__value &= get_value(other)
        return self

    def __ixor__(self, other):
        """
        Returns the value of this : class :.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        self._pfp__value ^= get_value(other)
        return self

    def __ior__(self, other):
        """
        Returns the value of self and other.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        self._pfp__value |= get_value(other)
        return self

    def __ifloordiv__(self, other):
        """
        Returns true ifloordivivivivivivivivivivative.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        self._pfp__value //= get_value(other)
        return self

    def __imod__(self, other):
        """
        Return the result of self and other.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        self._pfp__value %= get_value(other)
        return self

    def __ipow__(self, other):
        """
        Return a given ipow representation of self and other.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        self._pfp__value **= get_value(other)
        return self

    def __ilshift__(self, other):
        """
        Shifts the cursor objects.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        self._pfp__value <<= get_value(other)
        return self

    def __irshift__(self, other):
        """
        Shifts the current time by another.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        self._pfp__value >>= get_value(other)
        return self

    def __add__(self, other):
        """
        Add another : class to self to self.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        res = self.__class__()
        res._pfp__set_value(
            self._pfp__value + get_value(other)
        )
        return res

    def __sub__(self, other):
        """
        Subtodel.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        res = self.__class__()
        res._pfp__set_value(
            self._pfp__value - get_value(other)
        )
        return res

    def __mul__(self, other):
        """
        Mulmulvalue objects.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        res = self.__class__()
        res._pfp__set_value(
            self._pfp__value * get_value(other)
        )
        return res

    def __truediv__(self, other):
        """
        Returns the partial value of this set.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        res = self.__class__()
        # if truediv is being called, then / should also behave like
        # truediv (2/3 == 0.6666 instead of 0 [classic division])
        # the default in python 3 is truediv
        res._pfp__set_value(
            self._pfp__value / get_value(other)
        )
        return res

    def __div__(self, other):
        """
        Divide the two values.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        res = self.__class__()
        res._pfp__set_value(
            self._pfp__value / get_value(other)
        )
        return res

    def __and__(self, other):
        """
        Shared version of - place.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        res = self.__class__()
        res._pfp__set_value(
            self._pfp__value & get_value(other)
        )
        return res

    def __xor__(self, other):
        """
        Returns the value of other.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        res = self.__class__()
        res._pfp__set_value(
            self._pfp__value ^ get_value(other)
        )
        return res

    def __or__(self, other):
        """
        Shared version of self or b.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        res = self.__class__()
        res._pfp__set_value(
            self._pfp__value | get_value(other)
        )
        return res

    def __floordiv__(self, other):
        """
        Returns a new value for this record.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        res = self.__class__()
        res._pfp__set_value(
            self._pfp__value // get_value(other)
        )
        return res

    def __mod__(self, other):
        """
        Return a new set objects in self.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        res = self.__class__()
        res._pfp__set_value(
            self._pfp__value % get_value(other)
        )
        return res

    def __pow__(self, other):
        """
        Pow of the values.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        res = self.__class__()
        res._pfp__set_value(
            self._pfp__value ** get_value(other)
        )
        return res

    def __lshift__(self, other):
        """
        Shift this timeseries with another one.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        res = self.__class__()
        res._pfp__set_value(
            self._pfp__value << get_value(other)
        )
        return res

    def __rshift__(self, other):
        """
        Shift the current rshift together with another one.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        res = self.__class__()
        res._pfp__set_value(
            self._pfp__value >> get_value(other)
        )
        return res

    def __invert__(self):
        """
        Invert the field.

        Args:
            self: (todo): write your description
        """
        res = self.__class__()
        res._pfp__set_value(~self._pfp__value)
        return res

    def __neg__(self):
        """
        Returns the value of the value of the set.

        Args:
            self: (todo): write your description
        """
        res = self.__class__()
        res._pfp__set_value(-self._pfp__value)
        return res

    def __getattr__(self, val):
        """
        Return the value.

        Args:
            self: (todo): write your description
            val: (str): write your description
        """
        if val.startswith("__") and val.endswith("__"):
            return getattr(self._pfp__value, val)
        raise AttributeError(val)


@inherit_hash
class IntBase(NumberBase):
    """The base class for all integers"""

    signed = True

    def _pfp__maybe_promote(self, val1, val2):
        """Determine if val1 or val2 is larger - if one is larger, then the
        smaller will be promoted to the larger size. If val1 and val2 are the
        same size, val2 will be promoted to val1.

        :returns: tuple of new (maybe_promoted_val1, maybe_promoted_val2)
        """
        w_val1 = get_width(val1)
        w_val2 = get_width(val2)

        if w_val1 > w_val2:
            res = (val1, val1._pfp__promote(val2))
        elif w_val2 > w_val1:
            res = (val2._pfp__promote(val1), val2)
        else:
            res = (val1, val1._pfp__promote(val2))

        return (get_value(res[0]), get_value(res[1]))

    # from https://wiki.sei.cmu.edu/confluence/display/c/INT02-C.%2BUnderstand%2Binteger%2Bconversion%2Brules
    #
    # Integer Conversion Rank
    #
    # Every integer type has an integer conversion rank that determines how conversions are performed. The ranking is based on the concept that each integer type contains at least as many bits as the types ranked below it. The following rules for determining integer conversion rank are defined in the C Standard, subclause 6.3.1.1 [ISO/IEC 9899:2011]:
    # 
    # No two signed integer types shall have the same rank, even if they have the same representation.
    # The rank of a signed integer type shall be greater than the rank of any signed integer type with less precision.
    # The rank of long long int shall be greater than the rank of long int, which shall be greater than the rank of int, which shall be greater than the rank of short int, which shall be greater than the rank of signed char.
    # The rank of any unsigned integer type shall equal the rank of the corresponding signed integer type, if any.
    # The rank of any standard integer type shall be greater than the rank of any extended integer type with the same width.
    # The rank of char shall equal the rank of signed char and unsigned char.
    # The rank of _Bool shall be less than the rank of all other standard integer types.
    # The rank of any enumerated type shall equal the rank of the compatible integer type.
    # The rank of any extended signed integer type relative to another extended signed integer type with the same precision is implementation-defined but still subject to the other rules for determining the integer conversion rank.
    # For all integer types T1, T2, and T3, if T1 has greater rank than T2 and T2 has greater rank than T3, then T1 has greater rank than T3.
    # The integer conversion rank is used in the usual arithmetic conversions to determine what conversions need to take place to support an operation on mixed integer types.
    # 
    # Usual Arithmetic Conversions
    #
    # The usual arithmetic conversions are rules that provide a mechanism to yield a common type when both operands of a binary operator are balanced to a common type or the second and third operands of the conditional operator ( ? : ) are balanced to a common type. Conversions involve two operands of different types, and one or both operands may be converted. Many operators that accept arithmetic operands perform conversions using the usual arithmetic conversions. After integer promotions are performed on both operands, the following rules are applied to the promoted operands:
    # 
    # If both operands have the same type, no further conversion is needed.
    # If both operands are of the same integer type (signed or unsigned), the operand with the type of lesser integer conversion rank is converted to the type of the operand with greater rank.
    # If the operand that has unsigned integer type has rank greater than or equal to the rank of the type of the other operand, the operand with signed integer type is converted to the type of the operand with unsigned integer type.
    # If the type of the operand with signed integer type can represent all of the values of the type of the operand with unsigned integer type, the operand with unsigned integer type is converted to the type of the operand with signed integer type.
    # Otherwise, both operands are converted to the unsigned integer type corresponding to the type of the operand with signed integer type.
    def _pfp__promote(self, val):
        """Promote the provided value to the current class
        """
        if isinstance(val, IntBase):
            # will automatically convert correctly between ints of
            # different sizes, unsigned/signed, etc
            raw = val._pfp__build(ignore_bitfields=True)
            while len(raw) < self.width:
                if self.endian == BIG_ENDIAN:
                    raw = b"\x00" + raw
                else:
                    raw += b"\x00"

            while len(raw) > self.width:
                if self.endian == BIG_ENDIAN:
                    raw = raw[1:]
                else:
                    raw = raw[:-1]

            val = self._pfp__parse(
                six.BytesIO(raw),
                save_offset=False,
                set_val=False,
            )
        else:
            mask = 1 << (8 * self.width)

            if self.signed:
                max_val = (mask // 2) - 1
                min_val = -(mask // 2)
            else:
                max_val = mask - 1
                min_val = 0

            if val < min_val:
                val += -(min_val)
                val &= mask - 1
                val -= -(min_val)
            elif val > max_val:
                val &= mask - 1

        return val

    def _pfp__set_value(self, new_val):
        """Set the value, potentially converting an unsigned
        value to a signed one (and visa versa)"""
        if self._pfp__frozen:
            raise errors.UnmodifiableConst()

        promoted = self._pfp__promote(new_val)
        self._pfp__value = promoted

        return self._pfp__notify_parent()

    def __repr__(self):
        """
        Return a representation of this field.

        Args:
            self: (todo): write your description
        """
        f = ":0{}x".format(self.width * 2)
        return ("{}({!r} [{" + f + "}]){}").format(
            self._pfp__cls_name(),
            self._pfp__value,
            self._pfp__value,
            ":{}".format(self.bitsize) if self.bitsize is not None else "",
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

    def __cmp__(self, other):
        """Compare the Field to something else, either another
        Field or something else

        :other: Another Field instance or something else
        :returns: result of cmp()

        """
        cmp_self, cmp_other = self._pfp__maybe_promote(self, other)
        return cmp(cmp_self, cmp_other)

    def __lt__(self, other):
        """Compare the Field to something else, either another
        Field or something else

        :other: The other field
        :returns: True if equal
        """
        cmp_self, cmp_other = self._pfp__maybe_promote(self, other)
        return cmp_self < cmp_other

    def __le__(self, other):
        """
        See : meth : ~pywbem. cim

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        cmp_self, cmp_other = self._pfp__maybe_promote(self, other)
        return cmp_self <= cmp_other

    def __gt__(self, other):
        """Compare the Field to something else, either another
        Field or something else

        :other: The other field
        :returns: True if equal
        """
        cmp_self, cmp_other = self._pfp__maybe_promote(self, other)
        return cmp_self > cmp_other

    def __ge__(self, other):
        """
        See placeholder. compare

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        cmp_self, cmp_other = self._pfp__maybe_promote(self, other)
        return cmp_self >= cmp_other

    def __ne__(self, other):
        """
        See : meth : ~pywbem. cim

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        cmp_self, cmp_other = self._pfp__maybe_promote(self, other)
        return cmp_self != cmp_other

    def __eq__(self, other):
        """See if the two items are equal (True/False)

        :other: 
        :returns: 
        """
        cmp_self, cmp_other = self._pfp__maybe_promote(self, other)
        return cmp_self == cmp_other

    def __iadd__(self, other):
        """
        Adds the set.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        other = self._pfp__promote(other)
        root = get_value(other)
        self._pfp__set_value(self._pfp__value + root)
        return self

    def __isub__(self, other):
        """
        Determine if other?

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        other = self._pfp__promote(other)
        root = get_value(other)
        self._pfp__set_value(self._pfp__value - root)
        return self

    def __imul__(self, other):
        """
        Promote. imulers of self and other.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        other = self._pfp__promote(other)
        root = get_value(other)
        self._pfp__set_value(self._pfp__value * root)
        return self

    def __idiv__(self, other):
        """
        Returns the integer id of the other.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        other = self._pfp__promote(other)
        root = get_value(other)
        self._pfp__set_value(int(self._pfp__value / root))
        return self

    def __iand__(self, other):
        """
        Returns the two values.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        other = self._pfp__promote(other)
        root = get_value(other)
        self._pfp__set_value(self._pfp__value & root)
        return self

    def __ixor__(self, other):
        """
        Set the class.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        other = self._pfp__promote(other)
        root = get_value(other)
        self._pfp__set_value(self._pfp__value ^ root)
        return self

    def __ior__(self, other):
        """
        Sets the integer value.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        other = self._pfp__promote(other)
        root = get_value(other)
        self._pfp__set_value(self._pfp__value | root)
        return self

    def __ifloordiv__(self, other):
        """
        Return true ifloordivivivivivivivivivivivivivivative.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        # will always be floordiv with IntBase numbers
        return self.__idiv__(self, other)

    def __imod__(self, other):
        """
        Return the result of self and other.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        # NOTE: We are not doing the same style of integer promotion here.
        # this current implementation matches the C implementation.
        #
        # See the test_imod function in test_integer_promotion.py
        self._pfp__value %= get_value(other)
        return self

    def __ipow__(self, other):
        """
        Return a given ipow representation of self and other.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        self._pfp__value **= get_value(other)
        return self

    def __ilshift__(self, other):
        """
        Shifts the cursor objects.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        self._pfp__value <<= get_value(other)
        return self

    def __irshift__(self, other):
        """
        Shifts the current time by another.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        self._pfp__value >>= get_value(other)
        return self

    def __add__(self, other):
        """
        Return a new : class to self.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        res = self.__class__()
        res._pfp__set_value(self)
        # takes care of promotion already
        res += other
        return res

    def __sub__(self, other):
        """
        Subtodal of self.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        res = self.__class__()
        res._pfp__set_value(self)
        # takes care of promotion already
        res -= other
        return res

    def __mul__(self, other):
        """
        Return a new mul ( self.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        res = self.__class__()
        res._pfp__set_value(self)
        # takes care of promotion already
        res *= other
        return res

    def __truediv__(self, other):
        """
        Returns the difference between self and b.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        # no truediv for pfp fields - only classic division
        return self.__div__(other)

    def __div__(self, other):
        """
        Return a new multiset with the other.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        res = self.__class__()
        res._pfp__set_value(self)
        # takes care of promotion already
        res.__idiv__(other)
        return res

    def __and__(self, other):
        """
        Construct a new and b.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        res = self.__class__()
        res._pfp__set_value(self)
        # takes care of promotion already
        res &= other
        return res

    def __xor__(self, other):
        """
        Returns the value of the value of other.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        res = self.__class__()
        res._pfp__set_value(self)
        # takes care of promotion already
        res ^= other
        return res

    def __or__(self, other):
        """
        A decorator that sets.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        res = self.__class__()
        res._pfp__set_value(self)
        # takes care of promotion already
        res |= other
        return res

    def __floordiv__(self, other):
        """
        Returns the difference between self and other.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        return self.__div__(self, other)

    def __mod__(self, other):
        """
        Return a new set objects in self.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        res = self.__class__()
        res._pfp__set_value(
            self._pfp__value % get_value(other)
        )
        return res

    def __pow__(self, other):
        """
        Pow of the values.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        res = self.__class__()
        res._pfp__set_value(
            self._pfp__value ** get_value(other)
        )
        return res

    def __lshift__(self, other):
        """
        Shift this timeseries with another one.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        res = self.__class__()
        res._pfp__set_value(
            self._pfp__value << get_value(other)
        )
        return res

    def __rshift__(self, other):
        """
        Shift the current rshift together with another one.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        res = self.__class__()
        res._pfp__set_value(
            self._pfp__value >> get_value(other)
        )
        return res

    def __invert__(self):
        """
        Invert the field.

        Args:
            self: (todo): write your description
        """
        res = self.__class__()
        res._pfp__set_value(~self._pfp__value)
        return res

    def __neg__(self):
        """
        Returns the value of the value of the set.

        Args:
            self: (todo): write your description
        """
        res = self.__class__()
        res._pfp__set_value(-self._pfp__value)
        return res


@inherit_hash
class Char(IntBase):
    """A field representing a signed char"""

    width = 1
    format = "b"


@inherit_hash
class UChar(Char):
    """A field representing an unsigned char"""

    format = "B"
    signed = False


@inherit_hash
class Short(IntBase):
    """A field representing a signed short"""

    width = 2
    format = "h"


@inherit_hash
class UShort(Short):
    """A field representing an unsigned short"""

    format = "H"
    signed = False


@inherit_hash
class WChar(Short):
    """A field representing a signed wchar (aka short)"""

    pass


@inherit_hash
class WUChar(UShort):
    """A field representing an unsigned wuchar (aka ushort)"""

    signed = False


@inherit_hash
class Int(IntBase):
    """A field representing a signed int"""

    width = 4
    format = "i"


@inherit_hash
class UInt(Int):
    """A field representing an unsigned int"""

    format = "I"
    signed = False


@inherit_hash
class Int64(IntBase):
    """A field representing a signed int64"""

    width = 8
    format = "q"


@inherit_hash
class UInt64(Int64):
    """A field representing an unsigned int64"""

    format = "Q"
    signed = False


@inherit_hash
class Float(NumberBase):
    """A field representing a float"""

    width = 4
    format = "f"


@inherit_hash
class Double(NumberBase):
    """A field representing a double"""

    width = 8
    format = "d"


@inherit_hash
class Enum(IntBase):
    """The enum field class"""

    enum_vals = None
    enum_cls = None
    enum_name = None

    def __init__(
        self,
        stream=None,
        enum_cls=None,
        enum_vals=None,
        bitsize=None,
        metadata_processor=None,
        bitfield_rw=None,
        bitfield_padded=False,
        bitfield_left_right=False,
    ):
        """Init the enum
        """
        self.enum_name = None

        if enum_vals is not None:
            self.enum_vals = enum_vals

        if enum_cls is not None:
            self.enum_cls = enum_cls
            self.endian = enum_cls.endian
            self.width = enum_cls.width
            self.format = enum_cls.format

        super(Enum, self).__init__(
            stream,
            metadata_processor=metadata_processor,
            bitfield_rw=bitfield_rw,
            bitsize=bitsize,
            bitfield_padded=bitfield_padded,
            bitfield_left_right=bitfield_left_right,
        )

    def _pfp__parse(self, stream, save_offset=False, set_val=True):
        """Parse the IO stream for this enum

        :stream: An IO stream that can be read from
        :returns: The number of bytes parsed
        """
        res = super(Enum, self)._pfp__parse(stream, save_offset, set_val=set_val)

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
        return "Enum<{}>".format(self.enum_cls.__name__)


# --------------------------------


@inherit_hash
class Array(Field):
    """The array field"""

    width = -1
    """The number of items of the array. ``len(array_field)`` also works"""

    raw_data = None
    """The raw data of the array. Note that this will only be
    set if the array's items are a core type (E.g. Int, Char, etc)"""

    field_cls = None
    """The class for items in the array"""

    implicit = False
    """If the array is an implicit array or not"""

    def __init__(self, width, field_cls, stream=None, metadata_processor=None):
        """ Create an array field of size "width" from the stream
        """
        super(Array, self).__init__(
            stream=None, metadata_processor=metadata_processor
        )

        self.width = width
        self.field_cls = field_cls
        self.items = []
        self.raw_data = None
        self.implicit = False

        self._pfp__snapshot_raw_stack = []

        if stream is not None:
            self._pfp__parse(stream, save_offset=True)
        else:
            if width is not None:
                for x in six.moves.range(self.width):
                    self.items.append(self.field_cls())

    def _pfp__snapshot(self, recurse=True):
        """Save off the current value of the field
        """
        super(Array, self)._pfp__snapshot(recurse=recurse)
        self._pfp__snapshot_raw_stack.append(self.raw_data)

        if recurse:
            for item in self.items:
                item._pfp__snapshot(recurse=recurse)

    def _pfp__restore_snapshot(self, recurse=True):
        """Restore the snapshotted value without triggering any events
        """
        super(Array, self)._pfp__restore_snapshot(recurse=recurse)
        self.raw_data = self._pfp__snapshot_raw_stack.pop()

        if recurse:
            for item in self.items:
                item._pfp__restore_snapshot(recurse=recurse)

    def append(self, item):
        """
        Append item to the end of the end of the end.

        Args:
            self: (todo): write your description
            item: (array): write your description
        """
        # TODO check for consistent type
        item._pfp__parent = self
        self.items.append(item)
        self.width = len(self.items)

    def is_stringable(self):
        """
        Return true if the field is a string

        Args:
            self: (todo): write your description
        """
        # TODO WChar
        return self.field_cls in [Char, UChar]

    def _array_to_str(self, max_len=-1):
        """
        Return a string representation : numpy : classable string.

        Args:
            self: (todo): write your description
            max_len: (int): write your description
        """
        if not self.is_stringable():
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
        """
        Returns true if other is a binary.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        if self.is_stringable() and other.__class__ in [String, WString, str, bytes]:
            res = self._array_to_str()
            return utils.binary(res) == utils.binary(PYSTR(other))
        else:
            raise Exception("TODO")

    def __ne__(self, other):
        """
        Determine if self and false otherwise.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        return not self.__eq__(other)

    def _pfp__set_value(self, value):
        """
        Set the field value of the field.

        Args:
            self: (todo): write your description
            value: (todo): write your description
        """
        is_string_type = False

        if isinstance(value, String):
            is_string_type = True
            value = value._pfp__build()

        else:
            for string_type in list(six.string_types) + [bytes]:
                if isinstance(value, string_type):
                    is_string_type = True
                    break

        if is_string_type and self.is_stringable():
            self.raw_data = value
            self.width = len(value)
            return self._pfp__notify_parent()

        if value.__class__ not in [list, tuple]:
            raise Exception("Error, invalid value for array")

        # this shouldn't be enforced
        # e.g.
        # local uchar[16] = {0};
        # where the first item should be 0
        #
        # if len(value) != PYVAL(self.width):
        #    raise Exception("Array was declared as having {} items, not {} items".format(
        #        PYVAL(self.width),
        #        len(value)
        #    ))

        if len(value) > len(self.items):
            self.items.extend([None] * (len(value) - len(self.items)))

        for idx, item in enumerate(value):
            if not isinstance(item, Field):
                new_item = self.field_cls()
                new_item._pfp__set_value(item)
                item = new_item
            self.items[idx] = item

        self.width = len(self.items)

        # see #54 - make sure raw_data is set to None if overwriting with
        # a new array/list/set/tuple
        self.raw_data = None

        return self._pfp__notify_parent()

    def _pfp__parse(self, stream, save_offset=False):
        """
        Parse the stream.

        Args:
            self: (todo): write your description
            stream: (todo): write your description
            save_offset: (bool): write your description
        """
        start_offset = stream.tell()
        if save_offset:
            self._pfp__offset = start_offset

        if self.width is None:
            return

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
                field._pfp__name = "{}[{}]".format(self._pfp__name, x)
                # field._pfp__parse(stream, save_offset)
                self.items.append(field)

            if self._pfp__can_unpack():
                curr_offset = stream.tell()
                stream.seek(start_offset, 0)
                data = stream.read(curr_offset - start_offset)

                # this shouldn't be necessary....
                # stream.seek(curr_offset, 0)

                self._pfp__unpack_data(data)

    def _pfp__build(self, stream=None, save_offset=False):
        """
        Build the raw binary stream.

        Args:
            self: (todo): write your description
            stream: (todo): write your description
            save_offset: (bool): write your description
        """
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
        """
        Handles the updated field.

        Args:
            self: (todo): write your description
            watched_field: (str): write your description
        """
        if (
            self.raw_data is not None
            and watched_field._pfp__name is not None
            and watched_field._pfp__name.startswith(self._pfp__name)
            and watched_field._pfp__array_idx is not None
        ):
            data = watched_field._pfp__build()
            offset = watched_field.width * watched_field._pfp__array_idx
            self.raw_data = (
                self.raw_data[0:offset]
                + data
                + self.raw_data[offset + len(data) :]
            )
        else:
            super(Array, self)._pfp__handle_updated(watched_field)

    def __getitem__(self, idx):
        """
        Return the item at index of the item

        Args:
            self: (todo): write your description
            idx: (list): write your description
        """
        if self.raw_data is None:
            return self.items[idx]
        else:
            if self.width < 0 or idx + 1 > self.width:
                raise IndexError(idx)
            width = self.field_cls.width
            offset = width * idx
            data = self.raw_data[offset : offset + width]

            stream = bitwrap.BitwrappedStream(six.BytesIO(data))
            res = self.field_cls(stream)
            res._pfp__watch(self)
            res._pfp__parent = self
            res._pfp__array_idx = idx
            res._pfp__name = "{}[{}]".format(self._pfp__name, idx)
            return res

    def __setitem__(self, idx, value):
        """
        Set the item to the given index.

        Args:
            self: (todo): write your description
            idx: (str): write your description
            value: (str): write your description
        """
        if isinstance(value, Field):
            if self.raw_data is None:
                self.items[idx] = value
            else:
                if self.width < 0 or idx + 1 > self.width:
                    raise IndexError(idx)
                data = value._pfp__build()
                offset = self.field_cls.width * idx
                self.raw_data = (
                    self.raw_data[0:offset]
                    + data
                    + self.raw_data[offset + self.field_cls.width :]
                )
        else:
            self[idx]._pfp__set_value(value)

        self._pfp__notify_update(self)

    def __repr__(self):
        """
        Return a human - readable string.

        Args:
            self: (todo): write your description
        """
        other = ""
        if self.is_stringable():
            res = self._array_to_str(20)
            other = " ({!r})".format(res)

        return "{}[{}]{}".format(
            self.field_cls.__name__
            if type(self.field_cls) is type
            else self.field_cls._typedef_name,
            PYVAL(self.width),
            other,
        )

    def _pfp__show(self, level=0, include_offset=False):
        """
        Return a string representation of this object.

        Args:
            self: (todo): write your description
            level: (int): write your description
            include_offset: (bool): write your description
        """
        if self.is_stringable():
            res = self.__repr__()
            if self._ is not None:
                packed_show = self._._pfp__show(
                    level=level + 1, include_offset=False
                )
                res += "\n" + ("    " * (level + 1)) + "_ = " + packed_show
            return res

        res = [self.__repr__()]
        for idx, item in enumerate(self.items):
            item_res = "{}{}{}[{}] = {}".format(
                "    " * (level + 1),
                "{:04x} ".format(item._pfp__offset) if include_offset else "",
                self._pfp__name,
                idx,
                item._pfp__show(level + 2, include_offset),
            )
            res.append(item_res)

        return "\n".join(res)

    def __len__(self):
        """
        The length of the field.

        Args:
            self: (todo): write your description
        """
        if self.raw_data is not None:
            return int(len(self.raw_data) / self.field_cls.width)
        else:
            return len(self.items)

    def __iter__(self):
        """Iterate over all items in this array
        """
        return self.items.__iter__()


# http://www.sweetscape.com/010editor/manual/ArraysStrings.htm
@inherit_hash
class String(Field):
    """A null-terminated string. String fields should be interchangeable
    with char arrays"""

    # if the width is -1 when parse is called, read until null
    # termination.
    width = -1
    read_size = 1
    terminator = utils.binary("\x00")

    def __init__(self, stream=None, metadata_processor=None):
        """
        Initialize the stream.

        Args:
            self: (todo): write your description
            stream: (todo): write your description
            metadata_processor: (str): write your description
        """
        self._pfp__value = utils.binary("")

        super(String, self).__init__(
            stream=stream, metadata_processor=metadata_processor
        )

    def _pfp__set_value(self, new_val):
        """Set the value of the String, taking into account
        escaping and such as well
        """
        if not isinstance(new_val, Field):
            new_val = utils.binary(new_val)
        return super(String, self)._pfp__set_value(new_val)

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
        """
        Return the item at indexx.

        Args:
            self: (todo): write your description
            idx: (list): write your description
        """
        if idx < 0 or idx + 1 > len(self._pfp__value):
            raise IndexError(idx)

        val = self._pfp__value[idx : idx + 1]
        stream = six.BytesIO(val)
        res = Char(stream)
        return res

    def __setitem__(self, idx, val):
        """
        Set the item at the given index.

        Args:
            self: (todo): write your description
            idx: (str): write your description
            val: (int): write your description
        """
        if idx < 0 or idx + 1 > len(self._pfp__value):
            raise IndexError(idx)

        if isinstance(val, Field):
            val = val._pfp__build()[-1:]
        elif isinstance(val, int):
            val = utils.binary(chr(val))

        self._pfp__value = (
            self._pfp__value[0:idx] + val + self._pfp__value[idx + 1 :]
        )

    def __add__(self, other):
        """Add two strings together. If other is not a String instance,
        a fields.String instance will still be returned

        :other: TODO
        :returns: TODO

        """
        res_field = String()
        res = utils.binary("")
        if isinstance(other, String):
            res = self._pfp__value + other._pfp__value
        else:
            res = self._pfp__value + utils.binary(PYSTR(other))
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
            self._pfp__value += utils.binary(PYSTR(other))
        return self

    def __len__(self):
        """
        Returns the length of the field.

        Args:
            self: (todo): write your description
        """
        return len(self._pfp__value)


@inherit_hash
class WString(String):
    width = -1
    read_size = 2
    terminator = utils.binary("\x00\x00")

    def _pfp__parse(self, stream, save_offset=False):
        """
        Parse the stream.

        Args:
            self: (todo): write your description
            stream: (str): write your description
            save_offset: (bool): write your description
        """
        String._pfp__parse(self, stream, save_offset)
        self._pfp__value = utils.binary(self._pfp__value.decode("utf-16le"))

    def _pfp__build(self, stream=None, save_offset=False):
        """
        Build the string representation of this field.

        Args:
            self: (todo): write your description
            stream: (todo): write your description
            save_offset: (bool): write your description
        """
        if stream is not None and save_offset:
            self._pfp__offset = stream.tell()

        val = (
            self._pfp__value.decode("ISO-8859-1").encode("utf-16le")
            + b"\x00\x00"
        )
        if stream is None:
            return val
        else:
            stream.write(val)
            return len(val)
