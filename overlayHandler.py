# Mathew Gray
# overlayHandler.py
# Virus Killer by Mathew Gray is licensed under a Creative Commons 
# Attribution-NonCommercial-ShareAlike 3.0 Unported License.

import pygame

class overlay(object):
    def __init__(self):
        """Initialize a new overlay (dims screen and displays text)"""
        pass
    
    def draw(self,screen,screenWidth, screenHeight, overlayAlpha, image = None):
        """Draws either an image over the screen or a semi-transparent color"""
        if image == None:
            # Create a transparent surface representing kernal power left.  The 
            # bar should be 4.5% of the screen (Measured Image)
            image = pygame.Surface((screenWidth,screenHeight), pygame.SRCALPHA)
            # RGBA
            image.fill((0,0,0,overlayAlpha))
        else:
            # Draw passed image
            image = pygame.transform.smoothscale(image, \
            (screenWidth,screenHeight))
        # blit whatever image we chose
        screen.blit(image, (0,0))
        
class mainMenu(overlay):
    def __init__(self,screenHeight):
        """Sub class to the overlay class -> This displays the main menu and a
        # start button"""
        # Start Icon is 300 x 300 so don't make the icon larger (avoid blur)
        START_ICON_MAX_SIZE = 300
        
        self.iconHover = False
        # Initialize start button (both unpressed and pressed states)
        self.startIcon = pygame.image.load(\
        'res/images/menu/begin.png').convert_alpha()
        self.startIcon_pressed = pygame.image.load(\
        'res/images/menu/begin_pressed.png').convert_alpha()
        self.startBkg = pygame.image.load('res/images/menu/title.jpg').convert()
        # Set sze of icon (with in 
        self.iconSize = int(.25*screenHeight)
        
        if self.iconSize > START_ICON_MAX_SIZE:
            self.iconSize = START_ICON_MAX_SIZE
        
        # Scale the icon
        self.startIcon = pygame.transform.smoothscale(self.startIcon, \
        (self.iconSize,self.iconSize))
        # Scale the pressed icon
        self.startIcon_pressed = pygame.transform.smoothscale(\
        self.startIcon_pressed, (self.iconSize,self.iconSize))
    
    def draw(self,screen, screenWidth, screenHeight):
        """Draws the menu picture and button to the screen"""

        pygame.mouse.set_visible(True)
        # Call draw function from superclass, draws menu picture
        super(mainMenu,self).draw(screen, screenWidth,screenHeight,0, \
        self.startBkg)
        # Position the button
        pos = (int(screenWidth/2 - 0.5*self.iconSize),\
        screenHeight/2- 0.5*self.iconSize)
        # If the mouse is hovering over the icon, show pressed state
        if not(self.iconHover):
            screen.blit(self.startIcon,pos)
        else:
            screen.blit(self.startIcon_pressed,pos)
        # Store Top Left, Bottom Right of button
        self.buttonCoods = [pos, (pos[0] + self.iconSize, pos[1] + \
        self.iconSize)]
        
    def update(self):
        """Updates the menu ie. update if the user is hovering over the icon"""
        mouse_x,mouse_y = pygame.mouse.get_pos()
        # See if the cursor is within the rectuangular bounds of the icon
        if mouse_x < self.buttonCoods[1][0] and mouse_x > \
        self.buttonCoods[0][0]:
                if mouse_y < self.buttonCoods[1][1] and mouse_x > \
                self.buttonCoods[0][1]:
                    # If it is, set the iconHover and break out of this function
                    self.iconHover = True
                    return
        # Only reach here if the player isn't hovering over the icon
        self.iconHover = False
        
    def checkClick(self):
        """Returns the current state of the icon"""
        return self.iconHover
    
class gameOver(overlay):
    def __init__(self,statTracker):
        """Initialize a new gameOver subclass of the overlay class"""
        # Need statTracker to print player stats
        self.stats = statTracker
        self.gameOverImage = pygame.image.load(\
        'res/images/menu/gameOver.jpg').convert()
    
    def draw(self,screen, screenWidth, screenHeight, gameSong):
        """Draws the game over screen"""
        gameSong.set_volume(0)
        pygame.mouse.set_visible(True)
        # Have super class draw the picture
        super(gameOver,self).draw(screen, screenWidth,screenHeight,0, \
        self.gameOverImage)
        
        customMessage = [("Game Over!", 30), (\
        "You Survived " + str(self.stats.level) + " Levels", 30), \
        ("Press r to reboot program", 20)]
        
        # Draw stats with game over on top
        drawStatsMessage(screen, screenWidth, screenHeight, self.stats, \
        customMessage)

class levelChanger(overlay):
    def __init__(self,statTracker):
        """Initialize a new level changer sub class of the overlay class"""
        self.stats = statTracker
    
    def draw(self,screen, screenWidth, screenHeight):
        """Draws the intermediate-level level screen"""
        # Make is semi-transparent (alpha out of 225)
        OVERLAY_ALPHA = 225
        # Have super class dim the screen
        super(levelChanger,self).draw(screen, screenWidth,screenHeight,\
        OVERLAY_ALPHA)
        # Draw stats with current level on top
        drawStatsMessage(screen, screenWidth, screenHeight, self.stats, \
        [("Level " + str(self.stats.level) + " Completed!", 30)])
        
def drawStatsMessage(screen, screenWidth, screenHeight, stats, prepend):
        """Draws the statistics to the screen with a custom title"""
        # Size of the level font 
        LEVEL_READOUT_SIZE = 30
        # Size of the kills readout font
        KILLS_READOUT_SIZE = 20
        # Size of the number of compromised files readout
        FILESCOMPROMISED_SIZE = 15
        # Size of the list of compromised files
        FILE_READOUT_SIZE = 10
        # List of things to blit to the screen. Insert as tuple with string on 
        # left and font size on right
        readout = [
                   ("Kills: " + str(stats.killCount),KILLS_READOUT_SIZE),
                   ("Copies of Files Compromised: " + str(stats.num_compFiles),\
                   KILLS_READOUT_SIZE),
                   ("", FILESCOMPROMISED_SIZE),
                   ("Files Compromised:", FILESCOMPROMISED_SIZE)
                   ]
        for t in xrange(len(prepend)):
            readout.insert(0, prepend[t])
        # Holds a single line of the files stolen
        fileListLine = ""
        # append the files together...
        for f in stats.compFiles:
            fileListLine +=  str(f) + ", "
            # If it gets too longs, append that line to the readout list, clear 
            # fileListLine, and keep moving
            if (len(fileListLine)*FILE_READOUT_SIZE > screenWidth):
                readout.append((fileListLine,FILE_READOUT_SIZE))
                fileListLine =""
        readout.append((fileListLine,FILE_READOUT_SIZE))
        
        # Set the y position to 25% of the way down the screen
        ypos = screenHeight/4
        for r in readout:
            # Create a new font and size for each line
            font = pygame.font.Font('res/fonts/kernalPower.TTF', r[1])
            text = font.render(r[0], True, (255, 255, 255))
            # Create rect so we can center the text
            textRect = text.get_rect()
            textRect.centerx = screen.get_rect().centerx
            screen.blit(text, (textRect[0], ypos))
            ypos += 2*r[1]
        
