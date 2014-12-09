from ctypes import *
from numpy import *
import numpy
import time
import scipy
import sys
import traceback
import scipy.optimize
import ctypes
import os

class DemodTest():

	def __init__(self):
		print self
		try:
			print "loading DLL demodulation"
			print os.path.dirname(os.path.abspath(__file__))+'/macros/demodulation/demodulation/Release/demodulation.dll'
			libHandle2 = ctypes.windll.kernel32.LoadLibraryA(os.path.dirname(os.path.abspath(__file__))+'/macros/demodulation/demodulation/Release/demodulation.dll')  
			self.demodulator = ctypes.WinDLL(None, handle=libHandle2)
			print "DLL demodulation loaded"
			print "Version " , self.demodulator.version()
		except:
			print "Loading DLL demodulation FAILED"
			print "Continue anyway"
			print ""
			raise

d=DemodTest()
##
n=10000
p=3000
size=n*p
ChA=zeros(size,dtype=float64)   
ChA[:]=random.rand(size)   
ChB=zeros(size,dtype=float64)      
ChB[:]=random.rand(size)   
horPos=zeros(n,dtype=float64)
horPos[:]=random.rand(n)*1e-9 
nbrSegments=int(n)
nbrSamplesPerSegment=int(p)
samplingTime=5e-10
frequency=0.12e9
phase=0
intervalMode=-1
tryCorrect=False
corrections=zeros(6,dtype=float64)
averageOnly=False
nbrIntervalsPerSegment=c_int(size)
array1=zeros(n,dtype=float64)
array2=zeros(n,dtype=float64)
arrayMean1=zeros(1,dtype=float64)
arrayMean2=zeros(1,dtype=float64)
ti=c_double(0.)

t=time.time()

d.demodulator.demodulate2ChIQ(
	                  ChA.ctypes.data,
	                  ChB.ctypes.data,
	                  horPos.ctypes.data,
	                  nbrSegments, 
	                  nbrSamplesPerSegment,
	                  c_float(samplingTime),
	                  c_float(frequency),
	                  c_float(phase),
	                  intervalMode,
	                  tryCorrect,
	                  corrections.ctypes.data,
	                  True,
	                  averageOnly,
	                  addressof(nbrIntervalsPerSegment),
	                  array1.ctypes.data,
	                  array2.ctypes.data,
	                  arrayMean1.ctypes.data,
	                  arrayMean2.ctypes.data,
	                  addressof(ti))
	

print time.time()-t
##
print random.rand(2)









