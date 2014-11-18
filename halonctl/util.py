import re
import arrow
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, wait
from dateutil import tz
from natsort import natsorted

executor = ThreadPoolExecutor(64)

def async_dispatch(tasks, node_sort_results=False):
	futures = { executor.submit(v): k for k, v in tasks.iteritems() }
	done, not_done = wait(futures)
	results = { futures[future]: future.result() for future in futures }
	
	return results if not node_sort_results else OrderedDict(natsorted(results.items(), key=lambda t: [t[0].cluster.name, t[0].name]))

def ask_confirm(prompt, default=True):
	'''Ask the user for confirmation.
	
	This prompts the user to answer either y/yes or n/no, with a default for if
	they just hit Enter.
	
	The question is presented as "Prompt [Yn]" or
	"Prompt [yN]", depending on the default answer, similar to for instance
	Debian's ``apt-get`` command. It will repeat until a valid answer is given.
	
	:rtype: bool
	'''
	if type(default) != bool:
		raise TypeError("The default value for ask_confirm must be a bool!")
	
	answers = {
		'y': True, 'yes': True,
		'n': False, 'no': False,
		'': default
	}
	suffixes = { True: '[Yn]', False: '[yN]' }
	
	while True:
		answer = raw_input("%s %s " % (prompt, suffixes[default])).lower()
		if not answer in answers:
			print "Enter either y/yes or n/no, or nothing for default (%s)" % \
				('yes' if default else 'no')
			continue
		return answers[answer]

filter_timestamp_re = re.compile(r'\{(.*)\}')
def hql_from_filters(filters, timezone):
	'''Gets a HQL statement from a list of filter components.
	
	Filter components may include ``{YYYY-MM-DD HH:MM:SS}`` placeholders, which
	are interpreted according to the given timezone and replaced with UTC
	timestamps.
	
	:param list filters: A list of filters to glue together
	:param int timezone: The UTC offset of the assumed timezone
	'''
	def get_date(s):
		return arrow.get(arrow.get(s).naive, tz.tzoffset(None, timezone*60*60))
	
	conditions = []
	for s in filters:
		s = filter_timestamp_re.sub(lambda m: str(get_date(m.groups(0)[0]).timestamp), s)
		conditions.append(s)
	
	return ' '.join(conditions)

def textualize_item(item):
	'''Formats an item in an output table for presentation.'''
	
	if item is None:
		return '-'
	elif item is True:
		return 'Yes'
	elif item is False:
		return 'No'
	return item

def textualize_row(row):
	'''Formats a row in an output table for presentation.'''
	return [textualize_item(item) for item in row]

def textualize_rows(rows):
	'''Formats a set of rows in an output table for presentation.'''
	return [textualize_row(row) for row in rows]
