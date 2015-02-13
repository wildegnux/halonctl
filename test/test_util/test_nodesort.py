import unittest
import random
from halonctl.util import nodesort
from halonctl.models import Node, NodeList

class TestNodeSort(unittest.TestCase):
	def setUp(self):
		self.nodes = [Node(name="n{0}".format(i)) for i in range(10)]
		
		self.c1 = NodeList([self.nodes[0], self.nodes[1], self.nodes[2], self.nodes[3]])
		self.c1.name = "c1"
		for node in self.c1:
			node.cluster = self.c1
		
		self.c2 = NodeList([self.nodes[4], self.nodes[5], self.nodes[6], self.nodes[7]])
		self.c2.name = "c2"
		for node in self.c2:
			node.cluster = self.c2
		
		self.c3 = NodeList([self.nodes[8], self.nodes[9]])
		self.c3.name = None
		for node in self.c3:
			node.cluster = self.c3
		
		self.correct_order = [
			self.nodes[8], self.nodes[9],
			self.nodes[0], self.nodes[1], self.nodes[2], self.nodes[3],
			self.nodes[4], self.nodes[5], self.nodes[6], self.nodes[7]
		]
	
	def test_sort_list(self):
		self.assertEqual(nodesort(self.nodes), self.correct_order)
	
	def test_sort_dict(self):
		d = { node: node.name for node in self.nodes }
		self.assertEqual(list(nodesort(d).keys()), self.correct_order)
