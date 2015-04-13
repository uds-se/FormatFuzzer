#!/usr/bin/env python

"""
Python format parser
"""

import sys
import os

import py010parser
from py010parser import c_ast as AST

from . import fields
from . import errors

class Scope(object):
	"""A class to keep track of the current scope of the interpreter"""
	def __init__(self):
		super(Scope, self).__init__()

		self._scope_stack = []
		self.push()
		
	def push(self):
		"""Create a new scope
		:returns: TODO

		"""
		self._curr_scope = {
			"types": {},
			"locals": {}
		}
		self._scope_stack.append(self._curr_scope)
	
	def pop(self):
		"""Leave the current scope
		:returns: TODO

		"""
		self._scope_stack.pop()
		self._curr_scope = self._scope_stack[-1]
	
	def add_type(self, new_name, orig_names):
		"""Record the typedefd name for orig_names. Resolve orig_names
		to their core names and save those.

		:new_name: TODO
		:orig_names: TODO
		:returns: TODO

		"""
		res = copy.copy(orig_names)
		resolved_names = self._resolve_name(res[-1])
		if resolved_names is not None:
			res.pop()
			res += resolved_names

		self._curr_scope["types"][new_name] = res
	
	def get_type(self, name):
		"""Get the names for the typename (created by typedef)

		:name: The typedef'd name to resolve
		:returns: An array of resolved names associated with the typedef'd name

		"""
		return self._search("types", name)
	
	# ------------------
	# PRIVATE
	# ------------------

	def _resolve_name(self, name):
		"""TODO: Docstring for _resolve_names.

		:names: TODO
		:returns: TODO

		"""
		res = [name]
		while True:
			orig_names = self._search("types", name)
			if orig_names is not None:
				# pop off the typedefd name
				res.pop()
				# add back on the original names
				res += orig_names

		return res
	
	def _search(self, category, name):
		"""Search the scope stack for the name in the specified
		category (types/locals).

		:category: the category to search in (locals/types)
		:name: name to search for
		:returns: None if not found, the result of the found local/type
		"""
		idx = len(self._scope_stack) - 1
		curr = self._curr_scope
		for scope in reversed(self._scope_stack):
			res = scope[category].get(name, None)
			if res is not None:
				return res

		return None
	
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

		return self._run()
	
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

		print(self._ast.show())

		# it is important to pass the stream in as the stream
		# may change (e.g. compressed data)
		return self._handle_node(self._ast, None, None, self._stream)

	def _handle_node(self, node, scope, ctxt, stream):
		"""Recursively handle nodes in the 010 AST

		:node: TODO
		:scope: TODO
		:ctxt: TODO
		:stream: TODO
		:returns: TODO

		"""
		if scope is None:
			scope = Scope()

		switch = {
			AST.FileAST:		self._handle_file_ast,
			AST.Decl:			self._handle_decl,
			AST.TypeDecl:		self._handle_type_decl,
			AST.Struct:			self._handle_struct,
			AST.IdentifierType:	self._handle_identifier_type,
			AST.Typedef:		self._handle_typedef
		}

		if type(node) is tuple:
			node = node[1]

		if node.__class__ not in switch:
			raise errors.UnsupportedASTNode("Pfp can not yet interpret {} nodes".format(node.__class__.__name__))

		return switch[node.__class__](node, scope, ctxt, stream)
	
	def _handle_file_ast(self, node, scope, ctxt, stream):
		"""TODO: Docstring for _handle_file_ast.

		:node: TODO
		:scope: TODO
		:ctxt: TODO
		:stream: TODO
		:returns: TODO

		"""
		ctxt = fields.Dom()

		for child in node.children():
			self._handle_node(child, scope, ctxt, stream)

		return ctxt
	
	def _handle_decl(self, node, scope, ctxt, stream):
		"""TODO: Docstring for _handle_decl.

		:node: TODO
		:scope: TODO
		:ctxt: TODO
		:stream: TODO
		:returns: TODO

		"""
		field = self._handle_node(node.type, scope, ctxt, stream)
		ctxt._pfp__add_child(field, node.name)
	
	def _handle_type_decl(self, node, scope, ctxt, stream):
		"""TODO: Docstring for _handle_type_decl.

		:node: TODO
		:scope: TODO
		:ctxt: TODO
		:stream: TODO
		:returns: TODO

		"""
		decl = self._handle_node(node.type, scope, ctxt, stream)
		return decl
	
	def _handle_struct(self, node, scope, ctxt, stream):
		"""TODO: Docstring for _handle_struct.

		:node: TODO
		:scope: TODO
		:ctxt: TODO
		:stream: TODO
		:returns: TODO

		"""
		import pdb ; pdb.set_trace()
		struct = fields.Struct()

		scope.push()

		for decl in node.decls:
			# new context! (struct)
			self._handle_node(decl, scope, struct, stream)

		return struct
	
	def _handle_identifier_type(self, node, scope, ctxt, stream):
		"""TODO: Docstring for _handle_identifier_type.

		:node: TODO
		:scope: TODO
		:ctxt: TODO
		:stream: TODO
		:returns: TODO

		"""
		import pdb ; pdb.set_trace()
		cls = self._resolve_to_field_class(node.names, scope, ctxt)
		return cls(stream)
	
	def _handle_typedef(self, node, scope, ctxt, stream):
		"""TODO: Docstring for _handle_typedef.

		:node: TODO
		:scope: TODO
		:ctxt: TODO
		:stream: TODO
		:returns: TODO

		"""
		pass
	
	# -----------------------------
	# UTILITY
	# -----------------------------
	
	def _resolve_to_field_class(self, names, scope, ctxt):
		"""Resolve the names to a class in fields.py, resolving past
		typedefs, etc

		:names: TODO
		:scope: TODO
		:ctxt: TODO
		:returns: TODO

		"""
		switch = {
			"char":		"Char",
			"int":		"Int",
			"long": 	"Int",
			#"double":	fields.Double,
			#"float":	fields.Float
		}

		core = names[-1]
		
		if core not in switch:
			# will return a list of resolved names
			cores = scope.get_type(core)
			if cores[-1] not in switch:
				raise UnresolvedType(
					"The type {!r} ({!r}) could not be resolved".format(
						" ".join(names),
						" ".join(defined_type)
					)
				)
			names = copy.copy(names)
			names.pop()
			names += cores

		res = switch[names[-1]]

		if names[-1] in ["char", "int", "long"] and "unsigned" in names[:-1]:
			res = "U" + res

		cls = getattr(fields, res)
		return cls
