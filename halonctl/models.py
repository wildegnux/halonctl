import socket
import urllib2
import keyring
from base64 import b64encode, b64decode
from suds.client import Client
from suds.transport.http import HttpAuthenticated
from .proxies import *
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
	
	_username = None
	_password = None
	_keyring_password = None
	
	
	
	@property
	def service(self):
		'''A proxy that can be used to make SOAP calls to the node.
		
		:rtype: :class:`halon.proxies.NodeSoapProxy`
		'''
		return NodeSoapProxy(self)
	
	@property
	def username(self):
		return self._username or self.cluster.username
	
	@username.setter
	def username(self, val):
		self._username = val
	
	@property
	def password(self):
		if not self._keyring_password:
			self._keyring_password = keyring.get_password(self.host, self.username) \
				if self.host and self.username else None
		return self._password or self._keyring_password or self.cluster.password
	
	@password.setter
	def password(self, val):
		self._password = val
	
	
	
	def __init__(self, data=None, name=None):
		'''Initializes a Node with the given configuration data and name.'''
		
		self.name = name
		self.cluster = NodeList([self])
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
	
	def _connect(self):
		'''Returns a SOAP client for the node.
		
		The first time this is called, it's a blocking operation, as the node's
		WSDL will be downloaded on the current thread.
		
		If the node is unreachable, None is returned.
		
		:returns: A suds.client.Client, or None if the server could not be found
		'''
		
		if not hasattr(self, '_client'):
			url = self.scheme + '://' + self.host + '/remote/'
			transport = HttpAuthenticated(username=self.username, password=self.password, timeout=5)
			
			try:
				self._client = Client("file://" + cache.get_path('wsdl.xml'), location=url, transport=transport, timeout=5, faults=False, nosend=True)
			except urllib2.URLError as e:
				self._client = None
		
		return self._client
	
	def make_request(self, name, *args, **kwargs):
		'''Convenience function that creates a SOAP request context from a
		function name and a set of parameters.
		
		The first call to this function is blocking, as the node's WSDL file
		will be dowbloaded synchronously.
		
		If the node is unreachable, None is returned.'''
		
		client = self._connect()
		if client:
			return getattr(client.service, name)(*args, **kwargs)
	
	def command(self, command, *args):
		'''Convenience function that executes a command on the node, and returns
		a CommandProxy that can be used to iterate the command's output, or interact
		with the running process.'''
		
		# Allow calls as command("cmd", "arg1", "arg2") or command("cmd arg1 arg2")
		parts = [command] + list(args)
		if not args:
			parts = command.split(' ')
		
		code, cid = self.service.commandRun(argv={'item': [b64encode(part) for part in parts]})
		if code == 200:
			return (200, CommandProxy(self, cid))
		else:
			return (code, None)
	
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
	username = None
	password = None
	
	
	
	@property
	def service(self):
		'''An asynchronous SOAP proxy.
		
		This is the recommended way to target multiple nodes with a call, as it
		will only take as long as the slowest node takes to respond, rather
		than taking longer and longer the mode nodes you're targeting.
		
		:rtype: :class:`halon.proxies.NodeListSoapProxy`
		'''
		return NodeListSoapProxy(self)
	
	
	
	def load_data(self, data):
		'''Updates the nodelist's data from the given configuration dictionary,
		overwriting any existing data.'''
		
		if 'username' in data:
			self.username = data['username']
		if 'password' in data:
			self.password = data['password']
	
	def sync_credentials(self):
		'''Synchronizes credentials through all contained nodes.
		
		If the list has its own set of username and password, it will be used
		for all contained nodes. Otherwise, it will attempt to find a username
		and optionally password on one of the nodes, and propagate that through
		the list.'''
		
		# If we don't have any credentials, and a node has, copy those
		for node in self:
			if not self.username and node.username:
				self.username = node.username
				self.password = node.password
				break
		
		# Properly assign every included node to this cluster
		for node in self:
			node.cluster = self
	
	def command(self, command, *args):
		'''Executes a command across all contained nodes.'''
		
		# Basically copypaste from NodeListSoapProxy; thread_pool_executor is
		# a ThreadPoolExecutor imported from and thus shared with proxies.py
		@gen.coroutine
		def _inner():
			results = yield {
				node: thread_pool_executor.submit(node.command, command, *args)
				for node in self
			}
			raise gen.Return(OrderedDict(natsorted(results.items(), key=lambda t: [t[0].cluster.name, t[0].name])))
		return IOLoop.instance().run_sync(_inner)
	
	def __unicode__(self):
		return u"%s -> [%s]" % (self.name, ', '.join([node.name for node in self]))
	
	def __str__(self):
		return unicode(self).encode('utf-8')
