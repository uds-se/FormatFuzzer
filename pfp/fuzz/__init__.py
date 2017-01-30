#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module contains the base classes used
when defining mutation strategies for pfp
"""


import glob
import os
import six


get_strategy = None
StratGroup = None
FieldStrat = None


def init():
    global get_strategy
    global StratGroup
    global FieldStrat
    import pfp.fuzz.strats

    get_strategy = pfp.fuzz.strats.get_strategy
    StratGroup = pfp.fuzz.strats.StratGroup
    FieldStrat = pfp.fuzz.strats.FieldStrat

    # load all of the built-in strategies
    for strat_file in glob.glob(os.path.join(os.path.dirname(__file__), "*.py")):
        filename = os.path.basename(strat_file)
        if filename in ["__init__.py", "base.py"]:
            continue
        mod_name = filename.replace(".py", "").replace(".pyc", "")
        __import__("pfp.fuzz." + mod_name)


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

    # save the current value of all subfields without
    # triggering events
    field._pfp__snapshot(recurse=True)

    count = 0
    for x in six.moves.range(num):

        chosen_fields = set()
        idx_pool = set([x for x in six.moves.xrange(len(with_strats))])

        # modify `at_once` number of fields OR len(with_strats) number of fields,
        # whichever is lower
        for at_onces in six.moves.xrange(min(len(with_strats), at_once)):
            # we'll never pull the same idx from idx_pool more than once
            # since we're removing the idx after choosing it
            rand_idx = rand.sample(idx_pool, 1)[0]
            idx_pool.remove(rand_idx)

            rand_field,field_strat = with_strats[rand_idx]
            chosen_fields.add(rand_field)

            field_strat.mutate(rand_field)
        
        if yield_changed:
            yield field, chosen_fields
        else:
            # yield back the original field
            yield field

        # restore the saved value of all subfields without
        # triggering events
        field._pfp__restore_snapshot(recurse=True)
