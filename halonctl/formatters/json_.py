import six
import json
from halonctl.modapi import DictFormatter

class JSONFormatter(DictFormatter):
	def format(self, data):
		return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
	
	def format_item(self, item):
		return item
	
	def format_header(self, item):
		return six.text_type(item).lower().replace(' ', '_')

formatter = JSONFormatter()
