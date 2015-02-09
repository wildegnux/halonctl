import unittest
from halonctl.__main__ import apply_slice

class TestApplySlice(unittest.TestCase):
	def setUp(self):
		self.items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
	
	def test_empty(self):
		self.assertEqual(apply_slice(self.items, ''), self.items)
	
	def test_single_number(self):
		self.assertEqual(apply_slice(self.items, '1'), [1])
		self.assertEqual(apply_slice(self.items, '2'), [2])
		self.assertEqual(apply_slice(self.items, '10'), [10])
	
	def test_range(self):
		self.assertEqual(apply_slice(self.items, '1:2'), [1, 2])
		self.assertEqual(apply_slice(self.items, '2:2'), [2])
		self.assertEqual(apply_slice(self.items, '5:6'), [5, 6])
		self.assertEqual(apply_slice(self.items, '2:7'), [2, 3, 4, 5, 6, 7])
	
	def test_uncapped_range(self):
		self.assertEqual(apply_slice(self.items, '6:'), [6, 7, 8, 9, 10])
		self.assertEqual(apply_slice(self.items, ':6'), [1, 2, 3, 4, 5, 6])
	
	def test_step(self):
		self.assertEqual(apply_slice(self.items, '::2'), [1, 3, 5, 7, 9])
		self.assertEqual(apply_slice(self.items, '1::2'), [1, 3, 5, 7, 9])
		self.assertEqual(apply_slice(self.items, '2::2'), [2, 4, 6, 8, 10])
		
		self.assertEqual(apply_slice(self.items, '::-1'), [10, 9, 8, 7, 6, 5, 4, 3, 2, 1])
		self.assertEqual(apply_slice(self.items, '::-2'), [10, 8, 6, 4, 2])
