from pyview.helpers.instrumentsmanager import Manager
from pyview.lib.datacube import Datacube
from pyview.lib.smartloop import SmartLoop
import numpy as np
import time
jba=Manager().getInstrument('jba_qb4')
acqiris=Manager().getInstrument('acqiris')
qb=Manager().getInstrument('qubit4')
qb._pulseGenerator._mixer._calibration._mwg=Manager().getInstrument('mwsource_qb')
acqiris=Manager().getInstrument('acqiris')
fsp=Manager().getInstrument('fsp')
########
## JBA Params
#######
jba._shapeParams['risingTime']=0
jba._shapeParams['latchLength']=700
jba._shapeParams['plateauLength']=25 
jba._shapeParams['latchLength']=2000
jba.generateShape()
jba.setAmplitude(0.45)
#########
# Calibrate power vs AWG V
#########
d=Datacube("jba power vs v")
d.toDataManager()
voltages=SmartLoop(0.2,0.005,0.8,name="Voltages")
for voltage in voltages:
	jba.setAmplitude(voltage)
	time.sleep(0.5)
	d.set(voltage=voltage)
	d.set(power=fsp.getValueAtMarker())
	d.commit()
d.savetxt()
########
## rabiMax vs repetition rate
#######
qb.clearPulses()
##
qb.setFrequency01(6.907)
qb._pulseGenerator.setCarrierFrequency(6.65)
qb.generateRabiPulseArea(area=5.5,maxHeight=1.2,offsetDelay=0,useCalibration=True,frequency=6.907,shape='gaussian')
d=Datacube("rabiMax repetition rate")
d.toDataManager()
repTimes=[21,30,40,50,60,70,80]#,50,100,200,500,1000,2000,5000]#SmartLoop(20,,name='frequencies')
for repTime in repTimes:
	jba._pulseGenerator._AWG.setTriggerInterval(repTime*1e-6)
	d.set(repTime=repTime)
	time.sleep(3)
	d.set(**qb._jba.measure(nLoops=100,fast=True)[0])
	d.commit()
d.savetxt()
jba._pulseGenerator._AWG.setTriggerInterval(20*1e-6)
##
qb._jba.measure(nLoops=100,fast=True)
###
qb.generateRabiPulseArea(area=800,maxHeight=1,offsetDelay=0,useCalibration=True,frequency=6.907,shape='gaussian')
######
##Rabi
######
qb._pulseGenerator.setCarrierFrequency(6.65)
qb.gaussianParameters={'sigma':4,'maxHeight':1,'cutOff':3}
rabiParameters={'frequency':'f01', 'nLoops':40, 'useCalibration':True,'remember':True,'maxHeight':1.2,'shape':'gaussian'}
areas=SmartLoop(0,0.5,10,name="areas")
qb.measureRabiArea(areas=areas,rabiParameters=rabiParameters)
######
##T1
######
qb._pulseGenerator.setCarrierFrequency(6.65)
d=Datacube("T1")
d.toDataManager()
durations=[0,10,20,50,100,200,500,750,1000,1500,2000,2500,3000,3500,4000,5000,6000,7000,8000,9000]
for duration in durations:
	qb.generateRabiPulseArea(area=5.4,maxHeight=1,offsetDelay=duration,useCalibration=True,frequency=6.907,shape='gaussian')
	d.set(duration=duration)
	time.sleep(0.2)
	d.set(**qb._jba.measure(nLoops=100,fast=True)[0])
	d.commit()
######
##T1 - 2
######
qb._pulseGenerator.setCarrierFrequency(6.65)
d=Datacube("T1")
d.toDataManager()
durations=[20,50,100,200,500,750,1000,1500,2000,2500,3000,3500,4000,5000,6000,7000,8000,9000]
for duration in durations:
	qb.generateRabiPulseArea(area=5.4,maxHeight=1,offsetDelay=duration+8,useCalibration=True,frequency=6.907,shape='gaussian')
	qb.generateRabiPulseArea(area=4.4,maxHeight=1.2,offsetDelay=duration,useCalibration=True,frequency=f12,shape='gaussian',clear=False)
	d.set(duration=duration)
	time.sleep(0.2)
	d.set(**qb._jba.measure(nLoops=100,fast=True)[0])
	d.commit()
d.savetxt()
#####
## f01 with power
#####
qb.setFrequency01(6.907)
qb._pulseGenerator.setCarrierFrequency(6.907)
qb.generateRabiPulseArea(area=5.4,maxHeight=1,offsetDelay=0,useCalibration=True,frequency=6.907,shape='gaussian')
d=Datacube("rabi vs freq 5.4nsV")
d.toDataManager()
frequencies=SmartLoop(6.895,0.0005,6.925,name='frequencies')
for frequency in frequencies:
	qb._pulseGenerator.setCarrierFrequency(frequency)
	d.set(frequency=frequency)
	time.sleep(0.1)
	d.set(**qb._jba.measure(nLoops=40,fast=True)[0])
	d.commit()
#####
## f01 with power SB
#####
jba.setAmplitude(0.37)
qb._pulseGenerator.setCarrierFrequency(6.65)
d=Datacube("rabi vs freq 60nsV")
d.toDataManager()
frequencies=SmartLoop(6.48,0.001,6.55,name='frequencies')
for frequency in frequencies:
	qb.generateRabiPulseArea(area=60,maxHeight=1.2,offsetDelay=0,useCalibration=True,frequency=frequency,shape='gaussian')
	d.set(frequency=frequency)
	time.sleep(0.1)
	d.set(**qb._jba.measure(nLoops=20,fast=True)[0])
	d.commit()

######
##Scurves
######
qb.clearPulses()
##
f12=6.48
start=0.4
step=0.005
stop=0.75
nLoops=20
area1=5.8
area2=4.4
##
qb.generateRabiPulseArea(area=area1,maxHeight=1.2,offsetDelay=0,useCalibration=True,shape='gaussian')
time.sleep(1)
qb._jba.measureSCurve(voltages=SmartLoop(start,step,stop,name="Voltages"),nLoops=nLoops) # 1 simple rabi
qb.generateRabiPulseArea(area=area1,maxHeight=1.2,offsetDelay=area1+8,useCalibration=True,shape='gaussian')
qb.generateRabiPulseArea(area=area2,maxHeight=1.2,offsetDelay=0,useCalibration=True,frequency=f12,shape='gaussian',clear=False)
time.sleep(1)
qb._jba.measureSCurve(voltages=SmartLoop(start,step,stop,name="Voltages"),nLoops=nLoops) # 1 + 2 (simple rabis)
qb.generateRabiPulseArea(area=area2,maxHeight=1.2,offsetDelay=0,useCalibration=True,frequency=f12,shape='gaussian')
time.sleep(1)
qb._jba.measureSCurve(voltages=SmartLoop(start,step,stop,name="Voltages"),nLoops=nLoops) # 2 simple rabi

##
qb.clearPulses()
qb._jba.measureSCurve(voltages=SmartLoop(start,step,stop,name="Voltages"),nLoops=nLoops) # OFF
qb.generateRabiPulseArea(area=area1,maxHeight=1.2,offsetDelay=0,useCalibration=True,shape='gaussian')
time.sleep(1)
qb._jba.measureSCurve(voltages=SmartLoop(start,step,stop,name="Voltages"),nLoops=nLoops) # 1 simple rabi
qb.generateRabiPulseArea(area=area,maxHeight=0.6,offsetDelay=0,useCalibration=True,shape='gaussian',clear=True)
qb.generateRabiPulseAreaDerivative(area=area,maxHeight=0.6,offsetDelay=0,useCalibration=True,shape='gaussian',clear=False,phase=-math.pi/2,coefficient=coef)
time.sleep(1)
qb._jba.measureSCurve(voltages=SmartLoop(start,step,stop,name="Voltages"),nLoops=nLoops) # DRAG

#####
## f12 with power SB
#####
jba.setAmplitude(0.37)
qb._pulseGenerator.setCarrierFrequency(6.65)
d=Datacube("f12 vs freq 4.4nsV")
d.toDataManager()
frequencies=SmartLoop(6.465,0.002,6.6,name='frequencies')
for frequency in frequencies:
	l=4.2
	qb.generateRabiPulseArea(area=5.6,maxHeight=1.2,offsetDelay=l+8,useCalibration=True,frequency=f01,shape='gaussian')
	qb.generateRabiPulseArea(area=l,maxHeight=1.2,offsetDelay=0,useCalibration=True,frequency=frequency,shape='gaussian',clear=False)
	d.set(frequency=frequency)
	time.sleep(0.1)
	d.set(**qb._jba.measure(nLoops=5,fast=True)[0])
	d.commit()

######
##Rabi 12
######
jba.setAmplitude(0.47)
qb._pulseGenerator.setCarrierFrequency(6.65)
f01=6.907
f12=6.49
d=Datacube("Rabi 12")
d.toDataManager()
areas=SmartLoop(0,0.2,40,name='areas12')
for area in areas:
	qb.generateRabiPulseArea(area=5.6,maxHeight=1.2,offsetDelay=area+8,useCalibration=True,frequency=f01,shape='gaussian')
	qb.generateRabiPulseArea(area=area,maxHeight=1.2,offsetDelay=0,useCalibration=True,frequency=f12,shape='gaussian',clear=False)
	d.set(area12=area)
	time.sleep(0.3)
	d.set(**qb._jba.measure(nLoops=20,fast=True)[0])
	d.commit()
######
## rabi 01 +2
####
area2=4.4
jba.setAmplitude(0.43)
qb._pulseGenerator.setCarrierFrequency(6.65)
f01=6.907
f12=6.49
d=Datacube("Rabi 12")
d.toDataManager()
areas=SmartLoop(0,0.2,40,name='areas12')
for area in areas:
	qb.generateRabiPulseArea(area=area,maxHeight=1.2,offsetDelay=area2+8,useCalibration=True,frequency=f01,shape='gaussian')
	qb.generateRabiPulseArea(area=area2,maxHeight=1.2,offsetDelay=0,useCalibration=True,frequency=f12,shape='gaussian',clear=False)
	d.set(area=area)
	time.sleep(0.3)
	d.set(**qb._jba.measure(nLoops=40,fast=True)[0])
	d.commit()
d.savetxt()
##############
## test arbitrary rotations
##############
qb.setRabiArea(5.6)
import math
d=Datacube("mag vs angle")
d.toDataManager()
angles=SmartLoop(0,20,360, name="angles")
for angle in angles:
	qb.generateRotation(math.pi/2,0,0,clear=True)
	qb.generateRotation(math.pi/2,angle*math.pi/180,60,clear=False)
	d.set(angle=angle)
	time.sleep(0.3)
	d.set(**qb._jba.measure(nLoops=10,fast=True)[0])
	d.commit()
d.savetxt()
#############
## measure leakage to 2 with phase 
#############
qb.setRabiArea(5.2)
qb.setFrequency01(6.877+0.021712)
##
qb.setRabiArea(5.5)
qb.setFrequency01(6.907)
##
import math
d=Datacube("mag vs angle")
d.toDataManager()
angles=SmartLoop(0,20,360, name="angles")
for angle in angles:
	d.set(angle=angle)
	for i in [0,1,2,3,4]:
		qb.generateRotation(math.pi/2,0,0,clear=True)
		qb.generateRotation(math.pi/2,angle*math.pi/180,20+50*4,clear=False)
		for j in range(0,i):
			offsetI=20+j*50
			for k in [0,1]:
				offsetK=offsetI+k*25
				qb.generateRotation(math.pi,0,offsetK,clear=False)
		time.sleep(0.3)
		b={'n%i'%i:qb._jba.measure(nLoops=10,fast=True)[0]['b3']}
		d.set(**b)
	d.commit()
d.savetxt()
####
#############
## measure leakage to 2 
#############
qb.setRabiArea(5.5)
qb.setFrequency01(6.907)
d=Datacube("mag vs delay")
d.toDataManager()
delays=SmartLoop(0,1,100,name="delays")
for delay in delays:
	d.set(delay=delay)
	qb.generateRotation(math.pi,0,0,clear=True)
	qb.generateRotation(math.pi,0,20+delay,clear=False)
	time.sleep(0.3)
	d.set(**qb._jba.measure(nLoops=10,fast=True)[0])
	d.commit()
d.savetxt()
####
qb.clearPulses()
for i in [0]:
	qb.generateRotation(math.pi/2,0,20*i,clear=False)
##
	


##############
## Ramsey
#############
d=Datacube("Ramsey")
d.toDataManager()
delays=SmartLoop(0,2,500, name="delays")
for delay in delays:
	qb.generateRotation(math.pi/2,0,0,clear=True, frequency=qb.frequency01()-0.03)
	qb.generateRotation(math.pi/2,0,delay+20,clear=False, frequency=qb.frequency01()-0.03)
	d.set(delay=delay)
	time.sleep(0.3)
	d.set(**qb._jba.measure(nLoops=10,fast=True)[0])
	d.commit()
d.savetxt()
###
qb.setFrequency01(6.877-0.03+0.057252)
print qb.frequency01()
########
## tomo Rabi
########
qb.setRabiArea(5.4)
qb._pulseGenerator.setCarrierFrequency(6.65)
d=Datacube("rabi")
d.toDataManager()
nLoops=10
areas=SmartLoop(0,0.2,20,name="durations")
for area in areas:
	qb.generateRotation(0,0,0,clear=True)
	qb.generateRabiPulseArea(area=area,maxHeight=0.6,offsetDelay=20,useCalibration=True,shape='gaussian',clear=False)
	d.set(areaR=area)
	time.sleep(0.2)
	d.set(sigmaZ=-1+2*qb._jba.measure(nLoops=nLoops,fast=True)[0]['b3'])
	qb.generateRotation(math.pi/2,0,0,clear=True)
	qb.generateRabiPulseArea(area=area,maxHeight=0.6,offsetDelay=20,useCalibration=True,shape='gaussian',clear=False)
	time.sleep(0.2)
	d.set(sigmaX=-1+2*qb._jba.measure(nLoops=nLoops,fast=True)[0]['b3'])
	qb.generateRotation(math.pi/2,math.pi/2,0,clear=True)
	qb.generateRabiPulseArea(area=area,maxHeight=0.6,offsetDelay=20,useCalibration=True,shape='gaussian',clear=False)
	time.sleep(0.2)
	d.set(sigmaY=-1+2*qb._jba.measure(nLoops=nLoops,fast=True)[0]['b3'])
	d.commit()
d.savetxt()
########
## tomo Rabi + HD
########
coef=0.05
qb.setRabiArea(5.4)
qb._pulseGenerator.setCarrierFrequency(6.65)
d=Datacube("rabi")
d.toDataManager()
nLoops=40
areas=SmartLoop(0,0.2,20,name="durations")
for area in areas:
	qb.generateRotation(0,0,0,clear=True)
	qb.generateRabiPulseArea(area=area,maxHeight=0.6,offsetDelay=20,useCalibration=True,shape='gaussian',clear=False)
	qb.generateRabiPulseAreaDerivative(area=area,maxHeight=0.6,offsetDelay=20,useCalibration=True,shape='gaussian',clear=False,phase=math.pi/2,coefficient=coef)
	d.set(areaR=area)
	time.sleep(0.2)
	d.set(sigmaZ=-1+2*qb._jba.measure(nLoops=nLoops,fast=True)[0]['b3'])
	qb.generateRotation(math.pi/2,0,0,clear=True)
	qb.generateRabiPulseArea(area=area,maxHeight=0.6,offsetDelay=20,useCalibration=True,shape='gaussian',clear=False)
	qb.generateRabiPulseAreaDerivative(area=area,maxHeight=0.6,offsetDelay=20,useCalibration=True,shape='gaussian',clear=False,phase=math.pi/2,coefficient=coef)
	time.sleep(0.2)
	d.set(sigmaX=-1+2*qb._jba.measure(nLoops=nLoops,fast=True)[0]['b3'])
	qb.generateRotation(math.pi/2,math.pi/2,0,clear=True)
	qb.generateRabiPulseArea(area=area,maxHeight=0.6,offsetDelay=20,useCalibration=True,shape='gaussian',clear=False)
	qb.generateRabiPulseAreaDerivative(area=area,maxHeight=0.6,offsetDelay=20,useCalibration=True,shape='gaussian',clear=False,phase=math.pi/2,coefficient=coef)
	time.sleep(0.2)
	d.set(sigmaY=-1+2*qb._jba.measure(nLoops=nLoops,fast=True)[0]['b3'])
	d.commit()
d.savetxt()
########
## Rabi + HD
########
import math
qb.clearPulses()
##
qb.setFrequency01(6.902159+0.013)
qb.setRabiArea(5.4)
qb._pulseGenerator.setCarrierFrequency(6.65)
d=Datacube("rabi")
d.toDataManager()
nLoops=20
areas=SmartLoop(0,0.2,20,name="durations")
for area in areas:
	qb.generateRabiPulseArea(area=area,maxHeight=0.6,offsetDelay=0,useCalibration=True,shape='gaussian',clear=True)
	qb.generateRabiPulseAreaDerivative(area=area,maxHeight=0.6,offsetDelay=0,useCalibration=True,shape='gaussian',clear=False,phase=-math.pi/2,coefficient=0.05)
	d.set(areaR=area)
	time.sleep(0.2)
	d.set(**qb._jba.measure(nLoops=nLoops,fast=True)[0])
	d.commit()
d.savetxt()
########
## Rabi + drag
########

import math
qb.clearPulses()
d=Datacube("rabi")
d.toDataManager()
nLoops=40
coef=0.03
areas=SmartLoop(5,0.1,20,name="durations")
for area in areas:
	qb.generateRabiPulseArea(area=area,maxHeight=0.6,offsetDelay=0,useCalibration=True,shape='gaussian',clear=True)
	qb.generateRabiPulseAreaDerivative(area=area,maxHeight=0.6,offsetDelay=0,useCalibration=True,shape='gaussian',clear=False,phase=-math.pi/2,coefficient=coef)
	d.set(areaR=area)
	time.sleep(0.2)
	d.set(**qb._jba.measure(nLoops=nLoops,fast=True)[0])
	d.commit()
d.savetxt()
########
## HD coef ?
########
qb.clearPulses()
##

qb.setFrequency01(6.9127)
qb.setRabiArea(5.5)
qb._pulseGenerator.setCarrierFrequency(6.65)
d=Datacube("rabi")
d.toDataManager()
nLoops=40
area=5.5
coefs=SmartLoop(-0.00,0.002,0.09,name="durations")
for coef in coefs:
	qb.generateRabiPulseArea(area=area,maxHeight=0.6,offsetDelay=0,useCalibration=True,shape='gaussian',clear=True)
	qb.generateRabiPulseAreaDerivative(area=area,maxHeight=0.6,offsetDelay=0,useCalibration=True,shape='gaussian',clear=False,phase=-math.pi/2,coefficient=coef)
	d.set(coef=coef)
	time.sleep(0.2)
	d.set(**qb._jba.measure(nLoops=nLoops,fast=True)[0])
	d.commit()
d.savetxt()
########
## drag frequency with coef from HD
########
qb.setFrequency01(6.9138)

##
qb.clearPulses()
qb._pulseGenerator.setCarrierFrequency(6.65)
d=Datacube("rabi")
d.toDataManager()
nLoops=20
area=5.5
coef=0.03
frequencyOffsets=SmartLoop(-0.005,0.0005,0.005,name="frequency offset")
for frequencyOffset in frequencyOffsets:
	qb.generateRabiPulseArea(area=area,maxHeight=0.6,offsetDelay=0,useCalibration=True,shape='gaussian',clear=True,frequency=qb.frequency01()+frequencyOffset)
	qb.generateRabiPulseAreaDerivative(area=area,maxHeight=0.6,offsetDelay=0,useCalibration=True,shape='gaussian',clear=False,phase=-math.pi/2,coefficient=coef,frequency=qb.frequency01()+frequencyOffset)
	time.sleep(0.2)
	d.set(**qb._jba.measure(nLoops=nLoops,fast=True)[0])
	d.set(frequency=qb.frequency01()+frequencyOffset)
	d.commit()
d.savetxt()
########
## tomo Rabi + DRAG
########
print qb.frequency01()
qb.setFrequency01(6.912779)
##
qb.setDragCoef(0.03)


coef=0.03
qb.setRabiArea(5.5)
qb._pulseGenerator.setCarrierFrequency(6.65)
d=Datacube("rabi")
d.toDataManager()
nLoops=20
areas=SmartLoop(0,0.05,20,name="durations")
for area in areas:
	qb.generateRotation(0,0,0,clear=True)
	qb.generateRabiPulseArea(area=area,maxHeight=0.6,offsetDelay=20,useCalibration=True,shape='gaussian',clear=False,frequency=qb.frequency01())
	qb.generateRabiPulseAreaDerivative(area=area,maxHeight=0.6,offsetDelay=20,useCalibration=True,shape='gaussian',clear=False,phase=-math.pi/2,coefficient=coef,frequency=qb.frequency01())
	d.set(areaR=area)
	time.sleep(0.2)
	d.set(sigmaZ=-1+2*qb._jba.measure(nLoops=nLoops,fast=True)[0]['b3'])
	qb.generateRotation(math.pi/2,0,0,clear=True)
	qb.generateRabiPulseArea(area=area,maxHeight=0.6,offsetDelay=20,useCalibration=True,shape='gaussian',clear=False,frequency=qb.frequency01())
	qb.generateRabiPulseAreaDerivative(area=area,maxHeight=0.6,offsetDelay=20,useCalibration=True,shape='gaussian',clear=False,phase=-math.pi/2,coefficient=coef,frequency=qb.frequency01())
	time.sleep(0.2)
	d.set(sigmaX=-1+2*qb._jba.measure(nLoops=nLoops,fast=True)[0]['b3'])
	qb.generateRotation(math.pi/2,math.pi/2,0,clear=True)
	qb.generateRabiPulseArea(area=area,maxHeight=0.6,offsetDelay=20,useCalibration=True,shape='gaussian',clear=False,frequency=qb.frequency01())
	qb.generateRabiPulseAreaDerivative(area=area,maxHeight=0.6,offsetDelay=20,useCalibration=True,shape='gaussian',clear=False,phase=-math.pi/2,coefficient=coef,frequency=qb.frequency01())
	time.sleep(0.2)
	d.set(sigmaY=-1+2*qb._jba.measure(nLoops=nLoops,fast=True)[0]['b3'])
	d.commit()
d.savetxt()

##
qb.clearPulses()
##
gv.d.createColumn("areaR",d['area'])
gv.d.createColumn("sigmaX",d['x'])
gv.d.createColumn("sigmaY",d['y'])
gv.d.createColumn("sigmaZ",d['z'])
##
d.removeColumn('area')
d.removeColumn('x')
d.removeColumn('y')
d.removeColumn('z')
##

qb.generateRabiPulseArea(area=area,maxHeight=0.6,offsetDelay=20,useCalibration=True,shape='gaussian',clear=True)
qb.generateRabiPulseAreaDerivative(area=area,maxHeight=0.6,offsetDelay=20,useCalibration=True,shape='gaussian',clear=False,phase=math.pi/2,coefficient=2.5)
##
import numpy
d=Datacube("waveform")
d.toDataManager()
wf=numpy.zeros(20000,dtype=numpy.complex128)
for pulse in qb._pulseGenerator.pulseList:
	wf[:]+=pulse._pulseArray[:]*numpy.exp(1.j*pulse.phase)
d.createColumn("Re",numpy.real(wf))
d.createColumn("Im",numpy.imag(wf))




####



##

print qb._jba.measure(nLoops=40,fast=True)[0]

##
print qb._pulseGenerator.pulseList

##
qb.gaussianParameters={'sigma':1,'maxHeight':1,'cutOff':3}
areas=SmartLoop(3,0.2,20,name='areas')
for area in areas:
	qb.generateRabiPulseArea(area=area,shape='gaussian')
##
spectroscopyParameters={'useCalibration':False,'nLoops':1,'duration':2000,'amplitude':0.2}
frequencies=SmartLoop(6.6,0.001,7.3,name='frequencies')
qb.measureSpectroscopy(frequencies=frequencies,spectroscopyParameters=spectroscopyParameters)
##
print qb._pulseGenerator
##
import sys
import time
from macros.generatorFunctionLib import *
reload(sys.modules['macros.generatorFunctionLib'])
from macros.generatorFunctionLib import *

sigma=1.
cutOff=3
end=10000-20
center=None
area=4.2
maxHeight=1.
areas=SmartLoop(0,0.2,30,name='areas')

for area in areas:
	d.createColumn('I',gaussianSlopePulse(20000,1, sigma=sigma, cutOff=cutOff, end=end, center=center, area=area, maxHeight=maxHeight)[9900:10000])
	d.createColumn('P',gaussianSquarePulseHeight(20000,1,9950,area,sigma=sigma,cutOff=cutOff,height=1.)[9900:10000])
	time.sleep(0.2)

##
from macros.generatorFunctionLib import *
reload(sys.modules['macros.generatorFunctionLib'])
from macros.generatorFunctionLib import *



d.createColumn('P',gaussianSquarePulseHeight(20000,1,9961.2,7.5,sigma=sigma,cutOff=cutOff,height=1.)[9900:10000])
##
from macros.generatorFunctionLib import *
reload(sys.modules['macros.generatorFunctionLib'])
from macros.generatorFunctionLib import *
print gaussianSquarePulseHeight(20000,1,9961,7.5,sigma=sigma,cutOff=cutOff,height=1.)

##
m=Manager().getInstrument('iqmixer_qb')
print dir(m._calibration.sidebandCalibrationData().toDataManager())

#####

gv.d.createColumn('a',gv.d['area'])
gv.d.removeColumn('area')

