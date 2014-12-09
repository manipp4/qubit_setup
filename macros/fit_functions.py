import sys
import getopt
import re
import struct
import math
import numpy
import scipy
from pyview.lib.classes import *
from numpy import * 


def fitLorentzian(x,y,orientation=None,bounds=None):
  """
  fit a lorentzian peak with x and y as data
  formula : p[3]+orientation*p[0]/(1.0+pow((x-p[1])/p[2],2.0))
  orientation=1:up, -1:down
  norm : 2
  return parameters and fit
  """

  if bounds==None:
  	def bounds(p,x,y):
	   if abs(p[0])>1 or abs(p[3])>1:  return 1e12
	   if p[1]>max(x) or p[1]<min(x):     return 1e12
	   if abs(p[2])>abs(max(x)-min(x)):   return 1e12
	   return 0

  if orientation==None:
  	if abs(max(y)-mean(y))>abs(min(y)-mean(y)):
  		orientation=1
  	else: orientation=-1

  reverse=orientation==1
  (xex,yex)=sorted(zip(x,y),key = lambda t: t[1], reverse=reverse)[0]
  ymean=mean(y)

  fitfunc = lambda p, x: p[3]+orientation*p[0]/(1.0+pow((x-p[1])/p[2],2.0))
  errfunc = lambda p, x, y,ff: pow(numpy.linalg.norm(ff(p,x)-y,2),2.0)+bounds(p,x,y)

  pi=[(yex-ymean)*orientation,xex,0.001,ymean]
  print "initial guess :"
  print pi 
  
  p1s = scipy.optimize.fmin(errfunc, pi,args=(x,y,fitfunc))
  print "fit result :"
  print p1s
  yfit=[fitfunc(p1s,xv) for xv in x]

  return p1s,yfit
  


def estimatePeriod(x,y):
  """
  Estimate the period of a signal (approximative), do NOT use this result except for a 'real' fit
  return the period
  """
  fft=numpy.fft.rfft(y)
  fft[0]=0
  return x[-1]/argmax(abs(fft))/2     

def fitRabi(x,y,period=None,T1=1000):
  """
  fit a rabi with x and y as data and period as initial value for the period
  formula : p[0]+p[1]*cos(math.pi*x/p[2])*exp(-x/p[3])
  return parameters and fit
  """
  # initial guessing
  if period==None:
  	period=estimatePeriod(x,y)
  pi=[mean(y),y[0]-mean(y),period,T1]
  print "initial guess :"
  print pi 

  fitfunc = lambda p, x: p[0]+p[1]*cos(math.pi*x/p[2])*exp(-x/p[3])
  errfunc = lambda p, x, y,ff: pow(numpy.linalg.norm(ff(p,x)-y,2),2.0)

  p1s = scipy.optimize.fmin(errfunc, pi,args=(x,y,fitfunc))
  print "fit result :"
  print p1s
  yfit=[fitfunc(p1s,xv) for xv in x]

  return pi,yfit

def fitT1(x,y):	
  """
  Fit a t1 in guessing all parameters
  formula : p[0]+p[1]*exp(-x/p[2])
  return parameters and fit
  """
  # initial guessing
  pi=[0.5,0.1,200]
  print "initial guess :"
  print pi 

  fitfunc = lambda p, x: p[0]+p[1]*exp(-x/p[2])
  errfunc = lambda p, x, y,ff: pow(numpy.linalg.norm(ff(p,x)-y,2),2.0)

  p1s = scipy.optimize.fmin(errfunc, pi,args=(x,y,fitfunc))
  print "fit result :"
  print p1s
  yfit=[fitfunc(p1s,xv) for xv in x]

  return p1s,yfit

