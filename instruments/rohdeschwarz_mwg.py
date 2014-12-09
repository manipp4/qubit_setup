import sys
import getopt
import math

from pyview.lib.classes import *

class Instr(VisaInstrument):
  
  def saveState(self,name):
    """
    Save the instrument state. Just returns a dictionary with all relevant parameters.
    """
    return self.parameters()
    
  def restoreState(self,state):
    """
    Restores a previously saved state.
    """
    print state
    self.setFrequency(state["frequency"])
    self.setPower(state["power"])
    if state["output"] == True:
      self.turnOn()
    elif state["output"] == False:
      self.turnOff()
  
  def frequency(self):
    """
    Returns the current microwave frequency.
    """    
    freq = float(self.ask("FREQ:FIXED?"))/1e9
    self.notify("frequency",freq)
    return freq
  
  def power(self):
    """
    Returns the current microwave power.
    """
    power = float(self.ask("POW?"))
    self.notify("power",power)
    return power
  
  def setFrequency(self,freq):
    """
    Sets the microwave frequency.
    "freq" is given in GHz.
    """
    self.write("SOUR:FREQ:FIX %f" % (freq*1e9))
    return self.frequency()
    
  def setPower(self,power):
    """
    Sets the output power in dBm
    """
    self.write("POW %f" % power)
    return self.power()

      
  def parameters(self):
    """
    Returns all relevant parameters of the instrument.
    """
    params = dict()
    params['frequency'] = self.frequency()
    params['power'] = self.power()
    params['output'] = self.output()
    return params
  
  def turnOn(self):
    """
    Turn on the microwave.
    """
    self.write("OUTP ON")
    return self.output()
    
  def turnOff(self):
    """
    Turn off the microwave.
    """
    self.write("OUTP OFF")
    return self.output()
    
  def setOutput(self,output):
    """
    set output to On(True) or Off(False)
    """
    if output:
      return self.turnOn()
    else:
      return self.turnOff()

  def output(self):
    """
    Return the current state of the microwave output.
    """
    state = int(self.ask("OUTP?"))
    if state != 0:
      state = True
    else:
      state = False
    self.notify("output",state)
    return state

    
  def initialize(self,name = "RohdeSchwarz_MWG", visaAddress = "GPIB0::28"):
    self._output = None
    try:
      self._name = name
      if DEBUG:
        print "Initializing an RohdeSchwarz MWG with address %s" % visaAddress
      self._visaAddress = visaAddress
    except:
      self.statusStr("An error has occured. Cannot initialize RohdeSchwarz MWG.")        
