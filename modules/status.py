from halon.modules import Module

class StatusModule(Module):
	command = "status"
	description = "Checks node statuses"
	
	def register_arguments(self, parser):
		parser.add_argument('-v', '--verbosity', help="increase output verbosity",
			action='store_true')
	
	def run(self, nodes, args):
		print "Do little status things"

module = StatusModule()
