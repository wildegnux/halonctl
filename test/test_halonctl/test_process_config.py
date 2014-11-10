import unittest
from halonctl import process_config

class TestProcessConfig(unittest.TestCase):
	def test_empty(self):
		nodes, clusters = process_config({})
		
		self.assertEqual(len(nodes), 0)
		self.assertEqual(len(clusters), 0)
	
	def test_no_nodes_or_clusters(self):
		nodes, clusters = process_config({
			'nodes': {},
			'clusters': {}
		})
		
		self.assertEqual(len(nodes), 0)
		self.assertEqual(len(clusters), 0)
	
	def test_single_node(self):
		nodes, clusters = process_config({
			'nodes': {
				'n1': 'http://admin:password@10.2.0.30'
			}
		})
		
		self.assertEqual(len(nodes), 1)
		self.assertEqual(len(clusters), 0)
		
		self.assertEqual(nodes['n1'].host, '10.2.0.30')
		self.assertEqual(nodes['n1'].username, 'admin')
		self.assertEqual(nodes['n1'].password, 'password')
	
	def test_cluster(self):
		nodes, clusters = process_config({
			'nodes': {
				'n1': "http://admin@10.2.0.30",
				'n2': "http://10.2.0.31"
			},
			'clusters': {
				'mycluster': [ 'n1', 'n2' ]
			}
		})
		
		self.assertEqual(len(nodes), 2)
		self.assertEqual(len(clusters), 1)
		
		# N1's username should be synced through the whole cluster
		self.assertEqual(clusters['mycluster'].username, 'admin')
		self.assertEqual(nodes['n1'].username, 'admin')
		self.assertEqual(nodes['n2'].username, 'admin')
	
	def test_cluster_username(self):
		nodes, clusters = process_config({
			'nodes': {
				'n1': "http://10.2.0.30",
				'n2': "http://10.2.0.31"
			},
			'clusters': {
				'mycluster': {
					'nodes': [ 'n1', 'n2' ],
					'username': 'admin'
				}
			}
		})
		
		# The cluster's username should be synced to the nodes
		self.assertEqual(clusters['mycluster'].username, 'admin')
		self.assertEqual(nodes['n1'].username, 'admin')
		self.assertEqual(nodes['n2'].username, 'admin')
	
	def test_cluster_password(self):
		nodes, clusters = process_config({
			'nodes': {
				'n1': "http://10.2.0.30",
				'n2': "http://10.2.0.31"
			},
			'clusters': {
				'mycluster': {
					'nodes': [ 'n1', 'n2' ],
					'password': 'password'
				}
			}
		})
		
		self.assertEqual(clusters['mycluster'].password, 'password')
		self.assertEqual(nodes['n1'].password, 'password')
		self.assertEqual(nodes['n2'].password, 'password')
