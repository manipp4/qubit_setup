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
      'name' : 'register3D',
      'serverAddress': serverAddress
    },
    {
      'name' : 'vna',
      'visaAddress': "GPIB0::6"
    },
    {
      'name' : 'temperature',
      'serverAddress': serverAddress,
      'kwargs' : {}
    },
    {
      'name' : 'helium_level',
      'serverAddress': serverAddress
    },
    {
      'name' : 'acqiris',
      'serverAddress' : 'rip://192.168.0.22:8000',
      'kwargs' : {'name': 'Acqiris Card'}
    },
    {
      'name' : 'awgMW',
      'class' : 'awg',
      'serverAddress' : serverAddress,
      'kwargs' : {'visaAddress' : "TCPIP0::192.168.0.14::inst0"}
    },
    {
      'name' : 'MWSource_Qubit',
      'class' : 'agilent_mwg',
      'serverAddress' : serverAddress,
      'kwargs' : {'visaAddress' : "TCPIP::192.168.0.12"}
    },
    {
      'name' : 'MWSource_cavity',
      'class' : 'anritsu_mwg',
      'serverAddress' : serverAddress,
      'kwargs' : {'visaAddress' : "GPIB0::4"}
    }      
]
instrumentManager.initInstruments(instruments,globalParameters = {'forceReload' : True} )

for name in instrumentManager.instrumentNames():
  globals()[name] = instrumentManager.getInstrument(name)
  
