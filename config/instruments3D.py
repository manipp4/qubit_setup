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
      'serverAddress': serverAddress
    },
    {
      'name' : 'vna',
      'kwargs' : {'visaAddress' : "GPIB0::6"}
    },
    {
      'name' : 'fsp',
      'serverAddress': serverAddress
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
      'class' : 'acqiris2',
      'serverAddress' : 'rip://192.168.0.22:8000',
      'kwargs' : {'name': 'Acqiris Card','__includeModuleDLL2__':False}
    },
    {
      'name' : 'awgMW',
      'class' : 'awg',
      'serverAddress' : serverAddress,
      'kwargs' : {'visaAddress' : "TCPIP0::192.168.0.14::inst0"}#192.168.0.14::inst0
    },
     {
      'name' : 'awgMW2',
      'class' : 'awgV2',
      'serverAddress' : serverAddress,
      'kwargs' : {'visaAddress' : "TCPIP0::192.168.0.14::inst0"}#192.168.0.14::inst0
    },
    {
      'name' : 'MWSource_Qubit',
      'class' : 'anritsu_mwg',
      'serverAddress' : serverAddress,
      'kwargs' : {'visaAddress' : "GPIB0::4"}
    },
    {
      'name' : 'MWSource_cavity',
      'class' : 'anritsu_mwg',
      'serverAddress' : serverAddress,
      'kwargs' : {'visaAddress' : "GPIB0::19"}
    },
    {
      'name' : 'MWSource_Qubit2',
      'class' : 'agilent_mwg',
      'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'MWSource_qubit2','visaAddress' : "TCPIP::192.168.0.25."}
    },
    {
      'name' : 'IQMixer_Cav',
      'class' : 'iqmixer',
      'kwargs' : {'name' : 'MixerJBA', 'MWSource':'MWSource_cavity', 'AWG':'awgMW', 'AWGChannels':(1,2), 'fsp':'fsp'}
    },
    {
      'name':'PG_Cavity',
      'class':'pulse_generator',
      'kwargs':{'name':'Pulse Generator Cavity', 'MWSource':'MWSource_cavity', 'mixer':'mixerQB', 'modulationMode':'SimpleMixer', 'formGenerator':'awgMW2', 'AWGChannels':(1)}
    },
     {
      'name':'PG_Cavity_switch',
      'class':'pulse_generator',
      'kwargs':{'name':'Pulse Generator Cavity Switch', 'MWSource':'MWSource_cavity', 'mixer':'mixerQB', 'modulationMode':'SimpleMixer', 'formGenerator':'awgMW2', 'AWGChannels':(2)}
    },
    {
      'name' : 'mixerQB',
      'class' : 'simplemixer',
      'kwargs' : {'name' : 'mixerQB', 'MWSource':'MWSource_Qubit', 'AWG':'awgMW', 'AWGChannel':(3), 'fsp':'fsp'}
    }
    ,
    {
      'name':'PG_QB',
      'class':'pulse_generator',
      'kwargs':{'name':'Pulse Generator QB', 'MWSource':'MWSource_Qubit2', 'mixer':'mixerQB', 'modulationMode':'SimpleMixer', 'formGenerator':'awgMW2', 'AWGChannels':(3)}
    },
    {
      'name':'PG_SWITCH',
      'class':'pulse_generator',
      'kwargs':{'name':'Pulse Generator SW', 'MWSource':'MWSource_Qubit', 'mixer':'mixerQB', 'modulationMode':'SimpleMixer', 'formGenerator':'awgMW', 'AWGChannels':(4)}
    },
    {
      'name':'PG_QU_GENE_SW',
      'class':'pulse_generator',
      'kwargs':{'name':'Pulse Generator SW', 'MWSource':'MWSource_Qubit', 'mixer':'mixerQB', 'modulationMode':'SimpleMixer', 'formGenerator':'awgMW', 'AWGChannels':(2)}
    },
    {
      'name' : 'Yoko3',
      'class' : 'yokogawa',
      'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'Yoko3','visaAddress' : 'GPIB0::3'}
    },
        {
      'name' : 'Yoko1',
      'class' : 'yokogawa',
      'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'Yoko1','visaAddress' : 'GPIB0::11'}
    },
    {
      'name' : 'Keithley2400',
      'class' : 'keithley2400',
      'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'Keithley2400','visaAddress' : 'GPIB0::9'}
    }    
]
instrumentManager.initInstruments(instruments,globalParameters = {'forceReload' : True} )

for name in instrumentManager.instrumentNames():
  globals()[name] = instrumentManager.getInstrument(name)
  