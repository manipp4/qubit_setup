##Start the instruments panel and the data manager
import matplotlib
matplotlib.use('module://pyview.gui.mpl.backend')

from numpy import *
from matplotlib.pyplot import *	

import sys
from pyview.gui.coderunner import *
from pyview.gui.instrumentspanel import *

from pyview.gui.datamanager import *
reload(sys.modules["pyview.gui.datamanager"])
from pyview.gui.datamanager import *

from pyview.gui.loopspanel import *

from pyview.gui.variablepanel import *
reload(sys.modules["pyview.gui.variablepanel"])
from pyview.gui.variablepanel import *

if not os.path.realpath(__file__+'../../../') in sys.path:
	sys.path.append(os.path.realpath(__file__+'../../../'))

def startInstrumentsPanel():
	
	global panel
	global manager
	global loopspanel
	global vPanel
	
	panel = InstrumentsPanel()
	manager= DataManager(globals = gv)
	gv.managerGUI = manager
	loopspanel = LoopsPanel()
	vPanel = VariablePanel(globals = gv)
	vPanel.show()
	manager.show()
	panel.show()
	loopspanel.show()
	
	# get a handle to the datamanager frontend in the scripts
	gv.managerGUI=manager
	gv.manager=manager.manager
	
	# put the different modules in debug mode if necessary
	manager.debugOn() # this is the GUI
	manager.manager.debugOn()
	#manager.plotters2D[0].debugOn() # first 2D plotter
	manager.plotters3D[0].debugOn() # first 3D plotter
	# for each datacube you want to debug in your scripts => cube.debugOn()
	
execInGui(startInstrumentsPanel)
##