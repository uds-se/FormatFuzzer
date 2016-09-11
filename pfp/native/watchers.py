#!/usr/bin/env python
# encoding: utf-8

import binascii
import zlib
import six

from pfp.native import native
import pfp.fields
from pfp.dbg import PfpDbg
import pfp.utils as utils
import pfp.errors as errors

@native(name="WatchLength", ret=pfp.fields.Void)
def watch_length(params, ctxt, scope, stream, coord):
    """WatchLength - Watch the total length of each of the params.
    
    Example:
        The code below uses the ``WatchLength`` update function to update
        the ``length`` field to the length of the ``data`` field ::

            int length<watch=data, update=WatchLength>;
            char data[length];
    """
    if len(params) <= 1:
        raise errors.InvalidArguments(coord, "{} args".format(len(params)), "at least two arguments")
    
    to_update = params[0]

    total_size = 0
    for param in params[1:]:
        total_size += param._pfp__width()
    
    to_update._pfp__set_value(total_size)

@native(name="WatchCrc32", ret=pfp.fields.Void)
def watch_crc(params, ctxt, scope, stream, coord):
    """WatchCrc32 - Watch the total crc32 of the params.
    
    Example:
        The code below uses the ``WatchCrc32`` update function to update
        the ``crc`` field to the crc of the ``length`` and ``data`` fields ::

            char length;
            char data[length];
            int crc<watch=length;data, update=WatchCrc32>;
    """
    if len(params) <= 1:
        raise errors.InvalidArguments(coord, "{} args".format(len(params)), "at least two arguments")
    
    to_update = params[0]

    total_data = utils.binary("")
    for param in params[1:]:
        total_data += param._pfp__build()
    
    to_update._pfp__set_value(binascii.crc32(total_data))
