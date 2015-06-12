#!/usr/bin/env python

"""
Python format parser
"""

import copy
import glob
import logging
import six
import sys
import os

import py010parser
import py010parser.c_parser
from py010parser import c_ast as AST

import pfp.fields as fields
import pfp.errors as errors
import pfp.functions as functions
import pfp.native as native
import pfp.utils as utils

logging.basicConfig(level=logging.CRITICAL)

class StructUnionDef(object):

	"""A class used to instantiate structs/unions as
	needed (used for typedefs)"""

	def __init__(self, interp, node):
		"""Save the interpreter and the node so that when
		this instance is called (will act like instantiation),
		the interpreter is just told to handle the node
		
		:interp: The interpreter
		:node: The node to interpret upon instantiation
		"""
		self._interp = interp
		self._node = node
	
	def __call__(self, stream):
		"""Create an instance of the struct/union

		:stream: The stream that data will be parsed from
		:returns: A struct or union instance
		"""
		# TODO stream should be optional to act like other fields classes
		res = self._interp._handle_node(self._node, stream=stream)
		return res

class DebugLogger(object):
	def __init__(self, active=False):
		self._log = logging.getLogger("")
		self._indent = 0
		self._active = active
		if self._active:
			self._log.setLevel(logging.DEBUG)
	
	def debug(self, prefix, msg, indent_change=0):
		if not self._active:
			return

		self._indent += indent_change
		self._log.debug("\n".join(prefix + ": " + "  "*self._indent + line for line in msg.split("\n")))
	
	def inc(self):
		self._indent += 1
	
	def dec(self):
		self._indent -= 1

class Scope(object):
	"""A class to keep track of the current scope of the interpreter"""
	def __init__(self, logger):
		super(Scope, self).__init__()

		self._log = logger

		self._scope_stack = []
		self.push()
	
	def level(self):
		"""Return the current scope level
		"""
		return len(self._scope_stack)
		
	def push(self):
		"""Create a new scope
		:returns: TODO

		"""
		self._curr_scope = {
			"types": {},
			"locals": {},
			"vars": {}
		}
		self._dlog("pushing new scope, scope level = {}".format(self.level()))
		self._scope_stack.append(self._curr_scope)
	
	def clone(self):
		"""Return a new Scope object that has the curr_scope
		pinned at the current one
		:returns: A new scope object
		"""
		self._dlog("cloning the stack")
		# TODO is this really necessary to create a brand new one?
		# I think it is... need to think about it more.
		# or... are we going to need ref counters and a global
		# scope object that allows a view into (or a snapshot of)
		# a specific scope stack?
		res = Scope(self._log)
		res._scope_stack = self._scope_stack
		res._curr_scope = self._curr_scope
		return res
	
	def pop(self):
		"""Leave the current scope
		:returns: TODO

		"""
		self._scope_stack.pop()
		self._dlog("popping scope, scope level = {}".format(self.level()))
		self._curr_scope = self._scope_stack[-1]
	
	def add_var(self, field_name, field):
		"""Add a var to the current scope (vars are fields that
		parse the input stream)

		:field_name: TODO
		:field: TODO
		:returns: TODO

		"""
		self._dlog("adding var '{}'".format(field_name))
		# TODO do we allow clobbering of vars???
		self._curr_scope["vars"][field_name] = field
	
	def get_var(self, name):
		"""Return the first var of name ``name`` in the current
		scope stack (remember, vars are the ones that parse the
		input stream)

		:name: The name of the id
		:returns: TODO

		"""
		self._dlog("getting var '{}'".format(name))
		return self._search("vars", name)
	
	def add_local(self, field_name, field):
		"""Add a local variable in the current scope

		:field_name: The field's name
		:field: The field
		:returns: None

		"""
		self._dlog("adding local '{}'".format(field_name))
		field._pfp__name = field_name
		# TODO do we allow clobbering of locals???
		self._curr_scope["locals"][field_name] = field
	
	def get_local(self, name):
		"""Get the local field (search for it) from the scope stack

		:name: The name of the local field
		"""
		self._dlog("getting local '{}'".format(name))
		return self._search("locals", name)
	
	def add_type_struct_or_union(self, name, node):
		"""Store the node with the name. When it is instantiated,
		the node itself will be handled.

		:name: name of the typedefd struct/union
		:node: the union/struct node
		"""
		self._curr_scope["types"][name] = node
	
	def add_type(self, new_name, orig_names):
		"""Record the typedefd name for orig_names. Resolve orig_names
		to their core names and save those.

		:new_name: TODO
		:orig_names: TODO
		:returns: TODO

		"""
		self._dlog("adding a type '{}'".format(new_name))
		# TODO do we allow clobbering of types???
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
		self._dlog("getting type '{}'".format(name))
		return self._search("types", name)
	
	def get_id(self, name):
		"""Get the first id matching ``name``. Will either be a local
		or a var. Locals will be search before vars.

		:name: TODO
		:returns: TODO

		"""
		self._dlog("getting id '{}'".format(name))
		local = self._search("locals", name)
		if local is not None:
			return local

		var = self._search("vars", name)
		return var
	
	# ------------------
	# PRIVATE
	# ------------------

	def _dlog(self, msg):
		self._log.debug(" scope", msg)

	def _resolve_name(self, name):
		"""TODO: Docstring for _resolve_names.

		:name: TODO
		:returns: TODO

		"""
		res = [name]
		while True:
			orig_names = self._search("types", name)
			if orig_names is not None:
				name = orig_names[-1]
				# pop off the typedefd name
				res.pop()
				# add back on the original names
				res += orig_names
			else:
				break

		return res
	
	def _search(self, category, name):
		"""Search the scope stack for the name in the specified
		category (types/locals/vars).

		:category: the category to search in (locals/types/vars)
		:name: name to search for
		:returns: None if not found, the result of the found local/type/id
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

	# do not break (execute until finished)
	BREAK_NONE = 0
	# break on the next instruction on the same level
	BREAK_OVER = 1
	# break on the next instruction regardless of level
	BREAK_INTO = 2

	_natives = {}

	@classmethod
	def add_native(cls, name, func, ret, interp=None, send_interp=False):
		if interp is None:
			natives = cls._natives
		else:
			# the instance's natives
			natives = interp._natives

		natives[name] = functions.NativeFunction(
			name, func, ret, send_interp
		)
	
	@classmethod
	def define_natives(cls):
		"""Define the native functions for PFP
		"""
		if len(cls._natives) > 0:
			return

		glob_pattern = os.path.join(os.path.dirname(__file__), "native", "*.py")
		for filename in glob.glob(glob_pattern):
			basename = os.path.basename(filename).replace(".py", "")
			if basename == "__init__":
				continue

			try:
				mod_base = __import__("pfp.native", globals(), locals(), fromlist=[basename])
			except Exception as e:
				sys.stderr.write("cannot import native module {} at '{}'".format(basename, filename))
				raise e
				continue

			mod = getattr(mod_base, basename)
			setattr(mod, "PYVAL", fields.get_value) 

	def __init__(self, debug=False, parser=None):
		"""
		"""
		self.__class__.define_natives()

		self._log = DebugLogger(debug)
		# TODO nested debuggers aren't currently allowed
		self._debugger = None
		self._debug = debug
		self._break_type = self.BREAK_NONE
		self._break_level = 0
		self._no_debug = False

		self._ctxt = None
		self._scope = None
		
		if parser is None:
			parser = py010parser.c_parser.CParser()
		# this speeds things up a bit
		self._parser = parser

		self._node_switch = {
			AST.FileAST:		self._handle_file_ast,
			AST.Decl:			self._handle_decl,
			AST.TypeDecl:		self._handle_type_decl,
			AST.Struct:			self._handle_struct,
			AST.Union:			self._handle_union,
			AST.StructRef:		self._handle_struct_ref,
			AST.IdentifierType:	self._handle_identifier_type,
			AST.Typedef:		self._handle_typedef,
			AST.Constant:		self._handle_constant,
			AST.BinaryOp:		self._handle_binary_op,
			AST.Assignment:		self._handle_assignment,
			AST.ID:				self._handle_id,
			AST.UnaryOp:		self._handle_unary_op,
			AST.FuncDef:		self._handle_func_def,
			AST.FuncCall:		self._handle_func_call,
			AST.FuncDecl:		self._handle_func_decl,
			AST.ParamList:		self._handle_param_list,
			AST.ExprList:		self._handle_expr_list,
			AST.Compound:		self._handle_compound,
			AST.Return:			self._handle_return,
			AST.ArrayDecl:		self._handle_array_decl
		}
	
	def _dlog(self, msg, indent_increase=0):
		"""log the message to the log"""
		self._log.debug("interp", msg, indent_increase)
	
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
		self._dlog("parsing")

		self._stream = stream
		self._template = template
		self._template_lines = self._template.split("\n")
		self._ast = py010parser.parse_string(template, parser=self._parser)
		self._dlog("parsed template into ast")

		res = self._run()
		return res
	
	def step_over(self):
		"""Perform one step of the interpreter
		"""
		self.set_break(self.BREAK_OVER)
	
	def step_into(self):
		"""Step over/into the next statement
		"""
		self.set_break(self.BREAK_INTO)
	
	def cont(self):
		"""Continue the interpreter
		"""
		self.set_break(self.BREAK_NONE)
	
	def eval(self, statement, ctxt=None):
		"""Eval a single statement (something returnable)
		"""
		self._no_debug = True

		statement = statement.strip()

		if not statement.endswith(";"):
			statement += ";"

		ast = py010parser.parse_string(statement, parser=self._parser)

		#if "=" in statement:
			#if not statement.endswith(";"):
				#statement += ";"
		#else:
			#if statement.endswith(";"):
				#statement = statement[:-1]
			#statement = "( " + statement + " )"
			#if not statement.endswith(";"):
				#statement += ";"
			#statement = "return " + statement
		self._dlog("evaluating statement: {}".format(statement))
		
		try:
			if len(ast.children()) == 1:
				res = self._handle_node(ast.children()[0], self._scope, self._ctxt, self._stream)
				return res
			else:
				# explicitly iterate over each of the children so that
				# _handle_file_ast isn't called
				for child in ast.children():
					self._handle_node(child, self._scope, self._ctxt, self._stream)
		except errors.InterpReturn as e:
			return e.value
		finally:
			self._no_debug = False
	
	def set_break(self, break_type):
		"""Set if the interpreter should break.

		:returns: TODO
		"""
		self._break_type = break_type
		self._break_level = self._scope.level()
	
	def get_curr_lines(self):
		"""Return the current line number in the template,
		as well as the surrounding source lines
		"""
		start = max(0, self._coord.line - 5)
		end = min(len(self._template_lines), self._coord.line + 4)

		lines = [(x, self._template_lines[x]) for x in range(start, end, 1)]
		return self._coord.line, lines
	
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

		self._dlog("interpreting template")

		# it is important to pass the stream in as the stream
		# may change (e.g. compressed data)
		res = self._handle_node(self._ast, None, None, self._stream)

		# final drop-in after everything has executed
		if self._break_type != self.BREAK_NONE:
			self.debugger.cmdloop("execution finished")

		return res

	def _handle_node(self, node, scope=None, ctxt=None, stream=None):
		"""Recursively handle nodes in the 010 AST

		:node: TODO
		:scope: TODO
		:ctxt: TODO
		:stream: TODO
		:returns: TODO
		"""
		if scope is None:
			if self._scope is None:
				self._scope = scope = self._create_scope()
			else:
				scope = self._scope

		if ctxt is None and self._ctxt is not None:
			ctxt = self._ctxt
		else:
			self._ctxt = ctxt

		if type(node) is tuple:
			node = node[1]

		# need to check this so that debugger-eval'd statements
		# don't mess with the current state
		if not self._no_debug:
			self._coord = node.coord

		self._dlog("handling node type {}, line {}".format(node.__class__.__name__, node.coord.line if node.coord is not None else "?"))
		self._log.inc()

		breakable = self._node_is_breakable(node)

		if breakable and not self._no_debug and self._break_type != self.BREAK_NONE:
			# always break
			if self._break_type == self.BREAK_INTO:
				self._break_level = self._scope.level()
				self.debugger.cmdloop()

			# level <= _break_level
			elif self._break_type == self.BREAK_OVER:
				if self._scope.level() <= self._break_level:
					self._break_level = self._scope.level()
					self.debugger.cmdloop()
				else:
					pass

		if node.__class__ not in self._node_switch:
			raise errors.UnsupportedASTNode(node.coord, node.__class__.__name__)

		res = self._node_switch[node.__class__](node, scope, ctxt, stream)

		self._log.dec()

		return res
	
	def _handle_file_ast(self, node, scope, ctxt, stream):
		"""TODO: Docstring for _handle_file_ast.

		:node: TODO
		:scope: TODO
		:ctxt: TODO
		:stream: TODO
		:returns: TODO

		"""
		self._root = ctxt = fields.Dom("__root")
		self._dlog("handling file AST with {} children".format(len(node.children())))

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
		self._dlog("handling decl")
		field = self._handle_node(node.type, scope, ctxt, stream)
		
		# locals still get a field instance, but DON'T parse the
		# stream!
		if "local" in node.quals:
			field = field()
			scope.add_local(node.name, field)

			# this should only be able to be done with locals, right?
			# if not, move it to the bottom of the function
			if node.init is not None:
				val = self._handle_node(node.init, scope, ctxt, stream)
				field._pfp__set_value(val)

		elif isinstance(field, functions.Function):
			# eh, just add it as a local...
			# maybe the whole local/vars thinking needs to change...
			# and we should only have ONE map TODO
			field.name = node.name
			scope.add_local(node.name, field)

		elif getattr(node, "is_func_param", False):
			# we want to keep this as a class and not instantiate it
			# instantiation will be done in functions.ParamListDef.instantiate
			field = (node.name, field)

		else:
			# by this point, structs are already instantiated (they need to be
			# in order to set the new context)
			if not isinstance(field, fields.Field):
				field = field(stream)
			scope.add_var(node.name, field)
			ctxt._pfp__add_child(node.name, field)

		return field
	
	def _handle_type_decl(self, node, scope, ctxt, stream):
		"""TODO: Docstring for _handle_type_decl.

		:node: TODO
		:scope: TODO
		:ctxt: TODO
		:stream: TODO
		:returns: TODO

		"""
		self._dlog("handling type decl")
		decl = self._handle_node(node.type, scope, ctxt, stream)
		return decl
	
	def _handle_struct_ref(self, node, scope, ctxt, stream):
		"""TODO: Docstring for _handle_struct_ref.

		:node: TODO
		:scope: TODO
		:ctxt: TODO
		:stream: TODO
		:returns: TODO

		"""
		self._dlog("handling struct ref")

		# name
		# field
		struct = self._handle_node(node.name, scope, ctxt, stream)
		sub_field = getattr(struct, node.field.name)

		return sub_field
	
	def _handle_union(self, node, scope, ctxt, stream):
		"""TODO: Docstring for _handle_union.

		:node: TODO
		:scope: TODO
		:ctxt: TODO
		:stream: TODO
		:returns: TODO

		"""
		self._dlog("handling union")
		union = fields.Union()

		scope.push()

		max_pos = 0
		for decl in node.decls:
			start_pos = stream.tell()
			# new context! (union)
			self._handle_node(decl, scope, union, stream)
			end_pos = stream.tell()
			if end_pos > max_pos:
				max_pos = end_pos
			stream.seek(start_pos, 0)
		stream.seek(max_pos, 0)

		scope.pop()

		return union
	
	def _handle_struct(self, node, scope, ctxt, stream):
		"""TODO: Docstring for _handle_struct.

		:node: TODO
		:scope: TODO
		:ctxt: TODO
		:stream: TODO
		:returns: TODO

		"""
		self._dlog("handling struct")
		struct = fields.Struct()

		# new scope
		scope.push()

		for decl in node.decls:
			# new context! (struct)
			self._handle_node(decl, scope, struct, stream)

		# need to pop the scope!
		scope.pop()

		return struct
	
	def _handle_identifier_type(self, node, scope, ctxt, stream):
		"""TODO: Docstring for _handle_identifier_type.

		:node: TODO
		:scope: TODO
		:ctxt: TODO
		:stream: TODO
		:returns: TODO

		"""
		self._dlog("handling identifier")
		cls = self._resolve_to_field_class(node.names, scope, ctxt)
		return cls
	
	def _handle_typedef(self, node, scope, ctxt, stream):
		"""TODO: Docstring for _handle_typedef.

		:node: TODO
		:scope: TODO
		:ctxt: TODO
		:stream: TODO
		:returns: TODO

		"""
		is_union_or_struct = (node.type.type.__class__ in [AST.Union, AST.Struct])

		if is_union_or_struct:
			scope.add_type_struct_or_union(node.name, node.type.type)
		else:
			names = node.type.type.names

			self._dlog("handling typedef '{}' ({})".format(node.name, names))
			# don't actually handle the TypeDecl and Identifier nodes,
			# just directly add the types. Example structure:
			#
			#	 Typedef: BLAH, [], ['typedef']
			#		TypeDecl: BLAH, []
			#			IdentifierType: ['unsigned', 'char']
			#	
			scope.add_type(node.name, names)
	
	def _handle_constant(self, node, scope, ctxt, sream):
		"""TODO: Docstring for _handle_constant.

		:node: TODO
		:scope: TODO
		:ctxt: TODO
		:stream: TODO
		:returns: TODO

		"""
		self._dlog("handling constant type {}".format(node.type))
		switch = {
			"int": (lambda x: int(str(x).replace("l", "")), fields.Int),
			"long": (lambda x: int(str(x).replace("l", "")), fields.Int),
			# TODO this isn't quite right, but py010parser wouldn't have
			# parsed it if it wasn't correct...
			"float": (lambda x: float(x.replace("f", "")), fields.Float),
			"double": (float, fields.Double),

			# cut out the quotes
			"char": (lambda x: ord(x[1:-1]), fields.Char),

			# TODO should this be unicode?? will probably bite me later...
			# cut out the quotes
			"string": (lambda x: str(x[1:-1]), fields.String)
		}

		if node.type in switch:
			#return switch[node.type](node.value)
			conversion,field_cls = switch[node.type]
			field = field_cls()
			field._pfp__set_value(conversion(node.value))
			return field

		raise UnsupportedConstantType(node.coord, node.type)
	
	def _handle_binary_op(self, node, scope, ctxt, stream):
		"""TODO: Docstring for _handle_binary_op.

		:node: TODO
		:scope: TODO
		:ctxt: TODO
		:stream: TODO
		:returns: TODO

		"""
		self._dlog("handling binary operation {}".format(node.op))
		switch = {
			"+": lambda x,y: x+y,
			"-": lambda x,y: x-y,
			"*": lambda x,y: x*y,
			"/": lambda x,y: x/y,
			"|": lambda x,y: x|y,
			"^": lambda x,y: x^y,
			"&": lambda x,y: x&y,
			"%": lambda x,y: x%y,
			">": lambda x,y: x>y,
			"<": lambda x,y: x<y,
			">=": lambda x,y: x>=y,
			"<=": lambda x,y: x<=y,
			"==": lambda x,y: x == y,
			"!=": lambda x,y: x != y
		}

		left_val = self._handle_node(node.left, scope, ctxt, stream)
		right_val = self._handle_node(node.right, scope, ctxt, stream)

		if node.op not in switch:
			raise errors.UnsupportedBinaryOperator(node.coord, node.op)

		return switch[node.op](left_val, right_val)
	
	def _handle_unary_op(self, node, scope, ctxt, stream):
		"""TODO: Docstring for _handle_unary_op.

		:node: TODO
		:scope: TODO
		:ctxt: TODO
		:stream: TODO
		:returns: TODO

		"""
		self._dlog("handling unary op {}".format(node.op))
		switch = {
			"p++": lambda x,v: x.__iadd__(1),
			"p--": lambda x,v: x.__isub__(1),
			"~":   lambda x,v: ~x,
			"!":   lambda x,v: not x
		}

		if node.op not in switch:
			raise errors.UnsupportedUnaryOperator(node.coord, node.op)

		field = self._handle_node(node.expr, scope, ctxt, stream)
		switch[node.op](field, 1)
	
	def _handle_id(self, node, scope, ctxt, stream):
		"""Handle an ID node (return a field object for the ID)

		:node: TODO
		:scope: TODO
		:ctxt: TODO
		:stream: TODO
		:returns: TODO

		"""
		if node.name == "__root":
			return self._root
		if node.name == "__this":
			return ctxt

		self._dlog("handling id {}".format(node.name))
		field = scope.get_id(node.name)

		if field is None:
			raise errors.UnresolvedID(node.coord, node.name)

		return field
	
	def _handle_assignment(self, node, scope, ctxt, stream):
		"""Handle assignment nodes

		:node: TODO
		:scope: TODO
		:ctxt: TODO
		:stream: TODO
		:returns: TODO

		"""
		self._dlog("handling assignment")
		field = self._handle_node(node.lvalue, scope, ctxt, stream)
		self._dlog("field = {}".format(field))
		value = self._handle_node(node.rvalue, scope, ctxt, stream)
		self._dlog("value = {}".format(value))
		field._pfp__set_value(value)
	
	def _handle_func_def(self, node, scope, ctxt, stream):
		"""Handle FuncDef nodes

		:node: TODO
		:scope: TODO
		:ctxt: TODO
		:stream: TODO
		:returns: TODO

		"""
		self._dlog("handling function definition")
		func = self._handle_node(node.decl, scope, ctxt, stream)
		func.body = node.body
	
	def _handle_param_list(self, node, scope, ctxt, stream):
		"""Handle ParamList nodes

		:node: TODO
		:scope: TODO
		:ctxt: TODO
		:stream: TODO
		:returns: TODO

		"""
		self._dlog("handling param list")
		# params should be a list of tuples:
		# [(<name>, <field_class>), ...]
		params = []
		for param in node.params:
			param = self._handle_node(param, scope, ctxt, stream)
			params.append(param)

		param_list = functions.ParamListDef(params, node.coord)
		return param_list
	
	def _handle_func_decl(self, node, scope, ctxt, stream):
		"""Handle FuncDecl nodes

		:node: TODO
		:scope: TODO
		:ctxt: TODO
		:stream: TODO
		:returns: TODO

		"""
		self._dlog("handling func decl")

		if node.args is not None:
			# could just call _handle_param_list directly...
			for param in node.args.params:
				# see the check in _handle_decl for how this is kept from
				# being added to the local context/scope
				param.is_func_param = True
			params = self._handle_node(node.args, scope, ctxt, stream)
		else:
			params = functions.ParamListDef([], node.coord)

		func_type = self._handle_node(node.type, scope, ctxt, stream)

		func = functions.Function(func_type, params, scope)

		return func

	def _handle_func_call(self, node, scope, ctxt, stream):
		"""Handle FuncCall nodes

		:node: TODO
		:scope: TODO
		:ctxt: TODO
		:stream: TODO
		:returns: TODO

		"""
		self._dlog("handling function call to '{}'".format(node.name.name))
		if node.args is None:
			func_args = []
		else:
			func_args = self._handle_node(node.args, scope, ctxt, stream)
		func = self._handle_node(node.name, scope, ctxt, stream)
		return func.call(func_args, ctxt, scope, stream, self, node.coord)
	
	def _handle_expr_list(self, node, scope, ctxt, stream):
		"""Handle ExprList nodes

		:node: TODO
		:scope: TODO
		:ctxt: TODO
		:stream: TODO
		:returns: TODO

		"""
		self._dlog("handling expression list")
		exprs = [
			self._handle_node(expr, scope, ctxt, stream) for expr in node.exprs
		]
		return exprs
	
	def _handle_compound(self, node, scope, ctxt, stream):
		"""Handle Compound nodes

		:node: TODO
		:scope: TODO
		:ctxt: TODO
		:stream: TODO
		:returns: TODO

		"""
		self._dlog("handling compound statement")
		scope.push()

		try:
			for child in node.children():
				self._handle_node(child, scope, ctxt, stream)

		# in case a return occurs, be sure to pop the scope
		# (returns are implemented by raising an exception)
		finally:
			scope.pop()
	
	def _handle_return(self, node, scope, ctxt, stream):
		"""Handle Return nodes

		:node: TODO
		:scope: TODO
		:ctxt: TODO
		:stream: TODO
		:returns: TODO

		"""
		self._dlog("handling return")
		ret_val = self._handle_node(node.expr, scope, ctxt, stream)
		self._dlog("return value = {}".format(ret_val))
		raise errors.InterpReturn(ret_val)
	
	def _handle_array_decl(self, node, scope, ctxt, stream):
		"""Handle ArrayDecl nodes

		:node: TODO
		:scope: TODO
		:ctxt: TODO
		:stream: TODO
		:returns: TODO

		"""
		self._dlog("handling array declaration '{}'".format(node.type.declname))
		array_size = self._handle_node(node.dim, scope, ctxt, stream)
		self._dlog("array size = {}".format(array_size))
		# TODO node.dim_quals
		# node.type
		field_cls = self._handle_node(node.type, scope, ctxt, stream)
		self._dlog("field class = {}".format(field_cls))
		array = fields.Array(array_size, field_cls)
		array._pfp__name = node.type.declname
		array._pfp__parse(stream)
		return array
	
	# -----------------------------
	# UTILITY
	# -----------------------------

	def _node_is_breakable(self, node):
		breakable_classes = [
			AST.FileAST,
			AST.Decl,
			#AST.TypeDecl,
			#AST.Struct,
			#AST.IdentifierType,
			AST.Typedef,
			#AST.Constant,
			AST.BinaryOp,
			AST.Assignment,
			#AST.ID,
			AST.UnaryOp,
			#AST.FuncDef,
			AST.FuncCall,
			#AST.FuncDecl,
			#AST.ParamList,
			AST.ExprList,
			#AST.Compound,
			AST.Return,
			AST.ArrayDecl,
		]

		return node.__class__ in breakable_classes
	
	def _create_scope(self):
		"""TODO: Docstring for _create_scope.
		:returns: TODO

		"""
		res = Scope(self._log)

		for func_name,native_func in six.iteritems(self._natives):
			res.add_local(func_name, native_func)

		return res

	def _get_value(self, node, scope, ctxt, stream):
		"""Return the value of the node. It is expected to be
		either an AST.ID instance or a constant

		:node: TODO
		:returns: TODO

		"""

		res = self._handle_node(node, scope, ctxt, stream)

		if isinstance(res, fields.Field):
			return res._pfp__value

		# assume it's a constant
		else:
			return res
	
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
			"uint64":	"UInt64",
			"short":	"Short",
			"double":	"Double",
			"float":	"Float",
			"void":		"Void",
			"string":	"String",
			"wstring":	"WString"
		}

		core = names[-1]
		
		if core not in switch:
			# will return a list of resolved names
			type_info = scope.get_type(core)
			if isinstance(type_info, AST.Node):
				return StructUnionDef(self, type_info)
			resolved_names = type_info
			if resolved_names is None:
				raise errors.UnresolvedType(self._coord, " ".join(names), " ")
			if resolved_names[-1] not in switch:
				raise errors.UnresolvedType(self._coord, " ".join(names), " ".join(resolved_names))
			names = copy.copy(names)
			names.pop()
			names += resolved_names

		res = switch[names[-1]]

		if names[-1] in ["char", "short", "int", "long"] and "unsigned" in names[:-1]:
			res = "U" + res

		cls = getattr(fields, res)
		return cls
