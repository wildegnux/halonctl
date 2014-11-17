import unittest
from halonctl.models import Node

class TestNode(unittest.TestCase):
	def setUp(self):
		self.node = Node()
	
	def test_load_data_host_only(self):
		self.node.load_data("0.0.0.0")
		self.assertEqual(self.node.scheme, 'http')
		self.assertEqual(self.node.host, '0.0.0.0')
		self.assertIsNone(self.node.username)
		self.assertIsNone(self.node.password)
	
	def test_load_data_username(self):
		self.node.load_data("admin@0.0.0.0")
		self.assertEqual(self.node.scheme, 'http')
		self.assertEqual(self.node.host, '0.0.0.0')
		self.assertEqual(self.node.username, 'admin')
		self.assertIsNone(self.node.password)
	
	def test_load_data_username_password(self):
		self.node.load_data("admin:password@0.0.0.0")
		self.assertEqual(self.node.scheme, 'http')
		self.assertEqual(self.node.host, '0.0.0.0')
		self.assertEqual(self.node.username, 'admin')
		self.assertEqual(self.node.password, 'password')
	
	def test_load_data_username_password_protocol(self):
		self.node.load_data("http://admin:password@0.0.0.0")
		self.assertEqual(self.node.scheme, 'http')
		self.assertEqual(self.node.host, '0.0.0.0')
		self.assertEqual(self.node.username, 'admin')
		self.assertEqual(self.node.password, 'password')
	
	def test_load_data_https(self):
		self.node.load_data("https://admin@0.0.0.0")
		self.assertEqual(self.node.scheme, 'https')
		self.assertEqual(self.node.host, '0.0.0.0')
		self.assertEqual(self.node.username, 'admin')
		self.assertIsNone(self.node.password)
