from shutil import copyfileobj
from functools import partial


import pkg_resources
open_data = partial(pkg_resources.resource_stream, __name__)

def copy_default(filename, to_filename):
	with open_data("defaults/%s" % filename) as default:
		with open(to_filename, "w") as destination:
			copyfileobj(default, destination)