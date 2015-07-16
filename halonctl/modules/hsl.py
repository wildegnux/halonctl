from __future__ import print_function
import sys
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



class BaseFile(Module):
	filename = 'unnamed'
	extension = 'bin'
	
	name = None
	meta = None
	body = None
	
	def __init__(self, item=None):
		if item:
			self.load_data(item)
	
	def load_data(self, item):
		'''Loads data from a SOAP payload.'''
		pass
	
	def to_data(self):
		'''Returns a SOAP payload.'''
		pass
	
	def deserialize(self, data, extension):
		'''Deserializes data read from a file.'''
		pass
	
	def serialize(self):
		'''Serializes data for writing to a file.'''
		data = u""
		if self.name:
			data += u"//= NAME: {0}\n".format(self.name)
		if self.meta:
			data += u"//= META: {0}\n".format(self.meta)
		data += self.body or u""
		return data
	
	def path(self, args):
		'''Constructs a local path to the file.'''
		filename = u'{0}.{1}'.format(self.filename, self.extension)
		return os.path.join(args.path, filename)
	
	def save(self, args):
		if not os.path.exists(args.path):
			os.makedirs(args.path)
		
		with open(self.path(args), 'w') as f:
			f.write(self.serialize())
	
	def load(self, args):
		with open(self.path(args)) as f:
			self.deserialize(f.read())

class ScriptFile(BaseFile):
	extension = 'hsl.bin'
	
	def load_data(self, item):
		self.filename = item.name
		self.name = item.params.item[0]
		self.body = item.params.item[-1]
		
		match = CLEAN_RE.match(self.body)
		if match:
			self.extension = 'hsl'
			self.body = from_base64(match.group(1))
		else:
			print(u"WARNING: Cannot decode script containing visual blocks: {0}".format(item.name), file=sys.stderr)
		
		# Some kinds of scripts (ACL Flows) have an extra middle parameter...
		if len(item.params.item) > 2:
			self.meta = item.params.item[1]

class FragmentFile(BaseFile):
	extension = 'hsl'
	
	def load_data(self, item):
		self.filename = item.name
		self.name = item.params.item[0]
		self.body = from_base64(item.params.item[1])

class TextFile(BaseFile):
	extension = 'txt'
	
	def load_data(self, item):
		self.filename = item.name
		self.extension = MIMES.get(item.params.item[1], 'bin')
		self.name = item.params.item[0]
		self.body = from_base64(item.params.item[2])

def files_from_result(result):
	for item in result.item:
		if SCRIPT_RE.match(item.name):
			yield ScriptFile(item)
		elif item.name in FRAGMENTS:
			yield FragmentFile(item)
		elif item.name.startswith('file__'):
			yield TextFile(item)



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
		
		for f in files_from_result(result):
			f.save(args)
	
	def run(self, nodes, args):
		diffs = {}
		for node, (code, result) in nodes.service.configKeys():
			pass

class HSLModule(Module):
	'''Manages HSL scripts'''
	
	submodules = {
		'dump': HSLDumpModule(),
	}

module = HSLModule()
