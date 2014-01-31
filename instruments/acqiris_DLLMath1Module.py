from ctypes import *
from numpy import *
import time
import scipy
import sys
import traceback
import scipy.optimize
import os

#*******************************************************************************
#*  BELOW is the post-processing of acquired traces by the mathematical dll 
#* Acqiris_QuantroDLLMath1, which is based on the GSL library
# (see dll functions syntax below)                  
#*******************************************************************************
    
class DLLMath1Module():

  def __init__(self,acqirisInstr): # creator
    """
    Load the 'acqiris_QuantroDLLMath1.dll' DLL and make it an attribute of the DLLMath1Module object  .
    """
    self.acqirisInstr=acqirisInstr # define the acqiris instrument as an attribute of the module 
                                   # so that the module can access all the acqiris attributes.  
    try:
      print "\nLoading GSL based Mathematical DLL 'acqiris_QuantroDLLMath1.dll'"
      self._dll= windll.LoadLibrary(os.path.dirname(os.path.abspath(__file__))+'/acqiris_QuantroDLLMath1.dll')     
      #test with C function WINAPI mathDLLVersion
      print "acqiris_QuantroDLLMath1 version is %s"%self.mathDLLVersion()
    except :
      print "Cannot load DLL 'acqiris_QuantroDLLMath1.dll'"
      raise
    
    self.segmentProperties=[
      "minOfLastWaveForms",
      "maxOfLastWaveForms",
      "meanOfLastWaveForms",
      "boxcarOfLastWaveForms",
      "varianceOfLastWaveForms",
      "sdevOfLastWaveForms"]
     
    
    self.minArray=[None]*4
    self._dll.minArray.restype=c_double
    self.minArrayLastID=[-1,-1,-1,-1]
    
    self.maxArray=[None]*4
    self._dll.maxArray.restype=c_double
    self.maxArrayLastID=[-1,-1,-1,-1]
    
    self.mean=[None]*4
    self._dll.mean.restype=c_double
    self.meanLastID=[-1,-1,-1,-1]
    
    
    self.boxcarSlice=[None]*4
    self.boxcarMean=[None]*4
    self._dll.boxCar.restype=c_double
    self.boxcarLastID=[-1,-1,-1,-1]
    
    self.variance=[None]*4
    self._dll.variance.restype=c_double
    self.varianceLastID=[-1,-1,-1,-1]
    
    self.sdev=[None]*4
    self._dll.sdev.restype=c_double
    self.sdevLastID=[-1,-1,-1,-1]
    
    self.cov=None
    self._dll.cov.restype=c_double
    
    self.covMatrix=None   # None or 1D numpy array  of size 4 times the number of segments
                          # [ Seg1_var1,  Seg1_cov12, Seg1_cov12, Seg1_var2,
                          #   Seg2_var1,  Seg2_cov12, Seg2_cov12, Seg2_var2,
                          #   ...]
    
    self.eigenVal=None    # None or 1D numpy array of size 2 times the number of segments
                          # [ Seg1_Val1,  Seg1_Val2,
                          #   Seg2_Val1,  Seg2_Val2,
                          #   ...]
    
    self.eigenVec=None    # None or 1D numpy array of size 4 times the number of segments
                          # [ Seg1_Vec1_X,  Seg1_Vec1_Y, Seg1_Vec2_X,  Seg1_Vec2_Y,
                          #   Seg2_Vec1_X,  Seg2_Vec1_Y, Seg2_Vec2_X,  Seg2_Vec2_Y,
                          #   ...]
    
    self.aboveThresholdFrequencyArray=[None]*4
    self._dll.aboveThresholdFrequency.restype=c_double
    
    self.histoArray=[None]*4
      
  def mathDLLVersion(self):
    """
    Returns the version of the DLL.
    """
    versionString=c_char_p("          ")
    self._dll.mathDLLVersion(versionString)
    return versionString.value
  
  def mathDLLHelp(self,functionName=""):
    """
    Fill the passed string helpString of length helpStringLength with a help text on function functionName if it exists or on all function if functionName="".
    """
    helpString= create_string_buffer(1000)
    self._dll.mathDLLHelp(functionName,helpString,sizeof(helpString))
    return helpString.value
    
  def _propertyOfLastWaveForms(self,dllAndArrayName,targettedWaveform=15):
    """
    private generic function being used to compute a real property of type double per segment.
    Can be used for mean, variance, sdev, min, max, boxcar ...
    use dllAndArrayName as the name of the dll and of the array in which results are stored  
    """      
    lastIdentifier=self.acqirisInstr.lastWaveIdentifier
    lastTranferred=self.acqirisInstr.lastWave['transferedChannels']
    lastAveraged=self.acqirisInstr.lastWave['transferAverage']
    nbrSamplesPerSeg=self.acqirisInstr.lastWave['nbrSamplesPerSeg']
    if lastAveraged:
      nbrSegmentArray=[1,1,1,1] 
    else:
      nbrSegmentArray=self.acqirisInstr.lastWave['nbrSegmentArray'] 
    for i in range(4):
      if lastTranferred & targettedWaveform & (1 << i):
        nbrSegment=nbrSegmentArray[i]
        getattr(self,dllAndArrayName)[i]=zeros(nbrSegment)
        for j in range(nbrSegment):
          startAddress=self.acqirisInstr.lastWaveformArray[i][j*nbrSamplesPerSeg:].ctypes.data
          f=getattr(self._dll,dllAndArrayName)
          getattr(self,dllAndArrayName)[i][j]=f(startAddress,c_long(nbrSamplesPerSeg))
        getattr(self,dllAndArrayName+"LastID")[i]=lastIdentifier
      else:
        getattr(self,dllAndArrayName)[i]=None    
    return
    
  def minOfLastWaveForms(self,targettedWaveform=15):
    """
    minOfLastWaveForms(targettedWaveform):
    Finds the minima of the targetted lastly acquired waveforms (for each segment).
    TargettedWaveform encodes the waveforms to be processed (provided they were acquired at the last acquisition)
    TargettedWaveform is the Sum(an 2^n) for n=0 to 3 the channel number and an=1 for targetted channels and zero otherwise 
    Stores the results in the 4 element python array min.
    """
    self._propertyOfLastWaveForms(dllAndArrayName='minArray',targettedWaveform=targettedWaveform)
    return
  
  def maxOfLastWaveForms(self,targettedWaveform=15):
    """
    maxOfLastWaveForms(targettedWaveform):
    Finds the maxima of the targetted lastly acquired waveforms (for each segment).
    TargettedWaveform encodes the waveforms to be processed (provided they were acquired at the last acquisition)
    TargettedWaveform is the Sum(an 2^n) for n=0 to 3 the channel number and an=1 for targetted channels and zero otherwise 
    Stores the results in the 4 element python array max.
    """
    self._propertyOfLastWaveForms(dllAndArrayName='maxArray',targettedWaveform=targettedWaveform)
    return
  
  def meanOfLastWaveForms(self,targettedWaveform=15):
    """
    meanOfLastWaveForms(targettedWaveform):
    Computes the means of the targetted lastly acquired waveforms (for each segment).
    TargettedWaveform encodes the waveforms to be processed (provided they  have been acquired at the last acquisition)
    TargettedWaveform is the Sum(an 2^n) for n=0 to 3 the channel number and an=1 for targetted channels and zero otherwise 
    Stores the results in the 4 element python array mean.
    """
    self._propertyOfLastWaveForms(dllAndArrayName='mean',targettedWaveform=targettedWaveform)
    return
  
  def boxcarOfLastWaveForms(self,targettedWaveform=15,sliceArray=[slice(0,-1,1)]*4):
    """
    boxcarOfLastWaveForms(targettedWaveform):
    Computes the boxecar means of the targetted lastly acquired waveforms (for each segment).
    TargettedWaveform encodes the waveforms to be processed (provided they have been acquired at the last acquisition)
    TargettedWaveform is the Sum(an 2^n) for n=0 to 3 the channel number and an=1 for targetted channels and zero otherwise 
    Stores the results in the 4 element python array boxcarMean.
    """
    lastTranferred=self.acqirisInstr.lastWave['transferedChannels']
    targettedWaveform=lastTranferred & targettedWaveform
    lastAveraged=self.acqirisInstr.lastWave['transferAverage']
    nbrSamplesPerSeg=self.acqirisInstr.lastWave['nbrSamplesPerSeg']
    if lastAveraged:
      nbrSegmentArray=[1,1,1,1] 
    else:
      nbrSegmentArray=self.acqirisInstr.lastWave['nbrSegmentArray'] 
    for i in range(4):
      if  targettedWaveform & (1 << i):
        nbrSegment=nbrSegmentArray[i]
        self.boxcarMean[i]=zeros(nbrSegment)
        start=sliceArray[i].start
        if start<0 : start=nbrSamplesPerSeg+start
        stop=sliceArray[i].stop
        if stop<0 : stop=nbrSamplesPerSeg+stop
        if start>=0 and start <nbrSamplesPerSeg and  stop >=0 and stop <nbrSamplesPerSeg and start<=stop:
          self.boxcarSlice[i]=slice(start,stop,1)
          for j in range(nbrSegment):
            startAddress=self.acqirisInstr.lastWaveformArray[i][j*nbrSamplesPerSeg:].ctypes.data
            self.boxcarMean[i][j]=self._dll.boxCar(startAddress,c_long(start),c_long(stop))
        else:
          self.boxcarSlice[i]=None
          self.boxcarMean[i]=None
      else:
        self.boxcarMean[i]=None
        self.boxcarSlice[i]=None    
    return
  
  def varianceOfLastWaveForms(self,targettedWaveform=15):
    """
    varianceOfLastWaveForms(targettedWaveform):
    Computes the variances of the targetted lastly acquired waveforms (for each segment).
    TargettedWaveform encodes the waveforms to be processed (provided they  have been acquired at the last acquisition)
    TargettedWaveform is the Sum(an 2^n) for n=0 to 3 the channel number and an=1 for targetted channels and zero otherwise 
    Stores the results in the 4 element python array variance.
    """
    self._propertyOfLastWaveForms(dllAndArrayName='variance',targettedWaveform=targettedWaveform)
    return
    
  def sdevOfLastWaveForms(self,targettedWaveform=15):
    """
    sdevOfLastWaveForms(targettedWaveform):
    Computes the unbiased standard deviation of the targetted lastly acquired waveforms (for each segment).
    TargettedWaveform encodes the waveforms to be processed (provided they  have been acquired at the last acquisition)
    TargettedWaveform is the Sum(an 2^n) for n=0 to 3 the channel number and an=1 for targetted channels and zero otherwise 
    Stores the results in the 4 element python array sdev.
    """
    self._propertyOfLastWaveForms(dllAndArrayName='sdev',targettedWaveform=targettedWaveform)
    return
  
  def covarianceTwoWaveforms(self,waveform1=0,waveform2=1):
    """
    covarianceTwoWaveforms(waveform1,waveform2):
    Computes the covariance of two lastly acquired waveforms (for each segment).
    Waveform1 and waveform 2 are the channel number 0,1,2,or 3
    Stores the results in cov.
    """
    lastTranferred=self.acqirisInstr.lastWave['transferedChannels']
    lastAveraged=self.acqirisInstr.lastWave['transferAverage']
    nbrSamplesPerSeg=self.acqirisInstr.lastWave['nbrSamplesPerSeg']
    if lastAveraged:
      nbrSegmentArray=[1,1,1,1] 
    else:
      nbrSegmentArray=self.acqirisInstr.lastWave['nbrSegmentArray']
    sameLength=nbrSegmentArray[waveform1]==nbrSegmentArray[waveform2]
    waveform1Transferred=lastTranferred & (1 << waveform1)
    waveform2Transferred=lastTranferred & (1 << waveform2)
    if sameLength and waveform1Transferred and waveform2Transferred:
      nbrSegment=nbrSegmentArray[waveform1]
      self.cov=zeros(nbrSegment)
      for j in range(nbrSegment):
        startAddress1=self.acqirisInstr.lastWaveformArray[waveform1][j*nbrSamplesPerSeg:].ctypes.data
        startAddress2=self.acqirisInstr.lastWaveformArray[waveform2][j*nbrSamplesPerSeg:].ctypes.data
        self.cov[j]=self._dll.cov(startAddress1,startAddress2,c_long(nbrSamplesPerSeg))
    else:
      self.cov=None    
    return
    
  def covMatrixTwoWaveforms(self,waveform1=0,waveform2=1):
    """
    covMatrixTwoWaveforms(waveform1,waveform2):
    Computes the covariance matrices of two lastly acquired waveforms (for each segment).
    Waveform1 and waveform 2 are the channel number 0,1,2,or 3
    Stores the results in covMatrix.
    """
    lastTranferred=self.acqirisInstr.lastWave['transferedChannels']
    lastAveraged=self.acqirisInstr.lastWave['transferAverage']
    nbrSamplesPerSeg=self.acqirisInstr.lastWave['nbrSamplesPerSeg']
    if lastAveraged:
      nbrSegmentArray=[1,1,1,1] 
    else:
      nbrSegmentArray=self.acqirisInstr.lastWave['nbrSegmentArray']
    sameLength=nbrSegmentArray[waveform1]==nbrSegmentArray[waveform2]
    waveform1Transferred=lastTranferred & (1 << waveform1)
    waveform2Transferred=lastTranferred & (1 << waveform2)
    if sameLength and waveform1Transferred and waveform2Transferred:
      nbrSegment=nbrSegmentArray[waveform1]
      self.covMatrix=zeros(4*nbrSegment)
      for j in range(nbrSegment):
        pointer1=self.acqirisInstr.lastWaveformArray[waveform1][j*nbrSamplesPerSeg:].ctypes.data
        pointer2=self.acqirisInstr.lastWaveformArray[waveform2][j*nbrSamplesPerSeg:].ctypes.data
        pointer3=self.covMatrix[4*j:].ctypes.data
        self._dll.covMatrix2(pointer1,pointer2,c_long(nbrSamplesPerSeg),pointer3)
    else:
      self.covMatrix=None    
    return
  
  def diagCovMatrix(self):
    """
    diagCovMatrix():
    Diagonalize the covariance matrices stored in covMatrix and stores the eigenvalues in eigenVal
    and the eigenvectors in eigenVec.
    """
    if self.covMatrix!=None:
      covMatrixCopy=self.covMatrix  # copy the covariance matrices because the GSL function destroys its source
      print covMatrixCopy
      nbrsegment=len(covMatrixCopy)/4
      self.eigenVal=zeros(2*nbrsegment)
      self.eigenVec=zeros(4*nbrsegment)
      for j in range(nbrsegment):
        covMatPtr=covMatrixCopy[j*4:].ctypes.data
        eigValPtr=self.eigenVal[j*2:].ctypes.data
        eigVecPtr=self.eigenVec[j*4:].ctypes.data
        self._dll.eigenSystemSym(covMatPtr,c_long(4),eigValPtr,eigVecPtr)
    else:
      self.eigenVal=None
      self.eigenVec=None
    return  
    
  def modulusTwoWaveforms(self,targettedWaveform=15):
    """
    modulusTwoWaveforms(targettedWaveform=15):
    Calculate the modulus (xi^2+yi^2)^1/2 using for x and y the first two targetted waveforms if targettedWaveform <  15,
    or using both ch1 and ch2 for modulus 1 and ch3 and ch4 for modulus 2 if targettedWaveform =  15.
    Results are overwritten in the first waveform channel of each pair.
    """
    lastTranferred=self.acqirisInstr.lastWave['transferedChannels']
    targettedWaveform=lastTranferred & targettedWaveform
    lastAveraged=self.acqirisInstr.lastWave['transferAverage']
    waveSizes=self.acqirisInstr.lastWave['waveSizes']
    i=0
    while i<4:
      while (not(targettedWaveform & (1 << i))and i<=4) : i+=1
      waveform1=i
      i+=1
      while (not(targettedWaveform & (1 << i))and i<=4) : i+=1
      if i<4:
        waveform2=i
        pointer1=self.acqirisInstr.lastWaveformArray[waveform1].ctypes.data
        pointer2=self.acqirisInstr.lastWaveformArray[waveform2].ctypes.data
        size1=min(waveSizes[waveform1],waveSizes[waveform2])
        self._dll.modulus(pointer1,pointer2,pointer1,c_long(size1))
      i+=1 
    print "modulusTwoWaveforms() not debugged yet"
    return
  
  def thresholderOfLastWaveForms(self,threshold="auto",targettedWaveform=15):
    """
    thresholderOfLastWaveForms(threshold='auto',targettedWaveform=15):
    Overwrite values of dataArray with 0's or 1's if value is below and strictly above the threshold, respectively
    """
    lastTranferred=self.acqirisInstr.lastWave['transferedChannels']
    targettedWaveform=lastTranferred & targettedWaveform
    lastAveraged=self.acqirisInstr.lastWave['transferAverage']
    waveSizes=self.acqirisInstr.lastWave['waveSizes']
    for i in range(4):
      if targettedWaveform & (1 << i):
        pointer=self.acqirisInstr.lastWaveformArray[waveform1].ctypes.data
        size=c_long(waveSizes[i])
        threshold1=threshold
        if threshold=="auto": threshold1=(self._dll.maxArray(pointer,size)+self._dll.minArray(pointer,size))/2  
        self._dll.thresholder(pointer,pointer,size, c_double(threshold1))
    print "thresholderOfLastWaveForms() not debugged yet"
    return
    
  def histo1DProperty(self,propertyArray='mean',mini="auto",maxi="auto",binNumber=10,targettedWaveform=15):
    """
    histo1DProperty(propertyArray=self.mean,mini='auto',maxi='auto',binNumber=10,targettedWaveform=15):
    Do a 1D histogram of the 1D array propertyArray
    """
    for i in range(4):
      if (targettedWaveform & (1 << i) and getattr(self,propertyArray)[i]!=None):
        pointerData=getattr(self,propertyArray)[i].ctypes.data
        size= c_long(len(getattr(self,propertyArray)[i]))
        min1=mini
        if mini=="auto": min1=self._dll.minArray(pointerData,size)
        max1=maxi
        if maxi=="auto": max1=self._dll.maxArray(pointerData,size)
        if min1>max1 :
          u= max1
          max1=min1
          min1=u
        if mini=="auto": min1=min1-(max1-min1)/binNumber
        if maxi=="auto": max1=max1+(max1-min1)/binNumber
        self.histoArray[i]=zeros(binNumber)
        pointerHisto=self.histoArray[i].ctypes.data  
        self._dll.histo1D(pointerData,size,c_double(min1),c_double(max1),c_ulonglong(binNumber), pointerHisto )
    print "histo1DProperty() not debugged yet"
    return
    
  def thresholderProperty(self,propertyArray=mean,threshold="auto",targettedWaveform=15):
    """
    thresholderProperty(propertyArray=self.mean,threshold='auto',targettedWaveform=15):
    Overwrite values of dataArray with 0's or 1's if value is below and strictly above the threshold, respectively
    """
    for i in range(4):
      if targettedWaveform & (1 << i) and getattr(self,propertyArray)[i]!=None:
        pointer=getattr(self,propertyArray)[i].ctypes.data
        size= c_long(len(getattr(self,propertyArray)[i]))
        threshold1=threshold
        if threshold=="auto": threshold1=(self._dll.maxArray(pointer,size)+self._dll.minArray(pointer,size))/2  
        self._dll.thresholder(pointer,pointer,size, c_double(threshold1))
    return
    
  def aboveThresholdFrequencyProperty(self,propertyArray=mean,threshold="auto",targettedWaveform=15):
    """
    aboveThresholdFrequencyProperty(propertyArray=self.mean,threshold='auto',targettedWaveform=15):
    Overwrite values of dataArray with 0's or 1's if value is below and strictly above the threshold, respectively
    """
    for i in range(4):
      if targettedWaveform & (1 << i) and getattr(self,propertyArray)[i]!=None:
        pointer=getattr(self,propertyArray)[i].ctypes.data
        size= c_long(len(getattr(self,propertyArray)[i]))
        threshold1=threshold
        if threshold=="auto": threshold1=(self._dll.maxArray(pointer,size)+self._dll.minArray(pointer,size))/2
        self.aboveThresholdFrequencyArray[i]=self._dll.aboveThresholdFrequency(pointer,size,c_double(threshold1))
    return
     
     
'''**************************************************************************************
 BELOW IS THE SYNTAX OF THE QUANTRO_DLLMATH1 FUNCTIONS
 
 extern "C" {
	//These functions are built using the GSL mathematical library (see code DLLMath1Functions.cpp)
	
	//return the version string of the DLL
	impExp void	WINAPI mathDLLVersion (char* versionString);
  
  	//Fill the passed string helpString of length helpStringLength with a help text on function functionName if it exists or on all function if functionName=""
	impExp void WINAPI mathDLLHelp (char* functionName,char* helpString,long helpStringLength);    
	
	//mean of a 1D array
	impExp double WINAPI mean(double *array,long length);
	
	//unbiased variance of a 1D array, the mean of which is already known
	impExp double WINAPI variance_m(double *array,long length,double mean);
	
	//unbiased variance of a 1D array
	impExp double WINAPI variance(double *array,long length);
	
	//unbiased standard deviation of a 1D array,the mean of which is already known
	impExp double WINAPI sdev_m(double *array,long length,double mean);
	
	//unbiased standard deviation of a 1D array
	impExp double WINAPI sdev(double *array,long length);
	
	//Boxcar average between two indexes (mean of a subarray). Index of first element is 0.
	impExp double WINAPI boxCar(double *array,long firstIndex, long lastIndex);
	
	//Min of a 1D array.
	impExp double WINAPI minArray(double *array,long length);
	
	//Max of a 1D array.
	impExp double WINAPI maxArray(double *array,long length);
	
	//Covariance of two 1D arrays, the means of which are already known.
	impExp double WINAPI cov_m(double *array1,double *array2,long length,double mean1,double mean2);
	
	//Covariance of two 1D arrays of same length.
	impExp double WINAPI cov(double *array1,double *array2,long length);
	
	// 2x2 covariance matrix of two 1D arrays with the same length.
	impExp void WINAPI covMatrix2(double *array1,double *array2,long length,double covMatrix[2][2]);
	
	// Sorted eigenValues and eigneVectors of a symmetric nxn matrix
	impExp void WINAPI eigenSystemSym(double * array, long n,double* eigenValArray,double* eigenVecArray);

	// Do a 1D histogram of a 1D array
	impExp void WINAPI histo1D(double * dataArray,long lengthArray,double min,double max,size_t binNumber, double * histo );
	
	// Do a 2D histogram of two 1D arrays representing a 2D distribution
	impExp void WINAPI histo2D(double * xArray,double * yArray,long lengthArray,double xmin,double xmax,size_t binNumberX,double ymin,double ymax,size_t binNumberY, double *histo);
	
  // Calculate and store in the modulus array the modulus values (xi^2+yi^2)^1/2 of two 1D arrays xi and yi. All array have same length. Output array can be xi or yi if needed.
	impExp void WINAPI modulus(double * xArray,double * yArray,double * modulus, long lengthArray);
	
	// Calculate and store in the binaryArray array 0's or 1's for xi values below and strictly above the threshold, respectively. All array have same length. Output array can be xi if needed.
	impExp void WINAPI thresholder(double * xArray,double * binaryArray, long lengthArray, double threshold);

	// returns the frequency with which values xi in array xArray are stricly above threshold.
	impExp double  WINAPI aboveThresholdFrequency(double * xArray,  long lengthArray, double threshold);

}'''

