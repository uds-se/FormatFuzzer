
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

Functions are hoisted to the top of the scope they are declared in. E.g. the
following script is valid:

.. code-block:: c

    HelloWorld(10);

    typedef unsigned short custom_short;
    void HelloWorld(custom_short arg1) {
        Printf("Hello World, %d", arg1);
    }

Functions Reference Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: pfp.functions
   :members:

.. automodule:: pfp.native
   :members:
