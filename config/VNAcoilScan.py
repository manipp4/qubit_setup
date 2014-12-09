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
coilVoltage=instrumentManager.getInstrument('Yoko1')
print coil


##
def setMyVNAPower(power):
	atten=-20*math.modf(power/20.)[1]
	pow=power+atten-5
	vna.setAttenuation(atten)
	vna.setPower(pow)	
##
data=Datacube('VNAvsCoil1')
dataManager.addDatacube(data)
k=0
voltages=arange(-3,0.1,0.05)
for voltages in voltages:
	print "voltages=%f V"%voltages
	coilVoltage.setVoltage(voltages)
	#time.sleep(4)
	child=vna.getTrace(waitFullSweep=True)
	child.setName("voltages=%f V"%voltages)
	data.addChild(child)
	data.set(k=k,Voltage=voltages)
	data.commit()
	#child.savetxt()
	k+=1
data.savetxt()
coilVoltage.setVoltage(0)
##
#setMyVNAPower(-52)
child=vna.getTrace(waitFullSweep=False)

