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
	datas=acqiris.AcquireTransferV4()[0]
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
##
data=Datacube('cavity')
dataManager.addDatacube(data)

mwQB.turnOff()
mwCav.setPower(23)

try:
	for f in arange(6.17,6.25,0.001):
		mwCav.setFrequency(f)
		time.sleep(0.1)
		point=acqiris.getOnePointFullAveraged(nLoops=10)
		data.set(f=f,I=point[0],Q=point[1])
		data.commit()
except:
	raise
finally:
	data.savetxt()
	
##


fQB=5.338
pgQB.generatePulse(frequency=fQB,duration=42,DelayFromZero=9995-duration)
pgQB.sendPulse()

data=Datacube('cavity')
dataManager.addDatacube(data)

mwQB.turnOff()
mwCav.setPower(23)

try:
	for f in arange(6.17,6.25,0.001):
		mwCav.setFrequency(f)
		time.sleep(0.1)
		point=acqiris.getOnePointFullAveraged(nLoops=10)
		data.set(f=f,I=point[0],Q=point[1])
		data.commit()
except:
	raise
finally:
	data.savetxt()