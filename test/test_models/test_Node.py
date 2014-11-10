import unittest
from halon.models import Node

class TestNode(unittest.TestCase):
	def setUp(self):
		self.node = Node()
	
	def test_load_data_host_only(self):
		self.node.load_data("10.2.0.30")
		self.assertEqual(self.node.scheme, 'http')
		self.assertEqual(self.node.host, '10.2.0.30')
		self.assertIsNone(self.node.username)
		self.assertIsNone(self.node.password)
	
	def test_load_data_username(self):
		self.node.load_data("admin@10.2.0.30")
		self.assertEqual(self.node.scheme, 'http')
		self.assertEqual(self.node.host, '10.2.0.30')
		self.assertEqual(self.node.username, 'admin')
		self.assertIsNone(self.node.password)
	
	def test_load_data_username_password(self):
		self.node.load_data("admin:password@10.2.0.30")
		self.assertEqual(self.node.scheme, 'http')
		self.assertEqual(self.node.host, '10.2.0.30')
		self.assertEqual(self.node.username, 'admin')
		self.assertEqual(self.node.password, 'password')
	
	def test_load_data_username_password_protocol(self):
		self.node.load_data("http://admin:password@10.2.0.30")
		self.assertEqual(self.node.scheme, 'http')
		self.assertEqual(self.node.host, '10.2.0.30')
		self.assertEqual(self.node.username, 'admin')
		self.assertEqual(self.node.password, 'password')
	
	def test_load_data_https(self):
		self.node.load_data("https://admin@10.2.0.30")
		self.assertEqual(self.node.scheme, 'https')
		self.assertEqual(self.node.host, '10.2.0.30')
		self.assertEqual(self.node.username, 'admin')
		self.assertIsNone(self.node.password)
