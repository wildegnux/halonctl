import unittest
from halon.models import Node

class TestNode(unittest.TestCase):
	def setUp(self):
		self.node = Node()
	
	def test_load_data_host_only(self):
		self.node.load_data("http://10.2.0.30")
		self.assertEqual(self.node.host, 'http://10.2.0.30')
		self.assertIsNone(self.node.username)
	
	def test_load_data_host_and_username(self):
		self.node.load_data("http://admin@10.2.0.30")
		self.assertEqual(self.node.host, 'http://10.2.0.30')
		self.assertEqual(self.node.username, 'admin')
	
	def test_load_data_https(self):
		self.node.load_data("https://admin@10.2.0.30")
		self.assertEqual(self.node.host, 'https://10.2.0.30')
		self.assertEqual(self.node.username, 'admin')