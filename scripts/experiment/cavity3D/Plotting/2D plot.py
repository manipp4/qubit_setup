import scipy
from numpy import *
from matplotlib.pyplot import *
from pyview.lib.datacube import *

data = gv.noise3
print len(data.children())
child=data.children()[0]
print child
print len(child.children())
child2=child.children()[0]
print child2['bins']
##
data = gv.noise3
# bins vs power plot

#choose frequency and find its position in the list
freq=7.08322
freqs=arange(708082,708482,10)
for ind, f in enumerate(freqs):
	if int(f)==freq*100000:
		i=ind
#get the data for freq		
child1=data.children()[i]
# makes a 2d array of zeroes;(rows,columns),load any child of child to define row length
child2=child1.children()[0]
p = zeros((len(child2['bins']),len(child1.children())))
#For each power (column) fill in the hist data
for i in range(len(child1.children())):
	child2=child1.children()[i]
	p[::-1,i]=child2['hist']
powers=arange(0,2.01,0.2)
clf()
cla()
imshow(p,aspect = 'auto',extent = (powers[-1],powers[0],child2['bins'][0],child2['bins'][-1]),interpolation = 'nearest',cmap='jet')
#imshow(p,aspect = 'auto',extent = (v1,v2,child["freq"][length],child['frequencyId'][0]),interpolation = 'nearest',cmap='jet')
#imshow(p,aspect = 'auto',extent = (v1,v2,child["freq"][length],child['freq'][0]),interpolation = 'nearest',cmap='hsv') 
xlabel("power")
ylabel("bins")
colorbar()
draw()
show()


##

# bins vs frequency plot

#choose power and find its position in the list
power=0.5
powers=reversed(arange(0,201,10))
for ind, p in enumerate(powers):
	if int(p)==power*100:
		print p
		print ind
		idx=ind		
# make a 2d array of zeroes;(rows,columns),load any child of child to define row length
child1=data.children()[0]
child2=child1.children()[0]
p = zeros((len(child2['bins']),len(data.children())))
#For each frequency (column) fill in the hist data
print len(p[0,:])
for i in range(len(data.children())):
	child1=data.children()[i]
	child2=child1.children()[idx]
	#print child2['hist']
	p[::-1,i]=child2['hist']
#freqs=arange(708082,708482,10)
freqs=arange(707882,708882,10)
#clf()
cla()
figure()
imshow(p,aspect = 'auto',extent = (freqs[0],freqs[-1],child2['bins'][0],child2['bins'][-1]),interpolation = 'nearest',cmap='jet')
#imshow(p,aspect = 'auto',extent = (v1,v2,child["freq"][length],child['frequencyId'][0]),interpolation = 'nearest',cmap='jet')
#imshow(p,aspect = 'auto',extent = (v1,v2,child["freq"][length],child['freq'][0]),interpolation = 'nearest',cmap='hsv') 
xlabel("frequency")
ylabel("bins")
figtext(0.05,0.01,'power=%f'%power)
colorbar()
draw()
show()

##
#figure('2Dpf4')
cla()
clf()
draw()
show()
##
from numpy import *
from matplotlib.pyplot import *
from pyview.lib.datacube import *
import math


	

#channel="phase"
channel="hist"

	
figure()
length=-1
reverse=False

for i in range(0,1):
	try:
		data = gv.Noise2
		
		
		print data['freq'][i]
		if length>0:p = zeros((length,len(data[i])))
		# makes a 2d array of zeroes;(rows,columns)
		if length<0:p = zeros((len(data['freq'],len(data.children()[0]))))
		
		#for each freq row it fills in the data from various powers	
		for i in range(0,len(data['freq'])):
			child=data.children()[i]
			if length<0:l=len(child[channel])
			if reverse:
				#if length>0:p[::-1,i] = child[channel][:length]
				if length<0:p[::-1,i] = child[channel]
				if length<0:p[::-1,i] = child[channel]
			else:
				if length>0:p[:,i] = child[channel][:length]
				#if length<0:p[:len(child[channel]),i] = child[channel]
				if length<0:p[:len(child[channel]),i] = child[channel]
				
		
		v1=(data['power'][0]-atten_down)
		v2=(data['power'][i]-atten_down)
		if reverse: [v1,v2]=[v2,v1]
		clf()
		cla()
		imshow(p,aspect = 'auto',extent = (v1,v2,child["freq"][length],child['freq'][0]),interpolation = 'nearest',cmap='jet')
		#imshow(p,aspect = 'auto',extent = (v1,v2,child["freq"][length],child['frequencyId'][0]),interpolation = 'nearest',cmap='jet')
		#imshow(p,aspect = 'auto',extent = (v1,v2,child["freq"][length],child['freq'][0]),interpolation = 'nearest',cmap='hsv') 
		xlabel("Pump power [dB]")
		ylabel("Signal frequency [GHz]")
		colorbar()
		figtext(0.05,0.01,data.filename())
		draw()
		show()
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