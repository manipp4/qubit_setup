import sys
import time
import datetime
import numpy
import scipy
import scipy.optimize
import scipy.interpolate
from pyview.lib.smartloop import *
from pyview.lib.datacube import *
from pyview.helpers.datamanager import DataManager
from pyview.helpers.instrumentsmanager import Manager
##
import pyview.helpers.loopsmanager
##
loop=LoopManager()._loops[0]
##
loop.setStop(16.0)
##
print loop.getStop()
##


