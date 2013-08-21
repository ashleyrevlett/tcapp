import math
import random
from config import *


""" 
Helper functions 
"""

RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
DARKBLUE = (0,0,128)
WHITE = (255,255,255)
BLACK = (0,0,0)
GRAY = (100,100,100)
PINK = (255,200,200)


def random_color():
	r = random.randrange(0, 255, 1)
	g = random.randrange(0, 255, 1)
	b = random.randint(0, 255)
	return (r,g,b)

def random_point():
	x = random.randint(0, SCREEN_WIDTH)
	y = random.randint(0, SCREEN_WIDTH)
	return (x,y)

def distance(p1, p2):
	return math.sqrt( math.pow(p2[0] - p1[0], 2) + math.pow(p2[1] - p1[1], 2) )

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)
