import socket
import urllib2
import keyring
from base64 import b64encode, b64decode
from threading import Lock
from suds.client import Client
from suds.transport.http import HttpAuthenticated
from .proxies import *
from .util import async_dispatch
from . import cache



class Node(object):
	'''A single Halon node.
	
	:ivar str name: The configured name of the node.
	:ivar halon.models.NodeList cluster: The cluster the node belongs to.
	:ivar str scheme: The scheme the node should be accessed over, either http or https
	:ivar str host: The hostname of the node
	
	:ivar str username: The effective username; the node's, if any, otherwise the cluster's
	:ivar str password: The effective password; the node's or keychain's, if any, otherwise the cluster's
	
	'''
	
	name = "noname"
	cluster = None
	scheme = 'http'
	host = None
	
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
		
		return self.scheme + '://' + self.host + '/remote/'
	
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
	
	
	
	def __init__(self, data=None, name=None, cluster=None):
		'''Initializes a Node with the given configuration data and name.'''
		
		self.name = name
		self.cluster = cluster if not cluster is None else NodeList([self])
		
		if data:
			self.load_data(data)
	
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
		
		# Make a SOAP client
		self._client = Client("file://" + cache.get_path('wsdl.xml'), location=url, faults=False, nosend=True)
	
	def make_request(self, name, *args, **kwargs):
		'''Convenience function that creates a SOAP request context from a
		function name and a set of parameters.
		
		The first call to this function is blocking, as the node's WSDL file
		will be downloaded synchronously.'''
		
		return getattr(self._client.service, name)(*args, **kwargs)
	
	def command(self, command, *args):
		'''Convenience function that executes a command on the node, and returns
		a CommandProxy that can be used to iterate the command's output, or interact
		with the running process.'''
		
		# Allow calls as command("cmd", "arg1", "arg2") or command("cmd arg1 arg2")
		parts = [command] + list(args) if args else command.split(' ')
		
		code, cid = self.service.commandRun(argv={'item': [b64encode(part) for part in parts]})
		return (200, CommandProxy(self, cid)) if code == 200 else (code, None)
	
	def __unicode__(self):
		s = u"%s (%s)" % (self.name, self.host)
		if self.cluster.name:
			s = u"%s/%s" % (self.cluster.name, s)
		return s
	
	def __str__(self):
		return unicode(self).encode('utf-8')



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
		
		return async_dispatch({ node: lambda: node.command(command, *args) for node in self }, True)
	
	
	
	def load_data(self, data):
		'''Updates the nodelist's data from the given configuration dictionary,
		overwriting any existing data.'''
		
		if 'username' in data:
			self.local_username = data['username']
		if 'password' in data:
			self.local_password = data['password']
	
	def __unicode__(self):
		return u"%s -> [%s]" % (self.name, ', '.join([node.name for node in self]))
	
	def __str__(self):
		return unicode(self).encode('utf-8')
