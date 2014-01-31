##2D Spectro
from config.instruments import *
from matplotlib.pyplot import *
#from pyview.gui.mpl.backend import figure
import numpy
import scipy
from pyview.helpers.datamanager import DataManager
dataManager = DataManager()
instrumentManager=Manager()
register=instrumentManager.getInstrument('register')
qb=instrumentManager.getInstrument('qubit2')
awgflux=instrumentManager.getInstrument('awgflux')
print qb, awgflux
##
data=Datacube("qb6.75")
dataManager.addDatacube(data)
for channel in [1,2,3,4]:
	awgflux.setOffset(channel,0)
	awgflux.loadRealWaveform(zeros((20000)), channel=channel,waveformName=str(channel))

for channel in [1,2,3,4]:
		ch=Datacube("flux %i" %channel)
		data.addChild(ch)
		for v in [0]: #arange(-2,2,0.2):
#			awgflux.setOffset(channel,v)
			pulse=zeros((20000))#
			pulse+=-v/2*4000/20000
			pulse[5500:9500]=[v/2]*4000
			awgflux.loadRealWaveform(pulse, channel=channel,waveformName=str(channel))
			time.sleep(1.)
			child=Datacube("V=%f" %v)
			ch.addChild(child)
			acqiris.setNLoops(1)
			qb._jba.calibrate(bounds=[2,4,40],onlyOne=True)
			acqiris.setNLoops(10)
			qb.measureSpectroscopy(fstart=8.2,fstop=8.9,fstep=0.002,data=child,power=-20)
#		awgflux.loadRealWaveform(zeros((20000)), channel=channel,waveformName=str(channel))
		awgflux.setOffset(channel,0)
		data.savetxt()
##
channel=3
v=2
pulse=zeros((20000))#
pulse+=0#-v/2*4000/20000
#pulse[5500:9500]=[v/2]*4000
awgflux.loadRealWaveform(pulse, channel=channel,waveformName=str(channel))
##
jba2=instrumentManager.getInstrument('jba_qb2')
jba3=instrumentManager.getInstrument('jba_qb3')
print jba2,jba3
acqiris.setNLoops(40)
##
jba2.measureSCurve(voltages=linspace(0.21,0.26,50))
##
jba3.measureSCurve(voltages=linspace(0.41,0.47,50))

##
acqiris=instrumentManager.getInstrument("acqiris")
print acqiris
acqiris.setNLoops(10)
##
print qb._jba._pulseGenerator.clearPulse()
##
print qb._jba.sInterpolateVP(2.8)
##
pulse=zeros((20000))
pulse[5500:9500]=[0.5]*4000
awgflux.loadRealWaveform(pulse, channel=2,waveformName=str(2))
##
import scipy
gv.data.sortBy('p')
print gv.data['p'].index(0)
##
import numpy
gv.data.sortBy('p')
p=gv.data['p']
v=gv.data['v']

##
p=p[p>0]
v=v[p>0]
p=p[p<1]
v=v[p<1]
##
print p,v

from matplotlib.pyplot import *
#figure()
cla()
plot(p,v)
draw()
show()
##
f=scipy.interpolate.interpolate.interp1d(p,v,copy=True)
print f(0.5)
##
cla()
plot(arange(0.1,0.9,20),qb._jba.sInterpolateVP(arange(0,1,20)))
draw()
show()

##

jba=instrumentManager.getInstrument('jba_qb2')
jbaadded=instrumentManager.getInstrument('jba_qb3')
#
fjba=6.75
acqiris.setNLoops(20)
data=Datacube('jbas with jba=%f -41.19dBm '%fjba)
dataManager.addDatacube(data)
frequencies=arange(6.6,6.95,0.01)
powers=arange(0,0.5,0.05)
for f in frequencies:
	bounds=[0.2,0.35,40]
	for p in powers:
		fsp.setFrequency(f)
		jbaadded.setFrequency(f,amplitude=p)
		jba._findAmplitude(frequency=fjba,bounds=bounds,data=data)
		time.sleep(0.5)
		fsp.write("CALC:MARK:Y?")
		data.set(f_added=f, a=jba._vMaxAmplitude,amplitude=p,p_added=fsp.read())
		fsp.setFrequency(fjba)
		time.sleep(0.5)
		fsp.write("CALC:MARK:Y?")
		data.set(f_jba=fjba, p_jba=fsp.read())
		bounds=[jba._vMaxAmplitude-0.015,jba._vMaxAmplitude+0.015,15]
		data.commit()
		

###
time.sleep(60*60*2)
jba=instrumentManager.getInstrument('jba_qb1')
mw_qb=instrumentManager.getInstrument('mwsource_qb')
print jba, mw_qb
fjba=6.835
acqiris.setNLoops(1)
data=Datacube('jbas with jba=%f'%fjba)
dataManager.addDatacube(data)
mw_qb.turnOn()
frequencies=arange(6.8,7.1,0.01)
for f in frequencies:
	fsp.setFrequency(f)
	mw_qb.setFrequency(f)
	dataS=Datacube()	
	data.addChild(dataS)
	jba.calibrate(bounds=[3,5,40],dataS=dataS,voltages=linspace(3,4.5,80))
	time.sleep(0.5)
	fsp.write("CALC:MARK:Y?")
	data.set(f_added=f, a=jba._vMaxAmplitude,p_added=fsp.read())
	fsp.setFrequency(fjba)
	time.sleep(0.5)
	fsp.write("CALC:MARK:Y?")
	data.set(f_jba=fjba, p_jba=fsp.read())
	data.commit()
	data.savetxt()
## Mesure de la raideur des JBA
mw_qb.turnOff()
acqiris.setNLoops(1)
##
data=Datacube('raideur JBA 6.83')
dataManager.addDatacube(data)
for f in arange(6.835,6.8,-0.001):
	data.set(f=f)
	data.commit()
	dataS=Datacube("f=%f"%f)
	data.addChild(dataS)
	jba.setFrequency(f)
	jba.calibrate(bounds=[2,5,40],dataS=dataS)#,voltages=linspace(3.8,4.5,80))
	data.savetxt()




##
fsp=instrumentManager.getInstrument('fsp')
fsp.write("SENSE1:FREQUENCY:CENTER 6.75 GHZ")
fsp.write("CALC:MARK:Y?")
print fsp.read()
##
acqiris.setNLoops(1)
##
qb._jba._pulseGenerator.clearPulse()
##
data=Datacube('sdfg54cg53d..sd8f')
data.addChild(Datacube())
data.savetxt()