
import numpy
import scipy
from pyview.lib.datacube import *
from pyview.helpers.datamanager import DataManager
from pyview.helpers.instrumentsmanager import Manager
from pyview.lib.smartloop import *
dataManager = DataManager()
instrumentManager=Manager()

vna=instrumentManager.getInstrument('vna')
print vna
coil=instrumentManager.getInstrument('Yoko3')
fluxLine=instrumentManager.getInstrument('Yoko2')
mmr3_module2=Manager().getInstrument('mmr3_module2')
import math
##
data=Datacube()

##
def setMyVNAPower(power):              
	offsetVNA=-7
	power=power-offsetVNA
	if -80<=power<=0:
		atten,pow=divmod(power,-10)
		atten*=10
		if atten>60:
			atten=60
			pow=power+60
		print 'atten='+str(atten)+'dB and power='+str(pow)+'dB'
		vna.setAttenuation(atten)
		vna.setPower(pow)
	else:
		print 'target power out of range'

##
coil.setVoltage(-6.75,slewRate=0.5)
print coil.voltage()
##
cubeName='readoutVsCoil'
#yoko=fluxLine
yoko=coil
#xName='fluxLine_Voltage'
xName='coil_Voltage'
xMin,xMax,xStep=-32,32,1
slewRate=0.5

data=Datacube(cubeName)
data.toDataManager()
#currents1=arange(iMin,iMax,iStep)
#currents2=arange(iMax,iMin,-iStep)
#currents3=SmartLoop(-2.5,0.5,2.5,name="coilVoltages")
#currents=concatenate([currents1,currents2])
xList=SmartLoop(xMin,xStep,xMax,name=xName)
#coil.turnOn()
for x in xList:
	print xName," = ", x
	yoko.setVoltage(x,slewRate=slewRate)
	child1=vna.getTrace(waitFullSweep=True)
	child1.setName(xName+"=%f"%x)
	data.addChild(child1)
	#time.sleep(4)
	data.set(voltage=x,temperature=mmr3_module2.temperature(thermometerIndex=3))	
	data.commit()
data.savetxt()
#coil.setVoltage(0,slewRate=0.0005)
#####################
### demagnetizing ###
iMax=0.1
iStep=0.005
periodDegredation=0.2
loops=iMax/periodDegredation
currents=[]
for i in range(loops):
	newCurrents=arange((-1)**(i+1)*(1-i)*iMax,(-1)**i*(1-i)*iMax,(-1)**i*iStep)
	currents=concatenate([currents,newCurrents])
currents1=arange(0,iMax,iStep)
currents2=arange(iMax,-0.8*iMax,-iStep)
currents3=arange(-0.8*iMax,0.6*iMax,iStep)
currents4=arange(0.6*iMax,-0.4*iMax,-iStep)
currents5=arange(-0.4*iMax,0.2*iMax,iStep)
currents6=arange(0.2*iMax,-0.0*iMax,-iStep)
currents=concatenate([currents1,currents2,currents3,currents4,currents5,currents6])
#currents=arange(iMin,iMax,iStep)
periodStep=0.2*iMax
coil.turnOn()
for curr in currents:
	print "Current=%f"%curr
	coil.setVoltage(curr,slewRate=0.001)
coil.setVoltage(0,slewRate=0.0005)
#coil.turnOff()
############################
##
t1=time.time()
vna.getTrace(waitFullSweep=True)
t2=time.time()
print t2-t1
##
iMax=1
iStep=0.005
periodDegredation=0.2
loops=int(iMax/periodDegredation)
currents=[]
for x in np.nditer(a, op_flags=['readwrite']): 
for i in range(loops):
	newCurrents=arange((-1)**(i+1)*(1-i)*iMax,(-1)**i*(1-i)*iMax,(-1)**i*iStep)
	currents.concatenate(newCurrents)
print currents
##
currents1=arange(0,iMax,iStep)
##
iMax=1
iStep=0.005
periodDegredation=0.2
loops=int(iMax/periodDegredation)
currents=[]
for i in range(loops):
	newCurrents=arange(0,10,1)
	currents.append(newCurrents)
print currents