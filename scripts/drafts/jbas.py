from config.instruments import *
import numpy
from pyview.helpers.instrumentsmanager import Manager
import scipy
from pyview.helpers.datamanager import DataManager
dataManager = DataManager()
##
instrumentManager=Manager()
##
pg=instrumentManager.getInstrument('Pg_JBA')
print pg
##
print pg.pulses
##
jba=instrumentManager.getInstrument('jba_qb1')
print jba
##
jba.calibrate()

##
jba.stopJBA()
##
print jba._pulseGenerator.pulses
##
#print 
f=jba._pulseAnalyser._frequencies.values()
##
qb=instrumentManager.getInstrument('qubit1')
awgflux=instrumentManager.getInstrument('awgflux')
data=Datacube()
dataManager.addDatacube(data)
for v in arange(-0.5,0.5,0.1):
	for i in [1,2,3,4]:
		awgflux.setOffset(i,v)
	t=qb.measureSpectroscopy(fstart=9.4,fstop=9.9,fstep=0.002,power=0.,name=str(v))
	print t
	data.addChild(t)
	data.savetxt()
##

##
awgflux.setOffset(4,0)


t=jba._pulseAnalyser._acqiris.frequenciesAnalyse(f)
print t
##
data=Datacube()
dataManager.addDatacube()

##
cla()
plot(range(0,len(t[0])),t[0])
draw()
show()
##
r=fft(t[0])
print r
cla()
plot(range(0,len(r)),r)
draw()
show()
##
print len(t[0])
print len(t
##
from numpy import *
from matplotlib.pyplot import *
from pyview.lib.datacube import *
##
figure('f2')
cla()
while True:
	c=jba.getComponents()
	plot(c[0],c[1],'o')
	draw()
	show()
	time.sleep(0.1)
##
c=jba.getComponents()
##
##
cla()
plot(range(0,2000),c)
plot(range(0,2000),cos(2*math.pi*0.2*arange(0,2000)))
#plot(range(0,2000),c*cos(2*math.pi*0.2*arange(0,2000)))
draw()
show()
##
p=0
for i in range(0,2000):
	p+=c[i]*cos(2*math.pi*0.2*i)/2000
print p
##

print mean(c*cos(2*math.pi*0.2*arange(0,2000)))

##
jba._magnitudeButton='variableAttenuator'
##
data=Datacube()
dataManager.addDatacube(data)
for f in arange(6.7,6.9,0.001):
	jba.setFrequency(f)
	jba.sendWaveform()
	time.sleep(1)
	c=jba.getComponents()
	i=mean(c[0])
	q=mean(c[1])
	p=i**2+q**2
	data.set(f=f,p=p,i=i,q=q)
	data.commit()

##

iq=instrumentManager.getInstrument('iqmixer_jba')
print iq
##
awg=instrumentManager.getInstrument('awgmw')
print awg
##
awg.saveSetup("test")

##
print dir(iq)
##
iq.calibrate(f_sb=0.3)
##1
for fj in f:
	print fj



a=[[2,5],[1,8],[4,2],[11,11]]
##
a.sort(key=lambda x:x[0])
print a