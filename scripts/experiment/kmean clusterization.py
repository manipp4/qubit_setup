## imports
import numpy as np
from scipy.cluster import vq
from matplotlib import pyplot as plt

## parametrize a two cloud distribution
n1,center1,sigma1=[4000,[0,0],[4,1]]
n2,center2,sigma2=[1000,[10,8],[1,1]]

# generate two cloud distribution
x1= sigma1[0]*random.randn(n1)+center1[0]
y1= sigma1[1]*random.randn(n1)+center1[1] 
distrib1=[[x1[i],y1[i]] for i in range(len(x1))]

x2= sigma2[0]*random.randn(n2)+center2[0]
y2= sigma2[1]*random.randn(n2)+center2[1]
distrib2=[[x2[i],y2[i]] for i in range(len(x2))]

distrib=np.vstack((distrib1,distrib2))

plt.clf()
plt.scatter(distrib[:,0],distrib[:,1]),plt.xlabel('x'),plt.ylabel('y')
plt.show()

# analyze two cloud distribution
centroids,dist= vq.kmeans(distrib,2)
code,distance = vq.vq(distrib,centroids)
distrib1=distrib[code==0]
distrib2=distrib[code==1]

plt.clf()
plt.scatter(distrib1[:,0],distrib1[:,1]),plt.xlabel('x'),plt.ylabel('y')
plt.scatter(distrib2[:,0],distrib2[:,1],c = 'r')
plt.scatter(centroids[:,0],centroids[:,1],s = 80,c = 'y', marker = 's')
plt.show()

print centroids
##