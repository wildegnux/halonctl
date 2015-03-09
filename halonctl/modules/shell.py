from __future__ import print_function
import sys
import os
import six
import atexit
from inspect import getmembers
from code import InteractiveConsole
from halonctl import __version__ as version
from halonctl.modapi import Module

def dict_import(modname, members=['*']):
	mod = __import__(modname, globals(), locals(), members, 0)
	return dict(getmembers(mod))

class ShellModule(Module):
	'''Starts an interactive Python interpreter'''
	
	def run(self, nodes, args):
		# Banner
		banner = u'\n'.join([
			u"Python {pyversion[0]}.{pyversion[1]}.{pyversion[2]}, halonctl {version}",
			u"Variables: nodes, args",
			u"",
			u"{ps1}from __future__ import print_function",
			u"{ps1}import six",
			u"{ps1}from halonctl.util import *",
			u"",
		]).format(pyversion=sys.version_info, version=version, ps1='>>> ')
		
		# Shell context locals
		locals_ = {
			# Mimic Python's interactive sessions
			'__name__': '__console__',
			'__doc__': None,
			
			# Provide some variables
			'nodes': nodes,
			'args': args
		}
		
		# Mimic imports
		locals_.update(dict_import('__future__', 'print_function'))
		locals_.update(dict_import('halonctl.util'))
		
		# Set up readline for history navigation
		history_filename = os.path.join(os.path.expanduser('~'), '.halonctl_history')
		try:
			import readline
			import rlcompleter
		except ImportError:
			# We're on Windows, what's a readline?
			pass
		else:
			try:
				readline.read_history_file(history_filename)
			except IOError:
				# No history file exists (yet)
				pass
			
			completion_vars = globals()
			completion_vars.update(locals_)
			readline.set_completer(rlcompleter.Completer(completion_vars).complete)
			readline.parse_and_bind('tab: complete')
			
			atexit.register(readline.write_history_file, history_filename)
		
		# Run an interactive console session
		console = InteractiveConsole(locals_)
		console.interact(banner)

module = ShellModule()
