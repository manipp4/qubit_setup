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
qb_mw=instrumentManager.getInstrument('MWSource_qb')
vna.timeOut=200
import sys
import os
import os.path
##
print 4
## CREATE DATACUBE
data=Datacube("JBA analysis vs frequency - 2nd ")
dataManager.addDatacube(data)
vna.timeOut=200
i=0

## SET FREQUENCY RANGE
vna.setCenterFrequency(9.325)
vna.setSpanFrequency(0.02)
vna.setNumberOfPoints(51)
## PERFORM SWEEP
attenuation=-40
averaging=100
F=arange(8.5,8.7,0.001)
#vna.setNumberOfAveraging(averaging)
#vna.setNumberOfPoints(1601)
#vna.setCenterFrequency(9.25)
#vna.setSpanFrequency(0.08)
#vna.setVideoBW(100)

for f in F:
	qb_mw.setFrequency(f)
	print "f= %f" %f
	child=vna.getTrace(waitFullSweep=True)
#	child['mag']=child['mag']-20
#	child.createColumn('amp',child['mag']+attenuation)
	data.set(i=i, f=f,averaging=averaging)
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