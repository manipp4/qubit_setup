import sys

import os
import os.path

sys.path.append(os.path.realpath(os.path.dirname(__file__)+"/../") )
sys.path.append(os.path.realpath(os.path.dirname(__file__)+"/../../") )
#sys.path.append(os.path.realpath("L:\python\qubit_setup\scripts"+"/../") )
#sys.path.append(os.path.realpath("L:\python\qubit_setup\scripts"+"/../../") )


from config.environment import *
from pyview.gui.ide import *

if __name__ == '__main__':
  startIDE()
