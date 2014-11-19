class Module(object):
	'''Base class for all modules.
	
	:ivar int exitcode: Change the program's exit code, to signal an error. (default: 0)
	:ivar bool partial: Set to True if the results are partial, will cause the program to exit with code 99 unless ``--ignore-partial`` is specified on the commandline.
	:ivar dict submodules: If this module has any submodules of its own, specify them as { 'name': ModuleInstance() }, and do not implement register_arguments() or run().
	'''
	
	exitcode = 0
	partial = False
	
	submodules = {}
	
	def register_arguments(self, parser):
		'''Subclass hook for registering commandline arguments.
		
		Every module has its own subparser, and thus does not have to worry
		about clobbering other modules' arguments by accident, but should avoid
		registering arguments that conflict with ``halonctl``'s own arguments.
		
		Example::
		
		    def register_arguments(self, parser):
		        parser.add_argument('-t', '--test',
		            help="Lorem ipsum dolor sit amet")
		
		See Python's argparse_ module for more information, particularly the
		part about subcommands_.
		
		.. _argparse: https://docs.python.org/2/library/argparse.html
		.. _subcommands: https://docs.python.org/2/library/argparse.html#sub-commands
		
		:param argparse.ArgumentParser parser: The Argument Parser arguments should be registered on
		'''
		
		# The default implementation adds subcommands if there are any
		if self.submodules:
			subparsers = parser.add_subparsers(dest=type(self).__name__ + '_mod_name', metavar='subcommand')
			subparsers.required = True
			for name, mod in self.submodules.iteritems():
				p = subparsers.add_parser(name, help=mod.__doc__)
				p.set_defaults(**{type(self).__name__ + '_mod': mod})
				mod.register_arguments(p)
	
	def run(self, nodes, args):
		'''Subclass hook for running the command.
		
		This is invoked when ``halonctl`` is run with the module's name as an
		argument, and should contain the actual command logic.
		
		To output data, the preferred way is to ``yield`` a table, one row at a
		time, with the first row being the header. This will, by default,
		output an ASCII art table, but will also allow other formatters to
		correctly process the data::
		
		    def run(self, nodes, args):
		        # First, yield a header...
		        yield ("Cluster", "Node", "Result")
		        
		        # Make a call on all given nodes
		        for node, result in nodes.service.someCall(arg=123).iteritems():
		            # Mark the results as partial if a node isn't responding
		            if result[0] != 200:
		                self.partial = True
		                continue
		            
		            # Yield a row with the response
		            yield (node.cluster.name, node.name, results[1])
		
		Of course, if your command's purpose isn't to retrieve data, you should
		not do this, and instead adhere to the "rule of silence"; use prints,
		and say nothing unless there's an error::
		
		    def run(self, nodes, args):
		        for node, result in nodes.service.someCall(arg=123).iteritems():
		            if result[0] != 200:
		                print "Failure on {node}: {result}".format(node=node, result=result[1])
		'''
		# The default implementation simply delegates to a subcommand
		if self.submodules:
			return getattr(args, type(self).__name__ + '_mod').run(nodes, args)
