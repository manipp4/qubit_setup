import sys
import getopt
import numpy

from pyview.lib.classes import *
from pyview.helpers.instrumentsmanager import Manager
from numpy import *
register=Manager().getInstrument('register')
if 'lib.datacube' in sys.modules:
  reload(sys.modules['lib.datacube'])
  
from pyview.lib.classes import *
from pyview.lib.datacube import Datacube

from macros.simple_mixer_optimization import OffsetOptimization
reload(sys.modules["macros.simple_mixer_optimization"])
from macros.simple_mixer_optimization import OffsetOptimization

class Instr(Instrument):
    
      def saveState(self):
        return None


      def calibrate(self):
        self._calibration.calibrateOffset()

       
      def calibrationParameters(self):
        return self._calibration.calibrationParameters()  

      def reInitCalibration(self):
        """
        Re-create calibration file and store filenames in the register
        """
        register["%s OffsetCal" % self._name]=self._calibration.initCalibrationData()
        self._calibration=OffsetOptimization(fsp=self._fsp, awg=self._AWG, mwg=self._MWSource, channels=self._params["AWGChannel"])

              
      def parameters(self): 
        """
        Returns IQ mixer parameters
        """   
        return self._params


      def initialize(self, name, MWSource, AWG,AWGChannel, fsp):
        """
        Initialize instrument, and create calibration files if needed
        """
        instrumentManager=Manager()
        self._name=name
        self._MWSource=instrumentManager.getInstrument(MWSource)
        self._fsp=instrumentManager.getInstrument(fsp)
        self._AWG=instrumentManager.getInstrument(AWG)
        self._params=dict()
        self._params["MWSource"]=MWSource
        self._params["AFG"]=AWG
        self._params["AWGChannel"]=AWGChannel
        self._params["fsp"]=fsp
        
        self._calibration=OffsetOptimization(fsp=self._fsp, awg=self._AWG, mwg=self._MWSource, channels=self._params["AWGChannel"])
        try:
          self._calibration._offsetCalibrationData=Datacube()
          self._calibration._offsetCalibrationData.loadtxt(register["%s OffsetCal" % self._name], loadChildren=True)
        except:
          print "No calibration data found for mixer %s" % self._name
          try:
            print "creating new one..."
            self.reInitCalibration()
            print "creation succesful, continue"
          except:
            print "creation failed"
            raise
