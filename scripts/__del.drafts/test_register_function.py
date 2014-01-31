##
from config.instruments import *
import nump
y
from pyview.helpers.instrumentsmanager import Manager
import scipy
from pyview.helpers.datamanager import DataManager
dataManager = DataManager()
instrumentManager=Manager()
instrumentManager.initInstrument("rip://127.0.0.1:8000/register",forceReload = True)		
register=instrumentManager.getInstrument('register')
##
print awg.repetitionRate()
##
print register.keys()