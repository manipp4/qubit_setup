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
      'class' : 'register',
      'serverAddress': serverAddress
    },
    {
      'name' : 'vna',     
      'serverAddress' : "rip://192.168.0.1:8000",
      'visaAddress': "GPIB0::6"
    },
    {
      'name' : 'temperature',
      'serverAddress': serverAddress,
      'kwargs' : {}
    },
    {
      'name' : 'helium_level',
      'serverAddress': serverAddress,
    },
    {
      'name' : 'acqiris',
      'serverAddress' : 'rip://192.168.0.22:8000',
      'kwargs' : {'name': 'Acqiris Card'}
    },
    {
      'name' : 'awg3D',
      'class' : 'awg',
      'serverAddress' : serverAddress,
      'kwargs' : {'visaAddress' : "TCPIP0::192.168.0.14::inst0"}
    },
    {
      'name' : 'awgMW',
      'class' : 'awg',
      'serverAddress' : serverAddress,
      'kwargs' : {'visaAddress' : "TCPIP0::192.168.0.3::inst0"}
    },    
    {
      'name' : 'MWSource_JBA',
      'class' : 'agilent_mwg',
      'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'MWsource JBA','visaAddress' : "TCPIP0::192.168.0.12::inst0"}
    },
    {
	  'name' : 'coil',
      'class' : 'yokogawa',
      'serverAddress' : "rip://192.168.0.1:8000",
      'kwargs' : {'name' : 'Coil','visaAddress' : 'GPIB0::10'}
    },    
    {
      'name' : 'MWSource_QB',
      'class' : 'agilent_mwg',
      'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'MWsource QB','visaAddress' : "TCPIP0::192.168.0.13::inst0"}
    },    
    {
      'name' : 'MWSource_JBA_anritsu',
      'class' : 'anritsu_mwg',
      'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'MWsource JBA_old','visaAddress' : "GPIB0::4"}
    },    
    {
      'name' : 'MWSource_JBA_perturb_anritsu',
      'class' : 'anritsu_mwg',
      'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'MWsource JBA_old','visaAddress' : "GPIB0::14"}
    },
    {
      'name' : 'fsp',
      'serverAddress' : serverAddress
    },
    {
      'name' : 'IQMixer_JBA',
      'class' : 'iqmixer',
      'kwargs' : {'name' : 'MixerJBA', 'MWSource':'MWSource_JBA', 'AWG':'awgMW', 'AWGChannels':(1,2), 'fsp':'fsp'}
    },
    {
      'name' : 'mixerQBSimple',
      'class' : 'simplemixer',
      'kwargs' : {'name' : 'mixerQBSimple', 'MWSource':'MWSource_QB', 'AWG':'awgMW', 'AWGChannel':(3), 'fsp':'fsp'}
    },
    {
      'name':'PG_JBA_sb',
      'class':'pulse_generator',
      'kwargs':{'name':'Pulse Generator JBA sb', 'MWSource':'MWSource_JBA', 'mixer':'IQMixer_JBA', 'modulationMode':'IQMixer', 'formGenerator':'awgMW', 'AWGChannels':(1,2)}
    },
    {
      'name':'PG_QB',
      'class':'pulse_generator',
      'kwargs':{'name':'Pulse Generator QB', 'MWSource':'MWSource_QB', 'mixer':'mixerQBSimple', 'modulationMode':'SimpleMixer', 'formGenerator':'awgMW', 'AWGChannels':(3)}
    },
    {
      'name':'PG_JBA',
      'class':'pulse_generator',
      'kwargs':{'name':'Pulse Generator JBA', 'MWSource':'MWSource_JBA', 'mixer':'mixerJBASimple', 'modulationMode':'SimpleMixer', 'formGenerator':'awgMW', 'AWGChannels':(3,4)}
    },
    {
      'name' : 'PA_JBA',
      'class' : 'pulse_analyser',
      'kwargs' : {'name' : 'Pulse analyser JBA', 'MWSource':'MWSource_JBA', 'acqiris':'acqiris', 'acqirisChannels':(2,3), 'pulse_generator':'PG_JBA_sb'}
    },
    {
      'name' : 'JBA_Att',
      'class' : 'yokogawa',
      'serverAddress' : "rip://192.168.0.1:8000",
      'kwargs' : {'name' : 'Attenuator JBA','visaAddress' : 'GPIB0::11'}
    },
    {
      'name':'jba_QB1',
      'class':'jba_sb',
      'kwargs':{'name':'JBA 1','generator':'PG_JBA_sb','analyser':'PA_JBA','magnitudeButton':'formAmplitude'}
    },
    {
      'name':'jba_QB2',
      'class':'jba_sb',
      'kwargs':{'name':'JBA 2','generator':'PG_JBA_sb','analyser':'PA_JBA','magnitudeButton':'formAmplitude'}
    },
    {
      'name':'jba_QB3',
      'class':'jba_sb',
      'kwargs':{'name':'JBA 3','generator':'PG_JBA_sb','analyser':'PA_JBA','magnitudeButton':'formAmplitude'}
    },
    {
      'name':'jba_QB4',
      'class':'jba_sb',
      'kwargs':{'name':'JBA 4','generator':'PG_JBA_sb','analyser':'PA_JBA','magnitudeButton':'formAmplitude'}
    },
    {
      'name' : 'mixerJBASimple',
      'class' : 'iqmixer',
      'kwargs' : {'name' : 'MixerJBA', 'MWSource':'MWSource_JBA', 'AWG':'awgMW', 'AWGChannels':(1,2), 'fsp':'fsp'}
    }
]
instrumentManager.initInstruments(instruments,globalParameters = {'forceReload' : True} )

for name in instrumentManager.instrumentNames():
  globals()[name] = instrumentManager.getInstrument(name)
  
