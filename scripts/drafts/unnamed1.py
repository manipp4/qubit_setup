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
##
print fitQubitFrequency(data,variable = "p")
##
qb._f01=8.791

##
qb.measureRabi(0,500,1,power=-12.)
##
qb._rabiPower=-12.
qb._rabiDuration=9.
##
qb.measureT1(0,1000,2)

##
data.parameters()['defaultPlot']=[]

##
gv.data.savetxt()
##
coil=instrumentManager.getInstrument('coil')
coil.setVoltage(-0.25,slewRate=0.1)
##
import math
def p(omega,Q):
	return 10*math.log(1.05E-34*omega**2/(4*1E-3*Q),10)
	
	
##
from numpy import *
from matplotlib.pyplot import *
Q=linspace(200,2000,1000)
F=linspace(2E9,15E9,1000)
chi=zeros((1000,1000))
i=0
for q in Q:
	j=0
	for f in F:
		chi[i,j]=p(f*2*math.pi,q)
		j+=1
	i+=1
#

##
figure()
#
imshow(chi,aspect = 'auto',extent = (2,15,200,2000),interpolation = 'nearest')
xlabel("Frequency [GHZ]")
ylabel("Q factor")
colorbar()
draw()
show()
#savefig("fig.png")
##
print p(7E9*2*math.pi,800.)

##

print 4.*1E-3*10**(-113./10)*800/(1.05E-34*(2*math.pi*6.75E9)**2)
##
V=0.224*10**(-135/20)
R=25
omega=2*math.pi/40E-9
print omega
hbar=1.05E-34
T1=V**2/(2*R*omega**2*hbar)
print T1
