import pygame, sys, random
from pygame.locals import QUIT

pygame.init()
scale = 0.7
DISPLAYSURF = pygame.display.set_mode((1920 * scale, 1080 * scale))
pygame.display.set_caption('Hello World!')
framerate = 60
frame_time = 1/framerate
clock = pygame.time.Clock()

class background:
  background_image = pygame.image.load("Images/background.png")
  width = 1024
  height = 1024
  def __init__(self):
    pass
  def draw(self):
    player_pos = player.get_position()
    # converts the player coordinates to snap coordinates for the map image
    player_grid_pos = (int(player_pos[0]//self.width),int(player_pos[1]//self.height))
    print(player_grid_pos)
    # blits map images in a 3x3 grid where the player is in the centre tile
    for x in range(-1,2):
      for y in range(-1,2):
        DISPLAYSURF.blit(self.background_image, ((player_grid_pos[0]+x)*1024,(player_grid_pos[1]+y)*1024))

background = background()
# Entity class is used for players, enemies and projectiles and anything else that can collide with other entities or move around the screen

class entity:
  def __init__(self, radius, position, max_velocity):
    self.position = position
    self.radius = radius
    self.max_velocity = max_velocity
    self.velocity = [0,0]
  def set_position(self, new_position):
    self.position = new_position
  def get_position(self):
    return self.position
  # velocity is set as a list [velocity_x, velocity_y]
  def set_velocity(self, velocity):
    self.velocity = velocity
  def set_x_velocity(self, x_velocity):
    self.velocity[0] = x_velocity
  def set_y_velocity(self, y_velocity):
    self.velocity[1] = y_velocity
  def move(self):
    new_pos = (self.position[0]+self.velocity[0]*frame_time,self.position[1]+self.velocity[1]*frame_time)
    self.set_position(new_pos)
  # this will draw any entities onto the screen. currently defined as a blue circle
  def draw(self):
      self.move()
      pygame.draw.circle(DISPLAYSURF,(0,0,255),self.position,self.radius)



# player specific code such as weapons, exp and health will stay in this class
class player(entity):
  def __init__(self, radius, position, max_velocity):
    super().__init__(radius, position, max_velocity)
  
player = player(100, (500,500), 50)
player.set_y_velocity((100))  



while True:
  for event in pygame.event.get():
    if event.type == QUIT:
      pygame.quit()
      sys.exit()

  DISPLAYSURF.fill((255,255,255))
  #DISPLAYSURF.blit(background_image, (0,0))
  background.draw()
  pygame.draw.rect(DISPLAYSURF, (0,0,0),pygame.Rect(0,0,100,100))
  pygame.draw.circle(DISPLAYSURF,(0,0,255),(50,150),50)
  player.draw()
  #clock.tick(framerate)
  frame_time = clock.tick(framerate)/1000
  pygame.display.update()

