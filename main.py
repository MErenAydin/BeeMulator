import pygame
from pygame.locals import *

class Vec2():
	def __init__(self, x = 0, y = 0):
			self.x = x
			self.y = y

class Bee():
	def __init__(self):
		self.position = Vec2()
		self.velocity = Vec2()

	def Render(self, game):

		size = 8
		screenX = self.position.x
		screenY = self.position.y
		pygame.draw.circle(game.screen, [255,255,255], [screenX,screenY], size)

class Game():
	DRAW_MODE_NORMAL = 0
	DRAW_MODE_DEBUG = 1

    ########################
	def __init__(self):
		self.bees = None

    ########################
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

    ########################
	def UpdateDisplay(self):
		if self.drawMode == Game.DRAW_MODE_DEBUG:
			colorScreen = (0,0,255)
		else:
			colorScreen = (0,0,0)
		self.screen.fill(colorScreen)

		if self.bees != None:
			for bee in self.bees:
				bee.Render(self)

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
	game.bees = []
	for i in range(20,40):
		bee = Bee()
		bee.position = Vec2(i * 15, i * 15)
		game.bees.append(bee)

	game.Start("BeeMulator", is_fullscreen = False)
	while game.isRunning:
		game.Update()

	game.Shutdown()

if __name__ == "__main__":
	main()