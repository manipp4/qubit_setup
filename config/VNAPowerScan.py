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
print vna
cavity_drive=instrumentManager.getInstrument('MWSource_cavity')
print coil
dcpump=instrumentManager.getInstrument('dcpump')
print dcpump
temperature=instrumentManager.getInstrument('temperature')
print temperature.temperature()
import math

##
def setMyVNAPower(power):
	atten=-20*math.modf(power/20.)[1]
	pow=power+atten-5
	vna.setAttenuation(atten)
	vna.setPower(pow)	
##
data=Datacube('VNAvsPower')
dataManager.addDatacube(data)
i=0
powers=arange(-65,-5,1)
for power in powers:
	print "Power=%f"%power
	#setMyVNAPower(power)
	child=vna.getTrace(waitFullSweep=True)
	child.setName("power=%f"%power)
	data.addChild(child)
	data.set(i=i,power=power,temperature=temperature.temperature())
	data.commit()
	#child.savetxt()
	i+=1
data.savetxt()
##
#setMyVNAPower(-52)


