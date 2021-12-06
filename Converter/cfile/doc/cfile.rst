cfile
=====

C code generator for python


cfile.sequence
--------------

.. py:class:: sequence()

Returns a new sequence. A sequence is simply a list where each item in the list are statements or blocks.
Use sequence.append to insert a new items to the list. Use sequence.lines() to get the sequence as strings.
Use sequence.extend() to extend current sequence with items from another sequence.

Example::

   import cfile as C
   code = C.sequence()
   var_name='a'
   code.append(C.statement('%s=4'%(var_name)))
   print(str(code))

cfile.block
-----------

.. py:class:: block(indent=None, innerIndent=0, head=None, tail=None)

Creates a new C block (a block starts with '{' and ends with '}')

.. py:attribute:: block.code

An instance of cfile.sequence.


.. py::method:: sequence.append(item)

appends item to the sequence. the item can be any of:

* cfile.line: A line of code.
* cfile.include: An include.
* cfile.statement: A statement.
* cfile.sequence: another sequence.
* cfile.block: A block (a block is also a sequence).

cfile.variable
--------------

.. py:class:: variable(name, typename='int', static=0, const=0, pointer=0, alias=0,extern=0, array=None)

Creates a C variable. Note that static, const, pointer and extern can be initialized with True/False as well as 0,1,2 etc.


cfile.function
--------------

.. py:class:: function(name, typename='int', static=0, const=0, pointer=0, classname="", params=None)

Constructor parameters
~~~~~~~~~~~~~~~~~~~~~~

**Name**: Name of new function (string)

**typename**: return type name (string). Default='int'.

**static**: Controls the static property. Default=0.

* 0: function is not const
* 1: function is const
* False: See 0
* True: See 1

**const**: Controls the const property. Default=0.

* 0: function is not const
* 1: function is const
* False: See 0
* True: See 1

**pointer**: Controls the pointer property. Default=0.

* 0: return type is not pointer
* 1: return type is pointer (*)
* False: See 0
* True: See 1
* 2: return type is pointer to pointer (\**)
* 3: return type is pointer to pointer to pointer (\***)

**classname**: C++ class name

**params**: Function parameters (list of cfile.variable objects). Parameter(s) can also be added after the function has been
created using the add_param method.

Attributes
~~~~~~~~~~

**name**: name of the function.

**typename**: name of the return type of the function.

**params**: list of function parameters (expected type is cfile.variable).

**classname**: Very rudimentary support of c++ class name.

cfile.fcall
-----------

.. py:class:: fcall(name, args=None)

A C function call expression.

Constructor parameters
~~~~~~~~~~~~~~~~~~~~~~

**name**: Name of the function that is being called
**args**: Arguments of the function call. This can be a single expression or a list of expressions

Example::

   import cfile as C
   func = C.function('add_values', 'int', params=[C.variable('a', 'int'), C.variable('b', 'int')])
   body = C.block(innerIndent=4)
   body.append(C.statement('return %s+%s'%(func.params[0].name, func.params[1].name)))

   code = C.sequence()
   code.append(func)
   code.append(body)
   code.append(C.blank(1))
   code.append(C.statement(C.fcall(func.name, ['4', '5'])))
   print(str(code))
