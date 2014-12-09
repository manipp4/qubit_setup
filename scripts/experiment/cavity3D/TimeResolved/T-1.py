from pyview.lib.datacube import *
from pyview.helpers.datamanager import *
from pyview.helpers.instrumentsmanager import *
instrumentManager=Manager()
dataManager=DataManager()
import math
import numpy
from scipy.optimize import curve_fit

##
acqiris=instrumentManager.getInstrument('acqiris')
cavity_drive=instrumentManager.getInstrument('MWSource_cavity')
qubit_drive=instrumentManager.getInstrument('MWSource_Qubit')
qubit_drive2=instrumentManager.getInstrument('MWSource_Qubit2')
attenuator=instrumentManager.getInstrument('Yoko3')
pulseGenerator=instrumentManager.getInstrument('pg_qb')
pulseGenerator2=instrumentManager.getInstrument('PG_QU_GENE_SW')
cavitypulseGenerator=instrumentManager.getInstrument('pg_cavity') 
cavitySWGenerator=instrumentManager.getInstrument('PG_SWITCH') 

##
def fitFunc(x, a, b, x0):
    return a*exp(-x/x0)+b  
##############    
## T1 loop ##
##############
spp=20#seconds per awg point
attenuator.setVoltage(1.88)
cav_freq=7.07885
cavity_drive.setFrequency(cav_freq)
frequency=6.0968#qubit_drive.frequency()
qubit_drive.setPower(-4)
qubit_drive.turnOn()
pipulse=104/spp

cav_pulse=5000/spp
cavitypulseGenerator.clearPulse()
cavitypulseGenerator.generatePulse(frequency=cav_freq, duration=cav_pulse, DelayFromZero=15000, useCalibration=False)
cavitypulseGenerator.sendPulse()
cavitySWGenerator.clearPulse()
cavitySWGenerator.generatePulse(frequency=cav_freq, duration=cav_pulse, DelayFromZero=15000, useCalibration=False)
cavitySWGenerator.sendPulse()

data=Datacube('T1Loop_7')
dataManager.addDatacube(data)

iOff=0
qOff=0

durations=arange(5000,300000,5000)
indexes=arange(0,60,1)
for index in indexes:
	child=Datacube("i%i"%index)
	data.addChild(child)
	for duration in durations:
		print"duration=%f"%duration 
		pulseGenerator.clearPulse()
		pulseGenerator.generatePulse(frequency=frequency, duration=pipulse, DelayFromZero=15000-pipulse-duration/spp, useCalibration=False)
		pulseGenerator.sendPulse()
		pulseGenerator2.clearPulse()
		pulseGenerator2.generatePulse(frequency=frequency, duration=pipulse+200, DelayFromZero=15000-pipulse-duration/spp-200, useCalibration=False)
		pulseGenerator2.sendPulse()

		time.sleep(0.5)
		acqiris.AcquireTransferV4(transferAverage=True,nLoops=10,wantedChannels=3)
		acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
		chanels= acqiris("DLLMath1Module.mean")
		amp=sqrt((chanels[0]-iOff)**2+(chanels[1]-qOff)**2)
		child.set(duration=duration,i=chanels[0],q=chanels[1],amp=amp)
		child.commit()
	popt, pcov = curve_fit(fitFunc,child['duration'],child['amp'],[.05,0.,6000.])
	times=child['duration']
	t1fit=fitFunc(times,popt[0],popt[1],popt[2])
	child.createColumn('t1fit',t1fit)
	data.set(index=index,t1=popt[2])
	data.commit()
	data.savetxt()
########
## T1 ##
########
spp=20#seconds per awg point
data=Datacube('T1HPR_1')
dataManager.addDatacube(data)
attenuator.setVoltage(1.25)
cavity_drive.setFrequency(7.07885)
frequency=6.09682#qubit_drive.frequency()
durations=arange(0,200000,5000)
qubit_drive.setPower(-4)
qubit_drive.turnOn()
iOff=0
qOff=0
pipulse=100/spp
for duration in durations:
	print"duration=%f"%duration 
	pulseGenerator.clearPulse()
	pulseGenerator.generatePulse(frequency=frequency, duration=pipulse, DelayFromZero=10000-pipulse-duration/spp, useCalibration=False)
	pulseGenerator.sendPulse()
	time.sleep(0.5)
	acqiris.AcquireTransferV4(transferAverage=True,nLoops=5,wantedChannels=3)
	acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
	chanels= acqiris("DLLMath1Module.mean")
	amp=sqrt((chanels[0]-iOff)**2+(chanels[1]-qOff)**2)
	data.set(duration=duration,i=chanels[0],q=chanels[1],amp=amp)
	data.commit()
popt, pcov = curve_fit(fitFunc,data['duration'],data['amp'],[.05,0.,6000.])
times=data['duration']
t1fit=fitFunc(times,popt[0],popt[1],popt[2])
data.createColumn('t1fit',t1fit)
data.set(index=index,t1=popt[2])
data.commit()
data.savetxt()
     