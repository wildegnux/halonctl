import csv
from StringIO import StringIO
from halon.util import textualize_rows

def format(rows):
	rows = textualize_rows(rows)
	buf = StringIO()
	w = csv.writer(buf)
	w.writerows(rows)
	return buf.getvalue()
