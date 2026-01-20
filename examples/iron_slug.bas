' ============================================
' IRON SLUG - A Metal Slug Tribute
' For PaSiC BASIC Interpreter
' ============================================
' Controls (SIMULTANEOUS keys supported!):
'   Left/Right or A/D - Move
'   Up/W - Jump + Aim Up (can move while jumping!)
'   Down/S - Crouch + Aim Down
'   Space or X - Shoot (can shoot while moving!)
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

' ---- Game Limits (reduced for performance) ----
CONST MAXBULLETS = 20
CONST MAXENEMIES = 15
CONST MAXEXPLOSIONS = 5
CONST MAXPARTICLES = 10
CONST MAXPLATFORMS = 15
CONST MAXCRATES = 5
CONST LEVELWIDTH = 2400

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

' ---- Bullet Arrays (now with velocity for multi-direction) ----
DIM BulletX(MAXBULLETS) AS SINGLE
DIM BulletY(MAXBULLETS) AS SINGLE
DIM BulletVelX(MAXBULLETS) AS SINGLE
DIM BulletVelY(MAXBULLETS) AS SINGLE
DIM BulletActive(MAXBULLETS) AS INTEGER
DIM BulletOwner(MAXBULLETS) AS INTEGER

' ---- Enemy Arrays ----
' Types: 1=Soldier, 2=Tank, 3=Helicopter, 4=Turret, 5=Jetpack
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

' ---- Crate Arrays (destructible cover) ----
DIM CrateX(MAXCRATES) AS INTEGER
DIM CrateY(MAXCRATES) AS INTEGER
DIM CrateHealth(MAXCRATES) AS INTEGER
DIM CrateActive(MAXCRATES) AS INTEGER

' ---- POW/Prisoner Arrays (rescue for bonuses) ----
CONST MAXPOWS = 6
DIM PowX(MAXPOWS) AS INTEGER
DIM PowY(MAXPOWS) AS INTEGER
DIM PowActive(MAXPOWS) AS INTEGER
DIM PowRescued(MAXPOWS) AS INTEGER
DIM PowFrame(MAXPOWS) AS INTEGER

' ---- Pickup Arrays (weapons, ammo, health) ----
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

' ---- Background Elements ----
DIM BGBuildingX(8) AS INTEGER
DIM BGBuildingH(8) AS INTEGER
DIM BGBuildingType(8) AS INTEGER

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
DIM BossPhase AS INTEGER
DIM ZoneType AS INTEGER

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
  GOSUB SetupPOWs
  GOSUB SetupPickups
  GOSUB PlayLevelStart

  DO
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

    _DELAY 0.020

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

  ' Dark night sky
  LINE (0, 0)-(SCREENW, 80), 0, BF

  ' Stars twinkling
  COLOR 15
  FOR st = 1 TO 25
    starX = (st * 13 + TitleFrame) MOD SCREENW
    starY = (st * 7) MOD 60
    IF (TitleFrame + st) MOD 20 < 15 THEN
      PSET (starX, starY), 15
    END IF
  NEXT st

  ' Moon with glow
  COLOR 7
  CIRCLE (280, 25), 18, 7
  PAINT (280, 25), 7, 7
  COLOR 15
  CIRCLE (280, 25), 15, 15
  PAINT (280, 25), 15, 15
  ' Moon craters
  COLOR 7
  CIRCLE (275, 22), 3, 7
  CIRCLE (283, 28), 2, 7

  ' Destroyed cityscape silhouette (dark)
  COLOR 0
  LINE (0, 80)-(SCREENW, SCREENH), 0, BF

  ' Ruined buildings (dark silhouettes)
  COLOR 8
  LINE (20, 50)-(50, 80), 8, BF
  LINE (25, 40)-(45, 50), 8, BF
  LINE (70, 60)-(100, 80), 8, BF
  LINE (130, 45)-(170, 80), 8, BF
  LINE (140, 35)-(160, 45), 8, BF
  LINE (200, 55)-(240, 80), 8, BF
  LINE (260, 50)-(300, 80), 8, BF

  ' Lit windows in buildings (some lights still on)
  COLOR 14
  IF TitleFrame MOD 30 < 25 THEN
    LINE (32, 55)-(38, 60), 14, BF
    LINE (142, 50)-(148, 55), 14, BF
    LINE (155, 60)-(161, 65), 14, BF
    LINE (270, 55)-(276, 60), 14, BF
  END IF
  COLOR 6
  LINE (85, 65)-(91, 70), 6, BF
  LINE (215, 60)-(221, 65), 6, BF

  ' Fires burning (more prominent at night)
  COLOR 4
  IF TitleFrame MOD 10 < 5 THEN
    CIRCLE (35, 38), 6, 4
    CIRCLE (150, 33), 5, 4
    CIRCLE (220, 53), 4, 4
  END IF
  COLOR 14
  IF TitleFrame MOD 8 < 4 THEN
    CIRCLE (35, 40), 4, 14
    CIRCLE (150, 35), 3, 14
    CIRCLE (220, 55), 3, 14
  END IF
  COLOR 15
  IF TitleFrame MOD 6 < 2 THEN
    CIRCLE (35, 42), 2, 15
    CIRCLE (150, 37), 2, 15
  END IF

  ' Smoke rising
  COLOR 8
  smokeY = 30 - (TitleFrame MOD 20)
  CIRCLE (35, smokeY), 4, 8
  CIRCLE (150, smokeY + 5), 3, 8

  ' Title with heavy metal style - HIGH CONTRAST
  COLOR 8
  LOCATE 3, 11
  PRINT "=== IRON SLUG ==="
  COLOR 12
  LOCATE 2, 10
  PRINT "=== IRON SLUG ==="

  COLOR 15
  LOCATE 5, 9
  PRINT "Run and Gun Action"

  ' Draw soldier character
  GOSUB DrawTitleSoldier

  ' Draw tank
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
  ' Animated soldier - HIGH CONTRAST
  sx = 80
  sy = 130

  ' Body (bright green)
  COLOR 10
  LINE (sx - 6, sy - 15)-(sx + 6, sy), 10, BF
  COLOR 2
  LINE (sx - 6, sy - 15)-(sx + 6, sy), 2, B

  ' Head
  COLOR 14
  CIRCLE (sx, sy - 20), 6, 14
  PAINT (sx, sy - 20), 14, 14

  ' Helmet (bright green)
  COLOR 10
  LINE (sx - 7, sy - 26)-(sx + 7, sy - 20), 10, BF
  COLOR 2
  LINE (sx - 7, sy - 26)-(sx + 7, sy - 20), 2, B

  ' Gun (silver)
  COLOR 7
  LINE (sx + 6, sy - 10)-(sx + 20, sy - 8), 7
  LINE (sx + 18, sy - 12)-(sx + 22, sy - 6), 7, BF

  ' Legs - animated (bright green)
  COLOR 10
  IF TitleFrame MOD 20 < 10 THEN
    LINE (sx - 4, sy)-(sx - 6, sy + 10), 10
    LINE (sx + 4, sy)-(sx + 8, sy + 10), 10
  ELSE
    LINE (sx - 4, sy)-(sx - 8, sy + 10), 10
    LINE (sx + 4, sy)-(sx + 6, sy + 10), 10
  END IF

  ' Muzzle flash when shooting animation
  IF TitleFrame MOD 30 < 5 THEN
    COLOR 14
    CIRCLE (sx + 24, sy - 9), 5, 14
    COLOR 15
    CIRCLE (sx + 24, sy - 9), 3, 15
    PAINT (sx + 24, sy - 9), 15, 15
  END IF
RETURN

DrawTitleTank:
  ' Enemy tank on the right - HIGH CONTRAST (red/silver)
  tx = 230
  ty = 135

  ' Tank body (silver with red highlights)
  COLOR 7
  LINE (tx - 25, ty - 10)-(tx + 25, ty + 5), 7, BF
  COLOR 15
  LINE (tx - 25, ty - 10)-(tx + 25, ty + 5), 15, B

  ' Tank turret (red - enemy)
  COLOR 4
  LINE (tx - 15, ty - 20)-(tx + 10, ty - 10), 4, BF
  COLOR 12
  LINE (tx - 15, ty - 20)-(tx + 10, ty - 10), 12, B

  ' Tank cannon (bright)
  COLOR 15
  LINE (tx + 10, ty - 17)-(tx + 40, ty - 13), 15, BF

  ' Tracks (dark with outline)
  COLOR 8
  LINE (tx - 28, ty + 5)-(tx + 28, ty + 12), 8, BF
  COLOR 7
  LINE (tx - 28, ty + 5)-(tx + 28, ty + 12), 7, B
  ' Track wheels
  COLOR 0
  CIRCLE (tx - 20, ty + 8), 5, 0
  CIRCLE (tx, ty + 8), 5, 0
  CIRCLE (tx + 20, ty + 8), 5, 0

  ' Cannon smoke/flash
  IF TitleFrame MOD 40 < 8 THEN
    COLOR 15
    CIRCLE (tx + 45, ty - 15), 7, 15
    COLOR 14
    CIRCLE (tx + 45, ty - 15), 5, 14
    COLOR 4
    CIRCLE (tx + 45, ty - 15), 3, 4
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
  ' Reset player
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

  ' Reset camera
  CameraX = 0
  TargetCameraX = 0

  ' Determine zone type based on level
  ZoneType = ((Level - 1) MOD 3) + 1

  ' Clear bullets
  FOR i = 0 TO MAXBULLETS - 1
    BulletActive(i) = 0
  NEXT i

  ' Clear enemies
  FOR i = 0 TO MAXENEMIES - 1
    EnemyActive(i) = 0
  NEXT i

  ' Clear explosions
  FOR i = 0 TO MAXEXPLOSIONS - 1
    ExpActive(i) = 0
  NEXT i

  ' Clear platforms
  FOR i = 0 TO MAXPLATFORMS - 1
    PlatActive(i) = 0
  NEXT i

  ' Clear crates
  FOR i = 0 TO MAXCRATES - 1
    CrateActive(i) = 0
  NEXT i

  ' Setup platforms based on zone
  GOSUB SetupPlatforms

  ' Setup crates/cover
  GOSUB SetupCrates

  ' Initialize background buildings
  FOR i = 0 TO 7
    BGBuildingX(i) = i * 300 + 100
    BGBuildingH(i) = 30 + (i MOD 4) * 20
    BGBuildingType(i) = (i MOD 3) + 1
  NEXT i

  ' Boss setup
  BossActive = 0
  BossHealth = 25 + Level * 15
  BossX = LEVELWIDTH - 150
  BossY = GROUNDY - 60
  BossFrame = 0
  BossPhase = 1
RETURN

SetupPlatforms:
  ' Create platforms (simplified for performance)
  platIdx = 0

  ' Main platforms at different heights
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
  ' Place destructible crates for cover
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
  ' Place POW prisoners throughout level
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
  ' Place weapon/health pickups
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

        ' Random pickup type
        typeRoll = RND
        IF typeRoll < 0.4 THEN
          PickupType(pickIdx) = 1  ' Heavy MG
        ELSEIF typeRoll < 0.7 THEN
          PickupType(pickIdx) = 2  ' Rocket
        ELSE
          PickupType(pickIdx) = 3  ' Health
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
  ' Camera follows player with some lead
  TargetCameraX = PlayerX - 100

  ' Clamp camera to level bounds
  IF TargetCameraX < 0 THEN TargetCameraX = 0
  IF TargetCameraX > LEVELWIDTH - SCREENW THEN TargetCameraX = LEVELWIDTH - SCREENW

  ' Smooth camera movement
  CameraX = CameraX + (TargetCameraX - CameraX) * 0.1
RETURN

' ============================================
' DRAWING SUBROUTINES
' ============================================

DrawBackground:
  ' Clear screen with black (single operation)
  CLS

  ' Simplified stars - just a few PSETs (no loops)
  PSET (23, 12), 15
  PSET (69, 26), 15
  PSET (115, 5), 15
  PSET (161, 40), 7
  PSET (207, 19), 15
  PSET (253, 33), 7
  PSET (299, 8), 15
  PSET (41, 45), 7
  PSET (180, 28), 15

  ' Simplified moon - just filled rectangle (no PAINT)
  moonX = 270 - INT(CameraX * 0.02)
  IF moonX > -30 AND moonX < SCREENW + 30 THEN
    LINE (moonX - 18, 12)-(moonX + 18, 48), 15, BF
  END IF

  ' Horizon line
  LINE (0, 80)-(SCREENW, 80), 8
RETURN

DrawGround:
  ' Ground area - single filled rectangle
  LINE (0, GROUNDY)-(SCREENW, SCREENH), 8, BF
  ' Top ground edge
  LINE (0, GROUNDY)-(SCREENW, GROUNDY + 1), 7, BF
RETURN

DrawPlatforms:
  FOR pi = 0 TO MAXPLATFORMS - 1
    IF PlatActive(pi) = 1 THEN
      platSX = PlatX(pi) - CameraX
      IF platSX > -PlatW(pi) AND platSX < SCREENW + 10 THEN
        ' All platforms use simple filled rectangle + top line
        IF PlatType(pi) = 1 THEN
          LINE (platSX, PlatY(pi))-(platSX + PlatW(pi), PlatY(pi) + 6), 7, BF
          LINE (platSX, PlatY(pi))-(platSX + PlatW(pi), PlatY(pi)), 15
        ELSEIF PlatType(pi) = 2 THEN
          LINE (platSX, PlatY(pi))-(platSX + PlatW(pi), PlatY(pi) + 5), 6, BF
          LINE (platSX, PlatY(pi))-(platSX + PlatW(pi), PlatY(pi)), 14
        ELSE
          LINE (platSX, PlatY(pi))-(platSX + PlatW(pi), PlatY(pi) + 8), 8, BF
          LINE (platSX, PlatY(pi))-(platSX + PlatW(pi), PlatY(pi)), 7
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
        ' Wooden crate
        COLOR 6
        LINE (cx - 10, cy - 14)-(cx + 10, cy), 6, BF
        ' Crate detail
        COLOR 14
        LINE (cx - 10, cy - 14)-(cx + 10, cy), 14, B
        LINE (cx - 10, cy - 7)-(cx + 10, cy - 7), 14
        LINE (cx, cy - 14)-(cx, cy), 14
        ' Damage indicator
        IF CrateHealth(ci) = 1 THEN
          COLOR 8
          LINE (cx - 8, cy - 12)-(cx + 6, cy - 2), 8
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
          ' POW prisoner (tied up, waving for help)
          ' Body (gray prison clothes)
          COLOR 7
          LINE (px - 3, py - 10)-(px + 3, py), 7, BF
          ' Head
          COLOR 14
          CIRCLE (px, py - 14), 4, 14
          PAINT (px, py - 14), 14, 14
          ' Waving arm
          IF PowFrame(pw) < 20 THEN
            LINE (px + 3, py - 8)-(px + 8, py - 15), 14
          ELSE
            LINE (px + 3, py - 8)-(px + 6, py - 12), 14
          END IF
          ' "HELP" indicator
          COLOR 15
          IF PowFrame(pw) MOD 30 < 20 THEN
            LOCATE (py - 25) / 8, (px - 8) / 8
            PRINT "!"
          END IF
        ELSE
          ' Rescued - running away animation
          PowX(pw) = PowX(pw) - 2
          COLOR 10
          LINE (px - 3, py - 10)-(px + 3, py), 10, BF
          COLOR 14
          CIRCLE (px, py - 14), 4, 14
        END IF
      END IF
    END IF
  NEXT pw
RETURN

DrawPickups:
  FOR pk = 0 TO MAXPICKUPS - 1
    IF PickupActive(pk) = 1 THEN
      px = PickupX(pk) - CameraX
      py = PickupY(pk)
      IF px > -15 AND px < SCREENW + 15 THEN
        IF PickupType(pk) = 1 THEN
          ' Heavy Machine Gun - H icon
          COLOR 4
          LINE (px - 8, py - 10)-(px + 8, py + 2), 4, BF
          COLOR 15
          LINE (px - 8, py - 10)-(px + 8, py + 2), 15, B
          COLOR 14
          LOCATE py / 8, (px - 3) / 8
          PRINT "H"
        ELSEIF PickupType(pk) = 2 THEN
          ' Rocket Launcher - R icon
          COLOR 1
          LINE (px - 8, py - 10)-(px + 8, py + 2), 1, BF
          COLOR 15
          LINE (px - 8, py - 10)-(px + 8, py + 2), 15, B
          COLOR 14
          LOCATE py / 8, (px - 3) / 8
          PRINT "R"
        ELSE
          ' Health - + icon
          COLOR 4
          LINE (px - 8, py - 10)-(px + 8, py + 2), 4, BF
          COLOR 15
          LINE (px - 8, py - 10)-(px + 8, py + 2), 15, B
          LINE (px - 5, py - 4)-(px + 5, py - 4), 15
          LINE (px, py - 9)-(px, py + 1), 15
        END IF
      END IF
    END IF
  NEXT pk
RETURN

DrawPlayer:
  ' Get screen position
  px = INT(PlayerX - CameraX)
  py = INT(PlayerY)

  ' Skip if off screen
  IF px < -20 OR px > SCREENW + 20 THEN RETURN

  ' Flicker when hit
  IF PlayerHit = 1 THEN
    IF PlayerHitTimer MOD 4 < 2 THEN RETURN
  END IF

  ' Body (bright green - single rectangle)
  LINE (px - 5, py - 12)-(px + 5, py), 10, BF

  ' Head (rectangle instead of circle+paint)
  LINE (px - 4, py - 21)-(px + 4, py - 13), 14, BF

  ' Helmet
  LINE (px - 6, py - 23)-(px + 6, py - 18), 10, BF

  ' Gun
  IF PlayerDir > 0 THEN
    LINE (px + 5, py - 8)-(px + 15, py - 6), 7
    LINE (px + 13, py - 10)-(px + 17, py - 4), 7, BF
    ' Muzzle flash (simple rectangle)
    IF PlayerShooting > 0 THEN
      LINE (px + 16, py - 10)-(px + 24, py - 4), 14, BF
    END IF
  ELSE
    LINE (px - 5, py - 8)-(px - 15, py - 6), 7
    LINE (px - 17, py - 10)-(px - 13, py - 4), 7, BF
    IF PlayerShooting > 0 THEN
      LINE (px - 24, py - 10)-(px - 16, py - 4), 14, BF
    END IF
  END IF

  ' Legs - animated
  PlayerFrame = PlayerFrame + 1
  IF PlayerFrame > 20 THEN PlayerFrame = 0

  IF PlayerOnGround = 0 THEN
    LINE (px - 4, py)-(px - 7, py + 5), 10
    LINE (px + 4, py)-(px + 7, py + 5), 10
  ELSEIF PlayerFrame < 10 THEN
    LINE (px - 3, py)-(px - 5, py + 8), 10
    LINE (px + 3, py)-(px + 6, py + 8), 10
  ELSE
    LINE (px - 3, py)-(px - 6, py + 8), 10
    LINE (px + 3, py)-(px + 5, py + 8), 10
  END IF

  IF PlayerShooting > 0 THEN PlayerShooting = PlayerShooting - 1
RETURN

DrawBullets:
  FOR i = 0 TO MAXBULLETS - 1
    IF BulletActive(i) = 1 THEN
      bx = INT(BulletX(i) - CameraX)
      by = INT(BulletY(i))
      IF bx >= -10 AND bx < SCREENW + 10 AND by >= -10 AND by < SCREENH + 10 THEN
        IF BulletOwner(i) = 0 THEN
          ' Player bullet - simple line + pixel
          LINE (bx - 3, by)-(bx + 3, by), 14
          PSET (bx, by), 15
        ELSE
          ' Enemy bullet - simple line + pixel
          LINE (bx - 2, by)-(bx + 2, by), 4
          PSET (bx, by), 12
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
          ' Soldier - simplified (rectangles only)
          LINE (ex - 4, ey - 10)-(ex + 4, ey), 4, BF
          LINE (ex - 4, ey - 17)-(ex + 4, ey - 11), 14, BF
          LINE (ex - 5, ey - 18)-(ex + 5, ey - 14), 4, BF
          IF EnemyDir(i) > 0 THEN
            LINE (ex + 4, ey - 6)-(ex + 12, ey - 5), 7
          ELSE
            LINE (ex - 12, ey - 5)-(ex - 4, ey - 6), 7
          END IF
          LINE (ex - 2, ey)-(ex - 4, ey + 6), 4
          LINE (ex + 2, ey)-(ex + 4, ey + 6), 4

        ELSEIF EnemyType(i) = 2 THEN
          ' Tank - simplified
          LINE (ex - 15, ey - 8)-(ex + 15, ey), 7, BF
          LINE (ex - 8, ey - 15)-(ex + 5, ey - 8), 7, BF
          IF EnemyDir(i) > 0 THEN
            LINE (ex + 5, ey - 13)-(ex + 25, ey - 10), 15, BF
          ELSE
            LINE (ex - 25, ey - 13)-(ex - 5, ey - 10), 15, BF
          END IF
          LINE (ex - 18, ey)-(ex + 18, ey + 5), 8, BF

        ELSEIF EnemyType(i) = 3 THEN
          ' Helicopter - simplified (no COS calc)
          LINE (ex - 20, ey - 5)-(ex + 15, ey + 8), 7, BF
          LINE (ex + 5, ey - 3)-(ex + 13, ey + 5), 4, BF
          LINE (ex - 35, ey - 3)-(ex - 20, ey + 2), 8, BF
          ' Simple rotor line
          IF EnemyFrame(i) MOD 4 < 2 THEN
            LINE (ex - 30, ey - 10)-(ex + 20, ey - 10), 15
          ELSE
            LINE (ex - 5, ey - 10)-(ex - 5, ey - 10), 15
          END IF
          LINE (ex, ey + 8)-(ex, ey + 14), 8

        ELSEIF EnemyType(i) = 4 THEN
          ' Turret - simplified
          LINE (ex - 12, ey - 5)-(ex + 12, ey + 5), 8, BF
          IF EnemyDir(i) > 0 THEN
            LINE (ex, ey - 10)-(ex + 20, ey - 8), 7, BF
          ELSE
            LINE (ex - 20, ey - 10)-(ex, ey - 8), 7, BF
          END IF
          LINE (ex - 5, ey - 12)-(ex + 5, ey - 5), 7, BF
          IF EnemyFrame(i) MOD 10 < 5 THEN
            LINE (ex - 2, ey - 17)-(ex + 2, ey - 13), 4, BF
          END IF

        ELSEIF EnemyType(i) = 5 THEN
          ' Jetpack soldier - simplified
          LINE (ex - 6, ey - 8)-(ex - 2, ey + 2), 8, BF
          IF EnemyFrame(i) MOD 6 < 3 THEN
            LINE (ex - 5, ey + 2)-(ex - 3, ey + 8), 14
          END IF
          LINE (ex - 3, ey - 10)-(ex + 4, ey), 4, BF
          LINE (ex - 4, ey - 17)-(ex + 4, ey - 11), 14, BF
          LINE (ex - 5, ey - 18)-(ex + 5, ey - 14), 8, BF
          IF EnemyDir(i) > 0 THEN
            LINE (ex + 4, ey - 6)-(ex + 12, ey - 5), 7
          ELSE
            LINE (ex - 12, ey - 5)-(ex - 4, ey - 6), 7
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

  ' Main body
  LINE (bx - 40, by - 30)-(bx + 40, by + 10), 7, BF
  ' Cockpit
  LINE (bx - 20, by - 45)-(bx + 20, by - 30), 4, BF
  LINE (bx - 15, by - 42)-(bx + 15, by - 33), 11, BF
  ' Arms/Cannons
  LINE (bx - 60, by - 20)-(bx - 40, by - 15), 7, BF
  LINE (bx + 40, by - 20)-(bx + 60, by - 15), 7, BF
  ' Cannon tips (flashing)
  IF BossFrame < 15 THEN
    LINE (bx - 70, by - 22)-(bx - 60, by - 12), 14, BF
    LINE (bx + 60, by - 22)-(bx + 70, by - 12), 14, BF
  END IF
  ' Legs
  LINE (bx - 35, by + 10)-(bx - 30, by + 30), 7, BF
  LINE (bx + 30, by + 10)-(bx + 35, by + 30), 7, BF
  ' Feet
  LINE (bx - 45, by + 30)-(bx - 25, by + 35), 7, BF
  LINE (bx + 25, by + 30)-(bx + 45, by + 35), 7, BF
  ' Health bar
  LINE (bx - 40, by - 55)-(bx + 40, by - 50), 0, BF
  healthWidth = (BossHealth / (20 + Level * 10)) * 78
  IF healthWidth > 0 THEN
    LINE (bx - 39, by - 54)-(bx - 39 + healthWidth, by - 51), 4, BF
  END IF
RETURN

DrawExplosions:
  FOR i = 0 TO MAXEXPLOSIONS - 1
    IF ExpActive(i) = 1 THEN
      ex = INT(ExpX(i) - CameraX)
      ey = INT(ExpY(i))

      IF ex >= -30 AND ex < SCREENW + 30 THEN
        ' Explosion using rectangles instead of circles
        radius = ExpFrame(i) * 2
        IF ExpFrame(i) < 5 THEN
          LINE (ex - radius, ey - radius)-(ex + radius, ey + radius), 15, BF
        ELSEIF ExpFrame(i) < 10 THEN
          LINE (ex - radius, ey - radius)-(ex + radius, ey + radius), 14, BF
        ELSE
          LINE (ex - radius, ey - radius)-(ex + radius, ey + radius), 4, BF
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
  ' Score
  COLOR 15
  LOCATE 1, 1
  PRINT "SCORE:"; Score

  ' Level
  LOCATE 1, 15
  PRINT "ZONE:"; Level

  ' Weapon indicator
  COLOR 14
  LOCATE 1, 26
  IF PlayerWeapon = 1 THEN
    PRINT "P"
  ELSEIF PlayerWeapon = 2 THEN
    PRINT "H"
  ELSEIF PlayerWeapon = 3 THEN
    PRINT "R"
  END IF

  ' Lives - simple rectangles
  FOR i = 1 TO PlayerLives
    lx = 270 + (i * 10)
    LINE (lx - 2, 9)-(lx + 2, 16), 10, BF
  NEXT i

  ' Progress bar (distance to level end)
  COLOR 8
  LINE (100, 5)-(200, 10), 8, B
  progress = PlayerX / LEVELWIDTH
  IF progress > 1 THEN progress = 1
  progressWidth = progress * 98
  COLOR 10
  IF progressWidth > 0 THEN
    LINE (101, 6)-(101 + progressWidth, 9), 10, BF
  END IF

  ' Boss health bar when boss is active
  IF BossActive = 1 THEN
    COLOR 4
    LOCATE 3, 12
    PRINT "!! BOSS !!"
  END IF
RETURN

' ============================================
' INPUT HANDLING (using KEYDOWN for simultaneous keys)
' ============================================

HandleInput:
  ' Clear INKEY$ buffer and check for toggle keys
  k$ = INKEY$

  ' Reset aim direction each frame
  PlayerAimDir = 0
  PlayerCrouching = 0

  ' ESC to quit (use INKEY for one-shot)
  IF KEYDOWN(1) THEN
    GameOver = 1
    RETURN
  END IF

  ' M to toggle sound (use INKEY to avoid rapid toggle)
  IF k$ = "m" OR k$ = "M" THEN
    SoundOn = 1 - SoundOn
  END IF

  ' Z to switch weapon (use INKEY to avoid rapid switch)
  IF k$ = "z" OR k$ = "Z" THEN
    PlayerWeapon = PlayerWeapon + 1
    IF PlayerWeapon > 3 THEN PlayerWeapon = 1
  END IF

  ' === SIMULTANEOUS KEY DETECTION using KEYDOWN ===

  ' Left movement (Arrow Left=75 or A=30)
  IF KEYDOWN(75) OR KEYDOWN(30) THEN
    PlayerX = PlayerX - PLAYERSPEED
    PlayerDir = -1
    IF PlayerX < 20 THEN PlayerX = 20
  END IF

  ' Right movement (Arrow Right=77 or D=32)
  IF KEYDOWN(77) OR KEYDOWN(32) THEN
    PlayerX = PlayerX + PLAYERSPEED
    PlayerDir = 1
    IF PlayerX > LEVELWIDTH - 20 THEN PlayerX = LEVELWIDTH - 20
  END IF

  ' Up - Aim Up and Jump (Arrow Up=72 or W=17)
  IF KEYDOWN(72) OR KEYDOWN(17) THEN
    PlayerAimDir = -1
    IF PlayerOnGround = 1 AND JumpLock = 0 THEN
      PlayerVelY = JUMPVEL
      PlayerOnGround = 0
      JumpLock = 1
      GOSUB PlayJumpSound
    END IF
  ELSE
    JumpLock = 0
  END IF

  ' Down - Crouch/Aim Down (Arrow Down=80 or S=31)
  IF KEYDOWN(80) OR KEYDOWN(31) THEN
    PlayerCrouching = 1
    PlayerAimDir = 1
  END IF

  ' Shoot (Space=57 or X=45)
  IF KEYDOWN(57) OR KEYDOWN(45) THEN
    IF ShootCooldown = 0 THEN
      GOSUB FireBullet
      ShootCooldown = 5
    END IF
  END IF

  ' Decrease shoot cooldown
  IF ShootCooldown > 0 THEN ShootCooldown = ShootCooldown - 1
RETURN

FireBullet:
  ' Find inactive bullet
  FOR i = 0 TO MAXBULLETS - 1
    IF BulletActive(i) = 0 THEN
      BulletActive(i) = 1
      BulletOwner(i) = 0

      ' Determine bullet velocity based on aim direction
      IF PlayerAimDir = -1 THEN
        ' Shooting UP
        BulletX(i) = PlayerX
        BulletY(i) = PlayerY - 20
        BulletVelX(i) = 0
        BulletVelY(i) = -BULLETSPEED
      ELSEIF PlayerAimDir = 1 AND PlayerOnGround = 0 THEN
        ' Shooting DOWN (only in air)
        BulletX(i) = PlayerX
        BulletY(i) = PlayerY + 5
        BulletVelX(i) = 0
        BulletVelY(i) = BULLETSPEED
      ELSEIF PlayerAimDir = 1 AND PlayerOnGround = 1 THEN
        ' Crouching - shoot diagonal down
        BulletX(i) = PlayerX + PlayerDir * 10
        BulletY(i) = PlayerY - 3
        BulletVelX(i) = PlayerDir * BULLETSPEED * 0.7
        BulletVelY(i) = BULLETSPEED * 0.5
      ELSE
        ' Normal horizontal shot
        BulletX(i) = PlayerX + PlayerDir * 15
        BulletY(i) = PlayerY - 7
        BulletVelX(i) = PlayerDir * BULLETSPEED
        BulletVelY(i) = 0
      END IF

      ' Weapon-specific modifications
      IF PlayerWeapon = 2 THEN
        ' Spread shot - fire 3 bullets
        BulletVelY(i) = BulletVelY(i) - 2
      ELSEIF PlayerWeapon = 3 THEN
        ' Heavy shot - slower but powerful
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
  ' Apply gravity
  PlayerVelY = PlayerVelY + GRAVITY
  PlayerY = PlayerY + PlayerVelY

  ' Ground collision
  IF PlayerY >= GROUNDY - 8 THEN
    PlayerY = GROUNDY - 8
    PlayerVelY = 0
    PlayerOnGround = 1
  END IF

  ' Update hit timer
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
      ' Move bullet by velocity
      BulletX(i) = BulletX(i) + BulletVelX(i)
      BulletY(i) = BulletY(i) + BulletVelY(i)

      ' Deactivate if off screen
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
      ' Behavior based on enemy type
      IF EnemyType(i) = 1 THEN
        ' Soldier - ground movement towards player
        IF EnemyX(i) > PlayerX + 50 THEN
          EnemyX(i) = EnemyX(i) - ENEMYSPEED
          EnemyDir(i) = -1
        ELSEIF EnemyX(i) < PlayerX - 50 THEN
          EnemyX(i) = EnemyX(i) + ENEMYSPEED
          EnemyDir(i) = 1
        END IF

      ELSEIF EnemyType(i) = 2 THEN
        ' Tank - slower ground movement
        IF EnemyX(i) > PlayerX + 80 THEN
          EnemyX(i) = EnemyX(i) - ENEMYSPEED * 0.5
          EnemyDir(i) = -1
        ELSEIF EnemyX(i) < PlayerX - 80 THEN
          EnemyX(i) = EnemyX(i) + ENEMYSPEED * 0.5
          EnemyDir(i) = 1
        END IF

      ELSEIF EnemyType(i) = 3 THEN
        ' Helicopter - flies and bobs up/down
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
        ' Turret - stationary, just rotates to face player
        IF PlayerX < EnemyX(i) THEN
          EnemyDir(i) = -1
        ELSE
          EnemyDir(i) = 1
        END IF

      ELSEIF EnemyType(i) = 5 THEN
        ' Jetpack soldier - flies erratically
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

      ' Shooting timer for enemies - MUCH more aggressive!
      EnemyShootTimer(i) = EnemyShootTimer(i) + 1
      ' Different shoot rates for different enemy types
      shootDelay = 50 - Level * 8
      IF EnemyType(i) = 3 THEN shootDelay = 35 - Level * 5
      IF EnemyType(i) = 4 THEN shootDelay = 25 - Level * 4
      IF shootDelay < 15 THEN shootDelay = 15
      IF EnemyShootTimer(i) > shootDelay THEN
        EnemyShootTimer(i) = 0
        ' Only shoot if enemy can see player (in front)
        IF EnemyType(i) = 4 OR ABS(EnemyX(i) - PlayerX) < SCREENW THEN
          GOSUB EnemyShoot
        END IF
      END IF

      ' Keep on screen (relative to camera)
      IF EnemyX(i) < CameraX - 80 THEN
        EnemyActive(i) = 0
      END IF
    END IF
  NEXT i

  ' Update boss
  IF BossActive = 1 THEN
    ' Boss slowly moves towards player
    IF BossX > PlayerX + 100 THEN
      BossX = BossX - 0.5
    END IF

    ' Boss shoots at player - dual cannons!
    BossFrame = BossFrame + 1
    IF BossFrame MOD (25 - Level * 3) = 0 THEN
      ' Fire from left cannon
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
      ' Fire from right cannon
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
  ' Explosions update in DrawExplosions
RETURN

EnemyShoot:
  ' Enemy fires a bullet at player (uses loop variable i from UpdateEnemies)

  ' Find inactive bullet for enemy
  FOR eb = 0 TO MAXBULLETS - 1
    IF BulletActive(eb) = 0 THEN
      BulletActive(eb) = 1
      BulletOwner(eb) = 1

      ' Calculate direction to player with prediction
      dx = PlayerX - EnemyX(i)
      dy = PlayerY - EnemyY(i)
      dist = SQR(dx * dx + dy * dy)
      IF dist < 1 THEN dist = 1

      ' Different bullet behavior per enemy type
      IF EnemyType(i) = 1 THEN
        ' Soldier - medium speed aimed shot
        BulletX(eb) = EnemyX(i) + EnemyDir(i) * 8
        BulletY(eb) = EnemyY(i) - 6
        bulletSpd = 6 + Level * 0.5
        IF bulletSpd > 9 THEN bulletSpd = 9
        BulletVelX(eb) = (dx / dist) * bulletSpd
        BulletVelY(eb) = (dy / dist) * bulletSpd

      ELSEIF EnemyType(i) = 2 THEN
        ' Tank - slow but powerful cannon (horizontal)
        BulletX(eb) = EnemyX(i) + EnemyDir(i) * 25
        BulletY(eb) = EnemyY(i) - 12
        BulletVelX(eb) = EnemyDir(i) * 7
        BulletVelY(eb) = 0

      ELSEIF EnemyType(i) = 3 THEN
        ' Helicopter - fast downward aimed shots
        BulletX(eb) = EnemyX(i)
        BulletY(eb) = EnemyY(i) + 12
        bulletSpd = 8 + Level * 0.5
        IF bulletSpd > 11 THEN bulletSpd = 11
        ' Lead the target slightly
        leadX = dx + (dx / dist) * 10
        leadY = dy + 20
        leadDist = SQR(leadX * leadX + leadY * leadY)
        IF leadDist < 1 THEN leadDist = 1
        BulletVelX(eb) = (leadX / leadDist) * bulletSpd
        BulletVelY(eb) = (leadY / leadDist) * bulletSpd

      ELSEIF EnemyType(i) = 4 THEN
        ' Turret - rapid accurate fire!
        BulletX(eb) = EnemyX(i) + EnemyDir(i) * 18
        BulletY(eb) = EnemyY(i) - 9
        bulletSpd = 9 + Level * 0.5
        IF bulletSpd > 12 THEN bulletSpd = 12
        BulletVelX(eb) = (dx / dist) * bulletSpd
        BulletVelY(eb) = (dy / dist) * bulletSpd

      ELSEIF EnemyType(i) = 5 THEN
        ' Jetpack soldier - erratic spread shots
        BulletX(eb) = EnemyX(i) + EnemyDir(i) * 10
        BulletY(eb) = EnemyY(i) - 5
        bulletSpd = 7 + Level * 0.3
        IF bulletSpd > 10 THEN bulletSpd = 10
        ' Add some randomness to aim
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
  ' Check if player is on a platform
  FOR pi = 0 TO MAXPLATFORMS - 1
    IF PlatActive(pi) = 1 THEN
      platSX = PlatX(pi) - CameraX
      ' Check if player is landing on platform
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
  ' Check if player touches a POW to rescue them
  FOR pw = 0 TO MAXPOWS - 1
    IF PowActive(pw) = 1 AND PowRescued(pw) = 0 THEN
      dx = ABS(PlayerX - PowX(pw))
      dy = ABS(PlayerY - PowY(pw))
      IF dx < 20 AND dy < 20 THEN
        PowRescued(pw) = 1
        Score = Score + 500
        GOSUB PlayPOWSound
        ' POW gives random bonus
        IF RND < 0.5 THEN
          PlayerAmmo = PlayerAmmo + 20
        ELSE
          PlayerGrenades = PlayerGrenades + 2
        END IF
      END IF
      ' Animate POW
      PowFrame(pw) = PowFrame(pw) + 1
      IF PowFrame(pw) > 40 THEN PowFrame(pw) = 0
    END IF
  NEXT pw
RETURN

UpdatePickups:
  ' Check if player picks up items
  FOR pk = 0 TO MAXPICKUPS - 1
    IF PickupActive(pk) = 1 THEN
      dx = ABS(PlayerX - PickupX(pk))
      dy = ABS(PlayerY - PickupY(pk))
      IF dx < 15 AND dy < 15 THEN
        PickupActive(pk) = 0
        IF PickupType(pk) = 1 THEN
          ' Heavy Machine Gun
          PlayerWeapon = 2
          PlayerAmmo = PlayerAmmo + 50
        ELSEIF PickupType(pk) = 2 THEN
          ' Rocket Launcher
          PlayerWeapon = 3
          PlayerAmmo = PlayerAmmo + 10
        ELSEIF PickupType(pk) = 3 THEN
          ' Health
          IF PlayerLives < 5 THEN PlayerLives = PlayerLives + 1
        END IF
        GOSUB PlayPickupSound
      END IF
    END IF
  NEXT pk
RETURN

SpawnEnemies:
  ' Count active enemies
  enemyCount = 0
  FOR i = 0 TO MAXENEMIES - 1
    IF EnemyActive(i) = 1 THEN enemyCount = enemyCount + 1
  NEXT i

  ' MUCH more aggressive spawning - harder game!
  maxEnemiesOnScreen = 6 + Level * 3
  IF maxEnemiesOnScreen > MAXENEMIES THEN maxEnemiesOnScreen = MAXENEMIES

  IF enemyCount < maxEnemiesOnScreen THEN
    ' Higher spawn chance - enemies come faster
    spawnChance = 0.06 + Level * 0.02
    IF RND < spawnChance THEN
      FOR i = 0 TO MAXENEMIES - 1
        IF EnemyActive(i) = 0 THEN
          EnemyActive(i) = 1
          EnemyX(i) = PlayerX + SCREENW + 30 + RND * 100
          EnemyDir(i) = -1
          EnemyFrame(i) = 0
          ' Shorter initial shoot timer - enemies shoot sooner
          EnemyShootTimer(i) = INT(RND * 20)
          EnemyVelY(i) = 0

          ' Random enemy type - more variety
          typeRoll = RND
          IF typeRoll < 0.35 THEN
            ' Soldier - common but not too many
            EnemyType(i) = 1
            EnemyHealth(i) = 1 + INT(Level / 3)
            EnemyY(i) = GROUNDY - 8
          ELSEIF typeRoll < 0.50 THEN
            ' Tank - heavy ground unit
            EnemyType(i) = 2
            EnemyHealth(i) = 5 + Level * 2
            EnemyY(i) = GROUNDY - 5
          ELSEIF typeRoll < 0.70 THEN
            ' Helicopter - MORE air units!
            EnemyType(i) = 3
            EnemyHealth(i) = 4 + Level
            EnemyY(i) = 35 + RND * 40
            GOSUB PlayHelicopterSound
          ELSEIF typeRoll < 0.85 THEN
            ' Jetpack soldier - flying infantry
            EnemyType(i) = 5
            EnemyHealth(i) = 2 + INT(Level / 2)
            EnemyY(i) = 50 + RND * 50
            EnemyVelY(i) = -2 + RND * 4
          ELSE
            ' Turret - stationary defense
            EnemyType(i) = 4
            EnemyHealth(i) = 4 + Level
            EnemyY(i) = GROUNDY - 12
          END IF

          EXIT FOR
        END IF
      NEXT i
    END IF
  END IF

  ' Spawn multiple enemies at once sometimes (wave attack)
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

  ' Also spawn from behind MORE often
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

  ' Activate boss near end of level
  IF PlayerX > LEVELWIDTH - 400 AND BossActive = 0 THEN
    BossActive = 1
  END IF
RETURN

' ============================================
' COLLISION DETECTION
' ============================================

CheckCollisions:
  ' Bullet collisions
  FOR i = 0 TO MAXBULLETS - 1
    IF BulletActive(i) = 1 THEN

      ' Player bullets hit enemies
      IF BulletOwner(i) = 0 THEN
        ' Check against enemies
        FOR j = 0 TO MAXENEMIES - 1
          IF EnemyActive(j) = 1 THEN
            dx = ABS(BulletX(i) - EnemyX(j))
            dy = ABS(BulletY(i) - EnemyY(j))

            ' Different hit distances for different enemies
            hitDist = 15
            IF EnemyType(j) = 2 THEN hitDist = 25
            IF EnemyType(j) = 3 THEN hitDist = 30

            IF dx < hitDist AND dy < hitDist THEN
              BulletActive(i) = 0
              ' Weapon damage multiplier
              dmg = 1
              IF PlayerWeapon = 3 THEN dmg = 3
              EnemyHealth(j) = EnemyHealth(j) - dmg

              IF EnemyHealth(j) <= 0 THEN
                EnemyActive(j) = 0
                GOSUB CreateExplosion
                GOSUB PlayExplosionSound

                ' Score based on enemy type
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

        ' Player bullets hit crates
        FOR c = 0 TO MAXCRATES - 1
          IF CrateActive(c) = 1 AND BulletActive(i) = 1 THEN
            dx = ABS(BulletX(i) - CrateX(c))
            dy = ABS(BulletY(i) - CrateY(c))
            IF dx < 12 AND dy < 15 THEN
              BulletActive(i) = 0
              CrateHealth(c) = CrateHealth(c) - 1
              IF CrateHealth(c) <= 0 THEN
                CrateActive(c) = 0
                ' Crate may drop pickup
                IF RND < 0.3 THEN
                  GOSUB SpawnPickupAtCrate
                END IF
              END IF
            END IF
          END IF
        NEXT c

        ' Player bullets hit boss
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
              ' Multiple explosions for boss
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
        ' Enemy bullets hit player
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

  ' Enemy vs Player contact collisions
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

    ' Boss vs Player contact
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
  ' Spawn pickup where crate was destroyed
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
  ' Create explosion at enemy position
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
  ' Create explosion at ExpX(0), ExpY(0)
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
  ' Level complete when boss is defeated and player near end
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

  ' Victory background
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

  ' Draw victorious soldier
  sx = 160
  sy = 150
  COLOR 2
  LINE (sx - 6, sy - 15)-(sx + 6, sy), 2, BF
  COLOR 14
  CIRCLE (sx, sy - 20), 6, 14
  PAINT (sx, sy - 20), 14, 14
  COLOR 2
  LINE (sx - 7, sy - 26)-(sx + 7, sy - 20), 2, BF
  ' Arms up in victory
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

  ' Gold/celebration background
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
  COLOR 14
  CIRCLE (160, 155), 25, 14
  PAINT (160, 155), 14, 14
  COLOR 4
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

  ' Dark background
  LINE (0, 0)-(SCREENW, SCREENH), 0, BF

  COLOR 4
  LOCATE 5, 8
  PRINT "*** MISSION FAILED ***"

  ' Fallen soldier
  sx = 160
  sy = 120
  COLOR 2
  LINE (sx - 15, sy)-(sx + 15, sy + 8), 2, BF
  COLOR 14
  CIRCLE (sx - 20, sy + 4), 5, 14
  PAINT (sx - 20, sy + 4), 14, 14
  ' Helmet fallen off
  COLOR 2
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
