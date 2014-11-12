from halon.modules import Module
from base64 import b64encode, b64decode

class QueueModule(Module):
	'''Checks queue count'''

	def register_arguments(self, parser):
		parser.add_argument('-q', '--quiet', help="no per node information",
			action='store_true')

	def run(self, nodes, args):
		if not args.quiet:
			yield ('Node', 'Messages')
		totalCount = 0
		for node, result in nodes.service.commandRun(argv={
				'item': [b64encode(i) for i in ['statd', '-g', 'mail-queue-count']]
				}).iteritems():
			if result[0] != 200:
				if not args.quiet:
					yield (node.name, '-')
				self.partial = True
				continue
			
			output = ''
			while True:
				ret, data = node.service.commandPoll(commandid=result[1])
				if ret != 200:
					break
				if hasattr(data, 'item'):
					output += "".join([b64decode(i) for i in data.item])
			count = long(output.strip().split('=')[1])
			totalCount += count
			if not args.quiet:
				yield (node.name, count)
		if not args.quiet:
			yield ('Total', totalCount)
		else:
			print totalCount

module = QueueModule()
