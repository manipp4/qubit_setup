import numpy as np

__DEBUG__=False

def arb(numberOfPoints, samplingtime, shape, delay=0):
	mshape=np.zeros(numberOfPoints)
	mshape[delay:delay+len(shape)]=shape[:]
	return mshape


def square(numberOfPoints,samplingTime,start,stop,amplitude=1,offset=0):
	start,stop=convertInPoints(samplingTime,start,stop)
	shape=np.zeros(numberOfPoints)
	shape[:]=offset
	shape[start:stop]+=amplitude
	return shape

def gaussianPulseHeight(numberOfPoints,samplingTime,center,sigma,cutOff=2,height=1):
	"""
	numberOfPoints,samplingTime: pulse generator parameters
	center : pulse center in center
	sigma : pulse sigma in ns
	cutOff : in sigma unit
	height : height
	"""	
	center,sigma=convertInPoints(samplingTime,center,sigma)

	start=round(round(center-sigma*cutOff))
	stop=round(round(center+sigma*cutOff))


	if start<0:
		print 'Warning : start out of range-set start to 0'
		start=0
	if stop>numberOfPoints:
		print 'Warning : stop out of range-set start to ', numberOfPoints
		stop=numberOfPoints  

	values=np.zeros(numberOfPoints)	
	values[start:stop]=height*np.exp(-(center-np.arange(start,stop))**2/(2*sigma**2))
	return values

def gaussianPulseArea(numberOfPoints,samplingTime,center,sigma,cutOff=2,area=1):
	height=area/(sigma*np.sqrt(2*np.pi))
	return gaussianPulseHeight(numberOfPoints=numberOfPoints,samplingTime=samplingTime,center=center,sigma=sigma,cutOff=cutOff,height=height)


def gaussianSquarePulseHeight(numberOfPoints,samplingTime,center,plateau,sigma,cutOff=2,height=1):

	center,plateau,sigma=convertInPoints(samplingTime,center,plateau,sigma)
	
	plateau=float(plateau) # plateau/2
	plateauO2=round(plateau/2)
	plateauC=np.ceil(plateau)
	start=np.floor(center-plateau/2-sigma*cutOff)
	stop=np.ceil(center+plateau/2+sigma*cutOff)
	if start<0:
		print 'Warning : start out of range-set start to 0'
		start=0
	if stop>numberOfPoints:
		print 'Warning : stop out of range-set stop to ', numberOfPoints
		stop=numberOfPoints  

	values=np.zeros(numberOfPoints)	

	values[start:center-plateauO2]=[height*np.exp(-((center-plateau/2-x)/sigma)**2/2) for x in np.arange(int(start),int(center-plateauO2))]#[height*np.exp(-((center-plateau/2-x)/sigma)**2/2) for x in np.arange(start,center-plateauO2)]
	values[center-plateauO2:center+plateauC-plateauO2]=height
	values[center+plateauC-plateauO2:stop]=[height*np.exp(-((center+plateau/2-x)/sigma)**2/2) for x in np.arange(int(center+plateauC-plateauO2),int(stop))]

	return values

def gaussianSquarePulseArea(numberOfPoints,samplingTime,center,plateau,sigma,cutOff=2,area=1):
	height=area/(sigma*np.sqrt(2*np.pi)+plateau)
	return gaussianSquarePulseHeight(numberOfPoints=numberOfPoints,samplingTime=samplingTime,center=center,plateau=plateau,sigma=sigma,cutOff=cutOff,height=height)

def gaussianSlopePulse(numberOfPoints,samplingTime, sigma, cutOff=2, end=None, center=None, area=1, maxHeight=1):
	if __DEBUG__:print sigma, cutOff,end,center,area,maxHeight
	height=area/(sigma*np.sqrt(2*np.pi))
	if height<=maxHeight:
		if center==None:
			center=end-cutOff*sigma
		if __DEBUG__:print sigma, cutOff,end,center,area,maxHeight
		return gaussianPulseArea(numberOfPoints=numberOfPoints,samplingTime=samplingTime,center=center,sigma=sigma,cutOff=cutOff,area=area)
	else:

		gaussianArea=maxHeight*sigma*np.sqrt(2*np.pi)
		length=(area-gaussianArea)/maxHeight

		if center==None:
			center=end-sigma*cutOff-length/2

		return gaussianSquarePulseHeight(numberOfPoints=numberOfPoints,samplingTime=samplingTime,center=center,plateau=length,sigma=sigma,cutOff=cutOff,height=maxHeight)

def gaussianSlopePulseDerivative(numberOfPoints,samplingTime, sigma, cutOff=2, end=None, center=None, area=1, maxHeight=1,coefficient=1.):
	if __DEBUG__:print sigma, cutOff,end,center,area,maxHeight
	height=area/(sigma*np.sqrt(2*np.pi))
	if height<=maxHeight:
		if center==None:
			center=end-cutOff*sigma
		if __DEBUG__:print sigma, cutOff,end,center,area,maxHeight
		return coefficient*gaussianPulseAreaDerivative(numberOfPoints=numberOfPoints,samplingTime=samplingTime,center=center,sigma=sigma,cutOff=cutOff,area=area)
	else:

		gaussianArea=maxHeight*sigma*np.sqrt(2*np.pi)
		length=(area-gaussianArea)/maxHeight

		if center==None:
			center=end-sigma*cutOff-length/2

		return coefficient*gaussianSquarePulseHeightDerivative(numberOfPoints=numberOfPoints,samplingTime=samplingTime,center=center,plateau=length,sigma=sigma,cutOff=cutOff,height=maxHeight)


#		return gaussianSquarePulseArea(numberOfPoints=numberOfPoints,samplingTime=samplingTime,center=center,plateau=plateau,sigma=sigma,cutOff=cutOff,area=area)

def gaussianPulseAreaDerivative(numberOfPoints,samplingTime,center,sigma,cutOff=2,area=1):
	height=area/(sigma*np.sqrt(2*np.pi))
	return gaussianSquarePulseHeightDerivative(numberOfPoints=numberOfPoints,samplingTime=samplingTime,plateau=0,center=center,sigma=sigma,cutOff=cutOff,height=height)

def gaussianSquarePulseAreaDerivative(numberOfPoints,samplingTime,center,plateau,sigma,cutOff=2,area=1):
	height=area/(sigma*np.sqrt(2*np.pi)+plateau)
	return gaussianSquarePulseHeight(numberOfPoints=numberOfPoints,samplingTime=samplingTime,center=center,plateau=plateau,sigma=sigma,cutOff=cutOff,height=height)

def gaussianSquarePulseHeightDerivative(numberOfPoints,samplingTime,center,plateau,sigma,cutOff=2,height=1):

	center,plateau,sigma=convertInPoints(samplingTime,center,plateau,sigma)
	
	plateau=float(plateau) # plateau/2
	plateauO2=round(plateau/2)
	plateauC=np.ceil(plateau)
	start=np.floor(center-plateau/2-sigma*cutOff)
	stop=np.ceil(center+plateau/2+sigma*cutOff)
	if start<0:
		print 'Warning : start out of range-set start to 0'
		start=0
	if stop>numberOfPoints:
		print 'Warning : stop out of range-set stop to ', numberOfPoints
		stop=numberOfPoints  

	values=np.zeros(numberOfPoints)	

	values[start:center-plateauO2]=[-(center-plateau/2-x)/sigma**2*height*np.exp(-((center-plateau/2-x)/sigma)**2/2) for x in np.arange(int(start),int(center-plateauO2))]#[height*np.exp(-((center-plateau/2-x)/sigma)**2/2) for x in np.arange(start,center-plateauO2)]


	values[center+plateauC-plateauO2:stop]=[-(center+plateau/2-x)/sigma**2*height*np.exp(-((center+plateau/2-x)/sigma)**2/2) for x in np.arange(int(center+plateauC-plateauO2),int(stop))]

	return values*10

def convertInPoints(samplingTime,*args):
	return [float(float(x)/samplingTime) for x in args]












