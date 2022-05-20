
import pygame
from pygame.locals import *
from vector import Vec2

import random
import math
import copy

class Bee():

	WANDERING = 0
	COLLECTING = 1
	RETURNING = 2
	DEPOSIT = 3

	def __init__(self, hive, position = None, isQueen = False):
		self.hive = hive
		self.position = Vec2() if position is None else position
		self.direction = Vec2()
		self.__velocity = Vec2()
		self.__changed = False
		self.isQueen = isQueen
		self.trace = []
		self.traceLength = 50
		self.maxSpeed = 2
		self.steerStrength = 1.2
		self.wanderStrength = 0.2
		self.visionRange = 50
		self.state = Bee.WANDERING
		self.attachedFlower = None
		self.attachTime = 0
		self.collectingTime = 5

	def Render(self, game):
		if self.isQueen:
			size = 4
			color = [100, 100, 0]
		else:
			size = 2
			color = [255, 255, 0]
		screenX = self.position.x
		screenY = self.position.y
		if game.drawMode == Game.DRAW_MODE_DEBUG:
			pygame.draw.circle(game.screen, [255,0,0], [screenX,screenY], self.visionRange , 1)
			for t in self.trace:
				pygame.draw.circle(game.screen, [155, 155, 0], [t.x,t.y], 1)
		pygame.draw.circle(game.screen, color, [screenX,screenY], size)

	def Move(self,game):
		if self.state == Bee.WANDERING:
			flower, distance = self.ClosestFlower(game)
			if flower is not None:
				if distance < flower.size:
					self.attachedFlower = flower
					self.state = Bee.COLLECTING
					self.attachTime = pygame.time.get_ticks()
				self.direction = (flower.position - self.position).normalized()
			else:
				self.direction = (self.direction + Vec2(random.random() * 2 - 1, random.random() * 2 - 1) * self.wanderStrength).normalized()

		elif self.state == Bee.COLLECTING:
			delta = (pygame.time.get_ticks() - self.attachTime) / 1000
			if self.attachedFlower.collectCount <= 0:
				self.state = Bee.WANDERING
			if delta > self.collectingTime:
				self.state = Bee.RETURNING
				self.attachedFlower.collectCount -= 1

		elif self.state == Bee.RETURNING:
			self.direction = (self.hive.position - self.position).normalized()
			if self.hive.rect.collidepoint(self.position.x, self.position.y):
				self.state = Bee.DEPOSIT
				self.attachTime = pygame.time.get_ticks()

		elif self.state == Bee.DEPOSIT:
			delta = (pygame.time.get_ticks() - self.attachTime) / 1000
			if delta > self.collectingTime:
				self.state = Bee.WANDERING
		else:
			pass
		
		screenSize = game.screen.get_size()
		if self.state == self.WANDERING or self.state == self.RETURNING:
			if self.position.x < 0:
				self.position.x = 0
				self.direction.x = -self.direction.x
			elif self.position.x > screenSize[0]:
				self.position.x = screenSize[0]
				self.direction.x = -self.direction.x
			if self.position.y < 0:
				self.position.y = 0
				self.direction.y = -self.direction.y
			elif self.position.y > screenSize[1]:
				self.position.y = screenSize[1]
				self.direction.y = -self.direction.y
			desiredVelocity = self.direction *  self.maxSpeed
			desiredSteeringForce = (desiredVelocity - self.velocity) * self.steerStrength
			acceleration = Vec2.clamp_magnitude(desiredSteeringForce, self.steerStrength)

			#if self.position.x < self.hive.rect.right and self.position.x > self.hive.rect.left \
			#	and self.position.y < self.hive.rect.bottom and self.position.y > self.hive.rect.top:
			self.velocity = Vec2.clamp_magnitude((self.velocity + acceleration * Game.DELTA_TIME), self.maxSpeed)
			self.position += self.velocity * Game.DELTA_TIME
			
			#angle = math.degrees(math.atan2(self.velocity.x, self.velocity.y))

	def ClosestFlower(self, game):
		for flower in game.flowers:
			if flower.collectCount <= 0:
				continue
			distance = (self.position - flower.position).get_magnitude()
			if distance < self.visionRange:
				return flower, distance
		return None, None
		
	def _set_velocity(self, value):
		self.__velocity = value
		self.trace.append(copy.deepcopy(self.position))
		if len(self.trace) > self.traceLength:
			self.trace.pop(0)
		self.position += value
		self.__changed = True
		
	velocity = property(lambda self: self.__velocity, _set_velocity)

class Hive():
	def __init__(self, pos):
		self.position = pos
		self.rect = Rect(self.position.x - 50, self.position.y - 50, 100, 100)
		self.bees = None

	def PopulateHive(self, beeAmount):
		self.bees = []
		for i in range(beeAmount):
			bee = Bee(self)
			bee.position = Vec2(self.rect.centerx, self.rect.centery)
			self.bees.append(bee)
		self.bees[-1].isQueen = True

	def Render(self, game):
		color = [255, 255, 255]
		pygame.draw.rect(game.screen, color, self.rect, 2)
		for bee in self.bees:
			bee.Render(game)

class Flower():
	def __init__(self, pos):
		self.position = pos
		self.collectCount = 5
		self.refillTime = 10
		self.size = 12

	def Render(self, game):
		color = [255, 0, 0] if self.collectCount > 0 else [255, 255, 255]

		screenX = self.position.x
		screenY = self.position.y
		if game.drawMode == Game.DRAW_MODE_DEBUG:
			pass
		rect = Rect(self.position.x - self.size / 2, self.position.y - self.size / 2, self.size, self.size)
		pygame.draw.rect(game.screen, color, rect)
		pygame.draw.circle(game.screen, [255,255,0], [screenX,screenY], 2)

class Game():
	DRAW_MODE_NORMAL = 0
	DRAW_MODE_DEBUG = 1
	DELTA_TIME = 0
	
	def __init__(self):
		self.hives = []
		self.flowers = []

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
		self._getTicksLastFrame = 0.0

	def UpdateDisplay(self):
		if self.drawMode == Game.DRAW_MODE_DEBUG:
			colorScreen = (0,0,255)
		else:
			colorScreen = (0,0,0)
		self.screen.fill(colorScreen)

		if self.hives != None:
			for hive in self.hives:
				hive.Render(self)

		if len(self.flowers) > 0:
			for flower in self.flowers:
				flower.Render(self)

		pygame.display.flip()
		clock = pygame.time.Clock()
		clock.tick(30)
		t = pygame.time.get_ticks()
		Game.DELTA_TIME = (t - self._getTicksLastFrame) / 1000.0
		self._getTicksLastFrame = t
    
	def Update(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT or (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE):
				self.isRunning = False

			if event.type == pygame.MOUSEBUTTONDOWN:
				pos = event.pos
				button = event.button
				if button == 3:
					self.flowers.append(Flower(Vec2(pos[0], pos[1])))

		for hive in self.hives:
			for bee in hive.bees:
				bee.Move(self)

		self.UpdateDisplay()

	def Shutdown(self):
		pygame.quit()

def main():
	game = Game()
	game.Start("BeeMulator", is_fullscreen = False, draw_mode= Game.DRAW_MODE_NORMAL)

	game.hives = []
	for i in range(2):
		hive = Hive(Vec2(500 * (i + 1), 500))
		
		hive.PopulateHive(100)
		game.hives.append(hive)


	while game.isRunning:
		game.Update()

	game.Shutdown()

if __name__ == "__main__":
	main()