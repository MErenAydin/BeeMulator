
class Vec2():
	def __init__(self, x = 0.0, y = 0.0):
		self.__x = x
		self.__y = y
		self.magnitude = self.get_magnitude()
	
	def normalized(self):
		if self.magnitude > 0:
			return Vec2(self.x / self.magnitude, self.y / self.magnitude)
		else:
			return Vec2()

	def get_magnitude(self):
		return (self.__x ** 2 + self.__y ** 2) ** 0.5

	@staticmethod
	def clamp_magnitude(vector, clamp):
		mag = vector.magnitude
		if mag > 0:
			return Vec2(vector.x * clamp / mag, vector.y * clamp / mag)
		else:
			return Vec2()

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

	def set_x(self, value):
		self.__x = value
		self.magnitude = self.get_magnitude()
	
	def set_y(self, value):
		self.__y = value
		self.magnitude = self.get_magnitude()

	x = property(lambda self: self.__x, set_x)
	y = property(lambda self: self.__y, set_y)
