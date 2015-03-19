import halonctl.__main__ as m

try:
	import cProfile as profile
except ImportError:
	import profile as p

if __name__ == '__main__':
	profile.run('m.main()', sort='cumulative')
