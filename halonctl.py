#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys
import inspect
import pkgutil
import argparse
import json
import logging
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

def load_config():
	'''Loads user configuration'''
	
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
		print "A sample config can be found at:"
		print ""
		print "  - %s" % os.path.join(BASE, 'halonctl.sample.json')
		print ""
		sys.exit(1)
		
	with open(config_path) as f:
		return json.load(f, encoding='utf-8')

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
	
	return NodeList(targets)



if __name__ == '__main__':
	logging.basicConfig(level=logging.ERROR)
	logging.getLogger('suds.client').setLevel(logging.CRITICAL)
	
	# Load all the things!
	load_modules()
	config = load_config()
	nodes, clusters = process_config(config)
	
	# Add parser arguments; done here so that we can validate nodes/clusters
	parser.add_argument('-n', '--node', dest='nodes', action='append', metavar="NODES",
		choices=[str(s) for s in nodes.iterkeys()], default=[],
		help="target nodes")
	parser.add_argument('-c', '--cluster', dest='clusters', action='append', metavar="CLUSTERS",
		choices=[str(s) for s in clusters.iterkeys()], default=[],
		help="target clusters")
	parser.add_argument('-s', '--slice', dest='slice', default='',
		help="slicing, as a Python slice expression")
	
	parser.add_argument('-i', '--ignore-partial', action='store_true',
		help="don't exit with code 99 if some nodes' results are unavailable")
	
	# Parse and filter
	args = parser.parse_args()
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
