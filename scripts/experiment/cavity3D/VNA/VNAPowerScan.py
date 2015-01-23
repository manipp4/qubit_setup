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
vna=instrumentManager.getInstrument('vnak2')
fsp=instrumentManager.getInstrument('fsp')
coil=instrumentManager.getInstrument('Yoko3')
mmr3_module2=Manager().getInstrument('mmr3_module2')
mmr3_module1=Manager().getInstrument('mmr3_module1')
print vna
import math
import datetime
##
print vna.setTotalPower(-30)
##
data=Datacube('ParaAmp at working pointm, No Pump')
dataManager.addDatacube(data)
i=0
powers=arange(-20,0.5,0.5)
#vna.setStartFrequency(7.00)
#vna.setStopFrequency(7.05)
#vna.setVideoBW(10)

for power in powers:
	print "Power=%f"%vna.setTotalPower(power)
	time.sleep(0.5)
	child1=vna.getFreqMagPhase(waitFullSweep=True)
	child1.setName("power=%f"%power)
	data.addChild(child1)
	data.set(i=i,power=power)
	data.commit()
	#child.savetxt()
	i+=1
data.savetxt()
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
vna.setStartFrequency(6.431100)
vna.setStopFrequency(6.431450)
vna.s  etNumberOfPoints(201)
powerLoop=sl.SmartLoop(0,-30,-30,name="powerLoop")
for power in powerLoop:
	vna.setTotalPower(power)
	data=vna.getFreqMagPhase(waitFullSweep = True)
	data.setName('storageLine'+str(power)+'dBm')
	data.toDataManager()

##
vna.setStartFrequency(4.3728)
vna.setStopFrequency(4.3738)
vna.setNumberOfPoints(201)
powerLoop=sl.SmartLoop(0,-30,-30,name="powerLoop")
for power in powerLoop:
	vna.setTotalPower(power)
	data=vna.getFreqMagPhase(waitFullSweep = True)
	data.setName('fundamental'+str(power)+'dBm')
	data.toDataManager()

##
coil.setVoltage(10.06,slewRate=0.2)
print coil.voltage()
##
data=Datacube('readout_coilAtm21Vb')
data.toDataManager()
powerMin=-60
powerMax=-20
powerStep=1
powers=SmartLoop(powerMin,powerStep,powerMax,name="vnaPower")
for power in powers:
	power=vna.setTotalPower(power)
	print "power=%f"%power
	child1=vna.getFreqMagPhase(waitFullSweep=True)
	child1.setName("power=%f"%power)
	data.addChild(child1)
	#time.sleep(4)
	data.set(power=power,temperature=mmr3_module2.temperature(thermometerIndex=3))	
	data.commit()
data.savetxt()
##
print mmr3_module1.temperature(thermometerIndex=3)