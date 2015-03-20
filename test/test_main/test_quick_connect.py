import unittest
from halonctl.__main__ import quick_node_re

class TestQuickConnectRegex(unittest.TestCase):
	def test_match_host_only(self):
		m = quick_node_re.match('admin@10.2.0.30')
		self.assertEqual(m.group('username'), 'admin')
		self.assertEqual(m.group('host'), '10.2.0.30')
		self.assertEqual(m.group('data'), 'admin@10.2.0.30')
	
	def test_match_named(self):
		m = quick_node_re.match('name=admin@10.2.0.30')
		self.assertEqual(m.group('name'), 'name')
		self.assertEqual(m.group('username'), 'admin')
		self.assertEqual(m.group('host'), '10.2.0.30')
		self.assertEqual(m.group('data'), 'admin@10.2.0.30')
	
	def test_match_with_http(self):
		m = quick_node_re.match('name=http://admin@10.2.0.30')
		self.assertEqual(m.group('protocol'), 'http')
	
	def test_match_with_https(self):
		m = quick_node_re.match('name=https://admin@10.2.0.30')
		self.assertEqual(m.group('protocol'), 'https')
	
	def test_match_with_http_and_port(self):
		m = quick_node_re.match('name=http://admin@10.2.0.30:8080')
		self.assertEqual(m.group('port'), '8080')
	
	def test_match_host_and_port(self):
		m = quick_node_re.match('admin@10.2.0.30:8080')
		self.assertEqual(m.group('username'), 'admin')
		self.assertEqual(m.group('host'), '10.2.0.30')
		self.assertEqual(m.group('port'), '8080')
