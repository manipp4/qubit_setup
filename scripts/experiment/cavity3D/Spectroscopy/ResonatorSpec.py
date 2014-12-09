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

## Res g spec
data=Datacube('Cavityspec_9')
dataManager.addDatacube(data)
qubit_drive.turnOff()
freqs=arange(7.052,7.12,0.0003)	
power=4
attenuator.setVoltage(power)
for f in freqs:
	print"f=%f"%f 
	cavity_drive.setFrequency(f)
	time.sleep(.2)
	acqiris.AcquireTransferV4(transferAverage=True,nLoops=10,wantedChannels=3)
	acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
	chanels= acqiris("DLLMath1Module.mean")
	amp=sqrt((chanels[0])**2+(chanels[1])**2)
	data.set(f=f,i=chanels[0],q=chanels[1],amp=amp)
	data.commit()	
data.savetxt() 
	 
## Res g spec loop
data=Datacube('Cavityspec_1')
dataManager.addDatacube(data)
qubit_drive2.turnOff()
freqs=arange(7.078,7.092,0.0004)	
powers=arange(5.1,6.2,0.2)
for power in powers:
	child=Datacube('Power=%f'%power)
	data.addChild(child)
	attenuator.setVoltage(power)
	for f in freqs:
		print"f=%f"%f 
		cavity_drive.setFrequency(f)
		time.sleep(.2)
		acqiris.AcquireTransferV4(transferAverage=True,nLoops=50,wantedChannels=3)
		acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
		chanels= acqiris("DLLMath1Module.mean")
		amp=sqrt((chanels[0])**2+(chanels[1])**2)
		child.set(f=f,i=chanels[0],q=chanels[1],amp=amp)
		child.commit()
	data.set(power=power)
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
qubit_drive2.turnOff()
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
qubit_drive2.setPower(-4.7)
qubit_drive2.turnOn()
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
