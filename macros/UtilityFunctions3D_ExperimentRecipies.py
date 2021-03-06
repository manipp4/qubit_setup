#########################
## Experiment Recipies ##
#########################
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
def measureIQ(nLoops=1,wantedChannels=3,iOffset=0,qOffset=0,transferAverage=True,convertToAmpPhase=False,**kwargs):
	# acquire and transfer the sequence of traces for the selected channels, transferAverage=True means averageo over all the segments. i.e. n traces to 1 trace
	acqiris.AcquireTransfer(transferAverage=transferAverage,nLoops=nLoops,wantedChannels=wantedChannels)
	time.sleep(0.1)
	acqiris("DLLMath1Module.meanOfLastWaveForms("+str(wantedChannels)+")")		# calculate the mean of each trace in the sequence and store it in DLLMath1Module.mean
	channels= acqiris("DLLMath1Module.mean")	# get the sequence of means for the selected channels
	# get the indexes of selected channels
	indexes= [i for i,x in enumerate([1&wantedChannels!=0,2&wantedChannels!=0,4&wantedChannels!=0,8&wantedChannels!=0]) if x ==True]
	channels=[channels[indexes[0]],channels[indexes[1]]] # keep only the first and second selected channels as I and Q
	if iOffset!=0 : channels[0]=channels[0]-iOffset  	 # subtract I and Q offset if necessary
	if qOffset!=0 : channels[1]=channels[1]-qOffset
	averageOverSequence=kwargs['averageOverSequence']
	if not transferAverage and averageOverSequence:								 # average over sequence if requested
		channels=[numpy.mean(channels[0]),numpy.mean(channels[1])]
	if convertToAmpPhase:									 # convert I and Q into Amp and Phase
		channels=[sqrt((channels[0])**2+(channels[1])**2),arctan(channels[1]/channels[0])]		# calculate amplitude and phase
	# returns [I,Q] or [Amp, phi] or [array([I1,I2,I3,...],array([Q1,Q2,Q3,...])] or  [array([A1,A2,A3,...],array([phi1,phi2,phi3,...])]
	return channels 
def measureIQav(nLoops=1,wantedChannels=3,iOffset=0,qOffset=0,convertToAmpPhase=False,**kwargs):
	channels=measureIQ(nLoops=nLoops,wantedChannels=wantedChannels,iOffset=iOffset,qOffset=qOffset,transferAverage=True,convertToAmpPhase=convertToAmpPhase,**kwargs)
	return [channels[0][0],channels[1][0]]
def measureIQOffOn(nLoops=1,wantedChannels=3,transferAverage=False,convertToAmpPhase=False,**kwargs):
	# set values from keywords
	firstSlice=kwargs['firstSlice']
	secondSlice=kwargs['secondSlice']
	startMargin=kwargs['startMargin']
	middleMargin=kwargs['middleMargin']
	stopMargin=kwargs['stopMargin']
	OnBeforeOff=kwargs['OnBeforeOff']
	averageOverSequence=kwargs['averageOverSequence']
	# acquire and transfer the sequence of traces for the selected channels
	acqiris.AcquireTransfer(transferAverage=transferAverage,nLoops=nLoops,wantedChannels=wantedChannels)
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
def measureIQavOffOn(nLoops=1,wantedChannels=3,convertToAmpPhase=False,**kwargs):
	channels=measureIQOffOn(nLoops=nLoops,wantedChannels=wantedChannels,transferAverage=True,convertToAmpPhase=convertToAmpPhase,**kwargs)
	return channels
def adaptStepFunc1(adaptiveLoop,fSpan='',deltafMax='',deltafMin=''):
	if fSpan=='': 
		fSpan=qubitSpecPar['specfSpan']
	if deltafMax=='': 
		deltafMax=adaptStepFunc1Par['deltafMax']
	if deltafMin=='': 
		deltafMin=adaptStepFunc1Par['deltafMin']	
	stepMin=adaptStepFunc1Par['stepMin']
	stepMax=adaptStepFunc1Par['stepMax']	
	fbValues=adaptiveLoop.feedBackValues()
	if len(fbValues)>=2:
		step=adaptiveLoop.getStep()
		dir=1.0;
		if step<0:
			dir=-1.0
		deltaF=abs(fbValues[-1]-fbValues[-2])
		newStep=step
		if deltaF > deltafMax:
			newStep=max(abs(step/2.),stepMin)*dir
			adaptiveLoop.setStep(newStep)
		elif deltaF < deltafMin:
			newStep=min(abs(step*2),stepMax)*dir
			adaptiveLoop.setStep(newStep)
def getSquarePulseLength(channel):
	wfName=AWG.waveform(channel)
	wf=AWG.getWaveform(wfName)._data
	if max(wf)==min(wf):pulse_ns=0
	else:
		pulsePts=(wf==max(wf)).sum()
		pulse_ns=pulsePts*AWG.repetitionRate()*20000*1e-9
	return pulse_ns
#################################
## dictionaries for parameters ##
#################################
#a=readoutPar['subDict']
#print type(a)
#print type(readoutPar['subDict'])
##
readoutParSubDict1=dict()
readoutParSubDict1['method']=measureIQavOffOn
readoutParSubDict1['trigDelay']=-1e-5
readoutParSubDict1['samples']=800
readoutParSubDict1['segments']=140
readoutParSubDict1['nLoops']=35
readoutParSubDict1['pulseLength']=10000
readoutParSubDict1['pulseHeight']=1

readoutParSubDict2=dict()
readoutParSubDict2['method']=measureIQav
readoutParSubDict2['trigDelay']=3e-7
readoutParSubDict2['samples']=50
readoutParSubDict2['segments']=200
readoutParSubDict2['nLoops']=100
readoutParSubDict2['pulseLength']=3000
readoutParSubDict2['pulseHeight']=1

readoutPar=dict()
readoutPar['subDict']=readoutParSubDict2
readoutPar['freq']=7.3719
readoutPar['resVVAVoltage']=4.6
readoutPar['freq_sb']=0
readoutPar['setPulse']=True
readoutPar['setAcqiris']=True
readoutPar['UseSwitch']=False
readoutPar['SwitchDelay']=-200
readoutPar['kwargs']={'firstSlice':slice(0,375),'secondSlice':slice(422,799),'startMargin':0,'middleMargin':0.1,'stopMargin':0,'OnBeforeOff':False,'averageOverSequence':True}
readoutPar['useParamp']=False
readoutPar['parampCoil']=-20.0
readoutPar['parampPower']=4.4


ResSpecPar=dict()
ResSpecPar['ResSpecfcenter']=7.3
ResSpecPar['ResSpecfSpan']=0.03
ResSpecPar['ResSpecfstep']=0.0005
ResSpecPar['ResSpecPower']=1.9
ResSpecPar['ResPulseType']="square"
ResSpecPar['ResPulseHeight']=1
ResSpecPar['ResPulseLength']=17000


qubitSpecPar=dict()
qubitSpecPar['specfcenter']=8
qubitSpecPar['specfSpan']=0.5
qubitSpecPar['specfstep']=0.001
qubitSpecPar['qbVVAVoltage']=0.7
qubitSpecPar['pulseType']="square"
qubitSpecPar['pulseHeight']=1
qubitSpecPar['pulseLength']=5000
qubitSpecPar['sepFromReadout']=10

samplePar=dict()
samplePar['f_Res']=7.3467
samplePar['f_qb']=6.09668
samplePar['piPulse']=288
samplePar['gaussianPiPulse']=228
samplePar['T1']=1000
samplePar['vCoil']=-0

qubitTimeResPar=dict()
qubitTimeResPar['TimeResqbVVAVoltage']=1.6
qubitTimeResPar['qbFreq']=samplePar['f_qb']
qubitTimeResPar['pulseType']="square"
qubitTimeResPar['pulseHeight']=1
qubitTimeResPar['pulseLength']=samplePar['piPulse']
qubitTimeResPar['gaussianSigma']=1500
qubitTimeResPar['gaussianCutOff']=2 #in units of sigma
qubitTimeResPar['sepFromReadout']=10
qubitTimeResPar['ramseyDetuning']=+0.001
qubitTimeResPar['resPulseHeight']=1.0
qubitTimeResPar['resPulseLength']=3000
qubitTimeResPar['rabiStart']=0
qubitTimeResPar['rabiStop']=1000
qubitTimeResPar['rabiStep']=25
qubitTimeResPar['T1Start']=0
qubitTimeResPar['T1Stop']=4000
qubitTimeResPar['T1Step']=80

AWGParFast=dict()
AWGParFast['sampTime_ns']=1
AWGParFast['triggerInterval']=27000
AWGParFast['AWGnbrOfPoints']=20000

adaptStepFunc1Par=dict()
adaptStepFunc1Par['deltafMax']=0.04
adaptStepFunc1Par['deltafMin']=0.01
adaptStepFunc1Par['stepMin']=0.004
adaptStepFunc1Par['stepMax']=1

###########################################
### functions that use the dictionaries ###
###########################################
def setReadout(frequency=None,resVVAVoltage=None, useParamp=None, parSubDict=None, setPulse=None, pulseHeight=None, pulseLength=None, clearPulse=True, setAcqiris=None, trigDelay=None, samples=None, segments=None):
	# This method uses the readout method specified in the readout parameter dictionary. If onlyMeasure is true the readout is performed with the current parameters. If onlyMeasure is 	false the readout pulse parameters are applied to the AWG. readAtRes determines if the current readout frequency should be used(false) or the one given in the dictionary(true)
	if frequency!=None:
		if isinstance(frequency,str):
			frequency=readoutPar['freq']
		mw_cav.setFrequency(frequency)
	if resVVAVoltage!=None:
		if isinstance(resVVAVoltage,str):
			resVVAVoltage=readoutPar['resVVAVoltage']
		res_att.setVoltage(resVVAVoltage)	
	if useParamp!=None:
		if not isinstance(useParamp,bool):
			useParamp=readoutPar['useParamp']
		if useParamp:
			paraCoil.setVoltage(readoutPar['parampCoil'],slewRate=0.3)
			pumpfreq=2*readoutPar['freq']-0.000011
			mw_par.setFrequency(pumpfreq)
			mw_par.setPower(readoutPar['parampPower'])	
			mw_par.turnOn()
		else:
			mw_par.turnOff()
	if parSubDict==None: parSubDict=readoutPar['subDict']
	# setting the readout waveform
	if setPulse!=None:
		if not isinstance(setPulse,bool):
			setPulse=readoutPar['setPulse']
		if setPulse:
			if pulseHeight==None: pulseHeight=parSubDict['pulseHeight']
			if pulseLength==None: pulseLength=parSubDict['pulseLength']
			lenOfWaveform=setAWGPar(AWGParFast) ## sets the awg parameters and returns the number of points for a waveform
			if clearPulse:
				pg_cav.clearPulse()
			pg_cav.addPulse(generatorFunction="square",frequency=mw_cav.frequency(),amplitude=pulseHeight,start=lenOfWaveform-pulseLength, stop=lenOfWaveform,)
			if readoutPar['UseSwitch']:
				pg_cav.addMarker(channel=1,start1=0,stop1=lenOfWaveform-pulseLength)
				pg_cav.addMarker(channel=2,start1=lenOfWaveform-pulseLength+readoutPar['SwitchDelay'],stop1=lenOfWaveform)
			else :
				pg_cav.addMarker(channel=1,start1=0,stop1=lenOfWaveform-pulseLength)
			pg_cav.preparePulseSequence()
			pg_cav.prepareMarkerSequence()
			pg_cav.sendPulseSequence()
	if setAcqiris!=None:
		print 'setting Acqiris parameters'
		if not isinstance(setAcqiris,bool):
			setAcqiris=readoutPar['setAcqiris']
		if setAcqiris:
			if trigDelay==None: trigDelay=parSubDict['trigDelay']
			if samples==None: samples=parSubDict['samples']
			if segments==None: segments=parSubDict['segments']
			acqiris.setParameter('trigDelay',trigDelay)
			acqiris.setParameter('samples',samples)
			acqiris.setParameter('segments',segments)      	
def readout(method=None,nLoops=None,setReadout=False,**kwargs):
	if method==None: method=readoutPar['subDict']['method']
	if nLoops==None: nLoops=readoutPar['subDict']['nLoops']
	if setReadout: setReadout(kwargs)
	dataPoint=method(nLoops=nLoops,convertToAmpPhase=True,**readoutPar['kwargs'])
	return [dataPoint[0],dataPoint[1]]  # some readout methods return more that two values. Here the number of values returned is fixed to the first two values given by the method
def getReadoutParameters():
	returnDict=dict()
	readoutParameters={'readoutFrequency':mw_cav.frequency(),'resVVAVoltage':res_att.voltage(),'ParampOn':mw_par.parameters(),'ReadoutpulseLength':getSquarePulseLength(1),'ReadoutMethod':readoutPar['subDict']['method'],'readoutKwargs':readoutPar['kwargs']}
	returnDict.update(readoutParameters)
	returnDict.update(AWG.parameters())
	returnDict.update(acqiris.parameters())
	return returnDict
def resSpec(fcenter='',fspan='',fstep='',data='',setReadoutPar=False,useDict=False,parSubDict=None,resVVAVoltage=None,useParamp=None,coilVoltage=None,setPulse=None,setAcqiris=None, fit=True,autoPlot=True,autoClear=False,dataSave=True,savePar=True):
	if data=='':	
		data=Datacube('ResSpec')
		data.toDataManager()
	if autoPlot:
		data.plotInDataManager(names=["f_GHz","amp"],clear=autoClear,style='line')
		data.plotInDataManager(names=["f_GHz","ampFit"],clear=autoClear,style='line')
		data.toDataManager()
	if fcenter=='':fcenter=ResSpecPar['ResSpecfcenter']
	if fspan=='':fspan=ResSpecPar['ResSpecfSpan']
	if fstep=='':fstep=ResSpecPar['ResSpecfstep']
	if setReadoutPar:
		if useDict:
			setReadout(resVVAVoltage='dictValue', useParamp='dictValue', setPulse='dictValue', setAcqiris='dictValue')
		else:
			setReadout(resVVAVoltage=resVVAVoltage, useParamp=useParamp, setPulse=setPulse, setAcqiris=setAcqiris, parSubDict=parSubDict)
	if coilVoltage!=None:
		coil.setVoltage(coilVoltage,slewRate=0.2)
	mw_cav.turnOn()
	mw_qb.turnOff()
	frequencyLoop=SmartLoop(fcenter-fspan/2,fstep,fcenter+fspan/2,name='resonator frequency')
	time.sleep(1)
	for f in frequencyLoop:
		mw_cav.setFrequency(f)
		[amp,phase]=readout()
		data.set(f_GHz=f,amp=amp,phase=phase,columnOrder=['f_GHz','amp','phase'])
		data.commit()
	#frequencyRes=extremum(data['f'],data['amp'])[0]	
	data.createCol(name='power',values=data['amp']**2)
	toReturn=[]
	print savePar
	if savePar:
		print 'parameters saved'
		savedDict=dict()
		savedDict.update(getReadoutParameters())
		savedDict.update({'vCoil':samplePar['vCoil']})
		data.setParameters(savedDict)
	if fit:
		[y0,yAmp,x0,width], ampFit, ampFitGuess = fitLorentzian(data['power'],x=data['f_GHz'])
		data.createColumn('ampFitGuess',ampFitGuess)
		data.createColumn('ampFit',ampFit)	
		print "f_Res = %f"%x0
		samplePar['f_Res']=x0
		toReturn.append(['f_Res',x0])		
	if dataSave:
		data.savetxt()
	return toReturn
def qbSpecContinuous(fcenter='',fspan='',fstep='', data='',setReadoutPar=False,useDict=False, parSubDict=None, qbVVAVoltage=None, resFrequency=None, resVVAVoltage=None, coilVoltage=None, useParamp=None, setPulse=None,setAcqiris=None,fit=True,autoPlot=True,autoClear=False,dataSave=True,savePar=False):
	if data=='':	
		data=Datacube('ResQubitCont')
	if autoPlot:
		data.plotInDataManager(names=["f_GHz","amp"],clear=autoClear,style='line')
		data.plotInDataManager(names=["f_GHz","ampFit"],clear=autoClear,style='line')
	data.toDataManager()
	if qbVVAVoltage==None:qbVVAVoltage=qubitSpecPar['qbVVAVoltage']
	if fcenter=='':fcenter=qubitSpecPar['specfcenter']
	if fspan=='':fspan=qubitSpecPar['specfSpan']
	if fstep=='':fstep=qubitSpecPar['specfstep']
	if resFrequency==None: resFrequency=samplePar['f_Res']
	# this only sets readout parameters. 'dictValue' has no defined value. if given an arbitrary string setReadout will take the value from the dictionary
	if setReadoutPar:
		if useDict:
			setReadout(frequency='dictValue', resVVAVoltage='dictValue', useParamp='dictValue', setPulse='dictValue', setAcqiris='dictValue')
		else:
			setReadout(frequency=resFrequency, resVVAVoltage=resVVAVoltage, useParamp=useParamp, setPulse=setPulse, setAcqiris=setAcqiris, parSubDict=parSubDict)
	qb_att.setVoltage(qbVVAVoltage)
	mw_qb.turnOn()
	if coilVoltage!=None:
		coil.setVoltage(coilVoltage,slewRate=0.2)
	# set the qubit pulses 
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
		[amp,phase]=readout()
		data.set(f_GHz=f,amp=amp,phase=phase,columnOrder=['f_GHz','amp','phase'])
		data.commit()
	data.createCol(name='power',values=data['amp']**2)
	toReturn=[]
	if fit:
		[y0,yAmp,x0,width], ampFit, ampFitGuess = fitLorentzian(data['amp'],x=data['f_GHz'])
		data.createColumn('ampFitGuess',ampFitGuess)
		data.createColumn('ampFit',ampFit)		
		x0=extremum(data['f_GHz'],data['amp'],minOrMax="min")[0]
		print "f_qb = %f"%x0
		samplePar['f_qb']=x0
		toReturn.append(['f_qb',x0])	
	if savePar:
		savedDict=dict()
		savedDict.update(readoutPar)
		savedDict.update(qubitSpecPar)
		savedDict.update({'vCoil':coil.voltage()})
		data.setParameters(savedDict)
	if dataSave:
		data.savetxt()	
	return toReturn		
def qbSpecPulsed(fcenter='',fspan='',fstep='', data='',setReadoutPar=False,useDict=False, parSubDict=None, qbVVAVoltage=None, qbPulseLength=None, resFrequency=None, resVVAVoltage=None, coilVoltage=None, useParamp=None, setPulse=None,setAcqiris=None,fit=True,autoPlot=True,autoClear=False,dataSave=True,savePar=False):
	if data=='':	
		data=Datacube('ResQubitPulsed')
	if autoPlot:
		data.plotInDataManager(names=["f_GHz","amp"],clear=autoClear,style='line')
		data.plotInDataManager(names=["f_GHz","ampFit"],clear=autoClear,style='line')
	data.toDataManager()
	if qbVVAVoltage==None:qbVVAVoltage=qubitSpecPar['qbVVAVoltage']
	if fcenter=='':fcenter=qubitSpecPar['specfcenter']
	if fspan=='':fspan=qubitSpecPar['specfSpan']
	if fstep=='':fstep=qubitSpecPar['specfstep']
	if resFrequency==None: resFrequency=samplePar['f_Res']
	print resFrequency
	qb_att.setVoltage(qbVVAVoltage)
	# this only sets readout parameters. 'dictValue' has no defined value. if given an arbitrary string setReadout will take the value from the dictionary
	if setReadoutPar:
		print 'place1'
		if useDict:
			setReadout(frequency='dictValue', resVVAVoltage='dictValue', useParamp='dictValue', setPulse='dictValue', setAcqiris='dictValue')
			print 'place2'
		else:
			setReadout(frequency=resFrequency, resVVAVoltage=resVVAVoltage, useParamp=useParamp, setPulse=setPulse, setAcqiris=setAcqiris, parSubDict=parSubDict)
			print 'place3'
	mw_qb.turnOn()
	if coilVoltage!=None:
		coil.setVoltage(coilVoltage,slewRate=0.2)
	# set the qubit pulses
	if qbPulseLength==None:qbPulseLength=qubitSpecPar['pulseLength']	
	pg_qb.clearPulse()
	start=setAWGPar(AWGParFast)-(readoutPar['subDict']['pulseLength']+qubitSpecPar['sepFromReadout']+qbPulseLength)
	stop=setAWGPar(AWGParFast)-(readoutPar['subDict']['pulseLength']+qubitSpecPar['sepFromReadout'])
	pg_qb.addPulse(generatorFunction=qubitSpecPar['pulseType'],amplitude=qubitSpecPar['pulseHeight'],start=start, stop=stop,)
	pg_qb.addMarker(channel=1,start1=start,stop1=stop)
	pg_qb.preparePulseSequence()
	pg_qb.prepareMarkerSequence()
	pg_qb.sendPulseSequence() 
	frequencyLoop=SmartLoop(fcenter-fspan/2,fstep,fcenter+fspan/2,name='qubit frequency')
	time.sleep(1)
	print 'qbSpecPulsed'
	for f in frequencyLoop:
		mw_qb.setFrequency(f)
		[amp,phase]=readout()
		data.set(f_GHz=f,amp=amp,phase=phase,columnOrder=['f_GHz','amp','phase'])
		data.commit()
	data.createCol(name='power',values=data['amp']**2)
	toReturn=[]
	if fit:
		[y0,yAmp,x0,width], ampFit, ampFitGuess = fitLorentzian(data['amp'],x=data['f_GHz'])
		data.createColumn('ampFitGuess',ampFitGuess)
		data.createColumn('ampFit',ampFit)		
		x0=extremum(data['f_GHz'],data['amp'],minOrMax="min")[0]
		print "f_qb = %f"%x0
		samplePar['f_qb']=x0
		toReturn.append(['f_qb',x0])	
	if savePar:
		savedDict=dict()
		savedDict.update(readoutPar)
		savedDict.update(qubitSpecPar)
		savedDict.update({'vCoil':coil.voltage()})
		data.setParameters(savedDict)
	if dataSave:
		data.savetxt()	
	return toReturn
	
# Not ready
def qbSpecPiPulsed(fcenter='',fspan='',fstep='', powerQubit='', data='', fit=True,autoPlot=True,autoClear=False,dataSave=True,savePar=True):
	if data=='':	
		data=Datacube('QubitSpec')
		data.toDataManager()
	if autoPlot:
		data.plotInDataManager(names=["f_GHz","amp"],clear=autoClear,style='line')
		data.plotInDataManager(names=["f_GHz","ampFit"],clear=autoClear,style='line')
		data.toDataManager()
	if powerQubit=='':	powerQubit=qubitTimeResPar['TimeResPower']
	if fcenter=='':fcenter=qubitSpecPar['specfcenter']
	if fspan=='':fspan=qubitSpecPar['specfSpan']
	if fstep=='':fstep=qubitSpecPar['specfstep']
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
	toReturn=[]
	if fit:
		[y0,yAmp,x0,width], ampFit, ampFitGuess = fitLorentzian(data['amp'],x=data['f_GHz'])
		data.createColumn('ampFitGuess',ampFitGuess)
		data.createColumn('ampFit',ampFit)		
		x0=extremum(data['f_GHz'],data['amp'],minOrMax="min")[0]
		print "f_qb = %f"%x0
		toReturn.append(['f_qb',x0])
	if savePar:
		savedDict=dict()
		savedDict.update(readoutPar)
		savedDict.update(qubitTimeResPar)
		data.setParameters(savedDict)
	if dataSave:
		data.savetxt()
	return toReturn
# Not Ready		
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
		pg_cav.addMarker(channel=1,start1=resStart+readoutPar['SwitchDelay'],stop1=resStop)	
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
	return toReturn

		
def rabiMeas(fQubit='',qbVVAVoltage='',pulseType=None, piEst=None,rabiStart=None, rabiStop=None, rabiStep=None, cutOff=None, data='',setReadoutPar=False,useDict=False, useParamp=None, parSubDict=None, setPulse=None,setAcqiris=None, resFrequency=None, resVVAVoltage=None, fit=True,autoPlot=True,autoClear=False,dataSave=True,savePar=True):
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
	if qbVVAVoltage=='':qbVVAVoltage=qubitTimeResPar['TimeResqbVVAVoltage']
	if fQubit=='': fQubit=samplePar['f_qb']
	mw_qb.setFrequency(fQubit)
	qb_att.setVoltage(qbVVAVoltage)
	if setReadoutPar:
		if useDict:
			setReadout(frequency='dictValue', resVVAVoltage='dictValue', useParamp='dictValue', setPulse='dictValue', setAcqiris='dictValue')
		else:
			setReadout(frequency=resFrequency, resVVAVoltage=resVVAVoltage, useParamp=useParamp, setPulse=setPulse, setAcqiris=setAcqiris, parSubDict=parSubDict)
	time.sleep(1)
	print 'rabiMeas with fQubit=',mw_qb.frequency(),' VVAQubit=',qb_att.voltage()
	if piEst==None:
		if rabiStart==None:start=qubitTimeResPar['rabiStart']
		else: start=rabiStart
		if rabiStop==None:stop=qubitTimeResPar['rabiStop']
		else: stop=rabiStop
		if rabiStep==None:step=qubitTimeResPar['rabiStep']
		else: step=rabiStep
	else:
		start=0
		step=piEst/5
		stop=piEst*5
	durations=SmartLoop(start,step,stop,name="RabiLoop")
	if pulseType==None:pulseType=qubitSpecPar['pulseType']
	for duration in durations:
		pg_qb.clearPulse()
		## need to check which parameters the pulse generator wants for a gaussian pulse
		if pulseType=='gaussian':
			if cutOff==None: cutOff=qubitTimeResPar['gaussianCutOff']
			sigma=duration
			center=setAWGPar(AWGParFast)-(readoutPar['subDict']['pulseLength']+qubitTimeResPar['sepFromReadout']-sigma*cutOff/2)
			pg_qb.addPulse(generatorFunction=pulseType, amplitude=qubitTimeResPar['pulseHeight'],center=center, sigma=sigma, cutOff=cutOff)
		else:	
			start=setAWGPar(AWGParFast)-(readoutPar['subDict']['pulseLength']+qubitTimeResPar['sepFromReadout']+duration)
			stop=setAWGPar(AWGParFast)-(readoutPar['subDict']['pulseLength']+qubitTimeResPar['sepFromReadout'])
			pg_qb.addPulse(generatorFunction=pulseType, amplitude=qubitTimeResPar['pulseHeight'],start=start, stop=stop,)
		pg_qb.addMarker(channel=1,start1=start,stop1=stop)
		pg_qb.preparePulseSequence()
		pg_qb.prepareMarkerSequence()
		pg_qb.sendPulseSequence()
		time.sleep(0.1)
		[amp,phase]=readout()
		data.set(duration=duration,amp=amp,phase=phase,columnOrder=['duration','amp','phase'])
		data.commit()
	toReturn=[]
	if fit:
		[y0,yAmp,t0,rabiPeriod],yfit,yFitGuess=fitCosine(data['amp'],x=data['duration'])
		data.createColumn("rabiFit",yfit)
		piRabi=rabiPeriod/2
		print "Pi pulse length = %f ns"%piRabi
		if pulseType=='gaussian':
			samplePar['gaussianPiPulse']=piRabi
			toReturn.append(['gaussianPiPulse',piRabi])
		else:
			samplePar['piPulse']=piRabi
			toReturn.append(['piPulse',piRabi])				 
	if savePar:
		savedDict=dict()
		savedDict.update(readoutPar)
		savedDict.update(qubitTimeResPar)
		savedDict.update(qubitSpecPar)
		data.setParameters(AWGParFast)	
	if dataSave:
		data.savetxt()
	if fit:
		return toReturn
		
def t1MeasFast(fQubit='',qbVVAVoltage='',pulseType=None, piPulse=None, gaussianPiPulse=None, T1Est=None, T1DelayStart=None, T1DelayStop=None, T1DelayStep=None, cutOff=None, data='',setReadoutPar=False,useDict=False, useParamp=None, parSubDict=None, setPulse=None,setAcqiris=None, resFrequency=None, resVVAVoltage=None, fit=True,autoPlot=True,autoClear=False,dataSave=True,savePar=True):
# A T1 measurement with fixed delay intervals
	if data=='':
		if pulseType=='gaussian':	
			data=Datacube('T1fast-gaussian')
		else:
			data=Datacube('T1fast')
		data.toDataManager()
	if autoPlot:
		data.plotInDataManager(names=["delay","amp"],clear=autoClear,style='line')
		data.plotInDataManager(names=["delay","ampFit"],clear=autoClear,style='line')
	data.toDataManager()
	mw_qb.turnOn()
	if qbVVAVoltage=='':qbVVAVoltage=qubitTimeResPar['TimeResqbVVAVoltage']
	if fQubit=='': fQubit=samplePar['f_qb']
	mw_qb.setFrequency(fQubit)
	qb_att.setVoltage(qbVVAVoltage)
	if setReadoutPar:
		if useDict:
			setReadout(frequency='dictValue', resVVAVoltage='dictValue', useParamp='dictValue', setPulse='dictValue', setAcqiris='dictValue')
		else:
			setReadout(frequency=resFrequency, resVVAVoltage=resVVAVoltage, useParamp=useParamp, setPulse=setPulse, setAcqiris=setAcqiris, parSubDict=parSubDict)
	time.sleep(1)
	print 't1Meas with fQubit=',mw_qb.frequency(),'VVAQubit=',qb_att.voltage()
	if T1Est==None:
		if T1Start==None:start=qubitTimeResPar['T1Start']
		else:start=T1Start
		if T1Step==None:step=qubitTimeResPar['T1Step']
		else:step=T1Step
		if T1Stop==None:stop=qubitTimeResPar['T1Stop']
		else:stop=T1Stop
	else:
		start=0
		step=T1Est/8
		stop=T1Est*5
	delays=SmartLoop(start,step,stop,name="T1Loop")
	if pulseType==None:pulseType=qubitSpecPar['pulseType']
	if piPulse==None: piPulse=samplePar['piPulse']
	if gaussianPiPulse==None: gaussianPiPulse=samplePar['gaussianPiPulse']
	for delay in delays:
		pg_qb.clearPulse()
		## need to check which parameters the pulse generator wants for a gaussian pulse
		if pulseType=='gaussian':
			if cutOff==None: cutOff=qubitTimeResPar['gaussianCutOff']
			sigma=gaussianPiPulse
			center=setAWGPar(AWGParFast)-(readoutPar['subDict']['pulseLength']+qubitTimeResPar['sepFromReadout']-sigma*cutOff/2)
			pg_qb.addPulse(generatorFunction=pulseType, amplitude=qubitTimeResPar['pulseHeight'],center=center, sigma=sigma, cutOff=cutOff)
		else:
			start=setAWGPar(AWGParFast)-(readoutPar['subDict']['pulseLength']+qubitTimeResPar['sepFromReadout']+piPulse+delay)
			stop=setAWGPar(AWGParFast)-(readoutPar['subDict']['pulseLength']+qubitTimeResPar['sepFromReadout']+delay)
			pg_qb.addPulse(generatorFunction=pulseType, amplitude=qubitTimeResPar['pulseHeight'],start=start, stop=stop,)
		pg_qb.addMarker(channel=1,start1=start,stop1=stop)
		pg_qb.preparePulseSequence()
		pg_qb.prepareMarkerSequence()
		pg_qb.sendPulseSequence()
		time.sleep(0.1)
		[amp,phase]=readout()
		data.set(delay=delay,amp=amp,phase=phase,columnOrder=['delay','amp','phase'])
		data.commit()
	toReturn=[]
	if fit:			
		# fit exponential with reverseY=true
		[y0,yAmp,x0,t1],yFit,yFitGuess=fitT1(data['amp'],x=data['delay'],reverseY=True)
		data.createColumn("T1fit",yFit)
		print "T1 = %f"%t1
		samplePar['T1']=t1
		toReturn.append(['T1',t1])
	if savePar:
		savedDict=dict()
		savedDict.update(readoutPar)
		savedDict.update(qubitTimeResPar)
		savedDict.update(AWGParFast)
		data.setParameters(savedDict)
	if dataSave:
		data.savetxt()
	if fit:
		return toReturn
						
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
def runFuncList(functionList,data='',feedbackPar='', adaptiveLoop=None, setReadoutPar=False, useDict=True, fit=True, adaptParameters=True,dataSave=True):
	if data=='':data=Datacube('CoilVSweep %.16s' % datetime.datetime.now())
	for func in functionList:
		child=Datacube('%s at vCoil = %f'%(func[0].func_name,coil.voltage()))
		data.addChild(child)
		if len(func)>1 and func[2]==None: #No feedback values
			returnValues=func[0](data=child, setReadoutPar=setReadoutPar, useDict=useDict, fit=fit)
		elif len(func)>1 and func[2]!=None: #if feedback values are needed
			exec 'returnValues=func[0](data=child, setReadoutPar=setReadoutPar, useDict=useDict, fit=fit, '+func[1]+'=%f)'%func[2]	
		else:
			print 'No feedback'
			returnValues=func(data=child, setReadoutPar=setReadoutPar, useDict=useDict, fit=fit)
		print returnValues
		for value in returnValues:
			exec 'data.set('+value[0]+'= %f)'%value[1]
			if adaptiveLoop!=None:
				if feedbackPar !='' and feedbackPar == value[0]:adaptiveLoop.newFeedbackValue(value[1]) # feedback into coil loop
			if value[0]==func[3]:	func[2]=value[1] # feedback into experiment parameters
	data.commit()
	if dataSave:
		data.savetxt()

# This loop runs a list of functions (experiments) as a function of the coil voltage and collects its results. It is also possible to feed back a value from
# one (and only one) returned value to adapt the coil loop step.
def coilSweepLoopAdaptive(functionList,data='',feedbackPar='',VStart=0,VStep=0.1, VStop=1, setReadoutPar=False, useDict=True, fit=True, adaptParameters=True,dataSave=True):
	if data=='':data=Datacube('CoilVSweep %.16s' % datetime.datetime.now())
	data.toDataManager()
	coilVoltageLoop=AdaptiveLoop(VStart,step=VStep,stop=VStop,name='CoilVoltage',adaptFunc=adaptStepFunc1)
	for v in coilVoltageLoop:
		v=round(v,3)
		coil.setVoltage(v,slewRate=0.2)
		print "Coil Voltage = %f"%v
		data.set(CoilVoltage=v,commit=True)
		child0=Datacube('Measurements at vCoil = %f'%v)
		data.addChild(child0)
		runFuncList(functionList,data=child0,feedbackPar=feedbackPar,adaptiveLoop=coilVoltageLoop, setReadoutPar=setReadoutPar, useDict=useDict, fit=fit, adaptParameters=adaptParameters,dataSave=dataSave)
	if dataSave:
		data.savetxt()
		
##	
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
def t1MeasFastOld(fQubit='',powerQubit='',data='',start=0,step=10,stop=1000,fit=True,autoPlot=True,autoClear=False,dataSave=True,debug=False,savePar=True):
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


