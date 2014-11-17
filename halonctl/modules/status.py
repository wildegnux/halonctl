from halonctl.modapi import Module
import arrow

# This is intended as kind of a template module, and thus will be more
# extensively documented than anything else. Reading this should give you a
# fairly good idea of how to write your own modules.
# 
# First off, the command name is inferred from the filename, minus the .py
# suffix. Thus, calling 'halonctl status' will call the module contained in
# this file.
# 
# Second, see that triple-single-quoted string at the top of the StatusModule
# class? That's called a Docstring - a string with no variable name, at the
# very top of a block. It gets automatically assigned to the __doc__ variable,
# where halonctl will find it, and use it as a description for the --help page.
# 
# Third, the 'module' variable is expected to contain a halon.modules.Module
# instance, otherwise it will complain on startup about module being missing.
# 

class StatusModule(Module):
	'''Checks node statuses'''
	
	def register_arguments(self, parser):
		# 
		# This runs on startup, and can be used to register your own arguments.
		# Each module gets their own namespace, so don't worry about stepping
		# on other modules' toes.
		# 
		# See the Python documentation for argparse for more info:
		# https://docs.python.org/2/library/argparse.html#the-add-argument-method
		# 
		
		parser.add_argument('-v', '--verbose', action='store_true',
			help="verbose output")
	
	def run(self, nodes, args):
		# 
		# This runs when the command is actually called, eg. `halonctl status`.
		# 
		# The 'nodes' argument is a NodeList containing the nodes you're
		# supposed to target. NodeList is a normal list, with a few extra
		# attributes, the only one of interest here being 'service', which is a
		# proxy that allows you to target a group of Nodes with a SOAP call.
		# 
		# If you would target all nodes with the same call anyways, it's
		# recommended that you use this proxy - in the future, it will gain the
		# ability to target all nodes in parallel, greatly speeding things up.
		# 
		# There are two ways to print to the console from run(): Use normal
		# print statements, or `yield` a tuple of table headers, then any
		# number of rows - with the latter, it will automatically be rendered
		# into an appropriately formatted table when the function returns.
		# 
		# Your custom arguments will be available on the args object, as with
		# args.verbose below.
		# 
		
		yield ('Cluster', 'Name', 'Address', 'Uptime', 'Status')
		
		for node, result in nodes.service.getUptime().iteritems():
			# If some nodes cannot be reached, mark the results as partial
			# This will cause halonctl to exit with status 99 at the end, unless
			# the --ignore-partial flag is set.
			if result[0] != 200:
				self.partial = True
			
			# Use the excellent Arrow library to format the uptime
			uptime = None
			if result[0] == 200:
				if not args.verbose:
					uptime = arrow.utcnow().replace(seconds=-result[1]).humanize().replace(' ago', '')
				else:
					uptime = result[1]
			
			if args.verbose:
				status = result[0]
			elif result[0] == 200:
				status = "OK"
			elif result[0] == 0:
				status = "Offline"
			elif result[0] == 401:
				status = "Unauthorized"
			elif result[0] == 599:
				status = "Timeout"
			else:
				status = "Error " + str(result[0])
			
			yield (node.cluster.name, node.name, node.host, uptime, status)

module = StatusModule()