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
pg_cav=Manager().getInstrument('PG_Cavity')
attenuator=Manager().getInstrument('Yoko3')
print(mw_qb)
print(pg_qb)
#######################################################################
####### AUTOMATIC MEASUREMENT OF T1 VS COIL CURRENT
#######################################################################
mainData=Datacube("Spec vs coilCurrent 2")
DataManager().addDatacube(mainData)

frequency01=5.637
minimSpan01=0.16
span01=0
frequencyRes=7.0839
frequencyResBare=7.080
coilCurrents=concatenate((arange(-10.3e-3,-10.15e-3,0.05e-3),arange(-9.65e-3,-8.05e-3,0.05e-3),arange(-7.5e-3,-6.15e-3,0.05e-3)))
#coilCurrents=SmartLoop(-7.2e-3,0.02e-3,-4e-3)
for coilCurrent in coilCurrents:
	
	onePointData=Datacube("coilCurrent=%f"%coilCurrent)
	mainData.addChild(onePointData)
	mainData.set(coilCurrent=coilCurrent)
	
	#set awg
	spp=1 #nanoseconds per point
	samplRate=1e9/spp
	reprate=samplRate/20000
	AWG.setRepetitionRate(reprate)
	pg_qb.clearPulse()
	pg_qb.generatePulse(duration=2000, frequency=mw_qb.frequency(), DelayFromZero=10000-2000-20,useCalibration=False)
	pg_qb.sendPulse()
	pg_cav.clearPulse()
	pg_cav.generatePulse(duration=5000, frequency=mw_cav.frequency(), DelayFromZero=10000,useCalibration=False)
	pg_cav.sendPulse()

	
	coil.setCurrent(coilCurrent)
	time.sleep(0.1)
	freqcenter_qb=fvsIcoil(coilCurrent)
	chi=0.09**2/(freqcenter_qb-frequencyResBare)
	freqcenter_Res=frequencyResBare-chi
	# resonator readout config
		
	mw_qb.turnOff()
	mw_cav.turnOn()
	p=attenuator.setVoltage(4)
	
	
	data=Datacube('spectroscopyRes %f V, Icoil=%f'%(p,coil.current()))
	onePointData.addChild(data)
	ResSpan=0.03
	frequencyLoop=SmartLoop(freqcenter_Res-ResSpan/2,0.0003,freqcenter_Res+ResSpan/2,name='frequency')
	coil.turnOn()
	time.sleep(1)
	for f in frequencyLoop:
		mw_cav.setFrequency(f)
		acqiris.AcquireTransferV4(transferAverage=True,nLoops=5,wantedChannels=3)
		acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
		chanels= acqiris("DLLMath1Module.mean")
		amp=sqrt((chanels[0])**2+(chanels[1])**2)
		phase=arctan(chanels[0]/chanels[1])
		data.set(f=f,i=chanels[0],q=chanels[1],amp=amp,phase=phase)
		data.commit()
	#fit
	coil.turnOff()
	frequencyRes=findFreqOfMax(data['f'],data['amp'])	
	data.savetxt()	
	 
	mainData.set(frequencyRes=frequencyRes)	

	# Spectroscopy01

	#
	print freqcenter
	if freqcenter>6:
		p=-20
	elif freqcenter>5.5:
		p=-10
	else:
		p=0

	mw_qb.turnOn()
	mw_qb.setPower(p)
	mw_cav.setFrequency(frequencyRes)
	print 'frequencyRes'
	print mw_cav.frequency()

	
	pg_qb.clearPulse()
	pg_qb.generatePulse(duration=2000, frequency=mw_qb.frequency(), DelayFromZero=10000-2000-20,useCalibration=False)
	pg_qb.sendPulse()
	
	
	span01=max(span01,minimSpan01)
	data=Datacube('spectroscopy01 %f dBm, vcoil=%f'%(p,coil.current()))
	onePointData.addChild(data)
	frequencyLoop=SmartLoop(freqcenter_qb-span01/2,0.001,freqcenter_qb+span01/2,name='frequency')
	coil.turnOn()
	time.sleep(1)
	for i in range(10):
		for f in frequencyLoop:
			mw_qb.setFrequency(f)
			acqiris.AcquireTransferV4(transferAverage=True,nLoops=50,wantedChannels=3)
			acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
			chanels= acqiris("DLLMath1Module.mean")
			amp=sqrt((chanels[0])**2+(chanels[1])**2)
			phase=arctan(chanels[0]/chanels[1])
			data.set(f=f,i=chanels[0],q=chanels[1],amp=amp,phase=phase)
			data.commit()
		coil.turnOff()
		k=frequency01
		[dy,frequency01,dx,y0], Lorfit, Lorfitguess =fitLorentzianDip(data['f'],data['amp'])
		span01=abs(k-frequency01)*4
		if abs(k-frequency01)<0.15:
			break
	data.createColumn('Lorfitguess',Lorfitguess)
	data.createColumn('Lorfit',Lorfit)		
	data.savetxt()	 		
	mainData.set(frequency01=frequency01)
	mainData.commit()
	mainData.savetxt()
coil.turnOff()	
##
print fvsIcoil(-0.011)
##
def fvsIcoil(I):
	fmax=7.563
	Ioff=-0.0089
	Iperiod=6.72e-3
	f=fmax*sqrt(abs(cos((I-Ioff)*pi/Iperiod)))	
	return f
	
##
######
def fitLorentzianDip(x,y):
	# initial guessing
	(xmin,ymin)=sorted(zip(x,y),key = lambda t: t[1])[0]
	ymean=mean(y)

	fitfunc = lambda p, x: p[3]-abs(p[0])/(1.0+pow((x-p[1])/p[2],2.0))
	errfunc = lambda p, x, y,ff: pow(numpy.linalg.norm(ff(p,x)-y,2),2.0)

	pi=[ymin-ymean,xmin,0.002,ymean]
	print "initial guess :"
	print pi 
	
	p1s = scipy.optimize.fmin(errfunc, pi,args=(x,y,fitfunc))
	print "fit result :"
	print p1s
	yfitguess=[fitfunc(pi,xv) for xv in x]
	yfit=[fitfunc(p1s,xv) for xv in x]

	return p1s,yfit,yfitguess
	
######
def fitLorentzianPeak(x,y):
	# initial guessing
	(xmax,ymax)=sorted(zip(x,y),key = lambda t: t[1])[-1]
	ymean=mean(y)

	fitfunc = lambda p, x: p[3]+abs(p[0])/(1.0+pow((x-p[1])/p[2],2.0))
	errfunc = lambda p, x, y,ff: pow(numpy.linalg.norm(ff(p,x)-y,2),2.0)

	pi=[ymax-ymean,xmax,0.002,ymean]
	print "initial guess :"
	print pi 
	
	p1s = scipy.optimize.fmin(errfunc, pi,args=(x,y,fitfunc))
	print "fit result :"
	print p1s
	yfitguess=[fitfunc(pi,xv) for xv in x]
	yfit=[fitfunc(p1s,xv) for xv in x]

	return p1s,yfit,yfitguess
#####
def findFreqOfMax(x,y):
	# initial guessing
	(xmax,ymax)=sorted(zip(x,y),key = lambda t: t[1])[-1]
	return xmax
######

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



