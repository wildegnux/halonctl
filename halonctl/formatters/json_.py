import six
import json
from halonctl.modapi import DictFormatter
from halonctl.util import textualize

class JSONFormatter(DictFormatter):
	def format(self, data, args):
		return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
	
	def format_key(self, header, args):
		return six.text_type(header).lower().replace(' ', '_')

formatter = JSONFormatter()
