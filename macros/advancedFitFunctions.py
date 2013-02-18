from numpy import *
from matplotlib.pyplot import *
from scipy import *


################################################################################
#                                                                              #
#  This set of functions is able to convert some scatter plot to density plot  #
#  and fiting it with 1 or two gaussians. The 2 gaussian fit perform first a   #
#  1 gaussian fit to start with correct fitting parameters                     #
#                                                                              #
################################################################################


def fit2D2Gaussian(Chi,XY):
  """
  Two gaussian fit of a 2D plot having the form of a list.
  Use fit2D1Gaussian to start with correct fitting parameters
  Args: Chi: values, XY: coordinates
  Return: fiting parameters in list, function, fitting parameters
  """
  
  
  import numpy.linalg
   
  import scipy
  import scipy.optimize
  
  fitfunc = lambda p, x: p[0]+p[1]*exp(-pow((x[0]-p[2])/p[4],2.0)-pow((x[1]-p[3])/p[5],2.0))+p[6]*exp(-pow((x[0]-p[7])/p[9],2.0)-pow((x[1]-p[8])/p[10],2.0))
  
  
  errfunc = lambda p, x, y,ff: numpy.linalg.norm(ff(p,x)-y)
  
  p,f,o2=fit2D1Gaussian(Chi,XY)
  
  Chi2=Chi-f(p,XY.transpose())
  
  p0=zeros(11)
  
  p0[0]=p[0]
  p0[1]=p[1]
  p0[2]=p[2]
  p0[3]=p[3]
  p0[4]=p[4]
  p0[5]=p[5]
  
  
  p0[6]=max(Chi2)
  l=argmax(Chi2)
  p0[7]=XY[l][0]
  p0[8]=XY[l][1]
  p0[9]=0.2
  p0[10]=0.2
  
  
  	
  XY=transpose(XY)
  
  print errfunc(p0,XY,Chi,fitfunc)
  
  p1s = scipy.optimize.fmin(errfunc, p0,args=(XY,Chi,fitfunc),maxfun=10000,maxiter=10000,ftol=0.0001)
  
  return (p1s.tolist(),fitfunc,p1s)
  


def fit2D1Gaussian(Chi,XY):
  """
  One gaussian fit of a 2D plot having the form of a list.
  Args: Chi: values, XY: coordinates
  Return: fiting parameters in list, function, fitting parameters
  """
  
  
  fitfunc = lambda p, x: p[0]+p[1]*1/(1+pow(((x[0]-p[2])/p[4]),2)++pow(((x[1]-p[3])/p[5]),2))
  
  errfunc = lambda p, x, y,ff: numpy.linalg.norm(ff(p,x)-y)
  
  import numpy.linalg
   
  import scipy
  import scipy.optimize
  
  p0=zeros(6)
  p0[1]=max(Chi)
  l=argmax(Chi)
  p0[2]=XY[l][0]
  p0[3]=XY[l][1]
  p0[4]=0.2
  p0[5]=0.5	
  
  XY=transpose(XY)
  
  print errfunc(p0,XY,Chi,fitfunc)
  
  p1s = scipy.optimize.fmin(errfunc, p0,args=(XY,Chi,fitfunc),maxfun=10000,maxiter=10000,ftol=0.0001)
  
  return (p1s.tolist(),fitfunc,p1s)
  
  
  

def convertToDensity(X,domain=None,N=[50,50]):
  """
  Convert a scatter to density plot. autoscale works nice, but if u want, domain has to take form [[xmin,xmax],[ymin,ymax]].
  For special request N can be changed: N=[Nx,Ny]
  Return 2Ddensity, Chi=flatten(2Ddensity), XY=map and domain
  """
  
  
  density=zeros((N[0],N[1]))
  XY=zeros((N[0]*N[1],2))
  Chi=zeros((N[0]*N[1]))
  xi=0
  
  if domain==None:
  	domain=[[0,0],[0,0]]
  	for ax in [0,1]:
  		xmin=min(X[:,ax])
  		xmax=max(X[:,ax])
  		xmean=(xmin+xmax)/2
  		dx=(xmax-xmin)/2
  		domain[ax]=(xmean-dx*1.5,xmean+dx*1.5)
  
  for x in linspace(domain[0][0],domain[0][1],N[0]):
  	yi=0
  	for y in linspace(domain[1][0],domain[1][1],N[1]):
  		XY[xi*N[1]+yi,:]=[x,y]
  		yi+=1
  	xi+=1
  stepx=((domain[0][1]-domain[0][0])/N[0])
  stepy=((domain[1][1]-domain[1][0])/N[1])
  for x in X:
  
  	xi=floor((x[0]-domain[0][0])/stepx)
  	yi=floor((x[1]-domain[1][0])/stepy)
  	density[xi,yi]+=1
  	Chi[xi*N[1]+yi]+=1
  return density,Chi,XY,domain
