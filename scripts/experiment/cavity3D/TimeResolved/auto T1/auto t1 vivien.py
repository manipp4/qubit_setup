import numpy
import scipy
from pyview.lib.datacube import *
from pyview.helpers.datamanager import DataManager
from pyview.helpers.instrumentsmanager import Manager

from pyview.lib.smartloop import *

acqiris=Manager().getInstrument('acqiris') 
coil=Manager().getInstrument('Keithley2400')
AWG=Manager().getInstrument('awgMW')
#print coil.current()
mw_cav=Manager().getInstrument('MWSource_cavity')
mw_qb=Manager().getInstrument('MWSource_Qubit')
pg_qb=Manager().getInstrument('pg_qb')
attenuator=Manager().getInstrument('Yoko3')
print(mw_qb)
print(pg_qb)
#######################################################################
####### AUTOMATIC MEASUREMENT OF T1 VS COIL CURRENT
#######################################################################
mainData=Datacube("T1 vs coilCurrent")
DataManager().addDatacube(mainData)

frequency01=7.085
coilCurrents=SmartLoop(-11e-3,0.5e-3,-10e-3)

for coilCurrent in coilCurrents:
	
	onePointData=Datacube("coilCurrent=%f"%coilCurrent)
	mainData.addChild(onePointData)
	mainData.set(coilCurrent=coilCurrent)
	
	AWG.setRepetitionRate(50000)
	
	#coil.setCurrent(coilCurrent)
	
	time.sleep(0.1)
	# resonator readout config
		
	mw_qb.turnOff()
	mw_cav.turnOn()
	p=attenuator.setVoltage(3)
	
	
	data=Datacube('spectroscopyRes %f V, Icoil=%f'%(p,coil.current()))
	onePointData.addChild(data)
	frequencyLoop=SmartLoop(frequency01-0.150,0.002,frequency01+0.150,name='frequency')
	for f in frequencyLoop:
		mw_cav.setFrequency(f)
		acqiris.AcquireTransferV4(transferAverage=True,nLoops=50,wantedChannels=3)
		acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
		chanels= acqiris("DLLMath1Module.mean")
		amp=sqrt((chanels[0])**2+(chanels[1])**2)
		data.set(f=f,i=chanels[0],q=chanels[1],amp=amp)
		data.commit()	
	data.savetxt()	 	
	#fit
	[dy,frequency01,dx,y0]=fitLorentzianPeak(data['f'],data['amp'])
##
[dy,frequency01,dx,y0]=fitLorentzianPeak(data['f'],data['amp'])
print dy
##	
print Lorfit = y0+dy/(1.0+pow((x-frequency01)/dx,2.0)
##	
	data.createColumn('Lorfit',Lorfit)
	# Spectroscopy01
##	
	p=-25
	
	mw.turnOn()
	mw.setPower(p)
	
	pg_qb.clearPulse()
	pg_qb.generatePulse(duration=2000, frequency=5, DelayFromZero=10000-2000-20,useCalibration=False)
	pg_qb.sendPulse()
	
	data=Datacube('spectroscopy01 %f dBm, vcoil=%f'%(p,coil.voltage()))
	onePointData.addChild(data)
	frequencyLoop=SmartLoop(frequency01-0.150,0.002,frequency01+0.150,name='frequency')
	for frequency in frequencyLoop:
		mw.setFrequency(frequency)
		time.sleep(0.2)
		data.set(f=frequency)
		data.set(**jba.measure(nLoops=20,fast=True)[0])
		data.commit()
	data.savetxt() 	
	
	#fit
	[dy,frequency01,dx,y0]=fitLorentzian(data['f'],data['amp'])
	#data.createColumn('b0_fit',yfit)
	
	mainData.set(frequency01=frequency01)

	# Spectroscopy02
	
	p=-15
	
	mw.turnOn()
	mw.setPower(p)
	
	pg_qb.clearPulse()
	pg_qb.generatePulse(duration=2000, frequency=5, DelayFromZero=10000-2000-20,useCalibration=False)
	pg_qb.sendPulse()
	
	data=Datacube('spectroscopy02 %f dBm, vcoil=%f'%(p,coil.voltage()))
	onePointData.addChild(data)
	frequencyLoop=SmartLoop(frequency01-0.300,0.002,frequency01-0.100,name='frequency')
	for frequency in frequencyLoop:
		mw.setFrequency(frequency)
		time.sleep(0.2)
		data.set(f=frequency)
		data.set(**jba.measure(nLoops=20,fast=True)[0])
		data.commit()
	data.savetxt() 	

	# fit

	[dy,frequency02,dx,y0]=fitLorentzian(data['f'],data['b0'])
	#data.createColumn('b0_fit',yfit)
	mainData.set(frequency02=frequency02)

	# RABI
	
	p=-15
	mw.setPower(p)
	mw.setFrequency(frequency01)
	
	data=Datacube('rabi %f dBm, frequency=%f'%(p,frequency01))
	onePointData.addChild(data)
	durations=SmartLoop(0,1,200,name="durations")
	for duration in durations:
		pg_qb.clearPulse()
		pg_qb.generatePulse(duration=duration, frequency=frequency01, DelayFromZero=10000-duration-20,useCalibration=False)
		pg_qb.sendPulse()
		time.sleep(0.1)
		data.set(duration=duration)
		data.set(**jba.measure(nLoops=20,fast=True)[0])
		data.commit()
	
	# RABI HAS TO BE FITTED HERE
	period= estimatePeriod(c['b0'])
	[y0,dy,pi2Rabi,t10],yfit=fitRabi(data['duration'],data['b0'],period=period)
	data.createColumn("b0fit",yfit)
	piRabi=pi2Rabi/2
	mainData.set(piRabi=piRabi)
	
	#T1
	AWG.setRepetitionRate()
	pg_qb.clearPulse()
	pg_qb.sendPulse()
	
	p=-15
	mw.setPower(p)
	mw.setFrequency(frequency01)
	
	data=Datacube('t1 %f dBm, frequency=%f, pi=%f ns'%(p,frequency01,piRabi))
	onePointData.addChild(data)
	delays=SmartLoop(0,5,1000,name="delays")
	for delay in delays:
		pg_qb.clearPulse()
		pg_qb.generatePulse(duration=duration, frequency=frequency01, DelayFromZero=10000-piRabi-delay-200,useCalibration=False)
		pg_qb.sendPulse()
		time.sleep(0.1)
		data.set(delay=delay)
		data.set(**jba.measure(nLoops=20,fast=True)[0])
		data.commit()
	

	# T1 has to be fit here
	[y0,dy,T1],yfit=fitT1(data['delay'],data['b0'])
	data.createColumn("b0fit",yfit)
	
	mainData.set(T1=T1)
	mainData.commit()
	mainData.savetxt()


######
def fitLorentzianDip(x,y):
	# initial guessing
	(xmin,ymin)=sorted(zip(x,y),key = lambda t: t[1])[0]
	ymean=mean(y)

	fitfunc = lambda p, x: p[3]+p[0]/(1.0+pow((x-p[1])/p[2],2.0))
	errfunc = lambda p, x, y,ff: pow(numpy.linalg.norm(ff(p,x)-y,2),2.0)

	pi=[ymin-ymean,xmin,0.005,ymean]
	print "initial guess :"
	print pi 
	
	p1s = scipy.optimize.fmin(errfunc, pi,args=(x,y,fitfunc))
	print "fit result :"
	print p1s
	yfit=[fitfunc(p1s,xv) for xv in x]

	return p1s,yfit
	
######
def fitLorentzianPeak(x,y):
	# initial guessing
	(xmax,ymax)=sorted(zip(x,y),key = lambda t: t[1])[-1]
	ymean=mean(y)

	fitfunc = lambda p, x: p[3]-p[0]/(1.0+pow((x-p[1])/p[2],2.0))
	errfunc = lambda p, x, y,ff: pow(numpy.linalg.norm(ff(p,x)-y,2),2.0)

	pi=[ymax-ymean,xmax,0.005,ymean]
	print "initial guess :"
	print pi 
	
	p1s = scipy.optimize.fmin(errfunc, pi,args=(x,y,fitfunc))
	print "fit result :"
	print p1s
	yfit=[fitfunc(p1s,xv) for xv in x]

	return p1s,yfit

######
def fitRabi(x,y,period=20):
	# initial guessing
	pi=[0.5,0.1,period,200]
	print "initial guess :"
	print pi 

	fitfunc = lambda p, x: p[0]+p[1]*cos(math.pi*x/p[2])*exp(-x/p[3])
	errfunc = lambda p, x, y,ff: pow(numpy.linalg.norm(ff(p,x)-y,2),2.0)
	
	p1s = scipy.optimize.fmin(errfunc, pi,args=(x,y,fitfunc))
	print "fit result :"
	print p1s
	yfit=[fitfunc(p1s,xv) for xv in x]

	return p1s,yfit
###
def fitT1(x,y):
	# initial guessing
	pi=[0.5,0.1,200]
	print "initial guess :"
	print pi 

	fitfunc = lambda p, x: p[0]+p[1]*exp(-x/p[2])
	errfunc = lambda p, x, y,ff: pow(numpy.linalg.norm(ff(p,x)-y,2),2.0)
	
	p1s = scipy.optimize.fmin(errfunc, pi,args=(x,y,fitfunc))
	print "fit result :"
	print p1s
	yfit=[fitfunc(p1s,xv) for xv in x]

	return p1s,yfit

def estimatePeriod(y):
	fft=numpy.fft.rfft(y)
	fft[0]=0
	return len(y)/argmax(fft)/2

######
#amelioration du fit lorentzian
######
f02=zeros(len(gv.data['frequency01']))
for i in range(0,len(gv.data.children())):
	c=gv.data.children()[i].children()[1]
	o,y=fitLorentzian(c['f'],c['b0'])
	f02[i]=o[1]
gv.data.createColumn('f02corr',f02)
##	
print f01
##
def estimatePeriod(y):
	fft=numpy.fft.rfft(y)
	fft[0]=0
	return len(y)/argmax(fft)/2

##
gv.data.savetxt()



