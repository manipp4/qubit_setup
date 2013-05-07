from ctypes import *
from numpy import *
import time
import scipy
import sys
import traceback
import scipy.optimize

# Import the high level library

import lib.swig.acqiris_QuantroDLL2.acqiris_QuantroDLL2.acqiris_QuantroDLL2 as acqiris_QuantroDLL2_lib



#***************************************************************************************
#*  BELOW is the post processing by the second quantronics dll Acqiris_QuantroDLL2     *
#*  that contains more sophisticated treatment (demodulation, average,...)             *
#***************************************************************************************

def mybin(x,l = 8):         # utility function for clicks
  s = bin(x)[2:]
  return (l-len(s))*"0"+s    
    
class ModuleDLL2():
  # the acqiris instrument will inherite both from the instrument class and this present class : moduleDLL2
  # creator
  def __init__(self):
    
    print "initialize ModuleDLL2"
    
    self.demodulator=acqiris_QuantroDLL2_lib.Demodulator() 
    self.m = acqiris_QuantroDLL2_lib.MultiplexedBifurcationMap()
    try:   
      self.av = acqiris_QuantroDLL2_lib.Averager()
    except:
      pass
    self.iChannel=0
    self.qChannel=1
    self._nbrIntervalsPerSegment=0
    
    

    
  def setChannels(self,i=0,q=1):
    """
    Set channels to be used in frequencyAnalyse
    """
    self.iChannel=i
    self.qChannel=q
    
  def setDemodulatorCorrections(self, f, offsetI, offsetQ, gainI, gainQ, angleI, angleQ):
    self.demodulator.setCorrections(f,offsetI,offsetQ,gainI,gainQ,angleI,angleQ)
     
    
  def frequenciesAnalyse(self, frequencies,nLoops=1.,intervalMode=-1,maxBit=1,fast=False): 
    """
    Acquire nLoop, demodulate channels previously selected at requested frequencies, rotates and calculate clicks and probabilities
    """

    lenArray =4
    #Acquire
    self.AcquireTransferV4(voltages=True, wantedChannels=15, transferAverage=False, getHorPos=True, getTimeStamps=False,nLoops=nLoops)
    
    #Array for demodulation
    components=zeros((lenArray,2,self.lastWave['nbrSegmentArray'][0]))
    rotatedComponents=zeros((lenArray,2,self.lastWave['nbrSegmentArray'][0]))
    
    #Array for clicks
    clicks=zeros((lenArray,self.lastWave['nbrSegmentArray'][0]))
    
    #Array for probabilities
    probabilities=zeros(lenArray)
    
    results=dict()
    t0=time.time()   
    #Demodulation
    for i in range(0,len(frequencies)):
      if frequencies[i][1]:
        index=frequencies[i][2]
        frequency=frequencies[i][0]
  
        (o1,o2,components[frequencies[i][2],0,:],components[frequencies[i][2],1,:],o3,o4)=self.demodulate2ChIQ(self.lastWave['wave'][self.iChannel],self.lastWave['wave'][self.qChannel],self.lastWave['horPos'],self.lastWave['nbrSegmentArray'][0],int(self.lastWave['nbrSamplesPerSeg']),self.lastWave['samplingTime'], frequency * 1E9,intervalMode=intervalMode)
        
        co=zeros((2,self.lastWave['nbrSegmentArray'][0]))
        co[0,:]=components[frequencies[i][2],0,:]
        co[1,:]=components[frequencies[i][2],1,:]
        (clicks[index,:],cop)=self.multiplexedBifurcationMapAdd(co,frequency) 
        rotatedComponents[frequencies[i][2],0,:]=cop[0,:]
        rotatedComponents[frequencies[i][2],1,:]=cop[1,:]
    
        probabilities[frequencies[i][2]]=mean(clicks[index,:])        
        results['b%i'%frequencies[i][2]]=probabilities[frequencies[i][2]]      
      
        nJBA=maxBit+1
        proba=zeros(2**nJBA)
        nbSegments=self.lastWave['nbrSegmentArray'][0]
    for i in range(0,nbSegments):
      value=0
      for b in range(0,maxBit+1):
        value+=2**b*clicks[b,i]
      proba[value]+=1./nbSegments
    probasInDict=dict()
    for v in range(0,2**nJBA):
      probasInDict['p%s'%mybin(v,nJBA)]=proba[v]
    if fast:
      return (results,probasInDict)
    else:
      return (components,results,rotatedComponents,clicks,probasInDict)
    
  def demodulate1ChIQ(self,ChA,horPos,nbrSegments,nbrSamplesPerSegment,samplingTime, frequency,phase=0,intervalMode=-1,tryCorrect=False,averageOnly=False):
    """
    Performs a digital demodulation of a single channel ChA (I) at a given frequency f by direct multiplication of I by cos(2 pi f t+ phase) and sin(2 pi f t+ phase), and returns the two quadratures I and Q. This function operates on one segment or a sequence of several segments and demodulates over one or several sub-intervals of a segment.
    INPUT parameters:
    - ChA: pointer to the array in which the first quadrature (I) is stored (channel A)
    - nbrSegments: number of segments stored in ChA
    - nbrSamplesPerSegment: number of samples in each segment
    - samplingTime: time interval between two consecutive samples of a segment (in any units provided it is inverse from the frequency unit)
    - frequency: demodulation frequency (in any units provided it is inverse from the samplingTime unit)
    - phase: phase reference at the time of the first sample. Enters the (omega t + phase) argument of the cos and sin multiplicators
    - intervalMode: interval code used for demodulation:
      * intervalMode>0 means intervalMode half-periods if possible (otherwise try case below)
      * 0 means 1 interval with length equal to the maximum integer number of half-periods in the segment length (otherwise do case below)
      * -1 means 1 interval with full segment length (allways possible
    - tryCorrec: boolean telling wether gain, offset and IQ rotation corrections at the given frequency are to be performed (if present in memory)
    - averageOnly: boolean telling wether I and Q for all segments are to be returned (false) or only the average over all segments is to be returned (true).
    OUTPUT parameters
    - nbrIntervalsPerSegment: number of demodulation intervals per segment
    - arrayI,arrayQ: arrays of the nbrSegments*nbrIntervalsPerSegment I and Q quadratures when averageOnly is false (otherwise the two arrays are left empty)
    - arrayMeanI,arrayMeanQ: arrays of the nbrIntervalsPerSegment I and Q values averaged over the nbrSegments segments
    - P_Time_us: pointer to the evaluation duration of the function in microsecond
    """
  
    time=c_double(0.)
  
    
    nbrIntervalsPerSegment = c_int(self._nbrIntervalsPerSegment)
    
    self.defineOutputDemodulationArrays(nbrSegments,nbrSamplesPerSegment,samplingTime, frequency,intervalMode,averageOnly)
    self.demodulator.demodulate1ChIQ(ChA.ctypes.data,horPos.ctypes.data ,
                                    nbrSegments, 
                                    nbrSamplesPerSegment,
                                    samplingTime,
                                    frequency,
                                    phase,
                                    intervalMode,
                                    tryCorrect,
                                    averageOnly,
                                    addressof(nbrIntervalsPerSegment),
                                    self.array1.ctypes.data,
                                    self.array2.ctypes.data,
                                    self.arrayMean1.ctypes.data,
                                    self.arrayMean2.ctypes.data,
                                    addressof(time)
                                    )
  
    self._nbrIntervalsPerSegment = nbrIntervalsPerSegment.value
    
    return (nbrSegments,self._nbrIntervalsPerSegment,self.array1,self.array2,self.arrayMean1,self.arrayMean2,time)
    
  def demodulate2ChIQ(self,ChA,ChB,horPos,nbrSegments,nbrSamplesPerSegment,samplingTime, frequency,phase=0,intervalMode=-1,tryCorrect=False,averageOnly=False):
    """
    Performs a digital demodulation of two quadrature channels ChA and ChB at a given frequency f by direct multiplication of I and Q by cos(2 pi f t+ phase), and returns the two quadratures I and Q. This function operates on one segment or a sequence of several segments and demodulates over one or several sub-intervals of a segment.
    INPUT parameters:
    - ChA: pointer to the array in which the first quadrature (I) is stored (channel A)
    - nbrSegments: number of segments stored in ChA
    - nbrSamplesPerSegment: number of samples in each segment
    - samplingTime: time interval between two consecutive samples of a segment (in any units provided it is inverse from the frequency unit)
    - frequency: demodulation frequency (in any units provided it is inverse from the samplingTime unit)
    - phase: phase reference at the time of the first sample. Enters the (omega t + phase) argument of the cos and sin multiplicators
    - intervalMode: interval code used for demodulation:
      * intervalMode>0 means intervalMode half-periods if possible (otherwise try case below)
      * 0 means 1 interval with length equal to the maximum integer number of half-periods in the segment length (otherwise do case below)
      * -1 means 1 interval with full segment length (allways possible
    - tryCorrec: boolean telling wether gain, offset and IQ rotation corrections at the given frequency are to be performed (if present in memory)
    - averageOnly: boolean telling wether I and Q for all segments are to be returned (false) or only the average over all segments is to be returned (true).
    OUTPUT parameters
    - nbrIntervalsPerSegment: number of demodulation intervals per segment
    - arrayI,arrayQ: arrays of the nbrSegments*nbrIntervalsPerSegment I and Q quadratures when averageOnly is false (otherwise the two arrays are left empty)
    - arrayMeanI,arrayMeanQ: arrays of the nbrIntervalsPerSegment I and Q values averaged over the nbrSegments segments
    - P_Time_us: pointer to the evaluation duration of the function in microsecond
    """
  
    time=c_double(0.)
  
    nbrIntervalsPerSegment = c_int(self._nbrIntervalsPerSegment)
    nbrSegments=int(nbrSegments)
    self.defineOutputDemodulationArrays(nbrSegments,nbrSamplesPerSegment,samplingTime, frequency,intervalMode,averageOnly)
    self.demodulator.demodulate2ChIQ(
                  ChA.ctypes.data,
                  ChB.ctypes.data,  horPos.ctypes.data,
                  nbrSegments, 
                  nbrSamplesPerSegment,
                  samplingTime,
                  frequency,
                  phase,
                  intervalMode,
                  tryCorrect,
                  averageOnly,
                  addressof(nbrIntervalsPerSegment),
                  self.array1.ctypes.data,
                  self.array2.ctypes.data,
                  self.arrayMean1.ctypes.data,
                  self.arrayMean2.ctypes.data,
                  addressof(time))
                  
    self._nbrIntervalsPerSegment = nbrIntervalsPerSegment.value
  
    return (nbrSegments,self._nbrIntervalsPerSegment,self.array1,self.array2,self.arrayMean1,self.arrayMean2)
    
  def multiplexedBifurcationMapAdd(self,co,f):
    try:
      del self.r
    except AttributeError:
      pass
    self.r=zeros((len(co[0])))
    self.m.rotateAndClicks(f, co.ctypes.data, len(co[0]), self.r.ctypes.data)
    return (self.r, co)
    
  def multiplexedBifurcationMapSetRotation(self,f,Io,Qo,r):
      self.m.setRotation(f,Io,Qo,r)

  def defineOutputDemodulationArrays(self,nbrSegments,nbrSamplesPerSegment,samplingTime, frequency,intervalMode=-1,averageOnly=False):
    
    if frequency!=0:
      nbrSamplesPerHalfPeriod=1/(2*samplingTime*frequency) 
    else: 
      nbrSamplesPerHalfPeriod=1 
  
    if(intervalMode>0):
      nbrSamplesPerInterval=(int)(nbrSamplesPerHalfPeriod*abs(intervalMode))
      self._nbrIntervalsPerSegment=math.floor(nbrSamplesPerSegment/nbrSamplesPerInterval)
      
    if(intervalMode==0):
      self._nbrIntervalsPerSegment = 1
      nbrSamplesPerInterval=(int)(nbrSamplesPerHalfPeriod*(int)(nbrSamplesPerSegment/nbrSamplesPerHalfPeriod)+0.5)
      
    if(intervalMode==-1):
      self._nbrIntervalsPerSegment = 1
      nbrSamplesPerInterval=nbrSamplesPerSegment
      
    #print "nbrSegments : %i, nbrSamplesPerSegment : %i, nbrIntervalsPerSegment : %i, dim(array1) :  %i, dim(arrayMean1) :  %i" % (nbrSegments,nbrSamplesPerSegment,self._nbrIntervalsPerSegment,nbrSegments*self._nbrIntervalsPerSegment,self._nbrIntervalsPerSegment)
    if averageOnly:
      self.array1=zeros((1), dtype= float64)
      self.array2=zeros((1), dtype= float64)
    else:
      self.array1=zeros((nbrSegments*self._nbrIntervalsPerSegment), dtype= float64)
      self.array2=zeros((nbrSegments*self._nbrIntervalsPerSegment), dtype= float64)
    self.arrayMean1=zeros((self._nbrIntervalsPerSegment), dtype= float64)
    self.arrayMean2=zeros((self._nbrIntervalsPerSegment), dtype= float64)
  
  

























    
    
    
    
    
    
    
    
    
    
    
class ModuleDLL2_OLD:
  # creator
  def __init__(self):
  
    # The python SWIG to C++ interface of the DLL "acqiris_QuantroDLL2.dll" is loaded
  
    self.demodulator=acqiris_QuantroDLL2_lib.Demodulator() 
    self.m = acqiris_QuantroDLL2_lib.MultiplexedBifurcationMap()
    try:   
      self.av = acqiris_QuantroDLL2_lib.Averager()
      self.av.activeChannels = 15
    except:
      pass
  
    def mybin(x,l = 8):         # utility function for clicks
    	s = bin(x)[2:]
    	return (l-len(s))*"0"+s    
      
    #We initialize the C++ BifurcationMap class with the pointers of the numpy arrays that we created to store the bifurcation map data.
    self._params=dict()
    self._params["rotation"] = [0,0] 
    self._params['nFrequencies']=10
    self._nbrIntervalsPerSegment = 0
    self.bm = acqiris_QuantroDLL2_lib.BifurcationMap()
    self.bm.activeChannels = 15
  
    self.nLoops = self._params['nLoops']
    self.bm.nLoops = self.nLoops
    self._trends = zeros((4,self._params["numberOfSegments"]*self.nLoops))
    self.bm.trends = self._trends.ctypes.data

    self._probabilities = zeros((2,1))
    self._crossProbabilities = zeros((2,2))
    self.bm.crossProbabilities = self._crossProbabilities.ctypes.data
    self.bm.probabilities = self._probabilities.ctypes.data
  
    self._means = zeros((4,1))
    self.bm.means = self._means.ctypes.data
  
    self._averages = zeros((4,self._params["numberOfPoints"]))
    self.bm.averages = self._averages.ctypes.data
  
    self.bm.nPoints = self._params["numberOfPoints"]
    self.bm.nSegments = self._params["numberOfSegments"]
    
  #We initialize the C++ Frequencies analysis with the pointers of the numpy arrays that we created to store the frequencies analysis map data.

  def probabilities(self):
    return self._probabilities
    
  def clicks(self):
    """
    Returns a datacube that contains the individual detector clicks for all measured samples in binary form.
    """  
    clicks = Datacube("detector clicks",dtype = uint8)
    angles = self.bifurcationMapRotation()
    clicks1 = self.trends()[0]*cos(angles[0])+self.trends()[1]*sin(angles[0]) > 0
    clicks2 = self.trends()[2]*cos(angles[1])+self.trends()[3]*sin(angles[1]) > 0
    def mapper(t):
      (x1,x2) = t
      if x1 and x2:
        return 3
      elif x1 and not x2:
        return 1
      elif x2 and not x1:
        return 2
      else:
        return 0    
    clicks.createColumn("clicks",map(mapper,zip(clicks1,clicks2)))
    return clicks
    
  def averages(self):
    """
    Returns the averaged channel data, as generated by e.g. bifurcationMap
    """
    return self._averages
    
  def trends(self):
    """
    Returns the trend data as generated by bifurcationMap.        
    """
    return self._trends
    
  def means(self):
    """
    Returns the means data as generated by bifurcationMap.
    """
    return self._means
    
  def bifurcationMapRotation(self):
    return self._params["rotation"]
    
  def setBifurcationMapRotation(self,channel,angle):
    """
    Adjusts the rotation parameters used in the bifurcationMap routine.
    """
    print "Setting rotation of channel %d to %f" % (channel,angle)
    self._params["rotation"][channel] = angle
    
  def Psw(self):
    """
    Returns the switching probabilities as generated by bifurcationMap.
    """
    return {"p1x" : self._probabilities[0,0],"px1" : self._probabilities[1,0],"p00" : self._crossProbabilities[0,0],"p01" : self._crossProbabilities[0,1],"p10" : self._crossProbabilities[1,0],"p11" : self._crossProbabilities[1,1]}
            
  def bifurcationMap(self,acquireargs = [0],dmaargs = [True,False],ntimes = 20, calculateAverages = True,calculateMeans = True,calculateTrends = True,rotateChannels = True):
    """
    Analyzes the bifurcation behaviour of the JBA.
    """
    self.bm.setRotation(self._params["rotation"][0],self._params["rotation"][1])
    
    if self._rotatedWaveformArray == None:
      self._waveformArray = zeros((4,self._params["numberOfPoints"] *self._params["numberOfSegments"]))
  
    self.bm.rotatedWaveform = self._rotatedWaveformArray.ctypes.data
    
    if ntimes != self.nLoops:
      self.nLoops = ntimes
      self.bm.nLoops = self.nLoops
      self._trends = zeros((4,self._params["numberOfSegments"]*self.nLoops))
      self.bm.trends = self._trends.ctypes.data
  
    self._trends[:,:] = 0
    self._means[:,:] = 0
    self._probabilities[:,:] = 0
    self._crossProbabilities[:,:] = 0
    self._averages[:,:] = 0
  
    self.bm.init()
    
    for i in range(0,self.nLoops):
      self.AcquireV1(*acquireargs)
      self.DMATransferV1(*dmaargs)
      self.bm.add(self._waveformArray.ctypes.data)
  
    self.bm.finish()
            
    self.notify("average",None)
    
  def waveformArray(self):
    return self._waveformArray
    
  def averagedWaveformArray(self):
    return self._averagedWaveformArray
  
  def setNLoops(self,n):
    self.nLoops=n
  
  def getNLoops(self):
    return self.nLoops
  
  def frequenciesAnalyse(self, frequencies,nLoops=None): 
    if nLoops==None:
      nLoops=self.nLoops 
    t1=time.clock()
    # Acquire
    totWf=zeros((4,nLoops*self._params["numberOfSegments"]*self._params["numberOfPoints"]))
    k=0
    #########
  #        for j in range(0,self.nLoops):  
  #          self.AcquireV1(0)
  #          (status,wf,nbrSegments,nbrSamplesPerSegment)=self.DMATransferV1()
  #          for i in [0,1,2,3]:
  #            totWf[i,k:k+nbrSegments[i]*nbrSamplesPerSegment[i]]=wf[i,:]
  #          k+=nbrSegments[0]*nbrSamplesPerSegment[0]
  #        for j in range(0,nbrSegments[0]):
  #          c[1,:]+=totWf[0,nbrSamplesPerSegment[0]*j:nbrSamplesPerSegment[0]*(j+1)]
  #          c[0,:]+=totWf[1,nbrSamplesPerSegment[0]*j:nbrSamplesPerSegment[0]*(j+1)]
    
    ###########
    (totWf,horPos)=self.AcquireTransferV4(nLoops=nLoops)
    nbrSegments=len(horPos)
    nbrSamplesPerSegment=len(totWf[0])/nbrSegments
    
    samplingTime=self._params['sampleInterval']*1e9
  #        nbrSamplesPerSegment=int(nbrSamplesPerSegment[0])
  #        nbrSegments=len(totWf[0])/nbrSamplesPerSegment
    components=zeros((max(len(frequencies),4),2,nbrSegments))
    rotatedComponents=zeros((max(len(frequencies),4),2,nbrSegments))
    clicks=zeros((len(frequencies),nbrSegments))
    probabilities=zeros((max(len(frequencies),4)))
    results=dict()
    #frequencies.sort(key=lambda x:x[2])
    horPos=horPos*1e9
    for i in range(0,len(frequencies)):
      # loop over all frequencies
      frequency=frequencies[i][0]
  #          print frequency
      (o1,o2,components[frequencies[i][2],0,:],components[frequencies[i][2],1,:],o3,o4)=self.demodulate2ChIQ(totWf[0],totWf[1],horPos,nbrSegments,nbrSamplesPerSegment,samplingTime, frequency)
  #          print samplingTime
  #          for j in range(0,nbrSegments):
  #            components[i,0,j]=mean(cos(2*math.pi*frequency*samplingTime*arange(0,nbrSamplesPerSegment))*totWf[0,nbrSamplesPerSegment*j:nbrSamplesPerSegment*(j+1)])
  #            components[i,1,j]=mean(cos(2*math.pi*frequency*samplingTime*arange(0,nbrSamplesPerSegment))*totWf[1,nbrSamplesPerSegment*j:nbrSamplesPerSegment*(j+1)])
      co=zeros((2,len(components[0,0])))
      co[0,:]=components[frequencies[i][2],0,:]
      co[1,:]=components[frequencies[i][2],1,:]
      (clicks[i,:],cop)=self.multiplexedBifurcationMapAdd(co,frequency)
      rotatedComponents[frequencies[i][2],0,:]=cop[0,:]
      rotatedComponents[frequencies[i][2],1,:]=cop[1,:]
  
      probabilities[frequencies[i][2]]=mean(clicks[i,:])        
      results['b%i'%frequencies[i][2]]=probabilities[frequencies[i][2]]
      return (components,results,rotatedComponents)
   
    # Rotate
  
    # converting into Clicks
    
    # convert into probabilities       
    return 0 
    for l in range(0,len(totArray1)):
      pass
    return (transpose)

