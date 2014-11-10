import unittest
from halon.models import Node

class TestNode(unittest.TestCase):
	def setUp(self):
		self.node = Node()
	
	def test_load_data_host_only(self):
		self.node.load_data("10.2.0.30")
		self.assertEqual(self.node.host, '10.2.0.30')
		self.assertIsNone(self.node.username)
	
	def test_load_data_host_and_username(self):
		self.node.load_data("admin@10.2.0.30")
		self.assertEqual(self.node.host, '10.2.0.30')
		self.assertEqual(self.node.username, 'admin')
