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
data=Datacube('ParaAmp at working pointm, No Pump')
dataManager.addDatacube(data)
i=0
powers=arange(-20,0.5,0.5)
#vna.setStartFrequency(7.00)
#vna.setStopFrequency(7.05)
#vna.setVideoBW(10)

for power in powers:
	print "Power=%f"%power
	vna.setPower(power)
	time.sleep(0.5)
	child1=vna.getTrace(waitFullSweep=True)
	child1.setName("power=%f"%power)
	data.addChild(child1)
	data.set(i=i,power=power)
	data.commit()
	#child.savetxt()
	i+=1
data.savetxt()
##
setMyVNAPower2(-46)

##
data=Datacube('ParaAmp stability test')
data.toDataManager()

for i in range(720):
	print i
	data.set(index=i,Power=mean(fsp.getTrace()[1]),commit=True)
	time.sleep(60)
		
#myCube1.createCol(name='c',values=[0,1,2,3,4,5,6,7,8,9,10])
##
data=Datacube('ParaAmp SignalPower Sweep w 5dBmPump')
data.toDataManager()
Powers=arange(-30,-4,1)
for pow in Powers:
	mw_qb.setPower(pow)
	mw_cav.turnOff()
	time.sleep(5)
	signal=mean(fsp.getTrace()[1])
	mw_cav.turnOn()
	print pow
	time.sleep(5)
	data.set(SignalPower=pow,ReflectedPower=signal,Gain=mean(fsp.getTrace()[1])-signal,commit=True)

##
data=Datacube('ParaAmp characterization')
data.toDataManager()
##
child=Datacube('ParaAmp NoSignal_10dBmPump')
data.addChild(child)
child.createCol(name='Time',values=fsp.getTrace()[0])
child.createCol(name='Power',values=fsp.getTrace()[1])
##
trace=fsp.getTrace()
##
print mw_cav.setPower()

##zero before cooling cooling
data=Datacube('baseLine')
data=vna.getTrace()
data.toDataManager()
##spectra during cooling
import pyview.lib.smartloop as sl
data=Datacube('warmup')
data.toDataManager()
megaLoop=sl.SmartLoop(132,1,1000000,name="megaLoop")
for index in megaLoop:
	t1=datetime.datetime.now().time()
	t2=time.time()
	print 'scan ',index,' time = ',t1,' = ',t2
	child=vna.getTrace(waitFullSweep=True)
	child.setName("index=%f"%index)
	data.set(index=index,time=t2,MC_RuO2=mmr3_module2.temperature(thermometerIndex=3),MC_cernox=mmr3_module1.temperature(thermometerIndex=3),commit=True)
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
vna.setStartFrequency(6.431100)
vna.setStopFrequency(6.431450)
vna.s  etNumberOfPoints(201)
powerLoop=sl.SmartLoop(0,-30,-30,name="powerLoop")
for power in powerLoop:
	vna.setTotalPower(power)
	data=vna.getTrace(waitFullSweep = True)
	data.setName('storageLine'+str(power)+'dBm')
	data.toDataManager()

##
vna.setStartFrequency(4.3728)
vna.setStopFrequency(4.3738)
vna.setNumberOfPoints(201)
powerLoop=sl.SmartLoop(0,-30,-30,name="powerLoop")
for power in powerLoop:
	vna.setTotalPower(power)
	data=vna.getTrace(waitFullSweep = True)
	data.setName('fundamental'+str(power)+'dBm')
	data.toDataManager()

##
coil.setVoltage(10.06,slewRate=0.2)
print coil.voltage()
##
data=Datacube('readout_coilAt6p5V')
data.toDataManager()
powerMin=-50
powerMax=-30
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