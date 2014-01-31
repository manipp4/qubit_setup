""
##
from config.instruments import *
from matplotlib.pyplot import *
import numpy
import scipy
from pyview.helpers.datamanager import DataManager
dataManager = DataManager()
instrumentManager=Manager()
register=instrumentManager.getInstrument('register')
acqiris=instrumentManager.getInstrument('acqiris')
pa_jba=instrumentManager.getInstrument('pa_jba')
print acqiris,pa_jba
##
for i in range(0,100):
	time.sleep(.1)
	wf=acqiris.AcquireTransferV4(nLoops=2)
##
(wf,hr)=acqiris.AcquireTransferV4(nLoops=10)

print wf
#
print len(wf[0])
##
acqiris.setNLoops(5)
##
print acqiris.getNLoops()
##
frequencies=pa_jba._frequencies.values()
print frequencies
##
figure()
##
cla()
while True:
	co=acqiris.frequenciesAnalyse(frequencies=frequencies)[0]
	plot(co[1,0],co[1,1],'o')
	draw()
	show()
##
co=acqiris.frequenciesAnalyse(frequencies=[[0.070000000000000284, True, 1],[0.020000000000000284, True, 2]])[0]
print co
##
pa_jba.clear()


##
jba2=instrumentManager.getInstrument('jba_qb2')
print jba2
##
data=Datacube()
data.set(
##
r=jba2.measure()[1]
#
print r
##data.set(**r)
####
import numpy
print "done"
numpy.zeros((4,2e6))
##
print numpy.setbufsize(16384)
##
print 'maxint    :', sys.maxint
print 'maxsize   :', sys.maxsize
print 'maxunicode:', sys.maxunicode