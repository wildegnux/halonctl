from __future__ import print_function
import six
import socket
import keyring
from threading import Lock
from suds.client import Client
from suds.transport.http import HttpAuthenticated
from .proxies import *
from .util import async_dispatch, nodesort, to_base64, from_base64
from . import cache



@six.python_2_unicode_compatible
class Node(object):
	'''A single Halon node.
	
	:ivar str name: The configured name of the node.
	:ivar halon.models.NodeList cluster: The cluster the node belongs to.
	:ivar str scheme: The scheme the node should be accessed over, either http or https
	:ivar str host: The hostname of the node
	
	:ivar str username: The effective username; the node's, if any, otherwise the cluster's
	:ivar str password: The effective password; the node's or keychain's, if any, otherwise the cluster's
	
	'''
	
	name = u"noname"
	cluster = None
	scheme = 'http'
	host = None
	no_verify = False
	
	local_username = None
	local_password = None
	
	
	
	@property
	def service(self):
		'''A proxy that can be used to make SOAP calls to the node.
		
		:rtype: :class:`halon.proxies.NodeSoapProxy`
		'''
		return NodeSoapProxy(self)
	
	@property
	def url(self):
		'''The base URL for the node.'''
		
		return "{scheme}://{host}/remote/".format(scheme=self.scheme, host=self.host)
	
	@property
	def username(self):
		return self.local_username or self.cluster.username
	
	@username.setter
	def username(self, val):
		self.local_username = val
	
	@property
	def password(self):
		return self.local_password or self.keyring_password or self.cluster.password
	
	@password.setter
	def password(self, val):
		self.local_password = val
	
	@property
	def keyring_password(self):
		if not hasattr(self, '_keyring_password') and self.host and self.username:
			self._keyring_password = keyring.get_password(self.host, self.username)
		return getattr(self, '_keyring_password', None)
	
	
	
	def __init__(self, data=None, name=None, cluster=None, load_wsdl=False):
		'''Initializes a Node with the given configuration data and name.'''
		
		self.name = name
		self.cluster = cluster if not cluster is None else NodeList([self])
		
		if data:
			self.load_data(data)
		
		if load_wsdl:
			self.load_wsdl()
	
	def load_data(self, s):
		'''Updates the node's data from the given configuration string,
		overwriting any existing data.'''
		
		remainder = s
		
		# Split out any scheme
		parts = remainder.split('://', 1)
		if len(parts) == 2:
			self.scheme = parts[0]
			remainder = parts[1]
		
		# Split the host from the credentials
		parts = remainder.split('@', 1)
		if len(parts) == 2:
			remainder = parts[0]
			self.host = parts[1]
			
			# Credentials may or may not include the password
			parts = remainder.split(':', 1)
			if len(parts) == 2:
				self.username = parts[0]
				self.password = parts[1]
			else:
				self.username = parts[0]
		else:
			self.host = parts[0]
		
	def load_wsdl(self):
		'''Loads the cached WSDL file.
		
		This is called automatically the first time a SOAP call is attempted,
		or you may call it yourself on startup to e.g. create a bunch of
		clients at once over a bunch of threads.'''
		
		if not hasattr(self, '_client'):
			self._client = Client("file:{0}".format(cache.get_path('wsdl.xml')), location=self.url, faults=False, nosend=True)
			self._client.set_options(cache=None)
	
	def make_request(self, name, *args, **kwargs):
		'''Convenience function that creates a SOAP request context from a
		function name and a set of parameters.
		
		The first call to this function is blocking, as the node's WSDL file
		will be downloaded synchronously.'''
		
		self.load_wsdl()
		return getattr(self._client.service, name)(*args, **kwargs)
	
	def command(self, command, *args, **kwargs):
		'''Convenience function that executes a command on the node, and returns
		a CommandProxy that can be used to iterate the command's output, or interact
		with the running process.
		
		Note that ``args`` are the command's arguments (first one is the
		command name), while ``kwargs`` controls how it's executed, specified
		by the following flags:
		
		* ``size`` - the viewport size as (cols, rows), defaults to (80,24)
		* ``cols``, ``rows`` - individual components of ``size``
		'''
		
		# Allow calls as command("cmd", "arg1", "arg2") or command("cmd arg1 arg2")
		parts = [command] + list(args) if args else command.split(' ')
		
		# Allow size to be specified as size=(cols,rows) or cols=,rows=
		size = kwargs.get('size', (80, 24))
		size = (kwargs.get('cols', size[0]), kwargs.get('rows', size[1]))
		
		code, cid = self.service.commandRun(argv={'item': [to_base64(part) for part in parts]}, cols=size[0], rows=size[1])
		return (200, CommandProxy(self, cid)) if code == 200 else (code, None)
	
	def __str__(self):
		s = u"{name} ({host})".format(name=self.name, host=self.host)
		if self.cluster.name:
			s = u"{cluster}/{s}".format(cluster=self.cluster.name, s=s)
		return s
	
	def __repr__(self):
		return "Node(name={name}, cluster=<{cluster}>)".format(name=self.name, cluster=self.cluster.name if self.cluster else None)



@six.python_2_unicode_compatible
class NodeList(list):
	'''A list of Halon nodes.
	
	It's a regular list for all intents and purposes, but with the added
	benefit of keeping track of credentials, and the ability to execute SOAP
	calls, either synchronously on one node at a time, or asynchronously on all
	of them at once.
	'''
	
	name = None
	local_username = None
	local_password = None
	
	
	
	@property
	def username(self):
		if not self.local_username:
			for node in [node for node in self if node.local_username]:
				return node.local_username
		return self.local_username
	
	@property
	def password(self):
		if not self.local_password:
			for node in [node for node in self if node.local_password or node.keyring_password]:
				return node.password or node.keyring_password
		return self.local_password
	
	
	
	@property
	def service(self):
		'''An asynchronous SOAP proxy.
		
		This is the recommended way to target multiple nodes with a call, as it
		will only take as long as the slowest node takes to respond, rather
		than taking longer and longer the mode nodes you're targeting.
		
		:rtype: :class:`halon.proxies.NodeListSoapProxy`
		'''
		return NodeListSoapProxy(self)
	
	def command(self, command, *args):
		'''Executes a command across all contained nodes.'''
		
		return nodesort(async_dispatch({ node: (node.command, (command,) + args) for node in self }))
	
	
	
	def load_data(self, data):
		'''Updates the nodelist's data from the given configuration dictionary,
		overwriting any existing data.'''
		
		if 'username' in data:
			self.local_username = data['username']
		if 'password' in data:
			self.local_password = data['password']
	
	def __str__(self):
		return u"{name} -> [{nodes}]".format(name=self.name, nodes=', '.join([node.name for node in self]))
