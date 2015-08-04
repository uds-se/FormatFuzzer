
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
the input stream. Prefixing a declaration with `const` or `local`
will create a temporary variable that can be used in the script.

An example template script that parses TLV (type-length-value)
structures out of the input stream: ::

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

Note that a return statement in the main body of the script will
cause the template to stop being executed. Also note that declaring
multiple variables of the same name (in this case, `tlv`) will cause
that variable to be made into an array of the variable's type.

More about the 010 template script syntax can be read about
`on the 010 Editor website <http://www.sweetscape.com/010editor/templates.html>`_.

Parsing Data
^^^^^^^^^^^^

010 template scripts are interpreted from python using the `pfp.parse`
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

The `pfp.parse` function returns a dom of the parsed data. Individual
fields may be accessed using standard dot-notation: ::

    for tlv in parsed_tlv.tlvs:
        print("type: {}, value: {}".format(tlv.type, tlv.value))

Manipulating Data
^^^^^^^^^^^^^^^^^


