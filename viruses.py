# Mathew Gray
# viruses.py
# Virus Killer by Mathew Gray is licensed under a Creative Commons 
# Attribution-NonCommercial-ShareAlike 3.0 Unported License.

import pygame,random,virtSystem, math

class virus(object):
    def __init__(self, imageFile, size, loc, targetLoc, targetFile, level):
        """Create a new virus"""
        # Pixel-range to adjust spawn position from (to avoid everything spawning from same point)
        RAND_DISP_LOW = -20
        RAND_DISP_HI = 20
        # Speed of virus (unitless)
        self.speed = random.randint(50 + 10*level,100 + 10*level)
        # Random starting location in bounds
        loc = (loc[0] + random.randint(RAND_DISP_LOW,RAND_DISP_HI), loc[1] + random.randint(RAND_DISP_LOW,RAND_DISP_HI))
        # Store generated location
        self.loc = loc
        # Store thumbnail size
        self.size = size
        # load and scale thumbnail to given size
        self.image = pygame.image.load(imageFile).convert_alpha()
        self.image = pygame.transform.scale(self.image, size)
        # Coodinates of virus' target folder
        self.targetLoc = targetLoc
        # Calculate random direction (Left, Right, Neither) to go in
        self.xdir = random.randint(-1,1)
        # direction of the step: 1 is down, -1 is up
        self.ydir = 1
        # Virus has not stolen a file yet
        self.stolenFile = None
        # Name of file that this virus will steal
        self.targetFile = targetFile
                
    def __repr__(self):
        return self.name
    
    def getBoundingBox(self):
        """Returns the (top-left),(bottom-right) actual coordinates of the image"""
        lowerRight = (self.loc[0]+self.size[0], self.loc[1]+self.size[1])
        return self.loc, lowerRight, self.size
    
    def draw(self,screen):
        """Draws the virus to the given screen"""
        # Draw the virus
        screen.blit(self.image, self.loc)
        # If the virus is carrying a file, draw that file too
        if (self.stolenFile != None):
            self.stolenFile.draw(screen)
    
class malware(virus):
    def update(self,ticks,dimensions,bMove):
        """Updates the location and status (ie. if it has stolen a file) of the virus"""
        # If virus should move, update the delta
        if (bMove):
            self.dmx = float(self.speed) * ticks / 1000 * self.xdir
            self.dmy = float(self.speed) * ticks / 1000 * self.ydir
            
        # If we don't want to move, deltas should be 0
        else:
            self.dmx = 0
            self.dmy = 0
       
        self.loc = (self.loc[0] + self.dmx, self.loc[1] + self.dmy)
        # If the virus has reached the bottom
        if self.loc[1] > dimensions[1]:
            # Set the position to the target folder's location
            self.loc = self.targetLoc
            # Invert x and y step
            self.xdir = -1*self.xdir
            self.ydir = -1*self.ydir
            # initialize stolen file
            self.stolenFile = virtSystem.virtDoc(self.targetFile,self.loc)
        elif self.loc[1] < 0-2*self.size[1]:
            return False
        # If the virus has gone too far left
        if self.loc[0] < (0 - self.size[0]):
            #Come out on the right
            self.loc = (dimensions[0],self.loc[1])
        # If the virus has gone too far right, come out on the left
        elif self.loc[0] > dimensions[0]:
            self.loc = ((0 - self.size[0]),self.loc[1])
        # If virus has stolen a file
        if self.stolenFile != None:
            # Grab the file (ie. drag it across screen)
            self.stolenFile.grabDoc((self.loc[0],self.loc[1]+int(.5*self.size[0])))
            self.stolenFile.resizeIcon(self.size)
            
class trojan(virus):
    def update(self,ticks,dimensions,bMove):
        """Updates the location and status (ie. if it has stolen a file) of the virus"""
        # If virus should move, update the delta
        if (bMove):
            self.dmx = float(self.speed) * ticks / 1000 * (math.cos(self.loc[1]*100))
            self.dmy = float(self.speed) * ticks / 1000 * abs((math.sin(self.loc[1]*100))) * self.ydir
        # If we don't want to move, deltas should be 0
        else:
            self.dmx = 0
            self.dmy = 0
       
        self.loc = (self.loc[0] + self.dmx, self.loc[1] + self.dmy)
        # If the virus has reached the bottom
        if self.loc[1] > dimensions[1]:
            # Set the position to the target folder's location
            self.loc = self.targetLoc
            # Invert x and y step
            self.xdir = -1*self.xdir
            self.ydir = -1*self.ydir
            # initialize stolen file
            self.stolenFile = virtSystem.virtDoc(self.targetFile,self.loc)
        elif self.loc[1] < 0-2*self.size[1]:
            return False
        # If the virus has gone too far left
        if self.loc[0] < (0 - self.size[0]):
            #Come out on the right
            self.loc = (dimensions[0],self.loc[1])
        # If the virus has gone too far right, come out on the left
        elif self.loc[0] > dimensions[0]:
            self.loc = ((0 - self.size[0]),self.loc[1])
        # If virus has stolen a file
        if self.stolenFile != None:
            # Grab the file (ie. drag it across screen)
            self.stolenFile.grabDoc((self.loc[0],self.loc[1]+int(.5*self.size[0])))
            self.stolenFile.resizeIcon(self.size)