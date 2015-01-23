from pyview.helpers.instrumentsmanager import Manager
instrumentManager=Manager()
vna=instrumentManager.getInstrument('vna')
##
import math
def setMyVNAPower(power):              
	offsetVNA=-7
	power=power-offsetVNA
	if -80<=power<=0:
		atten,pow=divmod(power,-10)
		atten*=10
		if atten>60:
			atten=60
			pow=power+60
		print 'atten='+str(atten)+'dB and power='+str(pow)+'dB'
		vna.setAttenuation(atten)
		vna.setPower(pow)
	else:
		print 'target power out of range'
##
setMyVNAPower(-57)
print vna.attenuation()
print vna.power()
##
vna.setCenterFrequency(7.36)
print vna.centerFrequency()
vna.setSpanFrequency(0.400)
print vna.spanFrequency()
vna.setAttenuation(0)
print vna.attenuation()
vna.setNumberOfPoints(401)
vna.setAveraging(True)
vna.setAveraging(False)
vna.setNumberOfAveraging(4000)
print vna.numberOfAveraging()