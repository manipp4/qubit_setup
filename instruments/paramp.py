# imports

import sys
import getopt
import re
import struct
import math
import numpy
import scipy

from pyview.lib.classes import *
from pyview.helpers.instrumentsmanager import Manager
from pyview.lib.smartloop import *

from pyview.lib.datacube import Datacube

# Class definition
class Instr(Instrument):
"""
Class for a flux controlled parametric amplifier operated in reflection.
- The instrument can have optional sub-instruments for flux DC biasing, parametric pumping, and test vectorial network analyzer.
Each sub-instrument stores a dictionnary 'methods' of method names for setting or getting data.
It is defined at initilization of the class or using methods setBiasGen, setPumpGen, or setTestVna (see doc).
- The class can store in a dictionary 'charac' several paramp characteristics (center frequency, gain,bandwidth,saturation)
versus flux bias and/or pump power, in terms of 1D or 2D calibration datacubes.
charac={'gain': datacube1,'bandwidth': datacube2,'saturation': datacube3,...}
Each characteristic is set with setCharac[characName, datacube] or by running a calibration routine (see below)
- If a test VNA is defined and operational, the method calibrateFreq (see doc) can calibrate the paramp center frequency.
"""

  def initialize(self,name='paramp',biasGen=None,pumpGen=None,testVna=None):
    manager=Manager()
      self._subInstruments=dict() # {localInstrumentName:(instrument object,{method_alias:methodName,...}),...}
      self._params = dict()
      self.setBiasGen(biasGen)
      self.setPumpGen(pumpGen)
      self.setTestVna(testVna)

  def methods(self,instrument,methodNames):
    return [getattr(instrument,methodName for methodName in methodNames]

  def methodsFromAliases(self,localInstrumentName,methodAliases):
    instr,methodsDict=self._subInstruments[localInstrumentName]
    return self.methods(instr,[methodsDict[methodAlias] for methodAlias in methodAliases])

  def checkAliasedMethodsExist(self,localInstrumentName,methodAliases=None):
    if methodAliases==None: methodAliases=self._subInstruments[localInstrumentName][1].keys()
    methods= self.methodsFromAliases(localInstrumentName,methodAliases)
    indices = [i for i, x in enumerate(methods) if x == None]
      if len(indices)!=O:
        raise NameError('methods '+str([methodAliases[i] for i in indices])+' do not seem to exist')

  def setBiasGen(self,instr,setBiasFuncName='setVoltage',getBiasFuncName='voltage'):
    if instr!=None:
      if isinstance(instr,str):
        inst=getInstrument(instr)
      else:
        inst=instr
      methods={'setBias':setBiasFuncName,'getBias':getBiasFuncName}
      self._subInstruments['biasGen']=(inst,methods)
      self.checkAliasedMethodsExist('biasGen')

  def setPumpGen(self,instr,setFreqFuncName='setFrequency',getFreqFuncName='frequency',setPowFuncName='setPower',getPowFuncName='power'):
    if instr!=None:
      if isinstance(instr,str):
        inst=getInstrument(pumpGen)
      else:
        inst=instr
      methods={'setFreq':setFreqFuncName,'getFreq':getFreqFuncNam,'setPow':setPowFuncName,'getPow':getPowFuncName}
      self._subInstruments['pumpGen']=(inst,methods)
      self.checkAliasedMethodsExist('pumpGen')

  def setTestVna(self,instr,\
    setFreqFuncName='setCenterInGhz',getFreqFuncName='getCenterInGhz',\
    setSpanFuncName='setSpanInGhz',getSpanFuncName='setSpanInGhz',\
    setPowFuncName='setTotalPower',getPowFuncName='getTotalPower',\
    getSpectrumFuncName='getFreqMagPhase',check=True\
    ):
    if instr!=None:
      if isinstance(instr,str):
        inst=getInstrument(pumpGen)
      else:
        inst=instr
      methods={'setFreq':setFreqFuncName,'getFreq':getSpanFuncNam,'setSpan':setSpanFuncName,'getSpan':getSpanFuncName,\
      'setPow':setPowFuncName,'getPow':getPowFuncName,'getSpectrum':getSpectrumFuncName}
      self._subInstruments['testVNA']=(inst,methods)
      self.checkAliasedMethodsExist('testVNA')


  def adaptFunc1(self,adaptiveLoop,deltafMax=span/10.,deltafMin=span/20.,stepMin=0.1,stepMax=1.):
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

  def calibrateFreq(self,biasStart=None,biasStop=None,biasStep=1,centerStart=None,span=None,):
      
    if self._subInstruments['testVNA'].has_Key('biasGen')  
      setBias,getBias=self.methodsFromAliases('biasGen',['setBias','getBias'])     
      [setFreq,getFreq,setSpan,getSpan,setPow,getPow,getSpectrum]=self.methodsFromAliases('testVna',['setFreq','getFreq','setSpan','getSpan','setPow','getPow','getSpectrum'])
      if biasStart!=None : setFreq(biasStart)
      else :biasStart=getFreq()
      if biasStop==None : biasStop=biasStart+10*biasStep
      if centerStart!=None : setFreq(centerStart)
      if span!=None : setSpan(span)

      data=Datacube('parampFreqVsBias')
      data.toDataManager()
      xLoop=AdaptiveLoop(biasStart,step=biasStep,stop=biasStop,name=parampFreqVsBias,adaptFunc=self.adaptFunc1)
      setFreq(fCenter)
      for x in xLoop:
        print "Bias= ", x
        setBias(x,slewRate=0.5)
        child1=getSpectrum(waitFullSweep = True)
        child1.setName('bias'+str(x))
        data.addChild(child1)
        #Fit phase and determine center frequency f here
        xLoop.newFeedbackValue(f)
        data.set(bias=x,freq=f,commit=True,columnOrder=['bias','freq','peakdB']) 