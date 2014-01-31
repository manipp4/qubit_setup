##2D Spectro
from pyview.lib.datacube import *

from matplotlib.pyplot import *
import numpy
#reload(sys.modules["pyview.helpers.instrumentsmanager"])
import scipy
from pyview.helpers.datamanager import *
from pyview.helpers.datamanager import DataManager
dataManager = DataManager()
##
data=gv.data
print data

nbrChild=len(data.children())
nbrPoints=len(data.children()[0]['v'])

print nbrChild,nbrPoints

#Chi=numpy.zeros((nbrPoints,nbrChild-1))
Chi=numpy.zeros((nbrPoints,nbrChild-1))

for i in range(1,nbrChild):
	child=data.children()[i]
	l=0
	for j in range(0,nbrPoints):
		if child['bluePower'][l]==data['bluePower'][j]:
			Chi[j,i-1]=1
			l+=1
		if l==len(child['bluePower']):break

#
figure()
imshow(Chi)
draw()
show()










