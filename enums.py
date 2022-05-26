from enum import Enum

class BeeState(Enum):
    # Moving states
	WANDERING = 0
	TO_FOOD = 1
	COLLECTING = 2
	RETURNING = 3
	DEPOSIT = 4
	SLEEP = 5

class BeeLifeState(Enum):
	# Lifecycle states
	LARVA = 0
	FEEDER = 1
	BUILDER = 2
	SCOUT = 3
	COLLECTER = 4

class LarvaType(Enum):
    FEMALE_LARVA = 0
    MALE_LARVA = 1
    QUEEN_LARVA = 2

class CellType(Enum):
	EMPTY_CELL = 0
	HONEY_CELL = 1
	LARVA_CELL = 2

class FlowerSpecies(Enum):
    SPECIE_RED = 0
    SPECIE_GREEN = 1
    SPECIE_BLUE = 2

class DisplayState(Enum):
    DISPLAY_WORLD = 0
    DISPLAY_HIVE = 1
    DISPLAY_COMB = 2
    DISPLAY_CELL = 3