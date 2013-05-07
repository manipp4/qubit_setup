import sys
import getopt
import numpy

from pyview.lib.classes import *
from pyview.helpers.instrumentsmanager import Manager
from numpy import *
import scipy
register=Manager().getInstrument('register')
if 'lib.datacube' in sys.modules:
  reload(sys.modules['lib.datacube'])
  
from pyview.lib.classes import *
from pyview.lib.datacube import Datacube



class Instr(Instrument):

  def saveState(self,name):
    d=dict()
    d['frequencies']=self._frequencies
    return d

  def restoreState(self,state):
    self._frequencies=state['frequencies']

  def addFrequency(self, f,name, useCorrection=False,bit=0):
    """
    Add a new frequency to the analyser
    """
    self._frequencies[name]=[abs(f),True,bit]
    return True
        
  def startAnalyseFrequency(self,name):
    self._frequencies[name][1]=True
        
  def stopAnalyseFrequency(self,name):
    self._frequencies[name][1]=False

  def measureAll(self):
    return self._acqiris.frequenciesAnalyse(frequencies=self._frequencies.values)



  def analyse(self,nLoops=1,fast=False):
    """
    Acquire and analyse the frequencies previously sent and returns (components and probabilities)
    """
    
    maxBit=0
    for v in self._frequencies.values():
    	if v[2]>maxBit and v[1]:
    		maxBit=v[2]
    return self._acqiris.frequenciesAnalyse(frequencies=self._frequencies.values(),nLoops=nLoops,maxBit=maxBit,fast=fast)
    

  def measureBifurcationProbabilities(self):
    """
    Acquire, analyse the frequencies, convert it in clicks, and calculate averages values
    """
    (av,co,fr)=self.analyse()
    r=self._acqiris.multiplexedBifurcationMapAdd(co,fr)
    p=self._acqiris.convertToProbabilities(r)
   
  def clear(self):
    """
    Clear the list of frequencies to be analysed and the calibration paramaters associated
    """
    self._Ilist=[]  
    self._Qlist=[]
    self._philist=[]
    self._frequencies=dict()

  def calibrateAmplitudeAndOffset(self,f):
    """
    Only used when this pulse Analyser has to be used as real analyser, not when using it to see bifurcation
    """
    rowData=Datacube()
    for phi in arange(0,2*math.pi,math.pi/30):
      print "calibration : phi = %f deg" % (phi/math.pi*180)    
      self._pulse_generator.clearPulse()
      self.clear()
      self._pulse_generator.generatePulse(duration=20000, frequency=f, amplitude=0.6, DelayFromZero=0,useCalibration=True, phase=phi)
      self.addFrequency(f=f,useCorrection=False)    	
      self._pulse_generator.sendPulse()
      time.sleep(0.5)
      (av, co, fr)= self.analyse()
      rowData.set(I=av[0,0], Q=av[1,0],phi=phi)          	
      rowData.commit()
    #I0=2/ptp(rowData['I'])
    #Q0=2/ptp(rowData['Q'])
    (I,Q,phi,dphi)=scipy.optimize.fmin_powell(lambda (I,Q,phi0,dphi): sum((I*rowData['I'] - sin(rowData['phi']+phi0+dphi))**2)+sum((Q*rowData['Q'] - cos(rowData['phi']+phi0))**2),(1,1,0,0))
    print (I,Q,phi,dphi)
    f_c=self._MWSource.frequency()
    df=f-f_c
    index=self._calibration.search(f_sb=df,f_c=f_c)
    if index!=None:
      self._calibration.removeRow(index)
    self._calibration.set(I=I,Q=Q,phi=dphi,f_c=f_c,f_sb=df)
    self._calibration.commit()
    self._calibration.savetxt()
    register['%s Cal'% self._name]=self._calibration.filename()
    return rowData
      
  def parameters(self):    
    """
    Returns intrument parameters
    """
    return self._params
  
  def initCal(self):
    """
    Re-init the calibration when using this instrument as real analyser
    """
    self._calibration=Datacube()
    self._calibration.setName('analyser IQ mixer Calibration')
    self._calibration.savetxt()
    register['%s Cal'% self._name]=self._name.filename()
    
    
  def initialize(self, name, acqiris, MWSource,pulse_generator):
    """
    Initialize the instrument
    """
    instrumentManager=Manager()
    self._name=name
    self._acqiris=instrumentManager.getInstrument(acqiris)
    self._MWSource=instrumentManager.getInstrument(MWSource)
    self._pulse_generator=instrumentManager.getInstrument(pulse_generator)
    self._params=dict()
    self._params["acqiris"]=acqiris
    self._params["MWSource"]=MWSource
    self._frequencies=dict()
    try:
      self._calibration=Datacube()
      self._calibration.setName('analyser IQ mixer Calibration')
      self._calibration.loadtxt(register.parameters()['%s Cal'% self._name])
    except:
      pass
    self._Ilist=[]
    self._Qlist=[]
    self._philist=[]