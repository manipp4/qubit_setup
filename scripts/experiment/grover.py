import sys
reload(sys.modules["qulib"])
from qulib import *
from scripts.state_tomography.plot_density_matrix import *

swap = matrix([[1,0,0,0],[0,0,-1j,0],[0,-1j,0,0],[0,0,0,1]])

state = tensor(gs,gs)

rho = adjoint(state)*state

state = transpose(state)

rotation = tensor(roty(math.pi/2.),roty(math.pi/2.))

state = rotation*state

rho = rotation*rho*adjoint(rotation)

rho = swap*rho*adjoint(swap)

angles = [math.pi/2.,math.pi/2.]

rotation = tensor(rotz(angles[0]),rotz(angles[1]))

state = rotation*state

state = swap*state

print state

rho = rotation*rho*adjoint(rotation)

rho = swap*rho*adjoint(swap)

rotation = tensor(rotx(math.pi/2.),rotx(math.pi/2.))
rho = rotation*rho*adjoint(rotation)


figure("grover")
cla()
plotDensityMatrix(rho)
show()
