from pyview.lib.datacube import *


d=Datacube()
d.toDataManager()
for i in range(0,10):
	c=Datacube()
	d.addChild(c,v=i**2)
	for j in range(0,20):
		c.set(j=j,k=sqrt(j))
		c.commit()
d.savetxt()
####
di=Di()
for c in d.children():
	for k in d.attributesOfChild(c).keys():
		di.append(k)
print di	
##
class Di(list):
	def myAppend(self,obj):
		print self, obj
		if not(obj in self):
			self.append(obj)
##
a=Di()
##
a.myAppend(3)
##
print gv.d.attributesOfChildren()