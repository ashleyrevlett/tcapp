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
from pygame.locals import *
from config import *



class TCApp:


	def __init__(self):
		random.seed()
		pygame.font.init()
		self.draw_window()
		self.loop()
		

	def draw_window(self):		
		screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
		screen.fill((0, 0, 0))
		pygame.display.flip()


	def loop(self):
		# infinite loop
		running = 1
		while running:
		    event = pygame.event.poll()
		    if event.type == pygame.QUIT:
		        running = 0
