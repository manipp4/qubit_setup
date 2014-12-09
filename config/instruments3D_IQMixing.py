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
      'name' : 'vna',
      'kwargs' : {'visaAddress' : "GPIB0::6"}
    },
    {
      'name' : 'fsp',
      'serverAddress': serverAddress,
      'kwargs' : {'visaAddress' : "TCPIP0::192.168.0.27::inst0"}
    },
    {
      'name' : 'mmr3_module1',
      'class': 'mmr3_module',
      'serverAddress': serverAddress,
      'kwargs' : {'address':'192.168.0.61','port':11061,'thermoVarIndices':[5,16,27]}
    },
    {
      'name' : 'mmr3_module2',
      'class': 'mmr3_module',
      'serverAddress': serverAddress,
      'kwargs' : {'address':'192.168.0.62','port':11062,'thermoVarIndices':[5,16,27]}
    },
    #{
    #  'name' : 'helium_level',
    #  'serverAddress': serverAddress
    #},
    #{
    #  'name' : 'acqiris22',
   	#  'class' : 'acqiris2',
    #  'serverAddress' : 'rip://192.168.0.22:8000',
    #  'kwargs' : {'name': 'Acqiris Card','__includeModuleDLL2__':False}
    #},
     {
      'name' : 'acqiris34',
   	  'class' : 'acqiris3',
      'serverAddress' : 'rip://192.168.0.34:8000',
      'kwargs' : {'name': 'Acqiris Card','___includeDLLMath1Module___':True}
    },
    #{
      #'name' : 'acqiris19',
   	  #'class' : 'acqiris3',
     # 'serverAddress' : 'rip://192.168.0.19:8000',
    #  'kwargs' : {'name': 'Acqiris Card','__includeModuleDLL2__':False}
   # },
   # {
   #   'name' : 'awgMW',
   #   'class' : 'awg',
   #   'serverAddress' : serverAddress,
   #   'kwargs' : {'visaAddress' : "TCPIP0::192.168.0.14::inst0"}#192.168.0.14::inst0
   # },
     {
      'name' : 'awgMW2',
      'class' : 'awgV2',
      'serverAddress' : serverAddress,
      'kwargs' : {'visaAddress' : "TCPIP0::192.168.0.28::inst0"}#192.168.0.14::inst0
    },
    #{
    #  'name' : 'MWSource1',
    #  'class' : 'anritsu_mwg',
    #  'serverAddress' : serverAddress,
    #  'kwargs' : {'visaAddress' : "GPIB0::4"}
    #},
    {
      'name' : 'MWSource_Paramp',
      'class' : 'rohdeschwarz_mwg',
      'serverAddress' : serverAddress,
      'kwargs' : {'visaAddress' : "GPIB0::28"}
    },
    {
      'name' : 'MWSource_Cavity',
      'class' : 'agilent_mwg',
      'serverAddress' : serverAddress,
      'kwargs' : {'visaAddress' : "TCPIP::192.168.0.21"}
    },
    {
      'name' : 'MWSource_Qubit',
      'class' : 'agilent_mwg',
      'serverAddress' : serverAddress,
      'kwargs' : {'visaAddress' : "TCPIP::192.168.0.35"}
    },
    {
      'name' : 'IQMixer_Cav',
      'class' : 'iqmixer',
      'kwargs' : {'name' : 'MixerCavity', 'MWSource':'MWSource_Cavity', 'AWG':'awgMW2', 'AWGChannels':(1,2), 'fsp':'fsp'}
    },
    #{
    #  'name' : 'mixerCav',
    #  'class' : 'simplemixer',
    #  'kwargs' : {'name' : 'mixerCav', 'MWSource':'MWSource_Cavity', 'AWG':'awgMW2', 'AWGChannel':(1), 'fsp':'fsp'}
    #},
    {
      'name' : 'mixerQB',
      'class' : 'simplemixer',
      'kwargs' : {'name' : 'mixerQB', 'MWSource':'MWSource_Qubit', 'AWG':'awgMW2', 'AWGChannel':(3), 'fsp':'fsp'}
    },
    #{
    #  'name':'PG_Cavity',
    #  'class':'pulse_generator',
    #  'kwargs':{'name':'Pulse Generator Cavity', 'MWSource':'MWSource_Cavity', 'mixer':'IQMixer_Cav', 'modulationMode':'IQMixer', 'formGenerator':'awgMW2', 'AWGChannels':(1,2)}
    #},
    {
      'name':'PG_Cav',
      'class':'pulse_generator',
      'kwargs':{'name':'Pulse Generator QB', 'MWSource':'MWSource_Cavity', 'mixer':'IQMixer_Cav', 'modulationMode':'IQMixer', 'formGenerator':'awgMW2', 'AWGChannels':(1,2)}
    },
    {
      'name':'PG_QB',
      'class':'pulse_generator',
      'kwargs':{'name':'Pulse Generator QB', 'MWSource':'MWSource_Qubit', 'mixer':'mixerQB', 'modulationMode':'SimpleMixer', 'formGenerator':'awgMW2', 'AWGChannels':(3)}
    },
	{
      'name' : 'Yoko3',
      'class' : 'yokogawa',
      'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'Yoko2','visaAddress' : 'GPIB0::22'}
    },
    {
      'name' : 'Yoko1',
      'class' : 'yokogawa',
      'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'Yoko1','visaAddress' : 'GPIB0::1'}
    },
    {
      'name' : 'Yoko2',
      'class' : 'yokogawa',
      'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'Yoko1','visaAddress' : 'GPIB0::19'}
    },
    {
      'name' : 'Yoko4',
      'class' : 'yokogawa',
      'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'Yoko1','visaAddress' : 'GPIB0::4'}
    },
    #{
    #  'name' : 'Keithley2400',
    #  'class' : 'keithley2400',
    #  'serverAddress' : serverAddress,
    #  'kwargs' : {'name' : 'Keithley2400','visaAddress' : 'GPIB0::24'}
    #}    
]
instrumentManager.initInstruments(instruments,globalParameters = {'forceReload' : True} )

for name in instrumentManager.instrumentNames():
  globals()[name] = instrumentManager.getInstrument(name)
  