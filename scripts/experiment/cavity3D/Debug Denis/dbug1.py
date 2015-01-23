import sys
import time
import numpy

from pyview.lib.datacube import *
from pyview.helpers.datamanager import DataManager
from pyview.helpers.instrumentsmanager import Manager


#instruments
vnaK1=Manager().getInstrument('vnaK1')
fsp=Manager().getInstrument('fsp')
##
print fsp.name()
print fsp._visaAddress
print fsp.ask('*IDN?')

print vnaK1.name()
print vnaK1._visaAddress
print vnaK1.ask('*IDN?')
##

print vnaK1.clearDevice() 			# to be debugged
print vnaK1.triggerReset() 		# to be debugged

print vnaK1.turnOff()				# OK
print vnaK1.turnOn()				# OK
print vnaK1.power(port=1)			# OK
print vnaK1.setPower(-65,port=1)	# OK
print vnaK1.attenuation()			# OK
print vnaK1.setAttenuation(60)	# OK
print vnaK1.startFrequency()		# OK
print vnaK1.setStartFrequency(732000000)	# OK
print vnaK1.stopFrequency()		# OK
print vnaK1.setStopFrequency(734000000)	# OK
print vnaK1.centerFrequency()		# OK
print vnaK1.setCenterFrequency(7335000000)# OK
print vnaK1.spanFrequency()		# OK
print vnaK1.setSpanFrequency(10000000)	# OK
print vnaK1.numberOfPoints()		# OK
print vnaK1.setNumberOfPoints(200)# OK
print vnaK1.bandwidth()			# OK
print vnaK1.setBandwidth(1)		# OK
print vnaK1.average()				# OK
print vnaK1.averageOn()			# OK
print vnaK1.averageOff()			# OK
vnaK1.averageClear()				# OK
print vnaK1.averageMode()			# OK
print vnaK1.setAverageMode(mode='POINT')# OK
print vnaK1.averageCount()			# OK
print vnaK1.setAverageCount(10)	# OK

print vnaK1.electricalLength() 	# OK
print vnaK1.setElectricalLength(31.93)
print vnaK1.markerState()			# OK
print vnaK1.markerOff()			# OK
print vnaK1.markerOn()				# OK
print vnaK1.markerPosition()		# OK  	
print vnaK1.markerSetPosition(100)# OK
print vnaK1.markerX()				# OK
print vnaK1.markerSetX(7335025125)# OK
print vnaK1.markerGetValue(measNumber=2)[0]		# OK

vnaK1.getFreqMagPhase().toDataManager()
vnaK1.getFreqMagPhase(unwindPhase=True).toDataManager()
vnaK1.getFreqMagPhase(unwindPhase=True,flatten=True,deltaPhase=-180).toDataManager()
##
##
phase=vnaK1.getFreqMagPhase()['phase']
phaseU=vnaK1.unwind(phase)
print len(phaseU)
print arange(len(phaseU))
print phaseU-array((phaseU[-1]-phaseU[0])/len(phaseU)*arange(len(phaseU)))