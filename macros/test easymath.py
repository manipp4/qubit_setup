import ctypes
import os
import random
print "L:\lab_control\python\qubit_setup\macros\demodulation\demodulation\Release\demodulation.dll"
libHandle = ctypes.windll.kernel32.LoadLibraryA("L:\lab_control\python\qubit_setup\macros\demodulation\demodulation\Release\demodulation.dll")  
dll = ctypes.WinDLL(None, handle=libHandle)


print dll	
print dll.version()

ctypes.dllclose(libHandle)
#######

print easyMath	
print easyMath.version()

from numpy import *
from ctypes import *
l=100
cArray=zeros((2,l),dtype=c_float)
mArray=zeros(4,dtype=c_float)
dim=2
dArray=zeros(l,dtype=c_float)


for i in range(0,l):
	cArray[0,i]=random.randint(0,2)
	cArray[1,i]=random.randint(0,2)
dArray[:]+=cArray[0]+2*cArray[1]
print cArray

print [mean(cArray[0]),mean(cArray[1])]

###
dArray=zeros(l,dtype=c_float)
mArray=zeros(4,dtype=c_float)
easyMath.clicks(cArray.ctypes.data,dArray.ctypes.data, c_int(dim), c_long(l))
easyMath.counter(cArray.ctypes.data,mArray.ctypes.data, c_int(dim), c_long(l))
print dArray
print mArray
print [mean([1 if dArray[i]== j else 0 for i in range(0,l)]) for j in range(0,4)]



