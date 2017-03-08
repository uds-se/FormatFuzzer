#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
This module contains the base classes used
when defining fuzzing strategies for pfp
"""


# system imports
import glob
import os
import six


# local imports
import pfp.fields
import pfp.errors


class MutationError(pfp.errors.PfpError):
    pass


STRATS = {}
"""Stores information on registered StatGroups"""

def get_strategy(name_or_cls):
    """Return the strategy identified by its name. If ``name_or_class`` is a class,
    it will be simply returned.
    """
    if isinstance(name_or_cls, six.string_types):
        if name_or_cls not in STRATS:
            raise MutationError("strat is not defined")
        return STRATS[name_or_cls]()

    return name_or_cls()


class StratGroupMeta(type):
    """A metaclass for StratGroups that tracks subclasses
    of the StatGroup class.
    """
    def __init__(cls, *args, **kwargs):
        global STRATS

        if cls.name is None and cls.__name__ != "StratGroup":
            raise MutationError("Subclasses of StratGroup must specify a name for the group")

        STRATS[cls.name] = cls
            
        super(StratGroupMeta, cls).__init__(*args, **kwargs)


@six.add_metaclass(StratGroupMeta)
class StratGroup(object):
    """StatGroups choose which sub-fields should be mutated, and which FieldStrat should
    be used to do the mutating.

    The ``filter_fields`` method is intended to be overridden to provide
    custom filtering of child leaf fields should be mutated.
    """

    name = None
    """The unique name of the fuzzing strategy group. Can be used as the ``strat_name_or_cls`` parameter
    to the :any:`pfp.fuzz.mutate() <pfp.fuzz.mutate>` function
    """

    def __init__(self):
        self._strats = {}

        # make a mapping for quick lookups
        for member in dir(self):
            val = getattr(self, member)
            if type(val) == type and issubclass(val, FieldStrat):
                field_strat = val()

                if isinstance(field_strat.klass, (tuple, list)):
                    klasses = field_strat.klass
                else:
                    klasses = [field_strat.klass]

                for klass in klasses:
                    self._strats[klass] = field_strat
                    if hasattr(klass, "__name__"):
                        self._strats[klass.__name__] = field_strat

    def get_field_strat(self, field):
        """Return the strategy defined for the field.
        
        :field: The field
        :returns: The FieldStrat for the field or None
        """
        # this will work for exact matches if the class itself is referenced
        val = self._strats.get(field.__class__, None)
        if val is not None:
            return val

        # this will work for string names of classes
        val = self._strats.get(field.__class__.__name__, None)
        if val is not None:
            return val

        # now this will work for subclasses
        for k,v in six.iteritems(self._strats):
            # only check subclasses for class keys
            if type(k) is type and isinstance(field, k):
                return v

        return None


    def which(self, field):
        """Return a list of leaf fields that should be mutated. If the field
        passed in is a leaf field, it will be returned in a list.
        """
        if not isinstance(field, (pfp.fields.Struct, pfp.fields.Array)) and field._ is None:
            return [field]

        iter_fields = []

        # packed fields need to be checked first! Otherwise it may be a char array
        # and the list of field.items will be returned
        if field._ is not None:
            iter_fields = field._._pfp__children
            
        elif isinstance(field, pfp.fields.Struct):
            iter_fields = field._pfp__children

        elif isinstance(field, pfp.fields.Array):
            if field.raw_data is not None:
                return [field]
            else:
                iter_fields = field.items

        res = []
        for subfield in iter_fields:
            res += self.which(subfield)

        res = self.filter_fields(res)

        return res

    def filter_fields(self, field_list):
        """Intented to be overridden. Should return a list of fields to
        be mutated.

        :field_list: The list of fields to filter
        """
        return field_list


class FieldStrat(object):
    """A FieldStrat is used to define a fuzzing strategy for a specific field
    (or list of fields). A list of choices can be defined, or a set or probabilities
    that will yield 
    """

    choices = None
    """An enumerable of new value choices to choose from when mutating.

    This can also be a function/callable that returns an enumerable of choices. If it is
    a callable, the currently-being-fuzzed field will be passed in as a parameter.
    """

    prob = None
    """An enumerable of probabilities used to choose from when mutating
    E.g.::

        [
            (0.50, 0xffff),             # 50% of the time it should be the value 0xffff
            (0.25, xrange(0, 0x100)),   # 25% of the time it should be in the range [0, 0x100)
            (0.20, [0, 0xff, 0x100]),   # 20% of the time it should be on of 0, 0xff, or 0x100
            (0.05, {"min": 0, "max": 0x1000}), # 5% of the time, generate a number in [min, max)
        ]

    NOTE that the percentages need to add up to 100.

    This can also be a function/callable that returns an probabilities list. If it is
    a callable, the currently-being-fuzzed field will be passed in as a parameter.
    """

    klass = None
    """The class this strategy should be applied to. Can be a pfp.fields.field class
    (or subclass) or a string of the class name.

    Note that strings for the class name will only apply to direct instances
    of that class and not instances of subclasses.

    Can also be a list of classes or class names.
    """

    def mutate(self, field):
        """Mutate the given field, modifying it directly. This is not
        intended to preserve the value of the field.

        :field: The pfp.fields.Field instance that will receive the new value
        """
        new_val = self.next_val(field)
        field._pfp__set_value(new_val)
        return field

    def next_val(self, field):
        """Return a new value to mutate a field with. Do not modify the field directly
        in this function. Override the ``mutate()`` function if that is needed (the field is
        only passed into this function as a reference).

        :field: The pfp.fields.Field instance that will receive the new value. Passed in for reference only.
        :returns: The next value for the field
        """
        import pfp.fuzz.rand as rand

        if self.choices is not None:
            choices = self._resolve_member_val(self.choices, field)
            new_val = rand.choice(choices)
            return self._resolve_val(new_val)

        elif self.prob is not None:
            prob = self._resolve_member_val(self.prob, field)
            rand_val = rand.random()
            curr_total = 0.0
            # iterate through each of the probability choices until
            # we reach one that matches the current rand_val
            for prob_percent, prob_val in prob:
                if rand_val <= curr_total + prob_percent:
                    return self._resolve_val(prob_val)
                curr_total += prob_percent

            raise MutationError("probabilities did not add up to 100%! {}".format(
                [str(x[0]) + " - " + str(x[1])[:10] for x in prob]
            ))

    # -----------------
    # utility functions

    def _resolve_member_val(self, mval, field):
        if hasattr(mval, "__call__"):
            return  mval(field)
        else:
            return mval

    def _resolve_val(self, val):
        import pfp.fuzz.rand as rand

        if hasattr(val, "__call__"):
            return val()
        elif isinstance(val, dict) and "min" in val and "max" in val:
            return rand.randint(val["min"], val["max"])
        elif hasattr(val, "__iter__"):
            return rand.choice(val)
        else:
            return val
