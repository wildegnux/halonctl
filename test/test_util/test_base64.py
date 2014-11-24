# -*- coding=utf-8 -*-
import unittest
from halonctl.util import from_base64, to_base64

class TestBase64(unittest.TestCase):
	def test_to_base64(self):
		self.assertEqual(to_base64(u"Test"), u"VGVzdA==")
		self.assertEqual(to_base64(u"今日は"), u"5LuK5pel44Gv")
		self.assertEqual(to_base64(None), u"")
	
	def test_from_base64(self):
		self.assertEqual(from_base64(u"VGVzdA=="), u"Test")
		self.assertEqual(from_base64(u"5LuK5pel44Gv"), u"今日は")
		self.assertEqual(from_base64(None), u"")
