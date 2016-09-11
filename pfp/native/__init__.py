import functools

import pfp.interp

def native(name, ret, interp=None, send_interp=False):
    """Used as a decorator to add the decorated function to the
    pfp interpreter so that it can be used from within scripts.

    :param str name: The name of the function as it will be exposed in template scripts.
    :param pfp.fields.Field ret: The return type of the function (a class)
    :param pfp.interp.PfpInterp interp: The specific interpreter to add the function to
    :param bool send_interp: If the current interpreter should be passed to the function.

    Examples:

        The example below defines a ``Sum`` function that will return the sum of
        all parameters passed to the function: ::

            from pfp.fields import PYVAL

            @native(name="Sum", ret=pfp.fields.Int64)
            def sum_numbers(params, ctxt, scope, stream, coord):
                res = 0
                for param in params:
                    res += PYVAL(param)
                return res
        
        The code below is the code for the :any:`Int3 <pfp.native.dbg.int3>` function. Notice that it
        requires that the interpreter be sent as a parameter: ::

            @native(name="Int3", ret=pfp.fields.Void, send_interp=True)
            def int3(params, ctxt, scope, stream, coord, interp):
                if interp._no_debug:
                    return

                if interp._int3:
                    interp.debugger = PfpDbg(interp)
                    interp.debugger.cmdloop()
    """
    def native_decorator(func):
        @functools.wraps(func)
        def native_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        pfp.interp.PfpInterp.add_native(name, func, ret, interp=interp, send_interp=send_interp)
        return native_wrapper
    return native_decorator

def predefine(template):
    pfp.interp.PfpInterp.add_predefine(template)
