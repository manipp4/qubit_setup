from pyview.helpers.instrumentsmanager import Manager
acqiris=Manager().getInstrument('acqiris34')
from ctypes import *
from numpy import *
##
acqiris.reinit()
acqiris.createDictAndGlobals()    
acqiris.getInitialConfig()
##
print acqiris._params()
##
acqiris.AcquireTransfer(wantedChannels=1)
##
print acqiris("lastWaveIdentifier")
print acqiris("lastSamplingTime")
print acqiris("lastTransferredChannel")
print acqiris("lastTransferAverage")
print acqiris("lastNbrSegmentsArray")
print acqiris("lastNbrSamplesPerSeg")
print acqiris("lastWaveformArraySizes")
print acqiris("lastWaveformArray")
print acqiris("lastTimeStampsArraySize")
print acqiris("lastTimeStampsArray")
print acqiris("lastHorPositionsArraySize")
print acqiris("lastHorPositionsArray")

##
print acqiris.getLastWave()
##
a=zeros(3,dtype=float64)
b=ones(3,dtype=float64)
c=1
arr=[a,b,c]
#print arr
#arr[1]=[104,105,106]
print arr
print arr[1]
print arr[1].ctypes.data