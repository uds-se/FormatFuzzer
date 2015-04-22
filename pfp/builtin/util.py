import sys

from pfp.builtin import native
import pfp.fields

@native(name="Printf", ret=pfp.fields.Int)
def printf(params, ctxt, scope, stream):
	"""Prints format string to stdout

	:params: TODO
	:returns: TODO

	"""
	if len(params) == 1:
		print(PYVAL(params[0]))
		return

	import pdb ; pdb.set_trace()
	to_print = PYVAL(params[0]) % tuple(PYVAL(x) for x in params[1:])
	res = len(to_print)
	sys.stdout.write(to_print)
	sys.stdout.flush()
	return res
