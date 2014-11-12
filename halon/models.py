import socket
import urllib2
from tornado.httpclient import *
from suds.client import Client
from suds.transport.http import HttpAuthenticated



class NodeSoapProxy(object):
	def __init__(self, node, async=False):
		self.node = node
		self.async = async
	
	def __getattr__(self, name):
		def _soap_proxy_executor(*args, **kwargs):
			if not self.node._client:
				try:
					self.node._connect()
				except urllib2.URLError as e:
					return (0, e.reason)
			
			context = getattr(self.node.client.service, name)(*args, **kwargs)
			http_client = HTTPClient()
			try:
				result = http_client.fetch(context.client.location(), method="POST",
					body=context.envelope, headers=context.client.headers(),
					auth_username=self.node.username, auth_password=self.node.password)
				return context.process_reply(result.body, result.code, result.reason)
			except HTTPError as e:
				return context.process_reply(e.response.body if getattr(e, 'response', None) else None, e.code, e.message)
			except Exception as e:
				return (0, e.message)
			http_client.close()
		
		return _soap_proxy_executor

class Node(object):
	'''A single Halon node.'''
	
	name = None
	cluster = None
	scheme = 'http'
	host = None
	username = None
	password = None
	
	_client = None
	
	def __init__(self, data=None, name=None):
		self.name = name
		self.cluster = NodeList([self])
		if data:
			self.load_data(data)
	
	def load_data(self, s):
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
		url = self.scheme + '://' + self.host + '/remote/'
		transport = HttpAuthenticated(username=self.username, password=self.password, timeout=5)
		client = Client(url + '?wsdl', location=url, transport=transport, timeout=5, faults=False, nosend=True)
		self.client = client
	
	def soap(self, async=False):
		return NodeSoapProxy(self, async)
	
	def __unicode__(self):
		return u"%s@%s" % (self.username, self.host)
	
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
	service = None
	
	def __init__(self, *args, **kwargs):
		self.service = NodeListSoapProxy(self)
		super(NodeList, self).__init__(*args, **kwargs)
	
	def load_data(self, data):
		if 'username' in data:
			self.username = data['username']
		if 'password' in data:
			self.password = data['password']
	
	def sync_credentials(self):
		# If we don't have an username given for the cluster, see if one of the
		# nodes has one
		if not self.username:
			for node in self:
				if node.username:
					self.username = node.username
					self.password = node.password
					break
		
		# Propagate the credentials to all included nodes
		for node in self:
			node.username = self.username
			node.password = self.password
			node.cluster = self
	
	def __unicode__(self):
		return u"%s -> [%s]" % (self.name, ', '.join([node.name for node in self]))
	
	def __str__(self):
		return unicode(self).encode('utf-8')



class NodeListSoapProxy(object):
	'''Proxy for a NodeList that allows grouped SOAP calls.'''
	
	nodelist = None
	
	def __init__(self, nodelist):
		self.nodelist = nodelist
	
	def __getattr__(self, name):
		# TODO: Figure out how to make this asynchronous; generators are an
		# awful fit for this task, but they're better than lists in this case
		def proxy(*args, **kwargs):
			for node in self.nodelist:
				if not node.client:
					try:
						node.connect(True)
					except urllib2.URLError, e:
						yield (node, (0, e.reason))
						continue
				yield (node, getattr(node.client.service, name)(*args, **kwargs))
		
		return proxy
