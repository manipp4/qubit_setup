from pyview.helpers.instrumentsmanager import *

acqiris=Manager().getInstrument('acqiris')
print acqiris
##


print acqiris("DLLMath1Module.mathDLLVersion()")
##
del A
class A:
	def __str__(self):
		return 'object'
	def __getattr__(self,att):
		return 'asked value : ' + str(att)
##
a=A()
print a

print a.dll1.mean()

###
i=a.dll.ask('1+1')
##
i=1+1
print i
####

class B:
	pass
	
b=B()
##
b.a=1
print b.a
r=b.a
r=1
##
print b.__slots__()

##


from pyview.helpers.instrumentsmanager import *
from pyview.helpers.datamanager import *
from pyview.lib.datacube import *
dm=DataManager()
m=Manager()

##
print m.saveState("test")
##
d=Datacube()
dm.addDatacube(d)
d.setParameters(m.saveState("test"))
##
print d.parameters()
##
import yaml
yaml.dump(d.parameters())

##
print d.savetxt()
##
print type(d.parameters()['acqiris']['state']['offsets'][0])

