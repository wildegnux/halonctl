from halon.modules import Module

class StatusModule(Module):
	command = "status"
	description = "Checks node statuses"
	
	def register_arguments(self, parser):
		parser.add_argument('-v', '--verbosity', help="increase output verbosity",
			action='store_true')
	
	def run(self, nodes, args):
		rows = [('Name', 'Address', 'Status')]
		for node, result in nodes.login():
			if result[0] == 200:
				status = "Online"
			elif result[0] == 401:
				status = "Unauthorized"
			else:
				status = "Error " + result[0]
			
			rows.append((node.name, node.host, status))
		
		return rows

module = StatusModule()
