from prettytable import PrettyTable
from halonctl.modapi import Formatter

class TableFormatter(Formatter):
	def format(self, data, args):
		table = PrettyTable(data[0])
		
		table.align = "l"
		table.border = False
		table.left_padding_width = 0
		table.right_padding_width = 2
		
		for row in data[1:]:
			table.add_row(row)
		return table.get_string()

formatter = TableFormatter()
