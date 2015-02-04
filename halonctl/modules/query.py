import argparse
from halonctl.modapi import Module
from halonctl.util import hql_from_filters, filter_timestamp_re, ask_confirm, from_base64

class QueryModule(Module):
	'''Queries emails and performs actions'''
	
	def register_arguments(self, parser):
		parser.add_argument('--history', action='store_true',
			help="query history instead of queue")
		parser.add_argument('--offset', type=int,
			help="offset when just showing emails (default: 0)")
		parser.add_argument('--limit', type=int,
			help="limit when just showing emails (default: 100)")
		parser.add_argument('--debug-hql', action='store_true',
			help="print resulting hql queries, for debugging")
		
		tzgroup = parser.add_mutually_exclusive_group()
		tzgroup.add_argument('--utc', dest='timezone', action='store_const', const=0,
			help="timestamps are given in UTC")
		tzgroup.add_argument('--timezone', dest='timezone', type=float,
			help="timestamps are given in this UTC offset, in hours")
		
		actiongroup = parser.add_mutually_exclusive_group()
		actiongroup.add_argument('--delete', dest='action', action='store_const', const='delete',
			help="delete the matching emails (this can't be undone!)")
		actiongroup.add_argument('--deliver', dest='action', action='store_const', const='deliver',
			help="attempt to deliver the matching emails right away")
		actiongroup.add_argument('--deliver-duplicate', dest='action', action='store_const', const='deliver-duplicate',
			help="attempt to deliver a copy of the matching emails")
		
		parser.add_argument('filter', nargs=argparse.REMAINDER, metavar="...",
			help="HQL query matching all targeted emails; use 'id=X' to target a single one")
		
		parser.epilog = "\"{YYYY-mm-dd HH:mm:ss}\" can be used to insert timestamps into queries. For safety reasons, if this is used, you must use --utc or --timezone to mark what timezone the timestamp is in."
	
	def run(self, nodes, args):
		# Prevent accidents caused by calls such as "--delete --limit ..."
		if args.action and (args.offset or args.limit):
			print "--offset/--limit cannot be used together with actions!"
			self.exitcode = 1
			return

		if args.action and args.history:
			print "--history cannot be used together with actions!"
			self.exitcode = 1
			return
		
		# Timestamp placeholders need a timezone specified!
		for s in args.filter:
			if args.timezone is None and filter_timestamp_re.search(s):
				print "Timestamp placeholders need a --timezone/--utc parameter!"
				self.exitcode = 1
				return
		
		# Make a proper filter string
		hql = hql_from_filters(args.filter, args.timezone)
		if args.debug_hql:
			print hql
		
		# Dispatch!
		if args.action is None:
			return self.do_show(nodes, args, hql)
		elif args.action == "deliver":
			return self.do_deliver(nodes, args, hql, False)
		elif args.action == "deliver-duplicate":
			return self.do_deliver(nodes, args, hql, True)
		elif args.action == "delete":
			return self.do_delete(nodes, args, hql)
	
	def do_show(self, nodes, args, hql):
		yield ('Cluster', 'Node', 'From', 'To', 'Subject')
		
		source = getattr(nodes.service, 'mailHistory' if args.history else 'mailQueue')
		for node, result in source(filter=hql, offset=args.offset or None, limit=args.limit or 100).iteritems():
			if result[0] != 200:
				print "Failure on {0}: {1}".format(node, result[1])
				self.partial = True
			elif 'item' in result[1]['result']:
				for msg in result[1]['result']['item']:
					msg['msgsubject'] = from_base64(msg['msgsubject'])
					yield (node.cluster.name, node.name, msg['msgfrom'], msg['msgto'], msg['msgsubject'])
	
	def do_deliver(self, nodes, args, hql, duplicate):
		if not hql and not ask_confirm("You have no filter, do you really want to try to deliver everything?", False):
			return
		
		for node, result in nodes.service.mailQueueRetryBulk(filter=hql, duplicate=duplicate).iteritems():
			if result[0] != 200:
				print "Failure on {0}: {1}".format(node, result[1])
	
	def do_delete(self, nodes, args, hql):
		if not hql and not ask_confirm("You have no filter, do you really want to delete everything!?", False):
			return
		
		for node, result in nodes.service.mailQueueDeleteBulk(filter=hql).iteritems():
			if result[0] != 200:
				print "Failure on {0}: {1}".format(node, result[1])

module = QueryModule()
