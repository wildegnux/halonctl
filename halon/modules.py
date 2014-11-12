class Module(object):
	exitcode = 0
	partial = False
	
	submodules = {}
	
	def register_arguments(self, parser):
		# The default implementation adds subcommands if there are any
		if self.submodules:
			subparsers = parser.add_subparsers(metavar='subcommand')
			for name, mod in self.submodules.iteritems():
				p = subparsers.add_parser(name, help=mod.__doc__)
				p.set_defaults(_mod=mod)
	
	def run(self, nodes, args):
		# The default implementation simply delegates to a subcommand
		if self.submodules:
			return args._mod.run(nodes, args)
