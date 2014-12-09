#######################################################################
####### AUTOMATIC MEASUREMENT OF T1 VS COIL CURRENT
#######################################################################

## imports and instruments
import sys
import time
import numpy
import scipy
import scipy.optimize
print "Scipy version %s" %scipy.version.version
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
pg_cav=Manager().getInstrument('pg_cavity')
attenuator=Manager().getInstrument('Yoko3')

## function giving qubit frequency versus coil drive
def fvsIcoil(I):
	fmax=7.563
	Ioff=-0.0089
	Iperiod=6.72e-3
	f=fmax*sqrt(abs(cos((I-Ioff)*pi/Iperiod)))	
	return f

## Lorentzian pure function
def Lorenzian(y0,yAmp,x0,width):
	return lambda x: y0+yAmp/(1.0+pow(2.0*(x-x0)/width,2)) 

## Cosine pure function
def cosine(y0,yAmp,x0,period):
	return lambda x: y0+yAmp*cos(2*math.pi*(x-x0)/period)

## finding the closest point from a target
def closestXYofTargetX(x,y,xTarget):
	 position=min(range(len(x)), key=lambda i: abs(x[i]-xTarget))
	 return x[position],y[position],position,x[position]-xTarget 	

def closestXYofTargetY(x,y,yTarget):
	position=min(range(len(x)), key=lambda i: abs(y[i]-yTarget))
	return x[position],y[position],position,y[position]-yTarget

def firstXCrossTargetYFromAnEnd(x,y,yTarget=0,direction='leftToRight'):
	position=''
	if direction  =='leftToRight':
		if y[0]>yTarget:
			for i in range(len(y)): 
				if y[i]<=yTarget:
					position=i
					break
		else:
			for i in range(len(y)): 
				if y[i]>=yTarget:
					position=i
					break
	else: # right to left
		if y[-1]>yTarget:
			for i in range(len(y))[::-1]: 
				if y[i]<=yTarget:
					position=i
					break
		else: 
			for i in range(len(y))[::-1]: 
				if y[i]>=yTarget:
					position=i
					break
	if position!='':
		return x[position],y[position],position,y[position]-yTarget
	else:
		return  None
##
print firstXCrossTargetYFromAnEnd([1,2,3,4,5],[1,2,3,4,5],yTarget=2.1,direction='rightToLeft')
	
## finding an extremum 	
def extremum(x,y,minOrMax="max"):
	if minOrMax=='max':	extr=max(y)
	else:	extr=min(y)
	if 'numpy.ndarray' in str(type(y)): y=y.tolist()
	position=y.index(extr)
	return x[position],y[position],position

## Lorentzian fit of a dip or peak. Sorted y or sorted or unsorted x y accepted
def fitLorentzian(y,x='',initialBase='',initialHeight='',initialPosition='',initialWidth='',direction='',debug=False):
	""" fitLorentzian(y,x='',initialBase='',initialHeight='',initialPosition='',initialWidth='',direction='',debug=False) finds the fitting parameters of a lorentzian peak"""
	# generate the x if not defined
	indexes=''			# variable to store the initial order of x values
	if x=='':										
		x=range(len(y))							
	else: 				#sort x and y by ascending x but memorize the initial order
		indexes=argsort(x)
		x=[x[i] for i in indexes]
		y=[y[i] for i in indexes]	
	# analyze the shape by findind the min, max and mean values
	xMax,yMax,indexMax= extremum(x,y,minOrMax="max")
	xMin,yMin,indexMin= extremum(x,y,minOrMax="min")
	yMean=mean(y)
	# guess the direction (upward or downward peak)
	if direction=='':
		if yMax-yMean>yMean-yMin:	direction='up'
		else: 	direction='down'
	# find the peak value if position is imposed
	yLine=''
	if initialPosition!='' and initialHeight=='': yLine=numpy.interp(initialPosition, x,y)
	# find the baseline, positive or negative height, and position of the line
	if direction=='up':		# upward peak
		if initialBase=='': initialBase=yMin
		if initialHeight=='':
			if yLine=='':
				yLine=yMax
				initialHeight =yLine-yMin
		initialHeight=abs(initialHeight)
		if initialPosition=='':initialPosition=xMax
	else: 						#downward peak
		if initialBase=='': initialBase=yMax
		if initialHeight=='':
			if yLine=='':
				yLine=yMin
				initialHeight =yLine-yMax
		initialHeight=-abs(initialHeight)
		if initialPosition=='':initialPosition=xMin
	# guess the width
	if initialWidth=='' or initialWidth==0:
		indexLine=closestXYofTargetX(x,y,initialPosition)[2]			# find the index of the line in the x y lists
		middle=initialBase+initialHeight/2							# find the level at mid-height
		x1=x[0]
		if indexLine!=0:												# find the closest x on the left that corresponds to mid-height	
			x1=closestXYofTargetY(x[:indexLine],y[:indexLine],middle)[0]
		x2=x[-1]
		if indexLine!=len(x)-1:										# find the closest x on the right that corresponds to mid-height
			x2=closestXYofTargetY(x[indexLine:],y[indexLine:],middle)[0]							 
		initialWidth=x2-x1												# calulate the width
	paramGuess=[initialBase,initialHeight,initialPosition,initialWidth]
	LorentzGuess=Lorenzian(paramGuess[0],paramGuess[1],paramGuess[2],paramGuess[3])
	# fit
	def fitfunc(x,y0,yAmp,x0,width):
		return Lorenzian(y0,yAmp,x0,width)(x)							#y0+yAmp/(1.0+pow(2.0*(x-x0)/width,2)) 
	paramFit,fitCovariances =scipy.optimize.curve_fit(fitfunc, x, y,p0=paramGuess)
	LorentzFit=Lorenzian(paramFit[0],paramFit[1],paramFit[2],paramFit[3])
	if debug: 
		print "initial Lorentz guess: ",paramGuess 
		print "fit Lorentz result: ",paramFit
		clf()
		cla()
		pl=plot(x,y,'ro')
		xPlot=linspace(min(x),max(x),500)
		yGuessPlot=LorentzGuess(xPlot)
		yFitPlot=LorentzFit(xPlot)
		pl1=plot(xPlot,yGuessPlot)
		pl2=plot(xPlot,yFitPlot)
		show()
	if indexes!='': x=[x[i] for i in argsort(indexes)]	# reorder according to inital x if sorted	
	yFitGuess=[LorentzGuess(xv) for xv in x]
	yFit=[LorentzFit(xv) for xv in x]
	return paramFit,yFit,yFitGuess
##
fitLorentzian(gv.data['amp'],x=gv.data['f_GHz'],initialBase='',initialHeight='',initialPosition='',initialWidth='',direction='down',debug=True)
##
def areEquidistant(x,relativeTolerance=0.01):
	if type(x)=='list': x=array(x)		# convert to numpy array if necessary
	deltas=(np.roll(x,-1)-x)[:-1]			# calculate the x separations
	return max(deltas)/min(deltas)-1<=relativeTolerance	
## myFFT TO BE DONE
def myFFT(y,x='',forceX=False):
	if x=='':
		result=numpy.fft.rfft(y)	# use normal fft if only y is given
	else: 
		if not areEquidistant(x):
			numpy.interp(range(), x, y)[source]	
		result=1
	return result
##
def estimatePeriodByFFT(y,method='',debug=False):
	fft=numpy.fft.rfft(y)
	fft[0]=0	# cancel the zero frequency amplitude or signal mean
	if method=="fitLorentzian":
		[y0,yAmp,x0,width], LorentzFit, LorentzFitGuess = fitLorentzian(abs(fft),debug=False)
		estimatedPeriod=len(y)/x0
		if debug:
			clf()
			cla()
			pl1=plot(range(len(fft)),abs(fft),'ro')
			pl2=plot(range(len(fft)),LorentzFitGuess,'ro')
			Lor=Lorenzian(y0,yAmp,x0,width)
			yplot=Lor(linspace(0,len(fft),500))
			xplot=linspace(0,len(fft),500)
			pl1=plot(xplot,yplot)
			show()
	else:	estimatedPeriod=len(y)/argmax(fft) # default method returns the index of fft maximum
	if debug: print "Estimated period = ", estimatedPeriod
	return estimatedPeriod
##
def fitCosine(y,x='',initialY0='',initialYAmp='',initialX0='',initialPeriod='',debug=False):
	if x=='':										# if x not defined
		x=range(len(y))							# generate it
	yMax=max(y)
	yMin=min(y)
	if initialY0=='': initialY0=(yMax+yMin)/2
	if initialYAmp=='': initialYAmp=(yMax-yMin)/2
	if initialX0=='': initialX0=extremum(x,y,minOrMax="max")[0]
	if initialPeriod=='':							
		if areEquidistant(x):
			step=x[1]-x[0]
			initialPeriod=estimatePeriodByFFT(y,method='fitLorentzian',debug=debug)*step
		else: print "Non equidistant x => provide a value for the initialPeriod fitting parameter."		
	paramGuess=[initialY0,initialYAmp,initialX0,initialPeriod]
	cosineGuess=cosine(paramGuess[0],paramGuess[1],paramGuess[2],paramGuess[3])
	# fit
	def fitfunc(x,y0,yAmp,x0,period):
		return cosine(y0,yAmp,x0,period)(x)							#y0+yAmp*cos(2*math.pi*(x-x0)/period) 
	paramFit,fitCovariances =scipy.optimize.curve_fit(fitfunc, x, y,p0=paramGuess)
	cosineFit=cosine(paramFit[0],paramFit[1],paramFit[2],paramFit[3])
	if debug:
		print "initial cosine guess: ",paramGuess 
		print "fit cosine result: ",paramFit
		clf()
		cla()
		pl=plot(x,y,'ro')
		xPlot=linspace(min(x),max(x),500)
		yGuessPlot=cosineGuess(xPlot)
		yFitPlot=cosineFit(xPlot)
		pl1=plot(xPlot,yGuessPlot)
		pl2=plot(xPlot,yFitPlot)
		show()
	yFitGuess=[cosineGuess(xv) for xv in x]
	yFit=[cosineFit(xv) for xv in x]
	return paramFit,yFit,yFitGuess

##
def fitT1(y,x='',reverseX=False,reverseY=False,initialY0='',initialYAmp='',initialX0='',initialT1='',fitParamFlags=[True,True,True,True],debug=False):	
	indexes=''
	if x=='':	x=range(len(y))	# generate equidistant x=1,2,3,... if x not provided
	else: 							#sort x and y by ascending x but memorize the initial order in indexes
		indexes=argsort(x)
		x=[x[i] for i in indexes]
		y=[y[i] for i in indexes]	
	# initial guessing
	if initialY0=='':
		if reverseX : initialY0=y[0] 
		else: initialY0=y[-1]
	if initialYAmp=='':
		if reverseY: initialYAmp=y[0]-y[-1]
		else: initialYAmp=y[-1]-y[0]
	if initialX0=='':
		if reverseX : initialX0=x[-1]
		else: initialX0=x[0]
	if initialT1=='':
		if reverseX :initialT1=(x[0]-x[-1])/3
		else: initialT1=(x[-1]-x[0])/3
	def expFunc(x,y0,yAmp,x0,t1) : return y0+yAmp*exp(-(x-x0)/t1)
	paramGuess=[initialY0,initialYAmp,initialX0,initialT1]
	expFitGuess= lambda x :expFunc(x,initialY0,initialYAmp,initialX0,initialT1)
	if debug: 
		print "Guess [y0,yAmp,x0,t1 ]=",paramGuess
		clf()
		cla()
		pl=plot(x,y,'ro')
		xPlot=linspace(min(x),max(x),500)
		yGuessPlot=expFitGuess(xPlot)
		pl1=plot(xPlot,yGuessPlot)
		show()	
	for i in range (len(fitParamFlags)):												# if parameter is frozen
		if not fitParamFlags[i]:	print 'frozen parameters not implemented yet'	# modify the strings
	paramFit,fitCovariances =scipy.optimize.curve_fit(expFunc, x, y,p0=paramGuess)	# fit
	expFit=lambda x :expFunc(x,paramFit[0],paramFit[1],paramFit[2],paramFit[3])
	if debug: 
		print "fit Exp result: ",paramFit
		yFitPlot=expFit(xPlot)
		pl2=plot(xPlot,yFitPlot)
		show()
	if indexes!='': x=[x[i] for i in argsort(indexes)]	# reorder according to inital x order if sorted	
	yFitGuess=[expFitGuess(xv) for xv in x]
	yFit=[expFit(xv) for xv in x]
	return paramFit,yFit,yFitGuess
	
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
def resSpec(nLoops=1,fcenter=1,fspan=1,fstep=0.1,attenRes=4,data='',autoPlot=True,autoClear=False):
	if data=='':	
		data=Datacube('ResSpec')
		DataManager().addDatacube(data)
	if autoPlot:
		data.defineDefaultPlot("f_GHz","amp")
		data.defineDefaultPlot("f_GHz","ampFit")
		DataManager().addDatacube(data)
		DataManager().autoPlot(data,autoClear)
	#setAWG(sampTime_ns=1,qb_pulse_ns=2000,res_pulse_ns=3000,driveReadSep_ns=20)
	mw_qb.turnOff()
	mw_cav.turnOn()
	attenuator.setVoltage(attenRes)
	frequencyLoop=SmartLoop(fcenter-fspan/2,fstep,fcenter+fspan/2,name='resonator frequency')
	coil.turnOn()
	time.sleep(1)
	for f in frequencyLoop:
		mw_cav.setFrequency(f)
		[amp,phase]=measureIQ(nLoops=nLoops,averageOverSequence=True,convertToAmpPhase=True)
		data.set(f_GHz=f,amp=amp,phase=phase)
		data.commit()
	#fit
	coil.turnOff()
	[y0,yAmp,x0,width], ampFit, ampFitGuess = fitLorentzian(data['amp'],x=data['f_GHz'])
	data.createColumn('ampFitGuess',ampFitGuess)
	data.createColumn('ampFit',ampFit)		
	#frequencyRes=extremum(data['f'],data['amp'])[0]	
	data.savetxt()
	print "f_Res = %f"%x0	
	return x0

##
def qbSpec(nLoops=1,fcenter=1,fspan=1,fstep=0.1,power=1,fReadout='',attenRes='',data='',autoPlot=True,autoClear=False):
	if data=='':	
		data=Datacube('ResQubit')
		DataManager().addDatacube(data)
	if autoPlot:
		data.defineDefaultPlot("f_GHz","amp")
		data.defineDefaultPlot("f_GHz","ampFit")
		DataManager().addDatacube(data)
		DataManager().autoPlot(data,autoClear)
	#setAWG(sampTime_ns=1,qb_pulse_ns=2000,res_pulse_ns=3000,driveReadSep_ns=20)
	mw_qb.turnOn()
	mw_qb.setPower(power)
	if fReadout!='': mw_cav.setFrequency(fReadout)
	if attenRes!='':attenuator.setVoltage(attenRes)
	frequencyLoop=SmartLoop(fcenter-fspan/2,fstep,fcenter+fspan/2,name='qubit frequency')
	coil.turnOn()
	time.sleep(1)
	for f in frequencyLoop:
		mw_qb.setFrequency(f)
		[amp,phase]=measureIQ(nLoops=nLoops,averageOverSequence=True,convertToAmpPhase=True)
		data.set(f_GHz=f,amp=amp,phase=phase)
		data.commit()
	#coil.turnOff()
	#[y0,yAmp,x0,width], ampFit, ampFitGuess = fitLorentzian(data['amp'],x=data['f_GHz'])
	#data.createColumn('ampFitGuess',ampFitGuess)
	#data.createColumn('ampFit',ampFit)		
	x0=extremum(data['f_GHz'],data['amp'],minOrMax="min")[0]
	data.savetxt()
	print "f_qb = %f"%x0
	return x0

##
def rabiMeas(nLoops=1,fQubit='',pQubit='',fRes='',attenRes='',start=0,stop=1000,step=10,data='',autoPlot=True,autoClear=False):
	if data=='':	
		data=Datacube('Rabi')
		DataManager().addDatacube(data)
	if autoPlot:
		data.defineDefaultPlot("duration","amp")
		data.defineDefaultPlot("duration","rabiFit")
		DataManager().addDatacube(data)
		DataManager().autoPlot(data,autoClear)
	mw_qb.turnOn()
	if pQubit!='': mw_qb.setPower(pQubit)
	if fQubit!='': mw_qb.setFrequency(fQubit)
	if fRes!='': mw_cav.setFrequency(fRes)
	if attenRes!='': attenuator.setVoltage(attenRes)
	#coil.turnOn()
	time.sleep(1)
	durations=SmartLoop(start,step,stop,name="durations")
	for duration in durations:
		setAWG(sampTime_ns=2,qb_pulse_ns=duration,res_pulse_ns=1500,driveReadSep_ns=20)
		time.sleep(0.1)
		[amp,phase]=measureIQ(nLoops=nLoops,averageOverSequence=True,convertToAmpPhase=True)
		data.set(duration=duration,amp=amp,phase=phase)
		data.commit()	
	#coil.turnOff()
	[y0,yAmp,t0,rabiPeriod],yfit,yFitGuess=fitCosine(data['amp'],x=data['duration'])
	data.createColumn("rabiFit",yfit)
	piRabi=rabiPeriod/2
	print "Pi pulse length = %f ns"%piRabi	 
	return piRabi

##
def bestSamplingTime(qb_pulse_ns=10,driveReadSep0_ns=20,res_pulse_ns=1500,t1Estim_ns=10000,nT1Before=5,nT1After=5): # best sampling time to place a pi pulse and 4 T1 before the readout pulse
	best1= ceil((qb_pulse_ns+nT1Before*t1Estim_ns+driveReadSep0_ns)/10000.)
	best2= ceil((res_pulse_ns+nT1After*t1Estim_ns)/10000.)
	best=max(best1,best2)
	if best > piRabi/5: print 'Alert:step = ',best,'ns is longer than 20% of pi pulse'
	return best

##
qb_pulse_ns=20
res_pulse_ns=1500
nT1Before=5
nT1After=5
t1Estim_ns=10000
driveReadSep_ns=20+nT1Before*t1Estim_ns
best=bestSamplingTime2(qb_pulse_ns=qb_pulse_ns,res_pulse_ns=res_pulse_ns,t1Estim_ns=t1Estim_ns,nT1Before=nT1Before,nT1After=nT1After)
print best
setAWG(sampTime_ns=best,qb_pulse_ns=qb_pulse_ns,res_pulse_ns=res_pulse_ns,driveReadSep_ns=driveReadSep_ns)
##
setAWG(sampTime_ns=5,qb_pulse_ns=10,res_pulse_ns=1500,driveReadSep_ns=49980)
##
def t1Meas(nLoops=1,targettedPointAccuracy='',firstT1Try=10000,fQubit='',pQubit='',fRes='',attenRes='',piRabi=50,data='',autoPlot=True,autoClear=False,debug=False):
	if pQubit!='': mw_qb.setPower(pQubit)
	if fQubit!='': mw_qb.setFrequency(fQubit)
	if fRes!='': mw_cav.setFrequency(fRes)
	if attenRes!='': attenuator.setVoltage(attenRes)
	t1Estim=firstT1Try
	res_pulse_ns=1500
	#def bestSamplingTime(): # best sampling time to place a pi pulse and 4 T1 before the readout pulse
	#	return min(max(1,ceil((piRabi+(4*t1Estim+20))/10000)),ceil(piRabi/3))
	if data=='':	
		data=Datacube('T1')
		DataManager().addDatacube(data)
	if autoPlot:
		data.defineDefaultPlot("delay","amp")
		data.defineDefaultPlot("delay","T1fit")
		DataManager().addDatacube(data)
		DataManager().autoPlot(data,autoClear)
	# First step: Determine the signal for relaxed state by switching off the drive 
	delay=0
	sampTime_ns= bestSamplingTime(qb_pulse_ns=piRabi,driveReadSep0_ns=20,res_pulse_ns=1500,t1Estim_ns=t1Estim,nT1Before=4.5,nT1After=4.5)
	if debug:print "sampling time = %i"%sampTime_ns
	setAWG(sampTime_ns=sampTime_ns,qb_pulse_ns=piRabi,res_pulse_ns=res_pulse_ns,driveReadSep_ns=20+delay)
	mw_qb.turnOff()
	# proceed in two different ways depending if nLoops is to be calculated in order to reach a given accuracy on a single point
	if targettedPointAccuracy=='':	
		ampOff=measureIQ(nLoops=2*nLoops,averageOverSequence=True,convertToAmpPhase=True)[0]
	else:
		ampOffV=[]
		for i in range(5):
			ampOffV.append(measureIQ(nLoops=ceil(nLoops/2),averageOverSequence=True,convertToAmpPhase=True)[0])
		ampOff=numpy.mean(ampOffV)	
	if debug:
		if debug:
			print ampOffV
			print 'ampOff=%f'%ampOff	
	#data.set(delay=delay,ampOff=ampOff,relSig=0) # relative signal reduction is 0 by definition
	#data.commit()
	# Second step measure the signal just after excitation (zero time)
	mw_qb.turnOn()
	if targettedPointAccuracy=='':
		amp0=measureIQ(nLoops=2*nLoops,averageOverSequence=True,convertToAmpPhase=True)[0]
	else:
		amp0V=[]
		for i in range(5):
			amp0V.append(measureIQ(nLoops=ceil(nLoops/2),averageOverSequence=True,convertToAmpPhase=True)[0])
		amp0=numpy.mean(amp0V)
	deltaAmp=amp0-ampOff	# memorize the amplitude and direction of the signal decay
	if debug:
		print 'ampOn(Pi)=%f'%amp0
		print 'deltaAmp=%f'%deltaAmp
	data.set(delay=delay,amp=amp0,relSig=1)		# relative signal is 1 by definition
	data.commit()
	if targettedPointAccuracy!='': # we recalculate a better nLoop to reach the accuracy without loosing time
		accuracy1=sqrt((numpy.var(ampOffV)+numpy.var(amp0V))/2)/abs(deltaAmp)
		if debug : print 'measured accuracy with', int(nLoops/2),'loops =',accuracy1
		nLoops=min (max (ceil(nLoops/2*(accuracy1/targettedPointAccuracy)**2),1),100)
		print 'adapting nLoops to', nLoops,' to approach accuracy ',targettedPointAccuracy, 'in a minimum time'
	# Then we try to find a delay that corresponds to a decay between 30% and 60% as quickly as possible:
	# use firstT1Try as initial step, make an estimate of the next delay based on an exponential law,
	# but never multiply the time by a factor greater than 2 or smaller than 1/2.
	# Keep always the y axis direction initially measured.
	delay=t1Estim
	delayMax=delay
	delayMin=delay
	while True:
		sampTime_ns=bestSamplingTime()
		setAWG(sampTime_ns=sampTime_ns,qb_pulse_ns=piRabi,res_pulse_ns=res_pulse_ns,driveReadSep_ns=20+delay)
		amp=measureIQ(nLoops=nLoops,averageOverSequence=True,convertToAmpPhase=True)[0]
		relSig=(amp-ampOff)/deltaAmp
		if debug: print "sampling time = ",sampTime_ns, 'ampOn(',delay,')=',amp, ' relative signal = ', relSig
		data.set(delay=delay,amp=amp,relSig=relSig)
		data.commit()
		if relSig >0.6 :#and delay*2>delayMax :
			delay=2*delay
			delayMax=delay
		elif relSig <0.3 :#and delay/2>delayMin :
			delay=delay/2
			delayMin=delay
		else: 
			break
	# Estimate T1 from the closest point from 60% reduction
	x1,y1= closestXYofTargetY(data['delay'],data['relSig'],0.6)[0:2]
	t1Estim=x1/numpy.log(1/y1)
	if debug: print 't1Estim=%f'%t1Estim
	delays=array([0.25,0.5,1.,2.,2.5,3,3.7,3.8,3.9,4])*t1Estim
	for delay2 in delays:
		delay=delay2
		sampTime_ns=bestSamplingTime()
		delay= round(delay/sampTime_ns)*sampTime_ns
		setAWG(sampTime_ns=sampTime_ns,qb_pulse_ns=piRabi,res_pulse_ns=res_pulse_ns,driveReadSep_ns=20+delay)
		amp=measureIQ(nLoops=nLoops,averageOverSequence=True,convertToAmpPhase=True)[0]	
		relSig=(amp-ampOff)/deltaAmp
		if debug: print "sampling time = ",sampTime_ns, 'ampOn(',delay,')=',amp, ' relative signal = ', relSig
		data.set(delay=delay,amp=amp,relSig=relSig)
		data.commit()
	# sort the data by increasing delay before fitting
	dl=data['delay']
	indexes=argsort(dl)
	dl=[dl[i] for i in indexes]
	al= [data['amp'][i] for i in indexes]
	rsl= [data['relSig'][i] for i in indexes]
	data.removeColumns(['delay','amp','relSig'])
	data.createColumn('delay',dl)
	data.createColumn('amp',al)
	data.createColumn('relSig',rsl)
	# fit exponential with reverseY=true
	[y0,yAmp,x0,t1],yFit,yFitGuess=fitT1(data['amp'],x=data['delay'],reverseY=True)
	data.createColumn("T1fit",yFit)
	print "T1 = %f"%t1
	return t1

##
measureAtAWorkingPoint(coilCurrent=-10.8e-3,attenRes=4.5,stopRabi=100,stepRabi=2,firstT1Try=10000,data='')
## spectro Resonator + qubit + Rabi + T1
def measureAtAWorkingPoint(coilCurrent=-10.5e-3,attenRes=4.5,stopRabi=100,stepRabi=2,firstT1Try=10000,data=''):
	start = time.clock()
#create a datacube for this working point	 if none is specified
	if data=='':	
		data=Datacube("coilCurrent=%f"%coilCurrent)
		DataManager().addDatacube(data)
#initial parameters
	frequencyResBare=7.080
	coil.setCurrent(coilCurrent)
	coil.turnOn()
	freqCenter_qb=fvsIcoil(coilCurrent) 
	chi=0.09**2/(freqCenter_qb-frequencyResBare)
	freqCenter_Res=frequencyResBare-chi	
# resonator spectro
	setAWG(sampTime_ns=2,qb_pulse_ns=2000,res_pulse_ns=1500,driveReadSep_ns=20)
	resSpecData=Datacube('ResoSpec %f V, Icoil=%f'%(attenRes,coil.current()))
	data.addChild(resSpecData)
	frequencyRes=resSpec(nLoops=5,fcenter=freqCenter_Res,fspan=1.2*spanRes,fstep=0.0003,attenRes=attenRes,data=resSpecData,autoClear=True)
# qubit spectro
	setAWG(sampTime_ns=2,qb_pulse_ns=12000,res_pulse_ns=1500,driveReadSep_ns=20)
	qbSpecData=Datacube('spectroscopy01 %f dBm, vcoil=%f'%(p,coil.current()))
	data.addChild(qbSpecData)
	frequency01=qbSpec(nLoops=5,fcenter=freqCenter_qb,fspan=0.9*span01,fstep=0.00025,power=p-10,fReadout=frequencyRes,attenRes=attenRes,data=qbSpecData)
# Rabi oscillation
	pQubit=p+26
	setAWG(sampTime_ns=2,qb_pulse_ns=0,res_pulse_ns=1500,driveReadSep_ns=20)
	rabiData=Datacube('rabi %f dBm, frequency=%f'%(p+10,frequency01))
	data.addChild(rabiData)
	piRabi=rabiMeas(nLoops=20,fQubit=frequency01,pQubit=pQubit,fRes=frequencyRes,attenRes=attenRes,start=0,stop=stopRabi,step=2,data=rabiData)
# T1
	t1Data=Datacube('t1 %f dBm, frequency=%f, qubitPulse=%f ns'%(p+10,frequency01,piRabi))
	data.addChild(t1Data)
	t1=t1Meas(nLoops=10,targettedPointAccuracy=0.01,firstT1Try=firstT1Try,fQubit=frequency01,pQubit=pQubit,fRes=frequencyRes,attenRes=attenRes,piRabi=piRabi,data=t1Data)
	codeExecTime =time.clock()-start
	data.set(frequencyRes=frequencyRes,frequency01=frequency01,piRabi=piRabi,t1=t1,codeExecTime=codeExecTime)
	data.commit()
	return [frequencyRes,frequency01,piRabi,t1,codeExecTime]

## CODE DV
measureAtAWorkingPoint(coilCurrent=-10.5e-3,attenRes=4.5,stopRabi=100,stepRabi=2,firstT1Try=10000,data='')
 
##
mainData=Datacube("T1 vs coilCurrent 5")                                         # main datacube whole flux modulation
DataManager().addDatacube(mainData)
sampTime_ns=2
qb_pulse_ns=2000
res_pulse_ns=1500
driveReadSep_ns=20
stopRabi=200
stepRabi=4
firstT1Try=20000
attenRes=4.5

coilCurrents=SmartLoop(-10.8e-3,0.005e-3,-10.25e-3)
for coilCurrent in coilCurrents:
	onePointData=Datacube("coilCurrent=%f"%coilCurrent)    #create datacube a child for this flux
	mainData.addChild(onePointData)
  	print "current= %f"%coilCurrent
  	setAWG(sampTime_ns=sampTime_ns,qb_pulse_ns=qb_pulse_ns,res_pulse_ns=res_pulse_ns,driveReadSep_ns=driveReadSep_ns)
	resSpecData=Datacube('ResoSpec %f V, Icoil=%f'%(attenRes,coil.current()))
	onePointData.addChild(resSpecData)
	try:
		[frequencyRes,frequency01,piRabi,t1,codeExecTime]=measureAtAWorkingPoint(coilCurrent=coilCurrent,stopRabi=stopRabi,stepRabi=stepRabi,firstT1Try=targettedPointAccuracy=0.02,data=resSpecData)
		mainData.set(coilCurrent=coilCurrent,frequencyRes=frequencyRes,frequency01=frequency01,piRabi=piRabi,t1=t1,codeExecTime=codeExecTime)
		mainData.commit()
		stopRabi=round (3*piRabi)
		stepRabi=max(round(piRabi/5),2)
		firstT1Try=t1
	except: pass
mainData.savetxt()


##
measureAtAWorkingPoint(coilCurrent=-11.1e-3,stopRabi=200,firstT1Try=20000)

## SET AWG
setAWG(sampTime_ns=2,qb_pulse_ns=2000,res_pulse_ns=1500,driveReadSep_ns=20)

## Set working point and parameters
frequencyResBare=7.080
spanRes=0.03
coilCurrent=-10.25e-3
coil.setCurrent(coilCurrent)
coil.turnOn()
freqCenter_qb=fvsIcoil(coilCurrent)          		  # calculated first parameters 
chi=0.09**2/(freqCenter_qb-frequencyResBare)
freqCenter_Res=frequencyResBare-chi
span01=0.1
p=-10
T1est=10000
attenRes=4.5

## Resonator line
setAWG(sampTime_ns=2,qb_pulse_ns=2000,res_pulse_ns=1500,driveReadSep_ns=20)
resSpecData=Datacube('ResoSpec %f V, Icoil=%f'%(attenRes,coil.current()))
frequencyRes=resSpec(nLoops=5,fcenter=freqCenter_Res,fspan=spanRes,fstep=0.0003,attenRes=attenRes,data=resSpecData,autoClear=True)

## set cavity frequency
mw_cav.setFrequency(frequencyRes)

## Qubit Line
setAWG(sampTime_ns=2,qb_pulse_ns=12000,res_pulse_ns=1500,driveReadSep_ns=20)
qbSpecData=Datacube('spectroscopy01 %f dBm, vcoil=%f'%(p,coil.current()))
frequency01=qbSpec(nLoops=5,fcenter=freqCenter_qb,fspan=0.8*span01,fstep=0.00025,power=p-10,fReadout=frequencyRes,attenRes=attenRes,data=qbSpecData,autoClear=False)

## set qubit frequency
mw_qb.setFrequency(frequency01)

## Rabi oscillation
pQubit=p+26
setAWG(sampTime_ns=2,qb_pulse_ns=0,res_pulse_ns=1500,driveReadSep_ns=20)
rabiData=Datacube('rabi %f dBm, frequency=%f'%(p+10,frequency01))
piRabi= rabiMeas(nLoops=10,fQubit=frequency01,pQubit=pQubit,fRes=frequencyRes,attenRes=attenRes,start=0,stop=1000,step=2,data=rabiData,autoClear=False)

## set pi pulse
setAWG(sampTime_ns=2,qb_pulse_ns=piRabi,res_pulse_ns=1500,driveReadSep_ns=20)

## T1 measurement
T1Data=Datacube('t1 %f dBm, frequency=%f, qubitPulse=%f ns'%(p+10,frequency01,piRabi))
T1=t1Meas(nLoops=10,targettedPointAccuracy=0.01,firstT1Try=10000,fQubit=frequency01,pQubit=pQubit,fRes=frequencyRes,attenRes=attenRes,piRabi=piRabi,data=T1Data,autoPlot=True,autoClear=False,debug=True)












## CODE Kiddi
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




