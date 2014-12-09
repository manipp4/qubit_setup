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
pg_ch2=Manager().getInstrument('pg_cavity_switch')
attenuator=Manager().getInstrument('Yoko3')
register=Manager().getInstrument('register')

## function giving qubit frequency versus coil drive
def fvsIcoil(I):
	fmax=7.563
	Ioff=-0.00639 #Ioff=-0.0089 2.51 mA
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
##
def closestXYofTargetY(x,y,yTarget):
	position=min(range(len(x)), key=lambda i: abs(y[i]-yTarget))
	return x[position],y[position],position,y[position]-yTarget
##
def firstXCrossTargetYFromAnEnd(y,x='',yTarget=0,direction='leftToRight'):
	""" Finds the first point a y element crosses the yTarget value. If direction='leftToRight' it starts from the beginnig of x.If direction='rightToLeft' it starts from the end of x."""
	if x=='': x=range(len(y))
	crossing=False
	position=0
	step=+1
	mult=1
	if direction  !='leftToRight':
		position=-1
	differences=[yValue-yTarget for yValue in y]
	dist=abs(differences[position])
	if direction=='leftToRight':	
		if differences[0]>0:
			for i in range(1,len(y)):
				currentDist=abs(differences[i])
				if currentDist<=dist: 
					dist=currentDist
					position=i
				if differences[i]<=0:
					position=i
					crossing=True
					break
		else:
			for i in range(1,len(y)):
				currentDist=abs(differences[i])
				if currentDist<=dist: 
					dist=currentDist
					position=i
				if differences[i]>=0:
					position=i
					crossing=True
					break	
	else: # right to left	
		if differences[-1]>0:
			for i in range(-1,-len(y),-1):
				currentDist=abs(differences[i])
				if currentDist<=dist: 
					dist=currentDist
					position=i
				if differences[i]<=0:
					position=i
					crossing=True
					break
		else:
			for i in range(len(y)): 
				currentDist=abs(differences[i])
				if currentDist<=dist:
					dist=currentDist
					position=i
				if differences[i]>=0:
					position=i
					crossing=True
					break	
	if not crossing: print 'y values do not cross',yTarget
	return x[position],y[position],position,y[position]-yTarget,crossing
	
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
	if debug : print 'Entering fitLorentzian...'
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
			#x1=closestXYofTargetY(x[:indexLine],y[:indexLine],middle)[0]
			x1=firstXCrossTargetYFromAnEnd(y[:indexLine+1],yTarget=middle,x=x[:indexLine+1],direction='rightToLeft')[0]
		x2=x[-1]
		if indexLine!=len(x)-1:										# find the closest x on the right that corresponds to mid-height
			#x2=closestXYofTargetY(x[indexLine:],y[indexLine:],middle)[0]
			x2=firstXCrossTargetYFromAnEnd(y[indexLine:],yTarget=middle,x=x[indexLine:])[0]							 
		initialWidth=(x2-x1)											# calulate the width
		if initialWidth==0:
			index=indexLine
			if indexLine==0:index+=1
			initialWidth=abs(x[index]-x[index-1])/2
	paramGuess=[initialBase,initialHeight,initialPosition,initialWidth]
	LorentzGuess=Lorenzian(paramGuess[0],paramGuess[1],paramGuess[2],paramGuess[3])
	if debug: 
		print "initial Lorentz guess [y0,yAmp,x0, width] = ",paramGuess 
		figure()
		figNumber=gcf().number
		title('fitLorentzian')
		pl=plot(x,y,'ro')
		xPlot=linspace(min(x),max(x),500)
		yGuessPlot=LorentzGuess(xPlot)
		pl1=plot(xPlot,yGuessPlot,'--')
		show()
	# fit
	def fitfunc(x,y0,yAmp,x0,width):
		return Lorenzian(y0,yAmp,x0,width)(x)							#y0+yAmp/(1.0+pow(2.0*(x-x0)/width,2)) 
	paramFit,fitCovariances =scipy.optimize.curve_fit(fitfunc, x, y,p0=paramGuess)
	LorentzFit=Lorenzian(paramFit[0],paramFit[1],paramFit[2],paramFit[3])
	if debug:  
		print "fit Lorentz result [y0,yAmp,x0, width] = ",paramFit
		figure(figNumber)
		yFitPlot=LorentzFit(xPlot)
		pl2=plot(xPlot,yFitPlot)
		show()
	if indexes!='': x=[x[i] for i in argsort(indexes)]	# reorder according to inital x if sorted	
	yFitGuess=[LorentzGuess(xv) for xv in x]
	yFit=[LorentzFit(xv) for xv in x]
	return paramFit,yFit,yFitGuess

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
	if debug:	print 'Entering estimatePeriodByFFT...'
	fft=numpy.fft.rfft(y)
	fft[0]=0	# cancel the zero frequency amplitude or signal mean
	if method=="fitLorentzian":
		try:
			[y0,yAmp,x0,width], LorentzFit, LorentzFitGuess = fitLorentzian(abs(fft),debug=debug)
			estimatedPeriod=len(y)/x0
		except:
			estimatedPeriod=len(y)/argmax(fft)
	else:	estimatedPeriod=len(y)/argmax(fft) # default method returns the index of fft maximum
	if debug: print "Estimated period = ", estimatedPeriod,' points'
	return estimatedPeriod

##
def fitCosine(y,x='',initialY0='',initialYAmp='',initialX0='',initialPeriod='',debug=False):
	if debug: print 'Entering fitCosine...'
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
			try:
				initialPeriod=estimatePeriodByFFT(y,method='fitLorentzian',debug=debug)*step
			except:
				initialPeriod=estimatePeriodByFFT(y,debug=debug)*step
		else: print "Non equidistant x => provide a value for the initialPeriod fitting parameter."		
	paramGuess=[initialY0,initialYAmp,initialX0,initialPeriod]
	cosineGuess=cosine(paramGuess[0],paramGuess[1],paramGuess[2],paramGuess[3])
	if debug:
		print "initial cosine guess [y0,yAmp,x0,period] = ",paramGuess 
		figure()
		figNumber=gcf().number
		title('fitCosine')
		pl=plot(x,y,'ro')
		xPlot=linspace(min(x),max(x),500)
		yGuessPlot=cosineGuess(xPlot)
		pl1=plot(xPlot,yGuessPlot,'--')
		show()
	
	# fit
	def fitfunc(x,y0,yAmp,x0,period):
		return cosine(y0,yAmp,x0,period)(x)							#y0+yAmp*cos(2*math.pi*(x-x0)/period) 
	paramFit,fitCovariances =scipy.optimize.curve_fit(fitfunc, x, y,p0=paramGuess)
	cosineFit=cosine(paramFit[0],paramFit[1],paramFit[2],paramFit[3])
	if debug: 
		print "fit cosine result [y0,yAmp,x0,period] = ",paramFit
		figure(figNumber)
		yFitPlot=cosineFit(xPlot)
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
def setAWG(sampTime_ns=1,qb_pulse_ns=2000,res_pulse_ns=5000,driveReadSep_ns=20,triggerInterval=21000,debug=False): #nanoseconds per point
	samplRate=1e9/sampTime_ns
	reprate=samplRate/20000
	AWG.setRepetitionRate(reprate)
	AWG.setTriggerInterval(triggerInterval)
	
	qb_pulse=abs(round(qb_pulse_ns/sampTime_ns))
	res_pulse=abs(round(res_pulse_ns/sampTime_ns))
	driveReadSep=abs(round(driveReadSep_ns/sampTime_ns))
	
	DelayFromZero_res=20000-res_pulse
	DelayFromZero_qb=20000-(res_pulse+driveReadSep+qb_pulse)
	#register['readoutDelay']=20000-res_pulse
	
	pg_qb.clearPulse()
	pg_qb.generatePulse(duration=qb_pulse, frequency=mw_qb.frequency(), DelayFromZero=DelayFromZero_qb,useCalibration=False)
	pg_qb.generateMarker(name='marker3',start=DelayFromZero_res-1000,stop=DelayFromZero_res,level=3)
	pg_qb.sendPulse(markersName='marker3')
	
	pg_cav.clearPulse()
	pg_cav.generatePulse(duration=res_pulse, frequency=mw_cav.frequency(), DelayFromZero=DelayFromZero_res,useCalibration=False)
	pg_cav.generateMarker(name='marker1',start=DelayFromZero_res-1000,stop=DelayFromZero_res,level=3)
	pg_cav.sendPulse(markersName='marker1')
	
	pg_ch2.clearPulse()
	pg_ch2.generatePulse(duration=res_pulse_ns, frequency=mw_cav.frequency(), DelayFromZero=DelayFromZero_res,useCalibration=False)
	pg_ch2.generateMarker(name='marker2',start=DelayFromZero_res-1000,stop=DelayFromZero_res,level=3)
	pg_ch2.sendPulse(markersName='marker2')
	#time.sleep(4)
	return qb_pulse*sampTime_ns, res_pulse*sampTime_ns, driveReadSep*sampTime_ns

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
def resSpec(nLoops=1,fcenter=1,fspan=1,fstep=0.1,attenRes=4,data='',autoPlot=True,autoClear=False,dataSave=True):
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
	#coil.turnOff()
	[y0,yAmp,x0,width], ampFit, ampFitGuess = fitLorentzian(data['amp'],x=data['f_GHz'])
	data.createColumn('ampFitGuess',ampFitGuess)
	data.createColumn('ampFit',ampFit)		
	#frequencyRes=extremum(data['f'],data['amp'])[0]	
	if dataSave:
		data.savetxt()
	print "f_Res = %f"%x0	
	return x0

##
def qbSpec(nLoops=1,fcenter=1,fspan=1,fstep=0.1,power=1,fReadout='',attenRes='',data='',autoPlot=True,autoClear=False,dataSave=True):
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
	if dataSave:
		data.savetxt()
	print "f_qb = %f"%x0
	return x0

##
def rabiMeas(nLoops=1,fQubit='',pQubit='',fRes='',attenRes='',start=0,stop=1000,step=10,data='',autoPlot=True,autoClear=False,dataSave=True):
	print nLoops,fQubit,pQubit,fRes,attenRes,start,stop,step,data,autoPlot,autoClear,dataSave
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
		[qb_pulse,res_pulse,DelayFromZero]=setAWG(sampTime_ns=2,qb_pulse_ns=duration,res_pulse_ns=1500,driveReadSep_ns=20,triggerInterval=40000)
		if duration-qb_pulse!=0:
			print "desired pulse = %f ns"%duration
			print "actual pulse = %f ns"%qb_pulse
		time.sleep(0.1)
		[amp,phase]=measureIQ(nLoops=nLoops,averageOverSequence=True,convertToAmpPhase=True)
		data.set(duration=duration,amp=amp,phase=phase)
		data.commit()	
	#coil.turnOff()
	[y0,yAmp,t0,rabiPeriod],yfit,yFitGuess=fitCosine(data['amp'],x=data['duration'])
	data.createColumn("rabiFit",yfit)
	piRabi=rabiPeriod/2
	if dataSave:
		data.savetxt()
	print "Pi pulse length = %f ns"%piRabi	 
	return piRabi
##
##
def rabiSinglePointMeas(nLoops=1,fQubit='',pQubit='',fRes='',qb_pulse_ns=10 ,attenRes='',start=0,stop=1000,step=10,data='',staccato=False,autoPlot=True,autoClear=False):
	if data=='':	
		data=Datacube('Rabi')
		DataManager().addDatacube(data)
	if autoPlot:
		data.defineDefaultPlot("iteration","amp")
		DataManager().addDatacube(data)
		DataManager().autoPlot(data,autoClear)
	mw_qb.turnOn()
	if pQubit!='': mw_qb.setPower(pQubit)
	if fQubit!='': mw_qb.setFrequency(fQubit)
	if fRes!='': mw_cav.setFrequency(fRes)
	if attenRes!='': attenuator.setVoltage(attenRes)
	#coil.turnOn()
	time.sleep(1)
	iterations=SmartLoop(start,step,stop,name="iterations")
	#[qb_pulse,res_pulse,DelayFromZero]=setAWG(sampTime_ns=2,qb_pulse_ns=qb_pulse_ns,res_pulse_ns=1500,driveReadSep_ns=20)
	for iteration in iterations:
		[qb_pulse,res_pulse,DelayFromZero]=setAWG(sampTime_ns=2,qb_pulse_ns=qb_pulse_ns,res_pulse_ns=1500,driveReadSep_ns=20)
		#if piRabi1.5-qb_pulse!=0:
		#	print "desired pulse = %f ns"%duration
		#	print "actual pulse = %f ns"%qb_pulse
		#time.sleep(0.1)
		if staccato:
			AWG.stopAWG()
			ask
		[amp,phase]=measureIQ(nLoops=nLoops,averageOverSequence=True,convertToAmpPhase=True)
		data.set(iteration=iteration,amp=amp)
		data.commit()	
	#coil.turnOff()
##
def bestAWGParameters(qb_pulse_ns=10,driveReadSep0_ns=20,res_pulse_ns=1500,t1Estim_ns=10000,nT1Before=5,nT1After=5): # best sampling time to place a pi pulse and 4 T1 before the readout pulse
	#best1= ceil((qb_pulse_ns+nT1Before*t1Estim_ns+driveReadSep0_ns)/10000.)
	#best2= ceil((res_pulse_ns+nT1After*t1Estim_ns)/10000.)
	bestSampTime=ceil((qb_pulse_ns+nT1Before*t1Estim_ns+driveReadSep0_ns)/(20000.-res_pulse_ns)) #max(best1,best2)
	if bestSampTime > qb_pulse_ns/5: print 'Alert:step = ',bestSampTime,'ns is longer than 20% of pi pulse'
	bestTriggerInterval=ceil(bestSampTime*20000+nT1After*t1Estim_ns)
	return bestSampTime, bestTriggerInterval
##
def t1Meas(nLoops=1,targettedPointAccuracy='',firstT1Try=10000,fQubit='',pQubit='',fRes='',attenRes='',piRabi=50,data='',autoPlot=True,autoClear=False,dataSave=True,debug=False):
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
	sampTime_ns,triggerInterval=bestAWGParameters(qb_pulse_ns=piRabi,driveReadSep0_ns=20,res_pulse_ns=1500,t1Estim_ns=t1Estim,nT1Before=4.5,nT1After=4.5)
	if debug:print "sampling time = %i"%sampTime_ns
	setAWG(sampTime_ns=sampTime_ns,qb_pulse_ns=piRabi,res_pulse_ns=res_pulse_ns,driveReadSep_ns=20+delay,triggerInterval=triggerInterval)
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
	if dataSave:
		data.savetxt()
	print "T1 = %f"%t1
	return t1

## spectro Resonator + qubit + Rabi + T1
def measureAtAWorkingPoint(coilCurrent=-10.9e-3,attenRes=4.5,stopRabi=100,stepRabi=2,firstT1Try=10000,targettedPointAccuracy=0.01,data=''):
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
	frequencyRes=resSpec(nLoops=5,fcenter=freqCenter_Res,fspan=1.2*0.03,fstep=0.0003,attenRes=attenRes,data=resSpecData,autoClear=True)
# qubit spectro
	setAWG(sampTime_ns=2,qb_pulse_ns=12000,res_pulse_ns=1500,driveReadSep_ns=20)
	qbSpecData=Datacube('spectroscopy01 %f dBm, vcoil=%f'%(p,coil.current()))
	data.addChild(qbSpecData)
	frequency01=qbSpec(nLoops=5,fcenter=freqCenter_qb,fspan=0.9*span01,fstep=0.00025,power=p-10,fReadout=frequencyRes,attenRes=attenRes,data=qbSpecData)
# Rabi oscillation
	pQubit=p+10
	rabiData=Datacube('rabi %f dBm, frequency=%f'%(pQubit,frequency01))
	data.addChild(rabiData)
	piRabi=rabiMeas(nLoops=20,fQubit=frequency01,pQubit=pQubit,fRes=frequencyRes,attenRes=attenRes,start=0,stop=stopRabi,step=2,data=rabiData)
# T1
	t1Data=Datacube('t1 %f dBm, frequency=%f, qubitPulse=%f ns'%(p+10,frequency01,piRabi))
	data.addChild(t1Data)
	t1=1	#t1=t1Meas(nLoops=10,targettedPointAccuracy=targettedPointAccuracy,firstT1Try=firstT1Try,fQubit=frequency01,pQubit=pQubit,fRes=frequencyRes,attenRes=attenRes,piRabi=piRabi,data=t1Data)
	codeExecTime =time.clock()-start
	data.set(frequencyRes=frequencyRes,frequency01=frequency01,piRabi=piRabi,t1=t1,codeExecTime=codeExecTime)
	data.commit()
	data.savetxt()
	return [frequencyRes,frequency01,piRabi,t1,codeExecTime]
	
##
def measureAtAWorkingPoint_SingleRabiPoint(coilCurrent=-10.7e-3,attenRes=4.5,stopRabi=100,stepRabi=2,firstT1Try=10000,data=''):
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
	rabiData=Datacube('rabi %f dBm, frequency=%f'%(p+26,frequency01))
	data.addChild(rabiData)
	piRabi=rabiMeas(nLoops=20,fQubit=frequency01,pQubit=pQubit,fRes=frequencyRes,attenRes=attenRes,start=0,stop=stopRabi,step=2,data=rabiData)	
# Measure single point
#	pQubit=p+26
#	setAWG(sampTime_ns=2,qb_pulse_ns=0,res_pulse_ns=1500,driveReadSep_ns=20)
#	rabiSinglePointData=Datacube('rabi %f dBm, frequency=%f'%(p+26,frequency01))
#	data.addChild(rabiSinglePointData)
#	rabiSinglePointMeas(nLoops=20,fQubit=frequency01,pQubit=pQubit,fRes=frequencyRes,attenRes=attenRes,start=0,stop=stopRabi,step=2,data=rabiData)		
#	
	codeExecTime =time.clock()-start
	data.set(frequencyRes=frequencyRes,frequency01=frequency01,piRabi=piRabi,codeExecTime=codeExecTime)
	data.commit()
	return [frequencyRes,frequency01,piRabi,codeExecTime]


## CODE DV
mainData=Datacube("T1 vs coilCurrent 1")                                         # main datacube whole flux modulation
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
	try:		
		[frequencyRes,frequency01,piRabi,t1,codeExecTime]=measureAtAWorkingPoint(coilCurrent=coilCurrent,attenRes=4.5,stopRabi=stopRabi,stepRabi=stepRabi,firstT1Try=firstT1Try,targettedPointAccuracy=0.02,data=onePointData)
		mainData.set(coilCurrent=coilCurrent,frequencyRes=frequencyRes,frequency01=frequency01,piRabi=piRabi,t1=t1,codeExecTime=codeExecTime)
		mainData.commit()
		stopRabi=round (3*piRabi)
		stepRabi=max(round(piRabi/5),2)
		if 100<t1<100000:
			firstT1Try=t1
		else:
			firstT1Try=10000
		print 'success' 
	except RuntimeError: 
		print 'Fitting error at %f'%coilCurrent
		pass

mainData.savetxt()

## SET AWG
setAWG(sampTime_ns=2,qb_pulse_ns=2000,res_pulse_ns=1500,driveReadSep_ns=20)

## Set working point and parameters
frequencyResBare=7.080
spanRes=0.03
coilCurrent=(-10.25+2.1)*1e-3
coil.setCurrent(coilCurrent)
coil.turnOn()
freqCenter_qb=fvsIcoil(coilCurrent)          		  # calculated first parameters 
chi=0.09**2/(freqCenter_qb-frequencyResBare)
freqCenter_Res=frequencyResBare-chi
span01=0.1
p=-10
T1est=10000
attenRes=4.5
print fvsIcoil(coilCurrent)
print freqCenter_Res
print freqCenter_qb

## Resonator line
#setAWG(sampTime_ns=1,qb_pulse_ns=2000,res_pulse_ns=5000,driveReadSep_ns=20,triggerInterval=21000,debug=False)
setAWG(sampTime_ns=2,qb_pulse_ns=2000,res_pulse_ns=1500,driveReadSep_ns=20,triggerInterval=51000)
resSpecData=Datacube('ResoSpec %f V, Icoil=%f'%(attenRes,coil.current()))
frequencyRes=resSpec(nLoops=5,fcenter=freqCenter_Res,fspan=1.2*spanRes,fstep=0.0003,attenRes=attenRes,data=resSpecData,autoClear=True)

#qubit spectroscopy
setAWG(sampTime_ns=2,qb_pulse_ns=12000,res_pulse_ns=1500,driveReadSep_ns=20,triggerInterval=51000)
qbSpecData=Datacube('spectroscopy01 %f dBm, vcoil=%f'%(p,coil.current()))
frequency01=qbSpec(nLoops=5,fcenter=freqCenter_qb,fspan=0.15,fstep=0.0002,power=p+5,fReadout=frequencyRes,attenRes=attenRes,data=qbSpecData,autoClear=False)

## Rabi oscillation
pQubit=16
frequencyRes=7.085369
frequency01=5.939058
attenRes=4.5
#setAWG(sampTime_ns=2,qb_pulse_ns=0,res_pulse_ns=1500,driveReadSep_ns=20)
rabiData=Datacube('rabi %f dBm, frequency=%f'%(pQubit,frequency01))
piRabi= rabiMeas(nLoops=10,fQubit=frequency01,pQubit=pQubit,fRes=frequencyRes,attenRes=attenRes,start=0,stop=100,step=2,data=rabiData,autoClear=False)

## set pi pulse
setAWG(sampTime_ns=2,qb_pulse_ns=piRabi,res_pulse_ns=1500,driveReadSep_ns=20)
,triggerInterval
## T1 measurement
pQubit=16
frequencyRes=7.08593
frequency01=6.02513
attenRes=4.5
piRabi=37
T1Data=Datacube('t1 %f dBm, frequency=%f, qubitPulse=%f ns'%(p+10,frequency01,piRabi))
T1=t1Meas(nLoops=10,targettedPointAccuracy=0.01,firstT1Try=10000,fQubit=frequency01,pQubit=pQubit,fRes=frequencyRes,attenRes=attenRes,piRabi=piRabi,data=T1Data,autoPlot=True,autoClear=False,debug=True)






##
print frequency01





