#!/usr/bin/env python
# encoding: utf-8

import zlib
import six

from pfp.native import native
import pfp.fields
from pfp.dbg import PfpDbg
import pfp.utils as utils

@native(name="GZipper", ret=pfp.fields.Array)
def gzipper(params, ctxt, scope, stream, coord):
	"""params [pack (true/false), data]

	:pack: True if the data should be packed, false if it should be unpacked
	:data: The data to operate on
	:returns: 
	"""
	if len(params) <= 1:
		raise errors.InvalidArguments(coord, "{} args".format(len(params)), "at least two arguments")

	import pdb; pdb.set_trace()
	
	# to gzip it (pack it)
	if params[0]:
		return gzip_compress(params[1:], ctxt, scope, stream, coord)
	else:
		return gzip_decompress(params[1:], ctxt, scope, stream, coord)

@native(name="GZip", ret=pfp.fields.Array)
def gzip_compress(params, ctxt, scope, stream, coord):
	"""Concat the build output of all params and gzip the
	resulting data, returning a char array
	"""
	if len(params) == 0:
		raise errors.InvalidArguments(coord, "{} args".format(len(params)), "at least one argument")
	
	built = utils.binary("")
	for param in params:
		if isinstance(param, pfp.fields.Field):
			built += param._pfp__build()
		else:
			built += param
	
	return zlib.compress(built)

@native(name="GUnzip", ret=pfp.fields.Array)
def gzip_decompress(params, ctxt, scope, stream, coord):
	"""Concat the build output of all params and gunzip the
	resulting data, returning a char array
	"""
	if len(params) == 0:
		raise errors.InvalidArguments(coord, "{} args".format(len(params)), "at least one argument")
	
	built = utils.binary("")
	for param in params:
		if isinstance(param, pfp.fields.Field):
			built += param._pfp__build()
		else:
			built += param
	
	return zlib.decompress(built)
