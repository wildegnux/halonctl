import urlparse
from suds.client import Client
from suds.transport.http import HttpAuthenticated

class Node(object):
	'''A single Halon node.'''
	
	name = None
	host = None
	username = None
	password = None
	
	client = None
	
	def __init__(self, data=None, name=None):
		self.name = name
		if data:
			self.load_data(data)
	
	def load_data(self, data):
		url = urlparse.urlparse(data, 'http')
		self.username = url.username
		self.password = url.password
		self.host = url.scheme + "://" + url.hostname
	
	def connect(self):
		url = self.host + '/remote/?wsdl'
		transport = HttpAuthenticated(username=self.username, password=self.password, timeout=5)
		client = Client(url, location=self.host + '/remote/', transport=transport, timeout=5, faults=False)
		self.client = client
	
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
	
	def __unicode__(self):
		return u"%s @ [%s]" % (self.name, [node.name for node in self].join(', '))
	
	def __str__(self):
		return unicode(self).encode('utf-8')
