##########
## Main ##
#########
## imports  and handles to instruments
import sys
import time
import numpy
import scipy
import scipy.optimize
import scipy.interpolate
import experiment.cavity3D.Pulses.waveformGenerator as waveGen
from pyview.lib.datacube import *
from pyview.helpers.datamanager import DataManager
from pyview.helpers.instrumentsmanager import Manager
from matplotlib.pyplot import *
from pyview.lib.smartloop import *
from macros.UtilityFunctions3D_fitting import *
reload(sys.modules["macros.UtilityFunctions3D_fitting"])
from macros.UtilityFunctions3D_fitting import *
from macros.UtilityFunctions3D_ExperimentRecipies import *
reload(sys.modules["macros.UtilityFunctions3D_ExperimentRecipies"])
from macros.UtilityFunctions3D_ExperimentRecipies import *

#instruments
acqiris=Manager().getInstrument('acqiris34') 
coil=Manager().getInstrument('Yoko3')
paraCoil=Manager().getInstrument('Yoko2')
AWG=Manager().getInstrument('awgMW2')
mw_cav=Manager().getInstrument('MWSource_Cavity')
mw_qb=Manager().getInstrument('MWSource_Qubit')
mw_par=Manager().getInstrument('MWSource_Paramp')
pg_qb=Manager().getInstrument('pg_qb')
pg_cav=Manager().getInstrument('pg_cav')
atten_cav=Manager().getInstrument('Yoko1')
atten_qb=Manager().getInstrument('Yoko4')
register=Manager().getInstrument('register')
##
reload(sys.modules["macros.UtilityFunctions3D_fitting"])
reload(sys.modules["macros.UtilityFunctions3D_ExperimentRecipies"])
## paramp settings
paraCoil.setVoltage(-20.42)
pumpfreq=2*7.309-0.000011
mw_par.setFrequency(pumpfreq)
mw_par.setPower(5)
##
##
def fvsIcoil(I):
	fmax=8.039
	Ioff=-0.002 #Ioff=-0.0089 2.51 mA
	Iperiod=0.0463
	f=fmax*sqrt(abs(cos((I-Ioff)*pi/Iperiod)))	
	return f
##	single tone spec
data=Datacube('resSpec_Vcoil5p5')
f_center=7.309
f_span=0.05
f_step=0.001
resSpec(data=data,fcenter=f_center,fspan=f_span,fstep=f_step,power=2.4,fit=False,autoPlot=True,autoClear=True,dataSave=True)

## 2 tone spec continous
data=Datacube('qbSpecCont3')
f_center=8.2
f_span=0.4
f_step=0.001	
qbSpecContinous(data=data,fcenter=f_center,fspan=f_span,fstep=f_step,fit=False,autoPlot=True,autoClear=True,dataSave=True)
#qbSpec(nLoops=1,fcenter=1,fspan=1,fstep=0.1, powerQubit=1., data='', fit=True,autoPlot=True,autoClear=False,dataSave=True)

## 2 tone spec pulsed
data=Datacube('qbSpecPulsed1')
f_center=8.2
f_span=0.3
f_step=0.001
qbSpecPulsed(data=data,fcenter=f_center,fspan=f_span,fstep=f_step,fit=False,autoPlot=True,autoClear=True,dataSave=True)
#qbSpec(nLoops=1,fcenter=1,fspan=1,fstep=0.1, powerQubit=1., data='', fit=True,autoPlot=True,autoClear=False,dataSave=True)
##
data0=Datacube('qbSpecContVsResPower4')
data0.toDataManager()
start=2.2
step=-0.05
stop=1.85
f_center=7.90
f_span=0.3
f_step=0.002
VVALoop=SmartLoop(start,step,stop,name='VVAVoltages')
for VVAVoltage in VVALoop:
	print "VVAVoltage=%f"%VVAVoltage
	data0.set(VVAVoltage=VVAVoltage,commit=True)
	child=Datacube('qbSpecCont')
	data0.addChild(child)	
	qbSpecContinous(data=child,fcenter=f_center,fspan=f_span,power=VVAVoltage,fstep=f_step,fit=False,autoPlot=True,autoClear=True,dataSave=True)
data0.savetxt()
## Rabi measurement
data=Datacube('Rabi_qbVVAat0p5')
QBpower=''
start=0
step=2
stop=400
rabiMeas(data=data,powerQubit=QBpower,start=start,stop=stop,step=step,fit=False,autoPlot=True,autoClear=False,dataSave=True)
## T1 Meas
data=Datacube('T1_1b')
start=1000
step=10
stop=2000
t1MeasFast(data=data,fit=False,autoPlot=True,autoClear=False,dataSave=True)
##
q=''
print q
