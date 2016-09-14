#!/usr/bin/env python
# encoding: utf-8

import cmd
import collections
import os
import sys

import pfp.fields as fields
import pfp.errors as errors
import pfp.utils as utils

class PfpDbg(cmd.Cmd, object):
    """The pfp debugger cmd.Cmd class"""
    
    prompt = "pfp> "

    def __init__(self, interp):
        """Create the pfp debugger

        :scope: The scope in which to start debugging
        """
        super(PfpDbg, self).__init__()

        self._interp = interp

        self._do_print_from_last_cmd = False
    
    def _update_prompt(self):
        if fields.NumberBase.endian == fields.BIG_ENDIAN:
            self.prompt = "BE pfp> "
        else:
            self.prompt = "LE pfp> "
    
    def update(self, ctxt, scope):
        self._ctxt = ctxt
        self._scope = scope
    
    def preloop(self):
        self._update_prompt()
        self.print_lines()
    
    def postcmd(self, stop, line):
        self._update_prompt()
        return stop
    
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
    
    def do_peek(self, args):
        """Peek at the next 16 bytes in the stream::

        Example:

            The peek command will display the next 16 hex bytes in the input
            stream::
                pfp> peek
                89 50 4e 47 0d 0a 1a 0a 00 00 00 0d 49 48 44 52 .PNG........IHDR
        """
        s = self._interp._stream
        # make a copy of it
        pos = s.tell()
        saved_bits = collections.deque(s._bits)
        data = s.read(0x10)
        s.seek(pos, 0)
        s._bits = saved_bits

        parts = ["{:02x}".format(ord(data[x:x+1])) for x in range(len(data))]
        if len(parts) != 0x10:
            parts += ["  "] * (0x10 - len(parts))
        hex_line = " ".join(parts)

        res = utils.binary("")
        for x in range(len(data)):
            char = data[x:x+1]
            val = ord(char)
            if 0x20 <= val <= 0x7e:
                res += char
            else:
                res += utils.binary(".")
        
        if len(res) < 0x10:
            res += utils.binary(" " * (0x10 - len(res)))

        res = "{} {}".format(hex_line, utils.string(res))
        if len(saved_bits) > 0:
            reverse_bits = reversed(list(saved_bits))
            print("bits: {}".format(" ".join(str(x) for x in reverse_bits)))
        print(res)
    
    def do_next(self, args):
        """Step over the next statement
        """
        self._do_print_from_last_cmd = True
        self._interp.step_over()
        return True
    
    def do_step(self, args):
        """Step INTO the next statement
        """
        self._do_print_from_last_cmd = True
        self._interp.step_into()
        return True
    
    def do_s(self, args):
        """Step into the next statement
        """
        return self.do_step(args)
    
    def do_continue(self, args):
        """Continue the interpreter
        """
        self._do_print_from_last_cmd = True
        self._interp.cont()
        return True
    
    def do_eval(self, args):
        """Eval the user-supplied statement. Note that you can do anything with
        this command that you can do in a template.

        The resulting value of your statement will be displayed.
        """
        try:
            res = self._interp.eval(args)
            if res is not None:
                if hasattr(res, "_pfp__show"):
                    print(res._pfp__show())
                else:
                    print(repr(res))
        except errors.UnresolvedID as e:
            print("ERROR: " + e.message)
        except Exception as e:
            raise
            print("ERROR: " + e.message)
            
        return False
    
    def do_show(self, args):
        """Show the current structure of __root (no args),
        or show the result of the expression (something that can be eval'd).
        """
        args = args.strip()

        to_show = self._interp._root
        if args != "":
            try:
                to_show = self._interp.eval(args)
            except Exception as e:
                print("ERROR: " + e.message)
                return False

        if hasattr(to_show, "_pfp__show"):
            print(to_show._pfp__show())
        else:
            print(repr(to_show))
    def do_x(self, args):
        pass
    do_x = do_show
    
    def do_list(self, args):
        """List the current location in the template
        """
        self.print_lines()
        return False
    
    def do_quit(self, args):
        """The quit command
        """
        self._interp.set_break(self._interp.BREAK_NONE)
        return True
    
    def do_EOF(self, args):
        """The eof command
        """
        return True
    
    # ---------------------

    def print_lines(self):
        curr_line,lines = self._interp.get_curr_lines()

        for line_no, line in lines:
            prefix = "    "
            line_no += 1
            if line_no == curr_line:
                prefix = "--> "
            print("{}{:3d} {}".format(prefix, line_no, line.replace("\t", "    ")))
