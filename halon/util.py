from texttable import Texttable

def make_table(rows):
	table = Texttable()
	table.set_deco(Texttable.HEADER)
	table.add_rows(rows)
	return table

def print_table(*args, **kwargs):
	print make_table(*args, **kwargs).draw()
