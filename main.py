import pygame, sys, random
from pygame.locals import QUIT
from PIL import Image, ImageOps
import numpy as np
import math as maths
import random
import time
import json

pygame.init()
scale = 720/1080
DISPLAYSURF = pygame.display.set_mode((1920 * scale, 1080 * scale))
player_screen_offset = np.array((1920,1080))/2
pygame.display.set_caption('Hello World!')
main_font = pygame.font.Font("Fonts\\ezarion\\Ezarion-Black.ttf",40)
framerate = 240
frame_time = 1/framerate
clock = pygame.time.Clock()
frames_rendered = 0
uptime = 0
num_enemies_spawned = 0
total_experience = 0
current_level = 0
player_base_damage = 50
base_pierce = 2

#temp
t_since_last = 0

ENEMY_SPAWN_RADIUS = 2000
ENEMY_DESPAWN_RADIUS = 6000

all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

def vector_magnitude(vector):
  try:
    sum = (vector[0]**2)+(vector[1]**2)
    return np.sqrt(sum)
  except:
    return 0
def spawn_enemy_attempt(radius, max_speed, max_health):
  global num_enemies_spawned
  # The position is calculated by generating a random angle that represents the angle between the player and the enemy.
  # Trigonometry is then used to determine the x and y coordinates of the enemy relative to the player.
  # These values are then added to the player position to get a potential spawning position. 
  # If the enemy spawn collides with an existing enemy the spawn attempt will cancel and a new location will be chosen. 
  # In the event that an enemy has not found a spawn location in 5 attempts the spawn attempt will fail.
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
    new_enemy = enemy(radius,max_speed,spawn_pos, max_health,hurt_image = ("Images\\Skull\\Hurt.png","Skull_Hurt.png"))
    all_sprites.add(new_enemy)
    enemies.add(new_enemy)
    num_enemies_spawned += 1
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
def find_num_enemies_to_spawn():
  total_num_enemies = (10*uptime + (uptime**2/20) + ((uptime**3)/6000))/60
  enemies_to_spawn = total_num_enemies - num_enemies_spawned
  if enemies_to_spawn < 0:
    return 0
  else:
    return int(enemies_to_spawn)
def closest_enemy(self):
  closest_enemy = False
  closest_distance = -1
  for enemy in enemies: #find closest enemy loop
    try:
      distance = vector_magnitude(self.position-enemy.position)
    except:
      print("faulty position data")
      distance = -1
    if closest_enemy == False or closest_distance < 0:
      closest_enemy = enemy
      closest_distance = distance
    elif distance < closest_distance:
      closest_enemy = enemy
      closest_distance = distance
  if closest_enemy == False or closest_distance<0:
    return False
  else:
    #pygame.draw.circle(DISPLAYSURF,(17,17,127),(closest_enemy.position-player_screen_offset)*scale,64*scale,int(10*scale))
    #print(closest_enemy.position)
    return closest_enemy

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
  def __init__(self, radius, position, max_speed, colour,image, animation_json = False):
    pygame.sprite.Sprite.__init__(self)
    self.position = np.array(position)
    self.radius = radius
    self.velocity = np.array([0,0])
    self.direction = np.array((0,0))
    self.max_speed = max_speed
    self.colour = colour
    self.time_since_update = uptime
    #self.image,_,_ = resize_image(image_location,image_destination)
    self.image = image
    self.rect = pygame.Rect(self.position,(radius*2,radius*2))

    """if animation_json != False:
      #try:
      with open(animation_json) as f:
        self.animation_info = json.load(f)
        
      self.frame_dict = self.set_animation()
      #except:
      #  print("failed")
      #  self.animation_info = False
    else:
      self.animation_info = False
    #self.rect[0:2] = self.position"""
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
    self.rect[0:2] = self.position-np.array((self.radius,self.radius))
  def draw(self):
    # this will draw any entities onto the screen. currently defined as a coloured circle
    #pygame.draw.circle(DISPLAYSURF,self.colour,(self.position-player_screen_offset)*scale,int(self.radius*scale))
    #debug code thad draws an outline box around all entities
    """
    drawing_rect = self.rect.copy()
    drawing_rect = drawing_rect.move(-player_screen_offset)#.move(-self.radius,-self.radius)
    drawing_rect = pygame.Rect(drawing_rect[0]*scale,drawing_rect[1]*scale,drawing_rect[2]*scale,drawing_rect[3]*scale)
    pygame.draw.rect(DISPLAYSURF, (0,0,0),drawing_rect,width = 3)
    """
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
  def update(self):
    self.move()
    self.draw()
  def set_animation(self):
    """
    global scale
    num_frames = self.animation_info["num_of_frames"]
    frame_dict = {}
    for instance in self.animation_info["instances"]:
      frame_dict[instance] = {}
      for motion in self.animation_info["motions"]:
        frame_dict[instance][motion]=[]
        for i in range(num_frames):
          try:
            source = self.animation_info["base_file_path"] + "\\" + instance \
                      + "\\" + motion + "\\Frame" + str(i+1) + ".png"
            dest = "Converted\\"+ self.animation_info["name"] + "\\" + instance \
                      + "\\" + motion + "\\Frame" + str(i+1) + ".png"
            print(dest)
            original_image = Image.open(source)
            image_size = np.array(original_image.size)
            scaled_image_size = np.trunc(self.radius*2*scale)
            scale = scaled_image_size/image_size[0]
            background_image = ImageOps.scale(original_image, scale).save(dest)
            background_image = pygame.image.load(dest).convert_alpha()
            frame_dict[instance][motion].append(background_image)
          except:
            pass
    return frame_dict
    """
    pass
        





class playerClass(entity):
  # player specific code such as weapons, exp and health will stay in this class
  max_health = 10
  health = max_health
  def __init__(self, radius, position):
    image,_,_ = resize_image("Images/player.png","converted_player.png")
    super().__init__(radius, position, 500, (0,0,255),image)
  def move(self):
    #moves based on velocity, saves the result to self.rect
    global player_screen_offset 
    self.position = self.position+self.velocity*frame_time
    player_screen_offset = self.position - np.array((1920,1080))/2
    self.rect[0:2] = self.position-np.array((self.radius,self.radius))
  def draw(self):
    #redefined so that the player's health is displayed above player
    #the text is rendered and then scaled down before being displayed
    text_surface = main_font.render(str(self.health)+"/"+str(self.max_health), False, (0, 0, 0))
    text_width = int(text_surface.get_width())
    text_surface = pygame.transform.scale_by(text_surface,scale)
    DISPLAYSURF.blit(text_surface,(self.position-player_screen_offset-np.array((text_width/2,self.radius*1.5)))*scale)
    DISPLAYSURF.blit(self.image,(self.position-player_screen_offset-np.array((self.radius,self.radius)))*scale)
  def check_input(self):
    if pressed_keys[pygame.K_w] != pressed_keys[pygame.K_s]:
      if pressed_keys[pygame.K_w]:
        self.set_y_direction(-1)
      elif pressed_keys[pygame.K_s]:
        self.set_y_direction(1)
    else:
      self.set_y_direction(0)
    if pressed_keys[pygame.K_a] != pressed_keys[pygame.K_d]:
      if pressed_keys[pygame.K_a]:
        self.set_x_direction(-1)
      elif pressed_keys[pygame.K_d]:
        self.set_x_direction(1)
    else:
      self.set_x_direction(0)
  def check_if_damaged(self):
    for i in enemies:
      if pygame.sprite.collide_circle(self,i) and uptime - i.time_since_damaging_player >2:
        self.health -= 1
        i.time_since_damaging_player = uptime

class enemy(entity):
  def __init__(self, radius, max_speed, position, max_health, health = 0, hurt_image = (None,None)):
    #hurt_image is a tuple (source,destination) where both are file paths for an image to be saved or loaded
    self.time_since_damaging_player = 0
    self.max_health = max_health
    self.last_damaged = 0
    image,_,_ = resize_image("Images\\Skull\\Normal.png","converted_enemy.png")
    try:
      if hurt_image[0] and hurt_image[1]:
        self.hurt_image,_,_ = resize_image(hurt_image[0],hurt_image[1])
      else:
        self.hurt_image = None
    except:
      self.hurt_image = None

    if health == 0:
      self.health = max_health
    
    super().__init__(radius, position, max_speed,(255,0,0),image)
  def point_towards_player(self):
    #vect diff calculated using vct(AB) = vct(OB) - vct(OA)
    player_pos = player.get_position()
    vect_difference = player_pos - self.position
    self.set_direction(vect_difference)
  def despawn_check(self):
    player_pos = player.get_position()
    distance_from_player = vector_magnitude(player_pos-self.position)
    return distance_from_player >= ENEMY_DESPAWN_RADIUS
  def move(self):
    #redefined from entity class so that the enemy points towards the player before moving
    #After moving the enemy will check if it is outside of the despawn circle. If it is it will be killed.
    self.point_towards_player()
    time_difference = uptime - self.time_since_update
    self.time_since_update = uptime
    self.position = self.position+self.velocity*time_difference
    display_position = self.position-player_screen_offset
    if (display_position[0] <= 1920 and display_position[0] >= 0) and (display_position[1] <= 1080 and display_position[1] >= 0):
      collision_check = enemies.copy()
      collision_check.remove(self)
      collision_check.add(player)
      for i in collision_check:
        if pygame.sprite.collide_circle(self,i):
          displacement_vect = self.position - i.position
          combined_radius = self.radius + i.radius
          scale = (combined_radius/vector_magnitude(displacement_vect))-1
          movement = displacement_vect*scale
          self.position = self.position + movement
      collision_check.empty()
    self.rect[0:2] = self.position-np.array((self.radius,self.radius))
    # Delete enemies if they are too far from the player
    if self.despawn_check():
      pygame.sprite.Sprite.kill(self)
  def on_death(self):
    global total_experience
    total_experience += 1
    experience.update()
    pygame.sprite.Sprite.kill(self)
  def deal_damage(self, damage):
    self.health -= damage
    self.last_damaged = uptime
    if self.health <= 0:
      self.on_death()
  def draw(self):
    if uptime-self.last_damaged <0.2 and self.hurt_image:
      DISPLAYSURF.blit(self.hurt_image,(self.position-player_screen_offset-np.array((self.radius,self.radius)))*scale)
    else:
      DISPLAYSURF.blit(self.image,(self.position-player_screen_offset-np.array((self.radius,self.radius)))*scale)

class bullet(entity):
  def __init__(self, position, speed, damage, angle, pierce, radius, image):
    super().__init__(radius,position,speed,(0,0,0),image)
    self.damage = damage
    self.pierce = pierce
    self.set_direction(np.array((np.cos(angle),np.sin(angle))))
    self.last_entity_touched = False
    all_sprites.add(self)
    bullets.add(self)
    self.collision_group = enemies
  def set_angle(self,angle):
    self.set_direction(np.array((np.cos(angle),np.sin(angle))))
  def remove_self(self):
    pygame.sprite.Sprite.kill(self)
  def is_touching_wall(self):
    distance_from_player = player.position-self.position
    if distance_from_player[0] > 1920/2 \
    or distance_from_player[0] < -1920/2 \
    or distance_from_player[1] > 1080/2 \
    or distance_from_player[1] < -1080/2:
      return True
    else:
      return False
  def collides_with_entity(self):
    for entity in self.collision_group:
      if pygame.sprite.collide_circle(self,entity):
        #pygame.draw.circle(DISPLAYSURF,(0,0,255),(entity.position-player_screen_offset)*scale,50)
        return entity
    return False
  def move(self):
    super().move()
    collided_entity = self.collides_with_entity()
    if self.is_touching_wall():
      self.remove_self()
    elif collided_entity != self.last_entity_touched and collided_entity != False:
      self.last_entity_touched = collided_entity
      self.pierce -= 1
      # damage enemy here
      collided_entity.deal_damage(self.damage)
      if self.pierce < 0:
        self.remove_self()

class weapon():
  fire_delay = 1 #Time between bullets
  damage_mult = 1 #multiplier to base damage applied to bullets
  speed = 700 #in pixels per second
  image_location = "Images/musket_bullet.png"
  image_destination = "converted_musket_bullet.png"
  time_since_fire = 0
  def __init__(self):
    image = Image.open(self.image_location)
    self.radius = image.width/2
    self.image,_,_ = resize_image(self.image_location,self.image_destination)
  def find_angle_to_closest_enemy(self):
    relative_vector = np.array((1,0))
    target = closest_enemy(player)
    print(type(target))
    if type(target) == enemy:
      enemy_pos = target.get_position()
      player_pos = player.get_position()
      resultant_vector = enemy_pos-player_pos
      dot_prod = relative_vector[0]*resultant_vector[0]+relative_vector[1]*resultant_vector[1]
      positive_angle=np.arccos(dot_prod/np.sqrt(resultant_vector[0]**2+resultant_vector[1]**2))
      if resultant_vector[1]<0:
        angle = -positive_angle
      else: 
        angle = positive_angle
      return angle
    else:
      return 0
  def fire_bullet(self):
    angle = self.find_angle_to_closest_enemy()
    position = player.get_position()
    damage = player_base_damage*self.damage_mult
    pierce = base_pierce
    self.time_since_fire = uptime
    new_bullet = bullet(position, self.speed, damage, angle, pierce, self.radius, self.image)
  def update(self):
    if uptime-self.time_since_fire>self.fire_delay:
      self.fire_bullet()








      
  


class experience():
  def __init__(self):
    self.colour = (128,0,0)
    self.progress_to_next_level = 0
  def update(self):
    global current_level, total_experience
    #a and b are constants used in the level up equation
    #they are kept seperate so they can be easily changed if needed
    a = -1/50000
    b = 1/12
    next_level = current_level+1
     # total exp required for the player to level up
    exp_to_level_up = int((-b+(4*a*next_level+b**2)**(1/2))/(2*a))
    # total exp required for the player to acheive their current level
    current_level_exp = int((-b+(4*a*current_level+b**2)**(1/2))/(2*a)) 
    #used for the exp bar. same as (exp gained since leveling up/exp difference between levels)
    self.progress_to_next_level = (total_experience-current_level_exp)/(exp_to_level_up-current_level_exp)
    if total_experience >= exp_to_level_up:
      current_level += 1
      # Todo Notify player of a level up
      self.update()
  def draw(self):
    level_box_width = 100
    text_size = 50
    exp_bar_height = 20
    level_font = pygame.font.Font("Fonts\\ezarion\\Ezarion-Black.ttf",text_size)
    text_surface = level_font.render(str(current_level), False, (255, 255, 255))
    text_width = int(text_surface.get_width())
    text_height = int(text_surface.get_height())
    text_surface = pygame.transform.scale_by(text_surface,scale)
    text_centre_pos = np.array((text_width/2,text_height/2))
    exp_bar_size = np.array((level_box_width,0,(1920-level_box_width)*self.progress_to_next_level,exp_bar_height))

    pygame.draw.rect(DISPLAYSURF, (17,17,129),
                     pygame.Rect(np.array((0,0,level_box_width,level_box_width))*scale)) #Draw box
    pygame.draw.rect(DISPLAYSURF, (0,0,0),
                     pygame.Rect(np.array((0,0,level_box_width,level_box_width))*scale), int(10*scale)) #Draw Border
    DISPLAYSURF.blit(text_surface,
                     (np.array((level_box_width,level_box_width))/2-text_centre_pos)*scale) #Display level
    pygame.draw.rect(DISPLAYSURF, self.colour,pygame.Rect(exp_bar_size*scale)) #Display progress bar

total = 0
gun = weapon()
player = playerClass(100, [0,0])
all_sprites.add(player)
experience = experience()
experience.update()
#for i in range(50):
#  spawn_enemy_attempt(50,100)
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
  for i in range(find_num_enemies_to_spawn()):
    spawn_enemy_attempt(50,100,100)
  
  enemies.update()
  
  player.check_if_damaged()
  player.move()
  player.draw()
  closest_enemy(player)
  bullets.update()
  # print(player.health)
  
  if uptime-t_since_last>1:
    t_since_last = uptime
    print(1/frame_time)
    print(len(enemies))
    gun.update()
    #bullet(player.position,700,1,np.pi,1,"Images/musket_bullet.png","converted_musket_bullet.png")
  experience.draw()

  frame_time = clock.tick(framerate)/1000
  uptime += frame_time
  frames_rendered += 1
  pygame.display.update()