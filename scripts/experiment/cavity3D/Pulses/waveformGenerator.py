#############################################################################
#### waveform generator->generates Waveforms and can send them to the AWG ###
#############################################################################
import sys
import time
import math
import experiment.cavity3D.Pulses.pulseLibrary as pl
from numpy import *
import scipy
import scipy.optimize
print "Scipy version %s" %scipy.version.version
from matplotlib.pyplot import *
from pyview.helpers.instrumentsmanager import Manager
##
reload(pl)
##
AWG=Manager().getInstrument('awgMW2')
pg_cav=Manager().getInstrument('pg_cav')
##
####################################
### Helping functions here below ###
####################################

def pulsePlot(wave,marker1,marker2):
	x=range(20000)
	#wave=waveform[0]
	#marker1=waveform[1]
	#marker2=waveform[2]
	figure()
	subplot(311)
	plot(x,wave)
	subplot(312)
	plot(x,marker1)
	subplot(313)
	plot(x,marker2)
	show()
def send2AWG(waveform):
	wave=waveform[0]
	marker=waveform[1]
	name=waveform[2]
	AWG.listRealWaveform(wave,marker,name)
def marker2AWGform(marker1,marker2):
	markerAWG=[sum(i)for i in zip(marker1,marker2)]
	return markerAWG
def loadWF2Channel(channel,wfName):
	# wfName must be a string
	AWG.setWaveform(channel,wfName)
def clearWFList():
	AWG.deleteWaveform('ALL')
#########################################
### Waveforms here below              ###
### Everything in units of AWG points ###
### Use int                           ###
#########################################

### List of functions in pulsLibrary.py
#
# singleSquarePulse(start,stop, height=1)
# singleGaussianPulse(center,sigma,cutOff,height=1)
#
# outputs an array of 20000 values.
#
def openMixer(name='open',modulation=None,plot=False):
	wave=pl.singleSquarePulse(0,20000)
	marker1=pl.singleSquarePulse(0,10000)
	marker2=pl.singleSquarePulse(0,10000,height=2) #Marker2 must have height=2 
	if plot:
		pulsePlot(wave,marker1,marker2)
	markerAWG=marker2AWGform(marker1,marker2)
	if modulation==None:
		return wave,markerAWG,name
def markerOnly(name='readout',modulation=None,plot=False):
	wave=pl.singleSquarePulse(20000-0,20000)
	marker1=pl.singleSquarePulse(0,10000)
	marker2=pl.singleSquarePulse(0,10000,height=2) #Marker2 must have height=2 
	if plot:
		pulsePlot(wave,marker1,marker2)
	markerAWG=marker2AWGform(marker1,marker2)
	if modulation==None:
		return wave,markerAWG,name
# Sets a wavefrom for mixers and a marker on channel 2 for gating	
def readoutWaveform(length,name='readout',height=1,modulation=None,plot=False):
	wave=pl.singleSquarePulse(20000-length,20000,height=height)
	marker1=pl.singleSquarePulse(0,20000-length)
	marker2=pl.singleSquarePulse(0,20000-length,height=2) #Marker2 must have height=2 
	if plot:
		pulsePlot(wave,marker1,marker2)
	markerAWG=marker2AWGform(marker1,marker2)
	if modulation==None:
		return wave,markerAWG,name
# Sets a wavefrom for mixers and a marker on channel 2 for gating		
def readoutSwitchWaveform(length,name='readout_switch',height=1,switchRiseBuffer=0,modulation=None,plot=False):
	wave=pl.singleSquarePulse(20000-length,20000,height=height)
	marker1=pl.singleSquarePulse(0,20000-length)
	marker2=pl.singleSquarePulse(20000-(length+switchRiseBuffer),20000,height=2) #Marker2 must have height=2 
	if plot:
		pulsePlot(wave,marker1,marker2)
	markerAWG=marker2AWGform(marker1,marker2)
	if modulation==None:
		return wave,markerAWG,name
		
def squarePulseWaveform(start,stop,name='square',modulation=None,plot=False):
	wave=pl.singleSquarePulse(start,stop)
	marker1=pl.singleSquarePulse(0,10000)
	marker2=pl.singleSquarePulse(0,10000,height=2) #Marker2 must have height=2
	if plot:
		pulsePlot(wave,marker1,marker2)
	markerAWG=marker2AWGform(marker1,marker2)
	if modulation==None:
		return wave,markerAWG,name

def gaussianPulseWaveform(center,sigma,cutOff='',name='gaussian',markerOffset1=0,markerOffset2=0,marker1Start='',marker1Stop='',marker2Start='',marker2Stop='',modulation=None,plot=False):
	if cutOff=='':
		cutOff=6*sigma
	if marker1Start==''or marker1Stop=='':
		marker1Start=center-round(cutOff/2)+markerOffset1
		marker1Stop=center+round(cutOff/2)+markerOffset1
	if marker2Start==''or marker2Stop=='':
		marker2Start=center-round(cutOff/2)+markerOffset2
		marker2Stop=center+round(cutOff/2)+markerOffset2
	wave=pl.singleGaussianPulse(center,sigma,cutOff,height=1)
	marker1=pl.singleSquarePulse(marker1Start,marker1Stop)
	marker2=pl.singleSquarePulse(marker2Start,marker2Stop,height=2) #Marker2 must have height=2
	if plot:
		pulsePlot(wave,marker1,marker2)
	markerAWG=marker2AWGform(marker1,marker2)
	if modulation==None:
		return wave,markerAWG,name
def ramseyGaussianWaveform(center1,center2,sigma,name='ramseyGaussian'):
	#to be finished
	if cutOff=='':
		cutOff=6*sigma
	if marker1Start==''or marker1Stop=='':
		marker1Start=center-round(cutOff/2)
		marker1Stop=center+round(cutOff/2)
	if marker2Start==''or marker2Stop=='':
		marker2Start=center-round(cutOff/2)
		marker2Stop=center+round(cutOff/2)
	wave=pl.singleGaussianPulse(center,sigma,cutOff,height=1)
	marker1=pl.singleSquarePulse(marker1Start,marker1Stop)
	marker2=pl.singleSquarePulse(marker2Start,marker2Stop,height=2) #Marker2 must have height=2
	if plot:
		pulsePlot(wave,marker1,marker2)
	markerAWG=marker2AWGform(marker1,marker2)
	if modulation==None:
		return wave,markerAWG,name
#
def sinWaveform(frequency,phase=0,height=1,name='sin',markerOffset1=0,markerOffset2=0,marker1Start='',marker1Stop='',marker2Start='',marker2Stop='',modulation=None,plot=False):
	if marker1Start==''or marker1Stop=='':
		marker1Start=10000
		marker1Stop=20000
	if marker2Start==''or marker2Stop=='':
		marker2Start=10000
		marker2Stop=20000
	wave=pl.sinPulse(frequency,phase=phase,height=height)
	marker1=pl.singleSquarePulse(marker1Start,marker1Stop)
	marker2=pl.singleSquarePulse(marker2Start,marker2Stop,height=2) #Marker2 must have height=2
	if plot:
		pulsePlot(wave,marker1,marker2)
	markerAWG=marker2AWGform(marker1,marker2)
	if modulation==None:
		return wave,markerAWG,name


#############################
### Executions here below ###
#############################
"""
#wf1=gaussianPulseWaveform(18000,5,marker1Start=17900,marker1Stop=18100,marker2Start=17900,marker2Stop=18100,plot=False)
#wf1=gaussianPulseWaveform(18000,3000,markerOffset2=-50,plot=False)
#send2AWG(wf1)
#loadWF2Channel(3,wf1[2])
##
wf1=readoutWaveform(10000)
send2AWG(wf1)
loadWF2Channel(1,wf1[2])
##
wf2=readoutWaveform(10000)
send2AWG(wf2)
loadWF2Channel(2 ,wf2[2])
##
wf3=openMixer()
send2AWG(wf3)
loadWF2Channel(4 ,wf3[2])
#wf2=sinWaveform(0.02,phase=-90,name='cos')
#send2AWG(wf2)
#loadWF2Channel(2 ,wf2[2])
##
pg_cav.clearPulse()
pg_cav.addPulse(generatorFunction="square",frequency=7.353,start=0,stop=20000,applyCorrections=True)
pg_cav.preparePulseSequence()
pg_cav.sendPulseSequence()

##
wf1=squarePulseWaveform(10000,12000)
send2AWG(wf1)
loadWF2Channel(1 ,wf1[2])
wf2=squarePulseWaveform(10000,12000)
send2AWG(wf2)
loadWF2Channel(2 ,wf2[2])

##
help(fmin_powell)
##
print AWG.offset(1)
"""