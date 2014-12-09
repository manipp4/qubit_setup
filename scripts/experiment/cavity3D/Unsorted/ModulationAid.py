import sys
import time
import numpy
import scipy
import scipy.optimize
import scipy.interpolate
import experiment.cavity3D.Pulses.waveformGenerator as waveGen
from pyview.lib.datacube import *
from pyview.helpers.datamanager import DataManager
from pyview.helpers.instrumentsmanager import Manager
from pyview.lib.smartloop import *

##
reload(waveGen)
#instruments
##################
## for IQ mixer ##
##################
acqiris=Manager().getInstrument('acqiris34') 
AWG=Manager().getInstrument('awgMW2')
pgCav=Manager().getInstrument('pg_cav')
iqMixer=Manager().getInstrument('iqmixer_cav')
##
print AWG.runMode()
##
data=Datacube('IQModulation2')
data.toDataManager()
freqs=arange(0.002,0.030,0.0002)
phases=range(0,360,5)
heights=arange(0.1,1.0,0.1)
freq=0.002
height=1
freqs=SmartLoop(0.002,0.0002,0.03,name='freqs')
for  freq in freqs:
	heightI=height
	heightQ=height
	wf1=waveGen.sinWaveform(freq,phase=ph,name='sin',height=heightI)
	waveGen.send2AWG(wf1)
	waveGen.loadWF2Channel(1 ,wf1[2])
	wf2=waveGen.sinWaveform(freq,phase=ph+90,name='cos',height=heightQ)
	waveGen.send2AWG(wf2)
	waveGen.loadWF2Channel(2 ,wf2[2])
	wantedChannels=3
	acqiris.AcquireTransfer(transferAverage=True,nLoops=10,wantedChannels=wantedChannels)
	time.sleep(0.1)
	acqiris("DLLMath1Module.meanOfLastWaveForms("+str(wantedChannels)+")")		# calculate the mean of each trace in the sequence 
	channels= acqiris("DLLMath1Module.mean")	# get the sequence of means for the selected channels
	# get the indexes of selected channels
	indexes= [i for i,x in enumerate([1&wantedChannels!=0,2&wantedChannels!=0,4&wantedChannels!=0,8&wantedChannels!=0]) if x ==True]
	channels=[channels[indexes[0]],channels[indexes[1]]]
	channels=[numpy.mean(channels[0]),numpy.mean(channels[1])]
	I=channels[0]
	Q=channels[1]
	print I
	data.set(phase=ph,I=I,Q=Q)
	data.commit()
data.savetxt()
	
##
height=1
heightI=height
heightQ=height
ph=0
phAdd=2.1
freq=-0.100
wf1=waveGen.sinWaveform(freq,phase=ph,name='sin',height=heightI)
waveGen.send2AWG(wf1)
waveGen.loadWF2Channel(1 ,wf1[2])
wf2=waveGen.sinWaveform(freq,phase=ph+90+phAdd,name='cos',height=heightQ)
waveGen.send2AWG(wf2)
waveGen.loadWF2Channel(2 ,wf2[2])
##

wf1=waveGen.sinWaveform(0.010,phase=ph,name='sin',height=0)
waveGen.send2AWG(wf1)
waveGen.loadWF2Channel(1 ,wf1[2])
wf2=waveGen.sinWaveform(0.010,phase=ph+90+phAdd,name='cos',height=heightQ)
waveGen.send2AWG(wf2)
waveGen.loadWF2Channel(2 ,wf2[2])
##
pgCav.pulseList=()
pgCav.addPulse(generatorFunction="square",frequency=7.433,amplitude=1,start=0, stop=20000, applyCorrections=True,phase=0)
pgCav.preparePulseSequence()
pgCav.sendPulseSequence()
##

######################
## for simple mixer ##
######################
acqiris=Manager().getInstrument('acqiris34') 
AWG=Manager().getInstrument('awgMW2')
pgCav=Manager().getInstrument('pg_Cav')

##

#wf1=waveGen.sinWaveform(0.000000001,phase=0,name='sin',height=1.0)
waveGen.openMixer()
waveGen.send2AWG(wf1)
waveGen.loadWF2Channel(1 ,wf1[2])
##
data=Datacube('IQModulation2')
data.toDataManager()
freqs=arange(0.002,0.030,0.0002)
phases=range(0,360,5)
heights=arange(0.1,1.0,0.1)
freq=0.002
height=1
freqs=SmartLoop(0.002,0.0002,0.03,name='freqs')
for  freq in freqs:
	heightI=height
	heightQ=height
	wf1=waveGen.sinWaveform(freq,phase=ph,name='sin',height=heightI)
	waveGen.send2AWG(wf1)
	waveGen.loadWF2Channel(1 ,wf1[2])
	wf2=waveGen.sinWaveform(freq,phase=ph+90,name='cos',height=heightQ)
	waveGen.send2AWG(wf2)
	waveGen.loadWF2Channel(2 ,wf2[2])
	wantedChannels=3
	acqiris.AcquireTransfer(transferAverage=True,nLoops=10,wantedChannels=wantedChannels)
	time.sleep(0.1)
	acqiris("DLLMath1Module.meanOfLastWaveForms("+str(wantedChannels)+")")		# calculate the mean of each trace in the sequence 
	channels= acqiris("DLLMath1Module.mean")	# get the sequence of means for the selected channels
	# get the indexes of selected channels
	indexes= [i for i,x in enumerate([1&wantedChannels!=0,2&wantedChannels!=0,4&wantedChannels!=0,8&wantedChannels!=0]) if x ==True]
	channels=[channels[indexes[0]],channels[indexes[1]]]
	channels=[numpy.mean(channels[0]),numpy.mean(channels[1])]
	I=channels[0]
	Q=channels[1]
	print I
	data.set(phase=ph,I=I,Q=Q)
	data.commit()
data.savetxt()
	
##
height=1
heightI=height
heightQ=height
ph=0
phAdd=2.1
freq=-0.100
wf1=waveGen.sinWaveform(freq,phase=ph,name='sin',height=heightI)
waveGen.send2AWG(wf1)
waveGen.loadWF2Channel(1 ,wf1[2])
wf2=waveGen.sinWaveform(freq,phase=ph+90+phAdd,name='cos',height=heightQ)
waveGen.send2AWG(wf2)
waveGen.loadWF2Channel(2 ,wf2[2])
##

wf1=waveGen.sinWaveform(0.010,phase=ph,name='sin',height=0)
waveGen.send2AWG(wf1)
waveGen.loadWF2Channel(1 ,wf1[2])

wf2=waveGen.sinWaveform(0.010,phase=ph+90+phAdd,name='cos',height=heightQ)
waveGen.send2AWG(wf2)
waveGen.loadWF2Channel(2 ,wf2[2])
##
pgCav.pulseList=()
pgCav.addPulse(generatorFunction="square",frequency=7.433,amplitude=1,start=0, stop=20000, applyCorrections=True,phase=0)
pgCav.preparePulseSequence()
pgCav.sendPulseSequence()
##
