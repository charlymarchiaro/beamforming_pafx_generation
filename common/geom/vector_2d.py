import math


class Vector2d:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def get_norm(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def get_argument_rad(self):
        return math.atan2(self.y, self.x)


def scalar_prod(k: float, v: Vector2d) -> Vector2d:
    return Vector2d(k * v.x, k * v.y)


def dot_prod(v1: Vector2d, v2: Vector2d) -> float:
    return v1.x * v2.x + v1.y * v2.y


def add(v1: Vector2d, v2: Vector2d) -> Vector2d:
    return Vector2d(v1.x + v2.x, v1.y + v2.y)
