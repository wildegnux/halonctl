from __future__ import print_function
import six
from halonctl.modapi import Module
import datetime

class StatusModule(Module):
	'''Checks node statuses'''
	
	def run(self, nodes, args):
		yield (u"Cluster", u"Name", u"Address", u"Uptime", u"Status")
		
		for node, result in six.iteritems(nodes.service.getUptime()):
			if result[0] != 200:
				self.partial = True
			
			uptime = None
			if result[0] == 200:
				uptime = datetime.timedelta(seconds=result[1])
			
			if args.raw:
				status = result[0]
			elif result[0] == 200:
				status = u"OK"
			elif result[0] == 0:
				status = u"Offline"
			elif result[0] == 401:
				status = u"Unauthorized"
			elif result[0] == 599:
				status = u"Timeout"
			else:
				status = u"Error {0}".format(result[0])
			
			yield (node.cluster.name, node.name, node.host, uptime, status)

module = StatusModule()
