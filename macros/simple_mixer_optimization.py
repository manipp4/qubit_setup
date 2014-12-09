#This class optimizes the AWG offset in order to increase the contrast
import scipy
import sys
from numpy import *
import traceback
import scipy.optimize

if 'lib.datacube' in sys.modules:
  reload(sys.modules['lib.datacube'])

from macros.optimization import Minimizer
reload(sys.modules['macros.optimization'])
from macros.optimization import Minimizer
  
from pyview.lib.classes import *
from pyview.lib.datacube import Datacube

import sys
import time

print "simple_level_optimization reloaded"

class OffsetOptimization(Reloadable):

  """
  Find offset of a single mixer
  """  
  def __init__(self,mwg,fsp,awg,channels = [1,2]):
    Reloadable.__init__(self)
    self._mwg = mwg
    self._fsp = fsp
    self._awg = awg
    self._awgChannel = channels
    self.initCalibrationData()
  
  def initCalibrationData(self):
    """
    Initialize the datacubes that contain the IQ calibration data.
    """
    self._offsetCalibrationData = Datacube()
    self._offsetCalibrationData.setName("mixer calibration - Offset Calibration Data")
    self._offsetCalibrationData.savetxt()
    return self._offsetCalibrationData.filename()
    
  
  def offsetCalibrationData(self):
    """
    Return the datacube containing the offset calibration data.
    """
    return self._offsetCalibrationData
  
  def setOffsetCalibrationData(self,data):
    self._offsetCalibrationData = data
     
  def teardown(self):
  	"""
  	Restore the original configuration.
  	"""
  	self._fsp.loadConfig("IQCalibration")
  	self._awg.loadSetup("iq_calibration.awg")
  	self._mwg.restoreState(self._mwgState)
  
  def setup(self,averaging = 10,reference = -50):
    """
    Configure the AWG and the FSP for the IQ mixer calibration.
    """
    self._fsp.storeConfig("IQCalibration")
    self._awg.saveSetup("iq_calibration.awg")
    self._mwgState = self._mwg.saveState("iq calibration")
    self._fsp.write("SENSE1:FREQUENCY:SPAN 0 MHz")
    self.period = 20000#int(1.0/self._awg.repetitionRate()*1e9)
    self._fsp.write("SWE:TIME 20 ms")
    self._rbw = 10000
    self._fsp.write("SENSE1:BAND:RES %f Hz" % self._rbw)
    self._fsp.write("SENSE1:BAND:VIDEO AUTO")
    self._fsp.write("TRIG:SOURCE EXT")
    self._fsp.write("TRIG:HOLDOFF 0.02 s")
    self._fsp.write("TRIG:LEVEL 0.5 V")
    self._fsp.write("TRIG:SLOP POS")
    self._fsp.write("SENSE1:AVERAGE:COUNT %d" % averaging)
    self._fsp.write("SENSE1:AVERAGE:STAT1 ON")
    self._fsp.write("DISP:TRACE1:Y:RLEVEL %f" % reference)
    self.setupWaveforms()
  	
  def setupWaveforms(self):
    self._awg.write("AWGC:RMOD CONT")
    self.period=20000
    waveformOffset = zeros((self.period))
    self._markers = zeros((self.period),dtype = uint8)
    self._markers[1:len(self._markers)/2] = 255
    self._awg.createRawWaveform("Offset_Calibration",(waveformOffset+1.0)/2.0*((1<<14)-1),self._markers,"INT")
    self._awg.setWaveform(int(self._awgChannel),"Offset_Calibration")


  def calibrateOffset(self):
    """
    Calibrate the IQ mixer DC offset.
    """
    self.initCalibrationData()
    frequency=round(self._mwg.frequency(),6)
    print frequency
    try:
      self.setup()
      params = dict()
      params["power"] = self._mwg.power()
      params["channels"] = self._awgChannel
      params["mwg"] = self._mwg.name()
      params["awg"] = self._awg.name()
      params["fsp"] = self._fsp.name()
      self.offsetCalibrationData().setParameters(params)
      self._mwg.turnOn()
      #self._awg.turnOn()
      self._awg.startAllChannels()
      self._mwg.turnOn()
      self._fsp.write("SENSE1:FREQUENCY:CENTER %f GHZ" % frequency)
#      (voltage,minimum) = self.optimizeIQMixerPowell()
      (voltage,minimum) = self.optimizeMixerVS()
      minimum = self.measurePower(voltage)
      print "Optimum value of %g dBm at offset %g V" % (minimum,voltage[0])
      self._offsetCalibrationData.set(i = voltage[0], minimum = minimum,frequency=frequency)
      self._offsetCalibrationData.commit()
      self._offsetCalibrationData.savetxt()
    finally:
      self.teardown()

  def optimizeMixerVS(self):
    self.d=Datacube()
    self.d.toDataManager()
    self.d.plotInDataManager("offset","minimum",clear=True)
    minimizer=Minimizer(lambda x: self.measurePower(x),[0.],[[-0.1,0.1]],xtol=0.000001,maxfun=50,maxiter=5)
    minimizer.minimize()
    return minimizer.result()

  def optimizeIQMixerPowell(self):
    """
    Use Powell's biconjugate gradient method to minimize the power leak in the mixer.
    """
    result = scipy.optimize.fmin_powell(lambda x: self.measurePower(x),[0.],full_output = 1,xtol = 0.001,ftol = 1e-2,maxiter =50,maxfun =50, disp=True, retall=True)
    return (result,result)

  def measurePower(self,low):
    """
    Measure the leaking power of the mixer at a given point.
    Used by optimizeIQMixerPowell and optimizeMixerVS.
    """
    if math.fabs(low[0]) > 2.0:
      return 100.0
    self._awg.setOffset(self._awgChannel,low[0])
    minimum = self.measureAveragePower()
    print "Measuring power at %g : %g" % (low[0],minimum)
    self.d.set(minimum=minimum, offset=low[0])
    self.d.commit()
    linpower = math.pow(10.0,minimum/10.0)/10.0
    return minimum 

  def calibrationParameters(self):    
    return self.offsetCalibrationData()['i'][0]    
    
  def measureAveragePower(self):
    trace = self._fsp.getSingleTrace()
    if trace == None:
      print "returning trace error"
      return 0
    minimum =  mean(trace[1])
    return minimum
  


