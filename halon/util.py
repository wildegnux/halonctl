import re
import arrow
from dateutil import tz

filter_timestamp_re = re.compile(r'\{(.*)\}')

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

def hql_from_filters(filters, timezone):
	def get_date(s):
		return arrow.get(arrow.get(s).naive, tz.tzoffset(None, timezone*60*60))
	
	conditions = []
	for s in filters:
		s = filter_timestamp_re.sub(lambda m: str(get_date(m.groups(0)[0]).timestamp), s)
		conditions.append(s)
	
	return ' '.join(conditions)

def textualize_item(item):
	if item is None:
		return '-'
	elif item is True:
		return 'Yes'
	elif item is False:
		return 'No'
	return item

def textualize_row(row):
	return [textualize_item(item) for item in row]

def textualize_rows(rows):
	return [textualize_row(row) for row in rows]
