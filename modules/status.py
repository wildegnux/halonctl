from halon.modules import Module

class StatusModule(Module):
	command = "status"
	description = "Checks node statuses"
	
	def register_arguments(self, parser):
		parser.add_argument('-v', '--verbosity', help="increase output verbosity",
			action='store_true')
	
	def run(self, nodes, args):
		rows = [('Name', 'Address', 'Status')]
		for node in nodes:
			status = "Online"
			try:
				node.client.service.login()
			except Exception, e:
				if e.message[0] == 401:
					status = "Unauthorized"
				else:
					status = "Error"
			
			rows.append((node.name, node.host, status))
		return rows

module = StatusModule()
