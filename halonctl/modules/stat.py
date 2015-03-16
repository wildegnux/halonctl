from __future__ import print_function
import six
import re
from collections import OrderedDict
from halonctl.modapi import Module
from halonctl.roles import UTCDate

counters = [
	'system-cpu-usage',
	'system-mem-usage',
	'system-storage-iops',
	'system-storage-latency',
	'system-storage-usage',
	'system-swap-iops',
	'system-swap-usage',
	'mail-license-count',
	'mail-quarantine-count',
	'mail-queue-count',
]

interface_prefix = 'interface'
interface_counters = [
	'bandwidth',
	'packets',
]

class StatModule(Module):
	'''Reads stat counters'''

	def register_arguments(self, parser):
		parser.add_argument('-s', '--sum', action='store_true',
			help=u"print only the sum of all nodes")
		parser.add_argument('key', nargs='*',
			help=u"the counter to read")
	
	def run(self, nodes, args):
		if len(args.key) == 0:
			return self.run_help(nodes, args)
		elif len(args.key) == 1:
			return self.run_statd(nodes, args)
		elif len(args.key) == 3:
			return self.run_statlist(nodes, args)
		else:
			print(u"Pass in either 1 counter, or three keys for stat() lookup.")
			print(u"For stat() lookup, pass in a . for the parts you don't care about.")
			self.exitcode = 1
			return self.run_help(nodes, args)
	
	def run_help(self, nodes, args):
		print(u"Available counters (all nodes):")
		for counter in counters:
			print(u"  - {0}".format(counter))
		
		for node, (code, result) in six.iteritems(nodes.command('ifconfig')):
			print(u"")
			print(u"{node.name}:".format(node=node))
			interfaces = re.findall(r'^([\w\d]+):.*$', result.all(), re.MULTILINE)
			for interface in interfaces:
				for counter in interface_counters:
					print(u"  - {prefix}-{interface}-{counter}".format(
						prefix=interface_prefix, interface=interface, counter=counter))
	
	def run_statd(self, nodes, args):
		sum_ = 0
		is_first = True
		for node, (code, result) in six.iteritems(nodes.command('statd', '-g', args.key[0])):
			if code != 200:
				self.partial = True
				continue
			
			data = OrderedDict()
			for line in [line.strip() for line in result.all().split('\n')]:
				if not line:
					continue
				
				key, count = line.split('=', 2)
				count = int(count) if '.' not in count else float(count)
				data[key] = count
				sum_ += count
			
			if not args.sum:
				if is_first:
					yield [u"Node"] + list(data.keys())
					is_first = False
				yield [node] + list(data.values())
		
		if args.sum:
			print(sum_)
	
	def run_statlist(self, nodes, args):
		if not args.sum:
			yield (u"Node", u"Key 1", u"Key 2", u"Key 3", u"Count", u"Updated", u"Created")
		
		sum_ = 0
		keys = [k if k != '.' else None for k in args.key]
		for node, (code, result) in six.iteritems(nodes.service.statList(*keys, limit=10000)):
			if code != 200:
				self.partial = True
				continue
			
			for res in result.item:
				sum_ += res.count
				if not args.sum:
					yield (node, res.key1, res.key2, res.key3, res.count, UTCDate(res.updated), UTCDate(res.created))
		
		if args.sum:
			print(sum_)

module = StatModule()
