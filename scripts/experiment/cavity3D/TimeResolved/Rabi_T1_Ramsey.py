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
cavity_drive=instrumentManager.getInstrument('MWSource_Cavity')
qubit_drive=instrumentManager.getInstrument('MWSource_Qubit')
attenuator=instrumentManager.getInstrument('Yoko1')
pulseGenerator=instrumentManager.getInstrument('pg_qb')
pulseGenerator2=instrumentManager.getInstrument('PG_QU_GENE_SW')
cavitypulseGenerator=instrumentManager.getInstrument('PG_Cavity') 
cavitySWGenerator=instrumentManager.getInstrument('PG_SWITCH') 

## Rabi
data=Datacube('RabiHPR_1')
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
durations=arange(0,800,10)
qubit_drive.setPower(-4)
qubit_drive.turnOn()
iOff=0
qOff=0
for duration in durations:
	print"duration=%f"%duration 
	pulseGenerator.clearPulse()
	pulseGenerator.generatePulse(frequency=frequency, duration=duration, DelayFromZero=10000-duration, useCalibration=False)
	pulseGenerator.sendPulse()
	pulseGenerator2.clearPulse()
	pulseGenerator2.generatePulse(frequency=frequency, duration=duration+200, DelayFromZero=10000-duration-200, useCalibration=False)
	pulseGenerator2.sendPulse()
	time.sleep(0.5)
	acqiris.AcquireTransferV4(transferAverage=True,nLoops=10,wantedChannels=3)
	acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
	chanels= acqiris("DLLMath1Module.mean")
	amp=sqrt((chanels[0]-iOff)**2+(chanels[1]-qOff)**2)
	data.set(duration=duration,i=chanels[0],q=chanels[1],amp=amp)
	data.commit()
data.savetxt() 

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
##
def fitFunc(x, a, b, x0):
    return a*exp(-x/x0)+b  
    
## T1 loop

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
##
p0=[1,2]
print type(p0)
print p0
popt, pcov = curve_fit(fitFunc,child['duration'],child['amp'],[.05,0.,300.])
print popt
##
print popt[2]

## T1
spp=20#seconds per awg point
data=Datacube('T1LPR_2')
dataManager.addDatacube(data)
attenuator.setVoltage(3)
cavity_drive.setFrequency(7.085)
frequency=5.97#qubit_drive.frequency()
durations=arange(0,200000,5000)
qubit_drive.setPower(-20)
qubit_drive.turnOn()
iOff=0
qOff=0
pipulse=300/spp
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
data.set(t1=popt[2])
data.commit()
data.savetxt()
     
##
print popt[2]

## Ramsey
spp=10#seconds per awg point
data=Datacube('RamseyLPR_2')
dataManager.addDatacube(data)
attenuator.setVoltage(4.5)
cavity_drive.setFrequency(7.05481)
qbfreq=7.5312
qubit_drive.setFrequency(qbfreq)
durations=arange(0,20000,200)
#qubit_drive.setPower(-4)
iOff=0
qOff=0
pipulse=50/spp
for duration in durations:
	print"duration=%f"%duration 
	pulseGenerator.clearPulse()
	pulseGenerator.generatePulse(frequency=qbfreq, duration=pipulse/2, DelayFromZero=19000-pipulse/2, useCalibration=False)
	pulseGenerator.generatePulse(frequency=qbfreq, duration=pipulse/2, DelayFromZero=19000-pipulse-duration/spp, useCalibration=False)
	pulseGenerator.sendPulse()
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
		pulseGenerator2.generatePulse(frequency=frequency, duration=pipulse/2+200, DelayFromZero=15000-pipulse/2-100, useCalibration=False)
		pulseGenerator2.generatePulse(frequency=frequency, duration=pipulse/2+200, DelayFromZero=15000-pipulse-duration/spp-100, useCalibration=False)
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
	
	
## Res g spec
data=Datacube('Cavityspec_2')
dataManager.addDatacube(data)
qubit_drive.turnOff()

freqs=arange(7.078,7.089,0.00005)
power=4.3
attenuator.setVoltage(power)
for f in freqs:
	print"f=%f"%f 
	cavity_drive.setFrequency(f)
	time.sleep(.2)
	acqiris.AcquireTransferV4(transferAverage=True,nLoops=50,wantedChannels=3)
	acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
	chanels= acqiris("DLLMath1Module.mean")
	amp=sqrt((chanels[0])**2+(chanels[1])**2)
	data.set(f=f,i=chanels[0],q=chanels[1],amp=amp)
	data.commit()	
data.savetxt()  
        
## Res e spec
data=Datacube('CavityEspec_3')
dataManager.addDatacube(data)
qbfrequency=6.09682#qubit_drive.frequency()
qubit_drive.setPower(-4)
qubit_drive.turnOn()
pipulse=100
pulseGenerator.clearPulse()
pulseGenerator.generatePulse(frequency=qbfrequency, duration=pipulse, DelayFromZero=10000-pipulse, useCalibration=False)
pulseGenerator.sendPulse()
freqs=arange(7.078,7.089,0.0001)
power=4.3
attenuator.setVoltage(power)
for f in freqs:
	print"f=%f"%f 
	cavity_drive.setFrequency(f)
	time.sleep(.2)
	acqiris.AcquireTransferV4(transferAverage=True,nLoops=50,wantedChannels=3)
	acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
	chanels= acqiris("DLLMath1Module.mean")
	amp=sqrt((chanels[0])**2+(chanels[1])**2)
	data.set(f=f,i=chanels[0],q=chanels[1],amp=amp)
	data.commit()	
data.savetxt()       

## g resonance with qubit in g
qubit_drive.turnOff()
reps=arange(7.100,7.140,0.0002)
cavityfreq=7.126
cavity_drive.setFrequency(cavityfreq)
power=2.7
attenuator.setVoltage(power)
acqiris.AcquireTransferV4(transferAverage=True,nLoops=100,wantedChannels=3)
acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
chanels= acqiris("DLLMath1Module.mean")
amp=sqrt((chanels[0])**2+(chanels[1])**2)
print amp 

## g resonance with qubit in e
qbfrequency=6.87147
qubit_drive.setPower(-10)
qubit_drive.turnOn()
pipulse=64
pulseGenerator.clearPulse()
pulseGenerator.generatePulse(frequency=qbfrequency, duration=pipulse, DelayFromZero=10000-pipulse, useCalibration=False)
pulseGenerator.sendPulse()
time.sleep(0.5)
cavityfreq=7.126
cavity_drive.setFrequency(cavityfreq)
power=2.7
attenuator.setVoltage(power)
acqiris.AcquireTransferV4(transferAverage=True,nLoops=100,wantedChannels=3)
acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
chanels= acqiris("DLLMath1Module.mean")
amp=sqrt((chanels[0])**2+(chanels[1])**2)
print amp    

## T1 for 0.5 Gs on AWG
data=Datacube('T1HPR_2')
dataManager.addDatacube(data)
attenuator.setVoltage(1.7)
cavity_drive.setFrequency(7.07567)
frequency=6.5222#qubit_drive.frequency()
durations=arange(0,9000,50)
qubit_drive.setPower(-10)
iOff=0
qOff=0
pipulse=56/2
for duration in durations:
	print"duration=%f"%duration 
	pulseGenerator.clearPulse()
	pulseGenerator.generatePulse(frequency=frequency, duration=pipulse, DelayFromZero=10000-pipulse-duration, useCalibration=False)
	pulseGenerator.sendPulse()
	time.sleep(0.5)
	acqiris.AcquireTransferV4(transferAverage=True,nLoops=30,wantedChannels=3)
	acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
	chanels= acqiris("DLLMath1Module.mean")
	amp=sqrt((chanels[0]-iOff)**2+(chanels[1]-qOff)**2)
	data.set(duration=duration,i=chanels[0],q=chanels[1],amp=amp)
	data.commit()
data.savetxt()          