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

register = instrumentManager.initInstrument("register")


instruments = [
    {
      'name' : 'register',
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
      'serverAddress': serverAddress,
    },
    {
      'name' : 'acqiris',
      'serverAddress' : 'rip://192.168.0.22:8000',
      'kwargs' : {'name': 'Acqiris Card'}
    },
    {
      'name' : 'awg',
      'class' : 'awg',
      'serverAddress' : serverAddress,
      'kwargs' : {'visaAddress' : "TCPIP0::192.168.0.14::inst0"}
    },
    {
      'name' : 'MWSource_Cavite',
      'class' : 'anritsu_mwg',
      'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'MWSource_Cavite JBA','visaAddress' : "GPIB0::4"}
    },
    {
      'name' : 'MWSource_QB',
      'class' : 'agilent_mwg',
      'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'MWSource_QB','visaAddress' : "TCPIP::192.168.0.12"}
    },
    {
      'name' : 'fsp',
      'serverAddress' : serverAddress
    },
    {
      'name' : 'mixerCaviteSimple',
      'class' : 'simplemixer',
      'kwargs' : {'name' : 'mixerCaviteSimple', 'MWSource':'MWSource_Cavite', 'AWG':'awg', 'AWGChannel':(1), 'fsp':'fsp'}
    },
    {
      'name' : 'mixerQBSimple',
      'class' : 'simplemixer',
      'kwargs' : {'name' : 'mixerQBSimple', 'MWSource':'MWSource_QB', 'AWG':'awg', 'AWGChannel':(2), 'fsp':'fsp'}
    },
    {
      'name':'PG_Cavite',
      'class':'pulse_generator',
      'kwargs':{'name':'Pulse Generator Cavite', 'MWSource':'MWSource_Cavite', 'mixer':'mixerCaviteSimple', 'modulationMode':'SimpleMixer', 'formGenerator':'awg', 'AWGChannels':(1)}
    },
    {
      'name':'PG_QB',
      'class':'pulse_generator',
      'kwargs':{'name':'Pulse Generator QB', 'MWSource':'MWSource_QB', 'mixer':'mixerQBSimple', 'modulationMode':'SimpleMixer', 'formGenerator':'awg', 'AWGChannels':(2)}
    },
    {
      'name' : 'PA',
      'class' : 'pulse_analyser',
      'kwargs' : {'name' : 'Pulse analyser', 'MWSource':'MWSource_Cavite', 'acqiris':'acqiris', 'pulse_generator':'PG_Cavite'}
    },
    {
      'name' : 'Att',
      'class' : 'yokogawa',
      'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'Attenuator','visaAddress' : 'GPIB0::9'}
    }
]


instrumentManager.initInstruments(instruments,globalParameters = {'forceReload' : True} )

for name in instrumentManager.instrumentNames():
  globals()[name] = instrumentManager.getInstrument(name)

##
print dir(instrumentManager)

##
instruments_subset = [
    {
      'name' : 'register',
      'serverAddress': serverAddress
    },
    {
      'name' : 'vna',
      'gpibAddress': "GPIB0::6"
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
      'name' : 'coil',
      'class' : 'yokogawa',
      'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'Qubit Coil','visaAddress' : 'GPIB0::10'}
    },
    {
      'name' : 'jba_att',
      'class' : 'yokogawa',
      'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'Attenuator Qubit 2','visaAddress' : 'GPIB0::2'}
    }
]

unused = [
    {
      'name' : 'MWpulse_gene_JBA1',
      'class' : 'pulse_generator',
      'kwargs' : {'name' : 'Pulse generator JBA 1', 'MWSource':'cavity_1_mwg', 'IQMixer':'MixerJBA', 'AWG':'awg', 'AWGChannels':(1,2)}
    }, 
    {
      'name' : 'simpleMixerJBA',
      'class' : 'simplemixer',
      'kwargs' : {'name' : 'simpleMixerJBA', 'MWSource':'MWSource_JBA', 'AWG':'awg', 'AWGChannel':(4), 'fsp':'fsp'}
    },
    {
      'name':'PG_QB_simple',
      'class':'pulse_generator',
      'kwargs':{'name':'Pulse Generator QB', 'MWSource':'MWSource_QB', 'mixer':'mixerQBSimple', 'modulationMode':'SimpleMixer','formGenerator':'awg', 'AWGChannels':(1)}
    }, 
    {
      'name':'PG_JBA_single frequency',
      'class':'pulse_generator',
      'kwargs':{'name':'PG_JBA_single_frequency', 'MWSource':'MWSource_JBA', 'mixer':'simpleMixerJBA', 'formGenerator':'awg', 'AWGChannels':(4),'modulationMode':'SimpleMixer'}
    },
    {
      'name' : 'mixerQBSimple',
      'class' : 'simplemixer',
      'kwargs' : {'name' : 'mixerQBSimple', 'MWSource':'MWSource_QB', 'AWG':'awg', 'AWGChannel':(1), 'fsp':'fsp'}
    },
    {
      'name' : 'JBA1',
      'class' : 'jba_sb',
      'kwargs' : {'name' : 'JBA 1', 'generator':'MWpulse_gene_JBA1' , 'analyser':'Pulse_Analyser_JBA1'}
    },
    {
      'name' : 'afg3',
      'class' : 'afg',
      'serverAddress' : serverAddress,
      'kwargs' : {"visaAddress": "TCPIP0::192.168.0.5::inst0","name": "AFG 2, Channel 1"}
    },
    {
      'name' : 'qubit1',
      'class' : 'qubit',
      'kwargs' : {'fluxlineTriggerDelay':459,'fluxlineResponse':fluxline1Response,'fluxline':'awg2','fluxlineWaveform':'fluxlineQubit1','fluxlineChannel':1,'iqOffsetCalibration':qubit1IQOffset,'iqSidebandCalibration':qubit1IQSideband,'iqPowerCalibration':qubit1IQPower,'jba':'jba1',"awgChannels":[3,4],"variable":1,"waveforms":["qubit1iInt","qubit1qInt"],"awg":"awg","mwg":"qubit_1_mwg"}
    },
    {
      'name' : 'afg4',
      'class' : 'afg',
      'serverAddress' : serverAddress,
      'kwargs' : {"visaAddress": "TCPIP0::192.168.0.5::inst0","name": "AFG 2, Channel 2","source":2}
    },
    {
      'name' : 'qubit2',
      'class' : 'qubit',
      'kwargs' : {'fluxlineTriggerDelay':459,'fluxlineResponse':fluxline2Response,'fluxline':'awg2','fluxlineWaveform':'fluxlineQubit2','fluxlineChannel':2,'iqOffsetCalibration':qubit2IQOffset,'iqSidebandCalibration':qubit2IQSideband,'iqPowerCalibration':qubit2IQPower,'jba':'jba2',"awgChannels":[3,4],"variable":2,"waveforms":["qubit2iInt","qubit2qInt"],"awg":"awg","mwg":"qubit_2_mwg","acqirisVariable":"px1","additionalFluxlineDelay":-5}
    },
    {
      'name' : 'awg2',
      'class' : 'awg',
      'serverAddress' : serverAddress,
      'kwargs' : {'visaAddress' : "TCPIP0::192.168.0.14::inst0"}
    },
    {
      'name' : 'qubit_2_att',
      'class' : 'yokogawa',
      'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'Attenuator Qubit 2','visaAddress' : 'GPIB0::19'}
    },
    {
      'name' : 'qubit_2_mwg',
      'class' : 'agilent_mwg',
      'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'Qubit 2','visaAddress' : "TCPIP::192.168.0.13"}
    },
    {
      'name' : 'cavity_2_mwg',
      'class' : 'anritsu_mwg',
      'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'Cavity 2','visaAddress' : "GPIB0::6"}
    },
    {
      'name' : 'jba1',
      'class' : 'jba',
      'kwargs': {"attenuator":'qubit_1_att',"acqirisChannel":0,"muwave":'cavity_1_mwg','waveform':'USER1','awg':'awg',"awgChannels":[1,2],'variable':'p1x',"qubitmwg":"qubit_1_mwg"}    
    }
]

instrumentManager.initInstruments(instruments,globalParameters = {'forceReload' : True} )

for name in instrumentManager.instrumentNames():
  globals()[name] = instrumentManager.getInstrument(name)
