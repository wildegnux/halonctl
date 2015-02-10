import csv
from six.moves import StringIO
from halonctl.modapi import Formatter

class CSVFormatter(Formatter):
	def format(self, data):
		buf = StringIO()
		w = csv.writer(buf)
		w.writerows(data)
		return buf.getvalue()

formatter = CSVFormatter()
