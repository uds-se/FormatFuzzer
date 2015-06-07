#!/usr/bin/env python
# encoding: utf-8

from pfp.native import native
import pfp.fields
from pfp.dbg import PfpDbg

@native(name="Int3", ret=pfp.fields.Void)
def int3(params, ctxt, scope, stream):
	import pdb ; pdb.set_trace()
	debugger = PfpDbg(ctxt, scope, stream)
	debugger.cmdloop("\ndropping into pfp debugger...\n")
