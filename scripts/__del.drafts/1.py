##curve
from config.instruments import *
from matplotlib.pyplot import *
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
shape=zeros((20000),dtype = numpy.complex128)
shape[10000:10010]=linspace(0,1,10)
shape[10010:10210]=1
shape[10210:10215]=linspace(1,0.8,5)
shape[10215:13215]=0.85
shape[13215:13225]=linspace(0.8,0,10)
cla()
plot(range(0,len(shape)),shape)
draw()
show()
jba.shape=shape
jba.init()
jba.init()
jba.addFrequency(frequency=9.265, shape=shape)
jba.sendWaveforms()
time.sleep(0.5)


##
print dir(jba._pulseGenerator._mixer)


##
pg.clearPulse()
duration=2000
pg.generatePulse(duration=duration, frequency=7., amplitude=1.,DelayFromZero=register.parameters()['readoutDelay']-duration-5, useCalibration=True)
pg.sendPulse()
##

data=Datacube("spectro 1D")
dataManager.addDatacube(data)
#frequencies=arange(8.6,8.8,0.001)
pg._MWSource.setFrequency(8.6)
voltages=arange(-2,2,0.005)
try:
	for v in voltages:
		awg.setOffset(2,v)
		time.sleep(0.2)
		data.set(v=v)
		data.set(p=jba.takePoint()[1])
		data.commit()
finally:
	data.savetxt()
##
awg.setOffset(3,0)
##
vflux=-0.7
pg.clearPulse()
duration=2000
pg.generatePulse(duration=duration, frequency=7., amplitude=1.,DelayFromZero=register.parameters()['readoutDelay']-duration-25, useCalibration=True)
pg.sendPulse()
pg._MWSource.turnOn()
#awg.setOffset(2,vflux)
#awg.setOffset(3,vflux)
#coil.setVoltage(2.,slewRate=1.)
##
pg._MWSource.turnOff()
##
vcoil=0.15
coil.setVoltage(vcoil)
##
jba.measureSCurve(voltages=arange(2.6,3.3,0.01))
##
p=-25
pg._MWSource.setPower(p)
pg._MWSource.turnOn()
data=Datacube("spectro p = %f,vcoil=%f"%(p,vcoil))
dataManager.addDatacube(data)
try:
		frequencies=arange(8.2,9.,0.002)
		for f in frequencies:
			pg._MWSource.setFrequency(f)
			time.sleep(0.1)
			data.set(f=f)
			data.set(p=jba.takePoint()[1])
			data.commit()
finally:
		data.savetxt()
		
##

pg._MWSource.setFrequency(8.318)
##
awg.setOffset(2,-1.03)
##
f0=8.925
awg.setOffset(2,vflux)
p=-7
pg._MWSource.setPower(p)
data=Datacube("Rabi p = %f"%p)
dataManager.addDatacube(data)
##
durations=arange(000,5000,2)
try:
	for duration in durations:
		data.set(duration=duration)
		pg.clearPulse()
		pg.generatePulse(duration=duration, frequency=f0, amplitude=1.,DelayFromZero=register.parameters()['readoutDelay']-duration-25, useCalibration=True)
		pg.sendPulse()
		time.sleep(0.5)
		data.set(p=jba.takePoint()[1])
		data.commit()
finally:
	data.savetxt()
	
##
f0=9.16
awg.setOffset(2,0.5)
p=-4
pg._MWSource.setPower(p)
pg._MWSource.turnOn()
duration=20.
data=Datacube("T1 p = %f"%p)
dataManager.addDatacube(data)

delays=arange(0,1000,5)
try:
	for delay in delays:
		data.set(delay=delay)
		pg.clearPulse()
		pg.generatePulse(duration=duration, frequency=f0, amplitude=1.,DelayFromZero=register.parameters()['readoutDelay']-duration-delay, useCalibration=True)
		pg.sendPulse()
		time.sleep(0.5)
		data.set(p=jba.takePoint()[1])
		data.commit()
finally:
	data.savetxt()
##
f0=9.16
awg.setOffset(2,0.5)
p=-4
pg._MWSource.setPower(p)
duration=20.
delays=arange(0,500,2)
delay=25.
voltages=arange(1.9,2.4,0.002)
try:
	pg.clearPulse()
	pg.generatePulse(duration=duration, frequency=f0, amplitude=1.,DelayFromZero=register.parameters()['readoutDelay']-duration-delay, useCalibration=True)
	pg.sendPulse()
	pg._MWSource.turnOff()
	jba.measureSCurve(voltages = voltages)
	pg._MWSource.turnOn()
	jba.measureSCurve(voltages = voltages)
finally:
	print "finish"	
##
data=Datacube()
data.createColumn('v',gv.data1['v'])
data.createColumn('p',abs(-gv.data1['p']+gv.data2['p']))
dataManager.addDatacube(data)
##
vflux=0.5
pg.clearPulse()
duration=2000
pg.generatePulse(duration=duration, frequency=7., amplitude=1.,DelayFromZero=register.parameters()['readoutDelay']-duration-25, useCalibration=True)
pg.sendPulse()
awg.setOffset(2,vflux)
p=-28.
pg._MWSource.setPower(p)
data=Datacube("spectro")
dataManager.addDatacube(data)
##
try:
	i=0
	frequencies=arange(8.9,9.2,0.002)
	powers=arange(0,12.1,3)
	for p in powers:
		pg._MWSource.setPower(p)
		child=Datacube("p=%f"%p)
		data.addChild(child)
		data.set(i=i)
		data.set(p=p)
		data.commit()
		i+=1
		for f in frequencies:
			pg._MWSource.setFrequency(f)
			time.sleep(0.1)
			child.set(f=f)
			child.set(p=jba.takePoint()[1])
			child.commit()
		child.savetxt()
finally:
	data.savetxt()
	
##
pg._MWSource.turnOff()
##
voltages=arange(1.5,3,0.01)
jba.measureSCurve(voltages = voltages)
	