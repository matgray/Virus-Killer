# Mathew Gray
# powerUps.py
# Virus Killer by Mathew Gray is licensed under a Creative Commons 
# Attribution-NonCommercial-ShareAlike 3.0 Unported License.

import pygame,random,virtProgram, logging

logging.basicConfig(level=logging.DEBUG)

# Import global key constants
from pygame.locals import *
    
class spawner(object):
        def __init__(self, screenWidth,screenHeight, level):
            """Initialize a new spawning object"""
            # Level stops at 4
            self.Upgradelevel =1
            self.screenWidth = screenWidth
            self.screenHeight = screenHeight
            # Holds Currently displayed (not picked up) power ups
            self.powerUps = list()
            # Holds all of the available power ups
            self.types = dict()
            # INSERT NEW POWER UPS IN THIS ARRAY -> (name, image file, key to use, pygame keycode (ie. avoids me having to use eval))
            self.availablePowerUps = [
                                      ("Program Upgrade", 'res/images/upgrade.png',     None, None),
                                      ("Thread Stopper",'res/images/threadStop.png',    's', K_s),
                                      ("OverClock", 'res/images/overclock.png',         'o', K_o),
                                      ("Bomb", 'res/images/killAll.png',                'b', K_b),
                                      ("Thread Killer",'res/images/threadKill.png',     't', K_t),
                                      ('Firewall','res/images/firewall.png',            'f', K_f)
                                      ]
            # Put all of the available power ups into the type list
            for i in xrange(len(self.availablePowerUps)):
                self.types[self.availablePowerUps[i][0]] = self.powerUp(self.availablePowerUps[i][0], self.availablePowerUps[i][1], self.availablePowerUps[i][2], screenWidth, screenHeight, self.availablePowerUps[i][3])
            
            # These define the updates for each program in the order (top to bottom) that they go through
            self.browserUpgrade = progUpgrade([
                                                virtProgram.program("res/images/progIcons/ie.png", "Internet Explorer", 'browser',  1, "Internet Browser"),
                                                virtProgram.program("res/images/progIcons/safari.png","Safari","browser",           2, "Internet Browser"),
                                                virtProgram.program("res/images/progIcons/firefox.png", "Firefox","browser",        3, "Internet Browser"),
                                                virtProgram.program("res/images/progIcons/chrome.png",  "Google Chrome", "browser", 4, "Internet Browser")
                                                ])
            self.wpUpgrade = progUpgrade([
                                          virtProgram.program("res/images/progIcons/word.png", "Microsoft Word", "wp",      1, "Word Processor"),
                                          virtProgram.program("res/images/progIcons/pages.png", "Pages", "wp",              2, "Word Processor"),
                                          virtProgram.program("res/images/progIcons/openOffice.png", "Open Office", "wp",   3, "Word Processor"),
                                          virtProgram.program("res/images/progIcons/vim.png", "Vim", "wp",                  4, "Word Processor")
                                          ])
            
            self.torUpgrade = progUpgrade([
                                          virtProgram.program("res/images/progIcons/limewire.png", "Limewire", 'torrent',           1, "Torrent Client"),
                                          virtProgram.program("res/images/progIcons/transmission.png", "Transmission", "torrent",   2, "Torrent Client"),
                                          virtProgram.program("res/images/progIcons/azureus.png", "Azureus", "torrent",             3, "Torrent Client"),
                                          virtProgram.program("res/images/progIcons/uTorrent.png", "uTorrent", "torrent",           4, "Torrent Client"),
                                          ])
            
            self.compressionUpgrade = progUpgrade([
                                          virtProgram.program("res/images/progIcons/windowsCompression.png", "NTFS Compression",'archiver', 1, "File Archiver"),
                                          virtProgram.program("res/images/progIcons/winzip.png", "winZIP", "archiver",                      2, "File Archiver"),
                                          virtProgram.program("res/images/progIcons/winrar.png", "winRAR", "archiver",                      3, "File Archiver"),
                                          virtProgram.program("res/images/progIcons/7zip.png", "7zip", "archiver",                          4, "File Archiver"),
                                          ])
            self.ftpUpgrade = progUpgrade([
                                           virtProgram.program("res/images/progIcons/smartftp.png", "smartFTP", 'ftp',  1, "FTP Client"),
                                           virtProgram.program("res/images/progIcons/winscp.png", "winSCP", "ftp",      2, "FTP Client"),
                                           virtProgram.program("res/images/progIcons/fireftp.png", "fireFTP", "ftp",    3, "FTP Client"),
                                           virtProgram.program("res/images/progIcons/filezilla.png", "FileZilla", "ftp",4, "FTP Client"),
                                           ])
            self.mpUpgrade = progUpgrade([
                                           virtProgram.program("res/images/progIcons/wmp.png", "Windows Media",'mp',1, "Media Player"),
                                           virtProgram.program("res/images/progIcons/itunes.png", "iTunes", "mp",   2, "Media Player"),
                                           virtProgram.program("res/images/progIcons/winamp.png", "winAmp", "mp",   3, "Media Player"),
                                           virtProgram.program("res/images/progIcons/mm.png", "MediaMonkey", "mp",  4, "Media Player"),
                                           ])
            
        # New programs MUST be checked here for upgrade
        def upgrade(self,progType, getCurrent = False):
            """This returns the next upgrade for the given program type"""
            # browser upgrade
            if progType == "browser":
                return self.browserUpgrade.getUpgrade(getCurrent)
            # Word Processor upgrade
            elif progType == "wp":
                return self.wpUpgrade.getUpgrade(getCurrent)
            # Torrent upgrade
            elif progType == "torrent":
                return self.torUpgrade.getUpgrade(getCurrent)
            # File archiver upgrade
            elif progType == "archiver":
                return self.compressionUpgrade.getUpgrade(getCurrent)
            # FTP upgrade
            elif progType == "ftp":
                return self.ftpUpgrade.getUpgrade(getCurrent)
            # Media Player Upgrade
            elif progType == "mp":
                return self.mpUpgrade.getUpgrade(getCurrent)
            # Return None if no upgrade exists
            else:
                return None
        
        def spawnRand(self):
            """Spawns a random power up"""
            # Generate random power up
            powType = self.types[random.choice(self.types.keys())]
            # If the power up is not already displayed, display it
            if powType not in self.powerUps:
                powType.genPosition()
                self.powerUps.append(powType)
        
        def removePowerUp(self):
            """Removes the oldest power up from the screen"""
            if len(self.powerUps) > 0:
                self.powerUps.pop(0)
            else:
                logging.info('There Are No Power Ups to Remove')
        
        def showPowerUps(self, screen, size):
            """Displays the power ups on the screen"""
            for p in self.powerUps:
                p.draw(screen,size)
                
        def checkClick(self, statTracker, soundFile):
            """Checks to see if the player clicked on any of the power ups"""
            removeUs = list()
            for p in self.powerUps:
                topLeft, bottomRight, size = p.getBoundingBox()    
                mousePos = pygame.mouse.get_pos()
                # If the mouse if on the virus, add it to the remove list (avoids changing length of powerUps when iterating though it
                if (topLeft[0] < mousePos[0] and mousePos[0] < bottomRight[0]):
                    if (topLeft[1] < mousePos[1] < bottomRight[1]):
                        removeUs.append(p)
            # Remove clicked power ups
            for p in removeUs:
                self.powerUps.remove(p)
                # Add power up type to the tracker
                statTracker.addPowerUp(p.name, 1)
                soundFile.play()
                logging.info("-EXEC-PICKUP:" + str(p))
            
        class powerUp(object):
            def __init__(self, name, imageFile, usageKey, screenWidth,screenHeight, pygameKeyCode):
                """Initializes a new instance of a power up"""
                self.name = name
                # Position of the powerup on the screen
                self.pos=(0,0)
                # key that uses powerup.  Set to None if there is no key
                self.key = usageKey
                # Store the pygame constant, that way I don't have to use eval in powerUpKeyListener ;)
                self.keyCode = pygameKeyCode
                # Save original thumbnail for on-the-fly magnification during harder levels
                self.originalThumbnail = self.scaledthumbnail = pygame.image.load(imageFile).convert_alpha()
                # Icon size
                self.size = (0,0)
                # Need screen dimensions to calculate positions
                self.screenWidth = screenWidth
                self.screenHeight = screenHeight
                # Generate a random position
                self.genPosition()
                
            def __repr__(self):
                return self.name
                
            def genPosition(self):
                """Generates a random position for the power up"""
                # self.pos is a tuple
                self.pos = (random.randint(0,(self.screenWidth-(5*self.size[0]))), random.randint(0,(self.screenHeight-(5*self.size[1]))))
                
            def resizeIcon(self, size):
                """Resizes the icon for the power up"""
                # Transform thumbnail using original to avoid pixelation
                self.scaledthumbnail = pygame.transform.smoothscale(self.originalThumbnail, size)
                self.size = size
                
            def draw(self,screen,size):
                """Draws the power up to the screen"""
                self.resizeIcon(size)
                screen.blit(self.scaledthumbnail,self.pos)
                    
            def getBoundingBox(self):
                """Returns the (top-left),(bottom-right) actual coordinates of the image"""
                lowerRight = (self.pos[0]+self.size[0], self.pos[1]+self.size[1])
                return self.pos, lowerRight, self.size

class progUpgrade(object):
    def __init__(self, updateList):
        """Initialize a new program upgrade class"""
        self.updateNumber = 0
        self.progs = updateList
        
    def getUpgrade(self,getCurrent = False):
        """Gets the updated Program, if getCurrent=true, returns the current upgrade"""
        if (getCurrent):
                return self.progs[self.updateNumber]
        # Make sure that there is a next upgrade
        if self.updateNumber + 1 < len(self.progs):
            self.updateNumber += 1
            return self.progs[self.updateNumber]
        # Return none if there is no upgrade
        else:
            return None
        
class powerUpKeyListener(object):
    """This class checks the keys and returns the power up (or none) 
    if the player wants to use a powerup (checks to make sure that powerup is valid)"""
    def __init__(self):
        pass
    
    def checkKeys(self, keyPress, types, powerList):
        """Call this to check the keys to see if a powerup was used"""
        # Go though all of powerups
        for p in types:
            # if there's a key to use the powerup
            if not(types[p].key == None):
                # We stored the pygame keycode in the spawner init, so now we can reference it...
                if keyPress == types[p].keyCode:
                    # Avoid exception before we try to do some math
                    if (types[p].name in powerList):
                        #Make sure the player has some of this power up before we use it
                        if (powerList[types[p].name] > 0):
                            # If they do, take one away
                            powerList[types[p].name] -= 1
                            #return the name of the powerup
                            return p
        # If anything failed, return None
        return None
                
