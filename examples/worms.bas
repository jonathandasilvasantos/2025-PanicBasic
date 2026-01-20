' WORMS - A Snake Game
' For PASIC Interpreter
'
' Controls: Arrow keys or WASD to move
' Eat food to grow, avoid walls and yourself!

SCREEN 7
RANDOMIZE TIMER

' Game constants
CONST GRIDW = 20        ' Grid width in cells
CONST GRIDH = 12        ' Grid height in cells
CONST CELLSIZE = 15     ' Pixels per cell
CONST OFFSETX = 10      ' Screen offset X
CONST OFFSETY = 25      ' Screen offset Y
CONST MAXLEN = 100      ' Maximum snake length

' Colors
CONST COLBG = 0         ' Background
CONST COLWALL = 8       ' Wall color
CONST COLSNAKE = 10     ' Snake color
CONST COLHEAD = 2       ' Head color
CONST COLFOOD = 4       ' Food color
CONST COLTEXT = 15      ' Text color
CONST COLTITLE = 14     ' Title color

' Game variables
DIM snakeX(MAXLEN)      ' Snake X positions
DIM snakeY(MAXLEN)      ' Snake Y positions
DIM snakeLen AS INTEGER ' Current snake length
DIM headX AS INTEGER    ' Head X position
DIM headY AS INTEGER    ' Head Y position
DIM dirX AS INTEGER     ' Direction X (-1, 0, 1)
DIM dirY AS INTEGER     ' Direction Y (-1, 0, 1)
DIM foodX AS INTEGER    ' Food X position
DIM foodY AS INTEGER    ' Food Y position
DIM score AS INTEGER    ' Current score
DIM highScore AS INTEGER
DIM gameOver AS INTEGER
DIM speed AS SINGLE     ' Game speed (delay)
DIM lastMove AS SINGLE  ' Last move time

highScore = 0

' ============ TITLE SCREEN ============
TitleScreen:
CLS
COLOR COLTITLE
LOCATE 3, 12
PRINT "W O R M S"
COLOR COLTEXT
LOCATE 6, 8
PRINT "A Classic Snake Game"

' Draw a demo snake
FOR i = 0 TO 7
    LINE (100 + i * 15, 80)-(113 + i * 15, 93), COLSNAKE, BF
NEXT i
LINE (100 + 8 * 15, 80)-(113 + 8 * 15, 93), COLHEAD, BF
' Draw food
CIRCLE (260, 86), 5, COLFOOD
PAINT (260, 86), COLFOOD, COLFOOD

COLOR COLTEXT
LOCATE 11, 6
PRINT "Use Arrow Keys or WASD"
LOCATE 13, 10
PRINT "Eat food to grow"
LOCATE 14, 8
PRINT "Avoid walls and tail"

COLOR COLTITLE
LOCATE 17, 8
PRINT "Press SPACE to Start"

IF highScore > 0 THEN
    COLOR COLTEXT
    LOCATE 19, 9
    PRINT "High Score: "; highScore
END IF

' Play title music
PLAY "T180 O3 L8 C E G > C < G E C"

' Wait for space
WaitStart:
k$ = INKEY$
IF k$ = " " THEN GOTO StartGame
IF k$ = CHR$(27) THEN END
_DELAY 0.05
GOTO WaitStart

' ============ START GAME ============
StartGame:
' Initialize game state
snakeLen = 3
headX = GRIDW / 2
headY = GRIDH / 2
dirX = 1
dirY = 0
score = 0
gameOver = 0
speed = 0.15
lastMove = TIMER

' Initialize snake body
FOR i = 0 TO snakeLen - 1
    snakeX(i) = headX - i
    snakeY(i) = headY
NEXT i

' Spawn first food
GOSUB SpawnFood

' Play start sound
SOUND 440, 2
SOUND 550, 2
SOUND 660, 2

' ============ MAIN GAME LOOP ============
GameLoop:
' Handle input
k$ = INKEY$
IF k$ <> "" THEN
    IF (k$ = CHR$(0) + "H" OR k$ = "w" OR k$ = "W") AND dirY <> 1 THEN
        dirX = 0: dirY = -1
    END IF
    IF (k$ = CHR$(0) + "P" OR k$ = "s" OR k$ = "S") AND dirY <> -1 THEN
        dirX = 0: dirY = 1
    END IF
    IF (k$ = CHR$(0) + "K" OR k$ = "a" OR k$ = "A") AND dirX <> 1 THEN
        dirX = -1: dirY = 0
    END IF
    IF (k$ = CHR$(0) + "M" OR k$ = "d" OR k$ = "D") AND dirX <> -1 THEN
        dirX = 1: dirY = 0
    END IF
    IF k$ = CHR$(27) THEN GOTO TitleScreen
END IF

' Move snake based on speed
IF TIMER - lastMove >= speed THEN
    lastMove = TIMER
    GOSUB MoveSnake
    IF gameOver = 1 THEN GOTO GameOverScreen
    GOSUB DrawGame
END IF

_DELAY 0.016
GOTO GameLoop

' ============ MOVE SNAKE ============
MoveSnake:
' Calculate new head position
newX = headX + dirX
newY = headY + dirY

' Check wall collision
IF newX < 0 OR newX >= GRIDW OR newY < 0 OR newY >= GRIDH THEN
    gameOver = 1
    SOUND 100, 5
    RETURN
END IF

' Check self collision
FOR i = 0 TO snakeLen - 1
    IF snakeX(i) = newX AND snakeY(i) = newY THEN
        gameOver = 1
        SOUND 100, 5
        RETURN
    END IF
NEXT i

' Check food collision
IF newX = foodX AND newY = foodY THEN
    ' Eat food - grow snake
    snakeLen = snakeLen + 1
    IF snakeLen > MAXLEN THEN snakeLen = MAXLEN
    score = score + 10
    ' Speed up slightly
    IF speed > 0.05 THEN speed = speed - 0.005
    ' Play eat sound
    SOUND 880, 1
    SOUND 1100, 1
    GOSUB SpawnFood
END IF

' Move body (shift all positions)
FOR i = snakeLen - 1 TO 1 STEP -1
    snakeX(i) = snakeX(i - 1)
    snakeY(i) = snakeY(i - 1)
NEXT i

' Move head
snakeX(0) = newX
snakeY(0) = newY
headX = newX
headY = newY
RETURN

' ============ SPAWN FOOD ============
SpawnFood:
' Find empty cell for food
tryAgain:
foodX = INT(RND * GRIDW)
foodY = INT(RND * GRIDH)

' Make sure food doesn't spawn on snake
FOR i = 0 TO snakeLen - 1
    IF snakeX(i) = foodX AND snakeY(i) = foodY THEN
        GOTO tryAgain
    END IF
NEXT i
RETURN

' ============ DRAW GAME ============
DrawGame:
CLS

' Draw border
LINE (OFFSETX - 2, OFFSETY - 2)-(OFFSETX + GRIDW * CELLSIZE + 1, OFFSETY + GRIDH * CELLSIZE + 1), COLWALL, B

' Draw score
COLOR COLTEXT
LOCATE 1, 1
PRINT "Score: "; score; "  High: "; highScore

' Draw snake body
FOR i = 1 TO snakeLen - 1
    px = OFFSETX + snakeX(i) * CELLSIZE
    py = OFFSETY + snakeY(i) * CELLSIZE
    LINE (px + 1, py + 1)-(px + CELLSIZE - 2, py + CELLSIZE - 2), COLSNAKE, BF
NEXT i

' Draw snake head
px = OFFSETX + snakeX(0) * CELLSIZE
py = OFFSETY + snakeY(0) * CELLSIZE
LINE (px + 1, py + 1)-(px + CELLSIZE - 2, py + CELLSIZE - 2), COLHEAD, BF

' Draw food
px = OFFSETX + foodX * CELLSIZE + CELLSIZE / 2
py = OFFSETY + foodY * CELLSIZE + CELLSIZE / 2
CIRCLE (px, py), CELLSIZE / 3, COLFOOD
PAINT (px, py), COLFOOD, COLFOOD

RETURN

' ============ GAME OVER ============
GameOverScreen:
' Update high score
IF score > highScore THEN
    highScore = score
    ' Play new high score fanfare
    PLAY "T200 O4 L8 C E G > C < G > E C"
END IF

' Flash effect
FOR flash = 1 TO 3
    COLOR 12
    LOCATE 8, 11
    PRINT "GAME OVER!"
    _DELAY 0.2
    COLOR 0
    LOCATE 8, 11
    PRINT "          "
    _DELAY 0.1
NEXT flash

COLOR 12
LOCATE 8, 11
PRINT "GAME OVER!"

COLOR COLTEXT
LOCATE 10, 9
PRINT "Final Score: "; score

IF score >= highScore AND score > 0 THEN
    COLOR COLTITLE
    LOCATE 12, 9
    PRINT "NEW HIGH SCORE!"
END IF

COLOR COLTEXT
LOCATE 15, 6
PRINT "Press SPACE to continue"

' Wait for input
WaitEnd:
k$ = INKEY$
IF k$ = " " THEN GOTO TitleScreen
IF k$ = CHR$(27) THEN END
_DELAY 0.05
GOTO WaitEnd
