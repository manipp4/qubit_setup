from pyview.helpers.instrumentsmanager import Manager



pm=Manager().getInstrument('pulsersManager')
##
print pm._generators[0][0]._MWSource
##
for g in pm._generators:
	g[0].clearPulse()
	g[0].addPulse(generatorFunction='square',start=10000,stop=19000,applyCorrections=True,name="P1")
	g[0].preparePulseSequence()
	g[0].sendPulseSequence()
##

pm._generators[0][0].clearPulse()
pm._generators[0][0].addPulse(generatorFunction='square',start=1000,stop=2000,pulseOn=False,applyCorrections=True,name="P1")
pm._generators[0][0].addPulse(generatorFunction='square',start=0000,stop=2600,applyCorrections=True,name="P2")
pm._generators[0][0].addPulse(generatorFunction='square',start=5000,stop=6000,pulseOn=False,applyCorrections=True,name="P3")
pm._generators[0][0].addPulse(generatorFunction='square',start=7000,stop=8000,applyCorrections=True,name="P4")
pm._generators[0][0].preparePulseSequence()
pm._generators[0][0].sendPulseSequence()
##
pm._generators[1][0].clearPulse()
pm._generators[1][0].addPulse(generatorFunction='square',start=1000,stop=2000,pulseOn=False,applyCorrections=True,name="P1")
pm._generators[1][0].addPulse(generatorFunction='square',start=0000,stop=2600,applyCorrections=True,name="P2")
pm._generators[1][0].addPulse(generatorFunction='square',start=5000,stop=6000,pulseOn=False,applyCorrections=True,name="P3")
pm._generators[1][0].addPulse(generatorFunction='square',start=7000,stop=8000,applyCorrections=True,name="P4")
pm._generators[1][0].preparePulseSequence()
pm._generators[1][0].sendPulseSequence()
##
pm._generators[1][0].clearPulse()
pm._generators[1][0].addPulse(generatorFunction='square',start=8000,stop=9000,pulseOn=False,applyCorrections=True,name="P1")
pm._generators[1][0].addPulse(generatorFunction='square',start=1000,stop=2600,applyCorrections=True,name="P2")
pm._generators[1][0].addPulse(generatorFunction='square',start=4000,stop=5200,pulseOn=False,applyCorrections=True,name="P3")
pm._generators[1][0].addPulse(generatorFunction='square',start=6000,stop=7750,applyCorrections=True,name="P4")
pm._generators[1][0].preparePulseSequence()
pm._generators[1][0].sendPulseSequence()
pm._generators[2][0].clearPulse()
pm._generators[2][0].addPulse(generatorFunction='square',start=18000,stop=19000,pulseOn=False,applyCorrections=True,name="P1")
pm._generators[2][0].addPulse(generatorFunction='square',start=11000,stop=12600,applyCorrections=True,name="P2")
pm._generators[2][0].addPulse(generatorFunction='square',start=14000,stop=15200,pulseOn=False,applyCorrections=True,name="P3")
pm._generators[2][0].addPulse(generatorFunction='square',start=17000,stop=17750,applyCorrections=True,name="P4")
pm._generators[2][0].preparePulseSequence()
pm._generators[2][0].sendPulseSequence()
###
import numpy
import math
def cor(l):
	def cutoff(f):
		f0=500e6
		return 1/(1+(1j*f/f0)**9)

	def filter(f):
		f0=400e6
		f1=200e6
		return 1/(1+1j*f/f0-(f/f1)**2)

	def phase(f):
		t0=25e-9
		return numpy.exp(1j*2*math.pi*f*t0)

	fft=numpy.fft.fft(l)

	for i in range(len(l)):
		fft[i]*=1/filter(i*50e3)*cutoff(i*50e3)#*phase(i*50e3)#1/filter(i*50e3)*cutoff(i*50e3)*phase(i*50e3)
	tr=numpy.fft.ifft(fft)
	tr=[min(x,1) for x in tr]
	return tr
##
pm._generators[0][0].pulseCorrectionFunction=None
##
print numpy.fft.rfft
##
pm._generators[0][0].pulseCorrectionFunction=lambda x:x





##
pm._generators[0][0].sendPulseSequence()
##


pm._generators[1][0].addPulse(generatorFunction='square',start=7000,stop=8000,frequency=4)
pm._generators[1][0].addPulse(generatorFunction='square',start=4000,stop=8000,frequency=4,pulseOn=False)
pm._generators[1][0].addPulse(generatorFunction='square',start=5000,stop=5500,frequency=4)
pm._generators[1][0].addPulse(generatorFunction='square',start=8000,stop=9000,frequency=4,pulseOn=False)