import os
import os.path
from ctypes import *
p = os.path.join(os.path.dirname(os.path.abspath(__file__)),'t.dll')
print p
windll.LoadLibrary(p)
##
CDLL('t.dll')