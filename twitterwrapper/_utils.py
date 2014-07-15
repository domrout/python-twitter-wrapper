from shutil import copyfileobj
from functools import partial
from contextlib import closing

import pkg_resources

PACKAGE_NAME = "twitterwrapper"

open_data = partial(pkg_resources.resource_stream, PACKAGE_NAME)

def copy_default(filename, to_filename = None):
  if to_filename is None:
      to_filename = filename

  with closing(open_data("defaults/%s" % filename)) as default:
    with open(to_filename, "w") as destination:
      copyfileobj(default, destination)