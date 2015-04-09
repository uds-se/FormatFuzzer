#!/usr/bin/env python

"""
Python format parser
"""

import sys
import os

import py010parser
from py010parser import c_ast as AST

class Scope(object):
	"""A class to keep track of the current scope of the interpreter"""
	def __init__(self):
		super(Scope, self).__init__()

		self._curr_scope = {}
		self._scope_stack = [self._curr_scope]
		
	def push(self):
		"""Create a new scope
		:returns: TODO

		"""
		self._curr_scope = {}
		self._scope_stack.append(self._curr_scope)
	
	def pop(self):
		"""Leave the current scope
		:returns: TODO

		"""
		self._scope_stack.pop()
		self._curr_scope = self._scope_stack[-1]
	
	# def __getattr__
	# def __setattr__

class PfpInterp(object):
	"""
	"""

	def __init__(self):
		"""
		"""
		pass
	
	# --------------------
	# PUBLIC
	# --------------------

	def parse(self, stream, template):
		"""Parse the data stream using the template (e.g. parse the 010 template
		and interpret the template using the stream as the data source).

		:stream: The input data stream
		:template: The template to parse the stream with
		:returns: Pfp Dom

		"""
		self._stream = stream
		self._template = template
		self._ast = py010parser.parse_string(template)

		self._run()
	
	# --------------------
	# PRIVATE
	# --------------------
	
	def _run(self):
		"""Interpret the parsed 010 AST
		:returns: PfpDom

		"""

		# example self._ast.show():
		#	FileAST:
		#	  Decl: data, [], [], []
		#		TypeDecl: data, []
		#		  Struct: DATA
		#			Decl: a, [], [], []
		#			  TypeDecl: a, []
		#				IdentifierType: ['char']
		#			Decl: b, [], [], []
		#			  TypeDecl: b, []
		#				IdentifierType: ['char']
		#			Decl: c, [], [], []
		#			  TypeDecl: c, []
		#				IdentifierType: ['char']
		#			Decl: d, [], [], []
		#			  TypeDecl: d, []
		#				IdentifierType: ['char']

		self._handle_node(self._ast)

	def _handle_node(self, node, scope=None):
		"""Recursively handle nodes in the 010 AST

		:node: TODO
		:returns: TODO

		"""
		if scope is None:
			scope = Scope()

		import pdb ; pdb.set_trace()
		switch = {
			AST.FileAST: self._handle_file_ast,
			AST.Decl: self._handle_decl,
			AST.TypeDecl: self._handle_type_decl,
			AST.Struct: self._handle_struct,
			AST.IdentifierType: self._handle_identifier_type
		}

		if node.__class__ not in switch:
			raise NotImplemented("Pfp can not yet interpret {} nodes".format(node.__class__.__name__))

		return switch[node.__class__](node, scope)
	
	def _handle_file_ast(self, node, scope):
		"""TODO: Docstring for _handle_file_ast.

		:node: TODO
		:returns: TODO

		"""
		for child in node.children():
			self._handle_node(child, scope)
	
	def _handle_decl(self, node):
		"""TODO: Docstring for _handle_decl.

		:node: TODO
		:returns: TODO

		"""
		pass
	
	def _handle_type_decl(self, node):
		"""TODO: Docstring for _handle_type_decl.

		:node: TODO
		:returns: TODO

		"""
		pass
	
	def _handle_struct(self, node):
		"""TODO: Docstring for _handle_struct.

		:node: TODO
		:returns: TODO

		"""
		pass
	
	def _handle_identifier_type(self, node):
		"""TODO: Docstring for _handle_identifier_type.

		:node: TODO
		:returns: TODO

		"""
		pass
