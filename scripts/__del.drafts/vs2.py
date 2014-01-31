from config.instruments import *
from matplotlib.pyplot import *
from pyview.gui.mpl.backend import figure
import numpy
import scipy
from pyview.helpers.datamanager import DataManager
dataManager = DataManager()
instrumentManager=Manager()
pg=instrumentManager.getInstrument('pg_jba_single frequency')
##
jba=instrumentManager.getInstrument('jba_qb1')
##
pg._mixer.calibrate()
##
dataManager.addDatacube(pg._mixer._calibration._offsetCalibrationData)
##
pg._mixer._calibration.setupWaveforms()
##
shape=zeros((20000),dtype = numpy.complex128)
shape[10000:10200]=1
shape[10200:11000]=0.8
shape=shape
pg.clearPulse()
pg.generatePulse(frequency=9.55, shape=shape)
pg.sendPulse()

##
cla()
plot(range(0,len(pg.totalPulse)),pg.totalPulse)
draw()
show()
##
pg._AWG.loadRealWaveform(pg.totalPulse, channel=4,waveformName='toto')
##
print instrumentManager.getInstrument('AWG').waveform(3)
##
print pg._mixer.calibrationParameters()
## 
a=2
b=a
b=3
print a[
a=range(0,2)
b=a
b=range(3,4)
print a
##
shape=zeros((20000),dtype = numpy.complex128)
shape[10000:10200]=1
shape[10200:11000]=0.8
shape=shape
jba.shape=shape

frequency=9.268
jba.init()
jba.addFrequency(frequency=9.268,shape=shape)
jba.sendWaveforms()
##

co= jba.getMeasurement()
print scipy.cov(co[:,0])+scipy.cov(co[:,1])
	
cla()
plot(co[:,0],co[:,1],'o')
draw()
show()
	
(Io,Qo,angle)=jba._adjustRotationAndOffset(frequency=frequency)

plot([Io],[Qo],'o')
plot([Io,Io+cos(angle)],[Qo,Qo-sin(angle)])
draw()
show()

##
dataManager.addDatacube(jba.data)
center= jba._findAmplitude(frequency=9.268,shape=shape,magnitudeButton='variableAttenuator')
print jba._findAmplitude(frequency=9.268,shape=shape,magnitudeButton='variableAttenuator',center=center)
##
jba.sendWaveforms()
##
jba._adjustRotationAndOffset(frequency=frequency)
co=jba.getMeasurement()
c = jba.acquire(co=co,f=0)
cla()
plot(co[:,0],co[:,1],'o')
draw()
show()
##
print c
##
c = jba._pulseAnalyser._acqiris.multiplexedBifurcationMapAdd(co,0)
print c
##
r = jba._pulseAnalyser._acqiris.convertToProbabilities(c)
print r  
##
print jba.acquire(co=co,f=0)
##

import lib.swig.acqiris_QuantroDLL2.acqiris_QuantroDLL2.acqiris_QuantroDLL2 as acqirislib
m=acqirislib.MultiplexedBifurcationMap()
print m
##
m.setRotation(2,0,0,0)
##

jba.init()
jba.addFrequency(frequency=9.268, shape=shape)
jba.sendWaveforms()
print jba.takePoint()


#### MESURE DE LA NUIT DU 12/01/2012
flux=instrumentManager.getInstrument('coil')
jba=instrumentManager.getInstrument('jba_qb1')
mw_qb=instrumentManager.getInstrument('cavity_2_mwg')
print flux
print jba
print mw_qb
#
mw_qb.setFrequency(5)
#
jba.init()
jba.addFrequency(frequency=9.268, shape=shape)
jba.sendWaveforms()
##
data=Datacube('Spectro 2D - vFlux1')
dataManager.addDatacube(data)
i=0
jba._adjustRotationAndOffset(frequency=0)
try:
	for v in arange(-3,3.01,0.02):
		flux.setVoltage(v,slewRate=1.)
		data.set(i=i,v=v)
		child=Datacube('v=%f'%v)
		data.addChild(child) 
		for f in arange(5,9,0.02):
			mw_qb.setFrequency(f)
#			jba._pulseAnalyser._acqiris.all(frequency=9.268)
			child.set(p=jba.takePoint())
			child.set(f=f)
			child.commit()
		child.savetxt()
		data.commit()
		data.savetxt()
finally:
	flux.setVoltage(0,slewRate=1.)		
##

jba._adjustRotationAndOffset(frequency=0)
##
co= jba.getMeasurement()
print co
print jba.acquire(co=co,f=0)
##
print jba.takePoint()	
##

jba._adjustRotationAndOffset(frequency=0)
##
print jba.takePoint()
##
co=jba.getMeasurement()

print jba.acquire(co=co,f=0)
