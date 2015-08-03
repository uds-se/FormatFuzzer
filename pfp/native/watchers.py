#!/usr/bin/env python
# encoding: utf-8

import binascii
import zlib
import six

from pfp.native import native
import pfp.fields
from pfp.dbg import PfpDbg
import pfp.utils as utils

@native(name="WatchLength", ret=pfp.fields.Void)
def watch_length(params, ctxt, scope, stream, coord):
	"""Watch the total length of each of the params
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
	"""Watch the crc32 of each of the params
	"""
	if len(params) <= 1:
		raise errors.InvalidArguments(coord, "{} args".format(len(params)), "at least two arguments")
	
	to_update = params[0]
	import pdb; pdb.set_trace()

	total_data = utils.binary("")
	for param in params[1:]:
		total_data += param._pfp__build()
	
	to_update._pfp__set_value(binascii.crc32(total_data))
