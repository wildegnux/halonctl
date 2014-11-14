from texttable import Texttable

def format(rows):
	table = Texttable()
	table.set_deco(Texttable.HEADER)
	table.add_rows([ [ str(item) if item is not None else '-' for item in row ] for row in rows ])
	return table.draw()
