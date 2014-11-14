import csv
from StringIO import StringIO

def format(rows):
	buf = StringIO()
	w = csv.writer(buf)
	w.writerows(rows)
	return buf.getvalue()
