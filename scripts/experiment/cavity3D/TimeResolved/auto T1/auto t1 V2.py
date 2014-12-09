#######################################################################
####### AUTOMATIC MEASUREMENT OF T1 VS COIL CURRENT
#######################################################################

## imports and instruments
import numpy
import scipy
from pyview.lib.datacube import *
from pyview.helpers.datamanager import DataManager
from pyview.helpers.instrumentsmanager import Manager
from matplotlib.pyplot import *
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

## function giving qubit frequency versus coil drive
def fvsIcoil(I):
	fmax=7.563
	Ioff=-0.0089
	Iperiod=6.72e-3
	f=fmax*sqrt(abs(cos((I-Ioff)*pi/Iperiod)))	
	return f
## Lorentzian pure function
def Lorenzian(yAmp,x0,dx,y0):
	return lambda x: y0+yAmp/(1.0+pow((x-x0)/dx,2.0)) 
## Cosine pure function
def cosine(y0,yAmp,period,x0):
	return lambda x: y0+yAmp*cos(2*math.pi*(x-x0)/period)
## Lorentzian fit of a dip  or peak
def fitLorentzian(x,y,width=0,direction="up",debug=False,method="fitPeak"):
	""" fitLorentzian(x,y,direction="up",debug=False) finds the fitting parameters of a lorentzian peak (direction="up) or dip"""
	dir=1
	index=-1
	if direction!="up":
		dir=-1
		index=0
	# initial guessing
	if width==0:
		width=(max(x)-min(x))/10
	(xPeak,yPeak)=sorted(zip(x,y),key = lambda t: t[1])[index]
	ymean=mean(y)
	pi=[yPeak-ymean,xPeak,width,ymean]
	# fit definition
	fitfunc = lambda p, x: p[3]+dir*abs(p[0])/(1.0+pow((x-p[1])/p[2],2.0))
	errfunc = lambda p, x, y,ff: pow(numpy.linalg.norm(ff(p,x)-y,2),2.0)
	# fit
	if debug: 
		print "initial guess :"
		print pi 
		print "fit result :"
	p1s = scipy.optimize.fmin(errfunc, pi,args=(x,y,fitfunc))
	if direction!="up":
		p1s[0]=-abs(p1s[0])
	else:
		p1s[0]=abs(p1s[0])
	if debug: 
		print p1s
	yfitguess=[fitfunc(pi,xv) for xv in x]
	yfit=[fitfunc(p1s,xv) for xv in x]
	return p1s,yfit,yfitguess
## finding an extremum 	
def xOfYExtremum(x,y,extremum="max"):
	index=-1
	if extremum != "max":
		index=0
	(xExtr,yExtr)=sorted(zip(x,y),key = lambda t: t[1])[index]
	return xExtr,yExtr
##
def estimatePeriod(y):
	fft=numpy.fft.rfft(y)
	fft[0]=0
	return len(y)/argmax(fft)
##
def fitRabi(x,y,period=200,x0=0,debug=False):
	# initial guessing
	pin=[mean(y),(max(y)-min(y))/2,period,x0]
	print "initial guess :"
	print pin 

	fitfunc = lambda p, x: p[0]+p[1]*cos(math.pi*2*(x-p[3])/p[2])
	errfunc = lambda p, x, y,ff: pow(numpy.linalg.norm(ff(p,x)-y,2),2.0)
	
	p1s = scipy.optimize.fmin(errfunc, pin,args=(x,y,fitfunc))
	print "fit result :"
	print p1s
	yfit=[fitfunc(p1s,xv) for xv in x]
	if debug:
		clf()
		cla()
		pl=plot(x,y,'ro')
		cos1=cosine(p1s[0],p1s[1],p1s[2],p1s[3])
		xplot=linspace(min(x),max(x),500)
		yplot=cos1(xplot)
		pl1=plot(xplot,yplot)
		show()

	return p1s,yfit
##
def fitT1(x,y,debug=False):
	# initial guessing
	pi=[max(y),max(y)-min(y),max(x)/4]
	print "initial guess :"
	print pi 

	fitfunc = lambda p, x: p[0]+p[1]*exp(-x/p[2])
	errfunc = lambda p, x, y,ff: pow(numpy.linalg.norm(ff(p,x)-y,2),2.0)
	
	p1s = scipy.optimize.fmin(errfunc, pi,args=(x,y,fitfunc))
	print "fit result :"
	print p1s
	yfit=[fitfunc(p1s,xv) for xv in x]

	return p1s,yfit
## set the awg
def setAWG(sampTime_ns=1,qb_pulse_ns=2000,res_pulse_ns=5000,driveReadSep_ns=20): #nanoseconds per point
	samplRate=1e9/sampTime_ns
	reprate=samplRate/20000
	AWG.setRepetitionRate(reprate)
	pg_qb.clearPulse()
	pg_qb.generatePulse(duration=qb_pulse_ns/sampTime_ns, frequency=mw_qb.frequency(), DelayFromZero=10000-(qb_pulse_ns+driveReadSep_ns)/sampTime_ns,useCalibration=False)
	pg_qb.sendPulse()
	pg_cav.clearPulse()
	pg_cav.generatePulse(duration=res_pulse_ns/sampTime_ns, frequency=mw_cav.frequency(), DelayFromZero=10000,useCalibration=False)
	pg_cav.sendPulse()
##
def measureIQ(nLoops=1,wantedChannels=3,iOffset=0,qOffset=0,averageOverSequence=False,convertToAmpPhase=False):
	# acquire and transfer the sequence of traces for the selected channels
	acqiris.AcquireTransferV4(transferAverage=False,nLoops=nLoops,wantedChannels=wantedChannels)
	acqiris("DLLMath1Module.meanOfLastWaveForms("+str(wantedChannels)+")")		# calculate the mean of each trace in the sequence 
	channels= acqiris("DLLMath1Module.mean")	# get the sequence of means for the selected channels
	# get the indexes of selected channels
	indexes= [i for i,x in enumerate([1&wantedChannels!=0,2&wantedChannels!=0,4&wantedChannels!=0,8&wantedChannels!=0]) if x ==True]
	channels=[channels[indexes[0]],channels[indexes[1]]] # keep only the first and second selected channels as I and Q
	if iOffset!=0 : channels[0]=channels[0]-iOffset  	 # subtract I and Q offset if necessary
	if qOffset!=0 : channels[1]=channels[1]-qOffset
	if averageOverSequence:								 # average over sequence if requested
		channels=[numpy.mean(channels[0]),numpy.mean(channels[1])]
	if convertToAmpPhase:									 # convert I and Q into Amp and Phase
		channels=[sqrt((channels[0])**2+(channels[1])**2),arctan(channels[1]/channels[0])]		# calculate amplitude and phase
	# returns [I,Q] or [Amp, phi] or [array([I1,I2,I3,...],array([Q1,Q2,Q3,...])] or  [array([A1,A2,A3,...],array([phi1,phi2,phi3,...])]
	return channels 
##
def resSpec(fcenter=1,fspan=1,fstep=0.1,power=1,data='',autoPlot=True,autoClear=False):
	if data=='':	
		data=Datacube('ResSpec')
		DataManager().addDatacube(data)
	if autoPlot:
		data.defineDefaultPlot("f","amp")
		DataManager().addDatacube(data)
		DataManager().autoPlot(data,autoClear)
	setAWG(sampTime_ns=1,qb_pulse_ns=2000,res_pulse_ns=3000,driveReadSep_ns=20)
	mw_qb.turnOff()
	mw_cav.turnOn()
	attenuator.setVoltage(power)
	frequencyLoop=SmartLoop(fcenter-fspan/2,fstep,fcenter+fspan/2,name='resonator frequency')
	coil.turnOn()
	time.sleep(1)
	for f in frequencyLoop:
		mw_cav.setFrequency(f)
		[amp,phase]=measureIQ(nLoops=10,wantedChannels=3,iOffset=0,qOffset=0,averageOverSequence=True,convertToAmpPhase=True)
		data.set(f=f,amp=amp,phase=phase)
		data.commit()
	#fit
	coil.turnOff()
	frequencyRes=xOfYExtremum(data['f'],data['amp'])[0]	
	data.savetxt()
	print "f_Res = %f"%frequencyRes	
	return frequencyRes
##
def qbSpec(fcenter=1,fspan=1,fstep=0.1,power=1,fReadout=1,pReadout=4,data='',autoPlot=True,autoClear=False):
	if data=='':	
		data=Datacube('ResQubit')
		DataManager().addDatacube(data)
	if autoPlot:
		data.defineDefaultPlot("f","amp")
		data.defineDefaultPlot("f","Lorfit")
		DataManager().addDatacube(data)
		DataManager().autoPlot(data,autoClear)
	setAWG(sampTime_ns=1,qb_pulse_ns=2000,res_pulse_ns=3000,driveReadSep_ns=20)
	mw_qb.turnOn()
	mw_qb.setPower(power)
	mw_cav.setFrequency(fReadout)
	attenuator.setVoltage(pReadout)
	frequencyLoop=SmartLoop(fcenter-fspan/2,fstep,fcenter+fspan/2,name='qubit frequency')
	coil.turnOn()
	time.sleep(1)
	for f in frequencyLoop:
		mw_qb.setFrequency(f)
		[amp,phase]=measureIQ(nLoops=10,wantedChannels=3,iOffset=0,qOffset=0,averageOverSequence=True,convertToAmpPhase=True)
		data.set(f=f,amp=amp,phase=phase)
		data.commit()
	coil.turnOff()
	[dy,frequency01,dx,y0], Lorfit, Lorfitguess =fitLorentzian(data['f'],data['amp'],width=0.0005,direction='down')
	data.createColumn('Lorfitguess',Lorfitguess)
	data.createColumn('Lorfit',Lorfit)		
	data.savetxt()
	print "f_01 = %f"%frequency01
	return frequency01
##
def rabiMeas(fQubit=1,pQubit=-20,fRes=1,pRes=4,start=0,stop=1000,step=10,data='',autoPlot=True,autoClear=False):
	if data=='':	
		data=Datacube('Rabi')
		DataManager().addDatacube(data)
	if autoPlot:
		data.defineDefaultPlot("duration","amp")
		data.defineDefaultPlot("duration","rabiFit")
		DataManager().addDatacube(data)
		DataManager().autoPlot(data,autoClear)
	mw_qb.turnOn()
	mw_qb.setPower(pQubit)
	mw_qb.setFrequency(fQubit)
	mw_cav.setFrequency(fRes)
	attenuator.setVoltage(pRes)
	durations=SmartLoop(start,step,stop,name="durations")
	coil.turnOn()
	time.sleep(1)
	for duration in durations:
		setAWG(sampTime_ns=1,qb_pulse_ns=duration,res_pulse_ns=3000,driveReadSep_ns=20)
		time.sleep(0.1)
		[amp,phase]=measureIQ(nLoops=50,wantedChannels=3,iOffset=0,qOffset=0,averageOverSequence=True,convertToAmpPhase=True)
		data.set(duration=duration,amp=amp,phase=phase)
		data.commit()
		
	coil.turnOff()
	fftperiod= estimatePeriod(data['amp'])
	[y0,dy,pi2Rabi,dx],yfit=fitRabi(data['duration'],data['amp'],period=fftperiod*step,x0=100)
	data.createColumn("rabiFit",yfit)
	piRabi=pi2Rabi/2
	print "Pi pulse length = %f ns"%piRabi	 
	return piRabi
##
def estimatePeriod(y,debug=False):
	fft=numpy.fft.rfft(y)
	fft[0]=0
	[dy,xPeak,dx,y0], Lorfit, Lorfitguess =fitLorentzian(range(len(fft)),abs(fft),2,)
	if debug:
		clf()
		cla()
		print dy,xPeak,dx,y0
		print len(fft)
		#print fft, abs(fft),argmax(abs(fft))
		pl=plot(range(len(fft)),abs(fft),'ro')
		Lor=Lorenzian(dy,xPeak,dx,y0)
		print Lor(2)
		yplot=Lor(linspace(0,len(fft),500))
		xplot=linspace(0,len(fft),500)
		pl1=plot(xplot,yplot)
		show()
	return len(y)/xPeak
##
def t1Meas(fQubit=1,pQubit=-20,fRes=1,pRes=4,piRabi=50,start=0,stop=1000,step=10,data='',autoPlot=True,autoClear=False):
	if data=='':	
		data=Datacube('T1')
		DataManager().addDatacube(data)
	if autoPlot:
		data.defineDefaultPlot("delay","amp")
		data.defineDefaultPlot("delay","T1fit")
		DataManager().addDatacube(data)
		DataManager().autoPlot(data,autoClear)
	mw_qb.turnOn()
	mw_qb.setPower(pQubit)
	mw_qb.setFrequency(fQubit)
	mw_cav.setFrequency(fRes)
	attenuator.setVoltage(pRes)
	sampTime_ns=stop/10000+1
	coil.turnOn()
	time.sleep(1)
	delays=concatenate((arange(start,stop/4,step),arange(stop/4,stop*3/4,step*2),arange(stop*3/4,stop,step)))
	frequencyLoop=SmartLoop(0,10,fcenter+fspan/2,name='delay drive-readout')
	for delay in delays:
		setAWG(sampTime_ns=sampTime_ns,qb_pulse_ns=piRabi,res_pulse_ns=3000,driveReadSep_ns=20+delay)
		time.sleep(0.1)
		[amp,phase]=measureIQ(nLoops=50,wantedChannels=3,iOffset=0,qOffset=0,averageOverSequence=True,convertToAmpPhase=True)
		data.set(delay=delay,amp=amp,phase=phase)
		data.commit()
	coil.turnOff()
	[y0,dy,T1],yfit=fitT1(data['delay'],data['amp'])
	data.createColumn("T1fit",yfit)
	return T1

## SET AWG
setAWG(sampTime_ns=1,qb_pulse_ns=2000,res_pulse_ns=3000,driveReadSep_ns=20)
## Set working point and parameters
frequencyResBare=7.080
spanRes=0.03
coilCurrent=-10.5e-3
coil.setCurrent(coilCurrent)
coil.turnOn()
freqCenter_qb=fvsIcoil(coilCurrent)          		  # calculated first parameters 
chi=0.09**2/(freqcenter_qb-frequencyResBare)
freqCenter_Res=frequencyResBare-chi
span01=0.1
p=-10
T1est=10000
##
resSpecData=Datacube('ResoSpec %f V, Icoil=%f'%(4,coil.current()))
frequencyRes=resSpec(fcenter=freqCenter_Res,fspan=spanRes,fstep=0.0003,power=4,data=resSpecData)

##
qbSpecData=Datacube('spectroscopy01 %f dBm, vcoil=%f'%(p,coil.current()))
frequency01=qbSpec(fcenter=freqcenter_qb,fspan=span01/2,fstep=0.00025,power=p-10,fReadout=frequencyRes,data=qbSpecData,autoClear=False)

##
rabiData=Datacube('rabi %f dBm, frequency=%f'%(p+10,frequency01))
piRabi= rabiMeas(fQubit=frequency01,pQubit=p+26,fRes=frequencyRes,pRes=4,start=0,stop=1000,step=2,data=rabiData,autoClear=False)

##
T1Data=Datacube('t1 %f dBm, frequency=%f, qubitPulse=%f ns'%(p+10,frequency01,piRabi))
T1start=0
T1stop=int(4*T1est)
T1step=int (T1est/10)
T1=t1Meas(fQubit=frequency01,pQubit=p+10,fRes=frequencyRes,pRes=4,piRabi=piRabi,start=T1start,stop=T1stop,step=T1step,data=T1Data,autoClear=False)
T1est=T1
print T1
##
print T1






## CODE
mainData=Datacube("T1 vs coilCurrent 4")                                         # main datacube whole flux modulation
DataManager().addDatacube(mainData)

#frequency01=5.637
span01=0.15
spanRes=0.03
#frequencyRes=7.0839
frequencyResBare=7.080
p=-10
T1est=6000
coilCurrents=arange(-11.3e-3,-10.30e-3,2.0e-5)
#coilCurrents=SmartLoop(-7.35e-3,0.05e-3,-6.5e-3)
for coilCurrent in coilCurrents:
	onePointData=Datacube("coilCurrent=%f"%coilCurrent)    #create datacube a child for this flux
	mainData.addChild(onePointData)
	mainData.set(coilCurrent=coilCurrent)
  	coil.setCurrent(coilCurrent)                           #set the coil current
  	print "current %f"%coilCurrent 

	freqcenter_qb=fvsIcoil(coilCurrent)          		  # calculated first parameters
	chi=0.09**2/(freqcenter_qb-frequencyResBare)
	freqcenter_Res=frequencyResBare-chi
	
	# Resonator Spectroscopy	
	ResSpecdata=Datacube('spectroscopyRes %f V, Icoil=%f'%(4,coil.current()))             # create a child datacube for resonator
	onePointData.addChild(ResSpecdata)
	frequencyRes=ResSpec(fcenter=freqcenter_Res,fspan=spanRes,fstep=0.0003,power=4,data=ResSpecdata) 
	mainData.set(frequencyRes=frequencyRes)
	print 'fr=%f'%frequencyRes
	# Spectroscopy01
		
	#span01=max(span01,minimSpan01)
	qbSpecdata=Datacube('spectroscopy01 %f dBm, vcoil=%f'%(p,coil.current()))
	onePointData.addChild(qbSpecdata)

	frequency01=qbSpec(fcenter=freqcenter_qb,fspan=span01,fstep=0.0005,power=p,fReadout=frequencyRes,data=qbSpecdata)		
	mainData.set(frequency01=frequency01)
	print 'f01=%f'%frequency01
	
	# Rabi
	
	Rabidata=Datacube('rabi %f dBm, frequency=%f'%(p+10,frequency01))
	onePointData.addChild(Rabidata)
	Rabistop=1000
	Rabistart=0
	Rabistep=10
	piRabi= Rabi(fQubit=frequency01,pQubit=p+10,fRes=frequencyRes,pRes=4,start=Rabistart,stop=Rabistop,step=Rabistep,data=Rabidata)
	print 'pi pulse=%f ns'%piRabi
	mainData.set(piRabi=piRabi)
	if 5*piRabi>Rabistop:
		pNext=p+3
	elif 10*piRabi<Rabistop:
		pNext=p-3
	else:
		pNext=p
	#T1
	
	T1data=Datacube('t1 %f dBm, frequency=%f, qubitPulse=%f ns'%(p+10,frequency01,piRabi))
	onePointData.addChild(T1data)
	T1start=0
	T1stop=int(4*T1est)
	T1step=T1stop/40
	T1=T1Meas(fQubit=frequency01,pQubit=p+10,fRes=frequencyRes,pRes=4,piRabi=piRabi,start=T1start,stop=T1stop,step=T1step,data=T1data)
	T1est=T1
	print 'T1=%f ns'%T1
	mainData.set(T1=T1)
	mainData.commit()
	p=pNext
	# finish
	mainData.savetxt()

##
print piRabi


