import sys
import getopt

from pyview.lib.classes import *

class Instr(Instrument):

      def temperature(self):
        
          
      def parameters(self):
        params = dict()
        params['temperature'] = self.temperature()
        return params

      def initialize(self,address = "132.166.19.2", port = 444):
        try:
          self._name = "Temperature sensor"
          print "Initializing temperature sensor"
          self.host = address
          self.port = port
        except:
          self.statusStr("An error has occured. Cannot initialize sensor.")    
          print "An error has occured. Cannot initialize sensor."

      def saveState(self,name):
        return self.parameters()