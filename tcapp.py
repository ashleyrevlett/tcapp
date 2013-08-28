"""
tcapp.py

@title 	Tile-based Terrain Generator

@desc 	Tile heights are calculated via cellular automata algorithm. 
		Tile info is stored in 2-d array and accessed via [x][y] tile coords.
		Pygame is required.
		Currently working in coarse-grain resolution. 

@todo	Add fractal layer of detail to current low-res map

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
		pygame.display.set_caption("Press Enter to reset, Esc to quit")

		self.draw_window()

		# init map
		self.generate_map()
		
		#wait for events in game loop
		self.loop()



	def reset_tile_size(self):
		self.tile_size = TILE_SIZE


	def generate_map(self):
		self.draw_grid()

		# smooth it out a little via mode
		if SMOOTH_PASSES > 1:
			for i in xrange(SMOOTH_PASSES):
				self.evolve_state(evolve_mode=1)
		else:
			self.evolve_state(evolve_mode=1)
		
		self.evolve_state(evolve_mode=2)
		self.evolve_state(evolve_mode=1)
		
		self.draw_grid_refined()
				
		self.evolve_state(evolve_mode=1)
		self.evolve_state(evolve_mode=2)

	def loop(self):
		# infinite loop
		running = 1
		while running:
			event = pygame.event.poll()
			keys = pygame.key.get_pressed()

			if event.type == pygame.QUIT:
				running = 0
			
			if keys[pygame.K_RETURN]:
				self.reset_tile_size()
				self.generate_map()
				time.sleep (50.0 / 1000.0)
			
			if keys[pygame.K_ESCAPE]:
				sys.exit()	
		

	def draw_window(self):		
		""" draw black window to start """
		bg = pygame.Surface(self.screen.get_size())
		bg = bg.convert()
		bg.fill(GRAY)
		self.screen.blit(bg, (0,0))
		pygame.display.flip()
	
		
	def draw_grid(self):
		""" initialize grid structure to random noise """
		# init the grid
		self.cols = int((self.map_width)/self.tile_size)
		self.rows = int((self.map_height)/self.tile_size)
		self.tiles = [[0 for x in xrange(0, self.rows, 1)] for x in xrange(0, self.cols, 1)] 
		for i in xrange(0, self.cols, 1):
			for j in xrange(0, self.rows, 1):

				#if on border of world, make water
				if i == 0 or i == self.cols-1 or j == 0 or j == self.rows-1:
					self.tiles[i][j] = 0				
				else:
					rnd_key = random.randint(0,MAX_HEIGHT)					
					self.tiles[i][j] = rnd_key

		# now that random grid data is set up, draw the recs
		self.draw_current_state()


	def draw_current_state(self):
		""" draw each tile with current known z val """
		offset_x = 0
		offset_y = 0
		for i in xrange(0, self.cols, 1):
			for j in xrange(0, self.rows, 1):
				color_val = self.calc_grayscale( self.tiles[i][j] )
				pygame.draw.rect(self.screen, color_val, ((i*self.tile_size)+offset_x, (j*self.tile_size)+offset_y, self.tile_size, self.tile_size), 0)									
				
				if TESTING == True:
					# draw label					
					text_surface = self.tile_size			
					label_text = str(i) + ', ' + str(j)
					label = self.base_font.render(label_text, 1, PINK)
					label_rect = pygame.Rect( (self.tile_size*i+offset_x+1,self.tile_size*j+offset_y+1), (self.tile_size+10,self.tile_size+10))
					self.screen.blit(label,label_rect)
		
		time.sleep (50.0 / 1000.0)

		pygame.display.flip()


	def evolve_state(self, evolve_mode):
		""" smooth map via averaging or mode 
			1 is mode, 2 is average """
		new_tiles = [[0 for x in xrange(0, self.rows, 1)] for x in xrange(0, self.cols, 1)] 
		for i in xrange(0, self.cols-1, 1):
			for j in xrange(0, self.rows-1, 1):
				# if on map border, make ocean
				if i == 0 or i == self.cols or j == 0 or j == self.rows:
					new_tiles[i][j] = 0
				else:
					state = self.tiles[i][j]
					neighbors = self.get_neighbor_tiles( (i, j) )
					z_vals = [self.tiles[n[0]][n[1]] for n in neighbors]
					# rnd_var = random.randint(0, (MAX_HEIGHT*NOISE_SCALE) )												
					rnd_var = 0
					if evolve_mode == 1:								
						mode_state = mode(z_vals)
						new_tiles[i][j] = mode_state + rnd_var
					else:
						avg_state = sum(z_vals)/len(z_vals)
						new_tiles[i][j] = avg_state + rnd_var

		self.tiles = new_tiles
		self.draw_current_state()


		
	def draw_grid_refined(self):
		""" draw new grid in finer detail than parent """
		# init the scaled grid
		grid_scale = 4
		self.tile_size = self.tile_size/grid_scale
		self.cols = int(self.map_width/self.tile_size)
		self.rows = int(self.map_height/self.tile_size)
		new_tiles = [[0 for x in xrange(0, self.rows, 1)] for x in xrange(0, self.cols, 1)] 

		for i in xrange(0, self.cols-1, 1):
			for j in xrange(0, self.rows-1, 1):
				#if on border of world, make water				
				parent_tile_x = int(i/grid_scale)
				parent_tile_y = int(j/grid_scale)
					
				if i == 0 or i == self.cols or j == 0 or j == self.rows:
					new_tiles[i][j] = 0				
				else:					
					neighbors = self.get_neighbor_tiles( (parent_tile_x,parent_tile_y) )
					# print self.cols, self.rows, self.tile_size, i,j, parent_tile_x, parent_tile_y
					# pprint.pprint(neighbors)
					try:
						# value of new small tile is avg of parents' neighbors +- random variance
						rnd_key = random.randint(0,100)									
						if rnd_key < 70:
							rnd_val = random.randint( 0, MAX_HEIGHT*NOISE_SCALE )									
						else:
							rnd_val = 0
						z_vals = [self.tiles[n[0]][n[1]] for n in neighbors]
						avg_state = sum(z_vals)/len(z_vals)										
						new_tiles[i][j] = clamp(avg_state+rnd_val, 0, MAX_HEIGHT)						
					except Exception, e:
						# print 'fail', e
						pass
			
		#  update screen
		self.tiles = new_tiles
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
					new_x = clamp(x_pos + i, 0, self.cols)
					new_y = clamp(y_pos + j, 0, self.rows)					
					neighbors.append( (new_x, new_y) )					
		return neighbors


	def calc_grayscale(self, z_val):
		g_val = clamp(z_val * (255/MAX_HEIGHT), 0, 255)
		return (g_val,g_val,g_val)


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

