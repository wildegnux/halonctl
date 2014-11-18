import sys
import argparse
from natsort import natsorted
from halonctl.modapi import Module
from halonctl.util import async_dispatch

def print_waiting_message(sigint_sent, num_dots, max_dots):
	if sys.stderr.isatty():
		dots = ('.' * num_dots).ljust(max_dots)
		num_dots = num_dots + 1 if num_dots < max_dots else 1
		if not sigint_sent:
			sys.stderr.write("\rWaiting for processes to complete%s (Press Ctrl+C to stop it)" % dots)
		else:
			sys.stderr.write("\rTermination requested, waiting%s (Press Ctrl+C to kill)" % dots)
	
	return num_dots

class CommandModule(Module):
	'''Executes a shell command'''
	
	def register_arguments(self, parser):
		parser.add_argument('cli', nargs=argparse.REMAINDER, metavar="...",
			help="The command to execute")
	
	def run(self, nodes, args):
		if not args.cli:
			print "No command specified"
			self.exitcode = 1
			return
		
		buffers = { node: "" for node in nodes }
		handles = { node: result[1] for node, result in nodes.command(*args.cli).iteritems() if result[0] == 200 }
		unfinished = handles
		
		max_dots = 3
		num_dots = max_dots
		sigint_sent = False
		while len(unfinished) > 0:
			# Write progress information to stderr if it's a terminal
			num_dots = print_waiting_message(sigint_sent, num_dots, max_dots)
			
			# Listen for Ctrl+C presses while we poll the commands for output
			try:
				for node, cmd in unfinished.items():
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
					for node, cmd in unfinished.iteritems():
						cmd.signal('SIGINT')
				else:
					for node, cmd in unfinished.items():
						cmd.stop()
			
			finally:
				sys.stderr.write("\r")
		
		for node, buf in natsorted(buffers.items(), key=lambda t: [t[0].cluster.name, t[0].name]):
			for line in buf.split('\r\n'):
				print "%s / %s> %s" % (node.cluster.name, node.name, line)
			
			print ""
			
module = CommandModule()
