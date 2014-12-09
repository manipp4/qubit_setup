 # general import section
import time
from numpy import *
import numpy as np
from scipy import linalg
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import random
from sklearn import mixture,preprocessing,pipeline
# random cloud generation with normal (gaussian) distribution
def cloud(center,sigmas,angleInDeg,nbrPoints,debug=False):
	v0=sigmas[0]**2;v1=sigmas[1]**2;
	covMat=[[v0,0],[0,v1]]
	if debug: print 'covMat=',covMat
	a=3.14157/180*float(angleInDeg)
	c=cos(a);s=sin(a)
	if debug: print 'a=',a,' c=',c,' s=',s
	rot=array([[c,-s],[s,c]])
	if debug: print 'rot=',rot
	covMatRot=(rot.dot(covMat)).dot(rot.T)
	if debug: print 'covMatRot=',covMatRot
	return np.random.multivariate_normal(center,covMatRot,nbrPoints)	

def myPlot(pl,*clouds):
	s=2
	colors=['r','b','g','y','m']
	for i in range(len(clouds)):
		if len(clouds[i])!=0:
			x,y=array(clouds[i]).T
			pl.scatter(x,y,marker='o',s=s,color=colors[i % len(colors)])
	w=1.25*max(map(abs,pl.axis()))
	pl.axis([-w,w,-w,w])
	pl.set_aspect('equal')

def multiGaussianClusters(distribution,n_components=2,scale=False,returnGMM=False,predict=False):
	scaler = preprocessing.StandardScaler()
	distribution2=distribution
	if scale: 
		distribution2=scaler.fit_transform(distribution)
	gmm = mixture.GMM(n_components=n_components, covariance_type='full') 
	gmm.fit(distribution2)
	weights,centers,covars=[gmm.weights_,gmm.means_,gmm.covars_]
	if scale:
		centers=scaler.inverse_transform(centers) 	 
		for i in range(len(covars)):
			covars[i]= np.diag(scaler.std_).dot(covars[i]).dot(np.diag(scaler.std_))
	ind=argsort(weights)[::-1];weights=weights[ind]  # sort by decreasing weights
	[weights,centers,covars]= [elmt[ind] for elmt in [weights,centers,covars]]
	eigen= map(linalg.eigh,covars) # diagonalize all covariance matrices to find the principal axes and variances
	model=()                       #sort principal axes with largest variance first
	for index in range(len(weights))	:
		eigvals,eigvecs=eigen[index]
		ind=argsort(eigvals)[::-1]                   # principal axis with largest sigma first
		[eigvals,eigvecs]=[elmt[ind] for elmt in [eigvals,eigvecs]]
		angle=rad2deg(arctan(eigvecs[0,1]/eigvecs[0,0]))
		model=model+([weights[index],centers[index],angle,sqrt(eigvals)],)
	if returnGMM: model=model+(gmm,)
	if predict:	model=model+(gmm.predict(distribution2),)
	return(model)

def separatrixBimodal( bimodalGaussian):
    '''
    Find the best separatrix orthogonal to the line joining the two centers of a 2D bimodal Gaussian distribution.
    Return the list [sepPoint,beta,array([w1,w2]),array([c1,c2]),array([s1,s2])] with
        - sepPoint the point of the separatrix on the segment joining the centers C1 and C2,
        - beta the angle between x and the separatrix,
        - w1,w2 the weights of the two components,
        - c1,c2 the two centers of the Gaussian
        - s1,s2 the two sigmas along the C1C2
    Note that the first component is on the left of the oriented axe defined by the point and the oriented angle. 
    '''
    cluster1,cluster2=bimodalGaussian[0:2]
    w1,w2=cluster1[0],cluster2[0]
    c1,c2=cluster1[1],cluster2[1]
    x,y=c1c2=c2-c1
    dist=linalg.norm([x,y])
    alpha=rad2deg(arctan2(y,x)) # angle between the segment joining the centers and X
    sigmasAlongC1C2=[]
    for cluster in [cluster1,cluster2]:
        c,a,s=cluster[1:4]
        tangent=tan(deg2rad(a-alpha))
        sAlongC1C2=sqrt((1+tangent**2)/(1/s[0]**2+(tangent/s[1])**2))   
        sigmasAlongC1C2.append(sAlongC1C2)
    s1,s2=sigmasAlongC1C2
    sigmaSum=sum(sigmasAlongC1C2)
    if  sigmaSum>dist: print 'Alert: separation between clouds 1 and 2 smaller than sigma1 + sigma2'
    sepPoint= s1/(s1+s2)*c1c2+c1
    beta=alpha+90
    return [sepPoint,beta,array([w1,w2]),array([c1,c2]),array([s1,s2])]
    
## Test code
random.seed(time.time())
center1=[-0.165,-0.04];sigmas1=[1e-2,1e-2];angle1=15
center2=[-0.15,-0.08];sigmas2=[1e-2,1e-2];angle2=90
nTotal=10000; fraction1=0.8

n1=int(nTotal*fraction1) 
cloud1=cloud(center1,sigmas1,angle1,n1)
cloud2=cloud(center2,sigmas2,angle2,nTotal-n1)

fig1 = plt.figure()
pl1=fig1.add_subplot(121)
pl1.set_xlabel('x');pl1.set_xlabel('y')
myPlot(pl1,cloud1,cloud2)

distribution= concatenate((cloud1,cloud2))

cluster1,cluster2,gmm,inCloud1=multiGaussianClusters(distribution,scale=True,returnGMM=True,predict=True)
clusters=[cluster1,cluster2]

sepPoint,angleSep=separatrixBimodal(clusters)[:2]
cloud1f=[]
cloud2f=[]
for i in range(len(distribution)):
	if inCloud1[i]: 
		cloudi=cloud1f
	else:
		cloudi=cloud2f
	cloudi.append(distribution[i])	
pl2=fig1.add_subplot(122)
pl2.set_xlabel('x');pl2.set_xlabel('y')
myPlot(pl2,cloud1f,cloud2f)

sigmaList=[]
mult=2
for cluster in clusters:
	weight,center,angle,sigmas=cluster
	sigmaList.extend(sigmas.tolist())
	pl2.plot([center[0]],[center[1]],ls='-',marker='+',markersize=15,color='g')
	ell = Ellipse(xy=center,width=mult*2*sigmas[0],height=mult*2*sigmas[1],angle=angle)
	ell.set_facecolor('none')
	ell.set_edgecolor('g')
	pl2.add_artist(ell)
x,y=sepPoint
pl2.plot(x,y,ls='-',marker='+',markersize=15,color='g')
maxSigma=max(sigmaList)
angleSep=deg2rad(angleSep)
vector=4*maxSigma*array([cos(angleSep),sin(angleSep)])
x,y=array([sepPoint-vector,sepPoint+vector]).T
pl2.plot(x,y,ls='-',markersize=15,color='g')

plt.show()

#
def separatrixMulti(ListOfSeparatrices,wMin=0,wMax=1):
    '''
    Find the best separatrix line given a list of separatrices of the form [separatrix1,separatrix2,...] with
    separatrixi = [sepPoint,beta,weightsW1W2,centersC1C2,sigmasAlongC1C2]
    Return the a and b parameters of the separatrix equation y=a x + b
    Separatrices correponding to weight > wMax or weight < wMin are ignored  
    Alert with a message if the separatrix 
        - approaches one of the Gaussian peak at less than a sigma
        - or is on the wrong side of the gaussian peak
    '''
    selection=[elmt for elmt in ListOfSeparatrices if (elmt[2][0] > wMin and elmt[2][1] < wMax)]
    weights=[elmt[2] for elmt in selection]
    points=[elmt[0] for elmt in selection]
    status='ok'
    if len(points)==0:													# no separatrices selected => error
    	status='Error:Cannot proceed with an empty ListOfSeparatrices.'
    	print status
    	return [None,status]
    elif len(points)==1:												# only one separatrice selected => return it
    	sepPoint,angle=ListOfSeparatrices[1][:2]
    	a=tan(deg2rad(angle))
    	b=sepPoint[1]-a*sepPoint[0]
    	return [array([a,b]),status]
    x,y=array(points).T												# several separatrices => fit the best new separatrix
    A = vstack([x, ones(len(x))]).T
    a,b= abarray = linalg.lstsq(A, y)[0]
    for separatrix in ListOfSeparatrices:                           # Check if the new separatrix a x + b is valid 
        sepPoint,beta,weights,[c1,c2],[s1,s2]=separatrix
        c1c2=c2-c1
        xi=dot(array([b-c1[1],c1[0]]),c1c2)/dot(array([-a,1]),c1c2) # intersection of a x +b separatrix with C1C2
        yi=a*xi+b
        ci=array([xi,yi])
        cic1=c1-ci;cic2=c2-ci;
        inside=dot(cic1,cic2)<0
        if inside:
            tooClose=linalg.norm(cic1) < s1 or linalg.norm(cic2) <s2
            if tooClose:
            	status='invalid'
            	print 'Alert: Separatrix for weights=',weights,' approaches one of the peak by less than a sigma.' 
        else:
            status='invalid'
            print 'Alert: Separatrix for weights=',weights,' does not pass between the gaussian peaks'  
            status='invalid' 
    return [abarray,status]
##
# generate two normal disributions and plot them in a square space

#random.seed(0)
center1=[-5,0];sigmas1=[2,1];angle1=15
center2=[8,12];sigmas2=[4,2];angle2=90
nTotal=10000; fraction1=0.5

n1=int(nTotal*fraction1) 
cloud1=cloud(center1,sigmas1,angle1,n1)
cloud2=cloud(center2,sigmas2,angle2,nTotal-n1)

s=2
fig1 = plt.figure()
pl1=fig1.add_subplot(121)
pl1.set_xlabel('x');pl1.set_xlabel('y')
x1,y1=cloud1.T
x2,y2=cloud2.T
pl1.scatter(x1,y1,marker='o',s=s,color='r')
pl1.scatter(x2,y2,marker='o',s=s,color='b')
w=1.25*max(map(abs,pl1.axis()))
pl1.axis([-w,w,-w,w])
pl1.set_aspect('equal')
#plt.show()

distribution= concatenate((cloud1,cloud2))	# numpy concatenate

# analyze the bimodal distribution using the sklearn module
cluster1,cluster2,gmm=multiGaussianClusters(distribution,returnGMM=True) 
clusters=[cluster1,cluster2]
sepPoint,angleSep=separatrixBimodal(clusters)[:2]
inCloud1=gmm.predict(distribution)

cloud1f=[]
cloud2f=[]
for i in range(len(distribution)):
	if inCloud1[i]: 
		cloudi=cloud1f
	else:
		cloudi=cloud2f
	cloudi.append(distribution[i])	
pl2=fig1.add_subplot(122)
pl2.set_xlabel('x');pl2.set_xlabel('y')
x,y=array(cloud1f).T
pl2.scatter(x,y,marker='o',s=s,color='r')
x,y=array(cloud2f).T
pl2.scatter(x,y,marker='o',s=s,color='b')
w=1.25*max(map(abs,pl2.axis()))
pl2.axis([-w,w,-w,w])
pl2.set_aspect('equal')
sigmaList=[]
mult=2
for cluster in clusters:
	weight,center,angle,sigmas=cluster
	sigmaList.extend(sigmas.tolist())
	pl2.plot([center[0]],[center[1]],ls='-',marker='+',markersize=15,color='g')
	ell = Ellipse(xy=center,width=mult*2*sigmas[0],height=mult*2*sigmas[1],angle=angle)
	ell.set_facecolor('none')
	ell.set_edgecolor('g')
	pl2.add_artist(ell)
x,y=sepPoint
pl2.plot(x,y,ls='-',marker='+',markersize=15,color='g')
maxSigma=max(sigmaList)
angleSep=deg2rad(angleSep)
vector=4*maxSigma*array([cos(angleSep),sin(angleSep)])
x,y=array([sepPoint-vector,sepPoint+vector]).T
pl2.plot(x,y,ls='-',markersize=15,color='g')
plt.show() 
##