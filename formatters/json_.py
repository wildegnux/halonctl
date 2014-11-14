import json

def format(rows):
	data = [ { rows[0][i].lower(): row[i] for i in xrange(len(row)) } for row in rows[1:] ]
	return json.dumps(data, encoding='utf-8')
