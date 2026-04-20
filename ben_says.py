# Simulate (a Simon clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random, sys, time, pygame, os
from pygame.locals import *

FPS = 30
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
FLASHSPEED = 500 # in milliseconds
FLASHDELAY = 200 # in milliseconds
BUTTONSIZE = 200
BUTTONGAPSIZE = 20
TIMEOUT = 4 # seconds before game over if no button is pushed.

#                R    G    B
WHITE        = (255, 255, 255)
BLACK        = (  0,   0,   0)
BRIGHTTEAL   = (0,   222,   170)
TEAL         = (0,   166,   127)
BRIGHTGREEN  = (  8, 207,   18)
GREEN        = (  4, 138,   11)
BRIGHTBLUE   = (  2,   115, 207)
BLUE         = (  2,   92, 166)
BRIGHTPURPLE = (120, 0,   207)
PURPLE       = (85, 0,   145)
DARKGRAY     = ( 40,  40,  40)
bgColor = BLACK

XMARGIN = int((WINDOWWIDTH - (2 * BUTTONSIZE) - BUTTONGAPSIZE) / 2)
YMARGIN = int((WINDOWHEIGHT - (2 * BUTTONSIZE) - BUTTONGAPSIZE) / 2)

# Rect objects for each of the four buttons
STARTBUTTONRECT = pygame.Rect(WINDOWWIDTH // 2 - 50, WINDOWHEIGHT // 2, 100, 50)
PURPLERECT = pygame.Rect(XMARGIN, YMARGIN, BUTTONSIZE, BUTTONSIZE)
BLUERECT   = pygame.Rect(XMARGIN + BUTTONSIZE + BUTTONGAPSIZE, YMARGIN, BUTTONSIZE, BUTTONSIZE)
TEALRECT    = pygame.Rect(XMARGIN, YMARGIN + BUTTONSIZE + BUTTONGAPSIZE, BUTTONSIZE, BUTTONSIZE)
GREENRECT  = pygame.Rect(XMARGIN + BUTTONSIZE + BUTTONGAPSIZE, YMARGIN + BUTTONSIZE + BUTTONGAPSIZE, BUTTONSIZE, BUTTONSIZE)

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, BEEP1, BEEP2, BEEP3, BEEP4, GAMEOVERBEEP
    
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Ben Says')

    showStartScreen()

    BASICFONT = pygame.font.Font('freesansbold.ttf', 16)
    infoSurf = BASICFONT.render('Match the pattern by clicking on the button or using the Q, W, A, S keys.', 1, DARKGRAY)
    infoRect = infoSurf.get_rect()
    infoRect.topleft = (10, WINDOWHEIGHT - 25)

    # load the sound files
    BEEP1 = pygame.mixer.Sound('ben.mp3')                                               ##CHANGED SOUNDS
    BEEP2 = pygame.mixer.Sound('phone.mp3')                                             ##CHANGED SOUNDS
    BEEP3 = pygame.mixer.Sound('yes.mp3')                                               ##CHANGED SOUNDS
    BEEP4 = pygame.mixer.Sound('ugh.mp3')                                               ##CHANGED SOUNDS
    GAMEOVERBEEP = pygame.mixer.Sound('laugh.mp3') 

    # Initialize some variables for a new game
    pattern = [] # stores the pattern of colors
    currentStep = 0 # the color the player must push next
    lastClickTime = 0 # timestamp of the player's last button push
    score = 0
    highScore = load_high_score()                              ##ADD HIGHSCORE COUNTER
    # when False, the pattern is playing. when True, waiting for the player to click a colored button:
    waitingForInput = False

    while True: # main game loop
        clickedButton = None # button that was clicked (set to PURPLE, TEAL, GREEN, or BLUE)
        DISPLAYSURF.fill(bgColor)
        drawButtons()

        scoreSurf = BASICFONT.render('Score: ' + str(score), 1, WHITE)
        scoreRect = scoreSurf.get_rect()
        scoreRect.topleft = (WINDOWWIDTH - 100, 10)
        DISPLAYSURF.blit(scoreSurf, scoreRect)
        highScoreSurf = BASICFONT.render('High Score: ' + str(highScore), 1, WHITE)
        highScoreRect = highScoreSurf.get_rect()
        highScoreRect.topleft = (20, 10) # 20px from left, 10px from top
        DISPLAYSURF.blit(highScoreSurf, highScoreRect)

        DISPLAYSURF.blit(infoSurf, infoRect)

        checkForQuit()
        for event in pygame.event.get(): # event handling loop
            if event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                clickedButton = getButtonClicked(mousex, mousey)
            elif event.type == KEYDOWN:
                if event.key == K_q:
                    clickedButton = PURPLE
                elif event.key == K_w:
                    clickedButton = BLUE
                elif event.key == K_a:
                    clickedButton = TEAL
                elif event.key == K_s:
                    clickedButton = GREEN



        if not waitingForInput:
            # play the pattern
            pygame.display.update()
            pygame.time.wait(1000)
            pattern.append(random.choice((PURPLE, BLUE, TEAL, GREEN)))
            for button in pattern:
                flashButtonAnimation(button)
                pygame.time.wait(FLASHDELAY)
            waitingForInput = True
        else:
            # wait for the player to enter buttons
            if clickedButton and clickedButton == pattern[currentStep]:
                # pushed the correct button
                flashButtonAnimation(clickedButton)
                currentStep += 1
                lastClickTime = time.time()

                if currentStep == len(pattern):
                    # pushed the last button in the pattern
                    changeBackgroundAnimation()
                    score += 1
                    waitingForInput = False
                    currentStep = 0 # reset back to first step

            elif (clickedButton and clickedButton != pattern[currentStep]) or (currentStep != 0 and time.time() - TIMEOUT > lastClickTime):
                # pushed the incorrect button, or has timed out
                if score > highScore:
                    highScore = score
                    save_high_score(highScore)

                gameOverAnimation()
                # reset the variables for a new game:
                pattern = []
                currentStep = 0
                waitingForInput = False
                score = 0
                pygame.time.wait(1000)
                changeBackgroundAnimation()

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def terminate():
    pygame.quit()
    sys.exit()


def checkForQuit():
    for event in pygame.event.get(QUIT): # get all the QUIT events
        terminate() # terminate if any QUIT events are present
    for event in pygame.event.get(KEYUP): # get all the KEYUP events
        if event.key == K_ESCAPE:
            terminate() # terminate if the KEYUP event was for the Esc key
        pygame.event.post(event) # put the other KEYUP event objects back


def flashButtonAnimation(color, animationSpeed=50):
    if color == PURPLE:
        sound = BEEP1
        flashColor = BRIGHTPURPLE
        rectangle = PURPLERECT
    elif color == BLUE:
        sound = BEEP2
        flashColor = BRIGHTBLUE
        rectangle = BLUERECT
    elif color == TEAL:
        sound = BEEP3
        flashColor = BRIGHTTEAL
        rectangle = TEALRECT
    elif color == GREEN:
        sound = BEEP4
        flashColor = BRIGHTGREEN
        rectangle = GREENRECT

    origSurf = DISPLAYSURF.copy()
    flashSurf = pygame.Surface((BUTTONSIZE, BUTTONSIZE))
    flashSurf = flashSurf.convert_alpha()
    r, g, b = flashColor
    sound.play()
    for start, end, step in ((0, 255, 1), (255, 0, -1)): # animation loop
        for alpha in range(start, end, animationSpeed * step):
            checkForQuit()
            DISPLAYSURF.blit(origSurf, (0, 0))
            flashSurf.fill((r, g, b, alpha))
            DISPLAYSURF.blit(flashSurf, rectangle.topleft)
            pygame.display.update()
            FPSCLOCK.tick(FPS)
    DISPLAYSURF.blit(origSurf, (0, 0))


def drawButtons():
    pygame.draw.rect(DISPLAYSURF, PURPLE, PURPLERECT)
    pygame.draw.rect(DISPLAYSURF, BLUE,   BLUERECT)
    pygame.draw.rect(DISPLAYSURF, TEAL,    TEALRECT)
    pygame.draw.rect(DISPLAYSURF, GREEN,  GREENRECT)


def changeBackgroundAnimation(animationSpeed=40):
    global bgColor
    newBgColor = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    newBgSurf = pygame.Surface((WINDOWWIDTH, WINDOWHEIGHT))
    newBgSurf = newBgSurf.convert_alpha()
    r, g, b = newBgColor
    for alpha in range(0, 255, animationSpeed): # animation loop
        checkForQuit()
        DISPLAYSURF.fill(bgColor)

        newBgSurf.fill((r, g, b, alpha))
        DISPLAYSURF.blit(newBgSurf, (0, 0))

        drawButtons() # redraw the buttons on top of the tint

        pygame.display.update()
        FPSCLOCK.tick(FPS)
    bgColor = newBgColor


def gameOverAnimation(color=WHITE, animationSpeed=50):
    global GAMEOVERBEEP
    # play all beeps at once, then flash the background
    origSurf = DISPLAYSURF.copy()
    flashSurf = pygame.Surface(DISPLAYSURF.get_size())
    flashSurf = flashSurf.convert_alpha()
    ##Plays first sound
    GAMEOVERBEEP.play()
    ##waits and plays second sound
    pygame.time.wait(2000)
    GAMEOVERBEEP.play()
    r, g, b = color
    for i in range(3): # do the flash 3 times
        for start, end, step in ((0, 255, 1), (255, 0, -1)):
            # The first iteration in this loop sets the following for loop
            # to go from 0 to 255, the second from 255 to 0.
            for alpha in range(start, end, animationSpeed * step): # animation loop
                # alpha means transparency. 255 is opaque, 0 is invisible
                checkForQuit()
                flashSurf.fill((r, g, b, alpha))
                DISPLAYSURF.blit(origSurf, (0, 0))
                DISPLAYSURF.blit(flashSurf, (0, 0))
                drawButtons()
                pygame.display.update()
                FPSCLOCK.tick(FPS)



def getButtonClicked(x, y):
    if PURPLERECT.collidepoint( (x, y) ):
        return PURPLE
    elif BLUERECT.collidepoint( (x, y) ):
        return BLUE
    elif TEALRECT.collidepoint( (x, y) ):
        return TEAL
    elif GREENRECT.collidepoint( (x, y) ):
        return GREEN
    return None


def load_high_score():
    if os.path.exists("highscore.txt"):
            with open("highscore.txt", "r") as f:
                try:
                    return int(f.read().strip())
                except ValueError:
                    return 0
    return 0
 
def save_high_score(score):
    with open("highscore.txt", "w") as f:
        f.write(str(score))

def showStartScreen():
    titleFont = pygame.font.Font('freesansbold.ttf', 100)
    subFont = pygame.font.Font('freesansbold.ttf', 20)
    buttonFont = pygame.font.Font('freesansbold.ttf', 30)
    scoreFont = pygame.font.Font('freesansbold.ttf', 25)    

    highScore=load_high_score()
    while True:
        DISPLAYSURF.fill(TEAL)
        
        # Draw Title
        titleSurf = titleFont.render('Ben Says', True, WHITE)
        titleRect = titleSurf.get_rect()
        titleRect.center = (WINDOWWIDTH // 2, WINDOWHEIGHT // 2 - 100)
        DISPLAYSURF.blit(titleSurf, titleRect)

        # Draw SubTitle
        subSurf1 = subFont.render('A Reimagined', True, PURPLE)
        subRect1 = subSurf1.get_rect()
        subRect1.center = (WINDOWWIDTH // 2, WINDOWHEIGHT // 2 - 50)
        DISPLAYSURF.blit(subSurf1, subRect1)
        # Draw second half
        subSurf2 = subFont.render('Simon Says Game', True, PURPLE)
        subRect2 = subSurf2.get_rect()
        subRect2.center = (WINDOWWIDTH // 2, WINDOWHEIGHT // 2 - 25)
        DISPLAYSURF.blit(subSurf2, subRect2)


        # Draw Start Button
        BUTTON_Y = WINDOWHEIGHT // 2 + 40
        STARTBUTTONRECT.y = BUTTON_Y # Update the rect position
        pygame.draw.rect(DISPLAYSURF, GREEN, STARTBUTTONRECT)
        
        startSurf = buttonFont.render('START', True, WHITE)
        startRect = startSurf.get_rect()
        startRect.center = (WINDOWWIDTH // 2, BUTTON_Y + 25)
        DISPLAYSURF.blit(startSurf, startRect)
        

        #Show highscore at bottom
        highScoreSurf = scoreFont.render(f'Current Record: {highScore}', True, BRIGHTPURPLE)
        highScoreRect = highScoreSurf.get_rect()
        highScoreRect.center = (WINDOWWIDTH // 2, WINDOWHEIGHT - 50) 
        DISPLAYSURF.blit(highScoreSurf, highScoreRect)

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                if STARTBUTTONRECT.collidepoint((mousex, mousey)):
                    return # Exit function to start the game
                    
        pygame.display.update()
        FPSCLOCK.tick(FPS)


if __name__ == '__main__':
    main()