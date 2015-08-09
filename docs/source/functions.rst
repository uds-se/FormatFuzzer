
Functions
=========

Functions in pfp can either be defined natively in python, or
in the template script itself.

Native Functions
^^^^^^^^^^^^^^^^

Two main methods exist to add native python functions to the
pfp interpreter:

1. The :any:`@native decorator <pfp.native.native>`
2. The :any:`add_native method <pfp.interp.PfpInterp.add_native>`

Follow the links above for detailed information.

Interpreted Functions
^^^^^^^^^^^^^^^^^^^^^

Interpreted functions can declared as you normally would in
an 010 template (basically c-style syntax).

Functions Reference Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: pfp.functions
   :members:

.. automodule:: pfp.native
   :members:
