from halon.modules import Module
import base64

class QueueModule(Module):
	'''Checks queue count'''
	
	def register_arguments(self, parser):
		parser.add_argument('-v', '--verbose', help="verbose output",
			action='store_true')
	
	def run(self, nodes, args):
		yield ('Node', 'Messages')
		totalCount = 0
		for node, result in nodes.service.commandRun(argv=[
				{'item':[
				base64.b64encode('statd'),
				base64.b64encode('-g'),
				base64.b64encode('mail-queue-count'),
				]}]):
			output = ''
			while True:	
				ret, data = node.client.service.commandPoll(commandid=result[1])
				if ret != 200:
					break
				if hasattr(data, 'item'):
					output += "".join([base64.b64decode(i) for i in data.item])
			count = long(output.strip().split('=')[1])
			totalCount += count
			yield (node.name, count)
		yield ('Total', totalCount)

module = QueueModule()
