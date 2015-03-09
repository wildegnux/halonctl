import os
from pkg_resources import get_distribution, DistributionNotFound

__version__ = None

try:
	__version__ = get_distribution('halonctl').version
except DistributionNotFound:
	pass
