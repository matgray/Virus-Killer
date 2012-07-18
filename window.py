# Mathew Gray
# window.py
# Virus Killer by Mathew Gray is licensed under a Creative Commons 
# Attribution-NonCommercial-ShareAlike 3.0 Unported License.

import pygame

# I did not write rot_center - http://stackoverflow.com/questions/4183208/pygame-rotating-an-image-around-its-center
def rot_center(image, angle):
    """Rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image


def centerImageOnPos(imageFile,x,y):
    """Centers an image on the given position"""
    x -= imageFile.get_width()/2
    y -= imageFile.get_height()/2
    return x,y

class window(object):
    def __init__(self,FULLSCREEN, width,height,bits, fill = False):
        """Creates a pygame window"""
        # A set of all the cursors to be rendered
        self.cursorList = set()
        # Auto-scale to full screen
        if (fill):
            self.autoFullScreen(FULLSCREEN,bits)
        #Manually Sized Window
        else:
            #Create a window
            self.screen = pygame.display.set_mode((width,height),0,bits)
            self.width = width
            self.height = height

    def autoFullScreen(self,FULLSCREEN, bits):
        """Auto-detects window screen and chooses largest resolution, then goes full screen"""
        # Get all supported Modes
        screenModes = pygame.display.list_modes()
        # Set screen to maximum supported resolution
        self.screen = pygame.display.set_mode(screenModes[0],FULLSCREEN,bits)
        self.width = screenModes[0][0]
        self.height = screenModes[0][1]
    
    class cursor(object):
        """Create a custom cursor with transparency (use png)"""
        #where size is a tuple of the resolution of the cursor
        def __init__(self,imageFile,size, rot = False, rotSpeed = 0):
            #Set the system cursor invisible
            pygame.mouse.set_visible(False)
            # Convert mouse cursor and convert the transparency
            self.mouseCursor = pygame.image.load(imageFile).convert_alpha()
            self.mouseCursor = pygame.transform.scale(self.mouseCursor, size)
            #Current rotated angle
            self.rotAngle = 0
            # Boolean of whether or not we are rotating
            self.rot = rot
            # Speed at which cursor is rotating
            self.rotSpeed = rotSpeed
            #What Factor to adjust the rotSpeed by
            self.rotSpeedAdjFactor = 1
            # Store Size
            self.size = size
            
        # Increases rotation speed by the passed factor
        def increaseRot(self,factor):
            """Increases the  rotation of any spinning cursor by this factor"""
            self.rotSpeedAdjFactor = factor
            
        def __repr__(self):
            return "Mouse Cursor\nRotation:",self.rot,"Size:",self.size
            
        def show(self,screen,seconds):
            """blits the cursor to the passed screen"""
            # Update cursor position
            self.x,self.y = pygame.mouse.get_pos()
            self.x,self.y = centerImageOnPos(self.mouseCursor, self.x,self.y)
            # If we want this cursor to rotate
            if (self.rot):
                #Rotate at cross-platform constant speed
                speed = self.rotSpeed*self.rotSpeedAdjFactor
                self.rotAngle = (self.rotAngle + seconds*speed)%360
                # Render the rotated mouse ie. preserve original
                newMouse = rot_center(self.mouseCursor, self.rotAngle)
                screen.blit(newMouse, (self.x,self.y))
            else:
                #Blit mouse
                screen.blit(self.mouseCursor, (self.x,self.y))
        
        #Returns coodinates of the top left of the cursor (NOT THE ACTUAL MOUSE)
        def getCoords(self):
            return (self.x,self.y)
            
    class background(object):
        """Creates a custom background (No transparency)"""
        def __init__(self,imageFile,screenWidth,screenHeight):
            self.image = pygame.image.load(imageFile).convert()
            self.image = pygame.transform.smoothscale(self.image, (screenWidth,screenHeight))
        
        #blits the background to the passed screen
        def show(self,screen):
            screen.blit(self.image, (0,0))
            
    def showCursor(self,seconds):
        """blits the cursors"""
        for i in self.cursorList:
            vars(self)[i].show(self.screen,seconds)

    def showBackground(self):
        """blits the background"""
        self.backgroundImage.show(self.screen)
        
    def setBackground(self,imageFile):
        """Sets the background image to the passed path"""
        self.backgroundImage = self.background(imageFile,self.width,self.height)
    
    def newCursor(self,name,imageFile,size, rot=False, rotSpeed = 0):
        """Sets the cursor image to the passed path"""
        if name not in self.cursorList:
            vars(self)[name] = self.cursor(imageFile,size,rot, rotSpeed)
            self.cursorList.add(name)
    
    def getCursorPos(self):
        """This is the PNG pos (top left) NOT the actual mouse"""
        return self.mouse.getCoords()
    
    def removeCursor(self,name):
        """remove the cursor with the given name"""
        self.cursorList.discard(name)