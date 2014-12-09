##curve
from config.instrumentsRSV import *
from matplotlib.pyplot import *
#from pyview.gui.mpl.backend import figure
import numpy
import scipy
from pyview.helpers.datamanager import DataManager
dataManager = DataManager()
instrumentManager=Manager()
vna=instrumentManager.getInstrument('vna')
temperature=instrumentManager.getInstrument('temperature')
import math

##
def setMyVNAPower(power):
	atten=-20*math.modf(power/20.)[1]
	pow=power+atten-5
	vna.setAttenuation(atten)
	vna.setPower(pow)	
##
data=Datacube('ResVsTemp')
dataManager.addDatacube(data)
setMyVNAPower(5)
for i in range(100):
	child=vna.getTrace(waitFullSweep=True)
	child.setName("Temp=%f"%temperature.temperature())
	data.addChild(child)
	data.set(i=i,temperature=temperature.temperature())
	data.commit()
	time.sleep(600)
	#child.savetxt()
data.savetxt()
##
vna.setStartFrequency(7.00)
vna.setStopFrequency(7.15)
vna.setVideoBW(10)
##
data=Datacube('130507_TiFilter')
dataManager.addDatacube(data)
vna.setStartFrequency(0.04)
vna.setStopFrequency(20)
vna.setVideoBW(10)
child=vna.getTrace(waitFullSweep=True)
child.setName("power=%f"%power)
data.addChild(child)
data.set(i=i,power=power,temperature=temperature.temperature())
data.commit()
data.savetxt()
