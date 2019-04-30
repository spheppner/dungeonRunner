"""
author: Simon HEPPNER
website: simon.heppner.at
email: simon@heppner.at
name of game: dungeonrunner
"""
import pygame
#import math
import dungeonGenerator
import random
import os
import time
#import operator
import math
#import vectorclass2d as v
#import textscroller_vertical as ts
#import subprocess

def randomize_color(color, delta=50):
    d=random.randint(-delta, delta)
    color = color + d
    color = min(255,color)
    color = max(0, color)
    return color

def make_text(msg="pygame is cool", fontcolor=(255, 0, 255), fontsize=42, font=None):
    """returns pygame surface with text. You still need to blit the surface."""
    myfont = pygame.font.SysFont(font, fontsize)
    mytext = myfont.render(msg, True, fontcolor)
    mytext = mytext.convert_alpha()
    return mytext

def write(background, text, x=50, y=150, color=(0,0,0),
          fontsize=None, center=False):
        """write text on pygame surface. """
        if fontsize is None:
            fontsize = 24
        font = pygame.font.SysFont('mono', fontsize, bold=True)
        fw, fh = font.size(text)
        surface = font.render(text, True, color)
        if center: # center text around x,y
            background.blit(surface, (x-fw//2, y-fh//2))
        else:      # topleft corner is x,y
            background.blit(surface, (x,y))

def elastic_collision(sprite1, sprite2):
        """elasitc collision between 2 VectorSprites (calculated as disc's).
           The function alters the dx and dy movement vectors of both sprites.
           The sprites need the property .mass, .radius, pos.x pos.y, move.x, move.y
           by Leonard Michlmayr"""
        if sprite1.static and sprite2.static:
            return
        dirx = sprite1.pos.x - sprite2.pos.x
        diry = sprite1.pos.y - sprite2.pos.y
        sumofmasses = sprite1.mass + sprite2.mass
        sx = (sprite1.move.x * sprite1.mass + sprite2.move.x * sprite2.mass) / sumofmasses
        sy = (sprite1.move.y * sprite1.mass + sprite2.move.y * sprite2.mass) / sumofmasses
        bdxs = sprite2.move.x - sx
        bdys = sprite2.move.y - sy
        cbdxs = sprite1.move.x - sx
        cbdys = sprite1.move.y - sy
        distancesquare = dirx * dirx + diry * diry
        if distancesquare == 0:
            dirx = random.randint(0,11) - 5.5
            diry = random.randint(0,11) - 5.5
            distancesquare = dirx * dirx + diry * diry
        dp = (bdxs * dirx + bdys * diry) # scalar product
        dp /= distancesquare # divide by distance * distance.
        cdp = (cbdxs * dirx + cbdys * diry)
        cdp /= distancesquare
        if dp > 0:
            if not sprite2.static:
                sprite2.move.x -= 2 * dirx * dp
                sprite2.move.y -= 2 * diry * dp
            if not sprite1.static:
                sprite1.move.x -= 2 * dirx * cdp
                sprite1.move.y -= 2 * diry * cdp

class Flytext(pygame.sprite.Sprite):
    def __init__(self, x, y, text="hallo", color=(255, 0, 0),
                 dx=0, dy=-50, duration=2, acceleration_factor = 1.0, delay = 0, fontsize=22):
        """a text flying upward and for a short time and disappearing"""
        self._layer = 57  # order of sprite layers (before / behind other sprites)
        pygame.sprite.Sprite.__init__(self, self.groups)  # THIS LINE IS IMPORTANT !!
        self.text = text
        self.r, self.g, self.b = color[0], color[1], color[2]
        self.dx = dx
        self.dy = dy
        self.x, self.y = x, y
        self.duration = duration  # duration of flight in seconds
        self.acc = acceleration_factor  # if < 1, Text moves slower. if > 1, text moves faster.
        self.image = make_text(self.text, (self.r, self.g, self.b), fontsize)  # font 22
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        self.time = 0 - delay

    def update(self, seconds):
        self.time += seconds
        if self.time < 0:
            self.rect.center = (-100,-100)
        else:
            self.y += self.dy * seconds
            self.x += self.dx * seconds
            self.dy *= self.acc  # slower and slower
            self.dx *= self.acc
            self.rect.center = (self.x, self.y)
            if self.time > self.duration:
                self.kill()      # remove Sprite from screen and from groups

class VectorSprite(pygame.sprite.Sprite):
    """base class for sprites. this class inherits from pygames sprite class"""
    number = 0
    numbers = {} # { number, Sprite }

    def __init__(self, **kwargs):
        self._default_parameters(**kwargs)
        self._overwrite_parameters()
        pygame.sprite.Sprite.__init__(self, self.groups) #call parent class. NEVER FORGET !
        self.number = VectorSprite.number # unique number for each sprite
        VectorSprite.number += 1
        VectorSprite.numbers[self.number] = self
        self.create_image()
        self.distance_traveled = 0 # in pixel
        #self.rect.center = (-300,-300) # avoid blinking image in topleft corner
        self.rect.center = (int(self.pos.x), -int(self.pos.y))
        
        if self.angle != 0:
            self.set_angle(self.angle)

    def _overwrite_parameters(self):
        """change parameters before create_image is called"""
        pass

    def _default_parameters(self, **kwargs):
        """get unlimited named arguments and turn them into attributes
           default values for missing keywords"""

        for key, arg in kwargs.items():
            setattr(self, key, arg)
        if "layer" not in kwargs:
            self._layer = 4
        else:
            self._layer = self.layer
        if "static" not in kwargs:
            self.static = False
        if "pos" not in kwargs:
            self.pos = pygame.math.Vector2(random.randint(0, Viewer.width),-50)
        if "move" not in kwargs:
            self.move = pygame.math.Vector2(0,0)
        if "radius" not in kwargs:
            self.radius = 5
        if "width" not in kwargs:
            self.width = self.radius * 2
        if "height" not in kwargs:
            self.height = self.radius * 2
        if "color" not in kwargs:
            #self.color = None
            self.color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
        if "hitpoints" not in kwargs:
            self.hitpoints = 100
        self.hitpointsfull = self.hitpoints # makes a copy
        if "mass" not in kwargs:
            self.mass = 10
        if "damage" not in kwargs:
            self.damage = 10
        if "bounce_on_edge" not in kwargs:
            self.bounce_on_edge = False
        if "kill_on_edge" not in kwargs:
            self.kill_on_edge = False
        if "angle" not in kwargs:
            self.angle = 0 # facing right?
        if "max_age" not in kwargs:
            self.max_age = None
        if "max_distance" not in kwargs:
            self.max_distance = None
        if "picture" not in kwargs:
            self.picture = None
        if "bossnumber" not in kwargs:
            self.bossnumber = None
        if "kill_with_boss" not in kwargs:
            self.kill_with_boss = False
        if "sticky_with_boss" not in kwargs:
            self.sticky_with_boss = False
        if "mass" not in kwargs:
            self.mass = 15
        if "upkey" not in kwargs:
            self.upkey = None
        if "downkey" not in kwargs:
            self.downkey = None
        if "rightkey" not in kwargs:
            self.rightkey = None
        if "leftkey" not in kwargs:
            self.leftkey = None
        if "speed" not in kwargs:
            self.speed = None
        if "age" not in kwargs:
            self.age = 0 # age in seconds
        if "warp_on_edge" not in kwargs:
            self.warp_on_edge = False

    def kill(self):
        if self.number in self.numbers:
           del VectorSprite.numbers[self.number] # remove Sprite from numbers dict
        pygame.sprite.Sprite.kill(self)

    def create_image(self):
        if self.picture is not None:
            self.image = self.picture.copy()
        else:
            self.image = pygame.Surface((self.width,self.height))
            self.image.fill((self.color))
        self.image = self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect= self.image.get_rect()
        self.width = self.rect.width
        self.height = self.rect.height

    def rotate(self, by_degree):
        """rotates a sprite and changes it's angle by by_degree"""
        self.angle += by_degree
        oldcenter = self.rect.center
        self.image = pygame.transform.rotate(self.image0, self.angle)
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = oldcenter

    def set_angle(self, degree):
        """rotates a sprite and changes it's angle to degree"""
        self.angle = degree
        oldcenter = self.rect.center
        self.image = pygame.transform.rotate(self.image0, self.angle)
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = oldcenter

    def update(self, seconds):
        """calculate movement, position and bouncing on edge"""
        # ----- kill because... ------
        if self.hitpoints <= 0:
            self.kill()
        if self.max_age is not None and self.age > self.max_age:
            self.kill()
        if self.max_distance is not None and self.distance_traveled > self.max_distance:
            self.kill()
        # ---- movement with/without boss ----
        if self.bossnumber is not None:
            if self.kill_with_boss:
                if self.bossnumber not in VectorSprite.numbers:
                    self.kill()
            if self.sticky_with_boss:
                boss = VectorSprite.numbers[self.bossnumber]
                #self.pos = pygame.math.Vector2(boss.pos.x, boss.pos.y)
                self.pos = pygame.math.Vector2(boss.pos.x, boss.pos.y)
        self.pos += self.move * seconds
        self.distance_traveled += self.move.length() * seconds
        self.age += seconds
        self.rect.center = ( round(self.pos.x, 0), -round(self.pos.y, 0) )

class Player(VectorSprite):

    def _overwrite_parameters(self):
        self._layer = 50
        self.hitpoints = 50
        self.max_hitpoints = 50
        self.endurance = 100
        self.max_endurance = 100
        self.coins = 25
        self.multiplicant = 3
        self.character = "@"
        self.inventory = []

    def create_image(self):
        self.fontsize = 32
        self.color = (255, 0, 255)
        self.text = self.character
        self.image = make_text(self.text, self.color, self.fontsize)
        self.image.set_colorkey((0, 0, 0))
        self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
        

            

class Monster(VectorSprite):

    def _overwrite_parameters(self):
        self._layer = 50
        self.hitpoints = 50
        self.max_mhitpoints = 50
        self.character = "M"
        self.p_moving = 0.25 # probability for moving per turn
        self.intelligence = 0
        
    def create_image(self):
        self.fontsize = 32
        self.color = (255, 0, 255)
        self.text = self.character
        self.image = make_text(self.text, self.color, self.fontsize)
        self.image.set_colorkey((0, 0, 0))
        self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
    
    def ai(self, target):
        if self.intelligence == 0:
            dx, dy = random.choice(((20, 0), (-20, 0), (0, 20), (0, -20)))
        elif self.intelligence == 1:
            dx = target.pos.x - self.pos.x
            dy = target.pos.y - self.pos.y
            if dx > 0:
                dx = 20
            elif dx < 0:
                dx = -20
            if dy > 0:
                dy = 20
            elif dy < 0:
                dy = -20
            
            if dx != 0:
                dy = 0
            if dy != 0:
                dx = 0
        
        return dx, dy

class Monster1(Monster):
    def _overwrite_parameters(self):
        Monster._overwrite_parameters(self)
        self._layer = 50
        self.hitpoints = 25
        self.max_mhitpoints = 25
        self.character = "1"
        self.intelligence = 0
        self.damage = 5

class Monster2(Monster):
    def _overwrite_parameters(self):
        Monster._overwrite_parameters(self)
        self._layer = 50
        self.hitpoints = 50
        self.max_mhitpoints = 50
        self.character = "2"
        self.intelligence = 1
        self.damage = 10

class Monster3(Monster):
    def _overwrite_parameters(self):
        Monster._overwrite_parameters(self)
        self._layer = 50
        self.hitpoints = 75
        self.max_mhitpoints = 75
        self.character = "3"
        self.intelligence = 1
        self.damage = 15

class Monster4(Monster):
    def _overwrite_parameters(self):
        Monster._overwrite_parameters(self)
        self._layer = 50
        self.hitpoints = 100
        self.max_mhitpoints = 100
        self.character = "4"
        self.intelligence = 1
        self.damage = 20

class Grid(VectorSprite):

    def _overwrite_parameters(self):
        self._layer = -10

    def create_image(self):
        self.image = pygame.Surface((20, 20))
        pygame.draw.rect(self.image, (215,215,215), (0,0, 19,19),1)
        self.image.set_colorkey((0,0,0))
        self.image.convert_alpha()
        self.rect = self.image.get_rect()

class Wall(VectorSprite):

    def _overwrite_parameters(self):
        self._layer = 5

    def create_image(self):
        self.image = pygame.Surface((20, 20))
        self.image.fill((0, 255, 0))
        pygame.draw.rect(self.image, (255,0,255), (0,0, 19,19),1)
        self.image.set_colorkey((0,0,0))
        self.image.convert_alpha()
        self.rect = self.image.get_rect()

class SecretWall(VectorSprite):

    def _overwrite_parameters(self):
        self._layer = 5

    def create_image(self):
        self.image = pygame.Surface((20, 20))
        self.image.fill((0, 255, 0))
        pygame.draw.rect(self.image, (255,0,255), (0,0, 19,19),1)
        self.image.set_colorkey((0,0,0))
        self.image.convert_alpha()
        self.rect = self.image.get_rect()

class Srock(VectorSprite):
    def _overwrite_parameters(self):
        self._layer = 5

    def create_image(self):
        self.image = pygame.Surface((20, 20))
        self.image.fill((0, 110, 0))
        pygame.draw.rect(self.image, (255,0,255), (0,0, 19,19),1)
        self.image.set_colorkey((0,0,0))
        self.image.convert_alpha()
        self.rect = self.image.get_rect()

class Coin(VectorSprite):
    def _overwrite_parameters(self):
        self._layer = -5

    def create_image(self):
        self.fontsize = 32
        self.color = (255, 165, 0)
        self.text = "0"
        self.image = make_text(self.text, self.color, self.fontsize)
        self.image.set_colorkey((0, 0, 0))
        self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
        
class SecretCoin(VectorSprite):
    def _overwrite_parameters(self):
        self._layer = 5

    def create_image(self):
        self.image = pygame.Surface((20, 20))
        self.image.fill((0, 255, 0))
        pygame.draw.rect(self.image, (255,0,255), (0,0, 19,19),1)
        self.image.set_colorkey((0,0,0))
        self.image.convert_alpha()
        self.rect = self.image.get_rect()

class GoldLicense(VectorSprite):
    
    def _overwrite_parameters(self):
        self._layer = -5
        self.item_name = "Goldmining License"
        self.item_price = random.randint(5, 15)

    def create_image(self):
        self.fontsize = 32
        self.color = (255, 127, 0)
        self.text = self.item_name[0]
        self.image = make_text(self.text, self.color, self.fontsize)
        self.image.set_colorkey((0, 0, 0))
        self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
    
    def get_item_price(self):
        return self.item_price
    def get_item_name(self):
        return self.item_name
        
class Upgrade1(VectorSprite):
    
    def _overwrite_parameters(self):
        self._layer = -5
        self.item_name = "Damage Upgrade"
        self.item_price = random.randint(10, 20)

    def create_image(self):
        self.fontsize = 32
        self.color = (255, 127, 0)
        self.text = self.item_name[0]
        self.image = make_text(self.text, self.color, self.fontsize)
        self.image.set_colorkey((0, 0, 0))
        self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
    
    def get_item_price(self):
        return self.item_price
    def get_item_name(self):
        return self.item_name

class Upgrade2(VectorSprite):
    
    def _overwrite_parameters(self):
        self._layer = -5
        self.item_name = "HP Upgrade"
        self.item_price = random.randint(10, 20)

    def create_image(self):
        self.fontsize = 32
        self.color = (255, 127, 0)
        self.text = self.item_name[0]
        self.image = make_text(self.text, self.color, self.fontsize)
        self.image.set_colorkey((0, 0, 0))
        self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
    
    def get_item_price(self):
        return self.item_price
    def get_item_name(self):
        return self.item_name

class Healing(VectorSprite):
    
    def _overwrite_parameters(self):
        self._layer = -5
        self.item_name = "Healing"
        self.item_price = random.randint(1, 5)

    def create_image(self):
        self.fontsize = 32
        self.color = (255, 127, 0)
        self.text = self.item_name[0]
        self.image = make_text(self.text, self.color, self.fontsize)
        self.image.set_colorkey((0, 0, 0))
        self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
    
    def get_item_price(self):
        return self.item_price
    def get_item_name(self):
        return self.item_name

class ExitChar(VectorSprite):
    def _overwrite_parameters(self):
        self._layer = -5

    def create_image(self):
        self.fontsize = 32
        self.color = (255, 0, 0)
        self.text = "-"
        self.image = make_text(self.text, self.color, self.fontsize)
        self.image.set_colorkey((0, 0, 0))
        self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()

class Shop(VectorSprite):
    def _overwrite_parameters(self):
        self._layer = -5

    def create_image(self):
        self.fontsize = 32
        self.color = (0, 0, 255)
        self.text = "+"
        self.image = make_text(self.text, self.color, self.fontsize)
        #write(self.image
        self.image.set_colorkey((0, 0, 0))
        self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()

class Goldrock(VectorSprite):
    def _overwrite_parameters(self):
        self._layer = 5

    def create_image(self):
        self.image = pygame.Surface((20, 20))
        self.image.fill((255, 255, 0))
        pygame.draw.rect(self.image, (255,0,255), (0,0, 19,19),1)
        self.image.set_colorkey((0,0,0))
        self.image.convert_alpha()
        self.rect = self.image.get_rect()

class StairDown(VectorSprite):
    def _overwrite_parameters(self):
        self._layer = -5

    def create_image(self):
        self.fontsize = 32
        self.color = (255, 165, 0)
        self.text = "<"
        self.image = make_text(self.text, self.color, self.fontsize)
        self.image.set_colorkey((0, 0, 0))
        self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()


class Explosion():

    def __init__(self, pos, maxspeed=150, minspeed=20, color=(255,255,0),maxduration=2.5,gravityy=3.7,sparksmin=5,sparksmax=20, a1=0,a2=360):

        for s in range(random.randint(sparksmin,sparksmax)):
            v = pygame.math.Vector2(1,0) # vector aiming right (0°)
            a = random.triangular(a1,a2)
            v.rotate_ip(a)
            g = pygame.math.Vector2(0, - gravityy)
            speed = random.randint(minspeed, maxspeed)     #150
            duration = random.random() * maxduration
            Spark(pos=pygame.math.Vector2(pos.x, pos.y), angle=a, move=v*speed,
                  max_age = duration, color=color, gravity = g)

class Spark(VectorSprite):

    def __init__(self, **kwargs):
        VectorSprite.__init__(self, **kwargs)
        if "gravity" not in kwargs:
            self.gravity = pygame.math.Vector2(0, -3.7)

    def _overwrite_parameters(self):
        self._layer = 10000000
        self.kill_on_edge = True

    def create_image(self):
        r,g,b = self.color
        r = randomize_color(r,75)    #50
        g = randomize_color(g,75)
        b = randomize_color(b,75)
        self.image = pygame.Surface((10,10))
        pygame.draw.line(self.image, (r,g,b),
                         (10,5), (5,5), 3)
        pygame.draw.line(self.image, (r,g,b),
                          (5,5), (2,5), 1)
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.image0 = self.image.copy()

    def update(self, seconds):
        VectorSprite.update(self, seconds)
        self.move += self.gravity

class Endanimation(VectorSprite):
    def _overwrite_parameters(self):
        self._layer = 50000
        #self.max_distance = Viewer.width//2
        self.enough = False

    def create_image(self):
        self.image = pygame.Surface((Viewer.width//2, Viewer.height))
        self.image.fill((170, 170, 170))
        pygame.draw.rect(self.image, (110,110,110), (0,0, Viewer.width//2,Viewer.height),40)
        self.image.set_colorkey((0,0,0))
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        
    def update(self, seconds):
        VectorSprite.update(self, seconds)
        if self.distance_traveled >= (Viewer.width / 2):
            self.move = pygame.math.Vector2(0,0)
            if not self.enough:
                self.enough = True
                for _ in range(22):
                    Explosion(pos=pygame.math.Vector2(Viewer.width//2, -random.randint(0, Viewer.height)))
            
            
        
class Rocket(VectorSprite):
    
    def _overwrite_parameters(self):
        self._layer = 1000
        # start?
        self.move = pygame.math.Vector2(Viewer.width // 2, Viewer.height // 2)
        self.move.normalize_ip()
        self.move *= 100 # speed
        if random.random() < 0.5:
            self.angle = 45
            x = 0
        else:
            x = Viewer.width
            self.move.x *= -1
            self.angle = 135
        self.pos = pygame.math.Vector2(x, -Viewer.height)
        self.max_distance = ((Viewer.width/2) ** 2 + (Viewer.height/2) ** 2 )**0.5
        
    def update(self, seconds):
        if self.distance_traveled > self.max_distance:
            Explosion(pos=pygame.math.Vector2(self.pos.x, self.pos.y))
        VectorSprite.update(self, seconds)
        
    
    def create_image(self):
        self.image = pygame.Surface((20, 10))
        self.image.fill((255, 255, 0))
        #pygame.draw.rect(self.image, (255,0,255), (0,0, 19,19),1)
        self.image.set_colorkey((0,0,0))
        self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()

        
    
class Viewer(object):
    width = 0
    height = 0
    menuitems = ["play", "credits", "quit"]
    cursorindex = 0

    def __init__(self, width=640, height=400, fps=30):
        """Initialize pygame, window, background, font,...
           default arguments """
        pygame.init()
        Viewer.width = width    # make global readable
        Viewer.height = height
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill((255,255,255)) # fill background white
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.playtime = 0.0
        self.onshop = False
        self.onexitchar = False
        self.fstart = True
        self.item_list = ["Goldmining License", "Damage Upgrade", "HP Upgrade", "Healing", "Nothing"]
        self.onbuyitem = False
        self.level = 0
        self.showing = False
        self.y = 475
        self.y2 = 500
        # ------ background images ------
        self.backgroundfilenames = [] # every .jpg file in folder 'data'
        try:
            for root, dirs, files in os.walk("data"):
                for file in files:
                    if file[-4:] == ".jpg" or file[-5:] == ".jpeg":
                        self.backgroundfilenames.append(file)
            random.shuffle(self.backgroundfilenames) # remix sort order
        except:
            print("no folder 'data' or no jpg files in it")
        #if len(self.backgroundfilenames) == 0:
        #    print("Error: no .jpg files found")
        #    pygame.quit
        #    sys.exit()
        Viewer.bombchance = 0.015
        Viewer.rocketchance = 0.001
        Viewer.wave = 0
        self.age = 0
        # ------ joysticks ----
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        for j in self.joysticks:
            j.init()
        self.paint()
        self.loadbackground()
        self.loadlevel()
        self.menu_visited = False

    def loadlevel(self, shop=False):
        self.shopActive = shop
        if self.fstart is True:
            with open("shop_pos.txt", "w") as f:
                f.write("a" + str("\n"))
            self.fstart = False
        if self.shopActive is False:
            with open("dungeon.txt", "r") as f:
                self.lines = f.readlines()
        else:
            with open("shop.txt", "r") as f:
                self.lines = f.readlines()
        for y, line in enumerate(self.lines):
            for x, char in enumerate(line):
                if x < len(line)-1:
                    p = pygame.math.Vector2(x * 20+10, -y*20-10)
                    Grid(pos=p)
                if char == "#":
                    p = pygame.math.Vector2(x * 20+10, -y*20-10)
                    Wall(pos=p)
                elif char == "@":
                    if self.shopActive is True:
                        p = pygame.math.Vector2(x * 20+10, -y*20-10)
                        self.player.pos = p
                    else:
                        with open("shop_pos.txt", "r") as f:
                            player_pos = f.readlines()[0]
                        if player_pos != "a\n":
                            player_pos_splitted = player_pos.split(",")
                            p = pygame.math.Vector2(float(player_pos_splitted[0]), -float(player_pos_splitted[1]))
                            self.player.pos.x = float(player_pos_splitted[0])
                            self.player.pos.y = float(player_pos_splitted[1])
                        else:
                            p = pygame.math.Vector2(x * 20+10, -y*20-10)
                            self.player.pos = p
                elif char == "<":
                    p = pygame.math.Vector2(x * 20+10, -y*20-10)
                    StairDown(pos=p)
                elif char == "s":
                    p = pygame.math.Vector2(x * 20+10, -y*20-10)
                    Srock(pos=p)
                elif char == "c":
                    p = pygame.math.Vector2(x * 20+10, -y*20-10)
                    Coin(pos=p)
                elif char == "g":
                    p = pygame.math.Vector2(x * 20+10, -y*20-10)
                    Goldrock(pos=p)
                elif char == "S":
                    p = pygame.math.Vector2(x * 20+10, -y*20-10)
                    Shop(pos=p)
                elif char == "i":
                    p = pygame.math.Vector2(x * 20+10, -y*20-10)
                    n = random.randint(1, len(self.item_list))
                    if n == 1:
                        pass
                    elif n == 2:
                        GoldLicense(pos=p)
                    elif n == 3:
                        Upgrade1(pos=p)
                    elif n == 4:
                        Upgrade2(pos=p)
                    elif n == 5:
                        Healing(pos=p)
                elif char == "e":
                    p = pygame.math.Vector2(x * 20+10, -y*20-10)
                    ExitChar(pos=p)
                elif char == "1":
                    p = pygame.math.Vector2(x * 20+10, -y*20-10)
                    Monster1(pos=p)
                elif char == "2":
                    p = pygame.math.Vector2(x * 20+10, -y*20-10)
                    Monster2(pos=p)
                elif char == "3":
                    p = pygame.math.Vector2(x * 20+10, -y*20-10)
                    Monster3(pos=p)
                elif char == "4":
                    p = pygame.math.Vector2(x * 20+10, -y*20-10)
                    Monster4(pos=p)
                elif char == "J":
                    p = pygame.math.Vector2(x * 20+10, -y*20-10)
                    SecretWall(pos=p)
                elif char == "O":
                    p = pygame.math.Vector2(x * 20+10, -y*20-10)
                    SecretCoin(pos=p)

    def loadbackground(self):

        try:
            self.background = pygame.image.load(os.path.join("data",
                 self.backgroundfilenames[Viewer.wave %
                 len(self.backgroundfilenames)]))
        except:
            self.background = pygame.Surface(self.screen.get_size()).convert()
            self.background.fill((255,255,255)) # fill background white

        self.background = pygame.transform.scale(self.background,
                          (Viewer.width,Viewer.height))
        self.background.convert()


    def paint(self):
        """painting on the surface and create sprites"""
        self.allgroup =  pygame.sprite.LayeredUpdates() # for drawing
        self.explosiongroup = pygame.sprite.Group()
        self.tilegroup = pygame.sprite.Group()
        self.nogogroup = pygame.sprite.Group()
        self.playergroup = pygame.sprite.Group()
        self.stairgroup = pygame.sprite.Group()
        self.digablegroup = pygame.sprite.Group()
        self.coingroup = pygame.sprite.Group()
        self.shopgroup = pygame.sprite.Group()
        self.floorgroup = pygame.sprite.Group()
        self.exitchargroup = pygame.sprite.Group()
        self.pickupgroup = pygame.sprite.Group()
        self.buyablegroup = pygame.sprite.Group()
        self.monstergroup = pygame.sprite.Group()
        self.flytextgroup = pygame.sprite.Group()
        self.secretwallgroup = pygame.sprite.Group()
        self.secretcoingroup = pygame.sprite.Group()
        self.endanimationgroup = pygame.sprite.Group()
        
        VectorSprite.groups = self.allgroup
        Flytext.groups = self.allgroup, self.flytextgroup
        Explosion.groups= self.allgroup, self.explosiongroup
        Wall.groups = self.allgroup, self.tilegroup, self.nogogroup, self.digablegroup
        Coin.groups = self.allgroup, self.tilegroup, self.coingroup
        Srock.groups = self.allgroup, self.tilegroup, self.nogogroup
        Goldrock.groups = self.allgroup, self.tilegroup, self.nogogroup, self.digablegroup
        StairDown.groups = self.allgroup, self.tilegroup, self.stairgroup
        Player.groups = self.allgroup, self.playergroup
        Spark.groups = self.allgroup
        Shop.groups = self.allgroup, self.tilegroup, self.shopgroup
        Grid.groups = self.allgroup, self.tilegroup, self.floorgroup
        ExitChar.groups = self.allgroup, self.tilegroup, self.exitchargroup
        GoldLicense.groups = self.allgroup, self.tilegroup, self.buyablegroup
        Upgrade1.groups = self.allgroup, self.tilegroup, self.buyablegroup
        Upgrade2.groups = self.allgroup, self.tilegroup, self.buyablegroup
        Healing.groups = self.allgroup, self.tilegroup, self.buyablegroup
        Monster.groups = self.allgroup, self.tilegroup, self.monstergroup
        Monster1.groups = self.allgroup, self.tilegroup, self.monstergroup
        Monster2.groups = self.allgroup, self.tilegroup, self.monstergroup
        Monster3.groups = self.allgroup, self.tilegroup, self.monstergroup
        Monster4.groups = self.allgroup, self.tilegroup, self.monstergroup
        SecretWall.groups = self.allgroup, self.tilegroup, self.secretwallgroup, self.nogogroup, self.digablegroup
        SecretCoin.groups = self.allgroup, self.tilegroup, self.secretcoingroup, self.coingroup
        Endanimation.groups = self.allgroup, self.endanimationgroup
        self.player = Player(pos = pygame.math.Vector2(100,-100))
        #Flytext(Viewer.width/2, Viewer.height/2,  "@", color=(255,0,0), duration = 3, fontsize=20)

    def battlerun(self, opponent):
        self.showing = False
        e = opponent.__class__.__name__
        v = int(e[-1])
        if v == 1:
            a = random.randint(5, 13)
            self.battle_max_time = 10
        elif v == 2:
            a = random.randint(7, 10)
            self.battle_max_time = 7
        elif v == 3:
            a = random.randint(4, 10)
            self.battle_max_time = 6
        elif v == 4:
            a = random.randint(1, 10)
            self.battle_max_time = 4
        b = random.randint(3,10)
        c = a * b
        if self.showing != True:
            text = Flytext(1315, 450, "? {} x {} ?".format(a,b), duration = 10, fontsize=30, color=(0,0,200), dy=0)
            self.showing = True
        else:
            return
        running = True
        self.battleage = 0
        self.answer = ""
        while running:
            
            pressed_keys = pygame.key.get_pressed()
            milliseconds = self.clock.tick(self.fps) #
            seconds = milliseconds / 1000
            self.battleage += seconds
            if self.battleage > self.battle_max_time:
                running = False
            # -------- events ------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # ------- pressed and released key ------
                elif event.type == pygame.KEYDOWN:
                    #if event.key == pygame.K_ESCAPE:
                    #    running = False
                    if event.key == pygame.K_0:
                        self.answer += "0"
                    if event.key == pygame.K_1:
                        self.answer += "1"
                    if event.key == pygame.K_2:
                        self.answer += "2"
                    if event.key == pygame.K_3:
                        self.answer += "3"
                    if event.key == pygame.K_4:
                        self.answer += "4"
                    if event.key == pygame.K_5:
                        self.answer += "5"
                    if event.key == pygame.K_6:
                        self.answer += "6"
                    if event.key == pygame.K_7:
                        self.answer += "7"
                    if event.key == pygame.K_8:
                        self.answer += "8"
                    if event.key == pygame.K_9:
                        self.answer += "9"
                    
            
            if self.answer != "":
                #answer = int(self.answer)
                if int(self.answer) == c:
                    text1 = Flytext(1315, self.y, "Correct!", duration = 1.5, fontsize=30, color=(0,0,200), dy=0)
                    text2 = Flytext(1315, self.y2, "Answer: {}".format(c), duration = 1.5, fontsize=30, color=(0,0,200), dy=0)
                    running = False
                    self.showing = False
                    text.kill()
                    # how fast did the player answered...how much time is left
                    return self.battle_max_time - self.battleage
            # delete everything on screen
            self.screen.blit(self.background, (0, 0))
            # ganzes kasterl
            pygame.draw.rect(self.screen, (255, 165, 0), (Viewer.width-230, 0, 230, Viewer.height))
            # oberes hp kasterl
            pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 20, 200, 30), 10)
            # unteres endurance rect
            pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 75, 200, 30), 10)
            
            pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 130, 200, 30), 10)
            
            write(self.screen, "HP: {}/{}".format(self.player.hitpoints, self.player.max_hitpoints), 1315, 200, (255, 0, 0), 20, True)
            write(self.screen, "Endurance: {}/{}".format(self.player.endurance, self.player.max_endurance), 1315, 225, (255, 0, 0), 20, True)
            write(self.screen, "Coins: {}".format(self.player.coins), 1315, 250, (255, 0, 0), 20, True)
            write(self.screen, "FPS: {:6.3}".format(self.clock.get_fps()), 1315, 275, (255, 0, 0), 20, True)
            hp = self.player.hitpoints / ( self.player.max_hitpoints / 100)
            if self.player.hitpoints > 0:
                pygame.draw.rect(self.screen, (0, 255, 0), (Viewer.width-215, 26, int(hp*2), 19))
            ed = self.player.endurance / (self.player.max_endurance / 100)
            if self.player.endurance > 0:
                pygame.draw.rect(self.screen, (0, 150, 200), (Viewer.width-215, 81, int(ed*2), 19))
            bt = self.battleage / (self.battle_max_time / 100)
            pygame.draw.rect(self.screen, (200,0,200), (Viewer.width-215, 136, int(bt*2), 19)) 
            if self.player.hitpoints <= 0:
                self.player.hitpoints = 0
            elif self.player.hitpoints >= self.player.max_hitpoints:
                self.player.hitpoints = 50


            self.flytextgroup.update(seconds)

            # --------- collision detection between target and Explosion -----
            #for e in self.explosiongroup:
            #    crashgroup = pygame.sprite.spritecollide(e, self.targetgroup,
            #                 False, pygame.sprite.collide_circle)
            #    for t in crashgroup:
            #        t.hitpoints -= e.damage
            #        if random.random() < 0.5:
            #            Fire(pos = t.pos, max_age=3, bossnumber=t.number)


            # ----------- clear, draw , update, flip -----------------
            self.allgroup.draw(self.screen)

            # -------- next frame -------------
            pygame.display.flip()
        ### battle over ####
        return 0
    
    def menurun(self):
        running = True
        while running:
            
            pressed_keys = pygame.key.get_pressed()
            milliseconds = self.clock.tick(self.fps) #
            seconds = milliseconds / 1000
            # -------- events ------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # ------- pressed and released key ------
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                    if event.key == pygame.K_UP:
                        Viewer.cursorindex -= 1
                        if Viewer.cursorindex <= 0:
                            Viewer.cursorindex = 0
                    if event.key == pygame.K_DOWN:
                        Viewer.cursorindex += 1
                        if Viewer.cursorindex >= len(Viewer.menuitems):
                            Viewer.cursorindex = len(Viewer.menuitems)-1
                    if event.key == pygame.K_RETURN:
                        activeitem = Viewer.menuitems[Viewer.cursorindex]
                        if activeitem == "play":
                            return
                        elif activeitem == "quit":
                            pygame.quit()
                            
            # delete everything on screen
            self.screen.blit(self.background, (0, 0))
            self.flytextgroup.update(seconds)
            
            # draw menuitems
            for y, i in enumerate(Viewer.menuitems):
                write(self.screen, i, 1280, 100+y*20, color=(0,0,200))
            # draw cursor
            write(self.screen, "-->", 1225, 100+Viewer.cursorindex*20, color=(0,0,random.randint(200,255)))
                
            
            # --------- collision detection between target and Explosion -----
            #for e in self.explosiongroup:
            #    crashgroup = pygame.sprite.spritecollide(e, self.targetgroup,
            #                 False, pygame.sprite.collide_circle)
            #    for t in crashgroup:
            #        t.hitpoints -= e.damage
            #        if random.random() < 0.5:
            #            Fire(pos = t.pos, max_age=3, bossnumber=t.number)


            # ----------- clear, draw , update, flip -----------------
            self.allgroup.draw(self.screen)

            # -------- next frame -------------
            pygame.display.flip()
        ### battle over ####
        return 0
        
        
    def run(self):
        """The mainloop"""
        running = True
        leftcorner = pygame.math.Vector2(0,self.height)
        rightcorner = pygame.math.Vector2(self.width,self.height)
        pygame.mouse.set_visible(False)
        oldleft, oldmiddle, oldright  = False, False, False
        self.snipertarget = None
        gameOver = False
        exittime = 0
        if not self.menu_visited:
            self.menurun()
        while running:
            #print(pygame.key.get_mods())
            pressed_keys = pygame.key.get_pressed()
            milliseconds = self.clock.tick(self.fps) #
            seconds = milliseconds / 1000
            self.playtime += seconds
            if gameOver:
                if self.playtime > exittime:
                    break
            #Game over?
            #if not gameOver:
            # -------- events ------
            self.player.move = pygame.math.Vector2(0,0) # rumstehen
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # ------- pressed and released key ------
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        self.menurun()
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    #=============================================
                    dx = 0
                    dy = 0
                    
                    if event.key == pygame.K_RIGHT:
                        dx = 20
                        
                        x = self.player.pos.x + 20
                        y = self.player.pos.y + 0
                        for c in self.coingroup:
                            if c.pos.x == x and c.pos.y == y:
                                self.player.coins += 1
                                Explosion(pos=pygame.math.Vector2(c.pos.x, c.pos.y), maxduration=0.5, gravityy=0, sparksmin= 10, color = (255, 255, 0))
                                c.kill()
                                break
                        for s in self.shopgroup:
                            if s.pos.x == x and s.pos.y == y:
                                self.onshop = True
                            else:
                                self.onshop = False
                        for e in self.exitchargroup:
                            if e.pos.x == x and e.pos.y == y:
                                self.onexitchar = True
                            else:
                                self.onexitchar = False
                        for b in self.buyablegroup:
                            if b.pos.x == x and b.pos.y == y:
                                self.onbuyitem = True
                            elif self.player.pos.x == b.pos.x and self.player.pos.y == b.pos.y:
                                self.onbuyitem = True
                                
                        if pressed_keys[pygame.K_LSHIFT]:
                            for d in self.digablegroup:
                                for v in self.secretwallgroup:
                                    if v.pos.x == x and v.pos.y == y:
                                        for s in self.secretcoingroup:
                                            if random.random() < 0.1:
                                                Monster4(pos=s.pos)
                                            else:
                                                Coin(pos=s.pos)
                                            for v in self.secretwallgroup:
                                                if v.pos.x == x and v.pos.y == y:
                                                    v.kill()
                                                else:
                                                    Srock(pos=v.pos)
                                                    v.kill()
                                            s.kill()
                                if d.pos.x == x and d.pos.y == y:
                                    if self.player.endurance > 0:
                                        print("buddle nach rechts")
                                        Explosion(pos=pygame.math.Vector2(d.pos.x, d.pos.y), maxduration=0.5, gravityy=0, sparksmin= 10, color = (150, 0, 0))
                                        d.kill()
                                        if self.shopActive is False:
                                            self.player.endurance -= 1
                                        break
                                for s in self.shopgroup:
                                    if s.pos.x != self.player.pos.x and s.pos.y != self.player.pos.y:
                                        self.onshop = False
                                for e in self.exitchargroup:
                                    if e.pos.x != self.player.pos.x and e.pos.y != self.player.pos.y:
                                        self.onexitchar = False
                        # is da was?
                        for w in self.nogogroup:
                            if w.pos.x == x and w.pos.y == y:
                                #Flytext(w.pos.x, -w.pos.y, "Ouch!", color = (255, 0, 0), duration = 0.5, fontsize = 16)
                                ex = w.pos.x-10
                                ey = w.pos.y
                                ep = pygame.math.Vector2(ex,ey)
                                Explosion(pos=ep, maxduration=0.5, gravityy=0, sparksmin= 10, a1 = 100, a2 = 260, color= (255, 0, 255))
                                for s in self.shopgroup:
                                    if s.pos.x == self.player.pos.x and s.pos.y == self.player.pos.y:
                                        self.onshop = True
                                for e in self.exitchargroup:
                                    if e.pos.x == self.player.pos.x and e.pos.y == self.player.pos.y:
                                        self.onexitchar = True
                                for b in self.buyablegroup:
                                    if b.pos.x == self.player.pos.x and b.pos.y == self.player.pos.y:
                                        self.onbuyitem = True
                                break
                        else:
                            # ------------ player wants to go to right ---
                            #---battle? --
                            for m in self.monstergroup:
                                if self.player.pos == m.pos:
                                    if self.showing != True:
                                        dx, dy = 0, 0
                                        # do not move into monster
                                        result = self.battlerun(m)
                                        if result == 0:
                                            self.player.hitpoints -= m.damage
                                        damage = result * self.player.multiplicant
                                        m.hitpoints -= damage    
                                        break                           
                            # -------------
                            for s in self.shopgroup:
                                if self.player.pos.x == s.pos.x and self.player.pos.y == s.pos.y:
                                    self.onshop = False
                            for e in self.exitchargroup:
                                if self.player.pos.x == e.pos.x and self.player.pos.y == e.pos.y:
                                    self.onexitchar = False
                            for b in self.buyablegroup:
                                if b.pos.x == self.player.pos.x and b.pos.y == self.player.pos.y:
                                    self.onbuyitem = False
                                
                            self.player.pos += pygame.math.Vector2(dx,dy)
                            for b in self.buyablegroup:
                                if b.pos.x == self.player.pos.x and b.pos.y == self.player.pos.y:
                                    self.onbuyitem = True
                            self.newturn()
#----------------------------------------------------
                    if event.key == pygame.K_LEFT:
                        dx = -20
                        x = self.player.pos.x - 20
                        y = self.player.pos.y + 0
                        for c in self.coingroup:
                            if c.pos.x == x and c.pos.y == y:
                                self.player.coins += 1
                                Explosion(pos=pygame.math.Vector2(c.pos.x, c.pos.y), maxduration=0.5, gravityy=0, sparksmin= 10, color = (255, 255, 0))
                                c.kill()
                                break
                        for s in self.shopgroup:
                            if s.pos.x == x and s.pos.y == y:
                                self.onshop = True
                            else:
                                self.onshop = False
                        for e in self.exitchargroup:
                            if e.pos.x == x and e.pos.y == y:
                                self.onexitchar = True
                            else:
                                self.onexitchar = False
                        for b in self.buyablegroup:
                            if b.pos.x == x and b.pos.y == y:
                                self.onbuyitem = True
                            elif self.player.pos.x == b.pos.x and self.player.pos.y == b.pos.y:
                                self.onbuyitem = True
                        if pressed_keys[pygame.K_LSHIFT]:
                            for d in self.digablegroup:
                                for v in self.secretwallgroup:
                                    if v.pos.x == x and v.pos.y == y:
                                        for s in self.secretcoingroup:
                                            Coin(pos=s.pos)
                                            for v in self.secretwallgroup:
                                                if v.pos.x == x and v.pos.y == y:
                                                    v.kill()
                                                else:
                                                    Srock(pos=v.pos)
                                                    v.kill()
                                            s.kill()
                                if d.pos.x == x and d.pos.y == y:
                                    if self.player.endurance > 0:
                                        print("buddle nach links")
                                        Explosion(pos=pygame.math.Vector2(d.pos.x, d.pos.y), maxduration=0.5, gravityy=0, sparksmin= 10, color = (150, 0, 0))
                                        d.kill()
                                        if self.shopActive is False:
                                            self.player.endurance -= 1
                                        break
                                for s in self.shopgroup:
                                    if s.pos.x != self.player.pos.x and s.pos.y != self.player.pos.y:
                                        self.onshop = False
                                for e in self.exitchargroup:
                                    if e.pos.x != self.player.pos.x and e.pos.y != self.player.pos.y:
                                        self.onexitchar = False
                        # is da was?
                        for w in self.nogogroup:
                            if w.pos.x == x and w.pos.y == y:
                                #Flytext(w.pos.x, -w.pos.y, "Ouch!", color = (255, 0, 0), duration = 0.5, fontsize = 16)
                                ex = w.pos.x+10
                                ey = w.pos.y
                                ep = pygame.math.Vector2(ex,ey)
                                Explosion(pos=ep, maxduration=0.5, gravityy=0, sparksmin= 10, a1 = 80, a2 = -80, color= (255, 0, 255))
                                for s in self.shopgroup:
                                    if s.pos.x == self.player.pos.x and s.pos.y == self.player.pos.y:
                                        self.onshop = True
                                for e in self.exitchargroup:
                                    if e.pos.x == self.player.pos.x and e.pos.y == self.player.pos.y:
                                        self.onexitchar = True
                                for b in self.buyablegroup:
                                    if b.pos.x == self.player.pos.x and b.pos.y == self.player.pos.y:
                                        self.onbuyitem = True
                                break
                        else:
                            
                            for m in self.monstergroup:
                                if self.player.pos == m.pos:
                                    if self.showing != True:
                                        dx, dy = 0, 0
                                        # do not move into monster
                                        result = self.battlerun(m)
                                        if result == 0:
                                            self.player.hitpoints -= m.damage
                                        damage = result * self.player.multiplicant
                                        m.hitpoints -= damage    
                                        break
                            
                            for s in self.shopgroup:
                                if self.player.pos.x == s.pos.x and self.player.pos.y == s.pos.y:
                                    self.onshop = False
                            for e in self.exitchargroup:
                                if self.player.pos.x == e.pos.x and self.player.pos.y == e.pos.y:
                                    self.onexitchar = False
                            for b in self.buyablegroup:
                                if self.player.pos.x == b.pos.x and self.player.pos.y == b.pos.y:
                                    self.onbuyitem = False
                                elif b.pos.x == x and b.pos.y == y:
                                    self.onbuyitem = True
                            self.player.pos += pygame.math.Vector2(dx,dy)
                            for b in self.buyablegroup:
                                if b.pos.x == self.player.pos.x and b.pos.y == self.player.pos.y:
                                    self.onbuyitem = True
                            self.newturn()
                            
                    if event.key == pygame.K_UP:
                        dy = 20
                        
                        x = self.player.pos.x + 0
                        y = self.player.pos.y + 20
                        for c in self.coingroup:
                            if c.pos.x == x and c.pos.y == y:
                                self.player.coins += 1
                                Explosion(pos=pygame.math.Vector2(c.pos.x, c.pos.y), maxduration=0.5, gravityy=0, sparksmin= 10, color = (255, 255, 0))
                                c.kill()
                                break
                        for s in self.shopgroup:
                            if s.pos.x == x and s.pos.y == y:
                                self.onshop = True
                            else:
                                self.onshop = False
                        for e in self.exitchargroup:
                            if e.pos.x == x and e.pos.y == y:
                                self.onexitchar = True
                            else:
                                self.onexitchar = False
                        for b in self.buyablegroup:
                            if b.pos.x == x and b.pos.y == y:
                                self.onbuyitem = True
                            elif self.player.pos.x == b.pos.x and self.player.pos.y == b.pos.y:
                                self.onbuyitem = True
                        if pressed_keys[pygame.K_LSHIFT]:
                            for d in self.digablegroup:
                                for v in self.secretwallgroup:
                                    if v.pos.x == x and v.pos.y == y:
                                        for s in self.secretcoingroup:
                                            Coin(pos=s.pos)
                                            for v in self.secretwallgroup:
                                                if v.pos.x == x and v.pos.y == y:
                                                    v.kill()
                                                else:
                                                    Srock(pos=v.pos)
                                                    v.kill()
                                            s.kill()
                                if d.pos.x == x and d.pos.y == y:
                                    if self.player.endurance > 0:
                                        print("buddle nach oben")
                                        Explosion(pos=pygame.math.Vector2(d.pos.x, d.pos.y), maxduration=0.5, gravityy=0, sparksmin= 10, color = (150, 0, 0))
                                        d.kill()
                                        if self.shopActive is False:
                                            self.player.endurance -= 1
                                        break
                                for s in self.shopgroup:
                                    if s.pos.x != self.player.pos.x and s.pos.y != self.player.pos.y:
                                        self.onshop = False
                                for e in self.exitchargroup:
                                    if e.pos.x != self.player.pos.x and e.pos.y != self.player.pos.y:
                                        self.onexitchar = False
                        # is da was?
                        for w in self.nogogroup:
                            if w.pos.x == x and w.pos.y == y:
                                #Flytext(w.pos.x, -w.pos.y, "Ouch!", color = (255, 0, 0), duration = 0.5, fontsize = 16)
                                ex = w.pos.x
                                ey = w.pos.y-10
                                ep = pygame.math.Vector2(ex,ey)
                                Explosion(pos=ep, maxduration=0.5, gravityy=0, sparksmin= 10, a1 = -10, a2 = -170, color= (255, 0, 255))
                                for s in self.shopgroup:
                                    if s.pos.x == self.player.pos.x and s.pos.y == self.player.pos.y:
                                        self.onshop = True
                                for e in self.exitchargroup:
                                    if e.pos.x == self.player.pos.x and e.pos.y == self.player.pos.y:
                                        self.onexitchar = True
                                for b in self.buyablegroup:
                                    if b.pos.x == self.player.pos.x and b.pos.y == self.player.pos.y:
                                        self.onbuyitem = True
                                break
                        else:
                            
                            for m in self.monstergroup:
                                if self.player.pos == m.pos:
                                    if self.showing != True:
                                        dx, dy = 0, 0
                                        # do not move into monster
                                        result = self.battlerun(m)
                                        if result == 0:
                                            self.player.hitpoints -= m.damage
                                        damage = result * self.player.multiplicant
                                        m.hitpoints -= damage    
                                        break
                            
                            for s in self.shopgroup:
                                if self.player.pos.x == s.pos.x and self.player.pos.y == s.pos.y:
                                    self.onshop = False
                            for e in self.exitchargroup:
                                if self.player.pos.x == e.pos.x and self.player.pos.y == e.pos.y:
                                    self.onexitchar = False
                            for b in self.buyablegroup:
                                if self.player.pos.x == b.pos.x and self.player.pos.y == b.pos.y:
                                    self.onbuyitem = False
                                elif b.pos.x == x and b.pos.y == y:
                                    self.onbuyitem = True
                            self.player.pos += pygame.math.Vector2(dx,dy)
                            for b in self.buyablegroup:
                                if b.pos.x == self.player.pos.x and b.pos.y == self.player.pos.y:
                                    self.onbuyitem = True
                            self.newturn()
                            
                    if event.key == pygame.K_DOWN:
                        dy = -20
                        x = self.player.pos.x + 0
                        y = self.player.pos.y - 20
                        for c in self.coingroup:
                            if c.pos.x == x and c.pos.y == y:
                                self.player.coins += 1
                                Explosion(pos=pygame.math.Vector2(c.pos.x, c.pos.y), maxduration=0.5, gravityy=0, sparksmin= 10, color = (255, 255, 0))
                                c.kill()
                                break
                        for s in self.shopgroup:
                            if s.pos.x == x and s.pos.y == y:
                                self.onshop = True
                            else:
                                self.onshop = False
                        for e in self.exitchargroup:
                            if e.pos.x == x and e.pos.y == y:
                                self.onexitchar = True
                            else:
                                self.onexitchar = False
                        for b in self.buyablegroup:
                            if b.pos.x == x and b.pos.y == y:
                                self.onbuyitem = True
                            elif self.player.pos.x == b.pos.x and self.player.pos.y == b.pos.y:
                                self.onbuyitem = True
                        if pressed_keys[pygame.K_LSHIFT]:
                            for d in self.digablegroup:
                                for v in self.secretwallgroup:
                                    if v.pos.x == x and v.pos.y == y:
                                        for s in self.secretcoingroup:
                                            Coin(pos=s.pos)
                                            for v in self.secretwallgroup:
                                                if v.pos.x == x and v.pos.y == y:
                                                    v.kill()
                                                else:
                                                    Srock(pos=v.pos)
                                                    v.kill()
                                            s.kill()
                                if d.pos.x == x and d.pos.y == y:
                                    if self.player.endurance > 0:
                                        print("buddle nach unten")
                                        Explosion(pos=pygame.math.Vector2(d.pos.x, d.pos.y), maxduration=0.5, gravityy=0, sparksmin= 10, color = (150, 0, 0))
                                        d.kill()
                                        if self.shopActive is False:
                                            self.player.endurance -= 1
                                        break
                                for s in self.shopgroup:
                                    if s.pos.x != self.player.pos.x and s.pos.y != self.player.pos.y:
                                        self.onshop = False
                                for e in self.exitchargroup:
                                    if e.pos.x != self.player.pos.x and e.pos.y != self.player.pos.y:
                                        self.onexitchar = False
                        # is da was?
                        for w in self.nogogroup:
                            if w.pos.x == x and w.pos.y == y:
                                #Flytext(w.pos.x, -w.pos.y, "Ouch!", color = (255, 0, 0), duration = 0.5, fontsize = 16)
                                ex = w.pos.x
                                ey = w.pos.y+10
                                ep = pygame.math.Vector2(ex,ey)
                                Explosion(pos=ep, maxduration=0.5, gravityy=0, sparksmin= 10, a1 = 10, a2 = 170, color= (255, 0, 255))
                                for s in self.shopgroup:
                                    if s.pos.x == self.player.pos.x and s.pos.y == self.player.pos.y:
                                        self.onshop = True
                                for e in self.exitchargroup:
                                    if e.pos.x == self.player.pos.x and e.pos.y == self.player.pos.y:
                                        self.onexitchar = True
                                for b in self.buyablegroup:
                                    if b.pos.x == self.player.pos.x and b.pos.y == self.player.pos.y:
                                        self.onbuyitem = True
                                break
                        else:
                            
                            for m in self.monstergroup:
                                if self.player.pos == m.pos:
                                    if self.showing != True:
                                        dx, dy = 0, 0
                                        # do not move into monster
                                        result = self.battlerun(m)
                                        if result == 0:
                                            self.player.hitpoints -= m.damage
                                        damage = result * self.player.multiplicant
                                        m.hitpoints -= damage    
                                        break
                            
                            for s in self.shopgroup:
                                if self.player.pos.x == s.pos.x and self.player.pos.y == s.pos.y:
                                    self.onshop = False
                            for e in self.exitchargroup:
                                if self.player.pos.x == e.pos.x and self.player.pos.y == e.pos.y:
                                    self.onexitchar = False
                            for b in self.buyablegroup:
                                if self.player.pos.x == b.pos.x and self.player.pos.y == b.pos.y:
                                    self.onbuyitem = False
                                elif b.pos.x == x and b.pos.y == y:
                                    self.onbuyitem = True
                            self.player.pos += pygame.math.Vector2(dx,dy)
                            for b in self.buyablegroup:
                                if b.pos.x == self.player.pos.x and b.pos.y == self.player.pos.y:
                                    self.onbuyitem = True
                            self.newturn()
                    
                    if event.key == pygame.K_k:
                        self.level = 13
                    
                    if event.key == pygame.K_LESS:
                        for s in self.stairgroup:
                            if s.pos.x == self.player.pos.x and s.pos.y == self.player.pos.y:
                                #Viewer.numbers = {}
                                #---- GOINg down the stairs ------
                                self.level += 1
                                if self.level >= 14:
                                    pos = pygame.math.Vector2(1000, -800)
                                    Endanimation(pos = pygame.math.Vector2(-Viewer.width *.25, -Viewer.height//2),
                                                 move = pygame.math.Vector2(100,0))
                                    Endanimation(pos = pygame.math.Vector2(Viewer.width * 1.25, -Viewer.height//2),
                                                 move = pygame.math.Vector2(-100,0))
                                    #Flytext(500,500,"You escaped from the dungeon of math", color=(255, 0, 0))
                                    Rocket()
                                    Rocket()
                                    Rocket()
                                    Rocket()
                                for tile in self.tilegroup:
                                    tile.kill()
                                self.player.endurance = self.player.max_endurance
                                dungeonGenerator.start()
                                with open("shop_pos.txt", "w") as f:
                                    f.write("a\n")
                                self.loadlevel()
                    if event.key == pygame.K_RETURN:
                        if self.onshop is True and self.shopActive is False:
                            with open("shop_pos.txt", "w") as f:
                                for s in self.shopgroup:
                                    f.write(str(s.pos.x) + "," + str(s.pos.y))
                            for tile in self.tilegroup:
                                    tile.kill()
                            self.loadlevel(shop=True)
                    if event.key == pygame.K_SPACE:
                        self.newturn()
                    if event.key == pygame.K_e:
                        if self.onexitchar is True:
                            for tile in self.tilegroup:
                                tile.kill()
                            self.loadlevel()
                    if event.key == pygame.K_b:
                        if self.onbuyitem is True:
                            for b in self.buyablegroup:
                                if b.pos == self.player.pos:
                                    if b.item_name not in self.player.inventory:
                                        if self.player.coins >= b.item_price:
                                            if b.item_name == "Damage Upgrade":
                                                self.player.multiplicant += 1.5
                                            elif b.item_name == "HP Upgrade":
                                                self.player.max_hitpoints += 20
                                                self.player.hitpoints += 10
                                            elif b.item_name == "Healing":
                                                self.player.hitpoints += 20
                                            self.player.coins -= b.item_price
                                            self.player.inventory.append(b.item_name)
                                            b.kill()
                                            self.onbuyitem = False
                                        else:
                                            Flytext(1315, 575, "Not enough", duration = 1.5, fontsize=30, color=(0,0,200), dy=0)
                                            Flytext(1315, 600, "coins!", duration = 1.5, fontsize=30, color=(0,0,200), dy=0)
                                    else:
                                        Flytext(1315, 575, "You already", duration = 1.5, fontsize=30, color=(0,0,200), dy=0)
                                        Flytext(1315, 600, "bought this!", duration = 1.5, fontsize=30, color=(0,0,200), dy=0)
                                        
            
            # delete everything on screen
            self.screen.blit(self.background, (0, 0))
            # ganzes kasterl
            pygame.draw.rect(self.screen, (255, 165, 0), (Viewer.width-230, 0, 230, Viewer.height))
            # oberes hp kasterl
            pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 20, 200, 30), 10)
            # unteres endurance rect
            pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 75, 200, 30), 10)
            
            
            
            write(self.screen, "HP: {}/{}".format(self.player.hitpoints, self.player.max_hitpoints), 1315, 200, (255, 0, 0), 20, True)
            write(self.screen, "Endurance: {}/{}".format(self.player.endurance, self.player.max_endurance), 1315, 225, (255, 0, 0), 20, True)
            write(self.screen, "Multiplicant: {}".format(self.player.multiplicant), 1315, 250, (255, 0, 0), 20, True)
            write(self.screen, "Coins: {}".format(self.player.coins), 1315, 275, (255, 0, 0), 20, True)
            write(self.screen, "Level: {}".format(self.level), 1315, 300, (255, 0, 0), 20, True)
            write(self.screen, "FPS: {:6.3}".format(self.clock.get_fps()), 1315, 325, (255, 0, 0), 20, True)
            if self.onshop is True and self.shopActive is False:
                write(self.screen, "Standing on SHOP.", 1315, 450, (255, 0, 0), 20, True)
                write(self.screen, "Press ENTER", 1315, 475, (255, 0, 0), 20, True)
                write(self.screen, "to enter!", 1315, 500, (255, 0, 0), 20, True)
            elif self.onexitchar is True and self.shopActive is True:
                write(self.screen, "Standing on EXIT.", 1315, 450, (255, 0, 0), 20, True)
                write(self.screen, "Press E", 1315, 475, (255, 0, 0), 20, True)
                write(self.screen, "to [e]xit!", 1315, 500, (255, 0, 0), 20, True)
            elif self.onbuyitem is True and self.shopActive is True:
                for b in self.buyablegroup:
                    if b.pos.x == self.player.pos.x and b.pos.y == self.player.pos.y:
                        price = b.get_item_price()
                        name = b.get_item_name()
                write(self.screen, "Standing on:", 1315, 450, (255, 0, 0), 20, True)
                write(self.screen, "{}.".format(name), 1315, 475, (255, 0, 0), 20, True)
                write(self.screen, "Costs: {}.".format(price), 1315, 500, (255, 0, 0), 20, True)
                write(self.screen, "Press B", 1315, 525, (255, 0, 0), 20, True)
                write(self.screen, "to [b]uy!", 1315, 550, (255, 0, 0), 20, True)
            # hp = self.player.hitpoints
            # hpfull = self.player.max_hitpoints
            hp = self.player.hitpoints / ( self.player.max_hitpoints / 100)
            #50 / ( 50 / 100)
            if self.player.hitpoints > 0:
                pygame.draw.rect(self.screen, (0, 255, 0), (Viewer.width-215, 26, int(hp*2), 19))
            ed = self.player.endurance / (self.player.max_endurance / 100)
            if self.player.endurance > 0:
                pygame.draw.rect(self.screen, (0, 150, 200), (Viewer.width-215, 81, int(ed*2), 19))

            if self.player.hitpoints <= 0:
                self.player.hitpoints = 0
            elif self.player.hitpoints >= self.player.max_hitpoints:
                self.player.hitpoints = self.player.max_hitpoints


            self.allgroup.update(seconds)

            # --------- collision detection between target and Explosion -----
            #for e in self.explosiongroup:
            #    crashgroup = pygame.sprite.spritecollide(e, self.targetgroup,
            #                 False, pygame.sprite.collide_circle)
            #    for t in crashgroup:
            #        t.hitpoints -= e.damage
            #        if random.random() < 0.5:
            #            Fire(pos = t.pos, max_age=3, bossnumber=t.number)


            # ----------- clear, draw , update, flip -----------------
            self.allgroup.draw(self.screen)

            # -------- next frame -------------
            pygame.display.flip()
        #-----------------------------------------------------
        pygame.mouse.set_visible(True)
        pygame.quit()
    
    def newturn(self):
        for m in self.monstergroup:
                # will monster wandern?
                if random.random() < m.p_moving:
                    #dx, dy = random.choice(((20,0), (-20,0), (0, 20), (0,-20)))
                    dx, dy = m.ai(target = self.player)
                    for n in self.nogogroup:
                        if n.pos.x == m.pos.x + dx and n.pos.y == m.pos.y + dy:
                            if dx > 0:
                                b1, b2 = 100, 260
                            if dx < 0:
                                b1, b2 = 80, -80
                            if dy > 0:
                                b1, b2 = 10, 170
                            if dy < 0:
                                b1, b2 = -10, -170
                            
                            Explosion(pos=m.pos + pygame.math.Vector2(dx//2,dy//2), maxduration=0.5, gravityy=0, sparksmin= 10, a1 = b1, a2 = b2, color= (255, 0, 255))
                            dx, dy = 0,0
                        #else:
                        #    m.pos += pygame.math.Vector2(dx, dy)
                    # move the monster
                    # moving into player?
                    if m.pos + pygame.math.Vector2(dx, dy) == self.player.pos:
                        Flytext(x=m.pos.x, y=-m.pos.y, text="attacking player")
                        bonustime = self.battlerun(m)
                        if bonustime == 0:
                            self.player.hitpoints -= m.damage
                        damage = bonustime * self.player.multiplicant
                        m.hitpoints -= damage
                        if m.hitpoints <= 0:
                            self.player.coins += random.randint(1, 10)
                        # TODO: Fight-System
                        return
                    
                    # 1 monster moving into 2 monster
                    myclass = m.__class__.__name__ 
                    for m2 in self.monstergroup:
                        if m2.number == m.number:
                            continue
                        if m.pos + pygame.math.Vector2(dx, dy) == m2.pos:
                            #collision
                            otherclass = m2.__class__.__name__
                            if myclass == "Monster1" and otherclass == "Monster1":
                                Monster2(pos=pygame.math.Vector2(m.pos + pygame.math.Vector2(dx, dy)))
                                Flytext(x=m2.pos.x, y=-m.pos.y, text="merging")
                                m.hitpoints = 0
                                m2.hitpoints = 0
                                break
                            elif myclass == "Monster2" and otherclass == "Monster2":
                                Monster3(pos=pygame.math.Vector2(m.pos + pygame.math.Vector2(dx, dy)))
                                Flytext(x=m2.pos.x, y=-m.pos.y, text="merging")
                                m.hitpoints = 0
                                m2.hitpoints = 0
                                break
                            elif myclass == "Monster3" and otherclass == "Monster3":
                                Monster4(pos=pygame.math.Vector2(m.pos + pygame.math.Vector2(dx, dy)))
                                Flytext(x=m2.pos.x, y=-m.pos.y, text="merging")
                                m.hitpoints = 0
                                m2.hitpoints = 0
                                break
                            # 1 v 2 oder sonstige
                            break
                        #else:
                    # no collision, move please
                    else:
                        m.pos += pygame.math.Vector2(dx, dy)
                    
    
if __name__ == '__main__':
    Viewer(1430,800).run() # try Viewer(800,600).run()
