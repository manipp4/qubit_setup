#######################################################################
####### AUTOMATIC MEASUREMENT OF T1 VS COIL CURRENT
#######################################################################

## imports  and handles to instruments
import sys
import time
import numpy
import scipy
import scipy.optimize
import scipy.interpolate
import experiment.cavity3D.Pulses.waveformGenerator as waveGen
from pyview.lib.datacube import *
from pyview.helpers.datamanager import DataManager
from pyview.helpers.instrumentsmanager import Manager
from matplotlib.pyplot import *
from pyview.lib.smartloop import *

#instruments
acqiris=Manager().getInstrument('acqiris34') 
coil=Manager().getInstrument('Yoko1')
AWG=Manager().getInstrument('awgMW2')
mw_cav=Manager().getInstrument('MWSource_Cavity')
mw_qb=Manager().getInstrument('MWSource_Qubit')
pg_qb=Manager().getInstrument('pg_qb')
pg_cav=Manager().getInstrument('pg_cav')
attenuator=Manager().getInstrument('Yoko3')
register=Manager().getInstrument('register')

##
print datetime.datetime.now()
##
print fvsVcoil(0)
## All functions
##
# function giving qubit frequency versus coil drive
def fvsIcoil(I):
	fmax=8.039
	Ioff=-0.002 #Ioff=-0.0089 2.51 mA
	Iperiod=0.0463
	f=fmax*sqrt(abs(cos((I-Ioff)*pi/Iperiod)))	
	return f
	
# Lorentzian pure function
def Lorenzian(y0,yAmp,x0,width):
	return lambda x: y0+yAmp/(1.0+pow(2.0*(x-x0)/width,2)) 

# Cosine pure function
def cosine(y0,yAmp,x0,period):
	return lambda x: y0+yAmp*cos(2*math.pi*(x-x0)/period)
	
# exponentially decaying cosine pure function
def cosineExp(y0,yAmp,x0,period,xc):
	return lambda x: y0+yAmp*cos(2*math.pi*(x-x0)/period)*exp(-x/xc)

# finding the closest point from a target
def closestXYofTargetX(x,y,xTarget):
	 position=min(range(len(x)), key=lambda i: abs(x[i]-xTarget))
	 return x[position],y[position],position,x[position]-xTarget 	
#
def closestXYofTargetY(x,y,yTarget):
	position=min(range(len(x)), key=lambda i: abs(y[i]-yTarget))
	return x[position],y[position],position,y[position]-yTarget
#
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
	
# finding an extremum 	
def extremum(x,y,minOrMax="max"):
	if minOrMax=='max':	extr=max(y)
	else:	extr=min(y)
	if 'numpy.ndarray' in str(type(y)): y=y.tolist()
	position=y.index(extr)
	return x[position],y[position],position

# sorting function v1,v2 
def sortV1V2AscendingV1(v1,v2):
	initialIndexes=argsort(v1)
	v1=[v1[i] for i in initialIndexes]
	v2=[v2[i] for i in initialIndexes]
	return v1,v2,initialIndexes

# Lorentzian fit of a dip or peak. Sorted y or sorted or unsorted x y accepted
def fitLorentzian(y,x='',initialBase='',initialHeight='',initialPosition='',initialWidth='',direction='',debug=False):
	""" fitLorentzian(y,x='',initialBase='',initialHeight='',initialPosition='',initialWidth='',direction='',debug=False) finds the fitting parameters of a lorentzian peak"""
	if debug : print 'Entering fitLorentzian...'
	# generate the x if not defined
	indexes=''			# variable to store the initial order of x values
	if x=='':										
		x=range(len(y))							
	else: 				#sort x and y by ascending x but memorize the initial order
		x,y,indexes=sortV1V2AscendingV1(x,y)
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

def areEquidistant(x,relativeTolerance=0.01):
	if type(x)=='list': x=array(x)		# convert to numpy array if necessary
	deltas=(np.roll(x,-1)-x)[:-1]			# calculate the x separations
	return max(deltas)/min(deltas)-1<=relativeTolerance

# myFFT TO BE DONE
def myFFT(y,x='',forceX=False):
	if x=='':	
		result=numpy.fft.rfft(y)	# use normal fft if only y is given
	else: 
		if not areEquidistant(x):
			numpy.interp(range(), x, y)[source]	
		result=1
	return result

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

def fitCosine(y,x='',initialY0='',initialYAmp='',initialX0='',initialPeriod='',debug=False):
	if debug: print 'Entering fitCosine...'
	if x=='':	x=range(len(y))		# generate  x if not defined
	yMax=max(y)
	yMin=min(y)
	if initialY0=='': initialY0=(yMax+yMin)/2
	if initialYAmp=='': initialYAmp=(yMax-yMin)/2
	if initialX0=='': initialX0=extremum(x,y,minOrMax="max")[0]
	if initialPeriod=='':
		x2,y2,indexes= sortV1V2AscendingV1(x,y)
		if not areEquidistant(x2):
			if debug: print 'non equidistant x => using interpolation'
			interpF=scipy.interpolate.interp1d(x2, y2)
			x2=linspace(min(x),max(x),len(x))
			y2=interpF(x2)
		step=x2[1]-x2[0]
		try:
			initialPeriod=estimatePeriodByFFT(y2,method='fitLorentzian',debug=debug)*step
		except:
			initialPeriod=estimatePeriodByFFT(y2,debug=debug)*step
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

def fitCosineExp(y,x='',initialY0='',initialYAmp='',initialX0='',initialPeriod='',initialXc='',debug=False):
	if debug: print 'Entering fitCosineExp...'
	if x=='':	x=range(len(y))		# generate  x if not defined								
	yMax=max(y)
	yMin=min(y)
	if initialY0=='': initialY0=(yMax+yMin)/2
	if initialYAmp=='': initialYAmp=(yMax-yMin)/2
	if initialX0=='': initialX0=extremum(x,y,minOrMax="max")[0]
	if initialPeriod=='':
		x2,y2,indexes= sortV1V2AscendingV1(x,y)
		if not areEquidistant(x2):
			if debug: print 'non equidistant x => using interpolation'
			interpF=scipy.interpolate.interp1d(x2, y2)
			x2=linspace(min(x),max(x),len(x))
			y2=interpF(x2)
		step=x2[1]-x2[0]
		try:
			initialPeriod=estimatePeriodByFFT(y2,method='fitLorentzian',debug=debug)*step
		except:
			initialPeriod=estimatePeriodByFFT(y2,debug=debug)*step
	if initialXc=='': initialXc= (max(x)-min(x))/10.
	paramGuess=[initialY0,initialYAmp,initialX0,initialPeriod,initialXc]
	cosineExpGuess=cosineExp(paramGuess[0],paramGuess[1],paramGuess[2],paramGuess[3],paramGuess[4])
	if debug:
		print "initial cosineEXp guess [y0,yAmp,x0,period,xc] = ",paramGuess 
		figure()
		figNumber=gcf().number
		title('fitExpCosine')
		pl=plot(x,y,'ro')
		xPlot=linspace(min(x),max(x),500)
		yGuessPlot=cosineExpGuess(xPlot)
		pl1=plot(xPlot,yGuessPlot,'--')
		show()
	
	# fit
	def fitfunc(x,y0,yAmp,x0,period,xc):
		return cosineExp(y0,yAmp,x0,period,xc)(x)							#y0+yAmp*exp(-x/xc)cos(2*math.pi*(x-x0)/period) 
	paramFit,fitCovariances =scipy.optimize.curve_fit(fitfunc, x, y,p0=paramGuess)
	cosineExpFit=cosineExp(paramFit[0],paramFit[1],paramFit[2],paramFit[3],paramFit[4])
	if debug: 
		print "fit cosineExp result [y0,yAmp,x0,period,xc] = ",paramFit
		figure(figNumber)
		yFitPlot=cosineExpFit(xPlot)
		pl2=plot(xPlot,yFitPlot)
		show()
	yFitGuess=[cosineExpGuess(xv) for xv in x]
	yFit=[cosineExpFit(xv) for xv in x]
	return paramFit,yFit,yFitGuess

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
##
print setAWG(sampTime_ns=1,qb_pulse_ns=2000,res_pulse_ns=1500,resDriveLength_ns=1000,resDriveDelay_ns=1000,pulseSep_ns=3050,driveReadSep_ns=20,ramsey=False,echoSep1=3000)
##
##
print measureIQ(nLoops=10,wantedChannels=3,iOffset=0,qOffset=0,averageOverSequence=True,convertToAmpPhase=True)
##
def setAWG(sampTime_ns=1,qb_pulse_ns=2000,res_pulse_ns=5000,resDriveLength_ns='',resDriveDelay_ns='',driveReadSep_ns=20,pulseSep_ns=0,triggerInterval=21000,ramsey=False,echoSep1=100,debug=False): #nanoseconds per point
	samplRate=1.e9/sampTime_ns
	reprate=samplRate/20000.
	AWG.setRepetitionRate(reprate)
	AWG.setTriggerInterval(triggerInterval*1e-9)# has to be specidfied in seconds
	
	if ramsey!=False:
		#print 'ramsey pulse'
		qb_pulse_ns=qb_pulse_ns/2
	
	qb_pulse=abs(round(qb_pulse_ns/sampTime_ns))
	qb_pulseHalf=abs(round(qb_pulse_ns/sampTime_ns/2))
	res_pulse=abs(round(res_pulse_ns/sampTime_ns))
	driveReadSep=abs(round(driveReadSep_ns/sampTime_ns))
	pulseSep=abs(round(pulseSep_ns/sampTime_ns))
	pulseSepHalf=abs(round(pulseSep_ns/sampTime_ns/2))
	if resDriveLength_ns!='':
		resDriveLength=abs(round(resDriveLength_ns/sampTime_ns))
		resDriveDelay=abs(round(resDriveDelay_ns/sampTime_ns))
	
	if qb_pulse_ns<150:
		markerLength_ns=150
	else:
		markerLength_ns=qb_pulse_ns+60
	markerLength=abs(round(markerLength_ns/sampTime_ns))
	markerLengthHalf=abs(round(markerLength_ns/sampTime_ns/2))
	markerDelay_ns=95
	markerDelay=abs(round(markerDelay_ns/sampTime_ns))
	DelayFromZero_res=20000-res_pulse
	DelayFromZero_qb=20000-(res_pulse+driveReadSep+qb_pulse)
	markerStart=20000-(res_pulse+driveReadSep+qb_pulseHalf+markerLengthHalf+markerDelay)
	markerStop=20000-(res_pulse+driveReadSep+qb_pulseHalf-markerLengthHalf+markerDelay)

	#QubitPulse
	
	if ramsey=='normal':
		DelayFromZeroPulse2=DelayFromZero_qb
		DelayFromZeroPulse1=DelayFromZeroPulse2-(pulseSep+qb_pulse)
		
	
		markerStart2=markerStart
		markerStop2=markerStop
		markerStart1=20000-(res_pulse+driveReadSep+qb_pulseHalf+markerLengthHalf+markerDelay+pulseSep+qb_pulse)
		markerStop1=20000-(res_pulse+driveReadSep+qb_pulseHalf-markerLengthHalf+markerDelay+pulseSep+qb_pulse)
		
		if (markerStart2-markerStop1)*sampTime_ns<150:
			markerStart2=markerStart1

		pg_qb.clearPulse()
		pg_qb.generatePulse(duration=qb_pulse, frequency=mw_qb.frequency(), DelayFromZero=DelayFromZeroPulse1,useCalibration=False)
		pg_qb.generatePulse(duration=qb_pulse, frequency=mw_qb.frequency(), DelayFromZero=DelayFromZeroPulse2,useCalibration=False)
		pg_qb.generateMarker(name='marker3',start=markerStart1,stop=markerStop1,level=3,start2=markerStart2,stop2=markerStop2)
		pg_qb.sendPulse(markersName='marker3')
	
	elif ramsey=='echo':
		if pulseSep<2*qb_pulse:
			print 'pulse separation too short!!'
		DelayFromZeroPulse3=DelayFromZero_qb
		DelayFromZeroPulse2=DelayFromZeroPulse3-(pulseSepHalf+qb_pulse)
		DelayFromZeroPulse1=DelayFromZeroPulse3-(pulseSep+qb_pulse)
		
		markerStart3=markerStart
		markerStop3=markerStop
		markerStart2=20000-(res_pulse+driveReadSep+qb_pulse+markerLength+markerDelay+pulseSepHalf)
		markerStop2=20000-(res_pulse+driveReadSep+qb_pulse-markerLength+markerDelay+pulseSepHalf)
		markerStart1=20000-(res_pulse+driveReadSep+qb_pulseHalf+markerLengthHalf+markerDelay+pulseSep+qb_pulse)
		markerStop1=20000-(res_pulse+driveReadSep+qb_pulseHalf-markerLengthHalf+markerDelay+pulseSep+qb_pulse)
		
		if (markerStart2-markerStop1)*sampTime_ns<150:
			markerStart3=markerStart1
			
		pg_qb.clearPulse()
		pg_qb.generatePulse(duration=qb_pulse, frequency=mw_qb.frequency(), DelayFromZero=DelayFromZeroPulse1,useCalibration=False)
		pg_qb.generatePulse(duration=2*qb_pulse, frequency=mw_qb.frequency(), DelayFromZero=DelayFromZeroPulse2,useCalibration=False)
		pg_qb.generatePulse(duration=qb_pulse, frequency=mw_qb.frequency(), DelayFromZero=DelayFromZeroPulse3,useCalibration=False)
		pg_qb.generateMarker(name='marker3',start=markerStart1,stop=markerStop1,level=3,start2=markerStart2,stop2=markerStop2,start3=markerStart3,stop3=markerStop3)
		pg_qb.sendPulse(markersName='marker3')
		
	elif ramsey=='echo2':
		if pulseSep<(2*qb_pulse+echoSep1):
			print 'pulse separation too short!!'
		DelayFromZeroPulse3=DelayFromZero_qb
		DelayFromZeroPulse2=DelayFromZeroPulse3-(pulseSep+qb_pulse-echoSep1)
		DelayFromZeroPulse1=DelayFromZeroPulse3-(pulseSep+qb_pulse)
		
		markerStart3=markerStart
		markerStop3=markerStop
		markerStart2=20000-(res_pulse+driveReadSep+qb_pulseHalf+markerLengthHalf+markerDelay+pulseSep+qb_pulse-echoSep1)
		markerStop2=20000-(res_pulse+driveReadSep+qb_pulseHalf-markerLengthHalf+markerDelay+pulseSep+qb_pulse-echoSep1)
		markerStart1=20000-(res_pulse+driveReadSep+qb_pulseHalf+markerLengthHalf+markerDelay+pulseSep+qb_pulse)
		markerStop1=20000-(res_pulse+driveReadSep+qb_pulseHalf-markerLengthHalf+markerDelay+pulseSep+qb_pulse)
		
		if (markerStart2-markerStop1)*sampTime_ns<150:
			markerStart2=markerStart1
		if (markerStart3-markerStop2)*sampTime_ns<150:
			markerStart3=markerStart2
			
		pg_qb.clearPulse()
		pg_qb.generatePulse(duration=qb_pulse, frequency=mw_qb.frequency(), DelayFromZero=DelayFromZeroPulse1,useCalibration=False)
		pg_qb.generatePulse(duration=2*qb_pulse, frequency=mw_qb.frequency(), DelayFromZero=DelayFromZeroPulse2,useCalibration=False)
		pg_qb.generatePulse(duration=qb_pulse, frequency=mw_qb.frequency(), DelayFromZero=DelayFromZeroPulse3,useCalibration=False)
		pg_qb.generateMarker(name='marker3',start=markerStart1,stop=markerStop1,level=3,start2=markerStart2,stop2=markerStop2,start3=markerStart3,stop3=markerStop3)
		pg_qb.sendPulse(markersName='marker3')
	else:
		pg_qb.clearPulse()
		pg_qb.generatePulse(duration=qb_pulse, frequency=mw_qb.frequency(), DelayFromZero=DelayFromZero_qb,useCalibration=False)
		pg_qb.generateMarker(name='marker3',start=markerStart,stop=markerStop,level=3)
		pg_qb.sendPulse(markersName='marker3')
	
	#ResonatorPulse
	
	if resDriveLength_ns=='':
		pg_cav.clearPulse()
		pg_cav.generatePulse(duration=res_pulse, frequency=mw_cav.frequency(), DelayFromZero=DelayFromZero_res,useCalibration=False)
		pg_cav.generateMarker(name='marker1',start=DelayFromZero_res-1000,stop=DelayFromZero_res,level=3)
		pg_cav.sendPulse(markersName='marker1')
	else:
		DelayFromZero_resPulse=DelayFromZero_res-driveReadSep-resDriveDelay-resDriveLength
		
		pg_cav.clearPulse()
		pg_cav.generatePulse(duration=res_pulse, frequency=mw_cav.frequency(), DelayFromZero=DelayFromZero_res,useCalibration=False)
		pg_cav.generatePulse(duration=resDriveLength, frequency=mw_cav.frequency(), DelayFromZero=DelayFromZero_res,useCalibration=False)
		pg_cav.generateMarker(name='marker1',start=DelayFromZero_res-1000,stop=DelayFromZero_res,level=3)
		pg_cav.sendPulse(markersName='marker1')
	
	#Chanel 2 ( markers are used)
	#pg_ch2.clearPulse()
	#pg_ch2.generatePulse(duration=res_pulse, frequency=mw_cav.frequency(), DelayFromZero=DelayFromZero_res,useCalibration=False)
	#pg_ch2.generateMarker(name='marker2',start=DelayFromZero_res-1000,stop=DelayFromZero_res,level=3)
	#pg_ch2.sendPulse(markersName='marker2')
	#time.sleep(4)
	return qb_pulse*sampTime_ns, res_pulse*sampTime_ns, driveReadSep*sampTime_ns, pulseSep*sampTime_ns
#### Need to implement Ramsey pulses for set AWGV2
def setAWGV2(sampTime_ns=1,triggerInterval=21000,ch1=True,ch1_pulseType='readout',ch1_pulse_ns=2500,ch1_amp=1,driveReadSep_ns=20,ch2=False,ch2_pulseType='readout',ch2_pulse_ns=2500,ch2_amp=1,ch3=True,ch3_pulseType='gaussian',sigma_ns=20,sqLength_ns=1000,ch4=False,debug=False): #nanoseconds per point
	samplRate=1.e9/sampTime_ns
	reprate=samplRate/20000.
	AWG.setRepetitionRate(reprate)
	AWG.setTriggerInterval(triggerInterval*1e-9)# has to be specidfied in seconds
	ch1Return=[]
	ch2Return=[]
	ch3Return=[]
	ch4Return=[]
	if ch1:
		if ch1_pulseType=='readout':
			ch1_pulse=abs(round(ch1_pulse_ns/sampTime_ns))
			wf1=waveGen.readoutWaveform(ch1_pulse,height=ch1_amp)
			waveGen.send2AWG(wf1)
			waveGen.loadWF2Channel(1,wf1[2])
		elif ch1_pulseType=='readout_switch':
			# for a 30 ns riseTime switch
			switchRiseBuffer=abs(round(30/sampTime_ns))
			ch1_pulse=abs(round(ch1_pulse_ns/sampTime_ns))
			wf1=waveGen.readoutSwitchWaveform(ch1_pulse,height=ch1_amp,switchRiseBuffer=switchRiseBuffer)
			waveGen.send2AWG(wf1)
			waveGen.loadWF2Channel(1,wf1[2])
		else:
			print 'pulsetype for channel 1 not defined in setAWGV2'
		ch1Return=ch1_pulse*sampTime_ns,
	if ch2:
		if ch2_pulseType=='readout':
			ch2_pulse=abs(round(ch2_pulse_ns/sampTime_ns))
			wf2=waveGen.readoutWaveform(ch2_pulse,height=ch2_amp)
			waveGen.send2AWG(wf2)
			waveGen.loadWF2Channel(2,wf2[2])
		elif ch2_pulseType=='readout_switch':
			# for a 30 ns riseTime switch
			switchRiseBuffer=abs(round(30/sampTime_ns))
			ch2_pulse=abs(round(ch2_pulse_ns/sampTime_ns))
			wf2=waveGen.readoutSwitchWaveform(ch2_pulse,height=ch2_amp,switchRiseBuffer=switchRiseBuffer)
			waveGen.send2AWG(wf2)
			waveGen.loadWF2Channel(2,wf1[2])
		else:
			print 'pulsetype for channel 2 not defined in setAWGV2'
		ch2Return=ch1_pulse*sampTime_ns,
	if ch3:
		if ch3_pulseType=='gaussian':
			markerOffset_ns=-100
			center_ns=20000*sampTime_ns-ch1_pulse_ns-driveReadSep_ns-3*sigma_ns
			driveReadSep=abs(round(driveReadSep_ns/sampTime_ns))
			markerOffset=round(markerOffset_ns/sampTime_ns)
			center=abs(round(center_ns/sampTime_ns))
			sigma=abs(round(sigma_ns/sampTime_ns))
			wf3=waveGen.gaussianPulseWaveform(center,sigma,name='gaussian,sigma=%f'%sigma,markerOffset2=markerOffset)
			waveGen.send2AWG(wf3)
			waveGen.loadWF2Channel(3,wf3[2])	
		elif ch3_pulseType=='square':
			markerOffset_ns=-100
			start_ns=20000*sampTime_ns-ch1_pulse_ns-driveReadSep_ns-sqLength_ns
			stop_ns=20000*sampTime_ns-ch1_pulse_ns-driveReadSep_ns
			driveReadSep=abs(round(driveReadSep_ns/sampTime_ns))
			markerOffset=round(markerOffset_ns/sampTime_ns)
			start=abs(round(start_ns/sampTime_ns))
			stop=abs(round(stop_ns/sampTime_ns))
			length=(stop-start)*sampTime_ns
			wf3=waveGen.squarePulseWaveform(start,stop,name='square,len=%f'%length)
			waveGen.send2AWG(wf3)
			waveGen.loadWF2Channel(3,wf3[2])
			sigma=0
			center=0
		elif ch3_pulseType=='open':
			wf3=waveGen.openMixer()
			waveGen.send2AWG(wf3)
			waveGen.loadWF2Channel(3,wf3[2])
			sigma=0
			center=0
			driveReadSep=0	
		else:
			print 'pulsetype for channel 3 not defined in setAWGV2'
		ch3Return=sigma*sampTime_ns, center*sampTime_ns, ch1_pulse*sampTime_ns, driveReadSep*sampTime_ns
	if ch4:
		print 'pulsetype for channel 4 not defined in setAWGV2'
		ch4Return=[]
	
	return concatenate([ch1Return,ch2Return,ch3Return,ch4Return])

##
print measureIQ(nLoops=1,wantedChannels=3,iOffset=0,qOffset=0,averageOverSequence=False,convertToAmpPhase=False)
##
def measureIQ(nLoops=1,wantedChannels=3,iOffset=0,qOffset=0,averageOverSequence=False,convertToAmpPhase=False):
	# acquire and transfer the sequence of traces for the selected channels
	acqiris.AcquireTransfer(transferAverage=False,nLoops=nLoops,wantedChannels=wantedChannels)
	time.sleep(0.1)
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
#
def measureIQOffOn(nLoops=1,wantedChannels=3, firstSlice=None,secondSlice=None,startMargin=0,middleMargin=0.1,stopMargin=0,averageOverSequence=False,convertToAmpPhase=False,OnBeforeOff=False):
	# acquire and transfer the sequence of traces for the selected channels
	acqiris.AcquireTransfer(transferAverage=False,nLoops=nLoops,wantedChannels=wantedChannels)
	time.sleep(0.1)
	nbrSamplesPerSeg=acqiris.getLastWave()['nbrSamplesPerSeg']
	if firstSlice==None:
		if secondSlice==None:
			index1=int(nbrSamplesPerSeg/2*(1+middleMargin/2))
			if index1 <0 : index1=1
			if index1 > nbrSamplesPerSeg-1 : index1=nbrSamplesPerSeg-2
			index2=int(nbrSamplesPerSeg*(1-stopMargin))
			if index2 < index1: index2=index1+1
			if index2 > nbrSamplesPerSeg-1 : index2=nbrSamplesPerSeg-1
			secondSlice=slice(index1,index2)
		index1=int(nbrSamplesPerSeg*startMargin)
		if index1 <0 : index1=0
		if index1> secondSlice.start-1: index1 = secondSlice.start-1
		index2=int(secondSlice.start- middleMargin*nbrSamplesPerSeg)
		if index2 < index1: index2=index1+1
		if index2 > secondSlice.start:index2=secondSlice.start-1
		firstSlice=slice(index1,index2)
	elif secondSlice==None:
		index1=int(firstSlice.stop+ middleMargin*nbrSamplesPerSeg)
		if index1 <= firstSlice.stop : index1=firstSlice.stop+1
		if index1 > nbrSamplesPerSeg-1 : index1=nbrSamplesPerSeg-1
		index2=int(nbrSamplesPerSeg*(1-stopMargin))
		if index2<index1: index2=index1
		if index2 > nbrSamplesPerSeg-1 : index2=nbrSamplesPerSeg-1
		secondSlice=slice(index1,index2)
	
	def getBoxcarMeans(slic=slice(0,-1),wantedChannels=3,averageOverSequence=False):
		commandString="DLLMath1Module.boxcarOfLastWaveForms(targettedWaveform="+str(wantedChannels)+",sliceArray="+str([slic,slic,slic,slic])+")"
		acqiris(commandString)		# calculate the mean of each trace in the sequence COMPLETE HERE
		boxcarMeans= acqiris("DLLMath1Module.boxcarMean")	# get the sequence of boxcarMeans for the selected channels
		# get the indexes of selected channels	
		indexes= [i for i,x in enumerate([1&wantedChannels!=0,2&wantedChannels!=0,4&wantedChannels!=0,8&wantedChannels!=0]) if x ==True]
		boxcarMeans=[boxcarMeans[indexes[0]],boxcarMeans[indexes[1]]] # keep only the first and second selected channels
		if averageOverSequence:								 # average over sequence if requested
			boxcarMeans=[numpy.mean(boxcarMeans[0]),numpy.mean(boxcarMeans[1])]
		return boxcarMeans
	
	boxcarMeansA=getBoxcarMeans(slic=firstSlice,wantedChannels=wantedChannels,averageOverSequence=averageOverSequence)
	boxcarMeansB=getBoxcarMeans(slic=secondSlice,wantedChannels=wantedChannels,averageOverSequence=averageOverSequence)
	channels=[boxcarMeansB[0]-boxcarMeansA[0],boxcarMeansB[1]-boxcarMeansA[1],boxcarMeansA[0],boxcarMeansA[1],boxcarMeansB[0],boxcarMeansB[1]]
	if OnBeforeOff:
		channels[0]=-channels[0]
		channels[1]=-channels[1]
	
	if convertToAmpPhase:									 # convert I and Q into Amp and Phase
		channels=[sqrt((channels[0])**2+(channels[1])**2),arctan(channels[1]/channels[0]),sqrt((channels[2])**2+(channels[3])**2),arctan(channels[3]/channels[2]),sqrt((channels[4])**2+(channels[5])**2),arctan(channels[5]/channels[4])]		# calculate amplitude and phase
	# returns [IB-IA,QB-QA,IA,QA,IB,QB] or [AmpCor, phiCor,] or [array([(I2-I1)1,(I2-I1)2,(I2-I1)3,...]),array([(Q2-Q1)1,(Q2-Q1)2,(Q2-Q1)3,...])] or  ...
	return channels
#
def resSpec(nLoops=1,fcenter=1,fspan=1,fstep=0.1,attenRes=4,data='',qbGen=False,fit=True,autoPlot=True,autoClear=False,dataSave=True,returnRes=True):
	if data=='':	
		data=Datacube('ResSpec')
		DataManager().addDatacube(data)
	if autoPlot:
		data.defineDefaultPlot("f_GHz","amp")
		data.defineDefaultPlot("f_GHz","ampFit")
		DataManager().addDatacube(data)
		data.toDataManager()
	mw_cav.turnOn()
	mw_qb.turnOff()
	attenuator.setVoltage(attenRes)
	frequencyLoop=SmartLoop(fcenter-fspan/2,fstep,fcenter+fspan/2,name='resonator frequency')
	coil.turnOn()
	print 'resSpec with attenRes=',attenuator.voltage()
	time.sleep(1)
	for f in frequencyLoop:
		mw_cav.setFrequency(f)
		[amp,phase,ampOff,phaseOff,ampOn,phaseOn]=measureIQOffOn(nLoops=nLoops,wantedChannels=3, firstSlice=slice(5,155),secondSlice=slice(200,399),startMargin=0,middleMargin=0.1,stopMargin=0,averageOverSequence=True,convertToAmpPhase=True,OnBeforeOff=True)
		data.set(f_GHz=f,amp=amp,phase=phase,columnOrder=['f_GHz','amp','phase'])
		data.commit()
	#fit
	#coil.turnOff()
	if fit:
		[y0,yAmp,x0,width], ampFit, ampFitGuess = fitLorentzian(data['amp'],x=data['f_GHz'])
		data.createColumn('ampFitGuess',ampFitGuess)
		data.createColumn('ampFit',ampFit)		
	#frequencyRes=extremum(data['f'],data['amp'])[0]	
	if dataSave:
		data.savetxt()
	if returnRes:
		print "f_Res = %f"%x0	
		return x0

#
def qbSpec(nLoops=1,fcenter=1,fspan=1,fstep=0.1,powerQubit=1.,fReadout='',attenRes='',data='',autoPlot=True,autoClear=False,dataSave=True):
	if data=='':	
		data=Datacube('ResQubit')
		DataManager().addDatacube(data)
	if autoPlot:
		data.defineDefaultPlot("f_GHz","amp")
		data.defineDefaultPlot("f_GHz","ampFit")
		DataManager().addDatacube(data)
		DataManager().autoPlot(data,autoClear)
	data.toDataManager()
	#setAWG(sampTime_ns=1,qb_pulse_ns=2000,res_pulse_ns=3000,driveReadSep_ns=20)
	mw_qb.turnOn()
	mw_qb.setPower(powerQubit)
	if fReadout!='': mw_cav.setFrequency(fReadout)
	if attenRes!='':attenuator.setVoltage(attenRes)
	frequencyLoop=SmartLoop(fcenter-fspan/2,fstep,fcenter+fspan/2,name='qubit frequency')
	coil.turnOn()
	time.sleep(1)
	print 'qbSpec with powerQubit=',mw_qb.power()
	for f in frequencyLoop:
		mw_qb.setFrequency(f)
		[amp,phase,ampOff,phaseOff,ampOn,phaseOn]=measureIQOffOn(nLoops=nLoops,wantedChannels=3, firstSlice=slice(5,155),secondSlice=slice(200,399),startMargin=0,middleMargin=0.1,stopMargin=0,averageOverSequence=True,convertToAmpPhase=True,OnBeforeOff=True)
		data.set(f_GHz=f,amp=amp,phase=phase,columnOrder=['f_GHz','amp','phase'])
		data.commit()
	#coil.turnOff()
	[y0,yAmp,x0,width], ampFit, ampFitGuess = fitLorentzian(data['amp'],x=data['f_GHz'])
	#data.createColumn('ampFitGuess',ampFitGuess)
	data.createColumn('ampFit',ampFit)		
	#x0=extremum(data['f_GHz'],data['amp'],minOrMax="min")[0]
	if dataSave:
		data.savetxt()
	print "f_qb = %f"%x0
	return x0
#
def qbSpecDiscr(nLoops=1,fStart=5,fStop=6,fstep=0.1,powerQubit=1.,fReadout='',attenRes='',data='',qbGen=True,autoPlot=True,autoClear=False,dataSave=True):
	if data=='':	
		data=Datacube('ResQubitDisc')
		DataManager().addDatacube(data)
	#setAWG(sampTime_ns=1,qb_pulse_ns=2000,res_pulse_ns=3000,driveReadSep_ns=20)
	if qbGen:
		mw_qb.turnOn()
		mw_qb.setPower(powerQubit)
	if fReadout!='': mw_cav.setFrequency(fReadout)
	if attenRes!='':attenuator.setVoltage(attenRes)
	frequencyLoop=SmartLoop(fStart,fstep,fStop,name='qubit frequency')
	coil.turnOn()
	time.sleep(1)
	print 'qbSpec with powerQubit=',mw_qb.power()
	for f in frequencyLoop:
		mw_qb.setFrequency(f)
		[amp,phase]=measureIQ(nLoops=nLoops,averageOverSequence=True,convertToAmpPhase=True)
		data.set(f_GHz=f,amp=amp,phase=phase)
		data.commit()
	if dataSave:
		data.savetxt()
#
def qbSpecCoil(nLoops=1,iCoilStart=0, iCoilStop=10e-3,iCoilStep=0.01e-3,fQubit='',powerQubit='',fReadout='',attenRes='',data='',autoPlot=True,autoClear=False,dataSave=True):
	if data=='':	
		data=Datacube('ResQubitCoil')
		DataManager().addDatacube(data)
	if autoPlot:
		data.defineDefaultPlot("iCoil","amp")
		data.defineDefaultPlot("iCoil","ampFit")
		DataManager().addDatacube(data)
		DataManager().autoPlot(data,autoClear)
	#setAWG(sampTime_ns=1,qb_pulse_ns=2000,res_pulse_ns=3000,driveReadSep_ns=20)
	if fReadout!='': mw_cav.setFrequency(fReadout)
	if attenRes!='':attenuator.setVoltage(attenRes)
	if fQubit!='': mw_qb.setFrequency(fQubit)
	if powerQubit!='': 
		mw_qb.setPower(powerQubit)
		mw_qb.turnOn()
	iCoilLoop=SmartLoop(iCoilStart,iCoilStep,iCoilStop,name='iCoil')
	coil.turnOn()
	time.sleep(1)
	for iCoil in iCoilLoop:
		coil.setCurrent(iCoil)
		[amp,phase]=measureIQ(nLoops=nLoops,averageOverSequence=True,convertToAmpPhase=True)
		data.set(iCoil=iCoil,amp=amp,phase=phase)
		data.commit()
	#coil.turnOff()
	[y0,yAmp,x0,width], ampFit, ampFitGuess = fitLorentzian(data['amp'],x=data['iCoil'])
	#data.createColumn('ampFitGuess',ampFitGuess)
	data.createColumn('ampFit',ampFit)		
	#x0=extremum(data['f_GHz'],data['amp'],minOrMax="min")[0]
	if dataSave:
		data.savetxt()
	print "f_qb = %f"%x0
	return x0

def rabiMeas(nLoops=1,fQubit='',powerQubit='',fRes='',attenRes='',pulseType='square',readoutType='readout',t1Estim=10000,start=0,stop=1000,step=10,data='',autoPlot=True,autoClear=False,dataSave=True):
	if data=='':
		if pulseType=='gaussian':	
			data=Datacube('Rabi-gaussian')
		else:
			data=Datacube('Rabi')
		DataManager().addDatacube(data)
	if autoPlot:
		data.defineDefaultPlot("duration","amp")
		data.defineDefaultPlot("duration","rabiFit")
		DataManager().addDatacube(data)
		DataManager().autoPlot(data,autoClear)
	mw_qb.turnOn()
	if powerQubit!='': mw_qb.setPower(powerQubit)
	if fQubit!='': mw_qb.setFrequency(fQubit)
	if fRes!='': mw_cav.setFrequency(fRes)
	if attenRes!='': attenuator.setVoltage(attenRes)
	#coil.turnOn()
	time.sleep(1)
	print 'rabiMeas with fQubit=',mw_qb.frequency(),' powerQubit=',mw_qb.power()
	durations=SmartLoop(start,step,stop,name="durations")
	for duration in durations:
		sampTime_ns,triggerInterval=bestAWGParameters(qb_pulse_ns=duration,driveReadSep0_ns=20,res_pulse_ns=2500,t1Estim_ns=t1Estim,nT1Before=4.5,nT1After=4.5)
		if pulseType=='gaussian':	[qb_pulse,center,ch1_pulse,driveReadSep]=setAWGV2(sampTime_ns=2,triggerInterval=triggerInterval,ch1=True,ch1_pulseType=readoutType,ch1_pulse_ns=2500,driveReadSep_ns=20,ch3=True,ch3_pulseType='gaussian',sigma_ns=duration)
		else:	
			[qb_pulse,res_pulse,DelayFromZero,pulseSep]=setAWG(sampTime_ns=2,qb_pulse_ns=duration,res_pulse_ns=2500,driveReadSep_ns=20,triggerInterval=triggerInterval)
		time.sleep(0.1)
		[amp,phase]=measureIQ(nLoops=nLoops,averageOverSequence=True,convertToAmpPhase=True)
		data.set(duration=qb_pulse,amp=amp,phase=phase)
		data.commit()	
	#coil.turnOff()
	[y0,yAmp,t0,rabiPeriod],yfit,yFitGuess=fitCosine(data['amp'],x=data['duration'])
	data.createColumn("rabiFit",yfit)
	piRabi=rabiPeriod/2
	if dataSave:
		data.savetxt()
	print "Pi pulse length = %f ns"%piRabi	 
	return piRabi

# best sampling time to place two pi/2 pulse and a given number of T1 after readout pulse
def bestAWGRamsey(qb_pulse_ns=10,pulseSep_ns=100,driveReadSep0_ns=20,res_pulse_ns=2500,t1Estim_ns=10000,nT1After=5): 
	bestSampTime=ceil((2*qb_pulse_ns+pulseSep_ns+driveReadSep0_ns+res_pulse_ns)/20000.) 
	if bestSampTime > qb_pulse_ns/5: print 'Alert:step = ',bestSampTime,'ns is longer than 20% of qubit pulse'
	bestTriggerInterval=ceil(bestSampTime*20000+nT1After*t1Estim_ns)
	return bestSampTime, bestTriggerInterval
#
def ramseyMeas(nLoops=1,fQubit='',powerQubit='',fRes='',attenRes='',piPulse=25,detuning='',t1Estim=10000,start=0,stop=1000,step=10,data='',pulseType='square',readoutType='readout',type='normal',echoSep1=1, autoPlot=True,autoClear=False,debug=False,dataSave=False):
	if data=='':	
		data=Datacube('Ramsey')
		DataManager().addDatacube(data)
	if autoPlot:
		data.defineDefaultPlot("duration","amp")
		data.defineDefaultPlot("duration","ramseyFit")
		DataManager().addDatacube(data)
		DataManager().autoPlot(data,autoClear)
	mw_qb.turnOn()
	if powerQubit!='': mw_qb.setPower(powerQubit)
	if fQubit!='': mw_qb.setFrequency(fQubit)
	if detuning !='': mw_qb.setFrequency(mw_qb.frequency()+detuning)
	if fRes!='': mw_cav.setFrequency(fRes)
	if attenRes!='': attenuator.setVoltage(attenRes)
	#coil.turnOn()
	print 'ramseyMeas with fQubit=',mw_qb.frequency(),' powerQubit=',mw_qb.power()
	time.sleep(1)
	durations=SmartLoop(start,step,stop,name="durations")
	for duration in durations:
		sampTime_ns,triggerInterval=bestAWGRamsey(qb_pulse_ns=piPulse,pulseSep_ns=duration,res_pulse_ns=2500,t1Estim_ns=t1Estim,nT1After=4.5)
		[qbPulse, resPulse,driveReadSep,pulseSep]=setAWG(sampTime_ns=sampTime_ns,qb_pulse_ns=piPulse,res_pulse_ns=2500,ramsey=type,echoSep1=echoSep1,triggerInterval=triggerInterval,pulseSep_ns=duration,debug=debug)
		if qbPulse!=piPulse and duration==start: print 'Alert: pi/2 pulse =',qbPulse,' ns instead of ',piPulse/2,' ns'
		time.sleep(0.1)
		[amp,phase]=measureIQ(nLoops=nLoops,averageOverSequence=True,convertToAmpPhase=True)
		data.set(duration=pulseSep,amp=amp,phase=phase)
		data.commit()	
	#coil.turnOff()
	ramseyPeriod=0
	t2=0
	if type=='normal':
		[y0,yAmp,t0,ramseyPeriod,t2],yfit,yFitGuess=fitCosineExp(data['amp'],x=data['duration'])
		data.createColumn("ramseyFit",yfit)
		print "Ramsey period = ", ramseyPeriod," ns. T2 = ",t2, " ns."
		if 0.8*abs(detuning)<1/ramseyPeriod<1.2*abs(detuning):
			newQbFreq=mw_qb.frequency()+1/ramseyPeriod
		else:
			newQbFreq=mw_qb.frequency()-detuning
		if dataSave:
			data.savetxt()
		return [ramseyPeriod,t2,newQbFreq]
	elif type=='echo':
		[y0,yAmp,t0,t2],yfit,yFitGuess=fitT1(data['amp'],x=data['duration'],initialT1=10000)
		data.createColumn("ramseyFit",yfit)
		print " T2 = ",t2, " ns."
		if dataSave:
			data.savetxt()
		return t2
	else:
		if dataSave:
				data.savetxt()
		return
		
# best sampling time to place a pi pulse and nT1Before and nT1After T1 before and after the readout pulse, respectively
def bestAWGParameters(qb_pulse_ns=20,driveReadSep0_ns=20,res_pulse_ns=1500,t1Estim_ns=10000,nT1Before=5,nT1After=5):
	bestSampTime=ceil((qb_pulse_ns+nT1Before*t1Estim_ns+driveReadSep0_ns+res_pulse_ns)/(20000.))
	bestTriggerInterval=ceil(bestSampTime*20000+nT1After*t1Estim_ns)
	return bestSampTime, bestTriggerInterval
#
def t1Meas(nLoops=1,targettedPointAccuracy='',firstT1Try=10000,fQubit='',powerQubit='',fRes='',attenRes='',pulseType='square',readoutType='readout',piRabi=50,data='',autoPlot=True,autoClear=False,dataSave=True,debug=False):
	if powerQubit!='': mw_qb.setPower(powerQubit)
	if fQubit!='': mw_qb.setFrequency(fQubit)
	if fRes!='': mw_cav.setFrequency(fRes)
	if attenRes!='': attenuator.setVoltage(attenRes)
	t1Estim=firstT1Try
	res_pulse_ns=2500
	if data=='':	
		data=Datacube('T1')
		DataManager().addDatacube(data)
	if autoPlot:
		data.defineDefaultPlot("delay","amp")
		data.defineDefaultPlot("delay","T1fit")
		DataManager().addDatacube(data)
		DataManager().autoPlot(data,autoClear)
	print 't1Meas with fQubit=',mw_qb.frequency(),' powerQubit=',mw_qb.power()
	# First step: Determine the signal for relaxed state by switching off the drive 
	mw_qb.turnOff()
	delay=0
	sampTime_ns,triggerInterval=bestAWGParameters(qb_pulse_ns=piRabi,driveReadSep0_ns=20,res_pulse_ns=res_pulse_ns,t1Estim_ns=t1Estim,nT1Before=4.5,nT1After=4.5)
	if debug:	print 'sampling time = ', sampTime_ns, 'triggerInterval = ',triggerInterval
	if pulseType=='gaussian':		
		[qb_pulse,center,ch1_pulse,driveReadSep]=setAWGV2(sampTime_ns=sampTime_ns,triggerInterval=triggerInterval,ch1=True,ch1_pulseType=readoutType,ch1_pulse_ns=res_pulse_ns,driveReadSep_ns=20+delay,ch3=True,ch3_pulseType='gaussian',sigma_ns=piRabi)
	else:	
		[qb_pulse,res_pulse,DelayFromZero,pulseSep]=setAWG(sampTime_ns=sampTime_ns,qb_pulse_ns=piRabi,res_pulse_ns=res_pulse_ns,driveReadSep_ns=20+delay,triggerInterval=triggerInterval)
	
	if qb_pulse!=piRabi: print 'Alert: pi pulse =',qb_pulse,' ns instead of ',piRabi,' ns'
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
			print 'ampOff=%f'%ampOff	
	#data.set(delay=delay,ampOff=ampOff,relSig=0) # relative signal reduction is 0 by definition
	#data.commit()
	# Second step measure the signal just after excitation (zero time)
	mw_qb.turnOn()
	
	if pulseType=='gaussian':		
		[qb_pulse,center,ch1_pulse,driveReadSep]=setAWGV2(sampTime_ns=sampTime_ns,triggerInterval=triggerInterval,ch1=True,ch1_pulseType=readoutType,ch1_pulse_ns=res_pulse_ns,driveReadSep_ns=20+delay,ch3=True,ch3_pulseType='gaussian',sigma_ns=piRabi)
	else:	
		[qb_pulse,res_pulse,DelayFromZero,pulseSep]=setAWG(sampTime_ns=sampTime_ns,qb_pulse_ns=piRabi,res_pulse_ns=res_pulse_ns,driveReadSep_ns=20+delay,triggerInterval=triggerInterval)
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
		sampTime_ns,triggerInterval= bestAWGParameters(qb_pulse_ns=piRabi,driveReadSep0_ns=20,res_pulse_ns=1500,t1Estim_ns=10000,nT1Before=5,nT1After=5)
		if pulseType=='gaussian':		
			[qb_pulse,center,ch1_pulse,driveReadSep]=setAWGV2(sampTime_ns=sampTime_ns,triggerInterval=triggerInterval,ch1=True,ch1_pulseType=readoutType,ch1_pulse_ns=res_pulse_ns,driveReadSep_ns=20+delay,ch3=True,ch3_pulseType='gaussian',sigma_ns=piRabi)
		else:		
			[qb_pulse,res_pulse,DelayFromZero,pulseSep]=setAWG(sampTime_ns=sampTime_ns,qb_pulse_ns=piRabi,res_pulse_ns=res_pulse_ns,driveReadSep_ns=20+delay,triggerInterval=triggerInterval)	
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
	delays=array([0.1,0.25,0.5,1.,2.,2.5,3,3.7,3.8,3.9,4])*t1Estim
	for delay2 in delays:
		delay=delay2
		sampTime_ns,triggerInterval=bestAWGParameters(qb_pulse_ns=piRabi,driveReadSep0_ns=20,res_pulse_ns=res_pulse_ns,t1Estim_ns=t1Estim,nT1Before=4.5,nT1After=4.5)
		delay= round(delay/sampTime_ns)*sampTime_ns
		if pulseType=='gaussian':		
			[qb_pulse,center,ch1_pulse,driveReadSep]=setAWGV2(sampTime_ns=sampTime_ns,triggerInterval=triggerInterval,ch1=True,ch1_pulseType=readoutType,ch1_pulse_ns=res_pulse_ns,driveReadSep_ns=20+delay,ch3=True,ch3_pulseType='gaussian',sigma_ns=piRabi)
		else:	
			[qb_pulse,res_pulse,DelayFromZero,pulseSep]=setAWG(sampTime_ns=sampTime_ns,qb_pulse_ns=piRabi,res_pulse_ns=res_pulse_ns,driveReadSep_ns=20+delay,triggerInterval=triggerInterval)
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
def measureAtAWorkingPoint(data='',coilCurrent=0,attenRes=3.75,freqCenter_qb='',powerQubitSpectro=0,powerQubitDrive=10,stopRabi=100,stepRabi=4,firstT1Try=10000,targettedPointAccuracy=0.01,stopRamsey=15000,stepRamsey=100,detuningRamsey=-0.001):
	start = time.clock()
	print 'measureAtAWorkingPoint VCoil=',coilVoltage,'...'
#create a datacube for this working point	 if none is specified
	if data=='':	
		data=Datacube("coilCurrent=%f"%coilCurrent)
		DataManager().addDatacube(data)
#initial parameters
	frequencyResBare=7.080
	coil.setCurrent(coilCurrent)
	coil.turnOn()
	if freqCenter_qb=='':	freqCenter_qb=fvsVcoil(coilVoltage) 
	chi=0.09**2/(freqCenter_qb-frequencyResBare)
	freqCenter_Res=frequencyResBare-chi
# resonator spectro
	setAWG(sampTime_ns=2,qb_pulse_ns=2000,res_pulse_ns=1500,driveReadSep_ns=20)
	resSpecData=Datacube('ResoSpec %f V, Icoil=%f'%(attenRes,coil.current()))
	data.addChild(resSpecData)
	frequencyRes=resSpec(nLoops=5,fcenter=freqCenter_Res,fspan=0.04,fstep=0.0005,attenRes=attenRes,data=resSpecData,autoClear=True)
# qubit spectro
	setAWG(sampTime_ns=2,qb_pulse_ns=12000,res_pulse_ns=1500,driveReadSep_ns=20)
	qbSpecData=Datacube('spectroscopy01 %f dBm, vcoil=%f'%(powerQubitSpectro,coil.current()))
	data.addChild(qbSpecData)
	frequency01=qbSpec(nLoops=5,fcenter=freqCenter_qb,fspan=0.23,fstep=0.001,powerQubit=powerQubitSpectro,fReadout=frequencyRes,attenRes=attenRes,data=qbSpecData)
# Rabi oscillation
	rabiData=Datacube('rabi %f dBm, frequency=%f'%(powerQubitDrive,frequency01))
	data.addChild(rabiData)
	piRabi=rabiMeas(nLoops=20,fQubit=frequency01,powerQubit=powerQubitDrive,fRes=frequencyRes,attenRes=attenRes,start=0,stop=stopRabi,step=stepRabi,data=rabiData)

# T1
	t1Data=Datacube('t1 %f dBm, frequency=%f, qubitPulse=%f ns'%(powerQubitDrive,frequency01,piRabi))
	data.addChild(t1Data)
	t1=t1Meas(nLoops=10,targettedPointAccuracy=targettedPointAccuracy,firstT1Try=firstT1Try,fQubit=frequency01,powerQubit=powerQubitDrive,fRes=frequencyRes,attenRes=attenRes,piRabi=piRabi,data=t1Data)

# T2 Ramsey
	t2Data=Datacube('t2 %f dBm, frequency=%f, qubitPulse=%f ns'%(powerQubitDrive,frequency01,piRabi/2))
	data.addChild(t2Data)
	t2=ramseyMeas(nLoops=20,fQubit=frequency01,powerQubit=powerQubitDrive,piPulse=piRabi,detuning=detuningRamsey,t1Estim=10000,start=0,stop=stopRamsey,step=stepRamsey,data=t2Data)[1]
	

	codeExecTime =time.clock()-start
	data.set(frequencyRes=frequencyRes,frequency01=frequency01,piRabi=piRabi,t1=t1,t2=t2,codeExecTime=codeExecTime)
	data.commit()
	data.savetxt()
	print 'done in ',codeExecTime, 's.'
	return [frequencyRes,frequency01,piRabi,t1,t2,codeExecTime]
## spectro Resonator + qubit + Rabi + T1 + Ramsey + HahnEcho+ spectro Resonator e
def measureAtAWorkingPointV2(doResSpec=True,data='',coilVoltage=0,attenRes=3.75,doQbSpec=True,freqCenter_qb='',powerQubitSpectro=0,doRabi=True,powerQubitDrive=10,stopRabi=100,stepRabi=4,doT1=True,firstT1Try=10000,targettedPointAccuracy=0.01,doRamsey=True,stopRamsey=15000,stepRamsey=100,detuningRamsey=-0.001,doEcho=True,stopEcho=15000,stepEcho=100,detuningEcho=-0.001,doResSpecE=False):
	start = time.clock()
	print 'measureAtAWorkingPoint VCoil=',coilVoltage,'...'
#create a datacube for this working point	 if none is specified
	if data=='':	
		data=Datacube("coilVoltage=%f"%coilVoltage)
		DataManager().addDatacube(data)
#initial parameters
	frequencyResBare=7.045
	coil.setVoltage(coilVoltage)
	coil.turnOn()
	if freqCenter_qb=='':	freqCenter_qb=fvsVcoil(coilVoltage) 
	chi=0.09**2/(freqCenter_qb-frequencyResBare)
	chi_e=0.09**2/(freqCenter_qb-0.3-frequencyResBare)
	freqCenter_Res=frequencyResBare-chi
	freqCenter_Res_e=frequencyResBare-chi_e
	toReturn=[]
# resonator spectro
	if doResSpec:
		setAWG(sampTime_ns=2,qb_pulse_ns=50,res_pulse_ns=2500,driveReadSep_ns=20)
		resSpecData=Datacube('ResoSpec %f V, Vcoil=%f'%(attenRes,coil.voltage()))
		data.addChild(resSpecData)
		frequencyRes=resSpec(nLoops=5,fcenter=freqCenter_Res_e,fspan=0.04,fstep=0.0002,attenRes=attenRes,data=resSpecData,autoClear=True)
		data.set(frequencyRes=frequencyRes)
		toReturn.append(frequencyRes)
# qubit spectro
	if doQbSpec:
		setAWG(sampTime_ns=2,qb_pulse_ns=12000,res_pulse_ns=2500,driveReadSep_ns=20)
		qbSpecData=Datacube('spectroscopy01 %f dBm, Vcoil=%f'%(powerQubitSpectro,coil.voltage()))
		data.addChild(qbSpecData)
		frequency01=qbSpec(nLoops=5,fcenter=freqCenter_qb,fspan=0.1,fstep=0.0005,powerQubit=powerQubitSpectro,fReadout=frequencyRes,attenRes=attenRes,data=qbSpecData)
		data.set(frequency01=frequency01)
		toReturn.append(frequency01)
# Rabi oscillation
	if doRabi:
		rabiData=Datacube('rabi %f dBm, frequency=%f'%(powerQubitDrive,frequency01))
		data.addChild(rabiData)
		piRabi=rabiMeas(nLoops=20,fQubit=frequency01,powerQubit=powerQubitDrive,fRes=frequencyRes,attenRes=attenRes,start=0,stop=stopRabi,step=stepRabi,data=rabiData)
		data.set(piRabi=piRabi)
		toReturn.append(piRabi)

# T1
	if doT1:
		t1Data=Datacube('t1 %f dBm, frequency=%f, qubitPulse=%f ns'%(powerQubitDrive,frequency01,piRabi))
		data.addChild(t1Data)
		t1=t1Meas(nLoops=10,targettedPointAccuracy=targettedPointAccuracy,firstT1Try=firstT1Try,fQubit=frequency01,powerQubit=powerQubitDrive,fRes=frequencyRes,attenRes=attenRes,piRabi=piRabi,data=t1Data)
		data.set(t1=t1)
		toReturn.append(t1)

# T2 Ramsey
	if doRamsey:
		t2Data=Datacube('t2 %f dBm, frequency=%f, qubitPulse=%f ns'%(powerQubitDrive,frequency01,piRabi/2))
		data.addChild(t2Data)
		[ramseyPeriod,t2]=ramseyMeas(nLoops=20,fQubit=frequency01,powerQubit=powerQubitDrive,piPulse=piRabi,detuning=detuningRamsey,t1Estim=10000,start=0,stop=stopRamsey,step=stepRamsey,data=t2Data)[0:2]
		data.set(t2=t2)
		toReturn.append(t2)
		#frequency correction
		corr_QbFreq=mw_qb.frequency()-sign(detuningRamsey)*1.0/ramseyPeriod
	else:
		corr_QbFreq=5.58027
# Hahn echo
	if doEcho:
		detuningEcho=-0.001
		corr_QbFreq=5.58027
		powerQubit=5
		piRabi=39
		stopEcho=60000
		stepEcho=300
		t2DataHahnEcho=Datacube('t2 HahnEcho %f dBm, frequency=%f, qubitPulse=%f ns'%(powerQubit,corr_QbFreq,piRabi)) 
		t2Echo=ramseyMeas(nLoops=20,fQubit=corr_QbFreq,powerQubit=powerQubit,piPulse=piRabi,detuning=detuningEcho,t1Estim=19000,start=piRabi,stop=stopEcho,step=stepEcho,type='echo',data=t2DataHahnEcho,dataSave=True)
		data.set(t2DataHahnEcho=t2DataHahnEcho)
		toReturn.append(t2DataHahnEcho)
# resonator e spectro
	if doResSpecE:
		mw_qb.setFrequency(corr_QbFreq)
		setAWG(sampTime_ns=2,qb_pulse_ns=piRabi,res_pulse_ns=2500,driveReadSep_ns=20)
		resSpecData=Datacube('ResoSpec e %f V, Vcoil=%f'%(attenRes,coil.voltage()))
		data.addChild(resSpecData)
		frequencyRes=resSpec(nLoops=5,fcenter=freqCenter_Res_e,fspan=0.04,fstep=0.0002,attenRes=attenRes,data=resSpecData,qbGen=True,autoClear=False)
		data.set(frequencyRes=frequencyRes)
		toReturn.append(frequencyRes)

	codeExecTime =time.clock()-start
	data.set(codeExecTime=codeExecTime)
	data.commit()
	data.savetxt()
	toReturn.insert(0,codeExecTime)
	print 'done in ',codeExecTime, 's.'
	return toReturn
##
# T2 Ramsey Echo2
	t2DataEcho2=Datacube('t2 echo %f dBm, frequency=%f, qubitPulse=%f ns'%(powerQubitDrive,frequency01,piRabi/2))
	data.addChild(t2DataEcho2)
	t2Echo=ramseyMeas(nLoops=20,fQubit=frequency01,powerQubit=powerQubitDrive,piPulse=piRabi,detuning=0,t1Estim=10000,start=0,stop=stopRamsey,step=stepRamsey,type='echo2',data=t2DataEcho2)[1]
	
   # T2 Ramsey Echo
	t2DataEcho=Datacube('t2 echo %f dBm, frequency=%f, qubitPulse=%f ns'%(powerQubitDrive,frequency01,piRabi/2))
	data.addChild(t2DataEcho)
	t2Echo=ramseyMeas(nLoops=20,fQubit=frequency01,powerQubit=powerQubitDrive,piPulse=piRabi,detuning=0,t1Estim=10000,start=0,stop=stopRamsey,step=stepRamsey,type='echo',data=t2DataEcho)[1]
##
setAWGV2(sampTime_ns=1,triggerInterval=21000,ch1=True,ch1_pulseType='readout_switch',ch1_pulse_ns=2000,ch1_amp=1,ch2=True,ch2_pulseType='readout_switch',ch2_pulse_ns=2000,ch2_amp=1,driveReadSep_ns=20,ch3=False,ch3_pulseType='gaussian',sigma_ns=2000)
##
def measureAtAWorkingPointV3(doResSpec=True,data='',coilCurrent=0.0,attenRes=2.2,doQbSpec=True,freqCenter_qb=''):
	start = time.clock()
	print 'measureAtAWorkingPoint ICoil=',coilCurrent,'...'
#create a datacube for this working point	 if none is specified
	if data=='':	
		data=Datacube("coilCurrent=%f"%coilCurrent)
		data.toDataManager()
#initial parameters
	frequencyResBare=7.333
	coil.setVoltage(coilCurrent,slewRate=0.001)
	coil.turnOn()
	#chi_e=0.09**2/(freqCenter_qb-0.3-frequencyResBare)
	#freqCenter_Res=frequencyResBare-chi
	toReturn=[]
# resonator spectro
	if doResSpec:
		setAWGV2(sampTime_ns=1,triggerInterval=21000,ch1=True,ch1_pulseType='readout_switch',ch1_pulse_ns=6000,ch1_amp=1,ch2=True,ch2_pulseType='readout_switch',ch2_pulse_ns=6000,ch2_amp=1,driveReadSep_ns=20,ch3=False,ch3_pulseType='gaussian',sigma_ns=2000)

		resSpecData=Datacube('ResoSpec6, pulseAmp= %f V, Icoil=%f'%(attenRes,coil.voltage()))
		data.addChild(resSpecData)
		frequencyRes=resSpec(nLoops=20,fcenter=7.367,fspan=0.04,fstep=0.0005,attenRes=attenRes,data=resSpecData,fit=True,autoClear=False,autoPlot=False,returnRes=True)
		data.set(frequencyRes=frequencyRes)
		toReturn.append(frequencyRes)
# qubit spectro
	if doQbSpec:
		if freqCenter_qb=='':
			freqCenter_qb=frequencyResBare+0.150**2/(frequencyResBare-frequencyRes)
			print 'center of spec %f'%freqCenter_qb
		setAWGV2(sampTime_ns=1,triggerInterval=21000,ch1=True,ch1_pulseType='readout_switch',ch1_pulse_ns=6000,ch2=True,ch2_pulseType='readout_switch',ch2_pulse_ns=6000,ch2_amp=1,driveReadSep_ns=20,ch3=True,ch3_pulseType='open',sqLength_ns=10000)
		qbSpecData=Datacube('spectroscopy01 %f dBm, Icoil=%f'%(12,coil.voltage()))
		data.addChild(qbSpecData)
		frequency01=qbSpec(nLoops=25,fcenter=freqCenter_qb,fspan=0.35,fstep=0.001,powerQubit=12,fReadout=frequencyRes,attenRes=attenRes,data=qbSpecData,autoPlot=False,autoClear=False)
		data.set(frequency01=frequency01)
		toReturn.append(frequency01)
	 	codeExecTime =time.clock()-start
	data.set(codeExecTime=codeExecTime)
	data.commit()
	data.savetxt()
	toReturn.insert(0,codeExecTime)
	print 'done in ',codeExecTime, 's.'
	return toReturn
##
measureAtAWorkingPointV3(doResSpec=True,data='',coilCurrent=0.0160,attenRes=5.1,doQbSpec=True,freqCenter_qb=6.73)
##
par=measureAtAWorkingPointV2(doResSpec=False,data='',coilVoltage=10,attenRes=4.0,doQbSpec=False,freqCenter_qb='',powerQubitSpectro=-10,doRabi=False,powerQubitDrive=5,stopRabi=200,stepRabi=4,doT1=False,firstT1Try=25000,targettedPointAccuracy=0.01,doRamsey=False,stopRamsey=12000,stepRamsey=100,detuningRamsey=-0.001,doEcho=True,stopEcho=15000,stepEcho=300,detuningEcho=-0.001,doResSpecE=False)

##
for i in range(3):
	par=measureAtAWorkingPointV2(doResSpec=True,data='',coilVoltage=0.16,attenRes=4.0,doQbSpec=True,freqCenter_qb='',powerQubitSpectro=-20,doRabi=True,powerQubitDrive=-10,stopRabi=200,stepRabi=4,doT1=True,firstT1Try=8000,targettedPointAccuracy=0.01,doRamsey=True,stopRamsey=12000,stepRamsey=100,detuningRamsey=-0.001,doResSpecE=True)


## Main section
mainData=Datacube("Qubit charac vs ICoil 7")                   # main datacube whole flux modulation
DataManager().addDatacube(mainData)
doResSpec=True
doQbSpec=True
doRabi=False
doT1=False
doRamsey=False
sampTime_ns=1
qb_pulse_ns=10000
powerQubitSpectro=-20
#powerQubitDrive=10
driveReadSep_ns=20
res_pulse_ns=2000
attenRes=5.5
#stopRabi=120
#stepRabi=2
#stopRamsey=10000
#stepRamsey=100
#detuningRamsey=-0.001
#firstT1Try=10000

coilCurrents=SmartLoop(-0.005,0.0003,0.010,name="coilCurrents")
for coilCurrent in coilCurrents:
	onePointData=Datacube("coilCurrent=%f"%coilCurrent)    #create datacube a child for this flux
	mainData.addChild(onePointData)
  	print "current= %f"%coilCurrent
	try:		
		params0=measureAtAWorkingPointV3(doResSpec=True,data=onePointData,coilCurrent=coilCurrent,attenRes=attenRes,doQbSpec=True)
		
		#this assumes that a T1 has been done before a Ramsey !!!
		#params1=params0+[0]*(7-len(params0))
		#mainData.set(coilCurrent=coilCurrent,frequencyRes=params1[1],frequency01=params1[2],piRabi=params1[3],t1=params1[4],t2=params1[5],codeExecTime=params1[0]) 
		mainData.set(coilCurrent=coilCurrent) 
		mainData.commit()
	except RuntimeError: 
		print 'Fitting error at %f'%coilCurrent
		pass	
		
			
			
mainData.savetxt()
##
"""
		piRabi=params1[3]
		t1=params1[4]
		stopRabi=round (5*piRabi)
		stepRabi=max(round(piRabi/6),2)
		if 100<t1<100000:
			firstT1Try=t1
		else:
			firstT1Try=10000
		print 'success' 
	except RuntimeError: 
		print 'Fitting error at %f'%coilVoltage
		pass
"""
## CODE DV
mainData=Datacube("Qubit charac vs iCoil 2")                   # main datacube whole flux modulation
DataManager().addDatacube(mainData)
sampTime_ns=1
qb_pulse_ns=6000
powerQubitSpectro=-25
powerQubitDrive=10
driveReadSep_ns=20
res_pulse_ns=2500
attenRes=4.0
stopRabi=120
stepRabi=2
stopRamsey=10000
stepRamsey=100
detuningRamsey=-0.001
firstT1Try=10000

coilCurrents=SmartLoop(0.9e-3,0.05e-3,1.5e-3,name="coilCurrents")
for coilCurrent in coilCurrents:
	onePointData=Datacube("coilCurrent=%f"%coilCurrent)    #create datacube a child for this flux
	mainData.addChild(onePointData)
  	print "current= %f"%coilCurrent
	try:		
		[frequencyRes,frequency01,piRabi,t1,t2,codeExecTime]=measureAtAWorkingPoint(coilCurrent=coilCurrent,attenRes=attenRes,powerQubitSpectro=powerQubitSpectro,powerQubitDrive=powerQubitDrive,firstT1Try=firstT1Try,stopRabi=stopRabi,stepRabi=stepRabi,stopRamsey=stopRamsey,stepRamsey=stepRamsey,detuningRamsey=detuningRamsey,targettedPointAccuracy=0.01,data=onePointData)
		mainData.set(coilCurrent=coilCurrent,frequencyRes=frequencyRes,frequency01=frequency01,piRabi=piRabi,t1=t1,t2=t2,codeExecTime=codeExecTime)
		mainData.commit()
		stopRabi=round (5*piRabi)
		stepRabi=max(round(piRabi/6),2)
		if 100<t1<100000:
			firstT1Try=t1
		else:
			firstT1Try=10000
		print 'success' 
	except RuntimeError: 
		print 'Fitting error at %f'%coilCurrent
		pass
		
mainData.savetxt()



## Set working point and parameters
frequencyResBare=7.333
spanRes=0.03
coilCurrent=0.016
coil.turnOn()
coil.setVoltage(coilCurrent,slewRate=0.001)
freqCenter_qb=fvsIcoil(coilCurrent)          		  # calculated first parameters 
chi=0.135**2/(freqCenter_qb-frequencyResBare)
freqCenter_Res=frequencyResBare-chi
span01=0.1
powerQubit=12
T1est=10000
attenRes=5.1
readoutType='readout_switch'
print fvsIcoil(coilCurrent)
print freqCenter_Res
print freqCenter_qb

##

freqCenter_Res=7.334
mw_cav.setFrequency(frequencyRes)

## Resonator line

freqCenter_Res=6.435
fspan=0.1
fstep=0.0005
#setAWGV2(sampTime_ns=2,triggerInterval=51000,ch1=True,ch1_pulseType='readout_',ch1_pulse_ns=2500,driveReadSep_ns=20,ch3=True,ch3_pulseType='gaussian',sigma_ns=2000)
setAWGV2(sampTime_ns=1,triggerInterval=21000,ch1=True,ch1_pulseType='readout_switch',ch1_pulse_ns=6000,ch1_amp=1,ch2=True,ch2_pulseType='readout_switch',ch2_pulse_ns=6000,ch2_amp=1,driveReadSep_ns=20,ch3=False,ch3_pulseType='gaussian',sigma_ns=2000)
#setAWG(sampTime_ns=2,qb_pulse_ns=12000,res_pulse_ns=2500,driveReadSep_ns=20,triggerInterval=51000)
resSpecData=Datacube('ResoSpec6, pulseAmp= %f V, Icoil=%f'%(attenRes,coil.voltage()))
resSpecData.toDataManager()
frequencyRes=resSpec(nLoops=20,fcenter=freqCenter_Res,fspan=fspan,fstep=fstep,attenRes=attenRes,data=resSpecData,fit=True,autoClear=False,autoPlot=False,returnRes=True)

## Resonator line for e state->check piRabi and qubit frequency
setAWGV2(sampTime_ns=2,triggerInterval=150000,ch1=True,ch1_pulseType='readout_switch',ch1_pulse_ns=2500,driveReadSep_ns=20,ch3=True,ch3_pulseType='gaussian',sigma_ns=piRabi)
#setAWG(sampTime_ns=2,qb_pulse_ns=piRabi,res_pulse_ns=2500,driveReadSep_ns=20,triggerInterval=51000)
resSpecData=Datacube('ResoSpec-e, att= %f V, Vcoil=%f, piRabi=%f ns'%(attenRes,coil.voltage(),piRabi))
frequencyRes_E=resSpec(nLoops=10,fcenter=freqCenter_Res,fspan=0.05,fstep=0.0002,attenRes=attenRes,data=resSpecData,qbGen=True,autoClear=False)

##



##qubit spectroscopy in microwave frequency
#freqCenter_qb=frequencyResBare+0.150**2/(frequencyResBare-frequencyRes)
freqCenter_qb=6.712
##
setAWGV2(sampTime_ns=1,triggerInterval=21000,ch1=True,ch1_pulseType='readout_switch',ch1_pulse_ns=6000,ch2=True,ch2_pulseType='readout_switch',ch2_pulse_ns=6000,ch2_amp=1,driveReadSep_ns=20,ch3=True,ch3_pulseType='open',sqLength_ns=10000)
#setAWG(sampTime_ns=2,qb_pulse_ns=12000,res_pulse_ns=2500,driveReadSep_ns=20,triggerInterval=51000)
qbSpecData=Datacube('spectroscopy01 %f dBm, vcoil=%f'%(powerQubit,coil.voltage()))
frequency01=qbSpec(nLoops=25,fcenter=freqCenter_qb,fspan=0.15,fstep=0.001,powerQubit=powerQubit,fReadout=frequencyRes,attenRes=attenRes,data=qbSpecData,autoPlot=False,autoClear=False)

##
attenRes=5.5
freqCenter_qb=
freqCenter_Res=7.3597
#frequencyRes=7.2799#mw_cav.frequency()
##
#powerQubit=-10
##qubit spectroscopy in microwave frequency with population of the resonator
setAWG(sampTime_ns=2,qb_pulse_ns=12000,res_pulse_ns=1500,resDriveLength_ns=800,resDriveDelay_ns=20,driveReadSep_ns=20,triggerInterval=51000)
qbSpecData=Datacube('spectroscopy01 %f dBm, vcoil=%f'%(powerQubit,coil.current()))
frequency01=qbSpec(nLoops=10,fcenter=freqCenter_qb,fspan=0.3,fstep=0.005,powerQubit=powerQubit,fReadout=frequencyRes,attenRes=attenRes,data=qbSpecData,autoClear=False)


##qubit spectroscopy in flux
frequencyRes= 7.05672971825
frequency01= 6.40
iCoilStart=-6.0e-3
iCoilStop=6.0e-3
iCoilStep=0.08e-3
##
setAWG(sampTime_ns=2,qb_pulse_ns=12000,res_pulse_ns=1500,driveReadSep_ns=20,triggerInterval=51000)
qbSpecCoilData=Datacube('coil spectroscopy %s dBm, f=%f GHz'%(powerQubit,frequency01))
iCoilQubit=qbSpecCoil(nLoops=5,iCoilStart=iCoilStart, iCoilStop=iCoilStop,iCoilStep=iCoilStep,fQubit=frequency01,powerQubit='',fReadout=frequencyRes,attenRes=attenRes,data=qbSpecCoilData,autoClear=False)

## Rabi oscillation
#frequency01=correct_freq
#frequency01=5.0860
powerQubit=-5
rabiData=Datacube('rabi %f dBm, frequency=%f'%(powerQubit,frequency01))
piRabi= rabiMeas(nLoops=10,fQubit=frequency01,powerQubit=powerQubit,fRes=frequencyRes,attenRes=attenRes,start=0,stop=200,step=5,data=rabiData,autoClear=False)

## Rabi oscillations with gaussian pulses
powerQubit=-10
rabiData=Datacube('rabi-gaussian %f dBm, frequency=%f'%(powerQubit,frequency01))
piRabi= rabiMeas(nLoops=20,fQubit=frequency01,powerQubit=powerQubit,fRes=frequencyRes,attenRes=attenRes,pulseType='gaussian',readoutType='readout_switch',start=0,stop=600,step=2,data=rabiData,autoClear=False)
## T1 measurement
#frequency01=5.0797
powerQubit=-10
T1Data=Datacube('t1 %f dBm, frequency=%f, qubitPulse=%f ns'%(powerQubit,frequency01,piRabi))
T1=t1Meas(nLoops=30,firstT1Try=10000,fQubit=frequency01,powerQubit=powerQubit,fRes=frequencyRes,attenRes=attenRes,pulseType='gaussian',readoutType='readout_switch',piRabi=piRabi,data=T1Data,autoPlot=True,autoClear=False,debug=False)

## T2 Ramsey
frequency01=5.41213
mw_qb.setFrequency(frequency01)
##
#frequency01=correct_freq
powerQubit=5
piRabi=piRabi
t2Data=Datacube('t2 %f dBm, frequency=%f, qubitPulse=%f ns'%(powerQubit,frequency01,piRabi)) 
t2=ramseyMeas(nLoops=20,fQubit=frequency01,powerQubit=powerQubit,piPulse=piRabi,detuning=-0.002,t1Estim=19000,start=0,stop=6000,step=50,data=t2Data,dataSave=True)[1]
##
print mw_qb.frequency()
correct_freq=mw_qb.frequency()+1.0/1240
print correct_freq

## T2 Ramsey Echo
#frequency01=5.28282913865
powerQubit=5
piRabi=40
t2DataHahnEcho=Datacube('t2 HahnEcho %f dBm, frequency=%f, qubitPulse=%f ns'%(powerQubit,frequency01,piRabi)) 
t2Echo=ramseyMeas(nLoops=20,fQubit=frequency01,fRes=7.04966,powerQubit=powerQubit,piPulse=piRabi,detuning=-0.001,t1Estim=19000,start=piRabi,stop=60000,step=300,type='echo',data=t2DataHahnEcho,dataSave=True)

## T2 Ramsey Echo 2

frequency01=correct_freq
powerQubit=-5
piRabi=piRabi
echoSep1=4000
##
t2DataEcho2=Datacube('t2 echo 2 %f dBm, frequency=%f, qubitPulse=%f ns'%(powerQubit,frequency01,piRabi)) 
ramseyMeas(nLoops=20,fQubit=frequency01,powerQubit=powerQubit,piPulse=piRabi,detuning=-0.002,t1Estim=10000,start=piRabi+echoSep1,stop=18000,step=50,type='echo2',echoSep1=echoSep1,data=t2DataEcho2,dataSave=True)
##

for echoSep1 in [1000, 2000, 3000, 4000, 5000]:
	t2DataEcho2=Datacube('t2 echo 2 %f dBm, frequency=%f, qubitPulse=%f ns'%(powerQubit,frequency01,piRabi)) 
	ramseyMeas(nLoops=20,fQubit=frequency01,powerQubit=powerQubit,piPulse=piRabi,detuning=-0.000,t1Estim=10000,start=piRabi+echoSep1,stop=18000,step=10,type='echo2',echoSep1=echoSep1,data=t2DataEcho2,dataSave=True)


## Load data
data=gv.data
##
[y0,yAmp,t0,ramseyPeriod,t2],yfit,yFitGuess=fitCosineExp(data['amp'],x=data['duration'],initialY0='',initialYAmp='',initialX0='',initialPeriod='',initialXc='',debug=False)
print ramseyPeriod,t2
##
[y0,yAmp,t0,rabiPeriod],yfit,yFitGuess=fitCosine(data['amp'],x=data['duration'])
print rabiPeriod/2
##
[y0,yAmp,x0,t1],yFit,yFitGuess=fitT1(data['amp'],data['duration'],initialY0=0.004,initialYAmp=0.003,initialX0=0,initialT1=20000,debug=False)
print t1


##
reload(waveGen)
##
waveGen.openMixer()
AWG.setRunMode('CONT')
##
mw_qb.setFrequency(8.0)
##
fcenter=7.308
fspan=0.5
fstep=0.002
nLoops=10
data=Datacube('ResSpec1')
data.toDataManager()
frequencyLoop=SmartLoop(fcenter-fspan/2,fstep,fcenter+fspan/2,name='resonator frequency')
for f in frequencyLoop:
		mw_cav.setFrequency(f)
		time.sleep(0.1)
		[amp,phase]=measureIQ(nLoops=nLoops,averageOverSequence=True,convertToAmpPhase=False)
		data.set(f_GHz=f,amp=amp,phase=phase)
		data.commit()
## Testing measureIQOffOn ##
print measureIQOffOn(nLoops=1,wantedChannels=3, firstSlice=slice(0,180),secondSlice=slice(200,399),startMargin=0,middleMargin=0.1,stopMargin=0,averageOverSequence=True,convertToAmpPhase=False,OnBeforeOff=False)
##
fcenter=7.34
fspan=0.2
fstep=0.0005
nLoops=10
data=Datacube('ResSpec3')
data.toDataManager()
frequencyLoop=SmartLoop(fcenter-fspan/2,fstep,fcenter+fspan/2,name='resonator frequency')
for f in frequencyLoop:
		mw_cav.setFrequency(f)
		time.sleep(0.1)
		[I,Q,Ioff,Qoff,Ion,Qon]=measureIQOffOn(nLoops=10,wantedChannels=3, firstSlice=slice(0,180),secondSlice=slice(200,399),startMargin=0,middleMargin=0.1,stopMargin=0,averageOverSequence=True,convertToAmpPhase=False,OnBeforeOff=False)
		data.set(f_GHz=f,I=I,Q=Q)
		data.commit()
##
data.createCol(name='amp',values=sqrt(data['I']**2+data['Q']**2))
data.createCol(name='phase',values=arctan(data['Q']/data['I']))