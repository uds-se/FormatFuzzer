#!/usr/bin/env python
# encoding: utf-8

import cmd
import os
import sys

class PfpDbg(cmd.Cmd, object):
	"""The pfp debugger cmd.Cmd class"""
	
	prompt = "pfp>"

	def __init__(self, ctxt, scope, stream):
		"""Create the pfp debugger

		:scope: The scope in which to start debugging
		"""
		super(PfpDbg, self).__init__()

		self._ctxt = ctxt
		self._scope = scope
		self._stream = stream
	
	def default(self, line):
		cmd, arg, line = self.parseline(line)
		func = [getattr(self, n) for n in self.get_names() if n.startswith('do_' + cmd)]
		
		if func:
			return func[0](arg)
	
	def do_next(self, args):
		"""Step over the next statement
		"""
		pass
	
	def do_quit(self, args):
		"""The quit command
		"""
		return True
	
	def do_EOF(self, args):
		"""The eof command
		"""
		return True
