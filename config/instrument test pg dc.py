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
serverAddress = localServerAdress

instrumentManager = Manager()

instruments = [
    {
      'name' : 'awgF',
      'class' : 'awg',
      'kwargs' : {'visaAddress' : "TCPIP0::192.168.0.32::inst0"}
    },    
    {
      'name' : 'awgMW',
      'class' : 'awg',
      'kwargs' : {'visaAddress' : "TCPIP0::192.168.0.33::inst0"}
    },
    {
      'name':'PG_fake',
      'class':'pulse_generator',
      'kwargs':{'name':'Pulse Generator Flux fake', 'formGenerator':'awgMW', 'AWGChannels':[1]}
    },
    {
      'name':'PG_F1',
      'class':'pulse_generator',
      'kwargs':{'name':'Pulse Generator Flux 1', 'formGenerator':'awgF', 'AWGChannels':[1]}
    },
    {
      'name':'PG_F2',
      'class':'pulse_generator',
      'kwargs':{'name':'Pulse Generator Flux 2', 'formGenerator':'awgF', 'AWGChannels':[2]}
    },
    {
      'name':'PG_F3',
      'class':'pulse_generator',
      'kwargs':{'name':'Pulse Generator Flux 3', 'formGenerator':'awgF', 'AWGChannels':[3]}
    },
    {
      'name':'PG_F4',
      'class':'pulse_generator',
      'kwargs':{'name':'Pulse Generator Flux 4', 'formGenerator':'awgF', 'AWGChannels':[4]}
    },
    {
    'name':'pulsersManager',
    'class':'pulsers_manager',
    'kwargs':{'generators':[['PG_F1',True],['PG_F2',True],['PG_F3',True],['PG_F4',True],['PG_fake',True]]}
    },
    {
    'name':'scope',
    'class':'lecroy_waverunner_scope',
    'kwargs':{'visaAddress':"TCPIP0::192.168.0.30::inst0"}
    }
]
instrumentManager.initInstruments(instruments,globalParameters = {'forceReload' : True} )

for name in instrumentManager.instrumentNames():
  globals()[name] = instrumentManager.getInstrument(name)
  