import pfp.interp

def native(name, ret, interp=None, send_interp=False):
	def native_decorator(func):
		def native_wrapper(*args, **kwargs):
			return func(*args, **kwargs)
		pfp.interp.PfpInterp.add_native(name, func, ret, interp=interp, send_interp=send_interp)
		return native_wrapper
	return native_decorator

def predefine(template):
	pfp.interp.PfpInterp.add_predefine(template)
