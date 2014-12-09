###############################
## for DataCube-type of scans ##
###############################
import scipy
from numpy import *
from matplotlib.pyplot import *
from pyview.lib.datacube import *
from numpy import *
from pyview.lib.datacube import *
import math
from scipy.optimize import curve_fit
##
x=[]
y=[]
## Load the Global variable set in the data manager. ##
data = gv.data
##
# Load x axis
x=concatenate((x,data['coilCurrent']))
# Load y axis
y=concatenate((y,data['frequency01']))
##
ind=range(len(x))
indarray=zip(ind,x,y)
for i in range(len(x)):	
	print indarray[i]
##
toRemove=concatenate(([30,32,34,36,42,70],range(86,92),range(101,117)))

clf()
cla()
xtoplot=delete(x,toRemove)
ytoplot=delete(y,toRemove)
pl=plot(xtoplot,ytoplot,'ro')
xtoFit=xtoplot
ytoFit=ytoplot
popt, pcov = curve_fit(fitFunc,xtoFit,ytoFit,[7.6,-0.006,-0.008])
xplFit=linspace(min(x),-0.004,3000)
fit=fitFunc(xplFit,popt[0],popt[1],popt[2])
plfit=plot(xplFit,fit)
xlabel("Coil Current")
ylabel("Frequency")
show()
##
def fitFunc(x, a, b, c):
    return a*sqrt(abs(cos(pi*(b+x)/c)))
  
##    
def fitfunc(x,y):
	# initial guessing
	pinit=[-0.0089,-0.008,7.6]
	print "initial guess :"
	print pinit 

	fitfunc = lambda p, x: p[2]*abs(cos(pi*(p[0]+x)/p[1]))
	errfunc = lambda p, x, y,ff: pow(linalg.norm(ff(p,x)-y,2),2.0)
	
	p1s = scipy.optimize.fmin(errfunc, pinit,args=(x,y,fitfunc))
	print "fit result :"
	print p1s
	yfit=[fitfunc(p1s,xv) for xv in x]

	return yfit


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