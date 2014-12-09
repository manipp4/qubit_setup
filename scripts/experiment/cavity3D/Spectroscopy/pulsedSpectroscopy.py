from pyview.lib.datacube import *
from pyview.lib.smartloop import *
from pyview.helpers.datamanager import *
from pyview.helpers.instrumentsmanager import *
instrumentManager=Manager()
dataManager=DataManager()
import math

##
acqiris=instrumentManager.getInstrument('acqiris')
cavity_drive=instrumentManager.getInstrument('MWSource_cavity')
qubit_drive=instrumentManager.getInstrument('MWSource_Qubit')
qubit_drive2=instrumentManager.getInstrument('MWSource_Qubit2')
attenuator=instrumentManager.getInstrument('Yoko3')
pulseGenerator=instrumentManager.getInstrument('pg_qb')  
fsp=instrumentManager.getInstrument('fsp') 

## continous spectroscopy 1 tone FOR A SIMPLE SETUP
data=Datacube('ContSpec-res-5')
dataManager.addDatacube(data)
freqs=arange(7.07,7.085,0.0005)
power=1
attenuator.setVoltage(power)
for f in reversed(freqs):
	print"f=%f"%f 
	cavity_drive.setFrequency(f)
	time.sleep(.2)
	acqiris.AcquireTransferV4(transferAverage=True,nLoops=100,wantedChannels=3)
	acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
	chanels= acqiris("DLLMath1Module.mean")
	amp=sqrt((chanels[0])**2+(chanels[1])**2)
	data.set(f=f,i=chanels[0],q=chanels[1],amp=amp)
	data.commit()
data.savetxt()

## continous spectroscopy 2 tone FOR A SIMPLE SETUP
data=Datacube('ContSpec-ge-6')
dataManager.addDatacube(data)
freqs=arange(2.5,3,0.005)
power=3
attenuator.setVoltage(power)
qubit_drive.setPower(-20)
qubit_drive.turnOn()
cavity_drive.setFrequency(7.0844)
for f in reversed(freqs):
	print"f=%f"%f 
	qubit_drive.setFrequency(f)
	time.sleep(.2)
	acqiris.AcquireTransferV4(transferAverage=True,nLoops=50,wantedChannels=3)
	acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
	chanels= acqiris("DLLMath1Module.mean")
	amp=sqrt((chanels[0])**2+(chanels[1])**2)
	data.set(f=f,i=chanels[0],q=chanels[1],amp=amp)
	data.commit()
data.savetxt()


## pulse spectroscopy
data=Datacube('Qubit-ge-20')
dataManager.addDatacube(data)
freqs=SmartLoop(7.25,0.001,7.65)#arange(6.2,6.8,0.001)
power=4
attenuator.setVoltage(power)
qubit_drive.setPower(-20)
qubit_drive.turnOn()
cavity_drive.setFrequency(7.0579)
for f in freqs:
	print"f=%f"%f 
	qubit_drive.setFrequency(f)
	time.sleep(.2)
	acqiris.AcquireTransferV4(transferAverage=True,nLoops=10,wantedChannels=3)
	acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
	chanels= acqiris("DLLMath1Module.mean")
	amp=sqrt((chanels[0])**2+(chanels[1])**2)
	phase=arctan(chanels[0]/chanels[1])
	data.set(f=f,i=chanels[0],q=chanels[1],amp=amp,phase=phase)
	data.commit()
data.savetxt()

## pulse spectroscopy gf2
data=Datacube('Qubit-gf2-1')
dataManager.addDatacube(data)
freqs=arange(5.9,6,0.0002)
power=1.9
attenuator.setVoltage(power)
qubit_drive.setPower(-10)
qubit_drive.turnOn()
cavity_drive.setFrequency(7.07885)
for f in reversed(freqs):
	print"f=%f"%f 
	qubit_drive.setFrequency(f)
	time.sleep(.2)
	acqiris.AcquireTransferV4(transferAverage=True,nLoops=5,wantedChannels=3)
	acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
	chanels= acqiris("DLLMath1Module.mean")
	amp=sqrt((chanels[0])**2+(chanels[1])**2)
	data.set(f=f,i=chanels[0],q=chanels[1],amp=amp)
	data.commit()
data.savetxt()