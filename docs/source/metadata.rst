Metadata in PFP
===================

Fields in PFP are allowed to have metadata. Metadata is added to
a field by adding a `<key=val,key2=val2,...>` after a field's
declaration, but before the semicolon. 010 templates
`also allow <http://www.sweetscape.com/010editor/manual/TemplateVariables.htm>`
for metadata to be added to fields, although most of
those values changed how fields were displayed in the GUI::

    int someField<format=hex>;

PFP adds some more useful extensions to the 010 template syntax. E.g.
metadata values that allow fields to "watch" a different field and
update its own value when the watched field changes::

    struct {
        int length<watch=stringData, update=WatchLength>;
        string data;
    } stringWithLength;


PFP Metadata Extensions
-----------------------

Watch Metadata
^^^^^^^^^^^^^^

Watch metadata allows the template to specify that a field should
be modified or update when one of the fields it watches changes value.

Watch metadata must meet the requirements below:

* must contain the `watch` key to specify which field(s) to watch
* must contain the `update` key to specify a function to perform the updating

watch
"""""

The watch key must be one or more semi-colon-separated statements or field names. All
of the these fields will be passed to the specified `update` function. E.g. ::

    int field1;
    int field2;
    int field3<watch=field1;field2, ...>;

Note that each item in the semi-colon-separated watch field list
is eval'd as 010 template script. The resulting field will be
the result of the eval. This allows, for example, functions to be
called that will return which field to watch. (I have no idea why
you'd want to do this, but you can).

update 
""""""

The update key must be the name of a function, native or interpreted,
that will accept at least two parameters. The update function should
have the signature: ::

    void SumFields(int &to_update, int watched1, int watched2) {
        to_update = watched1 + watched2;
    }

The function above can then be used like so: ::

    int field1;
    int field2;
    int sum<watch=field1;field2, update=SumFields>;

Packer Metadata
^^^^^^^^^^^^^^^

Packer metadata allows data structures to be nested inside of transformed/encoded/compressed data.
The most common example of this would be gzip-compressed data, that when
decompressed also has a defined structure.

Packer metadata can be set in two different ways. In both ways, a
`packtype` key must be set that specifies the structure type that
should be used to parse the packed data.

The packing and unpacking function(s) have two ways to be defined:

1. A single function (`packer` key) that takes an additional parameter that says whether to
    pack or unpack the data.
2. Two functions that define separate `pack` and `unpack` functions. The `pack` function
    is optional if you never intend to rebuild the dom.

After packed data has been parsed, the packed data can be accessed
via the `_` field name: ::

    dom = pfp.parse(...)
    dom.packed_data._.unpacked_field
    ...

packtype
""""""""

The `packtype` key should point to a data type that will be used to parse the
packed data. E.g.: ::

    typedef struct {
        int a;
        int b;
    } packedData;

    struct {
        uchar data[4]<packtype=packedData, ...>;
    } main;

packer
""""""

The `packer` key should reference a function that can handle both packing *and*
unpacking. The function (native or interpreted) must have the signature: ::

    char[] packerFunction(pack, char data[]) {
        ...
        // must return an array of unpacked data
    }

Note that interpreted packer functions have not been thoroughly tested. Native
packers work just fine (see the `GZipper` packer in `native/packers.py` for
an example).

pack
""""

The `pack` key should be a function that accepts an array of the unpacked data,
and returns an array that represents the packed data.

unpack
""""""

The `unpack` key should be a function that accepts an array of packed data,
and returns an array that represents the unpacked data.
