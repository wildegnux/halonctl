#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys
import pkgutil
import argparse

# Figure out the absolute path to the directory this script is in
BASE = os.path.abspath(os.path.dirname(__file__))

# Create an argument parser
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

# A dictionary to hold all available modules
modules = {}



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



if __name__ == '__main__':
	load_modules()
	
	args = parser.parse_args()
	args._mod.run([], args)
