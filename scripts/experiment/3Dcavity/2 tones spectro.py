import sys
import os
import os.path
from pyview.helpers.instrumentsmanager import *
from pyview.lib.datacube import *
from pyview.config.parameters import params
instrumentManager=Manager()
from pyview.helpers.datamanager import DataManager
dataManager = DataManager()
##
acqiris=instrumentManager.getInstrument('acqiris')
def getOnePoint():
	datas=acqiris.AcquireTransferV4(nLoops=1,transferAverage=True,getHorPos=False)[0]
	return mean(datas[0]),mean(datas[1])
##
pgQB=instrumentManager.getInstrument('pg_qb')
print pgQB
mwQB=instrumentManager.getInstrument('MWSource_qb')
print mwQB
pgCav=instrumentManager.getInstrument('pg_Cavite')
print pgCav
mwCav=instrumentManager.getInstrument('MWSource_Cavite')
print mwCav
## 2 TONES SPECTROSCOPY

fcav=6.2143
mwCav.setFrequency(fcav)
mwCav.setPower(23)
pgQB.generatePulse(duration=4000,DelayFromZero=5995)
pgQB.sendPulse()
	
powerQB=-20.9
mwQB.setPower(powerQB)
mwQB.turnOn()
	
	
data=Datacube('SpectroQB pQB=%f'%powerQB)
dataManager.addDatacube(data)

try:
	for f in arange(5.3,5.4,0.001):
		mwQB.setFrequency(f)
		time.sleep(0.1)
		point=acqiris.getOnePointFullAveraged(nLoops=10)
		data.set(f=f,I=point[0],Q=point[1])
		data.commit()
except: 
	raise
finally:
	data.savetxt()
	
	
	
## RABI

fcav=6.2143
mwCav.setFrequency(fcav)
mwCav.setPower(23)
	
powerQB=-0.9
mwQB.setPower(powerQB)
mwQB.turnOn()
	
fQB=5.338

	
data=Datacube('rabi pQB=%f, fQB=%f' %(powerQB,fQB))
dataManager.addDatacube(data)
try:		pgQB.generatePulse(frequency=fQB,duration=duration,DelayFromZero=9995-duration)
		pgQB.sendPulse()

	for duration in arange(0,1000,10):


		time.sleep(0.2)
		
		point=acqiris.getOnePointFullAveraged(nLoops=100)
		data.set(duration=duration,I=point[0],Q=point[1])
		data.commit()
except: 
	raise
finally:
	data.savetxt()
	
	
	
	
## T1

fcav=6.2143
mwCav.setFrequency(fcav)
mwCav.setPower(23)
	
powerQB=-0.9
mwQB.setPower(powerQB)
mwQB.turnOn()
	
fQB=5.338

	
data=Datacube('T1 pQB=%f, fQB=%f' %(powerQB,fQB))
dataManager.addDatacube(data)
try:
	for delay in arange(0,10000,100):

		pgQB.generatePulse(frequency=fQB,duration=42,DelayFromZero=9995-delay-42)
		pgQB.sendPulse()

		time.sleep(0.2)
		
		point=acqiris.getOnePointFullAveraged(nLoops=100)
		data.set(delay=delay,I=point[0],Q=point[1])
		data.commit()
except: 
	raise
finally:
	data.savetxt()
	
	













##

from matplotlib.pyplot import *
datas=acqiris.AcquireTransferV4(nLoops=1,transferAverage=True,getHorPos=False)[0]
#figure()
plot(datas[0])
draw()
show()
##
print acqiris.parameters()


##
totalArraySizes=zeros(4,dtype=bool)
print totalArraySizes
totalArraySizes.ctypes.data


