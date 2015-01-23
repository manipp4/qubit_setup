import numpy
import scipy
from pyview.lib.datacube import *
from pyview.helpers.datamanager import DataManager
from pyview.helpers.instrumentsmanager import Manager
from pyview.lib.smartloop import *
dataManager = DataManager()
instrumentManager=Manager()

vna=instrumentManager.getInstrument('vna')
print vna
coil=instrumentManager.getInstrument('Yoko1')
gaussmeter=instrumentManager.getInstrument('Gaussmeter')

##
cubeName='coilRoomTemp'
yoko=coil
xName='fluxLine_Voltage'
xMin,xMax,xStep=32,-32,-1
slewRate=4
waitingTime=6

data=Datacube(cubeName)
data.toDataManager()
megaLoop=SmartLoop(1,1,1000000,name='megaLoop')
for index in megaLoop:
	xList=SmartLoop(xMin,xStep,xMax,name=xName)
	for x in xList:
		print xName," = ", x
		yoko.setVoltage(x,slewRate=slewRate)
		time.sleep(waitingTime)
		data.set(voltage=x,fieldInGauss=float(gaussmeter.readField()),columnOrder=['voltage','fieldInGauss'],commit=True)
	xMin,xMax,xStep=xMax,xMin,-xStep
data.savetxt()