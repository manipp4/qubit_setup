from pyview.helpers.instrumentsmanager import Manager
from pyview.lib.datacube import Datacube
from pyview.lib.smartloop import SmartLoop
import numpy as np
from numpy import *
from ctypes import *
from numpy import *
import time
import scipy
import sys
import traceback
import scipy.optimize
import ctypes
import os
awg=Manager().getInstrument('awgmw')

##
libHandle = ctypes.windll.kernel32.LoadLibraryA(os.path.dirname(os.path.abspath(__file__))+'/awg.dll')  
dll = ctypes.WinDLL(None, handle=libHandle)
print dll.awgint
###
values=zeros(20000)
markers=None

waveform = numpy.zeros(len(realWaveform))
waveform[:] = numpy.real(realWaveform)
       
if markers == None:
  markers=numpy.zeros(len(waveform),dtype=numpy.int8)
  markers[:10000]=3
  

output = ""

valuesFloat = numpy.zeros(len(values),dtype = numpy.float32)
markersInt = numpy.zeros(len(markers),dtype = numpy.uint8)

valuesFloat[:] = values[:]
markersInt[:] = markers[:] << 6

buf = ctypes.create_string_buffer(len(valuesFloat)*5)
numerical.awg_pack_real_data(len(valuesFloat),valuesFloat.ctypes.data,markersInt.ctypes.data,ctypes.addressof(buf))
return buf.raw





self.createWaveform(waveformName,data,"INT")
self.setWaveform(channel,waveformName)
    

####       
  def writeRealData(self,values,markers,useC=False):
    """
    Writes real-valued data to a string.
    """
    output = ""
    #Fast code that calls a C++ function to encode the data...

    valuesFloat = numpy.zeros(len(values),dtype = numpy.float32)
    markersInt = numpy.zeros(len(markers),dtype = numpy.uint8)

    valuesFloat[:] = values[:]
    markersInt[:] = markers[:] << 6

    buf = ctypes.create_string_buffer(len(valuesFloat)*5)
    if useC:
      numerical.awg_pack_real_data(len(valuesFloat),valuesFloat.ctypes.data,markersInt.ctypes.data,ctypes.addressof(buf))
      return buf.raw
    else:
      for i in range(0,len(values)):
        marker = float(markers[i])
        value = float(values[i])
        output+=struct.pack("<f",((marker & 3) << 14) + (value & (0xFFFF >> 2)))
      return output  
  