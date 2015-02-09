from __future__ import print_function
import six
from halonctl.modapi import Module

class QueueModule(Module):
	'''Checks queue count'''

	def register_arguments(self, parser):
		parser.add_argument('-q', '--quiet', help="no per node information",
			action='store_true')
	
	def run(self, nodes, args):
		if not args.quiet:
			yield ('Node', 'Messages')
		
		totalCount = 0
		for node, result in six.iteritems(nodes.command('statd -g mail-queue-count')):
			if result[0] != 200:
				if not args.quiet:
					yield (node.name, None)
				self.partial = True
				continue
			
			count = int(result[1].all().strip().split('=')[1])
			totalCount += count
			
			if not args.quiet:
				yield (node.name, count)
		
		if not args.quiet:
			yield ('Total', totalCount)
		else:
			print(totalCount)

module = QueueModule()
