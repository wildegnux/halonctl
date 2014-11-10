from halon.modules import Module

class StatusModule(Module):
	command = "status"
	description = "Checks node statuses"
	
	def register_arguments(self, parser):
		parser.add_argument('-v', '--verbose', help="verbose output",
			action='store_true')
	
	def run(self, nodes, args):
		yield ('Cluster', 'Name', 'Address', 'Status')
		
		for node, result in nodes.service.login():
			if args.verbose:
				status = str(result[0])
			elif result[0] == 200:
				status = "OK"
			elif result[0] == 0:
				status = "Offline"
			elif result[0] == 401:
				status = "Unauthorized"
			else:
				status = "Error " + str(result[0])
			
			yield (node.cluster.name, node.name, node.host, status)

module = StatusModule()
