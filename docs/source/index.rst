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

Please read the :ref:`getting_started` section for a better introduction.

A simple example of extracting the comments out of a PNG image using
the png template found below: ::

    import pfp

    dom = pfp.parse(data_file="image.png", template_file="png_template.bt")

    for chunk in png.chunks:
        if chunk.cname == "tEXt":
            print("Comment before: {}".format(chunk.data.tEXt.comment))
            chunk.data.tEXt.comment = "NEW COMMENT"
            print("Comment after: {}".format(chunk.data.tEXt.comment))

A simple png template is below. Notice how declaring variables parses
data from the input stream: ::

    typedef struct {
        // null-terminated
        string label;

        char comment[length - sizeof(label)];
    } TEXT;

    typedef struct {
        uint length<watch=data, update=WatchLength>;
        char cname[4];

        union {
            char raw[length];

            if(cname == "tEXt") {
                TEXT tEXt;
            }
        } data;
        uint crc<watch=cname;data, update=WatchCrc32>;
    } CHUNK;

    uint64 magic;

    while(!FEof()) {
        CHUNK chunks;
    }

Contents:

.. toctree::
   :maxdepth: 2

   getting_started
   metadata
   fields

.. automodule:: pfp
   :members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

