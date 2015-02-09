from __future__ import print_function
import six
from halonctl.modapi import Module
from halonctl.util import ask_confirm

class UpdateStatusModule(Module):
	'''Checks update status'''
	
	def run(self, nodes, args):
		yield ('Cluster', 'Name', 'Address', 'Version', 'Update Status')
		
		versions = nodes.service.getVersion()
		
		for node, result in six.iteritems(nodes.service.updateDownloadStatus()):
			if result[0] != 200:
				self.partial = True
			
			status = None
			if result[0] == 500:
				status = "No pending update"
			elif result[0] == 200:
				status_code = int(result[1])
				if status_code <= 100:
					status = "Downloading: {0}%%".format(status_code)
				elif status_code == 101:
					status = "Checksumming..."
				elif status_code == 102:
					status = "Ready to install!"
				elif status_code == 103:
					status = "Installing"
			
			yield (node.cluster.name, node.name, node.host, versions[node][1], status)

class UpdateDownloadModule(Module):
	'''Downloads an available update'''
	
	def run(self, nodes, args):
		for node, result in six.iteritems(nodes.service.updateDownloadStart()):
			if result[0] != 200:
				self.partial = True
				print("Failure on {0}!".format(node))

class UpdateInstallModule(Module):
	'''Installs a downloaded update'''
	
	def register_arguments(self, parser):
		parser.add_argument('-y', '--yes', help="don't ask for each node",
			action='store_true')
	
	def run(self, nodes, args):
		for node in nodes:
			if args.yes or ask_confirm("Install pending update and reboot {0}?".format(node)):
				code, _ = node.service.updateInstall()
				if code != 200:
					print("Failure on {0}!".format(node))

class UpdateCancelModule(Module):
	'''Cancels a pending update'''
	
	def run(self, nodes, args):
		for node, result in six.iteritems(nodes.service.updateDownloadCancel()):
			if result[0] != 200:
				self.partial = True
				print("Failure on {0}!".format(node))

class UpdateModule(Module):
	'''Manages node updates'''
	
	submodules = {
		'status': UpdateStatusModule(),
		'download': UpdateDownloadModule(),
		'install': UpdateInstallModule(),
		'cancel': UpdateCancelModule()
	}

module = UpdateModule()
