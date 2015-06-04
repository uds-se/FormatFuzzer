import pfp.interp

def native(name, ret, interp=None):
	def native_decorator(func):
		def native_wrapper(*args, **kwargs):
			return func(*args, **kwargs)
		pfp.interp.PfpInterp.add_native(name, func, ret, interp=interp)
		return native_wrapper
	return native_decorator
