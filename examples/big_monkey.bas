' ============================================
' BIG MONKEY - A Donkey Kong Clone
' For PaSiC BASIC Interpreter
' ============================================
' Controls:
'   Arrow Keys or WASD - Move
'   Up/W - Climb ladders
'   Space - Jump
'   M - Toggle music/sound
'   ESC - Quit
' ============================================

SCREEN 13
RANDOMIZE TIMER

' ---- Constants ----
CONST SCREENW = 320
CONST SCREENH = 200
CONST GRAVITY = 0.5
CONST JUMPVEL = -5
CONST PLAYERSPEED = 3
CONST MAXBARRELS = 8
CONST BARRELSPEED = 2

' ---- Player Variables ----
DIM PlayerX AS SINGLE
DIM PlayerY AS SINGLE
DIM PlayerVelY AS SINGLE
DIM PlayerOnGround AS INTEGER
DIM PlayerOnLadder AS INTEGER
DIM PlayerDir AS INTEGER
DIM PlayerLives AS INTEGER
DIM PlayerWon AS INTEGER
DIM PlayerWidth AS INTEGER
DIM PlayerHeight AS INTEGER
DIM JumpLock AS INTEGER

' ---- Barrel Arrays ----
DIM BarrelX(MAXBARRELS) AS SINGLE
DIM BarrelY(MAXBARRELS) AS SINGLE
DIM BarrelVelX(MAXBARRELS) AS SINGLE
DIM BarrelVelY(MAXBARRELS) AS SINGLE
DIM BarrelActive(MAXBARRELS) AS INTEGER
DIM BarrelOnLadder(MAXBARRELS) AS INTEGER
DIM BarrelJumped(MAXBARRELS) AS INTEGER

' ---- Platform Data (x1, y1, x2, y2) ----
CONST NUMPLATFORMS = 6
DIM PlatX1(NUMPLATFORMS) AS INTEGER
DIM PlatY1(NUMPLATFORMS) AS INTEGER
DIM PlatX2(NUMPLATFORMS) AS INTEGER
DIM PlatY2(NUMPLATFORMS) AS INTEGER

' ---- Ladder Data (x, y1, y2) ----
CONST NUMLADDERS = 7
DIM LadderX(NUMLADDERS) AS INTEGER
DIM LadderY1(NUMLADDERS) AS INTEGER
DIM LadderY2(NUMLADDERS) AS INTEGER

' ---- Game State ----
DIM Score AS INTEGER
DIM HighScore AS INTEGER
DIM Level AS INTEGER
DIM BarrelTimer AS INTEGER
DIM GameOver AS INTEGER
DIM MonkeyFrame AS INTEGER
DIM SoundOn AS INTEGER
DIM TitleFrame AS INTEGER
DIM MenuChoice AS INTEGER

' ---- Princess Position ----
DIM PrincessX AS INTEGER
DIM PrincessY AS INTEGER

' ---- Player hitbox ----
PlayerWidth = 8
PlayerHeight = 16

' ============================================
' MAIN PROGRAM
' ============================================

SoundOn = 1
HighScore = 0

TitleLoop:
  GOSUB TitleScreen

  GOSUB InitGame

MainGameLoop:
  GOSUB InitLevel
  GOSUB PlayLevelStart

  DO
    GOSUB ClearScreen
    GOSUB DrawPlatforms
    GOSUB DrawLadders
    GOSUB DrawMonkey
    GOSUB DrawPrincess
    GOSUB DrawPlayer
    GOSUB DrawBarrels
    GOSUB DrawHUD

    GOSUB HandleInput
    GOSUB UpdatePlayer
    GOSUB UpdateBarrels
    GOSUB SpawnBarrels
    GOSUB CheckCollisions
    GOSUB CheckWin

    _DELAY 0.03

  LOOP UNTIL GameOver = 1 OR PlayerWon = 1

  IF PlayerWon = 1 THEN
    GOSUB PlayWinSound
    GOSUB WinScreen
    Level = Level + 1
    IF Level > 5 THEN
      GOSUB VictoryScreen
      GOTO TitleLoop
    END IF
    GOTO MainGameLoop
  END IF

  IF GameOver = 1 THEN
    GOSUB PlayGameOverSound
    GOSUB GameOverScreen
    GOTO TitleLoop
  END IF

END

' ============================================
' SOUND SUBROUTINES
' ============================================

PlayTitleMusic:
  IF SoundOn = 0 THEN RETURN
  ' Donkey Kong style intro fanfare
  PLAY "T180O3L8CDEL4GL8EDL2C"
RETURN

PlayMenuBeep:
  IF SoundOn = 0 THEN RETURN
  SOUND 500, 1
RETURN

PlaySelectSound:
  IF SoundOn = 0 THEN RETURN
  PLAY "T200O4L16CE"
RETURN

PlayJumpSound:
  IF SoundOn = 0 THEN RETURN
  SOUND 400, 1
  SOUND 600, 1
RETURN

PlayLandSound:
  IF SoundOn = 0 THEN RETURN
  SOUND 150, 1
RETURN

PlayClimbSound:
  IF SoundOn = 0 THEN RETURN
  SOUND 300, 1
RETURN

PlayBarrelJumpSound:
  IF SoundOn = 0 THEN RETURN
  ' Bonus points sound
  PLAY "T200O5L16CEG"
RETURN

PlayHitSound:
  IF SoundOn = 0 THEN RETURN
  ' Death sound
  SOUND 200, 2
  SOUND 150, 2
  SOUND 100, 3
RETURN

PlayLevelStart:
  IF SoundOn = 0 THEN RETURN
  PLAY "T150O4L8CEGECE"
RETURN

PlayWinSound:
  IF SoundOn = 0 THEN RETURN
  ' Victory fanfare
  PLAY "T180O4L8CCL4EL8EL4GL2>C"
RETURN

PlayGameOverSound:
  IF SoundOn = 0 THEN RETURN
  ' Sad tune
  PLAY "T100O3L4EDC#L1C"
RETURN

PlayVictoryMusic:
  IF SoundOn = 0 THEN RETURN
  PLAY "T150O4L4CCEL8GL4>CL2C"
  PLAY "T150O4L8GGL4>CL8<BL4>CL2E"
RETURN

' ============================================
' TITLE SCREEN
' ============================================

TitleScreen:
  CLS
  MenuChoice = 1
  TitleFrame = 0

  GOSUB PlayTitleMusic

  DO
    GOSUB DrawTitleScreen
    GOSUB AnimateTitle

    k$ = INKEY$

    ' Menu navigation
    IF k$ = CHR$(0) + "H" OR k$ = "w" OR k$ = "W" THEN
      MenuChoice = MenuChoice - 1
      IF MenuChoice < 1 THEN MenuChoice = 3
      GOSUB PlayMenuBeep
    END IF

    IF k$ = CHR$(0) + "P" OR k$ = "s" OR k$ = "S" THEN
      MenuChoice = MenuChoice + 1
      IF MenuChoice > 3 THEN MenuChoice = 1
      GOSUB PlayMenuBeep
    END IF

    IF k$ = " " OR k$ = CHR$(13) THEN
      GOSUB PlaySelectSound
      IF MenuChoice = 1 THEN
        EXIT DO
      ELSEIF MenuChoice = 2 THEN
        GOSUB ShowInstructions
      ELSEIF MenuChoice = 3 THEN
        CLS
        END
      END IF
    END IF

    IF k$ = CHR$(27) THEN
      CLS
      END
    END IF

    _DELAY 0.05
  LOOP
RETURN

DrawTitleScreen:
  CLS

  ' Sky gradient background
  FOR y = 0 TO 60
    LINE (0, y)-(SCREENW, y), 1
  NEXT y
  FOR y = 61 TO 120
    LINE (0, y)-(SCREENW, y), 9
  NEXT y

  ' Construction site background
  LINE (0, 121)-(SCREENW, SCREENH), 0, BF

  ' Draw steel beams in background
  COLOR 8
  FOR bx = 0 TO SCREENW STEP 40
    LINE (bx, 120)-(bx + 20, 200), 8, BF
  NEXT bx

  ' Title with shadow effect
  LOCATE 3, 10
  COLOR 0
  PRINT "*** BIG MONKEY ***"
  LOCATE 2, 9
  COLOR 14
  PRINT "*** BIG MONKEY ***"

  COLOR 4
  LOCATE 4, 8
  PRINT "A Donkey Kong Tribute"

  ' Draw animated monkey
  GOSUB DrawTitleMonkey

  ' Draw Mario character
  GOSUB DrawTitleMario

  ' Draw Princess
  GOSUB DrawTitlePrincessSmall

  ' Menu options with selection highlight
  LOCATE 14, 12
  IF MenuChoice = 1 THEN
    COLOR 15
    PRINT ">> START GAME <<"
  ELSE
    COLOR 7
    PRINT "   START GAME   "
  END IF

  LOCATE 16, 12
  IF MenuChoice = 2 THEN
    COLOR 15
    PRINT ">> HOW TO PLAY <<"
  ELSE
    COLOR 7
    PRINT "   HOW TO PLAY  "
  END IF

  LOCATE 18, 12
  IF MenuChoice = 3 THEN
    COLOR 15
    PRINT ">>    EXIT    <<"
  ELSE
    COLOR 7
    PRINT "      EXIT      "
  END IF

  ' High score
  LOCATE 21, 10
  COLOR 14
  PRINT "HIGH SCORE: "; HighScore

  ' Sound status
  LOCATE 23, 8
  COLOR 8
  IF SoundOn = 1 THEN
    PRINT "Sound: ON  (M to toggle)"
  ELSE
    PRINT "Sound: OFF (M to toggle)"
  END IF

  LOCATE 24, 6
  COLOR 8
  PRINT "UP/DOWN: Select  SPACE: Confirm"
RETURN

DrawTitleMonkey:
  ' Big animated monkey at top
  mx = 60
  my = 75

  ' Body (brown)
  COLOR 6
  LINE (mx - 25, my)-(mx + 25, my + 25), 6, BF

  ' Head
  CIRCLE (mx, my - 15), 18, 6
  PAINT (mx, my - 15), 6, 6

  ' Face (tan)
  COLOR 14
  CIRCLE (mx, my - 10), 10, 14
  PAINT (mx, my - 10), 14, 14

  ' Eyes - animated blink
  COLOR 15
  IF TitleFrame MOD 60 < 55 THEN
    CIRCLE (mx - 6, my - 15), 4, 15
    CIRCLE (mx + 6, my - 15), 4, 15
    PAINT (mx - 6, my - 15), 15, 15
    PAINT (mx + 6, my - 15), 15, 15
    COLOR 0
    PSET (mx - 6, my - 15), 0
    PSET (mx + 6, my - 15), 0
  ELSE
    ' Blinking
    COLOR 6
    LINE (mx - 10, my - 15)-(mx - 2, my - 15), 6
    LINE (mx + 2, my - 15)-(mx + 10, my - 15), 6
  END IF

  ' Mouth
  COLOR 0
  LINE (mx - 5, my - 3)-(mx + 5, my - 3), 0

  ' Arms with barrel animation
  COLOR 6
  armPhase = TitleFrame MOD 40
  IF armPhase < 20 THEN
    ' Holding barrel up
    LINE (mx - 25, my + 5)-(mx - 35, my - 5), 6
    LINE (mx + 25, my + 5)-(mx + 35, my - 5), 6
    ' Barrel above head
    COLOR 4
    CIRCLE (mx, my - 40), 10, 4
    PAINT (mx, my - 40), 4, 4
    COLOR 6
    LINE (mx - 10, my - 42)-(mx + 10, my - 42), 6
    LINE (mx - 10, my - 38)-(mx + 10, my - 38), 6
  ELSE
    ' Throwing motion
    LINE (mx - 25, my + 5)-(mx - 30, my + 15), 6
    LINE (mx + 25, my + 5)-(mx + 40, my - 10), 6
    ' Barrel being thrown
    COLOR 4
    throwX = mx + 50 + (armPhase - 20) * 3
    throwY = my - 30 + (armPhase - 20)
    IF throwX < SCREENW THEN
      CIRCLE (throwX, throwY), 8, 4
    END IF
  END IF

  ' Legs
  COLOR 6
  LINE (mx - 15, my + 25)-(mx - 20, my + 40), 6
  LINE (mx + 15, my + 25)-(mx + 20, my + 40), 6
RETURN

DrawTitleMario:
  ' Small Mario at bottom
  mx = 270
  my = 170

  ' Body (red)
  COLOR 4
  LINE (mx - 5, my - 10)-(mx + 5, my), 4, BF

  ' Head
  COLOR 14
  CIRCLE (mx, my - 15), 6, 14
  PAINT (mx, my - 15), 14, 14

  ' Hat
  COLOR 4
  LINE (mx - 7, my - 22)-(mx + 7, my - 18), 4, BF

  ' Legs (blue)
  COLOR 1
  LINE (mx - 4, my)-(mx - 5, my + 8), 1
  LINE (mx + 4, my)-(mx + 5, my + 8), 1
RETURN

DrawTitlePrincessSmall:
  ' Princess at top right
  px = 260
  py = 55

  ' Dress (pink)
  COLOR 13
  LINE (px - 6, py)-(px + 6, py + 15), 13, BF

  ' Head
  COLOR 14
  CIRCLE (px, py - 6), 6, 14
  PAINT (px, py - 6), 14, 14

  ' Hair (blonde)
  COLOR 14
  LINE (px - 6, py - 10)-(px + 6, py - 4), 14

  ' Crown
  COLOR 14
  LINE (px - 4, py - 14)-(px + 4, py - 11), 14, BF
  PSET (px - 3, py - 15), 14
  PSET (px, py - 16), 14
  PSET (px + 3, py - 15), 14

  ' HELP! speech bubble
  COLOR 15
  LINE (px + 15, py - 20)-(px + 55, py - 5), 15, B
  LINE (px + 10, py - 10)-(px + 15, py - 12), 15
  LOCATE 4, 36
  PRINT "HELP!"
RETURN

AnimateTitle:
  TitleFrame = TitleFrame + 1
  IF TitleFrame > 1000 THEN TitleFrame = 0

  ' Check for M key to toggle sound
  IF k$ = "m" OR k$ = "M" THEN
    SoundOn = 1 - SoundOn
    IF SoundOn = 1 THEN
      SOUND 400, 1
    END IF
  END IF
RETURN

ShowInstructions:
  CLS

  ' Background
  LINE (0, 0)-(SCREENW, SCREENH), 1, BF

  COLOR 14
  LOCATE 2, 10
  PRINT "=== HOW TO PLAY ==="

  COLOR 15
  LOCATE 5, 3
  PRINT "Guide Mario up the platforms"
  LOCATE 6, 3
  PRINT "to rescue the Princess from"
  LOCATE 7, 3
  PRINT "the Big Monkey!"

  COLOR 11
  LOCATE 10, 5
  PRINT "CONTROLS:"
  COLOR 7
  LOCATE 12, 3
  PRINT "Left/Right or A/D - Move"
  LOCATE 13, 3
  PRINT "Up/W - Climb ladders"
  LOCATE 14, 3
  PRINT "SPACE - Jump"
  LOCATE 15, 3
  PRINT "M - Toggle sound"
  LOCATE 16, 3
  PRINT "ESC - Quit"

  COLOR 11
  LOCATE 18, 5
  PRINT "TIPS:"
  COLOR 7
  LOCATE 20, 3
  PRINT "* Jump over barrels for points"
  LOCATE 21, 3
  PRINT "* Use ladders to climb up"
  LOCATE 22, 3
  PRINT "* Avoid falling barrels!"

  COLOR 10
  LOCATE 24, 6
  PRINT "Press any key to return..."

  DO
    k$ = INKEY$
  LOOP UNTIL k$ <> ""
RETURN

' ============================================
' GAME SUBROUTINES
' ============================================

InitGame:
  Score = 0
  Level = 1
  PlayerLives = 3
  GameOver = 0
RETURN

InitLevel:
  ' Reset player
  PlayerX = 20
  PlayerY = 175
  PlayerVelY = 0
  PlayerOnGround = 1
  PlayerOnLadder = 0
  PlayerDir = 1
  PlayerWon = 0
  JumpLock = 0

  ' Setup platforms - slanted like original DK
  ' Bottom platform (ground)
  PlatX1(0) = 0:   PlatY1(0) = 185: PlatX2(0) = 319: PlatY2(0) = 190
  ' Platform 1 - slopes right
  PlatX1(1) = 0:   PlatY1(1) = 155: PlatX2(1) = 280: PlatY2(1) = 160
  ' Platform 2 - slopes left
  PlatX1(2) = 40:  PlatY1(2) = 125: PlatX2(2) = 319: PlatY2(2) = 130
  ' Platform 3 - slopes right
  PlatX1(3) = 0:   PlatY1(3) = 95:  PlatX2(3) = 280: PlatY2(3) = 100
  ' Platform 4 - slopes left
  PlatX1(4) = 40:  PlatY1(4) = 65:  PlatX2(4) = 319: PlatY2(4) = 70
  ' Top platform (monkey's platform)
  PlatX1(5) = 0:   PlatY1(5) = 35:  PlatX2(5) = 200: PlatY2(5) = 40

  ' Setup ladders (x, top_y, bottom_y)
  LadderX(0) = 260: LadderY1(0) = 155: LadderY2(0) = 185
  LadderX(1) = 60:  LadderY1(1) = 125: LadderY2(1) = 155
  LadderX(2) = 240: LadderY1(2) = 95:  LadderY2(2) = 125
  LadderX(3) = 60:  LadderY1(3) = 65:  LadderY2(3) = 95
  LadderX(4) = 200: LadderY1(4) = 35:  LadderY2(4) = 65
  LadderX(5) = 160: LadderY1(5) = 125: LadderY2(5) = 155
  LadderX(6) = 140: LadderY1(6) = 65:  LadderY2(6) = 95

  ' Princess position
  PrincessX = 160
  PrincessY = 20

  ' Clear all barrels
  FOR i = 0 TO MAXBARRELS - 1
    BarrelActive(i) = 0
    BarrelJumped(i) = 0
  NEXT i

  BarrelTimer = 0
  MonkeyFrame = 0
RETURN

ClearScreen:
  CLS
  ' Draw dark background
  LINE (0, 0)-(319, 199), 0, BF
RETURN

DrawPlatforms:
  FOR i = 0 TO NUMPLATFORMS - 1
    ' Draw main platform (red/orange like NES)
    COLOR 4
    LINE (PlatX1(i), PlatY1(i))-(PlatX2(i), PlatY2(i)), 4, BF
    ' Add girder pattern
    COLOR 6
    FOR gx = PlatX1(i) TO PlatX2(i) STEP 12
      LINE (gx, PlatY1(i))-(gx + 4, PlatY1(i) + 2), 6, BF
      LINE (gx + 6, PlatY1(i) + 3)-(gx + 10, PlatY1(i) + 5), 6, BF
    NEXT gx
  NEXT i
RETURN

DrawLadders:
  COLOR 11
  FOR i = 0 TO NUMLADDERS - 1
    ' Draw ladder sides (cyan like NES)
    LINE (LadderX(i) - 5, LadderY1(i))-(LadderX(i) - 5, LadderY2(i)), 11
    LINE (LadderX(i) + 5, LadderY1(i))-(LadderX(i) + 5, LadderY2(i)), 11
    ' Draw rungs
    FOR ly = LadderY1(i) TO LadderY2(i) STEP 6
      LINE (LadderX(i) - 5, ly)-(LadderX(i) + 5, ly), 11
    NEXT ly
  NEXT i
RETURN

DrawMonkey:
  ' Big Monkey at top left
  mx = 40
  my = 15

  ' Body (brown)
  COLOR 6
  LINE (mx - 20, my)-(mx + 20, my + 18), 6, BF

  ' Head
  CIRCLE (mx, my - 8), 12, 6
  PAINT (mx, my - 8), 6, 6

  ' Face (tan)
  COLOR 14
  CIRCLE (mx, my - 5), 6, 14
  PAINT (mx, my - 5), 14, 14

  ' Eyes
  COLOR 15
  CIRCLE (mx - 4, my - 8), 3, 15
  CIRCLE (mx + 4, my - 8), 3, 15
  COLOR 0
  PSET (mx - 4, my - 8), 0
  PSET (mx + 4, my - 8), 0

  ' Mouth
  COLOR 0
  LINE (mx - 3, my - 1)-(mx + 3, my - 1), 0

  ' Arms (animated)
  COLOR 6
  MonkeyFrame = MonkeyFrame + 1
  IF MonkeyFrame > 30 THEN MonkeyFrame = 0

  IF MonkeyFrame < 15 THEN
    ' Arms up
    LINE (mx - 20, my)-(mx - 30, my - 10), 6
    LINE (mx - 30, my - 10)-(mx - 25, my - 15), 6
    LINE (mx + 20, my)-(mx + 30, my - 10), 6
    LINE (mx + 30, my - 10)-(mx + 25, my - 15), 6
  ELSE
    ' Arms down with barrel
    LINE (mx - 20, my + 5)-(mx - 25, my + 15), 6
    LINE (mx + 20, my + 5)-(mx + 25, my + 15), 6
    ' Barrel in hands
    COLOR 4
    CIRCLE (mx, my + 22), 6, 4
    PAINT (mx, my + 22), 4, 4
    COLOR 6
    LINE (mx - 6, my + 20)-(mx + 6, my + 20), 6
    LINE (mx - 6, my + 24)-(mx + 6, my + 24), 6
  END IF
RETURN

DrawPrincess:
  px = PrincessX
  py = PrincessY

  ' Dress (pink)
  COLOR 13
  LINE (px - 5, py)-(px + 5, py + 12), 13, BF

  ' Head (skin color)
  COLOR 14
  CIRCLE (px, py - 5), 5, 14
  PAINT (px, py - 5), 14, 14

  ' Hair (blonde)
  COLOR 14
  LINE (px - 5, py - 8)-(px + 5, py - 3), 14

  ' Crown
  COLOR 14
  PSET (px - 2, py - 11), 14
  PSET (px, py - 12), 14
  PSET (px + 2, py - 11), 14

  ' Eyes
  COLOR 0
  PSET (px - 2, py - 5), 0
  PSET (px + 2, py - 5), 0

  ' Animated HELP text
  COLOR 15
  IF (MonkeyFrame MOD 20) < 10 THEN
    LOCATE 1, 22
    PRINT "HELP!"
  END IF
RETURN

DrawPlayer:
  plx = INT(PlayerX)
  ply = INT(PlayerY)

  ' Body (red overalls)
  COLOR 4
  LINE (plx - 4, ply - 8)-(plx + 4, ply), 4, BF

  ' Head (skin)
  COLOR 14
  CIRCLE (plx, ply - 12), 4, 14
  PAINT (plx, ply - 12), 14, 14

  ' Hat (red)
  COLOR 4
  LINE (plx - 5, ply - 17)-(plx + 5, ply - 14), 4, BF

  ' Hat brim
  COLOR 4
  IF PlayerDir > 0 THEN
    LINE (plx + 3, ply - 14)-(plx + 7, ply - 14), 4
  ELSE
    LINE (plx - 7, ply - 14)-(plx - 3, ply - 14), 4
  END IF

  ' Eyes
  COLOR 0
  IF PlayerDir > 0 THEN
    PSET (plx + 1, ply - 12), 0
  ELSE
    PSET (plx - 1, ply - 12), 0
  END IF

  ' Legs (blue)
  COLOR 1
  IF PlayerOnLadder = 1 THEN
    ' Climbing animation
    IF (MonkeyFrame MOD 10) < 5 THEN
      LINE (plx - 3, ply)-(plx - 4, ply + 6), 1
      LINE (plx + 3, ply)-(plx + 2, ply + 4), 1
    ELSE
      LINE (plx - 3, ply)-(plx - 2, ply + 4), 1
      LINE (plx + 3, ply)-(plx + 4, ply + 6), 1
    END IF
  ELSEIF PlayerOnGround = 0 THEN
    ' Jumping pose
    LINE (plx - 3, ply)-(plx - 5, ply + 4), 1
    LINE (plx + 3, ply)-(plx + 5, ply + 4), 1
  ELSE
    ' Walking legs
    LINE (plx - 3, ply)-(plx - 4, ply + 6), 1
    LINE (plx + 3, ply)-(plx + 4, ply + 6), 1
  END IF

  ' Arms
  COLOR 14
  IF PlayerOnLadder = 1 THEN
    ' Climbing arms
    LINE (plx - 4, ply - 6)-(plx - 8, ply - 10), 14
    LINE (plx + 4, ply - 6)-(plx + 8, ply - 2), 14
  ELSEIF PlayerDir > 0 THEN
    LINE (plx + 4, ply - 6)-(plx + 7, ply - 3), 14
  ELSE
    LINE (plx - 4, ply - 6)-(plx - 7, ply - 3), 14
  END IF
RETURN

DrawBarrels:
  FOR i = 0 TO MAXBARRELS - 1
    IF BarrelActive(i) = 1 THEN
      bx = INT(BarrelX(i))
      by = INT(BarrelY(i))
      ' Draw barrel (brown/orange)
      COLOR 4
      CIRCLE (bx, by), 6, 4
      PAINT (bx, by), 4, 4
      ' Barrel bands
      COLOR 6
      LINE (bx - 6, by - 2)-(bx + 6, by - 2), 6
      LINE (bx - 6, by + 2)-(bx + 6, by + 2), 6
      ' Rolling effect - skull mark
      COLOR 15
      rollAngle = (bx MOD 12)
      IF rollAngle < 6 THEN
        PSET (bx, by), 15
      END IF
    END IF
  NEXT i
RETURN

DrawHUD:
  ' Score
  COLOR 15
  LOCATE 1, 1
  PRINT "SCORE:"; Score

  ' Level
  LOCATE 1, 15
  PRINT "LVL:"; Level

  ' High score
  COLOR 14
  LOCATE 1, 23
  PRINT "HI:"; HighScore

  ' Draw lives as Mario heads
  FOR i = 1 TO PlayerLives
    lx = 285 + (i * 12)
    ly = 195
    COLOR 14
    CIRCLE (lx, ly), 3, 14
    PAINT (lx, ly), 14, 14
    COLOR 4
    LINE (lx - 3, ly - 4)-(lx + 3, ly - 2), 4, BF
  NEXT i
RETURN

HandleInput:
  ' Clear INKEY$ buffer for toggle keys
  k$ = INKEY$

  ' ESC to quit
  IF KEYDOWN(1) THEN
    GameOver = 1
    RETURN
  END IF

  ' M - Toggle sound (use INKEY to avoid rapid toggle)
  IF k$ = "m" OR k$ = "M" THEN
    SoundOn = 1 - SoundOn
    IF SoundOn = 1 THEN
      SOUND 400, 1
    END IF
  END IF

  ' === SIMULTANEOUS KEY DETECTION using KEYDOWN ===

  ' Left arrow (75) or A key (30)
  IF KEYDOWN(75) OR KEYDOWN(30) THEN
    IF PlayerOnLadder = 0 THEN
      PlayerX = PlayerX - PLAYERSPEED
      PlayerDir = -1
    END IF
  END IF

  ' Right arrow (77) or D key (32)
  IF KEYDOWN(77) OR KEYDOWN(32) THEN
    IF PlayerOnLadder = 0 THEN
      PlayerX = PlayerX + PLAYERSPEED
      PlayerDir = 1
    END IF
  END IF

  ' Up arrow (72) or W key (17) - climb ladder
  IF KEYDOWN(72) OR KEYDOWN(17) THEN
    GOSUB CheckLadderClimb
    IF PlayerOnLadder = 1 THEN
      PlayerY = PlayerY - 3
      PlayerVelY = 0
    END IF
  END IF

  ' Down arrow (80) or S key (31) - descend ladder
  IF KEYDOWN(80) OR KEYDOWN(31) THEN
    GOSUB CheckLadderClimb
    IF PlayerOnLadder = 1 THEN
      PlayerY = PlayerY + 3
      PlayerVelY = 0
    END IF
  END IF

  ' Space (57) - Jump (with lock to prevent continuous jumping)
  IF KEYDOWN(57) THEN
    IF PlayerOnGround = 1 AND PlayerOnLadder = 0 AND JumpLock = 0 THEN
      PlayerVelY = JUMPVEL
      PlayerOnGround = 0
      JumpLock = 1
      GOSUB PlayJumpSound
    END IF
  ELSE
    JumpLock = 0
  END IF
RETURN

CheckLadderClimb:
  wasOnLadder = PlayerOnLadder
  PlayerOnLadder = 0
  FOR i = 0 TO NUMLADDERS - 1
    lx = LadderX(i)
    ly1 = LadderY1(i)
    ly2 = LadderY2(i)

    ' Check if player is near ladder horizontally
    IF ABS(PlayerX - lx) < 12 THEN
      ' Check if player is within ladder vertical range
      IF PlayerY >= ly1 - 10 AND PlayerY <= ly2 + 10 THEN
        PlayerOnLadder = 1
        PlayerX = lx  ' Snap to ladder center
        IF wasOnLadder = 0 THEN
          GOSUB PlayClimbSound
        END IF
        RETURN
      END IF
    END IF
  NEXT i
RETURN

UpdatePlayer:
  ' Apply gravity if not on ladder
  IF PlayerOnLadder = 0 THEN
    PlayerVelY = PlayerVelY + GRAVITY
    PlayerY = PlayerY + PlayerVelY
  ELSE
    ' Check if still on ladder
    stillOnLadder = 0
    FOR i = 0 TO NUMLADDERS - 1
      IF ABS(PlayerX - LadderX(i)) < 8 THEN
        IF PlayerY >= LadderY1(i) - 5 AND PlayerY <= LadderY2(i) + 5 THEN
          stillOnLadder = 1
          EXIT FOR
        END IF
      END IF
    NEXT i
    IF stillOnLadder = 0 THEN
      PlayerOnLadder = 0
    END IF
  END IF

  ' Check platform collisions
  wasOnGround = PlayerOnGround
  PlayerOnGround = 0

  ' Player feet position
  playerFeetY = PlayerY + 6

  FOR i = 0 TO NUMPLATFORMS - 1
    px1 = PlatX1(i)
    py1 = PlatY1(i)
    px2 = PlatX2(i)
    py2 = PlatY2(i)

    ' Check if player is horizontally within platform
    IF PlayerX >= px1 - 5 AND PlayerX <= px2 + 5 THEN
      ' Check if player feet are at platform level (coming from above)
      IF playerFeetY >= py1 AND playerFeetY <= py2 + 8 THEN
        IF PlayerVelY >= 0 THEN
          PlayerY = py1 - 6
          IF PlayerVelY > 2 AND wasOnGround = 0 THEN
            GOSUB PlayLandSound
          END IF
          PlayerVelY = 0
          PlayerOnGround = 1
          IF PlayerOnLadder = 0 THEN
            PlayerOnLadder = 0
          END IF
        END IF
      END IF
    END IF
  NEXT i

  ' Keep player on screen
  IF PlayerX < 10 THEN PlayerX = 10
  IF PlayerX > 310 THEN PlayerX = 310

  ' Fall off bottom - lose life
  IF PlayerY > 195 THEN
    GOSUB LoseLife
  END IF
RETURN

SpawnBarrels:
  BarrelTimer = BarrelTimer + 1

  ' Spawn barrel based on level (faster at higher levels)
  spawnRate = 90 - (Level * 15)
  IF spawnRate < 25 THEN spawnRate = 25

  IF BarrelTimer >= spawnRate THEN
    BarrelTimer = 0

    ' Find inactive barrel
    FOR i = 0 TO MAXBARRELS - 1
      IF BarrelActive(i) = 0 THEN
        BarrelActive(i) = 1
        BarrelX(i) = 55
        BarrelY(i) = 28
        BarrelVelX(i) = BARRELSPEED + (Level * 0.3)
        BarrelVelY(i) = 0
        BarrelOnLadder(i) = 0
        BarrelJumped(i) = 0
        EXIT FOR
      END IF
    NEXT i
  END IF
RETURN

UpdateBarrels:
  FOR i = 0 TO MAXBARRELS - 1
    IF BarrelActive(i) = 1 THEN
      ' Check if barrel should go down a ladder (random chance)
      IF BarrelOnLadder(i) = 0 THEN
        FOR j = 0 TO NUMLADDERS - 1
          IF ABS(BarrelX(i) - LadderX(j)) < 8 THEN
            IF ABS(BarrelY(i) - LadderY1(j)) < 8 THEN
              ' Higher chance to go down ladder at higher levels
              ladderChance = 0.6 + (Level * 0.05)
              IF RND > ladderChance THEN
                BarrelOnLadder(i) = 1
                BarrelX(i) = LadderX(j)
                EXIT FOR
              END IF
            END IF
          END IF
        NEXT j
      END IF

      ' Move barrel
      IF BarrelOnLadder(i) = 1 THEN
        ' Going down ladder
        BarrelY(i) = BarrelY(i) + 2.5

        ' Check if reached bottom of ladder
        FOR j = 0 TO NUMLADDERS - 1
          IF ABS(BarrelX(i) - LadderX(j)) < 3 THEN
            IF BarrelY(i) >= LadderY2(j) THEN
              BarrelOnLadder(i) = 0
              ' Reverse direction based on platform
              BarrelVelX(i) = -BarrelVelX(i)
            END IF
          END IF
        NEXT j
      ELSE
        ' Rolling on platform
        BarrelX(i) = BarrelX(i) + BarrelVelX(i)
        BarrelVelY(i) = BarrelVelY(i) + GRAVITY
        BarrelY(i) = BarrelY(i) + BarrelVelY(i)

        ' Platform collision for barrels
        FOR j = 0 TO NUMPLATFORMS - 1
          bpx1 = PlatX1(j)
          bpy1 = PlatY1(j)
          bpx2 = PlatX2(j)

          IF BarrelX(i) >= bpx1 AND BarrelX(i) <= bpx2 THEN
            IF BarrelY(i) + 6 >= bpy1 AND BarrelY(i) + 6 <= bpy1 + 10 THEN
              IF BarrelVelY(i) >= 0 THEN
                BarrelY(i) = bpy1 - 6
                BarrelVelY(i) = 0
              END IF
            END IF
          END IF
        NEXT j

        ' Reverse at edges
        IF BarrelX(i) < 10 THEN
          BarrelVelX(i) = ABS(BarrelVelX(i))
        END IF
        IF BarrelX(i) > 305 THEN
          BarrelVelX(i) = -ABS(BarrelVelX(i))
        END IF
      END IF

      ' Deactivate if off screen
      IF BarrelY(i) > 200 THEN
        BarrelActive(i) = 0
      END IF
    END IF
  NEXT i
RETURN

CheckCollisions:
  ' Player bounding box
  pLeft = PlayerX - PlayerWidth / 2
  pRight = PlayerX + PlayerWidth / 2
  pTop = PlayerY - PlayerHeight
  pBottom = PlayerY + 6

  FOR i = 0 TO MAXBARRELS - 1
    IF BarrelActive(i) = 1 THEN
      ' Barrel bounding box
      bLeft = BarrelX(i) - 6
      bRight = BarrelX(i) + 6
      bTop = BarrelY(i) - 6
      bBottom = BarrelY(i) + 6

      ' AABB collision check
      IF pRight > bLeft AND pLeft < bRight THEN
        IF pBottom > bTop AND pTop < bBottom THEN
          ' Collision detected - but check if player is above barrel (jumping over)
          IF pBottom < BarrelY(i) - 2 AND PlayerVelY < 0 THEN
            ' Player jumped over - bonus points!
            IF BarrelJumped(i) = 0 THEN
              Score = Score + 100
              BarrelJumped(i) = 1
              GOSUB PlayBarrelJumpSound
            END IF
          ELSEIF pBottom > bTop + 4 THEN
            ' Actually hit by barrel
            GOSUB PlayHitSound
            GOSUB LoseLife
            RETURN
          END IF
        END IF
      END IF

      ' Also award points for jumping over barrel (not colliding but above)
      IF BarrelJumped(i) = 0 THEN
        IF ABS(PlayerX - BarrelX(i)) < 15 THEN
          IF PlayerY < BarrelY(i) - 12 AND PlayerOnGround = 0 THEN
            Score = Score + 100
            BarrelJumped(i) = 1
            GOSUB PlayBarrelJumpSound
          END IF
        END IF
      END IF
    END IF
  NEXT i
RETURN

CheckWin:
  ' Check if player reached the princess
  dx = ABS(PlayerX - PrincessX)
  dy = ABS(PlayerY - PrincessY)

  IF dx < 25 AND dy < 25 THEN
    PlayerWon = 1
    Score = Score + 1000 + (Level * 500)
    IF Score > HighScore THEN
      HighScore = Score
    END IF
  END IF
RETURN

LoseLife:
  PlayerLives = PlayerLives - 1

  ' Death animation - flash and shake
  FOR f = 1 TO 5
    COLOR 4
    LINE (0, 0)-(319, 199), 4, BF
    _DELAY 0.08
    COLOR 0
    LINE (0, 0)-(319, 199), 0, BF
    _DELAY 0.08
  NEXT f

  IF PlayerLives <= 0 THEN
    GameOver = 1
    IF Score > HighScore THEN
      HighScore = Score
    END IF
  ELSE
    ' Reset player position
    PlayerX = 20
    PlayerY = 175
    PlayerVelY = 0
    PlayerOnGround = 1
    PlayerOnLadder = 0

    ' Clear barrels for fairness
    FOR i = 0 TO MAXBARRELS - 1
      BarrelActive(i) = 0
    NEXT i
  END IF
RETURN

' ============================================
' END SCREENS
' ============================================

WinScreen:
  CLS

  ' Celebration background
  FOR y = 0 TO SCREENH
    c = 1
    IF y > 50 THEN c = 9
    IF y > 100 THEN c = 11
    LINE (0, y)-(SCREENW, y), c
  NEXT y

  COLOR 10
  LOCATE 5, 8
  PRINT "*** LEVEL COMPLETE! ***"

  COLOR 14
  LOCATE 8, 10
  PRINT "You rescued her!"

  COLOR 15
  LOCATE 11, 12
  PRINT "Score: "; Score

  LOCATE 13, 10
  PRINT "Level Bonus: "; Level * 500

  ' Draw happy scene - Mario and Princess
  ' Platform
  COLOR 6
  LINE (100, 150)-(220, 160), 6, BF

  ' Mario
  mx = 130
  my = 145
  COLOR 4
  LINE (mx - 5, my - 10)-(mx + 5, my), 4, BF
  COLOR 14
  CIRCLE (mx, my - 15), 5, 14
  PAINT (mx, my - 15), 14, 14
  COLOR 4
  LINE (mx - 6, my - 21)-(mx + 6, my - 17), 4, BF

  ' Princess
  px = 180
  py = 145
  COLOR 13
  LINE (px - 6, py - 12)-(px + 6, py), 13, BF
  COLOR 14
  CIRCLE (px, py - 18), 6, 14
  PAINT (px, py - 18), 14, 14

  ' Heart between them
  COLOR 4
  hx = 155
  hy = 125
  CIRCLE (hx - 3, hy), 4, 4
  CIRCLE (hx + 3, hy), 4, 4
  PAINT (hx - 3, hy), 4, 4
  PAINT (hx + 3, hy), 4, 4
  LINE (hx - 6, hy)-(hx, hy + 8), 4
  LINE (hx + 6, hy)-(hx, hy + 8), 4
  PAINT (hx, hy + 2), 4, 4

  COLOR 7
  LOCATE 21, 6
  PRINT "Press SPACE for next level"

  DO
    k$ = INKEY$
  LOOP UNTIL k$ = " "
RETURN

VictoryScreen:
  CLS

  GOSUB PlayVictoryMusic

  ' Gold background
  FOR y = 0 TO SCREENH
    LINE (0, y)-(SCREENW, y), 14
  NEXT y

  COLOR 4
  LOCATE 4, 8
  PRINT "*** CONGRATULATIONS! ***"

  COLOR 0
  LOCATE 7, 7
  PRINT "You defeated Big Monkey!"

  LOCATE 9, 5
  PRINT "The Princess is saved forever!"

  COLOR 4
  LOCATE 12, 10
  PRINT "FINAL SCORE: "; Score

  IF Score >= HighScore THEN
    COLOR 4
    LOCATE 14, 10
    PRINT "*** NEW HIGH SCORE! ***"
  END IF

  ' Draw trophy
  tx = 160
  ty = 150
  COLOR 14
  LINE (tx - 15, ty)-(tx + 15, ty + 30), 14, BF
  LINE (tx - 20, ty)-(tx + 20, ty + 10), 14, BF
  CIRCLE (tx, ty - 10), 20, 14
  PAINT (tx, ty - 10), 14, 14
  LINE (tx - 10, ty + 30)-(tx + 10, ty + 40), 6, BF

  COLOR 0
  LOCATE 22, 8
  PRINT "Press SPACE to continue"

  DO
    k$ = INKEY$
  LOOP UNTIL k$ = " "
RETURN

GameOverScreen:
  CLS

  ' Dark red background
  LINE (0, 0)-(SCREENW, SCREENH), 0, BF

  ' Fallen barrels decoration
  COLOR 4
  FOR i = 1 TO 8
    bx = 30 + (i * 35)
    by = 170 + RND * 20
    CIRCLE (bx, by), 8, 4
    PAINT (bx, by), 4, 4
    COLOR 6
    LINE (bx - 8, by - 2)-(bx + 8, by - 2), 6
    LINE (bx - 8, by + 2)-(bx + 8, by + 2), 6
    COLOR 4
  NEXT i

  COLOR 4
  LOCATE 6, 10
  PRINT "*** GAME OVER ***"

  ' Sad monkey face
  mx = 160
  my = 90
  COLOR 6
  CIRCLE (mx, my), 25, 6
  PAINT (mx, my), 6, 6
  COLOR 14
  CIRCLE (mx, my + 5), 12, 14
  PAINT (mx, my + 5), 14, 14
  ' Sad eyes
  COLOR 15
  CIRCLE (mx - 8, my - 5), 5, 15
  CIRCLE (mx + 8, my - 5), 5, 15
  COLOR 0
  PSET (mx - 8, my - 3), 0
  PSET (mx + 8, my - 3), 0
  ' Sad mouth
  LINE (mx - 8, my + 12)-(mx + 8, my + 8), 0

  COLOR 15
  LOCATE 14, 10
  PRINT "Final Score: "; Score

  IF Score >= HighScore THEN
    COLOR 14
    LOCATE 16, 9
    PRINT "*** NEW HIGH SCORE! ***"
  ELSE
    COLOR 7
    LOCATE 16, 10
    PRINT "High Score: "; HighScore
  END IF

  COLOR 7
  LOCATE 20, 8
  PRINT "Press SPACE to try again"
  LOCATE 21, 10
  PRINT "or ESC to quit"

  DO
    k$ = INKEY$
    IF k$ = CHR$(27) THEN
      CLS
      END
    END IF
  LOOP UNTIL k$ = " "
RETURN
