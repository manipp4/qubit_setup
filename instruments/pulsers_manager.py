import sys
import getopt
import numpy

from pyview.lib.classes import *
from pyview.helpers.instrumentsmanager import Manager
from numpy import *

__DEBUG__ = False

class Instr(Instrument):

      def initialize(self, name='pulses manager' , generators=[]):
        """
        Initialise the instrument at instantiation
        """
        self._name=name
        self._generators=[[Manager().getInstrument(n[0]),n[1]] for n in generators]
        self._params=[]

      def saveState(self,name):
        """
        returns the params dictionary
        """
        return self._params

      def restoreState(self,state):
        """
        Restores the pulse generator from the params dicitonary indicated
        """
        return None
      
      def pulses(self, generatorName=None):
        if generatorName!=None: 
          def cond(i,n): 
            if i[0]==n: return i
          generators=[cond(i,generatorName) for i in self._generators]
        else:
          generators=self._generators
        g=dict()
        for generator in generators:
          g[generator[0]]=dict()
          i=0
          for p in generator[0].pulseList:
              g[generator[0]][i]=p##{'shape':p._pulseArray,'frequency':p.frequency,'phase':p.phase,'corrections':p.applyCorrections,'name':p.name}
              i+=1
        return g


