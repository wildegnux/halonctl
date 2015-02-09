import six
import json

def format(rows):
	data = [ { rows[0][i].lower(): row[i] for i in six.moves.xrange(len(row)) } for row in rows[1:] ]
	return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
