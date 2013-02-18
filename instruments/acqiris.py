import sys
import getopt

from ctypes import *
from numpy import *
import time

import math
import os.path

from pyview.helpers.instrumentsmanager import *
from pyview.lib.classes import *
from pyview.lib.datacube import Datacube
import acqiris_ModuleDLL2


# Import the high level library
import lib.swig.acqiris_QuantroDLL2.acqiris_QuantroDLL2.acqiris_QuantroDLL2 as acqiris_QuantroDLL2_lib

#C++ library "Acqiris_QuantroDLL1.dll" contains the basic oscilloscope functions
# It is loaded below when initializing the acqiris intrument 

___TEST___ = False
___includeModuleDLL2___=True

# utility class for helping in c to python interface
class myType:                        
  def __init__(self,i,dtype=float64): 
    self._value=zeros(1,dtype=dtype)
    self._value[0]=i
  def adress(self):
    return self._value.ctypes.data
  def value(self):
    return self._value[0]

# intrument class for the acquisition board	
class Instr(Instrument,acqiris_ModuleDLL2.ModuleDLL2):
  """
  The instrument class for the Acqiris fast acquisition card.
  """
  #creator function  
  def initialize(self,*args,**kwargs): 
    """
    Initializes the Acqiris virtual instruments and the Acqiris board.
    """
    self.__instrumentID = c_uint32()
    self.__temperature = c_int32()
    self.__time_us = c_double()
    
    # C++ library "Acqiris_QuantroDLL1.dll"  that contains the basic oscilloscope functions is loaded.
    if ___TEST___:
      None
    else:
       if hasattr(self,"__acqiris") is False:
         try:
           self.__acqiris_QuantroDLL1= windll.LoadLibrary(os.path.dirname(os.path.abspath(__file__))+'/Acqiris_QuantroDLL1.dll')
           self.__acqiris_QuantroDLL1.FindDevicesV1(byref(self.__instrumentID),byref(self.__temperature))
           self.__acqiris_QuantroDLL1.TemperatureV1(self.__instrumentID,byref(self.__temperature))
         except ImportError:
           print "Cannot load DLL Acqiris_QuantroDLL1.dll!"
           print sys.exc_info()
           return False
     
    #Acqiris parameters defined in a in a dictionary.
    self._params = dict()
    self._params["synchro"] = True
    self._params["trigSource"] = -1
    self._params["trigCoupling"] = 3
    self._params["trigLevel1"] = 500        #in mV
    self._params["trigLevel2"] = 600        #in mV
    self._params["trigSlope"] = 0           
    self._params["trigDelay"] = 700e-9
    self._params["memType"] = 1
    self._params["configMode"]=0;           # flag modifier: 0=normal, 1=Start on trigger, 2=Wrap mode, 10=SAR mode
    self._params["convertersPerChannel"] = 1
    self._params["fullScales"] = [5.0] * 4
    self._params["offsets"] = [0.0] * 4
    self._params["couplings"] = [3] * 4
    self._params["bandwidths"] = [3] * 4
    self._params["usedChannels"] = 15
    self._params["sampleInterval"] = 5e-10  # in seconds
    self._params["numberOfPoints"] = 400
    self._params["numberOfSegments"] = 10   # per bank
    self._params["numberOfBanks"]=1         # in acqiris board memory
    
    self._params['nLoops']=1                # actually number of acquisition or of banks in SAR mode
    self._params["transferAverage"]=False   # transfer average only
    
    # Parameters of the last acquired sequence defiend below as global variables 
    self.lastWaveIdentifier=0
    self.lastTransferredChannel=0					  # code of transferred channels
    self.lastTransferAverage=False
    self.lastWaveformArraySizes=zeros(4,dtype=int32)	# number of samples in each waveform channels
    self.lastWaveformArray = zeros((4,1))		# waveform (full sequence) array
    self.lastSamplingTime=0						      # last sampling period
    self.lastNbrSamplesPerSeg=0					    # number of samples per segment in the  last waveforms returned
    self.lastNbrSegmentsArray=zeros(4,dtype=int32)# number of segments actually returned for each channel in the last transfer
    self.lastHorPositionsArraySize=0
    self.lastHorPositionsArray=zeros(1,dtype=float64)
    self.lastTimeStampsArraySize=0;         # total size time stamp array in the last transfer
    self.lastTimeStampsArray=zeros(1,dtype=float64)		# total size time stamp array in the last transfer
                   
    # and also saved in a dictionary lastWave
    self.lastWave=dict()
    self.lastWave['identifier']=self.lastWaveIdentifier
    self.lastWave['samplingTime']=self.lastSamplingTime
    self.lastWave['transferedChannels']=self.lastTransferredChannel
    self.lastWave['transferAverage']=self.lastTransferAverage
    self.lastWave['nbrSegmentArray']=self.lastNbrSegmentsArray
    self.lastWave['nbrSamplesPerSeg']=self.lastNbrSamplesPerSeg
    self.lastWave['waveSizes']=self.lastWaveformArraySizes
    self.lastWave['wave']=self.lastWaveformArray
    self.lastWave['timeStampsSize']=self.lastTimeStampsArraySize
    self.lastWave['timeStamps']=self.lastTimeStampsArray
    self.lastWave['horPosSize']=self.lastHorPositionsArraySize
    self.lastWave['horPos']=self.lastHorPositionsArray
    
    self.ConfigureAllInOne()  #preconfigure the acquisition board


    if ___includeModuleDLL2___ : acqiris_ModuleDLL2.ModuleDLL2.__init__(self)

  def transformErr2Str(self,*args):
    error_code = c_int32(args[0])
    error_str = create_string_buffer("\000"*1024)
    status = self.__acqiris_QuantroDLL1.transformErr2Str(self.__instrumentID,error_code,error_str)        
    return str(error_str)
    
  def saveState(self,name):
    return self._params
    
  def restoreState(self,state):
    self._params=state
    self.ConfigureAllInOne()
    
  def parameters(self):
    """
    Returns the parameters of the Acqiris card.
    """
    return self._params
    
  def updateParameters(self,*args,**kwargs):
    """
    Updates the parameter dictionary of the Acqiris card.
    """
    for key in kwargs.keys():
      self._params[key] = kwargs[key]     
        
  def setParameter(self,arg,value):
    """
    set the parameter dictionary of the Acqiris card.
    """
    self._params[arg] = value
    
  # calibrate function
  CAL_FULL=0               # full calibration code
  CAL_CURRENT_CONFIG=1     # calibrate current configuration code
  CAL_FAST=4               # calibrate specified channels  
  def CalibrateV1(self,option=CAL_FAST,channels=15):
    """
    Calibrates the Acqiris card.
    """ 
    status=self.__acqiris_QuantroDLL1.CalibrateV1(self.__instrumentID,option,channels)        
    if status != 0:
      raise Exception(self.transformErr2Str(status))
  
  # configure function
  def ConfigureAllInOne(self,*args,**kwargs):
    """
    Configures the Acqiris card with a new set of parameters that have to be passed as keyword arguments.
    """
    self.updateParameters(*args,**kwargs)
    #We create ctypes objects for all the parameters to be passed to acqiris_QuantroDLL1.DLL's functions :
    sync=c_bool(self._params["synchro"])
    trig = c_int32(self._params["trigSource"])
    trig_coupling = c_int32(self._params["trigCoupling"])
    trig_slope = c_int32(self._params["trigSlope"])
    trig_level1 = c_double(self._params["trigLevel1"])
    trig_level2 = c_double(self._params["trigLevel2"])
    trig_delay = c_double(self._params["trigDelay"])
    mem = c_int32(int(self._params["memType"]))
    configMode=c_int32(int(self._params["configMode"]))
    converters_per_channel=c_int32(self._params["convertersPerChannel"])
    used_channels = c_int32(self._params["usedChannels"])
    sample_interval = c_double(self._params["sampleInterval"])
    number_of_points = c_int32(self._params["numberOfPoints"])
    number_of_segments = c_int32(self._params["numberOfSegments"])
    numberOfBanks = c_int32(self._params["numberOfBanks"])
    fs=zeros(4,dtype=float64)
    fs[0]=self._params["fullScales"][0]
    fs[1]=self._params["fullScales"][1]
    fs[2]=self._params["fullScales"][2]
    fs[3]=self._params["fullScales"][3]
    
    of=zeros(4,dtype=float64)                
    of[0]=float(self._params["offsets"][0])
    of[1]=self._params["offsets"][1]
    of[2]=self._params["offsets"][2]
    of[3]=self._params["offsets"][3]
    
    cs=zeros(4,dtype=int32);                   
    cs[0]=self._params["couplings"][0]
    cs[1]=self._params["couplings"][1]
    cs[2]=self._params["couplings"][2]
    cs[3]=self._params["couplings"][3]
    
    bs=zeros(4,dtype=int32);
    bs[0]=self._params["bandwidths"][0]
    bs[1]=self._params["bandwidths"][1]
    bs[2]=self._params["bandwidths"][2]
    bs[3]=self._params["bandwidths"][3] 
    
    time_us=myType(0,float64) 
    
    nbPtNomMax=c_int32(100000)
    dataArraySize=c_int32(0)
    timeArraySize=c_int32(0)
    #We call the ConfigureAllInOne DLL function that configures all the acquisition parameters
    status = self.__acqiris_QuantroDLL1.ConfigureAllInOne(
      self.__instrumentID
      ,byref(sync)
      ,byref(used_channels)
      ,byref(converters_per_channel)
      ,byref(mem)
      ,byref(sample_interval)
      ,byref(number_of_points)
      ,byref(number_of_segments)
      ,byref(numberOfBanks)
      ,byref(trig)
      ,byref(trig_coupling)
      ,byref(trig_slope)
      ,byref(trig_level1)
      ,byref(trig_level2)
      ,byref(trig_delay)
      ,byref(configMode)
      ,byref(nbPtNomMax)
      ,byref(dataArraySize)
      ,byref(timeArraySize)
      ,fs.ctypes.data 
      ,of.ctypes.data 
      ,cs.ctypes.data 
      ,bs.ctypes.data
      ,time_us.adress()
      )      
    self.transformErr2Str(status)
    #Then we update all the parameters              
    self._params["trigSource"]=trig.value
    self._params["trigCoupling"]=trig_coupling.value
    self._params["trigSlope"]=trig_slope.value
    self._params["trigDelay"]= trig_delay.value
    self._params["convertersPerChannel"]= converters_per_channel.value
    self._params["usedChannels"]=used_channels.value
    self._params["sampleInterval"]=sample_interval.value
    self._params["numberOfPoints"]=number_of_points.value
    self._params["numberOfSegments"]=number_of_segments.value
    self._params["numberOfBanks"]=numberOfBanks.value
    self._params["fullScales"][0]=fs[0] #fs1.value
    self._params["fullScales"][1]=fs[1]
    self._params["fullScales"][2]=fs[2]
    self._params["fullScales"][3]=fs[3]
    self._params["offsets"][0]=of[0] #o1.value
    self._params["offsets"][1]=of[1]
    self._params["offsets"][2]=of[2]
    self._params["offsets"][3]=of[3]
    self._params["couplings"][0]=cs[0]#c1.value
    self._params["couplings"][1]=cs[1]
    self._params["couplings"][2]=cs[2]
    self._params["couplings"][3]=cs[3]
    self._params["bandwidths"][0]=bs[0]#b1.value
    self._params["bandwidths"][1]=bs[1]
    self._params["bandwidths"][2]=bs[2]
    self._params["bandwidths"][3]=bs[3]
    self.nbPtNomMax=nbPtNomMax.value
    self.dataArraySize=dataArraySize.value    # this is the data array size required for a raw data transfer
    self.timeArraySize=timeArraySize.value    # this is the time array size required for timestamps and horPositions
    # memory is now reserved in the aquire and transfer function since nloops can be changed in the interface
    #    without going through the present configure function     
    return status
 
  def ConfigureChannel(self,channel,fullscale = None,offset = None,coupling = None,bandwidth = None):
    """
    Configures one single channel of the Acqiris card.
    """
    channel-=1
    if fullscale != None:
      self._params["fullScales"][channel] = float(fullscale)
    if offset != None:
      self._params["offsets"][channel] = float(offset)
    if coupling != None:
      self._params["couplings"][channel] = int(coupling)
    if bandwidth != None:
      self._params["bandwidths"][channel] = int(bandwidth)
    fullScalesC = c_double(self._params["fullScales"][channel])
    offsetC=c_double(self._params["offsets"][channel])
    couplingC=c_int32(self._params["couplings"][channel])
    bandwidthC=c_int32(self._params["bandwidths"][channel])
    status = self.__acqiris_QuantroDLL1. ConfigureChannel(self.__instrumentID, c_int32(channel+1), byref(fullScalesC), byref(offsetC), byref(couplingC), byref(bandwidthC));
    self._params["fullScales"][channel]=fullScalesC.value
    self._params["offsets"][channel]=offsetC.value
    self._params["couplings"][channel]=couplingC.value
    self._params["bandwidths"][channel]=bandwidthC.value
    self.transformErr2Str(status)
 
  # acquisition and transfer function
  def AcquireTransferV4(self, voltages=True, wantedChannels=15, transferAverage=False, getHorPos=True, getTimeStamps=True,nLoops=1.):
    self.nLoops=nLoops
    # prepare all the parameters for calling DLL function AcquireTransferV4
    timeOut=10
    requestedLoopsOrBanks=myType(nLoops,dtype=int32)
    wantedChannels=myType(wantedChannels,dtype=int32)
    totalArraySizes=zeros(4,dtype=int32)
    transferAverages=zeros(4,dtype=bool)
    transferAverages[:]=[transferAverage]*4
    # We reserve the required size 
    if transferAverage == False:  # that will contain the transferred vertical data if no averaging
      size=int(self._params["numberOfPoints"] * self._params["numberOfSegments"]*self.nLoops)
    else:                         # that will contain the transferred vertical data if averaging
      size=int(self._params["numberOfPoints"])
    print size
    self.lastWaveformArray=zeros((4,size),dtype=float64)
      
    self.lastWaveformArraySizes=zeros(4,dtype=int32)
    self.lastWaveformArraySizes[:]=[size]*4                
     
    #number_of_segments = c_int32(self._params["numberOfSegments"])
    samplingTime=myType(0,float64)
    nbrSamplesPerSeg=myType(0,dtype=int32)
    nbrSegments=myType(0,dtype=int32)
    nbrSegmentsArray=zeros(4,dtype=int32) 
        
    if getHorPos: # reserve the required size for horizontal positions of the successive triggers
      horPosArraySize=myType(self._params["numberOfSegments"]*self.nLoops,dtype=int32)
      self.lastHorPositionsArray=zeros(self._params["numberOfSegments"]*self.nLoops,dtype=float64)
    else:
      horPosArraySize=myType(0,dtype=int32)
      self.horPosArray=zeros(1,dtype=float64)
    
    if getTimeStamps: # reserve the required size for timestamps of the successive triggers
      timeStampsArraySize=myType(self._params["numberOfSegments"]*self.nLoops,dtype=int32)
      self.lastTimeStampsArray=zeros(self._params["numberOfSegments"]*self.nLoops,dtype=float64) # float64 in the last version
    else:
      timeStampsArraySize=myType(0,dtype=int32)
      self.lastTimeStampsArray=zeros(1,dtype=float64)
    
    maxDelayBetweenTrigs_s=myType(100,dtype=float64)
    time_s=myType(0,float64)      
 
    status=self.__acqiris_QuantroDLL1.AcquireTransferV4(		#calling DLL function AcquireTransferV4
      self.__instrumentID,    
      c_int(timeOut),
      requestedLoopsOrBanks.adress(),
      c_bool(voltages),
      wantedChannels.adress(),
      #c_bool(transferAverage),
      transferAverages.ctypes.data,    
      self.lastWaveformArraySizes.ctypes.data,
      self.lastWaveformArray[0].ctypes.data, 
      self.lastWaveformArray[1].ctypes.data, 
      self.lastWaveformArray[2].ctypes.data, 
      self.lastWaveformArray[3].ctypes.data,	
      samplingTime.adress(),
      nbrSamplesPerSeg.adress(),
      nbrSegments.adress(),
      self.lastNbrSegmentsArray.ctypes.data,	
      c_bool(getHorPos),
      horPosArraySize.adress(), 
      self.lastHorPositionsArray.ctypes.data,	
      c_bool(getTimeStamps),
      timeStampsArraySize.adress(), 
      self.lastTimeStampsArray.ctypes.data,	
      maxDelayBetweenTrigs_s.adress(),	
      time_s.adress()
      )
    # update of class parameters from returned c values when needed
    self.lastTransferredChannel=wantedChannels.value()
    self.lastTransferAverage=transferAverage
    self.lastSamplingTime=samplingTime.value()
    
    self.lastNbrSamplesPerSeg=nbrSamplesPerSeg.value()
    self.lastTimeStampsArraySize=timeStampsArraySize.value()
    self.lastHorPositionsArraySize=horPosArraySize.value()
    self.lastTransferredChannel=wantedChannels.value()
    self.lastWaveIdentifier+=1
    
    self.lastWave['identifier']=self.lastWaveIdentifier
    self.lastWave['samplingTime']=self.lastSamplingTime
    self.lastWave['transferedChannels']=self.lastTransferredChannel
    self.lastWave['transferAverage']=self.lastTransferAverage
    self.lastWave['nbrSegmentArray']=self.lastNbrSegmentsArray
    self.lastWave['nbrSamplesPerSeg']=self.lastNbrSamplesPerSeg
    self.lastWave['waveSizes']=self.lastWaveformArraySizes
    self.lastWave['wave']=self.lastWaveformArray
    self.lastWave['timeStampsSize']=self.lastTimeStampsArraySize
    self.lastWave['timeStamps']=self.lastTimeStampsArray
    self.lastWave['horPosSize']=self.lastHorPositionsArraySize
    self.lastWave['horPos']=self.lastHorPositionsArray
    return   

  def AcquireV1(self,pre_acquisition = 0,timeOut=10000):
    """
    Triggers an acquisition sequence of the Acqiris card and wait for end of acquisition or timeOut(in milliseconds)
    """
    c_pre_acquisition = c_int32(pre_acquisition)
    c_timeOut=c_int32(timeOut)
    status=self.__acqiris_QuantroDLL1.AcquireV1(self.__instrumentID,c_pre_acquisition,byref(self.__time_us),c_timeOut) 
    return (status,self.__time_us)      
    if status != 0:
      raise Exception(self.transformErr2Str(status))
    return (status,self.__time_us)

  def DMATransferV1(self,voltage = True,getTimeStamps = False,transferAverage = False, *args):        
    """
    Transfers the data from the Acqiris card 
    """     
    if transferAverage == False:
      self.wf = zeros((4,self._params["numberOfPoints"] * self._params["numberOfSegments"]))
    else:
      self.wf = zeros((4,self._params["numberOfPoints"]))  
    c_converters_per_channel= c_int32(self._params["convertersPerChannel"]) # not used yet
    c_used_channels = c_int32(self._params["usedChannels"]) 
    c_voltage = c_bool(bool(voltage))
    c_get_timestamps = c_bool(bool(getTimeStamps))
    c_transferAverageType = c_bool * 4
    c_transferAverageArray = c_transferAverageType(*[transferAverage]*4)
    number_of_segments = c_int32(self._params["numberOfSegments"])
    number_of_samples_per_segment = c_int32(self._params["numberOfPoints"])
    number_of_segments_array = zeros(4,dtype = int32)
    number_of_segments_array[:] = self._params["numberOfSegments"]
    number_of_samples_per_segment_array = zeros(4,dtype = int32)
    number_of_samples_per_segment_array[:] = self._params["numberOfPoints"]
    sampling_intervals = zeros(4,dtype = float64)
    sampling_intervals[:] = self._params["sampleInterval"]
    time_stamps_1 = c_double()
    time_stamps_2 = c_double()
    time_stamps_3 = c_double()
    time_stamps_4 = c_double()        
    c_time_stamp = c_double()
    c_time_us = c_double()
    status=self.__acqiris_QuantroDLL1.DMATransferV1(
      self.__instrumentID,
      # number of converters per channel to be added here
      c_used_channels,
      number_of_segments,
      number_of_samples_per_segment,
      c_voltage,
      c_get_timestamps,
      c_transferAverageArray,
      number_of_segments_array.ctypes.data,
      number_of_samples_per_segment_array.ctypes.data,
      self.wf[0,:].ctypes.data,self.wf[1,:].ctypes.data,self.wf[2,:].ctypes.data,self.wf[3,:].ctypes.data,
      sampling_intervals.ctypes.data,
      byref(time_stamps_1),byref(time_stamps_2),byref(time_stamps_3),byref(time_stamps_4),
      byref(c_time_us)
      )
    return (status,self.wf,number_of_segments_array,number_of_samples_per_segment_array)     
    import numpy
    if status != 0:
      raise Exception(self.transformErr2Str(status))
    else:
      #print number_segments_returned
      self.notify("data",(list(self.waveform_1),list(self.waveform_2),list(self.waveform_3),list(self.waveform_4)))

  def getLastWaveIdentifier(self): 
    return self.lastWaveIdentifier

  def FinishApplicationV1(self,*args):
    self.__acqiris_QuantroDLL1.FinishApplicationV1(self.__instrumentID)
  
  def TemperatureV1(self,*args):
    """
    Returns the temperature of the Acqiris card.
    """
    print args[0]['foo']
    if ___TEST___:
      self.__temperature.value=random.randint(0,100)
    else:
       self.__acqiris_QuantroDLL1.TemperatureV1(self.__instrumentID,byref(self.__temperature))
    #We send out a notification that the temperature variable has changed.
    self.notify("temperature",self.__temperature.value)
    return self.__temperature.value       
        
