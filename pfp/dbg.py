#!/usr/bin/env python
# encoding: utf-8

import cmd
import os
import sys

class PfpDbg(cmd.Cmd, object):
	"""The pfp debugger cmd.Cmd class"""
	
	prompt = "pfp> "

	def __init__(self, interp):
		"""Create the pfp debugger

		:scope: The scope in which to start debugging
		"""
		super(PfpDbg, self).__init__()

		self._interp = interp
	
	def precmd(self, args_line):
		"""Print the current coords of the interp
		"""
		curr_line,lines = self._interp.get_curr_lines()

		for line_no, line in lines:
			prefix = "    "
			line_no += 1
			if line_no == curr_line:
				prefix = "--> "
			print("{}{:3d} {}".format(prefix, line_no, line.replace("\t", "    ")))

		return args_line
	
	def default(self, line):
		cmd, arg, line = self.parseline(line)
		funcs = [getattr(self, n) for n in self.get_names() if n.startswith('do_' + cmd)]
		
		if len(funcs) > 1:
			for func in funcs:
				print(func)
		elif len(funcs) == 1:
			return funcs[0](arg)
		elif len(funcs) == 0:
			return self.do_eval(line)
	
	def do_next(self, args):
		"""Step over the next statement
		"""
		self._interp.step_over()
		return True
	
	def do_step(self, args):
		"""Step into the next statement
		"""
		self._interp.step_into()
		return True
	
	def do_continue(self, args):
		"""Continue the interpreter
		"""
		self._interp.cont()
		return True
	
	def do_eval(self, args):
		"""Eval the user-supplied statement
		"""
		self._interp.eval(args)
		return True
	
	def do_quit(self, args):
		"""The quit command
		"""
		return True
	
	def do_EOF(self, args):
		"""The eof command
		"""
		return True
