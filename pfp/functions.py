from . import errors

class Function(object):
	"""A class to maintain function state and arguments"""
	def __init__(self, return_type, params, scope):
		"""
		Initialized the function. The Function body is intended to be set
		after the Function object has been created.
		"""
		super(Function, self).__init__()

		self.name = None
		self.body = None
		
		# note that the _scope is determined by where the function is
		# declared, not where it is called from
	 	# TODO see the comment in Scope.clone for potential future work/bugs
		self._scope = scope.clone()
		self._params = params
	
	def call(self, args, ctxt, stream, interp):
		if self.body is None:
			raise errors.InvalidState()

		# scopes will be pushed and popped by the Compound node handler!
		# If a return statement is interpreted in the function,
		# the Compound statement will pop the scope before the exception
		# bubbles up to here

		self._scope.push()

		params = self._params.instantiate(self._scope, args)

		ret_val = None
		try:
			interp._handle_node(self._node, self._scope, ctxt, stream)
		except errors.InterpReturn as e:
			# TODO do some type checking on the return value??
			# perhaps this should be done when initially traversing
			# the AST of the function... a dry run traversing it to find
			# return values??
			ret_val = e.value
		finally:
			self._scope.pop()

		return ret_val

class ParamListDef(object):
	"""docstring for ParamList"""
	def __init__(self, params, coords):
		super(ParamListDef, self).__init__()

		self._params = params
		self._coords = coords
	
	def instantiate(self, scope, args):
		"""Create a ParamList instance for actual interpretation

		:args: TODO
		:returns: A ParamList object

		"""
		param_instances = []

		# TODO are default values for function parameters allowed in 010?
		for param_name, param_cls in self._params:
			field = param_cls()
			field._pfp__name = param_name
			param_instances.append(field)

		if len(args) != len(param_instances):
			raise errors.InvalidArguments(
				self._coords,
				[x.__class__.__name__ for x in args],
				[x.__class__.__name__ for x in param_instances]
			)

		for x in xrange(args):
			param = param_instances[x]
			param._pfp__set_value(args[x])
			scope.add_local(param.name, param)

		return ParamList(param_instances, args)

class ParamList(object):
	"""Used for when a function is actually called. See ParamListDef
	for how function definitions store function parameter definitions"""
	def __init__(self, params):
		super(ParamList, self).__init__()
		self.params = params

		# for use by __getitem__
		self._params_map = {}
		for param in self.params:
			self._params_map[param.name] = param
	
	def __iter__(self):
		"""Return an iterator that will iterate through each of the
		parameters in order

		"""
		for param in self.params:
			yield param
	
	def __getitem__(self, name):
		if name in self._params_map:
			return self._params_map[name]
		raise KeyError(name)
	
	# def __setitem__???
