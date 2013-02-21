import sys

import os
import os.path

sys.path.append(os.path.realpath(os.path.dirname(__file__)+"/../") )
sys.path.append(os.path.realpath(os.path.dirname(__file__)+"/../../libs/") )

from pyview.server.pickle_server import *

if __name__ == '__main__':
  startServer()
