##Start the instruments panel and the data manager
#import matplotlib
#matplotlib.use('module://pyview.gui.mpl.backend')

from numpy import *
from matplotlib.pyplot import *	

import sys
from pyview.gui.coderunner import *
from pyview.gui.instrumentspanel import *
from pyview.gui.datamanager import *				
reload(sys.modules["pyview.gui.datamanager"])
from pyview.gui.datamanager import *
from pyview.gui.loopspanel import *

if not os.path.realpath(__file__+'../../../') in sys.path:
	sys.path.append(os.path.realpath(__file__+'../../../'))

def startInstrumentsPanel():
	
	global panel
	global manager
	global loopspanel
	
	panel = InstrumentsPanel()
	manager = DataManager(globals = gv)
	loopspanel = LoopsPanel()
	manager.show()
	panel.show()
	loopspanel.show()
	
execInGui(startInstrumentsPanel)