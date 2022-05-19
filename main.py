import pygame
from pygame.locals import *

import random

class Vec2():
	def __init__(self, x = 0, y = 0):
		self.x = x
		self.y = y
	
	def __add__(self, other):
		self.x += other.x
		self.y += other.y
		return self

	def __sub__(self, other):
		self.x -= other.x
		self.y -= other.y
		return self

	def __iadd__(self, other):
		self.x += other.x
		self.y += other.y
		return self

	def __isub__(self, other):
		self.x -= other.x
		self.y -= other.y
		return self

class Bee():
	def __init__(self, position = None, isQueen = False):
		self.position = Vec2() if position is None else position 
		self.__velocity = None
		self.__changed = False
		self.isQueen = isQueen

	def Render(self, game):
		if self.isQueen:
			size = 4
			color = [255, 0, 0]
		else:
			size = 2
			color = [255, 255, 0]
		screenX = self.position.x
		screenY = self.position.y
		pygame.draw.circle(game.screen, color, [screenX,screenY], size)

	def get_velocity(self):
		return self.__velocity
		
	def set_velocity(self, value):
		self.__velocity = value
		self.position += value
		self.__changed = True
		
	velocity = property(get_velocity, set_velocity)

class Hive():
	def __init__(self):
		self.rect = Rect(10, 10 ,10 ,10)
		self.bees = None

	def PopulateHive(self, beeAmount):
		self.bees = []
		for i in range(beeAmount):
			bee = Bee()
			bee.position = Vec2(self.rect.centerx, self.rect.centery)
			self.bees.append(bee)
		self.bees[-1].isQueen = True

	def Render(self, game):
		color = [255, 255, 255]
		pygame.draw.rect(game.screen, color, self.rect, 2)
		for bee in self.bees:
			bee.Render(game)

class Game():
	DRAW_MODE_NORMAL = 0
	DRAW_MODE_DEBUG = 1

	def __init__(self):
		self.bees = None
		self.hives = None

	def Start(self, NAME, width = 1280, height = 720, is_fullscreen = False, draw_mode = DRAW_MODE_NORMAL):
		pygame.init()
		self.isRunning = True

		if is_fullscreen:
			self.winstyle = pygame.FULLSCREEN
			self.width = 0
			self.height = 0
			
		else:
			self.winstyle = pygame.RESIZABLE
			self.width = width
			self.height = height
		
		self.winName = NAME
		pygame.display.set_caption(self.winName)
		self.drawMode = draw_mode
		self.screenRect = Rect(0, 0, self.width, self.height)
		self.bestdepth = pygame.display.mode_ok(self.screenRect.size, self.winstyle)
		self.screen = pygame.display.set_mode(self.screenRect.size, self.winstyle)

		if is_fullscreen:
			self.width = self.screen.get_size()[0]
			self.height = self.screen.get_size()[1]

	def UpdateDisplay(self):
		if self.drawMode == Game.DRAW_MODE_DEBUG:
			colorScreen = (0,0,255)
		else:
			colorScreen = (0,0,0)
		self.screen.fill(colorScreen)

		if self.hives != None:
			for hive in self.hives:
				hive.Render(self)

		pygame.display.flip()
		clock = pygame.time.Clock()
		clock.tick(30)
    
	def Update(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT or (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE):
				self.isRunning = False

		self.UpdateDisplay()

	def Shutdown(self):
		pygame.quit()

def main():
	game = Game()
	game.Start("BeeMulator", is_fullscreen = True)

	game.hives = []
	for i in range(1):
		hive = Hive()
		hive.rect = Rect(game.width / 2 - 50, game.height / 2 -50, 100, 100)
		hive.PopulateHive(1000)
		game.hives.append(hive)


	while game.isRunning:
		game.Update()
		for bee in game.hives[0].bees:
			bee.velocity = Vec2(random.randint(-3, 3), random.randint(-3, 3))

	game.Shutdown()

if __name__ == "__main__":
	main()