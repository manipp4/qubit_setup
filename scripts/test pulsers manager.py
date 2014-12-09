from pyview.helpers.instrumentsmanager import Manager
from pyview.lib.datacube import Datacube
import numpy as np

pm=Manager().getInstrument('pulsersManager')
print pm
print [i[0].name() for i in pm._generators]
###
pg_f1=Manager().getInstrument('pg_f1')
pg_f2=Manager().getInstrument('pg_f2')
pg_f3=Manager().getInstrument('pg_f3')
pg_f4=Manager().getInstrument('pg_f4')

def generateFunc(filename=None):
	if filename==None:
		print "using gv.c1"
		d=gv.c1
		cor=np.zeros(20000)
		cor[-999:]=d['correction']
	else:
		d=Datacube()
		d.loadtxt(filename)
		d.toDataManager()
		d.savetxt()
		cor=np.zeros(20000)
		cor[-999:]=d['y']
	
	def myCorrFunc(ishape):
		shape=np.zeros(20000)
		for i in range(1,20000):
			if(abs(cor[-(i+1)])<1e-5):continue
			shape[i-1:-1]+=ishape[:-(i)]*cor[-(i+1)]
		return shape
		
	return myCorrFunc


##
pg_f1.pulseCorrectionFunction=generateFunc("M:\\2014\\scalable architecture\\FluxCalib\\11_28\\cor1.txt")
##
pg_f1.pulseCorrectionFunction=generateFunc()
##
pg_f1.pulseCorrectionFunction=identity

pg_f2.pulseCorrectionFunction=generateFunc("M:\\2014\\scalable architecture\\FluxCalib\\11_28\\cor2.txt")
pg_f3.pulseCorrectionFunction=generateFunc("M:\\2014\\scalable architecture\\FluxCalib\\11_28\\cor3.txt")
pg_f4.pulseCorrectionFunction=generateFunc("M:\\2014\\scalable architecture\\FluxCalib\\11_28\\cor4.txt")


##
gl=pm._generators
[p[0].clearPulse() for p in gl]
##
[p[0].addPulse(generatorFunction='square',start=10000,stop=20000, applyCorrections=True,amplitude=0.5) for p in gl]
[p[0].preparePulseSequence() for p in gl]
[p[0].sendPulseSequence() for p in gl]
##
pm._generators[0][0].pulseCorrectionFunction=identity
##
def myCorrFunc(ishape):
	shape=np.zeros(20000)
	for i in range(1,20000):
		if(abs(cor[-(i+1)])<1e-5):continue
		shape[i-1:-1]+=ishape[:-(i)]*cor[-(i+1)]
	return shape
def identity(shape):return shape

##
d=Datacube()
d.loadtxt("M:\\2014\\scalable architecture\\vs7-12-b5\\run1\\calib\\cor1.txt")
d.toDataManager()
d.savetxt()
cor=np.zeros(20000)
cor[-999:]=d['y']
##
d2=Datacube('wave')
d2.toDataManager()
d2.createColumn('cor',cor)
##
ishape=np.zeros(20000)
ishape[10000:]=1.
d2.createColumn('shape',ishape)
##
import time
t0=time.time()
shape=np.zeros(20000)
for i in range(1,20000):
	if(abs(cor[-(i+1)])<1e-5):continue
	shape[i:]+=ishape[:-(i)]*cor[-(i+1)]
print time.time()-t0
d2.createColumn('fshape',shape)



##

shape=np.zeros(20000)
shape[9500:10499]=gv.d['y'][:]
[p[0].clearPulse() for p in pm._generators]
[p[0].addPulse(generatorFunction='arb',shape=shape) for p in pm._generators]
[p[0].preparePulseSequence() for p in pm._generators]
[p[0].sendPulseSequence() for p in pm._generators]
##
[p[0].clearPulse() for p in pm._generators]
[p[0].addPulse(generatorFunction='square',start=10000,stop=20000,amplitude=0.78) for p in pm._generators]
[p[0].preparePulseSequence() for p in pm._generators]
[p[0].sendPulseSequence() for p in pm._generators]
##



##

pm._generators[0][0].addPulse(generatorFunction='square',start=1000,stop=2000,frequency=4,pulseOn=False)
pm._generators[0][0].addPulse(generatorFunction='square',start=0000,stop=2600,frequency=4)
pm._generators[0][0].addPulse(generatorFunction='square',start=5000,stop=6000,frequency=4,pulseOn=False)
pm._generators[0][0].addPulse(generatorFunction='square',start=7000,stop=8000,frequency=4)
pm._generators[1][0].addPulse(generatorFunction='square',start=7000,stop=8000,frequency=4)
pm._generators[1][0].addPulse(generatorFunction='square',start=4000,stop=8000,frequency=4,pulseOn=False)
pm._generators[1][0].addPulse(generatorFunction='square',start=5000,stop=5500,frequency=4)
pm._generators[1][0].addPulse(generatorFunction='square',start=8000,stop=9000,frequency=4,pulseOn=False)
##