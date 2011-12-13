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

  def addFrequency(self, f,useCorrection=True):
    f_c=self._MWSource.frequency()
    df=f-f_c
    toReturn=True
    if useCorrection:
      if self._calibration.search(f_sb=df,f_c=f_c)==['']:
        print 'Point not calibrated, calibration in progress.... (NOOOOO !!)'
#         self.calibrateAmplitudeAndOffset(f=f)
        print 'calibration over'
        toReturn=False
      index=self._calibration.search(f_sb=df,f_c=f_c)
      I=self._calibration['I'][index]
      Q=self._calibration['Q'][index]
      phi=self._calibration['phi'][index]
    else:
      I=1
      Q=1
      phi=3
    self._frequencies=append(self._frequencies,abs(df))
    self._Ilist=append(self._Ilist,I)
    self._Qlist=append(self._Qlist,Q)
    self._philist=append(self._philist,phi)
    
    return toReturn
    
  def analyse(self):
    (wa,av,co,fr)=self._acqiris.frequenciesAnalysis(frequencies=self._frequencies, Ilist=self._Ilist, Qlist=self._Qlist, philist=self._philist)
    return (av, co, fr)
    
  def clear(self):
    self._Ilist=[]  
    self._Qlist=[]
    self._philist=[]
    self._frequencies=[]  

  def calibrateAmplitudeAndOffset(self,f):
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
    register['%s Cal'% self._params['realMixer']]=self._calibration.filename()
    return rowData
      
  def parameters(self):    
    return self._params
  
  def initCal(self):
    self._calibration=Datacube()
    self._calibration.setName('analyser IQ mixer Calibration')
    self._calibration.savetxt()
    register['%s Cal'% self._params['realMixer']]=self._calibration.filename()
    
    
  def initialize(self, name, acqiris, MWSource,pulse_generator,realMixer):
    instrumentManager=Manager()
    self._acqiris=instrumentManager.getInstrument(acqiris)
    self._MWSource=instrumentManager.getInstrument(MWSource)
    self._pulse_generator=instrumentManager.getInstrument(pulse_generator)
    self._params=dict()
    self._params["acqiris"]=acqiris
    self._params["MWSource"]=MWSource
    self._params["realMixer"]=realMixer
    self._frequencies=zeros(0)
    try:
      self._calibration=Datacube()
      self._calibration.setName('analyser IQ mixer Calibration')
      self._calibration.loadtxt(register.parameters()['%s Cal'% self._params['realMixer']])
    except:
      pass
    self._Ilist=[]
    self._Qlist=[]
    self._philist=[]