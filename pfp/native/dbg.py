#!/usr/bin/env python
# encoding: utf-8

from pfp.native import native
import pfp.fields
from pfp.dbg import PfpDbg

@native(name="Int3", ret=pfp.fields.Void, send_interp=True)
def int3(params, ctxt, scope, stream, interp):
	if interp._no_debug:
		return

	interp.debugger = PfpDbg(interp)
	interp.debugger.cmdloop()
