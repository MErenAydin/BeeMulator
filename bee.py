import random
from enums import BeeState, DisplayState, LarvaType, CellType
from vector import Vec2
import pygame
import copy

class Bee():

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

	def Hatch(self, game):
		if game.drawMode == game.DRAW_MODE_NORMAL:
			self.trace = None
		self.lastFlowercollectCount = 0
		self.bornday = game.day
		self.state = BeeState.WANDERING
		self.lifespan = 35
		self.deathHour = random.randint(0,23)
		self.nectar = 0
		self.capacity = 10
		self.collectedFlowers = []

	def Kill(self, game):
		if game.time == self.deathHour:
			self.hive.bees.remove(self) 

	def Render(self, game):
		# if self.isQueen:
		# 	size = 4
		# 	color = [100, 100, 0]
		# else:
		size = 2
		color = [255, 255, 0]
		screenX = self.position.x
		screenY = self.position.y
		if game.drawMode == game.DRAW_MODE_DEBUG:
			pygame.draw.circle(game.screen, [255,0,0], [screenX,screenY], self.visionRange , 1)
			for t in self.trace:
				pygame.draw.circle(game.screen, [155, 155, 0], [t.x,t.y], 1)
		pygame.draw.circle(game.screen, color, [screenX,screenY], size)

	def Move(self,game):
		if self.state == BeeState.WANDERING:
			if game.time < 5 or game.time > 19:
				self.state = BeeState.RETURNING
			if self.hive.rect.collidepoint(self.position.x, self.position.y):
				if len(self.hive.knownFood) > 0:
					randomFood = random.sample( self.hive.knownFood.items(), 1)[0]
					if  self.hive.knownFood[randomFood[0]] > 0:
						self.state = BeeState.TO_FOOD
						self.attachedFlower = randomFood[0]
			

			flower, _ = self.ClosestFlower(game)
			if flower is not None:
				self.state = BeeState.TO_FOOD
				self.attachedFlower = flower
				self.direction = (flower.position - self.position).normalized()
			else:
				self.direction = (self.direction + Vec2(random.random() * 2 - 1, random.random() * 2 - 1) * self.wanderStrength).normalized()

		elif self.state == BeeState.TO_FOOD:
			if game.time < 5 or game.time > 19:
				self.state = BeeState.RETURNING
			else:
				self.direction = (self.attachedFlower.position - self.position).normalized()
				if (self.attachedFlower.position - self.position).magnitude < self.attachedFlower.size:
					self.state = BeeState.COLLECTING
					self.attachTime = pygame.time.get_ticks()

		elif self.state == BeeState.COLLECTING:
			if self.attachedFlower.collectCount <= 0:
				self.state = BeeState.WANDERING
				return
			delta = (pygame.time.get_ticks() - self.attachTime) / 1000
			if delta > self.collectingTime:
				self.attachedFlower.collectCount -= 1
				self.nectar += 1
				self.lastFlowercollectCount = self.attachedFlower.collectCount
				self.collectedFlowers.append(self.attachedFlower)
				rand = random.random()
				treshold = 0.95 if self.attachedFlower.specie in [specie for specie in self.collectedFlowers] else 0.99
				if rand > treshold:
					self.attachedFlower.Pollinate(game)
				self.state = BeeState.RETURNING if self.nectar >= self.capacity else BeeState.WANDERING

		elif self.state == BeeState.RETURNING:
			self.direction = (self.hive.position - self.position).normalized()
			if self.hive.rect.collidepoint(self.position.x, self.position.y):
				self.state = BeeState.DEPOSIT
				self.attachTime = pygame.time.get_ticks()

		elif self.state == BeeState.DEPOSIT:
			delta = (pygame.time.get_ticks() - self.attachTime) / 1000
			if delta > self.collectingTime:
				self.hive.honey += self.nectar
				self.hive.DepositNectar(self.nectar)
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
							self.state = BeeState.TO_FOOD
						else: 
							self.state = BeeState.WANDERING
					else:
						self.state = BeeState.WANDERING
				else:
					self.state = BeeState.SLEEP
		
		elif self.state == BeeState.SLEEP:
			if game.time >= 5 and game.time <= 19:
				if len(self.hive.knownFood) > 0:
					randomFood = random.sample( self.hive.knownFood.items(), 1 )[0]
					if  self.hive.knownFood[randomFood[0]] > 0:
						self.attachedFlower = randomFood[0]
						self.state = BeeState.TO_FOOD
					else: 
						self.state = BeeState.WANDERING

		else:
			pass
		
		screenSize = game.screen.get_size()
		if self.state == BeeState.WANDERING or self.state == BeeState.RETURNING or self.state == BeeState.TO_FOOD:
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
			self.velocity = Vec2.clamp_magnitude((self.velocity + acceleration * game.deltaTime), self.maxSpeed)
			self.position += self.velocity * game.deltaTime
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

class Larva():
	def __init__(self, game, eggType):
		self.eggType = eggType
		self.layingDay = game.day
		self.lastFed = game.day
		self.hatchingDay = self.layingDay + 21 if self.eggType == LarvaType.FEMALE_LARVA else self.layingDay + 24 if self.eggType == LarvaType.MALE_LARVA else self.layingDay + 16
		
	def Render(self, game):
		if game.state == DisplayState.DISPLAY_CELL:
			pass

class Queen(Bee):
	def __init__(self, hive, position = None):
		super.__init__(hive, position)
		self.EggLayingCapacity = 100
		self.isMated = False
		#"self.

	def Move(self, game):
		# totally different movement
		return super().Move(game)

	def LayEgg(self, game, cell):
		cell.state = CellType.LARVA_CELL
		cell.larva = Larva(game, LarvaType.FEMALE_LARVA if self.isMated else LarvaType.MALE_LARVA)
