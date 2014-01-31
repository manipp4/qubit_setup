import scipy
from numpy import *
from matplotlib.pyplot import *
from pyview.lib.datacube import *

data = gv.data

##
figure('test5')
cla()
clf()
XY=plot2D(datacube=data,xChannel='v',yChannel='f',zChannel='p',numbersOfPoints=[200,1000])
draw()
show()
##
print XY
##
XY=[[0,1],[1,1],[1,0]]
p=[1,1,1]
gridData=scipy.interpolate.griddata(XY,p,(xgrid,ygrid),method='nearest',fill_value=0.)

##
def plot2D(datacube,xChannel,yChannel,zChannel,ranges=None,numbersOfPoints=None):
	dimension=0
	for i in range(0,len(datacube['i'])):
		dimension+=len(datacube.children()[i])
	


	p=zeros((dimension))
	XY=zeros((dimension,2))
	index=0
	for i in range(0,len(datacube['i'])):
		for j in range(0,len(datacube.children()[i][yChannel])):
			p[index]=datacube.children()[i][zChannel][j]
			XY[index,:]=[datacube[xChannel][i],datacube.children()[i][yChannel][j]]
			index+=1
	if ranges==None:
		x=XY[:,0].tolist()
		y=XY[:,1].tolist()
		for j in range(0,len(XY)):
			try:
				x.remove(0)	
				y.remove(0)
			except:
				pass
	
		ranges=[[min(x),max(x)],[min(y),max(y)]]
	print ranges
	if numbersOfPoints==None:
		numbersOfPoints=[len(datacube['i'])*2,len(datacube.children()[0])*2]
	xgrid,ygrid=mgrid[ranges[0][0]:ranges[0][1]:numbersOfPoints[0]*1j,ranges[1][0]:ranges[1][1]:numbersOfPoints[1]*1j]
	gridData=scipy.interpolate.griddata(XY,p,(xgrid,ygrid),method='nearest',fill_value=0.)
	ratio=abs((ranges[0][0]-ranges[0][1])/(ranges[1][0]-ranges[1][1]))
	imshow(gridData.T,aspect=ratio, extent=(ranges[0][0],ranges[0][1],ranges[1][0],ranges[1][1]), origin='lower')
	colorbar()
	return XY
##
	print (ranges[0][0],ranges[0][1],ranges[1][0],ranges[1][1])
	
	##
	print mgrid[ranges[0][0]:ranges[0][1]:numbersOfPoints[0]*1j,ranges[1][0]:ranges[1][1]:numbersOfPoints[1]*1j]
	##
	
	i=0
	chi=zeros((numbersOfPoints))
	for x in linspace(ranges[0][0],ranges[0][1],numbersOfPoints[0]):
		j=0
		for y in linspace(ranges[1][0],ranges[1][1],numbersOfPoints[1]):
			chi[i,j]=f(x,y)
			j+=1
		i+=1
	figure('test')
	cla()
	imshow(chi,aspect=0.3,extent = (ranges[0][0],ranges[0][1],ranges[1][0],ranges[1][1]))
	colorbar()
	draw()
	show()
##



	p = zeros((len(data.children()[0]),len(data['i'])))
	
		child=data.children()[i]
		p[:,i] = child['p']
	
	v1=data['v'][0]
	v2=data['v'][i]
	
	clf()
	cla()
	
	figure("f")
	
	title("p3")
	imshow(p,aspect = 'auto',extent = (v1,v2,child["f"][0],child["f"][-1]),interpolation = 'nearest')
	xlabel("Flux line 1 voltage [V]")
	ylabel("frequency [GHz]")
	figtext(0.05,0.01,data.filename())
	colorbar()
	draw()
	show()
	time.sleep(2)
##	