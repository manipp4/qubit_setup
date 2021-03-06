#imports
import numpy
import scipy
from pyview.lib.datacube import *
from pyview.helpers.datamanager import DataManager
from pyview.helpers.instrumentsmanager import Manager

from pyview.lib.smartloop import *

#instruments
acqiris=Manager().getInstrument('acqiris') 
coil=Manager().getInstrument('Keithley2400')
AWG=Manager().getInstrument('awgMW')
mw_cav=Manager().getInstrument('MWSource_cavity')
mw_qb=Manager().getInstrument('MWSource_Qubit')
pg_qb=Manager().getInstrument('pg_qb')
pg_cav=Manager().getInstrument('PG_Cavity')
attenuator=Manager().getInstrument('Yoko3')

#######################################################################
####### AUTOMATIC MEASUREMENT OF T1 VS COIL CURRENT
#######################################################################

## function giving qubit frequency versus coil drive
def fvsIcoil(I):
	fmax=7.563
	Ioff=-0.0089
	Iperiod=6.72e-3
	f=fmax*sqrt(abs(cos((I-Ioff)*pi/Iperiod)))	
	return f

## Lorentzian fit of a dip  or peak
def fitLorentzian(x,y,direction="up",debug=False):
	""" fitLorentzian(x,y,direction="up",debug=False) finds the fitting parameters of a lorentzian peak (direction="up) or dip"""
	dir=1
	index=-1
	if direction!="up":
		dir=-1
		index=0
	# initial guessing
	(xPeak,yPeak)=sorted(zip(x,y),key = lambda t: t[1])[index]
	ymean=mean(y)
	pi=[yPeak-ymean,xPeak,0.002,ymean]
	# fit definition
	fitfunc = lambda p, x: p[3]+dir*abs(p[0])/(1.0+pow((x-p[1])/p[2],2.0))
	errfunc = lambda p, x, y,ff: pow(numpy.linalg.norm(ff(p,x)-y,2),2.0)
	# fit
	if debug: 
		print "initial guess :"
		print pi 
		print "fit result :"
	p1s = scipy.optimize.fmin(errfunc, pi,args=(x,y,fitfunc))
	if debug: 
		print p1s
	yfitguess=[fitfunc(pi,xv) for xv in x]
	yfit=[fitfunc(p1s,xv) for xv in x]
	return p1s,yfit,yfitguess
	
## finding an extremum 	
def xOfYExtremum(x,y,extremum="max"):
	index=-1
  	if extremum!="max": index=0
	(xExtr,yExtr)=sorted(zip(x,y),key = lambda t: t[1])[index]
  	return xExtr,yExtr

## set the awg
def setAWG(spp=1,qb_pulse=2000,res_pulse=5000,delay=20): #nanoseconds per point
	samplRate=1e9/spp
	reprate=samplRate/20000
	AWG.setRepetitionRate(reprate)
	pg_qb.clearPulse()
	pg_qb.generatePulse(duration=qb_pulse/spp, frequency=mw_qb.frequency(), DelayFromZero=10000-qb_pulse/spp-delay/spp,useCalibration=False)
	pg_qb.sendPulse()
	pg_cav.clearPulse()
	pg_cav.generatePulse(duration=res_pulse/spp, frequency=mw_cav.frequency(), DelayFromZero=10000,useCalibration=False)
	pg_cav.sendPulse()


##
def ResSpec(fcenter=1,fspan=1,fstep=0.1,power=1,data=''):
	if data=='':	
		data=Datacube('ResSpec')
		DataManager().addDatacube(data)
	setAWG(1,2000,5000,20)
  	mw_qb.turnOff()
	mw_cav.turnOn()
	attenuator.setVoltage(power)
	frequencyLoop=SmartLoop(fcenter-fspan/2,fstep,fcenter+fspan/2,name='resonator frequency')
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
	frequencyRes=xOfYExtremum(data['f'],data['amp'])[0]	
	data.savetxt()	
	return frequencyRes

##
def qbSpec(fcenter=1,fspan=1,fstep=0.1,power=1,fReadout=1,pReadout=4,data=''):
	if data=='':	
		data=Datacube('ResQubit')
		DataManager().addDatacube(data)
	setAWG(1,2000,5000,20)
	mw_qb.turnOn()
	mw_qb.setPower(power)
	mw_cav.setFrequency(fReadout)
	attenuator.setVoltage(pReadout)
	frequencyLoop=SmartLoop(fcenter-fspan/2,fstep,fcenter+fspan/2,name='qubit frequency')
	coil.turnOn()
	time.sleep(1)
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
	[dy,frequency01,dx,y0], Lorfit, Lorfitguess =fitLorentzian(data['f'],data['amp'],direction='down')
	data.createColumn('Lorfitguess',Lorfitguess)
	data.createColumn('Lorfit',Lorfit)		
	data.savetxt()
	return frequency01
########
########
mainData=Datacube("Spec vs coilCurrent 2")                                         # main datacube whole flux modulation
DataManager().addDatacube(mainData)

frequency01=5.637
minimSpan01=0.16
span01=0
frequencyRes=7.0839
frequencyResBare=7.080
coilCurrents=concatenate((arange(-10.3e-3,-10.15e-3,0.05e-3),arange(-9.65e-3,-8.05e-3,0.05e-3),arange(-7.5e-3,-6.15e-3,0.05e-3)))
#coilCurrents=SmartLoop(-7.2e-3,0.02e-3,-4e-3)
for coilCurrent in coilCurrents:
	onePointData=Datacube("coilCurrent=%f"%coilCurrent)                            #create datacube a child for this flux
	mainData.addChild(onePointData)
	mainData.set(coilCurrent=coilCurrent)
  	coil.setCurrent(coilCurrent)                                                   #set the coil current
  	print "current %f"%coilCurrent 

    freqcenter_qb=fvsIcoil(coilCurrent)          # calculated first parameters
	chi=0.09**2/(freqcenter_qb-frequencyResBare)
	freqcenter_Res=frequencyResBare-chi
	
	# Resonator Spectroscopy	
	ResSpecdata=Datacube('spectroscopyRes %f V, Icoil=%f'%(p,coil.current()))             # create a child datacube for resonator
	onePointData.addChild(ResSpecdata)
	frequencyRes=ResSpec(fcenter=freqcenter_Res,fspan=0.03,fstep=0.0003,power=4,data=ResSpecdata) 
	mainData.set(frequencyRes=frequencyRes)	

	# Spectroscopy01

	#
	if freqcenter_qb>6:
		p=-20
	elif freqcenter_qb>5:
		p=-10
	else:
		p=0
		
	span01=max(span01,minimSpan01)
	qbSpecdata=Datacube('spectroscopy01 %f dBm, vcoil=%f'%(p,coil.current()))
	onePointData.addChild(data)

	frequency01=qbSpec(fcenter=4.1,fspan=span01,fstep=0.0005,power=p,fReadout=frequencyRes,data=qbSpecdata)		
	mainData.set(frequency01=frequency01)
	mainData.commit()
	mainData.savetxt()
coil.turnOff()	
##

##

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
def estimatePeriod(y):
	fft=numpy.fft.rfft(y)
	fft[0]=0
	return len(y)/argmax(fft)/2

##
gv.data.savetxt()



