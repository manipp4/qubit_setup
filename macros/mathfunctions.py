import numpy
import math
import random
import scipy


def linearInterpolate(p1,p2):
  # y=ax+b
  a=(p1[1]-p2[1])/(p1[0]-p2[0])
  b=p1[1]-a*p1[0]
  return lambda x:a*x+b



