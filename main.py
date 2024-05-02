import pygame, sys, random
from pygame.locals import QUIT
from PIL import Image, ImageOps
import numpy as np

pygame.init()
scale = 720/1080
DISPLAYSURF = pygame.display.set_mode((1920 * scale, 1080 * scale))
pygame.display.set_caption('Hello World!')
framerate = 60
frame_time = 1/framerate
clock = pygame.time.Clock()

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
    print(player_pos)
    # converts the player coordinates to snap coordinates for the map image
    player_grid_pos = np.trunc(player_pos/self.image_size)
    print(player_grid_pos)
    # blits map images in a 3x3 grid where the player is in the centre tile
    for x in range(-1,2):
      for y in range(-1,2):
        offset = np.array((x,y))
        DISPLAYSURF.blit(self.background_image, ((player_grid_pos+offset)*self.scaled_image_size))

background = background()
# Entity class is used for players, enemies and projectiles and anything else that can collide with other entities or move around the screen

class entity:
  def __init__(self, radius, position):
    self.position = np.array(position)
    self.radius = radius
    self.velocity = np.array([0,0])
  def set_position(self, new_position):
    self.position = np.array(new_position)
  def get_position(self):
    return self.position
  # velocity is set as a list [velocity_x, velocity_y]
  def set_velocity(self, velocity):
    self.velocity = np.array(velocity)
  def set_x_velocity(self, x_velocity):
    self.velocity[0] = x_velocity
  def set_y_velocity(self, y_velocity):
    self.velocity[1] = y_velocity
  def move(self):
    self.position = self.position+self.velocity*frame_time
  # this will draw any entities onto the screen. currently defined as a blue circle
  def draw(self):
      self.move()
      pygame.draw.circle(DISPLAYSURF,(0,0,255),self.position*scale,int(self.radius*scale))

# player specific code such as weapons, exp and health will stay in this class
class player(entity):
  def __init__(self, radius, position):
    super().__init__(radius, position)
  
player = player(100, [450,200])
player.set_x_velocity((100))  



while True:
  for event in pygame.event.get():
    if event.type == QUIT:
      pygame.quit()
      sys.exit()

  DISPLAYSURF.fill((255,255,255))
  background.draw()
  #pygame.draw.rect(DISPLAYSURF, (0,0,0),pygame.Rect(0,0,100,100))
  #pygame.draw.circle(DISPLAYSURF,(0,0,255),(50,150),50)
  player.draw()
  frame_time = clock.tick(framerate)/1000
  pygame.display.update()