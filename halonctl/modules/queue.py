from __future__ import print_function
import six
from halonctl.modapi import Module

class QueueModule(Module):
	'''Checks queue count'''

	def register_arguments(self, parser):
		parser.add_argument('-q', '--quiet', action='store_true',
			help=u"no per node information")
	
	def run(self, nodes, args):
		if not args.quiet:
			yield (u"Node", u"Messages")
		
		totalCount = 0
		for node, (code, result) in six.iteritems(nodes.command('statd -g mail-queue-count')):
			if code != 200:
				if not args.quiet:
					yield (node.name, None)
				self.partial = True
				continue
			
			count = int(result.all().strip().split('=')[1])
			totalCount += count
			
			if not args.quiet:
				yield (node.name, count)
		
		if not args.quiet:
			yield (u"Total", totalCount)
		else:
			print(totalCount)

module = QueueModule()
