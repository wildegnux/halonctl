#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='halonctl',
	version='1.2.0',
	description='Manage Halon nodes from the commandline',
	author='Halon Security',
	author_email='support@halon.se',
	url='https://github.com/HalonSecurity/halonctl',
	packages=['halonctl', 'halonctl.modules', 'halonctl.formatters'],
	entry_points={
		'console_scripts': [
			'halonctl = halonctl.__main__:main'
		]
	},
	license='BSD',
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'Environment :: Console',
		'Intended Audience :: Developers',
		'Intended Audience :: System Administrators',
		'License :: OSI Approved :: BSD License',
		'Natural Language :: English',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 2.7',
		'Topic :: Communications :: Email',
		'Topic :: System :: Clustering',
		'Topic :: System :: Monitoring',
		'Topic :: System :: Recovery Tools',
		'Topic :: System :: Systems Administration',
		'Topic :: Utilities'
	],
	keywords='email halon commandline administration',
	install_requires=[
		'arrow',		# Saner datetime handling
		'futures',		# Backport of Python 3's futures, for thread pooling
		'keyring',		# Secure credential storage
		'natsort',		# Natural sorting of node names
		'suds-jurko',	# SOAP client library; improved fork of suds
		'prettytable',	# Fancy ASCII tables, feat. Py3 compatibility
		'requests',		# "HTTP for Humans"
		'blessings',	# Terminal magic made simple
	],
	package_data={
		'': ['*.json']
	},
	use_2to3=True
)
