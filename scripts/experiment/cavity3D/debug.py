import sys

from pyview.lib.datacube import *
from pyview.helpers.datamanager import DataManager
from pyview.helpers.instrumentsmanager import Manager


#instruments
print "DLLMath1Module.meanOfLastWaveForms("+str(2)+")"
acqiris=Manager().getInstrument('acqiris34') 
##
acqiris.AcquireTransfer(transferAverage=False,nLoops=1,wantedChannels=3)
acqiris("DLLMath1Module.meanOfLastWaveForms(3)")		# calculate the mean of each trace in the sequence
means= acqiris("DLLMath1Module.mean")	# get the sequence of means for the selected channels
print means