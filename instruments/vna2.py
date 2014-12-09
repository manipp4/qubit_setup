import sys
import getopt

from pyview.lib.classes import *
if 'lib.datacube2' in sys.modules:
  reload(sys.modules['lib.datacube2'])
from pyview.lib.datacube2 import Datacube
from numpy import *
from pyvisa import vpp43

class VNATrace:

  def __init__(self):
    self.frequencies = []
    self.phase = []
    self.magnitude = []
    self.timestamp = ''
    self.instrument = None  

#This is the VNA instrument.
class Instr(VisaInstrument):

    #Initializes the instrument.
    def initialize(self,visaAddress = "GPIB::29",name = "VNA"):
        self._name = "Anritsu VNA"
        print "Initializing with resource %s" % visaAddress
        if DEBUG:
          print "Initializing VNA"
        try:
          self._visaAddress = visaAddress
        except:
          print "ERROR: Cannot initialize instrument!"


    def clearDevice(self):
      handle = self.getHandle()
      handle.timeout = 1
      cnt = 0
      handle.write("*CLS")
      while True:
        try:
          if cnt>100:
            return False
          if int(vpp43.read_stb(handle.vi)) & 128:
            return True
          time.sleep(0.1)
        except visa.VisaIOError:
          cnt+=1
      return False
      
    def triggerReset(self):
      self.write("*CLS;TRS;")
      
    def setAttenuation(self,a):
      self.write("SA1 %f DB" % a)
      return self.attenuation()
      
    def attenuation(self):
      return float(self.ask("SA1?"))
    
    def setTotalPower(self, totalPower):
      power=totalPower%10
      attenuation=totalPower-power
      self.setAttenuation(-attenuation)
      time.sleep(0.3)
      self.setPower(power)
      print power,attenuation
      return self.totalPower()

    def totalPower(self):
      return 5+self.power()-self.attenuation()

    def setPower(self,power):
      self.write("PWR %f DB" % power)
      return self.power()
    
    def power(self):
      return float(self.ask("PWR?"))
    
    def startFrequency(self):
      return float(self.ask("SRT?"))
    
    def setStartFrequency(self,f):
      self.write("SRT %f GHZ" % f)
      return self.startFrequency()
      
    def stopFrequency(self):
      return float(self.ask("STP?"))
    
    def setStopFrequency(self,f):
      self.write("STP %f GHZ" % f)
      return self.stopFrequency()
    
    def centerFrequency(self):
      return float(self.ask("CNTR?"))
    
    def setCenterFrequency(self,f):
      self.write("CNTR %f GHZ" % f)
      return self.centerFrequency()
    
    def spanFrequency(self):
      return float(self.ask("SPAN?"))
    
    def setSpanFrequency(self,f):
      self.write("SPAN %f GHZ" % f)
      return self.spanFrequency()
    
    def setNumberOfPoints(self,n):
      self.write("NP%i" % n)
    
    def averaging(self):
      return self.ask("AOF?")
    
    def setAveraging(self,Q):
      if Q:
        self.write("AON")
      else :
        self.write("AOF")     
      return self.write("AOF?")
    
    def numberOfAveraging(self):
      return int(float(self.ask("AVG?")))
    
    def setNumberOfAveraging(self,n):
      self.write("AVG %i" % n)
      return self.numberOfAveraging()

    def videoBW(self):
      return int(10**(float(self.ask("IFX?"))))

    def setVideoBW(self, f):
      i=math.log10(f)
      self.write("IF%i" % i)
      return self.videoBW()
            
    def waitFullSweep(self):
      self.write("*CLS;HLD;TRS;WFS;")
      handle = self.getHandle()
      handle.timeout = 1
      cnt = 0
      while True:
        try:
          if cnt>100:
            return False
          time.sleep(1)
          status =  vpp43.read_stb(handle.vi)
          if int(status) & 128:
            return True
        except visa.VisaIOError:
          cnt+=1
          print sys.exc_info()
      return False

    def electricalLength(self):
  	  self.write("RDA")
  	  return float(self.ask("RDD?"))
  	  
    
    def getValuesAtMarker(self,i,waitNewSweep=False):
      if waitNewSweep: self.write("TRS;WFS;")
      return self.ask("OM"+str(i))
                 
                 
      
    #Get a trace from the instrument and store it to a local array.
    def getTrace(self,correctPhase = False,waitFullSweep = False,timeOut = 1600, addedAttenuators=0.):
      print "Getting trace..."
      trace = Datacube()
      if DEBUG:
        print "Getting trace..."
      handle = self.getHandle()
      handle.timeout = timeOut
      if waitFullSweep:
#        freqs = self.ask_for_values("HLD;TRS;WFS;fma;msb;OFV;") 2011/12 VS 
        self.write("TRS;WFS;")
      freqs = self.ask_for_values("fma;msb;OFV;")
      data = self.ask_for_values("fma;msb;OFD;")
      freqs.pop(0)
      data.pop(0)
      mag = []
      phase = []
      #If y length is twice the x length, we got phase and magnitude.
      if len(data) == 2*len(freqs):
        for i in range(0,len(data)):
          if i%2 == 0:	
            mag.append(data[i])
          else:
					 phase.append(data[i])
      else:
        mag = data
      trace.createColumn(name="freq",values=freqs)
      trace.createColumn(name="mag",values=mag)
      attenuation = float(self.ask("SA1?"))
      power = float(self.ask("PWR?"))
      trace.column("mag")[:]+= attenuation+addedAttenuators
      params = dict()
      params["attenuation"] = attenuation
      params["power"] = power
      trace.setParameters(params)
      if len(phase) > 0:
        correctedPhase = []
        if correctPhase:
          correctedPhase.append(phase[0])
          oldPhi = phase[0]
          for phi in phase[1:]:
            if fabs(phi+360.0-oldPhi) < fabs(phi-oldPhi):
              newPhi = phi+360.0
            elif fabs(phi-360.0-oldPhi) < fabs(phi-oldPhi):
              newPhi = phi-360.0
            else:
              newPhi = phi
            correctedPhase.append(newPhi)
            oldPhi = newPhi
        else:
          correctedPhase = phase
        trace.createColumn(name="phase",values=correctedPhase)
      print "returning trace."
      return trace

    def setCWFrequency(self,f):
      self.write("CWF %f GHZ" % f)
      return self.CWFrequency()

    def CWFrequency(self):
      return float(self.ask("CWF?"))
      
    def turnOffCW(self):
      self.write("SWP")
    
    def turnOnaver(self):
      self.write("AON")
      
    def turnOffaver(self):
      self.write("AOF")
      
    def turnOnHold(self):
      self.write("HLD")
      
    def turnOnSweep(self):
      self.write("CTN")
      
    def turnOffRFOnHold(self):
      self.write("RH0")
      
    def keepOnRFOnHold(self):
      self.write("RH1")