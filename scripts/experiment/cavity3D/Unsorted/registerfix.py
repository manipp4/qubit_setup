from pyview.lib.datacube import *
from pyview.helpers.datamanager import *
from pyview.helpers.instrumentsmanager import *
register=Manager().getInstrument('register')
register['readoutDelay']=10000