"""
Initializes all the instruments and stores references to them in global variables.
"""

import sys

import os
import os.path

if not os.path.realpath(__file__+'../../../') in sys.path:
	sys.path.append(os.path.realpath(__file__+'../../../'))

from pyview.helpers.instrumentsmanager import *
from pyview.lib.datacube import *
from pyview.config.parameters import params

print "Initializing instruments..."

serverAddress = "rip://127.0.0.1:8000"

instrumentManager = Manager()

instruments = [
    {
      'name' : 'vna',
      'serverAddress' : serverAddress,
      'kwargs' : {'visaAddress': "GPIB0::6"}
    },
    {
      'name' : 'acqiris19',
   	  'class' : 'acqiris3',
      'serverAddress' : 'rip://192.168.0.19:8000',
      'kwargs' : {'name': 'Acqiris Card','__includeModuleDLL2__':False}
    }, 
    {
      'name' : 'oscilloscope',
      'class' : 'lecroy_waverunner_scope',
      'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'oscilloscope','visaAddress' : "TCPIP::192.168.0.30"}
    },
]
instrumentManager.initInstruments(instruments,globalParameters = {'forceReload' : True} )

for name in instrumentManager.instrumentNames():
  globals()[name] = instrumentManager.getInstrument(name)
  
