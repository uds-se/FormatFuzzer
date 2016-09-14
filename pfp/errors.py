#!/usr/bin/env python

"""
Errors for pfp
"""

class PfpError(Exception): pass

class PrematureEOF(PfpError): pass

class InterpBreak(PfpError): pass
class InterpContinue(PfpError): pass
class InterpExit(PfpError):
    def __init__(self, error_code=0):
        self.error_code = error_code
class UnmodifiableConst(PfpError): pass

class CoordError(PfpError):
    """Base class for pfp exceptions"""
    def __init__(self, coord=None, *args):
        super(CoordError, self).__init__((self.msg + " at {}").format(*(args + (coord,))))

class InterpReturn(CoordError):
    def __init__(self, ret_val):
        self.value = ret_val

class InvalidArguments(CoordError):
    msg = "Invalid arguments, received {!r}, expected {!r}"

class InvalidState(CoordError):
    msg = "Pfp has reached an invalid state"

class UnsupportedASTNode(CoordError):
    msg = "Pfp can not yet interpret {!r} nodes"

class UnresolvedType(CoordError):
    """These exceptions will be raised when a type cannot be resolved"""
    msg = "The type {!r} ({!r}) could not be resolved"

class UnsupportedConstantType(CoordError):
    """These exceptions will be raised when a constant type is encountered
    that can not yet be handled (or not implemented yet)"""
    msg = "Unsupported constant type {!r}"

class UnresolvedID(CoordError):
    """These exceptionsn will be raised when a referenced ID cannot
    be resolved"""
    msg = "Could not resolve field {!r}"

class UnsupportedUnaryOperator(CoordError):
    """docstring for UnsupportedUnaryOperator"""
    msg = "Unsupported unary operator {!r}"

class UnsupportedBinaryOperator(CoordError):
    """docstring for UnsupportedUnaryOperator"""
    msg = "Unsupported binary operator {!r}"

class UnsupportedAssignmentOperator(CoordError):
    """docstring for UnsupportedAssignmentOperator"""
    msg = "Unsupported assignment operator {!r}"

