import socket
import urllib2
from suds.client import Client
from suds.transport.http import HttpAuthenticated
from .proxies import *



class Node(object):
	'''A single Halon node.'''
	
	name = None
	cluster = None
	scheme = 'http'
	host = None
	username = None
	password = None
	
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
	
	def client(self):
		if not hasattr(self, '_client'):
			url = self.scheme + '://' + self.host + '/remote/'
			transport = HttpAuthenticated(username=self.username, password=self.password, timeout=5)
			
			try:
				self._client = Client(url + '?wsdl', location=url, transport=transport, timeout=5, faults=False, nosend=True)
			except urllib2.URLError as e:
				self._client = None
		
		return self._client
	
	def make_request(self, name, *args, **kwargs):
		client = self.client()
		if client:
			return getattr(client.service, name)(*args, **kwargs)
	
	def make_tornado_request(self, context):
		return HTTPRequest(context.client.location(), method="POST",
			body=context.envelope, headers=context.client.headers(),
			auth_username=self.username, auth_password=self.password)
	
	def soap(self):
		return NodeSoapProxy(self)
	
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
