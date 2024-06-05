import pygame, sys, random
from pygame.locals import QUIT
from PIL import Image, ImageOps
import numpy as np
import math as maths
import random

pygame.init()
scale = 720/1080
DISPLAYSURF = pygame.display.set_mode((1920 * scale, 1080 * scale))
player_screen_offset = np.array((1920,1080))/2
pygame.display.set_caption('Hello World!')
framerate = 60
frame_time = 1/framerate
clock = pygame.time.Clock()

ENEMY_SPAWN_RADIUS = 2000

def vector_magnitude(vector):
  try:
    sum = (vector[0]**2)+(vector[1]**2)
    return np.sqrt(sum)
  except:
    return 0

class backgroundClass:
  def __init__(self):
    background_PIL = Image.open("Images/background.png")
    self.image_size = np.array(background_PIL.size)
    self.scaled_image_size = np.trunc(self.image_size*scale)
    self.width = int(self.scaled_image_size[0])
    self.height = int(self.scaled_image_size[1])
    background_PIL = ImageOps.fit(background_PIL, (self.width,self.height)).save("converted_background.png")
    print(background_PIL)
    self.background_image = pygame.image.load("converted_background.png")
  def draw(self):
    player_pos = player.get_position()
    # converts the player coordinates to snap coordinates for the map image
    player_grid_pos = np.trunc(player_pos/self.image_size)
    if player_pos[0] < 0:
      player_grid_pos[0] -= 1
    if player_pos[1] < 0:
      player_grid_pos[1] -= 1  
    # blits map images in a 3x3 grid where the player is in the centre tile
    for x in range(-1,2):
      for y in range(-1,2):
        offset = np.array((x,y))
        DISPLAYSURF.blit(self.background_image, (((player_grid_pos+offset))*self.scaled_image_size-(player_screen_offset*scale)))

background = backgroundClass()
# Entity class is used for players, enemies and projectiles and anything else that can collide with other entities or move around the screen

class entity:
  def __init__(self, radius, position, max_speed, colour):
    self.position = np.array(position)
    self.radius = radius
    self.velocity = np.array([0,0])
    self.direction = np.array((0,0))
    self.max_speed = max_speed
    self.colour = colour
  def set_position(self, new_position):
    self.position = np.array(new_position)
  def get_position(self):
    return self.position
  def set_direction(self, velocity):
    self.direction = np.array(velocity)
    self.calculate_velocity()
  def set_x_direction(self, x_velocity):
    self.direction[0] = x_velocity
    self.calculate_velocity()
  def set_y_direction(self, y_velocity):
    self.direction[1] = y_velocity
    self.calculate_velocity()
  def calculate_velocity(self):
    if vector_magnitude(self.direction) == 0:
      self.velocity = np.array((0,0))
    else:
      k = self.max_speed/vector_magnitude(self.direction)
      self.velocity = self.direction*k
  def move(self):
    self.position = self.position+self.velocity*frame_time
  def draw(self):
    # this will draw any entities onto the screen. currently defined as a coloured circle
    self.move()
    pygame.draw.circle(DISPLAYSURF,self.colour,(self.position-player_screen_offset)*scale,int(self.radius*scale))
  def is_touching(self,other_entity,other_coords = False):
    if type(other_coords) == np.ndarray:
      tested_position = other_coords
    else:
      tested_position = self.position
    if isinstance(other_entity, entity):
      print(tested_position)
      print(other_entity.get_position())
      vect_diff = tested_position-other_entity.get_position()
      collide_dist = self.radius+other_entity.radius
      if vector_magnitude(vect_diff) < collide_dist:
        return True
    return False


# player specific code such as weapons, exp and health will stay in this class
class playerClass(entity):
  def __init__(self, radius, position):
    super().__init__(radius, position, 500, (0,0,255))
  def move(self):
    global player_screen_offset 
    self.position = self.position+self.velocity*frame_time
    player_screen_offset = self.position - np.array((1920,1080))/2
  def check_input(self):
    if pressed_keys[pygame.K_w] != pressed_keys[pygame.K_s]:
      if pressed_keys[pygame.K_w]:
        self.set_y_direction(-1)
      if pressed_keys[pygame.K_s]:
        self.set_y_direction(1)
    else:
      self.set_y_direction(0)
    if pressed_keys[pygame.K_a] != pressed_keys[pygame.K_d]:
      if pressed_keys[pygame.K_a]:
        self.set_x_direction(-1)
      if pressed_keys[pygame.K_d]:
        self.set_x_direction(1)
    else:
      self.set_x_direction(0)

class enemy(entity):
  def __init__(self, radius, max_speed):
    self.radius = radius
    position = self.spawn_position()
    super().__init__(radius, position, max_speed,(255,0,0))
  def spawn_position(self): #fix
    # The position is calculated by generating a random angle that represents the angle between the player and the enemy.
    # Trigonometry is then used to determine the x and y coordinates of the enemy relative to the player.
    # These values are then added to the player position.
    player_pos = player.get_position()
    valid_pos = False
    count = 0
    while not valid_pos != count<=20:
      #if too many spawning attempts are made then the spawning attempt will be cancelled
      count += 1
      angle = random.uniform(0,3.142*2)
      x_pos = ENEMY_SPAWN_RADIUS*np.cos(angle)
      y_pos = ENEMY_SPAWN_RADIUS*np.sin(angle)
      spawn_pos = np.array((x_pos+player_pos[0],y_pos+player_pos[1]))
      valid_pos = True
      #check if the spawning space is filled by another enemy
      for i in enemies:
        if self.is_touching(i,spawn_pos):
          valid_pos = False
    if valid_pos:  
      return spawn_pos
    else:
      print("no valid spawning space")
  def point_towards_player(self):
    #vect diff calculated using vct(AB) = vct(OB) - vct(OA)
    player_pos = player.get_position()
    vect_difference = player_pos - self.position
    self.set_direction(vect_difference)
  def move(self):
    #redefined from entity class so that the enemy points towards the player before moving
    self.point_towards_player()
    super().move()


player = playerClass(100, [0,0])
enemies = []
for i in range(100):
  temp_enemy = enemy(50,100)
  if type(temp_enemy.get_position()) is np.ndarray:
    print(type(temp_enemy.get_position()))
    enemies.append(temp_enemy)
print(len(enemies))
while True:
  for event in pygame.event.get():
    if event.type == QUIT:
      pygame.quit()
      sys.exit()
  pressed_keys = pygame.key.get_pressed()
  player.check_input()
  
  
  DISPLAYSURF.fill((255,255,255))
  background.draw()
  #pygame.draw.rect(DISPLAYSURF, (0,0,0),pygame.Rect(0,0,100,100))
  #pygame.draw.circle(DISPLAYSURF,(0,0,255),(50,150),50)
  for individual_enemy in enemies:
    individual_enemy.draw()
  player.draw()
  frame_time = clock.tick(framerate)/1000
  pygame.display.update()