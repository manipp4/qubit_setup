##
from config.instrumentsDebug import *
##
oscilloscope=instrumentManager.getInstrument('oscilloscope')
print oscilloscope
oscilloscope.initialize()
print dir(oscilloscope)
print oscilloscope.parameters()

## testing communication with the scope
print oscilloscope.ask("*idn?")
## testing getParameters method
print oscilloscope.getParameters(trace="C1",parameter="MEAN")
## testing getCursorValue method
print oscilloscope.getCursorValue(trace="C1",mode="ALL")
## testing clearSweeps method
print oscilloscope.clearSweeps()
## testing getWaveformSetup method
print oscilloscope.getWaveformSetup()
## testing getWaveformSetup method
print oscilloscope.setWaveformSetup(sparsing=0,numberOfPoints=0,firstPoint=1,numberOfSegments=0)
## testing getTemplate method
print oscilloscope.getTemplate()
## testing inspect method
print oscilloscope.inspect(trace="C1",string1="WAVEDESC")
## testing getWaveforms method
#	DESC, TEXT, TIME, DAT1, DAT2, ALL
#print oscilloscope.getWaveforms(trace="C1",block="DESC")
#print oscilloscope.getWaveforms(trace="C1",block="TEXT")
#print oscilloscope.getWaveforms(trace="C1",block="TIME")
print oscilloscope.getWaveforms(trace="C1",block="DAT1")
#print oscilloscope.getWaveforms(trace="C1",block="DAT2")
##
desc=oscilloscope.ask("C1:WaveForm? DESC")
print len (desc)
pos=desc.index(chr(35))+1 # detect position after fist sharp character
sizeOfSizeOfDesc=int(desc[pos]) # read the number of chars encoding the subsequent wavedesc length
pos=pos+1
sizeOfDesc=int(desc[pos:pos+sizeOfSizeOfDesc]) #size of the wavedesc
pos=pos+sizeOfSizeOfDesc
print desc[pos-1]
desc=desc[pos:] # keep only the wavedesc in desc
print len (desc)
##
header=desc[0:8]
templateName=desc[8:16]
commType=desc[16]
lengthOfWaveDescBlock=desc[18:20]
lengthOfUserTextBlock=desc[20:22]
lengthOfRes1Block=desc[22:24]
lengthOfTrigTimeArrayBlock=desc[24:26]
lengthOfRisTimeArrayBlock=desc[26:28]
lengthOfResArray1Block=desc[28:30]
lengthOfWaveArray1Block=desc[30:32]
lengthOfWaveArray2Block=desc[32:34]
print header, templateName
print commType
print lengthOfWaveDescBlock,lengthOfUserTextBlock
print lengthOfRes1Block,lengthOfTrigTimeArrayBlock
print lengthOfRisTimeArrayBlock,lengthOfResArray1Block
print lengthOfWaveArray1Block,lengthOfWaveArray2Block
##
print ord(commType)

##
print int(lengthOfWaveDescBlock)
##
print desc.index(chr(9839))
##
oscilloscope.read()
