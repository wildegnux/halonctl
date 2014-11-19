from prettytable import PrettyTable
from halonctl.util import textualize_row

def format(rows):
	table = PrettyTable(rows[0])
	
	table.align = "l"
	table.border = False
	table.left_padding_width = 0
	table.right_padding_width = 2
	
	for row in rows[1:]:
		table.add_row(textualize_row(row))
	
	return table.get_string()
