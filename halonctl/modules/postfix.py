import six
import argparse
from time import time
from halonctl.modapi import Module

class PostfixQshapeModule(Module):
	'''Simulate postfix's qshape command'''
	
	def register_arguments(self, parser):
		parser.add_argument('-s', '--sender', action='store_true',
			help=u"use sender instead of recipient")
	
	def run(self, nodes, args):
		stats = {}
		t = time()
		limit = 5000
		offset = 0
		field = 'msgfrom' if args.sender else 'msgto'
		while True:
			askMore = False
			for node, (code, result) in six.iteritems(nodes.service.mailQueue(filter='action=DELIVER', offset=offset, limit=limit, options=None)):
				if code != 200:
					self.partial = True
				elif 'item' in result['result']:
					if len(result['result']['item']) == limit:
						askMore = True
					for msg in result['result']['item']:
						minutes = int(t - getattr(msg, 'msgts0', None)) / 60
						domain = getattr(msg, field, None)
						domain = domain.split('@')[1] if domain else '<MAILER-DAEMON>'
						email = getattr(msg, field, None);
						if domain not in stats:
							stats[domain] = {
									'10': [],
									'60': [],
									'120': [],
									'1440': [],
									'1440+': []
								}
						if minutes < 10:
							stats[domain]['10'].append(email)
						elif minutes < 60:
							stats[domain]['60'].append(email)
						elif minutes < 120:
							stats[domain]['120'].append(email)
						elif minutes < 1440:
							stats[domain]['1440'].append(email)
						else:
							stats[domain]['1440+'].append(email)
			if not askMore:
				break
			offset = offset + limit

		yield ['Domain', 'Total', '10', '60', '120', '1440', '1440+']
		def total_compare(d1, d2):
			return sum([len(y) for x, y in d2.iteritems()]) - sum([len(y) for x, y in d1.iteritems()])
		for domain in sorted(stats, key=stats.get, cmp=total_compare):
			data = stats[domain]
			total = sum([len(y) for x, y in data.iteritems()])
			yield [domain, total, len(data['10']), len(data['60']), len(data['120']), len(data['1440']), len(data['1440+'])]

class PostfixModule(Module):
	'''Simulate postfix commands'''
	
	submodules = {
		'qshape': PostfixQshapeModule()
	}

module = PostfixModule()
