def smartLoop(values=[]):
	i=0
	while True:
		try:
			newValue=(yield values[i])
			if newValue is not None:
				if newValue=="reverse":
					print "reverse"
					for j in range(0,i):
						values.insert(i,values[j])
					print values
				else:
					print "newValues added"
					for value in newValue:
						values.append(value)
			else:
				i+=1
		except:
			print "fin"
			print values
			break	
			
##

##

first=True
generateur = smartLoop(range(0,15))
for nombre in generateur:
	if nombre==11 and first:
		first=False
		generateur.send("reverse")        
        
        
##
print type("reverse")        
if "reverse"==2:
	print 'ok'        
        
        
##
r=[]
r.append(range(0,2))
print r[2]


##
del smartLoop,smartLoopIt
##
class smartLoop(Arrays):
	def __iter__(self):
		return smartLoopIter(self)

##
del smartLoop
class smartLoop():
	
	def __init__(self, values):
		self.values = values
		self.index = 0
		self.iter=+1

	def __iter__(self):
		return self

	def next(self):
		if self.index+self.iter >= len(self.values) or self.index+self.iter < 0  :
			raise StopIteration
		self.index+= self.iter
		return self	.values[self.index]

	def forward(self):
		self.iter=abs(self.iter)
	
	def backward(self):
		self.iter=-abs(self.iter)

	def reverse(self):
		self.iter=-self.iter
	
	def setSpeed(self,speed=1):	
		self.iter=speed
	
	def insertNow(self,values):
		for value in values:
			self.values.insert(self.index+self.iter,value)	
	
	def insertAtTheEnd(self,values):
		for value in values:
			self.values.append(value)	
	
	
	
	def __del__(self):
		#notify something to somewhere
		pass
	
	def getValues(self):
		return self.values

loop=smartLoop(range(0,9))	
for i in loop:
	print i
	if i==5:
		loop.insertNow([541,18])



##

	def __iter__(self):
		
		if self.i<len(self.values):
			raise StopIteration
		else:
			print "returning"
			toReturn=self.values[self.i]
			self.i+=1
			return toReturn
####

del test
class test:
	def __init__(self):
		self.i=0
	
	def __iter__(self):
		return self
			
	def next(self):
		self.i+=1
		if self.i<100:
			return self.i
		else:
			raise StopIteration
			
t=test()
for p in t:
	print p
	
	
	
	
	
	
	
	




