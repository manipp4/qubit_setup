"""
Initializes all the instruments and stores references to them in local variables.
"""

import sys

import os		
import os.path

if not os.path.realpath(__file__+'../../../') in sys.path:
	sys.path.append(os.path.realpath(__file__+'../../../'))

from pyview.helpers.instrumentsmanager import *
from pyview.config.parameters import params

print "Initializing instruments..."

localServerAdress = "rip://127.0.0.1:8000"
serverAddress = localServerAdress#"rip://192.168.0.1:8000"

instrumentManager = Manager()

instruments = [
    {
      'name' : 'register',
      'serverAddress':localServerAdress,
      'kwargs':{'filename' : 'registerScal5'}
    }
]
instrumentManager.initInstruments(instruments,globalParameters = {'forceReload' : True} )

for name in instrumentManager.instrumentNames():
  globals()[name] = instrumentManager.getInstrument(name)
  
  
##
d.setParameters(Manager().saveState('currentState'))