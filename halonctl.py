#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys
import inspect
import pkgutil
import argparse
import json
import logging
from natsort import natsorted
from halon.models import *
from halon.util import *

# Figure out the absolute path to the directory this script is in
BASE = os.path.abspath(os.path.dirname(__file__))

# Create an argument parser
parser = argparse.ArgumentParser(description="Easily manage Halon nodes and clusters.")
subparsers = parser.add_subparsers(title='subcommands', metavar='cmd')

# A dictionary to hold all available modules
modules = {}

# Loaded configuration, configured nodes and clusters
config = {}
nodes = {}
clusters = {}



# Add parser arguments
parser.add_argument('-C', '--config', type=argparse.FileType('rU'),
	help="use specified configuration file")

parser.add_argument('-n', '--node', dest='nodes', action='append', metavar="NODES",
	default=[], help="target nodes")
parser.add_argument('-c', '--cluster', dest='clusters', action='append', metavar="CLUSTERS",
	default=[], help="target clusters")
parser.add_argument('-s', '--slice', dest='slice',
	default='', help="slicing, as a Python slice expression")

parser.add_argument('-i', '--ignore-partial', action='store_true',
	help="exit normally even for partial results")



def load_modules():
	'''Load all modules from the 'modules' directory.'''
	
	# Figure out where all the modules are, then treat it as a package,
	# iterating over its modules and attempting to load each of them. The
	# 'module' variable in the imported module is the module instance to use -
	# register that with the application. Yay, dynamic loading abuse.
	modules_path = os.path.join(BASE, 'modules')
	for loader, name, ispkg in pkgutil.iter_modules(path=[modules_path]):
		mod = loader.find_module(name).load_module(name)
		if hasattr(mod, 'module'):
			register_module(name, mod.module)
		else:
			print "Ignoring invalid module (missing 'module' variable): %s" % name

def register_module(name, mod):
	'''Registers a loaded module instance'''
	
	p = subparsers.add_parser(name, help=mod.__doc__)
	p.set_defaults(_mod=mod)
	mod.register_arguments(p)
	modules[name] = mod

def open_config():
	'''Opens a configuration file from the first found default location.'''
	
	config_paths = [
		os.path.join(BASE, 'halonctl.json'),
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
		print "No configuration file found!"
		print ""
		print "Please create one in one of the following locations:"
		print ""
		for p in config_paths:
			print "  - %s" % p
		print ""
		print "Or use the -C/--config flag to specify a path."
		print "A sample config can be found at:"
		print ""
		print "  - %s" % os.path.join(BASE, 'halonctl.sample.json')
		print ""
		sys.exit(1)
	
	return open(config_path, 'rU')

def load_config(f):
	'''Loads configuration data from a given file.'''
	
	conf = json.load(f, encoding='utf-8')
	f.close()
	return conf

def process_config(config):
	'''Processes a configuration dictionary into usable components.'''
	
	nodes = {}
	clusters = {}
	
	for name, data in config.get('nodes', {}).iteritems():
		node = Node(data)
		node.name = name
		nodes[name] = node
	
	for name, data in config.get('clusters', {}).iteritems():
		nids = data['nodes'] if isinstance(data, dict) else data
		cluster = NodeList([nodes[nid] for nid in nids])
		cluster.name = name
		cluster.load_data(data)
		cluster.sync_credentials()
		clusters[name] = cluster
	
	return (nodes, clusters)

def apply_slice(list_, slice_):
	if not slice_:
		return list_
	
	parts = [int(p) if p else None for p in slice_.split(':')]
	return list_[slice(*parts)]

def apply_filter(available_nodes, available_clusters, nodes, clusters, slice_=''):
	targets = []
	
	if len(nodes) == 0 and len(clusters) == 0:
		targets = apply_slice(available_nodes.values(), slice_)
	elif len(clusters) > 0:
		for cid in clusters:
			targets += apply_slice(available_clusters[cid], slice_)
	
	if len(nodes) > 0:
		targets += [available_nodes[nid] for nid in nodes]
	
	return NodeList(natsorted(targets, key=lambda t: [t.cluster.name, t.name]))



if __name__ == '__main__':
	# Configure logging
	logging.basicConfig(level=logging.ERROR)
	logging.getLogger('suds.client').setLevel(logging.CRITICAL)
	
	# Load modules and parse
	load_modules()
	args = parser.parse_args()
	
	# Load configuration
	config = load_config(args.config or open_config())
	nodes, clusters = process_config(config)
	
	# Validate cluster and node choices
	invalid_clusters = [cid for cid in args.clusters if not cid in clusters]
	if invalid_clusters:
		print "Unknown clusters: %s" % ', '.join(invalid_clusters)
		print "Available: %s" % ', '.join(clusters.iterkeys())
		sys.exit(1)
	
	invalid_nodes = [nid for nid in args.nodes if not nid in nodes]
	if invalid_nodes:
		print "Unknown nodes: %s" % ', '.join(invalid_nodes)
		print "Available: %s" % ', '.join(nodes.iterkeys())
		sys.exit(1)
	
	# Filter nodes to choices
	target_nodes = apply_filter(nodes, clusters, args.nodes, args.clusters, args.slice)
	
	# Run the selected module
	mod = args._mod
	retval = mod.run(target_nodes, args)
	
	# Normalize generator mods into lists
	if inspect.isgenerator(retval):
		retval = list(retval)
	
	# Print something, if there's anything to print
	if retval:
		if hasattr(retval, 'draw'):
			print retval.draw()
		else:
			print_table(retval)
	
	# Let the module decide the exit code - either by explicitly setting it, or
	# by marking the result as partial, in which case a standard exit code is
	# returned unless the user has requested partial results to be ignored
	if mod.exitcode != 0:
		sys.exit(mod.exitcode)
	elif mod.partial and not args.ignore_partial:
		sys.exit(99)
