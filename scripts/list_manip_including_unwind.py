import numpy as np

def rotateLeft(li,shift=1):
	"""Rotate a list, tuple or 1st dimension of an array by shift positions to the left. Format is preserved."""
	shift=shift%len(li)
	result=np.concatenate((np.array(li)[shift:],np.array(li)[:shift]))
	if isinstance(li, list):		result=list(result)
	elif isinstance(li, tuple):	result=tuple(result) 
	return result
	
def rotateRight(li,shift=1):
	"""Rotate a list, tuple or 1D array by shift positions to the right. Format is preserved."""
	rotateLeft(li,shift=-shift)
  
def substract(li1,li2):
	"""Subtraction li1-li2 between two lists, tuples or 1D arrays. Format is preserved."""
	result=np.array(li1)-np.array(li2)
	if isinstance(li1, list):		result=list(result)
	elif isinstance(li1, tuple):	result=tuple(result) 
	return result
	
def derivList(li):
	"""Discrete derivative of a list, tuple or 1D array.
	Format is preserved, but with an output length 1 unit below the input length."""
	return substract(rotateLeft(li),li)[:-1]

def listIntegrate(li):
	"""Discrete integration a list, tuple or 1D array. Format is preserved."""
	for i in range(len(li))[1:]:
		li[i]+=li[i-1]
	return li
	
def unwind(li,period=2*np.pi):
	"""Unwind a list, tuple or 1D array initially defined on a circle with period period. Format is preserved."""
	def jump(x):
		dif=[abs(x-period),abs(x),abs(x+period)]
		return dif.index(min(dif))-1
	jumps=listIntegrate(map(jump,derivList(li)))
	jumps.insert(0,0.)
	result=np.array(jumps)*period+np.array(li)
	if isinstance(li, list):		result=list(result)
	elif isinstance(li, tuple):	result=tuple(result)
	return result 
	
##
phase=gv.vna1['phase']
phase2=unwind(phase,period=360.)
gv.vna1.createCol(name='unwoundPhase',values=phase2)


