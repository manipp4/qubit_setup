from pyview.lib.datacube2 import *
##
data=Datacube('cubeName')
data.toDataManager()
# defaultPlot ???
data.set(b=0,a=1,columnOrder=['a','b'])
data.createColumn(freq=listOfreqs)
child=Datacube('childName')
data.addChild(child)
data.plotInDataManager()