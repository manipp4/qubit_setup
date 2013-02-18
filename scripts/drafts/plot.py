import matplotlib.pyplot as plt
##
fig=plt.figure()
ax=fig.add_subplot(2,1,1)
##
import numpy as np
t = np.arange(0.,1.,0.01)
s=np.sin(2*np.pi*t)
line,=ax.plot(t,s)
##
print ax.lines




##
plt.draw()
plt.show()