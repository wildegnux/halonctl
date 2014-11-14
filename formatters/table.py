from texttable import Texttable
from halon.util import textualize_rows

def format(rows):
	rows = textualize_rows(rows)
	table = Texttable()
	table.set_deco(Texttable.HEADER)
	table.add_rows(rows)
	return table.draw()
