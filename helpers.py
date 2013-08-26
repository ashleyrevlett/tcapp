import math
import random
from config import *


def distance(p1, p2):
	return math.sqrt( math.pow(p2[0] - p1[0], 2) + math.pow(p2[1] - p1[1], 2) )

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

def mode(list_items):
	return max(set(list_items), key=list_items.count)