from __future__ import print_function
import six
import sys
from cProfile import Profile
from pstats import Stats
from contextlib import contextmanager
from halonctl.util import open_fuzzy

@contextmanager
def profile(to=None, sort_by='cumtime'):
	'''Profiles a chunk of code, use with the ``with`` statement::
	
	    from halonctl.debug import profile
	    
	    with profile('~/Desktop/stats'):
	    	pass # Do something performance-critical here...
	
	Results for individual runs are collected into ``to``. The specifics of how
	reports are done varies depending on what type ``to`` is.
	
	* **File-like objects**: Stats are dumped, according to ``sort_by``, into the stream, separated by newlines - watch out, the file/buffer may grow very big when used in loops.
	* **List-like objects**: A number of pstats.Stats objects are appended.
	* **str and unicode**: Treated as a path and opened for appending. Tildes (~) will be expanded, and intermediary directories created if possible.
	* **None or omitted**: Results are printed to sys.stderr.
	'''
	
	if isinstance(to, six.string_types):
		to = open_fuzzy(to, 'a')
	
	to_is_stream = hasattr(to, 'write')
	to_is_list = hasattr(to, 'append')
	
	p = Profile()
	p.enable()
	yield
	p.disable()
	
	ps = Stats(p, stream=to if to_is_stream else sys.stderr)
	ps.sort_stats('cumtime')
	
	if to_is_stream or to is None:
		ps.print_stats()
	elif to_is_list:
		to.append(ps)
