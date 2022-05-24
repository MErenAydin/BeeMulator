
import pygame
from pygame.locals import *
from vector import Vec2

import random
import math
import copy

class Bee():

	# Moving states
	WANDERING = 0
	TO_FOOD = 1
	COLLECTING = 2
	RETURNING = 3
	DEPOSIT = 4
	SLEEP = 5

	# Lifecycle states
	LARVA = 0
	FEEDER = 1
	BUILDER = 2
	SCOUT = 3
	COLLECTER = 4


	def __init__(self, hive, position = None):
		self.hive = hive
		self.position = Vec2() if position is None else position
		self.direction = Vec2()
		self.__velocity = Vec2()
		self.trace = []
		self.traceLength = 50
		self.maxSpeed = 2
		self.steerStrength = 1.2
		self.wanderStrength = 0.4
		self.visionRange = 50
		self.attachedFlower = None
		self.attachTime = 0
		self.collectingTime = 1

	def Hatch(self, game, isQueen = False):
		if game.drawMode == Game.DRAW_MODE_NORMAL:
			self.trace = None
		self.isQueen = isQueen
		self.lastFlowercollectCount = 0
		self.bornday = game.day
		self.state = Bee.WANDERING
		self.lifespan = 35
		self.deathHour = random.randint(0,23)
		self.nectar = 0
		self.capacity = 10
		self.collectedFlowers = []

	def Kill(self, game):
		if game.time == self.deathHour:
			self.hive.bees.remove(self) 

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
			if game.time < 5 or game.time > 19:
				self.state = Bee.RETURNING
			if self.hive.rect.collidepoint(self.position.x, self.position.y):
				if len(self.hive.knownFood) > 0:
					randomFood = random.sample( self.hive.knownFood.items(), 1)[0]
					if  self.hive.knownFood[randomFood[0]] > 0:
						self.state = Bee.TO_FOOD
						self.attachedFlower = randomFood[0]
			

			flower, _ = self.ClosestFlower(game)
			if flower is not None:
				self.state = Bee.TO_FOOD
				self.attachedFlower = flower
				self.direction = (flower.position - self.position).normalized()
			else:
				self.direction = (self.direction + Vec2(random.random() * 2 - 1, random.random() * 2 - 1) * self.wanderStrength).normalized()

		elif self.state == Bee.TO_FOOD:
			if game.time < 5 or game.time > 19:
				self.state = Bee.RETURNING
			else:
				self.direction = (self.attachedFlower.position - self.position).normalized()
				if (self.attachedFlower.position - self.position).magnitude < self.attachedFlower.size:
					self.state = Bee.COLLECTING
					self.attachTime = pygame.time.get_ticks()

		elif self.state == Bee.COLLECTING:
			if self.attachedFlower.collectCount <= 0:
				self.state = Bee.WANDERING
				return
			delta = (pygame.time.get_ticks() - self.attachTime) / 1000
			if delta > self.collectingTime:
				self.attachedFlower.collectCount -= 1
				self.nectar += 1
				self.lastFlowercollectCount = self.attachedFlower.collectCount
				self.collectedFlowers.append(self.attachedFlower)
				rand = random.random()
				treshold = 0.95 if self.attachedFlower.specie in [specie for specie in self.collectedFlowers] else 0.99
				if rand >= treshold:
					self.attachedFlower.Pollinate(game)
				self.state = Bee.RETURNING if self.nectar >= self.capacity else Bee.WANDERING

		elif self.state == Bee.RETURNING:
			self.direction = (self.hive.position - self.position).normalized()
			if self.hive.rect.collidepoint(self.position.x, self.position.y):
				self.state = Bee.DEPOSIT
				self.attachTime = pygame.time.get_ticks()

		elif self.state == Bee.DEPOSIT:
			delta = (pygame.time.get_ticks() - self.attachTime) / 1000
			if delta > self.collectingTime:
				self.hive.honey += self.nectar
				self.nectar = 0
				for f in self.collectedFlowers:
					f.isDiscovered = True
				self.collectedFlowers = []
				if self.attachedFlower in self.hive.knownFood.keys():
					self.hive.knownFood[self.attachedFlower] = self.lastFlowercollectCount if self.hive.knownFood[self.attachedFlower] > self.lastFlowercollectCount else self.hive.knownFood[self.attachedFlower]
				else:
					self.hive.knownFood[self.attachedFlower] = self.lastFlowercollectCount


				if game.time >= 5 and game.time <= 19:
					if len(self.hive.knownFood) > 0:
						randomFood = random.sample( self.hive.knownFood.items(), 1 )[0]
						if  self.hive.knownFood[randomFood[0]] > 0:
							self.attachedFlower = randomFood[0]
							self.state = Bee.TO_FOOD
						else: 
							self.state = Bee.WANDERING
					else:
						self.state = Bee.WANDERING
				else:
					self.state = Bee.SLEEP
		
		elif self.state == Bee.SLEEP:
			if game.time >= 5 and game.time <= 19:
				if len(self.hive.knownFood) > 0:
					randomFood = random.sample( self.hive.knownFood.items(), 1 )[0]
					if  self.hive.knownFood[randomFood[0]] > 0:
						self.attachedFlower = randomFood[0]
						self.state = Bee.TO_FOOD
					else: 
						self.state = Bee.WANDERING

		else:
			pass
		
		screenSize = game.screen.get_size()
		if self.state == self.WANDERING or self.state == self.RETURNING or self.state == Bee.TO_FOOD:
			if self.position.x < 0:
				self.position.x = 1
				self.direction.x = -self.direction.x
			elif self.position.x > screenSize[0]:
				self.position.x = screenSize[0] - 1
				self.direction.x = -self.direction.x
			if self.position.y < 0:
				self.position.y = 1
				self.direction.y = -self.direction.y
			elif self.position.y > screenSize[1]:
				self.position.y = screenSize[1] - 1
				self.direction.y = -self.direction.y

			desiredVelocity = self.direction *  self.maxSpeed
			desiredSteeringForce = (desiredVelocity - self.velocity) * self.steerStrength
			acceleration = Vec2.clamp_magnitude(desiredSteeringForce, self.steerStrength)

			#if self.position.x < self.hive.rect.right and self.position.x > self.hive.rect.left \
			#	and self.position.y < self.hive.rect.bottom and self.position.y > self.hive.rect.top:
			self.velocity = Vec2.clamp_magnitude((self.velocity + acceleration * Game.DELTA_TIME), self.maxSpeed)
			self.position += self.velocity * Game.DELTA_TIME
			#angle = math.degrees(math.atan2(self.velocity.x, self.velocity.y))

	def Update(self, game):
		self.Move(game)
		if game.day - self.bornday >= self.lifespan:
			self.Kill(game)

	def ClosestFlower(self, game):
		#flowers = [a for a in game.flowers if a.collectCount > 0]
		for flower in game.flowers:
			if flower.collectCount <= 0 or flower in self.collectedFlowers:
				continue
			distance2 = (self.position - flower.position).get_magnitude2()
			if distance2 < self.visionRange * self.visionRange:
				return flower, distance2
		return None, None
		
	def _set_velocity(self, value):
		self.__velocity = value
		if self.trace is not None:
			self.trace.append(copy.deepcopy(self.position))
			if len(self.trace) > self.traceLength:
				self.trace.pop(0)
		self.position += value
		
	velocity = property(lambda self: self.__velocity, _set_velocity)

class Hive():
	def __init__(self, pos):
		self.position = pos
		self.rect = Rect(self.position.x - 50, self.position.y - 50, 100, 100)
		self.bees = None
		self.honey = 0
		self.font = pygame.font.SysFont(None, 24)
		self.knownFood = {}
		self.combs = []

		self.combs.append(Honeycomb(0))
		#self.beesInside = 0

	def PopulateHive(self, game, beeAmount, maxBeeAmount = 1000):
		self.maxBeeAmount = maxBeeAmount
		beeAmount = beeAmount if maxBeeAmount >= beeAmount else maxBeeAmount
		self.bees = []
		for i in range(beeAmount):
			bee = Bee(self)
			bee.Hatch(game, True if i == beeAmount - 1 else False)
			bee.position = Vec2(self.rect.centerx, self.rect.centery)
			self.bees.append(bee)

	def Render(self, game):
		color = [255, 255, 255]
		if game.state == Game.DISPLAY_WORLD:
			pygame.draw.rect(game.screen, color, self.rect, 2)
			text = self.font.render(str(self.honey), True, [255,255,255])
			text_rect = text.get_rect()
			game.screen.blit(text, (self.position.x - text_rect.width / 2, self.position.y - text_rect.height / 2))
			for bee in self.bees:
				bee.Render(game)

		elif game.state == Game.DISPLAY_HIVE:
			for comb in self.combs:
				comb.Render(game)

		elif game.state == Game.DISPLAY_COMB:
			self.selectedComb.Render(game)

		elif game.state == Game.DISPLAY_CELL:
		 	self.selectedComb.selectedCell.Render(game)	

class Honeycomb():
	def __init__(self, index):
		self.index = index
		self.cells = []
		self.cellRow = 40
		self.cellColumn = 80
		self.cellAmount = self.cellRow * self.cellColumn
		self.larvaCellAmount = 0
		self.honeyCellAmount = 0
		self.BuildHoneycomb()

		screenSize = pygame.display.get_window_size()
		combProportion = 0.06
		combwidth = screenSize[0] * combProportion
		margin = screenSize[0] * (1 - (combProportion * 10)) / (10 + 1)
		self.rect = Rect(margin * (self.index + 1) + combwidth * self.index, 10 , combwidth, screenSize[1] - 10)
		#self.cellPolygons = 

	def Render(self, game):
		if game.state == Game.DISPLAY_HIVE:
			pygame.draw.rect(game.screen, [255,255,255], self.rect, 2)
		if game.state == Game.DISPLAY_COMB:
			for cell in self.cells:
				cell.Render(game)
		if game.state == Game.DISPLAY_CELL:
			self.selectedCell.Render(game)

	def BuildHoneycomb(self):	
		diameter = (pygame.display.get_window_size()[0] - 100)/ self.cellColumn
		for i in range(self.cellColumn):
			for j in range(self.cellRow):
				cell = Cell()
				if j % 2  == 0:
					cell.rect = Rect( 50 + i * diameter, 50 + j * 0.75 * diameter , diameter, diameter)
				else:
					cell.rect = Rect( 50 + i * diameter + diameter / 2, 50 + j * 0.75 * diameter, diameter, diameter)
				cell.index = Vec2(i, j)
				cell.diameter = diameter - 1
				self.cells.append(cell)				

class Cell():
	EMPTY_CELL = 0
	HONEY_CELL = 1
	LARVA_CELL = 2
	def __init__(self):
		self.position = Vec2()
		self.index = Vec2()
		self.rect = Rect(0,0,0,0)
		self.capacity = 100
		self.state = Cell.EMPTY_CELL
		self.color = [75, 45, 20]
		self.diameter = 0

	def Render(self, game):
		if game.state == Game.DISPLAY_COMB:
			pygame.draw.circle(game.screen, self.color, self.rect.center, self.diameter / 2 )
		elif game.state == Game.DISPLAY_CELL:
			text = game.font.render(f"{self.index.x}, {self.index.y}", True, [255,255,255])
			text_rect = text.get_rect()
			game.screen.blit(text, (self.rect.centerx - text_rect.width / 2, self.rect.centery - text_rect.height / 2))
		
class Flower():
	SPECIE_RED = 0
	SPECIE_GREEN = 1
	SPECIE_BLUE = 2

	def __init__(self, pos, specie = SPECIE_RED):
		self.position = pos
		self.collectCount = 50
		self.refillTime = 10
		self.size = 12
		self.specie = specie
		self.color = [0, 0, 0]
		self.color[self.specie] = 255
		self.isPollinated = False
		self.isDiscovered = True

	def Render(self, game):
		if self.isDiscovered:
			color = self.color if self.collectCount > 0 else [255, 255, 255]

			screenX = self.position.x
			screenY = self.position.y
			if game.drawMode == Game.DRAW_MODE_DEBUG:
				pass
			rect = Rect(self.position.x - self.size / 2, self.position.y - self.size / 2, self.size, self.size)
			pygame.draw.rect(game.screen, color, rect)
			pygame.draw.circle(game.screen, [255,255,0], [screenX,screenY], 2)
	
	def Pollinate(self, game):
		if not self.isPollinated:
			randomPos = self.position + Vec2(random.randint(-50, 50), random.randint(-50, 50))
			game.flowers.append(Flower(randomPos, self.specie))
			self.isPollinated = True

	@staticmethod
	def RandomlyLocate(game, amount):
		w,h = game.screen.get_size()
		ret = []
		for _ in range(amount):
			randSpecie = random.randint(0,2)
			randPosition = Vec2(random.randint(0,w), random.randint(0,h))
			ret.append(Flower(randPosition, randSpecie))
		return ret

class Game():
	DRAW_MODE_NORMAL = 0
	DRAW_MODE_DEBUG = 1

	DISPLAY_WORLD = 0
	DISPLAY_HIVE = 1
	DISPLAY_COMB = 2
	DISPLAY_CELL = 3

	DELTA_TIME = 0
	
	def __init__(self):
		self.hives = []
		self.flowers = []
		self.buttons = []

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
		self.clock = pygame.time.Clock()
		self.font = pygame.font.SysFont(None, 24)
		self.time = 0
		self.day = 1
		self.timeMultiplier = 1
		self.state = Game.DISPLAY_WORLD

		self.backButton = Button(Rect(100,100, 100,50), "Back")
		self.backButton.visible = False
		self.buttons.append(self.backButton)
		#self.flowers = Flower.RandomlyLocate(self, 100)


	def UpdateDisplay(self):
		if self.drawMode == Game.DRAW_MODE_DEBUG:
			colorScreen = (0,0,255)
		else:
			colorScreen = (0,0,0)
		self.screen.fill(colorScreen)

		if self.hives != None:
			for hive in self.hives:
				hive.Render(self)

		if self.state == Game.DISPLAY_WORLD:
			if len(self.flowers) > 0:
				for flower in self.flowers:
					flower.Render(self)

		for button in self.buttons:
			button.Render(self)

		self.clock.tick(30)

		t = pygame.time.get_ticks()
		oldTime = self.time
		self.time = int((self.timeMultiplier * t) // 2000 + 5) % 24
		if oldTime - self.time == 23:
			self.day += 1
		
		Game.DELTA_TIME =  (t - self._getTicksLastFrame) /  1000.0
		self._getTicksLastFrame = t
		
		self.Display_stats()

		
		pygame.display.flip()	
    
	def Update(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT or (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE):
				self.isRunning = False

			if event.type == pygame.MOUSEBUTTONDOWN:
				pos = event.pos
				button = event.button
				if button == 1:
					#if any([btn.rect.collidepoint(pos[0], pos[1]) for btn in self.buttons]):
					if self.state == Game.DISPLAY_WORLD:
						for hive in self.hives:
							if hive.rect.collidepoint(pos[0], pos[1]):
								self.selectedHive = hive
								self.state = Game.DISPLAY_HIVE
								self.backButton.visible = True
					elif self.state == Game.DISPLAY_HIVE:
						if self.backButton.rect.collidepoint(pos[0], pos[1]):
							self.state = Game.DISPLAY_WORLD
							self.selectedHive = None
							self.backButton.visible = False
						else:
							for comb in self.selectedHive.combs:
								if comb.rect.collidepoint(pos[0], pos[1]):
									self.selectedHive.selectedComb = comb
									self.state = Game.DISPLAY_COMB
					elif self.state == Game.DISPLAY_COMB:
						if self.backButton.rect.collidepoint(pos[0], pos[1]):
							self.state = Game.DISPLAY_HIVE
							self.selectedHive.selectedComb = None
						else:
							for cell in self.selectedHive.selectedComb.cells:
								if cell.rect.collidepoint(pos[0], pos[1]):
									self.selectedHive.selectedComb.selectedCell = cell
									self.state = Game.DISPLAY_CELL
					elif self.state == Game.DISPLAY_CELL:
						if self.backButton.rect.collidepoint(pos[0], pos[1]):
							self.state = Game.DISPLAY_COMB
							self.selectedHive.selectedComb.selectedCell = None

				if button > 1 and button < 4 and self.state == Game.DISPLAY_WORLD:
					self.flowers.append(Flower(Vec2(pos[0], pos[1]), button - 1))
			
			if event.type == pygame.MOUSEWHEEL:

				self.timeMultiplier += event.y * 0.05
				self.timeMultiplier 

		for hive in self.hives:
			for bee in hive.bees:
				bee.Update(self)

		self.UpdateDisplay()

	def Display_stats(self):
		text = self.font.render(f"Fps: {int(self.clock.get_fps())}", True, [255,255,255])
		self.screen.blit(text, (10, 10))
		text = self.font.render(str(f"Time: {self.time:02}.00"), True, [255,255,255])
		self.screen.blit(text, (110, 10))
		text = self.font.render(str(f"Day: {self.day}"), True, [255,255,255])
		self.screen.blit(text, (210, 10))
		text = self.font.render(str(f"Speed: {self.timeMultiplier:.2f}X"), True, [255,255,255])
		self.screen.blit(text, (310, 10))

	def Shutdown(self):
		pygame.quit()

class Button():
	def __init__(self, rect, text = "") -> None:
		self.rect = rect
		self.text = text
		self.visible = True
		self.command = None
	
	def Render(self, game):
		if self.visible:
			pygame.draw.rect(game.screen, [50,50,50], self.rect, border_radius = 5)
			text = game.font.render(self.text, True, [255,255,255])
			text_rect = text.get_rect()
			game.screen.blit(text, (self.rect.centerx - text_rect.width / 2, self.rect.centery - text_rect.height / 2))

def main():
	game = Game()
	game.Start("BeeMulator", is_fullscreen = True, draw_mode= Game.DRAW_MODE_NORMAL)

	game.hives = []
	for i in range(1):
		hive = Hive(Vec2(640 * (i + 1), 500))
		
		hive.PopulateHive(game, 100)
		game.hives.append(hive)


	while game.isRunning:
		game.Update()

	game.Shutdown()

if __name__ == "__main__":
	main()