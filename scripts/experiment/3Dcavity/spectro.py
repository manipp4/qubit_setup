from pyview.lib.datacube import Datacube
import numpy
import math
from config.instruments import *

from pyview.helpers.datamanager import DataManager
dataManager = DataManager()
from pyview.helpers.instrumentsmanager import Manager
##
instruments = Manager()
##
fsp=instrumentManager.getInstrument('fsp')

##

data1=Datacube()
dataManager.addDatacube(data1)
##
values=fsp.getSingleTrace()
data.setColumn("f",values[0])
data.setColumn("p",values[1])
data.setName("fspSpectrum")
data.savetxt()
##
# Spectro in CW mode for VNA and scan over agilent qubit gen
vna=instrumentManager.getInstrument("vna")
print vna
print vna.getValuesAtMarker(1,waitNewSweep=True)
print vna.getValuesAtMarker(1,waitNewSweep=True)
print vna.getValuesAtMarker(1,waitNewSweep=True)
print vna.getValuesAtMarker(1,waitNewSweep=True)
##
vna=instrumentManager.getInstrument("vna")
gen=instrumentManager.getInstrument("MWSource_QB")
data=Datacube("spectro1")
dataManager.addDatacube(data)
fStart=4
fStop=6.1
fStep=.0001
freqs=arange(fStart,fStop,fStep)
try:
	for f in freqs:
		gen.setFrequency(f)
		time.sleep(1)
		trace=vna.getTrace(waitFullSweep=True)
		data.set(f=f,amp=trace.column("mag")[0],phase=trace.column("phase")[0])
		data.commit()
except: 
	raise
finally:
	data.savetxt()
##
val=vna.getValuesAtMarker(1,waitNewSweep=True)
print val[0]
##
trace=vna.getTrace()
print trace.column("mag")[0]
