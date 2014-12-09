################################
## for Datacube-type of scans ##
###############################
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
## load x axis

x=data['coilCurrent']

# make y axis if y passes a maximum ymax can be set manually

localfreq0=data.children()[0].children()[1]['f']
localfreqm1=data.children()[-1].children()[1]['f']
ymin=localfreq0[0]
ystep=localfreq0[1]-localfreq0[0]
npointslocal=len(localfreq0)
ymax=7.0#localfreqm1[-1]
npoints=int((ymax-ymin)/ystep)+2
y=linspace(ymin,ymax,npoints)

#find the correct part of y axis
localamp0=data.children()[0].children()[1]['amp']
znorm=mean(localamp0)
z=ones((len(x),len(y)))*0
for i in range(len(x)):
	ydata=data.children()[i].children()[1]['f']
	y0=min(y, key=lambda x:abs(x-ydata[0]))
	y0indx=where(y==y0)[0][0]
	# load data to the correct part of the y axis
	zdata=data.children()[i].children()[1]['amp']
	normz=mean(zdata[:10])
	npointslocal=len(data.children()[i].children()[1]['f'])
	for j in range(y0indx,y0indx+npointslocal-1):
	 	z[i,j]=zdata[j-y0indx]/normz

clf()
cla()
imshow(rot90(z),aspect = 'auto',extent = (x[0],x[-1],y[0],y[-1]),interpolation = 'nearest',cmap='jet')
xlabel("Current")
ylabel("Frequency")
colorbar()
draw()
show()	
