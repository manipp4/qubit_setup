import sys
import getopt
import numpy

from pyview.lib.classes import *
from pyview.helpers.instrumentsmanager import Manager
from numpy import *
register=Manager().getInstrument('register')

class Instr(Instrument):

      def saveState(self,name):
        print self._params
        return self._params

      def restoreState(self,state):
        self.clearPulse() 
        print state
        for pulse in state["pulses"].values():
          if pulse["shape"]==None:
            self.generatePulse(duration=pulse["duration"],frequency=pulse["frequency"],gaussian=pulse["gaussian"],amplitude=pulse["amplitude"],phase=pulse["phase"],DelayFromZero=pulse["DelayFromZero"],useCalibration=pulse["useCalibration"],name=pulse["name"])
          else:
            print "cannot generate pulse %s, shape was required" %pulse["name"]
        return None
      
      def removeAllPulses(self):
        self.pulses=dict()
        self._params["pulses"]=dict()
        self.sendPulse()
      
      def setCarrierFrequency(self, frequency):
        """
        Define carrier Frequency of the microwave source, only work in modulationMode = "IQMixer"
        """
        if self._params['modulationMode']!="IQMixer":
          print "ERROR ! u dont have to set carrier frequency in mode %s" %self._params['modulationMode']
        else:
          self._MWSource.setFrequency(frequency)
  
      def generatePulse(self, duration=100, gaussian=False,frequency=12., amplitude=1.,phase=0.,DelayFromZero=0, useCalibration=True,shape=None, name=None):
        """
        Generate in the buffer a pulse using parameters sents 
        Or use the "shape" instead of (duration, amplitude, delayFromZero)
        """
        #        print "generating pulse"
        if name==None:
          name='self%i'%self.index
          self.index+=1
        self._params["pulses"][name]=dict()
        self._params["pulses"][name]["frequency"]=frequency
        self._params["pulses"][name]["name"]=name
        if shape==None:
          self._params["pulses"][name]["shape"]=None
          self._params["pulses"][name]["duration"]=duration
          self._params["pulses"][name]["gaussian"]=gaussian
          self._params["pulses"][name]["amplitude"]=amplitude
          self._params["pulses"][name]["phase"]=phase
          self._params["pulses"][name]["DelayFromZero"]=DelayFromZero
          self._params["pulses"][name]["useCalibration"]=useCalibration
        else:
            self._params["pulses"][name]["shape"]="userDefined"

        pulse = numpy.zeros(register['repetitionPeriod'],dtype = numpy.complex128)
        if self._params['modulationMode']=="IQMixer":
          MWFrequency=float(self._MWSource.frequency())
          self._MWSource.turnOn()
          f_sb=-(MWFrequency-frequency)
          try:
            if shape==None:
              if gaussian:
                print 'gaussian pulse is not working !!!'
                pulse = gaussianPulse2(length=duration,delay = DelayFromZero,flank = flank)
              else:
                pulse[DelayFromZero:DelayFromZero+duration] = amplitude
            else:
              pulse[:]=shape[:]
            pulse*=numpy.exp(1.0j*phase)/2
            if useCalibration:
              calibrationParameters=self._mixer.calibrationParameters(f_sb=f_sb, f_c=MWFrequency)
              #print calibrationParameters
              cr = float(calibrationParameters['c'])*exp(1j*float(calibrationParameters['phi']))
              sidebandPulse = exp(-1.j*f_sb*2.0*math.pi*(arange(DelayFromZero,DelayFromZero+len(pulse))))+cr*exp(1.j*f_sb*2.0*math.pi*(arange(DelayFromZero,DelayFromZero+len(pulse))))
              self._AWG.setOffset(self._params["AWGChannels"][0],calibrationParameters['i0'])
              self._AWG.setOffset(self._params["AWGChannels"][1],calibrationParameters['q0'])
            else:
              sidebandPulse = exp(-1.j*2.0*math.pi*f_sb*(arange(DelayFromZero,DelayFromZero+len(pulse))))
              self._AWG.setOffset(self._params["AWGChannels"][0],0)
              self._AWG.setOffset(self._params["AWGChannels"][1],0)
            pulse[:]*=sidebandPulse 
          except:
            raise
          
        if self._params['modulationMode']=="SimpleMixer":
          self._MWSource.setFrequency(frequency)
          if shape==None:
              if gaussian:
                print 'gaussian pulse is not working !!!'
                pulse = gaussianPulse2(length=duration,delay = DelayFromZero,flank = flank)
              else:
                pulse[DelayFromZero:DelayFromZero+duration] = amplitude
          else:
              pulse[:]=shape[:]  
          if useCalibration:
              self._AWG.setOffset(self._params["AWGChannels"],self._mixer.calibrationParameters())
        if self._params['modulationMode']=="InternalModulation":
          print "NOT CONFIGURED YET ! DO NOT USE !"
        self.pulses[name]=[pulse,True]
        
      def sendPulse(self,forceSend=False, name=None):
          """
          Send the pulse with the name set as parameter, if no name is set, send all pulses
          """
          ## self._waveformsModified not working !!!!!!!!!!!!!!
          pulse = numpy.zeros(register['repetitionPeriod'],dtype = numpy.complex128)
          if name!=None:
            for k in self.pulses.keys():
              pulses[k][1]=False
            pulses[name][1]=True
          values=self.pulses.values()
          for value in values:
            if value[1]:
              pulse+=value[0]                      
          
          if forceSend or True:
            if self._params['modulationMode']=="IQMixer":
              markers=(zeros(register['repetitionPeriod'],dtype=int8),zeros(register['repetitionPeriod'],dtype=int8))
              markers[0][:register['readoutDelay']]=3
              markers[1][:register['readoutDelay']]=3
              self._AWG.loadiqWaveform(iqWaveform=pulse,channels=self._params["AWGChannels"],waveformNames=(self.name()+'i',self.name()+'q'),markers=markers)
            elif self._params['modulationMode']=="SimpleMixer":
#              print "sending pulse"
              if self._formGeneratorType=='AWG':
                self._AWG.loadRealWaveform(pulse, channel=self._params['AWGChannels'],waveformName=self.name())
                self._AWG.startAllChannels()
                self._AWG.run()
              if self._formGeneratorType=='AFG':
                print "need to  be tried before use (pulse_generator.py)"
                self._AWG.writeWaveform(name=self.name(),waveform=pulse)
                self._AWG.turnOn()
              
            elif self._params['modulationMode']=="InternalModulation":
              print "NOT CONFIGURED YET ! DO NOT USE !"
            else:
              print "self._params['modulationMode'] not correctly set"

  
      def startPulse(self, name):
        self.pulses[name][1]=True

      def stopPulse(self, name):
        self.pulses[name][1]=False

          
      def clearPulse(self):
          """
          Clear the pulse in the buffer and send an empty pulse in the AWG
          """
          self.pulses=dict()
          self._params["pulses"]=dict()
          self.totalPulse[:]=0
          self.sendPulse()
          
          
      def gaussianPulse(length = 500,delay = 0,flank = 4,normalize = True,resolution = 1,filterFrequency = 0.2):
        """
        Generate a gaussian Pulse !!!! NOT CONFIGURED !!!!
        """
        print "U DONT HAVE TO USE GAUSSIAN PULSE ! NOT CONFIGURED !!!!!!!!!!!!!"
        print "U DONT HAVE TO USE GAUSSIAN PULSE ! NOT CONFIGURED !!!!!!!!!!!!!"
        print "U DONT HAVE TO USE GAUSSIAN PULSE ! NOT CONFIGURED !!!!!!!!!!!!!"
        print "U DONT HAVE TO USE GAUSSIAN PULSE ! NOT CONFIGURED !!!!!!!!!!!!!"
        print "U DONT HAVE TO USE GAUSSIAN PULSE ! NOT CONFIGURED !!!!!!!!!!!!!"
        waveform = numpy.zeros((math.ceil(flank*2)+1+int(math.ceil(length))+math.ceil(delay))*int(1.0/resolution),dtype = numpy.complex128)
        if length == 0:
          return waveform
        for i in range(0,len(waveform)):
          t = float(i)*resolution
          if t <= flank+delay:
            waveform[i] = numpy.exp(-0.5*math.pow(float(t-delay-flank)/float(flank)*3.0,2.0))
          elif t >= flank+delay+length:
            waveform[i] = numpy.exp(-0.5*math.pow(float(t-delay-flank-length)/float(flank)*3.0,2.0))
          else:
            waveform[i] = 1.0
        pulseFFT = numpy.fft.rfft(waveform)
        freqs = numpy.linspace(0,1.0,len(pulseFFT))
        filteredPulseFFT = pulseFFT
        filteredPulse = numpy.array(numpy.fft.irfft(filteredPulseFFT,len(waveform)),dtype = numpy.complex128)
        filteredPulse = waveform
        integral = numpy.sum(filteredPulse)
        if normalize:
          filteredPulse/=integral/float(length)*resolution
        return filteredPulse



      def parameters(self):
        """
        return the paramters
        """
        return self._params

      def initialize(self, name, MWSource, mixer, formGenerator, AWGChannels, modulationMode, formGeneratorType = 'AWG'):
        """
        Initialise the instrument
        """
        instrumentManager=Manager()
        self._MWSource=instrumentManager.getInstrument(MWSource)
        self._mixer=instrumentManager.getInstrument(mixer)
        self._AWG=instrumentManager.getInstrument(formGenerator)
        self._formGeneratorType=formGeneratorType
        self._params=dict()
        self._params["MWSource"]=MWSource
        self._params["mixer"]=mixer
        self._params["AWG"]=formGenerator
        self._params["AWGChannels"]=AWGChannels
        self._params["modulationMode"]=modulationMode
        self.pulses=dict()
        self._params["pulses"]=dict()
        register['repetitionPeriod']=20000
        self.totalPulse=numpy.zeros(20000,dtype = numpy.complex128)
        self.index=0
        return
