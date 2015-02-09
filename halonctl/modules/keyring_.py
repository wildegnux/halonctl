from __future__ import print_function
import six
import getpass
import keyring
from halonctl.modapi import Module
from halonctl.util import ask_confirm

class KeyringStatusModule(Module):
	'''Checks the authorization status of all nodes'''
	
	def run(self, nodes, args):
		yield (u'Cluster', u'Name', u'Address', u'Authorized?')
		
		for node, result in six.iteritems(nodes.service.login()):
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
			prefix = u"{cluster} / {name} ({host})".format(cluster=node.cluster.name, name=node.name, host=node.host)
			if not node.username:
				print(u"{prefix} - No username configured for node or cluster".format(prefix=prefix))
				continue
			
			result = node.service.login()[0]
			if result == 0:
				print(u"{prefix} - Node is unreachable :(".format(prefix=prefix))
			elif result == 200:
				# Follow the good ol' rule of silence
				pass
			elif result == 401:
				print(u"{prefix} - Enter password (blank to skip):".format(prefix=prefix))
				while True:
					password = getpass.getpass(u"{user}@{host}> ".format(user=node.username, host=node.host))
					if not password:
						break
					
					node.password = password
					
					result = node.service.login()[0]
					if result == 200:
						keyring.set_password(node.host, node.username, password)
						break
					elif result == 401:
						print(u"Invalid login, try again")
					elif result == 0:
						print(u"The node has gone away")
						break
					else:
						print(u"An error occurred, code {0}".format(result))
						break
			else:
				print(u"An error occurred, code {0}".format(result))

class KeyringLogoutModule(Module):
	'''Deletes stored credentials for the node(s)'''
	
	def register_arguments(self, parser):
		parser.add_argument('-y', '--yes', action='store_true',
			help=u"don't ask for each node")
	
	def run(self, nodes, args):
		for node in nodes:
			if not keyring.get_password(node.host, node.username):
				continue
			
			if args.yes or ask_confirm(u"Log out from {cluster} / {name} ({host})?".format(cluster=node.cluster.name, name=node.name, host=node.host)):
				keyring.delete_password(node.host, node.username)

class KeyringModule(Module):
	'''Manages the keyring (credential store)'''
	
	submodules = {
		'status': KeyringStatusModule(),
		'login': KeyringLoginModule(),
		'logout': KeyringLogoutModule()
	}

module = KeyringModule()
