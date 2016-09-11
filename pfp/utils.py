#!/usr/bin/env python
# encoding: utf-8

import six
import sys
    
def is_str(s):
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
        return bytes(string(s), "utf-8").decode("unicode_escape")

    def binary(s):
        if type(s) is bytes:
            return s
        return s.encode("ISO-8859-1")
    
    def string(s):
        if type(s) is bytes:
            return s.decode("ISO-8859-1")
        return s
else:
    from Queue import Queue

    def string_escape(s):
        return string(s).decode("string_escape")

    def binary(s):
        return s
    
    def string(s):
        return s
