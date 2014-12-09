#############################
## for VNA-type of scans ##
############################
import scipy
from numpy import *
from matplotlib.pyplot import *
from pyview.lib.datacube import *
from numpy import *
from matplotlib.pyplot import *
from pyview.lib.datacube import *
import math
## Load the Global variable set in the data manager. ##
## If the data consists of several VNA traces the ploted ##
## dimensions will be (rows=len(data), columns=len(data.child['{name of channel}'])
data = gv.data
##
print data['Current'][0]
p=zeros((len(data),len(data.children()[0])))
I=zeros(len(data))
for i in range(len(data)):
	child=data.children()[i]
	p[i]=child['mag']
	
clf()
cla()
imshow(p,aspect = 'auto',extent = (child['freq'][0],child['freq'][-1],data['Current'][-1]*1e3,data['Current'][0]*1e3),interpolation = 'nearest',cmap='jet')
xlabel("Freq")
ylabel("Current")
colorbar()
draw()
show()

##
###############################
## res vs power scans in dB ###
###############################
print data['power'][0]

##
p=zeros((len(data),len(data.children()[0])))
for i in range(len(data)):
	child=data.children()[i]
	p[i]=child['mag']
	
figure()
clf()
cla()
imshow(p,aspect = 'auto',extent = (child['freq'][0],child['freq'][-1],data['power'][0],data['power'][-1]),interpolation = 'nearest',cmap='jet',origin=['upper'])
xlabel("Freq")
ylabel("power")
colorbar()
draw()
show()
##
################################
## res vs power scans in dBm ###
################################


p=zeros((len(data),len(data.children()[0])))
for i in range(len(data)):
	child=data.children()[i]
	p[i]=child['mag']+data['power'][i]
	
figure()
clf()
cla()
imshow(p,aspect = 'auto',extent = (child['freq'][0],child['freq'][-1],data['power'][0],data['power'][-1]),interpolation = 'nearest',cmap='jet',origin=['upper'])
xlabel("Freq")
ylabel("power")
colorbar()
draw()
show()




## Older plot function(dont know exacatly how it works)	
#channel="phase"
channel="mag"

atten_down=64
	
figure()
length=-1
reverse=False

for i in range(0,1):
	try:
		data = gv.data
		
		
		print data['Qfreq'][i]
		p = zeros(len(data['Qfreq']))
		
		for i in range(0,len(data['Qfreq'])):
			child=data.children()[i]
			l=len(child[channel])
			p[i] = child[channel]
			
		
		clf()
		cla()
		#f, axarr = plt.subplots(2, sharex=True)
#axarr[0].plot(x, y)
#axarr[0].set_title('Sharing X axis')
#axarr[1].scatter(x, y)
		plot(data['Qfreq'],p)
		xlabel("Qbit frequency[GHz]")
		ylabel("Cavity output [dB or degree]")
		title(channel)
		show()
		#imshow(p,aspect = 'auto',extent = (v1,v2,child["freq"][length],child['frequencyId'][0]),interpolation = 'nearest',cmap='jet')
		#imshow(p,aspect = 'auto',extent = (v1,v2,child["freq"][length],child['freq'][0]),interpolation = 'nearest',cmap='hsv') 
		
	except:
		#print "error"
		raise
	finally:
		time.sleep(1)
 		#savefig("%s_mag.png" %data.name())
###################		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
###################		
		
		
##
#data.goTo(57)
##
#data.set(i=59,p=4)
#data.commit()

##
#data.removeRow(59)
##
#print len(data['p'])
#print len(data.children())
##
#data=gv.data
#p=data["mag"]
#data.setColumn("mag",p-20)
#savefig("300K calibration.png")