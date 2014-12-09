from pyview.lib.datacube import *
from pyview.helpers.datamanager import *
from pyview.helpers.instrumentsmanager import *
instrumentManager=Manager()
dataManager=DataManager()
import math
import numpy
##
pg=instrumentManager.getInstrument('pg_cavity') 
cavity_drive=instrumentManager.getInstrument('MWSource_cavity')
##
def gaussian(t,t0,sigma,amp=2.0,offset=0):
	return offset+amp*exp(-(t-t0)**2/(2*sigma**2))
##
pulse=zeros(20000)
for i in range(10000,14000):
	pulse[i]=gaussian(i,12000.0,1000.0)
frequency=cavity_drive.frequency()
pg.clearPulse()
pg.generatePulse(frequency=frequency,shape=pulse)
pg.sendPulse()
##
d=Datacube()
DataManager().addDatacube(d)
d.createColumn("test",pulse)