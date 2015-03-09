from __future__ import print_function
import sys
import os
import six
import atexit
import textwrap
from code import InteractiveConsole
from halonctl import __version__ as version
from halonctl.modapi import Module

class ShellModule(Module):
	'''Starts an interactive Python interpreter'''
	
	banner_template = u'''
	Python {pyversion[0]}.{pyversion[1]}.{pyversion[2]}, halonctl {version}
	Variables: nodes, args
	'''
	
	base_locals = {
		'__name__': '__console__',
		'__doc__': None,
	}
	
	def run(self, nodes, args):
		banner = textwrap.dedent(self.banner_template).strip('\n').format(
			pyversion=sys.version_info, version=version
		)
		
		locals_ = self.base_locals.copy()
		locals_.update({ 'nodes': nodes, 'args': args })
		
		self.setup_readline(locals_)
		
		console = InteractiveConsole(locals_)
		console.interact(banner)
	
	def setup_readline(self, locals_):
		try:
			import readline
			import rlcompleter
		except ImportError:
			# We're on Windows, what's a readline?
			return
		
		history_path = os.path.join(os.path.expanduser('~'), '.halonctl_history')
		try:
			readline.read_history_file(history_path)
		except IOError:
			# No history file exists (yet)
			pass
		
		completion_vars = globals().copy()
		completion_vars.update(locals_)
		
		readline.set_completer(rlcompleter.Completer(completion_vars).complete)
		readline.parse_and_bind('tab: complete')
		
		atexit.register(readline.write_history_file, history_path)

module = ShellModule()
