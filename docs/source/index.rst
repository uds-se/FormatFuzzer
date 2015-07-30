.. PFP documentation master file, created by
   sphinx-quickstart on Wed Apr  8 07:31:42 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PFP - Python Format Parser
===============================

Pfp (python format parser) is a python interpreter for
`010 Editor <http://www.sweetscape.com/010editor/>`_.

Pfp uses `py010parser <https://github.com/d0c-s4vage/py010parser>`_ to
parse 010 templates into an AST, which is then interpreted by
pfp. Pfp then returns a DOM object which can be used to access
individual fields of the defined data structure.

A simple example of parsing a PNG image: ::

    import pfp

    dom = pfp.parse(data_file="image.png", template_file="png_template.bt")

    for chunk in dom.png.chunk:
        if chunk.name == "tEXt":
            print("Found the comment:")
            print(chunk.data.comment)

Contents:

.. toctree::
   :maxdepth: 2

.. automodule:: pfp
   :members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

