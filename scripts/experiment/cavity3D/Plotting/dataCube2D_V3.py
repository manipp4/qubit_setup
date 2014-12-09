#######################################################
## for Datacube-type of scans with an irregular grid ##
#######################################################
import scipy
from numpy import *
from matplotlib.pyplot import *
from matplotlib.gridspec import *
from pyview.lib.datacube2 import *
from matplotlib.mlab import *
from mpl_toolkits.mplot3d import Axes3D
import math
## Load the Global variable set in the data manager. ##
## If the data consists of several VNA traces the ploted ##
## dimensions will be (rows=len(data), columns=len(data.child['{name of channel}'])

# load data
data = gv.data

## load utility functions
def makePlotMatrix(xname,yname,zname):
# Assumes x or y is table in the data cube and that the other is a table in the child in the child
# It returns the x axis, y axis and the z matrix with the values at each coordinate with the positive directons up and right

# arrange parent and child to x and y axis
	try:
		xdat=data[xname]
		#xdat=arange(-0.05,0.051,0.0005)
		ydat=data.children()[0][yname]
		if ydat[0]<ydat[-1]:
			invertChild=True
			yNew=ydat
		else:
			invertChild=False
			yNew=ydat[::-1]
		if xdat[0]>xdat[-1]:
			invertParent=True
			xNew=xdat[::-1]
		else:
			invertParent=False
			xNew=xdat
		xInParent=True
	except:
		ydat=data[yname]
		xdat=data.children()[0][xname]
		if ydat[0]>ydat[-1]:
			invertParent=True
			yNew=ydat[::-1]
		else:
			invertParent=False
			yNew=ydat
		if xdat[0]>xdat[-1]:
			invertChild=True
			xNew=xdat[::-1]
		else:
			invertChild=False
			xNew=xdat
		xInParent=False
	#create z matrix
	zdat=zeros((len(ydat),len(xdat)))
	#load z values into matrix
	for i in range(len(data.children())):
		#set positive y axis to up
		if invertParent:
			j=-i
		else:
			j=i
		# set positive x axis to rigth
		if xInParent:
			zTemp=zdat.transpose()	
			if invertChild:
				zTemp[i]=data.children()[j][zname][::-1]
			else:		
				zTemp[i]=data.children()[j][zname]
			zNew=zTemp.transpose()
		else:
			zNew=zdat
			zNew[i]=data.children()[j][zname]
	
	return xNew, yNew, zNew	

def plot2dData(xname,yname,zname):
#plots 2D data of teh currently active global variable data called data
	xd,yd,zd=makePlotMatrix(xname,yname,zname)
	imshow(zd,aspect = 'auto',extent = (xd[0],xd[-1],yd[0],yd[-1]),interpolation = 'nearest',cmap='jet')
	colorbar()
	xlabel(xname)
	ylabel(yname)
	show()
	cla()
	clf()
	

##
# load data
data = gv.data	
## PLot
plot2dData('current','freq','mag')


##################
## play zone ##### 
xd,yd,zd=makePlotMatrix('current','freq','mag')
##
a=data.children()[0]['mag']
b=data.children()[0]['mag'][::-1]
print a[0],a[-1]
print b[0],b[-1]
##
pcolor(zd)
show()
cla()
clf()
##
imshow(zd,aspect = 'auto',extent = (xd[0],xd[-1],yd[0],yd[-1]),interpolation = 'nearest',cmap='jet')
colorbar()
xlabel("Current")
ylabel("Frequency")
show()
cla()
clf()




