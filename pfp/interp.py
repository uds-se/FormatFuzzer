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
import platform

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


class UnionDecls(Decls):
    pass


class StructDecls(Decls):
    pass


def StructDeclWithParams(scope, struct_cls, struct_args):
    def _pfp__init(self, stream):
        for param in self._pfp__node.args.params:
            param.is_func_param = True

        params = self._pfp__interp._handle_node(
            self._pfp__node.args, scope, self, None
        )
        param_list = params.instantiate(scope, struct_args, self._pfp__interp)

        if hasattr(super(self.__class__, self), "_pfp__init"):
            super(self.__class__, self)._pfp__init(stream)

    new_class = type(
        struct_cls.__name__ + "_", (struct_cls,), {"_pfp__init": _pfp__init}
    )
    return new_class


def StructUnionTypeRef(curr_scope, typedef_name, refd_name, interp, node):
    """Create a typedef that resolves itself dynamically. This is needed in
    situations like:

    .. code-block:: c

        struct MY_STRUCT {
            char magic[4];
            unsigned int filesize;
        };
        typedef struct MY_STRUCT ME;
        LittleEndian();
        ME s;

    The typedef ``ME`` is handled before the ``MY_STRUCT`` declaration actually
    occurs. The typedef value for ``ME`` should not the empty struct that is
    resolved, but should be a dynamically-looked up struct definition when
    a ``ME`` instance is actually declared.
    """
    if isinstance(node, AST.Struct):
        cls = fields.Struct
    elif isinstance(node, AST.Union):
        cls = fields.Union

    def __new__(cls_, *args, **kwargs):
        refd_type = curr_scope.get_type(refd_name)
        if refd_type is None:
            refd_node = node
        else:
            refd_node = refd_type._pfp__node

        def merged_init(self, stream):
            if six.PY3:
                cls_._pfp__init(self, stream)
            else:
                cls_._pfp__init.__func__(self, stream)
            self._pfp__init_orig(stream)

        overrides = {}
        if hasattr(cls_, "_pfp__init"):
            overrides["_pfp__init"] = merged_init

        res = base_cls = StructUnionDef(
            typedef_name, interp, refd_node, overrides=overrides,
        )
        return res(*args, **kwargs)

    new_class = type(
        typedef_name,
        (cls,),
        {
            "__new__": __new__,
        },
    )
    return new_class


def StructUnionDef(typedef_name, interp, node, overrides=None, cls=None):
    if overrides is None:
        overrides = {}
    if isinstance(node, AST.Struct):
        if cls is None:
            cls = fields.Struct
        decls = StructDecls(node.decls, node.coord)
    elif isinstance(node, AST.Union):
        if cls is None:
            cls = fields.Union
        decls = UnionDecls(node.decls, node.coord)

    # this is so that we can have all nested structs added to
    # the root DOM, even if there's an error in parsing the data.
    # If we didn't do this, any errors parsing the data would cause
    # the new struct to not be added to its parent, and the user would
    # not be able to see how far the script got
    def __init__(self, stream=None, metadata_processor=None, do_init=True):
        cls.__init__(
            self,
            stream,
            metadata_processor=metadata_processor,
        )

        if do_init:
            self._pfp__init(stream)

    def _pfp__init(self, stream):
        self._pfp__interp._handle_node(decls, ctxt=self, stream=stream)

    cls_members = {
        "__init__": __init__,
        "_pfp__init": _pfp__init,
        "_pfp__node": node,
        "_pfp__interp": interp,
    }

    for k, v in six.iteritems(overrides or {}):
        if k in cls_members:
            cls_members[k + "_orig"] = cls_members[k]
        cls_members[k] = v

    new_class = type(
        typedef_name,
        (cls,),
        cls_members,
    )
    return new_class


def EnumDef(typedef_name, base_cls, enum_vals):
    new_class = type(
        typedef_name,
        (fields.Enum,),
        {
            "signed": base_cls.signed,
            "width": base_cls.width,
            "endian": base_cls.endian,
            "format": base_cls.format,
            "enum_vals": enum_vals,
            "enum_cls": base_cls,
        },
    )
    return new_class


def ArrayDecl(item_cls, item_count):
    width = fields.PYVAL(item_count)
    if item_count is None:
        width = 1

    def __init__(self, stream=None, metadata_processor=None):
        fields.Array.__init__(
            self,
            self.width,
            self.field_cls,
            stream,
            metadata_processor=metadata_processor,
        )

    new_class = type(
        "Array_{}_{}".format(item_cls.__name__, width),
        (fields.Array,),
        {"__init__": __init__, "width": width, "field_cls": item_cls},
    )
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

    new_class = type(
        lookup_name + "_lazy",
        (fields.Field,),
        {
            "__init__": __init__,
            "_pfp__scope": scope,
            "_pfp__lazy_name": lookup_name,
        },
    )
    return new_class


# class StructUnionDef(object):
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

        self._log.debug(
            "\n".join(
                prefix + ": " + "  " * self._indent + line
                for line in msg.split("\n")
            )
        )

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
            for type_name, type_cls in six.iteritems(scope_ctxt["types"]):
                if isinstance(type_cls, list):
                    type_cls = self._interp._resolve_to_field_class(
                        type_cls, self._scope
                    )
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
            new_scope = {"types": {}, "vars": {}, "meta": {}}
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
    
    def clear_meta(self):
        """Clear metadata about the current statement
        """
        self._curr_scope["meta"] = {}
    
    def push_meta(self, meta_name, meta_value):
        """Push metadata about the current statement onto the metadata stack
        for the current statement. Mostly used for tracking integer promotion
        and casting types
        """
        self._dlog("adding metadata '{}'".format(meta_name))
        self._curr_scope["meta"].setdefault(meta_name, []).append(meta_value)

    def get_meta(self, meta_name):
        """Get the current meta value named ``meta_name``
        """
        self._dlog("getting metadata '{}'".format(meta_name))
        return self._curr_scope["meta"].get(meta_name, [None])[-1]

    def pop_meta(self, name):
        """Pop metadata about the current statement from the metadata stack
        for the current statement.

        :name: The name of the metadata
        """
        self._dlog("getting meta '{}'".format(name))
        return self._curr_scope["meta"][name].pop()

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

    def add_refd_struct_or_union(self, name, refd_name, interp, node):
        """Add a lazily-looked up typedef struct or union

        :name: name of the typedefd struct/union
        :node: the typedef node
        :interp: the 010 interpreter
        """
        self.add_type_class(name, StructUnionTypeRef(self, name, refd_name, interp, node))

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
    _cpp = []
    _functions_cpp = []
    _read_funcs = set()
    _fstat_funcs = set()
    _generates_cpp = ""
    _known_values = {}
    _defined = {"time" : None}
    _declared = set()
    _to_define = {}
    _to_replace = []
    _is_substructunion = False
    _call_stack = [False]


    def add_decl(self, classname, classnode, node, is_union):
        if node.name not in self._defined:
            self._defined[node.name] = classname
            self._globals.append((node.name, classname + " " + node.name + "(" + classname + "_" + node.name + "_instances);\n"))
            self._instances += "std::vector<" + classname + "*> " + classname + "_" + node.name + "_instances;\n"
        if classname in self._defined:
            name = node.name
            if hasattr(node, "originalname"):
                name = node.originalname
            node.cpp = "GENERATE"
            if len(self._call_stack) > 1 and not self._call_stack[-1]:
                node.cpp += "_VAR"
            self._variable_types[node.name] = classname
            node.cpp += "(" + name + ", ::g->" + node.name + ".generate("
            arg_num = 0
            if hasattr(node.type, "args") and node.type.args:
                for arg in node.type.args.exprs:
                    arg_num += 1
                    node.cpp += arg.cpp + ", "
            if hasattr(classnode, "args") and classnode.args is not None:
                for i in range(arg_num, len(classnode.args.params)):
                    arg_num += 1
                    node.cpp += classnode.args.params[i].name + ", "
            if arg_num > 0:
                node.cpp = node.cpp[:-2]
            node.cpp += "))"
            node.type.cpp = classname
        else:
            if classname not in self._to_define:
                self._to_define[classname] = []
            is_var = len(self._call_stack) > 1 and not self._call_stack[-1]
            self._to_define[classname].append((node.name, node, is_var))

            name = node.name
            if hasattr(node, "originalname"):
                name = node.originalname
            node.cpp = "GENERATE"
            if is_var:
                node.cpp += "_VAR"
            self._variable_types[node.name] = classname
            node.cpp += "(" + name + ", ::g->" + node.name + ".generate("
            arg_num = 0
            if hasattr(node.type, "args") and node.type.args:
                for arg in node.type.args.exprs:
                    arg_num += 1
                    node.cpp += arg.cpp + ", "
            if arg_num > 0:
                node.cpp = node.cpp[:-2]
            node.cpp += "/*TODO class " + classname + "*/"
            node.cpp += "))"

            node.type.cpp = classname
            if not self._incomplete:
                self.add_class(classname, classnode, is_union)
                self.add_class_generate(classname, classnode, is_union)
            elif classname not in self._declared:
                self._declared.add(classname)
                self._cpp.append((classname, "\nclass " + classname + ";\n\n"))

    def add_string_class(self, classname):
        if classname not in self._defined:
            self._defined[classname] = None
            cpp = "\n\nclass " + classname + " {\n"
            cpp += "\tstd::vector<std::string> known_values;\n"
            cpp += "\tstd::string value;\n"
            cpp += "public:\n"
            cpp += "\tint64 _startof = 0;\n"
            cpp += "\tstd::size_t _sizeof = 0;\n"
            cpp += "\tstd::string operator () () { return value; }\n"
            cpp += "\t" + classname + "(std::vector<std::string> known_values = {}) : known_values(known_values) {}\n"
            cpp += "\n\tstd::string generate() {\n"
            cpp += "\t\t_startof = FTell();\n"
            cpp += "\t\tif (known_values.empty()) {\n"
            cpp += "\t\t\tvalue = file_acc.file_string();\n"
            cpp += "\t\t} else {\n"
            cpp += "\t\t\tvalue = file_acc.file_string(known_values);\n"
            cpp += "\t\t}\n"
            cpp += "\t\t_sizeof = value.length() + 1;\n"
            cpp += "\t\treturn value;\n"
            cpp += "\t}\n};\n\n"
            self._cpp.append((classname, cpp))

    def add_native_class(self, classname, classtype, is_bitfield=False):
        if classname not in self._defined:
            self._defined[classname] = None
            cpp = "\n\nclass " + classname + " {\n"
            cpp += "\tint small;\n"
            cpp += "\tstd::vector<" + classtype + "> known_values;\n"
            cpp += "\t" + classtype + " value;\n"
            cpp += "public:\n"
            if not is_bitfield:
                cpp += "\tint64 _startof = 0;\n"
                cpp += "\tstd::size_t _sizeof = sizeof(" + classtype + ");\n"
            cpp += "\t" + classtype + " operator () () { return value; }\n"
            cpp += "\t" + classname + "(int small, std::vector<" + classtype + "> known_values = {}) : small(small), known_values(known_values) {}\n"
            if is_bitfield:
                cpp += "\n\t" + classtype + " generate(unsigned bits) {\n"
                cpp += "\t\tif (!bits)\n"
                cpp += "\t\t\treturn 0;\n"
            else:
                cpp += "\n\t" + classtype + " generate() {\n"
            if not is_bitfield:
                cpp += "\t\t_startof = FTell();\n"
            cpp += "\t\tif (known_values.empty()) {\n"
            if is_bitfield:
                cpp += "\t\t\tvalue = file_acc.file_integer(sizeof(" + classtype + "), bits, small);\n"
            else:
                cpp += "\t\t\tvalue = file_acc.file_integer(sizeof(" + classtype + "), 0, small);\n"
            cpp += "\t\t} else {\n"
            if is_bitfield:
                cpp += "\t\t\tvalue = file_acc.file_integer(sizeof(" + classtype + "), bits, known_values);\n"
            else:
                cpp += "\t\t\tvalue = file_acc.file_integer(sizeof(" + classtype + "), 0, known_values);\n"
            cpp += "\t\t}\n"
            cpp += "\t\treturn value;\n"
            cpp += "\t}\n"
            if is_bitfield:
                cpp += "\n\t" + classtype + " generate(unsigned bits, std::vector<" + classtype + "> possible_values) {\n"
                cpp += "\t\tif (!bits)\n"
                cpp += "\t\t\treturn 0;\n"
            else:
                cpp += "\n\t" + classtype + " generate(std::vector<" + classtype + "> possible_values) {\n"
            if not is_bitfield:
                cpp += "\t\t_startof = FTell();\n"
            if is_bitfield:
                cpp += "\t\tvalue = file_acc.file_integer(sizeof(" + classtype + "), bits, possible_values);\n"
            else:
                cpp += "\t\tvalue = file_acc.file_integer(sizeof(" + classtype + "), 0, possible_values);\n"
            cpp += "\t\treturn value;\n"
            cpp += "\t}\n"
            cpp += "};\n\n"
            self._cpp.append((classname, cpp))

    def get_decls(self, node):
        decls = []
        if isinstance(node, AST.Decl):
            return [node]
        elif isinstance(node, list):
            for child in node:
                decls += self.get_decls(child)
            return decls
        elif isinstance(node, AST.Compound):
            return self.get_decls(node.block_items)
        elif isinstance(node, AST.Switch):
            if hasattr(node, "pfp_cases"):
                decls += self.get_decls(node.pfp_cases)
            else:
                decls += self.get_decls(node.stmt)
            return decls
        elif isinstance(node, AST.Case):
            decls += self.get_decls(node.stmts)
            return decls
        elif isinstance(node, AST.Default):
            decls += self.get_decls(node.stmts)
            return decls
        elif isinstance(node, AST.If):
            decls += self.get_decls(node.iftrue)
            decls += self.get_decls(node.iffalse)
            return decls
        elif isinstance(node, AST.While):
            decls += self.get_decls(node.stmt)
            return decls
        elif isinstance(node, AST.DoWhile):
            decls += self.get_decls(node.stmt)
            return decls
        elif isinstance(node, AST.For):
            decls += self.get_decls(node.stmt)
            return decls
        elif node is None or node.__class__ in [AST.UnaryOp, AST.Break, AST.Continue, AST.FuncCall, AST.Return, AST.Assignment, AST.EmptyStatement]:
            return []
        raise errors.PfpError("unhandled get_decls " + str(node.__class__))


    def add_class(self, classname, classnode, is_union=False):
        if classname in self._defined:
            return
        self._defined[classname] = None
        self._struct_locals = []
        self._struct_vars = []
        self._struct_repeated = []
        cpp = "\n\nclass " + classname + " {\n"
        cpp += "\tstd::vector<" + classname + "*>& instances;\n\n"
        decls = []
        for node in classnode.decls:
            decls += self.get_decls(node)
        variables = []
        defined = set()
        for decl in decls:
            if "const" in decl.quals:
                continue
            name = decl.name
            if hasattr(decl, "originalname"):
                name = decl.originalname
            if "local" in decl.quals:
                self._struct_locals.append(decl)
            else:
                self._struct_vars.append(name)
            if "local" not in decl.quals:
                if name in defined:
                    sametype = True
                    for n,d in variables:
                        if n == name and d.type.cpp != decl.type.cpp:
                            sametype = False
                    if not sametype:
                        self._struct_repeated.append(name)
                else:
                    defined.add(name)
                    variables.append((name, decl))
                    if not hasattr(decl.type, "cpp"):
                        if hasattr(decl.type.type, "name"):
                            decl.type.cpp = decl.type.type.name
                        elif hasattr(decl.type.type, "names"):
                            decl.type.cpp = " ".join(decl.type.type.names)
        variables = [(n,d) for (n,d) in variables if n not in self._struct_repeated]

        if is_union:
            cpp += "// union {\n"
        for name, decl in variables:
            if hasattr(decl, "is_structunion"):
                cpp += "\t" + decl.type.cpp + "* " + name + "_var;\n"
            elif False and is_union and decl.type.cpp == "std::string" and decl.type.__class__ == AST.ArrayDecl:
                cpp += "\t" + " ".join(decl.type.type.type.names) + " " + name + "_var[" + decl.type.dim.cpp + "];\n"
            elif decl.bitsize is not None:
                if "/**/" in decl.bitsize.cpp:
                    cpp += "\t" + decl.type.cpp + " " + name + "_var;  //  : " + decl.bitsize.cpp.replace("/**/", "") + ";\n"
                else:
                    cpp += "\t" + decl.type.cpp + " " + name + "_var : " + decl.bitsize.cpp + ";\n"
            else:
                cpp += "\t" + decl.type.cpp + " " + name + "_var;\n"
        if is_union:
            cpp += "// };\n"
        cpp += "\npublic:\n"
        for name, decl in variables:
            cpp += "\tbool " + name + "_exists = false;\n"
        cpp += "\n"
        for name, decl in variables:
            if hasattr(decl, "is_structunion"):
                if decl.type.cpp in self._defined:
                    cpp += "\t" + decl.type.cpp + "& " + name + "() {\n\t\tassert_cond(" + name + "_exists, \"struct field " + name + " does not exist\");\n\t\treturn *" + name + "_var;\n\t}\n"
                else:
                    cpp += "\t" + decl.type.cpp + "& " + name + "();\n"
                    self._to_define[decl.type.cpp].append((decl.type.cpp + "& " + classname + "::" + name + "() {\n\tassert_cond(" + name + "_exists, \"struct field " + name + " does not exist\");\n\treturn *" + name + "_var;\n}\n", decl, False))
            elif False and is_union and decl.type.cpp == "std::string" and decl.type.__class__ == AST.ArrayDecl:
                cpp += "\tstd::string " + name + "() {\n\t\tassert_cond(" + name + "_exists, \"struct field " + name + " does not exist\");\n\t\treturn std::string(" + name + "_var, " + decl.type.dim.cpp + ");\n\t}\n"
            elif decl.bitsize is not None:
                cpp += "\t" + decl.type.cpp + " " + name + "() {\n\t\tassert_cond(" + name + "_exists, \"struct field " + name + " does not exist\");\n\t\treturn " + name + "_var;\n\t}\n"
            else:
                cpp += "\t" + decl.type.cpp + "& " + name + "() {\n\t\tassert_cond(" + name + "_exists, \"struct field " + name + " does not exist\");\n\t\treturn " + name + "_var;\n\t}\n"

        locals_cpp = ""
        for decl in decls:
            name = decl.name
            if hasattr(decl, "originalname"):
                name = decl.originalname
            if "local" in decl.quals and "const" not in decl.quals and name not in defined:
                defined.add(name)
                if not hasattr(decl.type, "cpp"):
                    if hasattr(decl.type.type, "name"):
                        decl.type.cpp = decl.type.type.name
                    elif hasattr(decl.type.type, "names"):
                        decl.type.cpp = " ".join(decl.type.type.names)
                locals_cpp += "\t" + decl.type.cpp.replace("&", "") + " " + name + ";\n"
        if locals_cpp:
            cpp += "\n\t/* locals */\n" + locals_cpp.replace("/*local*/ ", "")

        local_args = []
        for frame in self._locals_stack[1:]:
            for local in frame:
                if local.name in [l.name for l in self._struct_locals] + self._struct_vars:
                    continue
                if hasattr(classnode, "args") and classnode.args is not None and local.name in [p.name for p in classnode.args.params]:
                    continue
                used = False
                for decl in classnode.decls:
                    if hasattr(decl, "cpp") and "/**/" + local.name + "()" in decl.cpp:
                        used = True
                        break
                if used:
                    local_args.append(local)
        for local in local_args:
            if not hasattr(classnode, "args") or classnode.args is None:
                classnode.args = AST.ParamList([])
            classnode.args.params.append(local)
        cpp += "\n\tunsigned char generated = 0;\n"
        cpp += "\tstatic int _parent_id;\n"
        cpp += "\tstatic int _index_start;\n"
        cpp += "\tint64 _startof = 0;\n"
        cpp += "\tstd::size_t _sizeof = 0;\n"
        cpp += "\t" + classname + "& operator () () { return *instances.back(); }\n"
        cpp += "\t" + classname + "& operator [] (int index) {\n"
        cpp += "\t\tassert_cond((unsigned)(_index_start + index) < instances.size(), \"instance index out of bounds\");\n"
        cpp += "\t\treturn *instances[_index_start + index];\n"
        cpp += "\t}\n"
        cpp += "\tstd::size_t array_size() {\n"
        cpp += "\t\treturn instances.size() - _index_start;\n"
        cpp += "\t}\n"
        cpp += "\t" + classname + "(std::vector<" + classname + "*>& instances) : instances(instances) { instances.push_back(this); }\n"
        cpp += "\t~" + classname + "() {\n"
        cpp += "\t\tif (generated == 2)\n"
        cpp += "\t\t\treturn;\n"
        cpp += "\t\twhile (instances.size()) {\n"
        cpp += "\t\t\t" + classname + "* instance = instances.back();\n"
        cpp += "\t\t\tinstances.pop_back();\n"
        cpp += "\t\t\tif (instance->generated == 2)\n"
        cpp += "\t\t\t\tdelete instance;\n"
        cpp += "\t\t}\n"
        cpp += "\t}\n"
        cpp += "\t" + classname + "* generate("
        if hasattr(classnode, "args") and classnode.args is not None:
            for param in classnode.args.params:
                if hasattr(param.type.type, "names"):
                    names = param.type.type.names
                else:
                    names = param.type.type.type.names
                paramtype = ""
                for name in names:
                    if name == "string":
                        name = "std::string"
                    paramtype += name + " "
                if param.type.__class__ == AST.ArrayDecl:
                    if paramtype[:-1] in ["char", "uchar", "unsigned char", "CHAR", "UCHAR"]:
                        paramtype = "std::string "
                    else:
                        paramtype = "std::vector<" + paramtype[:-1] + ">& "
                param.type.cpp = paramtype[:-1]
                cpp += param.type.cpp
                if cpp[-1] != "&" and (not hasattr(param, "is_func_param") or not param.is_func_param):
                    cpp += "&"
                cpp += " " + param.name + ", "
            cpp = cpp[:-2]
        cpp += ");\n};\n\n"
        cpp += "int " + classname + "::_parent_id = 0;\n"
        cpp += "int " + classname + "::_index_start = 0;\n\n"
        self._cpp.append((classname, cpp))
        if classname in self._to_define:
            for field_name, node, is_var in self._to_define[classname]:
                if "::" in field_name:
                    self._cpp.append((classname + "_to_define", field_name))
                    continue

                arg_num = 0
                if hasattr(node.type, "args") and node.type.args:
                    arg_num = len(node.type.args.exprs)
                todoclass = ", " if arg_num else ""
                if hasattr(classnode, "args") and classnode.args is not None:
                    for i in range(arg_num, len(classnode.args.params)):
                        todoclass += classnode.args.params[i].name + ", "
                if todoclass:
                    todoclass = todoclass[:-2]
                todo = "/*TODO class " + classname + "*/"
                node.cpp = node.cpp.replace(todo, todoclass)
                for decl in classnode.decls:
                    decl.cpp = decl.cpp.replace(todo, todoclass)
                self._to_replace.append((todo, todoclass))

    def add_class_generate(self, classname, classnode, is_union=False):
        if classname + "::generate" in self._defined:
            return
        self._defined[classname + "::generate"] = None
        cpp = ""
        cpp += "\n" + classname + "* " + classname + "::generate("
        params = []
        if hasattr(classnode, "args") and classnode.args is not None:
            for param in classnode.args.params:
                params.append(param)
                if hasattr(param.type.type, "names"):
                    param.type.cpp = " ".join(param.type.type.names)
                    if param.type.cpp == "string":
                        param.type.cpp = "std::string"
                cpp += param.type.cpp
                if cpp[-1] != "&" and (not hasattr(param, "is_func_param") or not param.is_func_param):
                    cpp += "&"
                cpp += " " + param.name + ", "
            cpp = cpp[:-2]
        cpp += ") {\n"
        body = "\tif (generated == 1) {\n"
        body += "\t\t" + classname + "* new_instance = new " + classname + "(instances);\n"
        body += "\t\tnew_instance->generated = 2;\n"
        body += "\t\treturn new_instance->generate("
        if hasattr(classnode, "args") and classnode.args is not None:
            for param in classnode.args.params:
                body += param.name + ", "
            body = body[:-2]
        body += ");\n"
        body += "\t}\n"
        body += "\tif (!generated)\n"
        body += "\t\tgenerated = 1;\n"
        body += "\t_startof = FTell();\n"
        body += "\tif (_parent_id != ::g->_struct_id && !global_indexing_of_arrays) {\n"
        body += "\t\t_index_start = instances.size() - 1;\n"
        body += "\t}\n"
        body += "\t_parent_id = ::g->_struct_id;\n"
        body += "\t::g->_struct_id = ++::g->_struct_id_counter;\n\n"
        first = True
        for decl in classnode.decls:
            for local in self._struct_locals + params:
                decl.cpp = decl.cpp.replace("/**/" + local.name + "()", local.name)
            for var in self._struct_vars:
                decl.cpp = decl.cpp.replace("/**/" + var + "()", var + "()")
            if is_union and not first:
                decl.cpp = decl.cpp.replace("GENERATE_VAR", "GENERATE_EXISTS")
            for n in self._struct_repeated:
                decl.cpp = decl.cpp.replace("GENERATE_VAR(" + n + ",", "GENERATE(" + n + ",")
            if decl.cpp:
                body += "\t" + decl.cpp.replace("\n", "\n\t") + ";\n"
            first = False
        if "break;" in body and (classname[-7:] == "_struct" or not ("switch (" in body or "do {" in body or "while (" in body or "for (" in body)):
            body = "do {\n" + body + "} while (false);\n"
        cpp += body
        cpp += "\n\t::g->_struct_id = _parent_id;\n"
        cpp += "\t_sizeof = FTell() - _startof;\n"
        cpp += "\treturn this;\n"
        cpp += "}\n\n"
        self._generates_cpp += cpp

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

        natives[name] = functions.NativeFunction(name, func, ret, send_interp)

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

        glob_pattern = os.path.join(
            os.path.dirname(__file__), "native", "*.py"
        )
        for filename in glob.glob(glob_pattern):
            basename = os.path.basename(filename).replace(".py", "")
            if basename == "__init__":
                continue

            try:
                mod_base = __import__(
                    "pfp.native", globals(), locals(), fromlist=[basename]
                )
            except Exception as e:
                sys.stderr.write(
                    "cannot import native module {} at '{}'".format(
                        basename, filename
                    )
                )
                raise e
                continue

            mod = getattr(mod_base, basename)
            setattr(mod, "PYVAL", fields.get_value)
            setattr(mod, "PYSTR", fields.get_str)

    def __init__(self, debug=False, parser=None, int3=True, generate=True):
        """Create a new instance of the ``PfpInterp`` class.

        :param bool debug: if debug output should be used (default=``False``)
        :param :any:`py010parser.c_parser.CParser` parser: The ``py010parser.c_parser.CParser`` to use (default=``None``)
        :param bool int3: If debug breakpoints (calls to :any:`pfp.native.dbg.int3` ``Int3()``) are active (default=``True``)
        """
        sys.setrecursionlimit(100000)
        self._generate = generate
        self._global_locals = []
        self._global_consts = []
        self._globals = []
        self._variable_types = {}
        self._integer_ranges = [("1", "16")]
        self._instances = ""
        self._locals_stack = [[]]
        self._incomplete_stack = [False]
        self._incomplete = False
        self._structs = set()
        self.__class__.define_natives()

        self._log = DebugLogger(debug)
        # TODO nested debuggers aren't currently allowed
        self._debugger = None
        # why is this here?? this isn't used at all
        self._debug = debug
        self._printf = True
        self._break_type = self.BREAK_NONE
        self._break_level = 0
        self._no_debug = False
        self._padded_bitfield = True
        # TODO does this default change based on the endianness?
        self._bitfield_direction = self.BITFIELD_DIR_DEFAULT
        # whether or not debugging is allowed (ie Int3())
        self._int3 = int3
        self._ast_frozen = False

        self._ctxt = None
        self._scope = None
        self._coord = None
        self._orig_filename = None

        if parser is None:
            parser = py010parser.c_parser.CParser()
        # this speeds things up a bit
        self._parser = parser

        self._node_switch = {
            AST.FileAST: self._handle_file_ast,
            AST.Decl: self._handle_decl,
            AST.TypeDecl: self._handle_type_decl,
            AST.ByRefDecl: self._handle_byref_decl,
            AST.Struct: self._handle_struct,
            AST.Union: self._handle_union,
            AST.StructRef: self._handle_struct_ref,
            AST.IdentifierType: self._handle_identifier_type,
            AST.Typedef: self._handle_typedef,
            AST.Constant: self._handle_constant,
            AST.BinaryOp: self._handle_binary_op,
            AST.Assignment: self._handle_assignment,
            AST.ID: self._handle_id,
            AST.UnaryOp: self._handle_unary_op,
            AST.FuncDef: self._handle_func_def,
            AST.FuncCall: self._handle_func_call,
            AST.FuncDecl: self._handle_func_decl,
            AST.ParamList: self._handle_param_list,
            AST.ExprList: self._handle_expr_list,
            AST.Compound: self._handle_compound,
            AST.Return: self._handle_return,
            AST.ArrayDecl: self._handle_array_decl,
            AST.InitList: self._handle_init_list,
            AST.If: self._handle_if,
            AST.For: self._handle_for,
            AST.While: self._handle_while,
            AST.DeclList: self._handle_decl_list,
            AST.Break: self._handle_break,
            AST.Continue: self._handle_continue,
            AST.ArrayRef: self._handle_array_ref,
            AST.Enum: self._handle_enum,
            AST.Switch: self._handle_switch,
            AST.Cast: self._handle_cast,
            AST.Typename: self._handle_typename,
            AST.EmptyStatement: self._handle_empty_statement,
            AST.DoWhile: self._handle_do_while,
            AST.StructCallTypeDecl: self._handle_struct_call_type_decl,
            AST.TernaryOp: self._handle_if,
            StructDecls: self._handle_struct_decls,
            UnionDecls: self._handle_union_decls,
        }

    def _dlog(self, msg, indent_increase=0):
        """log the message to the log"""
        self._log.debug(
            "interp",
            msg,
            indent_increase,
            filename=self._orig_filename,
            coord=self._coord,
        )

    # --------------------
    # PUBLIC
    # --------------------

    def load_template(self, template):
        """Load a template and all required predefines into this interpreter.
        Future calls to ``parse`` will not require the template to be parsed.
        """
        self._template = template
        self._template_lines = self._template.split("\n")
        self._ast = self._parse_string(template, predefines=True)
        self._dlog("parsed template into ast")
        self._ast_frozen = True

    def parse(
        self,
        stream,
        template=None,
        predefines=True,
        orig_filename=None,
        keep_successful=False,
        printf=True,
    ):
        """Parse the data stream using the template (e.g. parse the 010 template
        and interpret the template using the stream as the data source).

        :stream: The input data stream
        :template: The template to parse the stream with
        :keep_successful: Return whatever was successfully parsed before an error. ``_pfp__error`` will contain the exception (if one was raised)
        :param bool printf: If ``False``, printfs will be noops (default=``True``)
        :returns: Pfp Dom

        """
        self._dlog("parsing")

        if not isinstance(stream, bitwrap.BitwrappedStream):
            stream = bitwrap.BitwrappedStream(stream)

        if template is None and not self._ast_frozen:
            raise errors.InterpError("A template must be provided")

        self._printf = printf
        self._orig_filename = orig_filename
        self._stream = stream

        if not self._ast_frozen:
            self._template = template
            self._template_lines = self._template.split("\n")
            self._ast = self._parse_string(template, predefines)
            self._dlog("parsed template into ast")

        res = self._run(keep_successful)
        res._pfp__finalize()
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
                res = self._handle_node(
                    child, self._scope, self._ctxt, self._stream,
                )
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

        lines = [
            (x, self._template_lines[x])
            for x in six.moves.range(start, end, 1)
        ]
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

    # On Macs, need to invoke cpp with -xc++ to remove // comments
    # (This should actually be fixed in py010parser -- AZ)
    CPP_ARGS = None

    def set_cpp_args(self):
        if platform.system() == "Darwin":
            self.CPP_ARGS = "-xc++"
        else:
            self.CPP_ARGS = ""

    def _parse_string(self, string, predefines=True):
        if self.CPP_ARGS is None:
            self.set_cpp_args()
        exts = []
        if predefines:
            for idx, predefine in enumerate(self._predefines):
                try:
                    ast = py010parser.parse_string(
                        predefine,
                        parser=self._parser,
                        cpp_args=self.CPP_ARGS,
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
            cpp_args=self.CPP_ARGS,
            # only keep the scopes if we ran the predefines
            keep_scopes=predefines,
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
                    self._orig_filename, self._coord.line
                )
                six.reraise(
                    errors.PfpError,
                    errors.PfpError(
                        exc_obj.__class__.__name__
                        + ": "
                        + exc_obj.args[0]
                        + more_info
                        if len(exc_obj.args) > 0
                        else more_info
                    ),
                    traceback,
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
        elif type(node) is list and len(
            list(filter(lambda x: isinstance(x, AST.Node), node))
        ) == len(node):
            node = AST.Compound(block_items=node, coord=node[0].coord)
            return self._handle_node(node, scope, ctxt, stream)

        # need to check this so that debugger-eval'd statements
        # don't mess with the current state
        if not self._no_debug:
            self._coord = node.coord

        self._dlog(
            "handling node type {}, line {}".format(
                node.__class__.__name__,
                node.coord.line if node.coord is not None else "?",
            )
        )
        self._log.inc()

        breakable = self._node_is_breakable(node)

        if (
            breakable
            and not self._no_debug
            and self._break_type != self.BREAK_NONE
        ):
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
            raise errors.UnsupportedASTNode(
                node.coord, node.__class__.__name__
            )

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
        node.cpp = "#include <cstdlib>\n#include <cstdio>\n#include <string>\n#include <vector>\n#include <unordered_map>\n#include \"bt.h\"\n"
        self._root = ctxt = fields.Dom(stream)
        ctxt._pfp__scope = scope
        self._root._pfp__name = "__root"
        self._root._pfp__interp = self
        self._dlog(
            "handling file AST with {} children".format(len(node.children()))
        )

        children = list(node.children())

        # one pass to define all functions. Functions may only live at the
        # top-level (functions may not be nested or contained within structs,
        # if/else statements, or other code block types). aka hoisting
        for child in children:
            if type(child) is tuple:
                child = child[1]
            if not isinstance(child, (AST.FuncDef, AST.Typedef)) \
                    and not  is_forward_declared_struct(child):
                continue
            self._handle_node(child, scope, ctxt, stream)
            if child.cpp:
                node.cpp += child.cpp + ";\n"
            scope.clear_meta()

        node.cpp1 = ""
        for child in children:
            if type(child) is tuple:
                child = child[1]
            if isinstance(child, (AST.FuncDef, AST.Typedef)) or \
                    is_forward_declared_struct(child):
                continue
            self._handle_node(child, scope, ctxt, stream)
            for decl in self.get_decls(child):
                if "local" in decl.quals and "const" not in decl.quals and hasattr(decl.type, "cpp") and decl.name not in self._global_locals:
                    cpp = decl.type.cpp + " " + decl.name + ";\n"
                    self._globals.append((decl.name, cpp))
                    self._global_locals.append(decl.name)
            if child.cpp:
                node.cpp1 += "\t" + child.cpp.replace("\n", "\n\t") + ";\n"

        for n, c in self._cpp:
            #node.cpp += "/*" + n + "*/\n"
            node.cpp += c
        readfunctions = [["byte", "Byte"],
                         ["ubyte", "UByte"],
                         ["short", "Short"],
                         ["ushort", "UShort"],
                         ["int", "Int"],
                         ["uint", "UInt"],
                         ["int64", "Quad"],
                         ["uint64", "UQuad"],
                         ["int64", "Int64"],
                         ["uint64", "UInt64"],
                         ["hfloat", "HFloat"],
                         ["float", "Float"],
                         ["double", "Double"],
                         ["std::string", "Bytes"]]
        lookahead = []
        for t, n in readfunctions:
            node.cpp += "std::vector<" + t + "> Read" + n + "InitValues"
            if "Read" + n + "InitValues" in self._known_values:
                node.cpp += " = { " + ", ".join(self._known_values["Read" + n + "InitValues"]) + " }"
            elif "Read" + n in self._known_values:
                node.cpp += " = { " + ", ".join(self._known_values["Read" + n]) + " }"
            node.cpp += ";\n"
            if "Read" + n in self._read_funcs:
                lookahead.append("Read" + n)
        node.cpp += "\n\n" + self._instances
        node.cpp += "\n\nstd::unordered_map<std::string, std::string> variable_types = { "
        for var in self._variable_types:
            node.cpp += '{ "' + var + '", "' + self._variable_types[var] + '" }, '
        if self._variable_types:
            node.cpp = node.cpp[:-2]
        node.cpp += " };"
        node.cpp += "\n\nstd::vector<std::vector<int>> integer_ranges = { "
        for (a, b) in self._integer_ranges:
            node.cpp += '{ ' + a + ', ' + b + ' }, '
        node.cpp = node.cpp[:-2] + " };"
        node.cpp += "\n\nclass globals_class {\npublic:\n\tint _struct_id = 0;\n\tint _struct_id_counter = 0;\n"
        for n, c in self._globals:
            #node.cpp += "/*" + n + "*/\n"
            if c:
                node.cpp += "\t" + re.sub(r"\(.*\)", "", c)
        node.cpp += "\n\n\tglobals_class() :\n"
        for n, c in self._globals:
            index = c.find(" " + n + "(") + 1
            if index > 0:
                node.cpp += "\t\t" + c[index:-2] + ",\n"
        node.cpp = node.cpp[:-2] + "\n"
        node.cpp += "\t{}\n"
        node.cpp += "};\n\n"
        node.cpp += "globals_class* g;\n\n"
        for n, c in self._functions_cpp:
            #node.cpp += "/*" + n + "*/\n"
            node.cpp += c
        node.cpp += self._generates_cpp
        node.cpp += "\n\nvoid generate_file() {\n"
        node.cpp += "\t::g = new globals_class();\n\n"
        node.cpp += node.cpp1
        node.cpp += "\n\tfile_acc.finish();\n"
        node.cpp += "\tdelete_globals();\n"
        node.cpp += "}\n"
        node.cpp += "\nvoid delete_globals() { delete ::g; }\n"

        for a, b in self._to_replace:
            node.cpp = node.cpp.replace(a, b)
        for local in self._global_locals:
            node.cpp = node.cpp.replace("/**/" + local + "()", "::g->" + local)
        for n, c in self._globals:
            node.cpp = node.cpp.replace("/**/" + n + "()", "::g->" + n + "()")
        for local in self._global_consts:
            node.cpp = node.cpp.replace("/**/" + local + "()", local)
        node.cpp = node.cpp.replace("/**/", "")

        outfile = open(sys.argv[2], "w")
        print(node.cpp, file=outfile)
        outfile.close()
        if self._generate:
            print("Finished creating cpp generator.")
            if lookahead:
                print("\nLookahead functions found:\n")
            for f in lookahead:
                print(f)
            if self._known_values:
                print("\nMined interesting values:\n")
            for var in sorted(self._known_values):
                print(var + ":", self._known_values[var])
            if self._fstat_funcs:
                print("\nFile stat functions found:\n")
            for f in self._fstat_funcs:
                print(f)
            print()
            sys.exit(0)

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
        node.cpp = ""
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

        scope.push_meta("dest_type", to_type)
        val_to_cast = self._handle_node(node.expr, scope, ctxt, stream)
        try:
            scope.pop_meta("dest_type")
        except:
            pass

        res = to_type()

        if val_to_cast is not None:
            res._pfp__set_value(val_to_cast)
        node.cpp = "(" + " ".join(node.to_type.type.type.names) + ")" + node.expr.cpp
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
            #print("decl:metadata")
            # metadata_info = self._handle_metadata(node, scope, ctxt, stream)
            def process_metadata():
                metadata_info = self._handle_metadata(
                    node, scope, ctxt, stream
                )
                return metadata_info

            metadata_processor = process_metadata

        if not node.name and node.bitsize:
            node.name = "_".join(node.type.type.names) + "_bitfield_padding"
        field_name = self._get_node_name(node)
        #print("handling decl")
        #print(field_name)
        field = self._handle_node(node.type, scope, ctxt, stream)
        bitsize = None
        bitfield_rw = None

        if getattr(node, "bitsize", None) is not None:
            #print("decl:bitsize")
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
                if (
                    isinstance(prev, fields.NumberBase)
                    and
                    (
                        (
                            self._padded_bitfield
                            and prev.__class__.width == field.width
                        )
                        or not self._padded_bitfield
                    )
                    and prev.bitsize is not None
                    and prev.bitfield_rw.reserve_bits(bitsize, stream)
                ):
                    bitfield_rw = prev.bitfield_rw

            # either because there was no previous bitfield, or the previous was full
            if bitfield_rw is None:
                bitfield_rw = fields.BitfieldRW(self, field)
                bitfield_rw.reserve_bits(bitsize, stream)

        if is_forward_declared_struct(node):
            #print("decl:forward")
            node.cpp = ""
            scope.add_type_class(node.type.name, field)

        elif getattr(node, "is_func_param", False):
            #print("decl:func_param")
            # we want to keep this as a class and not instantiate it
            # instantiation will be done in functions.ParamListDef.instantiate
            field = (field_name, field)

        # locals and consts still get a field instance, but DON'T parse the
        # stream!
        elif "local" in node.quals or "const" in node.quals:
            if field_name.endswith("InitValues"):
                node.cpp = ""
                if node.init is not None:
                    self._handle_node(node.init, scope, ctxt, stream)
                    values = []
                    for expr in node.init.exprs:
                        values.append(expr.cpp)
                    self._known_values[field_name] = values
                else:
                    self._known_values[field_name] = []
                return
            #print("decl:local/const")
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
                    if val is not None:
                        field._pfp__set_value(val)

            field.is_local = True
            node.type.cpp = ""
            if "local" in node.quals:
                self._locals_stack[-1].append(node)
                node.type.cpp += "/*local*/ "
            if "const" in node.quals:
                field._pfp__freeze()
                node.type.cpp += "const "

            in_struct = "local" in node.quals and not self._call_stack[-1] and "const" not in node.quals
            field._pfp__interp = self
            if isinstance(node.type, AST.ArrayDecl):
                classname = " ".join(node.type.type.type.names)
                if classname == "string":
                    classname = "std::string"
                is_char_array = False
                if classname in ["char", "uchar", "unsigned char", "CHAR", "UCHAR"]:
                    is_char_array = True
                    node.type.cpp += "std::string"
                else:
                    classtype = classname
                    if classname == "long":
                        classtype = "LONG"
                    if classname == "ulong":
                        classtype = "ULONG"
                    if classname == "unsigned long":
                        classtype = "ULONG"
                    node.type.cpp += "std::vector<" + classtype + ">"

                if in_struct:
                    node.cpp = "/**/" + node.name + "()"
                else:
                    node.cpp = node.type.cpp + " " + node.name
                if node.init is None and node.type.dim.cpp != "0":
                    if in_struct:
                        node.cpp += ".resize(" + node.type.dim.cpp + ")"
                    else:
                        if is_char_array:
                            node.cpp += "(" + node.type.dim.cpp + ", 0)"
                        else:
                            node.cpp += "(" + node.type.dim.cpp + ")"
                elif is_char_array and node.init is not None and not hasattr(node.init, "exprs"):
                    node.cpp += " = " + node.init.cpp
                else:
                    node.cpp += " = { "
                    if node.init is not None:
                        for expr in node.init.exprs:
                            node.cpp += expr.cpp + ", "
                        node.cpp = node.cpp[:-2]
                    node.cpp += " }"
                    if "const" in node.quals:
                        self._global_consts.append(node.name)
                        self._cpp.append((node.name, node.cpp + ";"))
                        node.cpp = ""
            else:
                names = node.type.type.names
                for name in names:
                    if name == "string":
                        name = "std::string"
                    if name == "long":
                        name = "LONG"
                    node.type.cpp += name + " "
                node.type.cpp = node.type.cpp[:-1]
                if in_struct:
                    node.cpp = "/**/" + node.name + "()"
                else:
                    node.cpp = node.type.cpp + " " + node.name
                if node.name in ["true", "false"]:
                    node.cpp = ""
                elif node.init is not None:
                    if "const" in node.quals:
                        node.cpp += " = " + node.init.cpp + ";\n"
                        self._global_consts.append(node.name)
                        if node.name not in ["CHECKSUM_BYTE", "CHECKSUM_SHORT_LE", "CHECKSUM_SHORT_BE", "CHECKSUM_INT_LE", "CHECKSUM_INT_BE", "CHECKSUM_INT64_LE", "CHECKSUM_INT64_BE", "CHECKSUM_SUM8", "CHECKSUM_SUM16", "CHECKSUM_SUM32", "CHECKSUM_SUM64", "CHECKSUM_CRC16", "CHECKSUM_CRCCCITT", "CHECKSUM_CRC32", "CHECKSUM_ADLER32", "CHECKSUM_MD2", "CHECKSUM_MD4", "CHECKSUM_MD5", "CHECKSUM_RIPEMD160", "CHECKSUM_SHA1", "CHECKSUM_SHA256", "CHECKSUM_SHA384", "CHECKSUM_SHA512", "CHECKSUM_TIGER", "CHECKSUM_CRC8", "FINDMETHOD_NORMAL", "FINDMETHOD_WILDCARDS", "FINDMETHOD_REGEX", "cBlack", "cRed", "cDkRed", "cLtRed", "cGreen", "cDkGreen", "cLtGreen", "cBlue", "cDkBlue", "cLtBlue", "cPurple", "cDkPurple", "cLtPurple", "cAqua", "cDkAqua", "cLtAqua", "cYellow", "cDkYellow", "cLtYellow", "cDkGray", "cGray", "cSilver", "cLtGray", "cWhite", "cNone", "True", "TRUE", "False", "FALSE"]:
                            self._cpp.append((node.name, node.cpp))
                        node.cpp = ""
                    else:
                        node.cpp += " = " + node.init.cpp
                elif in_struct:
                    node.cpp = ""

        elif isinstance(field, functions.Function):
            #print("decl:function")
            # eh, just add it as a local...
            # maybe the whole local/vars thinking needs to change...
            # and we should only have ONE map TODO
            field.name = field_name
            scope.add_local(field_name, field)
            node.cpp = field_name + "()"

        elif field_name is not None:
            #print("decl:field")
            added_child = False

            # by this point, structs are already instantiated (they need to be
            # in order to set the new context)
            if not isinstance(field, fields.Field):
                if issubclass(field, fields.NumberBase):
                    #print("decl:NumberBase")
                    # use the default bitfield direction
                    if self._bitfield_direction is self.BITFIELD_DIR_DEFAULT:
                        bitfield_left_right = (
                            True
                            if field.endian == fields.BIG_ENDIAN
                            else False
                        )
                    else:
                        bitfield_left_right = (
                            self._bitfield_direction
                            is self.BITFIELD_DIR_LEFT_RIGHT
                        )

                    field = field(
                        stream,
                        bitsize=bitsize,
                        metadata_processor=metadata_processor,
                        bitfield_rw=bitfield_rw,
                        bitfield_padded=self._padded_bitfield,
                        bitfield_left_right=bitfield_left_right,
                    )

                # TODO
                # for now if there's a struct inside of a union that is being
                # parsed when there's an error, the user will lose information
                # about how far the parsing got. Here we are explicitly checking for
                # adding structs and unions to a parent union.
                elif (
                    (
                        issubclass(field, fields.Struct)
                        or issubclass(field, fields.Union)
                    )
                    and not isinstance(ctxt, fields.Union)
                    and hasattr(field, "_pfp__init")
                ):
                    #print("decl:substructunion")

                    # this is so that we can have all nested structs added to
                    # the root DOM, even if there's an error in parsing the data.
                    # If we didn't do this, any errors parsing the data would cause
                    # the new struct to not be added to its parent, and the user would
                    # not be able to see how far the script got
                    field = field(
                        stream,
                        metadata_processor=metadata_processor,
                        do_init=False,
                    )
                    field._pfp__interp = self
                    field_res = ctxt._pfp__add_child(field_name, field, stream)

                    # when adding a new field to a struct/union/fileast, add it to the
                    # root of the ctxt's scope so that it doesn't get lost by being declared
                    # from within a function
                    scope.add_var(field_name, field_res, root=True)

                    field_res._pfp__interp = self
                    #self._is_substructunion = True
                    field._pfp__init(stream)
                    self._is_substructunion = False
                    added_child = True
                else:
                    #print("decl:fieldfield")
                    field = field(
                        stream, metadata_processor=metadata_processor
                    )

            if not added_child:
                #print("decl:not added_child")
                field._pfp__interp = self
                field_res = ctxt._pfp__add_child(field_name, field, stream)
                field_res._pfp__interp = self
                #field_res._pfp__scope = scope
                #print(field_res)

                # when adding a new field to a struct/union/fileast, add it to the
                # root of the ctxt's scope so that it doesn't get lost by being declared
                # from within a function
                scope.add_var(field_name, field_res, root=True)

                # this shouldn't be used elsewhere, but should still be explicit with
                # this flag
                added_child = True

            if isinstance(node.type, AST.ArrayDecl):
                if hasattr(node.type.type.type, "name"):
                    classname = node.type.type.type.name
                else:
                    classname = " ".join(node.type.type.type.names)
                nodetype = scope.get_type(classname)
                if classname == field_name + "_struct" and ctxt._pfp__node.name is not None:
                    classname = ctxt._pfp__node.name + "_" + field_name + "_struct"
                if classname == field_name + "_union" and ctxt._pfp__node.name is not None:
                    classname = ctxt._pfp__node.name + "_" + field_name + "_union"
                if not hasattr(node, "originalname"):
                    node.originalname = node.name
                while node.name in self._defined and self._defined[node.name] != classname.replace(" ", "_") + "_array_class":
                    node.name += "_"
                is_char_array = False
                is_string = False
                classtype = classname
                if classname in ["char", "uchar", "unsigned char", "CHAR", "UCHAR"]:#, "byte", "ubyte", "BYTE", "UBYTE"]:
                    node.type.cpp = "std::string"
                    is_char_array = True
                else:
                    if classname == "long":
                        classtype = "LONG"
                    if classname == "ulong":
                        classtype = "ULONG"
                    if classname == "unsigned long":
                        classtype = "ULONG"
                    node.type.cpp = "std::vector<" + classtype + ">"
                if classname == "string":
                    classname = "std::string"
                    is_string = True

                element_classname = classname

                is_pointer = ""
                is_native = False
                if nodetype is None or isinstance(nodetype, list):
                    element_classname = classname.replace(" ", "_") + "_class"
                    if is_string:
                        self.add_string_class(element_classname)
                    else:
                        self.add_native_class(element_classname, classtype)
                    is_native = True
                elif issubclass(nodetype, fields.Enum) or issubclass(nodetype, fields.Union):
                    pass
                else:
                    node.type.cpp = "std::vector<" + classname + "*>"
                    is_pointer = "*"
                    if hasattr(nodetype, "_pfp__node"):
                        classnode = nodetype._pfp__node
                    else:
                        classnode = field.items[0]._pfp__node
                    is_union = classnode.__class__ == AST.Union
                    if classname not in self._defined and not self._incomplete:
                        self.add_class(classname, classnode, is_union)

                if node.name + "_element" not in self._defined:
                    self._defined[node.name + "_element"] = classname.replace(" ", "_") + "_class"
                    if is_native:
                        self._globals.append((node.name + "_element", element_classname + " " + node.name + "_element(false);\n"))
                    else:
                        self._globals.append((node.name + "_element", element_classname + " " + node.name + "_element" + "(" + element_classname + "_" + node.name + "_element_instances);\n"))
                        self._instances += "std::vector<" + element_classname + "*> " + element_classname + "_" + node.name + "_element_instances;\n"

                cpp = ""
                if classname.replace(" ", "_") + "_array_class" not in self._defined:
                    self._defined[classname.replace(" ", "_") + "_array_class"] = None
                    cpp += "\n\nclass " + classname.replace(" ", "_") + "_array_class {\n"
                    cpp += "\t" + element_classname + "& " + "element;\n"
                    if is_char_array:
                        cpp += "\tstd::vector<std::string> known_values;\n"
                    if is_native:
                        cpp += "\tstd::unordered_map<int, std::vector<" + classtype + ">> element_known_values;\n"
                    cpp += "\t" + node.type.cpp + " " + "value;\n"
                    cpp += "public:\n"
                    cpp += "\tint64 _startof = 0;\n"
                    cpp += "\tstd::size_t _sizeof = 0;\n"
                    cpp += "\t" + node.type.cpp + "& operator () () { return value; }\n"
                    cpp += "\t" + classtype + " operator [] (int index) {\n"
                    cpp += "\t\tassert_cond((unsigned)index < value.size(), \"array index out of bounds\");\n"
                    cpp += "\t\treturn " + is_pointer + "value[index];\n"
                    cpp += "\t}\n"
                    if is_native:
                        cpp += "\t" + classname.replace(" ", "_") + "_array_class(" + element_classname + "& element, std::unordered_map<int, std::vector<" + classtype + ">> element_known_values = {})\n\t\t: element(element), element_known_values(element_known_values) {}\n"
                    else:
                        cpp += "\t" + classname.replace(" ", "_") + "_array_class(" + element_classname + "& element) : element(element) {}\n"
                    if is_char_array:
                        cpp += "\t" + classname.replace(" ", "_") + "_array_class(" + element_classname + "& element, std::vector<std::string> known_values)\n\t\t: element(element), known_values(known_values) {}\n"
                        cpp += "\n\t" + node.type.cpp + " generate(unsigned size, std::vector<std::string> possible_values = {}) {\n"
                    else:
                        cpp += "\n\t" + node.type.cpp + " generate(unsigned size) {\n"
                    cpp += "\t\tcheck_array_length(size);\n"
                    cpp += "\t\t_startof = FTell();\n"
                    if is_char_array:
                        cpp += "\t\tvalue = \"\";\n"
                        cpp += "\t\tif (possible_values.size()) {\n"
                        cpp += "\t\t\tvalue = file_acc.file_string(possible_values);\n"
                        cpp += "\t\t\tassert(value.length() == size);\n"
                        cpp += "\t\t\t_sizeof = size;\n"
                        cpp += "\t\t\treturn value;\n"
                        cpp += "\t\t}\n"
                        cpp += "\t\tif (known_values.size()) {\n"
                        cpp += "\t\t\tvalue = file_acc.file_string(known_values);\n"
                        cpp += "\t\t\tassert(value.length() == size);\n"
                        cpp += "\t\t\t_sizeof = size;\n"
                        cpp += "\t\t\treturn value;\n"
                        cpp += "\t\t}\n"
                        if classname in ["char", "uchar", "unsigned char", "CHAR", "UCHAR"]:
                            cpp += "\t\tif (!element_known_values.size()) {\n"
                            cpp += "\t\t\tif (size == 0)\n"
                            cpp += "\t\t\t\t return \"\";\n"
                            cpp += "\t\t\tvalue = file_acc.file_string(size);\n"
                            cpp += "\t\t\t_sizeof = size;\n"
                            cpp += "\t\t\treturn value;\n"
                            cpp += "\t\t}\n"
                    else:
                        cpp += "\t\tvalue = {};\n"
                    cpp += "\t\tfor (unsigned i = 0; i < size; ++i) {\n"
                    if is_native:
                        cpp += "\t\t\tauto known = element_known_values.find(i);\n"
                        cpp += "\t\t\tif (known == element_known_values.end()) {\n"
                        cpp += "\t\t\t\tvalue.push_back(element.generate());\n"
                        cpp += "\t\t\t\t_sizeof += element._sizeof;\n"
                        cpp += "\t\t\t} else {\n"
                        cpp += "\t\t\t\tvalue.push_back(file_acc.file_integer(sizeof(" + classtype + "), 0, known->second));\n"
                        cpp += "\t\t\t\t_sizeof += sizeof(" + classtype + ");\n"
                        cpp += "\t\t\t}\n"
                    else:
                        cpp += "\t\t\tvalue.push_back(element.generate());\n"
                        cpp += "\t\t\t_sizeof += element._sizeof;\n"
                    cpp += "\t\t}\n"
                    cpp += "\t\treturn value;\n"
                    cpp += "\t}\n};\n\n"
                nodecpp = ""
                if node.name not in self._defined:
                    self._defined[node.name] = classname.replace(" ", "_") + "_array_class"
                    nodecpp = classname.replace(" ", "_") + "_array_class " + node.name + "(" + node.name + "_element"
                    nodecpp += ");\n"
                if nodetype is None or isinstance(nodetype, list) or issubclass(nodetype, fields.Enum) or issubclass(nodetype, fields.Union):
                    self._cpp.append((classname.replace(" ", "_") + "_array_class", cpp))
                    self._globals.append((node.name, nodecpp))
                else:
                    self._globals.append((node.name, nodecpp))
                    if classname in self._defined:
                        self._cpp.append((classname.replace(" ", "_") + "_array_class", cpp))
                        self.add_class_generate(classname, classnode, is_union)
                    else:
                        if classname not in self._to_define:
                            self._to_define[classname] = []
                        self._to_define[classname].append((cpp, node, False))
                        if classname not in self._declared:
                            self._declared.add(classname)
                            self._cpp.append((classname, "\nclass " + classname + ";\n\n"))

                node.cpp = "GENERATE"
                if len(self._call_stack) > 1 and not self._call_stack[-1]:
                    node.cpp += "_VAR"
                self._variable_types[node.name] = classname.replace(" ", "_") + "_array_class"
                node.cpp += "(" + node.originalname + ", ::g->" + node.name + ".generate("
                if node.type.dim is not None:
                    node.cpp += node.type.dim.cpp
                if node.init is not None:
                    val = self._handle_node(node.init, scope, ctxt, stream)
                    node.cpp += ", { "
                    for expr in node.init.exprs:
                        node.cpp += expr.cpp + ", "
                    node.cpp = node.cpp[:-2]
                    node.cpp += " }"
                node.cpp += "))"
            elif isinstance(node.type.type, AST.Enum):
                classname = " ".join(node.type.type.names)
                #node.originalname = node.name
                while node.name in self._defined and self._defined[node.name] != classname:
                    node.name += "_"
                self._defined[node.name] = classname
                node.cpp = "GENERATE"
                if len(self._call_stack) > 1 and not self._call_stack[-1]:
                    node.cpp += "_VAR"
                self._variable_types[node.name] = classname
                node.cpp += "(" + node.name + ", " + classname + "_generate("
                if node.init is not None:
                    self._handle_node(node.init, scope, ctxt, stream)
                    node.cpp += "{ "
                    for expr in node.init.exprs:
                        node.cpp += expr.cpp + ", "
                    node.cpp = node.cpp[:-2]
                    node.cpp += " }"
                node.cpp += "))"
                node.type.cpp = " ".join(node.type.type.type.names)
                if classname not in self._defined:
                    self._defined[classname] = None
                    cpp = "\nenum "
                    if node.type.type.name is None:
                        cpp += classname
                    else:
                        cpp += node.type.type.name
                    cpp += " : " + " ".join(node.type.type.type.names) + " {\n"
                    for enumerator in node.type.type.values.enumerators:
                        cpp += "\t" + enumerator.name
                        if enumerator.value is not None:
                            cpp += " = " + enumerator.value.value
                        cpp += ",\n"
                    cpp += "};\n"
                    self._cpp.append((classname, cpp))
                if classname + "_generate" not in self._defined:
                    self._defined[classname + "_generate"] = None
                    cpp = "\n" + classname + " " + classname + "_generate() {\n\treturn (" + classname + ") file_acc.file_integer(sizeof(" + " ".join(node.type.type.type.names) + "), 0, " + classname + "_values);\n}\n"
                    cpp += "\n" + classname + " " + classname + "_generate(std::vector<" + " ".join(node.type.type.type.names) + "> known_values) {\n\treturn (" + classname + ") file_acc.file_integer(sizeof(" + " ".join(node.type.type.type.names) + "), 0, known_values);\n}\n"
                    self._cpp.append((classname + "_generate", cpp))
            elif isinstance(node.type.type, AST.Union) or isinstance(node.type.type, AST.Struct):
                if hasattr(node.type.type, "name"):
                    classname = node.type.type.name
                else:
                    classname = " ".join(node.type.type.names)
                if classname == field_name + "_struct" and hasattr(ctxt, "_pfp__node") and ctxt._pfp__node.name is not None:
                    classname = ctxt._pfp__node.name + "_" + field_name + "_struct"
                if classname == field_name + "_union" and hasattr(ctxt, "_pfp__node") and ctxt._pfp__node.name is not None:
                    classname = ctxt._pfp__node.name + "_" + field_name + "_union"
                classnode = field._pfp__node
                if not hasattr(node, "originalname"):
                    node.originalname = node.name
                while node.name in self._defined and self._defined[node.name] != classname:
                    node.name += "_"
                is_union = isinstance(node.type.type, AST.Union)
                node.is_structunion = True
                self.add_decl(classname, classnode, node, is_union)
            else:
                if hasattr(node.type.type, "name"):
                    classname = node.type.type.name
                else:
                    classname = " ".join(node.type.type.names)
                nodetype = scope.get_type(classname)
                if nodetype is None or isinstance(nodetype, list):
                    is_bitfield = node.bitsize is not None
                    if is_bitfield:
                        classname = "_".join(node.type.type.names) + "_bitfield"
                    else:
                        classname = "_".join(node.type.type.names) + "_class"
                    if not hasattr(node, "originalname"):
                        node.originalname = node.name
                    while node.name in self._defined and self._defined[node.name] != classname:
                        node.name += "_"
                    node.type.cpp = " ".join(node.type.type.names)
                    if node.type.cpp == "long":
                        node.type.cpp = "LONG"
                    if node.type.cpp == "ulong":
                        node.type.cpp = "ULONG"
                    if node.type.cpp == "unsigned long":
                        node.type.cpp = "ULONG"
                    if node.type.cpp == "time_t":
                        node.type.cpp = "uint32"
                    is_string = False
                    if node.type.cpp == "string":
                        node.type.cpp = "std::string"
                        self.add_string_class(classname)
                        is_string = True
                    else:
                        self.add_native_class(classname, node.type.cpp, is_bitfield)
                    if node.name not in self._defined:
                        self._defined[node.name] = classname
                        if is_string:
                            self._globals.append((node.name, classname + " " + node.name + ";\n"))
                        elif node.metadata is not None and "arraylength" in node.metadata.keyvals:
                            self._globals.append((node.name, classname + " " + node.name + "(2);\n"))
                        elif node.metadata is not None and "max" in node.metadata.keyvals:
                            maxint = node.metadata.keyvals["max"].split(",")[0]
                            minint = "0"
                            if "min" in node.metadata.keyvals:
                                minint = node.metadata.keyvals["min"].split(",")[0]
                            else:
                                assert(int(maxint) >= 0)
                            self._integer_ranges.append((minint, maxint))
                            self._globals.append((node.name, classname + " " + node.name + "(" + str(len(self._integer_ranges)+1) + ");\n"))
                        elif node.metadata is not None and "min" in node.metadata.keyvals:
                            maxint = "INT_MAX"
                            minint = node.metadata.keyvals["min"].split(",")[0]
                            self._integer_ranges.append((minint, maxint))
                            self._globals.append((node.name, classname + " " + node.name + "(" + str(len(self._integer_ranges)+1) + ");\n"))
                        else:
                            self._globals.append((node.name, classname + " " + node.name + "(1);\n"))
                    node.cpp = "GENERATE"
                    if len(self._call_stack) > 1 and not self._call_stack[-1]:
                        node.cpp += "_VAR"
                    self._variable_types[node.name] = classname
                    node.cpp += "(" + node.originalname + ", ::g->" + node.name + ".generate("
                    if is_bitfield:
                        node.cpp += node.bitsize.cpp
                    if node.init is not None:
                        if is_bitfield:
                            node.cpp += ", "
                        val = self._handle_node(node.init, scope, ctxt, stream)
                        node.cpp += "{ "
                        for expr in node.init.exprs:
                            node.cpp += expr.cpp + ", "
                        node.cpp = node.cpp[:-2]
                        node.cpp += " }"
                    if node.metadata is not None and "values" in node.metadata.keyvals:
                        if is_bitfield:
                            node.cpp += ", "
                        node.cpp += "/**/" + node.metadata.keyvals["values"].split(",")[0] + "()"
                    node.cpp += "))"
                elif issubclass(nodetype, fields.Enum):
                    node.cpp = "GENERATE"
                    if len(self._call_stack) > 1 and not self._call_stack[-1]:
                        node.cpp += "_VAR"
                    self._variable_types[node.name] = classname
                    node.cpp += "(" + node.name + ", " + classname + "_generate("
                    if node.init is not None:
                        self._handle_node(node.init, scope, ctxt, stream)
                        node.cpp += "{ "
                        for expr in node.init.exprs:
                            node.cpp += expr.cpp + ", "
                        node.cpp = node.cpp[:-2]
                        node.cpp += " }"
                    node.cpp += "))"
                    node.type.cpp = nodetype.typename
                    if node.bitsize is not None:
                        node.type.cpp = " ".join(node.type.type.names)
                    if classname + "_generate" not in self._defined:
                        self._defined[classname + "_generate"] = None
                        cpp = "\n" + classname + " " + classname + "_generate() {\n\treturn (" + classname + ") file_acc.file_integer(sizeof(" + nodetype.typename + "), 0, " + classname + "_values);\n}\n"
                        cpp += "\n" + classname + " " + classname + "_generate(std::vector<" + nodetype.typename + "> known_values) {\n\treturn (" + classname + ") file_acc.file_integer(sizeof(" + nodetype.typename + "), 0, known_values);\n}\n"
                        self._cpp.append((classname + "_generate", cpp))
                else:
                    if hasattr(nodetype, "_pfp__node"):
                        classnode = nodetype._pfp__node
                    else:
                        classnode = field._pfp__node
                    if not hasattr(node, "originalname"):
                        node.originalname = node.name
                    while node.name in self._defined and self._defined[node.name] != classname:
                        node.name += "_"
                    is_union = issubclass(nodetype, fields.Union)
                    node.is_structunion = True
                    self.add_decl(classname, classnode, node, is_union)

        # enums will get here. If there is no name, then no
        # field is being declared (but the enum values _will_
        # get defined). E.g.:
        #     enum <uchar blah {
        #         BLAH1,
        #        BLAH2,
        #        BLAH3
        #     };
        elif field_name is None:
            #print("decl:none")
            node.cpp = ""
            pass

        #print("handled decl")
        #print(field_name)
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

        # char blah[60] <pack=Zip, unpack=Unzip, packtype=DataType>;
        # char blah[60] <packer=Zip, packtype=DataType>;
        # int checksum <watch=field1,field2,field3, update=Crc32>;

    def _handle_watch_metadata(self, node, scope, ctxt, stream):
        """Handle watch vars for fields
        """
        keyvals = node.metadata.keyvals
        if "watch" not in keyvals:
            raise errors.PfpError(
                "Packed fields require a packer function set"
            )
        if "update" not in keyvals:
            raise errors.PfpError(
                "Packed fields require a packer function set"
            )

        watch_field_name = keyvals["watch"]
        update_func_name = keyvals["update"]

        watch_fields = list(
            map(lambda x: self.eval(x.strip()), watch_field_name.split(";"))
        )
        update_func = scope.get_id(update_func_name)

        return {
            "type": "watch",
            "watch_fields": watch_fields,
            "update_func": update_func,
            "func_call_info": (ctxt, scope, stream, self, self._coord),
        }

    def _handle_packed_metadata(self, node, scope, ctxt, stream):
        """Handle packed metadata
        """
        keyvals = node.metadata.keyvals
        if "packer" not in keyvals and (
            "pack" not in keyvals or "unpack" not in keyvals
        ):
            raise errors.PfpError(
                "Packed fields require a packer function to be set or pack and unpack functions to be set"
            )
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
        if self._generate and node.type.__class__ is AST.Enum and node.type.name is None:
            node.type.names = [node.declname + "_enum"]
        if self._generate and node.type.__class__ is AST.Struct and node.type.name is None:
            node.type.name = node.declname + "_struct"
        if self._generate and node.type.__class__ is AST.Union and node.type.name is None:
            node.type.name = node.declname + "_union"
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

        node.cpp = node.name.cpp + "." + node.field.name + "()"

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
                if self._generate:
                    return None
                raise

        if "is_local" in vars(sub_field) and sub_field.is_local:
            node.cpp = node.cpp[:-2]

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
        for decl in node.decls:
            decl.type.cpp = "/* TODO union decl*/"
        self._locals_stack.append([])
        self._call_stack.append(False)
        if node.decls[0] in self._structs:
            self._incomplete_stack.append(True)
        else:
            self._structs.add(node.decls[0])
            self._incomplete_stack.append(False)

        # new scope
        scope = ctxt._pfp__scope = Scope(self._log, parent=scope)

        try:
            max_pos = 0
            for decl in node.decls:
                try:
                    self._handle_node(decl, scope, ctxt, stream)
                except errors.InterpReturn as e:
                    if not self._generate:
                        raise e
                scope.clear_meta()

        finally:
            # the union will have reset the stream
            stream.seek(stream.tell() + ctxt._pfp__width(), 0)
            self._scope = scope._parent
            self._locals_stack.pop()
            self._call_stack.pop()
            self._incomplete = self._incomplete_stack.pop()

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
        node.cpp = "{"
        for _, init_child in node.children():
            init_field = self._handle_node(init_child, scope, ctxt, stream)
            res.append(init_field)
            node.cpp += init_child.cpp + ", "
        if res:
            node.cpp = node.cpp[:-2]
        node.cpp += "}"
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

        if node.decls is not None:
            struct_cls = StructUnionDef("struct", self, node)
            if node.name is not None:
                scope.add_type_class(node.name, struct_cls)
            return struct_cls

        # it's declaring a struct field. E.g.
        #    struct IFD subDir;
        else:
            res = scope.get_type(node.name)
            if res is None:
                res = StructUnionDef(node.name, self, node)
            return res

    def _handle_struct_decls(self, node, scope, ctxt, stream):
        if not node.decls:
            return
        self._dlog("handling struct decls")
        self._locals_stack.append([])
        self._call_stack.append(False)
        if node.decls[0] in self._structs:
            self._incomplete_stack.append(True)
        else:
            self._structs.add(node.decls[0])
            self._incomplete_stack.append(False)

        # new scope
        if not self._is_substructunion:
            scope = ctxt._pfp__scope = Scope(self._log, parent=scope)
            self._scope = scope

        try:
            for decl in node.decls:
                # new context! (struct)
                try:
                    self._handle_node(decl, scope, ctxt, stream)
                except errors.InterpReturn as e:
                    if not self._generate:
                        raise e
                scope.clear_meta()

            ctxt._pfp__process_fields_metadata()

        # so that even if return statements/other exceptions
        # happen, we'll still pop scope
        finally:
            # need to pop the scope!
            if not self._is_substructunion:
                self._scope = scope._parent
            self._locals_stack.pop()
            self._call_stack.pop()
            self._incomplete = self._incomplete_stack.pop()

    def _handle_identifier_type(self, node, scope, ctxt, stream):
        """TODO: Docstring for _handle_identifier_type.

        :node: TODO
        :scope: TODO
        :ctxt: TODO
        :stream: TODO
        :returns: TODO

        """
        self._dlog("handling identifier")
        node.cpp = ""

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
        is_union_or_struct = node.type.type.__class__ in [
            AST.Union,
            AST.Struct,
        ]
        is_enum = node.type.type.__class__ is AST.Enum

        if is_union_or_struct:
            self._dlog("handling typedef struct/union '{}'".format(node.name))
            if node.type.type.name is None:
                scope.add_type_struct_or_union(node.name, self, node.type.type)
            else:
                scope.add_refd_struct_or_union(node.name, node.type.type.name, self, node.type.type)
            node.cpp = ""
        elif is_enum:
            enum_cls = self._handle_node(node.type, scope, ctxt, stream)
            scope.add_type_class(node.name, enum_cls)
            node.cpp = "\ntypedef enum "
            if node.type.type.name is None:
                name = " ".join(node.type.type.names)
            else:
                name = node.type.type.name
            node.cpp += name
            node.cpp += " " + node.name
            self._global_consts.append(node.name + "_values")
            enum_type = "int"
            if hasattr(node.type.type.type, "names"):
                enum_type = " ".join(node.type.type.type.names)
            cpp = "std::vector<" + enum_type + "> " + node.name + "_values = { "
            for enumerator in node.type.type.values.enumerators:
                cpp += enumerator.name + ", "
            cpp = cpp[:-2]
            cpp += " };\n"
            self._cpp.append((node.name, node.cpp + ";\n" + cpp))
            node.cpp = ""
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
            if node.name == 'wchar_t':
                node.cpp = ""
                return
            nodetype = ""
            for name in names:
                realnames = scope.get_type(name)
                if realnames:
                    for n in realnames:
                        nodetype += " " + n
                else:
                    nodetype += " " + name

            if nodetype == " long":
                nodetype = " LONG"
            if nodetype == " ulong":
                nodetype = " ULONG"
            if nodetype == " unsigned long":
                nodetype = " ULONG"
            node.cpp = "typedef" + nodetype + " " + node.name
        if node.name in ["UINT", "byte", "CHAR", "BYTE", "uchar", "ubyte", "UCHAR", "UBYTE", "int16", "SHORT", "INT16", "uint16", "ushort", "USHORT", "UINT16", "WORD", "int32", "INT", "INT32", "LONG", "uint", "uint32", "ulong", "UINT", "UINT32", "ULONG", "DWORD", "int64", "quad", "QUAD", "INT64", "__int64", "uint64", "uquad", "UQUAD", "UINT64", "QWORD", "__uint64", "FLOAT", "DOUBLE", "hfloat", "HFLOAT", "OLETIME", "time_t"]:
            node.cpp = ""

    def _str_to_int(self, string):
        """Check for the hex
        """
        string = string.lower()
        if string.endswith("l"):
            string = string[:-1]
        if string.lower().startswith("0x"):
            # should always match
            match = re.match(r"0[xX]([a-fA-F0-9]+)", string)
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
            "float": (
                lambda x: float(x.lower().replace("f", "")),
                fields.Float,
            ),
            "double": (float, fields.Double),
            # cut out the quotes
            "char": (lambda x: ord(utils.string_escape(x[1:-1])), fields.Char),
            # TODO should this be unicode?? will probably bite me later...
            # cut out the quotes
            "string": (
                lambda x: str(utils.string_escape(x[1:-1])),
                fields.String,
            ),
        }

        if node.type in switch:
            # return switch[node.type](node.value)
            conversion, field_cls = switch[node.type]
            val = conversion(node.value)
            node.cpp = node.value
            if node.type == "string" and '\0' in val:
                node.cpp = "std::string(" + node.value + ", {})".format(len(val))
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
            "+": lambda x, y: x + y,
            "-": lambda x, y: x - y,
            "*": lambda x, y: x * y,
            "/": lambda x, y: x / y,
            "|": lambda x, y: x | y,
            "^": lambda x, y: x ^ y,
            "&": lambda x, y: x & y,
            "%": lambda x, y: x % y,
            ">": lambda x, y: x > y,
            "<": lambda x, y: x < y,
            "||": lambda x, y: 1 if x or y else 0,
            ">=": lambda x, y: x >= y,
            "<=": lambda x, y: x <= y,
            "==": lambda x, y: x == y,
            "!=": lambda x, y: x != y,
            "&&": lambda x, y: 1 if x and y else 0,
            ">>": lambda x, y: x >> y,
            "<<": lambda x, y: x << y,
        }

        dest_type = scope.get_meta("dest_type")

        left_val = self._handle_node(node.left, scope, ctxt, stream)
        if dest_type is not None and left_val is not None and not isinstance(left_val, dest_type):
            new_left_val = dest_type()
            new_left_val._pfp__set_value(left_val)
            left_val = new_left_val

        # short circuit power!
        if node.op == "||" and left_val and not self._generate:
            res = 1
        else:
            right_val = self._handle_node(node.right, scope, ctxt, stream)
            if dest_type is not None and not isinstance(right_val, dest_type) and right_val is not None:
                new_right_val = dest_type()
                new_right_val._pfp__set_value(right_val)
                right_val = new_right_val

            if node.op not in switch:
                raise errors.UnsupportedBinaryOperator(node.coord, node.op)

            if node.op in ["==", "!="]:
                exp = None
                if node.right.__class__ == AST.Constant:
                    exp = node.left
                    const = node.right
                elif node.left.__class__ == AST.Constant:
                    exp = node.right
                    const = node.left
                
                if exp is not None and exp.__class__ == AST.ArrayRef and exp.subscript.__class__ == AST.Constant:
                    name = None
                    if exp.name.__class__ == AST.StructRef:
                        name = exp.name.field.name
                    elif exp.name.__class__ == AST.ID:
                        name = exp.name.name
                    if name is not None:
                        index = exp.subscript.value
                        value = const.cpp
                        if name not in self._known_values:
                            self._known_values[name] = {}
                        if index not in self._known_values[name]:
                            self._known_values[name][index] = []
                        self._known_values[name][index].append(value)
                        elemtype = self._variable_types[name].replace("_array_class", "")
                        cpp = "_element, (std::unordered_map<int, std::vector<" + elemtype + ">>) { "
                        for index in self._known_values[name]:
                            cpp += "{ " + index + ", {{"
                            for value in self._known_values[name][index]:
                                cpp += value + ", "
                            cpp = cpp[:-2]
                            cpp += "}} }, "
                        cpp = cpp[:-2]
                        cpp += " });"
                        for i, (n, c) in enumerate(self._globals):
                            if n == name:
                                self._globals[i] = (n, re.sub("_element.*", "###", c).replace("###", cpp))

                if exp is not None and exp.__class__ == AST.StructRef or exp.__class__ == AST.ID:
                    if exp.__class__ == AST.StructRef:
                        name = exp.field.name
                    else:
                        name = exp.name
                    value = const.cpp
                    if name in self._defined and not hasattr(scope.get_id(name), "is_local"):
                        if name not in self._known_values:
                            self._known_values[name] = []
                        self._known_values[name].append(value)
                        if len(set(self._known_values[name])) == 1:
                            self._known_values[name] = self._known_values[name][:1]
                        classname = self._defined[name]
                        if classname[-12:] == "_array_class":
                            cpp = "_element, { "
                            for value in self._known_values[name]:
                                cpp += value + ", "
                            cpp = cpp[:-2]
                            cpp += " });"
                            for i, (n, c) in enumerate(self._globals):
                                if n == name:
                                    self._globals[i] = (n, re.sub("_element.*", "###", c).replace("###", cpp))
                        else:
                            cpp = "(1, { "
                            for value in self._known_values[name]:
                                cpp += value + ", "
                            cpp = cpp[:-2]
                            cpp += " });"
                            for i, (n, c) in enumerate(self._globals):
                                if n == name:
                                    self._globals[i] = (n, re.sub(r"\(1.*", "###", c).replace("###", cpp))

                if exp is not None and exp.__class__ == AST.FuncCall:
                    name = exp.name.name
                    value = const.cpp
                    if name.startswith("Read"):
                        if name not in self._known_values:
                            self._known_values[name] = []
                        self._known_values[name].append(value)
                        if len(set(self._known_values[name])) == 1:
                            self._known_values[name] = self._known_values[name][:1]

            res = None
            try:
                res = switch[node.op](left_val, right_val)
            except:
                #print("* EXCEPTION IN BINARY OP " + str(left_val) + " " + node.op + " " + str(right_val) + ", in line " + str(node.coord.line))
                pass

        node.cpp = "(" + node.left.cpp + " " + node.op + " " + node.right.cpp + ")"

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
            "parentof": self._handle_parentof,
            "exists": self._handle_exists,
            "function_exists": self._handle_function_exists,
            "p++": self._handle_post_plus_plus,
            "p--": self._handle_post_minus_minus,
        }

        switch = {
            # for ++i and --i
            "++": lambda x, v: x.__iadd__(1),
            "--": lambda x, v: x.__isub__(1),
            "~": lambda x, v: ~x,
            "!": lambda x, v: not x,
            "-": lambda x, v: -x,
            "sizeof": lambda x, v: (fields.UInt64() + x._pfp__width()),
            "startof": lambda x, v: (fields.UInt64() + x._pfp__offset),
        }

        if node.op not in switch and node.op not in special_switch:
            raise errors.UnsupportedUnaryOperator(node.coord, node.op)


        if node.op in special_switch:
            result = special_switch[node.op](node, scope, ctxt, stream)
            return result

        field = self._handle_node(node.expr, scope, ctxt, stream)
        if node.op == "sizeof":
            if not hasattr(node.expr, "cpp") and issubclass(field, fields.IntBase):
                node.cpp = "{}".format(field.width)
            else:
                node.cpp = node.expr.cpp + "._sizeof"
        elif node.op == "startof":
            if node.expr.name == "this":
                node.cpp = "_startof"
            elif isinstance(node.expr.name, str):
                node.cpp = "::g->" + node.expr.name + "._startof"
            else:
                node.cpp = node.expr.cpp + "._startof"
        else:
            node.cpp = node.op + node.expr.cpp
        if type(field) is type:
            field = field()
        res = None
        try:
            res = switch[node.op](field, 1)
        except:
            pass
        if type(res) is bool:
            new_res = field.__class__()
            if type(new_res) == int:
                new_res = 1 if res == True else 0
            else:
                new_res._pfp__set_value(1 if res == True else 0)
            res = new_res
        return res

    def _handle_post_plus_plus(self, node, scope, ctxt, stream):
        field = self._handle_node(node.expr, scope, ctxt, stream)
        clone = field.__class__()
        clone._pfp__set_value(field)
        field += 1
        node.cpp = node.expr.cpp + "++"
        return clone

    def _handle_post_minus_minus(self, node, scope, ctxt, stream):
        field = self._handle_node(node.expr, scope, ctxt, stream)
        clone = field.__class__()
        clone._pfp__set_value(field)
        field -= 1
        node.cpp = node.expr.cpp + "--"
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
            a = self._handle_node(node.expr, scope, ctxt, stream)
            if a is not None:
                res._pfp__set_value(1)
            else:
                res._pfp__set_value(0)
        except AttributeError:
            res._pfp__set_value(0)

        if node.expr.__class__ == AST.StructRef:
            node.cpp = node.expr.name.cpp + "." + node.expr.field.name + "_exists"
        if node.expr.__class__ == AST.ArrayRef:
            if a._pfp__name in self._variable_types and "_array_class" not in self._variable_types[a._pfp__name]:
                node.cpp = "((unsigned long)" + node.expr.subscript.cpp + " < " + node.expr.name.cpp + ".array_size())"
            else:
                node.cpp = "((unsigned long)" + node.expr.subscript.cpp + " < " + node.expr.name.cpp + ".size())"

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
            if not self._generate:
                raise errors.UnresolvedID(node.coord, node.name)
        elif is_lazy:
            return LazyField(node.name, scope)

        if node.name in ["false", "true"]:
            node.cpp = node.name
        else:
            node.cpp = "/**/" + node.name + "()"
        return field

    def _handle_assignment(self, node, scope, ctxt, stream):
        """Handle assignment nodes

        :node: TODO
        :scope: TODO
        :ctxt: TODO
        :stream: TODO
        :returns: TODO
        """

        def add_op(x, y):
            x += y

        def sub_op(x, y):
            x -= y

        def div_op(x, y):
            x.__idiv__(y)

        def mod_op(x, y):
            x %= y

        def mul_op(x, y):
            x *= y

        def xor_op(x, y):
            x ^= y

        def and_op(x, y):
            x &= y

        def or_op(x, y):
            x |= y

        def lshift_op(x, y):
            x <<= y

        def rshift_op(x, y):
            x >>= y

        def assign_op(x, y):
            x._pfp__set_value(y)

        switch = {
            "+=": add_op,
            "-=": sub_op,
            "/=": div_op,
            "%=": mod_op,
            "*=": mul_op,
            "^=": xor_op,
            "&=": and_op,
            "|=": or_op,
            "<<=": lshift_op,
            ">>=": rshift_op,
            "=": assign_op,
        }

        scope.clear_meta()

        self._dlog("handling assignment")
        field = self._handle_node(node.lvalue, scope, ctxt, stream)
        self._dlog("field = {}".format(field))

        if type(field) is type:
            field = field()
        scope.push_meta("dest_type", field._pfp__get_class())

        value = self._handle_node(
            node.rvalue,
            scope,
            ctxt,
            stream,
        )

        if node.op is None:
            self._dlog("value = {}".format(value))
            field._pfp__set_value(value)
            node.cpp = node.lvalue.cpp + " = " + node.rvalue.cpp
        else:
            self._dlog("value {}= {}".format(node.op, value))
            if node.op not in switch:
                raise errors.UnsupportedAssignmentOperator(node.coord, node.op)
            try:
                if not hasattr(field, "width"):
                    switch[node.op](field, value)
            except:
                print("* EXCEPTION IN ASSIGNMENT " + str(field) + " " + node.op + " " + str(value) + ", in line " + str(node.coord.line))
                pass
            node.cpp = node.lvalue.cpp + " " + node.op + " " + node.rvalue.cpp
            if hasattr(field, "width") and hasattr(field, "implicit"):
                if node.op == "-=":
                    node.cpp = "VectorRemove(" + node.lvalue.cpp + ", { " + node.rvalue.cpp + " })"
                if node.op == "+=":
                    node.cpp = node.lvalue.cpp + ".insert(" + node.lvalue.cpp + ".end(), { " + node.rvalue.cpp + " })"
        return field

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
        node.cpp = ""
        func.node = node

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
            scope.clear_meta()
            func_args = self._handle_node(node.args, scope, ctxt, stream)
        func = self._handle_node(node.name, scope, ctxt, stream)
        if node.name.name.startswith("Read"):
            self._read_funcs.add(node.name.name)
        node.cpp = "" + node.name.name + "("
        if node.name.name in ["FEof", "FSeek", "FSkip", "FileSize"]:
            self._fstat_funcs.add(node.name.name)
        if node.name.name in ["Printf", "SPrintf", "Warning"]:
            is_sprintf = 1 if node.name.name == "SPrintf" else 0
            fmt = node.args.exprs[is_sprintf].cpp
            i = 0
            index = fmt.find("%")
            while index != -1:
                if fmt[index + 1] == "%":
                    index = fmt.find("%", index + 2)
                    continue
                i += 1
                if fmt[index + 1] == "s":
                    node.args.exprs[is_sprintf + i].cpp = "std::string(" + node.args.exprs[is_sprintf + i].cpp + ").c_str()"
                index = fmt.find("%", index + 2)
            if is_sprintf + i + 1 != len(node.args.exprs):
                print("Warning: wrong number of % formats in " + node.name.name)
        if node.args:
            node.cpp += ", ".join([arg.cpp for arg in node.args.exprs])
        node.cpp += ")"
        if node.name.name in ["SetEvilBit", "ChangeArrayLength", "EndChangeArrayLength", "GlobalIndexingOfArrays", "IsParsing", "FTellBits", "RSA_key_generate", "RSA_sign_SHA256", "EC_key_generate", "ECDSA_sign_SHA256"]:
            return
        self._locals_stack.append([])
        self._call_stack.append(True)
        ret = func.call(func_args, ctxt, scope, stream, self, node.coord)
        self._call_stack.pop()
        self._locals_stack.pop()
        if hasattr(func, "node") and func.node.cpp == "":
            for name in func.node.decl.type.type.type.names:
                if name == "string":
                    name = "std::string"
                func.node.cpp += name + " "
            func.node.cpp += func.name + "("
            params = []
            if func.node.decl.type.args:
                params = func.node.decl.type.args.params
                if not isinstance(params[0], AST.Decl):
                    params = []
            for param in params:
                if hasattr(param.type.type, "names"):
                    names = param.type.type.names
                else:
                    names = param.type.type.type.names
                paramtype = ""
                for name in names:
                    if name == "string":
                        name = "std::string"
                    paramtype += name + " "
                if param.type.__class__ == AST.ArrayDecl:
                    paramtype = "std::vector<" + paramtype[:-1] + ">& "
                if param.type.__class__ == AST.ByRefDecl:
                    paramtype = paramtype[:-1] + "& "
                func.node.cpp += paramtype
                func.node.cpp += param.name + ", "
                func.body.cpp = func.body.cpp.replace("/**/" + param.name + "()", param.name)
            decls = self.get_decls(func.body)
            for decl in decls:
                if "local" in decl.quals:
                    func.body.cpp = func.body.cpp.replace("/**/" + decl.name + "()", decl.name)
            if params:
                func.node.cpp = func.node.cpp[:-2]
            func.node.cpp += ") {\n"
            func.node.cpp += func.body.cpp
            func.node.cpp += "}\n"
            self._functions_cpp.append((func.name, func.node.cpp))
        return ret

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
        node.cpp = ", ".join([expr.cpp for expr in node.exprs])
        if ".insert(" in node.cpp:
            raise errors.PfpError("Missing parenthesis after +=")
        if "VectorRemove(" in node.cpp:
            raise errors.PfpError("Missing parenthesis after -=")
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
        # scope.push()

        node.cpp = ""
        try:
            ret = None
            for child in node.children():
                scope.clear_meta()
                try:
                    self._handle_node(child, scope, ctxt, stream)
                except errors.InterpReturn as e:
                    if not self._generate:
                        raise e
                    elif ret is None:
                        ret = e
                if child[1].cpp:
                    node.cpp += "\t" + child[1].cpp.replace("\n", "\n\t") + ";\n"
            if ret is not None:
                if self._call_stack[-1]:
                    raise ret
                else:
                    node.cpp = node.cpp.replace("return ", "exit_template")
                    node.cpp = node.cpp.replace("return;", "exit_template(0);")

        # in case a return occurs, be sure to pop the scope
        # (returns are implemented by raising an exception)
        finally:
            # scope.pop()
            scope.clear_meta()

    def _handle_return(self, node, scope, ctxt, stream):
        """Handle Return nodes

        :node: TODO
        :scope: TODO
        :ctxt: TODO
        :stream: TODO
        :returns: TODO

        """
        self._dlog("handling return")
        node.cpp = "return"
        if node.expr is None:
            ret_val = None
        else:
            ret_val = self._handle_node(node.expr, scope, ctxt, stream)
            node.cpp += " (" + node.expr.cpp + ")"
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
        curr_val._pfp__value = 0
        prev_val = None
        for enumerator in node.values.enumerators:
            if enumerator.value is not None:
                curr_val_parsed = self._handle_node(
                    enumerator.value, scope, ctxt, stream
                )
                curr_val = enum_cls()
                curr_val._pfp__set_value(curr_val_parsed._pfp__value)
            elif prev_val is not None:
                curr_val = prev_val + 1
            curr_val.signed = enum_cls.signed
            curr_val._pfp__freeze()
            enum_vals[enumerator.name] = curr_val
            enum_vals[fields.PYVAL(curr_val)] = enumerator.name
            scope.add_local(enumerator.name, curr_val)
            prev_val = curr_val

        if node.name is not None:
            enum_cls = EnumDef(node.name, enum_cls, enum_vals)
            scope.add_type_class(node.name, enum_cls)

        else:
            enum_cls = EnumDef(
                "enum_" + enum_cls.__name__, enum_cls, enum_vals
            )
            # don't add to scope if we don't have a name
        node.cpp = "\nenum "
        if node.name is None:
            if hasattr(node, "names"):
                name = " ".join(node.names)
            else:
                node.name = "unnamed_enum"
                name = node.name
        else:
            name = node.name
        node.cpp += name
        if node.type is not None:
            node.cpp += " : " + " ".join(node.type.names)
        node.cpp += " {\n"
        for enumerator in node.values.enumerators:
            self._global_consts.append(enumerator.name)
            self._defined[enumerator.name] = "enum value"
            node.cpp += "\t" + enumerator.name
            if enumerator.value:
                if node.type is not None:
                    node.cpp += " = (" + " ".join(node.type.names) + ") " + enumerator.value.cpp
                else:
                    node.cpp += " = " + enumerator.value.cpp
            node.cpp += ",\n"
        node.cpp += "}"
        if name in self._defined:
            node.cpp = ""
        else:
            self._defined[name] = "enum"
            if node.type is not None:
                self._global_consts.append(name + "_values")
                cpp = "std::vector<" + " ".join(node.type.names) + "> " + name + "_values = { "
                for enumerator in node.values.enumerators:
                    cpp += enumerator.name + ", "
                cpp = cpp[:-2]
                cpp += " };\n"
                self._cpp.append((name, node.cpp + ";\n" + cpp))
            else:
                self._cpp.append((name, node.cpp + ";\n"))
        if node.type is not None:
            enum_cls.typename = " ".join(node.type.names)

        return enum_cls

    def _handle_array_decl(self, node, scope, ctxt, stream):
        """Handle ArrayDecl nodes

        :node: TODO
        :scope: TODO
        :ctxt: TODO
        :stream: TODO
        :returns: TODO

        """
        self._dlog(
            "handling array declaration '{}'".format(node.type.declname)
        )

        if node.dim is None:
            # will be used
            array_size = None
        else:
            array_size = self._handle_node(node.dim, scope, ctxt, stream)
        if self._generate:
            array_size = None
        self._dlog("array size = {}".format(array_size))
        # TODO node.dim_quals
        # node.type
        field_cls = self._handle_node(node.type, scope, ctxt, stream)
        self._dlog("field class = {}".format(field_cls))
        array = ArrayDecl(field_cls, array_size)
        # array = fields.Array(array_size, field_cls)
        array._pfp__name = node.type.declname
        # array._pfp__parse(stream)
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
        if hasattr(ary, "field_cls") and not hasattr(ary.field_cls, "format") and ary.field_cls != fields.String and ary._pfp__name in self._variable_types and "_array_class" in self._variable_types[ary._pfp__name]:
            node.cpp = "(*" + node.name.cpp + "[" + node.subscript.cpp + "])"
        else:
            node.cpp = node.name.cpp + "[" + node.subscript.cpp + "]"
        index = fields.PYVAL(subscript)
        if self._generate:
            index = 0
            try:
                return ary[index]
            except:
                return None
        return ary[index]

    def _handle_if(self, node, scope, ctxt, stream):
        """Handle If nodes

        :node: TODO
        :scope: TODO
        :ctxt: TODO
        :stream: TODO
        :returns: TODO

        """
        if self._generate and node.__class__ == AST.If and self._incomplete_stack[-1]:
            return
        node.cpp = ""
        self._dlog("handling if/ternary_op")
        cond = self._handle_node(node.cond, scope, ctxt, stream)
        if self._generate:
            ret = None
            try:
                true_branch = self._handle_node(node.iftrue, scope, ctxt, stream)
            except errors.InterpReturn as e:
                if not self._generate:
                    raise e
                elif ret is None:
                    ret = e
            #except:
            #    print("exception on if true")
            #    true_branch = None
            if node.iffalse is not None:
                try:
                    false_branch = self._handle_node(node.iffalse, scope, ctxt, stream)
                except errors.InterpReturn as e:
                    if not self._generate:
                        raise e
                    elif ret is None:
                        ret = e
                #except:
                #    print("exception on if false")
                #    false_branch = None
            if node.__class__ == AST.TernaryOp:
                node.cpp = "(" + node.cond.cpp + " ? " + node.iftrue.cpp + " : " + node.iffalse.cpp + ")"
            if node.__class__ == AST.If:
                node.cpp = "if (" + node.cond.cpp + ") {\n"
                if isinstance(node.iftrue, list):
                    for e in node.iftrue:
                        node.cpp += "\t" + e.cpp.replace("\n", "\n\t") + ";\n"
                else:
                    node.cpp += node.iftrue.cpp
                    if not hasattr(node.iftrue, "block_items") or node.iftrue.block_items is None:
                        node.cpp += ";\n"
                node.cpp += "}"
                if node.iffalse is not None:
                    node.cpp += " else {\n"
                    if isinstance(node.iffalse, list):
                        for e in node.iffalse:
                            node.cpp += "\t" + e.cpp.replace("\n", "\n\t") + ";\n"
                    else:
                        node.cpp += node.iffalse.cpp
                        if not hasattr(node.iffalse, "block_items") or node.iffalse.block_items is None:
                            node.cpp += ";\n"
                    node.cpp += "}"
            if ret is not None:
                if self._call_stack[-1]:
                    raise ret
                else:
                    node.cpp = node.cpp.replace("return ", "exit_template")
                    node.cpp = node.cpp.replace("return;", "exit_template(0);")
            if node.iffalse is not None and not cond:
                return false_branch
            else:
                return true_branch
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
        if self._generate and self._incomplete_stack[-1]:
            return
        node.cpp = ""
        self._dlog("handling for")
        if node.init is not None:
            # perform the init
            self._handle_node(node.init, scope, ctxt, stream)

        while node.cond is None or self._handle_node(
            node.cond, scope, ctxt, stream
        ) or self._generate:
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

                except errors.InterpReturn as e:
                    if not self._generate:
                        raise e

            if node.next is not None:
                # do the next statement
                self._handle_node(node.next, scope, ctxt, stream)
            if self._generate:
                break
        node.cpp = "for ("
        if node.init is not None:
            node.cpp += node.init.cpp
        else:
            node.cpp += " "
        node.cpp += "; "
        if node.cond is not None:
            node.cpp += node.cond.cpp
        node.cpp += "; "
        if node.next is not None:
            node.cpp += node.next.cpp
        node.cpp += ") {\n"
        if isinstance(node.stmt, list):
            for stmt in node.stmt:
                node.cpp += "\t" + stmt.cpp + ";\n"
        elif node.stmt is not None:
            node.cpp += "\t" + node.stmt.cpp + ";\n"
        node.cpp += "}"

    def _handle_while(self, node, scope, ctxt, stream):
        """Handle break node

        :node: TODO
        :scope: TODO
        :ctxt: TODO
        :stream: TODO
        :returns: TODO

        """
        if self._generate and self._incomplete_stack[-1]:
            return
        node.cpp = ""
        self._dlog("handling while")
        while node.cond is None or self._handle_node(
            node.cond, scope, ctxt, stream
        ) or self._generate:
            if node.stmt is not None:
                try:
                    self._handle_node(node.stmt, scope, ctxt, stream)
                except errors.InterpBreak as e:
                    break
                except errors.InterpContinue as e:
                    pass
                except errors.InterpReturn as e:
                    if not self._generate:
                        raise e
            if self._generate:
                break
        node.cpp = "while (" + node.cond.cpp + ") {\n"
        if node.stmt.__class__ == AST.Compound:
            node.cpp += node.stmt.cpp
        else:
            node.cpp += "\t" + node.stmt.cpp + ";\n"
        node.cpp += "}"

    def _handle_do_while(self, node, scope, ctxt, stream):
        """Handle break node

        :node: TODO
        :scope: TODO
        :ctxt: TODO
        :stream: TODO
        :returns: TODO

        """
        if self._generate and self._incomplete_stack[-1]:
            return
        node.cpp = ""
        self._dlog("handling do while")

        while True:
            if node.stmt is not None:
                try:
                    self._handle_node(node.stmt, scope, ctxt, stream)
                except errors.InterpBreak as e:
                    break
                except errors.InterpContinue as e:
                    pass
                except errors.InterpReturn as e:
                    if not self._generate:
                        raise e
            if node.cond is not None and not self._handle_node(
                node.cond, scope, ctxt, stream,
            ):
                break
            if self._generate:
                break
        node.cpp = "do {\n"
        if node.stmt.__class__ == AST.Compound:
            node.cpp += node.stmt.cpp
        else:
            node.cpp += "\t" + node.stmt.cpp + ";\n"
        node.cpp += "} while (" + node.cond.cpp + ")"

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
        if self._generate and self._incomplete_stack[-1]:
            return
        node.cpp = ""

        def exec_case(idx, cases):
            # keep executing cases until a break is found,
            # or they've all been executed
            ret = None
            for case in cases[idx:]:
                stmts = case.stmts

                if self._generate:
                    for stmt in stmts:
                        try:
                            self._handle_node(stmt, scope, ctxt, stream)
                        except errors.InterpReturn as e:
                            if ret is None:
                                ret = e
                    continue

                try:
                    for stmt in stmts:
                        self._handle_node(stmt, scope, ctxt, stream)
                except errors.InterpBreak as e:
                    break
            return ret

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
        if cond is None:
            cond = 0
        is_string = False
        try:
            is_string = type(cond) == fields.String or "width" in vars(cond)
        except:
            pass

        default_idx = None
        found_match = False

        cases = getattr(node, "pfp_cases", None)
        if cases is None:
            cases = get_cases(node.stmt.children())
            node.pfp_cases = cases

        for idx, child in enumerate(cases):
            if child.__class__ == AST.Default:
                default_idx = idx
                continue
            elif child.__class__ == AST.Case:
                expr = self._handle_node(child.expr, scope, ctxt, stream)
                if expr == cond and not self._generate:
                    found_match = True
                    exec_case(idx, cases)
                    break

        if default_idx is not None and not found_match and not self._generate:
            exec_case(default_idx, cases)

        if self._generate:
            ret = exec_case(0, cases)
            node.cpp = "switch ("
            if is_string:
                node.cpp += "STR2INT("
            node.cpp += node.cond.cpp
            if is_string:
                node.cpp += ")"
            node.cpp += ") {\n"
            for child in cases:
                if child.__class__ == AST.Case:
                    node.cpp += "case "
                    if is_string:
                        node.cpp += "STR2INT("
                    node.cpp += child.expr.cpp
                    if is_string:
                        node.cpp += ")"
                    node.cpp += ":\n"
                    for stmt in child.stmts:
                        node.cpp += "\t" + stmt.cpp.replace("\n", "\n\t") + ";\n"
                elif child.__class__ == AST.Default:
                    node.cpp += "default:\n"
                    for stmt in child.stmts:
                        node.cpp += "\t" + stmt.cpp.replace("\n", "\n\t") + ";\n"
            node.cpp += "}"
            if ret is not None:
                if self._call_stack[-1]:
                    raise ret
                else:
                    node.cpp = node.cpp.replace("return ", "exit_template")
                    node.cpp = node.cpp.replace("return;", "exit_template(0);")

    def _handle_break(self, node, scope, ctxt, stream):
        """Handle break node

        :node: TODO
        :scope: TODO
        :ctxt: TODO
        :stream: TODO
        :returns: TODO

        """
        node.cpp = "break"
        self._dlog("handling break")
        if not self._generate:
            raise errors.InterpBreak()

    def _handle_continue(self, node, scope, ctxt, stream):
        """Handle continue node

        :node: TODO
        :scope: TODO
        :ctxt: TODO
        :stream: TODO
        :returns: TODO

        """
        node.cpp = "continue"
        self._dlog("handling continue")
        if not self._generate:
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
            # AST.ByRefDecl,
            # AST.TypeDecl,
            # AST.Struct,
            # AST.IdentifierType,
            AST.Typedef,
            # AST.Constant,
            AST.BinaryOp,
            AST.Assignment,
            # AST.ID,
            AST.UnaryOp,
            # AST.FuncDef,
            AST.FuncCall,
            # AST.FuncDecl,
            # AST.ParamList,
            # AST.ExprList,
            # AST.Compound,
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

        for func_name, native_func in six.iteritems(self._natives):
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
            "char": "Char",
            "int": "Int",
            "long": "Int",
            "int64": "Int64",
            "uint64": "UInt64",
            "short": "Short",
            "double": "Double",
            "float": "Float",
            "void": "Void",
            "string": "String",
            "wstring": "WString",
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
                raise errors.UnresolvedType(
                    self._coord, " ".join(names), " ".join(resolved_names)
                )
            names = copy.copy(names)
            names.pop()
            names += resolved_names

        if len(names) >= 2 and names[-1] == names[-2] and names[-1] == "long":
            res = "Int64"
        else:
            res = switch[names[-1]]

        if (
            names[-1] in ["char", "short", "int", "long"]
            and "unsigned" in names[:-1]
        ):
            res = "U" + res

        cls = getattr(fields, res)
        return cls

def is_forward_declared_struct(node):
    return (
        isinstance(node, AST.Decl)
        and node.init is None
        and isinstance(node.type, AST.Struct)
        and node.type.decls is None
    )

