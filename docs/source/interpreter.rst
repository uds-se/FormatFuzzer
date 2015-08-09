
Interpreter
===========

The Pfp interpreter is quite simple: it uses ``py010parser`` to parse
the template into an abstract-syntax-tree, and then handles each of
the nodes in the tree appropriately.

The main method for handling nodes is the ``_handle_node`` function.
The ``_handle_node`` function performs basic housekeeping, logging,
decides if the user should be dropped into the interactive debugger,
and of course, handles the node itself.

If a methods are not implemented to handle a certain AST node, an
``pfp.errors.UnsupportedASTNode`` error will be raised. Implemented
methods to handle AST node types are found in the ``_node_switch`` dict: ::

	self._node_switch = {
		AST.FileAST:		self._handle_file_ast,
		AST.Decl:			self._handle_decl,
		AST.TypeDecl:		self._handle_type_decl,
		AST.ByRefDecl:		self._handle_byref_decl,
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
		AST.ArrayDecl:		self._handle_array_decl,
		AST.InitList:		self._handle_init_list,
		AST.If:				self._handle_if,
		AST.For:			self._handle_for,
		AST.While:			self._handle_while,
		AST.DeclList:		self._handle_decl_list,
		AST.Break:			self._handle_break,
		AST.Continue:		self._handle_continue,
		AST.ArrayRef:		self._handle_array_ref,
		AST.Enum:			self._handle_enum,
		AST.Switch:			self._handle_switch,
		AST.Cast:			self._handle_cast,
		AST.Typename:		self._handle_typename,
		AST.EmptyStatement: self._handle_empty_statement,

		StructDecls:		self._handle_struct_decls,
		UnionDecls:			self._handle_union_decls,
	}

Interpreter Reference Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: pfp.interp
   :members:

.. automodule:: pfp.interp
   :members:
