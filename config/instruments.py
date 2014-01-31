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

localServerAdress = "rip://127.0.0.1:8000"
serverAddress = "rip://192.168.0.1:8000"

instrumentManager = Manager()

instruments = [
    {
      'name' : 'register',
    },
    {
      'name' : 'Coil',
      'class' : 'yokogawa',
      'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'Coil','visaAddress' : 'GPIB0::3'}
    },
    {
      'name' : 'vna',
      'serverAddress' : serverAddress,
      'kwargs' : {'visaAddress': "GPIB0::6"}
    },
    {
      'name' : 'temperature',
      'serverAddress' : serverAddress,
    },
    {
      'name' : 'helium_level',
      'serverAddress' : localServerAdress,
    },
    {
      'name' : 'acqiris',
      'serverAddress' : 'rip://192.168.0.22:8000',
      'kwargs' : {'name': 'Acqiris Card'}
    },
    {
      'name' : 'awgMW',
      'class' : 'awg',
      'serverAddress' : localServerAdress,
      'kwargs' : {'visaAddress' : "TCPIP0::192.168.0.3::inst0"}
    },
    {
      'name' : 'awgFlux',
      'class' : 'awg',
      'serverAddress' : localServerAdress,
      'kwargs' : {'visaAddress' : "TCPIP0::192.168.0.14::inst0"}
    },    
    {
      'name' : 'MWSource_JBA',
      'class' : 'agilent_mwg',
      'serverAddress' : localServerAdress,
      'kwargs' : {'name' : 'MWsource JBA','visaAddress' : "TCPIP0::192.168.0.25::inst0"}
    },    
    {
      'name' : 'MWSource_QB',
      'class' : 'agilent_mwg',
      'serverAddress' : localServerAdress,
      'kwargs' : {'name' : 'MWsource QB','visaAddress' : "TCPIP0::192.168.0.13::inst0"}
    },
    {
      'name' : 'fsp',
      'serverAddress' : localServerAdress,
    },
    {
      'name' : 'IQMixer_JBA',
      'class' : 'iqmixer',
      'kwargs' : {'name' : 'MixerJBA', 'MWSource':'MWSource_JBA', 'AWG':'awgMW', 'AWGChannels':(1,2), 'fsp':'fsp'}
    },
    {
      'name' : 'mixerQB',
      'class' : 'simpleMixer',
      'kwargs' : {'name' : 'MixerJBA', 'MWSource':'MWSource_QB', 'AWG':'awgMW', 'AWGChannel':3, 'fsp':'fsp'}
    },
    {
      'name':'PG_JBA_sb',
      'class':'pulse_generator',
      'kwargs':{'name':'Pulse Generator JBA sb', 'MWSource':'MWSource_JBA', 'mixer':'IQMixer_JBA', 'modulationMode':'IQMixer', 'formGenerator':'awgMW', 'AWGChannels':(1,2)}
    },
    {
      'name':'PG_QB',
      'class':'pulse_generator',
      'kwargs':{'name':'Pulse Generator QB', 'MWSource':'MWSource_QB', 'mixer':'mixerQB', 'modulationMode':'SimpleMixer', 'formGenerator':'awgMW', 'AWGChannels':(3)}
    },
   # {
   #   'name':'PG_JBA',
   #   'serverAddress' : serverAddress,
   #   'class':'pulse_generator',
   #   'kwargs':{'name':'Pulse Generator JBA', 'MWSource':'MWSource_JBA_perturb', 'mixer':'mixerJBASimple', 'modulationMode':'SimpleMixer', 'formGenerator':'awgMW', 'AWGChannels':(3)}
    #},
    {
      'name' : 'PA_JBA',
      'class' : 'pulse_analyser',
      'kwargs' : {'name' : 'Pulse analyser JBA', 'MWSource':'MWSource_JBA', 'acqiris':'acqiris', 'acqirisChannels':(0,1), 'pulse_generator':'PG_JBA_sb'}
    },
    {
      'name' : 'JBA_Att',
      'class' : 'yokogawa',
      'serverAddress' : serverAddress,
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
    },
    {
      'name' : 'qubit1',
      'class':'qubit',
      'kwargs':{'name':'qubit1','jba':'jba_QB1','pulseGenerator':'pg_qb'}
    }
]
instrumentManager.initInstruments(instruments,globalParameters = {'forceReload' : True} )

for name in instrumentManager.instrumentNames():
  globals()[name] = instrumentManager.getInstrument(name)
  