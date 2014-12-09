from pyview.lib.datacube import *
from pyview.helpers.datamanager import *
from pyview.helpers.instrumentsmanager import *
instrumentManager=Manager()
dataManager=DataManager()
import math
temperature=instrumentManager.getInstrument('temperature')

print temperature.temperature()

##
acqiris=instrumentManager.getInstrument('acqiris')
cavity_drive=instrumentManager.getInstrument('MWSource_cavity')
qubit_drive=instrumentManager.getInstrument('MWSource_Qubit')
qubit_drive2=instrumentManager.getInstrument('MWSource_Qubit2')
attenuator=instrumentManager.getInstrument('Yoko3')
pulseGenerator=instrumentManager.getInstrument('pg_qb')  
fsp=instrumentManager.getInstrument('fsp') 
Coil=instrumentManager.getInstrument('Keithley2400')
##

def telegraph(x0,x):
	if (x<x0):
		y=0
	else: y=1
	return y
##
def switchingProb(nSegments=1000,channel=1,threshold="auto"):
	wantedChannel=2**(channel-1)
	segmentsPerAcq=acqiris("_params['numberOfSegments']")
	nLoops=nSegments/segmentsPerAcq
	acqiris.AcquireTransferV4(transferAverage=False,nLoops=nLoops,wantedChannels=wantedChannel)
	acqiris("DLLMath1Module.meanOfLastWaveForms("+str(wantedChannel)+")")
	acqiris("DLLMath1Module.aboveThresholdFrequencyProperty(propertyArray='mean',targettedWaveform="+str(wantedChannel)+",threshold="+str(threshold)+")")
	return acqiris("DLLMath1Module.aboveThresholdFrequencyArray["+str(channel-1)+"]")
    
## HPR g
data=Datacube('CavityResponse_g1')
dataManager.addDatacube(data)
frequency=7.0795
cavity_drive.setFrequency(frequency)
VVAs=arange(1,5,0.1)
qubit_drive2.turnOff()
#pulseGenerator.clearPulse()
#power=fsp.getValueAtMarker()
probReadout=False
threshold=0.05
iOff=0
qOff=0
for VVA in reversed(VVAs):
	print"VVAVoltage=%f"%VVA
	attenuator.setVoltage(VVA)
	time.sleep(0.5)
	if probReadout==False:
		acqiris.AcquireTransferV4(transferAverage=True,nLoops=10,wantedChannels=3)
		acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
		chanels= acqiris("DLLMath1Module.mean")
		amp=sqrt((chanels[0]-iOff)**2+(chanels[1]-qOff)**2)
		data.set(VVA=VVA,i=chanels[0],q=chanels[1],amp=amp)
		data.commit()
	else:
		prob_e=switchingProb(channel=2,nSegments=10000,threshold=threshold)
		data.set(VVA=VVA,prob_e=prob_e)	
		data.commit()
data.savetxt()

## HPR g Loop
data=Datacube('CavityResponse_Loop_g9_inv')
dataManager.addDatacube(data)
frequency=7.07885
cavity_drive.setFrequency(frequency)
VVAs=arange(1.4,2.0,0.02)
qubit_drive.turnOff()
pulseGenerator.clearPulse()
probReadout=True
threshold=0.2
indexes=arange(0,100,1)
for index in indexes:
	child=Datacube("i%i"%index)
	data.addChild(child)
	for VVA in (VVAs):
		print"VVAVoltage=%f"%VVA
		attenuator.setVoltage(VVA)
		time.sleep(0.5)
		if probReadout==False:
			acqiris.AcquireTransferV4(transferAverage=True,nLoops=10,wantedChannels=3)
			acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
			chanels= acqiris("DLLMath1Module.mean")
			amp=sqrt((chanels[0]-iOff)**2+(chanels[1]-qOff)**2)
			child.set(VVA=VVA,i=chanels[0],q=chanels[1],amp=amp)
			child.commit()
		else:
			prob_e=switchingProb(channel=2,nSegments=1000,threshold=threshold)
			power=fsp.getValueAtMarker()
			child.set(VVA=VVA,prob_e=prob_e,power=power)	
			child.commit()
	data.savetxt()		

## HPR g fixed VVA
data=Datacube('CavityResponse_g1_fixed')
dataManager.addDatacube(data)
frequency=7.07885
cavity_drive.setFrequency(frequency)
VVA=1.67
qubit_drive.turnOff()
pulseGenerator.clearPulse()
probReadout=True
threshold=0.1
indexes=arange(0,10000,1)
attenuator.setVoltage(VVA)
time.sleep(0.5)
for index in indexes:
	print index
	prob_e=switchingProb(channel=2,nSegments=500,threshold=threshold)
	power=fsp.getValueAtMarker()
	data.set(index=index,VVA=VVA,prob_e=prob_e,power=power)	
	data.commit()
	data.savetxt()		

## HPR e
data=Datacube('CavityResponse_e1')
dataManager.addDatacube(data)
qubit_drive2.turnOn()
qbfrequency=6.0968
qubit_drive2.setPower(-4.7)
pipulse=120
pulseGenerator.clearPulse()
pulseGenerator.generatePulse(frequency=qbfrequency, duration=pipulse, DelayFromZero=10000-pipulse, useCalibration=False)
pulseGenerator.sendPulse()
frequency=7.07885
cavity_drive.setFrequency(frequency)
VVAs=arange(1.3,2.2,0.01)
probReadout=True
threshold=0.3
for VVA in reversed(VVAs):
	print"VVAVoltage=%f"%VVA
	attenuator.setVoltage(VVA)
	time.sleep(0.5)
	if probReadout==False:
		acqiris.AcquireTransferV4(transferAverage=True,nLoops=10,wantedChannels=3)
		acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
		chanels= acqiris("DLLMath1Module.mean")
		amp=sqrt((chanels[0]-iOff)**2+(chanels[1]-qOff)**2)
		data.set(VVA=VVA,i=chanels[0],q=chanels[1],amp=amp)
		data.commit()
	else:
		acqiris.AcquireTransferV4(transferAverage=False,nLoops=10,wantedChannels=3)
		acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
		chanels= acqiris("DLLMath1Module.mean")
		Q=chanels[1]
		#amp=sqrt((chanels[0]-iOff)**2+(chanels[1]-qOff)**2)
		events=map(lambda x:telegraph(threshold,x),Q)
		prob_e=mean(events)
		data.set(VVA=VVA,prob_e=prob_e)	
		data.commit()
data.savetxt()
## HPR 2D g
data=Datacube('CavityResponse2D_g4')
dataManager.addDatacube(data)
frequencys=arange(7.078,7.078,0.01)
cavity_drive.setFrequency(frequency)
VVAs=arange(1.6,2.2,0.01)
qubit_drive.turnOff()
pulseGenerator.clearPulse()
#power=fsp.getValueAtMarker()
iOff=0
qOff=0
for VVA in reversed(VVAs):
	print"VVAVoltage=%f"%VVA
	attenuator.setVoltage(VVA)
	time.sleep(0.5)
	acqiris.AcquireTransferV4(transferAverage=True,nLoops=10,wantedChannels=3)
	acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
	chanels= acqiris("DLLMath1Module.mean")
	amp=sqrt((chanels[0]-iOff)**2+(chanels[1]-qOff)**2)
	data.set(VVA=VVA,i=chanels[0],q=chanels[1],amp=amp)
	data.commit()
data.savetxt()



## noise look
data=Datacube('Noise')
dataManager.addDatacube(data)
freqs=arange(4.4,6.9,0.001)
indexes=arange(0,5,1)
power=1
attenuator.setVoltage(power)
qubit_drive.setPower(0)
iOff=0
qOff=0
cavity_drive.setFrequency(7.08282)
for f in reversed(freqs):
	print"f=%f"%f 
	qubit_drive.setFrequency(f)
	time.sleep(.2)
	acqiris.AcquireTransferV4(transferAverage=True,nLoops=5,wantedChannels=3)
	acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
	chanels= acqiris("DLLMath1Module.mean")
	amp=sqrt((chanels[0]-iOff)**2+(chanels[1]-qOff)**2)
	data.set(f=f,i=chanels[0],q=chanels[1],amp=amp)
	data.commit()
data.savetxt()
	
## HPR g switching proba

data=Datacube('Cavityswitching_g1')
dataManager.addDatacube(data)
frequency=7.07885
cavity_drive.setFrequency(frequency)
VVA=1.4
qubit_drive.turnOff()
pulseGenerator.clearPulse()
iOff=0
qOff=0

for index in range(0,100):
	print"VVAVoltage=%f"%VVA
	attenuator.setVoltage(VVA)
	time.sleep(0.5)
	acqiris.AcquireTransferV4(transferAverage=False,nLoops=1,wantedChannels=3)
	acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
	chanels= acqiris("DLLMath1Module.mean")
	amp=sqrt((chanels[0]-iOff)**2+(chanels[1]-qOff)**2)
	events=map(lambda x:telegraph(0.08,x),amp)
	l=len(events)
	mean1=mean(events)
	data.setColumn("i",chanels[0])
	data.setColumn("q",chanels[1])
	data.setColumn("amp",amp)
	data.setColumn("events",events)
	
	data.savetxt()
	print"mean1=%f"%mean1

## HPR e switching proba

data=Datacube('Cavityswitching_e1')
dataManager.addDatacube(data)
frequency=7.07885
cavity_drive.setFrequency(frequency)
VVA=1.4
qubit_drive.turnOn()
qbfrequency=6.0968
qubit_drive.setPower(-4)
pipulse=52
pulseGenerator.clearPulse()
pulseGenerator.generatePulse(frequency=qbfrequency, duration=pipulse, DelayFromZero=10000-pipulse, useCalibration=False)
pulseGenerator.sendPulse()
iOff=0
qOff=0

for index in range(0,10):
	print"VVAVoltage=%f"%VVA
	attenuator.setVoltage(VVA)
	time.sleep(0.5)
	acqiris.AcquireTransferV4(transferAverage=False,nLoops=10,wantedChannels=3)
	acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
	chanels= acqiris("DLLMath1Module.mean")
	amp=sqrt((chanels[0]-iOff)**2+(chanels[1]-qOff)**2)
	events=map(lambda x:telegraph(0.04,x),amp)
	l=len(events)
	mean1=mean(events)
	data.setColumn("i",chanels[0])
	data.setColumn("q",chanels[1])
	data.setColumn("amp",amp)
	data.setColumn("events",events)
	
	data.savetxt()
	print"mean1=%f"%mean1



