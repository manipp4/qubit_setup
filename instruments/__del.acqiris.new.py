import sys                              # comments by AD
import getopt

from ctypes import *
from numpy import *
import time

import math
import os.path

from pyview.lib.classes import *
from pyview.lib.datacube import Datacube

___TEST___ = False

class Instr(Instrument):
      """
      The instrument class for the Acqiris fast acquisition card.
      """      
      def initialize(self, *args, **kwargs):
        self.initializeOscillo(self,*args,**kwargs)  
        self.initializePostProcess(self,*args,**kwargs)  
        return True
      
      def saveState(self,name):
        return self._params
        
      def restoreState(self,state):
        self.ConfigureAllInOneV4(**state)
      
      def parameters(self):
        """
        Returns the parameters of the Acqiris card.
        """
        return self._params
        
      def updateParameters(self,notify=True,*args,**kwargs):
        """
        Updates the parameter dictionary of the Acqiris card.
        """

        for key in kwargs.keys():
          self._params[key] = kwargs[key]     
        if notify:
          self.notify('parameters',value=self._params)
            
      def setParameter(self,arg,value):
        """
        set the parameter dictionary of the Acqiris card.
        """
        self._params[arg] = value       
                  
###############################################################
#                                                             #
#     Basics oscilloscope functions and link to frontPannel   #
#                                                             #
###############################################################

      def initializeOscillo(self,*args,**kwargs): 
        """
        Initializes the Acqiris virtual instruments and the Acqiris board.
        """
        
        #Acqiris parameters in a dictionary. Default parameters initialisation:
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
        
        # parameters below contain feedback parameters from configure and acquire functions
        self.nbPtNomMax=self._params["numberOfPoints"] # maximum number of points per segment indicated by the configure functions
        self.dataArraySize=0;         # total size of the array needed to store 1 channel-full sequence with the last settings (in sample units i.e 64 bit reals )
        self.timeArraySize=0;         # total size of the array needed to store the starting times of each segment
        

        #We load  the C++ library "Acqiris_QuantroDLL1.dll"  that contains the basic oscilloscope functions.
        if ___TEST___:
          None
        else:
           if hasattr(self,"__acqiris") is False:
             try:
               self.__acqiris = windll.LoadLibrary(os.path.dirname(os.path.abspath(__file__))+'/Acqiris_QuantroDLL1.dll')
               self.__acqiris.FindDevicesV1(byref(self.__instrumentID),byref(self.__temperature))
             except ImportError:
               print "Cannot load DLL Acqiris_QuantroDLL1.dll!"
               print sys.exc_info()
               return False
        
        self.__instrumentID = c_uint32()
        self.__temperature = c_int32()
        self.__time_us = c_double()
        
        self._waveformArray = zeros((4,1))
        self._averages = zeros((4,1))
        
        self.ConfigureAllInOneV4() #preconfigure the acquisition board

      def FinishApplicationV1(self,*args):
        """
        Call FinishApplicationV1 in DLL1 to close the client session.
        """
        self.__acqiris.FinishApplicationV1(self.__instrumentID)

      def TemperatureV1(self,*args):
        """
        Returns the temperature of the Acqiris card.
        """
        print args[0]['foo']
        if ___TEST___:
          self.__temperature.value=random.randint(0,100)
        else:
           self.__acqiris.TemperatureV1(self.__instrumentID,byref(self.__temperature))
        #We send out a notification that the temperature variable has changed.
        self.notify("temperature",self.__temperature.value)
        return self.__temperature.value
 
      def CalibrateV1(self,*args):  
        """
        Calibrates the Acqiris card.
        """
        #Some numerical parameters:
        CAL_TOUT = 0
        CAL_VOIE_COURANTE	= 1
        CAL_RAPIDE = 4
        options = c_int32(CAL_TOUT)
        channels = c_int32(args[0])
        status=self.__acqiris.CalibrateV1(self.__instrumentID,options,channels)        
        if status != 0:
          raise Exception(self.transformErr2Str(status))
          
      def transformErr2Str(self,*args):
        error_code = c_int32(args[0])
        error_str = create_string_buffer("\000"*1024)
        status = self.__acqiris.transformErr2Str(self.__instrumentID,error_code,error_str)        
        return str(error_str)
        
      def ConfigureAllInOneV4(self,*args,**kwargs):
        """
        Configures the Acqiris card with a new set of parameters that have to be passed as keyword arguments.
        """     
        self.updateParameters(*args,**kwargs) # from GUI to self._params dictionary
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
        fs1=c_double(self._params["fullScales"][0])
        fs2=c_double(self._params["fullScales"][1])
        fs3=c_double(self._params["fullScales"][2])
        fs4=c_double(self._params["fullScales"][3])
        o1=c_double(self._params["offsets"][0])
        o2=c_double(self._params["offsets"][1])
        o3=c_double(self._params["offsets"][2])
        o4=c_double(self._params["offsets"][3])
        c1=c_double(self._params["couplings"][0])
        c2=c_double(self._params["couplings"][1])
        c3=c_double(self._params["couplings"][2])
        c4=c_double(self._params["couplings"][3])
        b1=c_double(self._params["bandwidths"][0])
        b2=c_double(self._params["bandwidths"][1])
        b3=c_double(self._params["bandwidths"][2])
        b4=c_double(self._params["bandwidths"][3])
        c_time_us = c_double(0.0)
        
        nbPtNomMax=c_int32(self.nbPtNomMax)
        dataArraySize=c_int32(self.dataArraySize)
        timeArraySize=c_int32(self.timeArraySize);
  
        #We call the ConfigureAllInOneV4 DLL function that configures all the acquisition parameters
        status = self.__acqiris.ConfigureAllInOneV4(self.__instrumentID
        ,byref(sync)
        ,byref(used_channels),byref(converters_per_channel)
        ,byref(mem)
        ,byref(sample_interval),byref(number_of_points),byref(number_of_segments),byref(numberOfBanks)
        ,byref(trig),byref(trig_coupling),byref(trig_slope),byref(trig_level1),byref(trig_level2),byref(trig_delay)
        ,byref(configMode)
        ,byref(nbPtNomMax),byref(dataArraySize),byref(timeArraySize)
        ,byref(fs1) ,byref(o1) ,byref(c1) ,byref(b1)
        ,byref(fs2) ,byref(o2) ,byref(c2) ,byref(b2)
        ,byref(fs3) ,byref(o3) ,byref(c3) ,byref(b3)
        ,byref(fs4) ,byref(o4) ,byref(c4) ,byref(b4)
        ,byref(c_time_us)
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
        self._params["fullScales"][0]=fs1.value
        self._params["fullScales"][1]=fs2.value
        self._params["fullScales"][2]=fs3.value
        self._params["fullScales"][3]=fs4.value
        self._params["offsets"][0]=o1.value
        self._params["offsets"][1]=o2.value
        self._params["offsets"][2]=o3.value
        self._params["offsets"][3]=o4.value
        self._params["couplings"][0]=c1.value
        self._params["couplings"][1]=c2.value
        self._params["couplings"][2]=c3.value
        self._params["couplings"][3]=c4.value
        self._params["bandwidths"][0]=b1.value
        self._params["bandwidths"][1]=b2.value
        self._params["bandwidths"][2]=b3.value
        self._params["bandwidths"][3]=b4.value
        self.nbPtNomMax=nbPtNomMax.value
        self.dataArraySize=dataArraySize.value
        self.timeArraySize=timeArraySize.value
        
        # create or recreate all structures written by the DLL  
        self.wfAve = zeros((4,self._params["numberOfPoints"]))
        self.totalArraySizesAve[:]=[self._params["numberOfPoints"]]*4
        
        size=self._params["numberOfSegments"]*self._params['nLoops']
        self.horPosArraySize=myType(size,dtype=int32)
        self.horPosArray=zeros(size,dtype=float64)

        timeStampsArraySize=myType(size,dtype=int32)
        timeStampsArray=zeros(size,dtype=int64)
        
        if self._params["transferAverage"] == False:
          size= self._params["numberOfPoints"] * self._params["numberOfSegments"]*self._params['nLoops']
          self.wf = zeros((4,size))
          self.totalArraySizes[:]=[size]*4 

      def AcquireTransferV4(self, voltages=True, wantedChannels=15, getHorPos=True, getTimeStamps=False,nLoops=1.):
        
        timeOut=100
        
        requestedLoopsOrBanks=myType(self._params["nLoops"],dtype=int32)
        voltages=c_bool(voltages)
        wantedChannels=myType(wantedChannels,dtype=int32)
        #totalArraySizes=zeros(4,dtype=int32)
         
        samplingTime=myType(0,float64)
        nbrSamplesPerSeg=zeros(4,dtype=int32)
        nbrSegments=myType(0,dtype=int32)
        nbrSegmentsArray=zeros(4,dtype=int32) 
  
        maxDelayBetweenTrigs_us=myType(100,dtype=float64)
        time_us=myType(0,float64)
	
        if self._params['transferAverage']:
          wf0=self.wfAve[0,:].ctypes.data
          wf1=self.wfAve[1,:].ctypes.data
          wf2=self.wfAve[2,:].ctypes.data
          wf3=self.wfAve[3,:].ctypes.data
        else:
          wf0=self.wf[0,:].ctypes.data
          wf1=self.wf[1,:].ctypes.data
          wf2=self.wf[2,:].ctypes.data
          wf3=self.wf[3,:].ctypes.data
	       
        status=self.__acqiris.AcquireTransferV4(self.__instrumentID, 
                      c_int(timeOut),
                      requestedLoopsOrBanks.adress(),
                      c_bool(voltages),
                      wantedChannels.adress(),
                      c_bool(self._params['transferAverage']),
                      totalArraySizes.ctypes.data,
                      wf0, 
                      wf1, 
                      wf2, 
                      wf3,	
                      samplingTime.adress(),
                      nbrSamplesPerSeg.ctypes.data,
                      nbrSegments.adress(),
                      nbrSegmentsArray.ctypes.data,	
                      c_bool(True),
                      self.horPosArraySize.adress(), 
                      self.horPosArray.ctypes.data,	
                      c_bool(True),
                      timeStampsArraySize.adress(), 
                      timeStampsArray.ctypes.data,	
                      maxDelayBetweenTrigs_us.adress(),	
                      time_us.adress(),
                      c_bool(True)
                      )
        return self.wf,self.horPosArray
               
###############################################################
#                                                             #
#     Post Processing                                         #
#                                                             #
###############################################################
      
      #We import the C++/SWIG part of the Acqiris library, i.e. the python interface to the DLL "acqiris_QuantroDLL2.dll"
      import lib.swig.acqiris_QuantroDLL2.acqiris_QuantroDLL2.acqiris_QuantroDLL2 as acqirislib            

      def initializePostProcess(self, *args, **kwargs):
        self._nbrIntervalsPerSegment = 0 
        self.demodulator=acqirislib.Demodulator() 
        self.m = acqirislib.MultiplexedBifurcationMap()
        try:   
          self.av = acqirislib.Averager()
          self.av.activeChannels = 15
        except:
          pass     
        return self._params    
  
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
          
      def frequenciesAnalysis(self,frequencies):
        """
        DEPRECATED
        """  
        (totArray1,totArray2)=([],[])
        for j in range(0,self.nLoops):  
          nbrSegments=self._params['numberOfSegments']
          nbrSamplesPerSegment=self._params["numberOfPoints"]
          samplingTime=self._params['sampleInterval']*1E9        
          self.AcquireV1(0)
          status=self.DMATransferV1()        
          for frequency in frequencies:
            (nbrSegments,_nbrIntervalsPerSegment,array1,array2,arrayMean1,arrayMean2)=self.demodulate2ChIQ(self.wf[0,:],self.wf[1,:],nbrSegments,nbrSamplesPerSegment,samplingTime, frequency)
          totArray1.extend(array1)
          totArray2.extend(array2)
        return transpose([totArray1,totArray2]) 
         
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
          
      def all(self, frequency):        
        try:
          del self.wf
        except AttributeError:
          pass
        nbrSegments=self._params['numberOfSegments']
        nbrSamplesPerSegment=self._params["numberOfPoints"]
        samplingTime=self._params['sampleInterval']*1E9        
        self.AcquireV1(0) 
        self.DMATransferV1()        
        #(nbrSegments,_nbrIntervalsPerSegment,self.array1,self.array2,self.arrayMean1,self.arrayMean2)=self.demodulate2ChIQ(self.wf[0,:],self.wf[1,:],nbrSegments,nbrSamplesPerSegment,samplingTime, frequency)
        #self.co= transpose([self.array1,self.array2]) 
        #self.r=zeros((len(self.co)))
        #self.m.add(frequency, self.co.ctypes.data, len(self.co), self.r.ctypes.data)
        #return mean(self.r)
        
      def multiplexedBifurcationMapSetRotation(self,f,Io,Qo,r):
          self.m.setRotation(f,Io,Qo,r)
          
      def convertToProbabilities(self,r):
        return mean(r)
#        nbQB=1 ##### len(r[0]) is not working
##        ro=zeros((nbQB,len(r)))
#        probabilitiesDatas=zeros((2**nbQB))
#        self.m.convertToProbabilities(nbQB,len(r),ro.ctypes.data,probabilitiesDatas.ctypes.data)
#        proba=dict()
#        for i in range(0,nbQB):
#          proba['p%s' % mybin(i)]=probabilitiesDatas[i]       
#        return proba




      def setCorrections(self, f, offsetI, offsetQ, gainI, gainQ, angleI, angleQ):
        self.demodulator.setCorrections(f,offsetI,offsetQ,gainI,gainQ,angleI,angleQ)
      
      def defineOutputDemodulationArrays(self,nbrSegments,nbrSamplesPerSegment,samplingTime, frequency,intervalMode=-1,averageOnly=False):
        
        if frequency!=0:nbrSamplesPerHalfPeriod=1/(2*samplingTime*frequency)
      
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
        self.defineOutputDemodulationArrays(nbrSegments,nbrSamplesPerSegment,samplingTime, frequency,intervalMode,averageOnly)
        self.demodulator.demodulate2ChIQ(
                      ChA.ctypes.data,
                      ChB.ctypes.data,  horPos.ctypes.data     ,
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


               
###############################################################
#                                                             #
#     Utilities                                               #
#                                                             #
###############################################################


    



def mybin(x,l = 8):
	s = bin(x)[2:]
	return (l-len(s))*"0"+s

class myType:
  def __init__(self,i,dtype=float64): 
    self._value=zeros(1,dtype=dtype)
    self._value[0]=i
  def adress(self):
    return self._value.ctypes.data
  def value(self):
    return self._value[0]
	        
        
        
        