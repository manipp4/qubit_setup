import sys

import os
import os.path

# print 'Adding different default pathes to python environment.' 
sys.path.append(os.path.realpath(os.path.dirname(__file__)+"/../") )
sys.path.append(os.path.realpath(os.path.dirname(__file__)+"/../../") )
sys.path.append(os.path.realpath(os.path.dirname(__file__)+"/../../libs/") )
#sys.path.append(os.path.realpath("L:\python\qubit_setup\scripts"+"/../") )
#sys.path.append(os.path.realpath("L:\python\qubit_setup\scripts"+"/../../") )


#from config.environment import *
#print 'Importing pyview.gui.ide for startIDE() call'
from pyview.gui.ide import *

if __name__ == '__main__':
  	startIDE()
