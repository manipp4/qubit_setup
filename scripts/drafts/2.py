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

##
f0=9.145
awg.setOffset(2,0.5)
p=-7
pg._MWSource.setPower(p)
data=Datacube("Rabi p = %f"%p)
dataManager.addDatacube(data)
durations=arange(0,200,1)
frequencies=arange(f0-0.05,f0+0.05,0.0005)
i=0
try:
	for f in frequencies:
		child=Datacube("f=%f"%f)
		data.addChild(child)
		data.set(f=f)
		data.set(i=i)
		pg._MWSource.setFrequency(f)
		for duration in durations:
			child.set(duration=duration)
			pg.clearPulse()
			pg.generatePulse(duration=duration, frequency=f, amplitude=1.,DelayFromZero=register.parameters()['readoutDelay']-duration-25, useCalibration=True)
			pg.sendPulse()
			time.sleep(0.5)
			child.set(p=jba.takePoint()[1])
			child.commit()
		child.savetxt()
		i+=1
		data.commit()
finally:
	data.savetxt()
	
##
f0=9.145
awg.setOffset(2,0.5)
p=-7
pg._MWSource.setPower(p)
data=Datacube("Rabi")
dataManager.addDatacube(data)
i=0
durations=arange(0,200,1)
powers=arange(-10,0,1)
##
powers=[0]
try:
	for power in powers:
		data.set(power=power)
		data.set(i=i)
		child=Datacube("p=%f"%p)
		data.addChild(child)
		for duration in durations:
			pg._MWSource.setPower(power)
			child.set(duration=duration)
			pg.clearPulse()
			pg.generatePulse(duration=duration, frequency=f0, amplitude=1.,DelayFromZero=register.parameters()['readoutDelay']-duration-25, useCalibration=True)
			pg.sendPulse()
			time.sleep(0.2)
			child.set(p=jba.takePoint()[1])
			child.commit()
		child.savetxt()
		data.commit()
		i+=1
finally:
	data.savetxt()
	