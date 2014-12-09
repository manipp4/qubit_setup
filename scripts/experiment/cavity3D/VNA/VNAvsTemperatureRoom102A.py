
import numpy
import scipy
from pyview.lib.datacube import *
from pyview.helpers.datamanager import DataManager
from pyview.helpers.instrumentsmanager import Manager
from pyview.lib.smartloop import *
import pyview.lib.smartloop as sl
import datetime
dataManager = DataManager()
instrumentManager=Manager()

vna=instrumentManager.getInstrument('vna')
print vna
coil=instrumentManager.getInstrument('Yoko3')
mmr3_module1=Manager().getInstrument('mmr3_module1')
mmr3_module2=Manager().getInstrument('mmr3_module2')
import math
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

##zero before cooling
data=Datacube('baseLine')
data=vna.getTrace()
data.toDataManager()
##spectra during cooling
data=Datacube('cooling21Nov2014')
data.toDataManager()
megaLoop=sl.SmartLoop(0,1,1000000,name="megaLoop")
for index in megaLoop:
	t1=datetime.datetime.now().time()
	t2=time.time()
	print 'scan ',index,' time = ',t1,' = ',t2
	child=vna.getTrace(waitFullSweep=True)
	child.setName("index=%f"%index)
	data.set(index=index,time=t2,HT3=mmr3_module1.temperature(thermometerIndex=3),BT3=mmr3_module2.temperature(thermometerIndex=3),commit=True)
	data.addChild(child)
##
vna.setStartFrequency(7.05)
vna.setStopFrequency(7.55)
vna.setNumberOfPoints(401)
vna.setTotalPower(-30)
data=vna.getTrace(waitFullSweep = True)
data.setName('readoutLinem30dBm')
data.toDataManager()
##
print mmr3_module2.temperature(thermometerIndex=3)