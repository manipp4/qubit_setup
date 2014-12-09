#######################################################
## for Datacube-type of scans with an irregular grid ##
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
## make axis
# x

xmin=min(Idata)*1000 #scale to mA
xmax=max(Idata)*1000
xstep=(Idata[1]-Idata[0])*1000
xpoints=int((xmax-xmin)/xstep)+1
x=linspace(xmin,xmax,xpoints)

#y
ymin=4
ymax=7.8
ystep=data.children()[0].children()[1]['f'][1]-data.children()[0].children()[1]['f'][0]
ypoints=int((ymax-ymin)/ystep)+1
y=linspace(ymin,ymax,ypoints)
##create matrix
z=zeros((len(x),len(y)))
## find which x coordinates to the data
Idata=data['coilCurrent']*1000 #scale to mA
print x, Idata
##
k=0
for i in range(len(x)):
	if x[i]-Idata[k]<xstep/2:
		ydata=data.children()[k].children()[1]['f']
		y0=min(y, key=lambda x:abs(x-ydata[0])) # this does: which point in the 'y' grid is the first datapoint 'ydata[0]' closes to
		y0indx=where(y==y0)[0][0]
		# load data to the correct part of the y axis
		zdata=data.children()[k].children()[1]['amp']
		normz=mean(zdata[:10])
		npointslocal=len(data.children()[i].children()[1]['f'])
		for j in range(y0indx,y0indx+npointslocal-1):
		 	z[i,j]=zdata[j-y0indx]/normz
		k=k+1
	
	
		
##
#
# load data
#localamp0=data.children()[0].children()[1]['amp']
#znorm=mean(localamp0)
x1=Idata*1000
z=zeros((len(x),len(y)))
k=0
for i in range(len(data.children())-1):
	for n in x1:
		if n-x[i]<xstep/2:
			ydata=data.children()[i].children()[1]['f']
			y0=min(y, key=lambda x:abs(x-ydata[0])) # this does: which point in the 'y' grid is the first datapoint 'ydata[0]' closes to
			y0indx=where(y==y0)[0][0]
			# load data to the correct part of the y axis
			zdata=data.children()[i].children()[1]['amp']
			normz=mean(zdata[:10])
			npointslocal=len(data.children()[i].children()[1]['f'])
			for j in range(y0indx,y0indx+npointslocal-1):
			 	z[i,j]=zdata[j-y0indx]/normz
		else:
			print i,x[i]

clf()
cla()
imshow(rot90(z),aspect = 'auto',extent = (x[0],x[-1],y[0],y[-1]),interpolation = 'nearest',cmap='jet')
xlabel("Current")
ylabel("Frequency")
colorbar()
draw()
show()	
##



