from pyview.helpers.instrumentsmanager import Manager
from pyview.lib.datacube import Datacube
import numpy as np
import time

##
t=scope.getWaveform(1)
d=Datacube()
d.toDataManager()
d.createColumn('t',t['C1'][u0:-1:5])
##
mc=np.zeros(999)
mc[-2]=1.

for i in range(200):
	pg_f1.pulseCorrectionFunction=generateFunc(mc)
	pg_f1.clearPulse()
	pg_f1.addPulse(generatorFunction='square',start=10000,stop=20000, applyCorrections=True,amplitude=0.5)
	pg_f1.preparePulseSequence()
	pg_f1.sendPulseSequence()
	print i
	time.sleep(10)
	t=scope.getWaveform(1)
	d.createColumn('t',t['C1'][u0:-1:5])
	print 'index', -(i+2), " =" ,mc[-(i+2)], "changed to"
	dy=(d['t'][i]/np.mean(d['t'][-20:-1])-1.)*1.3
	mc[-(2+i)]-=dy
	mc[-(3+i)]+=dy
	print mc[-(2+i)]
##
dc=Datacube("correction")
dc.toDataManager()
dc.createColumn("correction",mc)

	



##

pg_f3=Manager().getInstrument('pg_f3')
def generateFunc():
	cor=np.zeros(20000)
	cor[-2]=1+0.04
	for i in range(1,18000):
		cor[-(i+2)]=-0.04*np.exp(-i/20.)/20.
	cor/=sum(cor)
	
	def myCorrFunc(ishape):
		shape=np.zeros(20000)
		for i in range(1,20000):
			if(abs(cor[-(i+1)])<1e-7):continue
			shape[i-1:-1]+=ishape[:-(i)]*cor[-(i+1)]
		return shape
		
	return myCorrFunc
	
f=generateFunc()	
print f
pg_f3.pulseCorrectionFunction=f
##
acqiris=Manager().getInstrument('acqiris')
print acqiris.Temperature()
print acqiris("Temperature()")
