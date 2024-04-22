import pygame, sys, random
from pygame.locals import QUIT

pygame.init()
scale = 0.7
DISPLAYSURF = pygame.display.set_mode((1920 * scale, 1080 * scale))
pygame.display.set_caption('Hello World!')
framerate = 30
clock = pygame.time.Clock()

background_image = pygame.image.load("Images/background.png")

class background:
  background_image = pygame.image.load("Images/background.png")
  width = 1024
  height = 1024
  def __init__(self):
    pass
  def draw(self):
    player_pos = (0,0)#get player pos
    player_grid_pos = (player_pos[0]//self.width,player_pos[1]//self.height)
    for x in range(-1,2):
      for y in range(-1,2):
        DISPLAYSURF.blit(background_image, ((player_grid_pos[0]+x)*1024,(player_grid_pos[1]+y)*1024))

background = background()

class entity:
  def __init__(self, radius, position, max_velocity):
    self.position = position
    self.radius = radius
    self.max_velocity = max_velocity
  def set_position(self, new_position):
    self.position = new_position
  def get_position(self):
    return self.position
  def set_velocity(self, velocity):
    self.velocity = velocity
  def move(self):
    new_pos = (self.position[0]+self.velocity[0]/framerate,self.position[1]+self.velocity[1]/framerate)
    self.set_position(new_pos)
  def draw(self):
      self.move()
      pygame.draw.circle(DISPLAYSURF,(0,0,255),self.position,self.radius)




class player(entity):
  def __init__(self, radius, position, max_velocity):
    super().__init__(radius, position, max_velocity)
  
player = player(100, (500,500), 50)
player.set_velocity((0,10))  



while True:
  for event in pygame.event.get():
    if event.type == QUIT:
      pygame.quit()
      sys.exit()
  DISPLAYSURF.fill((255,255,255))
  DISPLAYSURF.blit(background_image, (0,0))
  background.draw()
  pygame.draw.rect(DISPLAYSURF, (0,0,0),pygame.Rect(0,0,100,100))
  pygame.draw.circle(DISPLAYSURF,(0,0,255),(50,150),50)
  player.draw()
  clock.tick(framerate)
  pygame.display.update()

