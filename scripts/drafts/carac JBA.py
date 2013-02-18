##2D Spectro
from config.instruments import *
from pyview.lib.datacube import *

from matplotlib.pyplot import *
import numpy
#reload(sys.modules["pyview.helpers.instrumentsmanager"])
from pyview.helpers.instrumentsmanager import *
import scipy
from pyview.helpers.datamanager import *
from pyview.helpers.datamanager import DataManager
dataManager = DataManager()
instrumentManager=Manager()
#
jba=instrumentManager.getInstrument('jba_qb3')
print jba._sCurveParams
##
s=jba.caracteriseIQvsFvsP(frequencies=arange(6.77,6.7,-0.001),voltages=arange(1,5,0.05))
##
print dir(jba)
##
figure()
plot(arange(0,20000),s)
draw()
show()
##
s= jba._pulseGenerator.pulses.values()[0][0]
##
print jba._pulseGenerator.removeAllPulses()
##
print jba._pulseGenerator.pulses
##
print s
##
import scipy
print dir(scipy.interpolate.interp1d)



f=scipy.interpolate.interp1d([0,1],[0,1])
print f(0.5)

##




jba=instrumentManager.getInstrument('jba_qb1')
print jba

mwAdded=instrumentManager.getInstrument('mwsource_qb')
print mwAdded
##
frequencies=arange(5.8,6.2,0.005)
allData=Datacube("allData")
dataManager.addDatacube(allData)
for fadded in frequencies:

	ntimes=200
	voltages=linspace(1.5,2.5,1001)

	mwAdded.setFrequency(fadded)
	data=Datacube("JBA 6.23 added tone=%f"%fadded)

	allData.addChild(data)

	time.sleep(2)

	jba.calibrate(bounds=[1.5,2.5,101])

	#dataManager.addDatacube(data)	
	#dataOff=Datacube("2ndTone Off")
	#data.addChild(dataOff)
	#mwAdded.turnOff()
	#jba.measureSCurve(voltages=linspace(2.13,2.47,200),ntimes=ntimes,data=dataOff)
	
	data42=Datacube()
	data.addChild(data42)
	mwAdded.turnOn()
	mwAdded.setPower(-13)
	jba.measureSCurve(voltages=voltages,ntimes=ntimes,data=data42)
	data42.setName("2ndTone -42")
	
	
	
	data40=Datacube("2ndTone -40")
	data.addChild(data40)
	mwAdded.turnOn()
	mwAdded.setPower(-11)
	jba.measureSCurve(voltages=voltages,ntimes=ntimes,data=data40)
	data40.setName("2ndTone -40")
	
	data44=Datacube("2ndTone -44")
	data.addChild(data44)
	mwAdded.turnOn()
	mwAdded.setPower(-15)
	jba.measureSCurve(voltages=voltages,ntimes=ntimes,data=data44)
	data44.setName("2ndTone -44")
	
	
	
	allData.savetxt()
	
	
	


##








import numpy

jba=instrumentManager.getInstrument('jba_qb1')
print jba

jba.shape=numpy.zeros((20000),dtype = numpy.complex128)
jba.shape[10000:10010]=linspace(0,1,10)
jba.shape[10010:12100]=1
jba.shape[12100:12110]=linspace(1,0,10)
data=Datacube("phi vs f")
frequencies=arange(6.8,6.85,0.001)
for f in frequencies:
 jba.setFrequency(f)
 jba.setAmplitude(amplitude=2.2)
 time.sleep(0.5)
 co=jba.getThisMeasure()[1]
 [I,Q]=[mean(co[0]),mean(co[1])]
 data.set(f=f,v=2.2,I=I,Q=Q)
 data.set(M=sqrt(I**2+Q**2))
 data.set(phi=math.atan2(I,Q))
 data.commit()
data.savetxt()
##
dataManager.addDatacube(data)



##
jba3=instrumentManager.getInstrument('jba_qb3')
print jba3._sCurveParams


print [jba3._sCurveParams[3]-abs(jba3._sCurveParams[0])*1,jba3._sCurveParams[3]+abs(jba3._sCurveParams[0])*1]

##
data=Datacube()
dataManager.addDatacube(data)
for f in arange(7.0,7.25,0.005):
	jba3.setFrequency(f)
	jba3.calibrate()
	data.set(f=f)
	data.commit()
	child=Datacube()
	data.addChild(child)
	jba3.measureSCurve()
	data.savetxt()








