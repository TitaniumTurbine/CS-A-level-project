import pygame
from pygame.locals import *
from random import randint
import math

pygame.init()

global window
global running
global screenWidth
global screenHeight
global widthScale
global heightScale
global currentMenu
global levelNumber
global world
global player
global existingLevels
global attackCooldownValue

#main procedure, sets up required variables, loads screen width and height from settings file, sets up the game window then switches to the main menu
def main():
    global window
    global running
    global screenWidth
    global screenHeight
    global widthScale
    global heightScale
    global currentMenu
    global levelNumber
    global existingLevels
    global fullscreen

    #open settings file and set screen width and height to values on the top two lines in the file
    settings = open("settings.txt","r")
    lines = settings.readlines()
    settings.close()
    #print(lines)
    for i in range(0, len(lines) - 1):
        lines[i] = lines[i][:-1]
    #print(lines)

    if len(lines) < 8:
        screenWidth = 800
        screenHeight = 450
        settings = open("settings.txt","w")
        settings.write("800\n450\n119\n115\n97\n100\n304\n27\n292\nFalse")
        settings.close()

    else:
        if lines[0].isdigit() == True and lines[1].isdigit() == True:
            screenWidth = int(lines[0])
            screenHeight = int(lines[1])
        else:
            screenWidth = 800
            screenHeight = 450

    widthScale = screenWidth / 800
    heightScale = screenHeight / 450
        
    if openSettings()[9] == "True":
        fullscreen = True
        window = pygame.display.set_mode((screenWidth,screenHeight), pygame.FULLSCREEN)
    else:
        fullscreen = False
        window = pygame.display.set_mode((screenWidth,screenHeight))
    pygame.display.set_caption("game")
    gameIcon = pygame.image.load("icon.png")
    pygame.display.set_icon(gameIcon)
    print(screenWidth, screenHeight)
    running = True
    levelNumber = 1
    existingLevels = 3

    lines = openStats()
    if len(lines) < existingLevels + 1:
        string = ""
        for i in range(0, existingLevels + 1):
            if i == 0:
                string += "0"
            else:
                string += "\n0"

        stats = open("statistics.txt","w")
        stats.write(string)
        stats.close()

    currentMenu = "main"


#button for menu interactions
class button:
    def __init__(self, window, string, font, fontSize, fontColour, buttonColour, width, height, x, y, command):
        self.string = string
        self.font = font
        self.fontSize = int(heightScale * fontSize)
        self.fontColour = fontColour
        self.buttonColour = buttonColour
        self.width = widthScale * width
        self.height = heightScale * height
        self.x = widthScale * x
        self.y = heightScale * y
        self.command = command
        textFont = pygame.font.SysFont(self.font, self.fontSize) 
        text = textFont.render(self.string, True, self.fontColour)
        pygame.draw.rect(window,self.buttonColour,pygame.Rect(self.x,self.y,self.width,self.height))
        window.blit(text, (self.x + widthScale * 10, self.y + self.height / 2 - widthScale * 7))

    def click(self, cmdParams):
        if pygame.mouse.get_pos()[0] > self.x and pygame.mouse.get_pos()[0] < self.x + self.width and pygame.mouse.get_pos()[1] > self.y and pygame.mouse.get_pos()[1] < self.y + self.height and pygame.mouse.get_pressed()[0] == 1:
            if len(cmdParams) == 2:
                self.command(cmdParams[0], cmdParams[1])
            elif len(cmdParams) == 1:
                self.command(cmdParams[0])
            else:
                self.command()


#stores data about a level, has procedures for adding and removing enemies
class level:
    def __init__(self, name, playerStartCoords, obstacles, enemyStarts):
        self.name = name
        self.playerStartCoords = playerStartCoords
        self.obstacles = obstacles
        self.enemyStarts = enemyStarts
        self.activeEnemies = []
        self.playerProjectiles = []
        self.enemyProjectiles = []

        self.grid = []
        for i in range(0, 16):
            for j in range(0, 9):
                self.grid.append([(800/16) * i * widthScale, (450/9) * j * heightScale, False, False])
        print(len(self.grid))
        for obstacle in self.obstacles:
            for square in self.grid:
                if (obstacle.type == "hazard" and obstacle.isSolid == True) or (obstacle.type != "hazard"):
                    if obstacle.x < square[0] + 50 * widthScale and obstacle.x + obstacle.width > square[0] and obstacle.y < square[1] + 50 * heightScale and obstacle.y + obstacle.height> square[1]:
                        square[2] = True

    def addEnemy(self, enemy):
        num = 0
        for i in range(0, len(self.activeEnemies)):
            if self.activeEnemies[i].type == "none":
                if num == 0:
                    self.activeEnemies[i] = enemy
                    num += 1
        if num == 0:
            self.activeEnemies.append(enemy)

    def removeEnemy(self, enemy):
        for i in range(0, len(self.activeEnemies)):
            if self.activeEnemies[i] == enemy:
                #del self.activeEnemies[i]
                self.activeEnemies[i] = noneEnemy()

    def addEnemyProjectile(self, projectile):
        num = 0
        for i in range(0, len(self.enemyProjectiles)):
            if self.enemyProjectiles[i].active == False:
                if num == 0:
                    self.enemyProjectiles[i] = projectile
                    num += 1
        if num == 0:
            self.enemyProjectiles.append(projectile)

    def addPlayerProjectile(self, projectile):
        num = 0
        for i in range(0, len(self.playerProjectiles)):
            if self.playerProjectiles[i].active == False:
                if num == 0:
                    self.playerProjectiles[i] = projectile
                    num += 1
        if num == 0:
            self.playerProjectiles.append(projectile)

    def getAdjacentSquares(self, square):
        adjacentSquares = []
        for i in range(0,len(self.grid)):
            if self.grid[i] == square:
                if i-1 > 0 and i-1 < len(self.grid) and self.grid[i-1][2] == False:
                    upSquare = self.grid[i-1]
                    adjacentSquares.append(upSquare)
                else:
                    upSquare = None
                if i+1 > 0 and i+1 < len(self.grid) and self.grid[i+1][2] == False:
                    downSquare = self.grid[i+1]
                    adjacentSquares.append(downSquare)
                else:
                    downSquare = None
                if i+9 > 0 and i+9 < len(self.grid) and self.grid[i+9][2] == False:
                    rightSquare = self.grid[i+9]
                    adjacentSquares.append(rightSquare)
                else:
                    rightSquare = None
                if i-9 > 0 and i-9 < len(self.grid) and self.grid[i-9][2] == False:
                    leftSquare = self.grid[i-9]
                    adjacentSquares.append(leftSquare)
                else:
                    leftSquare = None
        return adjacentSquares


#entity, an object which can move around the screen
class entity:
    def __init__(self, health, x, y, speed):
        self.health = health
        self.x = widthScale * x
        self.y = heightScale * y
        self.speed = speed

    def getHealth(self):
        return self.health

    def setHealth(self, newHealth):
        self.health = newHealth

    def moveUp(self, amount):
        self.y -= amount

    def moveDown(self, amount):
        self.y += amount

    def moveLeft(self, amount):
        self.x -= amount

    def moveRight(self, amount):
        self.x += amount

    def getX(self):
        return self.x

    def setX(self, newX):
        self.x = newX

    def getY(self):
        return self.y

    def setY(self, newY):
        self.y = newY

    def getCurrentSquare(self):
        squareCoords = [50*widthScale * (self.x // (50*widthScale)), 50*heightScale * (self.y // (50*heightScale))]
        i = squareCoords[0] / widthScale / (800/16)
        j = squareCoords[1] / heightScale / (450/9)
        if i*9 + j <= 144:
            currentSquare = world.grid[int(i*9+j)]
            return currentSquare

    def pathFind(self, start, dest):
        global endSquare
        if start == self.getCurrentSquare():
            self.path = []
            self.checked = []
            self.toCheck = []
            self.totalDist = 0

        self.checked.append([start, self.totalDist])
        self.totalDist += 1
        print(self.totalDist)
        adjacentSquares = world.getAdjacentSquares(start)
        for item in self.checked:
            for square in adjacentSquares:
                if square == item[0]:
                    adjacentSquares.remove(square)
        for item in self.toCheck:
            for square in adjacentSquares:
                if square == item[0]:
                    adjacentSquares.remove(square)
        if len(adjacentSquares) > 0:
            for square in adjacentSquares:
                self.toCheck.append(square)
                self.pathFind(square, dest)
        else:
            while self.totalDist >= 0:
                self.path.append(self.checked[-1][0])
                self.totalDist -= 1
            self.setX(self.path[0][0])
            self.setY(self.path[0][1])

        
        

    def gotoSquare(self, square):
        self.dirVect = [(square[0] + 25*widthScale - self.x) / math.sqrt((square[0] + 25*widthScale - self.x)**2 + (square[1] + 25*heightScale - self.y)**2), (square[1] + 25*heightScale - self.y) / math.sqrt((square[0] + 25*widthScale - self.x)**2 + (square[1] + 25*heightScale - self.y)**2)]
        while self.getCurrentSquare != square:
            self.moveRight(widthScale * self.dirVect[0] * self.speed)
            self.moveDown(heightScale * self.dirVect[1] * self.speed)

#entity which the player controls
class playerChr(entity):
    def __init__(self, health, x, y, speed, shieldHealth, sprintMult, atkDamage):
        entity.__init__(self, health, x, y, speed)
        self.shieldHealth = shieldHealth
        self.sprintMult = sprintMult
        self.isSprinting = False
        self.atkDamage = atkDamage
        self.isBlocking = False
        self.xSize = widthScale * 17
        self.ySize = heightScale * 17
        self.blockTimerMax = float(openUpgrades()[3])
        self.blockTimer = self.blockTimerMax

    def getShieldHealth(self):
        return self.shieldHealth

    def setShieldHealth(self, newHealth):
        self.shieldHealth = newHealth

    def getIsSprinting(self):
        return self.isSprinting

    def setSprinting(self, boolean):
        self.isSprinting = boolean

    def shoot(self):
        if self.isBlocking == False:
            proj = projectile(self.atkDamage, float(openUpgrades()[5]), (0,255,0), pygame.mouse.get_pos()[0] - widthScale * 2.5, pygame.mouse.get_pos()[1] - heightScale * 2.5, self.x + self.xSize/2 - widthScale * 2.5, self.y + self.ySize/2 - heightScale * 2.5)
            world.addPlayerProjectile(proj)
    def setBlocking(self, boolean):
        self.isBlocking = boolean

#enemy entity which attacks player and the player must attack
class enemy(entity):
    def __init__(self, health, x, y, speed, atkDamage, scoreGiven):
        entity.__init__(self, health, x, y, speed)
        self.atkDamage = atkDamage
        self.scoreGiven = scoreGiven
        self.direction = 0
        self.xSize = widthScale * 15
        self.ySize = heightScale * 15
        self.type = "normal"
        self.attackCooldownValue = 30
        self.attackCooldown = 0

        #each enemy has a 1/10000 chance to be yellow instead of red, just for fun
        colourVariant = randint(1,10000)
        if colourVariant == 1:
            self.colour = (250,200,0)
        else:
            self.colour = (200,0,0)

    def shoot(self):
        proj = enemyProjectile(self.atkDamage, 5, (255,0,0), self.x + self.xSize/2 - widthScale * 2.5, self.y + self.ySize/2 - heightScale * 2.5)
        world.addEnemyProjectile(proj)

#enemy variant which is larger and can block incoming attacks
class blockingEnemy(enemy):
    def __init__(self, health, x, y, speed, atkDamage, scoreGiven, shieldHealth):
        enemy.__init__(self, health, x, y, speed, atkDamage, scoreGiven)
        self.shieldHealth = shieldHealth
        self.isBlocking = False
        self.xSize = widthScale * 20
        self.ySize = heightScale * 20
        self.type = "blocking"

    def getShieldHealth(self):
        return self.shieldHealth

    def setShieldHealth(self, newHealth):
        self.shieldHealth = newHealth

    def setBlocking(self, boolean):
        self.isBlocking = boolean

    def getBlocking(self):
        return self.isBlocking

    def shoot(self):
        if self.isBlocking == False:
            proj = enemyProjectile(self.atkDamage, 5, (255,0,0), self.x + self.xSize/2 - widthScale * 2.5, self.y + self.ySize/2 - heightScale * 2.5)
            world.addEnemyProjectile(proj)

#temporary enemy type to switch enemies to when they have been defeated, then gets replaced by new enemies when they are created
class noneEnemy(enemy):
    def __init__(self):
        enemy.__init__(self, 1, -20, -20, 0, 0, 0)
        self.type = "none"
        self.colour = (0,0,0)
    def shoot(self):
        self.x = -20

#projectile which is shot from a position in the direction of another position
class projectile:
    global screenWidth
    def __init__(self, damage, speed, colour, targetX, targetY, startX, startY):
        self.damage = damage
        self.speed = speed
        self.colour = colour
        self.targetX = targetX
        self.targetY = targetY
        self.startX = startX
        self.startY = startY
        self.x = startX
        self.y = startY
        self.active = True
        self.dirVect = [(self.targetX - self.startX) / math.sqrt((self.targetX - self.startX)**2 + (self.targetY - self.startY)**2), (self.targetY - self.startY) / math.sqrt((self.targetX - self.startX)**2 + (self.targetY - self.startY)**2)]

    #move the projectile and set it to inactive if it moves off the screen
    def checkHit(self):
        if self.x < 0 or self.x > screenWidth or self.y < 0 or self.y > screenHeight:
            self.active = False
        else:
            #self.x += (self.targetX - self.startX) / self.speed
            #self.y += (self.targetY - self.startY) / self.speed
            self.x += widthScale * self.dirVect[0] * self.speed
            self.y += heightScale * self.dirVect[1] * self.speed

    def setX(self, value):
        self.x = value

    def setY(self, value):
        self.y = value


#projectile variant that the enemies shoot, moves in direction of player and has interactions with player character
class enemyProjectile(projectile):
    def __init__(self, damage, speed, colour, startX, startY):
        projectile.__init__(self, damage, speed, colour, player.x + player.xSize / 2, player.y + player.ySize / 2, startX, startY)

    def checkHit(self):
        if self.x < 0 or self.x > screenWidth or self.y < 0 or self.y > screenHeight:
            self.active = False
        if self.x > player.x and self.x + widthScale * 5 < player.x + player.xSize and self.y > player.y and self.y + heightScale * 5 < player.y + player.ySize:
            self.active = False
            if player.isBlocking == True and player.getShieldHealth() > 0:
                player.setShieldHealth(player.getShieldHealth() - self.damage)
            else:
                player.setHealth(player.getHealth() - self.damage)
        else:    
            self.x += widthScale * self.dirVect[0] * self.speed
            self.y += heightScale * self.dirVect[1] * self.speed
            

#object which can be placed around level and interacts with entities
class obstacle:
    def __init__(self, x, y, width, height):
        self.x = widthScale * x
        self.y = heightScale * y
        self.width = widthScale * width
        self.height = heightScale * height

    #prevents entity from moving inside solid obstacle by comparing entity position to wall edges to work out which edge is closest and therefore which they tried to move through, then changing the enity's position to the other side of that edge
    def solid(self, ent):
        #left side
        if float(ent.getX()) - self.x < float(ent.getY()) - self.y and float(ent.getX() + ent.xSize) - self.x < (self.y + self.height) - float(ent.getY()) and float(ent.getX()) - self.x < (self.x + self.width) - float(ent.getX()):
            ent.setX(self.x - ent.xSize)

        #right side
        elif (self.x + self.width) - float(ent.getX() + ent.xSize) < float(ent.getY()) - self.y and (self.x + self.width) - float(ent.getX()) < (self.y + self.height) - float(ent.getY()):
            ent.setX(self.x + self.width)

        #top
        elif float(ent.getY()) - self.y < (self.y + self.height) - float(ent.getY()):
            ent.setY(self.y - ent.ySize)

        #bottom
        elif (self.y + self.height) - float(ent.getY()) < (self.x + self.width) - float(ent.getX()):
            ent.setY(self.y + self.height)

        #bottom right corner
        elif (self.x + self.width) - float(ent.getX()) < float(ent.getX()) - self.x and (self.y + self.height) - float(ent.getY()) < float(ent.getY() - self.y):
            ent.setX(self.x + self.width)
            ent.setY(self.y + self.height)

        #top left corner / just in case
        else:
            ent.setX(self.x - ent.xSize)
            ent.setY(self.y - ent.xSize)


#obstacle type that can't be moved or shot through
class wall(obstacle):
    def __init__(self, x, y, width, height):
        obstacle.__init__(self, x, y, width, height)
        self.colour = (255, 255, 255)
        self.type = "wall"

    def collideCheck(self, ent):
        if float(ent.getX() + ent.xSize) > self.x and float(ent.getX()) < self.x + self.width and float(ent.getY() + ent.ySize) > self.y and float(ent.getY()) < self.y + self.height:
            self.solid(ent)


#wall variant which can be broken by shooting a number of times
class breakableWall(wall):
    def __init__(self, x, y, width, height):
        wall.__init__(self, x, y, width, height)
        self.health = 5000
        self.colour = (150,150,150)
        self.type = "breakableWall"

    def collideCheck(self, ent):
        if self.health > 0:
            if float(ent.getX() + ent.xSize) > self.x and float(ent.getX()) < self.x + self.width and float(ent.getY() + ent.ySize) > self.y and float(ent.getY()) < self.y + self.height:
                self.solid(ent)

    def setHealth(self, value):
        self.health = value


#obstacle which causes damage to the player character whilst they are in contact with it. can be solid like a wall or can be moved and shot through
class hazard(obstacle):
    def __init__(self, x, y, width, height, isSolid):
        obstacle.__init__(self, x, y, width, height)
        self.isSolid = isSolid
        self.type = "hazard"
        if self.isSolid == True:
            self.colour = (240,20,20)
            self.damage = 25
        else:
            self.colour = (200,65,30)
            self.damage = 15

    def collideCheck(self, ent):
        if float(ent.getX() + ent.xSize) > self.x and float(ent.getX()) < self.x + self.width and float(ent.getY() + ent.ySize) > self.y and float(ent.getY()) < self.y + self.height:
            if self.isSolid == True:
                self.solid(ent)
            if ent == player:
                player.setHealth(player.getHealth() - self.damage)


#position from which enemies are created
class enemyStart:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    #define attributes of each enemy type and how likely each is to be created
    def newEnemy(self):
        enemyType = randint(0,9)

        if enemyType == 0:
            world.addEnemy(blockingEnemy(800, self.x, self.y, 0.75, 20, 100, 2000))

        else:
            world.addEnemy(enemy(200, self.x, self.y, 1, 30, 50))



#for testing if something, specifically buttons, correctly calls a procedure
def testClick():
    print("Hello World")

#procedure for drawing a title on the current screen
def drawTitle(text):
    textFont = pygame.font.SysFont("Arial", int(heightScale * 25)) 
    text = textFont.render(text, True, (255,255,255))
    window.blit(text, (widthScale * 350, 0))
    
#main menu screen, defines text and buttons on the screen when this screen is active
def mainMenu():
    global screenWidth
    global screenHeight
    global currentMenu
    window.fill((0,0,0))

    '''
    testButton = button(window, "Test", "Arial", 20, (0,0,0), (0,255,255), 40, 20, 0, 0, testClick)
    testButton.click([])
    '''
    
    currentMenu = "main"
    
    drawTitle("Main Menu")

    playButton = button(window, "Play", "Arial", 11, (0,0,0), (0, 255, 0), 100, 40, 800 / 2 - 50, 450 / 5, playMenu)
    settingsButton = button(window, "Settings", "Arial", 11, (0,0,0), (0, 255, 0), 100, 40, 800 / 2 - 50, 2 * 450 / 5, settingsMenu)
    statsButton = button(window, "Statistics", "Arial", 11, (0,0,0), (0, 255, 0), 100, 40, 800 / 2 - 50, 3 * 450 / 5, statsMenu)
    upgradesButton = button(window, "Upgrades", "Arial", 11, (0,0,0), (0, 255, 0), 100, 40, 800 / 2 - 50, 4 * 450 / 5, upgradesMenu)
    playButton.click([])
    settingsButton.click([])
    statsButton.click([])
    upgradesButton.click([])

#play menu screen, defines text and buttons on the screen when this screen is active
def playMenu():
    global screenWidth
    global screenHeight
    global currentMenu
    global levelNumber
    global existingLevels
    window.fill((0,0,0))
    currentMenu = "play"
    drawTitle("Play")

    back = button(window, "Back", "Arial", 11, (0,0,0), (0, 255, 0), 100, 40, 800 / 2 - 50, 450 - 50, mainMenu)
    levelButtons = []
    for i in range(0, existingLevels):
        levelButtons.append(button(window, "Level " + str(i + 1), "Arial", 11, (0,0,0), (0,255,0), 100, 40, 10 + (i)*110, 450 / 4 - 50, changeLevel))
        levelButtons[i].click([i + 1])
    back.click([])

#change to selected level when level button is pressed. defines layout of the obstacles, player and enemyStarts, defines player attributes and player attack attributes, sets score to 0, then calls the game procedure
def changeLevel(number):
    global levelNumber
    global world
    global player
    global score

    levelNumber = number

    if levelNumber == 1:
        world = level("Level 1", [800/2, 450/2], [wall(800/10, 450/10, 170, 20), wall(9*800/10 - 170, 450/10, 170, 20), wall(800/10, 9 * 450/10 - 20, 170, 20), wall(9*800/10 - 170, 9 * 450/10 - 20, 170, 20), breakableWall(800/10 + 150, 450/2 - 70, 20, 140), breakableWall(9 * 800/10 - 170, 450/2 - 70, 20, 140), breakableWall(800/2 - 60, 450/10, 120, 20), breakableWall(800/2 - 60, 9 * 450/10 - 20, 120, 20), hazard(800/10, 450/2 - 70, 45, 140, False), hazard(9 *800/10 - 45, 450/2 - 70, 45, 140, False)], [enemyStart(0, 0), enemyStart(800, 450)])

    elif levelNumber == 2:
        world = level("Level 2", [0, 450/2], [wall(0, 450/2 - 50, 115, 15), wall(0, 450/2 + 50, 115, 15), breakableWall(100, 450/2 - 35, 15, 85), hazard(800/3, 0, 15, 450 - 450/3, True), hazard(800 - 800/3, 450/3, 15, 450 - 450/3, True)], [enemyStart(800, 450/2), enemyStart(9*800/10, 450)])
    
    elif levelNumber == 3:
        world = level("Level 3", [800/2, 450 - 17], [wall(800/2 - 85, 450/2 - 50, 170, 100)],[])

    player = playerChr(float(openUpgrades()[1]), world.playerStartCoords[0], world.playerStartCoords[1], 100, float(openUpgrades()[2]), 1.7, float(openUpgrades()[4]))

    score = 0
    
    pygame.mouse.set_cursor(*pygame.cursors.broken_x)

    
    

    game()

#settings menu screen, defines text and buttons on the screen when this screen is active
def settingsMenu():
    global screenWidth
    global screenHeight
    global currentMenu
    window.fill((0,0,0))
    currentMenu = "settings"
    drawTitle("Settings")

    settings = openSettings()

    resSelect = button(window, "Resolution: " + str(screenWidth) + "x" + str(screenHeight), "Arial", 11, (0,0,0), (0,255,0), 200, 40, 300, 45, changeRes)
    back = button(window, "Back", "Arial", 11, (0,0,0), (0,255,0), 100, 40, 350, 400, mainMenu)
    up = button(window, "Up: " + str(pygame.key.name(int(settings[2]))), "Arial", 11, (0,0,0), (0,255,0), 100, 40, 10, 105, changeKey)
    down = button(window, "Down: " + str(pygame.key.name(int(settings[3]))), "Arial", 11, (0,0,0), (0,255,0), 100, 40, 120, 105, changeKey)
    left = button(window, "Left: " + str(pygame.key.name(int(settings[4]))), "Arial", 11, (0,0,0), (0,255,0), 100, 40, 230, 105, changeKey)
    right = button(window, "Right: " + str(pygame.key.name(int(settings[5]))), "Arial", 11, (0,0,0), (0,255,0), 100, 40, 340, 105, changeKey)
    sprint = button(window, "Sprint: " + str(pygame.key.name(int(settings[6]))), "Arial", 11, (0,0,0), (0,255,0), 100, 40, 450, 105, changeKey)
    toMain = button(window, "Exit to menu: " + str(pygame.key.name(int(settings[7]))), "Arial", 11, (0,0,0), (0,255,0), 100, 40, 560, 105, changeKey)
    toggleFullscreen = button(window, "Fullscreen: " + str(pygame.key.name(int(settings[8]))), "Arial", 11, (0,0,0), (0,255,0), 100, 40, 560, 105, changeKey)
    resSelect.click([])
    back.click([])
    up.click(["up"])
    down.click(["down"])
    left.click(["left"])
    right.click(["right"])
    sprint.click(["sprint"])
    toMain.click(["toMain"])
    toggleFullscreen.click(["toggleFullscreen"])

#changes screen size, cycles between several pre set values
def changeRes():
    global screenWidth
    global screenHeight
    global widthScale
    global heightScale
    global window
    widths = [400, 800, 1200, 1600, 1920, 2560]
    for i in range(0, len(widths)):
        if screenWidth == widths[i]:
            temp = i
    if screenWidth == widths[-1]:
        screenWidth = widths[0]
    else:
        screenWidth = widths[temp + 1]
    screenHeight = int(screenWidth * 9 / 16)

    if openSettings()[9] == "True":
        window = pygame.display.set_mode((screenWidth,screenHeight), pygame.FULLSCREEN)
    else:
        window = pygame.display.set_mode((screenWidth,screenHeight))

    current = openSettings()
    current[0] = str(screenWidth)
    current[1] = str(screenHeight)

    settings = open("settings.txt","w")
    settings.write("")
    settings.close()

    settings = open("settings.txt", "a")
    settings.write(str(screenWidth) + "\n" + str(screenHeight))
    for i in range(2, len(current)):
        settings.write("\n" + str(current[i]))
    settings.close()
    widthScale = screenWidth / 800
    heightScale = screenHeight / 450

#change input key of desired action
def changeKey(action):
    global actionChange
    actionChange = action
    inputUpdate()

def inputUpdate():
    global screenWidth
    global screenHeight
    global actionChange
    global currentMenu
    currentMenu = "inputUpdate"

    window.fill((0,0,0))
    drawTitle("Press a key")

    noKeysPressed = True
    if noKeysPressed == True:
        settings = openSettings()
        lines = {"up":2, "down":3, "left":4,"right":5,"sprint":6,"toMain":7,"toggleFullscreen":8}
        for i in range(0, len(pressed)):
            if pressed[i] == 1:
                settings[lines[actionChange]] = i
                noKeysPressed = False
                file = open("settings.txt","w")
                file.write("")
                file.close()
                file = open("settings.txt","a")
                for k in range(0,len(settings)):
                    if k > 0:
                        file.write("\n" + str(settings[k]))
                    else:
                        file.write(settings[k])
                file.close()
    if noKeysPressed == False:
        settingsMenu()

def toggleFullscreenSetting():
    settings = openSettings()
    if settings[9] == "True":
        settings[9] = "False"
    else:
        settings[9] = "True"
    file = open("settings.txt","w")
    file.write("")
    file.close()
    file = open("settings.txt","a")
    for k in range(0,len(settings)):
        if k > 0:
            file.write("\n" + str(settings[k]))
        else:
            file.write(settings[k])
    file.close()

#statistics menu screen, defines text and buttons on the screen when this screen is active
def statsMenu():
    global screenWidth
    global screenHeight
    global currentMenu
    global existingLevels
    window.fill((0,0,0))
    currentMenu = "stats"
    drawTitle("Statistics")

    textFont = pygame.font.SysFont("Arial", int(heightScale * 15))
    for i in range(0, existingLevels):
        text = textFont.render("Level " + str(i + 1) + ": " + openStats()[i], True, (255,255,255))
        window.blit(text, (widthScale * (10 + (i)*110), heightScale * (450 / 4 - 50)))
    enemiesDefeatedText = textFont.render("Enemies Defeated: " + openStats()[existingLevels], True, (255,255,255))
    window.blit(enemiesDefeatedText, (widthScale * 10, heightScale * (450 / 4)))

    back = button(window, "Back", "Arial", 11, (0,0,0), (0,255,0), 100, 40, 800 / 2 + 10, 450 - 50, mainMenu)
    reset = button(window, "Reset", "Arial", 11, (0,0,0), (0,255,0), 100, 40, 800 / 2 - 110, 450 - 50, resetStats)
    back.click([])
    reset.click([])

#resets all statistics values to 0
def resetStats():
    number = len(openStats())
    highScores = open("statistics.txt","w")
    highScores.write("")
    highScores.close()
    highScores = open("statistics.txt","a")
    for i in range(0, number):
        if i > 0:
            highScores.write("\n0")
        else:
            highScores.write("0")
    highScores.close()


def upgradesMenu():
    global screenWidth
    global screenHeight
    global currentMenu
    global existingLevels
    window.fill((0,0,0))
    currentMenu = "upgrades"
    drawTitle("Upgrades")

    upgrades = openUpgrades()
    points = upgrades[0]

    textFont = pygame.font.SysFont("Arial", int(heightScale * 20))
    pointsText = textFont.render("Points: "+ points, True, (255,255,255))
    costText1 = textFont.render("Cost: 10", True, (255,255,255))
    costText2 = textFont.render("Cost: 20", True, (255,255,255))
    window.blit(pointsText, (widthScale * (800 - 100), 0))
    window.blit(costText1, (widthScale * 10, heightScale * (450 / 5 + 6)))
    window.blit(costText2, (widthScale * 10, heightScale * (2 * 450 / 5 + 6)))


    back = button(window, "Back", "Arial", 11, (0,0,0), (0,255,0), 100, 40, 800 / 2 + 10, 450 - 50, mainMenu)
    reset = button(window, "Reset", "Arial", 11, (0,0,0), (0,255,0), 100, 40, 800 / 2 - 110, 450 - 50, resetUpgrades)
    health = button(window, "Health: " + str(upgrades[1][:-2]), "Arial", 11, (0,0,0), (0,255,0), 100, 40, 110, 450 / 5, upgradeStat)
    shieldHealth = button(window, "Shield: " + str(upgrades[2][:-2]), "Arial", 11, (0,0,0), (0,255,0), 100, 40, 220, 450 / 5, upgradeStat)
    shieldCooldown = button(window, "Shield CD: " + str(upgrades[3][:-2]), "Arial", 11, (0,0,0), (0,255,0), 100, 40, 330, 450 / 5, upgradeStat)
    atkDmg = button(window, "Attack Damage: " + str(upgrades[4][:-2]), "Arial", 11, (0,0,0), (0,255,0), 100, 40, 110, 2 * 450 / 5, upgradeStat)
    atkSpd = button(window, "Attack Speed: " + str(upgrades[5]), "Arial", 11, (0,0,0), (0,255,0), 100, 40, 220, 2 * 450 / 5, upgradeStat)
    atkRate = button(window, "Attack Rate: " + str(upgrades[6]), "Arial", 11, (0,0,0), (0,255,0), 100, 40, 330, 2 * 450 / 5, upgradeStat)
    back.click([])
    reset.click([])
    health.click(["health"])
    shieldHealth.click(["shieldHealth"])
    shieldCooldown.click(["shieldCooldown"])
    atkDmg.click(["atkDmg"])
    atkSpd.click(["atkSpd"])
    atkRate.click(["atkRate"])

def upgradeStat(stat):
    global attackCooldownValue
    statsList = {"health":1,"shieldHealth":2,"shieldCooldown":3,"atkDmg":4,"atkSpd":5,"atkRate":6}
    upgradeCost = {"health":10,"shieldHealth":10,"shieldCooldown":10,"atkDmg":20,"atkSpd":20,"atkRate":20}
    upgradeValue = {"health":1,"shieldHealth":5,"shieldCooldown":1,"atkDmg":1,"atkSpd":0.125,"atkRate":0.125}
    current = openUpgrades()
    if (stat == "atkSpd" and float(current[statsList[stat]]) >= 20.0) == False:
        if int(current[0]) >= upgradeCost[stat]:
            toUpgrade = float(current[statsList[stat]])
            toUpgrade += upgradeValue[stat]
            current[statsList[stat]] = str(toUpgrade)
            points = int(current[0])
            points -= upgradeCost[stat]
            current[0] = str(points)
        try:
            upgrades = open("upgrades.txt","w")
            upgrades.write("")
            upgrades.close()
        
            upgrades = open("upgrades.txt","a")
            for j in range(0,len(current)):
                if j > 0:
                    upgrades.write("\n" + str(current[j]))
                else:
                    upgrades.write(str(current[j]))
            upgrades.close() 
        except:
            print("upgrades write error")
        attackCooldownValue = 400 / float(openUpgrades()[6])

def resetUpgrades():
    global attackCooldownValue
    upgrades = open("upgrades.txt","w")
    upgrades.write("0\n100.0\n500.0\n50.0\n190.0\n2.0\n3.0")
    upgrades.close()
    attackCooldownValue = 400 / float(openUpgrades()[6])

#opens the statistics text file and returns a list containing the contents of each line
def openStats():
    stats = open("statistics.txt", "r")
    lines = stats.readlines()
    for i in range(0, len(lines) - 1):
        lines[i] = lines[i][:-1]
    stats.close()
    return lines

#opens the settings text file and returns a list containing the contents of each line
def openSettings():
    try:
        settings = open("settings.txt", "r")
        lines = settings.readlines()
        for i in range(0, len(lines) - 1):
            lines[i] = lines[i][:-1]
        settings.close()
        return lines
    except:
        print("settings read error")
    
def openUpgrades():
    try:
        upgrades = open("upgrades.txt", "r")
        lines = upgrades.readlines()
        for i in range(0, len(lines) - 1):
            lines[i] = lines[i][:-1]
        upgrades.close()
        return lines
    except:
        print("upgrades read error")

#displays the game over screen, displays button to return to main menu
def gameOver():
    global screenWidth
    global screenHeight
    global currentMenu
    global score
    global levelNumber

    currentMenu = "gameOver"
    pygame.draw.rect(window, (15,15,15), pygame.Rect(0, heightScale * (450/2 - 37), widthScale * 10000, heightScale * 75))
    textFont = pygame.font.SysFont("Arial", int(heightScale * 50)) 
    text = textFont.render("YOU DIED", True, (200,0,0))
    window.blit(text, (widthScale * (800 / 2 - 110), heightScale * (450 / 2 - 30)))
    back = button(window, "Main Menu", "Arial", 11, (0,0,0), (0,255,0), 100, 40, 800 / 2 - 50, 450 - 50, mainMenu)
    back.click([])

#main game procedure
def game():
    global screenWidth
    global screenHeight
    global currentMenu
    global levelNumber
    global world
    global player
    global score
    window.fill((0,0,0))
    currentMenu = "game"
    #drawTitle("Level " + str(levelNumber))

    playerSquare = player.getCurrentSquare()

    #go through all obstacles and perform required actions such as displaying them or running their collide check procedure
    for i in range(0, len(world.obstacles)):
        pygame.draw.rect(window,world.obstacles[i].colour,pygame.Rect(world.obstacles[i].x,world.obstacles[i].y,world.obstacles[i].width,world.obstacles[i].height))
        world.obstacles[i].collideCheck(player)

        for square in world.grid:
            if (world.obstacles[i].type == "breakableWall" and world.obstacles[i].health <= 0):
                if world.obstacles[i].x < square[0] + 50 * widthScale and world.obstacles[i].x + world.obstacles[i].width > square[0] and world.obstacles[i].y < square[1] + 50 * heightScale and world.obstacles[i].y + world.obstacles[i].height> square[1]:
                    square[2] = False
        

        for j in range(0, len(world.playerProjectiles)):
            #check if player attack collides with obstacle
            if world.playerProjectiles[j].x + widthScale * 5 > world.obstacles[i].x and world.playerProjectiles[j].x < world.obstacles[i].x + world.obstacles[i].width and world.playerProjectiles[j].y + heightScale * 5 > world.obstacles[i].y and world.playerProjectiles[j].y < world.obstacles[i].y + world.obstacles[i].height:
                if world.obstacles[i].type == "breakableWall" and world.playerProjectiles[j].active == True:
                    world.obstacles[i].health -= world.playerProjectiles[j].damage
                    if world.obstacles[i].health <= 0:
                        world.obstacles[i].colour = (0,0,0)
                    else:
                        world.playerProjectiles[j].active = False
                elif world.obstacles[i].type == "hazard":
                    if world.obstacles[i].isSolid == True:
                        world.playerProjectiles[j].active = False
                else:
                    world.playerProjectiles[j].active = False

        #check if enemy attacks collide with obstacle
        for j in range(0, len(world.activeEnemies)):
            world.obstacles[i].collideCheck(world.activeEnemies[j])

        for j in range(0,len(world.enemyProjectiles)):
            if world.enemyProjectiles[j].x + widthScale * 5 > world.obstacles[i].x and world.enemyProjectiles[j].x < world.obstacles[i].x + world.obstacles[i].width and world.enemyProjectiles[j].y + widthScale * 5 > world.obstacles[i].y and world.enemyProjectiles[j].y < world.obstacles[i].y + world.obstacles[i].height:
                if world.obstacles[i].type == "breakableWall":
                    if world.obstacles[i].health > 0:
                        world.enemyProjectiles[j].active = False
                elif world.obstacles[i].type == "hazard":
                    if world.obstacles[i].isSolid == True:
                        world.enemyProjectiles[j].active = False
                else:
                    world.enemyProjectiles[j].active = False

    #create new enemies at each enemy start. has a certain chance to create enemy on each frame, rate should increase slightly as score increases
    calc = 5000 - (score // 10)
    if calc <= 10:
        calc = 10
    for i in range(0,len(world.enemyStarts)):
        spawnChance = randint(0, calc)
        if spawnChance % calc // 10 == 0:
            world.enemyStarts[i].newEnemy()
        if len(world.activeEnemies) == 1:
            world.enemyStarts[i].newEnemy()

    #go through all enemies and perform required actions with them
    for i in range(0, len(world.activeEnemies)):
        if world.activeEnemies[i].type != "none":
            pygame.draw.rect(window, world.activeEnemies[i].colour, pygame.Rect(world.activeEnemies[i].x, world.activeEnemies[i].y, world.activeEnemies[i].xSize, world.activeEnemies[i].ySize))
            for j in range(0, len(world.playerProjectiles)):
                if world.activeEnemies[i].x < world.playerProjectiles[j].x and world.activeEnemies[i].y < world.playerProjectiles[j].y and world.activeEnemies[i].x + world.activeEnemies[i].xSize > world.playerProjectiles[j].x + widthScale * 5 and world.activeEnemies[i].y + world.activeEnemies[i].ySize > world.playerProjectiles[j].y + heightScale * 5 and world.playerProjectiles[j].active == True:
                    world.playerProjectiles[j].active = False
                    if world.activeEnemies[i].type != "blocking":
                        world.activeEnemies[i].setHealth(world.activeEnemies[i].getHealth() - (world.playerProjectiles[j].damage))
                    else:
                        if world.activeEnemies[i].isBlocking == True:
                            world.activeEnemies[i].setShieldHealth(world.activeEnemies[i].getShieldHealth() - (world.playerProjectiles[j].damage))
                        else:
                            world.activeEnemies[i].setHealth(world.activeEnemies[i].getHealth() - (world.playerProjectiles[j].damage))

        #give blocking enemies a random chance to toggle shield on/off if the shield health is greater than 0
        if world.activeEnemies[i].type == "blocking":
            if world.activeEnemies[i].shieldHealth > 0:
                blockChance = randint(0,500)
                if blockChance == 0:
                    world.activeEnemies[i].setBlocking(not world.activeEnemies[i].getBlocking())
                if world.activeEnemies[i].getBlocking() == True:
                    block(world.activeEnemies[i])
            else:
                world.activeEnemies[i].setBlocking(False)

        #when an enemy is defeated, increase score, remove the enemy, update high score and enemies defeated statistics
        if world.activeEnemies[i].getHealth() <= 0:
            score += world.activeEnemies[i].scoreGiven
            points = int(openUpgrades()[0])
            points += world.activeEnemies[i].scoreGiven
            world.removeEnemy(world.activeEnemies[i])

            try:
                current = openStats()
                stats = open("statistics.txt", "w")
                stats.write("")
                stats.close()
                stats = open("statistics.txt","a")
                for j in range(0, len(current)):
                    if j + 1 == levelNumber:
                        if int(score) > int(current[j]):
                            current[j] = score

                    elif j == existingLevels:
                        enemiesKilled = int(current[j])
                        enemiesKilled += 1
                        current[j] = str(enemiesKilled)
                
                    if j > 0:
                        stats.write("\n" + str(current[j]))
                    else:
                        stats.write(str(current[j]))
                stats.close()
            except:
                print("stats write error")

            try:
                current = openUpgrades()
                upgrades = open("upgrades.txt", "w")
                upgrades.write("")
                upgrades.close()
                upgrades = open("upgrades.txt","a")
                for j in range(0,len(current)):
                    if j == 0:
                        current[j] = points

                    if j > 0:
                        upgrades.write("\n" + str(current[j]))
                    else:
                        upgrades.write(str(current[j]))
                upgrades.close() 
            except:
                print("upgrades write error")


        #give enemies random chance to change direction to one of 4 different directions
        '''
        choice = randint(0,150)
        if choice == 0:
            world.activeEnemies[i].direction = 1
        elif choice == 50:
            world.activeEnemies[i].direction = 2
        elif choice == 100:
            world.activeEnemies[i].direction = 3
        elif choice == 150:
            world.activeEnemies[i].direction = 4
        
        if world.activeEnemies[i].type != "none":
            if world.activeEnemies[i].direction == 1:
                world.activeEnemies[i].moveUp(heightScale * world.activeEnemies[i].speed)
            elif world.activeEnemies[i].direction == 2:
                world.activeEnemies[i].moveDown(heightScale * world.activeEnemies[i].speed)
            elif world.activeEnemies[i].direction == 3:
                world.activeEnemies[i].moveLeft(widthScale * world.activeEnemies[i].speed)
            elif world.activeEnemies[i].direction == 4:
                world.activeEnemies[i].moveRight(widthScale * world.activeEnemies[i].speed)
        '''


        #make enemies shoot
        if world.activeEnemies[i].type != "none":
            if world.activeEnemies[i].attackCooldown < world.activeEnemies[i].attackCooldownValue:
                world.activeEnemies[i].attackCooldown += 1
            if world.activeEnemies[i].attackCooldown == world.activeEnemies[i].attackCooldownValue:
                #atkChance = randint(0,100)
                world.activeEnemies[i].shoot()
                world.activeEnemies[i].attackCooldown = 0                   

            #prevent enemies from moving off the screen
            gameBoundary(world.activeEnemies[i], 0)
            world.activeEnemies[i].pathFind(world.activeEnemies[i].getCurrentSquare(), player.getCurrentSquare())

    #draw the enemies' attack projectiles and make them move
    for j in range(0, len(world.enemyProjectiles)):
        if world.enemyProjectiles[j].active == True:
            world.enemyProjectiles[j].checkHit()
            pygame.draw.rect(window, (255,0,0), pygame.Rect(world.enemyProjectiles[j].x, world.enemyProjectiles[j].y, widthScale * 5, heightScale * 5))

    #draw the player's attack projectile and make it move
    for i in range(0, len(world.playerProjectiles)):
        if world.playerProjectiles[i].active == True:
            pygame.draw.rect(window, (0,255,0), pygame.Rect(world.playerProjectiles[i].x, world.playerProjectiles[i].y, widthScale * 5, heightScale * 5))
            world.playerProjectiles[i].checkHit()
            
    #draw the player
    pygame.draw.rect(window, (0,200,0), pygame.Rect(player.x, player.y, player.xSize, player.ySize))

    #add labels to the screen to tell the player their health, score, shield health and shield cooldown values
    textFont = pygame.font.SysFont("Arial", int(heightScale * 20))
    if player.health >= 0:
        healthText = textFont.render("Health: " + str(player.health)[:-2], True, (255,255,255))
    else:
        healthText = textFont.render("Health: 0", True, (255,255,255))
    window.blit(healthText, (widthScale * (800 - 100), 0))
    scoreText = textFont.render("Score: " + str(score), True, (255,255,255))
    window.blit(scoreText, (0, 0))
    if player.shieldHealth >= 0:
        shieldText = textFont.render("Shield: " + str(player.shieldHealth)[:-2], True, (255,255,255))
    else:
        shieldText = textFont.render("Shield: 0", True, (255,255,255))
    window.blit(shieldText, (widthScale * (800 - 100), heightScale * 25))
    if player.blockTimer >= 0:
        timerText = textFont.render("Shield Cooldown: " + str(int(player.blockTimer // 1)), True, (255,255,255))
    else:
        timerText = textFont.render("Shield Cooldown: 0", True, (255,255,255))
    window.blit(timerText, (0, heightScale * 25))

    #draw shield around player if they block
    if player.isBlocking == True:
        block(player)

    #inform the player that they have failed if their health falls to 0
    if player.health <= 0:
        currentMenu = "gameOver"

    #prevent the player from moving off the screen
    gameBoundary(player,0)

    drawGrid = True

    endSquare = None

    for square in world.grid:
        if drawGrid == True:
            if square[3] == True:
                pygame.draw.rect(window, (0,255,0), pygame.Rect(square[0], square[1], 10, 10))
            elif square[2] == True:
                pygame.draw.rect(window, (255,0,0), pygame.Rect(square[0], square[1], 3, 3))
            else:
                pygame.draw.rect(window, (255,255,255), pygame.Rect(square[0], square[1], 3, 3))
            if square == endSquare:
                pygame.draw.rect(window, (255,0,255), pygame.Rect(square[0], square[1], 5, 5))
        if square == playerSquare:
            square[3] = True
        else:
            square[3] = False

    


#prevent an entity from moving a certain number of pixels away from the screen edge
def gameBoundary(ent, size):
    if ent.getX() < size:
        ent.setX(size)
    if ent.getX() + ent.xSize > screenWidth - size:
        ent.setX(screenWidth - size - ent.xSize)
    if ent.getY() < size:
        ent.setY(size)
    if ent.getY() + ent.ySize > screenHeight - size:
        ent.setY(screenHeight - size - ent.ySize)

#draw a shield around the specified entity
def block(ent):
    pygame.draw.rect(window, (0,255,255), pygame.Rect(ent.x - 2, ent.y - 2, ent.xSize + 4, ent.ySize + 4), 1)

#return the set key code from the specified action, stored in settings file
def getControl(action):
    options = {"up":2, "down":3, "left":4,"right":5,"sprint":6,"toMain":7,"toggleFullscreen":8}
    settings = open("settings.txt","r")
    control = openSettings()[options[action]]
    if control.isdigit() == False or int(control) > 323 or int(control) < 0:
        control = 0
    return int(control)


#call the main procedure to start the program
main()

#match strings to menu procedures so each one is called depending on the string contained in currentMenu
menus = {"main": mainMenu, "play": playMenu, "settings": settingsMenu, "stats": statsMenu, "game": game, "gameOver": gameOver, "inputUpdate": inputUpdate, "upgrades":upgradesMenu}

attackCooldownValue = 400 / float(openUpgrades()[6])
attackCooldown = 0

#main while loop for running the game, repeats each frame
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == int(openSettings()[8]):
                fullscreen = not fullscreen
                print(fullscreen)
                if fullscreen == True:
                    window = pygame.display.set_mode((screenWidth,screenHeight), pygame.FULLSCREEN)
                else:
                    window = pygame.display.set_mode((screenWidth,screenHeight))
                toggleFullscreenSetting()

    pressed = pygame.key.get_pressed()

    #define what happens with each player input and which key controls it, keys read from settings file
    if currentMenu == "game":
        if pressed[getControl("sprint")] and player.isBlocking == False:
            player.setSprinting(True)
            x = player.sprintMult
        else:
            player.setSprinting(False)
            x = 1
        if pressed[getControl("up")]:
            player.moveUp(heightScale * 1.75 * x)
        if pressed[getControl("left")]:
            player.moveLeft(widthScale * 1.75 * x)
        if pressed[getControl("down")]:
            player.moveDown(heightScale * 1.75 * x)
        if pressed[getControl("right")]:
            player.moveRight(widthScale * 1.75 * x)
        if pressed[getControl("toMain")]:
            playMenu()

        #allow player to shoot, has cooldown so attack is not constant beam of projectiles
        if pygame.mouse.get_pressed()[0] == 1:
            if attackCooldown == attackCooldownValue:
                player.shoot()
            attackCooldown -= 1
        elif pygame.mouse.get_pressed()[0] == 0:
            if attackCooldown < attackCooldownValue:
                attackCooldown -= 1
        if attackCooldown <= 0:
            attackCooldown = attackCooldownValue

        
        
        #decrease block timer by 1 each frame if player is blocking
        if player.blockTimer > 0 and pygame.mouse.get_pressed()[2] == 1 and player.getShieldHealth() > 0:
            player.setBlocking(True)
            player.blockTimer -= 1

        #increase block timer by 0.25 each frame if player is not blocking
        else:
            player.setBlocking(False)
            if player.blockTimer < player.blockTimerMax:
                if pygame.mouse.get_pressed()[2] == 0 or player.getShieldHealth() <= 0:
                    player.blockTimer += 0.25

    else:
        pygame.mouse.set_cursor(*pygame.cursors.arrow)
    
                    
    #run the menu procedure correspoding to the string in currentMenu
    menus[currentMenu]()

       
    pygame.display.flip()
    pygame.time.Clock().tick(144) #define frame rate at which game runs
