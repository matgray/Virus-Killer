# Mathew Gray
# containers.py
# Virus Killer by Mathew Gray is licensed under a Creative Commons 
# Attribution-NonCommercial-ShareAlike 3.0 Unported License.

import pygame,random, viruses, logging

logging.basicConfig(level=logging.DEBUG)

def calculateContainerProperties(NUM_ICONS, screenWidth, screenHeight, \
bottomOffset = 0):
# These variables control how the application icons look / are spaced
    MAX_ICON_HEIGHT_PERCENT = .10
    PADDING_PERCENT = .05
    REL_ICON_SPACING = .70
    # AUTO-CALCULATED VARIABLES DO NOT MODIFY - MODIFY ABOVE VARIABLES TO CHANGE 
    #THE ONES BELOW
    REL_ICON_PERCENT = 1 - REL_ICON_SPACING
    REL_SPACE= screenWidth - 2*(PADDING_PERCENT*screenWidth)
    spacing = REL_ICON_SPACING*REL_SPACE/NUM_ICONS
    pos = PADDING_PERCENT*screenWidth  
    # Determine Optimal Icon Size
    iconLen = int(REL_ICON_PERCENT*REL_SPACE/NUM_ICONS)
    # Don't let the icon size be greater than the max icon size
    if iconLen > int(MAX_ICON_HEIGHT_PERCENT*screenHeight):
        iconLen = int(MAX_ICON_HEIGHT_PERCENT*screenHeight)
        # If there aren't enough icons to fill the space, center them
        pos = ((screenWidth/2)-(iconLen*(NUM_ICONS+1)))/2 + \
        int(bottomOffset*(2.5*iconLen))
        
    return iconLen, spacing, pos

class programContainer():
    def __init__(self):
        # set of programs
        self.progs = dict()
        #List of absolute program positions
        self.progsPos = list()
        # Dictionary of all of the threads running in each program
        self.runningThreads = dict()
        self.time = pygame.time.Clock()
        self.ticks = 0
        # virusTypes: list of tuples of types of viruses to spawn
        # [0] : virus subclass name
        # [1] : image to use
        self.virusTypes = [('malware','res/images/greenVirus.png'),('trojan','res/images/redVirus.png')]
    
    # Calculates the absolute positions of the top programs
    def calcProgsPos(self,screenWidth,screenHeight):
        NUM_ICONS = len(self.progs)
        # Can't perform calculations if there aren't any icons!
        if (NUM_ICONS == 0):
                return False
        # Calculate the 
        iconLen,spacing, pos = \
        calculateContainerProperties(NUM_ICONS,screenWidth, screenHeight)
        # Resize all of the icons
        for prog in self.progs:
            self.progs[prog].resizeIcon((iconLen, iconLen))
            
        # Calculate all of the positions
        for i in xrange(NUM_ICONS):
            self.progsPos.append(pos)
            pos +=iconLen + spacing
            # Store icon size
            self.iconLen = iconLen
    
    # Call this to initialize a new program
    def addProg(self,name,program):
        self.progs[name] = program
        # INITIALIZE NEW THREADS HERE
        self.progs[name].newProgramThread()
        runningThreads = self.progs[name].newProgramThread()
        # Store running threads
        self.runningThreads[name] = runningThreads
        
    def removeProg(self,program):
        try:
            logging.info('-EXEC-REMOVE: ' + program)
            del self.progs[program]
        except:
            logging.exception('Deletion Failed: ' + program + 'does not exist')
    
    #Removes a random thread from a random program
    def popThread(self):
        try:
            # Throws exception if it can't make a choice
            progThread = random.choice(self.progs.keys())
        except:
            logging.exception("There Are No More Programs to remove!")
            return False
            
        # remove the thread from program    
        self.progs[progThread].popThread()
        # update the list of threads
        self.runningThreads[progThread] = self.progs[progThread].threads
        #iterate though all of the programs and make sure there is at least 1 
        #thread running
        for p in self.progs:
            if len(self.runningThreads[p]) < 1:
                # if not, close the program (ie. remove icon)
                self.removeProg(p)
                # return to prevent data modified exception
                return True
        
    # Call this to show viruses
    def showViruses(self, screen):
        # Iterate though all of the running programs
        for prog in self.progs:
            # Iterate though all of the running threads of each program
            for t in self.runningThreads[prog]:
                # Display the viruses in the current thread
                vars(self.progs[prog])[t].displayViruses(screen)
                
    def updateViruses(self,folders, statTracker,dimensions, bMove, stolenSound):
        self.ticks = self.time.tick(70)  # this  time.tick() waits enough to make your max framerate n
        # Iterate though all of the running programs
        for prog in self.progs:
            # Iterate though all of the running threads of each program
            for t in self.runningThreads[prog]:
                # Spawn viruses until our virus spawner says stop
                # Command Clarification: 
                # Get dict of variables in self.progs[prog] and then grab the one with key t                
                while(vars(self.progs[prog])[t].checkForSpawn()):       
                    attackFolder = random.choice(folders.keys())
                    targetFile = random.sample(folders[attackFolder].files,1)
                    # Spawn a new virus to the current thread of the current program
                    virusTypeIndex = random.randint(0,len(self.virusTypes)-1)
                    vars(self.progs[prog])[t].spawnVirus(prog,vars(viruses)[self.virusTypes[virusTypeIndex][0]](self.virusTypes[virusTypeIndex][1], (self.iconLen/2, self.iconLen/2), self.progs[prog].loc, folders[attackFolder].loc, targetFile,statTracker.level))
                vars(self.progs[prog])[t].updateViruses(self.ticks,statTracker,dimensions, bMove, stolenSound)
    
    # Displays the currently running programs on the top of the screen
    def showProgs(self,screen,screenWidth,screenHeight):
        # Update where each program should be positioned
        self.calcProgsPos(screenWidth,screenHeight)
        # Set Vertical displacement
        vertDisp = self.iconLen/2
        
        #This will iterate though all of our stored positions
        currentPos = 0
        # self.progs is a dict -> grab each name in the dict and print it
        for prog in self.progs:
            progPos = self.progsPos[currentPos]
            # Grab associated program position
            self.progs[prog].draw(screen,progPos,currentPos,vertDisp)
            currentPos+= 1
            
class folderContainer():
    def __init__(self):
        # Store all of the folders in a dictionary
        self.folders = dict()
        #List of absolute folder  positions
        self.folderPos = list()
        
    def addFolder(self, folderName, givenFolder):
        self.folders[folderName] = givenFolder
        
    def removeFolder(self,folderName):
        try:
            logging.debug('-EXEC-REMOVE: ' + folderName + 'type: folder')
            del self.folders[folderName]
        except:
            logging.exception(\
            'Deletion Failed: '+ folderName + 'does not exist')
    
    def calcFolderPos(self,screenWidth,screenHeight):
    # Calculates the absolute positions of the top programs
        NUM_ICONS = len(self.folders)
        # Can't perform calculations if there aren't any icons!
        if (NUM_ICONS == 0):
                return False
        # Calculate the 
        iconLen,spacing, pos = calculateContainerProperties(NUM_ICONS,\
        screenWidth, screenHeight, 1)
        # Resize all of the icons
        for folder in self.folders:
            self.folders[folder].resizeIcon((iconLen, iconLen))
            
        # Calculate all of the positions
        for i in xrange(NUM_ICONS):
            self.folderPos.append(pos)
            pos += iconLen + spacing
            # Store icon size
            self.iconLen = iconLen
            
    # Displays the folders on the bottom of the screen
    def showFolders(self,screen,screenWidth,screenHeight):
        # Update where each program should be positioned
        self.calcFolderPos(screenWidth,screenHeight)
        # Set Vertical displacement
        vertDisp = screenHeight - self.iconLen
        
        #This will iterate though all of our stored positions
        currentPos = 0
        # self.folders is a dict -> grab each name in the dict and print it
        for folder in self.folders:
            # Grab associated program position
            folderPos = self.folderPos[currentPos]
            # Draw program to screen
            screen.blit(self.folders[folder].scaledthumbnail, \
            (folderPos,vertDisp))
            # notify program of where it's located
            self.folders[folder].storeLoc((folderPos,vertDisp))
            currentPos+= 1
