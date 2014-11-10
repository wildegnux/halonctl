import unittest
from halon.models import Node, NodeList

class TestNodeList(unittest.TestCase):
	def setUp(self):
		self.cluster = NodeList([Node("10.2.0.30", 'n1'), Node("10.2.0.31", 'n2')])
	
	def test_load_data_with_username(self):
		self.cluster.load_data({'username': 'admin'})
		self.assertEqual(self.cluster.username, 'admin')
	
	def test_load_data_empty(self):
		self.cluster.load_data({})
		self.assertIsNone(self.cluster.username)
	
	def test_load_data_list(self):
		self.cluster.load_data([])
		self.assertIsNone(self.cluster.username)
	
	def test_sync_credentials(self):
		self.cluster.load_data({'username': 'admin'})
		self.cluster.sync_credentials()
		for node in self.cluster:
			self.assertEqual(node.username, 'admin')
	
	def test_sync_credentials_node_username(self):
		self.cluster[1].username = 'admin'
		self.cluster.sync_credentials()
		for node in self.cluster:
			self.assertEqual(node.username, 'admin')
