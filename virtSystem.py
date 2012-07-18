# Mathew Gray
# virtSystem.py
# Virus Killer by Mathew Gray is licensed under a Creative Commons 
# Attribution-NonCommercial-ShareAlike 3.0 Unported License.

import pygame

class virtDoc(object):
    def __init__(self,name,pos):
        """Create a new Document"""
        self.name = name[0]
        #Save original thumbnail for on-the-fly magnification during harder levels
        self.originalThumbnail = self.scaledthumbnail = self.mouseCursor = pygame.image.load('res/images/stolenFile.png').convert_alpha()
        #position of the document
        self.pos = pos
        # Starting iconsize. initialize to (0,0)
        self.iconSize = (0,0)
        # Font to use for file name under icon
        font = pygame.font.Font(None, 17)
        # Render the text and store
        self.Filetext = font.render(self.name, True, (255, 255, 255))
        
    def resizeIcon(self, size):
        """Resizes the icon for the file"""
        self.scaledthumbnail = pygame.transform.smoothscale(self.originalThumbnail, size)
        self.iconSize = size
        
    def grabDoc(self,pos):
        """Set the document position to the passed coordinates"""
        self.pos = pos
        
    def draw(self,screen):
        # Create a rectangle so we can center the text under the icon
        textRect = self.Filetext.get_rect()

        # Center the rectangle under the icon
        textRect.centerx = self.pos[0]+(.5*self.iconSize[0])
        textRect.centery = self.pos[1]+1.25*self.iconSize[1]
        
        # Blit the file icon to the screen
        screen.blit(self.scaledthumbnail, self.pos)
        # Blit the file name to the screen
        screen.blit(self.Filetext, textRect)
        
        
class virtFolder(object):
    def __init__(self, name, thumbnail, dir):
        # Ignores files with names longer than MAX_FILE_CHARS
        self.MAX_FILE_CHARS = 10
        # Number of files that each folder holds
        self.NUM_FILES_TO_FETCH = 25
        # Store name, thumbnail, and folder location
        self.name = name
        self.originalThumbnail = self.scaledthumbnail = self.mouseCursor = pygame.image.load(thumbnail).convert_alpha()
        self.loc = (0,0)
        # If no folder is passed, assume we want the home
        if (dir.lower() == "home"):
            self.path = os.getenv("HOME")
        # If the string 'docs' is passed, assume we want the documents folder
        elif (dir.lower() == "docs"):
            self.path = os.getenv("HOME") + "/Documents"
        # Use the path given
        else:
            self.path = dir
        # Create a new system prober to get the files
        self.prober = systemProbe(self.path,self.MAX_FILE_CHARS)
        # Tell the prober to fetch the files
        self.fetchFiles(self.NUM_FILES_TO_FETCH)
        # store the files locally
        self.files = self.prober.files
        
    def fetchFiles(self, numFiles):
        """Tells the system prober to fetch n files and stores result in self.files"""
        self.prober.grabnFiles(self.prober.path, numFiles, self.MAX_FILE_CHARS)
        self.files = self.prober.files
        
    def resizeIcon(self, size):
        """Resize the folder icon to the given size"""
        self.scaledthumbnail = pygame.transform.smoothscale(self.originalThumbnail, size)
        
    def storeLoc(self, loc):
        """Changes the actual location of the folder"""
        self.loc = loc

import os
class systemProbe(object):
    def __init__(self,path,maxChars):
        """Initializes the prober"""
        self.files = set()
        self.path = path
        
    def grabnFiles(self,path,numFiles, maxNameLen):
        """Grabes n files from the specified path"""
        if (len(self.files) >= numFiles):
            # Kill search if max number of files have been found
            return
        # If file is found
        if (os.path.isdir(path) == False):
            # Grabs filename from path
            fileName = os.path.basename(path)
            # Ensure filename is less then the max length
            if (len(fileName) < maxNameLen):
                # If it is, add it to the set of files
                self.files.add(os.path.basename(path))
        else:
            # If the path isn't to a file
            for filename in os.listdir(path):
                # Recursivly find files in the folder.  Ignore hidden stuff and AppData on Windows so it runs
                if not(str(filename).startswith('.') or str(filename) == "AppData"):
                    self.grabnFiles(path + "/" + filename, numFiles, maxNameLen)
                