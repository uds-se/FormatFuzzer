#!/usr/bin/env python

"""
Errors for pfp
"""

class PrematureEOF(Exception): pass
# TODO

class UnsupportedASTNode(Exception): pass
# TODO

class UnresolvedType(Exception): pass
# TODO

class UnsupportedConstantType(Exception):
	"""These exceptions will be raised when a constant type is encountered
	that can not yet be handled (or not implemented yet)"""
	def __init__(self, constant_type, coord):
		super(UnsupportedConstantType, self).__init__("Unsupported constant type {!r} at {}".format(
			constant_type, coord
		))
		

class UnresolvedID(Exception):
	"""These exceptionsn will be raised when a referenced ID cannot
	be resolved"""

	def __init__(self, field_name, coord):
		super(UnresolvedID, self).__init__("Could not resolve field {!r} at {}".format(
			field_name, coord
		))
