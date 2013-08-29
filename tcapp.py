"""
tcapp.py

@title 	Tile-based Terrain Generator

@desc 	Tile heights are calculated via cellular automata algorithm. 
		Tile info is stored in 2-d array and accessed via [x][y] tile coords.
		Pygame is required.
		Currently working in coarse-grain resolution. 

@license MIT License
"""

import time
import math
import random
import pygame
import pprint
import sys
from pygame.locals import *
from config import *
from helpers import *
import colorsys


class TCApp:

	def __init__(self, map_width, map_height, tile_size):
		
		#init framework
		pygame.init()
		pygame.font.init()		
		random.seed()

		if not pygame.font: print 'Warning, fonts disabled'
		if not pygame.mixer: print 'Warning, sound disabled'
		
		self.tile_size = tile_size
		self.map_width = map_width
		self.map_height = map_height
		self.base_font = pygame.font.SysFont("helvetica", 7)
		self.menu_font = pygame.font.SysFont("monospace", 14)

		# init screen
		self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))	
		pygame.display.set_caption("Enter: New | 1: Evolve (Mode) | 2: Evolve (Avg) | 3: Erode | Esc: Exit")

		self.create_window()

		# init map
		self.create_map()
		
		#wait for events in game loop
		self.loop()


	def loop(self):
		# infinite loop
		running = 1
		while running:
			event = pygame.event.poll()
			keys = pygame.key.get_pressed()

			if event.type == pygame.QUIT:
				running = 0
			if keys[pygame.K_ESCAPE]:
				running = 0
			if keys[pygame.K_RETURN]:				
				self.create_map()
			if keys[pygame.K_1]:
				self.evolve_state(evolve_mode='mode')					
			if keys[pygame.K_2]:
				self.evolve_state(evolve_mode='average')					
			if keys[pygame.K_3]:
				self.erode(coverage=0.5, strength=0.1)
		

	def create_window(self):		
		""" draw black window to start """
		bg = pygame.Surface(self.screen.get_size())
		bg = bg.convert()
		bg.fill(GRAY)
		self.screen.blit(bg, (0,0))
		pygame.display.flip()
	

	def create_map(self):

		self.reset_tile_size()
		
		self.draw_grid()

		# magic formula

		self.evolve_state(evolve_mode='mode')		
		self.evolve_state(evolve_mode='mode')				
		self.evolve_state(evolve_mode='mode')				
		self.evolve_state(evolve_mode='mode')				
		self.evolve_state(evolve_mode='mode')				

		# self.erode(coverage=0.5, strength=0.1)		

		self.draw_grid_refined(grid_scale=2)							
		
		# self.evolve_state(evolve_mode='mode')				
		# self.evolve_state(evolve_mode='average')	

		self.draw_grid_refined(grid_scale=2)		
		self.draw_grid_refined(grid_scale=2)

	def draw_grid(self):
		""" initialize grid structure to random noise """
		# init the grid
		self.cols = int((self.map_width)/self.tile_size)
		self.rows = int((self.map_height)/self.tile_size)
		self.tiles = [[0 for x in xrange(0, self.rows, 1)] for x in xrange(0, self.cols, 1)] 
		for i in xrange(0, self.cols, 1):
			for j in xrange(0, self.rows, 1):
				rnd_key = random.randint(0,MAX_HEIGHT)					
				self.tiles[i][j] = rnd_key

		# now that random grid data is set up, draw the recs
		self.draw_current_state()


	def draw_grid_refined(self, grid_scale=4):
		""" draw new grid in finer detail than parent """
		# init the scaled grid
		tile_size_sm = self.tile_size/grid_scale
		cols_sm = int(self.map_width/tile_size_sm)
		rows_sm = int(self.map_height/tile_size_sm)
		new_tiles = [[0 for x in xrange(0, rows_sm, 1)] for x in xrange(0, cols_sm, 1)] 

		for i in xrange(0, cols_sm, 1):
			for j in xrange(0, rows_sm, 1):
				#if on border of world, make water				
				parent_tile_x = int(i/grid_scale)
				parent_tile_y = int(j/grid_scale)					
				neighbors = self.get_neighbor_tiles( (parent_tile_x, parent_tile_y) )
				z_vals = []
				for n in neighbors:
					if ( 0 <= n[0] <= self.cols ) and ( 0 <= n[1] <= self.rows ):
						z_vals.append( self.tiles[n[0]][n[1]] )
			
				# value of new small tile is avg of parents' neighbors +- random variance
				rnd_val = random.randint( 0, int(MAX_HEIGHT*NOISE_SCALE) )														
				avg_state = sum(z_vals)/len(z_vals)										
				new_tiles[i][j] = clamp(avg_state+rnd_val, 0, MAX_HEIGHT)						
							
		# reset obj properties to reflect new grid size
		self.cols = cols_sm
		self.rows = rows_sm		
		self.tile_size = tile_size_sm		
		self.tiles = new_tiles

		print "Cols: %d. Rows: %d. Tile Size: %d" % (self.cols, self.rows, self.tile_size)

		self.draw_current_state()


	def draw_current_state(self):
		""" draw each tile with current known z val """
		offset_x = 0
		offset_y = 0
		for i in xrange(0, self.cols, 1):
			for j in xrange(0, self.rows, 1):
				# color_val = self.calc_grayscale( self.tiles[i][j] )
				color_val = self.calc_hsv(self.tiles[i][j])
				# color_val = self.calc_color( self.tiles[i][j] )
				pygame.draw.rect(self.screen, color_val, ((i*self.tile_size)+offset_x, (j*self.tile_size)+offset_y, self.tile_size, self.tile_size), 0)									
				
				if TESTING == True:
					# draw label					
					text_surface = self.tile_size			
					label_text = str(i) + ', ' + str(j)
					label = self.base_font.render(label_text, 1, PINK)
					label_rect = pygame.Rect( (self.tile_size*i+offset_x+1,self.tile_size*j+offset_y+1), (self.tile_size+10,self.tile_size+10))
					self.screen.blit(label,label_rect)

		pygame.display.flip()
		# time.sleep (1000.0 / 1000.0)		


	def evolve_state(self, evolve_mode='average'):
		""" smooth map via averaging or mode 
			evolve_mode: string, 'mode' or 'average' """
		new_tiles = [[0 for x in xrange(0, self.rows, 1)] for x in xrange(0, self.cols, 1)] 
		for i in xrange(0, self.cols, 1):
			for j in xrange(0, self.rows, 1):					
				neighbors = self.get_neighbor_tiles( (i, j) )
				z_vals = []
				for n in neighbors:
					if ( 0 < n[0] < self.cols ) and ( 0 < n[1] < self.rows ):
						z_vals.append( self.tiles[n[0]][n[1]] )
				rnd_var = random.randint(-1*int(MAX_HEIGHT*NOISE_SCALE), int(MAX_HEIGHT*NOISE_SCALE) )												
				if evolve_mode == 'mode':								
					mode_state = mode(z_vals)
					new_tiles[i][j] = mode_state + rnd_var
				elif evolve_mode == 'average':
					avg_state = sum(z_vals)/len(z_vals)
					new_tiles[i][j] = avg_state + rnd_var

		self.tiles = new_tiles
		self.draw_current_state()


	def erode(self, coverage=0.5, strength=0.1):
		""" coverage, strength: float 0-1 """
		tile_total = int((self.cols * self.rows) * coverage)
		for tile in xrange(0,tile_total):
			rnd_tile_x = random.randint(0, self.cols-1)
			rnd_tile_y = random.randint(0, self.rows-1)
			rnd_var_max = MAX_HEIGHT * strength
			rnd_var_max = random.randint(0, int(rnd_var_max))
			# print rnd_tile_x, rnd_tile_y, self.tiles[rnd_tile_x][rnd_tile_y], rnd_var_max
			new_z = ''
			if rnd_var_max % 2 == 0:
				new_z = clamp(self.tiles[rnd_tile_x][rnd_tile_y]-rnd_var_max, 0, MAX_HEIGHT)
			else: 
				new_z = clamp(self.tiles[rnd_tile_x][rnd_tile_y]+rnd_var_max, 0, MAX_HEIGHT)
			self.tiles[rnd_tile_x][rnd_tile_y] = new_z
		
		self.draw_current_state()

	def get_neighbor_tiles(self, tile):
		""" accepts tuple of tile coords; returns array of tile coord tuples """
		x_pos = tile[0]
		y_pos = tile[1]
		neighbors = []
		for i in range(-1,2,1):
			for j in range(-1,2,1):
				if i==0 and j==0:
					pass # do nothing, it's the center tile					
				else:	
					new_x = (x_pos + i) % self.cols
					new_y = (y_pos + j) % self.rows
					# print "neighbor:", i, j, x_pos, y_pos, new_x, new_y					
					neighbors.append( (new_x, new_y) )					
		return neighbors


	def reset_tile_size(self):
		self.tile_size = TILE_SIZE


	def calc_grayscale(self, z_val):
		g_val = clamp(z_val * (255/MAX_HEIGHT), 0, 255)
		return (g_val,g_val,g_val)


	def calc_hsv(self, z_val):
		rgb_scale = 255.0/MAX_HEIGHT
		hsv_scale = 100.0/MAX_HEIGHT
		z_val_rgb = clamp( int(z_val * rgb_scale), 0, 255 )
		z_val_hsv = clamp( int(z_val * hsv_scale), 0, 100 )
		# print z_val, rgb_scale, hsv_scale, z_val_rgb, z_val_hsv
		color = pygame.Color(z_val_rgb, z_val_rgb, z_val_rgb, 100) # Have to create a Color object using RGBA, then change its color
		# color.hsva = (30,30,30,100)
		# HSVA: Hue, Saturation, Value, Alpha (transparency).               
		# find out how Hue values (0-359) correspond to colors;
		# saturation is the intensity of the color, from gray to
		# bright (0-100); value runs from dark to light (0-100).
		if z_val <= WATER_TABLE_LEVEL*MAX_HEIGHT: 
			z_val_hsv = clamp(z_val_hsv+10, 0, 100)
			color.hsva = (200, 60, z_val_hsv, 100)
		elif WATER_TABLE_LEVEL*MAX_HEIGHT < z_val <= BEACH_END*MAX_HEIGHT:
			z_val_hsv = clamp(z_val_hsv+15, 0, 100)			
			color.hsva = (52, 10, z_val_hsv, 100)
		elif z_val > TREE_LINE*MAX_HEIGHT:	
			color.hsva = (0, 0, z_val_hsv, 100)			
		else:
			z_val_hsv = clamp(z_val_hsv-15, 0, 100)			
			color.hsva = (137, 60, z_val_hsv, 100)
		return color

	def calc_color(self, z_val):
		""" accepts z value (int), returns color constant in RGB form """
		if z_val == 0: return CLR_SEA_3
		if z_val == 1: return CLR_SEA_2
		if z_val == 2: return CLR_SEA_1
		if z_val == 3: return CLR_BEACH
		if z_val == 4: return CLR_GRN_1
		if z_val == 5: return CLR_GRN_2
		if z_val == 6: return CLR_GRN_3
		if z_val == 7: return CLR_STN_1
		if z_val == 8: return CLR_STN_2
		if z_val == 9: return CLR_STN_3
		if z_val == 10: return CLR_PEAK
		return CLR_UNKNOWN


	def random_tile(self):
		""" return xy tuple for random tile on map """		
		x = random.randint(0, SCREEN_WIDTH/self.tile_size)
		y = random.randint(0, SCREEN_HEIGHT/self.tile_size)
		return (x,y)


	def random_point(self):
		""" return xy tuple for random point on screen """
		x = random.randint(0, SCREEN_WIDTH-1)
		y = random.randint(0, SCREEN_HEIGHT-1)
		return (x,y)

