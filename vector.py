import numpy as np
import math
class Vec2():
	def __init__(self, x = 0.0, y = 0.0):
		self.__x = x
		self.__y = y
		self.__magnitude = 0
		self.__magnitudeChanged = True
	
	def normalized(self):
		if self.magnitude > 0:
			return Vec2(self.x / self.magnitude, self.y / self.magnitude)
		else:
			return Vec2()
	
	def get_magnitude2(self):
		return self.x * self.x + self.y * self.y

	@staticmethod
	def clamp_magnitude(vector, clamp):
		mag = vector.magnitude
		if mag > clamp and mag > 0:
			return Vec2(vector.x * clamp / mag, vector.y * clamp / mag)
		else:
			return vector

	def __add__(self, other):
		ret = Vec2()
		ret.x = self.x + other.x
		ret.y = self.y + other.y
		return ret
	def __sub__(self, other):
		ret = Vec2()
		ret.x = self.x - other.x
		ret.y = self.y - other.y
		return ret

	def __iadd__(self, other):
		self.x += other.x
		self.y += other.y
		return self

	def __isub__(self, other):
		self.x -= other.x
		self.y -= other.y
		return self

	def __mul__(self, other):
		if isinstance(other, Vec2):
			self.x *= other.x
			self.y *= other.y
		else:
			self.x *= other
			self.y *= other
		return self

	def _set_x(self, value):
		self.__x = value
		self.__magnitudeChanged = True
	
	def _set_y(self, value):
		self.__y = value
		self.__magnitudeChanged = True

	def _get_magnitude(self):
		if self.__magnitudeChanged:
			self.__magnitude = math.sqrt(self.x * self.x + self.y * self.y)
			self.__magnitudeChanged = False
		return self.__magnitude

	x = property(lambda self: self.__x, _set_x)
	y = property(lambda self: self.__y, _set_y)
	magnitude = property(_get_magnitude, lambda self: None)
