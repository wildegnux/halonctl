from __future__ import print_function
import six
import argparse
from halonctl.modapi import Module
from halonctl.util import hql_from_filters, filter_timestamp_re, ask_confirm, from_base64
from halonctl.roles import UTCDate

class QueryModule(Module):
	'''Queries emails and performs actions'''
	
	def register_arguments(self, parser):
		parser.add_argument('--history', action='store_true',
			help=u"query history instead of queue")
		parser.add_argument('--offset', type=int,
			help=u"offset when just showing emails (default: 0)")
		parser.add_argument('--limit', type=int,
			help=u"limit when just showing emails (default: 100)")
		parser.add_argument('--debug-hql', action='store_true',
			help=u"print resulting hql queries, for debugging")
		parser.add_argument('--fields',
			help=u"print selected fields")
		parser.add_argument('-y', '--yes', action='store_true',
			help=u"don't ask to perform wildcard actions")
		
		tzgroup = parser.add_mutually_exclusive_group()
		tzgroup.add_argument('--utc', dest='timezone', action='store_const', const=0,
			help=u"timestamps are given in UTC")
		tzgroup.add_argument('-t', '--timezone', dest='timezone', type=float,
			help=u"timestamps are given in this UTC offset, in hours")
		
		actiongroup = parser.add_mutually_exclusive_group()
		actiongroup.add_argument('--delete', dest='action', action='store_const', const='delete',
			help=u"delete the matching emails (this can't be undone!)")
		actiongroup.add_argument('--deliver', dest='action', action='store_const', const='deliver',
			help=u"attempt to deliver the matching emails right away")
		actiongroup.add_argument('--deliver-duplicate', dest='action', action='store_const', const='deliver-duplicate',
			help=u"attempt to deliver a copy of the matching emails")
		
		parser.add_argument('filter', nargs=argparse.REMAINDER, metavar="...",
			help=u"HQL query matching all targeted emails; use 'id=X' to target a single one")
		
		parser.epilog = u"\"{YYYY-mm-dd HH:mm:ss}\" can be used to insert timestamps into queries. For safety reasons, if this is used, you must use --utc or --timezone to mark what timezone the timestamp is in."
	
	def run(self, nodes, args):
		# Prevent accidents caused by calls such as "--delete --limit ..."
		if args.action and (args.offset or args.limit):
			print(u"--offset/--limit cannot be used together with actions!")
			self.exitcode = 1
			return
		
		if args.action and args.history:
			print(u"--history cannot be used together with actions!")
			self.exitcode = 1
			return
		
		if args.action and args.fields:
			print(u"--fields cannot be used together with actions!")
			self.exitcode = 1
			return
		
		# Build an array with all supported fields for a particular source
		supported_fields = ['action', 'actionid', 'cluster', 'from', 'helo', 'ip',
			'messageid', 'node', 'queueid', 'sasl', 'server', 'size', 'subject',
			'time', 'to', 'transport']
		fields = []
		
		if args.history:
			supported_fields += ['historyid']
			fields = ['cluster', 'node', 'messageid', 'from', 'to', 'subject']
		else:
			supported_fields += ['quarantine', 'retry']
			fields = ['cluster', 'node', 'messageid', 'queueid', 'from', 'to', 'subject']
		
		if args.fields:
			fields = supported_fields if args.fields == '-' else args.fields.split(',')
			
		for f in fields:
			if not f in supported_fields:
				print(u"Field '{0}' is not available!".format(f))
				print(u"Available fields:")
				for p in supported_fields:
					print(u" {0}".format(p))
				self.exitcode = 1
				return
		
		# Timestamp placeholders need a timezone specified!
		for s in args.filter:
			if args.timezone is None and filter_timestamp_re.search(s):
				print(u"Timestamp placeholders need a --timezone/--utc parameter!")
				self.exitcode = 1
				return
		
		# Make a proper filter string
		hql = hql_from_filters(args.filter, args.timezone)
		if args.debug_hql:
			print(uhql)
		
		# Dispatch!
		if args.action is None:
			return self.do_show(nodes, args, hql, fields)
		elif args.action == 'deliver':
			return self.do_deliver(nodes, args, hql, False)
		elif args.action == 'deliver-duplicate':
			return self.do_deliver(nodes, args, hql, True)
		elif args.action == 'delete':
			return self.do_delete(nodes, args, hql)
	
	def do_show(self, nodes, args, hql, fields):
		yield fields
		
		source = getattr(nodes.service, 'mailHistory' if args.history else 'mailQueue')
		for node, (code, result) in six.iteritems(source(filter=hql, offset=args.offset or None, limit=args.limit or 100)):
			if code != 200:
				self.partial = True
			elif 'item' in result['result']:
				for msg in result['result']['item']:
					p = []
					for f in fields:
						if f == 'action': p.append(getattr(msg, 'msgaction', None))
						elif f == 'actionid': p.append(getattr(msg, 'msgactionid', None))
						elif f == 'cluster': p.append(node.cluster.name)
						elif f == 'from': p.append(getattr(msg, 'msgfrom', None))
						elif f == 'helo': p.append(getattr(msg, 'msghelo', None)) # Added in 3.3
						elif f == 'historyid': p.append(getattr(msg, 'id', None))
						elif f == 'ip': p.append(getattr(msg, 'msgfromserver', None))
						elif f == 'messageid': p.append(getattr(msg, 'msgid', None))
						elif f == 'node': p.append(node.name)
						elif f == 'quarantine': p.append(getattr(msg, 'msgquarantine', None))
						elif f == 'queueid': p.append(getattr(msg, 'msgqueueid' if args.history else 'id', None))
						elif f == 'retry': p.append(getattr(msg, 'msgretries', None))
						elif f == 'sasl': p.append(getattr(msg, 'msgsasl', None))
						elif f == 'server': p.append(getattr(msg, 'msglistener', None))
						elif f == 'size': p.append(getattr(msg, 'msgsize', None)) # Added in 3.3
						elif f == 'subject': p.append(from_base64(getattr(msg, 'msgsubject', None)))
						elif f == 'time': p.append(UTCDate(getattr(msg, 'msgts0', None), args.timezone))
						elif f == 'to': p.append(getattr(msg, 'msgto', None))
						elif f == 'transport': p.append(getattr(msg, 'msgtransport', None))
					yield p
	
	def do_deliver(self, nodes, args, hql, duplicate):
		if not hql and not args.yes and not ask_confirm(u"You have no filter, do you really want to try to deliver everything?", False):
			return
		
		for node, (code, result) in six.iteritems(nodes.service.mailQueueRetryBulk(filter=hql, duplicate=duplicate)):
			if code != 200:
				print(u"Failure on {0}: {1}".format(node, result))
	
	def do_delete(self, nodes, args, hql):
		if not hql and not args.yes and not ask_confirm(u"You have no filter, do you really want to delete everything!?", False):
			return
		
		for node, (code, result) in six.iteritems(nodes.service.mailQueueDeleteBulk(filter=hql)):
			if code != 200:
				print(u"Failure on {0}: {1}".format(node, result))

module = QueryModule()
