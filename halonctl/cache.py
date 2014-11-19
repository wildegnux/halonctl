import os
import tempfile

def get_filename(name):
	return "halonctl_{name}".format(name=name)

def get_path(name):
	return os.path.abspath(os.path.join(tempfile.gettempdir(), get_filename(name)))

def get(name):
	path = get_path(name)
	if os.path.exists(path):
		with open(get_path(name), 'rU') as f:
			return f.read()

def set(name, data):
	path = get_path(name)
	with open(get_path(name), 'wU') as f:
		f.write(data)
