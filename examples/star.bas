' Catch the Star Game
SCREEN 13          ' Set 320x200 graphics mode
CLS

'-------------------------------
' Define constants and colors
'-------------------------------
CONST BASKET_WIDTH = 40
CONST BASKET_HEIGHT = 10
CONST BASKET_Y = 180          ' Vertical position of the basket
CONST STAR_SIZE = 4
CONST STAR_COLOR = 14         ' Yellowish color
CONST BASKET_COLOR = 2        ' Green
CONST BG_COLOR = 0

'-------------------------------
' Initialize game variables
'-------------------------------
RANDOMIZE TIMER
basketX = (320 - BASKET_WIDTH) / 2    ' Center the basket horizontally
starX = INT(RND * (320 - STAR_SIZE))    ' Random X for star
starY = 0                             ' Start star at the top
score = 0

'-------------------------------
' Main Game Loop
'-------------------------------
DO
    ' Check for player input
    a$ = INKEY$
    ' Move basket with A/D keys (or lowercase a/d)
    IF a$ = "A" OR a$ = "a" THEN
        basketX = basketX - 5
        IF basketX < 0 THEN basketX = 0
    END IF
    IF a$ = "D" OR a$ = "d" THEN
        basketX = basketX + 5
        IF basketX > 320 - BASKET_WIDTH THEN basketX = 320 - BASKET_WIDTH
    END IF
    ' Also allow use of left/right arrow keys:
    IF a$ = CHR$(0) + "K" THEN
        basketX = basketX - 5
        IF basketX < 0 THEN basketX = 0
    END IF
    IF a$ = CHR$(0) + "M" THEN
        basketX = basketX + 5
        IF basketX > 320 - BASKET_WIDTH THEN basketX = 320 - BASKET_WIDTH
    END IF

    ' Clear the screen for the new frame
    CLS

    ' Draw the basket as a filled rectangle
    LINE (basketX, BASKET_Y)-(basketX + BASKET_WIDTH, BASKET_Y + BASKET_HEIGHT), BASKET_COLOR, BF

    ' Draw the falling star as a small circle with fill
    CIRCLE (starX + STAR_SIZE/2, starY + STAR_SIZE/2), STAR_SIZE/2, STAR_COLOR
    PAINT (starX + STAR_SIZE/2, starY + STAR_SIZE/2), STAR_COLOR

    ' Display the current score at the top of the screen
    LOCATE 1, 10
    PRINT "Score: "; score

    ' Update the star’s vertical position (falling down)
    starY = starY + 3

    ' Check for collision between the star and the basket:
    IF starY + STAR_SIZE >= BASKET_Y THEN
        IF starX + STAR_SIZE >= basketX AND starX <= basketX + BASKET_WIDTH THEN
            score = score + 1
            ' Star caught! Reset it to the top at a new random horizontal position.
            starX = INT(RND * (320 - STAR_SIZE))
            starY = 0
        ELSE
            ' If the star falls below the screen, end the game.
            IF starY > 200 THEN EXIT DO
        END IF
    END IF

    ' Brief delay to control the game speed (approx. 20 FPS)
    _DELAY 0.05
LOOP

'-------------------------------
' Game Over Screen
'-------------------------------
CLS
LOCATE 10, 10
PRINT "Game Over! Your score is "; score
PRINT "Press any key to exit."
DO UNTIL INKEY$ <> "": LOOP
END

