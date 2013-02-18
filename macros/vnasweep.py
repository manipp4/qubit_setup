from config.instruments import *
from matplotlib.pyplot import *
from pyview.gui.mpl.backend import figure
import numpy
import scipy
from pyview.helpers.datamanager import DataManager
dataManager = DataManager()
instrumentManager=Manager()
vna=instrumentManager.getInstrument('vna')
yoko=instrumentManager.getInstrument('coil')
vna.timeOut=200
import sys
import os
import os.path


## CREATE DATACUBE
data=Datacube("JBA4 analysis test")
dataManager.addDatacube(data)
vna.timeOut=200
i=0

## SET FREQUENCY RANGE
vna.setCenterFrequency(9.34)
vna.setSpanFrequency(0.12)

## PERFORM SWEEP
attenuation=-40
averaging=100
P=arange(-20.,5,1.)
vna.setNumberOfAveraging(averaging)
#vna.setNumberOfPoints(1601)
#vna.setCenterFrequency(9.25)
#vna.setSpanFrequency(0.08)
#vna.setVideoBW(100)

for p in P:
	vna.setPower(p)
	print "P= %f" %p
	child=vna.getTrace(waitFullSweep=True)
#	child['mag']=child['mag']-20
	child.createColumn('amp',child['mag']+attenuation)
	data.set(i=i, p=(p+attenuation),averaging=averaging)
	data.commit()
	child.setName(i)
	data.addChild(child)
	child.savetxt()
	data.savetxt()
	i+=1
	
## PERFORM SINGLE POINT ACQUISITION
attenuation=-50
averaging=100
p=-20
print "P= %f" %p
child=vna.getTrace()
#	child['mag']=child['mag']-20
child.createColumn('amp',child['mag']+attenuation)
data.set(i=i, p=(p+attenuation),averaging=averaging)
data.commit()
child.setName(i)
data.addChild(child)
child.savetxt()
data.savetxt()
i+=1
##




yoko=instrumentManager.getInstrument('coil')

data=Datacube("JBA 3-4 analysis - vflux 3")
dataManager.addDatacube(data)
vna.timeOut=200
i=0


##
attenuation=-40
#averaging=100.
#p=-14.
#vna.setNumberOfAveraging(averaging)
#vna.setNumberOfPoints(101)
#vna.setPower(p)
#vna.setCenterFrequency(9.55)
#vna.setSpanFrequency(0.05)
#vna.setVideoBW(100)
#
for v in arange(0,-5,-0.1):
	yoko.setVoltage(v)
try:
	for vFlux in arange(-5,5.01,0.1):
		yoko.setVoltage(vFlux)
		print "v= %f" %vFlux
		child=vna.getTrace(waitFullSweep=True)
#		child['mag']=child['mag']-20
#		data.set(i=i, p=(p+attenuation),averaging=averaging,vFlux=vFlux)
		data.set(vFlux=vFlux, i=i)#,averaging=averaging)
		data.commit()
		child.setName(i)
		data.addChild(child)
		child.savetxt()
		data.savetxt()
		i+=1
		lastv=vFlux
finally:
	for v in arange(lastv,0,-lastv/100):
		yoko.setVoltage(v)
	yoko.setVoltage(0.)
##
vna.setPower(-10)
vna.setNumberOfAveraging(100)
vna.setCenterFrequency(8.86)
vna.setSpanFrequency(0.3)
vna.setNumberOfPoints(201)
##
print yoko