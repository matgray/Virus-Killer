# Mathew Gray
# virtProgram.py
# Virus Killer by Mathew Gray is licensed under a Creative Commons 
# Attribution-NonCommercial-ShareAlike 3.0 Unported License.

import pygame, logging

logging.basicConfig(level=logging.DEBUG)

class program(object):
    def __init__(self, thumbnail, name, progType, progLevel = 1, progid = None):
        """Creates a new program instance"""
        self.name = name
        # Save original thumbnail for on-the-fly magnification during harder levels
        self.originalThumbnail = self.scaledthumbnail = pygame.image.load(thumbnail).convert_alpha()
        # Location of the program
        self.loc = (0,0)
        # Number of threads currently running
        self.threadCount = 0
        # Name of all of the threads
        self.threads = list()
        # Font to use for info readout
        self.font = pygame.font.Font('res/fonts/readout.TTF', 25)
        self.progType = progType
        self.progid = progid
        self.progLevel = progLevel
        
    def update(self):
        # Cap number of the threads
        THREAD_CAP = 2
        if self.threadCount > THREAD_CAP:
            numRemove = self.threadCount-THREAD_CAP
            # Remove extra threads
            for i in xrange(numRemove):
                self.popThread()
        
    def checkClick(self,powerUps):
        """Checks to see if a program was clicked on"""
        topLeft, bottomRight = self.getBoundingBox()
        # Get the position of the mouse
        mousePos = pygame.mouse.get_pos()
        # If the mouse clicks on the virus
        if (topLeft[0] < mousePos[0] and mousePos[0] < bottomRight[0]):
            if (topLeft[1] < mousePos[1] < bottomRight[1]):
                # Return the power up of the program clicked
                return powerUps.upgrade(self.progType)
        # Return none if the user didnt click or there are no upgrade left
        return None
                        
    def getBoundingBox(self):
        """Gets the bounding box for a program"""
        return self.loc,(self.loc[0]+self.iconSize[0], self.loc[1] + self.iconSize[1])
        
    def draw(self,screen,progPos,currentPos,vertDisp):
        """Draw program to screen"""
        screen.blit(self.scaledthumbnail, (progPos,vertDisp))
        # notify program of where it's located
        self.storeLoc((progPos,vertDisp))
        
        # Render the text and store
        textReadout = self.font.render("Threads: " + str(self.threadCount), True, (255, 255, 255))
        
        # Blit the number of threads
        screen.blit(textReadout, (progPos - 28, vertDisp-15))
        
    def __repr__(self):
        return self.name
    
    def resizeIcon(self, size):
        """Resizes the program icon the the given size"""
        self.scaledthumbnail = pygame.transform.smoothscale(self.originalThumbnail, size)
        self.iconSize = size
        self.font = pygame.font.Font('res/fonts/readout.TTF', size[0]/3)
        
    def storeLoc(self,loc):
        """Store programs location (ie. move program and it's threads to given position"""
        # Store location
        self.loc = loc
        # Step through all of the threads
        for t in self.threads:
            # Update thread location
            vars(self)[t].updateLocation(self.loc)
                
    def newProgramThread(self):
        """Creates a new thread in the program"""
        self.threadCount += 1
        # Name the thread 'thread' with the thread number appended
        name = "thread" + str(self.threadCount)
        # Create a thread with the generated name
        vars(self)[name]= self.virusContainer(self.progLevel)
        # append the name of the thread to our thread list
        self.threads.append(name)
        # return the list of threads so the program container can confirm thread was created
        return self.threads
    
    def popThread(self,nameOfThread=None):
        """Remove the given thread, or remove the last thread initialized if no name passed"""
        if nameOfThread == None:
            # Try to pop the thread
            try:
                logging.info('-EXEC-REMOVE:' + str(self.threads[len(self.threads)-1]) + '\ntype: Thread \nfrom' + str(self.name))
                self.threads.pop()
                self.threadCount-=1
            except:
                logging.exception('Error no threads Remain!')
        # If given a name of a thread, try to remove the thread with that name
        else:
            try:
                logging.info('-EXEC-REMOVE: ' + nameOfThread + 'type: Thread')
                del self.spawnedList[nameOfThread]
                self.threadCount-=1
            except:
                logging.exception('Error no thread named: ' + nameOfThread)
        
    class virusContainer(object):
        def __init__(self, progLevel):
            """Initialize a new virus container (aka thread) instance"""
            #Store the viruses in a dictionary with the key being their name and the value being the virus object
            self.spawnedList = dict()
            # Create a new spawner (keeps track of when to spawn more viruses)
            self.spawner = spawner()
            # location of the container
            self.loc = (0,0)
            # Keeps track of the number of viruses in the container
            self.count = 0
            self.progLevel = progLevel
            
        def restartProcess(self):
            """Clears all of the viruses in the thread from the screen"""
            self.spawnedList = dict()
            
        def updateLocation(self, loc):
            """Changes the thread's location"""
            self.loc = loc
        
        def spawnVirus(self,name,virusType):
            """Spawns a virus in the given thread"""
            # Name the virus the program's name with the virus number appended
            name = name + str(self.count)
            # Register that a new virus was spawned
            self.count += 1
            # add the type of virus and it's location to the spawn lit
            self.spawnedList[name] = [virusType,self.loc]
            
        def displayViruses(self,screen):
            """Blits the viruses to the screen"""
            # Iterate though the dictionary of viruses in the current thread
            for i in self.spawnedList:
                # Draw the virus
                self.spawnedList[i][0].draw(screen)
                
        def updateViruses(self,ticks,statTracker, dimensions, bMove, stolenSound):
            """Updates the viruses on the screen"""
            deleteUs = set()
            # Iterate though the dictionary of viruses
            for i in self.spawnedList:
                # Update the virus properties
                status = self.spawnedList[i][0].update(ticks, dimensions,bMove)
                # Returns false if it sole a file
                if (status == False):
                    deleteUs.add(i)
            # delete all viruses that stole data
            for v in deleteUs:
                # make sure the virus exists before removing from dictionary
                if v in self.spawnedList:
                    # Remember the compromised file
                    statTracker.addCompFile(self.spawnedList[v][0].targetFile[0])
                    del self.spawnedList[v]
                    logging.info("EXEC-DEL "+ str(v))
                    stolenSound.play()
                else:
                    logging.error("EXEC-DEL FAILED "+ str(v) +"Does Not Exist")
        
        def checkForSpawn(self):
            """returns bool of whether or not new viruses should be spawned"""
            return self.spawner.update(len(self.spawnedList), self.progLevel)
        
        def checkClick(self,statTracker, delSound):
            """Check to see if the player clicked on any of the viruses in the thread"""
            # Iterate though all of the viruses in the thread
            for i in self.spawnedList:
                # get the bounding box of the virus
                topLeft, bottomRight, size = self.spawnedList[i][0].getBoundingBox()
                # Get the position of the mouse
                mousePos = pygame.mouse.get_pos()
                # If the mouse if on the virus
                if (topLeft[0] < mousePos[0] and mousePos[0] < bottomRight[0]):
                    if (topLeft[1] < mousePos[1] < bottomRight[1]):
                        # Try to delete the virus from the list
                        try:
                            logging.info('-EXEC-REMOVE: ' + str(i) + ' type: Virus')
                            del self.spawnedList[i]
                            statTracker.addKill()
                            delSound.play()
                        except:
                            logging.exception('Error no virus named: ' + str(i))
                        return True
                    
        def checkFirewall(self, statTracker, screenWidth, screenHeight):
            """Ensures that no viruses cross the firewall"""
            for i in self.spawnedList:
                # get the bounding box of the virus
                topLeft, bottomRight, size = self.spawnedList[i][0].getBoundingBox()
                if (topLeft[1] < .7*screenHeight and topLeft[1] > .63*screenHeight) or (bottomRight[1] < .63*screenHeight and bottomRight[1] > .7*screenHeight):
                    try:
                        logging.info('-EXEC-REMOVE: ' + str(i) + 'type: Virus')
                        del self.spawnedList[i]
                        statTracker.addKill()
                    except:
                        logging.exception('Error no virus named: ' + str(i))
                    return True

class spawner(object):
    def __init__(self):
        """Initialize a new thread"""
        self.numActive = 0
        self.MAX_SPAWN = 2
        self.newlySpawned = 0
    
    def update(self,numActive, progLevel):
        """Returns bool if more viruses should be spawned"""
        secsRunning = pygame.time.get_ticks() / 1000
        self.numActive = numActive
        # The higher the level of the PROGRAM (NOT PLAYER) the less viruses spawned
        if (numActive < (6/progLevel)):
            if (secsRunning % 5 == 0 and self.newlySpawned%2 == 0):
                self.newlySpawned += 1
                return True
        return False
        