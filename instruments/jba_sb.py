import sys
import getopt
import numpy
from matplotlib.pyplot import *
from pyview.lib.classes import *
from pyview.helpers.instrumentsmanager import Manager
from numpy import *
register=Manager().getInstrument('register')
import time
import numpy.linalg
import scipy
import scipy.optimize
from pyview.lib.classes import *
from pyview.lib.datacube import Datacube
from pyview.helpers.datamanager import DataManager
from pyview.helpers.instrumentsmanager import Manager
from pyview.lib.datacube import Datacube
from macros.advancedFitFunctions import *
import scipy
from pyview.helpers.datamanager import DataManager
dataManager = DataManager()
class Instr(Instrument):

  """
  Single frequency JBA - VS 2012/01
  Virtual Instrument able to generate and analyse JBA signals.
  """
  
  def startJBA(self):
    self._pulseGenerator.startPulse(name=self.name())
    self._pulseAnalyser.startAnalyseFrequency(name=self.name())
  
  def stopJBA(self):
    self._pulseGenerator.stopPulse(name=self.name())
    self._pulseAnalyser.stopAnalyseFrequency(name=self.name())
  
  
  def initialize(self, name, generator, analyser,magnitudeButton='formAmplitude'):
    """
    Initialize instrument, and define default shape in self.shape
    """
    instrumentManager=Manager()
    self._pulseGenerator=instrumentManager.getInstrument(generator)
    self._pulseAnalyser=instrumentManager.getInstrument(analyser)
    self._params=dict()
    self._params["pulseGenerator"]=generator
    self._params["pulseAnalyser"]=analyser
    self._change=True
    self._magnitudeButton=magnitudeButton
    self.data=Datacube()
    try:
      self._variableAttenuator=instrumentManager.getInstrument('jba_att')
    except:
      pass
    plateau=0.8   
    plateauLength=1000  
    self.shape=zeros((20000),dtype = numpy.complex128)
    self.shape[10000:10010]=linspace(0,1,10)
    self.shape[10010:10210]=1
    self.shape[10210:10220]=linspace(1,plateau,10)
    self.shape[10220:10220+plateauLength]=plateau
    self.shape[10220+plateauLength:10230+plateauLength]=linspace(plateau,0,10)
    self.bit=int(self.name()[-1])-1
    self._phase=0
  def parameters(self):
    """
    Return parameters
    """    
    return self._params      


  def init(self):
    """
    Clear the JBA (no frequency to analyse)
    """
    self._pulseGenerator.clearPulse()
    self._pulseAnalyser.clear()
    self._change=True
          
  def setFrequency(self, frequency, amplitude=1., duration=0., gaussian=False, delayFromZero=0,phase=None,shape=None):
    """
    Add a new frequency to analyse
    """
    if shape==None:shape=self.shape
    if phase==None:
      phase=self._phase
    self.phase=phase
    self._frequency=frequency
    self._amplitude=amplitude
    #self._pulseGenerator.clearPulse()
    self._pulseGenerator.generatePulse(duration=duration, frequency=self._frequency, amplitude=self._amplitude, DelayFromZero=delayFromZero,useCalibration=True, phase=phase,shape=amplitude*shape, name=self.name())
    self._fsb=-(self._pulseGenerator._MWSource.frequency()-frequency)
    self._pulseAnalyser.addFrequency(f=self._fsb, name=self.name(),bit=self.bit)
    self._change=True
            
  def sendAllWaveforms(self,forceSend=False):
    """
    Send all waveforms in pulseGenerator buffer
    """
    self._pulseGenerator.sendPulse(forceSend)
    
  def sendWaveform(self,forceSend=False):
    """
    Send waveform pf this JBA
    """
    self._pulseGenerator.sendPulse(forceSend)
    
  def setAmplitude(self, amplitude, magnitudeButton=None, phase=None,**args):
    """
    Set amplitude of the JBA pulse with button=magnitudeButton (if define, else self._magnitudeButton)
    """
    if magnitudeButton==None: magnitudeButton=self._magnitudeButton
    if magnitudeButton=='formAmplitude':
        if phase==None:
          phase=self._phase
        self.phase=phase
        if abs(amplitude)>0.8: amplitude=amplitude/abs(amplitude)*0.8
        self.setFrequency(frequency=self._frequency,shape=amplitude*self.shape,phase=phase)
        self.sendWaveform()
        time.sleep(0.5)
    elif magnitudeButton=='variableAttenuator':
        if amplitude>5:amplitude=5
        if amplitude<0:amplitude=0
        self._variableAttenuator.setVoltage(amplitude)
        time.sleep(0.2)
    elif magnitudeButton=='microwaveSource':
        if amplitude>19:amplitude=19
        if amplitude<-19:amplitude=-19
        self._pulseGenerator._MWSource.setPower(amplitude)
        time.sleep(0.1)
    else: print "Error in magnitudeButton value"
    self.amplitude=amplitude
    return amplitude

  def getMeasurement(self):
    """
    Measure IQ signal at all frequencies previously added
    """
    self.co=self._pulseAnalyser.analyse()
    self._change=False
    return self.co    
      
  def calculateBifurcation(self):
    """
    Acquire and calculate if JBA bifurcates or not
    """
    if self._change:
      self._pulseGenerator.sendPulse()
      time.sleep(0.5)
    (av, co, fr)=self._pulseAnalyser.analyse()
    self._change=False
    r=self._pulseAnalyser._acqiris.multiplexedBifurcationMapAdd(co,fr)
    proba=self._pulseAnalyser._acqiris.convertToProbabilities(r)
    return (av, co, fr, proba)
    
  def calibrate(self,bounds=None,level = 0.5,accuracy = 0.025, magnitudeButton=None,onlyOne=False,dataS=None,voltages=None,**kwargs):
    """
    Calibrate Offset and rotation for a single frequency f, and store it
    """
    if magnitudeButton==None:magnitudeButton=self._magnitudeButton
    self.notify("status","Starting calibration...")
    self.notify("variance",0)
    maxVoltage = self._findAmplitude(magnitudeButton=magnitudeButton, frequency=self._frequency, shape=self.shape,bounds=bounds,**kwargs)
    if not(onlyOne): maxVoltage = self._findAmplitude(magnitudeButton=magnitudeButton, frequency=self._frequency, shape=self.shape,center=maxVoltage,color=1,bounds=bounds)
    self.notify("status","Voltage calibration complete...")
    self.voltage=maxVoltage
    self._adjustRotationAndOffset()
    self.adjustSwitchingLevel(level)
    
     
  def _findAmplitude(self,frequency=None,shape=None,magnitudeButton=None,center=None,color=0,bounds=None,dataValues=None):
    """
    Only used by function calibrate.
    Measure and find the amplitude where the JBA is bi-evaluated, go to this point, and store this amplitude
    """
    
    def fitLorentzian(fs,p1,f0=None):
    
      fitfunc = lambda p, x: p[2]+p[0]/(1.0+pow((x-fs[argmax(p1)])/p[1],2.0))
      errfunc = lambda p, x, y,ff: pow(numpy.linalg.norm(ff(p,x)-y),2.0)
      
      ps = [(max(p1)-min(p1)),0.005,min(p1)]
      if f0!=None:
        if max(fs)>f0 and min(fs)<f0:ps[1]=f0
      
      print "Initial guess:",ps
    
      import numpy.linalg
      import scipy
      import scipy.optimize
      p1s = scipy.optimize.fmin(errfunc, ps,args=(fs,p1,fitfunc))
      rsquare = 1.0-numpy.cov(p1-fitfunc(p1s,fs))/numpy.cov(p1)
      print p1s
      return p1s.tolist()
      
      
    if frequency==None:frequency=self._frequency
    if shape==None:shape=self.shape
    if magnitudeButton==None:magnitudeButton=self._magnitudeButton


    
    self.setFrequency(frequency=frequency,shape=shape)
    self.sendWaveform()
    if magnitudeButton=='formAmplitude':
      """
      values = voltage amplitude
      """
      if center==None:
        values=arange(0,0.8,0.01)
      else:
        values=arange(center-0.025,center+0.025,0.001)
    elif magnitudeButton=='variableAttenuator':
      """
      values = attenuator voltage 
      """
      if center==None:
        values=arange(0,5,0.1)
      else:
        values=arange(center-0.2,center+0.2,0.01)
    elif magnitudeButton=='microwaveSource':
      """
      values = microwave Output power in dB
      """
      self.setFrequency(frequency=frequency,shape=shape)
      self.sendWaveform()
      if center==None:
        values=arange(0,20,0.20)
      else:
        values=arange(center-1,center+1,0.05)
    else:
      print "Error in the value of magnitudeButton"
    
    if bounds!=None:
      if center==None:
        values=linspace(bounds[0],bounds[1],bounds[2])
      else:
        print ''
    
    self.notify('iqP',0)
    ps = []
    maxcov = 0
    maxVoltage = 0
    self.variances = zeros((len(values),2))
    self.variances[:,0] = values
    self.data.clear()
    try:
      self.setAmplitude(magnitudeButton=magnitudeButton, amplitude=values[0])
      time.sleep(0.5)
      for i in range(0,len(values)):
        if self.stopped():
          self._stopped = False
          raise Exception("Got stopped!")
        v = values[i] 
        v=self.setAmplitude(magnitudeButton=magnitudeButton, amplitude=v)
        trends=self.getComponents()
        varsum =cov(trends[0])+cov(trends[1])
        if not dataValues==None:
          ch=Datacube()
          dataValues.addChild(ch)
          ch.createColumn('I',trends[0])
          ch.createColumn('Q',trends[0])
          dataValues.set(v=v,varsum=varsum)
          dataValues.commit()
        self.data.set(v = v)
        self.data.set(varsum=varsum)
        self.data.commit()
        self.notify("variance",(self.data.column("v"),self.data.column("varsum"),((color,0,0))))
        x=1.*i/len(values)
        self.notify("iqP",(trends[0],trends[1],((x,0,1-x))))
        self.notify("status","Variance at %g V: %g" % (v,varsum))
        print "Variance at v = %f : %f" % (v,varsum)
        self.variances[i,1] = varsum
        ps.append(varsum)
        if varsum > maxcov:
          maxcov = varsum
          maxVoltage = values[i]
      self.setAmplitude(magnitudeButton=magnitudeButton,amplitude=maxVoltage)
      self._vMaxAmplitude=maxVoltage
      self._sCurveParams=fitLorentzian(self.data['varsum'],self.data['v'])
    except:
      raise
    finally:    
      return maxVoltage
    
  def _adjustRotationAndOffset(self,accurate=False):
    frequency=self._fsb
    """
    Only used by function calibrate, use only where the JBA is bi-valued
    To find the rotation angle and offsets to discriminate properly the bi-valued values, at a single frequency, and store thoses values
    """
    trends=self.getComponents()

    if accurate:    
      density,Chi,XY,domain=convertToDensity(trends.transpose())
      e,f,p= fit2D2Gaussian(Chi,XY)
      centers=[[p[2],p[3]],[p[7],p[8]]]
      sepCenter=(mean([centers[0][0],centers[1][0]]),mean([centers[0][1],centers[1][1]]))
      sepAngle=-math.atan2(centers[0][0]-centers[1][0],centers[0][1]-centers[1][1])
    else:
      covar = cov(trends[0],trends[1]) 
      print covar
      la,v = linalg.eig(covar)    
      if la[1] > la[0]:
        angle = math.atan2(v[0,0],v[0,1])
      else:
        angle = math.atan2(v[1,0],v[0,0])    
      sepCenter=(mean(trends[0]),mean(trends[1]))
      print sepCenter
      print angle
      sepAngle=angle
        
    self._setRotationAndOffset(sepCenter[0],sepCenter[1],sepAngle)
    p0=self.takePoint()
    self.setAmplitude(amplitude=self._vMaxAmplitude+0.05)
    p1=self.takePoint()
    self.setAmplitude(amplitude=self._vMaxAmplitude)
    print p0,p1
    if p0<p1:
      self._setRotationAndOffset(sepCenter[0],sepCenter[1],sepAngle+math.pi)
    
    
    
  def _setRotationAndOffset(self, I0,Q0, angle):
    print I0,Q0,angle
    self._pulseAnalyser._acqiris.multiplexedBifurcationMapSetRotation(self._fsb,I0,Q0,angle)
    self.notify("iqPaxes",(I0,Q0,math.pi/2+angle))      


  def measureSCurve(self,voltages = None,ntimes = 10,microwaveOff = True,data=None,fspPower=False,corelations=False,**extraInDatacube):
    self.notify("status","Measuring S curve...")
    def getVoltageBounds(v0,jba,variable,ntimes):
      return (0.5,5)
      v = v0
      jba.setVoltage(v)
      jba._acqiris.bifurcationMap(ntimes = ntimes)
      p = jba._acqiris.Psw()[variable]
      
      while p > 0.03 and v < v0*2.0:
        v*=1.05
        jba.setVoltage(v)
        jba._acqiris.bifurcationMap(ntimes = ntimes)
        p = jba._acqiris.Psw()[variable]
      vmax = v
      
      v = v0
      jba.setVoltage(v)
      jba._acqiris.bifurcationMap(ntimes = ntimes)
      p = jba._acqiris.Psw()[variable]
      
      while p < 0.98 and v > v0/2.0:
        v/=1.05
        jba.setVoltage(v)
        jba._acqiris.bifurcationMap(ntimes = ntimes)
        p = jba._acqiris.Psw()[variable]
      vmin = v
      return (vmin*0.95,vmax*1.2)
    if fspPower:
      self._pulseGenerator._mixer._fsp.setFrequency(self._frequency)  
    if data==None:
      data = Datacube("%s S Curve - f=%f" %(self.name(),self._frequency))
      dataManager = DataManager()
      dataManager.addDatacube(data)
    else:
      data.setName("%s S Curve - f=%f" %(self.name(),self._frequency))
    bounds=[self._vMaxAmplitude-2*max(self._vMaxAmplitude/5,abs(self._sCurveParams[0])),self._vMaxAmplitude+2*max(self._vMaxAmplitude/5,abs(self._sCurveParams[0]))]
    #bounds=[0,1]
    print bounds
    if voltages==None:
      voltages=linspace(bounds[0],bounds[1],200)
    try:
      for v in voltages:
        self.setAmplitude(v)
        data.set(v = v)
        d=self.measure(nLoops=ntimes)
        #d=self.getThisMeasure()
        data.set(**d[1])
        if corelations:
          data.set(**d[4])
        data.set(**extraInDatacube)
        if fspPower:
          time.sleep(1)
          data.set(fspPower=self._pulseGenerator._mixer._fsp.getValueAtMarker())          
        #self.notify("histograms",d[2][self.bit][0])
        #self.notify("iqdata",(d[2][self.bit][0],d[2][self.bit][1]))
        ##self.notify("iqP",(d[0][:,0],d[0][:,1],((0,0,0))))
        data.commit()
        #self.notify("sCurve",(data.column("v"),data.column("b%i"%self.bit)))
      data.createColumn("p-0.5",abs(data["b%i"%self.bit]-0.5))
      data.sortBy("p-0.5")
      self._p50fromS=data['v'][0]
      data.sortBy('v')
      #data.sortBy("b%i"%self.bit)
      #p=data["b%i"%self.bit]
      #v=data['v']
      #p=p[p>0]
      #v=v[p>0]
      ##p=p[p<1]
      #v=v[p<1]
      #self.sInterpolateVP=scipy.interpolate.interp1d(p,v)
      #data.sortBy('v')
      
    except:
      raise
    finally:
      data.savetxt()
      self.notify("status","S curve complete.")
      self.setAmplitude(self._vMaxAmplitude)
      return data

  def measureAll(self):
    return self._pulseAnalyser.measureAll()

    
    
  def adjustSwitchingLevel(self,level = 0.2,accuracy = 0.05):#,verbose = False,minSensitivity = 15.0,microwaveOff = True,nmax = 100):
      fitfuncS = lambda p, x: exp(1-exp((x-p[0])/p[1]))/exp(1)
    def fitS(x,y,x0,dx):
      errfunc = lambda p, x, y,ff: pow(numpy.linalg.norm(ff(p,x)-y),2.0)
      ps=[x0,dx]
      p1s = scipy.optimize.fmin(errfunc, ps,args=(x,y,fitfuncS),retall=False,disp=False)
      rsquare = 1.0-numpy.cov(y-fitfuncS(p1s,x))/numpy.cov(y)
      return p1s.tolist()
      
    def levelAt(amplitude,nLoops=1,**args):
      v=self.setAmplitude(amplitude,**args)
      return (v,self.takePoint(nLoops=nLoops))
      
    def addToArray(x):
      (nx,ny)=levelAt(x)
      print nx,ny
      self.x.append(nx)    
      self.y.append(ny)    
      
    self.x=[]
    self.y=[]
    
    [vmin,vmax]=[0.8*self._vMaxAmplitude,1.2*self._vMaxAmplitude]#[self._vMaxAmplitude-2*max(self._vMaxAmplitude/5,abs(self._sCurveParams[0])),self._vMaxAmplitude+2*max(self._vMaxAmplitude/5,abs(self._sCurveParams[0]))]
    
    addToArray(vmin)
    addToArray(vmax)
    print self.x, self.y
    for i in [1,2,3,4,5,6,7]:
      params=fitS(self.x,self.y,self._vMaxAmplitude,0.2)
      print params
      addToArray(params[0])
      print self.x,self.y
    
    # Define the invert function from center-2linewidth to center+2linewidth
    x = linspace(params[0]-2*params[1],params[0]-2*params[1],1000)
    f = lambda x: fitfunc(params,x)
    y = map(f,x)
    
    
    
    
    
    
    
    
    #self.setAmplitude(self.sInterpolateVP(level))
    #self.setAmplitude(self._vMaxAmplitude)
    #return True
    #def levelAt(amplitude,nLoops=1,**args):
    #  self.setAmplitude(amplitude,**args)
    #  return self.takePoint(nLoops=nLoops)
    #
    #[vmin,vmax]=[self._vMaxAmplitude-2*max(self._vMaxAmplitude/5,abs(self._sCurveParams[0])),self._vMaxAmplitude+2*max(self._vMaxAmplitude/5,abs(self._sCurveParams[0]))]
    #options=dict()
    #options['maxiter']=15
    #result=scipy.optimize.minimize_scalar(levelAt,bracket=(vmin,self._vMaxAmplitude,vmax),bounds=(vmin,vmax),method='bounded',tol=accuracy,options=options)
    #return result
  

  
  
  
  
  
  
  
  
  
  
  
  
    #errfunc = lambda p, x, f:abs(f(x)-p)
    #v = scipy.optimize.fmin(errfunc, self._vMaxAmplitude,args=(p, self.sInterpolate),xtol=1e-5,ftol=1e-3)
    #print v
    #self.setAmplitude(v)
    



  def getIQp(self):
    co=self.getMeasurement()
    (clicks,IQData)=self._pulseAnalyser._acqiris.multiplexedBifurcationMapAdd(co,self._fsb)
    r = self._pulseAnalyser._acqiris.convertToProbabilities(clicks)
    return (r,IQData)
    
  def measure(self,nLoops=1,fast=False):
    """
    acquire, measure and calculate probabilities
    """
    toReturn = self._pulseAnalyser.analyse(nLoops,fast=fast)

    return toReturn

  
  def getThisMeasure(self):
    """
    Return proba, non-corrected IQ, corrected IQ
    """
    r=self.measure()
    return (r[1]['b%i'%self.bit],r[0][self.bit],r[2][self.bit])
    
    
  def takePoint(self,nLoops=1):
    return self.measure(nLoops=nLoops)[1]['b%i'%self.bit]
  def getComponents(self): 
    return self.measure()[0][self.bit]


  def caracteriseJBA(self, shape, frequencies,test=False):
    for f in frequencies:
      self._pulseGenerator._MWSource.setFrequency(f)
      self._pulseGenerator._IQMixer.calibrate(offsetOnly=True)
      self.frequency(frequency=f,shape=shape)
      self._pulseGenerator.sendPulse()
      
  def caracteriseIQvsFvsP(self,frequencies,voltages,data=None):
  
    if data==None:
      data=Datacube("JBA mapping")
      dataManager.addDatacube(data)
    try:
      previousShape=self.shape
      self.shape=zeros((20000),dtype = numpy.complex128)
      self.shape[10000:10010]=linspace(0,1,10)
      self.shape[10010:12100]=1
      self.shape[12100:12110]=linspace(1,0,10)
#      return self.shape
      import scipy

      pvsv=Datacube("power")
      data.addChild(pvsv)
      for v in voltages:
        self.setAmplitude(amplitude=v)
        p=self.measureJBAPower(f='autodetect')
        pvsv.set(v=v,bluePower=p)       
        pvsv.commit()
      pv=scipy.interpolate.interp1d(pvsv.column("v"),pvsv.column("bluePower"))
      data.savetxt()
      
      
      for f in frequencies:
        child=Datacube("f=%f"%f)
        data.addChild(child)
        self.setFrequency(f)
        for v in voltages:
          self.setAmplitude(amplitude=v)
          time.sleep(0.5)
          co=self.getThisMeasure()[1]
          var=cov(co[0])+cov(co[1])
          if var>0.01:
              cod=Datacube("components at p=%f" %pv(v))
              cod.createColumn('I',co[0])
              cod.createColumn('Q',co[1])
              cod.createColumn('bluePower',[pv(v)]*len(co[0]))
              child.addChild(cod)
          else:
             ####### ECRIRE QUELQUE CHOSE ICI
            [I,Q]=[mean(co[0]),mean(co[1])]
            child.set(f=f,v=v,I=I,Q=Q,sigma=var,bluePower=pv(v))
            child.set(M=sqrt(I**2+Q**2))
            child.set(phi=math.atan2(I,Q))
            child.commit()
            data.set(f=f,v=v,I=I,Q=Q,sigma=var,bluePower=pv(v))
            data.set(M=sqrt(I**2+Q**2))
            data.set(phi=math.atan2(I,Q))
            data.commit()
        data.savetxt()
    except:
      raise
    finally:
      data.savetxt()
      self.shape=previousShape
      
  def measureJBAPower(self,f=None):
    if f==None:
      f=frequency=self._f01
    else:
      f=self._pulseGenerator._MWSource.frequency()


    self._pulseGenerator.clearPulse()
    
    self._pulseGenerator.pulses[self.name()][1]=False
    self._pulseGenerator.generatePulse(duration=register['repetitionPeriod'],frequency=f,DelayFromZero=0.,useCalibration=False,name='calibration')
    self._pulseGenerator.pulses['calibration'][1]=True
    
    self._pulseGenerator.sendPulse()
    
    fsp=self._pulseGenerator._mixer._fsp
    fsp.write("SENSE1:FREQUENCY:CENTER %f GHZ" % f)
    fsp.write("SENSE1:FREQUENCY:SPAN 0 MHz")
    fsp.write("SWE:TIME 1 ms")
    rbw = 10000
    fsp.write("SENSE1:BAND:RES %f Hz" % rbw)
    fsp.write("SENSE1:BAND:VIDEO AUTO")
    fsp.write("TRIG:SOURCE EXT")
    fsp.write("TRIG:HOLDOFF 0.0 s")
    fsp.write("TRIG:LEVEL 0.5 V")
    fsp.write("TRIG:SLOP POS")
    averaging=0
    fsp.write("SENSE1:AVERAGE:COUNT %d" % averaging)
    fsp.write("SENSE1:AVERAGE:STAT1 ON")
    time.sleep(0.5)
    m=mean(fsp.getSingleTrace()[1])
    print self._pulseGenerator.pulses
    self._pulseGenerator.pulses['calibration'][1]=False
    self._pulseGenerator.pulses[self.name()][1]=True
    self._pulseGenerator.sendPulse()
    print self._pulseGenerator.pulses
    return m 
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
  
