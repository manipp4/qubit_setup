##########################
## Not ready yet #########
##########################
import sys
import time
import numpy
import scipy
import experiment.cavity3D.Pulses.waveformGenerator as wg
import scipy.optimize
print "Scipy version %s" %scipy.version.version
from pyview.lib.datacube import *
from pyview.helpers.datamanager import DataManager
from pyview.helpers.instrumentsmanager import Manager
from matplotlib.pyplot import *
from pyview.lib.smartloop import *

#instruments
acqiris=Manager().getInstrument('acqiris') 
coil=Manager().getInstrument('Keithley2400')
AWG=Manager().getInstrument('awgMW2')
mw_cav=Manager().getInstrument('MWSource_cavity')
mw_qb=Manager().getInstrument('MWSource_Qubit2')
attenuator=Manager().getInstrument('Yoko3')
register=Manager().getInstrument('register')
##
sampTime_ns = 2
triggerInterval=50000
##
def AWGSettings():
	AWG.setRunMode("SEQ")
	AWG.deleteWaveform('ALL')
	samplRate=1e9/sampTime_ns
	reprate=samplRate/20000
	AWG.setRepetitionRate(reprate)
	AWG.setTriggerInterval(triggerInterval*1e-9)
##
def rabiWaveforms(driveReadSep_ns=20,readout_pulse_ns=1200,rabiStart_ns=0,rabiStop_ns=100,rabiStep_ns=4,markerGated='False'):
# has to be specidfied in seconds
	AWGSettings()
	
	readout_pulse=abs(round(readout_pulse_ns/sampTime_ns))
	startReadout=int(20000-readout_pulse)
	stopReadout=int(20000)
	readout=wg.readoutWaveform(startReadout,stopReadout)
	wg.send2AWG(readout)
	
	driveReadSep=abs(round(driveReadSep_ns/sampTime_ns))
	stopPulses=int(20000-readout_pulse-driveReadSep)
	rabiStart=int(round(rabiStart_ns/sampTime_ns))
	rabiStop=int(round(rabiStop_ns/sampTime_ns))
	rabiStep=int(round(rabiStep_ns/sampTime_ns))	
	pulses=range(rabiStart,rabiStop,rabiStep)
	wfNames=[]
	for pulse in pulses:
		time.sleep(0.1)
		wfName='Rabi %s'%(pulse*sampTime_ns)
		wfNames.append(wfName)
		wf=wg.squarePulseWaveform(stopPulses-pulse,stopPulses,name=wfName)
		wg.send2AWG(wf)
	return wfNames

##
##
def rabiSequence(rabiStart_ns=0,rabiStop_ns=100,rabiStep_ns=4,repetitions='inf'):
	readoutChannel=1
	pulseChannel=2
	wfNames=rabiWaveforms(rabiStart_ns=rabiStart_ns,rabiStop_ns=rabiStop_ns,rabiStep_ns=rabiStep_ns)
	for i in range(len(wfNames)):
		AWG.appendWaveformToSequence(i,readoutChannel,"readout",repeat=repetitions)
		AWG.appendWaveformToSequence(i,pulseChannel,wfNames[i],repeat=repetitions)
	AWG.startAllChannels()
	AWG.runAWG()
	return wfNames	
##
rabiSequence()
##
print sys.version