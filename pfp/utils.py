#!/usr/bin/env python
# encoding: utf-8

import contextlib
import six
import sys
import time


@contextlib.contextmanager
def timeit(msg, num=None):
    """
    Yields a message at the start.

    Args:
        msg: (str): write your description
        num: (int): write your description
    """
    start = time.time()
    yield
    end = time.time()
    if num is None:
        print("{} took {:.04f}s".format(msg, end - start))
    else:
        print("{} with {:.04f}/s".format(msg, (num / (end - start))))


def is_str(s):
    """
    Returns true if s is a string.

    Args:
        s: (array): write your description
    """
    for type_ in six.string_types:
        if isinstance(s, type_):
            return True
    if isinstance(s, bytes):
        return True
    return False


# Useful for very coarse version differentiation.
PY3 = sys.version_info[0] == 3

if PY3:
    from queue import Queue

    def string_escape(s):
        """
        Escape s with special characters.

        Args:
            s: (todo): write your description
        """
        return bytes(string(s), "utf-8").decode("unicode_escape")

    def binary(s):
        """
        Convert s to binary.

        Args:
            s: (str): write your description
        """
        if type(s) is bytes:
            return s
        return s.encode("ISO-8859-1")

    def string(s):
        """
        Convert a string to bytes.

        Args:
            s: (str): write your description
        """
        if type(s) is bytes:
            return s.decode("ISO-8859-1")
        return s


else:
    from Queue import Queue

    def string_escape(s):
        """
        Escape given string with special characters.

        Args:
            s: (todo): write your description
        """
        return string(s).decode("string_escape")

    def binary(s):
        """
        Convert a binary string.

        Args:
            s: (int): write your description
        """
        return s

    def string(s):
        """
        Convert a string to a given string.

        Args:
            s: (int): write your description
        """
        return s
