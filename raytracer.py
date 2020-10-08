from lib import *
from rayUtils import *
from sphere import *
from plane import *
from cube import *
from pyramid import *
from envmap import *
from math import pi, tan

BLACK = color(0, 0, 0)
WHITE = color(255, 255, 255)
FONDO = color(50, 50, 200)
MAX_RECURSION_DEPTH = 3


class Raytracer(object):
  def __init__(self, width, height):
    self.width = width
    self.height = height
    self.background_color = BLACK
    self.light = None
    self.scene = []
    self.envMap = None
    self.clear()

  def clear(self):
    self.pixels = [
      [self.background_color for x in range(self.width)]
      for y in range(self.height)
    ]

  def write(self, filename):
    writebmp(filename, self.width, self.height, self.pixels)

  def display(self, filename='outtri.bmp'):
    self.render()
    self.write(filename)

  def point(self, x, y, c = None):
    try:
      self.pixels[y][x] = c or self.current_color
    except:
      pass

  def scene_intersect(self, orig, direction):
    zbuffer = float('inf')

    material = None
    intersect = None

    for obj in self.scene:
      hit = obj.ray_intersect(orig, direction)
      if hit is not None:
        if hit.distance < zbuffer:
          zbuffer = hit.distance
          material = obj.material
          intersect = hit

    return material, intersect

  def cast_ray(self, orig, direction, recursion = 0):
    material, intersect = self.scene_intersect(orig, direction)

    if material is None or recursion >= MAX_RECURSION_DEPTH:  # break recursion of reflections after n iterations
      if self.envMap:
        #si hay imagen bitmap de background se obtiene el color
        return self.envMap.get_color(direction)
      return self.background_color

    offset_normal = mul(intersect.normal, 1.1)

    if material.albedo[2] > 0:
      reverse_direction = mul(direction, -1)
      reflect_dir = reflect(reverse_direction, intersect.normal)
      reflect_orig = sub(intersect.point, offset_normal) if dot(reflect_dir, intersect.normal) < 0 else sum(intersect.point, offset_normal)
      reflect_color = self.cast_ray(reflect_orig, reflect_dir, recursion + 1)
    else:
      reflect_color = color(0, 0, 0)

    if material.albedo[3] > 0:
      refract_dir = refract(direction, intersect.normal, material.refractive_index)
      refract_orig = sub(intersect.point, offset_normal) if dot(refract_dir, intersect.normal) < 0 else sum(intersect.point, offset_normal)
      refract_color = self.cast_ray(refract_orig, refract_dir, recursion + 1)
    else:
      refract_color = color(0, 0, 0)

    light_dir = norm(sub(self.light.position, intersect.point))
    light_distance = length(sub(self.light.position, intersect.point))

    shadow_orig = sub(intersect.point, offset_normal) if dot(light_dir, intersect.normal) < 0 else sum(intersect.point, offset_normal)
    shadow_material, shadow_intersect = self.scene_intersect(shadow_orig, light_dir)
    shadow_intensity = 0

    if shadow_material and length(sub(shadow_intersect.point, shadow_orig)) < light_distance:
        shadow_intensity = 0.9

    intensity = self.light.intensity * max(0, dot(light_dir, intersect.normal)) * (1 - shadow_intensity)

    reflection = reflect(light_dir, intersect.normal)
    specular_intensity = self.light.intensity * (
      max(0, -dot(reflection, direction))**material.spec
    )

    diffuse = material.diffuse * intensity * material.albedo[0]
    specular = color(255, 255, 255) * specular_intensity * material.albedo[1]
    reflection = reflect_color * material.albedo[2]
    refraction = refract_color * material.albedo[3]

    return diffuse + specular + reflection + refraction

  """def cast_ray(self, orig, direction, sphere):
    if sphere.ray_intersect(orig, direction):
      return color(255, 0, 0)
    else:
      return color(0, 0, 255)"""

  def render(self):
    alfa = int(pi/2)
    for y in range(self.height):
      for x in range(self.width):
        i =  (2*(x + 0.5)/self.width - 1)*self.width/self.height*tan(alfa/2)
        j =  (2*(y + 0.5)/self.height - 1 )*tan(alfa/2)
        # x = int(x)
        # y = int(y)
        # print(x, y)
        direction = norm(V3(i, j, -1))
        self.pixels[y][x] = self.cast_ray(V3(0,0,0), direction)

  """def basicRender(self):
  #Esto llena la pantalla de colores degradado
    for x in range(self.width):
      for y in range(self.height):
        r = int((x/self.width)*255) if x/self.width < 1 else 1
        g = int((y/self.height)*255) if y/self.height < 1 else 1
        b = 0
        self.pixels[y][x] = color(r, g, b)"""


r = Raytracer(1920, 1080)
#r = Raytracer(1200, 900)
r.envMap = Envmap('bosque.bmp')
r.light = Light(
  position=V3(0, 0, 20),
  intensity=1.5
)

#r.background_color = FONDO

r.scene = [
  #Sphere(V3(0, 0, -10), 1.5, ivory),
  #puente
  #Cube(V3(4, -4, -10), 3, coffee),
  #Cube(V3(0, -2, -10), 2.5, coffee),
  #Cube(V3(0, 0, -10), 2, coffee),
  Cube(V3(3.5, -2, -12), 4, gray),
  Sphere(V3(2.3, -1, -9 ), 0.5, mirror),
  Sphere(V3(4, -1, -9 ), 0.5, mirror),
  Pyramid([V3(2, 0, -10), V3(1.5, 2, -5), V3(5.5, 0, -10), V3(1, 0, -7.5)], graylight)
  #Cube(V3(0, 2, -10), 1.7, coffee),
  #MONTANIAS derecha frente - punta - izquierda frente - derecha atras
  #Pyramid([V3(0, 1, -10), V3(-2.5, 3.5, -5), V3(-10, 1, -10), V3(-2, 1, -7.5)], gray),
  #Pyramid([V3(4.5, 1.5, -10), V3(3.5, 4, -5), V3(12, 2, -10), V3(3, 1.5, -7.5)], gray)
]
"""r.scene = [
  Sphere(V3(0, -1.5, -10), 1.5, ivory),
  Sphere(V3(0, 0, -5), 0.5, glass),
  Sphere(V3(1, 1, -8), 1.7, rubber),
  Sphere(V3(-3, 3, -10), 2, mirror),
  Plane(-2, rubber),
]
Pyramid([(1, -2, -10), (-1, 2, -5), (-5, -2, -10), (-0.0, -1, -7.5)
"""
r.display()