import sys

import os
import os.path

sys.path.append(os.path.realpath(os.path.dirname(__file__)+"/../") )

from pyview.server.pickle_server import *

if __name__ == '__main__':
  startServer()
