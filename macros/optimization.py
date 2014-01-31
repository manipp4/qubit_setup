class Minimizer:
  """
  This class can be used in replaceament of scipy.optimize.fmin. 
  It's a stepest descent algorithm
  Results are not guaranted but behaviour is well controled.
  Perform minimization using Minimizer.minimize
  Get resuls using Minimizer.result
  """

  def __init__(self,function, initParameters, bounds,xtol=1e-7,maxfun=100,maxiter=1):
    """
    Initialize instance of the class. 
    Function is the n-dimension function to minimize, initParameters are initial parameters (n-dimension), boundaries are given by bounds ((n,2)-dimension)
    xtol is the tolerance in x (absolute value (i.e. not relative)). Can be n-dimension or float.
    maxfun is total maximum of function evalutation
    maxiter is the number of turn
    """
    self._function=function
    self._initParameters=initParameters
    self._bounds=bounds
    self._dim=len(initParameters)
    if type(xtol)==type(0.1): xtol=[xtol]*self._dim
    self._xtol=xtol
    self._maxfun=maxfun
    self._maxiter=maxiter
    
    self._initMeasuredPoints()
    self._dim=len(initParameters)
    self._currentPoint=initParameters

    self._functionIteration=0
    print self._bounds

  def minimize(self):
    """
    Perform minimization
    """
    for i in range(0,self._maxiter):
      for d in range(0,self._dim):
        for j in range(0,self._maxfun):
          xl=[self._bounds[d][0],(self._bounds[d][0]+self._bounds[d][1])/2,self._bounds[d][1]]
          yl= [self._getValueAt(self._makePoint(self._currentPoint,d,value)) for value in xl]
          xyl=sorted(zip(xl,yl),key=lambda x:x[1])
          self._bounds[d]=[xyl[k][0] for k in [0,1]]
          if abs(self._bounds[d][0]-self._bounds[d][1])<self._xtol[d]: break
          if self._functionIteration>self._maxfun: break
        self._currentPoint[d]=(self._bounds[d][0]+self._bounds[d][1])/2
      newBounds=[[self._currentPoint[d]-self._xtol[d]*3,self._currentPoint[d]+self._xtol[d]*3] for d in range(0,self._dim)]
    print "function evaluations : ", self._functionIteration

        
  def result(self):
    """
    Return xmin (n-dimension) and function(xmin)
    """
    point=[(self._bounds[d][0]+self._bounds[d][1])/2 for d in range(0,self._dim)]
    return point, self._getValueAt(point)
    
  def _makePoint(self,basePoint,direction, value):
    newPoint=self._currentPoint[:]
    newPoint[direction]=value
    return newPoint 
      
  
  def _initMeasuredPoints(self):
    self._xm=[]
    self._ym=[]
  
  def _hasPointAt(self,x):
    return x in self._xm

  def _setPointAt(self,x,y):
    self._xm.append(x)
    self._ym.append(y)
  
  def _getStoredValueAt(self,x):
    index=self._xm.index(x)
    if self._xm[index]==x:
      return self._ym[index]
    else :return None
  def _getMeasuredValueAt(self,x):
    self._functionIteration+=1
    y=self._function(x)
    self._setPointAt(x,y)
    return y
  
  def _getValueAt(self,x):
    if self._hasPointAt(x):
      return self._getStoredValueAt(x)
    else:
      return self._getMeasuredValueAt(x)

