import sys
import getopt
import numpy


from pyview.lib.classes import *
from pyview.helpers.instrumentsmanager import Manager
from numpy import *

import macros.generatorFunctionLib as generatorFunctionLib
reload(sys.modules['macros.generatorFunctionLib'])
import macros.generatorFunctionLib as generatorFunctionLib

__DEBUG__ = False

class Pulse:
  """   
  Class for a pulse  with following parameters:
    - name: name of the pulse
    - pulseGenerator : attached pulseGenerator defined in the class Instr below
    - frequency: frequency of the microwave inside the enveloppe defined by generatorFunction
    - phase: phase  of the microwave inside the enveloppe defined by generatorFunction
    - generatorFunction: shape or enveloppe of the pulse if frequency !=0.
    - applyCorrections: boolean indicating if corrections are to be done at the pulse generation, depending on a generation mode (simple mining, IQ mixing, etc).
  """
  def __init__(self,name="untitled",pulseGenerator=None, frequency=0,phase=0,generatorFunction="square",applyCorrections=False,pulseOn=True, **kwargs):
    """
    Creator of Pulse instance
    """
    self._pulseGenerator=pulseGenerator
    self.frequency=frequency
    self.phase=phase
    self.applyCorrections=applyCorrections
    self.name=name
    self.pulseOn=pulseOn
    self._numberOfPoints=self._pulseGenerator.numberOfPoints()
    self._samplingTime=self._pulseGenerator.samplingTime()
    self._pulseArray=zeros(self._numberOfPoints)
    self._generatorFunction=generatorFunction
    self._parameters=kwargs

    try:
      self._pulseArray[:]=getattr(generatorFunctionLib,generatorFunction)(self._numberOfPoints, self._samplingTime, **kwargs)
    except "Attribute Error":
      print "function %s does not exist" %generatorFunction
    except:
      raise

  def __str__(self):
    return self._generatorFunction +" pulse %s" %str(self._parameters)+ ", frequency : "+str(self.frequency)+ ", apply corrections : "+str(self.applyCorrections)



## old marker class
#class Marker:    
#  """
#  Class for a Marker  with following parameters:
#    - name:
#    - pulseGenerator : attached pulseGenerator defined in the class Instr below
#  """
#  def __init__(self,name="untitled",pulseGenerator=None, onPairs=[]):
#    """
#    Creator of marker instance
#    """
#    self.name=name
#    self._pulseGenerator=pulseGenerator
#    self._numberOfPoints=self._pulseGenerator.numberOfPoints()
#    self._shape=numpy.zeros(self._numberOfPoints,dtype=bool)
#    for [on,off] in onPairs:
#      self._shape[on:off]=True

# new marker class made by Kiddi 20/08/2014
class Marker:
  """
  Class for a Marker  with following parameters:
    - name:
    - pulseGenerator : attached pulseGenerator defined in the class Instr below
  """
  def __init__(self,name="untitled",pulseGenerator=None, start1=0, stop1=10000, start2=None, stop2=None):
    """
    Creator of marker instance. A marker contains a markerArray which is the array sent to a specific channel of the AWG. The markerArray is made up of two shapes, one for each marker output of a single channel
    """
    self.name=name
    self._pulseGenerator=pulseGenerator
    self._numberOfPoints=self._pulseGenerator.numberOfPoints()
    self._samplingTime=self._pulseGenerator.samplingTime()
    self._shape1=numpy.zeros(self._numberOfPoints)
    self._shape2=numpy.zeros(self._numberOfPoints)
    self._shape1[:]=getattr(generatorFunctionLib,'square')(self._numberOfPoints, self._samplingTime, start1, stop1, amplitude=1)
    if start2==None: start2=start1
    if stop2==None: stop2=stop1
    self._shape2[:]=getattr(generatorFunctionLib,'square')(self._numberOfPoints, self._samplingTime, start2, stop2, amplitude=2)
    self.markerArray=[sum(i)for i in zip(self._shape1,self._shape2)]

class Instr(Instrument):
      """
      Pulse generator class.
      A pulse generator is an object that stores a list of pulses and possibly optional markers.
      Its input parameters at creation are:
      - name: name of the generator
      - MWSource: the microwave source attached to the generator
      - mixer: an optional mixer attached to the generator
      - formGenerator: the hardware AWG or AFG attache dto this generator
      - AWGChannels: tuple of 1 or 2 channel numbers of the formGenerator
      - modulationMode: None or string describing how to obtain the pulse frequency, possibly by modulation ("simplerMixer", "IQMixer", "internalModulation")
      - formGeneratorType: string describing the type of hardware used to define the waveform ('AWG' , 'AFG4',...)
      The main properties and methods are:
      - a params dictionary with keys {"MWSource","AWG","modulationMode","AWGChannels","mixer"}
      - pulseList : a tuple of pulses
      - markersList : a list of markers
      - saveState(name): returns the current params dictionary
      - restoreState(params): restores the pulse generator from the params dicitonary indicated
      - setCarrierFrequency(frequency): defines carrier Frequency of the microwave source; work only in modulationMode = "IQMixer"
      - parameters(): returns the current params dictionary
      - samplingTime(): returns the current samplingTime
      - numberOfPoints(): returns the current numberOfPoints
      - getPulseList(): returns the current list of pulses
      - getMarkerList(): returns the current list of markers
      - addPulse(): Adds a pulse to the pulseList list
      - addMarker(channel=None, **kwargs): Adds a marker to the markerList list
      - preparePulseSequence():  Generates the sample values of each pulse waveform channels and markers in pulseList and markersList, and adds them to form a single waveform per channel.
      - clearPulse(): clears all pulses from pulseList
      - clearMarkersList(): clears all markers from markerList
      - sendPulseSequence(outputName=None):Sends the pulse and markers  built by  preparePulseSequence on the appropriate channels of the appropriate hardware.

      """
      def initialize(self, name, formGenerator, AWGChannels, modulationMode=None, MWSource=None, mixer=None, formGeneratorType = 'AWG'):
        """
        Initialise the instrument at instantiation
        """
        instrumentManager=Manager()
        self._MWSource=instrumentManager.getInstrument(MWSource) if MWSource!=None else None  # optional microwave source attached to this pulse generator
        self._mixer=instrumentManager.getInstrument(mixer)  if mixer!=None else None          # optional mixer attached to this pulse generator
        self._AWG=instrumentManager.getInstrument(formGenerator)  # hardware generator attached to this pulse generator
        self._formGeneratorType=formGeneratorType                # type of generators in AWG, AFG, NOne, ...
        self._params=dict()                                       # dictionary of parameters
        self._params["MWSource"]=MWSource
        self._params["formGenerator"]=formGenerator                         # confusion here: should be change for formGenerator
        self._params["modulationMode"]=modulationMode
        self._params["AWGChannels"]=AWGChannels                   
        self._params["mixer"]=mixer
        self.pulses=dict()                                        # Obsolete. Replaced by pulseList. Mainted for compatinbbility reasons
        self._params["pulses"]=self.pulses
        self.markersDict=dict()                                   # Obsolete. Replaced by markersList. Mainted for compatinbbility reasons
        self._params["markersDict"]=self.markersDict
        self.totalPulse=numpy.zeros(self.numberOfPoints(),dtype = numpy.complex128) # Obsolete.
        self.index=0                                              # Obsolete.
        self.indexMarker=0                                        # Obsolete.
        self.pulseList=()                                         # List of pulses (object of class pulse)
        self.markersList1=()                                       # List of markers (object of class marker)
        self.markerArray1=zeros(self.numberOfPoints(),dtype=numpy.int8) # An array of zeros into which the markers will be concatented
        self.markersChannels= 2 if self._params["modulationMode"]=='IQMixer' else 1 # total number of markers attached to this pulse generator #self._AWG.markersPerChannel()*
        if self.markersChannels==2:
          self.markersList2=()                                    # List of markers (object of class marker)
          self.markerArray2=zeros(self.numberOfPoints(),dtype=numpy.int8) # An array of zeros into which the markers will be concatented
        return

      def saveState(self,name):
        """
        returns the params dictionary
        """
        return self._params

      def restoreState(self,state):
        """
        Restores the pulse generator from the params dicitonary indicated
        """
        self.clearPulse() 
        print state
        for pulse in state["pulses"].values():
          if pulse["shape"]==None:
            self.generatePulse(duration=pulse["duration"],frequency=pulse["frequency"],gaussian=pulse["gaussian"],amplitude=pulse["amplitude"],phase=pulse["phase"],DelayFromZero=pulse["DelayFromZero"],useCalibration=pulse["useCalibration"],name=pulse["name"])
          else:
            print "cannot generate pulse %s, shape was required" %pulse["name"]
        return None
      
      def setCarrierFrequency(self, frequency):
        """
        Define carrier Frequency of the microwave source, only work in modulationMode = "IQMixer"
        """
        if self._params['modulationMode']!="IQMixer":
          print "WARNING ! Carrier Frequency change also Tone Frequency in %s mode" %self._params['modulationMode']
        self._MWSource.setFrequency(frequency)

      def parameters(self):
        """
        return the paramters
        """
        return self._params

      def samplingTime(self):
        """
        Supposed to return sampling time in ns. 
        Not written yet
        return 1 ns
        """
        return 1
      
      def numberOfPoints(self):
        """
        Should ask the AWG/AFG/or anything else the max numberOfPoints
        define a way to choose cleverly the num of points
        !!!!!!!!!!!!!!
        Not implemented yet, always return 20000 
        !!!!!!!!!!!!!!
        """
        return 20000

      def carrierFrequency(self):
        return self._MWSource.frequency()

      def getPulseList(self):
        return self.pulseList

      def getMarkerList(self,channel=1):
        if channel==1:
          return self.markersList1
        if channel==2:
          return self.markersList2
      
      def addPulse(self, **kwargs):
        """
        Adds a pulse to the pulseList list
        """
        self.pulseList+=(Pulse(pulseGenerator=self, **kwargs),)
        if __DEBUG__:print "pulseAdded"

      def addMarker(self, channel=None, start1=0, stop1=10000):
        if channel==None:
          print "ERROR : YOU NEED TO GIVE A CHANNEL IN ADDING A MARKER !!!! OPERATION ARBORED"
          return None
        if channel>self.markersChannels:
          print "ERROR : you are trying to tune a marker channel that does not belong to this pulseGenerator"
        elif channel==1:
          self.markersList1+=(Marker(pulseGenerator=self, start1=start1, stop1=stop1),)
        else:
          self.markersList2+=(Marker(pulseGenerator=self, start1=start1, stop1=stop1),)
        if __DEBUG__:print "markerAdded"

      def preparePulseSequence(self):
        """
          Generates the sample values of each pulse waveform channels and markers in pulseList and markersList, and adds them to form a single waveform per channel.
          The method used depends on _params["modulationMode"] in the generator and on the applyCorrections property of each pulse.0
        """
        # get carrier frequency
        if self._MWSource!=None:
          carrierFrequency=self.carrierFrequency() 
        else: carrierFrequency=0

        # Decide to apply or not corrections
        applyCorrectionsArray=[pulse.applyCorrections for pulse in self.pulseList]
        applyCorrection=True in applyCorrectionsArray

        # Define self.pulseSequenceArray
        self.pulseSequenceArray=zeros(self.numberOfPoints(),dtype=numpy.complex128)
        self._offsets=[None,None]

        for pulse in self.pulseList:
          if not(pulse.pulseOn): continue
          correctedPulseArray=zeros(self.numberOfPoints(),dtype=numpy.complex128)

          if self._params["modulationMode"]=="IQMixer":
            f_sb=pulse.frequency-carrierFrequency
            if applyCorrection:
              calibrationParameters=self._mixer.calibrationParameters(f_sb=pulse.frequency-carrierFrequency, f_c=carrierFrequency)
              if __DEBUG__: print calibrationParameters
              sidebandPulse=self._mixer._calibration.generateSidebandWaveform(f_sb = f_sb,c = calibrationParameters['c'],phi = calibrationParameters['phi'],length=self.numberOfPoints())
              self._offsets=[calibrationParameters["i0"],calibrationParameters["q0"]]
            else:
              sidebandPulse = exp(-1.j*(2.0*math.pi*f_sb*arange(0,self.numberOfPoints())))
            correctedPulseArray[:]=pulse._pulseArray*sidebandPulse*exp(1.j*pulse.phase)

          elif self._params["modulationMode"]=="SimpleMixer":
            if applyCorrection:
              self._offsets=[self._mixer.calibrationParameters()]
            else:
              self._offsets[0]=0
            correctedPulseArray[:]=pulse._pulseArray

          elif self._params["modulationMode"]=="InternalModulation":
            print "not configured yet"

          elif self._params["modulationMode"]==None:
            if applyCorrection:
              if hasattr(self,"pulseCorrectionFunction"):
                correctedPulseArray[:]=self.pulseCorrectionFunction(pulse._pulseArray) 
              else:
                print self.name(), ": no correction function found for DC pulses"
                correctedPulseArray[:]=pulse._pulseArray
            else:
              correctedPulseArray[:]=pulse._pulseArray        
          else:
            print "bad modulationMode"

          self.pulseSequenceArray[:]+=correctedPulseArray[:]
          if self._formGeneratorType=='AWG':
            if max(abs(self.pulseSequenceArray))>1:
              print self.name(), "error : Asked pulse not in the range [-1,1]....."
              print "Continue anyway. Generated pulse will be wrong."

      def prepareMarkerSequence(self):
        """
          concatenates the markers. If it is a 2 channel mixer (i.e. an IQ mixer) and markers list for the second cannel is empty, markersList2=(), then the first on is copied to it (i.e markersList2=markersList1)
        """
        # first prepare the markers for the first channel of the pulse generaton
        markerSequence1shape1=zeros(self.numberOfPoints(),dtype=numpy.int8)
        markerSequence1shape2=zeros(self.numberOfPoints(),dtype=numpy.int8)
        for marker in self.markersList1:
          markerSequence1shape1[:]+=marker._shape1
          markerSequence1shape2[:]+=marker._shape2

        # take care of marker ovelap
        for i in range(len(markerSequence1shape1)):
          if markerSequence1shape1[i]>1:
            markerSequence1shape1[i]=1
          if markerSequence1shape2[i]>2:
            markerSequence1shape2[i]=2

        self.markerArray1[:]=[sum(i)for i in zip(markerSequence1shape1[:],markerSequence1shape2[:])]

        # if there are 2 channels the second one is prepared here
        if self.markersChannels==2:
  
          markerSequence2shape1=zeros(self.numberOfPoints(),dtype=numpy.int)
          markerSequence2shape2=zeros(self.numberOfPoints(),dtype=numpy.int)
          
          if self.markersList2==():
            self.markersList2=self.markersList1
          for marker in self.markersList2:
            markerSequence2shape1[:]+=marker._shape1
            markerSequence2shape2[:]+=marker._shape2
          for i in range(len(markerSequence2shape1)):
            if markerSequence2shape1[i]>1:
              markerSequence2shape1[i]=1
            if markerSequence2shape2[i]>2:
              markerSequence2shape2[i]=2

          self.markerArray2[:]=[sum(i)for i in zip(markerSequence2shape1[:],markerSequence2shape2[:])]

        



      def clearPulse(self):
          """
          Clear the pulse in the buffer and send an empty pulse in the AWG
          """
          self.pulses=dict()              # old mode for compatibility reasons
          self._params["pulses"]=dict()   # old mode  
          self.totalPulse[:]=0            # old mode
          self.sendPulse()                # old mode

          self.clearMarkersList()         # new mode
          self.pulseList=()
          self.preparePulseSequence()
          self.prepareMarkerSequence()
          self.sendPulseSequence()

      def clearMarkersList(self):
        self.markersList1=()
        self.markersList2=()


      def sendPulseSequence(self,outputName=None):
        """
          Sends the pulse and markers  built by  preparePulseSequence on the appropriate channels of the appropriate hardware.
        """
        if outputName==None:outputName=str(self.name())
        if self._params['modulationMode']=="IQMixer":
          if self.markersList1==():
            self.markerArray1[:10000]=3
          if self.markersList2==():
            self.markerArray2[:10000]=3
          markers=(self.markerArray1,self.markerArray2) #################### NOT WRITTEN YET
          #markers[0][:10000]=3 #################### NOT WRITTEN YET
          #markers[1][:10000]=3 #################### NOT WRITTEN YET
          self._AWG.loadComplexWaveforms(complexWaveform=self.pulseSequenceArray,channels=self._params["AWGChannels"],waveformNames=(outputName+'i',outputName+'q'),markers=markers) #################### NOT WRITTEN YET
          if self._offsets[0]!=None:self._AWG.setOffset(self._params["AWGChannels"][0],self._offsets[0])
          if self._offsets[1]!=None:self._AWG.setOffset(self._params["AWGChannels"][1],self._offsets[1])
        elif self._params['modulationMode']=="SimpleMixer":
          if self._formGeneratorType=='AWG':
            if self.markersList1==():
              self.markerArray1[:10000]=3
            markers=(self.markerArray1,self.markerArray1)
            #self._AWG.loadComplexWaveforms(complexWaveform=self.pulseSequenceArray,channels=(3,3),waveformNames=(outputName+'i',outputName+'q'),markers=markers)
            self._AWG.loadRealWaveform(self.pulseSequenceArray, channel=self._params['AWGChannels'],markers=markers[0],waveformName=outputName)
            #self._AWG.setOffset(self._params["AWGChannels"],self._offsets[0])
            self._AWG.startAllChannels()
            self._AWG.run()
          if self._formGeneratorType=='AFG':
            print "need to  be tried before use (pulse_generator.py)"
            self._AWG.writeWaveform(name=outputName,waveform=pulse)
            self._AWG.setOffset(self._params["AWGChannels"][0],self._offsets[0])
            self._AWG.turnOn()
        elif self._params['modulationMode']==None:
            if self.markersList1==():
              self.markerArray1[:10000]=3
            markers=(self.markerArray1,self.markerArray1)
            self._AWG.loadRealWaveform(self.pulseSequenceArray, channel=self._params['AWGChannels'][0],markers=markers[0],waveformName=outputName)
        elif self._params['modulationMode']=="InternalModulation":
          print "NOT CONFIGURED YET ! DO NOT USE !"
        else:
          pass
          print "self._params['modulationMode'] not correctly set: ",self._params['modulationMode'] # This is the valid sender to the hardware apparatus

##### MODE SEQUENCE IMPLEMENTED BY KIDDI
      def sequenceWaveform(self,seqNumber,channel=None,name=None,repeat=1):
          """
          Takes the waveform name and loads it into a sequence slot seqNumber on channel
          """
          if channel==None:
            channel=self._params['AWGChannels']
          self._AWG.appendWaveformToSequence(seqNumber,channel,name,repeat=repeat)
          
      def sequenceWaveformList(self,channel=None,names=None,start=0,stop=0):
          """
          Takes all the waveforms in the user defined waveform list or a given list and loads them into a sequence on channel
          """
          if channel==None:
            channel=self._params['AWGChannels']
          if names==None:
            allNames=self._AWG.getWaveformNames()
            if start==0 and stop==0:
              names=allNames[25:] # The first 25 waveforms are the predfined ones
            else:
              names=allNames[25+start:25+stop]
          for i in range(0,len(names)):
            self._AWG.appendWaveformToSequence(i+1,channel,names[i])
            
      def clearSequence(self):
        self._AWG.createSequence(0)

#####
# OBSOLETE DON NOT USE ANY MORE. KEPT FOR COMPATIBILITY REASONS
      def generatePulse(self, duration=100, gaussian=False,frequency=12., amplitude=1.,phase=0.,DelayFromZero=0, useCalibration=False,shape=None, name=None):
        """
        Generates in the buffer a pulse using parameters sents 
        If gaussian is true, generates a gaussian pulse using duration as sigma and DelayFromZero as central time for the gaussian (also using amplitude for maximum)
        Or use the "shape" instead of (duration, amplitude, delayFromZero)
        """
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

        pulse = numpy.zeros(self.numberOfPoints(),dtype = numpy.complex128)
        if self._params['modulationMode']=="IQMixer":
          MWFrequency=float(self._MWSource.frequency())
          self._MWSource.turnOn()
          f_sb=frequency-MWFrequency
          try:
            if shape==None:
              if gaussian:
                print 'gaussian pulse is not working !!!'
                pulse = self.gaussianPulse(sigma=duration,delay = DelayFromZero,amplitude=amplitude)
              else:
                pulse[DelayFromZero:DelayFromZero+duration] = amplitude
            else:
              pulse[:]=shape[:]
            pulse*=numpy.exp(1.0j*phase)/2
            if useCalibration:
              calibrationParameters=self._mixer.calibrationParameters(f_sb=f_sb, f_c=MWFrequency)
              if __DEBUG__:print calibrationParameters
              #cr = float(calibrationParameters['c'])*exp(1j*float(calibrationParameters['phi']))
              if __DEBUG__:print "f_sb=",f_sb
              #sidebandPulse = exp(-1.j*f_sb*2.0*math.pi*(arange(DelayFromZero,DelayFromZero+len(pulse))))+cr*exp(1.j*f_sb*2.0*math.pi*(arange(DelayFromZero,DelayFromZero+len(pulse))))
              sidebandPulse=self._mixer._calibration.generateSidebandWaveform(f_sb = f_sb,c = calibrationParameters['c'],phi = calibrationParameters['phi'],length=self.numberOfPoints())
              self._AWG.setOffset(self._params["AWGChannels"][0],calibrationParameters['i0'])
              self._AWG.setOffset(self._params["AWGChannels"][1],calibrationParameters['q0'])
            else:
              sidebandPulse = exp(-1.j*2.0*math.pi*f_sb*(arange(DelayFromZero,DelayFromZero+len(pulse))))
              #self._AWG.setOffset(self._params["AWGChannels"][0],0)
              #self._AWG.setOffset(self._params["AWGChannels"][1],0)
            pulse[:]*=sidebandPulse 
          except:
            raise
          
        if self._params['modulationMode']=="SimpleMixer":
          self._MWSource.setFrequency(frequency)
          if shape==None:
              if gaussian:
                print 'gaussian pulse is not working !!!'
                print duration, DelayFromZero,amplitude
                pulse = self.gaussianPulse(sigma=duration,delay=DelayFromZero,amplitude=amplitude)
              else:
                pulse[DelayFromZero:DelayFromZero+duration] = amplitude
          else:
              pulse[:]=shape[:]  
          if useCalibration:
              self._AWG.setOffset(self._params["AWGChannels"],self._mixer.calibrationParameters())
        if self._params['modulationMode']=="InternalModulation":
          print "NOT CONFIGURED YET ! DO NOT USE !"
        self.pulses[name]=[pulse,True] 

      def generateMarker(self,name=None,start=0,stop=10000,level=3,start2='',stop2='',start3='',stop3=''):   # Made by Kiddi 17/09/13
        'generates markers which rise to level at point start and return to zero at stop '
        if name==None:
          name='self%i'%self.indexMarker
          self.indexMarker+=1
        self._params["markersDict"][name]=dict()
        self._params["markersDict"][name]["name"]=name
        self._params["markersDict"][name]["start"]=start
        self._params["markersDict"][name]["stop"]=stop
        self._params["markersDict"][name]["level"]=level
        
        marker=numpy.zeros(self.numberOfPoints(),dtype=numpy.int8)
        marker[start:stop]=level
        if start2!='':
          marker[start2:stop2]=level
        if start3!='':
          marker[start3:stop3]=level
        self.markersDict[name]=[marker,True]

      def sendPulse(self,forceSend=False, name=None, markersName=None, outputName=None): # markersName=None added by Kiddi 17/09/2013
          """
          Sends the pulse with the name set as parameter, if no name is set, send all pulses
          """
          pulse = numpy.zeros(self.numberOfPoints(),dtype = numpy.complex128)
          if name!=None:
            for k in self.pulses.keys():
              self.pulses[k][1]=False
            self.pulses[name][1]=True
          values=self.pulses.values()
          for value in values:
            if value[1]:
              pulse+=value[0]
  
          markers=None                            # section marker added by DV + KJ 09/2013
          if markersName!= None:
            markers = numpy.zeros(self.numberOfPoints(),dtype=int8)
            if markersName!='All':
              for k in self.markersDict.keys():
                self.markersDict[k][1]=False
              self.markersDict[markersName][1]=True
            values=self.markersDict.values()    # section marker added by DV + KJ 09/2013             
            for value in values:
              if value[1]:
                markers+=value[0]
          if outputName==None:
            outputName=self.name()
               
          if forceSend or True:
            if self._params['modulationMode']=="IQMixer":
              markers=(zeros(self.numberOfPoints(),dtype=int8),zeros(self.numberOfPoints(),dtype=int8))
              markers[0][:self.readoutDelay()]=3
              markers[1][:self.readoutDelay()]=3
              self._AWG.loadiqWaveform(iqWaveform=pulse,channels=self._params["AWGChannels"],waveformNames=(outputName+'i',outputName+'q'),markers=markers)
            elif self._params['modulationMode']=="SimpleMixer":
              #print "sending pulse"
              if self._formGeneratorType=='AWG':
                self._AWG.loadRealWaveform(pulse, channel=self._params['AWGChannels'],markers=markers,waveformName=outputName)# Markers=None added by Kiddi 17/09/2013
                self._AWG.startAllChannels()
                self._AWG.run()
              if self._formGeneratorType=='AFG':
                print "need to  be tried before use (pulse_generator.py)"
                self._AWG.writeWaveform(name=outputName,waveform=pulse)
                self._AWG.turnOn()
            elif self._params['modulationMode']=="InternalModulation":
              print "NOT CONFIGURED YET ! DO NOT USE !"
            else:
              print "self._params['modulationMode'] not correctly set"

      def loadWaveformToList(self, waveformName=None, markersName=None, outputName=None):
          """
          Loads a square pulse and markers from the corresponding dictionaries to the AWG Waveformlist
          """
          pulse = numpy.zeros(self.numberOfPoints(),dtype = numpy.complex128)
          if waveformName!=None:
            for k in self.pulses.keys():
              self.pulses[k][1]=False
            self.pulses[waveformName][1]=True
          values=self.pulses.values()
          for value in values:
            if value[1]:
              pulse+=value[0]
  
          markers=None                          
          if markersName!= None:
            markers = numpy.zeros(self.numberOfPoints(),dtype=int8)
            if markersName!='All':
              for k in self.markersDict.keys():
                self.markersDict[k][1]=False
              self.markersDict[markersName][1]=True
            values=self.markersDict.values()            
            for value in values:
              if value[1]:
                markers+=value[0]
          if outputName==None:
            outputName=self.name()
          
          self._AWG.listRealWaveform(pulse,markers=markers,waveformName=outputName)

      def startPulse(self, name):
        self.pulses[name][1]=True

      def stopPulse(self, name):
        self.pulses[name][1]=False

      def removeAllPulses(self):
        self.pulses=dict()
        self._params["pulses"]=dict()
        self.sendPulse()

      def gaussianPulse(self,sigma,delay,amplitude=1.):
        """
        Return a gaussian Shape, using length as sigman and delay as time at maximum
        OLD FUNCTION ! DO NOT USE
        """
        def gaussianFunction(t,t0,sigma,amp=1):
          v= amp*numpy.exp(-(t-float(t0))**2/(2*sigma**2))
          return v

        shape=zeros(20000)
        for t in range(int(delay-2*sigma),int(delay+2*sigma)):
            shape[t]=gaussianFunction(t,delay,sigma,amp=amplitude)
        return shape

      def readoutDelay(self):
        return 10000

      def getCorrections(self, frequency, carrierFrequency):
        pass
        #     switch(self.modulationMode){
        #        case "IQMixer":
        #          calibrationParameters=self._mixer.calibrationParameters(f_sb=f_sb, f_c=MWFrequency)
        #          break
        #        case "SimpleMixer":
        #          calibrationParameters=self._mixer.calibrationParameters() # ??????????????????????????????????????
        #          break
        #        case "InternalModulation":
        #          calibrationParameters=None
        #          break
        #        default:
        #          print "generatorFunction called (%s) unknown" %generatorFunction
        #          break            
        #      } # OBSOLETE. Kept for compatibility reasons

      def generateDefaultMarker(self):
        m=numpy.zeros(self.numberOfPoints())
        m[:]=0
        m[self.numberOfPoints()/2:]=1
        return m

      def getMarker(self, index):
        print index, len(self.markersList)
        if len(self.markersList)<index+1:
          return self.generateDefaultMarker()
        else:
          return self.markersList[index]


