import csv
from six.moves import StringIO
from halonctl.util import textualize_rows

def format(rows):
	rows = textualize_rows(rows)
	buf = StringIO()
	w = csv.writer(buf)
	w.writerows(rows)
	return buf.getvalue()
