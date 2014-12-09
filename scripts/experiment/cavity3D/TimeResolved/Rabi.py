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
cavitypulseGenerator=instrumentManager.getInstrument('PG_Cavity') 
cavitySWGenerator=instrumentManager.getInstrument('PG_SWITCH') 
##
def telegraph(x0,x):
	if (x<x0):
		y=0
	else: y=1
	return y

##
def fitRabi(t, f, a, b):
	return a*cos(f*t)+b

## Rabi
spp=1
data=Datacube('RabiLPR_3')
dataManager.addDatacube(data)
attenuator.setVoltage(3)
cav_freq=7.085
cavity_drive.setFrequency(cav_freq)
cav_pulse=5000/spp
cavitypulseGenerator.clearPulse()
cavitypulseGenerator.generatePulse(frequency=cav_freq, duration=cav_pulse, DelayFromZero=10000, useCalibration=False)
cavitypulseGenerator.sendPulse()
#cavitySWGenerator.clearPulse()
#cavitySWGenerator.generatePulse(frequency=cav_freq, duration=cav_pulse, DelayFromZero=10000, useCalibration=False)
#cavitySWGenerator.sendPulse()
probReadout=False
frequency=5.97#qubit_drive.frequency()
durations=arange(0,4000,20)
qubit_drive.setPower(-20)
qubit_drive.setFrequency(frequency)
qubit_drive.turnOn()
threshold=0.2
for duration in durations:
	print"duration=%f"%duration 
	pulseGenerator.clearPulse()
	pulseGenerator.generatePulse(frequency=frequency, duration=duration/spp, DelayFromZero=10000-duration/spp, useCalibration=False)
	pulseGenerator.sendPulse()
	#pulseGenerator2.clearPulse()
	#pulseGenerator2.generatePulse(frequency=frequency, duration=duration/spp+100, DelayFromZero=10000-duration/spp-100, useCalibration=False)
	#pulseGenerator2.sendPulse()
	time.sleep(0.5)
	if probReadout==False:
		acqiris.AcquireTransferV4(transferAverage=True,nLoops=10,wantedChannels=3)
		acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
		chanels= acqiris("DLLMath1Module.mean")
		amp=sqrt((chanels[0])**2+(chanels[1])**2)
		data.set(duration=duration,i=chanels[0],q=chanels[1],amp=amp)
		data.commit()
	else:
		acqiris.AcquireTransferV4(transferAverage=False,nLoops=10,wantedChannels=3)
		acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
		chanels= acqiris("DLLMath1Module.mean")
		Q=chanels[1]
		#amp=sqrt((chanels[0]-iOff)**2+(chanels[1]-qOff)**2)
		events=map(lambda x:telegraph(threshold,x),Q)
		prob_e=mean(events)
		data.set(duration=duration,prob_e=prob_e)	
		data.commit()
data.savetxt() 
##
print amp
##
popt, pcov = curve_fit(fitRabi,durations,amp,[0.1,0.1,0.01])
print popt[0]

## Rabi Amplitude
spp=20
data=Datacube('RabiAmpHPR_4')
dataManager.addDatacube(data)
attenuator.setVoltage(1.88)
cavity_drive.setFrequency(7.07885)
cav_pulse=5000/spp
cavitypulseGenerator.clearPulse()
cavitypulseGenerator.generatePulse(frequency=cav_freq, duration=cav_pulse, DelayFromZero=15000, useCalibration=False)
cavitypulseGenerator.sendPulse()
cavitySWGenerator.clearPulse()
cavitySWGenerator.generatePulse(frequency=cav_freq, duration=cav_pulse, DelayFromZero=15000, useCalibration=False)
cavitySWGenerator.sendPulse()

frequency=6.0968#qubit_drive.frequency()
duration=120/spp
amplitudes=arange(0.0,1.0,0.05)
qubit_drive2.setPower(5)
qubit_drive2.turnOn()
iOff=0
qOff=0
for amplitude in amplitudes:
	print"amplitude=%f"%amplitude 
	pulseGenerator.clearPulse()
	pulseGenerator.generatePulse(amplitude=amplitude, frequency=frequency, duration=duration, DelayFromZero=15000-duration, useCalibration=False)
	pulseGenerator.sendPulse()
	pulseGenerator2.clearPulse()
	pulseGenerator2.generatePulse(frequency=frequency, duration=duration+200/spp, DelayFromZero=15000-duration-200/spp, useCalibration=False)
	pulseGenerator2.sendPulse()
	time.sleep(0.5)
	acqiris.AcquireTransferV4(transferAverage=True,nLoops=10,wantedChannels=3)
	acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
	chanels= acqiris("DLLMath1Module.mean")
	amp=sqrt((chanels[0]-iOff)**2+(chanels[1]-qOff)**2)
	data.set(amplitude=amplitude,i=chanels[0],q=chanels[1],amp=amp)
	data.commit()
data.savetxt() 