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

#Load the IQ mixer calibration data for the first qubit.
qubit1IQOffset = Datacube()
qubit1IQPower = Datacube()
qubit1IQSideband = Datacube()
#Load the IQ mixer calibration data for the second qubit.
qubit2IQOffset = Datacube()
qubit2IQPower = Datacube()
qubit2IQSideband = Datacube()

fluxline1Response = Datacube()
fluxline2Response = Datacube()

register = instrumentManager.initInstrument("register")

try:
  qubit2IQOffset.loadtxt(register["calibration.iqmixer.qubit2.offset"],loadChildren = False)
  qubit2IQPower.loadtxt(register["calibration.iqmixer.qubit2.amplitude"],loadChildren = False)
  if register.hasKey("calibration.iqmixer.qubit2.sideband"):
    qubit2IQSideband.loadtxt(register["calibration.iqmixer.qubit2.sideband"])

  qubit1IQOffset.loadtxt(register["calibration.iqmixer.qubit1.offset"],loadChildren = False)
  qubit1IQPower.loadtxt(register["calibration.iqmixer.qubit1.amplitude"],loadChildren = False)
  if register.hasKey("calibration.iqmixer.qubit1.sideband"):
    qubit1IQSideband.loadtxt(register["calibration.iqmixer.qubit1.sideband"])

  fluxline1Response.loadtxt(register["calibration.fluxline.qubit1"])
  fluxline2Response.loadtxt(register["calibration.fluxline.qubit2"])

except:
  print "Cannot load qubit calibration data!"
  print sys.exc_info()

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
      'name' : 'awgMW',
      'class' : 'awg',
      'serverAddress' : serverAddress,
      'kwargs' : {'visaAddress' : "TCPIP0::192.168.0.3::inst0"}
    },
    {
      'name' : 'awgFlux',
      'class' : 'awg',
      'serverAddress' : serverAddress,
      'kwargs' : {'visaAddress' : "TCPIP0::192.168.0.14::inst0"}
    },    
    {
      'name' : 'MWSource_JBA',
      'class' : 'anritsu_mwg',
      'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'MWsource JBA','visaAddress' : "GPIB0::4"}
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
      'name' : 'coil',
      'class' : 'yokogawa',
      'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'Qubit Coil','visaAddress' : 'GPIB0::10'}
    },
    {
      'name' : 'IQMixer_JBA',
      'class' : 'iqmixer',
      'kwargs' : {'name' : 'MixerJBA', 'MWSource':'MWSource_JBA', 'AWG':'awgMW', 'AWGChannels':(3,4), 'fsp':'fsp'}
    },
    {
      'name' : 'mixerJBASimple',
      'class' : 'simplemixer',
      'kwargs' : {'name' : 'mixerJBASimple', 'MWSource':'MWSource_JBA', 'AWG':'awgMW', 'AWGChannel':(3), 'fsp':'fsp'}
    },
    {
      'name' : 'mixerQBSimple',
      'class' : 'simplemixer',
      'kwargs' : {'name' : 'mixerQBSimple', 'MWSource':'MWSource_JBA', 'AWG':'awgMW', 'AWGChannel':(1), 'fsp':'fsp'}
    },
    {
      'name' : 'IQMixer_QB',
      'class' : 'iqmixer',
      'kwargs' : {'name' : 'MixerQB', 'MWSource':'MWSource_QB', 'AWG':'awgMW', 'AWGChannels':(1,2), 'fsp':'fsp'}
    },
    {
      'name':'PG_JBA',
      'class':'pulse_generator',
      'kwargs':{'name':'Pulse Generator JBA', 'MWSource':'MWSource_JBA', 'mixer':'mixerJBASimple', 'modulationMode':'SimpleMixer', 'formGenerator':'awgMW', 'AWGChannels':(3)}
    },
    {
      'name':'PG_JBA_sb',
      'class':'pulse_generator',
      'kwargs':{'name':'Pulse Generator JBA sb', 'MWSource':'MWSource_JBA', 'mixer':'IQMixer_JBA', 'modulationMode':'IQMixer', 'formGenerator':'awgMW', 'AWGChannels':(3,4)}
    },
    {
      'name' : 'PA_JBA',
      'class' : 'pulse_analyser',
      'kwargs' : {'name' : 'Pulse analyser JBA', 'MWSource':'MWSource_JBA', 'acqiris':'acqiris', 'pulse_generator':'PG_JBA'}
    },
    {
      'name':'PG_QB',
      'class':'pulse_generator',
      'kwargs':{'name':'Pulse Generator JBA', 'MWSource':'MWSource_QB', 'mixer':'mixerQBSimple', 'modulationMode':'SimpleMixer', 'formGenerator':'awgMW', 'AWGChannels':(1)}
    },
    {
      'name':'PG_QB_sb',
      'class':'pulse_generator',
      'kwargs':{'name':'Pulse Generator QB', 'MWSource':'MWSource_QB', 'mixer':'IQMixer_QB', 'modulationMode':'IQMixer','formGenerator':'awgMW', 'AWGChannels':(1,2)}
    },
    {
      'name' : 'JBA_Att',
      'class' : 'yokogawa',
      'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'Attenuator JBA','visaAddress' : 'GPIB0::9'}
    },
    {
      'name':'jba_QB1',
      'class':'jba_sb',
      'kwargs':{'name':'JBA 1','generator':'PG_JBA','analyser':'PA_JBA','magnitudeButton':'variableAttenuator'}
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
      'kwargs':{'name':'JBA 4','generator':'PG_JBA','analyser':'PA_JBA','magnitudeButton':'formAmplitude'}
    },
    {
      'name':'Qubit1',
      'class':'new_qubit',
      'kwargs':{'name':'Qubit 1','jba':'jba_QB1','pulseGenerator':'PG_QB'}
    },
    {
      'name':'Qubit2',
      'class':'new_qubit',
      'kwargs':{'name':'Qubit 2','jba':'jba_QB2','pulseGenerator':'PG_QB'}
    },
    {
      'name':'Qubit3',
      'class':'new_qubit',
      'kwargs':{'name':'Qubit 3','jba':'jba_QB3','pulseGenerator':'PG_QB'}
    },
    {
      'name':'Qubit4',
      'class':'new_qubit',
      'kwargs':{'name':'Qubit 4','jba':'jba_QB4','pulseGenerator':'PG_QB'}
    }
]

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
