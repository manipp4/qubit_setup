#######################################################
## for Datacube-type of scans with a regular grid ##
#######################################################
import scipy
from numpy import *
from matplotlib.pyplot import *
from matplotlib.gridspec import *
from pyview.lib.datacube import *
from matplotlib.mlab import *
import math
## Load the Global variable set in the data manager. ##
## If the data consists of several VNA traces the ploted ##
## dimensions will be (rows=len(data), columns=len(data.child['{name of channel}'])
data = gv.data

##
def Plot2D(data=''):
	## make axis
	# y
	# y
	if data=='':
		ymin=-4.5
		ymax=-1.6
		ystep=0.1
	else:
		ymin=data['attenuation'][0]
		ymax=data['attenuation'][-1]
		ystep=data['attenuation'][1]-data['attenuation'][0]
	ypoints=int((ymax-ymin)/ystep)+1
	y=arange(ymin,ymax,ystep)
	
	#x
	xmin=data.children()[0]['f_GHz'][0]
	xmax=data.children()[0]['f_GHz'][-1]
	xstep=data.children()[0]['f_GHz'][1]-data.children()[0]['f_GHz'][0]
	xpoints=int((xmax-xmin)/xstep)+1
	x=linspace(xmin,xmax,xpoints)
	##create matrix z
	z=zeros((len(x),len(y)))
	k=0
	for i in range(len(y)):
		z[:,i]=data.children()[i]['amp']
	
	figure()
	clf()
	cla()
	imshow(rot90(log(z)),aspect = 'auto',extent = (x[0],x[-1],y[0],y[-1]),interpolation = 'nearest',cmap='jet')
	xlabel("Frequency [GHz]")
	ylabel("attenuation [mV]")
	colorbar()
	show()
##
def createMatrix(data=''):
	## make axis
	# y
	if data=='':
		ymin=-4.5
		ymax=-1.6
		ystep=0.1
	else:
		ymin=data['attenuation'][0]
		ymax=data['attenuation'][-1]
		ystep=data['attenuation'][1]-data['attenuation'][0]
	ypoints=int((ymax-ymin)/ystep)+1
	y=arange(ymin,ymax,ystep)
	
	#x
	xmin=data.children()[0]['f_GHz'][0]
	xmax=data.children()[0]['f_GHz'][-1]
	xstep=data.children()[0]['f_GHz'][1]-data.children()[0]['f_GHz'][0]
	xpoints=int((xmax-xmin)/xstep)+1
	x=linspace(xmin,xmax,xpoints)
	##create matrix z
	z=zeros((len(x),len(y)))
	k=0
	for i in range(len(y)):
		z[:,i]=data.children()[i]['amp']
	
	return z
##
gData=data
figG=Plot2D(data=gData)
##
figE=Plot2D(data=eData)

##
print len(data)
##
f, axarr = subplots(2, sharex=True)
axarr[0].imshow(rot90(zG),aspect = 'auto',interpolation = 'nearest',cmap='jet')
axarr[0].set_title('Freq %s GHz'%round(data['frequency01'][0],3))
axarr[1].imshow(rot90(zE),aspect = 'auto',interpolation = 'nearest',cmap='jet')
show()
##
data=data3
##
f, axarr = subplots(3,len(data), sharex=True,sharey=True)
for i in range(len(data)):
	gData=data.children()[i].children()[3]
	eData=data.children()[i].children()[4]
	zG=createMatrix(data=gData)
	zE=createMatrix(data=eData)
	zDiff=zE/zG
	axarr[0,i].imshow(rot90(log(zG)),aspect = 'auto',interpolation = 'nearest',cmap='jet',extent=(7.06,7.1,4.5,1))
	axarr[0,i].set_title('D=%s GHz'%(7.0794-round(data['frequency01'][i],3)))
	axarr[1,i].imshow(rot90(log(zE)),aspect = 'auto',interpolation = 'nearest',cmap='jet',extent=(7.06,7.1,4.5,1))
	axarr[2,i].imshow(rot90(zDiff),aspect = 'auto',interpolation = 'nearest',cmap='jet',extent=(7.06,7.1,4.5,1))
	axarr[2,i].set_xlabel('Freq [GHz]')
	axarr[2,i].set_xticks([7.06,7.08,7.1])
f.subplots_adjust(hspace=0.1)	
show()
	
##
print data.children()[0].children()[3][']