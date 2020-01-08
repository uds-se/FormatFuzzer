
.. _differences:

Differences Between 010 and pfp
===============================

This section documents the known differences between pfp and 010 editor.

.. toctree::
    :maxdepth: 1

Duplicate Arrays
----------------

*TLDR*: Pfp does not [yet] support non-consecutive duplicate arrays.
Consecutive duplicate arrays are fully supported.

First, some definitions and back story.

Duplicate arrays are what occurs when multiple variables of the same name
are declared in the same scope. E.g.:

.. code-block:: c

    int x;
    int x;
    if (x[0] == x[1] || x[0] == x) {
        Printf("Same!");
    }

The 010 template script above declares ``x`` twice, creating a duplicate, or
as pfp originally called it, an implicit array. Notice the two comparisons -
they actually perform the same comparison:

.. code-block:: c

    x[0] != x[1]

and

.. code-block:: c

    x[0] == x

In 010, if the duplicate/implicit array is referenced without indexing, the
most recently parsed field in the duplicate array is returned. I.e., it's treated
as a normal field and not an array. However, if indexing is done on the duplicate
array variable, the variable is treated as an array.

Below is a quote on duplicate arrays from the
`010 Editor documentation <https://www.sweetscape.com/010editor/manual/ArraysDuplicates.htm>`_:

    When writing a template, regular arrays can be declaring using the same syntax
    as scripts (see Arrays and Strings). However, 010 Editor has a syntax that
    allows arrays to be built in a special way. When declaring template variables,
    multiple copies of the same variable can be declared. For example:

    .. code-block:: c

        int x;
        int y;
        int x;

    010 Editor allows you to treat the multiple declarations of the variable as
    an array (this is called a Duplicate Array). In this example, x[0] could
    be used to reference the first occurrence of x and x[1] could be used to
    reference the second occurrence of x. Duplicate arrays can even be defined
    with for or while loops. For example:

    .. code-block:: c

        local int i;
        for( i = 0; i < 5; i++ )
            int x;

This breaks down in pfp when non-consecutive arrays are created, as is done
in the first code sample from the 010 Editor documentation above.
`Issue #111 <https://github.com/d0c-s4vage/pfp/issues/111>`_ tracks the effort
to add support for non-consecutive duplicate arrays.
