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
      'name' : 'vmw',
      'class' : 'anritsu_mwg',
      'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'vmw','visaAddress' : "GPIB0::14"}
    },
    {
      'name' : 'MWSource_Signal',
      'class' : 'agilent_mwg',
      'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'MWSource_Signal','visaAddress' : "TCPIP::192.168.0.12"}
    },
     {
      'name' : 'MWSource_pump',
      'class' : 'agilent_mwg',
      'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'MWSource_pump','visaAddress' : "TCPIP::192.168.0.13"}
    },
    {
      'name' : 'MWSource_lo',
      'class' : 'agilent_mwg',
      'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'MWSource_lo','visaAddress' : "TCPIP::192.168.0.117"}
    },
    {
      'name' : 'Lecroy_104xi',
      'class' : 'LeCroy_waveRunner_scope',
      'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'LeCroy_waveRunner_scope','visaAddress' : "TCPIP::192.168.0.30"}
    },
    {
      'name' : 'fsp',
      'serverAddress' : serverAddress
    },
    {
      'name' : 'coil',
      'class' : 'yokogawa',
      'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'Coil','visaAddress' : 'GPIB0::10'}
    },
        {
      'name' : 'dcpump',
      'class' : 'yokogawa',
      'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'Dcpump','visaAddress' : 'GPIB0::11'}
    },
     {
      'name' : 'vca_attenuator',
      'class' : 'yokogawa',
      'serverAddress' : serverAddress,
      'kwargs' : {'name' : 'Vca_attenuator','visaAddress' : 'GPIB0::3'}
    }
]
instrumentManager.initInstruments(instruments,globalParameters = {'forceReload' : True} )

for name in instrumentManager.instrumentNames():
  globals()[name] = instrumentManager.getInstrument(name)
  
