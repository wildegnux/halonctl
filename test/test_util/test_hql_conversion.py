# -*- coding=utf-8 -*-
import unittest
from halonctl.util import hql_from_filters

class TestHQLConversion(unittest.TestCase):
	def test_hql_from_filters(self):
		self.assertEqual(hql_from_filters(["from~%@halon.se", "to~%@example.com"]), "from~%@halon.se to~%@example.com")
		self.assertEqual(hql_from_filters([]), "")
	
	def test_hql_from_filters_timestamps(self):
		self.assertEqual(hql_from_filters(["time>{2010-01-02 13:37:05}"]), "time>1262439425")
		self.assertEqual(hql_from_filters(["time>{2010-01-02 13:37:05}", "time<{2010-01-02 23:59:59}"]), "time>1262439425 time<1262476799")
		self.assertEqual(hql_from_filters(["time>{2010-01-02 13:37:05} time<{2010-01-02 23:59:59}"]), "time>1262439425 time<1262476799")
	
	def test_hql_from_filters_timezones(self):
		filters = ["time>{2010-01-02 13:37:05}"]
		self.assertEqual(hql_from_filters(filters, 0), "time>1262439425")
		self.assertEqual(hql_from_filters(filters, 1), "time>1262435825")
		self.assertEqual(hql_from_filters(filters, 6), "time>1262417825")
		self.assertEqual(hql_from_filters(filters, -7), "time>1262464625")
