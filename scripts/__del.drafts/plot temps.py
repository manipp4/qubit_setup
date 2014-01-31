##curve
from config.instruments import *
from matplotlib.pyplot import *
#from pyview.gui.mpl.backend import figure
import numpy
import scipy
from pyview.helpers.datamanager import DataManager
dataManager = DataManager()
instrumentManager=Manager()
register=instrumentManager.getInstrument('register')
jba=instrumentManager.getInstrument('jba_qb1')
awg=instrumentManager.getInstrument('awg')
pg=instrumentManager.getInstrument('pg_qb_simple')
print pg
print jba_att
print jba
#
jba=instrumentManager.getInstrument('jab_qb1')
print jba
acqiris=instrumentManager.getInstrument('acqiris')
print acqiris
##
acqiris.setNLoops(10)
jba.measureSCurve(voltages=arange(3.2,3.5,0.005))
acqiris.setNLoops(1)
print 'finish'

##
mw_qb=instrumentManager.getInstrument('mwsource_qb')
print mw_qb
f=6.70348
mw_qb.setFrequency(f)
#
fsp=instrumentManager.getInstrument('fsp')
fsp.setFrequency(f)
time.sleep(0.5)
fsp.write("CALC:MARK:Y?")
print fsp.read()
##
from matplotlib.pyplot import *
figure()
cla()
f0=6.91
data=gv.data
vmin=3.2
vmax=3.8
j=0
for i in range(0,len(data.children())):
	try:
		child=data.children()[i]
		f=data['f_added'][j]
		f_max=max(data['f_added'])
		f_min=min(data['f_added'])
		x=(f_max-f)/(f_max-f_min)
		color=((x,0,1-x))
		p=child['p']
		v=child['v']
		j+=1
		p=p[v>vmin]
		v=v[v>vmin]
		p=p[v<vmax]
		v=v[v<vmax]
		if f<f0-0.01 or f>f0+0.03:
			plot(v,p+f*140,color=color)
			annotate(f,(3.7,f*140+0.02))
	except:
		print "error %i %i"%(i,j)
		pass
title("f drive = %f"%f0)
xlabel('voltage')
ylabel('switching probability')
figtext(0.05,0.01,data.filename(),size='xx-small')
draw()
show()	
##
from matplotlib.pyplot import *
import time
for i in range(0,1):
	figure()
	cla()
	data=gv.data
	vmin=2
	vmax=6
	j=0
	for i in range(0,len(data.children())):
		child=data.children()[i]
		f=data['f_added'][i]
		f_max=max(data['f_added'])
		f_min=min(data['f_added'])
		x=(f_max-f)/(f_max-f_min)
		color=((x,0,1-x))
		try:
			p=child['p']
			v=child['v']
			if min(v)>1. and max(v)<5.:
				p=p[v>vmin]
				v=v[v>vmin]
				p=p[v<vmax]
				v=v[v<vmax]
				if v[0]>v[-1]:
					p[:]=p[::-1]
					v[:]=v[::-1]
				if p[0]<0.001:p[:]=1-p[:]
				plot(v,p,color=color)
		except:
			print "error"

	xlabel('voltage')
	ylabel('switching probability')
	figtext(0.05,0.01,data.filename())
	draw()
	show()	
	time.sleep(1.)
##
	for i in range(0,len(data.children())):
		try:
			p=data.children()[i]['p']
			print p[10]
		except:
			print i
			data.removeChild(data.children()[i])
	time.s
		
##
data.setName("jbas jba=6.91")
data.savetxt()