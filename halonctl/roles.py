import six
import arrow
from dateutil import tz

@six.python_2_unicode_compatible
class Role(object):
	'''
	A Role allows you to indicate the meaning of an otherwise context-sensitive
	value, such as a number. This allows intelligent formatting of values whose
	meaning would otherwise be impossible to discern.
	
	Feel free to implement your own roles, should you find that no built-in
	role suits your use-case.
	
	To implement your own Role, simply subclass Role, and override the
	constructor (to take whatever parameters you need), :func:`raw` and
	:func:`human`.
	'''
	
	def raw(self):
		'''
		Returns the raw, machine-readable value.
		
		This does not have to be the original value passed in, but should be
		in a form easily processed by a machine. Human-readability is welcome,
		but not required nor expected.
		'''
		raise NotImplementedError()
	
	def human(self):
		'''
		Returns a formatted, human-readable representation.
		
		Remember to be brief - your output is likely to be a space-constrained
		ASCII table; try not to break the layout with excessive verbosity.
		'''
		raise NotImplementedError()
	
	def __str__(self):
		return self.human()

class StatusCode(Role):
	'''
	A generic status code.
	
	A status code's raw representation is the code itself, the human
	representation (meaning) is looked up in a dictionary.
	
	:ivar dict codes: A dictionary of status codes to their meanings
	'''
	
	codes = {}
	
	def __init__(self, code):
		self.code = code
	
	def raw(self):
		return self.code
	
	def human(self):
		return self.codes[self.code] if self.code in self.codes else self.get_default(self.code)
	
	def get_default(self, code):
		return six.text_type(code)

class HTTPStatus(StatusCode):
	'''
	Denotes an HTTP status code.
	
	Note that the human representation is not always the spec-defined name of
	the status - in some cases, verbose names have been shortened.
	'''
	
	codes = {
		100: u"Continue",
		101: u"Switching protocols",
		200: u"OK",
		201: u"Created",
		202: u"Accepted",
		203: u"Unauthoritative",
		204: u"Empty",
		205: u"Reset",
		206: u"Partial",
		226: u"IM Used",
		300: u"Multiple Choices",
		301: u"Moved",
		302: u"Found",
		303: u"See Other",
		304: u"Not Modified",
		305: u"Use Proxy",
		306: u"Switch Proxy",
		307: u"Redirect", # Temporary Redirect
		308: u"Redirect", # Permanent Redirect
		400: u"Bad Request",
		401: u"Unauthorized",
		402: u"Payment Required",
		403: u"Forbidden",
		404: u"Not found",
		405: u"Method not allowed",
		406: u"Uncceptable",
		407: u"Proxy auth required",
		408: u"Request timeout",
		409: u"Conflict",
		410: u"Gone",
		411: u"Length required",
		412: u"Precondition failed",
		413: u"Body too large",
		414: u"URL too long",
		415: u"Unsupported media type",
		416: u"Range not satisfiable",
		417: u"Expectation failed",
		418: u"I'm a teapot",
		419: u"Auth timeout",
		426: u"Upgrade Required",
		428: u"Precondition Required",
		429: u"Too many requests",
		431: u"Header too large",
		451: u"Legal trouble",
		500: u"Error",
		501: u"Unimplemented",
		502: u"Bad Gateway",
		503: u"Unavailable",
		504: u"Gateway Timeout",
		505: u"HTTP Version Not Supported",
		506: u"Variant Also Negotiates",
		599: u"Timeout",		# Nonstandard
		
		0: u"Unreachable",		# Requests
		None: u"Unreachable",	# Requests
	}

class UTCDate(Role):
	'''
	Format UTC date with optional timezone
	
	A UTC date's raw representation is the unixtime itself, the human
	representation is a nicely formated date string (with timezone)
	'''
	
	def __init__(self, timestamp, timezone=0):
		self.timestamp = timestamp
		self.timezone = timezone
	
	def raw(self):
		return self.timestamp
	
	def human(self):
		return str(arrow.get(arrow.get(self.timestamp).naive, tz.tzoffset(None, self.timezone * 3600 if self.timezone else 0)))
