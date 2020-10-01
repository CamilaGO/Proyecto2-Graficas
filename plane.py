from lib import *
from rayUtils import *

class Plane(object):
  def __init__(self, position, normal, material):
    self.position = position
    self.normal = norm(normal)
    self.material = material

  def ray_intersect(self, orig, dir):
    denom = dot(dir, self.normal)

    if abs(denom) > 0.0001:
      t = dot(self.normal, sub(self.position, orig)) / denom
      if t > 0:
        hit = sum(orig, mul(dir, t))

        return Intersect(distance = t,
                         point = hit,
                         normal = self.normal)

    return None