from __future__ import print_function
import six
from halonctl.modapi import Module
import datetime

class StatusModule(Module):
	'''Checks node statuses'''
	
	def run(self, nodes, args):
		yield (u"Cluster", u"Name", u"Address", u"Uptime", u"Status")
		
		for node, (code, result) in six.iteritems(nodes.service.getUptime()):
			if code != 200:
				self.partial = True
			
			uptime = None
			if code == 200:
				uptime = datetime.timedelta(seconds=result)
			
			if args.raw:
				status = code
			elif code == 200:
				status = u"OK"
			elif code == 0:
				status = u"Offline"
			elif code == 401:
				status = u"Unauthorized"
			elif code == 599:
				status = u"Timeout"
			else:
				status = u"Error {0}".format(code)
			
			yield (node.cluster.name, node.name, node.host, uptime, status)

module = StatusModule()
