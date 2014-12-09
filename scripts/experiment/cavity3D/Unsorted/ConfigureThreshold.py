from pyview.lib.datacube import *
from pyview.helpers.datamanager import *
from pyview.helpers.instrumentsmanager import *
instrumentManager=Manager()
dataManager=DataManager()
import math
import numpy
from scipy.optimize import curve_fit
from matplotlib.pyplot import *

##
acqiris=instrumentManager.getInstrument('acqiris')
cavity_drive=instrumentManager.getInstrument('MWSource_cavity')
qubit_drive=instrumentManager.getInstrument('MWSource_Qubit')
attenuator=instrumentManager.getInstrument('Yoko3')
pulseGenerator=instrumentManager.getInstrument('pg_qb')  
fsp=instrumentManager.getInstrument('fsp')
##
def telegraph(x0,x):
	if (x<x0):
		y=0
	else: y=1
	return y
##
nLoop=2
data=Datacube("Traces0.95")
dataManager.addDatacube(data)

iOff=0
qOff=0
threshold=0.2
acqiris.AcquireTransferV4(transferAverage=False,nLoops=nLoop,wantedChannels=3)
acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
chanels= acqiris("DLLMath1Module.mean")
amp=sqrt((chanels[0]-iOff)**2+(chanels[1]-qOff)**2)
Q=traces[1]
events=map(lambda x:telegraph(threshold,x),Q)
mean0=mean(events)
lastwave=acqiris.lastWave()
traces=lastwave['wave']
data.createColumn("tracesI",traces[0])
data.createColumn("tracesQ",traces[1])
data.commit()
data.savetxt()
################
## PlotTraces ##
################
clf()
fig1=figure()
for i in xrange(0,len(traces[0])/100,1):
	time=range(100)
	I=traces[0][i*100:i*100+100]
	Q=traces[1][i*100:i*100+100]
	amp=sqrt(I**2+Q**2)
	#plot(time,I)
	#plot(time,Q)
	plot(time,Q)
figtext(0.05,0.01,'Q')
show()
###############
## histogram ##
###############
amps=[]
for i in xrange(0,len(traces[0])/100,1):
	time=range(100)
	I=traces[0][i*100+100-1]
	Q=traces[1][i*100+100-1]
	amp=sqrt(I**2+Q**2)
	amps.append(amp)
[hist,bins]=numpy.histogram(amps, arange(0,1,0.01))
bins1=bins[1:]
fig1a=figure()
plot(bins1,hist)
figtext(0.05,0.01,'Q')
show()
##
print hist