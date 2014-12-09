import sys
import time
import numpy
import scipy
import scipy.optimize
import scipy.interpolate
from pyview.lib.datacube import *

##

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
	deltas=(roll(x,-1)-x)[:-1]			# calculate the x separations, this line was: deltas=(np.roll(x,-1)-x)[:-1]
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