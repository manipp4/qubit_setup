##########
## Main ##
#########
## imports  and handles to instruments
import sys
import time
import datetime
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
AWG=Manager().getInstrument('awgMW2')
mw_cav=Manager().getInstrument('MWSource_Cavity')
mw_qb=Manager().getInstrument('MWSource_Qubit')
mw_par=Manager().getInstrument('MWSource_Paramp')
pg_qb=Manager().getInstrument('pg_qb')
pg_cav=Manager().getInstrument('pg_cav')
res_att=Manager().getInstrument('Yoko1')
paraCoil=Manager().getInstrument('Yoko2')
coil=Manager().getInstrument('Yoko3')
qb_att=Manager().getInstrument('Yoko4')
register=Manager().getInstrument('register')

## Run this section if parameters where changed in UtilityFunctions3D_ExperimentRecipies. 
## NOTE: If functions where changed in UtilityFunctions3D_ExperimentRecipies reload the top section of this module
reload(sys.modules["macros.UtilityFunctions3D_fitting"])
reload(sys.modules["macros.UtilityFunctions3D_ExperimentRecipies"])

##
def fvsIcoil(I):
	fmax=8.039
	Ioff=-0.002 #Ioff=-0.0089 2.51 mA
	Iperiod=0.0463
	f=fmax*sqrt(abs(cos((I-Ioff)*pi/Iperiod)))	
	return f
##	single tone spec
data=Datacube('resSpec %.16s' % datetime.datetime.now())
f_center=7.38
f_span=0.15
f_step=0.001
coilVoltage=11.15
resSpec(fcenter=f_center,fspan=f_span,fstep=f_step,data=data,setReadoutPar=False,useDict=False,parSubDict=None,resVVAVoltage=None,useParamp=None,coilVoltage=coilVoltage,setPulse=None,setAcqiris=None, fit=True,autoPlot=True,autoClear=False,dataSave=True,savePar=True)

## 2 tone spec continous
data=Datacube('qbSpecCont %.16s' % datetime.datetime.now())
f_center=7.0
f_span=0.4
f_step=0.001
resFrequency=7.3719
qbSpecContinuous(fcenter=f_center,fspan=f_span,fstep=f_step, data=data,setReadoutPar=True,useDict=False, parSubDict=None, qbVVAVoltage=None, resFrequency=resFrequency, resVVAVoltage=None, coilVoltage=None, useParamp=None, setPulse=None,setAcqiris=None,fit=False,autoPlot=True,autoClear=False,dataSave=True,savePar=False)

## 2 tone spec pulsed with saturation pulse
data=Datacube('qbSpecPulsed %.16s' % datetime.datetime.now())
f_center=6.57
f_span=0.4
f_step=0.001
resFrequency=7.366	
qbSpecPulsed(fcenter=f_center,fspan=f_span,fstep=f_step, data=data,setReadoutPar=True, qbPulseLength=None, useDict=False, parSubDict=None, qbVVAVoltage=0.3, resFrequency=resFrequency, resVVAVoltage=None, coilVoltage=None, useParamp=None, setPulse=None,setAcqiris=None,fit=True,autoPlot=True,autoClear=False,dataSave=True,savePar=False)


## 2 tone spec pulsed with Pi pulse
data=Datacube('qbSpecPiPulsed1 %.16s' % datetime.datetime.now())
f_center=6.75
f_span=0.25
f_step=0.001
qbSpecPiPulsed(data=data,fcenter=f_center,fspan=f_span,fstep=f_step,fit=False,autoPlot=True,autoClear=True,dataSave=True)

## 2 tone spec pulsed with Pi pulse and same length cavity pulse
data=Datacube('qbSpecPiAndCavPulsed1 %.16s' % datetime.datetime.now())
f_center=7.95
f_span=0.2
f_step=0.0005
cavPulse_Height=0.5
qbSpecPiPulsedWithResPulse(data=data,fcenter=f_center,fspan=f_span,fstep=f_step,cavPulseHeight=cavPulse_Height,fit=False,autoPlot=True,autoClear=True,dataSave=True)

## Photon qubit spectroscopy where a cavity pulse with a variable height is put on at the same time as the qubit is driven 
data=Datacube('photonNumberSplittingAmp %.16s' % datetime.datetime.now())
f_center=6.075
f_span=0.12
f_step=0.001
cavPulse_start=0.5
cavPulse_step=0.1
cavPulse_stop=1
photonNumberSplittingAmp(data=data,ampStart=cavPulse_start,ampStep=cavPulse_step, ampStop=cavPulse_stop,fcenter=f_center,fspan=f_span,fstep=f_step,fit=False,autoPlot=False,autoClear=False,dataSave=True,savePar=True)

## Photon qubit spectroscopy where a cavity pulse with a variable length is put on at the same time as the qubit is driven 
data=Datacube('photonNumberSplittingLength %.16s' % datetime.datetime.now())
f_center=6.075
f_span=0.15
f_step=0.001
cavPulseLen_start=0.0
cavPulseLen_step=50
cavPulseLen_stop=1000
photonNumberSplittingLength(data=data,cavLenStart=cavPulseLen_start,cavLenStep=cavPulseLen_step, cavLenStop=cavPulseLen_stop,fcenter=f_center,fspan=f_span,fstep=f_step,fit=False,autoPlot=False,autoClear=False,dataSave=True,savePar=True)

## Qubit spectroscopy Vs coil voltage using qbSpecPiPulsed. i.e. the pulse is not a pi pulse everywhere
data=Datacube('qbSpecVsCoilV3 %.16s' % datetime.datetime.now())
f_center=8.02
f_span=0.05
f_step=0.001
vCoil_start=-0.5
vCoil_step=0.1
vCoil_stop=0.5
qbPiSpecVsCoilVolt(data=data,VStart=vCoil_start,VStep=vCoil_step, VStop=vCoil_stop,fcenter=f_center,fspan=f_span,fstep=f_step,fit=False,autoPlot=False,autoClear=False,dataSave=True,savePar=True)


reload(sys.modules["macros.UtilityFunctions3D_fitting"])
reload(sys.modules["macros.UtilityFunctions3D_ExperimentRecipies"])
################################
## Time resolved measurements ##
################################
## Rabi measurement
data=Datacube('Rabi_qb %.16s' % datetime.datetime.now())
QBpower=''
start=0
step=20
stop=1000
rabiMeas(data=data,powerQubit=QBpower,start=start,stop=stop,step=step,fit=True,autoPlot=True,autoClear=False,dataSave=True)

## T1 Meas
data=Datacube('T1_1b %.16s' % datetime.datetime.now())
start=0
step=300
stop=16000
t1MeasFast(data=data,start=start,stop=stop,step=step,fit=True,autoPlot=True,autoClear=False,dataSave=True)

## Ramsey
data=Datacube('Ramsey %.16s' % datetime.datetime.now())
start=0
step=50
stop=9000
ramseyMeas(data=data,start=start,stop=stop,step=step,fit=True,autoPlot=True,autoClear=False,dataSave=True)

#########
## Loop	##
#########
# functionList is a list of lists. The first element is a name of a function (an experiment), the second is a name of a variable that can be adjusted (followed) during the coil sweep
functionList=[[resSpec,'fcenter',7.373,'f_Res'],[qbSpecPulsed,'fcenter',6.821,'f_qb']]	
coilSweepLoopAdaptive(functionList,data='',feedbackPar='f_qb',VStart=10.72,VStep=-0.05, VStop=9, setReadoutPar=True, useDict=False, adaptParameters=True,dataSave=True)
##

,[rabiMeas,'piEst',200,'piPulse'],[t1MeasFast,'T1Est',1600,'T1']
