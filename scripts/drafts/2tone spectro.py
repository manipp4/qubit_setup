##curve
from config.instruments import *
from matplotlib.pyplot import *
import numpy
import scipy
from pyview.helpers.datamanager import DataManager
dataManager = DataManager()
instrumentManager=Manager()
register=instrumentManager.getInstrument('register')
jba=instrumentManager.getInstrument('jba_qb1')
awg=instrumentManager.getInstrument('awg')
pg=instrumentManager.getInstrument('pg_qb_simple')
acqiris=instrumentManager.getInstrument('acqiris')
coil=instrumentManager.getInstrument('coil')
print coil
print pg
print jba_att
print jba
print acqiris
##
coil.slewRate=0.1
##

data=Datacube('spectro jba')
dataManager.addDatacube(data)
#for j in range(0,100):
#jba_att.setVoltage(4)
try:
	frequencies=arange(6.86,6.9,0.0005)
	for f in frequencies:
		print "f=%f"%f
		time.sleep(0.1)
		jba._pulseGenerator._MWSource.setFrequency(f)
		acqiris.AcquireV1()
		time.sleep(0.3)
		try:
			co=acqiris.DMATransferV1(transferAverage=True)[1]
			I=mean(co[0])
			Q=mean(co[1])
			m=sqrt(I**2+Q**2)
			data.set(f=f,mag=m,I=I,Q=Q)
			data.commit()
		except:
			print 'acquisition error'
finally:
	data.savetxt()
	
##
coil.setVoltage(0.1,slewRate=0.1)
##
data=Datacube()
dataManager.addDatacube(data)
for j in range(0,10000):
	print j
	acqiris.AcquireV1()
	time.sleep(0.2)
	cos=acqiris.DMATransferV1(transferAverage=True)[1]
	m1= mean(cos[0])
	m2=mean(cos[1])
	data.set(m1=m1,m2=m2)
	data.commit()
##
print cos
#acqiris.DMATransferV1()
##
print mean(co[:,0])**2

##
print pg._MWSource
##


frequencies_jba=[6.771,6.852,6.896,6.946]
for f_jba in frequencies_jba:
##
jba_att.setVoltage(3)
##
coil.setVoltage(0,slewRate=0.1)
f_jba=6.854
powers=arange(-2,15,3)
i=0
data=Datacube('qubit spectro f=%f'%f_jba)
dataManager.addDatacube(data)
for p in powers:
	jba._pulseGenerator._MWSource.setFrequency(f_jba)
	pg._MWSource.turnOn()
	pg._MWSource.setPower(p)
	child=Datacube('p=%f'%p)
	data.addChild(child)

	try:
		frequencies=arange(7,12,0.005)
		for f in frequencies:
			print p, f
			pg._MWSource.setFrequency(f)
			time.sleep(0.1)
			acqiris.AcquireV1()
			time.sleep(0.2)
			cos=acqiris.DMATransferV1(transferAverage=True)[1]
			m1=mean(cos[0])
			m2=mean(cos[1])
			m=sqrt(m1**2+m2**2)/10
			child.set(f=f,mag=m)
			child.commit()
	except:
		print "ERROR"
	finally:
		data.set(i=i, p=p)
		data.commit()
		i+=1
		data.savetxt()
##
f_jba0=6.854
power=5	
i=0
data=Datacube('qubit spectro f=%f'%f_jba0)
dataManager.addDatacube(data)
jba._pulseGenerator._MWSource.setFrequency(f_jba0)
pg._MWSource.turnOn()
pg._MWSource.setPower(power)
voltages=arange(-0.,-0.42,-0.05)
f_jba=f_jba0
for v in voltages:
	coil.setVoltage(v,slewRate=0.1)
	child=Datacube('v=%f'%v)
	data.addChild(child)
	try:
		print 'calibration in progress'
		d=Datacube('calibration')
		child.addChild(d)
		for f in arange(f_jba-0.005,f_jba+0.005,0.0002):
			jba._pulseGenerator._MWSource.setFrequency(f)
			time.sleep(0.1)
			acqiris.AcquireV1()
			time.sleep(0.2)
			cos=acqiris.DMATransferV1(transferAverage=True)[1]
			m1=mean(cos[0])
			m2=mean(cos[1])
			m=sqrt(m1**2+m2**2)/10
			d.set(f=f,mag=m)
			d.commit()
		d.sortBy('mag')
		f_jba=d['f'][0]
		jba._pulseGenerator._MWSource.setFrequency(f_jba)			
		print f_jba0,f_jba
		d.setName('calibration f=%f'%f_jba)
	except:
		print "error"
		jba._pulseGenerator._MWSource.setFrequency(f_jba0)
		raise
	try:
		frequencies=arange(7,11,0.005)
		for f in frequencies:
			print v, f
			pg._MWSource.setFrequency(f)
			time.sleep(0.15)
			acqiris.AcquireV1()
			time.sleep(0.3)
			cos=acqiris.DMATransferV1(transferAverage=True)[1]
			m1=mean(cos[0])
			m2=mean(cos[1])
			m=sqrt(m1**2+m2**2)/10
			child.set(f=f,mag=m)
			child.commit()
	except:
		print "ERROR"
	finally:
		data.savetxt()
		data.set(i=i, v=v)
		i+=1
		data.commit()
		
		
##
coil.setVoltage(0.1,slewRate=0.1)

##
jba.measureSCurve(voltages=arange(2.5,3.5,0.01))