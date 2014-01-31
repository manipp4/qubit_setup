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
Coil=instrumentManager.getInstrument('Keithley2400')
import math

##
def setMyVNAPower(power):
	atten=-20*math.modf(power/20.)[1]
	pow=power+atten-5
	vna.setAttenuation(atten)
	vna.setPower(pow)	
##
data=Datacube('VNAvsCoil3')
dataManager.addDatacube(data)
k=0
currents=arange(-1.55e-3,-1.25e-3,0.02e-3)
Coil.turnOn()
for curr in currents:
	print "Current=%f"%curr
	Coil.setCurrent(curr)
	#time.sleep(4)
	child=vna.getTrace(waitFullSweep=True)
	child.setName("Current=%f"%curr)
	data.addChild(child)
	data.set(k=k,Current=curr)
	data.commit()
	#child.savetxt()
	k+=1
data.savetxt()
Coil.turnOff()
##
#setMyVNAPower(-52)
child=vna.getTrace(waitFullSweep=False)

