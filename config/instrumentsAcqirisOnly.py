"""
Initializes all the instruments and stores references to them in local variables.
"""

import sys

import os
import os.path

if not os.path.realpath(__file__+'../../../') in sys.path:
	sys.path.append(os.path.realpath(__file__+'../../../'))

from pyview.helpers.instrumentsmanager import *
if 'pyview.lib.datacube' in sys.modules:
  reload(sys.modules['pyview.lib.datacube'])
from pyview.lib.datacube import *
from pyview.config.parameters import params

print "Initializing instruments..."

serverAddress = "rip://127.0.0.1:8000"

instrumentManager = Manager()

instruments = [
    {
      'name' : 'register',
      #'serverAddress': serverAddress
    },
    {
     'name' : 'acqiris22',
   	  'class' : 'acqiris3',
      'serverAddress' : 'rip://192.168.0.22:8000',
      'kwargs' : {'name': 'Acqiris Card','__includeModuleDLL2__':True}
    },
    {
      'name' : 'fsp',
      #'serverAddress': serverAddress,
      'kwargs' : {'visaAddress' : 'TCPIP0::192.168.0.38::inst0'}
    } 
]
instrumentManager.initInstruments(instruments,globalParameters = {'forceReload' : True} )

for name in instrumentManager.instrumentNames():
  globals()[name] = instrumentManager.getInstrument(name)
 
  