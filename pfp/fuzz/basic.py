#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module defines basic mutation strategies
"""


import six


import pfp.fuzz as fuzz
import pfp.fields as fields


class BasicStrat(fuzz.StratGroup):
    """A basic strategy that has FieldStrats (field strategies) defined
    for every field type. Nothing fancy, just basic.
    """

    name = "basic"

    class Char(fuzz.FieldStrat):
        klass = fields.Char
        choices = six.moves.range(0x100)

    class UChar(fuzz.FieldStrat):
        klass = fields.UChar
        choices = six.moves.range(-0x7f, 0x7f)

    class Ints(fuzz.FieldStrat):
        klass = [fields.Short, fields.Int, fields.Int64]

        def prob(self, field):
            # generate the probabilities table
            offset = 0

            max_val = (1 << (field.width*8))

            if field.signed:
                min_val = -max_val/2
                max_val = max_val/2 -1
                vals = [min_val, max_val, 0]
                vals += [1 << (x*8) for x in six.moves.range(field.width)]
                vals += [-x for x in vals]
                vals = sorted(set(vals))
                vals = vals[:-1]

            else:
                min_val = 0
                max_val -= 1
                vals = [0]
                vals += [1 << (x*4) for x in six.moves.range(field.width*2)]
                vals.append((1 << (field.width*8)) - 1)

            # now add the +-1 values
            new_vals = []
            for val in vals[2:-1]:
                new_vals.append(val-1)
                new_vals.append(val+1)
            vals += new_vals

            pv = 1.0 / 3.0
            res = [
                (pv, vals),
                (pv, six.moves.range(0, 0x100)),
                (pv, {"min": min_val, "max": max_val}),
            ]

            return res

    class Float(fuzz.FieldStrat):
        klass = fields.Float
        prob = [
            (1.0, lambda: fuzz.rand.randfloat(-0x10000000, 0x10000000))
        ]

    class Double(fuzz.FieldStrat):
        klass = fields.Double
        prob = [
            (1.0, lambda: fuzz.rand.randfloat(-0x10000000, 0x10000000))
        ]

    class Enum(Ints):
        klass = fields.Enum

        def prob(self, field):
            # treat it the same as ints, with the addition of the actual (valid)
            # enum values
            res = super(Enum, self).prob(field)

            # add in the new enum values
            prob_percent = 1.0 / float(len(res)+1)
            res = [(prob_percent, x[1]) for x in res]
            res.append(field.enum_vals.keys())

            return res

    class Array(fuzz.FieldStrat):
        klass = fields.Array

        # set the raw data to be a random string
        def next_val(self, field):
            rand_data_size = fuzz.rand.randint(0, 0x100) * field.field_cls.width
            return fuzz.rand.data(rand_data_size, [chr(x) for x in six.moves.range(0x100)])

    class String(fuzz.FieldStrat):
        klass = fields.String

        def next_val(self, field):
            rand_data_size = fuzz.rand.randint(0, 0x100)
            res = fuzz.rand.data(rand_data_size, [chr(x) for x in six.moves.range(0x100)])

            if fuzz.rand.maybe():
                res += "\x00"

            return res
