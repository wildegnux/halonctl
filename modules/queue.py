from halon.modules import Module
from base64 import b64encode, b64decode

class QueueModule(Module):
	'''Checks queue count'''

	def register_arguments(self, parser):
		parser.add_argument('-v', '--verbose', help="verbose output",
			action='store_true')

	def run(self, nodes, args):
		yield ('Node', 'Messages')
		totalCount = 0
		for node, result in nodes.service.commandRun(argv={
				'item': [b64encode(i) for i in ['statd', '-g', 'mail-queue-count']]
				}):
			output = ''
			while True:
				ret, data = node.client.service.commandPoll(commandid=result[1])
				if ret != 200:
					break
				if hasattr(data, 'item'):
					output += "".join([b64decode(i) for i in data.item])
			count = long(output.strip().split('=')[1])
			totalCount += count
			yield (node.name, count)
		yield ('Total', totalCount)

module = QueueModule()
