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
Qbit_drive=instrumentManager.getInstrument('MWSource_Qubit')

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
data=Datacube('datacube name')
dataManager.addDatacube(data)
i=0
Qfreqs=arange(4,6,0.002)
Qpower=-20

Qbit_drive.setPower(Qpower)
for Qfreq in Qfreqs:
	print "Qfreq=%f"%Qfreq
	#setMyVNAPower(power)
	Qbit_drive.setFrequency(Qfreq)
	Qbit_drive.turnOn()
	child=vna.getTrace(waitFullSweep=True)
	child.setName("Qfreq=%f"%Qfreq)
	data.addChild(child)
	data.set(i=i,Qfreq=Qfreq,temperature=temperature.temperature())
	data.commit()
	#child.savetxt()
	i+=1
data.savetxt()
##
#setMyVNAPower(-52)


