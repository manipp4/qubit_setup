from config.startup import *

figure("flux")
clf()
subplot(311)
signal = zeros(2000)
ts = linspace(0,len(signal),len(signal))
signal[1000:] = 1.0

from scipy.interpolate import interp1d

ts_measured = linspace(gv.data["t"][0],gv.data["t"][-1],gv.data["t"][-1]-gv.data["t"][0])

dataInterpolation = interp1d(gv.data["t"],gv.data["flux"])
signalInterpolation = interp1d(ts,signal)

ts_diff = ts_measured[1:]

measuredData = -dataInterpolation(ts_measured)
measuredData -= measuredData[0]
measuredData/= max(measuredData)-min(measuredData)
signalData = signalInterpolation(ts_measured)

measuredDiffs = measuredData[1:]-measuredData[:-1]
signalDiffs = signalData[1:]-signalData[:-1]

from instruments.qubit import gaussianFilter

response = gaussianFilter(linspace(0,1.0,len(numpy.fft.rfft(signalData))),cutoff = 0.4)
responseDiffs = gaussianFilter(linspace(0,1.0,len(numpy.fft.rfft(signalDiffs))),cutoff = 0.4)

signalfft = numpy.fft.rfft(signalData)

dsignalfft = numpy.fft.rfft(signalDiffs)
dmeasuredfft = numpy.fft.rfft(measuredDiffs)

freqs = linspace(0,0.5,len(dmeasuredfft))
responseFunction = interp1d(freqs,dmeasuredfft/dmeasuredfft[0]/dsignalfft*exp(1j*6*2.0*math.pi*freqs))

plot(ts_measured,measuredData)
plot(ts_measured,signalData)
plot(ts_measured,numpy.fft.irfft(signalfft/responseFunction(linspace(0,0.5,len(signalfft)))*gaussianFilter(linspace(0,0.5,len(signalfft)),cutoff = 0.12),len(ts_measured)))

ylabel("signal")

subplot(312)

plot(ts_diff,measuredDiffs)
plot(ts_diff,signalDiffs)

ylabel("signal derivative")

subplot(313)

plot(freqs,abs(responseFunction(freqs)))
plot(freqs,abs(dsignalfft))

ylabel("FFT")
xlabel("frequency [GHz]")

##Write the response function to a file...

response = Datacube("response function",dtype = complex128)
response.setColumn("frequency",freqs)
response.setColumn("response",responseFunction(freqs))
response.savetxt()

##

register["calibration.fluxline.qubit1"] = response.filename()
register["calibration.fluxline.qubit2"] = response.filename()

qubit1._fluxlineResponse = response
qubit2._fluxlineResponse = response
##

baseWaveform = qubit1.loadFluxlineBaseWaveform(compensateResponse = True,compensationFactor = 1)

waveform = zeros(len(baseWaveform))+baseWaveform
waveform[200:600] += 0.1

compensatedWaveform = qubit1.loadFluxlineWaveform(waveform)

figure("fluxline")
cla()
plot(waveform)
plot(compensatedWaveform)