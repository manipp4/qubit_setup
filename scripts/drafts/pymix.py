##curve
from config.instruments import *
from matplotlib.pyplot import *
from pyview.gui.mpl.backend import figure
import numpy
import scipy
instrumentManager=Manager()
jba=instrumentManager.getInstrument('jba_qb1')
co=jba.takePoint()[0]
##
cla()
scatter(co[:,0],co[:,1])
draw()
show()
##
from pymix import mixture

##
data=mixture.DataSet()
data.fromArray(co[:,0])
print data
##
n1 = mixture.NormalDistribution(-2,0.4)
n2 = mixture.NormalDistribution(2,0.6)
m = mixture.MixtureModel(2,[0.5,0.5], [n1,n2])
print m
print n1
##
m.EM(data,40,0.1)
