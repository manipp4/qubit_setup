##curve
from config.instruments import *
from matplotlib.pyplot import *
from pyview.gui.mpl.backend import figure
import numpy
import scipy
from pyview.helpers.datamanager import DataManager
dataManager = DataManager()
instrumentManager=Manager()

jba_att=instrumentManager.getInstrument('jba_att')
jba=instrumentManager.getInstrument('jba_qb1')
awg=instrumentManager.getInstrument('awg')
print jba_att
print jba
##
shape=zeros((20000),dtype = numpy.complex128)
shape[10000:10200]=1
shape[10200:11000]=0.8
shape=shape
jba.shape=shape
jba.init()
frequency=9.28
jba.addFrequency(frequency=frequency, shape=shape)
jba.sendWaveforms()
##
jba._findAmplitude(frequency=frequency,shape=shape,magnitudeButton='variableAttenuator',center=jba._findAmplitude(frequency=frequency,shape=shape,magnitudeButton='variableAttenuator'))
jba._adjustRotationAndOffset(frequency=0)
##
data=Datacube('sCurve')
dataManager.addDatacube(data)
try:
	cla()
	axvline(0,ls= ":")
	axhline(0,ls=":")
	voltages=arange(0,5.01,0.2)
	for i in range(0,len(voltages)):
#	for v in arange(0,4.01,0.05):
		v=voltages[i]
		print v
		jba.setAmplitude(v)
		co=jba.getMeasurement()
		x=1.*i/len(voltages)
		plot(co[:,0],co[:,1],'o',color=((1-x,0,x)))
		axis([-3,4,-3,3])
		draw()
		show()
		data.set(p=jba.takePoint()[1])
		data.set(v=v)
		data.commit()
		data.savetxt()
finally:
	jba.setAmplitude(jba._vMaxAmplitude)
##
jba.init()
jba.addFrequency(frequency=9.28, shape=shape)
jba.sendWaveforms()
###
co=jba.getMeasurement()

##
jba.init()
##
print jba._fsb
print jba._pulseAnalyser._frequencies

##
cla()
plot(co[:,0],co[:,1],'o')
draw()
show()
##
co=jba.getMeasurement()
(clicks,IQData)=jba._pulseAnalyser._acqiris.multiplexedBifurcationMapAdd(co,0)
print IQData[:,0]
##
print jba._adjustRotationAndOffset(frequency=0)

##
jba.setAmplitude(0.55)
##
jba._magnitudeButton='variableAttenuator'	
##
jba._findAmplitude()
##
##
jba._findAmplitude()
##
jba.setRotation
jba.notify("iqPaxes",(1,0.2,2.2))
##
jba._setRotationAndOffset(1.3,-0.05,0.75)
##
print jba._magnitudeButton
##
jba.setAmplitude(1.)
##
print jba._vMaxAmplitude
##
cla()
plot(range(0,len(jba.shape)),shape)
draw()
show()
##
jba.init()
jba.addFrequency(frequency=9.28)
jba.sendWaveforms()