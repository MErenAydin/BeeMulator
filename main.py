
import argparse
import pygame
from pygame.locals import *
from vector import Vec2
from collections import deque as queue
from bee import Bee
from enums import *

import random

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
			bee.Hatch(game)
			bee.position = Vec2(self.rect.centerx, self.rect.centery)
			self.bees.append(bee)

	def DepositNectar(self, nectarAmount):
		if nectarAmount > 0:
			for comb in self.combs:
				if comb.usage < 0.6:
					comb.DepositNectar(nectarAmount)
					break
		# implement distribution logic

	def Render(self, game):
		color = [255, 255, 255]
		if game.state == DisplayState.DISPLAY_WORLD:
			pygame.draw.rect(game.screen, color, self.rect, 2)
			text = self.font.render(str(self.honey), True, [255,255,255])
			text_rect = text.get_rect()
			game.screen.blit(text, (self.position.x - text_rect.width / 2, self.position.y - text_rect.height / 2))
			for bee in self.bees:
				bee.Render(game)
		
		elif game.selectedHive == self:

			if game.state == DisplayState.DISPLAY_HIVE:
				for comb in self.combs:
					comb.Render(game)

			elif game.state == DisplayState.DISPLAY_COMB:
				self.selectedComb.Render(game)

			elif game.state == DisplayState.DISPLAY_CELL:
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
		self.usage = 0
		self.BuildHoneycomb()

		screenSize = pygame.display.get_window_size()
		combProportion = 0.06
		combwidth = screenSize[0] * combProportion
		margin = screenSize[0] * (1 - (combProportion * 10)) / (10 + 1)
		self.rect = Rect(margin * (self.index + 1) + combwidth * self.index, 10 , combwidth, screenSize[1] - 10)
		#self.cellPolygons = 

	def DepositNectar(self, nectarAmount):
		if self.honeyCellAmount == 0:
			self.baseCol = random.randint(25,55)
			self.baseRow = random.randint(10,20)
			cell = self.cells[self.cellColumn * (self.baseRow - 1) + self.baseCol]
			self.honeyCellAmount += 1
		
		else:
			cell = self.BFS(self.baseCol, self.baseRow, True)
			if cell is not None and cell.state != CellType.HONEY_CELL:
				self.honeyCellAmount += 1

		if cell is not None:
			cell.state = CellType.HONEY_CELL
			cell.nectar += nectarAmount
		
	
	def isValid(self, vis, row, col):
		if (row < 0 or col < 0 or row >= self.cellRow or col >= self.cellColumn):
			return False
		if (vis[row][col]):
			return False
		return True
	
	def BFS(self, col, row, isHoney):
		visited = [[ False for i in range(self.cellColumn)] for i in range(self.cellRow)]
		dRow = [ -1, 0, 1, 0]
		dCol = [ 0, 1, 0, -1]

		q = queue()
		q.append(( row, col , None))
		visited[row][col] = True
	
		while (len(q) > 0):
			node = q.popleft()
			x = node[0]
			y = node[1]
			last = node[2]
			cell = self.cells[(x - 1) * self.cellColumn + y]
			if cell.state == CellType.HONEY_CELL:
				if last is not None and isHoney:
					#if cell.nectar < last.nectar:
					#	return cell
					if cell.nectar >= last.nectar and last.nectar <= last.capacity - 10:
						return last
			if cell.state == CellType.EMPTY_CELL:
				return cell
			for i in range(4):
				adjx = x + dRow[i]
				adjy = y + dCol[i]
				if (self.isValid(visited, adjx, adjy)):
					q.append((adjx, adjy, cell))
					visited[adjx][adjy] = True
	
	def Render(self, game):
		if game.state == DisplayState.DISPLAY_HIVE:
			pygame.draw.rect(game.screen, [255,255,255], self.rect, 2)
		if game.state == DisplayState.DISPLAY_COMB:
			for cell in self.cells:
				cell.Render(game)
		if game.state == DisplayState.DISPLAY_CELL:
			self.selectedCell.Render(game)

	def BuildHoneycomb(self):	
		diameter = (pygame.display.get_window_size()[0] - 100)/ self.cellColumn
		for i in range(self.cellRow):
			for j in range(self.cellColumn):
				cell = Cell()
				if i % 2  == 0:
					cell.rect = Rect( 50 + j * diameter, 50 + i * 0.75 * diameter , diameter, diameter)
				else:
					cell.rect = Rect( 50 + j * diameter + diameter / 2, 50 + i * 0.75 * diameter, diameter, diameter)
				cell.index = Vec2(j, i)
				cell.diameter = diameter - 1
				self.cells.append(cell)

class Cell():
	def __init__(self):
		self.position = Vec2()
		self.index = Vec2()
		self.rect = Rect(0,0,0,0)
		self.capacity = 100
		self.nectar = 0
		self.__state = CellType.EMPTY_CELL
		self.color = [75, 45, 20]
		self.diameter = 0

	def Render(self, game):
		if game.state == DisplayState.DISPLAY_COMB:
			pygame.draw.circle(game.screen, self.color, self.rect.center, self.diameter / 2 )
		elif game.state == DisplayState.DISPLAY_CELL:
			size = game.screen.get_size()
			proportionX = 0.35
			rect = Rect(size[0] * proportionX, 100, size[0] * proportionX, size[1] - 200)
			pygame.draw.rect(game.screen, [255, 255, 255], rect, 5)
			if self.state == CellType.HONEY_CELL:
				fill_amount = self.nectar / self.capacity
				fill_rect = Rect(	rect.left + 5,
									rect.top + rect.height - (rect.height * fill_amount),
									rect.width - 10,
									rect.height * fill_amount - 5)
				pygame.draw.rect(game.screen, [255, 255, 0], fill_rect, 0)
			elif self.state == CellType.LARVA_CELL:
				#TODO: proportion will be arranged to growing
				fill_amount = 0.5
				fill_rect = Rect(	rect.left + rect.width / 2 - (rect.width * fill_amount) / 2 + 5,
									rect.top + rect.height - (rect.height * fill_amount) + 5,
									rect.width * fill_amount - 10,
									rect.height * fill_amount - 10)
				pygame.draw.ellipse(game.screen, [255, 255, 255], fill_rect)
			#text = game.font.render(f"{self.index.x}, {self.index.y}\n{self.nectar}", True, [255,255,255])
			#text_rect = text.get_rect()
			#game.screen.blit(text, (self.rect.centerx - text_rect.width / 2, self.rect.centery - text_rect.height / 2))
		
	def _set_state (self, value):
		self.__state = value
		if value == CellType.LARVA_CELL:
			self.color = [140, 75, 30]
		elif value == CellType.HONEY_CELL:
			self.color = [200, 200, 0]
		else:
			self.color = [75, 45, 20]
	state = property(lambda self: self.__state, _set_state)

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
			randPosition = self.position + Vec2(random.randint(-50, 50), random.randint(-50, 50))
			while any([hive.rect.inflate(10, 10).collidepoint(randPosition.x, randPosition.y) for hive in game.hives]):
				randPosition = self.position + Vec2(random.randint(-50, 50), random.randint(-50, 50))
			game.flowers.append(Flower(randPosition, self.specie))
			self.isPollinated = True

	@staticmethod
	def RandomlyLocate(game, amount):
		w,h = game.screen.get_size()
		ret = []
		for _ in range(amount):
			randSpecie = random.randint(0,2)
			randPosition = Vec2(random.randint(10, w - 10), random.randint(10, h - 10))
			while any([hive.rect.inflate(10, 10).collidepoint(randPosition.x, randPosition.y) for hive in game.hives]):
				randPosition = Vec2(random.randint(10, w - 10), random.randint(10, h - 10))
			ret.append(Flower(randPosition, randSpecie))
		return ret

class Game():
	DRAW_MODE_NORMAL = 0
	DRAW_MODE_DEBUG = 1
	
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
		self.state = DisplayState.DISPLAY_WORLD
		self.deltaTime = 0

		self.backButton = Button(Rect(100,100, 100,50), "Back")
		self.addButton = Button(Rect(self.screen.get_size()[0] - 200, 100, 100,50), "Add")
		self.removeButton = Button(Rect(self.screen.get_size()[0] - 350, 100, 100,50), "Remove")
		self.backButton.visible = False
		self.addButton.visible = False
		self.removeButton.visible = False
		self.buttons.append(self.backButton)
		self.buttons.append(self.addButton)
		self.buttons.append(self.removeButton)

	def UpdateDisplay(self):
		if self.drawMode == Game.DRAW_MODE_DEBUG:
			colorScreen = (0,0,255)
		else:
			colorScreen = (0,0,0)
		self.screen.fill(colorScreen)
		
		if self.hives != None:
			for hive in self.hives:
				hive.Render(self)

		if self.state == DisplayState.DISPLAY_WORLD:
			if len(self.flowers) > 0:
				for flower in self.flowers:
					flower.Render(self)

		for button in self.buttons:
			button.Render(self)

		self.clock.tick()

		t = pygame.time.get_ticks()
		oldTime = self.time
		self.time = int((self.timeMultiplier * t) // 2000 + 5) % 24
		if oldTime - self.time == 23:
			self.day += 1
		
		self.deltaTime =  (t - self._getTicksLastFrame) /  1000.0
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
					if self.state == DisplayState.DISPLAY_WORLD:
						for hive in self.hives:
							if hive.rect.collidepoint(pos[0], pos[1]):
								self.selectedHive = hive
								self.state = DisplayState.DISPLAY_HIVE
								self.backButton.visible = True
								if len(self.selectedHive.combs) > 1:
									self.removeButton.visible = True
								if len(self.selectedHive.combs) < 10:
									self.addButton.visible = True
					elif self.state == DisplayState.DISPLAY_HIVE:
						if self.addButton.visible and self.addButton.rect.collidepoint(pos[0], pos[1]):
							self.addButton.visible = True
							if len(self.selectedHive.combs) == 9:
								self.addButton.visible = False
							if len(self.selectedHive.combs) < 10:
								self.selectedHive.combs.append(Honeycomb(len(self.selectedHive.combs)))
								if len(self.selectedHive.combs) > 1:
									self.removeButton.visible = True
								break
								
						if self.removeButton.visible and self.removeButton.rect.collidepoint(pos[0], pos[1]):
							self.addButton.visible = True
							if len(self.selectedHive.combs) == 2:
								self.removeButton.visible = False
							if len(self.selectedHive.combs) > 1:
								self.selectedHive.combs.pop()
								break
						if self.backButton.visible and self.backButton.rect.collidepoint(pos[0], pos[1]):
							self.state = DisplayState.DISPLAY_WORLD
							self.selectedHive = None
							self.backButton.visible = False
							self.addButton.visible = False
							self.removeButton.visible = False
						else:
							for comb in self.selectedHive.combs:
								if comb.rect.collidepoint(pos[0], pos[1]):
									self.selectedHive.selectedComb = comb
									self.state = DisplayState.DISPLAY_COMB
									self.addButton.visible = False
									self.removeButton.visible = False
					elif self.state == DisplayState.DISPLAY_COMB:
						if self.backButton.rect.collidepoint(pos[0], pos[1]):
							self.state = DisplayState.DISPLAY_HIVE
							self.selectedHive.selectedComb = None
							if len(self.selectedHive.combs) > 1:
								self.removeButton.visible = True
							if len(self.selectedHive.combs) < 10:
								self.addButton.visible = True
						else:
							for cell in self.selectedHive.selectedComb.cells:
								if cell.rect.collidepoint(pos[0], pos[1]):
									self.selectedHive.selectedComb.selectedCell = cell
									self.state = DisplayState.DISPLAY_CELL
					elif self.state == DisplayState.DISPLAY_CELL:
						if self.backButton.rect.collidepoint(pos[0], pos[1]):
							self.state = DisplayState.DISPLAY_COMB
							self.selectedHive.selectedComb.selectedCell = None

				if button > 1 and button < 4 and self.state == DisplayState.DISPLAY_WORLD:
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
	ap = argparse.ArgumentParser()
	ap.add_argument("-b", "--bees", type=int, default=100, help='Number of the bees in each hive')
	ap.add_argument("-H", "--hives", type=int, default=1, help='Number of the hives in simulation')
	args = vars(ap.parse_args())

	game = Game()
	game.Start("BeeMulator", is_fullscreen = False, draw_mode= Game.DRAW_MODE_NORMAL)

	game.hives = []
	screenSize = game.screen.get_size()
	rows = ((args["hives"] * 150 // screenSize[0])) + 1
	cols = screenSize[0] //  150
	for i in range(cols) if args["hives"] > cols else range(args["hives"]):
		for j in range(rows):
			if args["hives"] > cols:
				xPos = screenSize[0] / cols * (i + 1) - 75
			else:
				xPos = screenSize[0] / (args["hives"] + 1) * (i + 1)
			yPos = screenSize[1] - 150 * (j + 1) + 75
			hive = Hive(Vec2(xPos, yPos))
			
			hive.PopulateHive(game, args["bees"])
			game.hives.append(hive)

	game.flowers = Flower.RandomlyLocate(game, 100)

	while game.isRunning:
		game.Update()

	game.Shutdown()

if __name__ == "__main__":
	main()