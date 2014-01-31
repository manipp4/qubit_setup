##
from config.instruments import *
from matplotlib.pyplot import *
import numpy
import scipy
from pyview.helpers.datamanager import DataManager
dataManager = DataManager()
instrumentManager=Manager()
register=instrumentManager.getInstrument('register')
vna=instrumentManager.getInstrument('vna')
vna.timeOut=200
##
data=Datacube('4 JBA spectroscopy')
dataManager.addDatacube(data)
i=0
## VS POWER
vna.setVideoBW(1000)
vna.setNumberOfAveraging(01)
vna.setAveraging(True)
##
powers=[0]#arange(-16.8,0.001,0.2)
try:
	for p in powers:
		print "P=%f"%p
		vna.setPower(p)
		child=vna.getTrace(waitFullSweep=True)
		child.setName("P=%f"%p)
		data.addChild(child)
		data.set(i=i,p=p)
		child.savetxt()
		data.commit()
		i+=1
finally:
	data.savetxt()
################################
##### VS vFlux
p=-14
data=Datacube('4 JBA spectroscopy P=%f'%p)
dataManager.addDatacube(data)
i=0
#
#
vna.setPower(p)
#
voltages=arange(0,0.9,0.05)
try:
	for v in voltages:
		print "v=%f"%v
		coil.setVoltage(v,slewRate=0.1)
		child=vna.getTrace(waitFullSweep=True)
		child.setName("v=%f"%v)
		data.addChild(child)
		data.set(i=i,v=v)
		child.savetxt()
		data.commit()
		i+=1
finally:
	data.savetxt()
	coil.setVoltage(0,slewRate=0.1)
	
	
##
















