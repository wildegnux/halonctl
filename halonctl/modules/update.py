from __future__ import print_function
import six
from halonctl.modapi import Module
from halonctl.util import ask_confirm
from halonctl.roles import StatusCode, HTTPStatus

class UpdateStatusCode(StatusCode):
	codes = {
		101: u"Checksumming...",
		102: u"Ready to install!",
		103: u"Installing...",
		None: u"No pending update"
	}
	
	def get_default(self, code):
		if code <= 100:
			return u"Downloading: {0}%".format(code)
		return super(UpdateStatusCode, self).get_default(code)

class UpdateStatusModule(Module):
	'''Checks update status'''
	
	def run(self, nodes, args):
		yield (u"Cluster", u"Name", u"Address", u"Version", u"Update Status")
		
		versions = nodes.service.getVersion()
		
		for node, (code, result) in six.iteritems(nodes.service.updateDownloadStatus()):
			if code != 200 and code != 500:
				self.partial = True
			
			status = UpdateStatusCode(int(result) if code == 200 else None)
			yield (node.cluster, node, node.host, versions[node][1], status)

class UpdateDownloadModule(Module):
	'''Downloads an available update'''
	
	def run(self, nodes, args):
		for node, (code, result) in six.iteritems(nodes.service.updateDownloadStart()):
			if code != 200:
				self.partial = True
				print(u"Failure on {0}!".format(node))

class UpdateInstallModule(Module):
	'''Installs a downloaded update'''
	
	def register_arguments(self, parser):
		parser.add_argument('-y', '--yes', action='store_true',
			help=u"don't ask for each node")
	
	def run(self, nodes, args):
		for node in nodes:
			if args.yes or ask_confirm(u"Install pending update and reboot {0}?".format(node)):
				code, _ = node.service.updateInstall()
				if code != 200:
					print(u"Failure on {0}!".format(node))

class UpdateCancelModule(Module):
	'''Cancels a pending update'''
	
	def run(self, nodes, args):
		for node, (code, result) in six.iteritems(nodes.service.updateDownloadCancel()):
			if code != 200:
				self.partial = True
				print(u"Failure on {0}!".format(node))

class UpdateModule(Module):
	'''Manages node updates'''
	
	submodules = {
		'status': UpdateStatusModule(),
		'download': UpdateDownloadModule(),
		'install': UpdateInstallModule(),
		'cancel': UpdateCancelModule()
	}

module = UpdateModule()
