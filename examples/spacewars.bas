' SPACEWARS - A Shoot'em Up Game
' For PASIC Interpreter
'
' Controls: Arrow keys or WASD to move, SPACE to shoot
' Destroy all enemies to advance!

SCREEN 7
RANDOMIZE TIMER

' ============ CONSTANTS ============
CONST SCRW = 320        ' Screen width
CONST SCRH = 200        ' Screen height
CONST MAXBULLETS = 10   ' Max player bullets
CONST MAXENEMIES = 8    ' Max enemies on screen
CONST MAXSTARS = 30     ' Background stars
CONST MAXEXPLOSIONS = 5 ' Max simultaneous explosions

' Colors
CONST COLBG = 0         ' Background (black)
CONST COLSHIP = 11      ' Player ship (cyan)
CONST COLBULLET = 14    ' Bullets (yellow)
CONST COLENEMY = 4      ' Enemies (red)
CONST COLENEMY2 = 12    ' Enemy type 2 (light red)
CONST COLTEXT = 15      ' Text (white)
CONST COLTITLE = 10     ' Title (green)
CONST COLSTAR = 7       ' Stars (gray)
CONST COLEXPLODE = 6    ' Explosion (brown/orange)

' ============ ARRAYS ============
' Player bullets
DIM bulletX(MAXBULLETS)
DIM bulletY(MAXBULLETS)
DIM bulletActive(MAXBULLETS)

' Enemies
DIM enemyX(MAXENEMIES)
DIM enemyY(MAXENEMIES)
DIM enemyActive(MAXENEMIES)
DIM enemyType(MAXENEMIES)
DIM enemyDX(MAXENEMIES)

' Background stars
DIM starX(MAXSTARS)
DIM starY(MAXSTARS)
DIM starSpeed(MAXSTARS)

' Explosions
DIM explodeX(MAXEXPLOSIONS)
DIM explodeY(MAXEXPLOSIONS)
DIM explodeFrame(MAXEXPLOSIONS)

' ============ GAME VARIABLES ============
DIM playerX AS INTEGER
DIM playerY AS INTEGER
DIM score AS INTEGER
DIM highScore AS INTEGER
DIM lives AS INTEGER
DIM level AS INTEGER
DIM gameOver AS INTEGER
DIM enemyCount AS INTEGER
DIM shootDelay AS SINGLE
DIM lastShot AS SINGLE
DIM frameCount AS INTEGER

highScore = 0

' ============ INITIALIZE STARS ============
FOR i = 0 TO MAXSTARS - 1
    starX(i) = INT(RND * SCRW)
    starY(i) = INT(RND * SCRH)
    starSpeed(i) = 1 + INT(RND * 3)
NEXT i

' ============ TITLE SCREEN ============
TitleScreen:
CLS

' Draw starfield
GOSUB DrawStars

' Title
COLOR COLTITLE
LOCATE 3, 10
PRINT "S P A C E W A R S"

COLOR COLTEXT
LOCATE 6, 8
PRINT "Galactic Defender"

' Draw demo ship
GOSUB DrawDemoShip

COLOR COLTEXT
LOCATE 12, 5
PRINT "Arrow Keys / WASD - Move"
LOCATE 13, 9
PRINT "SPACE - Fire"
LOCATE 14, 8
PRINT "ESC - Quit Game"

COLOR COLTITLE
LOCATE 17, 8
PRINT "Press SPACE to Start"

IF highScore > 0 THEN
    COLOR COLTEXT
    LOCATE 19, 9
    PRINT "High Score: "; highScore
END IF

' Title music
PLAY "T150 O4 L8 E G > C < B G E"
PLAY "T150 O3 L4 C E G > C"

' Wait for space
WaitTitle:
k$ = INKEY$
IF k$ = " " THEN GOTO StartGame
IF k$ = CHR$(27) THEN END
GOSUB UpdateStars
GOSUB DrawStars
_DELAY 0.05
GOTO WaitTitle

' ============ DRAW DEMO SHIP ============
DrawDemoShip:
' Draw a ship in the center for title screen
shipDemoX = 145
shipDemoY = 85
' Main body
LINE (shipDemoX, shipDemoY - 15)-(shipDemoX - 12, shipDemoY + 10), COLSHIP
LINE (shipDemoX, shipDemoY - 15)-(shipDemoX + 12, shipDemoY + 10), COLSHIP
LINE (shipDemoX - 12, shipDemoY + 10)-(shipDemoX + 12, shipDemoY + 10), COLSHIP
' Wings
LINE (shipDemoX - 12, shipDemoY + 5)-(shipDemoX - 20, shipDemoY + 12), COLSHIP
LINE (shipDemoX + 12, shipDemoY + 5)-(shipDemoX + 20, shipDemoY + 12), COLSHIP
' Engine
LINE (shipDemoX - 4, shipDemoY + 10)-(shipDemoX + 4, shipDemoY + 15), 4
RETURN

' ============ START GAME ============
StartGame:
' Initialize game state
playerX = SCRW / 2
playerY = SCRH - 30
score = 0
lives = 3
level = 1
gameOver = 0
shootDelay = 0.2
lastShot = 0
frameCount = 0

' Clear bullets
FOR i = 0 TO MAXBULLETS - 1
    bulletActive(i) = 0
NEXT i

' Clear explosions
FOR i = 0 TO MAXEXPLOSIONS - 1
    explodeFrame(i) = 0
NEXT i

' Spawn initial enemies
GOSUB SpawnWave

' Play start sound
SOUND 440, 2
SOUND 660, 2
SOUND 880, 2

' ============ MAIN GAME LOOP ============
GameLoop:
frameCount = frameCount + 1

' Handle input
k$ = INKEY$
IF k$ <> "" THEN
    ' Movement
    IF k$ = CHR$(0) + "K" OR k$ = "a" OR k$ = "A" THEN
        playerX = playerX - 5
        IF playerX < 15 THEN playerX = 15
    END IF
    IF k$ = CHR$(0) + "M" OR k$ = "d" OR k$ = "D" THEN
        playerX = playerX + 5
        IF playerX > SCRW - 15 THEN playerX = SCRW - 15
    END IF
    IF k$ = CHR$(0) + "H" OR k$ = "w" OR k$ = "W" THEN
        playerY = playerY - 4
        IF playerY < 50 THEN playerY = 50
    END IF
    IF k$ = CHR$(0) + "P" OR k$ = "s" OR k$ = "S" THEN
        playerY = playerY + 4
        IF playerY > SCRH - 15 THEN playerY = SCRH - 15
    END IF
    ' Shooting
    IF k$ = " " THEN
        IF TIMER - lastShot >= shootDelay THEN
            GOSUB FireBullet
            lastShot = TIMER
        END IF
    END IF
    IF k$ = CHR$(27) THEN GOTO TitleScreen
END IF

' Update game objects
GOSUB UpdateBullets
GOSUB UpdateEnemies
GOSUB UpdateExplosions
GOSUB CheckCollisions
GOSUB UpdateStars

' Check if wave cleared
IF enemyCount <= 0 THEN
    GOSUB NextLevel
END IF

' Check game over
IF gameOver = 1 THEN GOTO GameOverScreen

' Draw everything
GOSUB DrawGame

_DELAY 0.02
GOTO GameLoop

' ============ FIRE BULLET ============
FireBullet:
bulletFired = 0
FOR i = 0 TO MAXBULLETS - 1
    IF bulletActive(i) = 0 AND bulletFired = 0 THEN
        bulletX(i) = playerX
        bulletY(i) = playerY - 15
        bulletActive(i) = 1
        bulletFired = 1
        ' Shoot sound
        SOUND 1200, 1
    END IF
NEXT i
RETURN

' ============ UPDATE BULLETS ============
UpdateBullets:
FOR i = 0 TO MAXBULLETS - 1
    IF bulletActive(i) = 1 THEN
        bulletY(i) = bulletY(i) - 8
        IF bulletY(i) < 0 THEN
            bulletActive(i) = 0
        END IF
    END IF
NEXT i
RETURN

' ============ UPDATE ENEMIES ============
UpdateEnemies:
FOR i = 0 TO MAXENEMIES - 1
    IF enemyActive(i) = 1 THEN
        ' Move horizontally
        enemyX(i) = enemyX(i) + enemyDX(i)
        ' Bounce off walls
        IF enemyX(i) < 15 OR enemyX(i) > SCRW - 15 THEN
            enemyDX(i) = -enemyDX(i)
        END IF
        ' Move down slowly
        IF frameCount MOD 30 = 0 THEN
            enemyY(i) = enemyY(i) + 5
        END IF
        ' Check if enemy reached bottom
        IF enemyY(i) > SCRH - 30 THEN
            ' Player loses a life
            lives = lives - 1
            GOSUB SpawnExplosion
            enemyActive(i) = 0
            enemyCount = enemyCount - 1
            SOUND 150, 3
            IF lives <= 0 THEN
                gameOver = 1
            END IF
        END IF
    END IF
NEXT i
RETURN

' ============ SPAWN WAVE ============
SpawnWave:
enemyCount = 0
FOR i = 0 TO MAXENEMIES - 1
    IF i < 4 + level THEN
        enemyX(i) = 30 + (i MOD 4) * 70
        enemyY(i) = 20 + (i \ 4) * 30
        enemyActive(i) = 1
        enemyType(i) = (i MOD 2)
        enemyDX(i) = 1 + (RND * 2) - 1
        IF RND > 0.5 THEN enemyDX(i) = -enemyDX(i)
        enemyCount = enemyCount + 1
    ELSE
        enemyActive(i) = 0
    END IF
NEXT i
RETURN

' ============ NEXT LEVEL ============
NextLevel:
level = level + 1
' Level up sound
PLAY "T200 O4 L16 C E G > C"
' Brief pause
COLOR COLTITLE
LOCATE 10, 11
PRINT "LEVEL "; level
_DELAY 1
GOSUB SpawnWave
RETURN

' ============ CHECK COLLISIONS ============
CheckCollisions:
' Check bullet-enemy collisions
FOR b = 0 TO MAXBULLETS - 1
    IF bulletActive(b) = 1 THEN
        FOR e = 0 TO MAXENEMIES - 1
            IF enemyActive(e) = 1 THEN
                ' Simple bounding box collision
                dx = ABS(bulletX(b) - enemyX(e))
                dy = ABS(bulletY(b) - enemyY(e))
                IF dx < 12 AND dy < 10 THEN
                    ' Hit!
                    bulletActive(b) = 0
                    enemyActive(e) = 0
                    enemyCount = enemyCount - 1
                    score = score + 10 * level
                    ' Create explosion at enemy position
                    ex = enemyX(e)
                    ey = enemyY(e)
                    GOSUB CreateExplosion
                    ' Hit sound
                    SOUND 200, 2
                    SOUND 100, 2
                END IF
            END IF
        NEXT e
    END IF
NEXT b

' Check player-enemy collision
FOR e = 0 TO MAXENEMIES - 1
    IF enemyActive(e) = 1 THEN
        dx = ABS(playerX - enemyX(e))
        dy = ABS(playerY - enemyY(e))
        IF dx < 15 AND dy < 15 THEN
            ' Player hit!
            lives = lives - 1
            enemyActive(e) = 0
            enemyCount = enemyCount - 1
            ex = playerX
            ey = playerY
            GOSUB CreateExplosion
            SOUND 100, 5
            IF lives <= 0 THEN
                gameOver = 1
            END IF
        END IF
    END IF
NEXT e
RETURN

' ============ CREATE EXPLOSION ============
CreateExplosion:
explodeCreated = 0
FOR i = 0 TO MAXEXPLOSIONS - 1
    IF explodeFrame(i) = 0 AND explodeCreated = 0 THEN
        explodeX(i) = ex
        explodeY(i) = ey
        explodeFrame(i) = 1
        explodeCreated = 1
    END IF
NEXT i
RETURN

SpawnExplosion:
ex = playerX
ey = playerY
GOSUB CreateExplosion
RETURN

' ============ UPDATE EXPLOSIONS ============
UpdateExplosions:
FOR i = 0 TO MAXEXPLOSIONS - 1
    IF explodeFrame(i) > 0 THEN
        explodeFrame(i) = explodeFrame(i) + 1
        IF explodeFrame(i) > 8 THEN
            explodeFrame(i) = 0
        END IF
    END IF
NEXT i
RETURN

' ============ UPDATE STARS ============
UpdateStars:
FOR i = 0 TO MAXSTARS - 1
    starY(i) = starY(i) + starSpeed(i)
    IF starY(i) >= SCRH THEN
        starY(i) = 0
        starX(i) = INT(RND * SCRW)
    END IF
NEXT i
RETURN

' ============ DRAW STARS ============
DrawStars:
FOR i = 0 TO MAXSTARS - 1
    c = COLSTAR
    IF starSpeed(i) > 2 THEN c = COLTEXT
    PSET (starX(i), starY(i)), c
NEXT i
RETURN

' ============ DRAW GAME ============
DrawGame:
CLS

' Draw stars
GOSUB DrawStars

' Draw HUD
COLOR COLTEXT
LOCATE 1, 1
PRINT "Score: "; score
LOCATE 1, 20
PRINT "Lives: "; lives
LOCATE 1, 32
PRINT "Lv:"; level

' Draw bullets
FOR i = 0 TO MAXBULLETS - 1
    IF bulletActive(i) = 1 THEN
        LINE (bulletX(i), bulletY(i))-(bulletX(i), bulletY(i) - 5), COLBULLET
    END IF
NEXT i

' Draw enemies
FOR i = 0 TO MAXENEMIES - 1
    IF enemyActive(i) = 1 THEN
        ec = COLENEMY
        IF enemyType(i) = 1 THEN ec = COLENEMY2
        ' Simple enemy shape
        LINE (enemyX(i) - 10, enemyY(i))-(enemyX(i), enemyY(i) - 8), ec
        LINE (enemyX(i) + 10, enemyY(i))-(enemyX(i), enemyY(i) - 8), ec
        LINE (enemyX(i) - 10, enemyY(i))-(enemyX(i) + 10, enemyY(i)), ec
        LINE (enemyX(i) - 5, enemyY(i))-(enemyX(i) - 8, enemyY(i) + 5), ec
        LINE (enemyX(i) + 5, enemyY(i))-(enemyX(i) + 8, enemyY(i) + 5), ec
    END IF
NEXT i

' Draw explosions
FOR i = 0 TO MAXEXPLOSIONS - 1
    IF explodeFrame(i) > 0 THEN
        r = explodeFrame(i) * 3
        ec = COLEXPLODE
        IF explodeFrame(i) > 4 THEN ec = 14
        CIRCLE (explodeX(i), explodeY(i)), r, ec
        IF explodeFrame(i) > 2 THEN
            CIRCLE (explodeX(i), explodeY(i)), r - 3, 4
        END IF
    END IF
NEXT i

' Draw player ship
' Main body triangle
LINE (playerX, playerY - 12)-(playerX - 10, playerY + 8), COLSHIP
LINE (playerX, playerY - 12)-(playerX + 10, playerY + 8), COLSHIP
LINE (playerX - 10, playerY + 8)-(playerX + 10, playerY + 8), COLSHIP
' Cockpit
PSET (playerX, playerY - 5), COLTEXT
' Wings
LINE (playerX - 10, playerY + 3)-(playerX - 15, playerY + 10), COLSHIP
LINE (playerX + 10, playerY + 3)-(playerX + 15, playerY + 10), COLSHIP
' Engine glow (animated)
IF frameCount MOD 4 < 2 THEN
    LINE (playerX - 3, playerY + 8)-(playerX + 3, playerY + 12), 4
ELSE
    LINE (playerX - 3, playerY + 8)-(playerX + 3, playerY + 14), 12
END IF

RETURN

' ============ GAME OVER ============
GameOverScreen:
' Update high score
IF score > highScore THEN
    highScore = score
    PLAY "T200 O4 L8 C E G > C E G > C"
END IF

' Game over sound
SOUND 400, 3
SOUND 300, 3
SOUND 200, 4

' Flash effect
FOR flash = 1 TO 3
    COLOR 12
    LOCATE 9, 11
    PRINT "GAME OVER!"
    _DELAY 0.2
    COLOR 0
    LOCATE 9, 11
    PRINT "          "
    _DELAY 0.1
NEXT flash

COLOR 12
LOCATE 9, 11
PRINT "GAME OVER!"

COLOR COLTEXT
LOCATE 11, 9
PRINT "Final Score: "; score
LOCATE 12, 11
PRINT "Level: "; level

IF score >= highScore AND score > 0 THEN
    COLOR COLTITLE
    LOCATE 14, 8
    PRINT "NEW HIGH SCORE!"
END IF

COLOR COLTEXT
LOCATE 17, 5
PRINT "Press SPACE to continue"

' Wait for input
WaitGameOver:
k$ = INKEY$
IF k$ = " " THEN GOTO TitleScreen
IF k$ = CHR$(27) THEN END
_DELAY 0.05
GOTO WaitGameOver
