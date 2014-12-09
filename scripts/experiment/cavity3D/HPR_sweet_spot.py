#imports
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
fsp=Manager().getInstrument('fsp')
pg_cav=Manager().getInstrument('PG_Cavity')
pg_cav_sw=Manager().getInstrument('PG_Cavity_switch')
attenuator=Manager().getInstrument('Yoko3')

######################
########## Shape for the cavity pulse
############

shape=zeros(20000)
shape[8000:10020]=1
shape[10021:11000]=0.1

#######################################################################
####### AUTOMATIC MEASUREMENT OF T1 VS COIL CURRENT
#######################################################################
## Telegraph
def telegraph(x0,x):
	if (x<x0):
		y=0
	else: y=1
	return y
## switchingProb
def switchingProb(nSegments=1000,channel=1,threshold="auto"):
	wantedChannel=2**(channel-1)
	segmentsPerAcq=acqiris("_params['numberOfSegments']")
	nLoops=nSegments/segmentsPerAcq
	acqiris.AcquireTransferV4(transferAverage=False,nLoops=nLoops,wantedChannels=wantedChannel)
	acqiris("DLLMath1Module.meanOfLastWaveForms("+str(wantedChannel)+")")
	acqiris("DLLMath1Module.aboveThresholdFrequencyProperty(propertyArray='mean',targettedWaveform="+str(wantedChannel)+",threshold="+str(threshold)+")")
	return acqiris("DLLMath1Module.aboveThresholdFrequencyArray["+str(channel-1)+"]")
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
	if extremum!="max": index=0
	(xExtr,yExtr)=sorted(zip(x,y),key = lambda t: t[1])[index]
	return xExtr,yExtr

## Estimate period
def estimatePeriod(y):
	fft=numpy.fft.rfft(y)
	fft[0]=0
	return len(y)/argmax(fft)

## fit Rabi
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

## fit T1
def fitT1(x,y):
	# initial guessing
	pi=[max(y),mean(y),20000]
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
def setAWG(spp=1,qb_pulse=2000,res_pulse=5000,delay=20,bool_shape=False,cav_shape_start=8000,cav_shape_length=20,level_mixer=0.1,bool_gauss=False,sigma=500,bool_sin=False,rise=100): #nanoseconds per point
	samplRate=1e9/spp
	reprate=samplRate/20000
	AWG.setRepetitionRate(reprate)
	if bool_shape:
		shape=zeros(20000)
		shape[cav_shape_start:(10000+cav_shape_length)]=1
		shape[(10000+cav_shape_length):(10000+res_pulse)]=level_mixer
		pg_cav.clearPulse()
		pg_cav.generatePulse(frequency=mw_cav.frequency(), shape=shape,useCalibration=False)
		pg_cav.sendPulse()
	else:
		if bool_sin:
			shape=sinrise(10000+delay,rise,res_pulse,amplitude=level_mixer)
			pg_cav.clearPulse()
			pg_cav.generatePulse(frequency=mw_cav.frequency(), shape=shape,useCalibration=False)
			pg_cav.sendPulse()
		else:
			shape=zeros(20000)
			shape[cav_shape_start:(10000+res_pulse)]=level_mixer
			pg_cav.clearPulse()
			pg_cav.generatePulse(frequency=mw_cav.frequency(), shape=shape,useCalibration=False)
			pg_cav.sendPulse()
	pg_qb.clearPulse()
	pg_qb.generatePulse(duration=qb_pulse/spp, frequency=mw_qb.frequency(), DelayFromZero=10000-qb_pulse/spp-delay/spp,useCalibration=False)
	pg_qb.sendPulse()
	pg_cav_sw.clearPulse()
	pg_cav_sw.generatePulse(duration=res_pulse/spp, frequency=mw_cav.frequency(), DelayFromZero=10000-100,useCalibration=False)
	pg_cav_sw.sendPulse()
	
## Gaussian Function
def gaussianPulse(sigma,delay,amplitude=1.):
        """
        Return a gaussian Shape, using length as sigman and delay as time at maximum
        """
        def gaussianFunction(t,t0,sigma,amp=1):
          v= amp*numpy.exp(-(t-float(t0))**2/(2*sigma**2))
          return v

        shape=zeros(20000)
        for t in range(int(delay-2*sigma),int(delay+2*sigma)):
            shape[t]=gaussianFunction(t,delay,sigma,amp=amplitude)
        print mean(shape)
        return shape	
        
## Sinus Function
def SinusFunction(t,t0,dt,amp=1):
	v= amp*numpy.sin(math.pi*(t-float(t0))/(2*dt))
	return v
def sinrise(delay,rise,length_tot,amplitude=1.):
	shape=zeros(20000)
	for t in range(int(delay),int(delay+rise)):
		shape[t]=SinusFunction(t,delay,rise,amp=amplitude)
	shape[int(delay+rise):int(delay+length_tot)]=1
	return shape


## Measure IQ
def measure(nLoops=1,wantedChannels=3,iOffset=0,qOffset=0,amplitudeOnly=False,convertToAmpPhase=False,averageOverSequence=False):
	# acquire and transfer the sequence of traces for the selected channels
	acqiris.AcquireTransferV4(transferAverage=False,nLoops=nLoops,wantedChannels=wantedChannels)
	acqiris("DLLMath1Module.meanOfLastWaveForms("+str(wantedChannels)+")")		# calculate the mean of each trace in the sequence 
	channels= acqiris("DLLMath1Module.mean")	# get the sequence of means for the selected channels
	# get the indexes of selected channels
	indexes= [i for i,x in enumerate([1&wantedChannels!=0,2&wantedChannels!=0,4&wantedChannels!=0,8&wantedChannels!=0]) if x ==True]
	channels=[channels[indexes[0]],channels[indexes[1]]] # keep only the first and second selected channels as I and Q
	if iOffset!=0 : channels[0]=channels[0]-iOffset  	 # subtract I and Q offset if necessary
	if qOffset!=0 : channels[1]=channels[1]-qOffset
	if not(amplitudeOnly):
		if averageOverSequence:								 # average over sequence if requested
			channels=[numpy.mean(channels[0]),numpy.mean(channels[1])]
		if convertToAmpPhase :									 # convert I and Q into Amp and Phase
			channels=[sqrt((channels[0])**2+(channels[1])**2),arctan(channels[1]/channels[0])]		# calculate amplitude and phase
	else:
		channels=sqrt((channels[0])**2+(channels[1])**2)		# calculate amplitude and phase		
		if averageOverSequence:								 # average over sequence if requested
			channels=numpy.mean(channels)
	# returns [I,Q] or [Amp, phi] or
	# [array([I1,I2,I3,...],array([Q1,Q2,Q3,...])] or  [array([A1,A2,A3,...],array([phi1,phi2,phi3,...])] or
	# Amp or array([A1,A2,A3,...]
	return channels 
	
## ResSpec(fcenter=7.0578,fspan=0.015,fstep=0.0001,power=4,data='')
def ResSpec(fcenter=1,fspan=1,fstep=0.1,power=1,data='',nLoops=5,qb_mw_bool=False,cav_pulse=5000,qb_pulse=2000,spp=1,bool_shape=False,cav_shape_start=8000,cav_shape_length=50,level=1):
	if data=='':	
		data=Datacube('ResSpec')
		DataManager().addDatacube(data)
	setAWG(spp,qb_pulse,cav_pulse,0,bool_shape=bool_shape,cav_shape_start=cav_shape_start,cav_shape_length=cav_shape_length,level_mixer=level)
	
	if qb_mw_bool:
		mw_qb.turnOn()
	else:
  		mw_qb.turnOff()
	mw_cav.turnOn()
	attenuator.setVoltage(power)
	frequencyLoop=SmartLoop(fcenter-fspan/2,fstep,fcenter+fspan/2,name='resonator frequency')
	coil.turnOn()
	time.sleep(1)
	for f in frequencyLoop:
		mw_cav.setFrequency(f)
		[amp,phase]=measure(nLoops=nLoops,wantedChannels=3,iOffset=0,qOffset=0,amplitudeOnly=False,convertToAmpPhase=True,averageOverSequence=True)
		data.set(f=f,amp=amp,phase=phase)
		data.commit()
	#fit
	coil.turnOff()
	frequencyRes=xOfYExtremum(data['f'],data['amp'])[0]	
	data.savetxt()	
	return frequencyRes

## qbSpec(fcenter=7.563,fspan=0.16,fstep=0.001,power=-20,fReadout=7.0578,pReadout=4,data='')
def qbSpec(fcenter=1,fspan=1,fstep=0.1,power=1,fReadout=1,pReadout=4,data='',nLoops=50,cav_pulse=5000,qb_pulse=2000,spp=1,direction='down',bool_shape=False,cav_shape_start=8000,cav_shape_length=50,level=1):
	if data=='':	
		data=Datacube('ResQubit')
		DataManager().addDatacube(data)
	setAWG(spp,qb_pulse,cav_pulse,0,bool_shape=bool_shape,cav_shape_start=cav_shape_start,cav_shape_length=cav_shape_length,level_mixer=level)
	mw_qb.turnOn()
	mw_qb.setPower(power)
	mw_cav.setFrequency(fReadout)
	attenuator.setVoltage(pReadout)
	frequencyLoop=SmartLoop(fcenter-fspan/2,fstep,fcenter+fspan/2,name='qubit frequency')
	coil.turnOn()
	time.sleep(1)
	for f in frequencyLoop:
		mw_qb.setFrequency(f)
		[amp,phase]=measure(nLoops=nLoops,wantedChannels=3,iOffset=0,qOffset=0,amplitudeOnly=False,convertToAmpPhase=True,averageOverSequence=True)
		data.set(f=f,amp=amp,phase=phase)
		data.commit()
	coil.turnOff()
	[dy,frequency01,dx,y0], Lorfit, Lorfitguess =fitLorentzian(data['f'],data['amp'],width=0.0005,direction=direction)
	data.createColumn('Lorfitguess',Lorfitguess)
	data.createColumn('Lorfit',Lorfit)		
	data.savetxt()
	return frequency01
## Rabi(fQubit=7.563,pQubit=-10,fRes=7.0578,pRes=4,start=0,stop=500,step=5,data='')
def Rabi(fQubit=1,pQubit=-20,fRes=1,pRes=4,start=0,stop=1000,step=10,data=''):
	if data=='':	
		data=Datacube('Rabi')
		DataManager().addDatacube(data)
	mw_qb.turnOn()
	mw_qb.setPower(pQubit)
	mw_qb.setFrequency(fQubit)
	mw_cav.setFrequency(fRes)
	attenuator.setVoltage(pRes)
	durations=SmartLoop(start,step,stop,name="durations")
	coil.turnOn()
	time.sleep(1)
	for duration in durations:
		setAWG(spp=1,qb_pulse=duration,res_pulse=5000,delay=20)
		time.sleep(0.1)
		acqiris.AcquireTransferV4(transferAverage=True,nLoops=50,wantedChannels=3)
		acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
		chanels= acqiris("DLLMath1Module.mean")
		amp=sqrt((chanels[0])**2+(chanels[1])**2)
		phase=arctan(chanels[0]/chanels[1])
		data.set(duration=duration,i=chanels[0],q=chanels[1],amp=amp,phase=phase)
		data.commit()
		
	coil.turnOff()
	fftperiod= estimatePeriod(data['amp'])
	[y0,dy,pi2Rabi,dx],yfit=fitRabi(data['duration'],data['amp'],period=fftperiod*step,x0=100)
	data.createColumn("Rabifit",yfit)
	piRabi=pi2Rabi/2
	return piRabi

## Estimate period V2
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
## T1 measurement
def T1Meas(fQubit=1,pQubit=-20,fRes=1,pRes=4,piRabi=50,start=0,stop=1000,step=10,data=''):
	if data=='':	
		data=Datacube('T1')
		DataManager().addDatacube(data)
	mw_qb.turnOn()
	mw_qb.setPower(pQubit)
	mw_qb.setFrequency(fQubit)
	mw_cav.setFrequency(fRes)
	attenuator.setVoltage(pRes)
	spp=stop/10000+1
	delays=concatenate((arange(start,stop/4,step/2),arange(stop/4,stop*3/4,step*2),arange(stop*3/4,stop,step/2)))
	coil.turnOn()
	time.sleep(1)
	for delay in delays:
		setAWG(spp=spp,qb_pulse=piRabi,res_pulse=5000,delay=20+delay)
		time.sleep(0.1)
		acqiris.AcquireTransferV4(transferAverage=True,nLoops=50,wantedChannels=3)
		acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
		chanels= acqiris("DLLMath1Module.mean")
		amp=sqrt((chanels[0])**2+(chanels[1])**2)
		phase=arctan(chanels[0]/chanels[1])
		data.set(delay=delay,i=chanels[0],q=chanels[1],amp=amp,phase=phase)
		data.commit()
	coil.turnOff()
	[y0,dy,T1],yfit=fitT1(data['delay'],data['amp'])
	data.createColumn("T1fit",yfit)
	return T1





##############################
########

########  Resonator spectroscopy
coilCurrent=-0.010180
coil.setCurrent(coilCurrent)
coil.turnOn()

mainData=Datacube('Resonator_spectroscopy, Icoil=%f'%(coil.current()))                                         # main datacube whole flux modulation
DataManager().addDatacube(mainData)

# Low power Resonator
freqcenter_Res=7.11
spanRes=0.015
power=4
ResSpecdataLP=Datacube('spectroscopyRes LP %f V, Icoil=%f'%(power,coil.current()))             # create a child datacube for resonator
mainData.addChild(ResSpecdataLP)
frequencyRes=ResSpec(fcenter=freqcenter_Res,fspan=spanRes,fstep=0.0001,power=power,data=ResSpecdataLP) 
coil.turnOff()
print frequencyRes

# High power Resonator
freqcenter_Res=7.0795
spanRes=0.015
power=0
ResSpecdataHP=Datacube('spectroscopyRes HP %f V, Icoil=%f'%(power,coil.current()))             # create a child datacube for resonator
mainData.addChild(ResSpecdataHP)
frequencyRes=ResSpec(fcenter=freqcenter_Res,fspan=spanRes,fstep=0.0001,power=power,data=ResSpecdataHP) 
coil.turnOff()
print frequencyRes
#mainData.set(frequencyRes=frequencyRes)

########  HPR power scan VVA ground state
coilCurrent=-0.010180
coil.setCurrent(coilCurrent)
coil.turnOn()

data=Datacube('CavityResponse_noshape_g3')
DataManager().addDatacube(data)
frequency=7.0795
mw_cav.setFrequency(frequency)
setAWG(spp=1,qb_pulse=1000,res_pulse=1000,delay=00,bool_shape=False,cav_shape_start=10000,cav_shape_length=10,level_mixer=1,bool_sin=True,rise=500)

VVAs=arange(0,5,0.1)
mw_qb.turnOff()

probReadout=False
threshold=0.05
iOff=0
qOff=0
for VVA in reversed(VVAs):
	print"VVAVoltage=%f"%VVA
	attenuator.setVoltage(VVA)
	time.sleep(0.5)
	if probReadout==False:
		acqiris.AcquireTransferV4(transferAverage=True,nLoops=10,wantedChannels=3)
		acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
		chanels= acqiris("DLLMath1Module.mean")
		amp=sqrt((chanels[0]-iOff)**2+(chanels[1]-qOff)**2)
		data.set(VVA=VVA,i=chanels[0],q=chanels[1],amp=amp)
		data.commit()
	else:
		prob_e=switchingProb(channel=2,nSegments=10000,threshold=threshold)
		data.set(VVA=VVA,prob_e=prob_e)	
		data.commit()
data.savetxt()
coil.turnOff()

########  HPR power scan mixer_level ground state
coilCurrent=-0.010180
coil.setCurrent(coilCurrent)
coil.turnOn()
power=2.5
data=Datacube('CavityResponse_shape_g4, VVA%f'%power)
DataManager().addDatacube(data)
frequency=7.0795
mw_cav.setFrequency(frequency)

attenuator.setVoltage(power)
levels=arange(0,1,0.05)
mw_qb.turnOff()

probReadout=False
threshold=0.05
iOff=0
qOff=0
for level in levels:
	print"LevelVoltage=%f"%level
	setAWG(spp=1,qb_pulse=1000,res_pulse=1000,delay=00,bool_shape=True,cav_shape_start=10000,cav_shape_length=60,level_mixer=level)

	time.sleep(0.5)
	if probReadout==False:
		acqiris.AcquireTransferV4(transferAverage=True,nLoops=10,wantedChannels=3)
		acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
		chanels= acqiris("DLLMath1Module.mean")
		amp=sqrt((chanels[0]-iOff)**2+(chanels[1]-qOff)**2)
		data.set(level=level,i=chanels[0],q=chanels[1],amp=amp)
		data.commit()
	else:
		prob_e=switchingProb(channel=2,nSegments=10000,threshold=threshold)
		data.set(VVA=VVA,prob_e=prob_e)	
		data.commit()
data.savetxt()
coil.turnOff()

########  HPR power scan VVA e state
coilCurrent=-0.010180
coil.setCurrent(coilCurrent)
coil.turnOn()

data=Datacube('CavityResponse_e2')
DataManager().addDatacube(data)
mw_qb.turnOn()
qbfrequency=6.8387
mw_qb.setPower(-20)
pipulse=385
pg_qb.clearPulse()
pg_qb.generatePulse(frequency=qbfrequency, duration=pipulse, DelayFromZero=10000-pipulse, useCalibration=False)
pg_qb.sendPulse()


frequency=7.081
mw_cav.setFrequency(frequency)
setAWG(spp=1,qb_pulse=pipulse,res_pulse=1000,delay=0,bool_shape=False,cav_shape_start=10000,cav_shape_length=10,level_mixer=1,bool_sin=True,rise=500)

VVAs=arange(0,5,0.1)

probReadout=False
threshold=0.05
iOff=0
qOff=0
for VVA in reversed(VVAs):
	print"VVAVoltage=%f"%VVA
	attenuator.setVoltage(VVA)
	time.sleep(0.5)
	if probReadout==False:
		acqiris.AcquireTransferV4(transferAverage=True,nLoops=10,wantedChannels=3)
		acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
		chanels= acqiris("DLLMath1Module.mean")
		amp=sqrt((chanels[0]-iOff)**2+(chanels[1]-qOff)**2)
		data.set(VVA=VVA,i=chanels[0],q=chanels[1],amp=amp)
		data.commit()
	else:
		prob_e=switchingProb(channel=2,nSegments=10000,threshold=threshold)
		data.set(VVA=VVA,prob_e=prob_e)	
		data.commit()
data.savetxt()
coil.turnOff()

########  HPR power scan mixer_level e state
coilCurrent=-0.010180
coil.setCurrent(coilCurrent)
coil.turnOn()

power=2.5
data=Datacube('CavityResponse_e_mixerlevel_2, level:%f'%power)

DataManager().addDatacube(data)
mw_qb.turnOn()
qbfrequency=6.8387
mw_qb.setPower(-20)
pipulse=385
pg_qb.clearPulse()
pg_qb.generatePulse(frequency=qbfrequency, duration=pipulse, DelayFromZero=10000-pipulse, useCalibration=False)
pg_qb.sendPulse()


frequency=7.0795
mw_cav.setFrequency(frequency)

attenuator.setVoltage(power)
levels=arange(0,1,0.05)
mw_qb.turnOn()

probReadout=False
threshold=0.05
iOff=0
qOff=0
for level in levels:
	print"LevelVoltage=%f"%level
	setAWG(spp=1,qb_pulse=pipulse,res_pulse=1000,delay=0,bool_shape=True,cav_shape_start=10000,cav_shape_length=60,level_mixer=level)

	time.sleep(0.5)
	if probReadout==False:
		acqiris.AcquireTransferV4(transferAverage=True,nLoops=10,wantedChannels=3)
		acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
		chanels= acqiris("DLLMath1Module.mean")
		amp=sqrt((chanels[0]-iOff)**2+(chanels[1]-qOff)**2)
		data.set(level=level,i=chanels[0],q=chanels[1],amp=amp)
		data.commit()
	else:
		prob_e=switchingProb(channel=2,nSegments=10000,threshold=threshold)
		data.set(VVA=VVA,prob_e=prob_e)	
		data.commit()
data.savetxt()
coil.turnOff()

########  qb spectroscopy HPR
coilCurrent=-0.010180
coil.setCurrent(coilCurrent)
coil.turnOn()

mainData=Datacube('Qb_spec_ge_shape_HPR_5, Icoil=%f'%(coilCurrent))                                         # main datacube whole flux modulation
DataManager().addDatacube(mainData)

# High power spectroscopy
freqcenter_Res=7.07975
pread=1.7
freqcenter_Qb=6.838
spanQb=0.030

frequencyQb=qbSpec(fcenter=freqcenter_Qb,fspan=spanQb,fstep=0.0001,power=-20,fReadout=freqcenter_Res,pReadout=pread,data=mainData,nLoops=2,spp=1,qb_pulse=500,cav_pulse=1000,direction='up',bool_shape=True,cav_shape_start=10000,cav_shape_length=20,level=0.15)
coil.turnOff()
print frequencyQb

########  qb spectroscopy LPR
coilCurrent=-0.010180
coil.setCurrent(coilCurrent)
coil.turnOn()

mainData=Datacube('Qb_spec_ge_LPR_5, Icoil=%f'%(coilCurrent))                                         # main datacube whole flux modulation
DataManager().addDatacube(mainData)

# High power spectroscopy
freqcenter_Res=7.117
pread=4
freqcenter_Qb=6.85
spanQb=0.030

frequencyQb=qbSpec(fcenter=freqcenter_Qb,fspan=spanQb,fstep=0.0002,power=-20,fReadout=freqcenter_Res,pReadout=pread,data=mainData,nLoops=10,spp=1,qb_pulse=500,cav_pulse=1000,direction='down')
coil.turnOff()
print frequencyQb

######## Rabi LPR
coilCurrent=-0.010220
coil.setCurrent(coilCurrent)
coil.turnOn()

data=Datacube('RabiLPR_1')
DataManager().addDatacube(data)
attenuator.setVoltage(4)

spp=1
frequencycav=7.1084
mw_cav.setFrequency(frequencycav)
cav_pulse=1000/spp
pg_cav.clearPulse()
pg_cav.generatePulse(frequency=frequencycav, duration=cav_pulse, DelayFromZero=10000, useCalibration=False)
pg_cav.sendPulse()

frequencyqb=6.7986
durations=arange(0,800,10)
mw_qb.setPower(-20)
mw_qb.turnOn()
iOff=0
qOff=0
for duration in durations:
	print"duration=%f"%duration 
	pg_qb.clearPulse()
	pg_qb.generatePulse(frequency=frequencyqb, duration=duration, DelayFromZero=10000-duration, useCalibration=False)
	pg_qb.sendPulse()
	
	time.sleep(0.5)
	acqiris.AcquireTransferV4(transferAverage=True,nLoops=2,wantedChannels=3)
	acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
	chanels= acqiris("DLLMath1Module.mean")
	amp=sqrt((chanels[0]-iOff)**2+(chanels[1]-qOff)**2)
	data.set(duration=duration,i=chanels[0],q=chanels[1],amp=amp)
	data.commit()
data.savetxt() 
######## Rabi HPR
coilCurrent=-0.010180
coil.setCurrent(coilCurrent)
coil.turnOn()

data=Datacube('RabiHPR_1')
DataManager().addDatacube(data)
attenuator.setVoltage(1.8)

spp=1
frequencycav=7.0795
mw_cav.setFrequency(frequencycav)
cav_pulse=1000/spp
pg_cav.clearPulse()
pg_cav.generatePulse(frequency=frequencycav, duration=cav_pulse, DelayFromZero=10000, useCalibration=False)
pg_cav.sendPulse()

frequencyqb=6.8385
durations=arange(0,1500,20)
mw_qb.setPower(-20)
mw_qb.turnOn()
iOff=0
qOff=0
for duration in durations:
	print"duration=%f"%duration 
	pg_qb.clearPulse()
	pg_qb.generatePulse(frequency=frequencyqb, duration=duration, DelayFromZero=10000-duration, useCalibration=False)
	pg_qb.sendPulse()
	
	time.sleep(0.5)
	acqiris.AcquireTransferV4(transferAverage=True,nLoops=2,wantedChannels=3)
	acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
	chanels= acqiris("DLLMath1Module.mean")
	amp=sqrt((chanels[0]-iOff)**2+(chanels[1]-qOff)**2)
	data.set(duration=duration,i=chanels[0],q=chanels[1],amp=amp)
	data.commit()
data.savetxt() 


########  Resonator spectroscopy for qb in g state
coilCurrent=-0.010180
coil.setCurrent(coilCurrent)
coil.turnOn()

mainData=Datacube('Res_spec_qb_g_shape_1, Icoil=%f'%(coilCurrent))                                         # main datacube whole flux modulation
DataManager().addDatacube(mainData)

# Low power Resonator
freqcenter_Res=7.095
spanRes=0.06
power=1.5

frequencyRes=ResSpec(fcenter=freqcenter_Res,fspan=spanRes,fstep=0.0005,power=power,data=mainData,qb_mw_bool=False,nLoops=10,spp=1,qb_pulse=pipulse,cav_pulse=1000,bool_shape=True,cav_shape_start=10000,cav_shape_length=10,level=0.075)

coil.turnOff()
print frequencyRes

########  Resonator spectroscopy for qb in e state
coilCurrent=-0.010180
coil.setCurrent(coilCurrent)
coil.turnOn()


# Low power Resonator
freqcenter_Res=7.095
spanRes=0.06
power=1.6

mainData=Datacube('Res_spec_qb_e_20, Icoil=%f, VVA=%f'%(coilCurrent,power))                                         # main datacube whole flux modulation
DataManager().addDatacube(mainData)


qbfrequency=6.8381
mw_qb.setPower(-20)
pipulse=385
pg_qb.clearPulse()
pg_qb.generatePulse(frequency=qbfrequency, duration=pipulse, DelayFromZero=10000-pipulse, useCalibration=False)
pg_qb.sendPulse()
frequencyRes=ResSpec(fcenter=freqcenter_Res,fspan=spanRes,fstep=0.0005,power=power,data=mainData,qb_mw_bool=True,nLoops=10,spp=1,qb_pulse=pipulse,cav_pulse=1000)
coil.turnOff()
print frequencyRes
########  Resonator spectroscopy scan VVA for qb in g state
coilCurrent=-0.010180
coil.setCurrent(coilCurrent)
coil.turnOn()

mainData=Datacube('Res_spec_power_scan_qb_g_1, Icoil=%f'%(coilCurrent))                                # main datacube whole flux modulation
DataManager().addDatacube(mainData)

# Variable power Resonator
freqcenter_Res=7.095
spanRes=0.06

VVAs=arange(1.5,4.6,0.5)
probReadout=True
threshold=0.1
for VVA in reversed(VVAs):
	print"VVAVoltage=%f"%VVA
	attenuator.setVoltage(VVA)
	time.sleep(0.5)
	dataVVA=Datacube('VVA=%f'%(VVA))  
	mainData.addChild(dataVVA)
	mainData.set(VVA=VVA)
	frequencyRes=ResSpec(fcenter=freqcenter_Res,fspan=spanRes,fstep=0.0005,power=VVA,data=dataVVA,qb_mw_bool=False,nLoops=10,spp=1,qb_pulse=pipulse,cav_pulse=1000)
	coil.turnOff()
	print frequencyRes
	
########  Resonator spectroscopy scan VVA for qb in e state
coilCurrent=-0.010180
coil.setCurrent(coilCurrent)
coil.turnOn()

mainData=Datacube('Res_spec_power_scan_qb_e_1, Icoil=%f'%(coilCurrent))                                # main datacube whole flux modulation
DataManager().addDatacube(mainData)

# Variable power Resonator
freqcenter_Res=7.095
spanRes=0.06

qbfrequency=6.8381
mw_qb.setPower(-20)
pipulse=385
pg_qb.clearPulse()
pg_qb.generatePulse(frequency=qbfrequency, duration=pipulse, DelayFromZero=10000-pipulse, useCalibration=False)
pg_qb.sendPulse()

VVAs=arange(1.5,4.6,0.5)
for VVA in reversed(VVAs):
	print"VVAVoltage=%f"%VVA
	attenuator.setVoltage(VVA)
	time.sleep(0.5)
	dataVVA=Datacube('VVA=%f'%(VVA))  
	mainData.addChild(dataVVA)
	mainData.set(VVA=VVA)
	frequencyRes=ResSpec(fcenter=freqcenter_Res,fspan=spanRes,fstep=0.0002,power=VVA,data=dataVVA,qb_mw_bool=True,nLoops=10,spp=1,qb_pulse=pipulse,cav_pulse=1000)
	coil.turnOff()
	print frequencyRes

	###########################

## calibration of the attenuation by the mixers

mainData=Datacube('calibration attenuation_3')                                # main datacube whole flux modulation
DataManager().addDatacube(mainData)

data_attenuator=Datacube('global_attenuation')  
mainData.addChild(data_attenuator)
setAWG(spp=1,qb_pulse=2000,res_pulse=10000,delay=20,bool_shape=False,cav_shape_start=10000,cav_shape_length=500,level_mixer=1)
VVAs=arange(0,5,0.2)
for VVA in reversed(VVAs):
	attenuator.setVoltage(VVA)
	time.sleep(5)
	power=fsp.getValueAtMarker()
	data_attenuator.set(VVA=VVA,power=power)
	data_attenuator.commit()
data_attenuator.savetxt() 
	
data_mixer=Datacube('mixer_attenuation')  
mainData.addChild(data_mixer)
setAWG(spp=1,qb_pulse=2000,res_pulse=10000,delay=20,bool_shape=False,cav_shape_start=10000,cav_shape_length=500,level_mixer=1)
levels=arange(0.5,1,0.05)
attenuator.setVoltage(0)
for level in reversed(levels):
	setAWG(spp=1,qb_pulse=2000,res_pulse=10000,delay=0,bool_shape=True,cav_shape_start=10000,cav_shape_length=500,level_mixer=level)
	time.sleep(5)
	power=fsp.getValueAtMarker()
	data_mixer.set(level=level,power=power)
	data_mixer.commit()
data_mixer.savetxt() 

##
attenuator.setVoltage(1.9)
setAWG(spp=1,qb_pulse=385,res_pulse=2000,delay=00,bool_shape=False,cav_shape_start=10000,cav_shape_length=20,level_mixer=1,bool_sin=True,rise=1000)
mw_cav.setFrequency(7.078)
mw_qb.turnOn()
coil.turnOn()
############################
coil.turnOn()
pg_cav.clearPulse()
pg_cav.generatePulse(duration=1000, frequency=7.0795, DelayFromZero=10000,useCalibration=False)
pg_cav.sendPulse()
attenuator.setVoltage(1)


##
# Resonator Spectroscopy	
ResSpecdata=Datacube('spectroscopyRes %f V, Icoil=%f'%(4,coil.current()))             # create a child datacube for resonator
onePointData.addChild(ResSpecdata)
frequencyRes=ResSpec(fcenter=freqcenter_Res,fspan=spanRes,fstep=0.0003,power=4,data=ResSpecdata) 
mainData.set(frequencyRes=frequencyRes)



#frequency01=5.637
span01=0.1
spanRes=0.03
#frequencyRes=7.0839
frequencyResBare=7.080
p=-10
T1est=6000
coilCurrents=concatenate((arange(-11.3e-3,-10.15e-3,0.05e-3),arange(-9.65e-3,-8.05e-3,0.05e-3),arange(-7.4e-3,-6.15e-3,0.05e-3)))
#coilCurrents=SmartLoop(-7.35e-3,0.05e-3,-6.5e-3)
for coilCurrent in coilCurrents:
	onePointData=Datacube("coilCurrent=%f"%coilCurrent)                            #create datacube a child for this flux
	mainData.addChild(onePointData)
	mainData.set(coilCurrent=coilCurrent)
  	coil.setCurrent(coilCurrent)                                                   #set the coil current
  	print "current %f"%coilCurrent 

	freqcenter_qb=fvsIcoil(coilCurrent)          								# calculated first parameters
	chi=0.09**2/(freqcenter_qb-frequencyResBare)
	freqcenter_Res=frequencyResBare-chi
	
	# Resonator Spectroscopy	
	ResSpecdata=Datacube('spectroscopyRes %f V, Icoil=%f'%(4,coil.current()))             # create a child datacube for resonator
	onePointData.addChild(ResSpecdata)
	frequencyRes=ResSpec(fcenter=freqcenter_Res,fspan=spanRes,fstep=0.0003,power=4,data=ResSpecdata) 
	mainData.set(frequencyRes=frequencyRes)

	# Spectroscopy01
		
	#span01=max(span01,minimSpan01)
	qbSpecdata=Datacube('spectroscopy01 %f dBm, vcoil=%f'%(p,coil.current()))
	onePointData.addChild(qbSpecdata)

	frequency01=qbSpec(fcenter=freqcenter_qb,fspan=span01,fstep=0.0005,power=p,fReadout=frequencyRes,data=qbSpecdata)		
	mainData.set(frequency01=frequency01)
	
	# Rabi
	
	Rabidata=Datacube('rabi %f dBm, frequency=%f'%(p+10,frequency01))
	onePointData.addChild(Rabidata)
	Rabistop=500
	Rabistart=0
	Rabistep=10
	piRabi= Rabi(fQubit=frequency01,pQubit=p+10,fRes=frequencyRes,pRes=4,start=Rabistart,stop=Rabistop,step=Rabistep,data=Rabidata)
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
	T1stop=int(6*T1est)
	T1step=T1stop/50
	T1=T1Meas(fQubit=frequency01,pQubit=p+10,fRes=frequencyRes,pRes=4,piRabi=piRabi,start=T1start,stop=T1stop,step=T1step,data=T1data)
	T1est=T1
	mainData.set(T1=T1)
	mainData.commit()
	p=pNext
	# finish
	mainData.savetxt()
	
	


	