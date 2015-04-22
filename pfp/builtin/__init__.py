import pfp.interp

def native(name, ret):
	def native_decorator(func):
		def native_wrapper(*args, **kwargs):
			return func(*args, **kwargs)
		pfp.interp.PfpInterp.add_builtin(name, func, ret)
		return native_wrapper
	return native_decorator
