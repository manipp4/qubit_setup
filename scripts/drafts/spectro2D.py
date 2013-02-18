##curve
from config.instruments import *
from matplotlib.pyplot import *
#from pyview.gui.mpl.backend import figure
import numpy
import scipy
from pyview.helpers.datamanager import DataManager
dataManager = DataManager()
instrumentManager=Manager()
register=instrumentManager.getInstrument('register')
jba=instrumentManager.getInstrument('jba_qb1')
awg=instrumentManager.getInstrument('awg')
pg=instrumentManager.getInstrument('pg_qb_simple')
print pg
print jba_att
print jba
##
print register.parameters()
##
Datacube()
##
pg._mixer._calibration.offsetCalibrationData().set(i=0)
pg._mixer._calibration.offsetCalibrationData().commit()
##
jba._pulseGenerator._mixer._calibration.offsetCalibrationData().set(i=0)
jba._pulseGenerator._mixer._calibration.offsetCalibrationData().commit()

##

shape=zeros((20000),dtype = numpy.complex128)
shape[10000:10200]=1
shape[10200:13200]=0.8
shape=shape
jba.shape=shape
jba.init()
jba.init()
jba.addFrequency(frequency=6.83, shape=shape)
jba.sendWaveforms()
time.sleep(0.5)
#jba.calibrate()
##
pg.clearPulse()
duration=2000
pg.generatePulse(duration=duration, frequency=7., amplitude=1.,DelayFromZero=register.parameters()['readoutDelay']-duration-15, useCalibration=True)
pg.sendPulse()
##
m=instrumentManager.getInstrument('mixerqbsimple')
m.calibrate()

##
coil=instrumentManager.getInstrument('coil')

#
data=Datacube('Spectro 2D')
dataManager.addDatacube(data)
i=0
#
try:
	powers=arange(-30,-60,-2.5)
	for p in powers:
		pg._MWSource.setPower(p)
		data.set(i=i,p=p)
		child=Datacube('p=%f'%p)	
		data.addChild(child) 
		for f in arange(8.2,9.0501,0.005):
			pg._MWSource.setFrequency(f)
			time.sleep(0.05)
			child.set(p=jba.takePoint()[1])
			child.set(f=f)
			child.commit()
		child.savetxt()
		data.commit()
		data.savetxt()
		i+=1
except:
	print "error"
	raise
finally:
	coil.setVoltage(0,slewRate=1.)
##
awg.setOffset(2,0)

##
child=Datacube('v1=-2')	
dataManager.addDatacube(child) 
for f in arange(6,7,0.002):
	pg._MWSource.setFrequency(f)
	time.sleep(0.1)
	child.set(p=jba.takePoint()[1])
	child.set(f=f)
	child.commit()
child.savetxt()
##
print jba._magnitudeButton
##
print jba._findAmplitude(center=0.52)
##
jba.setAmplitude(amplitude=
##
acqiris=instrumentManager.getInstrument('acqiris')
print 'start'
print acqiris.AcquireV1()
co=acqiris.DMATransferV1()
print 'stop'
##

w= co[1][1]
for i in range(0,len(w)):
	if w[i]==
##
for i in range(0,10):
	coil.setVoltage(2.,slewRate=1.)
	coil.setVoltage(-2.,slewRate=1.)
	
##


awgflux=instrumentManager.getInstrument('awgflux')
vna=instrumentManager.getInstrument('vna')
print vna.getTrace()
#

for v in arange(-2,2,0.1):
	awgflux.setOffset(2,v)
	time.sleep(1.)
##
for channel in [1,2,3,4]:
	awgflux.setOffset(channel,0)
	time.sleep(1)
## last datacube
awgflux=instrumentManager.getInstrument('awgflux')
vna=instrumentManager.getInstrument('vna')
coil=instrumentManager.getInstrument('coil')
#

maxVoltages=[3.,2.,2.,2.,2]
for channel in [0]:#[1,2,3,4]:
	data=Datacube("2D Spectroscopy flux %i" %channel)
	dataManager.addDatacube(data)
	i=0
	# last measurement
	voltages=linspace(-maxVoltages[i],maxVoltages[i],200)
	try:
		for v in voltages:
			print i,v
			if channel==0:
				coil.setVoltage(v,slewRate=.1)
			else:
				awgflux.setOffset(channel,v)
			child=vna.getTrace(waitFullSweep=True)
			data.set(i=i,v=v)
			data.commit()
		  	child.setName(i)
			data.addChild(child)
			child.savetxt()
			data.savetxt()
			i+=1
		time.sleep(1.)
		awgflux.setOffset(channel,0.)
	finally:
		awgflux.setOffset(channel,0.)

##
coil=instrumentManager.getInstrument('coil')
print coil
vna=instrumentManager.getInstrument('vna')
print vna

data=Datacube('2D spectro vs flux')
dataManager.addDatacube(data)

voltages=arange(-1.8,1.8,0.01)
i=0
for v in voltages:
	coil.setVoltage(v,slewRate=0.1)
	child=vna.getTrace(waitFullSweep=True)
	data.addChild(	child)
	data.set(i=i,v=v)
	data.commit()
	i+=1
data.savetxt()
##
coil.setVoltage(0,slewRate=0.1)

## stoping vortices.
#voltages=arange(0.9,-0.9,-0.01)
for j in range(0,20):
	print j
	for v in voltages:
		coil.setVoltage(v,slewRate=0.1)
		time.sleep(0.5)
		print v
	voltages*=-0.9
##
channel=2
data=Datacube('Spectro 2D - vFlux%i' %channel)
dataManager.addDatacube(data)
i=0
try:
	for v in arange(-2,2.01,0.1):
		coil.setVoltage(v,slewRate=1.)
		data.set(i=i,v=v)
		child=Datacube('v=%f'%v)	
		data.addChild(child) 
		for f in arange(7,13.0001,0.005):
			pg._MWSource.setFrequency(f)
			time.sleep(0.1)
			child.set(p=jba.takePoint()[1])
			child.set(f=f)
			child.commit()
		child.savetxt()
		data.commit()
		data.savetxt()
except:
	print "error"
finally:
	coil.setVoltage(0,slewRate=1.)
	
##
coil.setVoltage(1.,slewRate=0.1)
##
for channel in [2]:
	data=Datacube('Spectro 2D - vflux %i'%channel)
	dataManager.addDatacube(data)
	i=0
	voltages=arange(-1,1,0.05)
	frequencies=arange(8.5,8.7,0.001)
	try:
		for v in voltages:
			if channel>1:
				awg.setOffset(channel,v)
			else :
				coil.setVoltage(v,slewRate=1.)
			data.set(i=i,v=v)
			child=Datacube('v=%f'%v)	
			data.addChild(child) 
			for f in frequencies:
				pg._MWSource.setFrequency(f)
				time.sleep(0.1)
				child.set(p=jba.takePoint()[1])
				child.set(f=f)
				child.commit()
			child.sortBy('p',reverse=True)
			f0=child['f'][0]
			child.sortBy('f')
			frequencies=arange(f0-0.1,f0+0.1,0.001)
			print "f0=%f"%f0
			data.set(f0=f0)
			child.savetxt()
			data.commit()
			data.savetxt()
	except:
		print "error"
	finally:
		coil.setVoltage(0,slewRate=1.)
		if channel>1:
			awg.setOffset(channel,0)	
			
##
coil.setVoltage(0.25,slewRate=0.1)
##
coil.setVoltage(-0,slewRate=1.)
##
pg.clearPulse()
duration=2000
pg.generatePulse(duration=duration, frequency=7., amplitude=1.,DelayFromZero=register.parameters()['readoutDelay']-duration-15, useCalibration=True)
pg.sendPulse()
##
child=Datacube('qb spectro, vcoil=%f'%coil.voltage())
dataManager.addDatacube(child)
pg._MWSource.setPower(-15)
frequencies=arange(4,12,0.005	)
try:
	for f in frequencies:
		pg._MWSource.setFrequency(f)
		time.sleep(0.05)
		child.set(p=jba.takePoint()[1])
		child.set(f=f)
		child.commit()
finally:
	child.savetxt()
##

##
p=-25
data=Datacube("2D Spectroscopy p=%f"%p)
dataManager.addDatacube(data)
i=0
pg._MWSource.setPower(p)
try:
	voltages=arange(-0.2,0.5,-0.05)
	for v in voltages:
		coil.setVoltage(v,slewRate=1.)
		data.set(i=i,v=v)
		child=Datacube('p=%f'%p)	
		data.addChild(child) 
		frequencies=arange(8.65,8.95,0.005)
		for f in frequencies:
			pg._MWSource.setFrequency(f)
			time.sleep(0.05)
			child.set(p=jba.takePoint()[1])
			child.set(f=f)
			child.commit()
		child.sortBy('p',reverse=True)
		f0=child['f'][0]
		child.sortBy('f')
		frequencies=arange(f0-0.25,f0+0.1501,0.005)
		child.savetxt()
		data.commit()
		data.savetxt()
		i+=1
except:
	print "error"
	raise
finally:
	coil.setVoltage(0,slewRate=1.)
############


