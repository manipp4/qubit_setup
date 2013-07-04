import sys

sys.path.append('.')
sys.path.append('../')

from numpy import cos,sin,floor
from pyview.lib.classes import *
from pyview.gui.frontpanel import FrontPanel
from pyview.gui.mpl.canvas import *
#from instruments.acqiris import CAL_TOUT

import datetime
import instruments
import re

class Panel(FrontPanel):
    """
    The frontpanel class for the Acqiris Fast Acquisition card.
    
    Authors (add your name here if not present):
      - Andreas Dewes, andreas.dewes@gmail.com (creator)
      - Denis Vion, denis.vion@cea.fr (updates)
      - Vivien Schmitt, vovios@gmail.com (updates)
      
    Description:
    """
    
    def getParameters(self):
      """
      Reads all the parameter values from the frontpanel and returns them in a dictionary.
      This dictionary can be used as a parameter to a configure function as "ConfigureV2"
      """
      params = dict()
      params['offsets'] = list()          #list of the 4 vertical offsets
      params['fullScales'] = list()       #list of the 4 vertical fullscales
      params['couplings'] = list()        #list of the 4  coupling codes (see front panel)
      params['bandwidths'] = list()       #list of the 4 vertical bandwidth codes (see front panel)
      for i in range(0,4):                # read from front panel
        params["offsets"].append(float(self.offsets[i].text()))
        params["fullScales"].append(float(self.fullScales[i].text()))
        params["couplings"].append(self.couplings[i].itemData(self.couplings[i].currentIndex()).toInt()[0])
        params["bandwidths"].append(self.bandwidths[i].itemData(self.bandwidths[i].currentIndex()).toInt()[0])  
      if self.chCombine.currentIndex()==0: # channel combination for digitization above 2 GS/s
        params["convertersPerChannel"] = 1
      elif self.chCombine.currentIndex()<=6:
        params["convertersPerChannel"] = 2
      else :
        params["convertersPerChannel"] = 4
      params["usedChannels"] = 0          # used channels = sum 2^channel
      for i in range(0,4):
        if self.activated[i].isChecked():
          params["usedChannels"]+=1<<i
      params["synchro"] = bool(self.synchro.checkState())           # external synchro
      params["sampleInterval"] = float(self.sampleInterval.text())  # sampling interval in s
      params["trigSource"] = self.trigSource.itemData(self.trigSource.currentIndex()).toInt()[0]        # trigger source code
      if params["trigSource"] == 0:      
        params["trigSource"] = -1
      params["trigCoupling"] = self.trigCoupling.itemData(self.trigCoupling.currentIndex()).toInt()[0]  # trigger coupling code
      params["trigSlope"] = self.trigSlope.itemData(self.trigSlope.currentIndex()).toInt()[0]           # trigger slope code
      params["trigLevel1"] = float(self.trigLevel1.text())                                              # trigger level 1
      params["trigLevel2"] = float(self.trigLevel2.text())                                              # trigger level 2 for clever trigger
      params["trigDelay"] = float(self.trigDelay.text())                                                # trigger delay in s
      params["numberOfPoints"] = int(self.numberOfPoints.text())                                        # sampling interval 
      params["numberOfSegments"] = int(self.numberOfSegments.text())# sampling interval
      params["memType"] = self.memType.itemData(self.memType.currentIndex()).toInt()[0]   # memory to be used (defautl or force internal))
      params["configMode"] = self.configMode.currentIndex()                               # acquisition mode (see front panel)
      if  params["configMode"]==3:
        params["configMode"] = 10                                                         
      params["numberOfBanks"]= int(self.numberOfBanks.text())                                    # number of banks in memory (1 in all modes except SAR)
      params["nLoops"]= int(self.nLoops.text())                                           # number of acquisition loops (or banks in SAR mode)
      params["transferAverage"]= bool(self.transferAverage.isChecked())                  # transfer averaged trace only
      return params
    
    def requestCalibrate(self):
      """
      Requests a calibration of the Acqiris board.
      """
      result =  QMessageBox.question(self,"Calibrate?","Do you want to start the calibration of the Acqiris card?",buttons = QMessageBox.Cancel | QMessageBox.Ok)
      if result != QMessageBox.Ok:
        return
      usedChannels = 0          # used channels = sum 2^channel
      for i in range(0,4):
        if self.activated[i].isChecked():
          usedChannels+=1<<i
      self.instrument.dispatch("CalibrateV1",option=1,channels=usedChannels)      #channel
      
    def requestConfigure(self):
      """
      Configures the Acqiris board with the parameters that are displayed in the frontend.
      """
      params = self.getParameters()
      self.instrument.dispatch("ConfigureAllInOne",**params)  #self.instrument.dispatch("Configure",**params)
        
    def requestAcquire(self):
      """
      Request an acquisition and transfer.
      """
      params = self.getParameters()
      self.segmentPlot.axes.cla()
      self.averagePlot.axes.cla()
      self.fullWavePlot.axes.cla()
      self.timeStampsPlot.axes.cla()
      self.segmentPlot.draw()
      self.averagePlot.draw()
      self.fullWavePlot.draw()
      self.timeStampsPlot.draw()
      self.waitingNewData.setText("Acquiring new data...")
      self.waitingNewData.setVisible(True)
      self.waitingNewData.repaint()
      self.instrument.AcquireTransferV4(wantedChannels=params["usedChannels"],transferAverage=params["transferAverage"],nLoops=params["nLoops"])
      #self.instrument.dispatch("AcquireTransferV4", wantedChannels=params["usedChannels"],transferAverage=params["transferAverage"],nLoops=params["nLoops"])
      #self.instrument.dispatchCB("AcquireTransferV4", "newDataArrived", wantedChannels=params["usedChannels"],transferAverage=params["transferAverage"],nLoops=params["nLoops"])
      self.waitingNewData.setVisible(False)
      self.newDataArrived() 
        
    def newDataArrived(self,dispatchID=None,result=None):
      if bool(self.updatePlots.isChecked()):
        self.plotData()
      
    def plotData(self):
      if self.lastWave["identifier"]!=self.instrument.getLastWaveIdentifier():
        self.waitingNewData.setText("Transferring new data...")
        self.waitingNewData.setVisible(True)
        self.waitingNewData.repaint()
        self.lastWave=self.instrument.lastWave()
        self.waitingNewData.setVisible(False)
        max0=self.lastWave['nbrSegmentArray'][0]
        for i in range(1,4):
          max0=max(max0,self.lastWave['nbrSegmentArray'][i])
        self.segmentNumber.setMaximum(max0)
        self.NumOfSegDislay.setText("out of "+ str(max0))
        self.segmentNumber.setValue(1)
      self.segmentPlot.axes.cla()
      self.averagePlot.axes.cla()
      self.fullWavePlot.axes.cla()
      self.timeStampsPlot.axes.cla()
      
      if self.lastWave['timeStampsSize']!=0:
        if self.deltaTimestamps.isChecked():
          self.timeStampsPlot.axes.plot(self.lastWave['timeStamps'][1:]-self.lastWave['timeStamps'][:-1])
        else:
          self.timeStampsPlot.axes.plot(self.lastWave['timeStamps'][:]) 
      for i in range(0,4):
        if self.lastWave['transferedChannels'] & (1 << i):
          if self.lastWave['transferAverage']:
            self.averagePlot.axes.plot(self.lastWave['wave'][i])
          else:
            if self.plotTabs.currentIndex()==2:
              self.fullWavePlot.axes.plot(self.lastWave['wave'][i])
            requestedSegment=self.segmentNumber.value()
            #requestedSegment=max(0,min(requestedSegment,self.lastWave['nbrSegmentArray'][i]))
            if requestedSegment<=self.lastWave['timeStampsSize']:
              self.currentTimeStamp.setText(str(self.lastWave['timeStamps'][requestedSegment-1]))
            if requestedSegment<=self.lastWave['horPosSize']:
              self.currentHorPos.setText(str(self.lastWave['horPos'][requestedSegment-1]))
            start= (requestedSegment-1)*self.lastWave['nbrSamplesPerSeg']
            stop=start+self.lastWave['nbrSamplesPerSeg']-1
            self.segmentPlot.axes.plot(self.lastWave['wave'][i][start:stop+1])
      self.segmentPlot.draw()
      self.averagePlot.draw()
      self.fullWavePlot.draw()
      self.timeStampsPlot.draw()            

    
    def updatedGui(self,subject,property = None, value =None, message = None):
      """
      Processes status updates from the Acqiris card and updates the frontpanel information accordingly.
      """
      if subject==self.instrument:
        if property == "temperature":
          pass
        elif property == "AcquireV1":
          pass # DV 11/03/2012
          #self.instrument.dispatch("DMATransferV1",transferAverage = bool(self.transferAverage.isChecked()))
        elif property == "DMATransferV1":
          if self.updatePlots.isChecked():
            self._updatePlots = True
        elif property == "AcquireTransferV4":
          pass
          #if self.updatePlots.isChecked():
          #  self._updatePlots = True
        elif property == "parameters":
          self.updateParameters(**value)
        elif not "ask":
          print "bad message %s"%property


    def onTimer(self):
      if self._updatePlots:
        self._updatePlots = False
        self.plotData()
          
    def updateParameters(self,**params):
      """
      Updates the frontpanel information according to a given set of parameters.
      """
      if "couplings" in params and len(params["couplings"])==4:
        for i in range(0,4):
          self.couplings[i].setCurrentIndex(int(params["couplings"][i]))
      if "bandwidths" in params and len(params["bandwidths"])==4:
        for i in range(0,4):
          self.bandwidths[i].setCurrentIndex(int(params["bandwidths"][i]))
      if "fullScales" in params and len(params["fullScales"])==4:
        for i in range(0,4):
          self.fullScales[i].setText(str(params["fullScales"][i]))
      if "offsets" in params and len(params["offsets"])==4:
        for i in range(0,4):
          self.offsets[i].setText(str(params["offsets"][i]))
      if "usedChannels" in params:
        for i in range(0,4):
           self.activated[i].setChecked(int(params["usedChannels"]) & (1 << i))
      for key in ["sampleInterval","numberOfPoints","trigDelay","numberOfSegments","trigLevel1","trigLevel2"]:
        if key in params and hasattr(self,key):
          getattr(self,key).setText(str(params[key]))
      for key in ["memType","trigCoupling","trigSlope"]:
        if key in params and hasattr(self,key):
          getattr(self,key).setCurrentIndex(int(params[key]))   
      if "trigSource" in params:
        if int(params["trigSource"]) != -1:
          self.trigSource.setCurrentIndex(int(params["trigSource"]))
        else:
          self.trigSource.setCurrentIndex(0)
      for key in ["synchro","transferAverage"]:
        if key in params and hasattr(self,key):
          getattr(self,key).setChecked(bool(params[key]))
          
    def __init__(self,instrument,parent=None):
        """
        Initializes the frontpanel
        """
        super(Panel,self).__init__(instrument,parent)
        self.setWindowTitle("Acqiris DC282 Control Panel")
        
        self.lastWave=dict()     # create the lastWave dictionary to avoid errors before very first transfer
        self.lastWave['identifier']=-1
        
        #The grid layout channelGrid that contains the parameters for the different channels.
        self.channelGrid = QGridLayout()
        self.channelGrid.setVerticalSpacing(2)
        self.channelGrid.setHorizontalSpacing(10)
        
          #Lists containing the parameters controls of the different channels.
        self.couplings = list()
        self.fullScales = list()
        self.offsets = list()
        self.bandwidths = list()
        self.activated = list()
              
          #Here we generate the parameter controls of the 4 channels.
        self.chCombine = QComboBox()
        self.chCombine.addItem("1 ADC per channel (0)",0)
        self.chCombine.addItem("ADC pairs on CH 1 and 2 (1)",1)
        self.chCombine.addItem("ADC pairs on CH 1 and 3 (2)",2)
        self.chCombine.addItem("ADC pairs on CH 1 and 4 (3)",3)
        self.chCombine.addItem("ADC pairs on CH 2 and 3 (4)",4)
        self.chCombine.addItem("ADC pairs on CH 2 and 4 (5)",5)
        self.chCombine.addItem("ADC pairs on CH 3 and 4 (6)",6)
        self.chCombine.addItem("4 ADCs on CH 1 (7)",7)
        self.chCombine.addItem("4 ADCs on CH 2 (8)",8)
        self.chCombine.addItem("4 ADCs on CH 3 (9)",9)
        self.chCombine.addItem("4 ADCs on CH 4 (10)",10)
        self.chCombine.setCurrentIndex(0)
        self.channelGrid.addWidget(QLabel("Channel config:"),0,0)
        self.channelGrid.addWidget(self.chCombine,0,1,1,3)
        # response to a currentIndexChanged() event of self.chCombine
        def chCombineChanged():
          if self.chCombine.currentIndex()==0:
            for i in range(0,4):
              self.activated[i].setDisabled(False)
              self.activated[i].setChecked(True)
          elif self.chCombine.currentIndex()==1:
            for i in (0,1):
              self.activated[i].setDisabled(False)
              self.activated[i].setChecked(True)
            for i in (2,3):
              self.activated[i].setChecked(False)
              self.activated[i].setDisabled(True)
          elif self.chCombine.currentIndex()==2:
            for i in (0,2):
              self.activated[i].setDisabled(False)
              self.activated[i].setChecked(True)
            for i in (1,3):
              self.activated[i].setChecked(False)
              self.activated[i].setDisabled(True)
          elif self.chCombine.currentIndex()==3:
            for i in (0,3):
              self.activated[i].setDisabled(False)
              self.activated[i].setChecked(True)
            for i in (1,2):
              self.activated[i].setChecked(False)
              self.activated[i].setDisabled(True)
          elif self.chCombine.currentIndex()==4:
            for i in (1,2):
              self.activated[i].setDisabled(False)
              self.activated[i].setChecked(True)
            for i in (0,3):
              self.activated[i].setChecked(False)
              self.activated[i].setDisabled(True)
          elif self.chCombine.currentIndex()==5:
            for i in (1,3):
              self.activated[i].setDisabled(False)
              self.activated[i].setChecked(True)
            for i in (0,2):
              self.activated[i].setChecked(False)
              self.activated[i].setDisabled(True)
          elif self.chCombine.currentIndex()==6:
            for i in (2,3):
              self.activated[i].setDisabled(False)
              self.activated[i].setChecked(True)
            for i in (0,1):
              self.activated[i].setChecked(False)
              self.activated[i].setDisabled(True)
          elif self.chCombine.currentIndex()==7:
            self.activated[0].setDisabled(False)
            self.activated[0].setChecked(True)
            for i in (1,2,3):
              self.activated[i].setChecked(False)
              self.activated[i].setDisabled(True)
          elif self.chCombine.currentIndex()==8:
            self.activated[1].setDisabled(False)
            self.activated[1].setChecked(True)
            for i in (0,2,3):
              self.activated[i].setChecked(False)
              self.activated[i].setDisabled(True)
          elif self.chCombine.currentIndex()==9:
            self.activated[2].setDisabled(False)
            self.activated[2].setChecked(True)
            for i in (0,1,3):
              self.activated[i].setChecked(False)
              self.activated[i].setDisabled(True)
          elif self.chCombine.currentIndex()==10:
            self.activated[3].setDisabled(False)
            self.activated[3].setChecked(True)
            for i in (0,1,2):
              self.activated[i].setChecked(False)
              self.activated[i].setDisabled(True)
          self.sampleInterval.setFocus()
          self.sampleInterval.clearFocus()

        self.connect(self.chCombine,SIGNAL("currentIndexChanged(int)"),chCombineChanged)

        for i in range(0,4):
          myWidth=80
          activated = QCheckBox("Active")
          activated.setChecked(True)
          #def activatedChanged(self,i):
          #self.connect(self.activated,SIGNAL("stateChanged()"),activatedChanged)
            
          fullScale=QLineEdit("5.0")
          fullScale.setMaximumWidth(myWidth)
          offset=QLineEdit("0.0");
          offset.setMaximumWidth(myWidth)
          
          coupling = QComboBox()
          coupling.addItem("Ground",0)
          coupling.addItem("DC 1 MO",1)
          coupling.addItem("AC 1 MO",2)
          coupling.addItem("DC 50 O",3)
          coupling.addItem("AC 50 O",4)
          coupling.setCurrentIndex(3)
          coupling.setMaximumWidth(myWidth)
          
          bandwidth = QComboBox()
          bandwidth.addItem("Max 1GHz (0)",0)
          bandwidth.addItem("25  MHz (1)",1)
          bandwidth.addItem("700 MHz (2)",2)
          bandwidth.addItem("200 MHz (3)",3)
          bandwidth.addItem("20  MHz (4)",4)
          bandwidth.addItem("35  MHz (5)",5)
          bandwidth.setCurrentIndex(3)
          bandwidth.setMaximumWidth(myWidth)
                    
          self.activated.append(activated)
          self.couplings.append(coupling)
          self.fullScales.append(fullScale)
          self.bandwidths.append(bandwidth)
          self.offsets.append(offset)
          self.channelGrid.addWidget(QLabel("Channel %d" % (i+1)),1,i)
          self.channelGrid.addWidget(activated,2,i)
          self.channelGrid.addWidget(QLabel("Coupling %d" % (i+1)),3,i)
          self.channelGrid.addWidget(self.couplings[i],4,i)
          self.channelGrid.addWidget(QLabel("Fullscale %d (V)" % (i+1)),5,i)
          self.channelGrid.addWidget(self.fullScales[i],6,i)
          self.channelGrid.addWidget(QLabel("Offset %d (V)" % (i+1)),7,i)
          self.channelGrid.addWidget(self.offsets[i],8,i)
          self.channelGrid.addWidget(QLabel("Bandwidth "+str(i+1)),9,i)
          self.channelGrid.addWidget(self.bandwidths[i],10,i)

        #The parameter grid paramsGrid that contains all the global parameters of the card.
        self.paramsGrid = QGridLayout()
        self.paramsGrid.setVerticalSpacing(2)
        self.paramsGrid.setHorizontalSpacing(10)
        myWidth=90
          #trigger parameters        
        self.trigSource = QComboBox()        
        self.trigSource.addItem("Ext 1",0)
        self.trigSource.addItem("Ch 1",1)
        self.trigSource.addItem("Ch 2",2)
        self.trigSource.addItem("Ch 3",3)
        self.trigSource.addItem("Ch 4",4)
        self.trigSource.setMaximumWidth(myWidth)
        self.paramsGrid.addWidget(QLabel("Trigger source"),0,0)
        self.paramsGrid.addWidget(self.trigSource,1,0)

        self.trigCoupling = QComboBox()    
        self.trigCoupling.addItem("DC (0)",0)
        self.trigCoupling.addItem("AC (1)",1)
        self.trigCoupling.addItem("HF Reject (2)",2)
        self.trigCoupling.addItem("DC 50 O (3)",3)
        self.trigCoupling.addItem("AC 50 O (4)",4)
        self.trigCoupling.setCurrentIndex(3)
        self.trigCoupling.setMaximumWidth(myWidth)    
        self.paramsGrid.addWidget(QLabel("Trigger Coupling"),2,0)
        self.paramsGrid.addWidget(self.trigCoupling,3,0)

        self.trigSlope = QComboBox()      
        self.trigSlope.addItem("Pos. slope",0)
        self.trigSlope.addItem("Neg. slope",1)
        self.trigSlope.addItem("out of window",2)
        self.trigSlope.addItem("into window",3)
        self.trigSlope.addItem("HF divide",4)
        self.trigSlope.addItem("Spike stretcher",5)
        self.trigSlope.setCurrentIndex(1)
        self.trigSlope.setMaximumWidth(myWidth)   
        self.paramsGrid.addWidget(QLabel("Trigger event"),4,0)
        self.paramsGrid.addWidget(self.trigSlope,5,0)
        # response to a currentIndexChanged() event of self.trigSlope
        def trigSlopeChanged():
          if self.trigSlope.currentIndex()in (2,3):
            self.trigLevel2.setDisabled(False)
          else:
            self.trigLevel2.setDisabled(True)
        self.connect(self.trigSlope,SIGNAL("currentIndexChanged(int)"),trigSlopeChanged)

        self.triggerLevelGrid= QGridLayout()
        self.triggerLevelGrid.setVerticalSpacing(2)
        self.triggerLevelGrid.setHorizontalSpacing(5)
        myWidth2=40
        self.paramsGrid.addWidget(QLabel("Trigger levels (mV)"),6,0)
        self.trigLevel1 = QLineEdit("500.0")        
        self.trigLevel1.setMaximumWidth(myWidth2)   
        self.triggerLevelGrid.addWidget(self.trigLevel1,0,0)
        self.trigLevel2 = QLineEdit("600.0")        
        self.trigLevel2.setMaximumWidth(myWidth2)
        self.triggerLevelGrid.addWidget(self.trigLevel2,0,1)   
        self.paramsGrid.addItem(self.triggerLevelGrid,7,0)
          
        self.trigDelay = QLineEdit("400e-9")        
        self.trigDelay.setMaximumWidth(myWidth) 
        self.paramsGrid.addWidget(QLabel("Trigger delay (s)"),8,0)
        self.paramsGrid.addWidget(self.trigDelay,9,0)
          # horizontal parameters
        self.sampleInterval = QLineEdit("1e-9")
        self.sampleInterval.setMaximumWidth(myWidth)         
        self.paramsGrid.addWidget(QLabel("Sampling time (s)"),0,1)
        self.paramsGrid.addWidget(self.sampleInterval,1,1)
        # response to a editingFinished() event of sampleInterval
        def sampleIntervalChanged():
          minStep=0.5e-9
          if self.chCombine.currentIndex()>=1 and self.chCombine.currentIndex()<=6:
            minStep/=2
          elif self.chCombine.currentIndex()>=7 :
            minStep/=4
          step=floor(float(self.sampleInterval.text())/minStep)*minStep
          if step< minStep :
            mb=QMessageBox.warning(self, "Warning", "sampleInterval can't be shorter than "+str(minStep)+" s\n with the actual channel configuration.")
            step=minStep
          self.sampleInterval.setText(str(step))
            
        self.connect(self.sampleInterval ,SIGNAL("editingFinished ()"),sampleIntervalChanged)

        self.numberOfPoints = QLineEdit("1000")
        self.numberOfPoints.setMaximumWidth(myWidth)         
        self.paramsGrid.addWidget(QLabel("Samples/segment"),2,1)
        self.paramsGrid.addWidget(self.numberOfPoints,3,1)
        # response to a editingFinished() event of numberOfPoints
        def numberOfPointsChanged():
          self.numberOfPoints.setText(str(int(floor(float(self.numberOfPoints.text())))))
          if int(self.numberOfPoints.text())<1:
            self.numberOfSegments.setText("1")
            mb=QMessageBox.warning(self, "Warning", "Number of points >=1")
            
        self.connect(self.numberOfPoints ,SIGNAL("editingFinished()"),numberOfPointsChanged)
        
        self.numberOfSegments = QLineEdit("100")
        self.numberOfSegments.setMaximumWidth(myWidth)              
        self.paramsGrid.addWidget(QLabel("Segments/bank"),4,1)
        self.paramsGrid.addWidget(self.numberOfSegments,5,1)
        
        # response to a editingFinished() event of numberOfSegments
        def numberOfSegmentsChanged():
          self.numberOfSegments.setText(str(int(floor(float(self.numberOfSegments.text())))))
          if int(self.numberOfSegments.text())<1:
            self.numberOfSegments.setText("1")
            mb=QMessageBox.warning(self, "Warning", "Number of segments>=1")
          elif self.memType.currentIndex()==1 and int(self.numberOfSegments.text())>1000:
            self.nLoops.setText(str(int(self.numberOfSegments.text())/1000))
            self.numberOfSegments.setText("1000")
            mb=QMessageBox.warning(self, "Warning", "Number of segments<=1000 with internal memory.\nAdjust number of banks in acquisition,\nor swith to default memory.")
          elif self.memType.currentIndex()==0 and int(self.numberOfSegments.text())>16000:
            self.numberOfSegments.setText("16000")
            mb=QMessageBox.warning(self, "Warning", "Number of segments<=16000 with M32M extended memory.")
            
        self.connect(self.numberOfSegments ,SIGNAL("editingFinished()"),numberOfSegmentsChanged)
         
        self.numberOfBanks = QLineEdit("1")
        self.numberOfBanks.setMaximumWidth(myWidth)       
        self.numberOfBanks.setDisabled(True)        
        self.paramsGrid.addWidget(QLabel("Memory bank(s)"),6,1)
        self.paramsGrid.addWidget(self.numberOfBanks,7,1)
        
        self.nLoops = QLineEdit("1")
        self.nLoops.setMaximumWidth(myWidth)  
        self.paramsGrid.addWidget(QLabel("Acqs or banks/acq"),8,1)
        self.paramsGrid.addWidget(self.nLoops,9,1)
          # Ext sync and other config parameters
        self.synchro = QCheckBox("Ext 10MHz sync")
        self.synchro.setChecked(True)
        self.paramsGrid.addWidget(self.synchro,0,2)
        
        self.memType = QComboBox()     
        self.memType.addItem("default",0)
        self.memType.addItem("force internal",1)
        self.memType.setCurrentIndex(1)
        self.memType.setMaximumWidth(myWidth+10)     
        self.paramsGrid.addWidget(QLabel("Memory used"),2,2)
        self.paramsGrid.addWidget(self.memType,3,2)
        # response to a currentIndexChanged() event of self.memType
        def memTypeChanged():
            self.numberOfSegments.setFocus()
            self.numberOfSegments.clearFocus()
          
        self.connect(self.memType,SIGNAL("currentIndexChanged(int)"),memTypeChanged)
        
        self.configMode = QComboBox()     
        self.configMode.addItem("normal",0)
        self.configMode.addItem("start on trigger",1)
        self.configMode.addItem("sequence wrap",1)
        self.configMode.addItem("SAR mode",1)
        self.configMode.setCurrentIndex(0)
        self.configMode.setMaximumWidth(myWidth+10)     
        self.paramsGrid.addWidget(QLabel("Config mode"),4,2)
        self.paramsGrid.addWidget(self.configMode,5,2)
        # response to a currentIndexChanged() event of self.configMode
        def configModeChanged():
          if self.configMode.currentIndex()==3: # SAR mode: simultaneous acquisition and transfer
            self.numberOfBanks.setText("2")
            self.numberOfBanks.setDisabled(False)
            self.memType.setCurrentIndex(1)
            self.memType.setDisabled(True)
          else :
            self.numberOfBanks.setText("1")
            self.numberOfBanks.setDisabled(True)
            self.memType.setDisabled(False)
            if self.configMode.currentIndex()==1: # start on trigger
              a=1
            elif self.configMode.currentIndex()==2: # wrap mode
              a=1
            elif self.configMode.currentIndex()==0:   #normal
              a=1
          
        self.connect(self.configMode,SIGNAL("currentIndexChanged(int)"),configModeChanged)
        
        #Several data graphs in a QTabWidget.
        myWidth=4
        myHeight=3
        mydpi=80
        
        # single segment tab
        self.segmentTab = QWidget()
        self.segTabLayout = QGridLayout(self.segmentTab)
        st=self.segTabLayout
        st.addWidget(QLabel("Segment number:"))
        self.segmentNumber=QSpinBox()
        self.segmentNumber.setMinimum(1)
        self.segmentNumber.setValue(1)
        self.segmentNumber.setWrapping(True)
        self.segmentNumber.setMinimumWidth(50)
        st.addWidget(self.segmentNumber,0,st.columnCount ())
        self.connect(self.segmentNumber,SIGNAL("valueChanged(int)"),self.plotData)
        self.NumOfSegDislay=QLabel("(out of ??)")
        self.NumOfSegDislay.setMinimumWidth(50)
        st.addWidget(self.NumOfSegDislay,0,st.columnCount ())
        st.addWidget(QLabel("Time stamp (s)="),0,st.columnCount ())
        self.currentTimeStamp=QLabel("??")
        self.currentTimeStamp.setMinimumWidth(50)
        st.addWidget(self.currentTimeStamp,0,st.columnCount ())
        self.segTabLayout.addWidget(QLabel("Horiz. position (s)="),0,st.columnCount ())
        self.currentHorPos=QLabel("??")
        self.currentHorPos.setMinimumWidth(50)
        st.addWidget(self.currentHorPos,0,st.columnCount ())
        self.segmentPlot = MatplotlibCanvas(width=myWidth, height=150, dpi=mydpi)
        st.addWidget(self.segmentPlot,1,0,1,-1)
        
        # Averaged of segments tab
        self.averagePlot = MatplotlibCanvas(width=myWidth, height=myHeight, dpi=mydpi)
        
        # Full sequence tab
        self.sequenceTab = QWidget()
        self.sequenceTabLayout = QGridLayout(self.sequenceTab)
        self.overlay=QCheckBox("Overlay segments")
        self.sequenceTabLayout.addWidget(self.overlay)
        self.fullWavePlot = MatplotlibCanvas(width=myWidth, height=myHeight, dpi=mydpi)
        self.sequenceTabLayout.addWidget(self.fullWavePlot)
        self.connect(self.overlay,SIGNAL("stateChanged(int)"),self.plotData)
      
        # Timestamps tab
        self.timestampTab = QWidget()
        self.timestampTabLayout = QGridLayout(self.timestampTab)
        self.deltaTimestamps=QCheckBox("Delta Timestamps")
        self.timestampTabLayout.addWidget(self.deltaTimestamps)
        self.timeStampsPlot = MatplotlibCanvas(width=myWidth, height=myHeight, dpi=mydpi)
        self.timestampTabLayout.addWidget(self.timeStampsPlot)
        self.connect(self.deltaTimestamps,SIGNAL("stateChanged(int)"),self.plotData)
        
        # add all the tabs
        self.plotTabs = QTabWidget()
        self.plotTabs.setMinimumHeight(300)
        self.plotTabs.addTab(self.segmentTab,"Segments")
        self.plotTabs.addTab(self.averagePlot,"Average")
        self.plotTabs.addTab(self.sequenceTab,"Sequences")
        self.plotTabs.addTab(self.timestampTab,"TimeStamps")
        
        #Some buttons and checkboxes, their grid, and corresponding functions
        calibrateButton = QPushButton("Calibrate")
        configureButton = QPushButton("Configure")
        acquireButton = QPushButton("Acquire + transfer")
        plotButton = QPushButton("Plot")
        self.updatePlots = QCheckBox("Auto-plot",checked=True)
        self.transferAverage = QCheckBox("Transfer average only")
        self.waitingNewData=QLabel("\tHello :-)")
        self.waitingNewData.setStyleSheet("QLabel {color : red;}");
        self.waitingNewData.setVisible(True)
        # button grid
        buttonGrid = QBoxLayout(QBoxLayout.LeftToRight)
        buttonGrid.addWidget(calibrateButton)
        buttonGrid.addWidget(configureButton)
        buttonGrid.addWidget(acquireButton)      
        buttonGrid.addWidget(plotButton)
        buttonGrid.addWidget(self.updatePlots)
        buttonGrid.addWidget(self.transferAverage)
        buttonGrid.addWidget(self.waitingNewData)
        buttonGrid.addStretch()
          # connections between buttons' clicked() signals and corresponding functions
        self.connect(calibrateButton,SIGNAL("clicked()"),self.requestCalibrate)
        self.connect(configureButton,SIGNAL("clicked()"),self.requestConfigure)
        self.connect(acquireButton,SIGNAL("clicked()"),self.requestAcquire)
        self.connect(plotButton,SIGNAL("clicked()"),self.plotData)

        #The grid layout for delivering messages: messageGrid.
        self.messageGrid = QGridLayout()
        self.messageGrid.setVerticalSpacing(2)
        self.messageGrid.setHorizontalSpacing(10)
        self.errorString=QLabel("")
        self.messageString = QLineEdit("")
        self.messageString.setReadOnly(True)
        self.mess=QLabel("Last message:")
        self.mess.setMaximumWidth(70)
        self.messageGrid.addWidget(self.mess,0,0)
        self.messageGrid.addWidget(self.messageString,0,1)

        #The grid layout of the whole frontpanel:
        self.grid = QGridLayout()
        self.grid.setHorizontalSpacing(20)
        
        self.grid.addItem(self.channelGrid,0,0)
        self.grid.addWidget(self.plotTabs,1,0,1,2)
        self.grid.addItem(self.paramsGrid,0,1)        
        self.grid.addItem(buttonGrid,2,0,1,2)
        self.grid.addItem(self.messageGrid,3,0,1,2)

        self.setLayout(self.grid)
        
        self._updatePlots = False
        #We request the current parameters from the card.
        self.instrument.dispatch("parameters")
       
        # auto refresh of front panel based on a timer
        timer = QTimer(self)
        timer.setInterval(2000)
        timer.start()
        self.connect(timer,SIGNAL("timeout()"),self.onTimer)
