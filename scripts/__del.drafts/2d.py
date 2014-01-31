

from pyview.helpers.datamanager import DataManager

dataManager = DataManager()

##
figure("spectro")
cla()
for i in range(0,len(data['i'])):
	child=data.children()[i]
	v=data['v'][i]
	print v
	plot(child['freq'],child['mag']+30*v)
	draw()
	show()

## 2D SPECTRO WITH VNA
from numpy import *
from matplotlib.pyplot import *
from pyview.lib.datacube import *

length=-1
reverse=False
for j in range(0,1000):
	try:
		data = gv.data
		if length>0:p = zeros((length,len(data['i'])-1))
		if length<0:p = zeros((len(data.children()[0]),len(data['i'])))
		if length>0:phi = zeros((length,len(data['i'])-1))
		if length<0:phi = zeros((len(data.children()[0]),len(data['i'])))
		
			
		for i in range(0,len(data['i'])):
			if reverse:	j=len(data['i'])-i-1
			else:j=i
			child=data.children()[j]
			if length<0:l=len(child['mag'])
			else: l=length
	#		for k in range(0,l):
	#			p[k,i]=child['p'][k]
	#			p[k,i]=max(0.2,min(child['p'][k],0.4)	)
	#		child.sortBy('f',reverse=True)
			if length>0:p[::-1,i] = child['mag'][:length]
			if length<0:p[::-1,i] = child['mag']
			if length>0:phi[::-1,i] = child['phase'][:length]
			if length<0:phi[::-1,i] = child['phase']
		v1=data['v'][0]
		v2=data['v'][i]
		if reverse:[v1,v2]=[v2,v1]		
		clf()
		cla()
		
		figure("f")
			
		subplot(121)
		title("Mag")
		imshow(p,aspect = 'auto',extent = (v1,v2,child["freq"][0]*1e-9,child['freq'][length]*1e-9),interpolation = 'nearest')
		xlabel("Coil voltage [V]")
		ylabel("frequency [GHz]")
		colorbar()
		
		subplot(122)
		title("Phase")
		imshow(phi,aspect = 'auto',extent = (v1,v2,child["freq"][0]*1e-9,child['freq'][length]*1e-9),interpolation = 'nearest')
		xlabel("Coil voltage [V]")
#		ylabel("frequency [GHz]")
		colorbar()


		figtext(0.05,0.01,data.filename())

		draw()
		show()
#		savefig("%s.pdf" %data.name())
	except:
		#print "error"
		raise
	finally:
		time.sleep(1)
		
		
## 2D QUBIT SPECTRO VS FLUX
from numpy import *
from matplotlib.pyplot import *
from pyview.lib.datacube import *

length=-1
for j in range(0,1):
	try:
		data = gv.data
		if length>0:p = zeros((length,len(data['i'])))
		if length<0:p = zeros((len(data.children()[0]),len(data['i'])))
		p+=0.0075
			
		for i in range(0,len(data['i'])):
			child=data.children()[i]
			if length<0:l=len(child['p'])
			else: l=length
	#		for k in range(0,l):
	#			p[k,i]=child['p'][k]
	#			p[k,i]=max(0.2,min(child['p'][k],0.4)	)
#			child.sortBy('f',reverse=True)
			if length>0:p[:,i] = child['p'][:length]
			if length<0:p[:len(child['p']),i] = child['p']
		v1=data['p'][0]
		v2=data['p'][i]
		clf()
		cla()
		figure("f")
		imshow(p,aspect = 'auto',extent = (v1,v2,child["f"][length],child['f'][0]),interpolation = 'nearest')
		xlabel("Power [dB]")
		ylabel("frequency [GHz]")
		colorbar()
		figtext(0.05,0.01,data.filename())
		draw()
		show()
	except:
		#print "error"
		raise
	finally:
		time.sleep(1)
##
from numpy import *
from matplotlib.pyplot import *
from pyview.lib.datacube import *

length=-1
reverse=True
for j in range(0,1):
	try:
		data = gv.data
		print data
		if length>0:p = zeros((length,len(data['i'])))
		if length<0:p = zeros((len(data.children()[0].children()[0]),len(data['vi'])))
			
		for i in range(0,len(data['vi'])):
			child=data.children()[i].children()[0]
			if length<0:l=len(child['p'])
			else: l=length
	#		for k in range(0,l):
	#			p[k,i]=child['p'][k]
	#			p[k,i]=max(0.2,min(child['p'][k],0.4)	)
#			child.sortBy('f',reverse=True)
			if reverse:
				if length>0:p[::-1,i] = child['p'][:length]
				if length<0:p[::-1,i] = child['p']
			else:
				if length>0:p[:,i] = child['p'][:length]
				if length<0:p[:len(child['p']),i] = child['p']
		v1=data['v'][0]
		v2=data['v'][i]
		if reverse: [v1,v2]=[v2,v1]
		clf()
		cla()
		figure("f")
		imshow(p,aspect = 'auto',extent = (v1,v2,child["f"][0],child['f'][length]),interpolation = 'nearest')
		xlabel("Coil Voltage [V]")
		ylabel("frequency [GHz]")
		colorbar()
		figtext(0.05,0.01,data.filename())
		draw()
		show()
	except:
		#print "error"
		raise
	finally:
		time.sleep(1)
##
from numpy import *
from matplotlib.pyplot import *
from pyview.lib.datacube import *

length=-1
for j in range(0,1000):
	data = gv.data
	if length>0:p = zeros((length,len(data['i'])))
	if length<0:p = zeros((len(data.children()[0]),len(data['i'])))
	step=abs(data.children()[0]['f'][1]-data.children()[0]['f'][0])
	maxf=data.children()[0]['f'][-1]
	minf=data.children()[0]['f'][0]
	for i in range(0,len(data['i'])):
		child=data.children()[i]
		maxf=max(maxf,max(child['f']))
		minf=min(minf,min(child['f']))
	p=zeros(((maxf-minf)/step+2,len(data['v'])))
	for i in range(0,len(data['i'])):
		child=data.children()[i]
		child.sortBy('f')
		fstart=child['f'][0]
		fstop=child['f'][-1]
		nf=len(child['f'])
		p[round((fstart-minf)/step):round((fstart-minf)/step)+len(child['p']),i]=child['p']
#		if length<0:l=len(child['p'])
#		else: l=length
#		for k in range(0,l):
#			p[k,i]=child['p'][k]
#			p[k,i]=max(0.2,min(child['p'][k],0.4)	)
#		child.sortBy('f',reverse=True)
#		if length>0:p[:,i] = child['p'][:length]
#		if length<0:p[:,i] = child['p']
	v1=data['v'][0]
	v2=data['v'][i]
	
	clf()
	cla()
	
	figure("f")
	title("p(JBA9.38)")
	p[:]=p[::-1]
	p[:,:]=p[:,::-1]
	imshow(p,aspect = 'auto',extent = (v2,v1,minf,maxf),interpolation = 'nearest')
	xlabel("vFlux2 [V]")
	ylabel("Frequency [GHz]")
	figtext(0.05,0.01,data.filename())
	colorbar()
	draw()
	show()
	time.sleep(1)
	
##
data=gv.data
p=data.table()[2]


####





## 2D SPECTRO WITH VNA
from numpy import *
from matplotlib.pyplot import *
from pyview.lib.datacube import *

length=-1
number=-0#-1 if not finished, 0 else
reverse=False

for j in range(0,10000):
	try:
		data = gv.data
		if length>0:p = zeros((length,len(data['i'])-1))
		if length<0:p = zeros((len(data.children()[0]),len(data.children())+number))
		
			
		for i in range(0,len(data.children())+number):
			if reverse:	j=len(data.children())-i-1
			else:j=i
			child=data.children()[j]
			if length<0:l=len(child['b0'])
			else: l=length
	#		for k in range(0,l):
	#			p[k,i]=child['p'][k]
	#			p[k,i]=max(0.2,min(child['p'][k],0.4)	)
	#		child.sortBy('f',reverse=True)
			c=zeros((len(data.children()[0])))
			c[:len(child['b0'])]=child['b0']-mean(child['b0'])
			if length>0:p[::-1,i] = child['b0'][:length]
			if length<0:p[::-1,i] = c
		v1=-2;#data['v'][0]
		v2=float(child.name()[2:]);#data['v'][i]0.
		if reverse:[v1,v2]=[v2,v1]		
		clf()
		cla()
		

		title(data.name())
		imshow(p,aspect = 'auto',extent = (v1,v2,data.children()[0]["f"][0],data.children()[0]['f'][length]),interpolation = 'nearest')
		xlabel("Flux line %i voltage [V]"%int(data.name()[-1]))
		ylabel("frequency [GHz]")
		colorbar()
		


		figtext(0.05,0.01,data.filename())

		draw()
		show()
		time.sleep(1)
		savefig("pulsed/jba6.86 %s.png" %data.name())
	except:
		print "error" 
	#	raise
	finally:
		time.sleep(1)
##
from numpy import *
from matplotlib.pyplot import *
from pyview.lib.datacube import *
import scipy

data=gv.data
XY=zeros((len(data),2))
XY[:,0]=data['p_added']
XY[:,1]=data['f_added']
p=data['p_jba']
print len(XY),len(p)
gridData=scipy.interpolate.griddata(XY,p,(arange(6.6,6.8,0.01),arange(-70,-30,1.)),method='nearest',fill_value=0.)
imshow(gridData.T, origin='lower')







