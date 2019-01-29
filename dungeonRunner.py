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

"""Best game: 10 waves by Ines"""

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
        self._layer = 7  # order of sprite layers (before / behind other sprites)
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

#class Mouse(pygame.sprite.Sprite):
#    def __init__(self, radius = 50, color=(255,0,0), x=320, y=240,
#                    startx=100,starty=100, control="mouse", ):
#        """create a (black) surface and paint a blue Mouse on it"""
#        self._layer=10
#        pygame.sprite.Sprite.__init__(self,self.groups)
#        self.radius = radius
#        self.color = color
#        self.startx=startx
#        self.starty=starty
#        self.x = x
#        self.y = y
#        self.dx = 0
#        self.dy = 0
#        self.r = color[0]
#        self.g = color[1]
#        self.b = color[2]
#        self.delta = -10
#        self.age = 0
#        self.pos = pygame.mouse.get_pos()
#        self.move = 0
#        self.tail=[]
#        self.create_image()
#        self.rect = self.image.get_rect()
#        self.control = control # "mouse" "keyboard1" "keyboard2"
#        self.pushed = False
#
#    def create_image(self):
#
#        self.image = pygame.surface.Surface((self.radius*0.5, self.radius*0.5))
#        delta1 = 12.5
#        delta2 = 25
#        w = self.radius*0.5 / 100.0
#        h = self.radius*0.5 / 100.0
#        # pointing down / up
#        for y in (0,2,4):
#            pygame.draw.line(self.image,(self.r-delta2,self.g,self.b),
#                         (35*w,0+y),(50*w,15*h+y),2)
#            pygame.draw.line(self.image,(self.r-delta2,self.g,self.b),
#                         (50*w,15*h+y),(65*w,0+y),2)##
#
#            pygame.draw.line(self.image,(self.r-delta2,self.g,self.b),
#                         (35*w,100*h-y),(50*w,85*h-y),2)
#            pygame.draw.line(self.image,(self.r-delta2,self.g,self.b),
#                         (50*w,85*h-y),(65*w,100*h-y),2)
#        # pointing right / left
#        for x in (0,2,4):
#            pygame.draw.line(self.image,(self.r-delta2,self.g,self.b),
#                         (0+x,35*h),(15*w+x,50*h),2)
#            pygame.draw.line(self.image,(self.r-delta2,self.g,self.b),
#                         (15*w+x,50*h),(0+x,65*h),2)##
#
#            pygame.draw.line(self.image,(self.r-delta2,self.g,self.b),
#                         (100*w-x,35*h),(85*w-x,50*h),2)
#            pygame.draw.line(self.image,(self.r-delta2,self.g,self.b),
#                         (85*w-x,50*h),(100*w-x,65*h),2)
#        self.image.set_colorkey((0,0,0))
#        self.rect=self.image.get_rect()
#        self.rect.center = self.x, self.y##
#
#    def update(self, seconds):
#        if self.control == "keyboard2":
#            pressed = pygame.key.get_pressed()
#            if pressed[pygame.K_RSHIFT]:
#                delta = 2
#            else:
#                delta = 9
#            if pressed[pygame.K_UP]:
#                self.y -= delta
#            if pressed[pygame.K_DOWN]:
#                self.y += delta
#            if pressed[pygame.K_LEFT]:
#                self.x -= delta
#            if pressed[pygame.K_RIGHT]:
#                self.x += delta
#        self.create_image()##

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
        self.rect.center = (-300,-300) # avoid blinking image in topleft corner
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
            self.pos = pygame.math.Vector2(random.randint(0, PygView.width),-50)
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
                #self.pos = v.Vec2d(boss.pos.x, boss.pos.y)
                self.pos = pygame.math.Vector2(boss.pos.x, boss.pos.y)
        self.pos += self.move * seconds
        self.distance_traveled += self.move.length() * seconds
        self.age += seconds
        self.rect.center = ( round(self.pos.x, 0), -round(self.pos.y, 0) )

class Player(VectorSprite):

    def _overwrite_parameters(self):
        self._layer = 5
        self.phitpoints = 50
        self.max_phitpoints = 50
        self.endurance = 100
        self.max_endurance = 100
        self.coins = 0

    def create_image(self):
        self.fontsize = 32
        self.color = (255, 0, 255)
        self.text = "@"
        self.image = make_text(self.text, self.color, self.fontsize)
        self.image.set_colorkey((0, 0, 0))
        self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
        
class Grid(VectorSprite):

    def _overwrite_parameters(self):
        self._layer = -10

    def create_image(self):
        self.image = pygame.Surface((20, 20))
        pygame.draw.rect(self.image, (229,229,229), (0,0, 19,19),1)
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

class Floor(VectorSprite):

    def _overwrite_parameters(self):
        self._layer = -5

    def create_image(self):
        self.image = pygame.Surface((20, 20))
        self.image.fill((255, 255, 255))
        pygame.draw.rect(self.image, (229,229,229), (0,0, 19,19),1)
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

class Smoke(VectorSprite):

    def create_image(self):
        self.image = pygame.Surface((50,50))
        pygame.draw.circle(self.image, self.color, (25,25),
                           int(self.age*3))
        self.image.set_colorkey((0,0,0))
        self.image.convert_alpha()
        self.rect = self.image.get_rect()

    def update(self, seconds):
        VectorSprite.update(self, seconds)
        if self.gravity is not None:
            self.move += self.gravity * seconds
        self.create_image()
        self.rect=self.image.get_rect()
        self.rect.center=(self.pos.x, self.pos.y)
        c = int(self.age * 100)
        c = min(255,c)
        self.color=(c,c,c)


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
        self._layer = 8
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

class Rocket(VectorSprite):

    def __init__(self, **kwargs):
        self.readyToLaunchTime = 0
        VectorSprite.__init__(self, **kwargs)

        self.damage = 3
        self.color = (255,156,0)
        self.create_image()

    def _overwrite_parameters(self):
        self._layer = 1

    def create_image(self):
        self.angle = 90
        self.image = pygame.Surface((20,10))
        pygame.draw.polygon(self.image, self.color, [(0,0),(5,0), (20,5), (5,10), (0,10), (5,5)])
        self.image.set_colorkey((0,0,0))
        self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
        self.set_angle(self.angle)

    def update(self, seconds):
        # --- speed limit ---
        if self.move.length() != self.speed:
            if self.move.length() < 0:
                self.move = self.move.normalize() * self.speed
            else:
                pass
        if self.move.length() > 0:
            self.set_angle(-self.move.angle_to(pygame.math.Vector2(-1,0)))
            self.move = self.move.normalize() * self.speed
            # --- Smoke ---
            if random.random() < 0.2 and self.age > 0.1:
                Smoke(pos=pygame.math.Vector2(self.pos.x, self.pos.y),
                   gravity=pygame.math.Vector2(0,4), max_age = 4)
        self.oldage = self.age
        VectorSprite.update(self, seconds)
        # new rockets are stored offscreen 500 pixel below PygView.height
        if self.age > self.readyToLaunchTime and self.oldage < self.readyToLaunchTime:
            self.pos.y -= 500

    def kill(self):
        Explosion(pos=pygame.math.Vector2(self.pos.x, self.pos.y),max_age=2.1, color=(200,255,255), damage = self.damage)
        VectorSprite.kill(self)



class PygView(object):
    width = 0
    height = 0

    def __init__(self, width=640, height=400, fps=30):
        """Initialize pygame, window, background, font,...
           default arguments """
        pygame.init()
        PygView.width = width    # make global readable
        PygView.height = height
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill((255,255,255)) # fill background white
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.playtime = 0.0
        self.onshop = False
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
        PygView.bombchance = 0.015
        PygView.rocketchance = 0.001
        PygView.wave = 0
        self.age = 0
        # ------ joysticks ----
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        for j in self.joysticks:
            j.init()
        self.paint()
        self.loadbackground()
        self.loadlevel()

    def loadlevel(self):
        with open("dungeon.txt", "r") as f:
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
                elif char == ".":
                    p = pygame.math.Vector2(x * 20+10, -y*20-10)
                    Floor(pos=p)


    def loadbackground(self):

        try:
            self.background = pygame.image.load(os.path.join("data",
                 self.backgroundfilenames[PygView.wave %
                 len(self.backgroundfilenames)]))
        except:
            self.background = pygame.Surface(self.screen.get_size()).convert()
            self.background.fill((255,255,255)) # fill background white

        self.background = pygame.transform.scale(self.background,
                          (PygView.width,PygView.height))
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

        VectorSprite.groups = self.allgroup
        Flytext.groups = self.allgroup
        Explosion.groups= self.allgroup, self.explosiongroup
        Wall.groups = self.allgroup, self.tilegroup, self.nogogroup, self.digablegroup
        Coin.groups = self.allgroup, self.tilegroup, self.coingroup
        Srock.groups = self.allgroup, self.tilegroup, self.nogogroup
        Goldrock.groups = self.allgroup, self.tilegroup, self.nogogroup
        StairDown.groups = self.allgroup, self.tilegroup, self.stairgroup
        Player.groups = self.allgroup, self.playergroup
        Spark.groups = self.allgroup
        Shop.groups = self.allgroup, self.shopgroup
        Floor.groups = self.allgroup, self.floorgroup
        Grid.groups = self.allgroup, self.floorgroup

        self.player = Player(pos = pygame.math.Vector2(100,-100))
        #Flytext(PygView.width/2, PygView.height/2,  "@", color=(255,0,0), duration = 3, fontsize=20)

    def run(self):
        """The mainloop"""
        running = True
        pygame.mouse.set_visible(False)
        oldleft, oldmiddle, oldright  = False, False, False
        self.snipertarget = None
        gameOver = False
        exittime = 0
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
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    if event.key == pygame.K_RIGHT:
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
                        if pressed_keys[pygame.K_LSHIFT]:
                            for d in self.digablegroup:
                                if d.pos.x == x and d.pos.y == y:
                                    if self.player.endurance > 0:
                                        print("buddle nach rechts")
                                        Explosion(pos=pygame.math.Vector2(d.pos.x, d.pos.y), maxduration=0.5, gravityy=0, sparksmin= 10, color = (150, 0, 0))
                                        d.kill()
                                        self.player.endurance -= 1
                                        break
                                for s in self.shopgroup:
                                    if s.pos.x != self.player.pos.x and s.pos.y != self.player.pos.y:
                                        self.onshop = False
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
                                break
                        else:
                            for s in self.shopgroup:
                                if self.player.pos.x == s.pos.x and self.player.pos.y == s.pos.y:
                                    self.onshop = False
                            self.player.pos += pygame.math.Vector2(20,0)
                            
                    if event.key == pygame.K_LEFT:
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
                        if pressed_keys[pygame.K_LSHIFT]:
                            for d in self.digablegroup:
                                if d.pos.x == x and d.pos.y == y:
                                    if self.player.endurance > 0:
                                        print("buddle nach links")
                                        Explosion(pos=pygame.math.Vector2(d.pos.x, d.pos.y), maxduration=0.5, gravityy=0, sparksmin= 10, color = (150, 0, 0))
                                        d.kill()
                                        self.player.endurance -= 1
                                        break
                                for s in self.shopgroup:
                                    if s.pos.x != self.player.pos.x and s.pos.y != self.player.pos.y:
                                        self.onshop = False
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
                                break
                        else:
                            for s in self.shopgroup:
                                if self.player.pos.x == s.pos.x and self.player.pos.y == s.pos.y:
                                    self.onshop = False
                            self.player.pos += pygame.math.Vector2(-20,0)
                    if event.key == pygame.K_UP:
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
                        if pressed_keys[pygame.K_LSHIFT]:
                            for d in self.digablegroup:
                                if d.pos.x == x and d.pos.y == y:
                                    if self.player.endurance > 0:
                                        print("buddle nach oben")
                                        Explosion(pos=pygame.math.Vector2(d.pos.x, d.pos.y), maxduration=0.5, gravityy=0, sparksmin= 10, color = (150, 0, 0))
                                        d.kill()
                                        self.player.endurance -= 1
                                        break
                                for s in self.shopgroup:
                                    if s.pos.x != self.player.pos.x and s.pos.y != self.player.pos.y:
                                        self.onshop = False
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
                                break
                        else:
                            for s in self.shopgroup:
                                if self.player.pos.x == s.pos.x and self.player.pos.y == s.pos.y:
                                    self.onshop = False
                            self.player.pos += pygame.math.Vector2(0,20)
                    if event.key == pygame.K_DOWN:
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
                        if pressed_keys[pygame.K_LSHIFT]:
                            for d in self.digablegroup:
                                if d.pos.x == x and d.pos.y == y:
                                    if self.player.endurance > 0:
                                        print("buddle nach unten")
                                        Explosion(pos=pygame.math.Vector2(d.pos.x, d.pos.y), maxduration=0.5, gravityy=0, sparksmin= 10, color = (150, 0, 0))
                                        d.kill()
                                        self.player.endurance -= 1
                                        break
                                for s in self.shopgroup:
                                    if s.pos.x != self.player.pos.x and s.pos.y != self.player.pos.y:
                                        self.onshop = False
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
                                break
                        else:
                            for s in self.shopgroup:
                                if self.player.pos.x == s.pos.x and self.player.pos.y == s.pos.y:
                                    self.onshop = False
                            self.player.pos += pygame.math.Vector2(0,-20)

                    if event.key == pygame.K_LESS:
                        for s in self.stairgroup:
                            if s.pos.x == self.player.pos.x and s.pos.y == self.player.pos.y:
                                #PygView.numbers = {}
                                for tile in self.tilegroup:
                                    tile.kill()
                                self.player.endurance = self.player.max_endurance
                                dungeonGenerator.start()
                                self.loadlevel()
                    if event.key == pygame.K_RETURN:
                        if self.onshop is True:
                            print("hi")
                            
            # delete everything on screen
            self.screen.blit(self.background, (0, 0))
            # ganzes kasterl
            pygame.draw.rect(self.screen, (255, 165, 0), (PygView.width-230, 0, 230, PygView.height))
            # oberes hp kasterl
            pygame.draw.rect(self.screen, (133, 11, 133), (PygView.width-215, 20, 200, 30), 10)
            # unteres endurance rect
            pygame.draw.rect(self.screen, (133, 11, 133), (PygView.width-215, 75, 200, 30), 10)
            write(self.screen, "HP: {}/{}".format(self.player.phitpoints, self.player.max_phitpoints), 1315, 200, (255, 0, 0), 20, True)
            write(self.screen, "Endurance: {}/{}".format(self.player.endurance, self.player.max_endurance), 1315, 225, (255, 0, 0), 20, True)
            write(self.screen, "Coins: {}".format(self.player.coins), 1315, 250, (255, 0, 0), 20, True)
            if self.onshop is True:
                write(self.screen, "Standing on shop.", 1315, 450, (255, 0, 0), 20, True)
                write(self.screen, "Press ENTER!", 1315, 475, (255, 0, 0), 20, True)
            # hp = self.player.phitpoints
            # hpfull = self.player.max_phitpoints
            hp = self.player.phitpoints / ( self.player.max_phitpoints / 100)
            #50 / ( 50 / 100)
            if self.player.phitpoints > 0:
                pygame.draw.rect(self.screen, (0, 255, 0), (PygView.width-215, 26, int(hp*2), 19))
            ed = self.player.endurance / (self.player.max_endurance / 100)
            if self.player.endurance > 0:
                pygame.draw.rect(self.screen, (0, 150, 200), (PygView.width-215, 81, int(ed*2), 19))

            if self.player.phitpoints <= 0:
                self.player.phitpoints = 0
            elif self.player.phitpoints >= self.player.max_phitpoints:
                self.player.phitpoints = 50


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

if __name__ == '__main__':
    PygView(1430,800).run() # try PygView(800,600).run()
