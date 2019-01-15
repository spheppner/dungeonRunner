# -*- coding: utf-8 -*-
"""
menu system for pygame
"""

import vectorclass2d as v
import pygame 
import textscroller_vertical
import dungeonRunner
import dungeonGenerator
import random
import sys
import os.path

class Mouse(pygame.sprite.Sprite):
    def __init__(self, radius = 50, color=(255,0,0), x=320, y=240,
                    startx=100,starty=100, control="mouse", ):
        """create a (black) surface and paint a blue Mouse on it"""
        self._layer=10
        pygame.sprite.Sprite.__init__(self,self.groups)
        self.radius = radius
        self.color = color
        self.startx=startx
        self.starty=starty
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.r = color[0]
        self.g = color[1]
        self.b = color[2]
        self.delta = -10
        self.age = 0
        self.pos = pygame.mouse.get_pos()
        self.move = 0
        self.tail=[]
        self.create_image()
        self.rect = self.image.get_rect()
        self.control = control # "mouse" "keyboard1" "keyboard2"
        
    def create_image(self):
        
        self.image = pygame.surface.Surface((self.radius*0.5, self.radius*0.5))
        delta1 = 12.5
        delta2 = 25
        w = self.radius*0.5 / 100.0
        h = self.radius*0.5 / 100.0
        # pointing down / up
        for y in (0,2,4):
            pygame.draw.line(self.image,(self.r-delta2,self.g,self.b),
                         (35*w,0+y),(50*w,15*h+y),2)
            pygame.draw.line(self.image,(self.r-delta2,self.g,self.b),
                         (50*w,15*h+y),(65*w,0+y),2)
    
            pygame.draw.line(self.image,(self.r-delta2,self.g,self.b),
                         (35*w,100*h-y),(50*w,85*h-y),2)
            pygame.draw.line(self.image,(self.r-delta2,self.g,self.b),
                         (50*w,85*h-y),(65*w,100*h-y),2)
        # pointing right / left                 
        for x in (0,2,4):
            pygame.draw.line(self.image,(self.r-delta2,self.g,self.b),
                         (0+x,35*h),(15*w+x,50*h),2)
            pygame.draw.line(self.image,(self.r-delta2,self.g,self.b),
                         (15*w+x,50*h),(0+x,65*h),2)
            
            pygame.draw.line(self.image,(self.r-delta2,self.g,self.b),
                         (100*w-x,35*h),(85*w-x,50*h),2)
            pygame.draw.line(self.image,(self.r-delta2,self.g,self.b),
                         (85*w-x,50*h),(100*w-x,65*h),2)
            
       # for delta in (-2, 0, 2 ):
       #     pygame.draw.circle(self.image, (self.r, self.g, self.b), 
       #               (self.radius//2,self.radius//2), self.radius-delta, 1)
        
        self.image.set_colorkey((0,0,0))
        self.rect=self.image.get_rect()
        self.rect.center = self.x, self.y
        
    def update(self, seconds):
        if self.control == "mouse":
            self.x, self.y = pygame.mouse.get_pos()
        elif self.control == "keyboard1":
            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_LSHIFT]:
                delta = 2
            else:
                delta = 9
            if pressed[pygame.K_w]:
                self.y -= delta
            if pressed[pygame.K_s]:
                self.y += delta
            if pressed[pygame.K_a]:
                self.x -= delta
            if pressed[pygame.K_d]:
                self.x += delta
        elif self.control == "keyboard2":
            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_RSHIFT]:
                delta = 2
            else:
                delta = 9
            if pressed[pygame.K_UP]:
                self.y -= delta
            if pressed[pygame.K_DOWN]:
                self.y += delta
            if pressed[pygame.K_LEFT]:
                self.x -= delta
            if pressed[pygame.K_RIGHT]:
                self.x += delta
        elif self.control == "joystick1":
            pass 
        elif self.control == "joystick2":
            pass
        if self.x < 0:
            self.x = 0
        elif self.x > PygView.width:
            self.x = PygView.width
        if self.y < 0:
            self.y = 0
        elif self.y > PygView.height:
            self.y = PygView.height
            
        self.tail.insert(0,(self.x,self.y))
        self.tail = self.tail[:128]
        self.rect.center = self.x, self.y
        
        # self.r can take the values from 255 to 101
        self.r += self.delta
        if self.r < 151:
            self.r = 151
            self.delta = 10
        if self.r > 255:
            self.r = 255
            self.delta = -10
            
        self.create_image()

class Settings(object):
    menu = {"root":["Play","Help", "Credits", "Options","Quit"],
            "Options":["Change screen resolution", "Sounds off"],
            "Change screen resolution":["640x400","800x640","1024x800","1440x850","1920x1080","2560x1440","3840x2160","4096x2160"],
            "Credits":["Simon HEPPNER"],
            "Help":["How to play", "How to win"],
            } 
        


class Menu(object):
    """ each menu item name must be unique"""
    def __init__(self, menu={"root":["Play","Help","Quit"]}):
        self.menudict = menu
        self.menuname="root"
        self.oldnames = []
        self.oldnumbers = []
        self.items=self.menudict[self.menuname]
        self.active_itemnumber=0
    
    def nextitem(self):
        if self.active_itemnumber==len(self.items)-1:
            self.active_itemnumber=0
        else:
            self.active_itemnumber+=1
        return self.active_itemnumber
            
    def previousitem(self):
        if self.active_itemnumber==0:
            self.active_itemnumber=len(self.items)-1
        else:
            self.active_itemnumber-=1
        return self.active_itemnumber 
        
    def get_text(self):
        """ change into submenu?"""
        try:
            text = self.items[self.active_itemnumber]
        except:
           print("exception!")
           text = "root"
        if text in self.menudict:
            self.oldnames.append(self.menuname)
            self.oldnumbers.append(self.active_itemnumber)
            self.menuname = text
            self.items = self.menudict[text]
            # necessary to add "back to previous menu"?
            if self.menuname != "root":
                self.items.append("back")
            self.active_itemnumber = 0
            return None
        elif text == "back":
            #self.menuname = self.menuname_old[-1]
            #remove last item from old
            self.menuname =  self.oldnames.pop(-1)
            self.active_itemnumber= self.oldnumbers.pop(-1)
            print("back ergibt:", self.menuname)
            self.items = self.menudict[self.menuname]
            return None
            
        return self.items[self.active_itemnumber] 
        
        
        
            

class PygView(object):
    width = 640
    height = 400
    def __init__(self, width=640, height=400, fps=30):
        """Initialize pygame, window, background, font,...
           default arguments 
        """
        
        pygame.mixer.pre_init(44100, -16, 2, 2048) 

        pygame.init()
        pygame.display.set_caption("Press ESC to quit")
        PygView.width = width
        PygView.height = height
        self.set_resolution()
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.playtime = 0.0
        self.font = pygame.font.SysFont('mono', 24, bold=True)
        # --- so la la paint ---
        self.allgroup =  pygame.sprite.LayeredUpdates()
        self.mousegroup = pygame.sprite.Group()
        
        Mouse.groups = self.allgroup, self.mousegroup
        self.mouse1 = Mouse(control="mouse", color=(255,0,0))

    def set_resolution(self):
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.background = pygame.Surface(self.screen.get_size()).convert()  
        self.background.fill((255,255,255)) # fill background white

    def paint(self):
        """painting on the surface"""
        
        menuy = 0
        for i in  m.items:
            n=m.items.index(i)
            if n==m.active_itemnumber:
                self.draw_text("-->",50,  m.items.index(i)*30+10,(0,0,255))
                self.draw_text(i, 100, m.items.index(i)*30+10,(0,0,255))
                menuy = m.items.index(i)*30 + 10
            else:
                self.draw_text(i, 100, m.items.index(i)*30+10)
        
        y = self.height - 120
        if pygame.mouse.get_pos()[1] < menuy - 15:
            m.previousitem()
        elif pygame.mouse.get_pos()[1] > menuy + 15:
            m.nextitem()
        

    def run(self):
        """The mainloop
        """
        #self.paint() 
        running = True
        while running:
            self.screen.blit(self.background, (0, 0))
            milliseconds = self.clock.tick(self.fps)
            seconds = milliseconds / 1000
            self.playtime += milliseconds / 1000.0 
            self.allgroup.draw(self.screen)
            self.allgroup.update(seconds)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False 
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        result = m.get_text()
                        print(result)
                        if result is None:
                            break 
                        elif "x" in result:
                            # change screen resolution, menu text is something like "800x600"
                            left = result.split("x")[0]
                            right = result.split("x")[1]
                            if str(int(left))==left and str(int(right))== right:
                                PygView.width = int(left)
                                PygView.height = int(right)
                                self.set_resolution()
                                
                        
                        # important: no elif here, instead if, because every menupoint could contain an 'x'        
                        elif result == "Play":
                            print("activating external program")
                            dungeonGenerator.start()
                            dungeonRunner.PygView(1430,800).run()
                            print("bye") 
                            self.__init__()
                        elif result == "How to play":
                            text = "play this game\n as you like\n and win!"
                            textscroller_vertical.PygView(text, self.width, self.height).run()
                            pygame.display.set_caption("Press ESC to quit")
                        elif result == "How to win":
                            text = "to win the game:\n shoot down enemies\n avoid catching bullets"
                            textscroller_vertical.PygView(text, self.width, self.height).run()
                            pygame.display.set_caption("Press ESC to quit")
                        elif result == "Simon HEPPNER":
                            text = "Programmer of this game!\n:D"
                            textscroller_vertical.PygView(text, self.width, self.height).run()
                            pygame.display.set_caption("Press ESC to quit")
                        elif result == "Quit":
                            print("Bye")
                            pygame.quit()
                            sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    #if event.key == pygame.K_DOWN or event.key == pygame.K_KP2:
                    #    #print(m.active_itemnumber)
                    #   m.nextitem()
                    #    print(m.active_itemnumber)
                    #    #self.sound2.play()
                    #if event.key == pygame.K_UP or event.key == pygame.K_KP8:
                    #    m.previousitem()
                    #    print(m.active_itemnumber)
                    #    #self.sound1.play()
                    #if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    #    #self.sound3.play()
                    #    result = m.get_text()
                    #    #print(m.get_text())
                    #    print(result)
                    #    if result is None:
                    #        break 
                    #    elif "x" in result:
                    #        # change screen resolution, menu text is something like "800x600"
                    #        left = result.split("x")[0]
                    #        right = result.split("x")[1]
                    #        if str(int(left))==left and str(int(right))== right:
                    #            PygView.width = int(left)
                    #            PygView.height = int(right)
                    #            self.set_resolution()
                    ##            
                    #    
                    #    # important: no elif here, instead if, because every menupoint could contain an 'x'        
                    #    elif result == "Play":
                    #        print("activating external program")
                    #        # start imported game
                    #        print("bye") 
                    #        self.__init__()
                    #    elif result == "How to play":
                    #        text = "play this game\n as you like\n and win!"
                    #        textscroller_vertical.PygView(text, self.width, self.height).run()
                    #    elif result == "How to win":
                    #        text = "to win the game:\n shoot down enemies\n avoid catching bullets"
                    #        textscroller_vertical.PygView(text, self.width, self.height).run()
                    #    elif result == "Simon HEPPNER":
                    #        text = "Programmer of this game!\n:D"
                    #        textscroller_vertical.PygView(text, self.width, self.height).run()
                    #    elif result == "Quit":
                    #        print("Bye")
                    #        pygame.quit()
                    #        sys.exit()
                                            

            if self.clock.get_fps() > 30:
                self.draw_text("{} FPS: {:6.3}".format(" "*12, self.clock.get_fps()), color=(30, 180, 90))
            elif self.clock.get_fps() > 20 and self.clock.get_fps() < 30:
                self.draw_text("{} FPS: {:6.3}".format(" "*12, self.clock.get_fps()), color=(200, 210, 0))
            elif self.clock.get_fps() > 0 and self.clock.get_fps() < 20:
                self.draw_text("{} FPS: {:6.3}".format(" "*12, self.clock.get_fps()), color=(240, 70, 60))
            pygame.draw.line(self.screen,(random.randint(0,255),random.randint(0,255), random.randint(0,255)),(50,self.height - 80),(self.width -50,self.height - 80) ,3)             
            self.paint()
            pygame.display.flip()
            
            
        pygame.quit()


    def draw_text(self, text ,x=50 , y=0,color=(27,135,177)):
        if y==0:
            y= self.height - 50
        
        """Center text in window
        """
        fw, fh = self.font.size(text)
        surface = self.font.render(text, True, color)
        self.screen.blit(surface, (x,y))

    
####

if __name__ == '__main__':

    # call with width of window and fps
    m=Menu(Settings.menu)
    PygView().run()
