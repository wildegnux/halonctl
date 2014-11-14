from texttable import Texttable

def format(rows):
	table = Texttable()
	table.set_deco(Texttable.HEADER)
	table.add_rows(data)
	return table.draw()
