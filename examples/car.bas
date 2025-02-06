' Car Racing Game
SCREEN 13 ' Set 320x200 graphics mode
CLS

' Game Constants
CONST ROAD_WIDTH = 100
CONST CAR_WIDTH = 20
CONST CAR_HEIGHT = 30
CONST OBSTACLE_SIZE = 15
CONST PLAYER_Y = 160 ' Vertical position of player's car

' Game Variables
playerX = 150 ' Starting X position
obstacleX = 160
obstacleY = -OBSTACLE_SIZE
speed = 2
score = 0
gameOver = 0

' Main Game Loop
DO
    CLS ' Clear screen
    
    ' Draw road
    LINE (110, 0)-(210, 200), 8, BF ' Gray road
    LINE (110, 0)-(110, 200), 7 ' White left line
    LINE (210, 0)-(210, 200), 7 ' White right line
    
    ' Draw player car (red)
    LINE (playerX, PLAYER_Y)-(playerX + CAR_WIDTH, PLAYER_Y + CAR_HEIGHT), 4, BF
    LINE (playerX, PLAYER_Y)-(playerX + CAR_WIDTH, PLAYER_Y + CAR_HEIGHT), 0, B
    
    ' Draw obstacle (yellow)
    LINE (obstacleX, obstacleY)-(obstacleX + OBSTACLE_SIZE, obstacleY + OBSTACLE_SIZE), 14, BF
    
    ' Handle input
    k$ = INKEY$
    ' Move left with left arrow or A
    IF k$ = CHR$(0) + "K" OR k$ = "a" THEN
        playerX = playerX - 5
        IF playerX < 110 THEN playerX = 110
    END IF
    ' Move right with right arrow or D
    IF k$ = CHR$(0) + "M" OR k$ = "d" THEN
        playerX = playerX + 5
        IF playerX > 210 - CAR_WIDTH THEN playerX = 210 - CAR_WIDTH
    END IF
    
    ' Update obstacle position
    obstacleY = obstacleY + speed
    IF obstacleY > 200 THEN
        obstacleY = -OBSTACLE_SIZE
        obstacleX = 110 + INT(RND * (ROAD_WIDTH - OBSTACLE_SIZE))
        speed = speed + 0.2
        score = score + 1
    END IF
    
    ' Collision detection
    IF obstacleY + OBSTACLE_SIZE >= PLAYER_Y THEN
        IF (playerX < obstacleX + OBSTACLE_SIZE) AND (playerX + CAR_WIDTH > obstacleX) THEN
            gameOver = 1
        END IF
    END IF
    
    ' Display score
    LOCATE 1, 10
    PRINT "Score: "; score
    
    ' Game over check
    IF gameOver THEN
        LOCATE 10, 10
        PRINT "GAME OVER!"
        LOCATE 12, 10
        PRINT "Final Score: "; score
        LOCATE 14, 10
        PRINT "Press Q to quit"
        IF k$ = "q" THEN EXIT DO
    ELSE
        ' Game speed control
        _DELAY 0.05
    END IF
LOOP

CLS
PRINT "Thanks for playing!"
END
