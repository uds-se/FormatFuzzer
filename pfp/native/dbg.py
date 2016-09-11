#!/usr/bin/env python
# encoding: utf-8

from pfp.native import native
import pfp.fields
from pfp.dbg import PfpDbg

@native(name="Int3", ret=pfp.fields.Void, send_interp=True)
def int3(params, ctxt, scope, stream, coord, interp):
    """Define the ``Int3()`` function in the interpreter. Calling
    ``Int3()`` will drop the user into an interactive debugger.
    """
    if interp._no_debug:
        return

    if interp._int3:
        interp.debugger = PfpDbg(interp)
        interp.debugger.cmdloop()
