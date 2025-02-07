' Simple Infinite Runner
SCREEN 13
CLS

' Constants
CONST PLAYER_X = 20
CONST PLAYER_Y = 180
CONST PLAYER_SIZE = 10
CONST OBSTACLE_WIDTH = 10
CONST OBSTACLE_HEIGHT = 20
CONST FLOOR_HEIGHT = 190
CONST GAP_SIZE = 50
CONST JUMP_SPEED = 15
CONST GRAVITY = 1

' Variables
player_y_velocity = 0
obstacle_x = 320
obstacle_height = 50
score = 0
high_score = 0
is_jumping = 0

' Initialize the game
start:
player_y_velocity = 0
obstacle_x = 320
obstacle_height = 50
score = 0
is_jumping = 0
PLAYER_Y = 180

' Main Game Loop
DO

    CLS ' Clear screen

    ' Handle Input (Jump with Space)
    a$ = INKEY$
    IF a$ = " " THEN
        IF is_jumping = 0 THEN
            player_y_velocity = -JUMP_SPEED
            is_jumping = 1
        END IF
    END IF

    ' Update Player Position (Gravity and Jump)
    player_y_velocity = player_y_velocity + GRAVITY
    PLAYER_Y = PLAYER_Y + player_y_velocity

    'Floor collision
    IF PLAYER_Y > FLOOR_HEIGHT - PLAYER_SIZE THEN
        PLAYER_Y = FLOOR_HEIGHT - PLAYER_SIZE
        player_y_velocity = 0
        is_jumping = 0
    END IF


    ' Update Obstacle Position
    obstacle_x = obstacle_x - 5
    IF obstacle_x < -OBSTACLE_WIDTH THEN
        obstacle_x = 320
        obstacle_height = INT(RND * 80) + 20  ' Random obstacle height
        score = score + 1
    END IF

    ' Collision Detection
    IF PLAYER_X + PLAYER_SIZE > obstacle_x AND PLAYER_X < obstacle_x + OBSTACLE_WIDTH THEN
        IF PLAYER_Y + PLAYER_SIZE > FLOOR_HEIGHT - obstacle_height THEN
            GOTO game_over
        END IF
    END IF

    ' Draw Player (Square)
    LINE (PLAYER_X, PLAYER_Y)-(PLAYER_X + PLAYER_SIZE, PLAYER_Y + PLAYER_SIZE), 15, BF

    ' Draw Obstacle (Rectangle)
    LINE (obstacle_x, FLOOR_HEIGHT - obstacle_height)-(obstacle_x + OBSTACLE_WIDTH, FLOOR_HEIGHT), 12, BF

    ' Draw Floor (Line)
    LINE (0, FLOOR_HEIGHT)-(320, FLOOR_HEIGHT), 7

    ' Display Score
    LOCATE 1, 1
    PRINT "Score: "; score

    _DELAY 0.016

LOOP

game_over:
CLS
IF score > high_score THEN
    high_score = score
END IF

LOCATE 8, 10
PRINT "Game Over!"
LOCATE 10, 10
PRINT "Score: " ; score
LOCATE 12, 10
PRINT "High Score: " ; high_score
LOCATE 14, 10
PRINT "Press Space to Retry"

DO
    a$ = INKEY$
    IF a$ = " " THEN
        GOTO start
    END IF
LOOP
END