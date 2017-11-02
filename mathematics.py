import math
from noise import pnoise2,snoise2

def perlin(x,y,scale):
    return snoise2(x*scale,y*scale)