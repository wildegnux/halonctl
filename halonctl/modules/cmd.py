from __future__ import print_function
import six
import sys
import argparse
import platform
import curses
import termios
import tty
from select import select
from natsort import natsorted
from halonctl.modapi import Module
from halonctl.util import async_dispatch, get_terminal_size
from halonctl.roles import HTTPStatus

ON_WINDOWS = (platform.system() == 'Windows')

def print_waiting_message(sigint_sent, num_dots, max_dots):
	if sys.stderr.isatty():
		dots = ('.' * num_dots).ljust(max_dots)
		num_dots = num_dots + 1 if num_dots < max_dots else 1
		msg = u"Waiting for processes to complete{0} (Press Ctrl+C to stop it)" if not sigint_sent else \
				u"\rTermination requested, waiting{0} (Press Ctrl+C to kill)"
		
		clear_eol = "\x1b[K"
		if ON_WINDOWS:
			clear_eol = (' ' * (79 - len(msg.format(dots))))
		print(u"\r{msg}{clear}".format(msg=msg.format(dots), clear=clear_eol), file=sys.stderr, end='')
	
	return num_dots

class CommandModule(Module):
	'''Executes a shell command'''
	
	def register_arguments(self, parser):
		parser.add_argument('-i', '--interactive', action='store_true',
			help=u"Run an interactive shell")
		parser.add_argument('cli', nargs=argparse.REMAINDER, metavar="...",
			help=u"The command to execute")
	
	def run(self, nodes, args):
		if not args.cli:
			print(u"No command specified")
			self.exitcode = 1
			return
		
		if args.interactive:
			if ON_WINDOWS:
				print(u"Interactive mode does not work on Windows.")
				self.exitcode = 1
				return
			
			if not sys.stdout.isatty():
				print(u"Interactive mode requires a TTY")
				self.exitcode = 1
				return
			
			node = nodes[0]
			if len(nodes) > 1:
				node = self.pick_node(nodes, args)
			if node:
				return self.run_interactive(node, args)
		else:
			return self.run_default(nodes, args)
	
	def run_default(self, nodes, args):
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
	
	def run_interactive(self, node, args):
		size = get_terminal_size()
		
		# Try to run the command first - no need to mess with the terminal if
		# the remote node is down
		code, cmd = node.command(*args.cli, size=size)
		if code != 200:
			# TODO: Make it possible to just return a Role
			print(HTTPStatus(code).human())
			self.exitcode = 1
			return
		
		# Save the current terminal flags, then set it to raw mode - there's a
		# full TTY on the other side of the pipe, we're basically tunneling it
		old_flags = termios.tcgetattr(sys.stdout)
		tty.setraw(sys.stdout)
		
		# REPL time
		try:
			while not cmd.done:
				# Check for terminal resizes
				new_size = get_terminal_size()
				if new_size != size:
					size = new_size
					cmd.resize(size)
				
				# Read from stdin, use select to avoid blocking
				indata = u''
				while select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
					indata += sys.stdin.read(1)
				if indata:
					cmd.write(indata)
				
				# Write to stdout; latency here makes a sleep unnecessary
				code, output = cmd.read()
				if code != 200:
					if code != 500:
						print(HTTPStatus(code).human())
						self.exitcode = 1
					break
				sys.stdout.write(output)
				sys.stdout.flush()
		finally:
			# Whatever happens, barring a power outage, restore the user's
			# terminal to a usable state before exiting!
			termios.tcsetattr(sys.stdout, termios.TCSADRAIN, old_flags)
	
	def pick_node(self, nodes, args):
		stdscr = curses.initscr()
		curses.noecho()
		curses.cbreak()
		stdscr.keypad(1)
		
		i = 0
		
		try:
			stdscr.addstr(u"Interactive mode requires a single node.\n")
			stdscr.addstr(u"Use up/down to select a node, Enter to select.\n")
			stdscr.addstr(u"\n")
			
			while True:
				stdscr.clrtoeol()
				stdscr.addstr(u"Node: {node}\r".format(node=nodes[i]))
				stdscr.refresh()
				
				c = stdscr.getch()
				if c == ord('q'):
					return None
				elif c == curses.KEY_ENTER or c == ord('\n'):
					return nodes[i]
				elif c == curses.KEY_UP and i > 0:
					i -= 1
				elif c == curses.KEY_DOWN and i < len(nodes) - 1:
					i += 1
		finally:
			curses.nocbreak()
			stdscr.keypad(0)
			curses.echo()
			curses.endwin()

module = CommandModule()
