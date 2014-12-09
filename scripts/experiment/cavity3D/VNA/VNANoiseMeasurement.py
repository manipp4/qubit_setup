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
Qbit_drive=instrumentManager.getInstrument('MWSource_cavity')
#Qbit_drive=instrumentManager.getInstrument('MWSource_Qubit')

print coil
dcpump=instrumentManager.getInstrument('dcpump')
print dcpump
temperature=instrumentManager.getInstrument('temperature')
print temperature.temperature()
import math

##
def setMyVNAPower(power):
	atten=-10*math.modf(power/10.)[1]
	pow=power+atten-5
	vna.setAttenuation(atten)
	vna.setPower(pow)	
##
data=Datacube('datacube name')
dataManager.addDatacube(data)
i=0
freqs=arange(7.08235,7.091,0.00765)
powers=arange(-80,-40,5)

#Qbit_drive.setPower(Qpower)
for power in powers:
	setMyVNAPower(power)
	
	child_power=Datacube("VNA_power=%f"%power)
	data.addChild(child_power)
	for freq in freqs:
		print "VNA_freq=%f"%freq
		vna.setCWFrequency(freq)
		child_freq=Datacube("VNA_freq=%f"%freq)
		child_power.addChild(child_freq)
		for ind in range(1,1000):
			#setMyVNAPower(power)
			#Qbit_drive.setFrequency(Qfreq)
			#Qbit_drive.turnOn()
			para=vna.getTrace(waitFullSweep=True)
			#print para.column("mag")[0]
			
			child_freq.set(i=i,index=ind,VNA_freq=freq,VNA_power=power,mag=para.column("mag")[0],phase=para.column("phase")[0])
			child_freq.commit()
			#child.savetxt()
			i+=1
data.savetxt()
##
#setMyVNAPower(-52)


