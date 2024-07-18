import pygame, sys, random
from pygame.locals import QUIT
from PIL import Image, ImageOps
import numpy as np
import math as maths
import random
import time

pygame.init()
scale = 720/1080
DISPLAYSURF = pygame.display.set_mode((1920 * scale, 1080 * scale))
player_screen_offset = np.array((1920,1080))/2
pygame.display.set_caption('Hello World!')
framerate = 120
frame_time = 1/framerate
clock = pygame.time.Clock()
frames_rendered = 0
uptime = 0

ENEMY_SPAWN_RADIUS = 2000

def vector_magnitude(vector):
  try:
    sum = (vector[0]**2)+(vector[1]**2)
    return np.sqrt(sum)
  except:
    return 0
def spawn_enemy_attempt(radius, max_speed):
  # The position is calculated by generating a random angle that represents the angle between the player and the enemy.
  # Trigonometry is then used to determine the x and y coordinates of the enemy relative to the player.
  # These values are then added to the player position.
  player_pos = player.get_position()
  valid_pos = False
  count = 0
  while not valid_pos and count<=5:
    #if too many spawning attempts are made then the spawning attempt will be cancelled
    count += 1
    angle = random.uniform(0,3.142*2)
    x_pos = ENEMY_SPAWN_RADIUS*np.cos(angle)
    y_pos = ENEMY_SPAWN_RADIUS*np.sin(angle)
    spawn_pos = np.array((x_pos+player_pos[0],y_pos+player_pos[1]))
    valid_pos = True
    #check if the spawning space is filled by another enemy
    for i in enemies:
      if not isinstance(i, entity) or vector_magnitude(spawn_pos-i.position)<=radius+i.radius:  
        valid_pos = False
  if valid_pos:  
    enemies.append(enemy(radius,max_speed,spawn_pos))
    return True
  else:
    return False
def resize_image(source,dest):
  original_image = Image.open(source)
  image_size = np.array(original_image.size)
  scaled_image_size = np.trunc(image_size*scale)
  width = int(scaled_image_size[0])
  height = int(scaled_image_size[1])
  background_image = ImageOps.fit(original_image, (width,height)).save(dest)
  background_image = pygame.image.load(dest).convert_alpha()
  return background_image, image_size, scaled_image_size

class backgroundClass:
  def __init__(self):
    """
    background_PIL = Image.open("Images/background.png")
    self.image_size = np.array(background_PIL.size)
    self.scaled_image_size = np.trunc(self.image_size*scale)
    self.width = int(self.scaled_image_size[0])
    self.height = int(self.scaled_image_size[1])
    background_PIL = ImageOps.fit(background_PIL, (self.width,self.height)).save("converted_background.png")
    #print(background_PIL)
    self.background_image = pygame.image.load("converted_background.png")
    """
    self.background_image, self.image_size, self.scaled_image_size = resize_image("Images/background.png","converted_background.png")
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


class entity(pygame.sprite.Sprite):
  # Entity class is used for players, enemies and projectiles and anything else that can collide with other entities or move around the screen
  def __init__(self, radius, position, max_speed, colour,image_location,image_destination):
    pygame.sprite.Sprite.__init__(self)
    self.position = np.array(position)
    self.radius = radius
    self.velocity = np.array([0,0])
    self.direction = np.array((0,0))
    self.max_speed = max_speed
    self.colour = colour
    self.time_since_update = uptime
    self.image,_,_ = resize_image(image_location,image_destination)
    self.rect = self.image.get_rect()
    self.rect[0:2] = self.position
  def set_position(self, new_position):
    self.position = np.array(new_position)
  def get_position(self):
    return self.position
  def set_direction(self, direction):
    self.direction = np.array(direction)
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
    time_difference = uptime - self.time_since_update
    self.time_since_update = uptime
    self.position = self.position+self.velocity*time_difference
    self.rect[0:2] = self.position
  def draw(self):
    # this will draw any entities onto the screen. currently defined as a coloured circle
    #pygame.draw.circle(DISPLAYSURF,self.colour,(self.position-player_screen_offset)*scale,int(self.radius*scale))
    DISPLAYSURF.blit(self.image,(self.position-player_screen_offset-np.array((self.radius,self.radius)))*scale)
  def is_touching(self,other_entity,other_coords = False):
    if type(other_coords) == np.ndarray:
      tested_position = other_coords
    else:
      tested_position = self.position
    if isinstance(other_entity, entity):
      vect_diff = tested_position-other_entity.get_position()
      collide_dist = self.radius+other_entity.radius
      if (vector_magnitude(vect_diff) < collide_dist) and self != other_entity:
        return True
    return False



class playerClass(entity):
  # player specific code such as weapons, exp and health will stay in this class
  health_points = 10
  health = 10
  def __init__(self, radius, position):
    super().__init__(radius, position, 500, (0,0,255),"Images/player.png","converted_player.png")
  def move(self):
    #moves based on velocity, saves the result to self.rect
    global player_screen_offset 
    self.position = self.position+self.velocity*frame_time
    player_screen_offset = self.position - np.array((1920,1080))/2
    self.rect[0:2] = self.position
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
  def check_if_damaged(self):
    for i in enemies:
      distance = vector_magnitude(self.position-i.position)
      if distance <= self.radius + i.radius and uptime - i.time_since_damage >2:
        self.health -= 1
        i.time_since_damage = uptime


class enemy(entity):
  def __init__(self, radius, max_speed, position):
    self.time_since_damage = uptime
    super().__init__(radius, position, max_speed,(255,0,0),"Images/enemy.png","converted_enemy.png")
  def point_towards_player(self):
    #vect diff calculated using vct(AB) = vct(OB) - vct(OA)
    player_pos = player.get_position()
    vect_difference = player_pos - self.position
    self.set_direction(vect_difference)
  def move(self):
    #redefined from entity class so that the enemy points towards the player before moving
    self.point_towards_player()
    time_difference = uptime - self.time_since_update
    self.time_since_update = uptime
    self.position = self.position+self.velocity*time_difference
    display_position = self.position-player_screen_offset
    if (display_position[0] <= 1920 and display_position[0] >= 0) and (display_position[1] <= 1080 and display_position[1] >= 0):
      collision_check = enemies + [player]
      for i in collision_check:
        if self.is_touching(i) and isinstance(i, entity):
          displacement_vect = self.position - i.position
          combined_radius = self.radius + i.radius
          scale = (combined_radius/vector_magnitude(displacement_vect))-1
          movement = displacement_vect*scale
          self.position = self.position + movement
    self.rect[0:2] = self.position


total = 0

player = playerClass(100, [0,0])
enemies = []
for i in range(50):
  spawn_enemy_attempt(50,100)
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
  for individual_enemy in range(len(enemies)):
    enemies[individual_enemy].move()
    enemies[individual_enemy].draw()
  
  player.check_if_damaged()
  player.move()
  player.draw()
  print(1/frame_time)
  frame_time = clock.tick(framerate)/1000
  uptime += frame_time
  frames_rendered += 1
  pygame.display.update()