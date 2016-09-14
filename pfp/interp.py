#!/usr/bin/env python

"""
Python format parser
"""

import collections
import copy
import glob
import logging
import os
import re
import six
import sys
import traceback

import py010parser
import py010parser.c_parser
from py010parser import c_ast as AST

import pfp
import pfp.bitwrap as bitwrap
import pfp.errors as errors
import pfp.fields as fields
import pfp.functions as functions
import pfp.native as native
import pfp.utils as utils

logging.basicConfig(level=logging.CRITICAL)

class Decls(object):
    def __init__(self, decls, coord):
        self.decls = decls
        self.coord = coord

class UnionDecls(Decls): pass
class StructDecls(Decls): pass

def StructDeclWithParams(scope, struct_cls, struct_args):
    def _pfp__init(self, stream):
        for param in self._pfp__node.args.params:
            param.is_func_param = True

        params = self._pfp__interp._handle_node(
            self._pfp__node.args,
            scope,
            self,
            None
        )
        param_list = params.instantiate(scope, struct_args, self._pfp__interp)
        super(self.__class__, self)._pfp__init(stream)
        
    new_class = type(struct_cls.__name__ + "_", (struct_cls,), {
        "_pfp__init":    _pfp__init,
    })
    return new_class

def StructUnionDef(typedef_name, interp, node):
    if isinstance(node, AST.Struct):
        cls = fields.Struct
        decls = StructDecls(node.decls, node.coord)
    elif isinstance(node, AST.Union):
        cls = fields.Union
        decls = UnionDecls(node.decls, node.coord)

    # this is so that we can have all nested structs added to
    # the root DOM, even if there's an error in parsing the data.
    # If we didn't do this, any errors parsing the data would cause
    # the new struct to not be added to its parent, and the user would
    # not be able to see how far the script got
    def __init__(self, stream=None, metadata_processor=None, do_init=True):
        cls.__init__(self, stream, metadata_processor=metadata_processor)

        if do_init:
            self._pfp__init(stream)

    def _pfp__init(self, stream):
        self._pfp__interp._handle_node(
            decls,
            ctxt=self,
            stream=stream
        )

    new_class = type(typedef_name, (cls,), {
        "__init__":        __init__,
        "_pfp__init":    _pfp__init,
        "_pfp__node":    node,
        "_pfp__interp":    interp,
    })
    return new_class

def EnumDef(typedef_name, base_cls, enum_vals):
    new_class = type(typedef_name, (fields.Enum,), {
        "width"        : base_cls.width,
        "endian"    : base_cls.endian,
        "format"    : base_cls.format,
        "enum_vals"    : enum_vals,
        "enum_cls"    : base_cls
    })
    return new_class

def ArrayDecl(item_cls, item_count):
    width = fields.PYVAL(item_count)
    def __init__(self, stream=None, metadata_processor=None):
        fields.Array.__init__(self, self.width, self.field_cls, stream, metadata_processor=metadata_processor)
    new_class = type("Array_{}_{}".format(item_cls.__name__, width), (fields.Array,), {
        "__init__"    : __init__,
        "width"        : width,
        "field_cls"    : item_cls,
    })
    return new_class

def LazyField(lookup_name, scope):
    """Super non-standard stuff here. Dynamically changing the base
    class using the scope and the lazy name when the class is
    instantiated. This works as long as the original base class is
    not directly inheriting from object (which we're not, since
    our original base class is fields.Field).
    """
    def __init__(self, stream=None):
        base_cls = self._pfp__scope.get_id(self._pfp__lazy_name)
        self.__class__.__bases__ = (base_cls,)
        base_cls.__init__(self, stream)

    new_class = type(lookup_name + "_lazy", (fields.Field,), {
        "__init__"            : __init__,
        "_pfp__scope"        : scope,
        "_pfp__lazy_name"    : lookup_name
    })
    return new_class

#class StructUnionDef(object):
#
#    """A class used to instantiate structs/unions as
#    needed (used for typedefs)"""
#
#    def __init__(self, interp, node):
#        """Save the interpreter and the node so that when
#        this instance is called (will act like instantiation),
#        the interpreter is just told to handle the node
#        
#        :interp: The interpreter
#        :node: The node to interpret upon instantiation
#        :stream: The stream that data will be parsed from
#        """
#        self._interp = interp
#        self._node = node
#        self._typedef_name = node._pfp__typedef_name
#    
#    def __call__(self, stream=None):
#        """Create an instance of the struct/union
#
#        :stream: The stream that data will be parsed from
#        :returns: A struct or union instance
#        """
#        # TODO stream should be optional to act like other fields classes
#        res = self._interp._handle_node(self._node, stream=stream)
#        res._pfp__typedef_name = self._typedef_name
#        # UGH TODO HACK HACK HACK!!! stupid
#        res._pfp__class = self
#        return res

class DebugLogger(object):
    def __init__(self, active=False):
        self._log = logging.getLogger("")
        self._indent = 0
        self._active = active
        if self._active:
            self._log.setLevel(logging.DEBUG)
    
    def debug(self, prefix, msg, indent_change=0, filename=None, coord=None):
        if not self._active:
            return

        self._indent += indent_change
        if coord is not None and filename:
            prefix += ":{}:{}".format(filename, coord.line)

        self._log.debug("\n".join(prefix + ": " + "  "*self._indent + line for line in msg.split("\n")))
    
    def inc(self):
        self._indent += 1
    
    def dec(self):
        self._indent -= 1

class NullStream(object):
    def __init__(self):
        self._pos = 0
    
    def read(self, num):
        return utils.binary("\x00" * num)
    
    def write(self, data):
        pass
    
    def close(self):
        pass
    
    def seek(self, pos, seek_type=0):
        if seek_type == 0:
            self._pos = pos
        elif seek_type == 1:
            self._pos += pos
        elif seek_type == 2:
            # we never use this anyways
            pass
    
    def tell(self):
        return self._pos

class PfpTypes(object):
    """A class to hold all typedefd types in a template. Note that
    types are instantiated by having them parse a null-stream. This
    means that type creation will not work correctly for complicated
    structs that have internal control-flow"""

    _interp = None
    _scope = None
    _types_map = None
    _null_stream = None

    def __init__(self, interp, scope):
        """Init the ``PfpTypes`` class

        :param pfp.interp.PfpInterp interp: The pfp interpreter
        :param pfp.interp.Scope scope: The scope to pull all the types from
        """
        self._interp = interp
        self._scope = scope
        self._null_stream = bitwrap.BitwrappedStream(NullStream())

        self._types_map = {}

        for scope_ctxt in self._scope._scope_stack:
            for type_name,type_cls in six.iteritems(scope_ctxt["types"]):
                if isinstance(type_cls, list):
                    type_cls = self._interp._resolve_to_field_class(type_cls, self._scope)
                self._types_map[type_name] = type_cls
    
    def _wrap_type_instantiation(self, type_cls):
        """Wrap the creation of the type so that we can provide
        a null-stream to initialize it"""
        def wrapper(*args, **kwargs):
            # use args for struct arguments??
            return type_cls(stream=self._null_stream)
        return wrapper
    
    def __getattr__(self, attr_name):
        if attr_name in self._types_map:
            return self._wrap_type_instantiation(self._types_map[attr_name])
        else:
            # let this raise any errors
            return super(self.__class__, self).__getattribute__(attr_name)
    
    def __getitem__(self, attr_name):
        if attr_name in self._types_map:
            return self._wrap_type_instantiation(self._types_map[attr_name])
        else:
            raise KeyError(attr_name)

class Scope(object):
    """A class to keep track of the current scope of the interpreter"""
    def __init__(self, logger, parent=None):
        super(Scope, self).__init__()

        self._log = logger
        self._parent = parent

        self._scope_stack = []
        self.push()
    
    def level(self):
        """Return the current scope level
        """
        res = len(self._scope_stack)
        if self._parent is not None:
            res += self._parent.level()
        return res
        
    def push(self, new_scope=None):
        """Create a new scope
        :returns: TODO

        """
        if new_scope is None:
            new_scope = {
                "types": {},
                "vars": {}
            }
        self._curr_scope = new_scope
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
        res = self._scope_stack.pop()
        self._dlog("popping scope, scope level = {}".format(self.level()))
        self._curr_scope = self._scope_stack[-1]
        return res
    
    def add_var(self, field_name, field, root=False):
        """Add a var to the current scope (vars are fields that
        parse the input stream)

        :field_name: TODO
        :field: TODO
        :returns: TODO

        """
        self._dlog("adding var '{}' (root={})".format(field_name, root))

        # do both so it's not clobbered by intermediate values of the same name
        if root:
            self._scope_stack[0]["vars"][field_name] = field

        # TODO do we allow clobbering of vars???
        self._curr_scope["vars"][field_name] = field

    
    def get_var(self, name, recurse=True):
        """Return the first var of name ``name`` in the current
        scope stack (remember, vars are the ones that parse the
        input stream)

        :name: The name of the id
        :recurse: Whether parent scopes should also be searched (defaults to True)
        :returns: TODO

        """
        self._dlog("getting var '{}'".format(name))
        return self._search("vars", name, recurse)
    
    def add_local(self, field_name, field):
        """Add a local variable in the current scope

        :field_name: The field's name
        :field: The field
        :returns: None

        """
        self._dlog("adding local '{}'".format(field_name))
        field._pfp__name = field_name
        # TODO do we allow clobbering of locals???
        self._curr_scope["vars"][field_name] = field
    
    def get_local(self, name, recurse=True):
        """Get the local field (search for it) from the scope stack. An alias
        for ``get_var``

        :name: The name of the local field
        """
        self._dlog("getting local '{}'".format(name))
        return self._search("vars", name, recurse)
    
    def add_type_class(self, name, cls):
        """Store the class with the name
        """
        self._curr_scope["types"][name] = cls
    
    def add_type_struct_or_union(self, name, interp, node):
        """Store the node with the name. When it is instantiated,
        the node itself will be handled.

        :name: name of the typedefd struct/union
        :node: the union/struct node
        :interp: the 010 interpreter
        """
        self.add_type_class(name, StructUnionDef(name, interp, node))
    
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
    
    def get_type(self, name, recurse=True):
        """Get the names for the typename (created by typedef)

        :name: The typedef'd name to resolve
        :returns: An array of resolved names associated with the typedef'd name

        """
        self._dlog("getting type '{}'".format(name))
        return self._search("types", name, recurse)
    
    def get_id(self, name, recurse=True):
        """Get the first id matching ``name``. Will either be a local
        or a var.

        :name: TODO
        :returns: TODO

        """
        self._dlog("getting id '{}'".format(name))
        var = self._search("vars", name, recurse)
        return var
    
    # ------------------
    # PRIVATE
    # ------------------

    def _dlog(self, msg):
        self._log.debug(" scope({:08x})".format(id(self)), msg)

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
    
    def _search(self, category, name, recurse=True):
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

        if recurse and self._parent is not None:
            return self._parent._search(category, name, recurse)

        return None
    
    # def __getattr__
    # def __setattr__

class PfpInterp(object):
    """
    """

    BITFIELD_DIR_LEFT_RIGHT = -1
    BITFIELD_DIR_DEFAULT = 0
    BITFIELD_DIR_RIGHT_LEFT = 1

    # do not break (execute until finished)
    BREAK_NONE = 0
    # break on the next instruction on the same level
    BREAK_OVER = 1
    # break on the next instruction regardless of level
    BREAK_INTO = 2

    _natives = {}
    _predefines = []

    @classmethod
    def add_native(cls, name, func, ret, interp=None, send_interp=False):
        """Add the native python function ``func`` into the pfp interpreter with the
        name ``name`` and return value ``ret`` so that it can be called from
        within a template script.

        .. note::
            The :any:`@native <pfp.native.native>` decorator exists to simplify this.

        All native functions must have the signature ``def func(params, ctxt, scope, stream, coord [,interp])``,
        optionally allowing an interpreter param if ``send_interp`` is ``True``.

        Example:

            The example below defines a function ``Sum`` using the ``add_native`` method. ::

                import pfp.fields
                from pfp.fields import PYVAL

                def native_sum(params, ctxt, scope, stream, coord):
                    return PYVAL(params[0]) + PYVAL(params[1])

                pfp.interp.PfpInterp.add_native("Sum", native_sum, pfp.fields.Int64)

        :param basestring name: The name the function will be exposed as in the interpreter.
        :param function func: The native python function that will be referenced.
        :param type(pfp.fields.Field) ret: The field class that the return value should be cast to.
        :param pfp.interp.PfpInterp interp: The specific pfp interpreter the function should be defined in.
        :param bool send_interp: If true, the current pfp interpreter will be added as an argument to the function.
        """
        if interp is None:
            natives = cls._natives
        else:
            # the instance's natives
            natives = interp._natives

        natives[name] = functions.NativeFunction(
            name, func, ret, send_interp
        )
    
    @classmethod
    def add_predefine(cls, template):
        """Add a template that should be run prior to running any other templates.
        This is useful for predefining types, etc.

        :param basestring template: The template text (unicode is also fine here)
        """
        cls._predefines.append(template)
    
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
            setattr(mod, "PYSTR", fields.get_str)

    def __init__(self, debug=False, parser=None, int3=True):
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
        self._padded_bitfield = True
        # TODO does this default change based on the endianness?
        self._bitfield_direction = self.BITFIELD_DIR_DEFAULT
        # whether or not debugging is allowed (ie Int3())
        self._int3 = int3

        self._ctxt = None
        self._scope = None
        self._coord = None
        self._orig_filename = None
        
        if parser is None:
            parser = py010parser.c_parser.CParser()
        # this speeds things up a bit
        self._parser = parser

        self._node_switch = {
            AST.FileAST            : self._handle_file_ast,
            AST.Decl               : self._handle_decl,
            AST.TypeDecl           : self._handle_type_decl,
            AST.ByRefDecl          : self._handle_byref_decl,
            AST.Struct             : self._handle_struct,
            AST.Union              : self._handle_union,
            AST.StructRef          : self._handle_struct_ref,
            AST.IdentifierType     : self._handle_identifier_type,
            AST.Typedef            : self._handle_typedef,
            AST.Constant           : self._handle_constant,
            AST.BinaryOp           : self._handle_binary_op,
            AST.Assignment         : self._handle_assignment,
            AST.ID                 : self._handle_id,
            AST.UnaryOp            : self._handle_unary_op,
            AST.FuncDef            : self._handle_func_def,
            AST.FuncCall           : self._handle_func_call,
            AST.FuncDecl           : self._handle_func_decl,
            AST.ParamList          : self._handle_param_list,
            AST.ExprList           : self._handle_expr_list,
            AST.Compound           : self._handle_compound,
            AST.Return             : self._handle_return,
            AST.ArrayDecl          : self._handle_array_decl,
            AST.InitList           : self._handle_init_list,
            AST.If                 : self._handle_if,
            AST.For                : self._handle_for,
            AST.While              : self._handle_while,
            AST.DeclList           : self._handle_decl_list,
            AST.Break              : self._handle_break,
            AST.Continue           : self._handle_continue,
            AST.ArrayRef           : self._handle_array_ref,
            AST.Enum               : self._handle_enum,
            AST.Switch             : self._handle_switch,
            AST.Cast               : self._handle_cast,
            AST.Typename           : self._handle_typename,
            AST.EmptyStatement     : self._handle_empty_statement,
            AST.DoWhile            : self._handle_do_while,
            AST.StructCallTypeDecl : self._handle_struct_call_type_decl,
            AST.TernaryOp          : self._handle_if,

            StructDecls            : self._handle_struct_decls,
            UnionDecls             : self._handle_union_decls,
        }
    
    def _dlog(self, msg, indent_increase=0):
        """log the message to the log"""
        self._log.debug("interp", msg, indent_increase, filename=self._orig_filename, coord=self._coord)
    
    # --------------------
    # PUBLIC
    # --------------------

    def parse(self, stream, template, predefines=True, orig_filename=None, keep_successful=False):
        """Parse the data stream using the template (e.g. parse the 010 template
        and interpret the template using the stream as the data source).

        :stream: The input data stream
        :template: The template to parse the stream with
        :keep_successful: Return whatever was successfully parsed before an error. ``_pfp__error`` will contain the exception (if one was raised)
        :returns: Pfp Dom

        """
        self._dlog("parsing")

        self._orig_filename = orig_filename
        self._stream = stream
        self._template = template
        self._template_lines = self._template.split("\n")
        self._ast = self._parse_string(template, predefines)
        self._dlog("parsed template into ast")

        res = self._run(keep_successful)
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

        ast = self._parse_string(statement, predefines=False)

        self._dlog("evaluating statement: {}".format(statement))
        
        try:
            res = None
            for child in ast.children():
                res = self._handle_node(child, self._scope, self._ctxt, self._stream)
            return res
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

        lines = [(x, self._template_lines[x]) for x in six.moves.range(start, end, 1)]
        return self._coord.line, lines
    
    def set_bitfield_padded(self, val):
        """Set if the bitfield input/output stream should be padded

        :val: True/False
        :returns: None
        """
        self._padded_bitfield = val
        self._stream.padded = val
        self._ctxt._pfp__padded_bitfield = val
    
    def set_bitfield_direction(self, val):
        """Set the bitfields to parse from left to right (1), the default (None), or right to left (-1)
        """
        self._bitfield_direction = val
    
    def get_bitfield_padded(self):
        """Return if the bitfield input/output stream should be padded

        :returns: True/False
        """
        return self._padded_bitfield
    
    def get_bitfield_direction(self):
        """Return if the bitfield direction

        .. note:: This should be applied AFTER taking into account endianness.
        """
        return self._bitfield_direction
    
    def get_filename(self):
        """Return the filename of the data that is currently being
        parsed

        :returns: The name of the data file being parsed.
        """
        return self._orig_filename
    
    def get_types(self):
        """Return a types object that will contain all of the typedefd structs'
        classes.

        :returns: Types object

        Example:

            Create a new PNG_CHUNK object from a PNG_CHUNK type that was defined
            in a template: ::

            types = interp.get_types()
            chunk = types.PNG_CHUNK()
        """
        return PfpTypes(self, self._scope)
    
    # --------------------
    # PRIVATE
    # --------------------
    
    def _parse_string(self, string, predefines=True):
        exts = []
        if predefines:
            for idx,predefine in enumerate(self._predefines):
                try:
                    ast = py010parser.parse_string(
                        predefine,
                        parser=self._parser,
                        # clear out the scopes for the first one
                        # that we run
                        keep_scopes=(idx != 0),
                    )
                    exts += ast.ext
                except:
                    pass

        res = py010parser.parse_string(
            string,
            parser=self._parser,
            # only keep the scopes if we ran the predefines
            keep_scopes=predefines
        )
        res.ext = exts + res.ext

        return res
    
    def _run(self, keep_successfull):
        """Interpret the parsed 010 AST
        :returns: PfpDom

        """

        # example self._ast.show():
        #    FileAST:
        #      Decl: data, [], [], []
        #        TypeDecl: data, []
        #          Struct: DATA
        #            Decl: a, [], [], []
        #              TypeDecl: a, []
        #                IdentifierType: ['char']
        #            Decl: b, [], [], []
        #              TypeDecl: b, []
        #                IdentifierType: ['char']
        #            Decl: c, [], [], []
        #              TypeDecl: c, []
        #                IdentifierType: ['char']
        #            Decl: d, [], [], []
        #              TypeDecl: d, []
        #                IdentifierType: ['char']

        self._dlog("interpreting template")

        try:
            # it is important to pass the stream in as the stream
            # may change (e.g. compressed data)
            res = self._handle_node(self._ast, None, None, self._stream)
        except errors.InterpReturn as e:
            # TODO handle exit/return codes (e.g. return -1)
            res = self._root
        except errors.InterpExit as e:
            res = self._root
        except Exception as e:
            if keep_successfull:
                # return the root and set _pfp__error
                res = self._root
                res._pfp__error = e

            else:
                exc_type, exc_obj, traceback = sys.exc_info()
                more_info = "\nException at {}:{}".format(
                    self._orig_filename,
                    self._coord.line
                )
                six.reraise(
                    errors.PfpError,
                    errors.PfpError(exc_obj.__class__.__name__ + ": " + exc_obj.args[0] + more_info if len(exc_obj.args) > 0 else more_info),
                    traceback
                )

        # final drop-in after everything has executed
        if self._break_type != self.BREAK_NONE:
            self.debugger.cmdloop("execution finished")

        types = self.get_types()
        res._pfp__types = types

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

        # TODO probably a better way to do this...
        # this occurs with if-statements that have a single statement
        # instead of a compound statement (no curly braces)
        elif type(node) is list and len(list(filter(lambda x: isinstance(x, AST.Node), node))) == len(node):
            node = AST.Compound(
                block_items=node,
                coord=node[0].coord
            )
            return self._handle_node(node, scope, ctxt, stream)

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
        self._root = ctxt = fields.Dom(stream)
        ctxt._pfp__scope = scope
        self._root._pfp__name = "__root"
        self._root._pfp__interp = self
        self._dlog("handling file AST with {} children".format(len(node.children())))

        for child in node.children():
            self._handle_node(child, scope, ctxt, stream)

        ctxt._pfp__process_fields_metadata()

        return ctxt
    
    def _handle_empty_statement(self, node, scope, ctxt, stream):
        """Handle empty statements

        :node: TODO
        :scope: TODO
        :ctxt: TODO
        :stream: TODO
        :returns: TODO

        """
        self._dlog("handling empty statement")
    
    def _handle_cast(self, node, scope, ctxt, stream):
        """Handle cast nodes

        :node: TODO
        :scope: TODO
        :ctxt: TODO
        :stream: TODO
        :returns: TODO

        """
        self._dlog("handling cast")
        to_type = self._handle_node(node.to_type, scope, ctxt, stream)
        val_to_cast = self._handle_node(node.expr, scope, ctxt, stream)

        res = to_type()
        res._pfp__set_value(val_to_cast)
        return res
    
    def _handle_typename(self, node, scope, ctxt, stream):
        """TODO: Docstring for _handle_typename

        :node: TODO
        :scope: TODO
        :ctxt: TODO
        :stream: TODO
        :returns: TODO

        """
        self._dlog("handling typename")

        return self._handle_node(node.type, scope, ctxt, stream)
    
    def _get_node_name(self, node):
        """Get the name of the node - check for node.name and
        node.type.declname. Not sure why the second one occurs
        exactly - it happens with declaring a new struct field
        with parameters"""
        res = getattr(node, "name", None)
        if res is None:
            return res

        if isinstance(res, AST.TypeDecl):
            return res.declname
        
        return res
    
    def _handle_decl(self, node, scope, ctxt, stream):
        """TODO: Docstring for _handle_decl.

        :node: TODO
        :scope: TODO
        :ctxt: TODO
        :stream: TODO
        :returns: TODO

        """
        self._dlog("handling decl")

        metadata_processor = None
        if node.metadata is not None:
            #metadata_info = self._handle_metadata(node, scope, ctxt, stream)
            def process_metadata():
                metadata_info = self._handle_metadata(node, scope, ctxt, stream)
                return metadata_info
            metadata_processor = process_metadata

        field_name = self._get_node_name(node)
        field = self._handle_node(node.type, scope, ctxt, stream)
        bitsize = None
        bitfield_rw = None
        if getattr(node, "bitsize", None) is not None:
            bitsize = self._handle_node(node.bitsize, scope, ctxt, stream)
            has_prev = len(ctxt._pfp__children) > 0

            bitfield_rw = None
            if has_prev:
                prev = ctxt._pfp__children[-1]
                # if it was a bitfield as well
                # TODO I don't think this will handle multiple bitfield groups in a row.
                # E.g.
                #     char a: 8, b:8;
                #    char c: 8, d:8;
                if ((self._padded_bitfield and prev.__class__.width == field.width) or not self._padded_bitfield) \
                        and prev.bitsize is not None and prev.bitfield_rw.reserve_bits(bitsize, stream):
                    bitfield_rw = prev.bitfield_rw

            # either because there was no previous bitfield, or the previous was full
            if bitfield_rw is None:
                bitfield_rw = fields.BitfieldRW(self, field)
                bitfield_rw.reserve_bits(bitsize, stream)

        if getattr(node, "is_func_param", False):
            # we want to keep this as a class and not instantiate it
            # instantiation will be done in functions.ParamListDef.instantiate
            field = (field_name, field)
        
        # locals and consts still get a field instance, but DON'T parse the
        # stream!
        elif "local" in node.quals or "const" in node.quals:
            is_struct = issubclass(field, fields.Struct)
            if not isinstance(field, fields.Field) and not is_struct:
                field = field()
            scope.add_local(field_name, field)

            # this should only be able to be done with locals, right?
            # if not, move it to the bottom of the function
            if node.init is not None:
                val = self._handle_node(node.init, scope, ctxt, stream)
                if is_struct:
                    field = val
                    scope.add_local(field_name, field)
                else:
                    field._pfp__set_value(val)

            if "const" in node.quals:
                field._pfp__freeze()

            field._pfp__interp = self

        elif isinstance(field, functions.Function):
            # eh, just add it as a local...
            # maybe the whole local/vars thinking needs to change...
            # and we should only have ONE map TODO
            field.name = field_name
            scope.add_local(field_name, field)

        elif field_name is not None:
            added_child = False

    
            # by this point, structs are already instantiated (they need to be
            # in order to set the new context)
            if not isinstance(field, fields.Field):
                if issubclass(field, fields.NumberBase):
                    # use the default bitfield direction
                    if self._bitfield_direction is self.BITFIELD_DIR_DEFAULT:
                        bitfield_left_right = True if field.endian == fields.BIG_ENDIAN else False
                    else:
                        bitfield_left_right = (self._bitfield_direction is self.BITFIELD_DIR_LEFT_RIGHT)

                    field = field(
                        stream,
                        bitsize=bitsize,
                        metadata_processor=metadata_processor,
                        bitfield_rw=bitfield_rw,
                        bitfield_padded=self._padded_bitfield,
                        bitfield_left_right=bitfield_left_right
                    )

                # TODO
                # for now if there's a struct inside of a union that is being
                # parsed when there's an error, the user will lose information
                # about how far the parsing got. Here we are explicitly checking for
                # adding structs and unions to a parent union.
                elif (issubclass(field, fields.Struct) or issubclass(field, fields.Union)) \
                        and not isinstance(ctxt, fields.Union) \
                        and hasattr(field, "_pfp__init"):

                    # this is so that we can have all nested structs added to
                    # the root DOM, even if there's an error in parsing the data.
                    # If we didn't do this, any errors parsing the data would cause
                    # the new struct to not be added to its parent, and the user would
                    # not be able to see how far the script got
                    field = field(stream, metadata_processor=metadata_processor, do_init=False)
                    field._pfp__interp = self
                    field_res = ctxt._pfp__add_child(field_name, field, stream)

                    # when adding a new field to a struct/union/fileast, add it to the
                    # root of the ctxt's scope so that it doesn't get lost by being declared
                    # from within a function
                    scope.add_var(field_name, field_res, root=True)

                    field_res._pfp__interp = self
                    field._pfp__init(stream)
                    added_child = True
                else:
                    field = field(stream, metadata_processor=metadata_processor)

            if not added_child:
                field._pfp__interp = self
                field_res = ctxt._pfp__add_child(field_name, field, stream)
                field_res._pfp__interp = self

                # when adding a new field to a struct/union/fileast, add it to the
                # root of the ctxt's scope so that it doesn't get lost by being declared
                # from within a function
                scope.add_var(field_name, field_res, root=True)

                # this shouldn't be used elsewhere, but should still be explicit with
                # this flag
                added_child = True

        # enums will get here. If there is no name, then no
        # field is being declared (but the enum values _will_
        # get defined). E.g.:
        #     enum <uchar blah {
        #         BLAH1,
        #        BLAH2,
        #        BLAH3
        #     };
        elif field_name is None:
            pass

        return field
    
    def _handle_metadata(self, node, scope, ctxt, stream):
        """Handle metadata for the node
        """
        self._dlog("handling node metadata {}".format(node.metadata.keyvals))

        keyvals = node.metadata.keyvals

        metadata_info = []

        if "watch" in node.metadata.keyvals or "update" in keyvals:
            metadata_info.append(
                self._handle_watch_metadata(node, scope, ctxt, stream)
            )

        if "packtype" in node.metadata.keyvals or "packer" in keyvals:
            metadata_info.append(
                self._handle_packed_metadata(node, scope, ctxt, stream)
            )

        return metadata_info

        #char blah[60] <pack=Zip, unpack=Unzip, packtype=DataType>;
        #char blah[60] <packer=Zip, packtype=DataType>;
        #int checksum <watch=field1,field2,field3, update=Crc32>;
    
    def _handle_watch_metadata(self, node, scope, ctxt, stream):
        """Handle watch vars for fields
        """
        keyvals = node.metadata.keyvals
        if "watch" not in keyvals:
            raise errors.PfpError("Packed fields require a packer function set")
        if "update" not in keyvals:
            raise errors.PfpError("Packed fields require a packer function set")

        watch_field_name = keyvals["watch"]
        update_func_name = keyvals["update"]

        watch_fields = list(map(lambda x: self.eval(x.strip()), watch_field_name.split(";")))
        update_func = scope.get_id(update_func_name)

        return {
            "type": "watch",
            "watch_fields": watch_fields,
            "update_func": update_func,
            "func_call_info": (ctxt, scope, stream, self, self._coord)
        }
    
    def _handle_packed_metadata(self, node, scope, ctxt, stream):
        """Handle packed metadata
        """
        keyvals = node.metadata.keyvals
        if "packer" not in keyvals and ("pack" not in keyvals or "unpack" not in keyvals):
            raise errors.PfpError("Packed fields require a packer function to be set or pack and unpack functions to be set")
        if "packtype" not in keyvals:
            raise errors.PfpError("Packed fields require a packtype to be set")

        args_ = {}
        if "packer" in keyvals:
            packer_func_name = keyvals["packer"]
            packer_func = scope.get_id(packer_func_name)
            args_["packer"] = packer_func
        elif "pack" in keyvals and "unpack" in keyvals:
            pack_func = scope.get_id(keyvals["pack"])
            unpack_func = scope.get_id(keyvals["unpack"])
            args_["pack"] = pack_func
            args_["unpack"] = unpack_func

        packtype_cls_name = keyvals["packtype"]
        packtype_cls = scope.get_type(packtype_cls_name)
        args_["pack_type"] = packtype_cls

        args_["type"] = "packed"
        args_["func_call_info"] = (ctxt, scope, stream, self, self._coord)
        return args_
    
    def _handle_byref_decl(self, node, scope, ctxt, stream):
        """TODO: Docstring for _handle_byref_decl.

        :node: TODO
        :scope: TODO
        :ctxt: TODO
        :stream: TODO
        :returns: TODO

        """
        self._dlog("handling byref decl")
        field = self._handle_node(node.type.type, scope, ctxt, stream)

        # this will not really be used (maybe except for introspection)
        # with byref function params
        # see issue #35 - we need to wrap the field cls so that the byref
        # doesn't permanently stay on the class
        field = functions.ParamClsWrapper(field)
        field.byref = True
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

        try:
            sub_field = getattr(struct, node.field.name)
        except AttributeError as e:
            # should be able to access implicit array items by index OR
            # access the last one's members directly without index
            #
            # E.g.:
            # 
            # local int total_length = 0;
            # while(!FEof()) {
            #     HEADER header;
            #   total_length += header.length;
            # }
            if isinstance(struct, fields.Array) and struct.implicit:
                last_item = struct[-1]
                sub_field = getattr(last_item, node.field.name)
            else:
                raise

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

        union_cls = StructUnionDef("union", self, node)
        return union_cls
    
    def _handle_union_decls(self, node, scope, ctxt, stream):
        self._dlog("handling union decls")

        # new scope
        scope = ctxt._pfp__scope = Scope(self._log, parent=scope)

        try:
            max_pos = 0
            for decl in node.decls:
                self._handle_node(decl, scope, ctxt, stream)

        finally:
            # the union will have reset the stream
            stream.seek(stream.tell()+ctxt._pfp__width(), 0)
            self._scope = scope._parent
    
    def _handle_init_list(self, node, scope, ctxt, stream):
        """Handle InitList nodes (e.g. when initializing a struct)

        :node: TODO
        :scope: TODO
        :ctxt: TODO
        :stream: TODO
        :returns: TODO

        """
        self._dlog("handling init list")
        res = []
        for _,init_child in node.children():
            init_field = self._handle_node(init_child, scope, ctxt, stream)
            res.append(init_field)
        return res
    
    def _handle_struct_call_type_decl(self, node, scope, ctxt, stream):
        """TODO: Docstring for _handle_struct_call_type_decl.

        :node: TODO
        :scope: TODO
        :ctxt: TODO
        :stream: TODO
        :returns: TODO

        """
        self._dlog("handling struct with parameters")

        struct_cls = self._handle_node(node.type, scope, ctxt, stream)
        struct_args = self._handle_node(node.args, scope, ctxt, stream)

        res = StructDeclWithParams(scope, struct_cls, struct_args)
        return res
    
    def _handle_struct(self, node, scope, ctxt, stream):
        """TODO: Docstring for _handle_struct.

        :node: TODO
        :scope: TODO
        :ctxt: TODO
        :stream: TODO
        :returns: TODO

        """
        self._dlog("handling struct")

        if node.args is not None:
            for param in node.args.params:
                param.is_func_param = True

        # it's actually being defined
        if node.decls is not None:
            struct_cls = StructUnionDef("struct", self, node)

            if node.name is not None:
                scope.add_type_class(node.name, struct_cls)

            return struct_cls

        # it's declaring a struct field. E.g.
        #    struct IFD subDir;
        else:
            return scope.get_type(node.name)
    
    def _handle_struct_decls(self, node, scope, ctxt, stream):
        self._dlog("handling struct decls")

        # new scope
        scope = ctxt._pfp__scope = Scope(self._log, parent=scope)
        self._scope = scope

        try:
            for decl in node.decls:
                # new context! (struct)
                self._handle_node(decl, scope, ctxt, stream)

            ctxt._pfp__process_fields_metadata()

        # so that even if return statements/other exceptions
        # happen, we'll still pop scope
        finally:
            # need to pop the scope!
            self._scope = scope._parent
    
    def _handle_identifier_type(self, node, scope, ctxt, stream):
        """TODO: Docstring for _handle_identifier_type.

        :node: TODO
        :scope: TODO
        :ctxt: TODO
        :stream: TODO
        :returns: TODO

        """
        self._dlog("handling identifier")

        cls = self._resolve_to_field_class(node.names, scope)
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
        is_enum = (node.type.type.__class__ is AST.Enum)

        if is_union_or_struct:
            self._dlog("handling typedef struct/union '{}'".format(node.name))
            scope.add_type_struct_or_union(node.name, self, node.type.type)
        elif is_enum:
            enum_cls = self._handle_node(node.type, scope, ctxt, stream)
            scope.add_type_class(node.name, enum_cls)
        elif isinstance(node.type, AST.ArrayDecl):
            # this does not parse data, just creates the ArrayDecl class
            array_cls = self._handle_node(node.type, scope, ctxt, stream)
            scope.add_type_class(node.name, array_cls)
        else:
            names = node.type.type.names

            self._dlog("handling typedef '{}' ({})".format(node.name, names))
            # don't actually handle the TypeDecl and Identifier nodes,
            # just directly add the types. Example structure:
            #
            #     Typedef: BLAH, [], ['typedef']
            #        TypeDecl: BLAH, []
            #            IdentifierType: ['unsigned', 'char']
            #    
            scope.add_type(node.name, names)
    
    def _str_to_int(self, string):
        """Check for the hex
        """
        string = string.lower()
        if string.endswith("l"):
            string = string[:-1]
        if string.lower().startswith("0x"):
            # should always match
            match = re.match(r'0[xX]([a-fA-F0-9]+)', string)
            return int(match.group(1), 0x10)
        else:
            return int(string)
    
    def _choose_const_int_class(self, val):
        if -0x80000000 < val < 0x80000000:
            return fields.Int
        elif 0 <= val < 0x100000000:
            return fields.UInt
        elif -0x8000000000000000 < val < 0x8000000000000000:
            return fields.Int64
        elif 0 <= val < 0x10000000000000000:
            return fields.UInt64
    
    def _handle_constant(self, node, scope, ctxt, stream):
        """TODO: Docstring for _handle_constant.

        :node: TODO
        :scope: TODO
        :ctxt: TODO
        :stream: TODO
        :returns: TODO

        """
        self._dlog("handling constant type {}".format(node.type))
        switch = {
            "int": (self._str_to_int, self._choose_const_int_class),
            "long": (self._str_to_int, self._choose_const_int_class),
            # TODO this isn't quite right, but py010parser wouldn't have
            # parsed it if it wasn't correct...
            "float": (lambda x: float(x.lower().replace("f", "")), fields.Float),
            "double": (float, fields.Double),

            # cut out the quotes
            "char": (lambda x: ord(utils.string_escape(x[1:-1])), fields.Char),

            # TODO should this be unicode?? will probably bite me later...
            # cut out the quotes
            "string": (lambda x: str(utils.string_escape(x[1:-1])), fields.String)
        }

        if node.type in switch:
            #return switch[node.type](node.value)
            conversion,field_cls = switch[node.type]
            val = conversion(node.value)

            if hasattr(field_cls, "__call__") and not type(field_cls) is type:
                field_cls = field_cls(val)

            field = field_cls()
            field._pfp__set_value(val)
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
            "||": lambda x,y: x or y,
            ">=": lambda x,y: x>=y,
            "<=": lambda x,y: x<=y,
            "==": lambda x,y: x == y,
            "!=": lambda x,y: x != y,
            "&&": lambda x,y: x and y,
            ">>": lambda x,y: x >> y,
            "<<": lambda x,y: x << y,
        }

        left_val = self._handle_node(node.left, scope, ctxt, stream)
        right_val = self._handle_node(node.right, scope, ctxt, stream)

        if node.op not in switch:
            raise errors.UnsupportedBinaryOperator(node.coord, node.op)

        res = switch[node.op](left_val, right_val)

        if type(res) is bool:
            new_res = fields.Int()
            if res:
                new_res._pfp__set_value(1)
            else:
                new_res._pfp__set_value(0)
            res = new_res

        return res
    
    def _handle_unary_op(self, node, scope, ctxt, stream):
        """TODO: Docstring for _handle_unary_op.

        :node: TODO
        :scope: TODO
        :ctxt: TODO
        :stream: TODO
        :returns: TODO

        """
        self._dlog("handling unary op {}".format(node.op))

        special_switch = {
            "parentof"            : self._handle_parentof,
            "exists"            : self._handle_exists,
            "function_exists"    : self._handle_function_exists,
            "p++"                : self._handle_post_plus_plus,
            "p--"                : self._handle_post_minus_minus,
        }

        switch = {
            # for ++i and --i
            "++":        lambda x,v: x.__iadd__(1),
            "--":        lambda x,v: x.__isub__(1),

            "~":        lambda x,v: ~x,
            "!":        lambda x,v: not x,
            "-":        lambda x,v: -x,
            "sizeof":    lambda x,v: (fields.UInt64()+x._pfp__width()),
            "startof":    lambda x,v: x._pfp__offset,
        }

        if node.op not in switch and node.op not in special_switch:
            raise errors.UnsupportedUnaryOperator(node.coord, node.op)

        if node.op in special_switch:
            return special_switch[node.op](node, scope, ctxt, stream)

        field = self._handle_node(node.expr, scope, ctxt, stream)
        res = switch[node.op](field, 1)
        if res in [True, False]:
            new_res = field.__class__()
            new_res._pfp__set_value(1 if res == True else 0)
            res = new_res
        return res
    
    def _handle_post_plus_plus(self, node, scope, ctxt, stream):
        field = self._handle_node(node.expr, scope, ctxt, stream)
        clone = field.__class__()
        clone._pfp__set_value(field)
        field += 1
        return clone
    
    def _handle_post_minus_minus(self, node, scope, ctxt, stream):
        field = self._handle_node(node.expr, scope, ctxt, stream)
        clone = field.__class__()
        clone._pfp__set_value(field)
        field -= 1
        return clone
    
    def _handle_parentof(self, node, scope, ctxt, stream):
        """Handle the parentof unary operator

        :node: TODO
        :scope: TODO
        :ctxt: TODO
        :stream: TODO
        :returns: TODO

        """
        # if someone does something like parentof(this).blah,
        # we'll end up with a StructRef instead of an ID ref
        # for node.expr, but we'll also end up with a structref
        # if the user does parentof(a.b.c)...
        # 
        # TODO how to differentiate between the two??
        #
        # the proper way would be to do (parentof(a.b.c)).a or
        # (parentof a.b.c).a

        field = self._handle_node(node.expr, scope, ctxt, stream)
        parent = field._pfp__parent
        return parent
    
    def _handle_exists(self, node, scope, ctxt, stream):
        """Handle the exists unary operator

        :node: TODO
        :scope: TODO
        :ctxt: TODO
        :stream: TODO
        :returns: TODO

        """
        res = fields.Int()
        try:
            self._handle_node(node.expr, scope, ctxt, stream)
            res._pfp__set_value(1)
        except AttributeError:
            res._pfp__set_value(0)
        return res
    
    def _handle_function_exists(self, node, scope, ctxt, stream):
        """Handle the function_exists unary operator

        :node: TODO
        :scope: TODO
        :ctxt: TODO
        :stream: TODO
        :returns: TODO

        """
        res = fields.Int()
        try:
            func = self._handle_node(node.expr, scope, ctxt, stream)
            if isinstance(func, functions.BaseFunction):
                res._pfp__set_value(1)
            else:
                res._pfp__set_value(0)
        except errors.UnresolvedID:
            res._pfp__set_value(0)
        return res
    
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
        if node.name == "__this" or node.name == "this":
            return ctxt

        self._dlog("handling id {}".format(node.name))
        field = scope.get_id(node.name)

        is_lazy = getattr(node, "is_lazy", False)

        if field is None and not is_lazy:
            raise errors.UnresolvedID(node.coord, node.name)
        elif is_lazy:
            return LazyField(node.name, scope)

        return field
    
    def _handle_assignment(self, node, scope, ctxt, stream):
        """Handle assignment nodes

        :node: TODO
        :scope: TODO
        :ctxt: TODO
        :stream: TODO
        :returns: TODO

        """
        def add_op(x,y): x += y
        def sub_op(x,y): x -= y
        def div_op(x,y): x /= y
        def mod_op(x,y): x %= y
        def mul_op(x,y): x *= y
        def xor_op(x,y): x ^= y
        def and_op(x,y): x &= y
        def or_op(x,y): x |= y
        def lshift_op(x,y): x <<= y
        def rshift_op(x,y): x >>= y
        def assign_op(x,y): x._pfp__set_value(y)

        switch = {
            "+="    : add_op,
            "-="    : sub_op,
            "/="    : div_op,
            "%="    : mod_op,
            "*="    : mul_op,
            "^="    : xor_op,
            "&="    : and_op,
            "|="    : or_op,
            "<<="    : lshift_op,
            ">>="    : rshift_op,
            "="        : assign_op
        }

        self._dlog("handling assignment")
        field = self._handle_node(node.lvalue, scope, ctxt, stream)
        self._dlog("field = {}".format(field))
        value = self._handle_node(node.rvalue, scope, ctxt, stream)

        if node.op is None:
            self._dlog("value = {}".format(value))
            field._pfp__set_value(value)
        else:
            self._dlog("value {}= {}".format(node.op, value))
            if node.op not in switch:
                raise errors.UnsupportedAssignmentOperator(node.coord, node.op)
            switch[node.op](field, value)
    
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
            self._mark_id_as_lazy(param)
            param_info = self._handle_node(param, scope, ctxt, stream)
            params.append(param_info)

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
        #scope.push()

        try:
            for child in node.children():
                self._handle_node(child, scope, ctxt, stream)

        # in case a return occurs, be sure to pop the scope
        # (returns are implemented by raising an exception)
        finally:
            #scope.pop()
            pass
    
    def _handle_return(self, node, scope, ctxt, stream):
        """Handle Return nodes

        :node: TODO
        :scope: TODO
        :ctxt: TODO
        :stream: TODO
        :returns: TODO

        """
        self._dlog("handling return")
        if node.expr is None:
            ret_val = None
        else:
            ret_val = self._handle_node(node.expr, scope, ctxt, stream)
        self._dlog("return value = {}".format(ret_val))
        raise errors.InterpReturn(ret_val)
    
    def _handle_enum(self, node, scope, ctxt, stream):
        """Handle enum nodes

        :node: TODO
        :scope: TODO
        :ctxt: TODO
        :stream: TODO
        :returns: TODO

        """
        self._dlog("handling enum")
        if node.type is None:
            enum_cls = fields.Int
        else:
            enum_cls = self._handle_node(node.type, scope, ctxt, stream)

        enum_vals = {}
        curr_val = enum_cls()
        curr_val._pfp__value = -1
        for enumerator in node.values.enumerators:
            if enumerator.value is not None:
                curr_val = self._handle_node(enumerator.value, scope, ctxt, stream)
            else:
                curr_val = curr_val + 1
            curr_val._pfp__freeze()
            enum_vals[enumerator.name] = curr_val
            enum_vals[fields.PYVAL(curr_val)] = enumerator.name
            scope.add_local(enumerator.name, curr_val)

        if node.name is not None:
            enum_cls = EnumDef(node.name, enum_cls, enum_vals)
            scope.add_type_class(node.name, enum_cls)

        else:
            enum_cls = EnumDef("enum_" + enum_cls.__name__, enum_cls, enum_vals)
            # don't add to scope if we don't have a name

        return enum_cls
    
    def _handle_array_decl(self, node, scope, ctxt, stream):
        """Handle ArrayDecl nodes

        :node: TODO
        :scope: TODO
        :ctxt: TODO
        :stream: TODO
        :returns: TODO

        """
        self._dlog("handling array declaration '{}'".format(node.type.declname))

        if node.dim is None:
            # will be used
            array_size = None
        else:
            array_size = self._handle_node(node.dim, scope, ctxt, stream)
        self._dlog("array size = {}".format(array_size))
        # TODO node.dim_quals
        # node.type
        field_cls = self._handle_node(node.type, scope, ctxt, stream)
        self._dlog("field class = {}".format(field_cls))
        array = ArrayDecl(field_cls, array_size)
        #array = fields.Array(array_size, field_cls)
        array._pfp__name = node.type.declname
        #array._pfp__parse(stream)
        return array
    
    def _handle_array_ref(self, node, scope, ctxt, stream):
        """Handle ArrayRef nodes

        :node: TODO
        :scope: TODO
        :ctxt: TODO
        :stream: TODO
        :returns: TODO

        """
        ary = self._handle_node(node.name, scope, ctxt, stream)
        subscript = self._handle_node(node.subscript, scope, ctxt, stream)
        return ary[fields.PYVAL(subscript)]

    def _handle_if(self, node, scope, ctxt, stream):
        """Handle If nodes

        :node: TODO
        :scope: TODO
        :ctxt: TODO
        :stream: TODO
        :returns: TODO

        """
        self._dlog("handling if/ternary_op")
        cond = self._handle_node(node.cond, scope, ctxt, stream)
        if cond:
            # there should always be an iftrue
            return self._handle_node(node.iftrue, scope, ctxt, stream)
        else:
            if node.iffalse is not None:
                return self._handle_node(node.iffalse, scope, ctxt, stream)
    
    def _handle_for(self, node, scope, ctxt, stream):
        """Handle For nodes

        :node: TODO
        :scope: TODO
        :ctxt: TODO
        :stream: TODO
        :returns: TODO

        """
        self._dlog("handling for")
        if node.init is not None:
            # perform the init
            self._handle_node(node.init, scope, ctxt, stream)

        while node.cond is None or self._handle_node(node.cond, scope, ctxt, stream):
            if node.stmt is not None:
                try:
                    # do the for body
                    self._handle_node(node.stmt, scope, ctxt, stream)
                except errors.InterpBreak as e:
                    break
                
                # we still need to interpret the "next" statement,
                # so just pass
                except errors.InterpContinue as e:
                    pass

            if node.next is not None:
                # do the next statement
                self._handle_node(node.next, scope, ctxt, stream)
    
    def _handle_while(self, node, scope, ctxt, stream):
        """Handle break node

        :node: TODO
        :scope: TODO
        :ctxt: TODO
        :stream: TODO
        :returns: TODO

        """
        self._dlog("handling while")
        while node.cond is None or self._handle_node(node.cond, scope, ctxt, stream):
            if node.stmt is not None:
                try:
                    self._handle_node(node.stmt, scope, ctxt, stream)
                except errors.InterpBreak as e:
                    break
                except errors.InterpContinue as e:
                    pass

    def _handle_do_while(self, node, scope, ctxt, stream):
        """Handle break node

        :node: TODO
        :scope: TODO
        :ctxt: TODO
        :stream: TODO
        :returns: TODO

        """
        self._dlog("handling do while")

        while True:
            if node.stmt is not None:
                try:
                    self._handle_node(node.stmt, scope, ctxt, stream)
                except errors.InterpBreak as e:
                    break
                except errors.InterpContinue as e:
                    pass
            if node.cond is not None and not self._handle_node(node.cond, scope, ctxt, stream):
                break

    def _flatten_list(self, l):
        for el in l:
            if isinstance(el, list) and not isinstance(el, AST.Node):
                for sub in self._flatten_list(el):
                    yield sub
            else:
                yield el

    def _handle_switch(self, node, scope, ctxt, stream):
        """Handle break node

        :node: TODO
        :scope: TODO
        :ctxt: TODO
        :stream: TODO
        :returns: TODO

        """
        def exec_case(idx, cases):
            # keep executing cases until a break is found,
            # or they've all been executed
            for case in cases[idx:]:
                stmts = case.stmts
                try:
                    for stmt in stmts:
                        self._handle_node(stmt, scope, ctxt, stream)
                except errors.InterpBreak as e:
                    break

        def get_stmts(stmts, res=None):
            if res is None:
                res = []

            stmts = self._flatten_list(stmts)
            for stmt in stmts:
                if isinstance(stmt, tuple):
                    stmt = stmt[1]

                res.append(stmt)

                if stmt.__class__ in [AST.Case, AST.Default]:
                    get_stmts(stmt.stmts, res)

            return res

        def get_cases(nodes, acc=None):
            cases = []

            stmts = get_stmts(nodes)
            for stmt in stmts:
                if stmt.__class__ in [AST.Case, AST.Default]:
                    cases.append(stmt)
                    stmt.stmts = []
                else:
                    cases[-1].stmts.append(stmt)

            return cases

        cond = self._handle_node(node.cond, scope, ctxt, stream)
    
        default_idx = None
        found_match = False

        cases = getattr(node, "pfp_cases", None)
        if cases is None:
            cases = get_cases(node.stmt.children())
            node.pfp_cases = cases

        for idx,child in enumerate(cases):
            if child.__class__ == AST.Default:
                default_idx = idx
                continue
            elif child.__class__ == AST.Case:
                expr = self._handle_node(child.expr, scope, ctxt, stream)
                if expr == cond:
                    found_match = True
                    exec_case(idx, cases)
                    break

        if default_idx is not None and not found_match:
            exec_case(default_idx, cases)

    def _handle_break(self, node, scope, ctxt, stream):
        """Handle break node

        :node: TODO
        :scope: TODO
        :ctxt: TODO
        :stream: TODO
        :returns: TODO

        """
        self._dlog("handling break")
        raise errors.InterpBreak()
    
    def _handle_continue(self, node, scope, ctxt, stream):
        """Handle continue node

        :node: TODO
        :scope: TODO
        :ctxt: TODO
        :stream: TODO
        :returns: TODO

        """
        self._dlog("handling continue")
        raise errors.InterpContinue()
    
    def _handle_decl_list(self, node, scope, ctxt, stream):
        """Handle For nodes

        :node: TODO
        :scope: TODO
        :ctxt: TODO
        :stream: TODO
        :returns: TODO

        """
        self._dlog("handling decl list")
        # just handle each declaration
        for decl in node.decls:
            self._handle_node(decl, scope, ctxt, stream)
    
    # -----------------------------
    # UTILITY
    # -----------------------------

    def _mark_id_as_lazy(self, node):
        curr = node
        while curr is not None and curr.__class__ is not AST.ID:
            if getattr(curr, "type", None) is not None:
                curr = curr.type
            else:
                curr = None
                break
        if curr is not None:
            curr.is_lazy = True

    def _node_is_breakable(self, node):
        if not self._int3:
            return False

        breakable_classes = [
            AST.FileAST,
            AST.Decl,
            #AST.ByRefDecl,
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
            #AST.ExprList,
            #AST.Compound,
            AST.Return,
            AST.ArrayDecl,
            AST.Continue,
            AST.Break,
            AST.Switch,
            AST.Case,
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
    
    def _resolve_to_field_class(self, names, scope):
        """Resolve the names to a class in fields.py, resolving past
        typedefs, etc

        :names: TODO
        :scope: TODO
        :ctxt: TODO
        :returns: TODO

        """
        switch = {
            "char":        "Char",
            "int":        "Int",
            "long":     "Int",
            "uint64":    "UInt64",
            "short":    "Short",
            "double":    "Double",
            "float":    "Float",
            "void":        "Void",
            "string":    "String",
            "wstring":    "WString"
        }

        core = names[-1]
        
        if core not in switch:
            # will return a list of resolved names
            type_info = scope.get_type(core)
            if type(type_info) is type and issubclass(type_info, fields.Field):
                return type_info
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
