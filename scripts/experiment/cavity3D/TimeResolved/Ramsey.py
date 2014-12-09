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
############
## Ramsey ##
############

spp=5#seconds per awg point
data=Datacube('RamseyHPR_2')
dataManager.addDatacube(data)
attenuator.setVoltage(1.88	)
cavity_drive.setFrequency(7.07885)
frequency=6.0963#qubit_drive.frequency()
durations=arange(0,40000,240)
qubit_drive2.turnOn()
qubit_drive2.setPower(-4.7)
qubit_drive2.setFrequency(frequency)
iOff=0
qOff=0
pipulse=120/spp
d=dict()
d['freq']=frequency
for duration in durations:
	print"duration=%f"%duration 
	pulseGenerator.clearPulse()
	pulseGenerator.generatePulse(frequency=frequency, duration=pipulse/2, DelayFromZero=10000-pipulse/2, useCalibration=False)
	pulseGenerator.generatePulse(frequency=frequency, duration=pipulse/2, DelayFromZero=10000-pipulse-duration/spp, useCalibration=False)
	pulseGenerator.sendPulse()
	pulseGenerator2.clearPulse()
	pulseGenerator2.generatePulse(frequency=frequency, duration=duration/spp+100+pipulse, DelayFromZero=10000-duration/spp-100, useCalibration=False)
	#pulseGenerator2.generatePulse(frequency=frequency, duration=pipulse/2+200, DelayFromZero=10000-pipulse-duration/spp-100, useCalibration=False)
	pulseGenerator2.sendPulse()
	time.sleep(0.5)
	acqiris.AcquireTransferV4(transferAverage=True,nLoops=10,wantedChannels=3)
	acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
	chanels= acqiris("DLLMath1Module.mean")
	amp=sqrt((chanels[0]-iOff)**2+(chanels[1]-qOff)**2)
	data.set(duration=duration,i=chanels[0],q=chanels[1],amp=amp)
	data.commit()
data.setParameters(d)	
data.savetxt()

##
def fitFuncRam(x, a, b, f, p, x0):
    return a*exp(-x/x0)*cos(f*x+p)+b 


## Ramsey loop##
################
spp=20#seconds per awg point
attenuator.setVoltage(1.88)
cav_freq=7.07885
cavity_drive.setFrequency(cav_freq)
qubit_drive2.setFrequency(6.0966)
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

data=Datacube('RamseyLoop_2')
dataManager.addDatacube(data)

iOff=0
qOff=0

durations=arange(500,30000,500)
indexes=arange(0,60,1)
for index in indexes:
	child=Datacube("i%i"%index)
	data.addChild(child)
	for duration in durations:
		print"duration=%f"%duration 
		pulseGenerator.clearPulse()
		pulseGenerator.generatePulse(frequency=frequency, duration=pipulse/2, DelayFromZero=15000-pipulse/2, useCalibration=False)
		pulseGenerator.generatePulse(frequency=frequency, duration=pipulse/2, DelayFromZero=15000-pipulse-duration/spp, useCalibration=False)
		pulseGenerator.sendPulse()
		pulseGenerator2.clearPulse()
		pulseGenerator2.generatePulse(frequency=frequency, duration=pipulse/2+100, DelayFromZero=15000-pipulse/2-100, useCalibration=False)
		pulseGenerator2.generatePulse(frequency=frequency, duration=pipulse/2+100, DelayFromZero=15000-pipulse-duration/spp-100, useCalibration=False)
		pulseGenerator2.sendPulse()
		time.sleep(0.5)
		acqiris.AcquireTransferV4(transferAverage=True,nLoops=1,wantedChannels=3)
		acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
		chanels= acqiris("DLLMath1Module.mean")
		amp=sqrt((chanels[0]-iOff)**2+(chanels[1]-qOff)**2)
		child.set(duration=duration,i=chanels[0],q=chanels[1],amp=amp)
		child.commit()
	popt, pcov = curve_fit(fitFuncRam,child['duration'],child['amp'],[.05,0.,6000.,0.0005,0])
	times=child['duration']
	t2fit=fitFuncRam(times,popt[0],popt[1],popt[2],popt[3],popt[4])
	child.createColumn('t2fit',t2fit)
	data.set(index=index,t2=popt[4],Ramfreq=popt[2])
	data.commit()
	data.savetxt()
######################
## Ramsey spin echo ##
######################

spp=2#seconds per awg point
data=Datacube('SpinEchoLPR_2')
dataManager.addDatacube(data)
attenuator.setVoltage(1.88)
cavity_drive.setFrequency(7.07885)
frequency=6.0963#qubit_drive.frequency()
durations=arange(0,20000,176)
qubit_drive2.turnOn()
qubit_drive2.setPower(10)
qubit_drive2.setFrequency(frequency)
iOff=0
qOff=0
pipulse=22/spp
d=dict()
d['freq']=frequency
for duration in durations:
	print"duration=%f"%duration 
	pulseGenerator.clearPulse()
	pulseGenerator.generatePulse(frequency=frequency, duration=pipulse/2, DelayFromZero=10000-pipulse/2, useCalibration=False)
	pulseGenerator.generatePulse(frequency=frequency, duration=pipulse, DelayFromZero=10000-pipulse-(duration/2)/spp, useCalibration=False)
	pulseGenerator.generatePulse(frequency=frequency, duration=pipulse/2, DelayFromZero=10000-pipulse-duration/spp, useCalibration=False)
	pulseGenerator.sendPulse()
	pulseGenerator2.clearPulse()
	pulseGenerator2.generatePulse(frequency=frequency, duration=duration/spp+100+pipulse, DelayFromZero=10000-duration/spp-100, useCalibration=False)
	#pulseGenerator2.generatePulse(frequency=frequency, duration=pipulse/2+200, DelayFromZero=10000-pipulse-duration/spp-100, useCalibration=False)
	pulseGenerator2.sendPulse()
	time.sleep(0.5)
	acqiris.AcquireTransferV4(transferAverage=True,nLoops=10,wantedChannels=3)
	acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
	chanels= acqiris("DLLMath1Module.mean")
	amp=sqrt((chanels[0]-iOff)**2+(chanels[1]-qOff)**2)
	data.set(duration=duration,i=chanels[0],q=chanels[1],amp=amp)
	data.commit()
data.setParameters(d)	
data.savetxt()