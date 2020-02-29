#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module contains the base classes used
when defining mutation strategies for pfp
"""


import contextlib
import glob
import os
import six


from pfp.fields import BitfieldRW, NumberBase
from pfp.bitwrap import BitwrappedStream
from pfp.utils import timeit


get_strategy = None
StratGroup = None
FieldStrat = None


class Changer(object):
    """
    """
    def __init__(self, orig_data):
        self._orig_data = bytearray(orig_data)
        self._change_set_stack = []

    @contextlib.contextmanager
    def change(self, field_set):
        """Intended to be used with a ``with`` block. Takes care of pushing
        and popping the changes, yields the modified data.
        """
        self.push_changes(field_set)
        try:
            modified_data = self.build()
            yield modified_data
        finally:
            self.pop_changes()

    def push_changes(self, field_set):
        """Push a new changeset onto the changeset stack for the provided
        set of fields.
        """
        new_change_set = []
        new_data = []
        for field in field_set:
            offset = field._pfp__offset
            if isinstance(field, NumberBase) and field.bitsize is not None:
                new_data = self._handle_bitfield(field)
            else:
                new_data = field._pfp__build()
            new_change_set.append((offset, new_data))
        self._change_set_stack.append(new_change_set)

    def pop_changes(self):
        """Return a version of the original data after popping the latest 
        """
        self._change_set_stack.pop()

    def build(self):
        """Apply all changesets to the original data
        """
        new_data = bytearray(self._orig_data)
        for change_set in self._change_set_stack:
            for offset, new_field_data in change_set:
                new_data[offset:offset+len(new_field_data)] = new_field_data
        return new_data
    
    def _handle_bitfield(self, field):
        """Find the field's first evenly-aligned previous sibling that is
        also a bitfield, as well as all subsequent siblings until a full
        bit "class" is reached. Build the entire set of bitfields as a group.

        E.g.:

            ushort a:1;
            ushort b:3;
            ushort c:10;
            ushort d:2;

        This entire group should be built
        """
        total_bits = field.width * 8;
        bit_offset = lambda x: total_bits - x._pfp__offset_bits

        fields_to_build = []
        curr_field = field._pfp__prev_sibling
        # previous siblings
        while curr_field is not None and bit_offset(curr_field) >= 0:
            fields_to_build.append(curr_field)
            curr_field = curr_field._pfp__prev_sibling

        fields_to_build = list(reversed(fields_to_build))
        fields_to_build.append(field)

        # next siblings
        curr_field = field._pfp__next_sibling
        while (curr_field is not None
                and isinstance(curr_field, field.__class__)
                and curr_field.bitsize is not None):
            if bit_offset(curr_field) + curr_field.bitsize > total_bits:
                break
            fields_to_build.append(curr_field)
            curr_field = curr_field._pfp__next_sibling

        core_stream = six.BytesIO(b"")
        bit_stream = BitwrappedStream(core_stream)
        bitfield_rw = BitfieldRW(None, field.__class__)
        bitfield_rw.reserved_bits = field.bitfield_rw.reserved_bits

        for to_build in fields_to_build:
            old_bitfield_rw = to_build.bitfield_rw
            to_build.bitfield_rw = bitfield_rw
            to_build._pfp__build(bit_stream)
            to_build.bitfield_rw = old_bitfield_rw

        return core_stream.getvalue()


def init():
    global get_strategy
    global StratGroup
    global FieldStrat
    import pfp.fuzz.strats

    get_strategy = pfp.fuzz.strats.get_strategy
    StratGroup = pfp.fuzz.strats.StratGroup
    FieldStrat = pfp.fuzz.strats.FieldStrat

    # load all of the built-in strategies
    for strat_file in glob.glob(
        os.path.join(os.path.dirname(__file__), "*.py")
    ):
        filename = os.path.basename(strat_file)
        if filename in ["__init__.py", "base.py"]:
            continue
        mod_name = filename.replace(".py", "").replace(".pyc", "")
        __import__("pfp.fuzz." + mod_name)


def changeset_mutate(field, strat_name_or_cls, num=100, at_once=1, yield_changed=False, fields_to_modify=None, base_data=None):
    """Mutate the provided field (probably a Dom or struct instance) using the
    strategy specified with ``strat_name_or_class``, yielding ``num`` mutations
    that affect up to ``at_once`` fields at once.

    This function will yield back the field after each mutation, optionally
    also yielding a ``set`` of fields that were mutated in that iteration (if ``yield_changed`` is
    ``True``). It should also be noted that the yielded set of changed fields *can*
    be modified and is no longer needed by the mutate() function.

    :param pfp.fields.Field field: The field to mutate (can be anything, not just Dom/Structs)
    :param strat_name_or_class: Can be the name of a strategy, or the actual strategy class (not an instance)
    :param int num: The number of mutations to yield
    :param int at_once: The number of fields to mutate at once
    :param bool yield_changed: Yield a list of fields changed along with the mutated dom
    :param bool use_changesets: If a performance optimization should be used that builds the full
       output once, and then replaced only the changed fields, including watchers, etc. **NOTE**
       this does not yet work fully with packed structures (https://pfp.readthedocs.io/en/latest/metadata.html#packer-metadata)
    :returns: generator
    """
    import pfp.fuzz.rand as rand

    init()

    strat = get_strategy(strat_name_or_cls)

    if fields_to_modify is not None:
        to_mutate = fields_to_modify
    else:
        to_mutate = strat.which(field)

    with_strats = []
    for to_mutate_field in to_mutate:
        field_strat = strat.get_field_strat(to_mutate_field)
        if field_strat is not None:
            with_strats.append((to_mutate_field, field_strat))

    # we don't need these ones anymore
    del to_mutate

    # build it once at the beginning
    if base_data is not None:
        changer = Changer(base_data)
    else:
        changer = Changer(field._pfp__build())

    count = 0
    for x in six.moves.range(num):
        try:
            idx_pool = set([x for x in six.moves.xrange(len(with_strats))])
            modified_fields = []

            # modify `at_once` number of fields OR len(with_strats) number of fields,
            # whichever is lower
            count = 0
            for at_onces in six.moves.xrange(min(len(with_strats), at_once)):
                count += 1
                # we'll never pull the same idx from idx_pool more than once
                # since we're removing the idx after choosing it
                rand_idx = rand.sample(idx_pool, 1)[0]
                idx_pool.remove(rand_idx)

                rand_field, field_strat = with_strats[rand_idx]

                rand_field._pfp__snapshot()
                mutated_fields = field_strat.mutate(rand_field)
                modified_fields.append(rand_field)
                modified_fields += mutated_fields

            with changer.change(modified_fields) as modified_data:
                if yield_changed:
                    yield modified_data, modified_fields
                else:
                    yield modified_data
        finally:
            for rand_field in modified_fields:
                rand_field._pfp__restore_snapshot()


def mutate(field, strat_name_or_cls, num=100, at_once=1, yield_changed=False):
    """Mutate the provided field (probably a Dom or struct instance) using the
    strategy specified with ``strat_name_or_class``, yielding ``num`` mutations
    that affect up to ``at_once`` fields at once.
    This function will yield back the field after each mutation, optionally
    also yielding a ``set`` of fields that were mutated in that iteration (if ``yield_changed`` is
    ``True``). It should also be noted that the yielded set of changed fields *can*
    be modified and is no longer needed by the mutate() function.
    :param pfp.fields.Field field: The field to mutate (can be anything, not just Dom/Structs)
    :param strat_name_or_class: Can be the name of a strategy, or the actual strategy class (not an instance)
    :param int num: The number of mutations to yield
    :param int at_once: The number of fields to mutate at once
    :param bool yield_changed: Yield a list of fields changed along with the mutated dom
    :returns: generator
    """
    import pfp.fuzz.rand as rand

    init()

    strat = get_strategy(strat_name_or_cls)
    to_mutate = strat.which(field)

    with_strats = []
    for to_mutate_field in to_mutate:
        field_strat = strat.get_field_strat(to_mutate_field)
        if field_strat is not None:
            with_strats.append((to_mutate_field, field_strat))

    # we don't need these ones anymore
    del to_mutate

    count = 0
    for x in six.moves.range(num):
        # save the current value of all subfields without
        # triggering events
        field._pfp__snapshot(recurse=True)

        try:
            chosen_fields = set()
            idx_pool = set([x for x in six.moves.xrange(len(with_strats))])

            # modify `at_once` number of fields OR len(with_strats) number of fields,
            # whichever is lower
            for at_onces in six.moves.xrange(min(len(with_strats), at_once)):
                # we'll never pull the same idx from idx_pool more than once
                # since we're removing the idx after choosing it
                rand_idx = rand.sample(idx_pool, 1)[0]
                idx_pool.remove(rand_idx)

                rand_field, field_strat = with_strats[rand_idx]
                chosen_fields.add(rand_field)

                field_strat.mutate(rand_field)

            if yield_changed:
                yield field, chosen_fields
            else:
                # yield back the original field
                yield field
        finally:
            # restore the saved value of all subfields without
            # triggering events
            field._pfp__restore_snapshot(recurse=True)
