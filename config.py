# config.py

#testing config
TESTING = False

# app constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 400
TILE_SIZE = 16
MAX_HEIGHT = 255
MIN_HEIGHT = 0
COLORIZED = True
NOISE_SCALE = 0.09
WATER_TABLE_LEVEL = 0.55 # float 0-1; used as %
BEACH_END = WATER_TABLE_LEVEL + 0.05
TREE_LINE = 0.88

#colors
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
DARKBLUE = (0,0,128)
WHITE = (255,255,255)
BLACK = (0,0,0)
GRAY = (100,100,100)
PINK = (255,200,200)	

if COLORIZED == True:
	CLR_SEA_3 = (29,33,49)
	CLR_SEA_2 = (34,51,106)
	CLR_SEA_1 = (78,98,149)
	CLR_BEACH = (226,225,207)
	CLR_GRN_1 = (43,54,36)
	CLR_GRN_2 = (60,71,54)
	CLR_GRN_3 = (95,106,81)
	CLR_STN_1 = (135,135,134)
	CLR_STN_2 = (210,210,210)
	CLR_STN_3 = (230,230,230)
	CLR_PEAK = (255,255,255)
	CLR_UNKNOWN = (29,33,49)
else:
	CLR_SEA_3 = (0,0,0)
	CLR_SEA_2 = (30,30,30)
	CLR_SEA_1 = (60,60,60)
	CLR_BEACH = (80,80,80)
	CLR_GRN_1 = (100,100,100)
	CLR_GRN_2 = (130,130,130)
	CLR_GRN_3 = (160,160,160)
	CLR_STN_1 = (180,180,180)
	CLR_STN_2 = (205,205,205)
	CLR_STN_3 = (225,225,225)
	CLR_PEAK = (255,255,255)
	CLR_UNKNOWN = (0,0,0)
