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
      'name' : 'register',
      'kwargs':{'filename' : 'registerScal5'}
    },
    {
      'name' : 'awgMW',
      'class' : 'awg',
      'kwargs' : {'visaAddress' : "TCPIP0::192.168.0.32::inst0"}
    },   
    {
      'name' : 'MWSource_JBA',
      'class' : 'agilent_mwg',
      'serverAddress' : localServerAdress,
      'kwargs' : {'name' : 'MWsource JBA','visaAddress':'GPIB0::19'}
    },    
    {
      'name' : 'MWSource_QB',
      'class' : 'agilent_mwg',
      'serverAddress' : localServerAdress,
      'kwargs' : {'name' : 'MWsource QB','visaAddress' : "TCPIP0::192.168.0.35::inst0"}
    },
    {
      'name' : 'fsp',
      'serverAddress' : localServerAdress,
      'kwargs' : {'visaAddress' : "TCPIP0::192.168.0.34::inst0"}
    },
    {
      'name' : 'IQMixer_JBA',
      'class' : 'iqmixer',
      'kwargs' : {'name' : 'MixerJBA', 'MWSource':'MWSource_JBA', 'AWG':'awgMW', 'AWGChannels':(1,2), 'fsp':'fsp'}
    },
    {
      'name':'PG_JBA_sb',
      'class':'pulse_generator',
      'kwargs':{'name':'Pulse Generator JBA sb', 'MWSource':'MWSource_JBA', 'mixer':'IQMixer_JBA', 'modulationMode':'IQMixer', 'formGenerator':'awgMW', 'AWGChannels':(1,2)}
    },
    {
      'name' : 'IQMixer_QB',
      'class' : 'iqmixer',
      'kwargs' : {'name' : 'IQMixerQB1', 'MWSource':'MWSource_QB', 'AWG':'awgMW', 'AWGChannels':(3,4), 'fsp':'fsp'}
    },
    {
      'name':'PG_QB_sb',
      'class':'pulse_generator',
      'kwargs':{'name':'Pulse Generator QB SB', 'MWSource':'MWSource_QB', 'mixer':'IQMixer_QB', 'modulationMode':'IQMixer', 'formGenerator':'awgMW', 'AWGChannels':(3,4)}
    },
    {
    'name':'pulsersManager',
    'class':'pulsers_manager',
    'kwargs':{'generators':[['PG_JBA_SB',True],['PG_QB_SB',False]]}
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
  