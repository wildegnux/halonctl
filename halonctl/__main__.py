#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import six
import os, sys
import re
import inspect
import pkgutil
import importlib
import argparse
import json
import logging
import arrow
import requests
import getpass
from collections import OrderedDict
from natsort import natsorted
from .models import *
from .util import *
from .roles import Role
from . import __version__
from . import cache
from . import config as g_config

# Figure out where this script is, and change the PATH appropriately
BASE = os.path.abspath(os.path.dirname(sys.modules[__name__].__file__))
sys.path.insert(0, BASE)

# Create an argument parser
parser = argparse.ArgumentParser(description=u"Easily manage Halon nodes and clusters.")
subparsers = parser.add_subparsers(title='subcommands', dest='_mod_name', metavar='cmd')
subparsers.required = True

# All available modules and output formatters
modules = {}
formatters = {}

# Loaded configuration, configured nodes and clusters
config = {}
nodes = {}
clusters = {}

# Disable unverified HTTPS warnings - we know what we're doing
requests.packages.urllib3.disable_warnings()

# Regex that matches quick-connect nodes
quick_node_re = re.compile(r'^(?:(?P<name>[a-zA-Z0-9_-]+)=)?(?:(?P<protocol>https?)://)?(?P<data>(?P<username>[^@]+)@(?P<host>[a-zA-Z0-9\-\.]+)(?::(?P<port>[0-9]+))?)$')



def load_modules(modules_path):
	'''Load all modules from the 'modules' directory.'''
	
	# Figure out where all the modules are, then treat it as a package,
	# iterating over its modules and attempting to load each of them. The
	# 'module' variable in the imported module is the module instance to use -
	# register that with the application. Yay, dynamic loading abuse.
	for loader, name, ispkg in pkgutil.iter_modules(path=[modules_path]):
		mod = loader.find_module(name).load_module(name)
		if hasattr(mod, 'module'):
			register_module(name.rstrip('_'), mod.module)
		else:
			print(u"Ignoring invalid module (missing 'module' variable): {name}".format(name=name), file=sys.stderr)

def load_formatters(formatters_path):
	'''Load all formatters from the 'formatters' directory.'''
	
	for loader, name, ispkg in pkgutil.iter_modules(path=[formatters_path]):
		fmt = loader.find_module(name).load_module(name)
		if hasattr(fmt, 'formatter'):
			formatters[name.rstrip('_')] = fmt.formatter
		else:
			print(u"Ignoring invalid formatter (missing 'formatter' member): {name}".format(name=name), file=sys.stderr)

def register_module(name, mod):
	'''Registers a loaded module instance'''
	
	p = subparsers.add_parser(name, help=mod.__doc__)
	p.set_defaults(_mod=mod)
	mod.register_arguments(p)
	modules[name] = mod

def open_config():
	'''Opens a configuration file from the first found default location.'''
	
	config_paths = [
		os.path.abspath(os.path.join(BASE, '..', 'halonctl.json')),
		os.path.expanduser('~/.config/halonctl.json'),
		os.path.expanduser('~/halonctl.json'),
		os.path.expanduser('~/.halonctl.json'),
		'/etc/halonctl.json',
	]
	
	config_path = None
	for p in config_paths:
		if os.path.exists(p):
			config_path = p
			break
	
	if not config_path:
		print(u"No configuration file found!", file=sys.stderr)
		print(u"", file=sys.stderr)
		print(u"Please create one in one of the following locations:", file=sys.stderr)
		print(u"", file=sys.stderr)
		for p in config_paths:
			print("  - {0}".format(p), file=sys.stderr)
		print(u"", file=sys.stderr)
		print(u"Or use the -C/--config flag to specify a path.", file=sys.stderr)
		print(u"A sample config can be found at:", file=sys.stderr)
		print(u"", file=sys.stderr)
		print(u"  - {0}".format(os.path.abspath(os.path.join(BASE, 'halonctl.sample.json'))), file=sys.stderr)
		print(u"", file=sys.stderr)
		sys.exit(1)
	
	return open(config_path, 'rU')

def load_config(f):
	'''Loads configuration data from a given file.'''
	
	try:
		conf = json.load(f, encoding='utf-8', object_pairs_hook=OrderedDict)
	except ValueError as e:
		sys.exit(u"Configuration Syntax Error: {0}".format(e))
	
	f.close()
	g_config.config.update(conf)
	return conf

def process_config(config):
	'''Processes a configuration dictionary into usable components.'''
	
	nodes = OrderedDict([(name, Node(data, name)) for name, data in six.iteritems(config.get('nodes', {}))])
	clusters = {}
	
	for name, data in six.iteritems(config.get('clusters', {})):
		cluster = NodeList()
		cluster.name = name
		cluster.load_data(data)
		
		for nid in data['nodes'] if isinstance(data, dict) else data:
			if not nid in nodes:
				sys.exit(u"Configuration Error: Cluster '{cid}' references nonexistent node '{nid}'".format(cid=cluster.name, nid=nid))
			node = nodes[nid]
			node.cluster = cluster
			cluster.append(node)
		
		clusters[cluster.name] = cluster
	
	return (nodes, clusters)

def apply_slice(list_, slice_):
	if not slice_ or not list_:
		return list_
	
	offsets = [-1, 0, 0]
	parts = [int(p) + offsets[i] if p else None for i, p in enumerate(slice_.split(':'))]
	try:
		return list_[slice(*parts)] if len(parts) > 1 else [list_[parts[0]]]
	except IndexError:
		return []

def apply_filter(available_nodes, available_clusters, nodes, clusters, slice_=''):
	targets = OrderedDict()
	
	if len(nodes) == 0 and len(clusters) == 0:
		for node in six.itervalues(apply_slice(available_nodes, slice_)):
			targets[node.name] = node
	else:
		for cid in clusters:
			for node in apply_slice(available_clusters[cid], slice_):
				targets[node.name] = node
		
		for nid in apply_slice(nodes, slice_):
			targets[nid] = available_nodes[nid]
	
	return NodeList(targets.values())

def download_wsdl(nodes, verify):
	path = cache.get_path(u"wsdl.xml")
	min_mtime = arrow.utcnow().replace(hours=-12)
	if not os.path.exists(path) or arrow.get(os.path.getmtime(path)) < min_mtime:
		has_been_downloaded = False
		for node in nodes:
			try:
				r = requests.get(u"{scheme}://{host}/remote/?wsdl".format(scheme=node.scheme, host=node.host), stream=True, verify=False if node.no_verify else verify)
				if r.status_code == 200:
					with open(path, 'wb') as f:
						for chunk in r.iter_content(256):
							f.write(chunk)
					has_been_downloaded = True
					break
			except requests.exceptions.SSLError:
				print_ssl_error(node)
				sys.exit(1)
			except:
				pass
		
		if not has_been_downloaded:
			sys.exit("None of your nodes are available, can't download WSDL")



def main():
	# Configure logging
	logging.basicConfig(level=logging.ERROR)
	logging.getLogger('suds.client').setLevel(logging.CRITICAL)
	
	# Load modules and formatters
	base_paths = [BASE, os.path.expanduser('~/halonctl'), os.path.expanduser('~/.halonctl')]
	for path in base_paths:
		load_modules(os.path.join(path, 'modules'))
		load_formatters(os.path.join(path, 'formatters'))
	
	# Figure out the program version
	version = __version__
	try:
		head_path = os.path.join(os.path.dirname(__file__), '..', '.git', 'refs', 'heads', 'master')
		with open(head_path) as f:
			revision = f.read().strip()[:7]
			version = "{version} ({revision})".format(version=__version__, revision=revision)
	except IOError:
		pass
	
	# Add parser arguments
	parser.add_argument('-V', '--version', action='version', version=u"halonctl {version}".format(version=version),
		help=u"print version information and exit")
	
	parser.add_argument('-C', '--config', type=argparse.FileType('rU'),
		help="use specified configuration file")
	
	parser.add_argument('-n', '--node', dest='nodes', action='append', metavar="NODES",
		default=[], help=u"target nodes")
	parser.add_argument('-c', '--cluster', dest='clusters', action='append', metavar="CLUSTERS",
		default=[], help=u"target clusters")
	parser.add_argument('-s', '--slice', dest='slice',
		default='', help=u"slicing, as a Python slice expression")
	parser.add_argument('-d', '--dry', dest='dry_run', action='store_true',
		help=u"only list the nodes that would be affected")
	
	parser.add_argument('-i', '--ignore-partial', action='store_true',
		help=u"exit normally even for partial results")
	parser.add_argument('-f', '--format', choices=list(formatters.keys()), default='table',
		help=u"use the specified output format (default: table)")
	parser.add_argument('-r', '--raw', action='store_true',
		help=u"don't humanize the output, output it as raw as possible")
	parser.add_argument('-g', '--group-by', metavar="KEY",
		help=u"group output; ignored for table-like formats")
	parser.add_argument('-k', '--key', dest='group_key', action='store_true',
		help=u"assume grouper is unique, and key only a single value to it")
	
	parser.add_argument('--clear-cache', action='store_true',
		help=u"clear the WSDL cache")
	
	# Parse!
	args = parser.parse_args()
	
	# Clear cache if requested
	if args.clear_cache:
		os.remove(cache.get_path(u"wsdl.xml"))
	
	# Load configuration
	config = load_config(args.config or open_config())
	nodes, clusters = process_config(config)
	
	# Allow wildcard cluster- and node targeting
	if args.clusters == ['-']:
		args.clusters = list(clusters.keys())
	if args.nodes == ['-']:
		args.nodes = list(nodes.keys())
	
	# Allow slices without targeting, defaulting to each cluster
	if args.slice and not args.clusters and not args.nodes:
		args.clusters = list(clusters.keys())
	
	# Allow non-configured nodes to be specified as '[name:]username@host'
	quick_node_matches = [ quick_node_re.match(n) for n in args.nodes ]
	quick_node_args = []
	for m in [ m for m in quick_node_matches if m ]:
		arg = m.group(0)
		data = m.group('data')
		n = Node(data, name=m.group('name') or m.group('host'))
		n.no_verify = True # Don't verify SSL for quick nodes
		nodes[arg] = n
		quick_node_args.append(arg)
	
	if quick_node_args:
		l = NodeList([nodes[arg] for arg in quick_node_args])
		for node, (code, result) in six.iteritems(l.service.login()):
			if code == 401:
				while True:
					password = getpass.getpass(u"Password for {node.username}@{node.host}: ".format(node=node))
					if not password:
						break
					
					node.password = password
					code = node.service.login()[0]
					if code == 200:
						break
					elif code == 401:
						print(u"Invalid login, try again")
					elif code == 0:
						print(u"The node has gone away")
						break
					else:
						print(u"An error occurred, code {0}".format(code))
						break
	
	# Validate cluster and node choices
	invalid_clusters = [cid for cid in args.clusters if not cid in clusters]
	if invalid_clusters:
		print(u"Unknown clusters: {0}".format(', '.join(invalid_clusters)), file=sys.stderr)
		print(u"Available: {0}".format(', '.join(six.iterkeys(clusters))), file=sys.stderr)
		sys.exit(1)
	
	invalid_nodes = [nid for nid in args.nodes if not nid in nodes and nid not in quick_node_args]
	if invalid_nodes:
		print(u"Unknown nodes: {0}".format(', '.join(invalid_nodes)), file=sys.stderr)
		print(u"Available: {0}".format(', '.join(six.iterkeys(nodes))), file=sys.stderr)
		sys.exit(1)
	
	# Filter nodes to choices
	target_nodes = apply_filter(nodes, clusters, args.nodes, args.clusters, args.slice)
	
	# If this is a dry run - stop right here and just print the targets
	if args.dry_run:
		print(u"This action would have affected:")
		for node in target_nodes:
			print(u"  - {name} ({cluster})".format(name=node.name, cluster=node.cluster.name))
		return
	
	# Download WSDL and create client objects
	download_wsdl(target_nodes, verify=config.get('verify_ssl', True))
	for node in target_nodes:
		node.load_wsdl()
	
	# Run the selected module
	mod = args._mod
	retval = mod.run(target_nodes, args)
	
	# Normalize generator mods into lists (lets us detect emptiness)
	if inspect.isgenerator(retval):
		retval = list(retval)
	
	# Print something, if there's anything to print
	if retval:
		if hasattr(retval, 'draw'):
			print(retval.draw())
		elif isinstance(retval, Role):
			print(retval.raw() if args.raw else retval.human())
		else:
			print(formatters[args.format].run(retval, args))
	
	# Let the module decide the exit code - either by explicitly setting it, or
	# by marking the result as partial, in which case a standard exit code is
	# returned unless the user has requested partial results to be ignored
	if mod.exitcode != 0:
		sys.exit(mod.exitcode)
	elif mod.partial and not args.ignore_partial:
		sys.exit(99)

if __name__ == '__main__':
	main()
