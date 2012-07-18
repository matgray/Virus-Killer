# Mathew Gray
# statTracker.py
# Virus Killer by Mathew Gray is licensed under a Creative Commons 
# Attribution-NonCommercial-ShareAlike 3.0 Unported License.

import pygame

class tracker(object):
    def __init__(self, powerUpSpawner, fontSize = 20):
        """Create a objects to track player stats"""
        self.score = 0
        self.killCount = 0
        # Keep all of the current power ups in a dictionary
        self.powerUps = dict()
        # Font to use for info readout
        self.font = pygame.font.Font('res/fonts/readout.TTF', fontSize)
        # Keep all the names of the compromised files
        self.compFiles = set()
        # Keep track of how many files have been compromised
        self.num_compFiles = 0
        # Initialize a power module
        self.power = self.kernalPower()
        # Font size to print stats to the screen
        self.fontSize = fontSize
        # Starting level
        self.level = 1
        self.skill = 0
        # Initialize power ups
        self.updatePowerUps(powerUpSpawner.types)
        
    def checkGameOver(self, totalCompFiles):
        """Checks the conditions to see if the game is over.  Returns bool"""
        if self.num_compFiles > 15:
            return True
        else:
            return False
        
    def updatePowerUps(self,types):
        """(Re)initializes the player's powerups to zero"""
        for p in types:
            self.powerUps[p] = 0
    
    def addCompFile(self,name):
        """Adds the given string to the comprised files set (ie. no repeats)"""
        self.compFiles.add(name)
        self.num_compFiles += 1

    def addPowerUp(self,puName, increment):
        """Add the type of power up to the screen"""
        # Increment is the number of power ups to add
        if puName in self.powerUps:
            self.powerUps[puName] += increment
        else:
            self.powerUps[puName] = increment
            
    def addKill(self):
        """Adds a kill to the kill counter to be displayed"""
        self.killCount += 1
        
    def update(self, mouseHeld):
        """Updates the score and the power level"""
        self.score = self.killCount
        self.power.update(mouseHeld)
        self.skill = int(self.score/(self.num_compFiles+1))
        
    def draw(self, screen, types, screenWidth, screenHeight):
        """Draws the user's statistics to the screen"""
        # Note: Anti-aliasing MUST be disabled to draw text with alpha
        def __getOutputColor(powerNum):
            """Returns the color, alpha to draw the text (PRIVATE METHOD)"""
            # If the user has any powerups, return green
            if powerNum > 0:
                return (30,255,0), 175
            # If the user has no powerups, return red
            else:
                return (255,0,0), 100
        
        def __drawPowerUpsStatus():
            """Draws the current power up text to the screen (PRIVATE METHOD)"""
            readout.set_alpha(alphaLevel)           
            screen.blit(readout,currentPos)
            # Returns the new position to render text
            return (currentPos[0],currentPos[1] - 1.25*self.fontSize)
        
        # Render the text and score with semi-transparency
        score = self.font.render("Score: " + str(self.score), False, (255, 255, 255))
        score.set_alpha(100)
        compReadout = self.font.render("Compromised Files: " + str(self.num_compFiles), False, (255, 255, 255))
        compReadout.set_alpha(100)
        # playerInfo will hold everything we want to display in the mid left
        playerInfo = [score, compReadout]
        currentPos = (0,int(screenHeight/2))
        # Step though info and print on the left
        for e in playerInfo:
            screen.blit(e,currentPos)
            currentPos = (currentPos[0],currentPos[1]+int(2*self.fontSize))
            
        # Set though all of the power ups and blit them to the screen
        currentPos = (10,screenHeight-self.fontSize-10)
        
        # Draw all of the powerups that require a key to use first (blits bottom up)
        for p in self.powerUps:
            textColor, alphaLevel = __getOutputColor(self.powerUps[p])
            if types[p].key != None:
                # Prepend the key to press
                readout = self.font.render(types[p].key + ' : ' + p + 's : ' + str(self.powerUps[p]), False, textColor)
                # Update the current pos and draw to the screen
                currentPos = __drawPowerUpsStatus()
                
        # Draw all of the powerups that don't require a key to use (put them on top)
        for p in self.powerUps:
            if types[p].key == None:
                textColor, alphaLevel = __getOutputColor(self.powerUps[p])
                # Print the name and the number
                readout = self.font.render(p + 's : ' + str(self.powerUps[p]), False, textColor)
                # Update pos
                currentPos = __drawPowerUpsStatus()
      
        
    class kernalPower(object):
        def __init__(self):
            """Initialize a new power monitor"""
            self.power = 100
            # deltaBuffer holds a float between -1,1 (exclusive)  when it goes out of this interval, self.power is updated accordingly
            self.deltaBuffer = 0.0
        
        def add(self, amount = .01):
            """Adds amount to the power"""
            self.deltaBuffer += amount
                
        def rem(self,amount = .35):
            """removes amount from the power"""
            self.deltaBuffer -= amount
                
        def get(self):
            """Get current power"""
            return self.power
            
        def update(self, mouseHeld):
            """Updates the statistics"""
            if not(mouseHeld):
                REGENERAGE_RATE = .1
                self.deltaBuffer += REGENERAGE_RATE
            
            # If the deltaBuffer has gone out of bounds, add it's excess to power
            while self.deltaBuffer < -1.0:
                self.power -= 1
                self.deltaBuffer += 1
            while self.deltaBuffer > 1.0:
                self.power += 1
                self.deltaBuffer -= 1.0
            
            # Don't let the power go over 100
            if self.power > 100:
                self.power = 100
            # or negative
            if self.power < 0:
                self.power = 0
                    
        def draw(self,screen, screenWidth, screenHeight):
            """Draws the power bar in the appropriate place"""
            KERNAL_POWER_FONT_SIZE = 17
            BAR_COLOR = (255,0,0,75)
            READOUT_COLOR = (255, 255, 255)
            
            # Create a transparent surface representing kernal power left.  The bar should be 4.5% of the screen (Measured Image)
            bar = pygame.Surface((screenWidth*(self.power/100.0),.045*screenHeight), pygame.SRCALPHA)
            # RGBA
            bar.fill(BAR_COLOR)
            # The bar should start 64.3% of the way down the screen to be between the bar thing on the background
            screen.blit(bar, (0, int(.643*screenHeight)))
            # Create a font
            font = pygame.font.Font('res/fonts/kernalPower.TTF', KERNAL_POWER_FONT_SIZE)
            # Render the text as red
            text = font.render('Kernel Power: ' + str(int(self.power)), True, READOUT_COLOR)
            # Blit the text - The bar is 65% of the way down the screen
            screen.blit(text, (int(screenWidth/2 - (.55*KERNAL_POWER_FONT_SIZE*len("Kernel Power"))), 0 + .645*screenHeight))
            