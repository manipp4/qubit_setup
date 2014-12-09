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
serverAddress = "rip://192.168.0.1:8000"

instrumentManager = Manager()

instruments = [
    {
      'name' : 'register',
      'kwargs':{'filename' : 'registerScal5'}
    },
    {
      'name' : 'Coil',
      'class' : 'yokogawa',
      'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'Coil','visaAddress' : 'GPIB0::10'}
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
      'serverAddress' : serverAddress,
    },
    {
      'name' : 'acqiris',
      'class': 'acqiris3',
      'serverAddress' : 'rip://192.168.0.22:8000',
      'kwargs' : {'name': 'Acqiris Card','___includeModuleDLL2___':True}
    },
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
      'name' : 'MWSource_JBA',
      'class' : 'agilent_mwg',
      'serverAddress' : localServerAdress,
      'kwargs' : {'name' : 'MWsource JBA','visaAddress' : "TCPIP0::192.168.0.36::inst0"}
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
      'kwargs' : {'visaAddress' : "TCPIP0::192.168.0.38::inst0"}
    },
    {
      'name' : 'IQMixer_JBA',
      'class' : 'iqmixer',
      'kwargs' : {'name' : 'MixerJBA', 'MWSource':'MWSource_JBA', 'AWG':'awgMW', 'AWGChannels':(1,2), 'fsp':'fsp'}
    },
    {
      'name':'PG_JBA',
      'class':'pulse_generator',
      'kwargs':{'name':'Pulse Generator JBA', 'MWSource':'MWSource_JBA', 'mixer':'IQMixer_JBA', 'modulationMode':'IQMixer', 'formGenerator':'awgMW', 'AWGChannels':(1,2)}
    },
    {
      'name' : 'PA_JBA',
      'class' : 'pulse_analyser',
      'kwargs' : {'name' : 'Pulse analyser JBA', 'MWSource':'MWSource_JBA', 'acqiris':'acqiris', 'acqirisChannels':(2,3), 'pulse_generator':'PG_JBA'}
    },
    {
      'name' : 'JBA_Att',
      'class' : 'yokogawa',
      'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'Attenuator JBA','visaAddress' : 'GPIB0::11'}
    },
    {
      'name':'jba1',
      'class':'jba_sb',
      'kwargs':{'name':'JBA 1','generator':'PG_JBA','analyser':'PA_JBA','magnitudeButton':'formAmplitude'}
    },
    {
      'name':'jba2',
      'class':'jba_sb',
      'kwargs':{'name':'JBA 2','generator':'PG_JBA','analyser':'PA_JBA','magnitudeButton':'formAmplitude'}
    },
    {
      'name':'jba3',
      'class':'jba_sb',
      'kwargs':{'name':'JBA 3','generator':'PG_JBA','analyser':'PA_JBA','magnitudeButton':'formAmplitude'}
    },
    {
      'name':'jba4',
      'class':'jba_sb',
      'kwargs':{'name':'JBA 4','generator':'PG_JBA','analyser':'PA_JBA','magnitudeButton':'formAmplitude'}
    },
    {
      'name' : 'IQMixer_QB',
      'class' : 'iqmixer',
      'kwargs' : {'name' : 'IQMixerQB1', 'MWSource':'MWSource_QB', 'AWG':'awgMW', 'AWGChannels':(3,4), 'fsp':'fsp'}
    },
    {
      'name':'PG_QB',
      'class':'pulse_generator',
      'kwargs':{'name':'Pulse Generator QB', 'MWSource':'MWSource_QB', 'mixer':'IQMixer_QB', 'modulationMode':'IQMixer', 'formGenerator':'awgMW', 'AWGChannels':(3,4)}
    },
    {
      'name' : 'qubit1',
      'class':'qubit',
      'kwargs':{'name':'qubit1','jba':'jba1','pulseGenerator':'PG_QB'}
    },
    {
      'name' : 'qubit2',
      'class':'qubit',
      'kwargs':{'name':'qubit2','jba':'jba2','pulseGenerator':'PG_QB'}
    },
    {
      'name' : 'qubit3',
      'class':'qubit',
      'kwargs':{'name':'qubit3','jba':'jba3','pulseGenerator':'PG_QB'}
    },
    {
      'name' : 'qubit4',
      'class':'qubit',
      'kwargs':{'name':'qubit4','jba':'jba4','pulseGenerator':'PG_QB'}
    },
    {
    'name':'pulsersManager',
    'class':'pulsers_manager',
    'kwargs':{'generators':[['PG_F1',True],['PG_F2',True],['PG_F3',True],['PG_F4',True],['PG_QB',True],['PG_JBA',True]]}
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
  