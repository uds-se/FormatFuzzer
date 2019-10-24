
Fields
======

General
^^^^^^^

Every declared variable in 010 templates creates a :any:`pfp.fields.Field`
instance in memory.

Naming Convention
"""""""""""""""""

Some may find it annoying having the prefix ``_pfp__`` affixed to field methods
and variables, but I found it more annoying having to access all child fields
of a struct via square brackets. The prefix is simply to prevent name collisions
so that ``__getattr__`` can be used to access child fields with dot-notation.

Parsed Offset
"""""""""""""

Parsed offsets of fields are set during object parsing and are re-set each time
the main :any:`pfp.fields.Dom` instance is built. This means that operations
that should modify the offsets of fields will cause invalid offsets to exist
until the main dom is built again.

Printing
""""""""

Use the :any:`pfp.fields.Field._pfp__show` method to return a
pretty-printed representation of the field.

Full Field Paths
""""""""""""""""

Use the :any:`pfp.fields.Field._pfp__path` method to fetch the full path
of the field. E.g. in the template below, the ``inner`` field would have
a full path of ``root.nested1.nested2.inner``, and the second element of
the ``array`` field would have a full path of ``root.nested1.nested2.array[1]``:

.. code-block:: c

    struct {
        struct {
            struct {
                char inner;
                char array[4];
            } nested2;
            int some_int;
        } nested1;
        int some_int2;
    } root;

Structs
^^^^^^^

Structs are the main containers used to add fields to. A :any:`pfp.fields.Dom` instance
is the struct that all fields are added to.

Field Reference Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: pfp.fields.Field
   :members: _pfp__name, _pfp__parent, _pfp__build, _pfp__parse, _pfp__watchers, _pfp__watch_fields, _pfp__width, _pfp__set_value, _pfp__show, _pfp__path

.. autoclass:: pfp.fields.Array
   :members: width, field_cls, raw_data

.. autoclass:: pfp.fields.Struct
   :members: _pfp__children, _pfp__add_child

.. automodule:: pfp.fields
   :members:
