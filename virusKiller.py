# Mathew Gray
# virusKiller.py
# Virus Killer by Mathew Gray is licensed under a Creative Commons 
# Attribution-NonCommercial-ShareAlike 3.0 Unported License.

import pygame, sys, os,random, window, virtSystem, powerUps, statTracker, overlayHandler, containers, pygame.mixer, logging

from pygame.locals import *

# Initialize Logging
logging.basicConfig(level=logging.DEBUG)
# logger will be the name of the logging module
logger = logging.getLogger()
# Disable logging by default
logger.disabled = True

# This toggles logging/Debug mode.  Debugging mode is described down in the key handler portion of playgame()
def toggleLogging():
    #logger.disabled is a bool stating if logging is enabled
    if logger.disabled == True:
        logger.disabled = False
    else:
        logger.disabled = True
        # If the overlay is present, disable it
        game.renderOverlay = False
        # If gameplay is stopped, enable it
        game.gamePlay = True

#This initializes pygame
pygame.init()

class game(object):
    def __init__(self, height = 800, width = 600, bits = 32, fullscreen = False):
        # variable names of the three  main crosshairs to be stored in the window
        self.crosshairName = "innerTri"
        self.fireMarkerName = "fireMarker"
        self.noFireMarkerName = "No Fire"
        # Create a new window -> pass global FULLSCREEN incase we want full screen
        self.gameScreen = window.window(FULLSCREEN, height,width,bits, fullscreen)
        # This class instance handles powerups (eg. thread stopper / thread killer)
        self.powerUpSpawner = powerUps.spawner(self.gameScreen.width,self.gameScreen.height, 1)
        # This class instance handles the score and tracking
        self.statTracker = statTracker.tracker(self.powerUpSpawner)
        # Create a folder container class instance to store our folders
        self.levelFolders = containers.folderContainer()
        # True if the user is holding down the mouse, false otherwise
        self.mouseHeld = False;
        # Initialize programs
        self.initProgs(self.statTracker.level)
        # Initialize folders
        self.initFolders(self.statTracker.level)
        # This bool controls if viruses are moving or paused.
        self.gamePlay = True
        # Set default cursor and background
        self.initCursorAndBackground()
        # bool of if program is changing levels
        self.renderOverlay = False
        # Create a new overlay handler (subclass of overlay) subclass instance for changing levels
        self.levelOverlay = overlayHandler.levelChanger(self.statTracker)
        # True if we are rending a menu
        self.renderMenu = True
        # Create a overlay handler (subclass of overlay) instance for the main menu
        self.menuOverlay = overlayHandler.mainMenu(self.gameScreen.height)
        # If true, disables timers at the end of the main loop
        self.advance = True
        # True if game is over
        self.gameOver = False
        # Create a new overlay handler (subclass of overlay) instance for the game over screen
        self.gameOverOverlay = overlayHandler.gameOver(self.statTracker)
        # True if the threads are stopped by the thread stopper
        self.threadStop = False
        # True if a firewall is currently active
        self.firewallActive = False
        # Initialize the game sounds
        self.initSounds()
        # This class instance handles all of the timing in our game
        self.timeHandler = self.timeHandler()
        # This class instance handles all of the power ups in our game
        self.powerUpHandler = powerUps.powerUpKeyListener()
        #This is the font used for debugging
        DebuggingFont = pygame.font.Font(None, 30)
        # Render debugging font
        self.debuggingMessage = DebuggingFont.render('Debugging Mode Enabled', False, (255, 255, 255), (0, 0, 0))
        self.clock = pygame.time.Clock()
        
    def initSounds(self): 
        # Initialize the pygame sound module
        pygame.mixer.init()
        # Initialize all of our sounds
        self.themeSong = pygame.mixer.Sound('res/sound/music/theme.ogg')
        self.nextLevelSound = pygame.mixer.Sound('res/sound/levelEnd.ogg')
        self.powerUpAttained = pygame.mixer.Sound('res/sound/powerup.ogg')
        self.virusKilledSound = pygame.mixer.Sound('res/sound/virusKill.ogg')
        self.beepSound = pygame.mixer.Sound('res/sound/beep.ogg')
        self.boomSound = pygame.mixer.Sound('res/sound/boom.ogg')
        self.gameOverSound = pygame.mixer.Sound('res/sound/gameOver.ogg')
        self.clickSound = pygame.mixer.Sound('res/sound/click.ogg')
        self.stolenSound = pygame.mixer.Sound('res/sound/stolenFile.ogg')
        # Play the theme sound forever
        self.themeSong.play(-1)
        # Set song volume
        self.themeSong.set_volume(.75)
        
    def initCursorAndBackground(self):
        # Set our new cursor.  Have it rotate
        self.gameScreen.newCursor(self.crosshairName,"res/images/triCross.png",(50,50),True, 100)
        # Set the background
        self.gameScreen.setBackground("res/images/bkg/wall1.jpg")
        
    def initProgs(self, level):
        """Initialize programs on top of screen by adding them to the program container"""
        # Factor to cap number of programs. floor of SPAWN_LEVEL_FACTOR and level is the amount of programs
        SPAWN_LEVEL_FACTOR = 1.5
        # We only have enough programs for 4 levels
        if level > 4:
            level = 4
        # Create a program container to store all of our programs
        self.levelProgs = containers.programContainer()
        # Number of programs spawned
        spawned = 0
        # Types (NOT NAMES) of programs that can be spawned
        types = ["browser", "wp", "torrent", "archiver","ftp","mp"]
        # spawn the correct number of programs
        while spawned < (int(SPAWN_LEVEL_FACTOR*level)):
            self.levelProgs.addProg(types[spawned], self.powerUpSpawner.upgrade(types[spawned], True))
            spawned += 1
            
    def initFolders(self, level):
        """Initialize folders on bottom of screen by adding them to the folder container"""
        self.levelFolders.addFolder("docs", virtSystem.virtFolder("My Documents","res/images/docsFolder.png", "home"))
        self.levelFolders.addFolder("sys", virtSystem.virtFolder("My System","res/images/systemFolder.png","home"))

    def updateAll(self):
        """Update all of the parts of the game"""
        dimensions = (self.gameScreen.width, self.gameScreen.height)
        self.levelProgs.updateViruses(self.levelFolders.folders, self.statTracker, dimensions, self.gamePlay, self.stolenSound)
        # Update statistics
        self.statTracker.update(self.mouseHeld)
        # If the menu is currently active, update it
        if (self.renderMenu):
            self.menuOverlay.update()
        
        if logger.disabled == True:
            # Check conditions for game over if not in debugging mode
            totalFiles = 0
            # Count files
            for folder in self.levelFolders.folders:
                totalFiles += len(self.levelFolders.folders[folder].files)
            if (self.statTracker.checkGameOver(totalFiles)):
                self.gameOver = True
        
        # iterate though all of the open programs
        for prog in self.levelProgs.progs:
            self.levelProgs.progs[prog].update()
            
        # If the user is holding down the mouse
        if self.mouseHeld and not (self.renderOverlay):
            # Fire only if user has enough power and there is no firewall
            if self.statTracker.power.get() > 0 and not(self.firewallActive):
                # When the mouse is held down, add the fire marker to indicate fire is firing
                self.gameScreen.newCursor(self.fireMarkerName,"res/images/boxCross.png",(50,50))
                # When the player is firing, speed up the rotation of the crosshair
                vars(self.gameScreen)[self.crosshairName].increaseRot(2)
                        
                # iterate though all of the open programs
                for prog in self.levelProgs.progs:
                    #iterate over all of their threads
                    for t in self.levelProgs.runningThreads[prog]:
                        #Check each virus in each thread to see if it was clicked on
                        vars(self.levelProgs.progs[prog])[t].checkClick(self.statTracker, self.virusKilledSound)
                # Check to see if the user clicked on any power ups
                self.powerUpSpawner.checkClick(self.statTracker, self.powerUpAttained)
                # Draw power while user is clicking
                self.statTracker.power.rem()
            else:
                # If the user doen't have enough power to click
                logging.info('NO MORE POWER')
                self.cursorCeaseFire() 
            
        # Check to all viruses to make sure they don't cross the firewall
        if self.firewallActive:
            for prog in self.levelProgs.progs:
                #iterate over all of their threads
                for t in self.levelProgs.runningThreads[prog]:
                    #Check each virus in each thread to see if it crossed the firewall
                    vars(self.levelProgs.progs[prog])[t].checkFirewall(self.statTracker,dimensions[0],dimensions[1])
        
    def drawAll(self):
        """Redraw all of objects on the screen"""
        # Percent of the program icon size to set the power up icons to
        POWERUP_ICON_PERCENT = 2.0/3
        seconds = self.clock.tick()/1000.0
        screen = self.gameScreen.screen
        screenWidth = self.gameScreen.width
        screenHeight = self.gameScreen.height
        
        # First draw background
        self.gameScreen.showBackground()
        # Then Draw the programs at the top (need to do this before drawing viruses so viruses know where to spawn)
        self.levelProgs.showProgs(screen, screenWidth, screenHeight)
        # Draw folders
        self.levelFolders.showFolders(screen, screenWidth, screenHeight)
        if not(self.firewallActive or self.renderOverlay):
            #Draw the power bar
            self.statTracker.power.draw(screen, screenWidth, screenHeight)
        # Draw power ups
        self.powerUpSpawner.showPowerUps(screen,(int(POWERUP_ICON_PERCENT*self.levelProgs.iconLen),int(POWERUP_ICON_PERCENT*self.levelProgs.iconLen)))
        # Draw viruses only if there is no overlay present (ie. Hide viruses if overlay)
        if not(self.gameOver or self.renderOverlay or self.renderMenu):
            #  draw viruses
            self.levelProgs.showViruses(screen)
            #Then draw cursor last so it's on top
            self.gameScreen.showCursor(seconds)
            # Draw stats to screen
            self.statTracker.draw(screen,self.powerUpSpawner.types,  screenWidth, screenHeight)
        # If the level changing overlay should be drawn
        if (self.renderOverlay):
            # Dont move viruses
            self.gamePlay = False
            # Draw the overlay
            self.levelOverlay.draw(screen, screenWidth, screenHeight)
        # If the menu should be drawn
        elif(self.renderMenu):
            # Dont move viruses
            self.gamePlay = False
            # draw the menu
            self.menuOverlay.draw(screen, screenWidth, screenHeight)
        # If the game over screen should be shown
        elif(self.gameOver):
            # Draw the game over screen
            self.gameOverOverlay.draw(screen, screenWidth, screenHeight, self.themeSong)
            # If it's our first time in this loop...
            if self.gamePlay == True:
                self.gameOverSound.play()
            # Pause icon movement
            self.gamePlay = False
            self.timeHandler.disableTimers()
            self.resetAllThreads()
            
        if logger.disabled == False:
            # Print debug message to screen
            debugRect = self.debuggingMessage.get_rect()
            debugRect.centerx = screen.get_rect().centerx
            debugRect.centery = screen.get_rect().centery
            screen.blit(self.debuggingMessage, debugRect)
        
    def cursorCeaseFire(self):
        """Tasks to perform when the user releases the mouse button"""
        # Remove that box from around the cursor
        self.gameScreen.removeCursor(self.fireMarkerName)
        # Decrease the rotation
        vars(self.gameScreen)[self.crosshairName].increaseRot(0.5)
    
    def resetAllThreads(self):
        """Resets all threades ie. kill all viruses are re-spawn them"""
        # iterate though all of the open programs
        for prog in self.levelProgs.progs:
        #iterate over all of their threads
            for t in self.levelProgs.runningThreads[prog]:
                #Check each virus in each thread to see if it was clicked on
                vars(self.levelProgs.progs[prog])[t].restartProcess()
    
    class timeHandler(object):
        def __init__(self):
            # units are in seconds
            # Power ups will spawn between these bounds
            self.POWER_SPAWN_LOW = 8
            self.POWER_SPAWN_HIGH = 15
            # Power ups will be removed when left on the screen between these bounds
            self.POWER_REM_LOW = 7
            self.POWER_REM_HIGH = 15
            # how long a thread stop lasts
            self.THREAD_STOP_DURATION = 8
            # How many seconds a level lasts
            self.LEVEL_LENGTH = 45
            # How many seconds the level changing overlays last
            self.OVERLAY_DELAY = 7
            # How long firewalls last
            self.FIREWALL_DURATION = 4
            # AUTO-CONVERTED TO MILISECONDS, DON'T TOUCH -> EDIT VARIABLES ABOVE
            self.THREAD_STOP_DURATION *= 1000
            self.LEVEL_LENGTH *= 1000
            self.OVERLAY_DELAY *= 1000
            self.FIREWALL_DURATION *= 1000
            
            # Create new events for power ups
            self.POWERUP = pygame.USEREVENT
            self.REMOVE_POWERUP = pygame.USEREVENT+1
            self.THREAD_CONTINUE= pygame.USEREVENT+2
            self.NEXT_LEVEL = pygame.USEREVENT+3
            self.FIREWALL_STOP = pygame.USEREVENT+4
        
        def enableTimers(self):
            """Call this to re-enable timers after they have been removed from the event queue"""
            if logger.disabled == True:
                # Regenerate random timing for powerups
                POWER_UP_INTERVAL = random.randint(self.POWER_SPAWN_LOW,self.POWER_SPAWN_HIGH)*1000
                POWER_UP_REM_DELAY = POWER_UP_INTERVAL + random.randint(self.POWER_REM_LOW,self.POWER_REM_HIGH)*1000
            else:
                POWER_UP_INTERVAL = 3
                POWER_UP_REM_DELAY = 0
            # Spawn a power up every rand seconds by adding event to the event queue
            pygame.time.set_timer(self.POWERUP, POWER_UP_INTERVAL)
            pygame.time.set_timer(self.REMOVE_POWERUP, POWER_UP_REM_DELAY)
            pygame.time.set_timer(self.NEXT_LEVEL, self.LEVEL_LENGTH)
            
        def disableTimers(self):
            """Call this to disable all current timers"""
            # Setting the interval to zero disables a timer
            pygame.time.set_timer(self.POWERUP, 0)
            pygame.time.set_timer(self.REMOVE_POWERUP, 0)
            pygame.time.set_timer(self.NEXT_LEVEL, 0)
            pygame.time.set_timer(self.FIREWALL_STOP, 0)
            pygame.time.set_timer(self.THREAD_CONTINUE, 0)
            # Remove events from the event queue
            pygame.event.clear(self.NEXT_LEVEL)
            
        def disable(self, timerName):
            """Disables the passed timer name"""
            # Make sure the timer exists to avoid exception
            if timerName in vars(self):
                # Disable timer
                pygame.time.set_timer(vars(self)[timerName], 0)
            else:
                logging.warning("Can't Disable" + timerName + " - Doesn't Exist!")
                
        def debugNextLevel(self):
            """Forces the completion of the current level"""
            self.disableTimers()
            pygame.time.set_timer(self.NEXT_LEVEL, 500)
    
    def playGame(self):
        """Main Game Loop"""
        # Main game loop
        MAX_THREADS_KILLED = 4 
        while True:
            for event in pygame.event.get():
                # Quit if the user hits exit
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                    
                elif event.type==KEYDOWN:
                    # Check to see if the user wants to use a powerup
                    # powerupUsed will be the string name of the power up they used.
                    powerupUsed = self.powerUpHandler.checkKeys(event.key, self.powerUpSpawner.types, self.statTracker.powerUps)
                    # If they used a power up (checkKeys returns None if they didn't use a powerup)
                    if not(powerupUsed == None):
                        # INSERT POWER UP BEHAVIORS HERE
                        
                        if (powerupUsed == "Thread Killer"):
                            # Remove as many threads as there are levels (unless level is highter than MAX_THREADS_KILLED
                            for i in xrange(self.statTracker.level):
                                if i > MAX_THREADS_KILLED:
                                    break
                                self.levelProgs.popThread()
                            self.beepSound.play()
                            
                        elif (powerupUsed == "Thread Stopper"):
                            # Set timer to disable thread stopper
                            pygame.time.set_timer(self.timeHandler.THREAD_CONTINUE, self.timeHandler.THREAD_STOP_DURATION)
                            # Stop virus movement
                            self.gamePlay = False
                            # Notify game that the thread stopper is active
                            self.threadStop = True
                            self.beepSound.play()
                            
                        elif (powerupUsed == "OverClock"):
                            # Set the power to full
                            self.statTracker.power.power = 100
                            self.beepSound.play()
                        
                        elif (powerupUsed == "Bomb"):
                            #iterate though all of the open programs
                            for prog in self.levelProgs.progs:
                                # Reset the threads (ie. put viruses up top)
                                self.resetAllThreads()
                                self.boomSound.play()
                                    
                        elif (powerupUsed == "Firewall"):
                            # Set timer to disable firewall
                            pygame.time.set_timer(self.timeHandler.FIREWALL_STOP, self.timeHandler.FIREWALL_DURATION)
                            # Notify game that firewall is active
                            self.firewallActive = True
                            # Change the background to the firewall background
                            self.gameScreen.setBackground('res/images/bkg/wall2.jpg')
                            # Remove the main crosshair and replace it with an x (Player can't fire during firewall)
                            self.gameScreen.removeCursor(self.crosshairName)
                            self.gameScreen.newCursor(self.noFireMarkerName, 'res/images/xcross.png', (50,50))
                            self.beepSound.play()
                    
                    # Quit if user hits escape
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    # Toggle program debugging (ie player can't die, instant power up spawn, console logging, n advances to the next level)
                    elif event.key == K_d:
                        toggleLogging()
                        # Reset timers with debugging enabled
                        self.timeHandler.enableTimers()
                        logging.warning('Debugging Enabled. Have Fun!')
                    elif event.key == K_n:
                        if logger.disabled == False:
                            logging.warning('Debug Force Next Level')
                            self.timeHandler.disableTimers()
                            self.timeHandler.debugNextLevel()
#                            self.levelProgs.progs.clear()
                    elif event.key == K_r:
                        if (self.gameOver):
                            # Thanks to http://www.daniweb.com/software-development/python/code/260268 for helping me with the following two lines.
                            # This just restarts our program!
                            python = sys.executable
                            os.execl(python, python, * sys.argv)
                                
                # If the user is holding down the mouse
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.renderMenu:
                        # If the user is clicking and the menu is active, they are interacting with the menu
                        if self.menuOverlay.checkClick():
                            # checkClick() returns true if they clicked the start button
                            self.renderMenu = False
                            # Enable game
                            self.gamePlay = True
                            # Start the timers
                            self.timeHandler.enableTimers()
                            self.clickSound.play()
                            pygame.mouse.set_visible(False)
                    self.mouseHeld = True
                    if not(self.gameOver or self.renderOverlay or self.renderMenu):
                        # 3 is a pygame constant for right click
                        if event.button == 3:
                            if ("Program Upgrade" in self.statTracker.powerUps):
                                if (self.statTracker.powerUps["Program Upgrade"] > 0):
                                    newProg = None
                                    removeUs = list()
                                    addUs = list()
                                    # iterate over all of the programs
                                    for prog in self.levelProgs.progs:
                                        # check to see if the player clicked on them
                                        newProg = self.levelProgs.progs[prog].checkClick(self.powerUpSpawner)
                                        # checkClick() returns None if there is no powerUp or the user didnt click on program
                                        if (not(newProg == None)):
                                            # If the user clicked on the program
                                            self.statTracker.powerUps["Program Upgrade"] -= 1
                                            removeUs.append(prog)
                                            addUs.append(newProg)
                                    #  Avoids changing length of self.levelProgs.progs
                                    for i in xrange(len(removeUs)):
                                        # removeUs and addUs will always be equal
                                        # Grab the program id that will be replaced (to keep position)
                                        progid = self.levelProgs.progs[removeUs[i]].progid
                                        # remove the currently running program
                                        self.levelProgs.removeProg(removeUs[i])
                                        # Add the new program with the id of the old one
                                        self.levelProgs.addProg(progid, addUs[i])
                                        # store the id in the new program for later upgrade
                                        addUs[i].progid = progid
                   
                # If the user releases the mouse
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.mouseHeld = False
                    self.cursorCeaseFire()
                # Spawn new power up
                elif event.type == self.timeHandler.POWERUP:
                    self.powerUpSpawner.spawnRand()
                # Remove the power up if the player hasn't clicked it
                elif event.type == self.timeHandler.REMOVE_POWERUP:
                    self.powerUpSpawner.removePowerUp()
                # This event means end the current thread stopper
                elif event.type == self.timeHandler.THREAD_CONTINUE:
                    logging.info('ATTEMPT: Continue GamePlay')
                    # If the viruses are paused, resume their movement
                    self.gamePlay = True
                    # Notify game that thread stopper is over
                    self.threadStop = False
                    # Disable this timer until user uses another thread stopper
                    self.timeHandler.disable("THREAD_CONTINUE")
                # This event means stop the current firewall
                elif event.type == self.timeHandler.FIREWALL_STOP:
                    logging.info("ATTEMPT: FIREWALL DISABLE")
                    # Remove the no fire cursor
                    self.gameScreen.removeCursor(self.noFireMarkerName)
                    # Set cursor and background to default
                    self.initCursorAndBackground()
                    # Notify game that firewall is no longer active
                    self.firewallActive = False
                    self.timeHandler.disable("FIREWALL_STOP")
                # This event means advance to the next level
                elif event.type == self.timeHandler.NEXT_LEVEL or len(self.levelProgs.progs) < 1:
                    # If we should switch to the next level
                    if (self.gamePlay == True):
                        # Notify game that there is an overlay
                        self.renderOverlay = True
                        # Stop game from playing
                        self.gamePlay = False
                        # This means enter the disable timers loop and the timer to end the overlay
                        self.advance = True
                        self.nextLevelSound.play()
                    # If there is currently a thread stopper, delay the level switch
                    elif (self.gamePlay == False and self.threadStop == True):
                        pygame.time.set_timer(self.timeHandler.NEXT_LEVEL, self.timeHandler.THREAD_STOP_DURATION)
                    # If we should begin the next level
                    else:
                        self.timeHandler.enableTimers()
                        # Enable virus movement
                        self.gamePlay = True
                        # Notify game that there is no overlay
                        self.renderOverlay = False
                        # increase the player's level
                        self.statTracker.level += 1
                        # Initialize new programs
                        self.initProgs(self.statTracker.level)
                        # Uncomment line below to reset power ups to zero on level change
                        # self.statTracker.updatePowerUps(self.powerUpSpawner.types)
                        # Restore power
                        self.statTracker.power.power = 100
                    
            # Draw everything
            self.drawAll()
            # MUST BE CALLED AFTER drawAll() because updates rely on icon sizes and such, which are calculated in drawAll()
            self.updateAll()
            # Update the display
            pygame.display.update()
            # If there is an overlay to the game
            if (self.renderOverlay or self.renderMenu or self.gameOver):
                if self.advance:
                    # Disable timers
                    self.timeHandler.disableTimers()
                    #set a timer to hide the overlay
                    if self.renderOverlay:
                        pygame.time.set_timer(self.timeHandler.NEXT_LEVEL, self.timeHandler.OVERLAY_DELAY)
                    # Don't come back into this loop
                    self.advance = False
                    # Start all viruses at top
                    self.resetAllThreads()

# WIDTH, HEIGHT, BITS, FULLSCREEN FLAG
game = game(1024,600,32, False)
# Set the program icon
gameIcon = pygame.image.load('res/images/icon.png').convert_alpha()
pygame.display.set_icon(gameIcon)
# Set window title
pygame.display.set_caption("Virus Killer")
# Load the game icon for alt-tab
game.playGame()