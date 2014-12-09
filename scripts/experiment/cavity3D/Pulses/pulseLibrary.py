################################################
#### pulse library-> design arbitraty pulses ###
################################################
import sys
import time
import math
from numpy import *
import scipy
import scipy.optimize
print "Scipy version %s" %scipy.version.version
from matplotlib.pyplot import *
######################
#### pulse types ####
#####################
## outputs an array of 20000 values. 
def singleSquarePulse(start,stop, height=1):
	start=int(start)
	stop=int(stop)
	if start<0:
		print 'start out of range-set start to 0'
		start=0
	if stop>20000:
		print 'stop out of range-set start to 20000'
		stop=20000  
	values=zeros(20000)
	for i in range(start,stop):
		values[i]=float(height)
	return values
#
def singleGaussianPulse(center,sigma,cutOff,height=1):
	start=int(round(center-cutOff/2))
	stop=int(round(center+cutOff/2))
	if start<0:
		print 'start out of range-set start to 0'
		start=0
	if stop>20000:
		print 'stop out of range-set start to 20000'
		stop=20000  
	values=zeros(20000)	
	for i in range(start,stop,1):
		values[i]=height*exp(-(center-float(i))**2/(2*sigma**2))
	return values
#
def sinPulse(frequency,phase=0,height=1):
	values=zeros(20000)	
	for i in range(20000):
		values[i]=height*sin(2*pi*(frequency*i)+pi/180*phase)
	return values
#
def counterTransientPulse(t,height=1):
	values=zeros(20000)
	for i in range(20000):
		values[i]=height*(1+exp(float(-i)/float(t)))
	return values	
#	
def singleGaussianSquarePulse(startSq,stopSq,sigma,cutOff,height=1):
	start=int(round(startSq-cutOff/2))
	stop=int(round(stopSq+cutOff/2))
	if start<0:
		print 'start out of range->start set to 0'
		start=0
	if stop>20000:
		print 'stop out of range->stop set to 20000'
		stop=20000  
	values=np.zeros(20000)	
	for i in range(start,stop,1):
		if i<=startSq:
			values[i]=height*np.exp(-(startSq-float(i))**2/(2*sigma**2))
		elif startSq<i<stopSq:
			values[i]=float(height)
		else:
			values[i]=height*np.exp(-(stopSq-float(i))**2/(2*sigma**2))

	return values
###########################
#### utility functions ####
###########################
def applyCos(val,f,ph):
	values=[val[i]*cos(i*f+ph)for i in range(len(val))]
	return values
def pulsePlot(values):
	x=range(20000)
	y=values
	figure()
	plot(x,y)
	show()
#
def addPulses(*pulses):
	pulseMatrix=np.transpose(pulses)
	totalPulse=[sum(i) for i in pulseMatrix]
	return totalPulse
#
def multiplyTwoPulses(pulse1,pulse2):
	totalPulse=[i[0]*i[1] for i in zip(pulse1,pulse2)]
	return totalPulse
##
#a=counterTransientPulse(625)
#b=singleGaussianPulse(7000,1000,5000,1)
#c=multiplyTwoPulses(a,b)
#pulsePlot(a)
#pulsePlot(c)
##
