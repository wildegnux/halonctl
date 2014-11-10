import urlparse
import urllib2
from suds.client import Client
from suds.transport.http import HttpAuthenticated



class Node(object):
	'''A single Halon node.'''
	
	name = None
	cluster = None
	scheme = 'http'
	host = None
	username = None
	password = None
	
	client = None
	
	def __init__(self, data=None, name=None):
		self.name = name
		self.cluster = NodeList([self])
		if data:
			self.load_data(data)
	
	def load_data(self, data):
		url = urlparse.urlparse(data, 'http')
		self.username = url.username
		self.password = url.password
		self.scheme = url.scheme
		
		# Nodes are specified as "[http[s]://][username[:password]@]0.0.0.0",
		# but if the protocol is absent, urlparse will treat the whole thing as
		# a path... so we instead have to parse the path component instead
		if url.hostname:
			self.host = url.hostname
		else:
			parts = url.path.split('@', 1)
			if len(parts) == 2:
				if ':' in parts[0]:
					self.username, self.password = parts[0].split(':', 1)
				else:
					self.username = parts[0]
				self.host = parts[1]
			else:
				self.host = parts[0]
	
	def connect(self):
		url = self.scheme + '://' + self.host + '/remote/'
		transport = HttpAuthenticated(username=self.username, password=self.password, timeout=5)
		client = Client(url + '?wsdl', location=url, transport=transport, timeout=5, faults=False)
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
		return u"%s @ [%s]" % (self.name, ', '.join([node.name for node in self]))
	
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
						node.connect()
					except urllib2.URLError, e:
						yield (node, (0, e.reason))
						continue
				yield (node, getattr(node.client.service, name)(*args, **kwargs))
		
		return proxy
