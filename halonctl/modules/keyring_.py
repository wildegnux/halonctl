import getpass
import keyring
from halonctl.modapi import Module
from halonctl.util import ask_confirm

class KeyringStatusModule(Module):
	'''Checks the authorization status of all nodes'''
	
	def run(self, nodes, args):
		yield ('Cluster', 'Name', 'Address', 'Authorized?')
		
		for node, result in nodes.service.login().iteritems():
			if result[0] != 200:
				self.partial = True
			
			status = None
			if result[0] == 200:
				status = True
			elif result[0] == 401:
				status = False
			
			yield (node.cluster.name, node.name, node.host, status)

class KeyringLoginModule(Module):
	'''Attempts to log in to the node(s)'''
	
	def run(self, nodes, args):
		for node in nodes:
			prefix = "{cluster} / {name} ({host})".format(cluster=node.cluster.name, name=node.name, host=node.host)
			if not node.username:
				print prefix + " - No username configured for node or cluster"
				continue
			
			result = node.service.login()[0]
			if result == 0:
				print prefix + " - Node is unreachable :("
			elif result == 200:
				# Follow the good ol' rule of silence
				pass
			elif result == 401:
				print prefix + " - Enter password (blank to skip):"
				while True:
					password = getpass.getpass("{user}@{host}> ".format(user=node.username, host=node.host))
					if password == "":
						break
					
					node.password = password
					
					result = node.service.login()[0]
					if result == 200:
						keyring.set_password(node.host, node.username, password)
						break
					elif result == 401:
						print "Invalid login, try again"
					elif result == 0:
						print "The node has gone away"
						break
					else:
						print "An error occurred, code {0}".format(result)
						break
			else:
				print "An error occurred, code {0}".format(result)

class KeyringLogoutModule(Module):
	'''Deletes stored credentials for the node(s)'''
	
	def register_arguments(self, parser):
		parser.add_argument('-y', '--yes', help="don't ask for each node",
			action='store_true')
	
	def run(self, nodes, args):
		for node in nodes:
			if not keyring.get_password(node.host, node.username):
				continue
			
			if args.yes or ask_confirm("Log out from {cluster} / {name} ({host})?".format(cluster=node.cluster.name, name=node.name, host=node.host)):
				keyring.delete_password(node.host, node.username)

class KeyringModule(Module):
	'''Manages the keyring (credential store)'''
	
	submodules = {
		'status': KeyringStatusModule(),
		'login': KeyringLoginModule(),
		'logout': KeyringLogoutModule()
	}

module = KeyringModule()
