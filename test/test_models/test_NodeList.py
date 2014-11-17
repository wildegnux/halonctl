import unittest
from halonctl.models import Node, NodeList

class TestNodeList(unittest.TestCase):
	def setUp(self):
		self.cluster = NodeList([
			Node("http://0.0.0.1", 'n1'),
			Node("http://0.0.0.2", 'n2'),
			Node("http://0.0.0.3", 'n3'),
			Node("http://0.0.0.4", 'n4')
		])
	
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
		self.cluster.load_data({'username': 'admin', 'password': 'password'})
		self.cluster.sync_credentials()
		for node in self.cluster:
			self.assertEqual(node.username, 'admin')
			self.assertEqual(node.password, 'password')
	
	def test_sync_credentials_node_username(self):
		self.cluster[1].username = 'admin'
		self.cluster[1].password = 'password'
		self.cluster.sync_credentials()
		for node in self.cluster:
			self.assertEqual(node.username, 'admin')
			self.assertEqual(node.password, 'password')
	
	def test_sync_credentials_nodes_can_override(self):
		self.cluster[1].username = 'admin'
		self.cluster[1].password = 'password'
		self.cluster[2].username = 'admib'
		self.cluster[2].password = 'passbord'
		self.cluster.sync_credentials()
		self.assertEqual(self.cluster[0].username, 'admin')
		self.assertEqual(self.cluster[0].password, 'password')
		self.assertEqual(self.cluster[1].username, 'admin')
		self.assertEqual(self.cluster[1].password, 'password')
		self.assertEqual(self.cluster[2].username, 'admib')
		self.assertEqual(self.cluster[2].password, 'passbord')
