"""
Initializes all the instruments and stores references to them in local variables.
"""

import sys
import os
import os.path

if not os.path.realpath(__file__+'../../../') in sys.path:
	sys.path.append(os.path.realpath(__file__+'../../../'))

from pyview.helpers.instrumentsmanager import *
#if 'pyview.lib.datacube' in sys.modules:
#  reload(sys.modules['pyview.lib.datacube'])
#from pyview.lib.datacube import *
from pyview.config.parameters import params

print "Initializing instruments..."

serverAddress = "rip://127.0.0.1:8000"

instrumentManager = Manager()

instruments = [
    {
      'name' : 'register',
      'serverAddress': serverAddress
    },
    {
      'name' : 'acqiris34',
   	  'class' : 'acqiris3',
      'serverAddress' : 'rip://192.168.0.34:8000',
      'kwargs' : {'name': 'Acqiris Card','___includeDLLMath1Module___':True}
    },
    {
      'name' : 'vna',
      'kwargs' : {'visaAddress' : "GPIB0::6",'powerParams':{'offset':-7}}
    },
    {
      'name' : 'vnaK1',
      'class' : 'vna-keysight',
      'kwargs' : {'visaAddress' : "TCPIP0::192.168.0.71::inst0"}
    },
    {
      'name' : 'fsp',
      'class' : 'fsp',
      #'serverAddress': serverAddress,
      'kwargs' : {'visaAddress' : "TCPIP0::192.168.0.27::inst0"}
    },
    {
      'name' : 'Yoko3',
      'class' : 'yokogawa',
      #'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'Yoko2','visaAddress' : 'GPIB0::22'}
    },
    {
      'name' : 'Yoko1',
      'class' : 'yokogawa',
      #'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'Yoko1','visaAddress' : 'GPIB0::1'}
    },
]
instrumentManager.initInstruments(instruments,globalParameters = {'forceReload' : True} )

for name in instrumentManager.instrumentNames():
  globals()[name] = instrumentManager.getInstrument(name)
  