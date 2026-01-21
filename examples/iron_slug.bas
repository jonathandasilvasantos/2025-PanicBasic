' ============================================
' IRON SLUG - A Metal Slug Tribute
' For PaSiC BASIC Interpreter
' ============================================
' ENHANCED VERSION with:
' - Sprite-based graphics (BLOAD/PUT)
' - Speed optimizations
' - Pre-computed lookup tables
' - Fixed helicopter sprite direction
' - Balanced enemy shooting rate
' ============================================
' Controls:
'   Left/Right Arrows - Move
'   Up Arrow - Aim Up
'   Down Arrow - Crouch + Aim Down
'   S - Jump
'   A - Shoot
'   Arrow + A - Diagonal shooting
'   Z - Switch weapon (Pistol/Heavy MG/Rocket)
'   M - Toggle sound
'   ESC - Quit
' ============================================

SCREEN 13
RANDOMIZE TIMER

' ---- Screen Constants ----
CONST SCREENW = 320
CONST SCREENH = 200
CONST GROUNDY = 170

' ---- Physics ----
CONST GRAVITY = 0.5
CONST JUMPVEL = -9
CONST PLAYERSPEED = 3
CONST BULLETSPEED = 10
CONST ENEMYSPEED = 1.2

' ---- Game Limits ----
CONST MAXBULLETS = 20
CONST MAXENEMIES = 15
CONST MAXEXPLOSIONS = 5
CONST MAXPLATFORMS = 15
CONST MAXCRATES = 5
CONST LEVELWIDTH = 2400

' ---- Sprite Array Indices ----
' Player sprites (20x24 each)
CONST SPR_PLAYER_R0 = 0
CONST SPR_PLAYER_R1 = 1
CONST SPR_PLAYER_R2 = 2
CONST SPR_PLAYER_R3 = 3
CONST SPR_PLAYER_L0 = 4
CONST SPR_PLAYER_L1 = 5
CONST SPR_PLAYER_L2 = 6
CONST SPR_PLAYER_L3 = 7
CONST SPR_PLAYER_JR = 8
CONST SPR_PLAYER_JL = 9
CONST SPR_PLAYER_CR = 10
CONST SPR_PLAYER_CL = 11

' Enemy sprites
CONST SPR_SOLDIER_R = 12
CONST SPR_SOLDIER_L = 13
CONST SPR_TANK_R = 14
CONST SPR_TANK_L = 15
CONST SPR_HELI_0 = 16
CONST SPR_HELI_1 = 17
CONST SPR_TURRET_R = 18
CONST SPR_TURRET_L = 19
CONST SPR_JETPACK_R = 20
CONST SPR_JETPACK_L = 21

' Effects and pickups
CONST SPR_PICKUP_H = 22
CONST SPR_PICKUP_R = 23
CONST SPR_PICKUP_PLUS = 24
CONST SPR_POW = 25
CONST SPR_POW_FREE = 26
CONST SPR_CRATE = 27
CONST SPR_CRATE_DMG = 28
CONST SPR_EXP0 = 29
CONST SPR_EXP1 = 30
CONST SPR_EXP2 = 31
CONST SPR_EXP3 = 32
CONST SPR_EXP4 = 33
CONST SPR_BULLET_P = 34
CONST SPR_BULLET_E = 35

' ---- Sprite storage arrays ----
' Each sprite is stored in its own array (required by GET/PUT syntax)
DIM SprPlayer0%(500)
DIM SprPlayer1%(500)
DIM SprPlayer2%(500)
DIM SprPlayer3%(500)
DIM SprPlayer4%(500)
DIM SprPlayer5%(500)
DIM SprPlayer6%(500)
DIM SprPlayer7%(500)
DIM SprPlayerJR%(500)
DIM SprPlayerJL%(500)
DIM SprPlayerCR%(500)
DIM SprPlayerCL%(500)
DIM SprSoldierR%(400)
DIM SprSoldierL%(400)
DIM SprTankR%(1500)
DIM SprTankL%(1500)
DIM SprHeliR%(1500)
DIM SprHeliL%(1500)
DIM SprTurretR%(700)
DIM SprTurretL%(700)
DIM SprJetpackR%(500)
DIM SprJetpackL%(500)
DIM SprPickupH%(200)
DIM SprPickupR%(200)
DIM SprPickupPlus%(200)
DIM SprPOW%(400)
DIM SprPOWFree%(400)
DIM SprCrate%(400)
DIM SprCrateDmg%(400)

' ---- Player Variables ----
DIM PlayerX AS SINGLE
DIM PlayerY AS SINGLE
DIM PlayerVelY AS SINGLE
DIM PlayerDir AS INTEGER
DIM PlayerOnGround AS INTEGER
DIM PlayerLives AS INTEGER
DIM PlayerHit AS INTEGER
DIM PlayerHitTimer AS INTEGER
DIM PlayerFrame AS INTEGER
DIM PlayerShooting AS INTEGER
DIM PlayerAimDir AS INTEGER
DIM PlayerCrouching AS INTEGER
DIM PlayerWeapon AS INTEGER
DIM PlayerAmmo AS INTEGER
DIM PlayerGrenades AS INTEGER
DIM JumpLock AS INTEGER
DIM ShootCooldown AS INTEGER

' ---- Camera/Scroll ----
DIM CameraX AS SINGLE
DIM TargetCameraX AS SINGLE

' ---- Bullet Arrays ----
DIM BulletX(MAXBULLETS) AS SINGLE
DIM BulletY(MAXBULLETS) AS SINGLE
DIM BulletVelX(MAXBULLETS) AS SINGLE
DIM BulletVelY(MAXBULLETS) AS SINGLE
DIM BulletActive(MAXBULLETS) AS INTEGER
DIM BulletOwner(MAXBULLETS) AS INTEGER

' ---- Enemy Arrays ----
DIM EnemyX(MAXENEMIES) AS SINGLE
DIM EnemyY(MAXENEMIES) AS SINGLE
DIM EnemyVelY(MAXENEMIES) AS SINGLE
DIM EnemyType(MAXENEMIES) AS INTEGER
DIM EnemyHealth(MAXENEMIES) AS INTEGER
DIM EnemyActive(MAXENEMIES) AS INTEGER
DIM EnemyDir(MAXENEMIES) AS INTEGER
DIM EnemyFrame(MAXENEMIES) AS INTEGER
DIM EnemyShootTimer(MAXENEMIES) AS INTEGER

' ---- Platform Arrays ----
DIM PlatX(MAXPLATFORMS) AS INTEGER
DIM PlatY(MAXPLATFORMS) AS INTEGER
DIM PlatW(MAXPLATFORMS) AS INTEGER
DIM PlatType(MAXPLATFORMS) AS INTEGER
DIM PlatActive(MAXPLATFORMS) AS INTEGER

' ---- Crate Arrays ----
DIM CrateX(MAXCRATES) AS INTEGER
DIM CrateY(MAXCRATES) AS INTEGER
DIM CrateHealth(MAXCRATES) AS INTEGER
DIM CrateActive(MAXCRATES) AS INTEGER

' ---- POW Arrays ----
CONST MAXPOWS = 6
DIM PowX(MAXPOWS) AS INTEGER
DIM PowY(MAXPOWS) AS INTEGER
DIM PowActive(MAXPOWS) AS INTEGER
DIM PowRescued(MAXPOWS) AS INTEGER
DIM PowFrame(MAXPOWS) AS INTEGER

' ---- Pickup Arrays ----
CONST MAXPICKUPS = 6
DIM PickupX(MAXPICKUPS) AS INTEGER
DIM PickupY(MAXPICKUPS) AS INTEGER
DIM PickupType(MAXPICKUPS) AS INTEGER
DIM PickupActive(MAXPICKUPS) AS INTEGER

' ---- Explosion Arrays ----
DIM ExpX(MAXEXPLOSIONS) AS SINGLE
DIM ExpY(MAXEXPLOSIONS) AS SINGLE
DIM ExpFrame(MAXEXPLOSIONS) AS INTEGER
DIM ExpActive(MAXEXPLOSIONS) AS INTEGER

' ---- Game State ----
DIM Score AS INTEGER
DIM HighScore AS INTEGER
DIM Level AS INTEGER
DIM GameOver AS INTEGER
DIM LevelComplete AS INTEGER
DIM SoundOn AS INTEGER
DIM MenuChoice AS INTEGER
DIM TitleFrame AS INTEGER
DIM BossActive AS INTEGER
DIM BossHealth AS INTEGER
DIM BossX AS SINGLE
DIM BossY AS SINGLE
DIM BossFrame AS INTEGER
DIM ZoneType AS INTEGER

' ---- Optimization: Pre-computed values ----
DIM ScreenCenterX AS INTEGER
DIM HalfScreenW AS INTEGER
DIM FrameCounter AS INTEGER
DIM SpritesLoaded AS INTEGER

' ---- Optimization: Cached screen coordinates ----
DIM LastDrawnPlayerX AS INTEGER
DIM LastDrawnPlayerY AS INTEGER

' Initialize pre-computed values
ScreenCenterX = SCREENW / 2
HalfScreenW = SCREENW / 2
SpritesLoaded = 0

' ============================================
' MAIN PROGRAM
' ============================================

SoundOn = 1
HighScore = 0

' Load sprites at startup
GOSUB LoadSprites

TitleLoop:
  GOSUB TitleScreen
  GOSUB InitGame

MainGameLoop:
  GOSUB InitLevel
  GOSUB SetupPOWs
  GOSUB SetupPickups
  GOSUB PlayLevelStart

  DO
    FrameCounter = FrameCounter + 1
    IF FrameCounter > 1000 THEN FrameCounter = 0

    GOSUB UpdateCamera
    GOSUB DrawBackground
    GOSUB DrawGround
    GOSUB DrawPlatforms
    GOSUB DrawCrates
    GOSUB DrawPickups
    GOSUB DrawPOWs
    GOSUB DrawPlayer
    GOSUB DrawBullets
    GOSUB DrawEnemies
    GOSUB DrawExplosions
    GOSUB DrawHUD

    GOSUB HandleInput
    GOSUB UpdatePlayer
    GOSUB UpdatePlatforms
    GOSUB UpdateBullets
    GOSUB UpdateEnemies
    GOSUB UpdateExplosions
    GOSUB UpdatePOWs
    GOSUB UpdatePickups
    GOSUB SpawnEnemies
    GOSUB CheckCollisions
    GOSUB CheckLevelComplete

    _DELAY 0.018

  LOOP UNTIL GameOver = 1 OR LevelComplete = 1

  IF LevelComplete = 1 THEN
    GOSUB PlayWinSound
    GOSUB LevelCompleteScreen
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
' SPRITE LOADING
' ============================================

LoadSprites:
  ' Check if sprite file exists and load it
  ' If not available, use fallback drawing
  ON ERROR GOTO SpritesNotFound

  ' Load spritesheet into video memory
  DEF SEG = &HA000
  BLOAD "iron_slug_sprites.bin", 0

  ' Capture individual sprites using GET
  ' Player sprites (20x24 each, row 0)
  GET (0, 0)-(19, 23), SprPlayer0%
  GET (20, 0)-(39, 23), SprPlayer1%
  GET (40, 0)-(59, 23), SprPlayer2%
  GET (60, 0)-(79, 23), SprPlayer3%
  GET (80, 0)-(99, 23), SprPlayer4%
  GET (100, 0)-(119, 23), SprPlayer5%
  GET (120, 0)-(139, 23), SprPlayer6%
  GET (140, 0)-(159, 23), SprPlayer7%
  GET (160, 0)-(179, 23), SprPlayerJR%
  GET (180, 0)-(199, 23), SprPlayerJL%
  GET (200, 0)-(219, 23), SprPlayerCR%
  GET (220, 0)-(239, 23), SprPlayerCL%

  ' Enemy soldiers (16x20 each, row 1 starting at y=26)
  GET (0, 26)-(15, 45), SprSoldierR%
  GET (64, 26)-(79, 45), SprSoldierL%

  ' Tank (55x25, row 2 starting at y=50)
  GET (0, 50)-(54, 74), SprTankR%
  GET (60, 50)-(114, 74), SprTankL%

  ' Helicopter (55x25, row 3 starting at y=80)
  GET (0, 80)-(54, 104), SprHeliR%
  GET (60, 80)-(114, 104), SprHeliL%

  ' Turret (32x20, row 4 starting at y=110)
  GET (0, 110)-(31, 129), SprTurretR%
  GET (35, 110)-(66, 129), SprTurretL%

  ' Jetpack soldier (20x20)
  GET (75, 110)-(94, 129), SprJetpackR%
  GET (125, 110)-(144, 129), SprJetpackL%

  ' Pickups (16x12, row 5 starting at y=135)
  GET (0, 135)-(15, 146), SprPickupH%
  GET (20, 135)-(35, 146), SprPickupR%
  GET (40, 135)-(55, 146), SprPickupPlus%

  ' POWs (14x24)
  GET (60, 132)-(73, 155), SprPOW%
  GET (80, 132)-(93, 155), SprPOWFree%

  ' Crates (20x16)
  GET (100, 135)-(119, 150), SprCrate%
  GET (125, 135)-(144, 150), SprCrateDmg%

  SpritesLoaded = 1
  CLS
  RETURN

SpritesNotFound:
  SpritesLoaded = 0
  ON ERROR GOTO 0
  CLS
  RETURN

' ============================================
' SOUND SUBROUTINES
' ============================================

PlayTitleMusic:
  IF SoundOn = 0 THEN RETURN
  PLAY "T200O3L8EGAL4>CL8<BL4AL8GL2E"
RETURN

PlayMenuBeep:
  IF SoundOn = 0 THEN RETURN
  SOUND 600, 1
RETURN

PlaySelectSound:
  IF SoundOn = 0 THEN RETURN
  PLAY "T200O4L16EG"
RETURN

PlayShootSound:
  IF SoundOn = 0 THEN RETURN
  SOUND 800, 1
  SOUND 400, 1
RETURN

PlayExplosionSound:
  IF SoundOn = 0 THEN RETURN
  SOUND 100, 2
  SOUND 80, 2
  SOUND 60, 3
RETURN

PlayHitSound:
  IF SoundOn = 0 THEN RETURN
  SOUND 200, 2
  SOUND 150, 2
RETURN

PlayJumpSound:
  IF SoundOn = 0 THEN RETURN
  SOUND 300, 1
  SOUND 500, 1
RETURN

PlayLevelStart:
  IF SoundOn = 0 THEN RETURN
  PLAY "T180O4L8CEGECE>C"
RETURN

PlayWinSound:
  IF SoundOn = 0 THEN RETURN
  PLAY "T150O4L4CEL8GL4>CL2E"
RETURN

PlayGameOverSound:
  IF SoundOn = 0 THEN RETURN
  PLAY "T100O3L4EDC#L1C"
RETURN

PlayVictoryMusic:
  IF SoundOn = 0 THEN RETURN
  PLAY "T150O4L4CCEL8GL4>CL2C"
  PLAY "T150O4L8GGL4>CL8<BL4>CL2E"
RETURN

PlayPOWSound:
  IF SoundOn = 0 THEN RETURN
  PLAY "T200O5L16CEGC"
RETURN

PlayPickupSound:
  IF SoundOn = 0 THEN RETURN
  SOUND 1000, 1
  SOUND 1200, 1
RETURN

PlayHelicopterSound:
  IF SoundOn = 0 THEN RETURN
  SOUND 150, 1
  SOUND 180, 1
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

    IF k$ = "m" OR k$ = "M" THEN
      SoundOn = 1 - SoundOn
    END IF

    _DELAY 0.05
  LOOP
RETURN

DrawTitleScreen:
  CLS

  ' Night sky gradient (dark blue to black)
  LINE (0, 0)-(SCREENW, 30), 1, BF
  LINE (0, 30)-(SCREENW, 60), 0, BF
  LINE (0, 60)-(SCREENW, 80), 0, BF

  ' Many twinkling stars
  PSET (15, 8), 15
  PSET (23, 12), 15
  PSET (45, 5), 7
  PSET (69, 26), 15
  PSET (85, 15), 7
  PSET (115, 5), 15
  PSET (135, 22), 7
  PSET (155, 10), 15
  PSET (180, 28), 15
  PSET (195, 8), 7
  PSET (207, 19), 15
  PSET (230, 5), 7
  PSET (253, 33), 7
  PSET (275, 12), 15
  PSET (299, 8), 15
  PSET (310, 25), 7
  ' Blinking stars
  IF TitleFrame MOD 20 < 10 THEN
    PSET (50, 18), 15
    PSET (170, 6), 15
    PSET (240, 28), 15
  END IF

  ' Big beautiful moon with glow
  moonX = 50
  moonY = 30
  ' Moon glow (outer ring)
  CIRCLE (moonX, moonY), 24, 8
  CIRCLE (moonX, moonY), 22, 7
  ' Moon body
  CIRCLE (moonX, moonY), 20, 15
  PAINT (moonX, moonY), 15, 15
  ' Detailed craters
  CIRCLE (moonX - 8, moonY - 6), 5, 7
  PAINT (moonX - 8, moonY - 6), 7, 7
  CIRCLE (moonX + 6, moonY + 5), 4, 7
  PAINT (moonX + 6, moonY + 5), 7, 7
  CIRCLE (moonX - 3, moonY + 8), 3, 7
  CIRCLE (moonX + 10, moonY - 3), 2, 7
  CIRCLE (moonX - 5, moonY + 2), 2, 8

  ' Ground/horizon
  LINE (0, 80)-(SCREENW, SCREENH), 0, BF

  ' Detailed destroyed buildings with windows
  ' Building 1 - tall damaged
  LINE (15, 40)-(45, 80), 8, BF
  LINE (15, 40)-(45, 40), 7
  LINE (15, 40)-(15, 80), 7
  LINE (20, 45)-(25, 50), 0, BF
  LINE (30, 55)-(35, 60), 0, BF
  LINE (20, 65)-(25, 70), 1, BF

  ' Building 2 - medium
  LINE (60, 55)-(95, 80), 8, BF
  LINE (60, 55)-(95, 55), 7
  LINE (65, 60)-(70, 65), 0, BF
  LINE (80, 60)-(85, 65), 1, BF
  LINE (72, 70)-(77, 75), 0, BF

  ' Building 3 - tall tower
  LINE (120, 35)-(155, 80), 8, BF
  LINE (120, 35)-(155, 35), 7
  LINE (120, 35)-(120, 80), 7
  ' Windows
  LINE (125, 40)-(130, 45), 0, BF
  LINE (140, 40)-(145, 45), 1, BF
  LINE (125, 52)-(130, 57), 1, BF
  LINE (140, 52)-(145, 57), 0, BF
  LINE (125, 64)-(130, 69), 0, BF
  LINE (140, 64)-(145, 69), 1, BF

  ' Building 4
  LINE (180, 50)-(220, 80), 8, BF
  LINE (180, 50)-(220, 50), 7
  LINE (185, 55)-(195, 62), 0, BF
  LINE (200, 55)-(210, 62), 1, BF
  LINE (190, 68)-(200, 75), 0, BF

  ' Building 5 - damaged
  LINE (250, 45)-(290, 80), 8, BF
  LINE (250, 45)-(275, 45), 7
  LINE (275, 45)-(290, 55), 7
  LINE (255, 50)-(265, 58), 0, BF
  LINE (270, 60)-(280, 68), 1, BF
  LINE (255, 70)-(265, 78), 1, BF

  ' Rubble on ground
  LINE (95, 78)-(115, 80), 8, BF
  LINE (225, 77)-(245, 80), 8, BF
  LINE (295, 78)-(310, 80), 8, BF

  ' Animated fires on buildings
  IF TitleFrame MOD 10 < 5 THEN
    ' Fire on building 1
    CIRCLE (30, 38), 4, 4
    PAINT (30, 38), 4, 4
    CIRCLE (30, 36), 2, 14
    ' Fire on building 3
    CIRCLE (137, 33), 5, 4
    PAINT (137, 33), 4, 4
    CIRCLE (137, 30), 3, 14
  END IF
  IF TitleFrame MOD 8 < 4 THEN
    CIRCLE (30, 34), 2, 14
    PAINT (30, 34), 14, 14
    CIRCLE (137, 28), 2, 15
  END IF
  IF TitleFrame MOD 12 < 6 THEN
    ' Smoke
    CIRCLE (32, 28), 3, 8
    CIRCLE (139, 22), 4, 8
  END IF

  ' Title
  COLOR 8
  LOCATE 3, 11
  PRINT "=== IRON SLUG ==="
  COLOR 12
  LOCATE 2, 10
  PRINT "=== IRON SLUG ==="

  COLOR 15
  LOCATE 5, 9
  PRINT "Run and Gun Action"

  ' Draw soldier and tank characters
  GOSUB DrawTitleSoldier
  GOSUB DrawTitleTank

  ' Menu options
  LOCATE 13, 12
  IF MenuChoice = 1 THEN
    COLOR 15
    PRINT ">> MISSION START <<"
  ELSE
    COLOR 7
    PRINT "   MISSION START   "
  END IF

  LOCATE 15, 12
  IF MenuChoice = 2 THEN
    COLOR 15
    PRINT ">>   BRIEFING   <<"
  ELSE
    COLOR 7
    PRINT "     BRIEFING     "
  END IF

  LOCATE 17, 12
  IF MenuChoice = 3 THEN
    COLOR 15
    PRINT ">>    RETREAT   <<"
  ELSE
    COLOR 7
    PRINT "      RETREAT     "
  END IF

  ' High score
  LOCATE 20, 10
  COLOR 14
  PRINT "HIGH SCORE: "; HighScore

  ' Sound status
  LOCATE 22, 8
  COLOR 8
  IF SoundOn = 1 THEN
    PRINT "Sound: ON  (M to toggle)"
  ELSE
    PRINT "Sound: OFF (M to toggle)"
  END IF

  LOCATE 24, 4
  COLOR 8
  PRINT "UP/DOWN: Select  SPACE: Confirm"
RETURN

DrawTitleSoldier:
  sx = 80
  sy = 130

  ' Shadow
  CIRCLE (sx, sy + 12), 8, 8

  ' Legs animated with boots
  IF TitleFrame MOD 20 < 10 THEN
    LINE (sx - 4, sy)-(sx - 8, sy + 8), 2, BF
    LINE (sx + 2, sy)-(sx + 6, sy + 8), 2, BF
    LINE (sx - 10, sy + 6)-(sx - 6, sy + 10), 6, BF
    LINE (sx + 4, sy + 6)-(sx + 8, sy + 10), 6, BF
  ELSE
    LINE (sx - 2, sy)-(sx + 2, sy + 8), 2, BF
    LINE (sx + 4, sy)-(sx + 8, sy + 8), 2, BF
    LINE (sx - 4, sy + 6)-(sx + 4, sy + 10), 6, BF
    LINE (sx + 6, sy + 6)-(sx + 10, sy + 10), 6, BF
  END IF

  ' Body - vest with detail
  LINE (sx - 7, sy - 16)-(sx + 7, sy), 10, BF
  LINE (sx - 6, sy - 14)-(sx + 6, sy - 2), 2, BF
  LINE (sx - 7, sy - 16)-(sx + 7, sy - 16), 10
  ' Belt
  LINE (sx - 7, sy - 2)-(sx + 7, sy), 6, BF

  ' Head - round
  CIRCLE (sx, sy - 21), 6, 14
  PAINT (sx, sy - 21), 14, 14
  ' Eye
  PSET (sx + 2, sy - 22), 0

  ' Helmet - rounded
  CIRCLE (sx, sy - 24), 8, 8
  LINE (sx - 8, sy - 24)-(sx + 8, sy - 20), 8, BF
  LINE (sx - 7, sy - 26)-(sx + 7, sy - 24), 7

  ' Back arm
  LINE (sx - 8, sy - 12)-(sx - 10, sy - 6), 2, BF

  ' Gun arm
  LINE (sx + 6, sy - 14)-(sx + 10, sy - 10), 10, BF
  ' Hand
  CIRCLE (sx + 11, sy - 9), 2, 14
  ' Gun
  LINE (sx + 10, sy - 12)-(sx + 24, sy - 10), 8, BF
  LINE (sx + 10, sy - 10)-(sx + 22, sy - 8), 7, BF
  LINE (sx + 22, sy - 14)-(sx + 26, sy - 6), 8, BF

  ' Muzzle flash with circle
  IF TitleFrame MOD 30 < 5 THEN
    CIRCLE (sx + 28, sy - 10), 6, 14
    PAINT (sx + 28, sy - 10), 14, 14
    CIRCLE (sx + 28, sy - 10), 4, 15
    PAINT (sx + 28, sy - 10), 15, 15
  END IF
RETURN

DrawTitleTank:
  tx = 230
  ty = 135

  ' Shadow
  CIRCLE (tx, ty + 15), 25, 8

  ' Tracks with wheels
  LINE (tx - 30, ty + 5)-(tx + 30, ty + 14), 8, BF
  LINE (tx - 28, ty + 8)-(tx + 28, ty + 12), 0, BF
  ' Track wheels (circles!)
  CIRCLE (tx - 20, ty + 10), 5, 0
  PAINT (tx - 20, ty + 10), 0, 0
  CIRCLE (tx - 20, ty + 10), 3, 8
  CIRCLE (tx, ty + 10), 5, 0
  PAINT (tx, ty + 10), 0, 0
  CIRCLE (tx, ty + 10), 3, 8
  CIRCLE (tx + 20, ty + 10), 5, 0
  PAINT (tx + 20, ty + 10), 0, 0
  CIRCLE (tx + 20, ty + 10), 3, 8

  ' Tank hull with detail
  LINE (tx - 28, ty - 8)-(tx + 28, ty + 6), 7, BF
  LINE (tx - 26, ty - 6)-(tx + 26, ty + 4), 8, BF
  LINE (tx - 28, ty - 8)-(tx + 28, ty - 8), 15
  ' Hull detail lines
  LINE (tx - 10, ty - 6)-(tx - 10, ty + 4), 7
  LINE (tx + 10, ty - 6)-(tx + 10, ty + 4), 7
  ' Viewport
  LINE (tx - 5, ty - 4)-(tx + 5, ty), 0, BF

  ' Turret (rounded look)
  CIRCLE (tx - 5, ty - 14), 12, 2
  LINE (tx - 17, ty - 14)-(tx + 7, ty - 8), 2, BF
  LINE (tx - 15, ty - 18)-(tx + 5, ty - 10), 10, BF
  LINE (tx - 15, ty - 18)-(tx + 5, ty - 18), 2
  ' Hatch
  CIRCLE (tx - 5, ty - 16), 4, 10
  LINE (tx - 8, ty - 18)-(tx - 2, ty - 14), 7

  ' Main cannon with muzzle brake
  LINE (tx + 5, ty - 16)-(tx + 42, ty - 12), 8, BF
  LINE (tx + 5, ty - 16)-(tx + 40, ty - 16), 7
  LINE (tx + 38, ty - 18)-(tx + 44, ty - 10), 7, BF

  ' Cannon flash with circles
  IF TitleFrame MOD 40 < 8 THEN
    CIRCLE (tx + 48, ty - 14), 8, 14
    PAINT (tx + 48, ty - 14), 14, 14
    CIRCLE (tx + 48, ty - 14), 5, 15
    PAINT (tx + 48, ty - 14), 15, 15
    CIRCLE (tx + 50, ty - 14), 3, 15
  END IF
RETURN

AnimateTitle:
  TitleFrame = TitleFrame + 1
  IF TitleFrame > 1000 THEN TitleFrame = 0
RETURN

ShowInstructions:
  CLS
  LINE (0, 0)-(SCREENW, SCREENH), 0, BF

  COLOR 12
  LOCATE 2, 8
  PRINT "=== MISSION BRIEFING ==="

  COLOR 15
  LOCATE 4, 1
  PRINT "Soldier, infiltrate enemy lines"
  LOCATE 5, 1
  PRINT "and eliminate all hostiles!"

  COLOR 11
  LOCATE 7, 2
  PRINT "CONTROLS:"
  COLOR 7
  LOCATE 8, 1
  PRINT "A/D or Arrows - Move"
  LOCATE 9, 1
  PRINT "W/Up - Jump + Aim Up"
  LOCATE 10, 1
  PRINT "S/Down - Crouch + Aim Down"
  LOCATE 11, 1
  PRINT "Space/X - Fire  Z - Switch Gun"
  LOCATE 12, 1
  PRINT "M - Sound  ESC - Abort"

  COLOR 11
  LOCATE 14, 2
  PRINT "WEAPONS:"
  COLOR 7
  LOCATE 15, 1
  PRINT "P-Pistol H-Heavy MG R-Rocket"

  COLOR 11
  LOCATE 17, 2
  PRINT "ENEMIES:"
  COLOR 4
  LOCATE 18, 1
  PRINT "Soldiers Tanks Helicopters"
  LOCATE 19, 1
  PRINT "Turrets Jetpack Troops"

  COLOR 11
  LOCATE 21, 2
  PRINT "TIPS:"
  COLOR 7
  LOCATE 22, 1
  PRINT "* Rescue POWs for bonus!"
  LOCATE 23, 1
  PRINT "* Destroy crates for items"

  COLOR 10
  LOCATE 25, 5
  PRINT "Press any key..."

  DO
    k$ = INKEY$
  LOOP UNTIL k$ <> ""
RETURN

' ============================================
' GAME INITIALIZATION
' ============================================

InitGame:
  Score = 0
  Level = 1
  PlayerLives = 3
  GameOver = 0
RETURN

InitLevel:
  PlayerX = 50
  PlayerY = GROUNDY - 20
  PlayerVelY = 0
  PlayerDir = 1
  PlayerOnGround = 1
  PlayerHit = 0
  PlayerHitTimer = 0
  PlayerFrame = 0
  PlayerShooting = 0
  PlayerAimDir = 0
  PlayerCrouching = 0
  PlayerWeapon = 1
  PlayerAmmo = 50
  PlayerGrenades = 3
  JumpLock = 0
  ShootCooldown = 0
  LevelComplete = 0

  CameraX = 0
  TargetCameraX = 0

  ZoneType = ((Level - 1) MOD 3) + 1

  ' Clear arrays using optimized loop
  FOR i = 0 TO MAXBULLETS - 1
    BulletActive(i) = 0
  NEXT i

  FOR i = 0 TO MAXENEMIES - 1
    EnemyActive(i) = 0
  NEXT i

  FOR i = 0 TO MAXEXPLOSIONS - 1
    ExpActive(i) = 0
  NEXT i

  FOR i = 0 TO MAXPLATFORMS - 1
    PlatActive(i) = 0
  NEXT i

  FOR i = 0 TO MAXCRATES - 1
    CrateActive(i) = 0
  NEXT i

  GOSUB SetupPlatforms
  GOSUB SetupCrates

  BossActive = 0
  BossHealth = 25 + Level * 15
  BossX = LEVELWIDTH - 150
  BossY = GROUNDY - 60
  BossFrame = 0
RETURN

SetupPlatforms:
  platIdx = 0
  FOR px = 300 TO LEVELWIDTH - 400 STEP 250
    IF platIdx < MAXPLATFORMS THEN
      PlatActive(platIdx) = 1
      PlatX(platIdx) = px + INT(RND * 60)
      PlatY(platIdx) = GROUNDY - 35 - INT(RND * 50)
      PlatW(platIdx) = 50 + INT(RND * 30)
      PlatType(platIdx) = INT(RND * 3) + 1
      platIdx = platIdx + 1
    END IF
  NEXT px
RETURN

SetupCrates:
  crateIdx = 0
  FOR cx = 250 TO LEVELWIDTH - 500 STEP 300
    IF crateIdx < MAXCRATES THEN
      IF RND < 0.6 THEN
        CrateActive(crateIdx) = 1
        CrateX(crateIdx) = cx + RND * 100
        CrateY(crateIdx) = GROUNDY - 16
        CrateHealth(crateIdx) = 2
        crateIdx = crateIdx + 1
      END IF
    END IF
  NEXT cx
RETURN

SetupPOWs:
  FOR pw = 0 TO MAXPOWS - 1
    PowActive(pw) = 0
    PowRescued(pw) = 0
  NEXT pw

  powIdx = 0
  FOR px = 400 TO LEVELWIDTH - 600 STEP 350
    IF powIdx < MAXPOWS THEN
      IF RND < 0.7 THEN
        PowActive(powIdx) = 1
        PowX(powIdx) = px + RND * 100
        PowY(powIdx) = GROUNDY - 15
        PowRescued(powIdx) = 0
        PowFrame(powIdx) = INT(RND * 40)
        powIdx = powIdx + 1
      END IF
    END IF
  NEXT px
RETURN

SetupPickups:
  FOR pk = 0 TO MAXPICKUPS - 1
    PickupActive(pk) = 0
  NEXT pk

  pickIdx = 0
  FOR px = 500 TO LEVELWIDTH - 500 STEP 400
    IF pickIdx < MAXPICKUPS THEN
      IF RND < 0.5 THEN
        PickupActive(pickIdx) = 1
        PickupX(pickIdx) = px + RND * 150
        PickupY(pickIdx) = GROUNDY - 12
        typeRoll = RND
        IF typeRoll < 0.4 THEN
          PickupType(pickIdx) = 1
        ELSEIF typeRoll < 0.7 THEN
          PickupType(pickIdx) = 2
        ELSE
          PickupType(pickIdx) = 3
        END IF
        pickIdx = pickIdx + 1
      END IF
    END IF
  NEXT px
RETURN

' ============================================
' CAMERA SYSTEM
' ============================================

UpdateCamera:
  TargetCameraX = PlayerX - 100

  IF TargetCameraX < 0 THEN TargetCameraX = 0
  IF TargetCameraX > LEVELWIDTH - SCREENW THEN TargetCameraX = LEVELWIDTH - SCREENW

  ' Smooth camera (optimized multiply)
  CameraX = CameraX + (TargetCameraX - CameraX) * 0.1
RETURN

' ============================================
' DRAWING SUBROUTINES (Optimized with sprites)
' ============================================

DrawBackground:
  CLS

  ' Night sky gradient (dark blue to black)
  LINE (0, 0)-(SCREENW, 25), 1, BF
  LINE (0, 26)-(SCREENW, 50), 1, BF
  LINE (0, 51)-(SCREENW, 79), 0, BF

  ' Bright stars (white, varying sizes)
  CIRCLE (23, 12), 2, 15
  PAINT (23, 12), 15, 15
  PSET (69, 26), 15
  PSET (70, 26), 15
  CIRCLE (115, 8), 1, 15
  PSET (161, 40), 15
  CIRCLE (207, 19), 2, 15
  PAINT (207, 19), 15, 15
  PSET (253, 33), 15
  PSET (299, 8), 15
  PSET (300, 8), 15

  ' Dim stars (gray, small)
  PSET (41, 45), 7
  PSET (180, 28), 7
  PSET (90, 35), 7
  PSET (145, 18), 7
  PSET (280, 48), 7
  PSET (55, 58), 7
  PSET (220, 65), 7
  PSET (170, 55), 7

  ' Twinkling stars (animated)
  IF FrameCount MOD 30 < 15 THEN
    CIRCLE (135, 22), 2, 15
    PAINT (135, 22), 15, 15
    PSET (265, 15), 15
  ELSE
    PSET (135, 22), 7
    CIRCLE (265, 15), 1, 15
  END IF

  ' Moon (parallax scroll) with glow and craters
  moonX = 270 - INT(CameraX * 0.02)
  moonY = 30
  IF moonX > -30 AND moonX < SCREENW + 30 THEN
    ' Glow effect
    CIRCLE (moonX, moonY), 26, 8
    CIRCLE (moonX, moonY), 24, 7
    ' Main moon body
    CIRCLE (moonX, moonY), 20, 15
    PAINT (moonX, moonY), 15, 15
    ' Craters with shading
    CIRCLE (moonX - 6, moonY - 5), 5, 7
    CIRCLE (moonX - 7, moonY - 6), 3, 8
    CIRCLE (moonX + 7, moonY + 4), 4, 7
    CIRCLE (moonX + 6, moonY + 3), 2, 8
    CIRCLE (moonX - 3, moonY + 7), 3, 7
    CIRCLE (moonX + 2, moonY - 8), 2, 7
    CIRCLE (moonX + 1, moonY - 9), 1, 8
  END IF

  ' Horizon line with slight gradient
  LINE (0, 78)-(SCREENW, 78), 8
  LINE (0, 79)-(SCREENW, 79), 7
RETURN

DrawGround:
  ' Main ground fill
  LINE (0, GROUNDY)-(SCREENW, SCREENH), 8, BF
  ' Top edge highlight
  LINE (0, GROUNDY)-(SCREENW, GROUNDY), 7

  ' Ground texture - rubble and pebbles
  groundOffset = INT(CameraX * 0.5) MOD 40
  FOR gx = 0 TO 8
    baseX = gx * 40 - groundOffset
    ' Small pebbles
    CIRCLE (baseX + 10, GROUNDY + 8), 2, 7
    PSET (baseX + 25, GROUNDY + 5), 7
    PSET (baseX + 35, GROUNDY + 12), 7
    ' Darker spots
    PSET (baseX + 18, GROUNDY + 15), 0
    PSET (baseX + 32, GROUNDY + 8), 0
  NEXT gx

  ' Occasional rubble chunks
  rubbleX = 50 - (INT(CameraX) MOD 160)
  IF rubbleX > -20 AND rubbleX < SCREENW THEN
    CIRCLE (rubbleX, GROUNDY + 4), 4, 7
    CIRCLE (rubbleX + 8, GROUNDY + 6), 3, 8
  END IF
  rubbleX2 = 180 - (INT(CameraX) MOD 160)
  IF rubbleX2 > -20 AND rubbleX2 < SCREENW THEN
    CIRCLE (rubbleX2, GROUNDY + 5), 3, 7
  END IF
RETURN

DrawPlatforms:
  FOR pi = 0 TO MAXPLATFORMS - 1
    IF PlatActive(pi) = 1 THEN
      platSX = PlatX(pi) - CameraX
      curW = PlatW(pi)
      curY = PlatY(pi)
      IF platSX > -curW AND platSX < SCREENW + 10 THEN
        IF PlatType(pi) = 1 THEN
          ' Metal platform with rivets
          LINE (platSX, curY)-(platSX + curW, curY + 6), 7, BF
          LINE (platSX, curY)-(platSX + curW, curY), 15
          LINE (platSX, curY + 6)-(platSX + curW, curY + 6), 8
          ' Rivets
          CIRCLE (platSX + 5, curY + 3), 2, 8
          CIRCLE (platSX + curW - 5, curY + 3), 2, 8
          IF curW > 40 THEN
            CIRCLE (platSX + curW / 2, curY + 3), 2, 8
          END IF
        ELSEIF PlatType(pi) = 2 THEN
          ' Wooden platform with planks
          LINE (platSX, curY)-(platSX + curW, curY + 5), 6, BF
          LINE (platSX, curY)-(platSX + curW, curY), 14
          ' Wood grain lines
          LINE (platSX + 3, curY + 2)-(platSX + 8, curY + 2), 8
          LINE (platSX + curW - 10, curY + 3)-(platSX + curW - 5, curY + 3), 8
          ' Plank dividers
          LINE (platSX + curW / 3, curY)-(platSX + curW / 3, curY + 5), 8
          LINE (platSX + curW * 2 / 3, curY)-(platSX + curW * 2 / 3, curY + 5), 8
        ELSE
          ' Stone platform with rough edges
          LINE (platSX, curY)-(platSX + curW, curY + 8), 8, BF
          LINE (platSX, curY)-(platSX + curW, curY), 7
          ' Rough texture
          PSET (platSX + 4, curY + 4), 7
          PSET (platSX + 12, curY + 6), 0
          PSET (platSX + curW - 8, curY + 3), 7
          PSET (platSX + curW - 15, curY + 5), 0
          ' Rounded corners effect
          PSET (platSX, curY), 0
          PSET (platSX + curW, curY), 0
          PSET (platSX, curY + 8), 0
          PSET (platSX + curW, curY + 8), 0
        END IF
      END IF
    END IF
  NEXT pi
RETURN

DrawCrates:
  FOR ci = 0 TO MAXCRATES - 1
    IF CrateActive(ci) = 1 THEN
      cx = CrateX(ci) - CameraX
      cy = CrateY(ci)
      IF cx > -20 AND cx < SCREENW + 20 THEN
        IF SpritesLoaded = 1 THEN
          IF CrateHealth(ci) = 1 THEN
            PUT (cx - 10, cy - 14), SprCrateDmg%, PSET
          ELSE
            PUT (cx - 10, cy - 14), SprCrate%, PSET
          END IF
        ELSE
          ' Wooden crate with detail
          LINE (cx - 10, cy - 14)-(cx + 10, cy), 6, BF
          LINE (cx - 10, cy - 14)-(cx + 10, cy), 14, B
          ' Wood planks
          LINE (cx - 10, cy - 7)-(cx + 10, cy - 7), 8
          LINE (cx, cy - 14)-(cx, cy), 8
          ' Corner rivets
          CIRCLE (cx - 8, cy - 12), 1, 8
          CIRCLE (cx + 8, cy - 12), 1, 8
          CIRCLE (cx - 8, cy - 2), 1, 8
          CIRCLE (cx + 8, cy - 2), 1, 8
          ' Question mark or exclamation
          COLOR 14
          LOCATE (cy - 9) / 8, (cx - 2) / 8
          PRINT "?"
          IF CrateHealth(ci) = 1 THEN
            ' Damage cracks
            LINE (cx - 6, cy - 12)-(cx + 4, cy - 4), 8
            LINE (cx - 4, cy - 10)-(cx + 6, cy - 2), 8
          END IF
        END IF
      END IF
    END IF
  NEXT ci
RETURN

DrawPOWs:
  FOR pw = 0 TO MAXPOWS - 1
    IF PowActive(pw) = 1 THEN
      px = PowX(pw) - CameraX
      py = PowY(pw)
      IF px > -20 AND px < SCREENW + 20 THEN
        IF PowRescued(pw) = 0 THEN
          IF SpritesLoaded = 1 THEN
            PUT (px - 7, py - 23), SprPOW%, PSET
          ELSE
            ' Prisoner with tied hands
            ' Body
            LINE (px - 3, py - 10)-(px + 3, py), 7, BF
            ' Round head
            CIRCLE (px, py - 14), 4, 14
            PAINT (px, py - 14), 14, 14
            ' Worried eyes
            PSET (px - 1, py - 15), 0
            PSET (px + 1, py - 15), 0
            ' Tied hands (waving for help)
            IF PowFrame(pw) MOD 20 < 10 THEN
              LINE (px + 3, py - 8)-(px + 8, py - 14), 14
              CIRCLE (px + 8, py - 14), 2, 14
            ELSE
              LINE (px + 3, py - 8)-(px + 7, py - 12), 14
              CIRCLE (px + 7, py - 12), 2, 14
            END IF
            ' Rope around body
            LINE (px - 3, py - 6)-(px + 3, py - 6), 6
          END IF
          ' Help indicator
          IF PowFrame(pw) MOD 30 < 20 THEN
            CIRCLE (px, py - 24), 4, 15
            COLOR 4
            LOCATE (py - 26) / 8, (px - 2) / 8
            PRINT "!"
          END IF
        ELSE
          PowX(pw) = PowX(pw) - 2
          IF SpritesLoaded = 1 THEN
            PUT (px - 7, py - 23), SprPOWFree%, PSET
          ELSE
            ' Running freed prisoner
            ' Body (green = free)
            LINE (px - 3, py - 10)-(px + 3, py), 10, BF
            ' Happy head
            CIRCLE (px, py - 14), 4, 14
            PAINT (px, py - 14), 14, 14
            ' Happy eyes
            PSET (px - 1, py - 15), 0
            PSET (px + 1, py - 15), 0
            ' Smile
            LINE (px - 1, py - 13)-(px + 1, py - 12), 0
            ' Running arms
            IF PowFrame(pw) MOD 10 < 5 THEN
              LINE (px - 3, py - 8)-(px - 7, py - 6), 14
              LINE (px + 3, py - 8)-(px + 7, py - 10), 14
            ELSE
              LINE (px - 3, py - 8)-(px - 7, py - 10), 14
              LINE (px + 3, py - 8)-(px + 7, py - 6), 14
            END IF
          END IF
        END IF
      END IF
      PowFrame(pw) = PowFrame(pw) + 1
    END IF
  NEXT pw
RETURN

DrawPickups:
  FOR pk = 0 TO MAXPICKUPS - 1
    IF PickupActive(pk) = 1 THEN
      px = PickupX(pk) - CameraX
      py = PickupY(pk)
      IF px > -15 AND px < SCREENW + 15 THEN
        IF SpritesLoaded = 1 THEN
          IF PickupType(pk) = 1 THEN
            PUT (px - 8, py - 10), SprPickupH%, PSET
          ELSEIF PickupType(pk) = 2 THEN
            PUT (px - 8, py - 10), SprPickupR%, PSET
          ELSE
            PUT (px - 8, py - 10), SprPickupPlus%, PSET
          END IF
        ELSE
          ' Floating animation
          floatY = py - 2 + (FrameCount MOD 10) / 5

          IF PickupType(pk) = 1 THEN
            ' Heavy weapon pickup (red box)
            CIRCLE (px, floatY - 4), 8, 4
            PAINT (px, floatY - 4), 4, 4
            CIRCLE (px, floatY - 4), 8, 12
            ' H letter
            LINE (px - 4, floatY - 7)-(px - 4, floatY - 1), 15
            LINE (px + 4, floatY - 7)-(px + 4, floatY - 1), 15
            LINE (px - 4, floatY - 4)-(px + 4, floatY - 4), 15
          ELSEIF PickupType(pk) = 2 THEN
            ' Rapid fire pickup (blue box)
            CIRCLE (px, floatY - 4), 8, 1
            PAINT (px, floatY - 4), 1, 1
            CIRCLE (px, floatY - 4), 8, 9
            ' R letter
            LINE (px - 4, floatY - 7)-(px - 4, floatY - 1), 15
            LINE (px - 4, floatY - 7)-(px + 2, floatY - 7), 15
            LINE (px + 2, floatY - 7)-(px + 2, floatY - 4), 15
            LINE (px - 4, floatY - 4)-(px + 2, floatY - 4), 15
            LINE (px, floatY - 4)-(px + 4, floatY - 1), 15
          ELSE
            ' Health pickup (cross)
            CIRCLE (px, floatY - 4), 8, 4
            PAINT (px, floatY - 4), 4, 4
            CIRCLE (px, floatY - 4), 8, 12
            ' White cross
            LINE (px - 5, floatY - 5)-(px + 5, floatY - 3), 15, BF
            LINE (px - 1, floatY - 8)-(px + 1, floatY), 15, BF
          END IF

          ' Sparkle effect
          IF FrameCount MOD 20 < 10 THEN
            PSET (px - 6, floatY - 8), 15
            PSET (px + 6, floatY), 15
          END IF
        END IF
      END IF
    END IF
  NEXT pk
RETURN

DrawPlayer:
  px = INT(PlayerX - CameraX)
  py = INT(PlayerY)

  IF px < -20 OR px > SCREENW + 20 THEN RETURN

  IF PlayerHit = 1 THEN
    IF PlayerHitTimer MOD 4 < 2 THEN RETURN
  END IF

  ' Optimized: Use sprites if loaded
  IF SpritesLoaded = 1 THEN
    ' Select sprite based on state
    IF PlayerOnGround = 0 THEN
      IF PlayerDir > 0 THEN
        PUT (px - 10, py - 23), SprPlayerJR%, PSET
      ELSE
        PUT (px - 10, py - 23), SprPlayerJL%, PSET
      END IF
    ELSEIF PlayerCrouching = 1 THEN
      IF PlayerDir > 0 THEN
        PUT (px - 10, py - 23), SprPlayerCR%, PSET
      ELSE
        PUT (px - 10, py - 23), SprPlayerCL%, PSET
      END IF
    ELSE
      walkFrame = (PlayerFrame \ 5) MOD 4
      IF PlayerDir > 0 THEN
        IF walkFrame = 0 THEN
          PUT (px - 10, py - 23), SprPlayer0%, PSET
        ELSEIF walkFrame = 1 THEN
          PUT (px - 10, py - 23), SprPlayer1%, PSET
        ELSEIF walkFrame = 2 THEN
          PUT (px - 10, py - 23), SprPlayer2%, PSET
        ELSE
          PUT (px - 10, py - 23), SprPlayer3%, PSET
        END IF
      ELSE
        IF walkFrame = 0 THEN
          PUT (px - 10, py - 23), SprPlayer4%, PSET
        ELSEIF walkFrame = 1 THEN
          PUT (px - 10, py - 23), SprPlayer5%, PSET
        ELSEIF walkFrame = 2 THEN
          PUT (px - 10, py - 23), SprPlayer6%, PSET
        ELSE
          PUT (px - 10, py - 23), SprPlayer7%, PSET
        END IF
      END IF
    END IF
  ELSE
    ' Fallback drawing - detailed soldier with circles

    ' Shadow under feet
    LINE (px - 6, py + 9)-(px + 6, py + 10), 8

    ' Body (vest/torso)
    LINE (px - 5, py - 10)-(px + 5, py), 10, BF
    ' Chest detail
    LINE (px - 3, py - 8)-(px + 3, py - 4), 2, BF

    ' Head - round with helmet
    CIRCLE (px, py - 15), 5, 14
    PAINT (px, py - 15), 14, 14
    ' Helmet top
    CIRCLE (px, py - 18), 6, 2
    LINE (px - 6, py - 18)-(px + 6, py - 14), 2, BF
    ' Face visor
    CIRCLE (px + 2, py - 15), 2, 0
    PSET (px + 2, py - 15), 15

    ' Arms and gun
    IF PlayerDir > 0 THEN
      ' Right arm
      CIRCLE (px + 6, py - 6), 3, 14
      LINE (px + 6, py - 8)-(px + 12, py - 7), 14
      ' Gun
      LINE (px + 10, py - 9)-(px + 18, py - 6), 7, BF
      CIRCLE (px + 18, py - 7), 2, 8
      IF PlayerShooting > 0 THEN
        ' Muzzle flash with circles
        CIRCLE (px + 21, py - 7), 4, 14
        CIRCLE (px + 23, py - 7), 2, 15
      END IF
    ELSE
      ' Left arm
      CIRCLE (px - 6, py - 6), 3, 14
      LINE (px - 12, py - 7)-(px - 6, py - 8), 14
      ' Gun
      LINE (px - 18, py - 9)-(px - 10, py - 6), 7, BF
      CIRCLE (px - 18, py - 7), 2, 8
      IF PlayerShooting > 0 THEN
        ' Muzzle flash with circles
        CIRCLE (px - 21, py - 7), 4, 14
        CIRCLE (px - 23, py - 7), 2, 15
      END IF
    END IF

    PlayerFrame = PlayerFrame + 1
    IF PlayerFrame > 20 THEN PlayerFrame = 0

    ' Legs with boots
    IF PlayerOnGround = 0 THEN
      ' Jumping pose
      LINE (px - 4, py)-(px - 8, py + 4), 10
      LINE (px + 4, py)-(px + 8, py + 4), 10
      CIRCLE (px - 8, py + 5), 2, 8
      CIRCLE (px + 8, py + 5), 2, 8
    ELSEIF PlayerFrame < 10 THEN
      ' Walking frame 1
      LINE (px - 3, py)-(px - 5, py + 6), 10
      LINE (px + 3, py)-(px + 6, py + 6), 10
      CIRCLE (px - 5, py + 7), 2, 8
      CIRCLE (px + 6, py + 7), 2, 8
    ELSE
      ' Walking frame 2
      LINE (px - 3, py)-(px - 6, py + 6), 10
      LINE (px + 3, py)-(px + 5, py + 6), 10
      CIRCLE (px - 6, py + 7), 2, 8
      CIRCLE (px + 5, py + 7), 2, 8
    END IF
  END IF

  ' Muzzle flash with circular effect (always drawn when shooting)
  IF PlayerShooting > 0 THEN
    IF SpritesLoaded = 1 THEN
      IF PlayerDir > 0 THEN
        CIRCLE (px + 20, py - 7), 5, 14
        CIRCLE (px + 22, py - 7), 3, 15
      ELSE
        CIRCLE (px - 20, py - 7), 5, 14
        CIRCLE (px - 22, py - 7), 3, 15
      END IF
    END IF
    PlayerShooting = PlayerShooting - 1
  END IF

  PlayerFrame = PlayerFrame + 1
  IF PlayerFrame > 20 THEN PlayerFrame = 0
RETURN

DrawBullets:
  FOR i = 0 TO MAXBULLETS - 1
    IF BulletActive(i) = 1 THEN
      bx = INT(BulletX(i) - CameraX)
      by = INT(BulletY(i))
      IF bx >= -10 AND bx < SCREENW + 10 AND by >= -10 AND by < SCREENH + 10 THEN
        IF BulletOwner(i) = 0 THEN
          ' Player bullet - yellow/white tracer
          LINE (bx - 5, by)-(bx + 3, by), 14
          LINE (bx - 4, by - 1)-(bx + 2, by - 1), 6
          CIRCLE (bx + 3, by), 2, 15
          PSET (bx + 3, by), 15
        ELSE
          ' Enemy bullet - red tracer
          LINE (bx - 4, by)-(bx + 2, by), 4
          CIRCLE (bx + 2, by), 2, 12
          PSET (bx + 2, by), 15
        END IF
      END IF
    END IF
  NEXT i
RETURN

DrawEnemies:
  FOR i = 0 TO MAXENEMIES - 1
    IF EnemyActive(i) = 1 THEN
      ex = INT(EnemyX(i) - CameraX)
      ey = INT(EnemyY(i))

      IF ex >= -30 AND ex < SCREENW + 30 THEN
        EnemyFrame(i) = EnemyFrame(i) + 1
        IF EnemyFrame(i) > 20 THEN EnemyFrame(i) = 0

        IF EnemyType(i) = 1 THEN
          ' Soldier
          IF SpritesLoaded = 1 THEN
            IF EnemyDir(i) > 0 THEN
              PUT (ex - 6, ey - 19), SprSoldierR%, PSET
            ELSE
              PUT (ex - 6, ey - 19), SprSoldierL%, PSET
            END IF
          ELSE
            ' Detailed soldier with circles
            ' Body (red uniform)
            LINE (ex - 4, ey - 10)-(ex + 4, ey), 4, BF
            ' Round head
            CIRCLE (ex, ey - 14), 4, 14
            PAINT (ex, ey - 14), 14, 14
            ' Red beret
            CIRCLE (ex, ey - 17), 5, 4
            LINE (ex - 5, ey - 17)-(ex + 5, ey - 14), 4, BF
            ' Eye
            PSET (ex + 1, ey - 14), 0
            ' Arms and gun
            IF EnemyDir(i) > 0 THEN
              CIRCLE (ex + 5, ey - 6), 2, 14
              LINE (ex + 5, ey - 7)-(ex + 10, ey - 6), 7
              CIRCLE (ex + 10, ey - 6), 2, 8
            ELSE
              CIRCLE (ex - 5, ey - 6), 2, 14
              LINE (ex - 10, ey - 6)-(ex - 5, ey - 7), 7
              CIRCLE (ex - 10, ey - 6), 2, 8
            END IF
            ' Legs with boots
            LINE (ex - 2, ey)-(ex - 4, ey + 5), 4
            LINE (ex + 2, ey)-(ex + 4, ey + 5), 4
            CIRCLE (ex - 4, ey + 6), 2, 8
            CIRCLE (ex + 4, ey + 6), 2, 8
          END IF

        ELSEIF EnemyType(i) = 2 THEN
          ' Tank with circular wheels
          IF SpritesLoaded = 1 THEN
            IF EnemyDir(i) > 0 THEN
              PUT (ex - 27, ey - 24), SprTankR%, PSET
            ELSE
              PUT (ex - 27, ey - 24), SprTankL%, PSET
            END IF
          ELSE
            ' Tank treads with wheels
            LINE (ex - 18, ey + 2)-(ex + 18, ey + 6), 8, BF
            ' Wheels (circles)
            CIRCLE (ex - 14, ey + 3), 4, 7
            CIRCLE (ex - 14, ey + 3), 2, 8
            CIRCLE (ex, ey + 3), 4, 7
            CIRCLE (ex, ey + 3), 2, 8
            CIRCLE (ex + 14, ey + 3), 4, 7
            CIRCLE (ex + 14, ey + 3), 2, 8
            ' Hull body
            LINE (ex - 15, ey - 6)-(ex + 15, ey + 2), 7, BF
            LINE (ex - 12, ey - 4)-(ex + 12, ey), 8, BF
            ' Viewport
            CIRCLE (ex + 8, ey - 2), 3, 11
            ' Turret (rounded)
            CIRCLE (ex - 2, ey - 10), 8, 7
            LINE (ex - 10, ey - 10)-(ex + 6, ey - 6), 7, BF
            ' Turret hatch
            CIRCLE (ex - 2, ey - 14), 3, 8
            ' Cannon
            IF EnemyDir(i) > 0 THEN
              LINE (ex + 5, ey - 11)-(ex + 25, ey - 9), 8, BF
              CIRCLE (ex + 25, ey - 10), 2, 7
            ELSE
              LINE (ex - 25, ey - 11)-(ex - 5, ey - 9), 8, BF
              CIRCLE (ex - 25, ey - 10), 2, 7
            END IF
          END IF

        ELSEIF EnemyType(i) = 3 THEN
          ' Helicopter with detailed design
          IF SpritesLoaded = 1 THEN
            ' Use direction to choose sprite (not frame-based animation)
            IF EnemyDir(i) = 1 THEN
              PUT (ex - 27, ey - 12), SprHeliR%, PSET
            ELSE
              PUT (ex - 27, ey - 12), SprHeliL%, PSET
            END IF
          ELSE
            ' Main body (rounded)
            CIRCLE (ex - 5, ey), 12, 7
            LINE (ex - 17, ey - 8)-(ex + 7, ey + 8), 7, BF
            ' Cockpit window (round)
            CIRCLE (ex + 5, ey - 2), 6, 11
            PAINT (ex + 5, ey - 2), 11, 11
            CIRCLE (ex + 5, ey - 2), 6, 9
            ' Tail boom
            LINE (ex - 17, ey - 3)-(ex - 35, ey), 8, BF
            ' Tail rotor
            CIRCLE (ex - 35, ey - 1), 4, 7
            IF EnemyFrame(i) MOD 4 < 2 THEN
              LINE (ex - 35, ey - 6)-(ex - 35, ey + 4), 15
            ELSE
              LINE (ex - 38, ey - 1)-(ex - 32, ey - 1), 15
            END IF
            ' Main rotor with animation
            CIRCLE (ex - 5, ey - 10), 3, 8
            IF EnemyFrame(i) MOD 4 < 2 THEN
              LINE (ex - 35, ey - 10)-(ex + 25, ey - 10), 15
              LINE (ex - 34, ey - 11)-(ex + 24, ey - 9), 7
            ELSE
              LINE (ex - 30, ey - 12)-(ex + 20, ey - 8), 15
              LINE (ex - 20, ey - 8)-(ex + 10, ey - 12), 15
            END IF
            ' Landing skid
            LINE (ex - 10, ey + 10)-(ex + 5, ey + 10), 8
            LINE (ex - 8, ey + 8)-(ex - 8, ey + 10), 8
            LINE (ex + 3, ey + 8)-(ex + 3, ey + 10), 8
          END IF

        ELSEIF EnemyType(i) = 4 THEN
          ' Turret with rounded dome
          IF SpritesLoaded = 1 THEN
            IF EnemyDir(i) > 0 THEN
              PUT (ex - 16, ey - 20), SprTurretR%, PSET
            ELSE
              PUT (ex - 16, ey - 20), SprTurretL%, PSET
            END IF
          ELSE
            ' Base platform
            LINE (ex - 14, ey)-(ex + 14, ey + 6), 8, BF
            LINE (ex - 12, ey + 1)-(ex + 12, ey + 5), 7, BF
            ' Rounded dome
            CIRCLE (ex, ey - 6), 10, 7
            LINE (ex - 10, ey - 6)-(ex + 10, ey), 7, BF
            ' Dome highlight
            CIRCLE (ex - 3, ey - 10), 3, 15
            ' Gun barrel
            IF EnemyDir(i) > 0 THEN
              LINE (ex + 8, ey - 8)-(ex + 22, ey - 6), 8, BF
              CIRCLE (ex + 22, ey - 7), 2, 7
            ELSE
              LINE (ex - 22, ey - 8)-(ex - 8, ey - 6), 8, BF
              CIRCLE (ex - 22, ey - 7), 2, 7
            END IF
            ' Sensor/antenna
            LINE (ex, ey - 16)-(ex, ey - 12), 7
            CIRCLE (ex, ey - 18), 2, 4
            IF EnemyFrame(i) MOD 10 < 5 THEN
              ' Blinking light
              CIRCLE (ex, ey - 18), 3, 12
            END IF
          END IF

        ELSEIF EnemyType(i) = 5 THEN
          ' Jetpack soldier with detailed jetpack
          IF SpritesLoaded = 1 THEN
            IF EnemyDir(i) > 0 THEN
              PUT (ex - 9, ey - 18), SprJetpackR%, PSET
            ELSE
              PUT (ex - 9, ey - 18), SprJetpackL%, PSET
            END IF
          ELSE
            ' Jetpack unit (cylindrical tanks)
            CIRCLE (ex - 6, ey - 4), 4, 8
            CIRCLE (ex - 6, ey + 2), 4, 8
            LINE (ex - 10, ey - 4)-(ex - 2, ey + 2), 8, BF
            ' Flame exhaust (animated)
            IF EnemyFrame(i) MOD 6 < 3 THEN
              CIRCLE (ex - 6, ey + 8), 3, 14
              CIRCLE (ex - 6, ey + 10), 2, 12
            ELSE
              CIRCLE (ex - 6, ey + 7), 4, 14
              CIRCLE (ex - 6, ey + 9), 2, 15
            END IF
            ' Soldier body
            LINE (ex - 2, ey - 8)-(ex + 5, ey + 2), 4, BF
            ' Round head with helmet
            CIRCLE (ex + 1, ey - 12), 4, 14
            PAINT (ex + 1, ey - 12), 14, 14
            ' Helmet
            CIRCLE (ex + 1, ey - 15), 5, 8
            LINE (ex - 4, ey - 15)-(ex + 6, ey - 12), 8, BF
            ' Visor
            CIRCLE (ex + 2, ey - 13), 2, 11
            ' Arms and gun
            IF EnemyDir(i) > 0 THEN
              CIRCLE (ex + 6, ey - 4), 2, 14
              LINE (ex + 6, ey - 5)-(ex + 12, ey - 4), 7
              CIRCLE (ex + 12, ey - 4), 2, 8
            ELSE
              CIRCLE (ex - 2, ey - 4), 2, 14
              LINE (ex - 12, ey - 4)-(ex - 2, ey - 5), 7
              CIRCLE (ex - 12, ey - 4), 2, 8
            END IF
            ' Legs (dangling)
            LINE (ex, ey + 2)-(ex - 2, ey + 8), 4
            LINE (ex + 4, ey + 2)-(ex + 6, ey + 8), 4
          END IF
        END IF
      END IF
    END IF
  NEXT i

  IF BossActive = 1 THEN
    GOSUB DrawBoss
  END IF
RETURN

DrawBoss:
  bx = INT(BossX - CameraX)
  by = INT(BossY)

  IF bx < -80 OR bx > SCREENW + 80 THEN RETURN

  BossFrame = BossFrame + 1
  IF BossFrame > 30 THEN BossFrame = 0

  ' Shadow under mech
  LINE (bx - 45, by + 36)-(bx + 45, by + 38), 8, BF

  ' Feet (rounded)
  LINE (bx - 45, by + 28)-(bx - 25, by + 35), 7, BF
  CIRCLE (bx - 45, by + 31), 4, 8
  CIRCLE (bx - 25, by + 31), 4, 8
  LINE (bx + 25, by + 28)-(bx + 45, by + 35), 7, BF
  CIRCLE (bx + 45, by + 31), 4, 8
  CIRCLE (bx + 25, by + 31), 4, 8

  ' Legs with joint circles
  LINE (bx - 35, by + 10)-(bx - 30, by + 28), 7, BF
  LINE (bx + 30, by + 10)-(bx + 35, by + 28), 7, BF
  ' Knee joints
  CIRCLE (bx - 32, by + 20), 5, 8
  CIRCLE (bx - 32, by + 20), 3, 7
  CIRCLE (bx + 32, by + 20), 5, 8
  CIRCLE (bx + 32, by + 20), 3, 7
  ' Hip joints
  CIRCLE (bx - 32, by + 10), 6, 8
  CIRCLE (bx + 32, by + 10), 6, 8

  ' Main body (armored torso)
  LINE (bx - 40, by - 25)-(bx + 40, by + 10), 7, BF
  LINE (bx - 38, by - 23)-(bx + 38, by + 8), 8, BF
  ' Chest vents
  LINE (bx - 15, by - 10)-(bx - 5, by + 5), 0, BF
  LINE (bx + 5, by - 10)-(bx + 15, by + 5), 0, BF
  ' Central reactor glow
  CIRCLE (bx, by - 5), 8, 11
  PAINT (bx, by - 5), 11, 11
  CIRCLE (bx, by - 5), 5, 9
  IF BossFrame MOD 10 < 5 THEN
    CIRCLE (bx, by - 5), 10, 15
  END IF

  ' Shoulder joints
  CIRCLE (bx - 42, by - 18), 8, 8
  CIRCLE (bx - 42, by - 18), 5, 7
  CIRCLE (bx + 42, by - 18), 8, 8
  CIRCLE (bx + 42, by - 18), 5, 7

  ' Arms/Cannons
  LINE (bx - 65, by - 22)-(bx - 42, by - 14), 7, BF
  LINE (bx + 42, by - 22)-(bx + 65, by - 14), 7, BF

  ' Cannon barrels (round tips)
  CIRCLE (bx - 68, by - 18), 5, 8
  CIRCLE (bx - 68, by - 18), 3, 0
  CIRCLE (bx + 68, by - 18), 5, 8
  CIRCLE (bx + 68, by - 18), 3, 0

  ' Cannon flash (animated)
  IF BossFrame < 15 THEN
    CIRCLE (bx - 72, by - 18), 6, 14
    CIRCLE (bx - 74, by - 18), 4, 15
    CIRCLE (bx + 72, by - 18), 6, 14
    CIRCLE (bx + 74, by - 18), 4, 15
  END IF

  ' Cockpit (rounded dome)
  CIRCLE (bx, by - 38), 18, 4
  LINE (bx - 18, by - 38)-(bx + 18, by - 28), 4, BF
  ' Cockpit window (curved glass)
  CIRCLE (bx, by - 40), 12, 11
  PAINT (bx, by - 40), 11, 11
  CIRCLE (bx, by - 40), 12, 9
  ' Cockpit highlight
  CIRCLE (bx - 4, by - 44), 4, 15
  ' Antenna
  LINE (bx, by - 52)-(bx, by - 48), 7
  CIRCLE (bx, by - 54), 2, 4
  IF BossFrame MOD 8 < 4 THEN
    CIRCLE (bx, by - 54), 3, 12
  END IF

  ' Health bar with frame
  LINE (bx - 42, by - 62)-(bx + 42, by - 56), 8, BF
  LINE (bx - 41, by - 61)-(bx + 41, by - 57), 0, BF
  healthWidth = (BossHealth / (20 + Level * 10)) * 80
  IF healthWidth > 0 THEN
    LINE (bx - 40, by - 60)-(bx - 40 + healthWidth, by - 58), 4, BF
  END IF
  ' Health bar glow when low
  IF BossHealth < 10 THEN
    IF BossFrame MOD 6 < 3 THEN
      LINE (bx - 42, by - 62)-(bx + 42, by - 56), 12, B
    END IF
  END IF
RETURN

DrawExplosions:
  FOR i = 0 TO MAXEXPLOSIONS - 1
    IF ExpActive(i) = 1 THEN
      ex = INT(ExpX(i) - CameraX)
      ey = INT(ExpY(i))

      IF ex >= -30 AND ex < SCREENW + 30 THEN
        radius = ExpFrame(i) * 2 + 2

        IF ExpFrame(i) < 5 THEN
          ' Initial bright flash - white core with yellow ring
          CIRCLE (ex, ey), radius, 15
          PAINT (ex, ey), 15, 15
          CIRCLE (ex, ey), radius + 2, 14
          ' Spark particles
          PSET (ex - radius - 3, ey - 2), 15
          PSET (ex + radius + 3, ey + 1), 15
          PSET (ex + 2, ey - radius - 2), 15
          PSET (ex - 1, ey + radius + 3), 15
        ELSEIF ExpFrame(i) < 10 THEN
          ' Expanding fireball - yellow with orange ring
          CIRCLE (ex, ey), radius, 14
          PAINT (ex, ey), 14, 14
          CIRCLE (ex, ey), radius - 3, 12
          CIRCLE (ex, ey), radius + 2, 6
          ' Smoke wisps
          CIRCLE (ex - 4, ey - radius), 3, 8
          CIRCLE (ex + 5, ey - radius - 2), 2, 7
        ELSE
          ' Fading smoke - red to dark
          CIRCLE (ex, ey), radius, 4
          PAINT (ex, ey), 4, 4
          CIRCLE (ex, ey), radius - 4, 8
          ' Smoke clouds rising
          CIRCLE (ex - 3, ey - radius - 3), 4, 8
          CIRCLE (ex + 4, ey - radius - 5), 3, 7
          CIRCLE (ex, ey - radius - 8), 2, 7
        END IF

        ExpFrame(i) = ExpFrame(i) + 1
        IF ExpFrame(i) > 15 THEN
          ExpActive(i) = 0
        END IF
      END IF
    END IF
  NEXT i
RETURN

DrawHUD:
  ' Score display with box
  LINE (2, 2)-(70, 14), 8, BF
  LINE (2, 2)-(70, 14), 7, B
  COLOR 15
  LOCATE 1, 1
  PRINT " SCORE"
  COLOR 14
  LOCATE 2, 1
  PRINT Score

  ' Zone display
  LINE (SCREENW - 50, 2)-(SCREENW - 2, 14), 8, BF
  LINE (SCREENW - 50, 2)-(SCREENW - 2, 14), 7, B
  COLOR 15
  LOCATE 1, 35
  PRINT "ZONE"
  COLOR 10
  LOCATE 2, 36
  PRINT Level

  ' Weapon indicator with icon
  LINE (220, 2)-(250, 14), 8, BF
  LINE (220, 2)-(250, 14), 7, B
  IF PlayerWeapon = 1 THEN
    ' Pistol icon
    LINE (228, 5)-(238, 7), 7, BF
    LINE (230, 7)-(232, 11), 7, BF
    CIRCLE (226, 6), 2, 14
  ELSEIF PlayerWeapon = 2 THEN
    ' Heavy gun icon
    LINE (224, 5)-(244, 8), 7, BF
    LINE (230, 8)-(234, 11), 7, BF
    CIRCLE (224, 7), 3, 14
    CIRCLE (244, 7), 2, 14
  ELSEIF PlayerWeapon = 3 THEN
    ' Rapid fire icon
    LINE (226, 4)-(242, 10), 7, BF
    LINE (232, 10)-(236, 12), 7, BF
    ' Multiple barrels
    CIRCLE (244, 5), 1, 8
    CIRCLE (244, 7), 1, 8
    CIRCLE (244, 9), 1, 8
  END IF

  ' Lives display with soldier icons
  FOR i = 1 TO PlayerLives
    lx = 72 + (i * 14)
    ' Mini soldier icon
    CIRCLE (lx, 5), 3, 10
    PAINT (lx, 5), 10, 10
    LINE (lx - 2, 8)-(lx + 2, 13), 10, BF
  NEXT i

  ' Progress bar with markers
  LINE (100, 4)-(200, 12), 8, BF
  LINE (100, 4)-(200, 12), 7, B
  ' Start marker
  CIRCLE (102, 8), 2, 10
  ' End marker (flag)
  LINE (198, 5)-(198, 11), 15
  LINE (198, 5)-(195, 7), 4, BF
  ' Progress fill
  progress = PlayerX / LEVELWIDTH
  IF progress > 1 THEN progress = 1
  progressWidth = progress * 92
  IF progressWidth > 0 THEN
    LINE (104, 6)-(104 + progressWidth, 10), 10, BF
  END IF
  ' Player position marker
  IF progressWidth > 2 THEN
    CIRCLE (104 + progressWidth, 8), 2, 15
  END IF

  ' Boss warning with flashing effect
  IF BossActive = 1 THEN
    IF FrameCount MOD 20 < 10 THEN
      LINE (110, 20)-(210, 34), 4, BF
      LINE (110, 20)-(210, 34), 12, B
      COLOR 15
      LOCATE 3, 15
      PRINT "!! BOSS !!"
    ELSE
      LINE (110, 20)-(210, 34), 0, BF
      LINE (110, 20)-(210, 34), 4, B
      COLOR 4
      LOCATE 3, 15
      PRINT "!! BOSS !!"
    END IF
  END IF
RETURN

' ============================================
' INPUT HANDLING
' ============================================

HandleInput:
  k$ = INKEY$

  PlayerAimDir = 0
  PlayerCrouching = 0

  ' ESC = Quit
  IF KEYDOWN(1) THEN
    GameOver = 1
    RETURN
  END IF

  ' M = Toggle sound
  IF k$ = "m" OR k$ = "M" THEN
    SoundOn = 1 - SoundOn
  END IF

  ' Z = Switch weapon
  IF k$ = "z" OR k$ = "Z" THEN
    PlayerWeapon = PlayerWeapon + 1
    IF PlayerWeapon > 3 THEN PlayerWeapon = 1
  END IF

  ' NEW CONTROLS: Arrow keys for movement AND aiming

  ' Left Arrow (75) = move left
  IF KEYDOWN(75) THEN
    PlayerX = PlayerX - PLAYERSPEED
    PlayerDir = -1
    IF PlayerX < 20 THEN PlayerX = 20
  END IF

  ' Right Arrow (77) = move right
  IF KEYDOWN(77) THEN
    PlayerX = PlayerX + PLAYERSPEED
    PlayerDir = 1
    IF PlayerX > LEVELWIDTH - 20 THEN PlayerX = LEVELWIDTH - 20
  END IF

  ' Up Arrow (72) = aim up (for shooting)
  IF KEYDOWN(72) THEN
    PlayerAimDir = -1
  END IF

  ' Down Arrow (80) = crouch + aim down
  IF KEYDOWN(80) THEN
    PlayerCrouching = 1
    PlayerAimDir = 1
  END IF

  ' S key (31) = Jump
  IF KEYDOWN(31) THEN
    IF PlayerOnGround = 1 AND JumpLock = 0 THEN
      PlayerVelY = JUMPVEL
      PlayerOnGround = 0
      JumpLock = 1
      GOSUB PlayJumpSound
    END IF
  ELSE
    JumpLock = 0
  END IF

  ' A key (30) = Shoot
  IF KEYDOWN(30) THEN
    IF ShootCooldown = 0 THEN
      GOSUB FireBullet
      ShootCooldown = 5
    END IF
  END IF

  IF ShootCooldown > 0 THEN ShootCooldown = ShootCooldown - 1
RETURN

FireBullet:
  FOR i = 0 TO MAXBULLETS - 1
    IF BulletActive(i) = 0 THEN
      BulletActive(i) = 1
      BulletOwner(i) = 0

      ' Check if left or right arrow is held for diagonal shots
      aimX = 0
      IF KEYDOWN(75) THEN aimX = -1
      IF KEYDOWN(77) THEN aimX = 1
      IF aimX = 0 THEN aimX = PlayerDir

      ' Determine bullet direction based on arrow keys
      IF PlayerAimDir = -1 THEN
        ' Aiming UP
        IF aimX <> 0 AND aimX <> PlayerDir THEN
          ' Diagonal up-back (opposite direction)
          BulletX(i) = PlayerX + aimX * 10
          BulletY(i) = PlayerY - 15
          BulletVelX(i) = aimX * BULLETSPEED * 0.7
          BulletVelY(i) = -BULLETSPEED * 0.7
        ELSEIF aimX <> 0 THEN
          ' Diagonal up-forward
          BulletX(i) = PlayerX + aimX * 10
          BulletY(i) = PlayerY - 15
          BulletVelX(i) = aimX * BULLETSPEED * 0.7
          BulletVelY(i) = -BULLETSPEED * 0.7
        ELSE
          ' Straight up
          BulletX(i) = PlayerX
          BulletY(i) = PlayerY - 20
          BulletVelX(i) = 0
          BulletVelY(i) = -BULLETSPEED
        END IF
      ELSEIF PlayerAimDir = 1 AND PlayerOnGround = 0 THEN
        ' Aiming DOWN while in air
        IF aimX <> 0 THEN
          ' Diagonal down
          BulletX(i) = PlayerX + aimX * 10
          BulletY(i) = PlayerY + 5
          BulletVelX(i) = aimX * BULLETSPEED * 0.7
          BulletVelY(i) = BULLETSPEED * 0.7
        ELSE
          ' Straight down
          BulletX(i) = PlayerX
          BulletY(i) = PlayerY + 5
          BulletVelX(i) = 0
          BulletVelY(i) = BULLETSPEED
        END IF
      ELSEIF PlayerAimDir = 1 AND PlayerOnGround = 1 THEN
        ' Aiming DOWN while crouching on ground (diagonal forward-down)
        BulletX(i) = PlayerX + aimX * 10
        BulletY(i) = PlayerY - 3
        BulletVelX(i) = aimX * BULLETSPEED * 0.7
        BulletVelY(i) = BULLETSPEED * 0.5
      ELSE
        ' No vertical aim - shoot horizontally
        BulletX(i) = PlayerX + aimX * 15
        BulletY(i) = PlayerY - 7
        BulletVelX(i) = aimX * BULLETSPEED
        BulletVelY(i) = 0
      END IF

      IF PlayerWeapon = 2 THEN
        BulletVelY(i) = BulletVelY(i) - 2
      ELSEIF PlayerWeapon = 3 THEN
        BulletVelX(i) = BulletVelX(i) * 0.7
        BulletVelY(i) = BulletVelY(i) * 0.7
      END IF

      PlayerShooting = 5
      GOSUB PlayShootSound
      EXIT FOR
    END IF
  NEXT i
RETURN

' ============================================
' UPDATE SUBROUTINES
' ============================================

UpdatePlayer:
  PlayerVelY = PlayerVelY + GRAVITY
  PlayerY = PlayerY + PlayerVelY

  IF PlayerY >= GROUNDY - 8 THEN
    PlayerY = GROUNDY - 8
    PlayerVelY = 0
    PlayerOnGround = 1
  END IF

  IF PlayerHit = 1 THEN
    PlayerHitTimer = PlayerHitTimer + 1
    IF PlayerHitTimer > 60 THEN
      PlayerHit = 0
      PlayerHitTimer = 0
    END IF
  END IF
RETURN

UpdateBullets:
  FOR i = 0 TO MAXBULLETS - 1
    IF BulletActive(i) = 1 THEN
      BulletX(i) = BulletX(i) + BulletVelX(i)
      BulletY(i) = BulletY(i) + BulletVelY(i)

      IF BulletX(i) < CameraX - 20 OR BulletX(i) > CameraX + SCREENW + 20 THEN
        BulletActive(i) = 0
      END IF
      IF BulletY(i) < -10 OR BulletY(i) > SCREENH + 10 THEN
        BulletActive(i) = 0
      END IF
    END IF
  NEXT i
RETURN

UpdateEnemies:
  FOR i = 0 TO MAXENEMIES - 1
    IF EnemyActive(i) = 1 THEN
      IF EnemyType(i) = 1 THEN
        IF EnemyX(i) > PlayerX + 50 THEN
          EnemyX(i) = EnemyX(i) - ENEMYSPEED
          EnemyDir(i) = -1
        ELSEIF EnemyX(i) < PlayerX - 50 THEN
          EnemyX(i) = EnemyX(i) + ENEMYSPEED
          EnemyDir(i) = 1
        END IF

      ELSEIF EnemyType(i) = 2 THEN
        IF EnemyX(i) > PlayerX + 80 THEN
          EnemyX(i) = EnemyX(i) - ENEMYSPEED * 0.5
          EnemyDir(i) = -1
        ELSEIF EnemyX(i) < PlayerX - 80 THEN
          EnemyX(i) = EnemyX(i) + ENEMYSPEED * 0.5
          EnemyDir(i) = 1
        END IF

      ELSEIF EnemyType(i) = 3 THEN
        EnemyFrame(i) = EnemyFrame(i) + 1
        IF EnemyFrame(i) > 60 THEN EnemyFrame(i) = 0
        EnemyY(i) = 50 + SIN(EnemyFrame(i) * 0.1) * 20
        IF EnemyX(i) > PlayerX + 30 THEN
          EnemyX(i) = EnemyX(i) - ENEMYSPEED * 1.5
          EnemyDir(i) = -1
        ELSEIF EnemyX(i) < PlayerX - 30 THEN
          EnemyX(i) = EnemyX(i) + ENEMYSPEED * 1.5
          EnemyDir(i) = 1
        END IF

      ELSEIF EnemyType(i) = 4 THEN
        IF PlayerX < EnemyX(i) THEN
          EnemyDir(i) = -1
        ELSE
          EnemyDir(i) = 1
        END IF

      ELSEIF EnemyType(i) = 5 THEN
        EnemyFrame(i) = EnemyFrame(i) + 1
        EnemyVelY(i) = EnemyVelY(i) + 0.1
        IF EnemyVelY(i) > 2 THEN EnemyVelY(i) = -3
        EnemyY(i) = EnemyY(i) + EnemyVelY(i)
        IF EnemyY(i) < 30 THEN EnemyY(i) = 30
        IF EnemyY(i) > GROUNDY - 30 THEN EnemyY(i) = GROUNDY - 30
        IF EnemyX(i) > PlayerX THEN
          EnemyX(i) = EnemyX(i) - ENEMYSPEED
          EnemyDir(i) = -1
        ELSE
          EnemyX(i) = EnemyX(i) + ENEMYSPEED
          EnemyDir(i) = 1
        END IF
      END IF

      EnemyShootTimer(i) = EnemyShootTimer(i) + 1
      ' Reduced enemy bullet frequency (doubled delays)
      shootDelay = 100 - Level * 8
      IF EnemyType(i) = 3 THEN shootDelay = 70 - Level * 5
      IF EnemyType(i) = 4 THEN shootDelay = 50 - Level * 4
      IF shootDelay < 30 THEN shootDelay = 30
      IF EnemyShootTimer(i) > shootDelay THEN
        EnemyShootTimer(i) = 0
        IF EnemyType(i) = 4 OR ABS(EnemyX(i) - PlayerX) < SCREENW THEN
          GOSUB EnemyShoot
        END IF
      END IF

      IF EnemyX(i) < CameraX - 80 THEN
        EnemyActive(i) = 0
      END IF
    END IF
  NEXT i

  IF BossActive = 1 THEN
    IF BossX > PlayerX + 100 THEN
      BossX = BossX - 0.5
    END IF

    BossFrame = BossFrame + 1
    IF BossFrame MOD (25 - Level * 3) = 0 THEN
      FOR eb = 0 TO MAXBULLETS - 1
        IF BulletActive(eb) = 0 THEN
          BulletActive(eb) = 1
          BulletOwner(eb) = 1
          BulletX(eb) = BossX - 60
          BulletY(eb) = BossY - 17
          dx = PlayerX - BulletX(eb)
          dy = PlayerY - BulletY(eb)
          dist = SQR(dx * dx + dy * dy)
          IF dist < 1 THEN dist = 1
          BulletVelX(eb) = (dx / dist) * 8
          BulletVelY(eb) = (dy / dist) * 8
          EXIT FOR
        END IF
      NEXT eb
      FOR eb = 0 TO MAXBULLETS - 1
        IF BulletActive(eb) = 0 THEN
          BulletActive(eb) = 1
          BulletOwner(eb) = 1
          BulletX(eb) = BossX + 60
          BulletY(eb) = BossY - 17
          dx = PlayerX - BulletX(eb)
          dy = PlayerY - BulletY(eb)
          dist = SQR(dx * dx + dy * dy)
          IF dist < 1 THEN dist = 1
          BulletVelX(eb) = (dx / dist) * 8
          BulletVelY(eb) = (dy / dist) * 8
          EXIT FOR
        END IF
      NEXT eb
    END IF
  END IF
RETURN

UpdateExplosions:
RETURN

EnemyShoot:
  FOR eb = 0 TO MAXBULLETS - 1
    IF BulletActive(eb) = 0 THEN
      BulletActive(eb) = 1
      BulletOwner(eb) = 1

      dx = PlayerX - EnemyX(i)
      dy = PlayerY - EnemyY(i)
      dist = SQR(dx * dx + dy * dy)
      IF dist < 1 THEN dist = 1

      IF EnemyType(i) = 1 THEN
        BulletX(eb) = EnemyX(i) + EnemyDir(i) * 8
        BulletY(eb) = EnemyY(i) - 6
        bulletSpd = 6 + Level * 0.5
        IF bulletSpd > 9 THEN bulletSpd = 9
        BulletVelX(eb) = (dx / dist) * bulletSpd
        BulletVelY(eb) = (dy / dist) * bulletSpd

      ELSEIF EnemyType(i) = 2 THEN
        BulletX(eb) = EnemyX(i) + EnemyDir(i) * 25
        BulletY(eb) = EnemyY(i) - 12
        BulletVelX(eb) = EnemyDir(i) * 7
        BulletVelY(eb) = 0

      ELSEIF EnemyType(i) = 3 THEN
        BulletX(eb) = EnemyX(i)
        BulletY(eb) = EnemyY(i) + 12
        bulletSpd = 8 + Level * 0.5
        IF bulletSpd > 11 THEN bulletSpd = 11
        leadX = dx + (dx / dist) * 10
        leadY = dy + 20
        leadDist = SQR(leadX * leadX + leadY * leadY)
        IF leadDist < 1 THEN leadDist = 1
        BulletVelX(eb) = (leadX / leadDist) * bulletSpd
        BulletVelY(eb) = (leadY / leadDist) * bulletSpd

      ELSEIF EnemyType(i) = 4 THEN
        BulletX(eb) = EnemyX(i) + EnemyDir(i) * 18
        BulletY(eb) = EnemyY(i) - 9
        bulletSpd = 9 + Level * 0.5
        IF bulletSpd > 12 THEN bulletSpd = 12
        BulletVelX(eb) = (dx / dist) * bulletSpd
        BulletVelY(eb) = (dy / dist) * bulletSpd

      ELSEIF EnemyType(i) = 5 THEN
        BulletX(eb) = EnemyX(i) + EnemyDir(i) * 10
        BulletY(eb) = EnemyY(i) - 5
        bulletSpd = 7 + Level * 0.3
        IF bulletSpd > 10 THEN bulletSpd = 10
        spreadX = dx + (RND - 0.5) * 30
        spreadY = dy + (RND - 0.5) * 20
        spreadDist = SQR(spreadX * spreadX + spreadY * spreadY)
        IF spreadDist < 1 THEN spreadDist = 1
        BulletVelX(eb) = (spreadX / spreadDist) * bulletSpd
        BulletVelY(eb) = (spreadY / spreadDist) * bulletSpd
      END IF

      EXIT FOR
    END IF
  NEXT eb
RETURN

UpdatePlatforms:
  FOR pi = 0 TO MAXPLATFORMS - 1
    IF PlatActive(pi) = 1 THEN
      IF PlayerVelY > 0 THEN
        IF PlayerX > PlatX(pi) - 10 AND PlayerX < PlatX(pi) + PlatW(pi) + 10 THEN
          IF PlayerY >= PlatY(pi) - 12 AND PlayerY <= PlatY(pi) + 5 THEN
            PlayerY = PlatY(pi) - 8
            PlayerVelY = 0
            PlayerOnGround = 1
          END IF
        END IF
      END IF
    END IF
  NEXT pi
RETURN

UpdatePOWs:
  FOR pw = 0 TO MAXPOWS - 1
    IF PowActive(pw) = 1 AND PowRescued(pw) = 0 THEN
      dx = ABS(PlayerX - PowX(pw))
      dy = ABS(PlayerY - PowY(pw))
      IF dx < 20 AND dy < 20 THEN
        PowRescued(pw) = 1
        Score = Score + 500
        GOSUB PlayPOWSound
        IF RND < 0.5 THEN
          PlayerAmmo = PlayerAmmo + 20
        ELSE
          PlayerGrenades = PlayerGrenades + 2
        END IF
      END IF
      PowFrame(pw) = PowFrame(pw) + 1
      IF PowFrame(pw) > 40 THEN PowFrame(pw) = 0
    END IF
  NEXT pw
RETURN

UpdatePickups:
  FOR pk = 0 TO MAXPICKUPS - 1
    IF PickupActive(pk) = 1 THEN
      dx = ABS(PlayerX - PickupX(pk))
      dy = ABS(PlayerY - PickupY(pk))
      IF dx < 15 AND dy < 15 THEN
        PickupActive(pk) = 0
        IF PickupType(pk) = 1 THEN
          PlayerWeapon = 2
          PlayerAmmo = PlayerAmmo + 50
        ELSEIF PickupType(pk) = 2 THEN
          PlayerWeapon = 3
          PlayerAmmo = PlayerAmmo + 10
        ELSEIF PickupType(pk) = 3 THEN
          IF PlayerLives < 5 THEN PlayerLives = PlayerLives + 1
        END IF
        GOSUB PlayPickupSound
      END IF
    END IF
  NEXT pk
RETURN

SpawnEnemies:
  enemyCount = 0
  FOR i = 0 TO MAXENEMIES - 1
    IF EnemyActive(i) = 1 THEN enemyCount = enemyCount + 1
  NEXT i

  maxEnemiesOnScreen = 6 + Level * 3
  IF maxEnemiesOnScreen > MAXENEMIES THEN maxEnemiesOnScreen = MAXENEMIES

  IF enemyCount < maxEnemiesOnScreen THEN
    spawnChance = 0.06 + Level * 0.02
    IF RND < spawnChance THEN
      FOR i = 0 TO MAXENEMIES - 1
        IF EnemyActive(i) = 0 THEN
          EnemyActive(i) = 1
          EnemyX(i) = PlayerX + SCREENW + 30 + RND * 100
          EnemyDir(i) = -1
          EnemyFrame(i) = 0
          EnemyShootTimer(i) = INT(RND * 20)
          EnemyVelY(i) = 0

          typeRoll = RND
          IF typeRoll < 0.35 THEN
            EnemyType(i) = 1
            EnemyHealth(i) = 1 + INT(Level / 3)
            EnemyY(i) = GROUNDY - 8
          ELSEIF typeRoll < 0.50 THEN
            EnemyType(i) = 2
            EnemyHealth(i) = 5 + Level * 2
            EnemyY(i) = GROUNDY - 5
          ELSEIF typeRoll < 0.70 THEN
            EnemyType(i) = 3
            EnemyHealth(i) = 4 + Level
            EnemyY(i) = 35 + RND * 40
            GOSUB PlayHelicopterSound
          ELSEIF typeRoll < 0.85 THEN
            EnemyType(i) = 5
            EnemyHealth(i) = 2 + INT(Level / 2)
            EnemyY(i) = 50 + RND * 50
            EnemyVelY(i) = -2 + RND * 4
          ELSE
            EnemyType(i) = 4
            EnemyHealth(i) = 4 + Level
            EnemyY(i) = GROUNDY - 12
          END IF

          EXIT FOR
        END IF
      NEXT i
    END IF
  END IF

  IF RND < 0.02 AND enemyCount < maxEnemiesOnScreen - 2 THEN
    waveSize = 2 + INT(RND * 2)
    FOR w = 1 TO waveSize
      FOR i = 0 TO MAXENEMIES - 1
        IF EnemyActive(i) = 0 THEN
          EnemyActive(i) = 1
          EnemyX(i) = PlayerX + SCREENW + 20 + w * 40
          EnemyType(i) = 1
          EnemyHealth(i) = 1
          EnemyY(i) = GROUNDY - 8
          EnemyDir(i) = -1
          EnemyFrame(i) = 0
          EnemyShootTimer(i) = w * 10
          EXIT FOR
        END IF
      NEXT i
    NEXT w
  END IF

  IF RND < 0.015 AND enemyCount < maxEnemiesOnScreen THEN
    FOR i = 0 TO MAXENEMIES - 1
      IF EnemyActive(i) = 0 THEN
        EnemyActive(i) = 1
        EnemyX(i) = PlayerX - SCREENW / 2 - 30
        EnemyType(i) = 1
        EnemyHealth(i) = 1
        EnemyY(i) = GROUNDY - 8
        EnemyDir(i) = 1
        EnemyFrame(i) = 0
        EnemyShootTimer(i) = 0
        EXIT FOR
      END IF
    NEXT i
  END IF

  IF PlayerX > LEVELWIDTH - 400 AND BossActive = 0 THEN
    BossActive = 1
  END IF
RETURN

' ============================================
' COLLISION DETECTION (Optimized)
' ============================================

CheckCollisions:
  FOR i = 0 TO MAXBULLETS - 1
    IF BulletActive(i) = 1 THEN

      IF BulletOwner(i) = 0 THEN
        FOR j = 0 TO MAXENEMIES - 1
          IF EnemyActive(j) = 1 THEN
            dx = ABS(BulletX(i) - EnemyX(j))
            dy = ABS(BulletY(i) - EnemyY(j))

            hitDist = 15
            IF EnemyType(j) = 2 THEN hitDist = 25
            IF EnemyType(j) = 3 THEN hitDist = 30

            IF dx < hitDist AND dy < hitDist THEN
              BulletActive(i) = 0
              dmg = 1
              IF PlayerWeapon = 3 THEN dmg = 3
              EnemyHealth(j) = EnemyHealth(j) - dmg

              IF EnemyHealth(j) <= 0 THEN
                EnemyActive(j) = 0
                GOSUB CreateExplosion
                GOSUB PlayExplosionSound

                IF EnemyType(j) = 1 THEN
                  Score = Score + 100
                ELSEIF EnemyType(j) = 2 THEN
                  Score = Score + 400
                ELSEIF EnemyType(j) = 3 THEN
                  Score = Score + 500
                ELSEIF EnemyType(j) = 4 THEN
                  Score = Score + 300
                ELSEIF EnemyType(j) = 5 THEN
                  Score = Score + 200
                END IF
              ELSE
                GOSUB PlayHitSound
              END IF
              EXIT FOR
            END IF
          END IF
        NEXT j

        FOR c = 0 TO MAXCRATES - 1
          IF CrateActive(c) = 1 AND BulletActive(i) = 1 THEN
            dx = ABS(BulletX(i) - CrateX(c))
            dy = ABS(BulletY(i) - CrateY(c))
            IF dx < 12 AND dy < 15 THEN
              BulletActive(i) = 0
              CrateHealth(c) = CrateHealth(c) - 1
              IF CrateHealth(c) <= 0 THEN
                CrateActive(c) = 0
                IF RND < 0.3 THEN
                  GOSUB SpawnPickupAtCrate
                END IF
              END IF
            END IF
          END IF
        NEXT c

        IF BossActive = 1 AND BulletActive(i) = 1 THEN
          dx = ABS(BulletX(i) - BossX)
          dy = ABS(BulletY(i) - BossY)

          IF dx < 50 AND dy < 50 THEN
            BulletActive(i) = 0
            dmg = 1
            IF PlayerWeapon = 3 THEN dmg = 3
            BossHealth = BossHealth - dmg
            GOSUB PlayHitSound

            IF BossHealth <= 0 THEN
              BossActive = 0
              FOR exp = 1 TO 5
                ExpX(0) = BossX - 40 + RND * 80
                ExpY(0) = BossY - 30 + RND * 60
                GOSUB CreateExplosionAt
              NEXT exp
              GOSUB PlayExplosionSound
              Score = Score + 3000
            END IF
          END IF
        END IF

      ELSE
        IF PlayerHit = 0 THEN
          dx = ABS(BulletX(i) - PlayerX)
          dy = ABS(BulletY(i) - PlayerY)
          IF dx < 12 AND dy < 15 THEN
            BulletActive(i) = 0
            GOSUB PlayerTakeDamage
          END IF
        END IF
      END IF
    END IF
  NEXT i

  IF PlayerHit = 0 THEN
    FOR i = 0 TO MAXENEMIES - 1
      IF EnemyActive(i) = 1 THEN
        dx = ABS(PlayerX - EnemyX(i))
        dy = ABS(PlayerY - EnemyY(i))

        hitDist = 18
        IF EnemyType(i) = 2 THEN hitDist = 28
        IF EnemyType(i) = 3 THEN hitDist = 25

        IF dx < hitDist AND dy < hitDist THEN
          GOSUB PlayerTakeDamage
          EXIT FOR
        END IF
      END IF
    NEXT i

    IF BossActive = 1 THEN
      dx = ABS(PlayerX - BossX)
      dy = ABS(PlayerY - BossY)

      IF dx < 50 AND dy < 50 THEN
        GOSUB PlayerTakeDamage
      END IF
    END IF
  END IF
RETURN

SpawnPickupAtCrate:
  FOR pk = 0 TO MAXPICKUPS - 1
    IF PickupActive(pk) = 0 THEN
      PickupActive(pk) = 1
      PickupX(pk) = CrateX(c)
      PickupY(pk) = CrateY(c)
      typeRoll = RND
      IF typeRoll < 0.4 THEN
        PickupType(pk) = 1
      ELSEIF typeRoll < 0.7 THEN
        PickupType(pk) = 2
      ELSE
        PickupType(pk) = 3
      END IF
      EXIT FOR
    END IF
  NEXT pk
RETURN

CreateExplosion:
  FOR e = 0 TO MAXEXPLOSIONS - 1
    IF ExpActive(e) = 0 THEN
      ExpActive(e) = 1
      ExpX(e) = EnemyX(j)
      ExpY(e) = EnemyY(j)
      ExpFrame(e) = 0
      EXIT FOR
    END IF
  NEXT e
RETURN

CreateExplosionAt:
  FOR e = 0 TO MAXEXPLOSIONS - 1
    IF ExpActive(e) = 0 THEN
      ExpActive(e) = 1
      ExpX(e) = ExpX(0)
      ExpY(e) = ExpY(0)
      ExpFrame(e) = 0
      EXIT FOR
    END IF
  NEXT e
RETURN

PlayerTakeDamage:
  PlayerHit = 1
  PlayerHitTimer = 0
  PlayerLives = PlayerLives - 1
  GOSUB PlayHitSound

  IF PlayerLives <= 0 THEN
    GameOver = 1
    IF Score > HighScore THEN
      HighScore = Score
    END IF
  END IF
RETURN

CheckLevelComplete:
  IF PlayerX > LEVELWIDTH - 50 AND BossActive = 0 AND BossHealth <= 0 THEN
    LevelComplete = 1
    IF Score > HighScore THEN
      HighScore = Score
    END IF
  END IF
RETURN

' ============================================
' END SCREENS
' ============================================

LevelCompleteScreen:
  CLS

  FOR y = 0 TO SCREENH
    c = 2
    IF y > 60 THEN c = 10
    IF y > 120 THEN c = 2
    LINE (0, y)-(SCREENW, y), c
  NEXT y

  COLOR 14
  LOCATE 5, 8
  PRINT "*** ZONE CLEARED! ***"

  COLOR 15
  LOCATE 8, 10
  PRINT "Mission Success!"

  LOCATE 11, 10
  PRINT "Score: "; Score

  LOCATE 13, 8
  PRINT "Zone Bonus: "; Level * 1000
  Score = Score + Level * 1000

  sx = 160
  sy = 150
  LINE (sx - 6, sy - 15)-(sx + 6, sy), 2, BF
  LINE (sx - 5, sy - 25)-(sx + 5, sy - 15), 14, BF
  LINE (sx - 7, sy - 26)-(sx + 7, sy - 20), 2, BF
  LINE (sx - 6, sy - 12)-(sx - 15, sy - 25), 2
  LINE (sx + 6, sy - 12)-(sx + 15, sy - 25), 2

  COLOR 7
  LOCATE 20, 6
  PRINT "Press SPACE to continue"

  DO
    k$ = INKEY$
  LOOP UNTIL k$ = " "
RETURN

VictoryScreen:
  CLS

  GOSUB PlayVictoryMusic

  FOR y = 0 TO SCREENH
    LINE (0, y)-(SCREENW, y), 14
  NEXT y

  COLOR 4
  LOCATE 3, 6
  PRINT "*** MISSION COMPLETE ***"

  COLOR 0
  LOCATE 6, 5
  PRINT "All zones have been cleared!"
  LOCATE 8, 4
  PRINT "The enemy has been defeated!"

  COLOR 4
  LOCATE 11, 10
  PRINT "FINAL SCORE: "; Score

  IF Score >= HighScore THEN
    COLOR 4
    LOCATE 13, 8
    PRINT "*** NEW HIGH SCORE! ***"
  END IF

  ' Medal
  CIRCLE (160, 155), 25, 14
  CIRCLE (160, 155), 20, 4
  COLOR 15
  LOCATE 19, 19
  PRINT "*"

  COLOR 0
  LOCATE 23, 8
  PRINT "Press SPACE to continue"

  DO
    k$ = INKEY$
  LOOP UNTIL k$ = " "
RETURN

GameOverScreen:
  CLS

  LINE (0, 0)-(SCREENW, SCREENH), 0, BF

  COLOR 4
  LOCATE 5, 8
  PRINT "*** MISSION FAILED ***"

  sx = 160
  sy = 120
  LINE (sx - 15, sy)-(sx + 15, sy + 8), 2, BF
  LINE (sx - 24, sy)-(sx - 16, sy + 8), 14, BF
  LINE (sx + 25, sy + 5)-(sx + 35, sy + 10), 2, BF

  COLOR 15
  LOCATE 14, 10
  PRINT "Final Score: "; Score

  IF Score >= HighScore THEN
    COLOR 14
    LOCATE 16, 8
    PRINT "*** NEW HIGH SCORE! ***"
  ELSE
    COLOR 7
    LOCATE 16, 10
    PRINT "High Score: "; HighScore
  END IF

  COLOR 7
  LOCATE 20, 6
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
