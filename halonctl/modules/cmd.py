from __future__ import print_function
import six
import sys
import argparse
from blessings import Terminal
from natsort import natsorted
from halonctl.modapi import Module
from halonctl.util import async_dispatch

def print_waiting_message(sigint_sent, num_dots, max_dots):
	if sys.stderr.isatty():
		dots = ('.' * num_dots).ljust(max_dots)
		num_dots = num_dots + 1 if num_dots < max_dots else 1
		msg = u"Waiting for processes to complete{0} (Press Ctrl+C to stop it)" if not sigint_sent else \
				u"\rTermination requested, waiting{0} (Press Ctrl+C to kill)"
		
		term = Terminal(stream=sys.stderr)
		print(u"\r{msg}{clear}".format(msg=msg.format(dots), clear=term.clear_eol), file=sys.stderr, end='')
	
	return num_dots

class CommandModule(Module):
	'''Executes a shell command'''
	
	def register_arguments(self, parser):
		parser.add_argument('cli', nargs=argparse.REMAINDER, metavar="...",
			help=u"The command to execute")
	
	def run(self, nodes, args):
		if not args.cli:
			print(u"No command specified")
			self.exitcode = 1
			return
		
		buffers = { node: "" for node in nodes }
		handles = { node: result for node, (code, result) in six.iteritems(nodes.command(*args.cli)) if code == 200 }
		unfinished = handles
		
		max_dots = 3
		num_dots = max_dots
		sigint_sent = False
		while len(unfinished) > 0:
			# Write progress information to stderr if it's a terminal
			num_dots = print_waiting_message(sigint_sent, num_dots, max_dots)
			
			# Listen for Ctrl+C presses while we poll the commands for output
			try:
				for node, cmd in list(unfinished.items()):
					code, res = cmd.read()
					
					if code == 200:
						buffers[node] += res
					else:
						del unfinished[node]
			
			# Send a SIGINT if Ctrl+C is pressed, kill proc if it happens again
			except KeyboardInterrupt:
				if not sigint_sent:
					sigint_sent = True
					print_waiting_message(True, num_dots, max_dots)
					async_dispatch({ node: (cmd.signal, ['SIGINT']) for node, cmd in six.iteritems(unfinished) })
				else:
					async_dispatch({ node: (cmd.stop,) for node, cmd in six.iteritems(unfinished) })
			
			finally:
				sys.stderr.write("\r")
		
		for node, buf in natsorted(list(buffers.items()), key=lambda t: [t[0].cluster.name, t[0].name]):
			for line in buf.split('\r\n'):
				print(u"{cluster} / {name}> {line}".format(cluster=node.cluster.name, name=node.name, line=line))
			
			print(u"")
			
module = CommandModule()
