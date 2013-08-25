"""
terracellapp.py

plan of attack:
- init app, fonts, cells, menu
- draw window with menu screen and starting config cells
- listen for events to advance generation, then draw new cells 
- add with other effects :)

"""

import time
import math
import random
import pygame
import pprint
from pygame.locals import *
from config import *
from helpers import *



class TCApp:


	def __init__(self, map_width, map_height):
		
		if not pygame.font: print 'Warning, fonts disabled'
		if not pygame.mixer: print 'Warning, sound disabled'

		pygame.init()
		pygame.font.init()		
		
		self.tile_size = TILE_SIZE
		self.map_width = map_width
		self.map_height = map_height
		self.base_font = pygame.font.SysFont("helvetica", 7)
		self.menu_font = pygame.font.SysFont("monospace", 14)

		# init screen
		self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))	
		# pygame.display.set_caption("FysPhun, check command line for controls!")
				
		# draw the title screen 
		self.draw_window()

		# draw initial grid
		self.draw_grid()

		# smooth it out a little
		if SMOOTH_PASSES > 0:
			for i in xrange(SMOOTH_PASSES):
				self.evolve_state()

		# refine the granularity
		self.refine_grid()

		#wait for events in loop
		self.loop()


	def loop(self):
		# infinite loop
		running = 1
		while running:
			event = pygame.event.poll()
			keys = pygame.key.get_pressed()  #checking pressed keys

			if event.type == pygame.QUIT:
				running = 0
			
			# if keys[pygame.K_RETURN]:
			# 	self.evolve_state()
			# 	time.sleep (50.0 / 1000.0)
				
			if keys[pygame.K_ESCAPE]:
				self.draw_grid()
				time.sleep (50.0 / 1000.0)

			

		pygame.display.flip()
		

	def draw_window(self):		

		#draw black screen to start
		bg = pygame.Surface(self.screen.get_size())
		bg = bg.convert()
		bg.fill(GRAY)
		self.screen.blit(bg, (0,0))
		
		# draw title screen		
		text_surface = (SCREEN_WIDTH*.22) - 20
		label_text = "ENTER: Evolve a new generation. ESCAPE: Reset to initial random state."
		label = self.menu_font.render(label_text, 1, WHITE)
		label_rect = label.get_rect()
		label_rect = label_rect.move(20,5)
		self.screen.blit(label,label_rect)
		pygame.display.flip()

	
		
	def draw_grid(self):

		# init the grid
		self.cols = int((self.map_width)/self.tile_size)
		self.rows = int((self.map_height)/self.tile_size)
		self.tiles = [[0 for x in xrange(0, self.rows, 1)] for x in xrange(0, self.cols, 1)] 
		random.seed()
		for i in xrange(0, self.cols, 1):
			for j in xrange(0, self.rows, 1):

				#if on border of world, make water
				if i == 0 or i == self.cols-1 or j == 0 or j == self.rows-1:
					self.tiles[i][j] = 0				
				else:
					rnd_key = random.randint(0,100)
					if rnd_key > 50: 
						self.tiles[i][j] = 1
					else:
						self.tiles[i][j] = 0
				
		# now that random grid data is set up, draw the recs
		self.draw_current_state()



	def refine_grid(self):

		# re-init the grid
		self.tile_size = TILE_SIZE_FINE
		self.cols = int((self.map_width)/self.tile_size)
		self.rows = int((self.map_height)/self.tile_size)
		new_tiles = [[0 for x in xrange(0, self.rows, 1)] for x in xrange(0, self.cols, 1)] 
		random.seed()
		for i in xrange(0, self.cols, 1):
			for j in xrange(0, self.rows, 1):
				parent_i = clamp(i/5,0,self.map_width)
				parent_j = clamp(j/5,0,self.map_height)
				
				# if on border of world, make water
				if i == 0 or i == self.cols-1 or j == 0 or j == self.rows-1:
					new_tiles[i][j] = 0				
				else:
					# chance of being same as parent is 50%
					rnd_key = random.randint(0,100)
					new_tiles[i][j] = self.tiles[parent_i][parent_j]
					# if rnd_key > 80: 
					# 	new_tiles[i][j] = self.tiles[parent_i][parent_j]
					# else:
					# 	new_tiles[i][j] = rnd_key
				print 'i:' + str(i) + ' j:' + str(j) + ' parent_i: ' + str(parent_i) + ' parent_j: ' + str(parent_j) + ' parent z: ' + str(self.tiles[parent_i][parent_j]) + ' child z: ' + str(new_tiles[i][j])
		self.tiles = new_tiles
		# now that random grid data is set up, draw the recs
		self.draw_current_state()





	def draw_current_state(self):
		# draw each tile and its label
		offset_x = 0
		offset_y = 30
		for i in xrange(0, self.cols, 1):
			for j in xrange(0, self.rows, 1):
				# draw rect outline
				color_val = clamp(self.tiles[i][j]*255, 0, 255)
				pygame.draw.rect(self.screen, (color_val,color_val,color_val), ((i*self.tile_size)+offset_x, (j*self.tile_size)+offset_y, self.tile_size, self.tile_size), 0)									
				
				if TESTING == True and self.tile_size != TILE_SIZE_FINE:
					#draw border
					pygame.draw.rect(self.screen, GRAY, ((i*self.tile_size)+offset_x, (j*self.tile_size)+offset_y, self.tile_size, self.tile_size), 1)									
					# draw label					
					text_surface = self.tile_size			
					label_text = str(i) + ', ' + str(j)
					label = self.base_font.render(label_text, 1, PINK)
					label_rect = pygame.Rect( (self.tile_size*i+offset_x,self.tile_size*j+offset_y), (self.tile_size+10,self.tile_size+10))
					self.screen.blit(label,label_rect)


		pygame.display.flip()


	def evolve_state(self):
		new_tiles = [[0 for x in xrange(0, self.rows, 1)] for x in xrange(0, self.cols, 1)] 
		for i in xrange(0, self.cols, 1):
			for j in xrange(0, self.rows, 1):

				# if i == 0 or i == self.rows or j == 0 or j == self.cols: 
				# 	new_tiles[i][j] = 0
				if i == 0 or i == self.cols-1 or j == 0 or j == self.rows-1:
					self.tiles[i][j] = 0
				else:
					state = self.tiles[i][j]
					neighbors = self.get_neighbors(i, j)
					
					if state == 1 and sum(neighbors) >= 3:
						new_tiles[i][j] = 1
					elif state == 0 and sum(neighbors) >= 4:
						new_tiles[i][j] = 1
					else:
						new_tiles[i][j] = 0

		self.tiles = new_tiles
		self.draw_current_state()


	def get_neighbors(self, tile_x, tile_y):
		""" return list of neighboring tiles """
		x_pos = tile_x
		y_pos = tile_y
		neighbors = []
		i = 1

		#todo: rewrite this with nested loops
		if (int(x_pos) - i >= 0) and (int(y_pos) - i >=0):
			neighbors.append(self.tiles[x_pos - i][y_pos - i] ) #top_left	
			
 		if (int(y_pos) - i >= 0):				
			neighbors.append(self.tiles[x_pos][y_pos - i] ) #top_mid
		
		if (int(x_pos) + i <= self.cols - 1) and (int(y_pos) - i >=0):
			neighbors.append(self.tiles[x_pos + i][y_pos - i]) #top right
		
		if (int(x_pos) - i <= 0):
			neighbors.append(self.tiles[x_pos - i][y_pos]) #mid_left
		
		if (int(x_pos) + i <= self.cols - 1):
			neighbors.append(self.tiles[x_pos + i ][y_pos] ) #mid right

		if (int(x_pos) - i <= 0) and (int(y_pos) + i <= self.rows - 1):
			neighbors.append(self.tiles[x_pos - i][y_pos + i]) #btm left
		
		if (int(y_pos) + i <= self.rows - 1):
			neighbors.append(self.tiles[x_pos][y_pos + i]) #btm mid

		if (int(x_pos) + i <= self.cols - 1) and (int(y_pos) + i <= self.rows - 1):
			neighbors.append(self.tiles[x_pos + i][y_pos + i]) #btm right
			
		return neighbors
