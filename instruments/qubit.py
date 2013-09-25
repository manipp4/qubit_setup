import sys
import getopt
import re
import struct
import math
import numpy
import scipy

from pyview.lib.classes import *
from pyview.helpers.instrumentsmanager import Manager
from pyview.lib.smartloop import *
from pyview.lib.datacube import Datacube

#This is a virtual instrument representing a Quantum Bit.
#This class provides convenience functions for setting the Qubit parameters and for
#making measurements of the Qubit state.
class Instr(Instrument):

  def parameters(self):
    return self._params

  def saveState(self,name):
    params = copy.deepcopy(self._params)
    return params

  def restoreState(self,state):
    self._params = state

  def initialize(self,name, jba, pulseGenerator):
    manager=Manager()
    if not hasattr(self,'_params'):
      print("reseting self._params dictionnary")
      self._params = dict()
      self._params['jba']=jba
      self._jba=manager.getInstrument(jba)
      self._params['pulseGenerator']=pulseGenerator
      self._pulseGenerator=manager.getInstrument(pulseGenerator)

  def measureT1(self,delays,data=None,t1Parameters=None, dataParameters=None):
    """
    Measure a T1, will use what is in dictionnary if power/frequency/useCalibration/nLoops are not set
    Fit and save the period in the Qubit dictionnary under T1
    Return data and T1
    """
    if dataParameters==None:
      dataParameters=dict()
      dataParameters['addToDataManager']=True
      dataParameters['save']=True
    print t1Parameters
    if t1Parameters==None:
      if self._params.has_key('t1Parameters'):
        t1Parameters=self._params['t1Parameters']
      else: raise Exception("Unable to find rabi parameters... Exiting... ")

    useCalibration=t1Parameters['useCalibration']
    frequency=t1Parameters['frequency']
    if frequency=="f01":frequency=self.frequency01()
    print frequency 

    power=t1Parameters['power']
    nLoops=t1Parameters['nLoops']
    duration=t1Parameters['duration']
    if duration=="rabi":duration=self._params['piRabiTime']


    if t1Parameters.has_key('remember'):
      if t1Parameters['remember']: self._params['t1Parameters']=t1Parameters

    if self._params.has_key('offsetDelay'):
      offsetDelay=self._params['offsetDelay']
    else: offsetDelay=20

    if data==None:
      data=Datacube("T1 Measurement")
      if dataParameters['addToDataManager']:data.toDataManager()

    if power !="stay":self._pulseGenerator._MWSource.setPower(power)
   
    if power !="stay":self._pulseGenerator._MWSource.setPower(power)
  
    for delay in delays:

      self._pulseGenerator.clearPulse()
      self._pulseGenerator.generatePulse(duration=duration, frequency=frequency, DelayFromZero=10000-delay-duration-offsetDelay,useCalibration=False)
      self._pulseGenerator.sendPulse()

      result=self._jba.measure(nLoops=nLoops,fast=True)[0]
      data.set(**result)
      data.set(delay=delay)
      data.commit()

    [y0,dy,T1],yfit=fitT1(data['delay'],data['b0'])
    data.createColumn("b0fit",yfit)
    
    self._params['T1']=T1


    return data,T1

  def measureRabi(self,durations,data=None,rabiParameters=None, dataParameters=None):
    """
    Measure a rabi, will use what is in dictionnary if power/frequency/useCalibration/nLoops are not set
    Fit and save the period in the Qubit dictionnary under piRabiTime
    Return the datacube and rabiPeriod
    """

    if dataParameters==None:
      dataParameters=dict()
      dataParameters['addToDataManager']=True
      dataParameters['save']=True

    if rabiParameters==None:
      if self._params.has_key('rabiParameters'):
        rabiParameters=self._params['rabiParameters']
      else: raise Exception("Unable to find rabi parameters... Exiting... ")

    useCalibration=rabiParameters['useCalibration']
    frequency=rabiParameters['frequency']
    if frequency=="f01":frequency=self.frequency01()

    power=rabiParameters['power']
    nLoops=rabiParameters['nLoops']

    if rabiParameters.has_key('remember'):
      if rabiParameters['remember']: self._params['rabiParameters']=rabiParameters

    if self._params.has_key('offsetDelay'):
      offsetDelay=self._params['offsetDelay']
    else: offsetDelay=20

    if data==None:
      data=Datacube("Rabi Measurement")
      if dataParameters['addToDataManager']:data.toDataManager()


    if power !="stay":self._pulseGenerator._MWSource.setPower(power)
  
    for duration in durations:
      self._pulseGenerator.clearPulse()
      self._pulseGenerator.generatePulse(duration=duration, frequency=frequency, DelayFromZero=10000-duration-offsetDelay,useCalibration=False)
      self._pulseGenerator.sendPulse()

      result=self._jba.measure(nLoops=nLoops,fast=True)[0]
      data.set(**result)
      data.set(duration=duration)
      data.commit() 

    #Fit
    period= estimatePeriod(data['duration'],data['b0'])
    [y0,dy,piRabi,t10],yfit=fitRabi(data['duration'],data['b0'],period=period)
    data.createColumn("b0fit",yfit)

    self._params['piRabiTime']=piRabi

    if dataParameters['save']:data.savetxt()

    return data,piRabi

  def measureSpectroscopy(self,frequencies, data=None, spectroscopyParameters=None,dataParameters=None):
    """
    Measure a spectroscopy
    Fit
    Return the datacube and centerFrequency
    """

    if spectroscopyParameters==None:
      if self._params.has_key(spectroscopyParameters):
        spectroscopyParameters=self._params['spectroscopyParameters']
      else:
        raise Exception("No spectroscopy parameters found... Exiting...")

    if dataParameters==None:
      dataParameters=dict()
      dataParameters['addToDataManager']=True
      dataParameters['save']=True

    if spectroscopyParameters.has_key('remember'):self._params['spectroscopyParameters']=spectroscopyParameters

    useCalibration=spectroscopyParameters['useCalibration']
    power=spectroscopyParameters['power']
    nLoops=spectroscopyParameters['nLoops']
    duration=spectroscopyParameters['duration']


    if data==None:
      data=Datacube("Spectroscopy measurement")
      if dataParameters['addToDataManager']:data.toDataManager()


    if self._params.has_key('offsetDelay'):
      offsetDelay=self._params['offsetDelay']
    else: offsetDelay=20

    if power!="stay":self._pulseGenerator._MWSource.setPower(power)

    self._pulseGenerator.clearPulse()
    self._pulseGenerator.generatePulse(duration=duration, frequency=5, DelayFromZero=10000-duration-offsetDelay,useCalibration=False)
    self._pulseGenerator.sendPulse()
    
    for frequency in frequencies:
      self._pulseGenerator._MWSource.setFrequency(frequency)
      time.sleep(0.2)
      data.set(frequency=frequency)
      data.set(**self._jba.measure(nLoops=nLoops,fast=True)[0])
      data.commit()

    [dy,f0,df,y0],yfit=fitLorentzian(data['frequency'],data['b0'])
    data.createColumn("b0fit",yfit)

    if dataParameters['save']:data.savetxt()

    return data, f0

  def setFrequency01(self,f01,accuracy=7):
    """
    Set the input frequency under self._params['f01'] with given accuracy (round)
    """
    self._params['frequency01']=round(f01,6)

  def frequency01(self):
    return self._params['frequency01']

def fitLorentzian(x,y,orientation=-1):
  """
  fit a lorentzian peak with x and y as data
  formula : p[3]+orientation*p[0]/(1.0+pow((x-p[1])/p[2],2.0))
  norm : 2
  return parameters and fit
  """

  def bounds(p,x,y):
    if abs(p[0])>1 or abs(p[3])>1:  return 1e12
    if p[1]>max(x) or p[1]<min(x):     return 1e12
    if abs(p[2])>abs(max(x)-min(x)):   return 1e12
    return 0


  (xmin,ymin)=sorted(zip(x,y),key = lambda t: t[1])[(orientation-1)/2]
  ymean=mean(y)

  fitfunc = lambda p, x: p[3]+orientation*p[0]/(1.0+pow((x-p[1])/p[2],2.0))
  errfunc = lambda p, x, y,ff: pow(numpy.linalg.norm(ff(p,x)-y,2),2.0)+bounds(p,x,y)

  pi=[ymin-ymean,xmin,0.001,ymean]
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
  return x[-1]/argmax(fft)/2     

def fitRabi(x,y,period=20):
  """
  fit a rabi with x and y as data and period as initial value for the period
  formula : p[0]+p[1]*cos(math.pi*x/p[2])*exp(-x/p[3])
  return parameters and fit
  """
  # initial guessing
  pi=[0.5,0.1,period,200]
  print "initial guess :"
  print pi 

  fitfunc = lambda p, x: p[0]+p[1]*cos(math.pi*x/p[2])*exp(-x/p[3])
  errfunc = lambda p, x, y,ff: pow(numpy.linalg.norm(ff(p,x)-y,2),2.0)

  p1s = scipy.optimize.fmin(errfunc, pi,args=(x,y,fitfunc))
  print "fit result :"
  print p1s
  yfit=[fitfunc(p1s,xv) for xv in x]

  return p1s,yfit

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

