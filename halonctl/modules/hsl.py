from __future__ import print_function
import sys
import os
import re
import six
import difflib
from jinja2 import Template
from textwrap import dedent
from blessings import Terminal
from halonctl.modapi import Module
from halonctl.roles import HTTPStatus
from halonctl.util import from_base64, to_base64

FRAGMENTS = [
	'system_authentication_script',
	'transport_flow',
	'queue_flow',
]
MIMES = {
	'text/plain': 'txt',
	'text/csv': 'csv',
}
SCRIPT_RE = re.compile(r'\w+_flow__\d+')

t = Terminal()



class BaseFile(object):
	filename = u'unnamed'
	extension = u'bin'
	
	name = None
	meta = None
	body = u''
	
	@property
	def full_filename(self):
		return u"{0}.{1}".format(self.filename, self.extension)
	
	
	
	@classmethod
	def from_file(class_, path):
		f = class_()
		f.load(path)
		return f
	
	
	
	def __init__(self, item=None):
		if item:
			self.load_data(item)
	
	def load_data(self, item):
		'''Loads data from a SOAP payload.'''
		pass
	
	def to_data(self):
		'''Returns a SOAP payload.'''
		pass
	
	def deserialize(self, data):
		'''Deserializes data read from a file.'''
		lines = data.split('\n')
		if lines[0].startswith('//= NAME: '):
			self.name = lines.pop(0)[10:]
		if lines[0].startswith('//= META: '):
			self.meta = lines.pop(0)[10:]
		self.body = u'\n'.join(lines)
	
	def serialize(self, node=None):
		'''Serializes data for writing to a file.'''
		data = u""
		if self.name:
			data += u"//= NAME: {0}\n".format(self.name)
		if self.meta:
			data += u"//= META: {0}\n".format(self.meta)
		data += self.render(node)
		return data
	
	def path(self, args):
		'''Constructs a local path to the file.'''
		return os.path.join(args.path, self.full_filename)
	
	def save(self, args):
		if not os.path.exists(args.path):
			os.makedirs(args.path)
		
		with open(self.path(args), 'w') as f:
			f.write(self.serialize())
	
	def load(self, path):
		with open(path) as f:
			pts = os.path.splitext(os.path.basename(path))
			self.filename, self.extension = pts[0], pts[1][1:]
			self.deserialize(f.read())
	
	def diff(self, other, from_='', to='', node=None):
		if self.serialize(node) == other.serialize(node):
			return []
		
		return difflib.unified_diff(
			self.serialize().split('\n'),
			other.serialize().split('\n'),
			from_, to, lineterm=''
		)
	
	def render(self, node=None):
		if not node:
			return self.body
		
		return Template(self.body).render(node=node)

class ScriptFile(BaseFile):
	extension = 'hsl'
	
	def load_data(self, item):
		self.filename = item.name
		self.name = item.params.item[0]
		self.body = self.decode(item.params.item[-1])
		
		# Some kinds of scripts (ACL Flows) have an extra middle parameter...
		if len(item.params.item) > 2:
			self.meta = item.params.item[1]
	
	def decode(self, data):
		body = ''
		for block in data.split(','):
			if block.startswith('script '):
				body += u'{0}\n'.format(from_base64(block[8:-1]))
			else:
				body += u'//= {0}\n'.format(block)
		return body

class FragmentFile(BaseFile):
	extension = 'hsl'
	
	def load_data(self, item):
		self.filename = item.name
		self.name = item.name
		self.body = from_base64(item.params.item[0])

class TextFile(BaseFile):
	extension = 'txt'
	
	def load_data(self, item):
		self.filename = item.name
		self.extension = MIMES.get(item.params.item[1], 'bin')
		self.name = item.params.item[0]
		self.body = from_base64(item.params.item[2])

def files_from_result(result, ignore=[]):
	for item in result.item:
		if item.name in ignore:
			continue
		elif SCRIPT_RE.match(item.name):
			yield ScriptFile(item)
		elif item.name in FRAGMENTS:
			yield FragmentFile(item)
		elif item.name.startswith('file__'):
			yield TextFile(item)

def files_from_storage(path, ignore=[]):
	for filename in os.listdir(path):
		basename = os.path.splitext(filename)[0]
		filepath = os.path.join(path, filename)
		if basename in ignore:
			continue
		elif SCRIPT_RE.match(basename):
			yield ScriptFile.from_file(filepath)
		elif basename in FRAGMENTS:
			yield FragmentFile.from_file(filepath)
		elif basename.startswith('file__'):
			yield TextFile.from_file(filepath)

def load_ignore_list(path):
	ignore_path = os.path.join(path, '_ignore')
	if os.path.exists(ignore_path):
		with open(ignore_path, 'rU') as f:
			return f.read().split('\n')
	return []

def print_diff(diff):
	print(t.bold(diff[0]))
	print(t.bold(diff[1]))
	print(t.bold(diff[2]))
	for line in diff[3:]:
		if line.startswith('+'):
			print(t.green(line))
		elif line.startswith('-'):
			print(t.red(line))
		else:
			print(line)



class HSLDumpModule(Module):
	'''Dumps scripts from a node'''
	
	def register_arguments(self, parser):
		parser.add_argument('path', nargs='?', default='.',
			help=u"node configuration directory")
	
	def run(self, nodes, args):
		# It doesn't make sense to dump from multiple nodes into one directory
		node = nodes[0]
		code, result = node.service.configKeys()
		ignore = load_ignore_list(args.path)
		
		if code != 200:
			self.exitcode = 1
			return HTTPStatus(code)
		
		for f in files_from_result(result, ignore):
			f.save(args)

class HSLDiffModule(Module):
	'''Views differences between local and remote files.'''
	
	def register_arguments(self, parser):
		parser.add_argument('path', nargs='?', default='.',
			help=u"node configuration directory")
	
	def run(self, nodes, args):
		ignore = load_ignore_list(args.path)
		local = { f.full_filename: f for f in files_from_storage(args.path, ignore) }
		
		diffs = {}
		for node, (code, result) in six.iteritems(nodes.service.configKeys()):
			if code != 200:
				self.partial = True
				pass
			
			for f in files_from_result(result, ignore):
				f2 = local.get(f.full_filename, BaseFile())
				diff = list(f.diff(f2, node.name, f.full_filename))
				if diff:
					print_diff(diff)

class HSLPullModule(Module):
	'''Merges remote changes into local files.'''
	
	def register_arguments(self, parser):
		parser.add_argument('path', nargs='?', default='.',
			help=u"node configuration directory")
		parser.add_argument('-f', '--force', action='store_true',
			help=u"apply changes without confirmation")
	
	def run(self, nodes, args):
		ignore = load_ignore_list(args.path)
		local = { f.full_filename: f for f in files_from_storage(args.path, ignore) }
		
		for node, (code, result) in six.iteritems(nodes.service.configKeys()):
			if code != 200:
				self.partial = True
				pass
			
			for f in files_from_result(result, ignore):
				f2 = local.get(f.full_filename, BaseFile())
				diff = list(f2.diff(f, f.full_filename, node.name, node=node))
				if diff:
					print_diff(diff)
					
					abort = False
					while True:
						a = 'y' if args.force else six.moves.input(t.cyan(u"Apply patch [y/n/q/?]? "))
						if a == '?':
							print(t.magenta(dedent(u'''
							y - apply this patch
							n - do not apply this patch
							q - quit; do not apply this or any subsequent patch
							? - display a help message
							''').strip()))
							continue
						elif a == 'y':
							f.save(args)
						elif a == 'n':
							pass
						elif a == 'q':
							abort = True
						else:
							continue
						break
					
					if abort:
						break

class HSLModule(Module):
	'''Manages HSL scripts'''
	
	submodules = {
		'dump': HSLDumpModule(),
		'diff': HSLDiffModule(),
		'pull': HSLPullModule(),
	}

module = HSLModule()
