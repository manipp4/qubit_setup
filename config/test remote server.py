"""
Initializes all the instruments and stores references to them in local variables.
"""

import sys

import os
import os.path

if not os.path.realpath(__file__+'../../../') in sys.path:
	sys.path.append(os.path.realpath(__file__+'../../../'))

from pyview.helpers.instrumentsmanager import *
if 'pyview.helpers.instrumentsmanager' in sys.modules:
  reload(sys.modules['pyview.helpers.instrumentsmanager'])
if 'pyview.lib.datacube' in sys.modules:
  reload(sys.modules['pyview.lib.datacube'])
from pyview.lib.datacube import *
from pyview.config.parameters import params

print "Initializing instruments..."

serverAddress = "rip://192.168.0.1:8000"

instrumentManager = Manager()

instruments = [
	{
      'name' : 'JBA_Att',
      'class' : 'yokogawa',
      'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'Attenuator JBA','visaAddress' : 'GPIB0::10'}
    }
]
instrumentManager.initInstruments(instruments,globalParameters = {'forceReload' : True} )

for name in instrumentManager.instrumentNames():
  globals()[name] = instrumentManager.getInstrument(name)
  
