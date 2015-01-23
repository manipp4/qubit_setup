#########################
## Experiment Recipies ##
#########################
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

#instruments
acqiris=Manager().getInstrument('acqiris34') 
coil=Manager().getInstrument('Yoko3')
AWG=Manager().getInstrument('awgMW2')
mw_cav=Manager().getInstrument('MWSource_Cavity')
mw_par=Manager().getInstrument('MWSource_Paramp')
mw_qb=Manager().getInstrument('MWSource_Qubit')
pg_qb=Manager().getInstrument('pg_qb')
pg_cav=Manager().getInstrument('pg_cav')
res_att=Manager().getInstrument('Yoko1')
qb_att=Manager().getInstrument('Yoko4')
register=Manager().getInstrument('register')
paraCoil=Manager().getInstrument('Yoko2')


######################
### help functions ###
######################
def setAWGPar(AWGPar):
	samplRate=1.e9/AWGPar['sampTime_ns']
	reprate=samplRate/AWGPar['AWGnbrOfPoints']
	AWG.setRepetitionRate(reprate)
	AWG.setTriggerInterval(AWGPar['triggerInterval']*1e-9)# has to be specidfied in seconds
	lengthOfWaveform=AWGPar['AWGnbrOfPoints']*AWGPar['sampTime_ns']
	return lengthOfWaveform
def measureIQ(nLoops=1,wantedChannels=3,iOffset=0,qOffset=0,averageOverSequence=False,convertToAmpPhase=False,**kwargs):

	# acquire and transfer the sequence of traces for the selected channels
	acqiris.AcquireTransfer(transferAverage=False,nLoops=nLoops,wantedChannels=wantedChannels)
	time.sleep(0.1)
	acqiris("DLLMath1Module.meanOfLastWaveForms("+str(wantedChannels)+")")		# calculate the mean of each trace in the sequence 
	channels= acqiris("DLLMath1Module.mean")	# get the sequence of means for the selected channels
	# get the indexes of selected channels
	indexes= [i for i,x in enumerate([1&wantedChannels!=0,2&wantedChannels!=0,4&wantedChannels!=0,8&wantedChannels!=0]) if x ==True]
	channels=[channels[indexes[0]],channels[indexes[1]]] # keep only the first and second selected channels as I and Q
	if iOffset!=0 : channels[0]=channels[0]-iOffset  	 # subtract I and Q offset if necessary
	if qOffset!=0 : channels[1]=channels[1]-qOffset
	if averageOverSequence:								 # average over sequence if requested
		channels=[numpy.mean(channels[0]),numpy.mean(channels[1])]
	if convertToAmpPhase:									 # convert I and Q into Amp and Phase
		channels=[sqrt((channels[0])**2+(channels[1])**2),arctan(channels[1]/channels[0])]		# calculate amplitude and phase
	# returns [I,Q] or [Amp, phi] or [array([I1,I2,I3,...],array([Q1,Q2,Q3,...])] or  [array([A1,A2,A3,...],array([phi1,phi2,phi3,...])]
	return channels 
def measureIQOffOn(nLoops=1,wantedChannels=3,averageOverSequence=False,convertToAmpPhase=False,**kwargs):
	# set values from keywords
	firstSlice=kwargs['firstSlice']
	secondSlice=kwargs['secondSlice']
	startMargin=kwargs['startMargin']
	middleMargin=kwargs['middleMargin']
	stopMargin=kwargs['stopMargin']
	OnBeforeOff=kwargs['OnBeforeOff']
	# acquire and transfer the sequence of traces for the selected channels
	acqiris.AcquireTransfer(transferAverage=False,nLoops=nLoops,wantedChannels=wantedChannels)
	time.sleep(0.1)
	nbrSamplesPerSeg=acqiris.getLastWave()['nbrSamplesPerSeg']
	if firstSlice==None:
		if secondSlice==None:
			index1=int(nbrSamplesPerSeg/2*(1+middleMargin/2))
			if index1 <0 : index1=1
			if index1 > nbrSamplesPerSeg-1 : index1=nbrSamplesPerSeg-2
			index2=int(nbrSamplesPerSeg*(1-stopMargin))
			if index2 < index1: index2=index1+1
			if index2 > nbrSamplesPerSeg-1 : index2=nbrSamplesPerSeg-1
			secondSlice=slice(index1,index2)
		index1=int(nbrSamplesPerSeg*startMargin)
		if index1 <0 : index1=0
		if index1> secondSlice.start-1: index1 = secondSlice.start-1
		index2=int(secondSlice.start- middleMargin*nbrSamplesPerSeg)
		if index2 < index1: index2=index1+1
		if index2 > secondSlice.start:index2=secondSlice.start-1
		firstSlice=slice(index1,index2)
	elif secondSlice==None:
		index1=int(firstSlice.stop+ middleMargin*nbrSamplesPerSeg)
		if index1 <= firstSlice.stop : index1=firstSlice.stop+1
		if index1 > nbrSamplesPerSeg-1 : index1=nbrSamplesPerSeg-1
		index2=int(nbrSamplesPerSeg*(1-stopMargin))
		if index2<index1: index2=index1
		if index2 > nbrSamplesPerSeg-1 : index2=nbrSamplesPerSeg-1
		secondSlice=slice(index1,index2)
	
	def getBoxcarMeans(slic=slice(0,-1),wantedChannels=3,averageOverSequence=False):
		commandString="DLLMath1Module.boxcarOfLastWaveForms(targettedWaveform="+str(wantedChannels)+",sliceArray="+str([slic,slic,slic,slic])+")"
		acqiris(commandString)		# calculate the mean of each trace in the sequence COMPLETE HERE
		boxcarMeans= acqiris("DLLMath1Module.boxcarMean")	# get the sequence of boxcarMeans for the selected channels
		# get the indexes of selected channels	
		indexes= [i for i,x in enumerate([1&wantedChannels!=0,2&wantedChannels!=0,4&wantedChannels!=0,8&wantedChannels!=0]) if x ==True]
		boxcarMeans=[boxcarMeans[indexes[0]],boxcarMeans[indexes[1]]] # keep only the first and second selected channels
		if averageOverSequence:								 # average over sequence if requested
			boxcarMeans=[numpy.mean(boxcarMeans[0]),numpy.mean(boxcarMeans[1])]
		return boxcarMeans
	boxcarMeansA=getBoxcarMeans(slic=firstSlice,wantedChannels=wantedChannels,averageOverSequence=averageOverSequence)
	boxcarMeansB=getBoxcarMeans(slic=secondSlice,wantedChannels=wantedChannels,averageOverSequence=averageOverSequence)
	channels=[boxcarMeansB[0]-boxcarMeansA[0],boxcarMeansB[1]-boxcarMeansA[1],boxcarMeansA[0],boxcarMeansA[1],boxcarMeansB[0],boxcarMeansB[1]]
	if OnBeforeOff:
		channels[0]=-channels[0]
		channels[1]=-channels[1]
	
	if convertToAmpPhase:									 # convert I and Q into Amp and Phase
		channels=[sqrt((channels[0])**2+(channels[1])**2),arctan(channels[1]/channels[0]),sqrt((channels[2])**2+(channels[3])**2),arctan(channels[3]/channels[2]),sqrt((channels[4])**2+(channels[5])**2),arctan(channels[5]/channels[4])]		# calculate amplitude and phase
	# returns [IB-IA,QB-QA,IA,QA,IB,QB] or [AmpCor, phiCor,] or [array([(I2-I1)1,(I2-I1)2,(I2-I1)3,...]),array([(Q2-Q1)1,(Q2-Q1)2,(Q2-Q1)3,...])] or  ...
	return channels

#################################
## dictionaries for parameters ##
#################################
#print readoutPar['method'](nLoops=readoutPar['nLoops'],averageOverSequence=True,convertToAmpPhase=True,**readoutPar['kwargs'])
##
readoutPar=dict()
readoutPar['method']=measureIQ#OffOn
readoutPar['height']=1
readoutPar['freq']=7.3467
readoutPar['power']=4.0
readoutPar['freq_sb']=0
readoutPar['length']=2000
readoutPar['nLoops']=5
readoutPar['UseSwitch']=True
readoutPar['SwitchDelay']=-200
readoutPar['kwargs']={'firstSlice':slice(0,58),'secondSlice':slice(79,450),'startMargin':0,'middleMargin':0.1,'stopMargin':0,'OnBeforeOff':False}
readoutPar['useParamp']=True
readoutPar['parampCoil']=-20.0
readoutPar['parampPower']=4


qubitSpecPar=dict()
qubitSpecPar['specPower']=1.9
qubitSpecPar['pulseType']="square"
qubitSpecPar['pulseHeight']=1
qubitSpecPar['pulseLength']=1000
qubitSpecPar['sepFromReadout']=100

samplePar=dict()
samplePar['f_res']=7.3467
samplePar['f_qbit']=6.094
samplePar['PiPulse']=128
samplePar['vCoil']=-12.1

qubitTimeResPar=dict()
qubitTimeResPar['TimeResPower']=1.4
qubitTimeResPar['qbFreq']=samplePar['f_qbit']
qubitTimeResPar['pulseType']="square"
qubitTimeResPar['pulseHeight']=1
qubitTimeResPar['pulseLength']=samplePar['PiPulse']
qubitTimeResPar['sepFromReadout']=10
qubitTimeResPar['ramseyDetuning']=+0.001
qubitTimeResPar['resPulseHeight']=0.5
qubitTimeResPar['resPulseLength']=1000

AWGParFast=dict()
AWGParFast['sampTime_ns']=1
AWGParFast['triggerInterval']=41000
AWGParFast['AWGnbrOfPoints']=20000

###########################################
### functions that use the dictionaries ###
###########################################

def readout(measure=True, setParameters=True, paramp=readoutPar['useParamp'], readAtRes=True, clearPulse=True, setPower=True, power=''):
	# This method uses the readout method specified in the readout parameter dictionary. If onlyMeasure is true the readout is performed with the current parameters. If onlyMeasure is 	false the readout pulse parameters are applied to the AWG. readAtRes determines if the current readout frequency should be used(false) or the one given in the dictionary(true)
	if setParameters:
		mw_cav.turnOn()
		if readAtRes:
			frequency=readoutPar['freq']
			mw_cav.setFrequency(readoutPar['freq']-readoutPar['freq_sb'])
		else:
			frequency=mw_cav.frequency()
		
		if setPower:
			if power=='':
				power=readoutPar['power']
			res_att.setVoltage(power)	
		if paramp:
			paraCoil.setVoltage(readoutPar['parampCoil'],slewRate=0.3)
			pumpfreq=2*readoutPar['freq']-0.000011
			mw_par.setFrequency(pumpfreq)
			mw_par.setPower(readoutPar['parampPower'])	
			mw_par.turnOn()
		else:
			mw_par.turnOff()
		height=readoutPar['height']
		pulseLength=readoutPar['length']
		lenOfWaveform=setAWGPar(AWGParFast) ## sets the awg parameters and returns the number of points for a waveform
		if clearPulse:
			pg_cav.clearPulse()
		pg_cav.addPulse(generatorFunction="square",frequency=frequency,amplitude=height,start=lenOfWaveform-pulseLength, stop=lenOfWaveform,)
		if readoutPar['UseSwitch']:
			pg_cav.addMarker(channel=1,start1=0,stop1=lenOfWaveform-pulseLength)
			pg_cav.addMarker(channel=2,start1=lenOfWaveform-pulseLength+readoutPar['SwitchDelay'],stop1=lenOfWaveform)
		else:
			pg_cav.addMarker(channel=1,start1=0,stop1=lenOfWaveform-pulseLength)
		pg_cav.preparePulseSequence()
		pg_cav.prepareMarkerSequence()
    	pg_cav.sendPulseSequence()
	if measure:
		dataPoint=readoutPar['method'](nLoops=readoutPar['nLoops'],averageOverSequence=True,convertToAmpPhase=True,**readoutPar['kwargs'])
		toReturn=[dataPoint[0],dataPoint[1]]  # some readout methods return more that two values. Here the number of values returned is fixed to the first two values given by the method
		return toReturn
#
def resSpec(fcenter=1,fspan=1,fstep=0.1,data='',power='',paramp=readoutPar['useParamp'], fit=True,autoPlot=True,autoClear=False,dataSave=True,savePar=True):
	if data=='':	
		data=Datacube('ResSpec')
		data.toDataManager()
	if autoPlot:
		data.plotInDataManager(names=["f_GHz","amp"],clear=autoClear,style='line')
		data.plotInDataManager(names=["f_GHz","ampFit"],clear=autoClear,style='line')
		data.toDataManager()
	readout(measure=False, setParameters=True, paramp=paramp, readAtRes=False, clearPulse=True, setPower=True, power=power)
	coil.setVoltage(samplePar['vCoil'],slewRate=0.2)
	mw_cav.turnOn()
	mw_qb.turnOff()
	frequencyLoop=SmartLoop(fcenter-fspan/2,fstep,fcenter+fspan/2,name='resonator frequency')
	time.sleep(1)
	for f in frequencyLoop:
		mw_cav.setFrequency(f)
		[amp,phase]=readout(measure=True,setParameters=False)
		data.set(f_GHz=f,amp=amp,phase=phase,columnOrder=['f_GHz','amp','phase'])
		data.commit()
	#frequencyRes=extremum(data['f'],data['amp'])[0]	
	print savePar
	if savePar:
		print 'parameters saved'
		savedDict=dict()
		savedDict.update(readoutPar)
		savedDict.update({'vCoil':samplePar['vCoil']})
		data.setParameters(savedDict)
	if fit:
		[y0,yAmp,x0,width], ampFit, ampFitGuess = fitLorentzian(data['amp'],x=data['f_GHz'])
		data.createColumn('ampFitGuess',ampFitGuess)
		data.createColumn('ampFit',ampFit)	
		print "f_Res = %f"%x0
		samplePar['f_Res']=0		
	if dataSave:
		data.savetxt()
	if fit:
		return x0

def qbSpecContinous(fcenter=1,fspan=1,fstep=0.1, powerQubit='',power='', data='', fit=True,autoPlot=True,autoClear=False,dataSave=True,savePar=True):
	if data=='':	
		data=Datacube('ResQubitCont')
	if autoPlot:
		data.plotInDataManager(names=["f_GHz","amp"],clear=autoClear,style='line')
		data.plotInDataManager(names=["f_GHz","ampFit"],clear=autoClear,style='line')
	data.toDataManager()
	if powerQubit=='':
		powerQubit=qubitSpecPar['specPower']
	# this only sets readout parameters
	readout(measure=False, setParameters=True, readAtRes=True, clearPulse=True, setPower=True, power=power)
	qb_att.setVoltage(powerQubit)
	coil.setVoltage(samplePar['vCoil'],slewRate=0.2)
	mw_qb.turnOn()
	pg_qb.clearPulse()
	start=0
	stop=setAWGPar(AWGParFast)
	pg_qb.addPulse(generatorFunction=qubitSpecPar['pulseType'],amplitude=qubitSpecPar['pulseHeight'],start=start, stop=stop,)
	#pg_qb.addMarker(channel=1,start1=start,stop1=stop)
	pg_qb.preparePulseSequence()
	#pg_qb.prepareMarkerSequence()
	pg_qb.sendPulseSequence()
	frequencyLoop=SmartLoop(fcenter-fspan/2,fstep,fcenter+fspan/2,name='qubit frequency')
	time.sleep(1)
	print 'qbSpecCont'
	for f in frequencyLoop:
		mw_qb.setFrequency(f)
		[amp,phase]=readout(measure=True,setParameters=False)
		data.set(f_GHz=f,amp=amp,phase=phase,columnOrder=['f_GHz','amp','phase'])
		data.commit()
	if fit:
		[y0,yAmp,x0,width], ampFit, ampFitGuess = fitLorentzian(data['amp'],x=data['f_GHz'])
		data.createColumn('ampFitGuess',ampFitGuess)
		data.createColumn('ampFit',ampFit)		
		x0=extremum(data['f_GHz'],data['amp'],minOrMax="min")[0]
		print "f_qb = %f"%x0
	if savePar:
		savedDict=dict()
		savedDict.update(readoutPar)
		savedDict.update(qubitSpecPar)
		savedDict.update({'vCoil':samplePar['vCoil']})
		data.setParameters(savedDict)
	if dataSave:
		data.savetxt()	
	if fit:
		return x0
			
def qbSpecPulsed(fcenter=1,fspan=1,fstep=0.1, powerQubit='', data='', fit=True,autoPlot=True,autoClear=False,dataSave=True,savePar=True):
	if data=='':	
		data=Datacube('QubitSpec')
		data.toDataManager()
	if autoPlot:
		data.plotInDataManager(names=["f_GHz","amp"],clear=autoClear,style='line')
		data.plotInDataManager(names=["f_GHz","ampFit"],clear=autoClear,style='line')
		data.toDataManager()
	if powerQubit=='':
		powerQubit=qubitSpecPar['specPower']
	readout(measure=False, setParameters=True, readAtRes=True, clearPulse=True, setPower=True, power='')
	qb_att.setVoltage(powerQubit)
	mw_qb.turnOn()
	pg_qb.clearPulse()
	start=setAWGPar(AWGParFast)-(readoutPar['length']+qubitSpecPar['sepFromReadout']+qubitSpecPar['pulseLength'])
	stop=setAWGPar(AWGParFast)-(readoutPar['length']+qubitSpecPar['sepFromReadout'])
	pg_qb.addPulse(generatorFunction=qubitSpecPar['pulseType'],amplitude=qubitSpecPar['pulseHeight'],start=start, stop=stop,)
	pg_qb.addMarker(channel=1,start1=start,stop1=stop)
	pg_qb.preparePulseSequence()
	pg_qb.prepareMarkerSequence()
	pg_qb.sendPulseSequence()
	frequencyLoop=SmartLoop(fcenter-fspan/2,fstep,fcenter+fspan/2,name='qubit frequency')
	time.sleep(1)
	print 'qbSpec'
	for f in frequencyLoop:
		mw_qb.setFrequency(f)
		[amp,phase]=readout(measure=True,setParameters=False)
		data.set(f_GHz=f,amp=amp,phase=phase,columnOrder=['f_GHz','amp','phase'])
		data.commit()
	if fit:
		[y0,yAmp,x0,width], ampFit, ampFitGuess = fitLorentzian(data['amp'],x=data['f_GHz'])
		data.createColumn('ampFitGuess',ampFitGuess)
		data.createColumn('ampFit',ampFit)		
		x0=extremum(data['f_GHz'],data['amp'],minOrMax="min")[0]
		print "f_qb = %f"%x0
	if savePar:
		savedDict=dict()
		savedDict.update(readoutPar)
		savedDict.update(qubitSpecPar)
		data.setParameters(savedDict)
	if dataSave:
		data.savetxt()
	if fit:
		return x0
		
def qbSpecPiPulsed(fcenter=1,fspan=1,fstep=0.1, powerQubit='', data='', fit=True,autoPlot=True,autoClear=False,dataSave=True,savePar=True):
	if data=='':	
		data=Datacube('QubitSpec')
		data.toDataManager()
	if autoPlot:
		data.plotInDataManager(names=["f_GHz","amp"],clear=autoClear,style='line')
		data.plotInDataManager(names=["f_GHz","ampFit"],clear=autoClear,style='line')
		data.toDataManager()
	if powerQubit=='':
		powerQubit=qubitTimeResPar['TimeResPower']
	readout(measure=False, setParameters=True, readAtRes=True, clearPulse=True, setPower=True, power='')
	qb_att.setVoltage(powerQubit)
	mw_qb.turnOn()
	pg_qb.clearPulse()
	start=setAWGPar(AWGParFast)-(readoutPar['length']+qubitTimeResPar['sepFromReadout']+qubitTimeResPar['pulseLength'])
	stop=setAWGPar(AWGParFast)-(readoutPar['length']+qubitTimeResPar['sepFromReadout'])
	pg_qb.addPulse(generatorFunction=qubitTimeResPar['pulseType'],amplitude=qubitTimeResPar['pulseHeight'],start=start, stop=stop,)
	pg_qb.addMarker(channel=1,start1=start,stop1=stop)
	pg_qb.preparePulseSequence()
	pg_qb.prepareMarkerSequence()
	pg_qb.sendPulseSequence()
	frequencyLoop=SmartLoop(fcenter-fspan/2,fstep,fcenter+fspan/2,name='qubit frequency')
	time.sleep(1)
	print 'qbSpec'
	for f in frequencyLoop:
		mw_qb.setFrequency(f)
		[amp,phase]=readout(measure=True,setParameters=False)
		data.set(f_GHz=f,amp=amp,phase=phase,columnOrder=['f_GHz','amp','phase'])
		data.commit()
	if fit:
		[y0,yAmp,x0,width], ampFit, ampFitGuess = fitLorentzian(data['amp'],x=data['f_GHz'])
		data.createColumn('ampFitGuess',ampFitGuess)
		data.createColumn('ampFit',ampFit)		
		x0=extremum(data['f_GHz'],data['amp'],minOrMax="min")[0]
		print "f_qb = %f"%x0
	if savePar:
		savedDict=dict()
		savedDict.update(readoutPar)
		savedDict.update(qubitTimeResPar)
		data.setParameters(savedDict)
	if dataSave:
		data.savetxt()
	if fit:
		return x0
		
def qbSpecPiPulsedWithResPulse(fcenter=1,fspan=1,fstep=0.1, powerQubit='', data='',cavPulseHeight='',cavPulseLength='', fit=True,autoPlot=True,autoClear=False,dataSave=True,savePar=True):
	if data=='':	
		data=Datacube('QubitSpec')
	if autoPlot:
		data.plotInDataManager(names=["f_GHz","amp"],clear=autoClear,style='line')
		data.plotInDataManager(names=["f_GHz","ampFit"],clear=autoClear,style='line')
	data.toDataManager()
	if powerQubit=='':
		powerQubit=qubitTimeResPar['TimeResPower']
	readout(measure=False, setParameters=True, readAtRes=True, clearPulse=True, setPower=True, power='')
	qb_att.setVoltage(powerQubit)
	mw_qb.turnOn()
	# prepare qubit pulse
	pg_qb.clearPulse()
	start=setAWGPar(AWGParFast)-(readoutPar['length']+qubitTimeResPar['sepFromReadout']+qubitTimeResPar['pulseLength'])
	stop=setAWGPar(AWGParFast)-(readoutPar['length']+qubitTimeResPar['sepFromReadout'])
	pg_qb.addPulse(generatorFunction=qubitTimeResPar['pulseType'],amplitude=qubitTimeResPar['pulseHeight'],start=start, stop=stop,)
	pg_qb.addMarker(channel=1,start1=start,stop1=stop)
	pg_qb.preparePulseSequence()
	pg_qb.prepareMarkerSequence()
	pg_qb.sendPulseSequence()
	
	# put pulse on resonator
	if cavPulseHeight =='':
		cavPulseHeight=qubitTimeResPar['resPulseHeight']
	if cavPulseLength =='':
		cavPulseLength=qubitTimeResPar['resPulseLength']
	resStart=setAWGPar(AWGParFast)-(readoutPar['length']+qubitTimeResPar['sepFromReadout']+cavPulseLength)
	resStop=setAWGPar(AWGParFast)-(readoutPar['length']+qubitTimeResPar['sepFromReadout'])
	pg_cav.addPulse(generatorFunction=qubitTimeResPar['pulseType'],frequency=readoutPar['freq'],amplitude=cavPulseHeight,start=resStart, stop=resStop,)
	if readoutPar['UseSwitch']:
		pg_cav.addMarker(channel=1,start1=resStart+
readoutPar['SwitchDelay'],stop1=resStop)	
	pg_cav.addMarker(channel=1,start1=start,stop1=stop)
	pg_cav.preparePulseSequence()
	pg_cav.prepareMarkerSequence()
	pg_cav.sendPulseSequence()
	
	frequencyLoop=SmartLoop(fcenter-fspan/2,fstep,fcenter+fspan/2,name='qubit frequency')
	time.sleep(1)
	print 'qbSpec'
	for f in frequencyLoop:
		mw_qb.setFrequency(f)
		[amp,phase]=readout(measure=True,setParameters=False)
		data.set(f_GHz=f,amp=amp,phase=phase,columnOrder=['f_GHz','amp','phase'])
		data.commit()
	if fit:
		[y0,yAmp,x0,width], ampFit, ampFitGuess = fitLorentzian(data['amp'],x=data['f_GHz'])
		data.createColumn('ampFitGuess',ampFitGuess)
		data.createColumn('ampFit',ampFit)		
		x0=extremum(data['f_GHz'],data['amp'],minOrMax="min")[0]
		print "f_qb = %f"%x0
	if savePar:
		savedDict=dict()
		savedDict.update(readoutPar)
		savedDict.update(qubitTimeResPar)
		data.setParameters(savedDict)
	if dataSave:
		data.savetxt()
	if fit:
		return x0
		
def rabiMeas(fQubit='',powerQubit='',start=0,stop=1000,step=10,data='',fit=True,autoPlot=True,autoClear=False,dataSave=True,savePar=True):
	if data=='':
		if pulseType=='gaussian':	
			data=Datacube('Rabi-gaussian')
		else:
			data=Datacube('Rabi')
		data.toDataManager()
	if autoPlot:
		data.plotInDataManager(names=["duration","amp"],clear=autoClear,style='line')
		data.plotInDataManager(names=["duration","ampFit"],clear=autoClear,style='line')
		data.toDataManager()
	mw_qb.turnOn()
	if powerQubit=='':	powerQubit=qubitTimeResPar['TimeResPower']
	if fQubit=='': fQubit=qubitTimeResPar['qbFreq']
	mw_qb.setFrequency(fQubit)
	qb_att.setVoltage(powerQubit)
	readout(measure=False, setParameters=True, readAtRes=True, clearPulse=True, setPower=True, power='')
	#coil.turnOn()
	time.sleep(1)
	print 'rabiMeas with fQubit=',mw_qb.frequency(),' VVAQubit=',qb_att.voltage()
	durations=SmartLoop(start,step,stop,name="durations")
	for duration in durations:
		pg_qb.clearPulse()
		## need to check which parameters the pulse generator wants for a gaussian pulse
		if qubitSpecPar['pulseType']=='gaussian':
			start=setAWGPar(AWGParFast)-(readoutPar['length']+qubitSpecPar['sepFromReadout']+qubitSpecPar['pulseLength'])
			stop=setAWGPar(AWGParFast)-(readoutPar['length']+qubitSpecPar['sepFromReadout'])
			pg_qb.addPulse(generatorFunction=qubitSpecPar['pulseType'],amplitude=qubitSpecPar['pulseHeight'],start=start, stop=stop,)
		else:	
			start=setAWGPar(AWGParFast)-(readoutPar['length']+qubitSpecPar['sepFromReadout']+duration)
			stop=setAWGPar(AWGParFast)-(readoutPar['length']+qubitSpecPar['sepFromReadout'])
			pg_qb.addPulse(generatorFunction=qubitSpecPar['pulseType'],amplitude=qubitSpecPar['pulseHeight'],start=start, stop=stop,)
		pg_qb.addMarker(channel=1,start1=start,stop1=stop)
		pg_qb.preparePulseSequence()
		pg_qb.prepareMarkerSequence()
		pg_qb.sendPulseSequence()
		time.sleep(0.1)
		[amp,phase]=readout(measure=True,setParameters=False)
		data.set(duration=duration,amp=amp,phase=phase,columnOrder=['duration','amp','phase'])
		data.commit()
	if fit:
		[y0,yAmp,t0,rabiPeriod],yfit,yFitGuess=fitCosine(data['amp'],x=data['duration'])
		data.createColumn("rabiFit",yfit)
		piRabi=rabiPeriod/2
		print "Pi pulse length = %f ns"%piRabi	 
	if savePar:
		savedDict=dict()
		savedDict.update(readoutPar)
		savedDict.update(qubitTimeResPar)
		savedDict.update(qubitSpecPar)
		data.setParameters(AWGParFast)	
	if dataSave:
		data.savetxt()
	if fit:
		return piRabi
		
def t1MeasFast(fQubit='',powerQubit='',data='',start=0,step=10,stop=1000,fit=True,autoPlot=True,autoClear=False,dataSave=True,debug=False,savePar=True):
	if powerQubit=='':	powerQubit=qubitTimeResPar['TimeResPower']
	if fQubit=='': fQubit=qubitTimeResPar['qbFreq']
	mw_qb.setFrequency(fQubit)
	qb_att.setVoltage(powerQubit)
	if data=='':	
		data=Datacube('T1fast')
	if autoPlot:
		data.plotInDataManager(names=["delay","amp"],clear=autoClear,style='line')
		data.plotInDataManager(names=["delay","ampFit"],clear=autoClear,style='line')
	data.toDataManager()
	print 't1Meas with fQubit=',mw_qb.frequency(),'VVAQubit=',qb_att.voltage()
	delays=SmartLoop(start,step,stop,name="durations")
	for delay in delays:
		pg_qb.clearPulse()
		## need to check which parameters the pulse generator wants for a gaussian pulse
		if qubitSpecPar['pulseType']=='gaussian':
			start=setAWGPar(AWGParFast)-(readoutPar['length']+qubitSpecPar['sepFromReadout']+samplePar['PiPulse']+delay)
			stop=setAWGPar(AWGParFast)-(readoutPar['length']+qubitSpecPar['sepFromReadout']+delay)
			pg_qb.addPulse(generatorFunction=qubitSpecPar['pulseType'],height=qubitSpecPar['pulseHeight'],center=start, sigma=stop,)
		else:	
			start=setAWGPar(AWGParFast)-(readoutPar['length']+qubitSpecPar['sepFromReadout']+samplePar['PiPulse']+delay)
			stop=setAWGPar(AWGParFast)-(readoutPar['length']+qubitSpecPar['sepFromReadout']+delay)
			pg_qb.addPulse(generatorFunction=qubitSpecPar['pulseType'],amplitude=qubitSpecPar['pulseHeight'],start=start, stop=stop,)
		pg_qb.addMarker(channel=1,start1=start,stop1=stop)
		pg_qb.preparePulseSequence()
		pg_qb.prepareMarkerSequence()
		pg_qb.sendPulseSequence()
		time.sleep(0.1)
		[amp,phase]=readout(measure=True,setParameters=False)
		data.set(delay=delay,amp=amp,phase=phase,columnOrder=['delay','amp','phase'])
		data.commit()
	if fit:			
		# fit exponential with reverseY=true
		[y0,yAmp,x0,t1],yFit,yFitGuess=fitT1(data['amp'],x=data['delay'],reverseY=True)
		data.createColumn("T1fit",yFit)
		print "T1 = %f"%t1

	if savePar:
		savedDict=dict()
		savedDict.update(readoutPar)
		savedDict.update(qubitTimeResPar)
		savedDict.update(AWGParFast)
		data.setParameters(savedDict)
	if dataSave:
		data.savetxt()
	if fit:
		return t1

def ramseyMeas(fQubit='',powerQubit='',detuning='',t1Estim=10000,start=0,stop=1000,step=10,data='',fit=True,autoPlot=True,autoClear=False,debug=False,dataSave=False,savePar=True):
	if data=='':	
		data=Datacube('Ramsey')
	if autoPlot:
		data.plotInDataManager(names=["duration","amp"],clear=autoClear,style='line')
		data.plotInDataManager(names=["duration","ampFit"],clear=autoClear,style='line')
	data.toDataManager()
	mw_qb.turnOn()
	##
	savedDict=dict()
	savedDict.update(readoutPar)
	savedDict.update(qubitTimeResPar)
	savedDict.update(AWGParFast)
	if powerQubit=='':	powerQubit=qubitTimeResPar['TimeResPower']
	if fQubit=='': fQubit=samplePar['f_qbit']
	if detuning =='': detuning=qubitTimeResPar['ramseyDetuning']
	mw_qb.setFrequency(fQubit+detuning)
	qb_att.setVoltage(powerQubit)
	savedDict.update({'qbFreq':fQubit+detuning})
	savedDict.update({'ramseyDetuning':detuning})
	savedDict.update({'TimeResPower':powerQubit})
	print 'ramseyMeas with fQubit=',mw_qb.frequency(),' VVAQubit=',qb_att.voltage()
	time.sleep(1)
	durations=SmartLoop(start,step,stop,name="durations")
	for duration in durations:
		pg_qb.clearPulse()
		## need to check which parameters the pulse generator wants for a gaussian pulse
		if qubitSpecPar['pulseType']=='gaussian':
			start=setAWGPar(AWGParFast)-(readoutPar['length']+qubitSpecPar['sepFromReadout']+samplePar['PiPulse']+delay)
			stop=setAWGPar(AWGParFast)-(readoutPar['length']+qubitSpecPar['sepFromReadout']+delay)
			pg_qb.addPulse(generatorFunction=qubitSpecPar['pulseType'],height=qubitSpecPar['pulseHeight'],center=start, sigma=stop,)
		else:	
			start1=setAWGPar(AWGParFast)-(readoutPar['length']+qubitSpecPar['sepFromReadout']+samplePar['PiPulse']+duration)
			stop1=setAWGPar(AWGParFast)-(readoutPar['length']+qubitSpecPar['sepFromReadout']+samplePar['PiPulse']/2+duration)
			pg_qb.addPulse(generatorFunction=qubitSpecPar['pulseType'],amplitude=qubitSpecPar['pulseHeight'],start=start1, stop=stop1)
			start2=setAWGPar(AWGParFast)-(readoutPar['length']+qubitSpecPar['sepFromReadout']+samplePar['PiPulse']/2)
			stop2=setAWGPar(AWGParFast)-(readoutPar['length']+qubitSpecPar['sepFromReadout'])
			pg_qb.addPulse(generatorFunction=qubitSpecPar['pulseType'],amplitude=qubitSpecPar['pulseHeight'],start=start2, stop=stop2)
		pg_qb.addMarker(channel=1,start1=0,stop1=10000)
		pg_qb.preparePulseSequence()
		pg_qb.prepareMarkerSequence()
		pg_qb.sendPulseSequence()
		#if qbPulse!=piPulse and duration==start: print 'Alert: pi/2 pulse =',qbPulse,' ns instead of ',piPulse/2,' ns'
		time.sleep(0.1)
		[amp,phase]=readout(measure=True,setParameters=False)
		data.set(duration=duration,amp=amp,phase=phase)
		data.commit()
	if fit:	
		ramseyPeriod=0
		t2=0
		[y0,yAmp,t0,ramseyPeriod,t2],yfit,yFitGuess=fitCosineExp(data['amp'],x=data['duration'])
		data.createColumn("ramseyFit",yfit)
		print "Ramsey period = ", ramseyPeriod," ns. T2 = ",t2, " ns."
	if savePar:
		savedDict=dict()
		savedDict.update(readoutPar)
		savedDict.update(qubitTimeResPar)
		savedDict.update(AWGParFast)
		data.setParameters(savedDict)
	if dataSave:
		data.savetxt()
	if fit:
		return [ramseyPeriod,t2]

###########################
###### Loop recipies  #####
###########################

def photonNumberSplittingAmp(data='',ampStart=0,ampStep=0.1, ampStop=1,fcenter=1,fspan=1,fstep=0.1,fit=False,autoPlot=False,autoClear=False,dataSave=True,savePar=True):
	if data=='':	
		data=Datacube('PhotonNumberSplitting')
	data.toDataManager()
	cavPulseAmpLoop=SmartLoop(ampStart,ampStep,ampStop,name='Cav pulse Amplitude')
	for height in cavPulseAmpLoop:
		print "Cav pulse height = %f"%height
		data.set(CavPulseheight=height,commit=True)
		child=Datacube('qbPiSpec_CavAmp = %f'%height)
		data.addChild(child)
		qbSpecPiPulsedWithResPulse(data=child,fcenter=fcenter,fspan=fspan,fstep=fstep,cavPulseHeight=height,fit=fit,autoPlot=autoPlot,autoClear=autoClear,dataSave=dataSave,savePar=savePar)
	data.savetxt()
	
def photonNumberSplittingLength(data='',cavLenStart=0,cavLenStep=10, cavLenStop=100,fcenter=1,fspan=1,fstep=0.1,fit=False,autoPlot=False,autoClear=False,dataSave=True,savePar=True):
	if data=='':	
		data=Datacube('PhotonNumberSplitting')
	data.toDataManager()
	cavPulseLengthLoop=SmartLoop(cavLenStart,cavLenStep,cavLenStop,name='Cav pulse Length')
	for length in cavPulseLengthLoop:
		print "Cav pulse length = %f"%length
		data.set(CavPulseLength=length,commit=True)
		child=Datacube('qbPiSpec_CavLength = %f'%length)
		data.addChild(child)
		qbSpecPiPulsedWithResPulse(data=child,fcenter=fcenter,fspan=fspan,fstep=fstep,cavPulseLength=length,fit=fit,autoPlot=autoPlot,autoClear=autoClear,dataSave=dataSave,savePar=savePar)
	data.savetxt()
	
	
def qbPiSpecVsCoilVolt(data='',VStart=0,VStep=0.1, VStop=1,fcenter=1,fspan=1,fstep=0.1,fit=False,autoPlot=False,autoClear=False,dataSave=True,savePar=True):
	if data=='':	
		data=Datacube('qbPiSpecVsCoilVolt')
	data.toDataManager()
	coilVoltageLoop=SmartLoop(VStart,VStep,VStop,name='Coil Voltage')
	for volts in coilVoltageLoop:
		print "Coil Voltage = %f"%volts
		data.set(CoilVoltage=volts,commit=True)
		coil.setVoltage(volts,slewRate=0.2)
		child=Datacube('qbPiSpec_vCoil = %f'%volts)
		data.addChild(child)
		qbSpecPiPulsed(data=child,fcenter=fcenter,fspan=fspan,fstep=fstep,fit=fit,autoPlot=autoPlot,autoClear=autoClear,dataSave=dataSave,savePar=savePar)
	data.savetxt()
	
def specVsCoilV1(data='',VStart=0,VStep=0.1, VStop=1,fcenter=1,fspan=1,fstep=0.1,fit=False,autoPlot=False,autoClear=False,dataSave=True,savePar=True):
	if data=='':	
		data=Datacube('specVsCoilV1')
	data.toDataManager()
	coilVoltageLoop=SmartLoop(VStart,VStep,VStop,name='Coil Voltage')
	for volts in coilVoltageLoop:
		child0=Datacube('Measurements at Coil Voltage = %f'%volts)
		print "Coil Voltage = %f"%volts
		data.set(CoilVoltage=volts,commit=True)
		coil.setVoltage(volts,slewRate=0.2)
		child1=Datacube('resSpec_vCoil = %f'%volts)
		data.addChild(child1)
		
		qbSpecPiPulsed(data=child,fcenter=fcenter,fspan=fspan,fstep=fstep,fit=fit,autoPlot=autoPlot,autoClear=autoClear,dataSave=dataSave,savePar=savePar)
	data.savetxt()
##################################
###### old and unused stuff  #####
##################################
def setAWGV2(sampTime_ns=1,triggerInterval=21000,ch1=True,ch1_pulseType='readout',ch1_pulse_ns=2500,ch1_amp=1,driveReadSep_ns=20,ch2=False,ch3=True,ch3_pulseType='gaussian',sigma_ns=20,ch4=False,debug=False): #nanoseconds per point
	samplRate=1.e9/sampTime_ns
	reprate=samplRate/20000.
	AWG.setRepetitionRate(reprate)
	AWG.setTriggerInterval(triggerInterval*1e-9)# has to be specidfied in seconds
	ch1Return=[]
	ch2Return=[]
	ch3Return=[]
	ch4Return=[]
	if ch1:
		if ch1_pulseType=='readout':
			ch1_pulse=abs(round(ch1_pulse_ns/sampTime_ns))
			wf1=waveGen.readoutWaveform(ch1_pulse,height=ch1_amp)
			waveGen.send2AWG(wf1)
			waveGen.loadWF2Channel(1,wf1[2])
		elif ch1_pulseType=='readout_switch':
			# for a 30 ns riseTime switch
			switchRiseBuffer=abs(round(30/sampTime_ns))
			ch1_pulse=abs(round(ch1_pulse_ns/sampTime_ns))
			wf1=waveGen.readoutSwitchWaveform(ch1_pulse,height=ch1_amp,switchRiseBuffer=switchRiseBuffer)
			waveGen.send2AWG(wf1)
			waveGen.loadWF2Channel(1,wf1[2])
		else:
			print 'pulsetype for channel 1 not defined in setAWGV2'
		ch1Return=ch1_pulse*sampTime_ns,
	if ch2:
		print 'pulsetype for channel 2 not defined in setAWGV2'
		ch2Return=[]
	if ch3:
		if ch3_pulseType=='gaussian':
			markerOffset_ns=-100
			center_ns=20000*sampTime_ns-ch1_pulse_ns-driveReadSep_ns-3*sigma_ns
			driveReadSep=abs(round(driveReadSep_ns/sampTime_ns))
			markerOffset=round(markerOffset_ns/sampTime_ns)
			center=abs(round(center_ns/sampTime_ns))
			sigma=abs(round(sigma_ns/sampTime_ns))
			wf3=waveGen.gaussianPulseWaveform(center,sigma,name='gaussian,sigma=%f'%sigma,markerOffset2=markerOffset)
			waveGen.send2AWG(wf3)
			waveGen.loadWF2Channel(3,wf3[2])	
		else:
			print 'pulsetype for channel 3 not defined in setAWGV2'
		ch3Return=sigma*sampTime_ns, center*sampTime_ns, ch1_pulse*sampTime_ns, driveReadSep*sampTime_ns
	if ch4:
		print 'pulsetype for channel 4 not defined in setAWGV2'
		ch4Return=[]
	
	return concatenate([ch1Return,ch2Return,ch3Return,ch4Return])

# this function should be deleted if the new one works 
def measureIQOffOnOrginal(nLoops=1,wantedChannels=3, firstSlice=None,secondSlice=None,startMargin=0,middleMargin=0.1,stopMargin=0,averageOverSequence=False,convertToAmpPhase=False,OnBeforeOff=False):
	# acquire and transfer the sequence of traces for the selected channels
	acqiris.AcquireTransfer(transferAverage=False,nLoops=nLoops,wantedChannels=wantedChannels)
	time.sleep(0.1)
	nbrSamplesPerSeg=acqiris.getLastWave()['nbrSamplesPerSeg']
	if firstSlice==None:
		if secondSlice==None:
			index1=int(nbrSamplesPerSeg/2*(1+middleMargin/2))
			if index1 <0 : index1=1
			if index1 > nbrSamplesPerSeg-1 : index1=nbrSamplesPerSeg-2
			index2=int(nbrSamplesPerSeg*(1-stopMargin))
			if index2 < index1: index2=index1+1
			if index2 > nbrSamplesPerSeg-1 : index2=nbrSamplesPerSeg-1
			secondSlice=slice(index1,index2)
		index1=int(nbrSamplesPerSeg*startMargin)
		if index1 <0 : index1=0
		if index1> secondSlice.start-1: index1 = secondSlice.start-1
		index2=int(secondSlice.start- middleMargin*nbrSamplesPerSeg)
		if index2 < index1: index2=index1+1
		if index2 > secondSlice.start:index2=secondSlice.start-1
		firstSlice=slice(index1,index2)
	elif secondSlice==None:
		index1=int(firstSlice.stop+ middleMargin*nbrSamplesPerSeg)
		if index1 <= firstSlice.stop : index1=firstSlice.stop+1
		if index1 > nbrSamplesPerSeg-1 : index1=nbrSamplesPerSeg-1
		index2=int(nbrSamplesPerSeg*(1-stopMargin))
		if index2<index1: index2=index1
		if index2 > nbrSamplesPerSeg-1 : index2=nbrSamplesPerSeg-1
		secondSlice=slice(index1,index2)
	
	def getBoxcarMeans(slic=slice(0,-1),wantedChannels=3,averageOverSequence=False):
		commandString="DLLMath1Module.boxcarOfLastWaveForms(targettedWaveform="+str(wantedChannels)+",sliceArray="+str([slic,slic,slic,slic])+")"
		acqiris(commandString)		# calculate the mean of each trace in the sequence COMPLETE HERE
		boxcarMeans= acqiris("DLLMath1Module.boxcarMean")	# get the sequence of boxcarMeans for the selected channels
		# get the indexes of selected channels	
		indexes= [i for i,x in enumerate([1&wantedChannels!=0,2&wantedChannels!=0,4&wantedChannels!=0,8&wantedChannels!=0]) if x ==True]
		boxcarMeans=[boxcarMeans[indexes[0]],boxcarMeans[indexes[1]]] # keep only the first and second selected channels
		if averageOverSequence:								 # average over sequence if requested
			boxcarMeans=[numpy.mean(boxcarMeans[0]),numpy.mean(boxcarMeans[1])]
		return boxcarMeans
	
	boxcarMeansA=getBoxcarMeans(slic=firstSlice,wantedChannels=wantedChannels,averageOverSequence=averageOverSequence)
	boxcarMeansB=getBoxcarMeans(slic=secondSlice,wantedChannels=wantedChannels,averageOverSequence=averageOverSequence)
	channels=[boxcarMeansB[0]-boxcarMeansA[0],boxcarMeansB[1]-boxcarMeansA[1],boxcarMeansA[0],boxcarMeansA[1],boxcarMeansB[0],boxcarMeansB[1]]
	if OnBeforeOff:
		channels[0]=-channels[0]
		channels[1]=-channels[1]
	
	if convertToAmpPhase:									 # convert I and Q into Amp and Phase
		channels=[sqrt((channels[0])**2+(channels[1])**2),arctan(channels[1]/channels[0]),sqrt((channels[2])**2+(channels[3])**2),arctan(channels[3]/channels[2]),sqrt((channels[4])**2+(channels[5])**2),arctan(channels[5]/channels[4])]		# calculate amplitude and phase
	# returns [IB-IA,QB-QA,IA,QA,IB,QB] or [AmpCor, phiCor,] or [array([(I2-I1)1,(I2-I1)2,(I2-I1)3,...]),array([(Q2-Q1)1,(Q2-Q1)2,(Q2-Q1)3,...])] or  ...
	return channels


####################################################
##### Testing area !!!!  MUST BE COMMENTED OUT #####
####################################################
"""
##
pg_qb=Manager().getInstrument('pg_qb')
pg_qb.clearPulse()
pg_qb.addPulse(generatorFunction=qubitSpecPar['pulseType'],frequency=5,amplitude=qubitSpecPar['pulseHeight'],start=1000, stop=3000,)
pg_qb.addMarker(channel=1,start1=0,stop1=9000)
pg_qb.preparePulseSequence()
pg_qb.prepareMarkerSequence()
pg_qb.sendPulseSequence()
##
print qubitSpecPar['pulseType']
print pg_qb.markersChannels
##
pulseSequenceArray=zeros(20000)
marker=zeros(20000)
pg_qb._AWG.loadRealWaveform(pulseSequenceArray, channel=3,markers=marker,waveformName='name1')
##
pulseGenerator=Manager().getInstrument('pg_cav')
pulseGenerator.clearPulse()
pulseGenerator.clearMarkersList()
pulseGenerator.addPulse(generatorFunction="square",frequency=mw_cav.frequency(),amplitude=1.0,start=8000, stop=10000, applyCorrections=False,phase=pi/4)
pulseGenerator.addMarker(channel=1,start1=6000,stop1=10000)
pulseGenerator.addMarker(channel=1,start1=4000,stop1=5000)
pulseGenerator.addMarker(channel=2,start1=4000,stop1=5000)
pulseGenerator.preparePulseSequence()
pulseGenerator.prepareMarkerSequence()
pulseGenerator.sendPulseSequence()
##
pulseGenerator.clearMarkersList()
print pulseGenerator.markersChannels
##
print pulseGenerator.markersList1
print pulseGenerator.markersList2
##
readoutPar['method'](nLoops=readoutPar['nLoops'],averageOverSequence=True,convertToAmpPhase=True,**readoutPar['kwargs'])
measureIQOffOn(nLoops=1,wantedChannels=3,averageOverSequence=False,convertToAmpPhase=False,**readoutPar['kwargs'])
##
"""


