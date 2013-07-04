import sys

sys.path.append('.')
sys.path.append('../')

from pyview.lib.classes import *
from pyview.gui.frontpanel import FrontPanel
from pyview.gui.elements.numericedit import * 

import datetime

import instruments

class Panel(FrontPanel):
    
    def calibrate(self):
      kwargs={'f_sb':self.fsbEdit.getValue()}
      self.instrument.dispatch("calibrate",**kwargs)

    def calibrateOffset(self):
      self.instrument.dispatch("calibrateOffset")      

    def stop(self):
      self.instrument.stop()
    
    def reInit(self):
      self.instrument.dispatch("reInitCalibration")
      
    def __init__(self,instrument,parent=None):
    
    
        super(Panel,self).__init__(instrument,parent)
        
        self.title = QLabel(instrument.name())
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("QLabel {font:18px;}")
        self.fsbEdit = NumericEdit("")

        self.CalibrateButton = QPushButton("Calibrate")
        self.CalibrateButtonOffset = QPushButton("Calibrate Offset")
        self.StopButton = QPushButton("Stop")
        self.reInitButton = QPushButton("Re-init calibration")
 
        self.grid = QGridLayout(self)
        

        self.grid.addWidget(QLabel("sidebande ?  "),1,0)
        self.grid.addWidget(self.fsbEdit,1,1)
        
        self.grid.addWidget(self.CalibrateButton,0,0)     
        self.grid.addWidget(self.CalibrateButtonOffset,0,1)     
        self.grid.addWidget(self.StopButton,0,2)     
        self.grid.addWidget(self.reInitButton,0,3)

        self.connect(self.CalibrateButton,SIGNAL("clicked()"),self.calibrate)
        self.connect(self.CalibrateButtonOffset,SIGNAL("clicked()"),self.calibrateOffset)
        self.connect(self.StopButton,SIGNAL("clicked()"),self.instrument.terminate)
        self.connect(self.reInitButton,SIGNAL("clicked()"),self.reInit)

        self.setLayout(self.grid)

        instrument.attach(self)
#        self.updateValues()
           
