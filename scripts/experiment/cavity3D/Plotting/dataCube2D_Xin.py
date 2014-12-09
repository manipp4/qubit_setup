import scipy
from numpy import *
from matplotlib.pyplot import *
from pyview.lib.datacube import *

data = gv.data

##
#figure('2Dpf4')
cla()
clf()
draw()

##
from numpy import *
from matplotlib.pyplot import *
from pyview.lib.datacube import *


channel="phase"
#channel="gain"
    
figure()
length=-1
reverse=False
for i in range(0,1):
    try:
        data = gv.data
        if length>0:p = zeros((length,len(data['i'])))
        if length<0:p = zeros((len(data.children()[0]),len(data['voltage'])))
            
        for i in range(0,len(data['voltage'])):
            child=data.children()[i]
            if length<0:l=len(child[channel])
            if reverse:
                if length>0:p[::-1,i] = child[channel][:length]
                if length<0:p[::-1,i] = child[channel]
            else:
                if length>0:p[:,i] = child[channel][:length]
                if length<0:p[:len(child[channel]),i] = child[channel]
                
        
        v1=data['voltage'][0]
        v2=data['voltage'][i]
        if reverse: [v1,v2]=[v2,v1]
        clf()
        cla()
        imshow(p,aspect = 'auto',extent = (v1,v2,child["freq"][0],child['freq'][length]),interpolation = 'nearest',cmap='RdBu_r',origin='low')
        #imshow(p,aspect = 'auto',extent = (v1,v2,child["freq"][length],child['freq'][0]),interpolation = 'nearest',cmap='hsv') 
        xlabel("voltage (V)")
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
         #savefig("vnaX res1")