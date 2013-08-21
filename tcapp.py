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
		self.base_font = pygame.font.SysFont("monospace", 12)

		# init screen
		self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))	
		# pygame.display.set_caption("FysPhun, check command line for controls!")
				
		# draw the title screen 
		self.draw_window()

		# draw initial grid
		self.draw_grid()

		#wait for events
		self.loop()


	def loop(self):
		# infinite loop
		running = 1
		while running:
			event = pygame.event.poll()
			keys = pygame.key.get_pressed()  #checking pressed keys

			if event.type == pygame.QUIT:
				running = 0
			
			if keys[pygame.K_RETURN]:
				self.evolve_state()
				time.sleep (50.0 / 1000.0)
				
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
		label = self.base_font.render(label_text, 1, WHITE)
		label_rect = label.get_rect()
		label_rect = label_rect.move(20,5)
		self.screen.blit(label,label_rect)
		pygame.display.flip()

	
		
	def draw_grid(self):
		# init the grid
		self.cols = int((self.map_width-20)/self.tile_size)
		self.rows = int((self.map_height-40)/self.tile_size)
		self.tiles = [[0 for x in xrange(0, self.rows, 1)] for x in xrange(0, self.cols, 1)] 

		for i in xrange(0, self.cols, 1):
			for j in xrange(0, self.rows, 1):
				random.seed()
				rnd_key = random.randint(0,100)
				if rnd_key > 50: 
					self.tiles[i][j] = 1
				else:
					self.tiles[i][j] = 0

		# now that random grid data is set up, draw the recs
		self.draw_state()


	def draw_state(self):
		# draw each tile and its label
		offset_x = 10
		offset_y = 30
		for i in xrange(0, self.cols, 1):
			for j in xrange(0, self.rows, 1):
				# draw rect outline
				pygame.draw.rect(self.screen, (self.tiles[i][j]*255,self.tiles[i][j]*255,self.tiles[i][j]*255), ((i*self.tile_size)+offset_x, (j*self.tile_size)+offset_y, TILE_SIZE, TILE_SIZE), 0)									
		pygame.display.flip()


	def evolve_state(self):
		new_tiles = [[0 for x in xrange(0, self.rows, 1)] for x in xrange(0, self.cols, 1)] 
		for i in xrange(0, self.cols, 1):
			for j in xrange(0, self.rows, 1):

				state = self.tiles[i][j]
				neighbors = self.get_neighbors(i, j)
				
				if state == 1 and sum(neighbors) >= 3:
					new_tiles[i][j] = 1
				elif state == 0 and sum(neighbors) >= 4:
					new_tiles[i][j] = 1
				else:
					new_tiles[i][j] = 0

		self.tiles = new_tiles
		self.draw_state()


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
