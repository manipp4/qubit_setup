#########################
#### Pulse parameters ###
#########################
import sys
import time
import math
import experiment.cavity3D.Pulses.pulseLibrary as pl
import numpy as np
import scipy
import scipy.optimize
print "Scipy version %s" %scipy.version.version
from matplotlib.pyplot import *
from pyview.helpers.instrumentsmanager import Manager
##
AWG=Manager().getInstrument('awgMW2')
readoutPG=Manager().getInstrument('PulseGen...')
qubitPG=Manager().getInstrument('PulseGen...')
##
### parameters ###
driveReadSeparation_ns=20
standardHeight=1
sampTime_ns=1
triggerInterval_ns=21000
readoutPulseLength_ns=2500
awgWaitingOutput='first'  	## AWG output while waiting for a trigger 
##
def resSpecPulses:
	readoutPG=squareSweep
	qubitPG=flat
##
def qubitSpecPulses:
	readoutPG=square
	qubitPG=gaussianSquareSweep
##
def rabiPulses:
	readoutPG=square
	qubitPG=gaussian
##