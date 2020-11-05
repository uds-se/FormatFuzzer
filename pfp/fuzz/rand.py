#!/usr/bin/env python
# encoding: utf-8

import random as r
import six

RANDOM = r.Random()
_randint = RANDOM.randint
random = _random = RANDOM.random
choice = _choice = RANDOM.choice
sample = _sample = RANDOM.sample


def seed(val):
    """
    Sets the val to val

    Args:
        val: (int): write your description
    """
    RANDOM.seed(val)


def randint(a, b=None):
    """
    Return a random integer.

    Args:
        a: (array): write your description
        b: (array): write your description
    """
    if b is None:
        return _randint(0, a)
    else:
        return _randint(a, b)


def randfloat(min_, max_):
    """
    Generate a random number.

    Args:
        min_: (float): write your description
        max_: (int): write your description
    """
    diff = max_ - min_
    res = _random()
    res *= diff
    res += min_
    return res


def maybe(prob=0.5):
    """
    Return a random integer.

    Args:
        prob: (todo): write your description
    """
    return _random() < prob


def data(length, charset):
    """
    Returns a string of the given length.

    Args:
        length: (int): write your description
        charset: (str): write your description
    """
    return b"".join(_choice(charset) for x in six.moves.range(length))
