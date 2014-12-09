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
fsp=instrumentManager.getInstrument('fsp')

## Noise histogram
data=Datacube('Noise_2')
dataManager.addDatacube(data)
iOff=0
qOff=0
reps=arange(0,1)
power=1.0
attenuator.setVoltage(power)
cavity_drive.setFrequency(7.08282)
for r in reps:
	print"r=%r"%r 
	time.sleep(.2)
	acqiris.AcquireTransferV4(transferAverage=False,nLoops=10,wantedChannels=3)
	acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
	chanels= acqiris("DLLMath1Module.mean")
	amp=sqrt((chanels[0]-iOff)**2+(chanels[1]-qOff)**2)
	data.set(r=r,i=chanels[0],q=chanels[1],amp=amp)
	data.commit()	
data.savetxt() 
##
data=Datacube('Noise_2')
dataManager.addDatacube(data)
iOff=0
qOff=0
freqs=arange(7.07882,7.08882,0.0001)
powers=arange(0,2.01,0.1)
for freq in freqs:
	child0=Datacube("freq=%f"%freq)
	cavity_drive.setFrequency(freq)
	for power in reversed(powers):
		child=Datacube("power=%f"%power)
		attenuator.setVoltage(power)
		acqiris.AcquireTransferV4(transferAverage=False,nLoops=10,wantedChannels=3)
		acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
		chanels= acqiris("DLLMath1Module.mean")
		histo= acqiris("DLLMath1Module.mean")
		amp=sqrt((chanels[0]-iOff)**2+(chanels[1]-qOff)**2)
		#child.setColumn("amp",amp)
		[hist,bins]=numpy.histogram(amp, arange(0,2,0.01))
		child.setColumn("bins",bins)
		child.setColumn("hist",hist/10000.)
		child0.addChild(child)
	data.addChild(child0)
data.savetxt()
##
amp=sqrt((chanels[0]-iOff)**2+(chanels[1]-qOff)**2)
print len(amp);
##
data.setColumn("amp",amp)
##
help(boxcarOfLastWaveForms)

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
################################################
## loop to look at the fluctuations over time ##
################################################
# 100 us interval repetition
repint=100
inds=arange(0,50000,1)
nLoop=1
nseg=1000
data=Datacube("stats5_rep=%f"%repint+"_loop=%f"%nLoop+"_seg=%f"%nseg)
dataManager.addDatacube(data)

iOff=0
qOff=0

for ind in inds:
	acqiris.AcquireTransferV4(transferAverage=False,nLoops=nLoop,wantedChannels=3)
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
	data.set(time=repint*nLoop*nseg*ind/1000000.,p1=mean1,p1knowing1=p1knowing1,p1knowing11=p1knowing11)
	data.commit()
	#data.set(repint=repint,nLoop=nLoop,nseg=nseg)
	#data.commit()
	data.savetxt()          

##########################################################################
## loop to look at the fluctuations over time and moitoring input power ##
##########################################################################
# 100 us interval repetition
repint=100
inds=arange(0,50000,1)
nLoop=1
nseg=1000
data=Datacube("stats1_rep=%f"%repint+"_loop=%f"%nLoop+"_seg=%f"%nseg)
dataManager.addDatacube(data)

iOff=0
qOff=0

for ind in inds:
	#inputpow=fsp.getValueAtMarker()+17.4
	acqiris.AcquireTransferV4(transferAverage=False,nLoops=nLoop,wantedChannels=3)
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
	data.set(time=repint*nLoop*nseg*ind/1000000.,p1=mean1,p1knowing1=p1knowing1,p1knowing11=p1knowing11)
	data.commit()
	#data.set(repint=repint,nLoop=nLoop,nseg=nseg)
	#data.commit()
	data.savetxt()          
##
repint=100
inds=arange(0,50000,1)
nLoop=1
nseg=1000
data=Datacube("Traces")
dataManager.addDatacube(data)

iOff=0
qOff=0

acqiris.AcquireTransferV4(transferAverage=False,nLoops=nLoop,wantedChannels=3)
acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
chanels= acqiris("DLLMath1Module.mean")
amp=sqrt((chanels[0]-iOff)**2+(chanels[1]-qOff)**2)
events=map(lambda x:telegraph(0.3,x),amp)
mean0=mean(events)
lastwave=acqiris.lastWave()
traces=lastwave['wave']
data.createColumn("tracesQ",traces[0])
data.createColumn("tracesI",traces[1])
data.commit()
data.savetxt()
##
tracesI=traces[0]
print tracesI.shape
##
##########################################################################
## Record traces at switching ##
##########################################################################
# 100 us interval repetition
repint=100
inds=arange(0,50000,1)
nLoop=1
nseg=1000
data=Datacube("stats4_rep=%f"%repint+"_loop=%f"%nLoop+"_seg=%f"%nseg)
dataManager.addDatacube(data)

iOff=0
qOff=0

acqiris.AcquireTransferV4(transferAverage=False,nLoops=nLoop,wantedChannels=3)
acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
chanels= acqiris("DLLMath1Module.mean")
amp=sqrt((chanels[0]-iOff)**2+(chanels[1]-qOff)**2)
events=map(lambda x:telegraph(0.3,x),amp)
mean0=mean(events)
lastwave=acqiris.lastWave()
traces0=lastwave['wave']


threshold=0.1
for ind in inds:
	#inputpow=fsp.getValueAtMarker()+17.4
	acqiris.AcquireTransferV4(transferAverage=False,nLoops=nLoop,wantedChannels=3)
	acqiris("DLLMath1Module.meanOfLastWaveForms(3)")
	chanels= acqiris("DLLMath1Module.mean")
	amp=sqrt((chanels[0]-iOff)**2+(chanels[1]-qOff)**2)
	events=map(lambda x:telegraph(0.3,x),amp)
	mean1=mean(events)	
	if abs(mean0-mean1)>threshold:
		print mean1-mean0
		print 'break'
		child0=Datacube("mean=%f"%mean0)
		data.addChild(child0)
		child0.createColumn("traces0I",traces0[0])
		child0.createColumn("traces0Q",traces0[1])
		child0.commit()
		lastwave=acqiris.lastWave()
		traces1=lastwave['wave']
		child1=Datacube("mean=%f"%mean1)
		data.addChild(child1)
		child1.createColumn("traces1I",traces1[0])
		child1.createColumn("traces1Q",traces1[1])
		child1.commit()
		data.set(time=repint*nLoop*nseg*ind/1000000.,p1=mean1)
		data.commit()
		data.savetxt()
		break
	data.set(time=repint*nLoop*nseg*ind/1000000.,p1=mean1)
	data.commit()
	#data.set(repint=repint,nLoop=nLoop,nseg=nseg)
	#data.commit()
	data.savetxt()
##
print len(traces[0])	    
##plot traces##
clf()
fig1=figure()
for i in xrange(0,len(traces[0])/100,1):
	time=range(100)
	I=traces[0][i*100:i*100+100]
	Q=traces[1][i*100:i*100+100]
	amp=sqrt(I**2+Q**2)
	#plot(time,I)
	#plot(time,Q)
	plot(time,amp)
figtext(0.05,0.01,'amp')
show()
##
fig2=figure()
for i in xrange(0,len(traces0[0])/100,1):
	time=range(100)
	I=traces1[0][i*100:i*100+100]
	Q=traces1[1][i*100:i*100+100]
	amp=sqrt(I**2+Q**2)
	#plot(time,I)
	#plot(time,Q)
	plot(time,amp)
figtext(0.05,0.01,'mean=%f')
show()
###############
## histogram ##
###############
amps=[]
for i in xrange(0,len(traces0[0])/100,1):
	time=range(100)
	I=traces0[0][i*100+100-1]
	Q=traces0[1][i*100+100-1]
	amp=sqrt(I**2+Q**2)
	amps.append(amp)
[hist,bins]=numpy.histogram(amps, arange(0,0.6,0.01))
bins1=bins[1:]
fig1a=figure()
plot(bins1,hist)
figtext(0.05,0.01,'mean=%f'%mean0)
show()
##
amps=[]
for i in xrange(0,len(traces0[0])/100,1):
	time=range(100)
	I=traces1[0][i*100+100-1]
	Q=traces1[1][i*100+100-1]
	amp=sqrt(I**2+Q**2)
	amps.append(amp)
[hist,bins]=numpy.histogram(amps, arange(0,1.4,0.01))
bins1=bins[1:]
fig2a=figure()
plot(bins1,hist)
figtext(0.05,0.01,'mean=%f'%mean1)
show()

##
from matplotlib.pyplot import *
##
def sum(a,b):return [i+j for i,j in zip(a,b)]
print sum(time,time)
##
fig1=figure()
plot(time,time)
t=sum(time,time)
plot(time,t)

show()
##
print len(hist)
print len(bins)
print bins

