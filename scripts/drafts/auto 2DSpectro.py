##2D Spectro
from config.instruments import *
from pyview.lib.datacube import *
import numpy
reload(sys.modules["pyview.helpers.instrumentsmanager"])
from pyview.helpers.instrumentsmanager import *
import scipy
from pyview.helpers.datamanager import *
from pyview.helpers.datamanager import DataManager
dataManager = DataManager()
instrumentManager=Manager()
##
qb=instrumentManager.getInstrument('qubit1')
coil=instrumentManager.getInstrument('coil')
acqiris=instrumentManager.getInstrument('acqiris')
print qb,coil,acqiris
##
data=Datacube("JBA 6.91")
dataManager.addDatacube(data)
vi=0
#
###
frequencies=[8.2,8.7]
#
voltages=arange(-1.,-0.5,0.05)
#voltages=[0.2]
for v in voltages:
	coil.setVoltage(v,slewRate=0.1)
	acqiris.setNLoops(1)
	qb._jba.calibrate(bounds=[1,5,100])
	child=Datacube('vcoil=%f'%v)
	data.addChild(child)
	acqiris.setNLoops(10)
	spectro=Datacube('spectro')
	child.addChild(spectro)
	qb.measureSpectroscopy(fstart=frequencies[0],fstop=frequencies[1],fstep=0.005,power=-10.,data=spectro)
	data.set(v=v,vi=vi)#f01=qb._f01)
	rabi=Datacube('rabi')
	child.addChild(rabi)
	qb.measureRabi(tstart=0,tstop=60,tstep=2.,data=rabi)
	data.set(rabiPi=qb._rabiDuration)
	scurves=Datacube('sCurves')
	child.addChild(scurves)
	qb.measureSCurves(data=scurves,ntimes=10)
	t1=Datacube('t1')
	child.addChild(t1)
	qb.measureT1(tstart=0,tstop=500,tstep=4,data=t1)
	data.set(t1=qb._t1)
	if qb._f01>0:frequencies=[qb._f01-0.25,qb._f01+0.25]
	else:frequencies=[8.2,8.7]
	data.commit()
	data.savetxt()
	vi+=1
coil.setVoltage(0.,slewRate=0.01)
##
coil.setVoltage(0.8,slewRate=0.1)
##
print qb._t1
##
qb._pulseGenerator._MWSource.turnOff()
qb._jba.measureSCurve(ntimes=10)
##
jba=instrumentManager.getInstrument('jba_qb1')
print jba
##
jba.calibrate(bounds=[1.5,3.5,25])
##
jba.measureSCurve(ntimes=10)
##
print qb._rabiPower

##
coil.setVoltage(-0.5,slewRate=0.1)
##
jba.calibrate()
##
data=Datacube("Spectroscopy vs power with leak")
dataManager.addDatacube(data)
#
powers=arange(5,-45,-2)
try:
	for power in powers:
		data.set(p=power)
		data.commit()
		child=Datacube("power = %s"%str(power))
		data.addChild(child)
		qb.measureSpectroscopy(fstart=8.8,fstop=9.3,fstep=0.002,power=power,data=child)
finally:
	data.savetxt()
##
from matplotlib.pyplot import *
figure()
#
cla()
i=0
for child in gv.data1.children():
	color=[(gv.data1['p'][i]+40)/50,0,1-(gv.data1['p'][i]+40)/50]
	print color
	plot(child['f'],child['p']+gv.data1['p'][i]/50,color=color)
	figtext(0.15,0.65+gv.data1['p'][i]/50*0.65,"%s dBm"%gv.data1['p'][i],color=color)
	i+=1
	if i>9:break
i=0
for child in gv.data2.children():
	color=[(data['p'][i]+40)/50,0,1-(gv.data2['p'][i]+40)/50]
	print color
	plot(child['f'],child['p']+gv.data2['p'][i]/50-0.12,color=color)
	i+=1
	if i>9:break
draw()
show()
##
from matplotlib.pyplot import *
figure()
cla()
i=0
for child in gv.data.children():
	color=[(gv.data['p'][i]+45)/50,0,1-(gv.data['p'][i]+45)/50]
	plot(child['f'],child['p']+gv.data['p'][i]/50,color=color)
	#figtext(0.15,0.65+gv.data1['p'][i]/50*0.65,"%s dBm"%gv.data1['p'][i],color=color)
	i+=1
	draw()
show()
##
data=Datacube('JBA1')
dataManager.addDatacube(data)
##
##
v=0.7
coil.setVoltage(v,slewRate=0.1)
acqiris.setNLoops(1)
qb._jba.calibrate(bounds=[2,3,25])
##
frequencies=[4.73,5]
child=Datacube('vcoil=%f'%v)
data.addChild(child)
acqiris.setNLoops(10)
spectro=Datacube('spectro')
child.addChild(spectro)
qb.measureSpectroscopy(fstart=frequencies[0],fstop=frequencies[1],fstep=0.005,power=-5.,data=spectro)
data.set(v=v,vi=vi)#f01=qb._f01)
rabi=Datacube('rabi')
child.addChild(rabi)
qb.measureRabi(tstart=0,tstop=200,tstep=2.,data=rabi)
data.set(rabiPi=qb._rabiDuration)
t1=Datacube('t1')
child.addChild(t1)
qb.measureT1(tstart=0,tstop=5000,tstep=5.,data=t1,accurate=True)
data.set(t1=qb._t1)
qb._rabiPower=-5.
if qb._f01>0:frequencies=[qb._f01-0.25,qb._f01+0.25]
else:frequencies=[8.2,8.7]

data.savetxt()
print qb._f01, qb._rabiDuration, qb._t1
###
dataManager.addDatacube(child)
##
print child.children()
##
print qb._f01, qb._rabiDuration, qb._t1
print qb._rabiPower
###############################################
##                                           ##
##       WEEK END DU 17-18 MARS 2012         ##
##                                           ##
###############################################

for k in range(0,1):
	data=Datacube("JBA4")
	data.setParameters(instrumentManager.parameters())
	dataManager.addDatacube(data)
	voltages=arange(0.88,0.0,-0.01)
#	voltages=arange(0.30,0.8,0.002)
	#voltages=concatenate(voltages[:], voltages[::-1])
#	voltages=[0.15]
 #	voltages=arange(0.8,0.7,-0.05)
	print voltages
	
	for v in voltages:
		try:
			parameters=params2(v)
			print parameters
	
			coil.setVoltage(v,slewRate=0.1)
			acqiris.setNLoops(1)
			qb._jba.calibrate(bounds=[2,3,25])
		
			child=Datacube('vcoil=%f'%v)
			data.addChild(child)
			acqiris.setNLoops(10)
			
			spectro=Datacube('spectro')
			child.addChild(spectro)
			qb.measureSpectroscopy(fstart=parameters['fstart'],fstop=parameters['fstop'],fstep=0.005,power=parameters['ps'],data=spectro)
			data.set(v=v,f01=qb._f01)
			
			#qb._rabiPower=getDrivePower(f=qb._f01)
		
			qb._rabiPower=parameters['pr']
			rabi=Datacube('rabi')
			child.addChild(rabi)
			qb.measureRabi(tstart=0,tstop=300,tstep=2.,data=rabi)
			p=qb.measureDrivePower()
			data.set(rabiPi=qb._rabiDuration,measuredPower=p)
			
			t1=Datacube('t1')
			#child.addChild(t1)
			parameters['t1']=80
			qb.measureT1(tstart=0,tstop=max(100,10*parameters['t1']),tstep=max(int(2*parameters['t1']/10.),1),data=t1,accurate=True)
			t1_0=qb._t1
			t1=Datacube('t1')
			child.addChild(t1)
			qb.measureT1(tstart=0,tstop=max(100,10*t1_0),tstep=max(int(2*t1_0/10.),1),data=t1,accurate=True)

			data.set(t1=qb._t1)
		finally:
			data.commit()
			data.savetxt()
#			all.savetxt()
		
##
###############################################
##                                           ##
##      NUIT DU 21-22 MARS 2012              ##
##                                           ##
###############################################

def params2(v):
	d=dict()
	d['f']=10-abs(v+0.45)*3.5
	d['fstart']=min(d['f']-0.088,6.4)
	d['fstop']=min(d['f']+0.6,6.75)
	d['t1']=abs(d['f']-6.6)*200
	d['ps']=-30.+abs(d['f']-6.6)*6.
	d['pr']=d['ps']+30.
	return d
print params2(0.8)
##
data=Datacube("JBA4")
data.setParameters(instrumentManager.parameters())
dataManager.addDatacube(data)
##
for k in range(0,10000):
	voltages=arange(0.64,0.0,-0.01)
 #	voltages=[0.2]
	#voltages=concatenate(voltages[:], voltages[::-1])
#	voltages=[0.15]
 #	voltages=arange(0.8,0.7,-0.05)
	print voltages
	
	for v in voltages:
		try:
			parameters=params2(v)
			print parameters
	
			coil.setVoltage(v,slewRate=0.1)
			acqiris.setNLoops(1)
			qb._jba.calibrate(bounds=[2,3,25])
		
			child=Datacube('vcoil=%f'%v)
			data.addChild(child)
			acqiris.setNLoops(10)
			
			spectro=Datacube('spectro')
			child.addChild(spectro)
			qb.measureSpectroscopy(fstart=parameters['fstart'],fstop=parameters['fstop'],fstep=0.002,power=parameters['ps'],data=spectro)
			data.set(v=v,f01=qb._f01)
			
			#qb._rabiPower=getDrivePower(f=qb._f01)
		
			qb._rabiPower=parameters['pr']
			rabi=Datacube('rabi')
			child.addChild(rabi)
#			qb.measureRabi(tstart=0,tstop=200,tstep=2.,data=rabi)
			p=qb.measureDrivePower()
			qb._rabiDuration=500
			data.set(rabiPi=qb._rabiDuration,measuredPower=p)
			
			t1=Datacube('t1')
			#child.addChild(t1)
			parameters['t1']=200
			qb.measureT1(tstart=0,tstop=max(100,10*parameters['t1']),tstep=max(int(2*parameters['t1']/10.),1),data=t1,accurate=True)
			t1_0=qb._t1
			t1=Datacube('t1')
			child.addChild(t1)
			qb.measureT1(tstart=0,tstop=max(100,10*t1_0),tstep=max(int(2*t1_0/20.),1),data=t1,accurate=True)

			data.set(t1=qb._t1)
			data.set(i=k)
		finally:
			data.commit()
			data.savetxt()
#			all.savetxt()

##
coil.setVoltage(0.185,slewRate=0.1)
##

t1_0=qb._t1
t1=Datacube('t1')
child.addChild(t1)
qb.measureT1(tstart=0,tstop=max(100,10*t1_0),tstep=max(int(2*t1_0/10.),1),data=t1,accurate=True)
##
print qb._t1
##
data.set(t1=qb._t1)
data.commit()


##
qb._jba._frequency=6.75
##
data=gv.data
data.set(pMeas=0)
data.commit()
data.savetxt()
##
data=gv.data
for i in range(0,len(data['f01'])):
	print i
	qb._pulseGenerator._MWSource.setFrequency(data['f01'][i])
	qb._pulseGenerator._MWSource.setPower(data['pRabi'][i])
	time.sleep(1.)
	data['pMeas'][i]=qb.measureDrivePower(f='t')
##

print qb._f01
##
data=Datacube()
dataManager.addDatacube(data)
qb._pulseGenerator._MWSource.setFrequency(4.)
for pin in arange(-30,5,5):
	data.set(pin=pin)
	qb._pulseGenerator._MWSource.setPower(pin)
	time.sleep(1.)
	pout=qb.measureDrivePower(f='t')
	data.set(pout=pout)
	data.commit()

##
print qb.measureDrivePower(f='t')
##
register=instrumentManager.getInstrument("register")
##
def params1(v):
	d=dict()
	d['f']=2.5+abs(v-0.45)*10.
	d['fstart']=min(d['f']-0.5,6.4)
	d['fstop']=min(d['f']+0.3,6.7)
	d['t1']=abs(d['f']-6.6)*200
	d['ps']=-20.+abs(d['f']-6.6)*12.
	d['pr']=d['ps']+10.
	return d
	
def params2(v):
	d=dict()
	d['f']=3.+abs(v+0.45)*4.
	d['fstart']=min(d['f']-0.5,6.4)
	d['fstop']=min(d['f']+0.3,6.75)
	d['t1']=abs(d['f']-6.6)*200
	d['ps']=-25.+abs(d['f']-6.6)*6.
	d['pr']=d['ps']+15.
	return d

def getDrivePower(f):
	return -25+abs(f-6.75)*10


##
print params2(0.3)




