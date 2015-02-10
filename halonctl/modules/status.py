from __future__ import print_function
import six
import datetime
from halonctl.modapi import Module
from halonctl.roles import HTTPStatus

class StatusModule(Module):
	'''Checks node statuses'''
	
	def run(self, nodes, args):
		yield (u"Cluster", u"Name", u"Address", u"Uptime", u"Status")
		
		for node, (code, result) in six.iteritems(nodes.service.getUptime()):
			if code != 200:
				self.partial = True
			
			uptime = datetime.timedelta(seconds=result) if code == 200 else None
			yield (node.cluster.name, node.name, node.host, uptime, HTTPStatus(code))

module = StatusModule()
