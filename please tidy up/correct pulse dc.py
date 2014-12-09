from pyview.helpers.instrumentsmanager import Manager
from pyview.lib.datacube import Datacube
import numpy as np

sc=Manager().getInstrument('scope')

d=Datacube("Flux line caracterisation at 300K - FLUX4")
d.toDataManager()
d.createColumn('trig',sc.getWFFromInspect("C2"))
d.createColumn('FLUX4',sc.getWFFromInspect("C1"))
l=len(d['trig'])
[t0,dt]=sc.getHorizInfor("C1")
d.createColumn('t',t0+dt*np.arange(l))
##


d2=Datacube('fft')
d2.toDataManager()
outfftt=np.fft.rfft(d['OUT'])
infft=np.fft.rfft(d['IN'])
d2.createColumn('OUT',outfftt/outfftt[0])
d2.createColumn('IN',inrfft/inrfft[0])


##
d.createColumn("out2",np.fft.ifft(d2['OUT']))



