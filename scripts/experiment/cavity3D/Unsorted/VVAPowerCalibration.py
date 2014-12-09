#######################################################################
####### VVA Power calibration
#######################################################################

## imports  and handles to instruments
import sys
import time
import numpy
import scipy
import scipy.optimize
import scipy.interpolate
print "Scipy version %s" %scipy.version.version
from pyview.lib.datacube import *
from pyview.helpers.datamanager import DataManager
from pyview.helpers.instrumentsmanager import Manager


#instruments
attenuator=Manager().getInstrument('Yoko1')
fsp=Manager().getInstrument('fsp')
##
	
data=Datacube('Cavity VVA Yoko1V-fspPower')
DataManager().addDatacube(data)
attens=arange(0,8,0.1)
for atten in attens:
	attenuator.setVoltage(atten,slewRate=2)
	time.sleep(1)
	trace=fsp.getSingleTrace()
	pow=mean(trace[1])
	data.set(pow=pow,atten=atten)
	data.commit()
data.savetxt()
##
