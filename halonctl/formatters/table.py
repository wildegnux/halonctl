from texttable import Texttable
from blessings import Terminal
from halonctl.util import textualize_rows

def format(rows):
	rows = textualize_rows(rows)
	term = Terminal()
	table = Texttable(term.width)
	table.set_deco(Texttable.HEADER)
	table.add_rows(rows)
	return table.draw()
