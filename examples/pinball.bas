' Pinball Game for PanicBASIC
' Controls: Z = Left Flipper, X or / = Right Flipper, Space = Launch Ball
SCREEN 13
RANDOMIZE TIMER

' Game Constants
CONST SCREEN_W = 320
CONST SCREEN_H = 200
CONST GRAVITY = 0.15
CONST BALL_RADIUS = 4
CONST FLIPPER_LENGTH = 30
CONST FLIPPER_WIDTH = 4
CONST BUMPER_RADIUS = 12
CONST BOUNCE_DAMPING = 0.85
CONST FLIPPER_POWER = 6

' Ball Variables
ball_x = 300
ball_y = 180
ball_vx = 0
ball_vy = 0
ball_launched = 0

' Flipper state (0 = down, 1 = up)
left_flipper = 0
right_flipper = 0

' Flipper positions
CONST LEFT_FLIP_X = 90
CONST LEFT_FLIP_Y = 175
CONST RIGHT_FLIP_X = 230
CONST RIGHT_FLIP_Y = 175

' Bumper positions (3 bumpers)
CONST BUMP1_X = 100
CONST BUMP1_Y = 60
CONST BUMP2_X = 160
CONST BUMP2_Y = 40
CONST BUMP3_X = 220
CONST BUMP3_Y = 60

' Additional bumpers
CONST BUMP4_X = 130
CONST BUMP4_Y = 100
CONST BUMP5_X = 190
CONST BUMP5_Y = 100

' Score
score = 0
high_score = 0
balls_left = 3

' Game state
game_over = 0

' Start/Restart point
start:
ball_x = 305
ball_y = 150
ball_vx = 0
ball_vy = 0
ball_launched = 0
game_over = 0

' Main Game Loop
DO
    CLS

    ' Handle Input
    k$ = INKEY$

    ' Flipper controls
    IF k$ = "z" OR k$ = "Z" THEN
        left_flipper = 1
    ELSE
        left_flipper = 0
    END IF

    IF k$ = "x" OR k$ = "X" OR k$ = "/" THEN
        right_flipper = 1
    ELSE
        right_flipper = 0
    END IF

    ' Launch ball with space
    IF k$ = " " AND ball_launched = 0 THEN
        ball_launched = 1
        ball_vy = -8 - RND * 2
        ball_vx = -2 - RND * 2
    END IF

    ' Physics update (only if ball is launched)
    IF ball_launched = 1 THEN
        ' Apply gravity
        ball_vy = ball_vy + GRAVITY

        ' Update position
        ball_x = ball_x + ball_vx
        ball_y = ball_y + ball_vy

        ' Wall collisions - Left wall
        IF ball_x < BALL_RADIUS + 10 THEN
            ball_x = BALL_RADIUS + 10
            ball_vx = -ball_vx * BOUNCE_DAMPING
        END IF

        ' Right wall
        IF ball_x > SCREEN_W - BALL_RADIUS - 10 THEN
            ball_x = SCREEN_W - BALL_RADIUS - 10
            ball_vx = -ball_vx * BOUNCE_DAMPING
        END IF

        ' Top wall
        IF ball_y < BALL_RADIUS + 5 THEN
            ball_y = BALL_RADIUS + 5
            ball_vy = -ball_vy * BOUNCE_DAMPING
        END IF

        ' Check bumper collisions
        GOSUB check_bumpers

        ' Check flipper collisions
        GOSUB check_flippers

        ' Ball lost (bottom)
        IF ball_y > SCREEN_H + 10 THEN
            balls_left = balls_left - 1
            IF balls_left <= 0 THEN
                game_over = 1
            ELSE
                ' Reset ball for next attempt
                ball_x = 305
                ball_y = 150
                ball_vx = 0
                ball_vy = 0
                ball_launched = 0
            END IF
        END IF
    END IF

    ' Draw the playfield
    GOSUB draw_playfield

    ' Draw bumpers
    GOSUB draw_bumpers

    ' Draw flippers
    GOSUB draw_flippers

    ' Draw ball
    IF ball_launched = 1 OR ball_y < 190 THEN
        CIRCLE (ball_x, ball_y), BALL_RADIUS, 15, , , , F
    ELSE
        ' Ball in launch tube
        CIRCLE (ball_x, ball_y), BALL_RADIUS, 15, , , , F
    END IF

    ' Draw UI
    LOCATE 1, 1
    PRINT "Score: "; score;
    LOCATE 1, 28
    PRINT "Balls: "; balls_left;

    ' High score
    IF score > high_score THEN
        high_score = score
    END IF

    _DELAY 0.016

    IF game_over = 1 THEN
        EXIT DO
    END IF
LOOP

' Game Over Screen
game_over_screen:
CLS
LOCATE 8, 12
PRINT "GAME OVER"
LOCATE 10, 10
PRINT "Final Score: "; score
LOCATE 12, 10
PRINT "High Score: "; high_score
LOCATE 15, 8
PRINT "Press SPACE to play again"

DO
    k$ = INKEY$
    IF k$ = " " THEN
        score = 0
        balls_left = 3
        GOTO start
    END IF
    _DELAY 0.016
LOOP
END

' === SUBROUTINES ===

' Draw the playfield walls and decorations
draw_playfield:
    ' Main border - outer walls
    LINE (5, 5)-(315, 5), 7       ' Top
    LINE (5, 5)-(5, 195), 7       ' Left
    LINE (315, 5)-(315, 195), 7   ' Right

    ' Angled walls near flippers
    LINE (5, 160)-(60, 185), 8    ' Left guide
    LINE (315, 160)-(260, 185), 8 ' Right guide

    ' Launch tube
    LINE (295, 120)-(295, 195), 6
    LINE (315, 120)-(315, 195), 6
    LINE (295, 120)-(315, 120), 6

    ' Some decorative lines
    LINE (40, 30)-(40, 80), 1
    LINE (280, 30)-(280, 80), 1

    ' Central triangle obstacle
    LINE (140, 130)-(180, 130), 5
    LINE (140, 130)-(160, 150), 5
    LINE (180, 130)-(160, 150), 5
RETURN

' Draw the bumpers
draw_bumpers:
    ' Main bumpers (red filled circles)
    CIRCLE (BUMP1_X, BUMP1_Y), BUMPER_RADIUS, 4, , , , F
    CIRCLE (BUMP1_X, BUMP1_Y), BUMPER_RADIUS, 12

    CIRCLE (BUMP2_X, BUMP2_Y), BUMPER_RADIUS, 4, , , , F
    CIRCLE (BUMP2_X, BUMP2_Y), BUMPER_RADIUS, 12

    CIRCLE (BUMP3_X, BUMP3_Y), BUMPER_RADIUS, 4, , , , F
    CIRCLE (BUMP3_X, BUMP3_Y), BUMPER_RADIUS, 12

    ' Secondary bumpers (yellow)
    CIRCLE (BUMP4_X, BUMP4_Y), 8, 14, , , , F
    CIRCLE (BUMP4_X, BUMP4_Y), 8, 6

    CIRCLE (BUMP5_X, BUMP5_Y), 8, 14, , , , F
    CIRCLE (BUMP5_X, BUMP5_Y), 8, 6
RETURN

' Draw the flippers
draw_flippers:
    ' Left flipper
    IF left_flipper = 1 THEN
        ' Flipper up
        LINE (LEFT_FLIP_X, LEFT_FLIP_Y)-(LEFT_FLIP_X + 25, LEFT_FLIP_Y - 12), 10
        LINE (LEFT_FLIP_X, LEFT_FLIP_Y + 2)-(LEFT_FLIP_X + 25, LEFT_FLIP_Y - 10), 10
        LINE (LEFT_FLIP_X, LEFT_FLIP_Y + 4)-(LEFT_FLIP_X + 25, LEFT_FLIP_Y - 8), 10
    ELSE
        ' Flipper down
        LINE (LEFT_FLIP_X, LEFT_FLIP_Y)-(LEFT_FLIP_X + 30, LEFT_FLIP_Y + 5), 2
        LINE (LEFT_FLIP_X, LEFT_FLIP_Y + 2)-(LEFT_FLIP_X + 30, LEFT_FLIP_Y + 7), 2
        LINE (LEFT_FLIP_X, LEFT_FLIP_Y + 4)-(LEFT_FLIP_X + 30, LEFT_FLIP_Y + 9), 2
    END IF

    ' Right flipper
    IF right_flipper = 1 THEN
        ' Flipper up
        LINE (RIGHT_FLIP_X, RIGHT_FLIP_Y)-(RIGHT_FLIP_X - 25, RIGHT_FLIP_Y - 12), 10
        LINE (RIGHT_FLIP_X, RIGHT_FLIP_Y + 2)-(RIGHT_FLIP_X - 25, RIGHT_FLIP_Y - 10), 10
        LINE (RIGHT_FLIP_X, RIGHT_FLIP_Y + 4)-(RIGHT_FLIP_X - 25, RIGHT_FLIP_Y - 8), 10
    ELSE
        ' Flipper down
        LINE (RIGHT_FLIP_X, RIGHT_FLIP_Y)-(RIGHT_FLIP_X - 30, RIGHT_FLIP_Y + 5), 2
        LINE (RIGHT_FLIP_X, RIGHT_FLIP_Y + 2)-(RIGHT_FLIP_X - 30, RIGHT_FLIP_Y + 7), 2
        LINE (RIGHT_FLIP_X, RIGHT_FLIP_Y + 4)-(RIGHT_FLIP_X - 30, RIGHT_FLIP_Y + 9), 2
    END IF

    ' Flipper pivots
    CIRCLE (LEFT_FLIP_X, LEFT_FLIP_Y + 2), 3, 7, , , , F
    CIRCLE (RIGHT_FLIP_X, RIGHT_FLIP_Y + 2), 3, 7, , , , F
RETURN

' Check bumper collisions
check_bumpers:
    ' Bumper 1
    dx = ball_x - BUMP1_X
    dy = ball_y - BUMP1_Y
    dist = SQR(dx * dx + dy * dy)
    IF dist < BALL_RADIUS + BUMPER_RADIUS THEN
        ' Bounce away from bumper
        IF dist > 0 THEN
            nx = dx / dist
            ny = dy / dist
            ball_vx = nx * 5
            ball_vy = ny * 5
            score = score + 100
        END IF
    END IF

    ' Bumper 2
    dx = ball_x - BUMP2_X
    dy = ball_y - BUMP2_Y
    dist = SQR(dx * dx + dy * dy)
    IF dist < BALL_RADIUS + BUMPER_RADIUS THEN
        IF dist > 0 THEN
            nx = dx / dist
            ny = dy / dist
            ball_vx = nx * 5
            ball_vy = ny * 5
            score = score + 100
        END IF
    END IF

    ' Bumper 3
    dx = ball_x - BUMP3_X
    dy = ball_y - BUMP3_Y
    dist = SQR(dx * dx + dy * dy)
    IF dist < BALL_RADIUS + BUMPER_RADIUS THEN
        IF dist > 0 THEN
            nx = dx / dist
            ny = dy / dist
            ball_vx = nx * 5
            ball_vy = ny * 5
            score = score + 100
        END IF
    END IF

    ' Bumper 4 (smaller)
    dx = ball_x - BUMP4_X
    dy = ball_y - BUMP4_Y
    dist = SQR(dx * dx + dy * dy)
    IF dist < BALL_RADIUS + 8 THEN
        IF dist > 0 THEN
            nx = dx / dist
            ny = dy / dist
            ball_vx = nx * 4
            ball_vy = ny * 4
            score = score + 50
        END IF
    END IF

    ' Bumper 5 (smaller)
    dx = ball_x - BUMP5_X
    dy = ball_y - BUMP5_Y
    dist = SQR(dx * dx + dy * dy)
    IF dist < BALL_RADIUS + 8 THEN
        IF dist > 0 THEN
            nx = dx / dist
            ny = dy / dist
            ball_vx = nx * 4
            ball_vy = ny * 4
            score = score + 50
        END IF
    END IF
RETURN

' Check flipper collisions
check_flippers:
    ' Left flipper collision zone
    IF ball_x > LEFT_FLIP_X - 5 AND ball_x < LEFT_FLIP_X + 35 THEN
        IF ball_y > LEFT_FLIP_Y - 10 AND ball_y < LEFT_FLIP_Y + 15 THEN
            IF left_flipper = 1 THEN
                ' Ball hit active flipper - launch it up and right
                ball_vy = -FLIPPER_POWER - 2
                ball_vx = 3 + RND * 2
                score = score + 10
            ELSE
                ' Ball hit resting flipper - gentle bounce
                IF ball_vy > 0 THEN
                    ball_vy = -ball_vy * 0.3
                    ball_vx = ball_vx + 1
                END IF
            END IF
        END IF
    END IF

    ' Right flipper collision zone
    IF ball_x > RIGHT_FLIP_X - 35 AND ball_x < RIGHT_FLIP_X + 5 THEN
        IF ball_y > RIGHT_FLIP_Y - 10 AND ball_y < RIGHT_FLIP_Y + 15 THEN
            IF right_flipper = 1 THEN
                ' Ball hit active flipper - launch it up and left
                ball_vy = -FLIPPER_POWER - 2
                ball_vx = -3 - RND * 2
                score = score + 10
            ELSE
                ' Ball hit resting flipper - gentle bounce
                IF ball_vy > 0 THEN
                    ball_vy = -ball_vy * 0.3
                    ball_vx = ball_vx - 1
                END IF
            END IF
        END IF
    END IF

    ' Center triangle collision
    IF ball_x > 135 AND ball_x < 185 THEN
        IF ball_y > 125 AND ball_y < 155 THEN
            ' Simple bounce off triangle
            ball_vy = -ABS(ball_vy) * 0.8
            IF ball_x < 160 THEN
                ball_vx = ball_vx - 2
            ELSE
                ball_vx = ball_vx + 2
            END IF
            score = score + 25
        END IF
    END IF

    ' Guide rail collisions
    ' Left guide (angled)
    IF ball_x < 65 AND ball_y > 155 THEN
        IF ball_y > 160 + (ball_x - 5) * 0.4 THEN
            ball_vx = ball_vx + 2
            ball_vy = -ABS(ball_vy) * 0.7
        END IF
    END IF

    ' Right guide (angled)
    IF ball_x > 255 AND ball_y > 155 THEN
        IF ball_y > 160 + (315 - ball_x) * 0.4 THEN
            ball_vx = ball_vx - 2
            ball_vy = -ABS(ball_vy) * 0.7
        END IF
    END IF
RETURN
