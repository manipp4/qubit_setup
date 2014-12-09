import numpy
import scipy
from pyview.lib.datacube import *
from pyview.helpers.datamanager import DataManager
from pyview.helpers.instrumentsmanager import Manager
from pyview.lib.smartloop import *
dataManager = DataManager()
instrumentManager=Manager()
mw_cav=Manager().getInstrument('MWSource_Cavity')
mw_qb=Manager().getInstrument('MWSource_Qubit')
vna=instrumentManager.getInstrument('vna')
fsp=instrumentManager.getInstrument('fsp')
coil=instrumentManager.getInstrument('Yoko3')
mmr3_module2=Manager().getInstrument('mmr3_module2')
mmr3_module1=Manager().getInstrument('mmr3_module1')
print vna
import math
import datetime
##
print mmr3_module1.temperature(thermometerIndex=3)
##
print fsp.getValueAtMarker()
##
print thermometer.temperature()
##
def setMyVNAPower(power):
	atten=-20*math.modf(power/20.)[1]
	pow=power+atten-5
	vna.setAttenuation(atten)
	vna.setPower(pow)	

##
#for Anritsu 37397C
def setMyVNAPower2(power):              
	atten=-20*math.modf(power/20.)[1]
	pow=power+atten+7
	vna.setAttenuation(atten)
	vna.setPower(pow)	
# DV 08/11/2014
import math
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
vna.setStartFrequency(4.3728)
vna.setStopFrequency(4.3738)
vna.setNumberOfPoints(201)

##
data=Datacube('fundamental_coilAt0V')
data.toDataManager()
powerMin=-57
powerMax=-45
powerStep=1
powers=SmartLoop(powerMin,powerStep,powerMax,name="vnaPower")
for power in powers:
	print "power=%f"%power
	setMyVNAPower(power)
	child1=vna.getTrace(waitFullSweep=True)
	child1.setName("power=%f"%power)
	data.addChild(child1)
	#time.sleep(4)
	data.set(power=power,temperature=mmr3_module2.temperature(thermometerIndex=3))	
	data.commit()
data.savetxt()
##
print mmr3_module1.temperature(thermometerIndex=3)