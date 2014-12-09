from pyview.lib.datacube import *
from pyview.helpers.datamanager import *
from pyview.helpers.instrumentsmanager import *
instrumentManager=Manager()
dataManager=DataManager()
import math
###
acqiris=instrumentManager.getInstrument('acqiris')
cavity_drive=instrumentManager.getInstrument('MWSource_cavity')
qubit_drive=instrumentManager.getInstrument('MWSource_Qubit')
attenuator=instrumentManager.getInstrument('Yoko3')

##
print acqiris("DLLMath1Module.mathDLLVersion()")
acqiris("DLLMath1Module.meanOfLastWaveForms(15)")
print acqiris("DLLMath1Module.mean")
##
data=Datacube('riseFall')
dataManager.addDatacube(data)
acqiris.AcquireTransferV4(transferAverage=True,nLoops=50)
##
lw=acqiris.lastWave()['wave']
data=Datacube('riseFall')
dataManager.addDatacube(data)
data.createColumn('I',lw[0])
data.createColumn('Q',lw[1])
data.savetxt()
##
data=Datacube('spectroNoFridge')
dataManager.addDatacube(data)
freqs=arange(4,4.5,.001)
powers=[1.6,1.3,0.9,0.7,0]
iOff=.001
qOff=0
for power in powers:
	attenuator.setVoltage(power)
	child_power=Datacube("power=%f"%power)
	data.addChild(child_power)
	for f in freqs:
		print "f=%f"%f
		#qubit_drive.setFrequency(f)
		#time.sleep(.2)
		acqiris.AcquireTransferV4(transferAverage=True,nLoops=10,wantedChannels=3)
		acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
		chanels= acqiris("DLLMath1Module.mean")
		amp=sqrt((chanels[0]-iOff)**2+(chanels[1]-qOff)**2)
		child_power.set(f=f,i=chanels[0],q=chanels[1],amp=amp)
		child_power.commit()
data.savetxt()

## resonator scan
data=Datacube('CavitySpec1')
dataManager.addDatacube(data)
freqs=arange(7.086,7.093,0.00005)
power=1.4
attenuator.setVoltage(power)
iOff=0.0
qOff=0.0
for f in freqs:
	print "f=%f"%f
	cavity_drive.setFrequency(f)
	time.sleep(.2)
	acqiris.AcquireTransferV4(transferAverage=True,nLoops=100,wantedChannels=3)
	acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
	chanels= acqiris("DLLMath1Module.mean")
	amp=sqrt((chanels[0]-iOff)**2+(chanels[1]-qOff)**2)
	data.set(f=f,i=chanels[0],q=chanels[1],amp=amp)
	data.commit()
data.savetxt()

## qubit 
data=Datacube('QubitSpec1')
dataManager.addDatacube(data)
freqs=arange(5.42,5.6,0.0005)
power=1.87
attenuator.setVoltage(power)
iOff=0.09
qOff=0.0398
cavity_drive.setFrequency(7.09)
for f in freqs:
	print "f=%f"%f
	qubit_drive.setFrequency(f)
	time.sleep(.2)
	acqiris.AcquireTransferV4(transferAverage=True,nLoops=100,wantedChannels=3)
	acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
	chanels= acqiris("DLLMath1Module.mean")
	amp=sqrt((chanels[0]-iOff)**2+(chanels[1]-qOff)**2)
	data.set(f=f,i=chanels[0],q=chanels[1],amp=amp)
	data.commit()
data.savetxt()

## pulse spectroscopy
data=Datacube('Qubit-ge-1')
dataManager.addDatacube(data)
freqs=arange(6.39,6.41,0.001)
power=4.1
attenuator.setVoltage(power)
qubit_drive.setPower(-10)
iOff=0
qOff=0
cavity_drive.setFrequency(7.077)
for f in freqs:
	print"f=%f"%f 
	qubit_drive.setFrequency(f)
	time.sleep(.2)
	acqiris.AcquireTransferV4(transferAverage=True,nLoops=50,wantedChannels=3)
	acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
	chanels= acqiris("DLLMath1Module.mean")
	amp=sqrt((chanels[0]-iOff)**2+(chanels[1]-qOff)**2)
	data.set(f=f,i=chanels[0],q=chanels[1],amp=amp)
	data.commit()
data.savetxt()






