#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys
import pkgutil
import argparse
import json
from halon.models import *

# Figure out the absolute path to the directory this script is in
BASE = os.path.abspath(os.path.dirname(__file__))

# Create an argument parser
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

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
		register_module(mod.module)

def register_module(mod):
	'''Registers a loaded module instance'''
	
	p = subparsers.add_parser(mod.command, help=mod.description)
	p.set_defaults(_mod=mod)
	mod.register_arguments(p)
	modules[mod.command] = mod

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
	
	for name, data in config['nodes'].iteritems():
		node = Node(data)
		node.name = name
		nodes[name] = node
	
	for name, data in config['clusters'].iteritems():
		nids = data['nodes'] if isinstance(data, dict) else data
		nodes = [nodes[nid] for nid in nids]
		cluster = NodeList(nodes)
		cluster.name = name
		cluster.load_data(data)
		cluster.sync_credentials()
		clusters[name] = cluster
	
	return (nodes, clusters)



if __name__ == '__main__':
	load_modules()
	config = load_config()
	nodes, clusters = process_config(config)
	
	args = parser.parse_args()
	args._mod.run([], args)
