from texttable import Texttable

def make_table(rows):
	table = Texttable()
	table.set_deco(Texttable.HEADER)
	table.add_rows(rows)
	return table

def print_table(*args, **kwargs):
	print make_table(*args, **kwargs).draw()

def ask_confirm(prompt, default=True):
	if type(default) != bool:
		raise TypeError("The default value for ask_confirm must be a bool!")
	
	answers = {
		'y': True, 'yes': True,
		'n': False, 'no': False,
		'': default
	}
	suffixes = { True: '[Yn]', False: '[yN]' }
	
	while True:
		answer = raw_input("%s %s: " % (prompt, suffixes[default])).lower()
		if answer in answers:
			return answers[answer]
		else:
			print "Enter either y/yes or n/no, or nothing for default (%s)" % \
				('yes' if default else 'no')
