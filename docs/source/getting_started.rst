.. _getting_started:
Getting Started
===============

Installation
^^^^^^^^^^^^

Pfp can be installed via pip: ::

    pip install pfp

Introduction
^^^^^^^^^^^^

Pfp is an interpreter for 010 template scripts. 010 Template scripts
use a modified C syntax. Control-flow
statements are allowed within struct declarations, and type
checking is done dynamically, as statements are interpreted
instead of at compile time.

010 template scripts parse data from the input stream by declaring
variables. Each time a variable is declared, that much data is read
from the input stream and stored in the variable.

Variables are also allowed that do not cause data to be read from
the input stream. Prefixing a declaration with ``const`` or ``local``
will create a temporary variable that can be used in the script.

An example template script that parses TLV (type-length-value)
structures out of the input stream is shown below:

.. highlight:: c

::

    local int count = 0;
    const uint64 MAGIC = 0xaabbccddeeff0011;

    uint64 magic;

    if(magic != MAGIC) {
        Printf("Magic value is not valid, bailing");
        return 1;
    }

    while(!FEof()) {
        Printf("Parsing the %d-th TLV structure", ++count);
        struct {
            string type;
            int length;
            char value[length;
        } tlv;
    }

.. highlight:: python

Note that a return statement in the main body of the script will
cause the template to stop being executed. Also note that declaring
multiple variables of the same name (in this case, ``tlv``) will cause
that variable to be made into an array of the variable's type.

More about the 010 template script syntax can be read about
`on the 010 Editor website <http://www.sweetscape.com/010editor/templates.html>`_.

Parsing Data
^^^^^^^^^^^^

010 template scripts are interpreted from python using the ``pfp.parse``
function, as shown below: ::

    import pfp

    template = """
        local int count = 0;
        const uint64 MAGIC = 0xaabbccddeeff0011;

        uint64 magic;

        if(magic != MAGIC) {
            Printf("Magic value is not valid, bailing");
            return 1;
        }

        while(!FEof()) {
            Printf("Parsing the %d-th TLV structure", ++count);
            struct {
                string type;
                int length;
                char value[length];
            } tlvs;
        }
    """

    parsed_tlv = pfp.parse(
        template        = template,
        data_file       = "path/to/tlv.bin"
    )

The ``pfp.parse`` function returns a dom of the parsed data. Individual
fields may be accessed using standard dot-notation: ::

    for tlv in parsed_tlv.tlvs:
        print("type: {}, value: {}".format(tlv.type, tlv.value))

Manipulating Data
^^^^^^^^^^^^^^^^^

Parsed data contained within the dom can be manipulated and then
rebuilt: ::

    for tlv in parsed_tlv.tlvs:
        if tlv.type == "SOMETYPE":
            tlv.value = "a new value"

    new_data = parsed_tlv._pfp__build()

Printing Structures
^^^^^^^^^^^^^^^^^^^

The method :any:`pfp.fields.Field._pfp__show` will print data information
about the field. If called on a field that contains child fields, those
fields will also be printed: ::

    dom = pfp.parse(...)
    print(dom._pfp__show(include_offset=True))

Metadata
^^^^^^^^

010 template sytax supports adding "special attributes" (called
metadata in pfp). 010 editor's special attributes are largely
centered around how fields are displayed in the GUI; for this
reason, pfp currently ignores 010 editor's special attributes.

However, pfp also introduces new special attributes to help
manage relationships between fields, such as lengths, checksums,
and compressed data.

The template below has updated the TLV-parsing template from
above to add metadata to the length field:

.. highlight:: c
::

    local int count = 0;
    const uint64 MAGIC = 0xaabbccddeeff0011;

    uint64 magic;

    if(magic != MAGIC) {
        Printf("Magic value is not valid, bailing");
        return 1;
    }

    while(!FEof()) {
        Printf("Parsing the %d-th TLV structure", ++count);
        struct {
            string type;
            int length<watch=value, update=WatchLength>;
            char value[length];
        } tlvs;
    }
.. highlight:: python

With the metadata, if the ``value`` field of a tlv were changed,
the ``length`` field would be automatically updated to the
new length of the ``value`` field.

See :doc:`metadata` for detailed information.

Debugger
^^^^^^^^

Pfp comes with a built-in debugger, which can be dropped into
by calling the :any:`Int3() <pfp.native.dbg.int3>` function in a
template. ::

         23 //   length (4 bytes), chunk_type (4 bytes), data (length bytes), crc (4 bytes)
         24 //   CRC Does NOT include the length bytes.
         25 //--------------------------------------
         26 
    -->  27 Int3();
         28 
         29 BigEndian();                  // PNG files are in Network Byte order
         30 
         31 const uint64 PNGMAGIC = 0x89504E470D0A1A0AL;
    pfp> peek
    89 50 4e 47 0d 0a 1a 0a 00 00 00 0d 49 48 44 52 .PNG........IHDR
    pfp> help

    Documented commands (type help <topic>):
    ========================================
    EOF  continue  eval  help  list  next  peek  quit  s  show  step  x

    pfp> n
         25 //--------------------------------------
         26 
         27 Int3();
         28 
    -->  29 BigEndian();                  // PNG files are in Network Byte order
         30 
         31 const uint64 PNGMAGIC = 0x89504E470D0A1A0AL;
         32 
         33 // Chunk Type
    pfp>
