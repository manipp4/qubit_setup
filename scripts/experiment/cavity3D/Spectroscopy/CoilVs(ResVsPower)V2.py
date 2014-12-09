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
mw_qb=Manager().getInstrument('MWSource_Qubit2')
pg_qb=Manager().getInstrument('pg_qb')
pg_cav=Manager().getInstrument('pg_cavity')
pg_ch2=Manager().getInstrument('pg_cavity_switch')
attenuator=Manager().getInstrument('Yoko3')
register=Manager().getInstrument('register')


# All functions

##
# function giving qubit frequency versus coil drive
def fvsIcoil(I):
	fmax=7.5453
	Ioff=(-1.44)*1.e-3 #Ioff=-0.0089 2.51 mA
	Iperiod=(6.78)*1.e-3
	f=fmax*sqrt(abs(cos((I-Ioff)*pi/Iperiod)))	
	return f


# Lorentzian pure function
def Lorenzian(y0,yAmp,x0,width):
	return lambda x: y0+yAmp/(1.0+pow(2.0*(x-x0)/width,2)) 

# Cosine pure function
def cosine(y0,yAmp,x0,period):
	return lambda x: y0+yAmp*cos(2*math.pi*(x-x0)/period)
	

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

#
def setAWG(sampTime_ns=1,qb_pulse_ns=2000,res_pulse_ns=5000,resDriveLength_ns='',resDriveDelay_ns='',driveReadSep_ns=20,pulseSep_ns=0,triggerInterval=21000,ramsey=False,echoSep1=100,debug=False): #nanoseconds per point
	samplRate=1.e9/sampTime_ns
	reprate=samplRate/20000.
	AWG.setRepetitionRate(reprate)
	AWG.setTriggerInterval(triggerInterval*1e-9)# has to be specidfied in seconds
	
	if ramsey!=False:
		print 'ramsey pulse'
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
	pg_ch2.clearPulse()
	pg_ch2.generatePulse(duration=res_pulse, frequency=mw_cav.frequency(), DelayFromZero=DelayFromZero_res,useCalibration=False)
	pg_ch2.generateMarker(name='marker2',start=DelayFromZero_res-1000,stop=DelayFromZero_res,level=3)
	pg_ch2.sendPulse(markersName='marker2')
	#time.sleep(4)
	return qb_pulse*sampTime_ns, res_pulse*sampTime_ns, driveReadSep*sampTime_ns, pulseSep*sampTime_ns

#
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

#
def resSpec(nLoops=1,fcenter=1,fspan=1,fstep=0.1,attenRes=4,data='',qbGen=False,fit=True,autoPlot=True,autoClear=False,dataSave=True):
	if data=='':	
		data=Datacube('ResSpec')
		DataManager().addDatacube(data)
	if autoPlot:
		data.defineDefaultPlot("f_GHz","amp")
		if fit:
			data.defineDefaultPlot("f_GHz","ampFit")
		DataManager().addDatacube(data)
		DataManager().autoPlot(data,autoClear)
	#setAWG(sampTime_ns=1,qb_pulse_ns=2000,res_pulse_ns=3000,driveReadSep_ns=20)
	if qbGen:
		mw_qb.turnOn()
	else:
		mw_qb.turnOff()
	mw_cav.turnOn()
	attenuator.setVoltage(attenRes)
	frequencyLoop=SmartLoop(fcenter-fspan/2,fstep,fcenter+fspan/2,name='resonator frequency')
	coil.turnOn()
	print 'resSpec with attenRes=',attenuator.voltage()
	time.sleep(1)
	for f in frequencyLoop:
		mw_cav.setFrequency(f)
		[amp,phase]=measureIQ(nLoops=nLoops,averageOverSequence=True,convertToAmpPhase=True)
		data.set(f_GHz=f,amp=amp,phase=phase)
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
	if fit:
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
		[amp,phase]=measureIQ(nLoops=nLoops,averageOverSequence=True,convertToAmpPhase=True)
		data.set(f_GHz=f,amp=amp,phase=phase)
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
def rabiMeas(nLoops=1,fQubit='',powerQubit='',fRes='',attenRes='',t1Estim=10000,start=0,stop=1000,step=10,data='',autoPlot=True,autoClear=False,dataSave=True):
	if data=='':	
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
		sampTime_ns,triggerInterval=bestAWGParameters(qb_pulse_ns=duration,driveReadSep0_ns=20,res_pulse_ns=1500,t1Estim_ns=t1Estim,nT1Before=4.5,nT1After=4.5)
		[qb_pulse,res_pulse,DelayFromZero,pulseSep]=setAWG(sampTime_ns=2,qb_pulse_ns=duration,res_pulse_ns=1500,driveReadSep_ns=20,triggerInterval=triggerInterval)
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


		
# best sampling time to place a pi pulse and nT1Before and nT1After T1 before and after the readout pulse, respectively
def bestAWGParameters(qb_pulse_ns=20,driveReadSep0_ns=20,res_pulse_ns=1500,t1Estim_ns=10000,nT1Before=5,nT1After=5):
	bestSampTime=ceil((qb_pulse_ns+nT1Before*t1Estim_ns+driveReadSep0_ns+res_pulse_ns)/(20000.))
	bestTriggerInterval=ceil(bestSampTime*20000+nT1After*t1Estim_ns)
	return bestSampTime, bestTriggerInterval
# resonator spectroscopy vs power
def ResVsPow(nLoops=1,fcenter=7.08,fspan=0.04,fstep=0.1,attenStart=4,attenStop=0,attenStep=-0.1,qbState='g',qbFreq=6,qbPower=-10,piPulse=30,data='',autoPlot=True,autoClear=False,dataSave=True):
	if data=='':	
		data=Datacube('ResVsPow_%s'%qbState)
		DataManager().addDatacube(data)
	if autoPlot:
		data.defineDefaultPlot("f_GHz","amp")
		data.defineDefaultPlot("f_GHz","ampFit")
		DataManager().addDatacube(data)
		DataManager().autoPlot(data,autoClear)	
	setAWG(sampTime_ns=2,qb_pulse_ns=piPulse,res_pulse_ns=1500,driveReadSep_ns=20)
	attenuations=SmartLoop(attenStart,attenStep,attenStop,name='attenuator voltage')
	for attenuation in attenuations:
		if qbState=='g':
			resSpecData=Datacube('ResSpec_%s %f V'%(qbState,attenuation))
			data.addChild(resSpecData)
			frequencyRes=resSpec(nLoops=5,fcenter=fcenter,fspan=fspan,fstep=fstep,attenRes=attenuation,fit=False,data=resSpecData,autoPlot=autoPlot,autoClear=autoClear,dataSave=dataSave)
		else:
			mw_qb.setFrequency(qbFreq)
			mw_qb.setPower(qbPower)
			resSpecData=Datacube('ResSpec_%s %f V'%(qbState,attenuation))
			data.addChild(resSpecData)
			frequencyRes=resSpec(nLoops=5,fcenter=fcenter,fspan=fspan,fstep=fstep,attenRes=attenuation,qbGen=True,fit=False,data=resSpecData,autoPlot=autoPlot,autoClear=autoClear,dataSave=dataSave)
		data.set(attenuation=attenuation)
		data.commit()
	if dataSave:
		data.savetxt()			


## spectro Resonator + qubit + Rabi + ResVsPow g +ResVsPow e
def measureAtAWorkingPoint(coilCurrent=0,freqCenter_qb='',attenRes=3.75,powerQubitSpectro=0,powerQubitDrive=10,stopRabi=100,stepRabi=4,attenStart=4.5,attenStep=-0.1,attenStop=0.8,data=''):
	start = time.clock()
	print 'measureAtAWorkingPoint iCoil=',coilCurrent,'...'
#create a datacube for this working point	 if none is specified
	if data=='':	
		data=Datacube("coilCurrent=%f"%coilCurrent)
		DataManager().addDatacube(data)
#initial parameters
	frequencyResBare=7.080
	coil.setCurrent(coilCurrent)
	coil.turnOn()
	if freqCenter_qb=='':	freqCenter_qb=fvsIcoil(coilCurrent) 
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

# ResVsPow g
	ResVsPowData_g=Datacube('ResVsPow_g %f dBm, pi=%f ns, frequency=%f'%(powerQubitDrive,piRabi,frequency01))
	data.addChild(ResVsPowData_g)
	ResVsPow(nLoops=5,fcenter=7.09,fspan=0.05,fstep=0.0005,attenStart=attenStart,attenStop=attenStop,attenStep=attenStep,qbState='g',qbFreq=frequency01,qbPower=powerQubitDrive,piPulse=piRabi,data=ResVsPowData_g,autoPlot=True,autoClear=False,dataSave=True)
# ResVsPow e
	ResVsPowData_e=Datacube('ResVsPow_e %f dBm, pi=%f ns, frequency=%f'%(powerQubitDrive,piRabi,frequency01))
	data.addChild(ResVsPowData_e)
	ResVsPow(nLoops=5,fcenter=7.09,fspan=0.05,fstep=0.0005,attenStart=attenStart,attenStop=attenStop,attenStep=attenStep,qbState='e',qbFreq=frequency01,qbPower=powerQubitDrive,piPulse=piRabi,data=ResVsPowData_e,autoPlot=True,autoClear=False,dataSave=True)
	
	codeExecTime =time.clock()-start
	data.set(frequencyRes=frequencyRes,frequency01=frequency01,piRabi=piRabi,codeExecTime=codeExecTime)
	data.commit()
	data.savetxt()
	print 'done in ',codeExecTime, 's.'
	return [frequencyRes,frequency01,piRabi,codeExecTime]
	
	
## CODE DV
mainData=Datacube("Qubit charac vs iCoil 6")                   # main datacube whole flux modulation
DataManager().addDatacube(mainData)
sampTime_ns=2
powerQubitSpectro=-15
powerQubitDrive=-5
driveReadSep_ns=20
res_pulse_ns=1500
attenRes=4.5
stopRabi=400
stepRabi=2
attenStart=6
attenStep=-0.2
attenStop=1
coilCurrents=SmartLoop(-0.09e-3,0.05e-3,0.64e-3,name="coilCurrents")
for coilCurrent in coilCurrents:
	onePointData=Datacube("coilCurrent=%f"%coilCurrent)    #create datacube a child for this flux
	mainData.addChild(onePointData)
  	print "current= %f"%coilCurrent
	try:		
		[frequencyRes,frequency01,piRabi,codeExecTime]=measureAtAWorkingPoint(coilCurrent=coilCurrent,attenRes=attenRes,powerQubitSpectro=powerQubitSpectro,powerQubitDrive=powerQubitDrive,stopRabi=stopRabi,stepRabi=stepRabi,attenStart=attenStart,attenStep=attenStep,attenStop=attenStop,data=onePointData)
		mainData.set(coilCurrent=coilCurrent,frequencyRes=frequencyRes,frequency01=frequency01,piRabi=piRabi,codeExecTime=codeExecTime)
		mainData.commit()
		stopRabi=round (5*piRabi)
		stepRabi=max(round(piRabi/6),2) 
	except RuntimeError: 
		print 'Fitting error at %f'%coilCurrent
		pass
mainData.savetxt()



## Set working point and parameters
frequencyResBare=7.080
spanRes=0.03
coilCurrent=(-0.00)*1e-3
coil.setCurrent(coilCurrent)
coil.turnOn()
freqCenter_qb=fvsIcoil(coilCurrent)          		  # calculated first parameters 
chi=0.09**2/(freqCenter_qb-frequencyResBare)
freqCenter_Res=frequencyResBare-chi
span01=0.1
powerQubit=-4.5
T1est=10000
attenRes=4.5
print fvsIcoil(coilCurrent)
print freqCenter_Res
print freqCenter_qb
##
attenRes=4.5
frequencyRes=7.08
mw_cav.setFrequency(frequencyRes)
## Resonator line
setAWG(sampTime_ns=2,qb_pulse_ns=12000,res_pulse_ns=2500,driveReadSep_ns=20,triggerInterval=51000)
resSpecData=Datacube('ResoSpec %f V, Icoil=%f'%(attenRes,coil.current()))
frequencyRes=resSpec(nLoops=5,fcenter=frequencyRes,fspan=0.04,fstep=0.0003,attenRes=attenRes,data=resSpecData,autoClear=False)
#frequencyRes=resSpec(nLoops=5,fcenter=7.0794,fspan=.1,fstep=0.0005,attenRes=attenRes,data=resSpecData,autoClear=False)

##
freqCenter_qb=6.65
powerQubit=-20
##qubit spectroscopy in microwave frequency
setAWG(sampTime_ns=2,qb_pulse_ns=21000,res_pulse_ns=1500,driveReadSep_ns=20,triggerInterval=51000)
qbSpecData=Datacube('spectroscopy01 %f dBm, vcoil=%f'%(powerQubit,coil.current()))
frequency01=qbSpec(nLoops=5,fcenter=freqCenter_qb,fspan=0.2,fstep=0.0005,powerQubit=powerQubit,fReadout=frequencyRes,attenRes=attenRes,data=qbSpecData,autoClear=False)
#frequency01=qbSpec(nLoops=5,fcenter=freqCenter_qb,fspan=0.5,fstep=0.0004,power=p+10,fReadout=frequencyRes,attenRes=attenRes,data=qbSpecData,autoClear=False)
##
freqCenter_qb=6.262146
powerQubit=-10
##qubit spectroscopy in microwave frequency with population of the resonator
setAWG(sampTime_ns=2,qb_pulse_ns=12000,res_pulse_ns=1500,resDriveLength_ns=800,resDriveDelay_ns=20,driveReadSep_ns=20,triggerInterval=51000)
qbSpecData=Datacube('spectroscopy01 %f dBm, vcoil=%f'%(powerQubit,coil.current()))
frequency01=qbSpec(nLoops=10,fcenter=freqCenter_qb,fspan=0.06,fstep=0.0005,powerQubit=powerQubit,fReadout=frequencyRes,attenRes=attenRes,data=qbSpecData,autoClear=False)


## Rabi oscillation
#frequency01=correct_freq
frequency01=6.651481
powerQubit=-0
rabiData=Datacube('rabi %f dBm, frequency=%f'%(powerQubit,frequency01))
piRabi= rabiMeas(nLoops=10,fQubit=frequency01,powerQubit=powerQubit,fRes=frequencyRes,attenRes=attenRes,start=0,stop=400,step=2,data=rabiData,autoClear=False)

## Res Vs Power g
piRabi=20
frequency01=6.367018
powerQubit=-20
ResVsPowData=Datacube('ResVsPow g dBm, coil=%f'%coil.current())
ResVsPow(nLoops=5,fcenter=7.09,fspan=0.04,fstep=0.0003,attenStart=8,attenStop=1.0,attenStep=-0.2,qbState='g',qbFreq=6,qbPower=-10,piPulse=30,data=ResVsPowData,autoPlot=True,autoClear=False,dataSave=True)

## Res Vs Power e
piRabi=20
frequency01=6.367018
powerQubit=-20
ResVsPowData=Datacube('ResVsPow g dBm, coil=%f'%coil.current())
ResVsPow(nLoops=5,fcenter=7.09,fspan=0.04,fstep=0.0005,attenStart=4,attenStop=0,attenStep=-0.1,qbState='e',qbFreq=6,qbPower=-10,piPulse=30,data='',autoPlot=True,autoClear=False,dataSave=True)