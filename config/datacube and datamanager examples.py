from pyview.lib.datacube import * #import the datacube class from proper location
##
# Create a datacube and specify its name:
myCube1=Datacube('myCube1')

# Create the column and fill the data row by row with the method
# set(rowIndex=None,notify=False,commit=False,columnOrder=None,extendLength=False,**keys)
myCube1.set(a=1,b=2)
# to force the order of column creation use the optional keyword columnOrder
myCube1.set(a=1,b=2,columnOrder=['b','a'])
# a row has to be validated with the method commit() before editing (i.e. filling) the next row
myCube1.commit()
# alternatively fill and validate a row in a single call
myCube1.set(a=1,b=2,commit=True)

# Columns can also be created and filled column by column rather than row by row with the method
# createCol(name=None,columnIndex=None,offsetRow=0,values=None,notify=True,**kwargs)
# Note that createColumn(name,values,offset = 0) is obsolete and replaced by createCol
myCube1.createCol(name='c',values=[0,1,2,3,4,5,6,7,8,9,10])

# create and add a child to a datacube
myChild1=Datacube('myChild1')
myCube1.addChild(myChild1)

# add a datacube to the datamanager if loaded
myCube1.toDataManager()

# predefine default 'x', 'y' and 'z' variable names for future plots with the method
# defineDefaultPlot(listOfVariableNames,replaceAll=False)
myCube1.addDefaultPlot(['a','c'])

# Request a plot in the datamanager using the method
# plotInDataManager(*args,**kwargs)
myCube1.plotInDataManager()
# names of variables and other options can be specified
myCube1.plotInDataManager(names=['a','c'],clear=True,style='line+symbol')
##
d=dict()
d['firstThing']=3
d['secondThing']=4
logger=dict()
logger.update(d)
##
c=dict()
c['firstThing']=5
c['secondThing']=6
logger.update(c)
##
myCube1.setParameters(logger)


