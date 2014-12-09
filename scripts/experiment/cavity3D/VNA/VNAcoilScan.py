
import numpy
import scipy
from pyview.lib.datacube import *
from pyview.helpers.datamanager import DataManager
from pyview.helpers.instrumentsmanager import Manager
from pyview.lib.smartloop import *
dataManager = DataManager()
instrumentManager=Manager()

vna=instrumentManager.getInstrument('vna')
print vna
coil=instrumentManager.getInstrument('Yoko3')
mmr3_module2=Manager().getInstrument('mmr3_module2')
import math
##
data=Datacube()

##
def setMyVNAPower(power):              
	offsetVNA=-7
	power=power-offsetVNA
	if -80<=power<=0:
		atten,pow=divmod(power,-10)
		atten*=10
		if atten>60:
			atten=60
			pow=power+60
		print 'atten='+str(atten)+'dB and power='+str(pow)+'dB'
		vna.setAttenuation(atten)
		vna.setPower(pow)
	else:
		print 'target power out of range'


##
data=Datacube('readout_m57dBm')
data.toDataManager()
xMin=-17
xMax=+17
xStep=0.5
#currents1=arange(iMin,iMax,iStep)
#currents2=arange(iMax,iMin,-iStep)
#currents3=SmartLoop(-2.5,0.5,2.5,name="coilVoltages")
#currents=concatenate([currents1,currents2])
voltages=SmartLoop(xMin,xStep,xMax,name="coilVoltages")
coil.turnOn()
for volt in voltages:
	print "Voltage=%f"%volt
	coil.setVoltage(volt,slewRate=0.2)
	child1=vna.getTrace(waitFullSweep=True)
	child1.setName("Voltage=%f"%volt)
	data.addChild(child1)
	#time.sleep(4)
	data.set(voltage=volt,temperature=mmr3_module2.temperature(thermometerIndex=3))	
	data.commit()
data.savetxt()
#coil.setVoltage(0,slewRate=0.0005)
#####################
### demagnetizing ###
iMax=0.1
iStep=0.005
currents1=arange(0,iMax,iStep)
currents2=arange(iMax,-0.8*iMax,-iStep)
currents3=arange(-0.8*iMax,0.6*iMax,iStep)
currents4=arange(0.6*iMax,-0.4*iMax,-iStep)
currents5=arange(-0.4*iMax,0.2*iMax,iStep)
currents6=arange(0.2*iMax,-0.0*iMax,-iStep)
currents=concatenate([currents1,currents2,currents3,currents4,currents5,currents6])
#currents=arange(iMin,iMax,iStep)
coil.turnOn()
for curr in currents:
	print "Current=%f"%curr
	coil.setVoltage(curr,slewRate=0.001)
coil.setVoltage(0,slewRate=0.0005)
#coil.turnOff()
############################
##
t1=time.time()
vna.getTrace(waitFullSweep=True)
t2=time.time()
print t2-t1