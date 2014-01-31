from numpy import *
from matplotlib.pyplot import *
from pyview.lib.datacube import *

data = gv.data


##
##
length=-1
for j in range(0,1):
	if length>0:p = zeros((length,len(data['i'])))
	if length<0:p = zeros((len(data.children()[0]),len(data['i'])))

	
	
	for i in range(0,len(data['i'])):
		child=data.children()[i]
		if length>0:p[:,i] = child['p'][:length]
		if length<0:p[:,i] = child['p']
	v1=data['v'][0]
	v2=data['v'][i]
	
	clf()
	cla()
	
	figure("f")
		
	title("p3")
	imshow(p,aspect = 'auto',extent = (v1,v2,child["f"][length],child["f"][0]),interpolation = 'nearest')
	xlabel("Flux line 2 voltage [V]")
	ylabel("frequency [GHz]")
	figtext(0.05,0.01,data.filename())
	colorbar()
	draw()
	show()
	time.sleep(1)
##	
#cla()
#clf()
subplot(122)
title("Phase")
imshow(phase,aspect = 'auto',extent = (v1,v2,child["freq"][-1],child["freq"][0]),interpolation = 'nearest')
xlabel("frequency [GHz]")
#ylabel("VNA frequency [GHz]")
figtext(0.05,0.01,data.filename())
colorbar()
draw()
show()


###########
#		show()0
savefig('L:\s\phase %i.pdf' %iter)
##








