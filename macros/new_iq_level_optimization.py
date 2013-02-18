#This class optimizes the AWG offset in order to increase the contrast
import scipy
import sys
from numpy import *
import traceback
import scipy.optimize

if 'lib.datacube' in sys.modules:
  reload(sys.modules['lib.datacube'])
  
from pyview.lib.classes import *
from pyview.lib.datacube import Datacube

import sys
import time

print "iq_level_optimization reloaded"

class IqOptimization(Reloadable):
  
  """
  Optimizes the parameters of an IQ mixer.
  """
  
  def __init__(self,mwg,fsp,awg,channels = [1,2]):
    Reloadable.__init__(self)
    self._mwg = mwg
    self._fsp = fsp
    self._awg = awg
    self._awgChannels = channels
    self.initCalibrationData()
  
  def initCalibrationData(self):
    """
    Initialize the datacubes that contain the IQ calibration data.
    """
    self._offsetCalibrationData = Datacube()
    self._offsetCalibrationData.setName("IQ mixer calibration - Offset Calibration Data")
    self._offsetCalibrationData.savetxt()
#    self._powerCalibrationData = Datacube()
#    self._powerCalibrationData.setName("IQ mixer calibration - Power Calibration Data")
    self._sidebandCalibrationData = Datacube()
    self._sidebandCalibrationData.setName("IQ mixer calibration - Sideband Mixing Calibration Data")
    self._sidebandCalibrationData.savetxt()
    return (self._offsetCalibrationData.filename(),self._sidebandCalibrationData.filename())
    
  def sidebandCalibrationData(self):
    return self._sidebandCalibrationData
    
  def setSidebandCalibrationData(self,data):
    self._sidebandCalibrationData = data
  
  def offsetCalibrationData(self):
    """
    Return the datacube containing the offset calibration data.
    """
    return self._offsetCalibrationData
  
  def setOffsetCalibrationData(self,data):
    self._offsetCalibrationData = data
    self.updateOffsetCalibrationInterpolation()
    

  
  def powerCalibrationData(self):
    """
    Return the datacube containing the power calibration data.
    """
    return self._powerCalibrationData

  def setPowerCalibrationData(self,data):
    self._powerCalibrationData = data
  
  def teardown(self):
  	"""
  	Restore the original configuration.
  	"""
  	self._fsp.loadConfig("IQCalibration")
  	self._awg.loadSetup("iq_calibration.awg")
  	self._mwg.restoreState(self._mwgState)
  
  def setup(self,averaging = 10,reference = -30):
    """
    Configure the AWG and the FSP for the IQ mixer calibration.
    """
    print "reference : %f" % reference
    self._fsp.storeConfig("IQCalibration")
    self._awg.saveSetup("iq_calibration.awg")
    self._mwgState = self._mwg.saveState("iq calibration")
    self._fsp.write("SENSE1:FREQUENCY:SPAN 0 MHz")
    self.period = 20000#int(1.0/self._awg.repetitionRate()*1e9)
    self._fsp.write("SWE:TIME 20 ms")
    self._rbw = 100000
    self._fsp.write("SENSE1:BAND:RES %f Hz" % self._rbw)
    self._fsp.write("SENSE1:BAND:VIDEO AUTO")
    self._fsp.write("TRIG:SOURCE EXT")
    self._fsp.write("TRIG:HOLDOFF 0.002 s")
    self._fsp.write("TRIG:LEVEL 0.5 V")
    self._fsp.write("TRIG:SLOP POS")
    self._fsp.write("SENSE1:AVERAGE:COUNT %d" % averaging)
    self._fsp.write("SENSE1:AVERAGE:STAT1 ON")
    self._fsp.write("DISP:TRACE1:Y:RLEVEL %f" % reference)
    self.setupWaveforms()
  	
  def setupWaveforms(self):
    self._awg.write("AWGC:RMOD CONT")
 #   period = int(1.0/self._awg.repetitionRate()*1e9)
    self.period=20000
    waveformOffset = zeros((self.period))
    waveformActive = zeros((self.period))+1.0
    waveformPassive = zeros((self.period))-1.0
    self._markers = zeros((self.period),dtype = uint8)
    self._markers[1:len(self._markers)/2] = 255
    self._awg.createRawWaveform("IQ_Offset_Calibration",waveformOffset,self._markers,"REAL")
#    self._awg.createRawWaveform("IQ_Power_Calibration_active",waveformActive,self._markers,"REAL")
#    self._awg.createRawWaveform("IQ_Power_Calibration_passive",waveformPassive,self._markers,"REAL")

    length = self.period#int(1.0/self._awg.repetitionRate()*1e9)
    waveform = self.generateSidebandWaveform(f_sb = 0, c = 0,phi = 0,length = length)

    self._awg.createRawWaveform("IQ_Sideband_Calibration_I",waveform,self._markers,"REAL")
    self._awg.createRawWaveform("IQ_Sideband_Calibration_Q",waveform,self._markers,"REAL")
        
  def loadSidebandWaveforms(self):
    self._awg.setWaveform(1,"IQ_Sideband_Calibration_I")
    self._awg.setWaveform(2,"IQ_Sideband_Calibration_Q")
    self._awg.setWaveform(3,"IQ_Sideband_Calibration_I")
    self._awg.setWaveform(4,"IQ_Sideband_Calibration_Q")

  def calibrateIQOffset(self,frequencyRange = None,reference = 10):
    """
    Calibrate the IQ mixer DC offset.
    """
    if frequencyRange==None:
      frequencyRange=[self._mwg.frequency()]
    try:
      self.setup(reference=reference)
      params = dict()
      params["power"] = self._mwg.power()
      params["channels"] = self._awgChannels
      params["mwg"] = self._mwg.name()
      params["awg"] = self._awg.name()
      params["fsp"] = self._fsp.name()
      self.offsetCalibrationData().setParameters(params)
      self._mwg.turnOn()
      for channel in [1,2,3,4]:
        self._awg.setWaveform(channel,"IQ_Offset_Calibration")
      self._awg.runAWG()
      self._awg.startAllChannels()
      for frequency in frequencyRange:
        self._mwg.setFrequency(frequency)
        self._mwg.turnOn()
        self._fsp.write("SENSE1:FREQUENCY:CENTER %f GHZ" % frequency)
        (voltages,minimum) = self.optimizeIQMixerPowell()
        minimum = self.measurePower(voltages) 
        print "Optimum value of %g dBm at offset %g V, %g V" % (minimum,voltages[0],voltages[1])
        rows = self._offsetCalibrationData.search(frequency = frequency)
        if rows != []:
          self._offsetCalibrationData.removeRows(rows)
        self._offsetCalibrationData.set(frequency = frequency,lowI = voltages[0],lowQ = voltages[1],minimum = minimum)
        self._offsetCalibrationData.commit()
        self._offsetCalibrationData.sortBy("frequency")
        self._offsetCalibrationData.savetxt()
    except StopThread:
      pass
    except:
      raise
    finally:
      self.teardown()
      self.updateOffsetCalibrationInterpolation()
      self._awg.setOffset(self._awgChannels[0],self.iOffset(frequency))
      self._awg.setOffset(self._awgChannels[1],self.qOffset(frequency))
    return self._offsetCalibrationData.filename()

  def optimizeIQMixerPowell(self):
    """
    Use Powell's biconjugate gradient method to minimize the power leak in the IQ mixer.
    """
    result = scipy.optimize.fmin_powell(lambda x: self.measurePower(x),[0.,0.],full_output = 1,xtol = 0.001,ftol = 1e-2,maxiter =50,maxfun =50, disp=True, retall=True)
    return (result[0],result)

  def measurePower(self,lows):
    """
    Measure the leaking power of the IQ mixer at a given point.
    Used by optimizeIQMixerPowell.
    """
    for i in [0,1]:
      if math.fabs(lows[i]) > 0.1:
        return 100.0
      self._awg.setOffset(self._awgChannels[i],lows[i])
    minimum = self.measureAveragePower()
    print "Measuring power at %g,%g : %g" % (lows[0],lows[1],minimum)
    linpower = math.pow(10.0,minimum/10.0)/10.0
    return minimum 
    
  def updateOffsetCalibrationInterpolation(self):
    if len(self._offsetCalibrationData.column("frequency"))>1:
      frequencies = self._offsetCalibrationData.column("frequency")
      self._iOffsetInterpolation = scipy.interpolate.interp1d(frequencies,self._offsetCalibrationData.column("lowI"))        
      self._qOffsetInterpolation = scipy.interpolate.interp1d(frequencies,self._offsetCalibrationData.column("lowQ"))
    else:
      self._iOffsetInterpolation=lambda x:self._offsetCalibrationData.column("lowI")[0]
      self._qOffsetInterpolation=lambda x:self._offsetCalibrationData.column("lowQ")[0]


  def calibrateSidebandMixing(self,frequencyRange = None,sidebandRange = arange(-0.5,0.51,0.1),reference = 10):
    """
    Calibrate the IQ mixer sideband generation.
    """
    if frequencyRange==None:
      frequencyRange=[self._mwg.frequency()]
    try:
      self.setup(reference = reference)
      params = dict()
      params["power"] = self._mwg.power()
      params["channels"] = self._awgChannels
      params["mwg"] = self._mwg.name()
      params["awg"] = self._awg.name()
      params["fsp"] = self._fsp.name()
      self.sidebandCalibrationData().setParameters(params)
      self._mwg.turnOn()
      channels = self._awgChannels
      self.loadSidebandWaveforms()
      self._awg.runAWG()
      self._awg.startAllChannels()
      for f_c in frequencyRange:
        #We round the center frequency to an accuracy of 1 MHz
        f_c = round(f_c,3)
        self._mwg.setFrequency(f_c)
        self._awg.setAmplitude(channels[0],1.6)
        self._awg.setAmplitude(channels[1],1.6)
        self._awg.setOffset(channels[0],self.iOffset(f_c))
        self._awg.setOffset(channels[1],self.qOffset(f_c))
        data = Datacube("f_c = %g GHz" % f_c)
        rowsToDelete = []
        
   
        try:
          for i in range(0,len(self._sidebandCalibrationData.column("f_c"))):
           if abs(self._sidebandCalibrationData.column("f_c")[i]-f_c) < 0.1:
              rowsToDelete.append(i)
        except:
          pass
        self._sidebandCalibrationData.removeRows(rowsToDelete)
        self._sidebandCalibrationData.addChild(data, f_c=f_c)
        self._sidebandCalibrationData.set(f_c = f_c)
        self._sidebandCalibrationData.commit()
        for f_sb in sidebandRange: 
          print "f_c = %g GHz, f_sb = %g GHz" % (f_c,f_sb)
          self._fsp.write("SENSE1:FREQUENCY:CENTER %f GHZ" % (f_c-f_sb))
          #result = findMin(lambda x,*args: self.measureSidebandPower(x,*args),[0.02,0],args = [f_sb],full_output = 1,xtol = 0.00001,ftol = 1e-4,maxiter = 5,disp=True)
          
          result = scipy.optimize.fmin_powell(lambda x,*args: self.measureSidebandPower(x,*args),[0,0],args = [f_sb],full_output = 1,xtol = 0.001,ftol = 1e-2,maxiter =50,maxfun =50, disp=True, retall=True)
          #result = scipy.optimize.fmin_powell(lambda x,*args: self.measureSidebandPower2(x,*args),[0.7,0.2],args = [f_sb],full_output = 1,xtol = 0.001,ftol = 1e-2,maxiter =50,maxfun =50, disp=True, retall=True)
          
          params = result[0]
          value = result[1]
          print "f_c = %g GHz, f_sb = %g GHz, c = %g, phi = %g rad : value = %g" % (f_c,f_sb,params[0],params[1],self.measureAveragePower())
          self.loadSidebandCalibrationWaveform(f_sb = f_sb,c = params[0],phi = params[1])
          for i in [-3,-2,-1,0,1,2,3]:
            self._fsp.write("SENSE1:FREQUENCY:CENTER %f GHZ" % (f_c+f_sb*i))
            if i < 0:
              suppl = "m"
            else:
              suppl = ""
            data.set(**{"p_sb%s%d" % (suppl,abs(i)) : self.measureAveragePower()})
          data.set(f_c = f_c,f_sb = f_sb,c = params[0],phi = params[1])
          data.commit()
        self._sidebandCalibrationData.sortBy("f_c")
        self._sidebandCalibrationData.savetxt()
    except:
      raise
    finally:
      pass
      self.teardown()
    return self._sidebandCalibrationData.filename()

  def measureSidebandPower(self,x,f_sb):
    c = x[0]
    if abs(c)>0.4:
      return 100
    phi = fmod(x[1],math.pi*2)
    self.loadSidebandCalibrationWaveform(f_sb = f_sb,c = c,phi = phi)
    time.sleep(0.1)
    power = self.measureAveragePower()
    print "Sideband power at f_sb = %g GHz,c = %g, phi = %g : %g dBm" % (f_sb,c,phi,power) 
    return power
 
  def measureSidebandPower2(self,x,f_sb):
    i = x[0]
    q = x[1]
    c=sqrt(i**2+q**2)
    if c>1:
      print "bound"
      return 0
    phi=math.atan2(q,i)
    self.loadSidebandCalibrationWaveform(f_sb = f_sb,c = c,phi = phi)
    power = self.measureAveragePower()
    print "Sideband power at f_sb = %g GHz,i = %g, q = %g, c=%g, phi=%g : %g dBm" % (f_sb,i,q,c,phi,power) 
    return power
    
  def loadSidebandCalibrationWaveform(self,f_sb = 0,c = 0,phi = 0):
    
    length = 20000#self.period#int(1.0/self._awg.repetitionRate()*1e9)
    waveform = self.generateSidebandWaveform(f_sb = f_sb, c = c,phi = phi,length = length)
    self._awg.createRawWaveform("IQ_Sideband_Calibration_I",real(waveform),self._markers,"REAL")
    self._awg.createRawWaveform("IQ_Sideband_Calibration_Q",imag(waveform),self._markers,"REAL")

    return waveform

  def generateSidebandWaveform(self,f_sb = 0,c = 0,phi = 0,length = 100,delay = 0,normalize = True):
    """
    Generates a sideband waveform using a sideband frequency "f_sb", an amplitude correction "c" and a phase correction "phi"
    """
    if length == 0:
      return array([])
    waveformIQ = zeros((max(1,length)),dtype = complex128)
    times = arange(0,length,1)
    cr = c*exp(1j*phi)
    waveformIQ = 0.5*exp(-1j*f_sb*2.0*math.pi*(times+float(delay)))+0.5*cr*exp(1j*f_sb*2.0*math.pi*(times+float(delay)))
    return waveformIQ

  def measureAveragePower(self):
    trace = self._fsp.getSingleTrace()
    if trace == None:
      print "returning trace error"
      return 0
    minimum =  mean(trace[1])
    return minimum
  





  def calibrationParameters(self, f_c, f_sb):    
    try:
      (iO,qO)=(self.iOffset(f_c),self.qOffset(f_c))
      (c,phi) = self.sidebandParameters(f_c,f_sb)
      return {'i0':iO, 'q0':qO, 'c':c, 'phi':phi}
    except:
      print "unable to find correct parameters -> return (0,0,0,0)"
      return {'i0':0, 'q0':0, 'c':0, 'phi':0}
         
  def iOffset(self,f):
    return self._iOffsetInterpolation(f)
    
  def qOffset(self,f):
    return self._qOffsetInterpolation(f)
    
  def sidebandParameters(self,f_c,f_sb):
    if self.sidebandCalibrationData().column("f_c") == None:
      return (0,0)
    min_index = argmin(abs(self.sidebandCalibrationData().column("f_c")-f_c))
    f_c = self.sidebandCalibrationData()["f_c"][min_index]
    if min_index == None:
      return (0,0)
    calibrationData = self.sidebandCalibrationData().children(f_c = f_c)[0]
    rows = calibrationData.search(f_sb = f_sb)
    if rows != []:
      c = calibrationData.column("c")[rows[0]]
      phi = calibrationData.column("phi")[rows[0]]
    else:      
      try:
        phiInterpolation = scipy.interpolate.interp1d(calibrationData.column("f_sb"),calibrationData.column("phi"))      
        cInterpolation = scipy.interpolate.interp1d(calibrationData.column("f_sb"),calibrationData.column("c"))      
        c = cInterpolation(f_sb)
        phi = phiInterpolation(f_sb)
      except:
        return (0,0)
    return (c,phi)













