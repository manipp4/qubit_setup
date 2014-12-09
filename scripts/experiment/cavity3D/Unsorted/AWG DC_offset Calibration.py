#######################################################################
####### AWG DC offset 
#######################################################################

## imports  and handles to instruments
import sys
import time
import numpy
import scipy
import scipy.optimize
import scipy.interpolate
import experiment.cavity3D.Pulses.waveformGenerator as waveGen
print "Scipy version %s" %scipy.version.version
from pyview.lib.datacube import *
from pyview.helpers.datamanager import DataManager
from pyview.helpers.instrumentsmanager import Manager

#instruments
##
reload(waveGen)
##
AWG=Manager().getInstrument('awgMW2')
fsp=Manager().getInstrument('fsp')
##

def power(channel,voltage):
	AWG.setOffset(channel,voltage)
	#time.sleep(1)
	trace=fsp.getSingleTrace()
	return mean(trace[1])

##
wf1=waveGen.readoutWaveform(2500,height=0.8)
#wf1=waveGen.markerOnly()
waveGen.send2AWG(wf1)
waveGen.loadWF2Channel(1 ,wf1[2])	
##
channel=1
data=Datacube('SimpleMixers IFdc-sweepRef')
data.toDataManager()
dcOffsets=arange(-1,1,0.01)
for offset in dcOffsets:
	data.set(pow=power(channel,offset),offset=offset)
	data.commit()
data.savetxt()
data.set(pow=power(channel,offset),offset=0)
##
channel=1
def pow2(voltage):
	power(channel,voltage)
print scipy.optimize.fmin(pow2,.1,xtol=0.001)
#scipy.optimize.fmin(func, x0, args=(), xtol=0.0001, ftol=0.0001, maxiter=None, maxfun=None, full_output=0, disp=1, retall=0, callback=None)[source]


