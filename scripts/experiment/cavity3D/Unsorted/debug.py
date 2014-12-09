## init
from pyview.lib.datacube import *
from pyview.helpers.datamanager import *
from pyview.helpers.instrumentsmanager import *
instrumentManager=Manager()
dataManager=DataManager()
import math
import numpy
from matplotlib.pyplot import *

acqiris=instrumentManager.getInstrument('acqiris')

i=0
## tests
print acqiris("DLLMath1Module.mathDLLHelp('minOfLastWaveForms')")


## acquisition and fast processing directly in acqiris pc
i+=1
data=Datacube('acq'+str(i))
dataManager.addDatacube(data)
##
def switchingProb(nSegments=1000,channel=1,threshold="auto"):
	wantedChannel=2**(channel-1)
	segmentsPerAcq=acqiris("_params['numberOfSegments']")
	nLoops=nSegments/segmentsPerAcq
	acqiris.AcquireTransferV4(transferAverage=False,nLoops=nLoops,wantedChannels=wantedChannel)
	acqiris("DLLMath1Module.meanOfLastWaveForms("+str(wantedChannel)+")")
	acqiris("DLLMath1Module.aboveThresholdFrequencyProperty(propertyArray='mean',targettedWaveform="+str(wantedChannel)+",threshold="+str(threshold)+")")
	return acqiris("DLLMath1Module.aboveThresholdFrequencyArray["+str(channel-1)+"]")

##
print switchingProb(channel=2,nSegments=10000,threshold=0.2)
##
chanels= acqiris("DLLMath1Module.mean")
[hist,bins]=numpy.histogram(chanels[wantedChannels-1], arange(0,1,0.01))
bins1=bins[1:]
fig1a=figure()
plot(bins1,hist)
figtext(0.05,0.01,'Q')
show()





