from __future__ import print_function
import os
import re
import six
from halonctl.modapi import Module
from halonctl.roles import HTTPStatus
from halonctl.util import from_base64, to_base64

FRAGMENTS = [
	'system_authentication_script',
	'transport_flow',
]
MIMES = {
	'text/plain': 'txt',
	'text/csv': 'csv',
}
SCRIPT_RE = re.compile(r'\w+_flow__\d+')
CLEAN_RE = re.compile(r'script "([0-9a-zA-Z=]+)"')

class HSLDumpModule(Module):
	'''Dumps scripts from a node'''
	
	def register_arguments(self, parser):
		parser.add_argument('path', nargs='?', default='.',
			help=u"directory to export into")
	
	def run(self, nodes, args):
		# It doesn't make sense to dump from multiple nodes into one directory
		node = nodes[0]
		code, result = node.service.configKeys()
		
		if code != 200:
			self.exitcode = 1
			return HTTPStatus(code)
		
		for item in result.item:
			if SCRIPT_RE.match(item.name):
				self.dump_script(item, args)
			elif item.name in FRAGMENTS:
				self.dump_fragment(item, args)
			elif item.name.startswith('file__'):
				self.dump_file(item, args)
	
	def dump_script(self, item, args):
		extension = 'hsl.bin'
		body = item.params.item[-1]
		
		match = CLEAN_RE.match(body)
		if match:
			extension = 'hsl'
			body = from_base64(match.group(1))
		
		# Some script types have an extra data field in the middle
		if len(item.params.item) > 2:
			body = u"# META: {meta}\n{body}".format(
				meta=item.params.item[1],
				body=body,
			)
		
		self.dump(args, item.name, extension, body)
	
	def dump_fragment(self, item, args):
		self.dump(args, item.name, 'hsl', from_base64(item.params.item[1]))
	
	def dump_file(self, item, args):
		extension = MIMES.get(item.params.item[1], 'bin')
		body = u"# NAME: {name}\n{body}".format(
			name=item.params.item[0],
			body=from_base64(item.params.item[2])
		)
		self.dump(args, item.name, extension, body)
	
	def dump(self, args, name, extension, body):
		if not os.path.exists(args.path):
			os.makedirs(args.path)
		
		path = os.path.join(args.path, u"{0}.{1}".format(name, extension))
		with open(path, 'w') as f:
			f.write(body)
		return path

class HSLModule(Module):
	'''Manages HSL scripts'''
	
	submodules = {
		'dump': HSLDumpModule(),
	}

module = HSLModule()
