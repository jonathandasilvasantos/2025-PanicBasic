' Enhanced Enduro-style Car Racing Game
' Inspired by Atari Enduro (1983) by Activision
' This game features a bending road, distant mountains,
' a day-to-night cycle, and a simple scoreboard.
' (Customize constants as needed.)

SCREEN 13           ' 320x200 with 256 colors
CLS

'-------------------------------
' Constants and Game Variables
'-------------------------------
CONST ROAD_WIDTH = 40
CONST PADDLE_SPEED = 5
CONST CAR_SPEED = 3
CONST DAY_LENGTH = 300      ' Frames per "day" period
CONST SUN_RADIUS = 10

' Game variables
timeCounter = 0             ' Counts frames; resets every DAY_LENGTH
dayNumber = 1               ' Day counter
score = 0                   ' Score: number of obstacles passed
carX = (320 - ROAD_WIDTH) / 2 ' Start car near center
carY = 180                  ' Car vertical position on screen

' Road variables
roadDX = 0                ' Horizontal offset of road center (changes with curves)

'-------------------------------
' Main Game Loop
'-------------------------------
DO
    CLS
    
    ' Update time and day/night cycle
    timeCounter = timeCounter + 1
    IF timeCounter >= DAY_LENGTH THEN
        timeCounter = 0
        dayNumber = dayNumber + 1
    END IF
    
    ' Compute a simple time-of-day factor (0 = midnight, 1 = noon)
    ' We use a sine wave to simulate gradual light change.
    tod = (SIN(3.1416 * timeCounter / (DAY_LENGTH/2)) + 1) / 2  ' 0..1
    
    ' Update road curve: oscillate road center slowly
    roadDX = 10 * SIN(0.02 * timeCounter)
    
    ' Draw sky: change its color based on time-of-day
    ' (Bright blue at noon, darker blue at night)
    skyColor = INT( 20 + 100 * tod )   ' adjust as needed (range: 20 to 120)
    FOR y = 0 TO 100
      LINE 0, y, 319, y, skyColor
    NEXT y

    ' Draw distant mountains as a simple filled polygon.
    ' They move a little with roadDX to simulate parallax.
    mx1 = 0 : my1 = 100
    mx2 = 320 : my2 = 100
    mx3 = 240 + roadDX/2 : my3 = 140
    mx4 = 80 + roadDX/2 : my4 = 140
    ' Use a darker color if it's night:
    mountainColor = INT(40 + 60 * tod)
    FILL (mx1, my1)-(mx2, my2)-(mx3, my3)-(mx4, my4), mountainColor

    ' Draw the road: use a trapezoid that narrows toward the horizon.
    ' The road center shifts horizontally based on roadDX.
    roadY1 = 100    ' horizon level
    roadY2 = 200    ' bottom of screen
    ' Calculate widths: road is wider at the bottom
    wTop = ROAD_WIDTH / 2
    wBot = ROAD_WIDTH
    roadCenterTop = 160 + roadDX/2
    roadCenterBot = 160 + roadDX
    ' Draw grass (left and right)
    grassColor1 = 2: grassColor2 = 20 ' alternate colors for effect
    ' Left grass:
    FOR y = roadY1 TO roadY2
      factor = (y - roadY1) / (roadY2 - roadY1)
      center = roadCenterTop * (1 - factor) + roadCenterBot * factor
      width = wTop * (1 - factor) + wBot * factor
      LINE 0, y, center - width, y, grassColor1
      LINE center + width, y, 319, y, grassColor2
    NEXT y

    ' Draw the road surface
    roadColor = 15 ' light grey for the road
    FOR y = roadY1 TO roadY2
      factor = (y - roadY1) / (roadY2 - roadY1)
      center = roadCenterTop * (1 - factor) + roadCenterBot * factor
      width = wTop * (1 - factor) + wBot * factor
      LINE center - width, y, center + width, y, roadColor
    NEXT y

    ' Draw road markings: a dashed white line in the center
    markColor = 7 ' white
    dashLength = 4
    FOR y = roadY1 TO roadY2 STEP dashLength*2
      factor = (y - roadY1) / (roadY2 - roadY1)
      center = roadCenterTop * (1 - factor) + roadCenterBot * factor
      LINE center, y, center, y + dashLength, markColor
    NEXT y

    ' Draw the player's car (a filled rectangle)
    ' The car remains fixed vertically, but its horizontal position is carX.
    carColor = 4 ' choose a color for the car
    carWidth = 20
    carHeight = 10
    ' Simple car: a rectangle centered on (carX, carY)
    RECTANGLE carX, carY, carX + carWidth, carY + carHeight, carColor, BF

    ' Update Score: For demonstration, increase score slowly (simulate passing cars)
    score = score + 1
    ' Draw Score and Day
    LOCATE 1, 5
    PRINT "Day:"; dayNumber; " Score:"; score

    ' Simulate car input: use INKEY$ to adjust carX based on input
    k$ = INKEY$
    IF k$ = "A" OR k$ = "a" OR k$ = CHR$(0) + "K" THEN
        carX = carX - PADDLE_SPEED
        IF carX < 0 THEN carX = 0
    END IF
    IF k$ = "D" OR k$ = "d" OR k$ = CHR$(0) + "M" THEN
        carX = carX + PADDLE_SPEED
        IF carX > 320 - carWidth THEN carX = 320 - carWidth
    END IF

    ' Optional: add a simple sun/moon that moves across the sky
    IF tod > 0.5 THEN
        ' Sun: when tod is high (noon)
        sunX = 50 + 250 * ((tod - 0.5) * 2)
        sunY = 40
        CIRCLE (sunX, sunY), SUN_RADIUS, 14
        PAINT (sunX, sunY), 14
    ELSE
        ' Moon: when tod is low (night)
        moonX = 50 + 250 * (tod * 2)
        moonY = 40
        CIRCLE (moonX, moonY), SUN_RADIUS, 7
        PAINT (moonX, moonY), 7
    END IF

    ' Brief delay to control game speed (approx. 20 FPS)
    _DELAY 0.05

LOOP

' End of program
