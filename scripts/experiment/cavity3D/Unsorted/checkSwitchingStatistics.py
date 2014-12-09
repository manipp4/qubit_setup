from pyview.lib.datacube import *
from pyview.helpers.datamanager import *
from pyview.helpers.instrumentsmanager import *
instrumentManager=Manager()
dataManager=DataManager()
import math
import numpy
from scipy.optimize import curve_fit

##
acqiris=instrumentManager.getInstrument('acqiris')
cavity_drive=instrumentManager.getInstrument('MWSource_cavity')
qubit_drive=instrumentManager.getInstrument('MWSource_Qubit')
attenuator=instrumentManager.getInstrument('Yoko3')
pulseGenerator=instrumentManager.getInstrument('pg_qb')  

##
def telegraph(x0,x):
	if (x<x0):
		y=0
	else: y=1
	return y

##
def rotate(l,n):
    return l[n:] + l[:n]
##
acqiris.AcquireTransferV4(transferAverage=False,nLoops=80,wantedChannels=3)
acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
chanels= acqiris("DLLMath1Module.mean")
amp=sqrt((chanels[0]-iOff)**2+(chanels[1]-qOff)**2)
events=map(lambda x:telegraph(0.3,x),amp)
l=len(events)
mean1=mean(events)
r1=rotate(events,1)
r2=rotate(r1,1)
events11=[x*y for x,y in zip(events,r1)]
mean11=mean(events11)
p1knowing1=mean11/mean1
events111=[x*y for x,y in zip(events11,r2)]
mean111=mean(events111)
p1knowing11=mean111/mean11
print mean1
print p1knowing1
print p1knowing11
##