#!/usr/bin/env python

"""
Errors for pfp
"""

class PrematureEOF(Exception): pass
# TODO

class PfpError(Exception):
	"""Base class for pfp exceptions"""
	def __init__(self, coord, *args):
		super(PfpError, self).__init__((self.msg + " at {}").format(*(args + (coord,))))

class InterpReturn(PfpError):
	def __init__(self, ret_val):
		self.value = ret_val

class InvalidArguments(PfpError):
	msg = "Invalid arguments, received {!r}, expected {!r}"

class InvalidState(PfpError):
	msg = "Pfp has reached an invalid state"

class UnsupportedASTNode(PfpError):
	msg = "Pfp can not yet interpret {!r} nodes"

class UnresolvedType(PfpError):
	"""These exceptions will be raised when a type cannot be resolved"""
	msg = "The type {!r} ({!r}) could not be resolved"

class UnsupportedConstantType(PfpError):
	"""These exceptions will be raised when a constant type is encountered
	that can not yet be handled (or not implemented yet)"""
	msg = "Unsupported constant type {!r}"

class UnresolvedID(PfpError):
	"""These exceptionsn will be raised when a referenced ID cannot
	be resolved"""
	msg = "Could not resolve field {!r}"

class UnsupportedUnaryOperator(PfpError):
	"""docstring for UnsupportedUnaryOperator"""
	msg = "Unsupported unary operator {!r}"

class UnsupportedBinaryOperator(PfpError):
	"""docstring for UnsupportedUnaryOperator"""
	msg = "Unsupported binary operator {!r}"
