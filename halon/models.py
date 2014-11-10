class Node(object):
	'''A single VSP node.'''
	
	name = None
	host = None
	username = None
	password = None
	
	def __init__(self, data=None, name=None):
		self.name = name
		if data:
			self.load_data(data)
	
	def load_data(self, data):
		# Nodes are specified by strings, either as just an ip ('0.0.0.0'), or
		# with a username prepended ('admin@0.0.0.0'). Note that a cluster's
		# credentials will overwrite those of all nodes in it.
		parts = data.split('@', 1)
		if len(parts) == 2:
			self.username = parts[0]
			self.host = parts[1]
		else:
			self.host = parts[0]
	
	def __unicode__(self):
		return u"%s@%s" % (self.username, self.host)
	
	def __str__(self):
		return unicode(self).encode('utf-8')

class NodeList(list):
	'''A list of VSP nodes.
	
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
	
	def sync_credentials(self):
		# If we don't have an username given for the cluster, see if one of the
		# nodes has one
		if not self.username:
			for node in self:
				if node.username:
					self.username = node.username
					self.password = node.password
					break
		
		# Same deal with the password, if we didn't find one with the username
		if not self.password:
			for node in self:
				if node.password:
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
