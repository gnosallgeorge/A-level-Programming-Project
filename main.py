import pygame, sys, random
from pygame.locals import QUIT

pygame.init()
scale = 0.7
DISPLAYSURF = pygame.display.set_mode((1920 * scale, 1080 * scale))
pygame.display.set_caption('Hello World!')
framerate = 30
clock = pygame.time.Clock()

background_image = pygame.image.load("Images/background.png")

while True:
  for event in pygame.event.get():
    if event.type == QUIT:
      pygame.quit()
      sys.exit()
  DISPLAYSURF.fill((255,255,255))
  pygame.draw.rect(DISPLAYSURF, (0,0,0),pygame.Rect(0,0,100,100))
  pygame.draw.circle(DISPLAYSURF,(0,0,255),(50,150),50)
  clock.tick(framerate)
  pygame.display.update()