#############
### in instrument file
#############

instruments = [
    {
      'name' : 'awg',
      'class' : 'awg',
      'kwargs' : {'visaAddress' : "TCPIP0::192.168.0.xx::inst0"}
    },   
        {
      'name' : 'MWSource',
      'class' : 'agilent_mwg',
      'serverAddress' : localServerAdress,
      'kwargs' : {'name' : 'MWsource','visaAddress' : "TCPIP0::192.168.0.xx::inst0"}
    },
    {
      'name' : 'simpleMixer',
      'class' : 'simplemixer',
      'kwargs' : {'name' : 'simplemixer', 'MWSource':'MWSource', 'AWG':'awg', 'AWGChannels':(1), 'fsp':'fsp'}
    },
    {
      'name':'PG',
      'class':'pulse_generator',
      'kwargs':{'name':'Pulse Generator', 'MWSource':'MWSource', 'mixer':'simpleMixer', 'modulationMode':'simpleMixer', 'formGenerator':'awg', 'AWGChannels':(1)}
    }
]





###############
### in script file 
###############




pulseGenerator=Manager().getInstrument('pulseGenerator')

pulseGenerator.addPulse(generatorFunction="square",frequency=5.,amplitude=1.,start=8000, stop=10000, applyCorrections=False,phase=0.)
pulseGenerator.preparePulseSequence()
pulseGenerator.sendPulseSequence()









