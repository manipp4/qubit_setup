#################################################################################
# IQ Mixer Calibration, in offset and sideband amplitude                        #
#################################################################################


qubit=qubit2

f_min=4.6
f_max=6.5
step=0.2

## Clear calibration and reinit

qubit._optimizer.offsetCalibrationData().clear()
qubit._optimizer.sidebandCalibrationData().clear()
qubit._optimizer.offsetCalibrationData().set(frequency=0)
qubit._optimizer.sidebandCalibrationData().set(f_c=0)
qubit._optimizer.offsetCalibrationData().set(frequency=0)
qubit._optimizer.sidebandCalibrationData().set(f_c=0)
qubit._optimizer.offsetCalibrationData().commit()
qubit._optimizer.sidebandCalibrationData().commit()

## Calibrate the full range

for f in arange(f_min,f_max,step):
	qubit.calibrateIqOffset(frequency=f)
qubit.calibrateSidebandMixing(frequencyRange=arange(f_min,f_max,step))

## Calibrate a single point

f=qubit.driveFrequency()

qubit.calibrateIqOffset(frequency=f)
qubit.calibrateSidebandMixing(frequencyRange=[f])

## Diplay calibration datacube

dataManager.addDatacube(qubit._optimizer.sidebandCalibrationData())
dataManager.addDatacube(qubit._optimizer.offsetCalibrationData())

## get calibration at a given frequency

f=6.4


print "f = %g\n iOffset = %g; qOffset = %g" % (f,qubit._optimizer.iOffset(f),qubit._optimizer.qOffset(f))


min_index = argmin(abs(qubit._optimizer.sidebandCalibrationData().column("f_c")-f))
calibrationData = qubit._optimizer.sidebandCalibrationData().childrenAt(min_index)[0]
mat=array([calibrationData.column("f_sb").tolist(),calibrationData.column("phi").tolist(),calibrationData.column("c").tolist()]).transpose()
print("f_sb, phi, c = \n"+str(mat))