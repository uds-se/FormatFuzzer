
Debugger
========

QuickStart
^^^^^^^^^^

Pfp comes with a built-in debugger. You can drop into the interactive
debugger by calling the :any:`Int3() <pfp.native.dbg.int3>` function
within a template.

All commands are documented below in the debug reference documentation.
Command methods begin with ``do_``.

Internals
^^^^^^^^^

While the pfp interpreter is handling AST nodes, it decides if a node
can be "breaked" on using the ``_node_is_breakable`` method. If the
interpreter is in a debug state, and the current node can be breaked
on, the user will be dropped into the interactive debugger.

Debugger Reference Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: pfp.dbg
   :members:
.. automodule:: pfp.native.dbg
   :members:
