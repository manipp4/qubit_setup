from config.instruments import *
import numpy
from pyview.helpers.instrumentsmanager import Manager
import scipy
from pyview.helpers.datamanager import DataManager
dataManager = DataManager()
##
qb=instrumentManager.getInstrument('qubit1')
data=gv.data
#
from macros.qubit_functions import *
reload(sys.modules["macros.iq_level_optimization"])
print data
print fitT1Parameters(data,variable='p')