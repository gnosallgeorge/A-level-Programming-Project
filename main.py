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
    return maths.sqrt(sum)
  except:
    return 0

class background:
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

background = background()
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
    self.diretion = np.array(velocity)
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
  # this will draw any entities onto the screen. currently defined as a blue circle
  def draw(self):
      self.move()
      pygame.draw.circle(DISPLAYSURF,self.colour,(self.position-player_screen_offset)*scale,int(self.radius*scale))

# player specific code such as weapons, exp and health will stay in this class
class player(entity):
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
    position = self.spawn_position()
    super().__init__(radius, position, max_speed,(255,0,0))
  def spawn_position(self):
    player_pos = player.get_position()
    angle = random.uniform(0,3.142*2)
    x_pos = ENEMY_SPAWN_RADIUS*np.cos(angle)
    y_pos = ENEMY_SPAWN_RADIUS*np.sin(angle)
    return np.array((x_pos+player_pos[0],y_pos+player_pos[1]))

player = player(100, [0,0])
enemies = []

while True:
  for event in pygame.event.get():
    if event.type == QUIT:
      pygame.quit()
      sys.exit()
  pressed_keys = pygame.key.get_pressed()
  player.check_input()
  enemies.append(enemy(50,0))
  
  DISPLAYSURF.fill((255,255,255))
  background.draw()
  #pygame.draw.rect(DISPLAYSURF, (0,0,0),pygame.Rect(0,0,100,100))
  #pygame.draw.circle(DISPLAYSURF,(0,0,255),(50,150),50)
  for individual_enemy in enemies:
    individual_enemy.draw()
  player.draw()
  frame_time = clock.tick(framerate)/1000
  pygame.display.update()