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
##############################
## DDROP -Pulsed- unfinished##
##############################

data=Datacube('DDROP_1')
dataManager.addDatacube(data)
cav_freq
cavity_drive.setFrequency(cav_Freq)
alpha=0.2
qb_freq
qubit_drive2.setFrequency(6.0968)
qubit_drive2.setPower(-4.7)
pipulse=120
pulseGenerator.generatePulse(frequency=qb_freq, duration=pipulse, DelayFromZero=10000-pipulse, useCalibration=False)
acqiris.AcquireTransferV4(transferAverage=True,nLoops=50,wantedChannels=3)
acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
chanels= acqiris("DLLMath1Module.mean")
amp=sqrt((chanels[0])**2+(chanels[1])**2)
data.set(f=f,i=chanels[0],q=chanels[1],amp=amp)
data.commit()

######################
## DDROP -continous ##
######################
spp=2
data=Datacube('DDROP_22')
dataManager.addDatacube(data)
cav_freq=7.0866
cavity_drive.setFrequency(cav_freq)
attenuator.setVoltage(5.1)
alpha=1.0
qb_freq=6.0968
qubit_drive2.setFrequency(6.0968)
qubit_drive2.setPower(-16)
pulses=arange(0,4001,100)
for pulse in pulses:
	print "duration=%i"%pulse
	pulseGenerator.clearPulse()
	pulseGenerator.generatePulse(frequency=qb_freq, duration=pulse/spp, DelayFromZero=10000-pulse/spp, useCalibration=False)
	pulseGenerator.sendPulse()
	pulseGenerator2.clearPulse()
	pulseGenerator2.generatePulse(frequency=qb_freq, duration=pulse/spp, DelayFromZero=10000-pulse/spp, useCalibration=False)
	pulseGenerator2.sendPulse()
	cavitypulseGenerator.clearPulse()
	cavitypulseGenerator.generatePulse(frequency=cav_freq, amplitude=alpha, duration=pulse/spp+0, DelayFromZero=10000-(pulse/spp+0), useCalibration=False)
	cavitypulseGenerator.generatePulse(frequency=cav_freq, duration=3000/spp, DelayFromZero=10000+0000/spp, useCalibration=False)
	cavitypulseGenerator.sendPulse()
	cavitySWGenerator.clearPulse()
	cavitySWGenerator.generatePulse(frequency=cav_freq, duration=pulse/spp+0, DelayFromZero=10000-(pulse/spp+0), useCalibration=False)
	cavitySWGenerator.generatePulse(frequency=cav_freq, duration=3000/spp, DelayFromZero=10000+0000/spp, useCalibration=False)
	cavitySWGenerator.sendPulse()
	acqiris.AcquireTransferV4(transferAverage=True,nLoops=50,wantedChannels=3)
	acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
	chanels= acqiris("DLLMath1Module.mean")
	amp=sqrt((chanels[0])**2+(chanels[1])**2)
	data.set(duration=pulse,i=chanels[0],q=chanels[1],amp=amp)
	data.commit()
data.savetxt()