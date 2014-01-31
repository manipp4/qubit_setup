##curve
from config.instrumentsRSV import *
from matplotlib.pyplot import *
#from pyview.gui.mpl.backend import figure
import numpy
import scipy
from pyview.helpers.datamanager import DataManager
dataManager = DataManager()
instrumentManager=Manager()
Coil=instrumentManager.getInstrument('Keithley2400')
##
Coil.turnOn()
##
Coil.write(":SOUR:FUNC CURR")
Coil.write(":SOUR:CURR:LEV %s" %str(-0.001))
Coil.write(":SENS:CURR:PROT 2E-2")
Coil.write(":SENS:VOLT:PROT 1E+1")
Coil.write(":READ?")
#print Coil.read()  
##
Coil.current()
##
Coil.setCurrent(-0.0002)
##
print I
##
Coil.turnOff()
##
Coil.write("*RST")
