' =====================================================
'    ANGRY AND FURIOUS BIRDS - ENHANCED EDITION
'    A clone of Angry Birds for PanicBasic
'    With animated title screen, sounds & music!
' =====================================================
SCREEN 13
RANDOMIZE TIMER

' Game Constants
CONST SCREEN_W = 320
CONST SCREEN_H = 200
CONST GRAVITY = 0.18
CONST GROUND_Y = 185
CONST SLING_X = 40
CONST SLING_Y = 150

' Bird properties
CONST BIRD_RADIUS = 5
bird_x = SLING_X
bird_y = SLING_Y
bird_vx = 0
bird_vy = 0
bird_flying = 0
bird_done = 0

' Aiming
aim_angle = 45
aim_power = 0
power_dir = 1
aiming = 1
setting_power = 0

' Game state
score = 0
high_score = 0
birds_left = 3
level = 1
game_over = 0
level_complete = 0
sound_on = 1

' Block arrays (max 15 blocks)
DIM block_x(15)
DIM block_y(15)
DIM block_w(15)
DIM block_h(15)
DIM block_alive(15)
DIM block_type(15)
DIM block_hits(15)
num_blocks = 0

' Pig arrays (max 5 pigs)
DIM pig_x(5)
DIM pig_y(5)
DIM pig_alive(5)
num_pigs = 0

' Debris particles (for destruction effect)
DIM debris_x(30)
DIM debris_y(30)
DIM debris_vx(30)
DIM debris_vy(30)
DIM debris_life(30)
DIM debris_color(30)
num_debris = 0

' Star particles for effects
DIM star_x(20)
DIM star_y(20)
DIM star_life(20)
num_stars = 0

' Cloud positions for background
DIM cloud_x(5)
DIM cloud_y(5)
FOR i = 0 TO 4
    cloud_x(i) = RND * SCREEN_W
    cloud_y(i) = 20 + RND * 40
NEXT i

' =====================================================
' TITLE SCREEN
' =====================================================
title_screen:
GOSUB play_title_music
GOSUB draw_title_screen

' Wait for input on title screen
menu_choice = 1
title_frame = 0
DO
    ' Animate title screen
    title_frame = title_frame + 1
    GOSUB animate_title

    k$ = INKEY$
    IF k$ = CHR$(0) + "H" THEN
        menu_choice = menu_choice - 1
        IF menu_choice < 1 THEN menu_choice = 3
        GOSUB play_menu_beep
    END IF
    IF k$ = CHR$(0) + "P" THEN
        menu_choice = menu_choice + 1
        IF menu_choice > 3 THEN menu_choice = 1
        GOSUB play_menu_beep
    END IF
    IF k$ = " " OR k$ = CHR$(13) THEN
        GOSUB play_select_sound
        IF menu_choice = 1 THEN
            EXIT DO
        ELSEIF menu_choice = 2 THEN
            GOSUB show_instructions
            GOSUB draw_title_screen
        ELSEIF menu_choice = 3 THEN
            CLS
            END
        END IF
    END IF
    IF k$ = CHR$(27) THEN
        CLS
        END
    END IF

    _DELAY 0.03
LOOP

' Initialize first level
GOSUB init_level

' =====================================================
' MAIN GAME LOOP
' =====================================================
main_loop:
DO
    CLS

    ' Move clouds
    GOSUB update_clouds

    ' Handle input
    k$ = INKEY$

    IF bird_flying = 0 AND bird_done = 0 THEN
        ' Aiming phase
        IF aiming = 1 THEN
            IF k$ = CHR$(0) + "H" THEN
                aim_angle = aim_angle + 2
                IF aim_angle > 80 THEN aim_angle = 80
            END IF
            IF k$ = CHR$(0) + "P" THEN
                aim_angle = aim_angle - 2
                IF aim_angle < 10 THEN aim_angle = 10
            END IF
            IF k$ = " " THEN
                aiming = 0
                setting_power = 1
                aim_power = 0
                power_dir = 1
            END IF
        ELSEIF setting_power = 1 THEN
            ' Power meter animation
            aim_power = aim_power + power_dir * 3
            IF aim_power >= 100 THEN
                power_dir = -1
                aim_power = 100
            END IF
            IF aim_power <= 0 THEN
                power_dir = 1
                aim_power = 0
            END IF

            IF k$ = " " THEN
                ' Launch the bird!
                setting_power = 0
                bird_flying = 1
                power_factor = aim_power / 100
                rad = aim_angle * 3.14159 / 180
                bird_vx = COS(rad) * (5 + power_factor * 7)
                bird_vy = -SIN(rad) * (5 + power_factor * 7)
                GOSUB play_launch_sound
            END IF
        END IF
    END IF

    ' Update bird physics
    IF bird_flying = 1 THEN
        bird_vy = bird_vy + GRAVITY
        bird_x = bird_x + bird_vx
        bird_y = bird_y + bird_vy

        ' Check collision with blocks
        GOSUB check_block_collision

        ' Check collision with pigs
        GOSUB check_pig_collision

        ' Ground collision
        IF bird_y > GROUND_Y THEN
            bird_y = GROUND_Y
            bird_flying = 0
            bird_done = 1
            GOSUB play_thud_sound
        END IF

        ' Off screen
        IF bird_x > SCREEN_W + 20 OR bird_x < -20 THEN
            bird_flying = 0
            bird_done = 1
        END IF
    END IF

    ' Update debris particles
    GOSUB update_debris

    ' Update star particles
    GOSUB update_stars

    ' Check if bird turn is over
    IF bird_done = 1 THEN
        ' Wait a moment then reset
        _DELAY 0.5

        ' Check for level complete
        pigs_remaining = 0
        FOR i = 0 TO num_pigs - 1
            IF pig_alive(i) = 1 THEN pigs_remaining = pigs_remaining + 1
        NEXT i

        IF pigs_remaining = 0 THEN
            level_complete = 1
        ELSE
            birds_left = birds_left - 1
            IF birds_left <= 0 THEN
                game_over = 1
            ELSE
                ' Reset bird for next shot
                bird_x = SLING_X
                bird_y = SLING_Y
                bird_vx = 0
                bird_vy = 0
                bird_flying = 0
                bird_done = 0
                aiming = 1
                setting_power = 0
                aim_angle = 45
            END IF
        END IF
    END IF

    ' Draw everything
    GOSUB draw_scene

    ' Draw UI
    GOSUB draw_ui

    _DELAY 0.02

    ' Check for quit
    IF k$ = CHR$(27) THEN
        GOSUB show_pause_menu
        IF pause_quit = 1 THEN
            game_over = 1
        END IF
    END IF

    ' Level complete?
    IF level_complete = 1 THEN
        GOSUB play_victory_music
        GOSUB show_level_complete
        level = level + 1
        IF level > 5 THEN
            GOSUB show_victory
            GOTO title_screen
        END IF
        birds_left = 3 + level - 1
        score = score + birds_left * 500
        GOSUB init_level
        level_complete = 0
    END IF

    ' Game over?
    IF game_over = 1 THEN
        EXIT DO
    END IF
LOOP

' Game Over Screen
GOSUB play_gameover_music
GOSUB show_game_over
GOTO title_screen

' =====================================================
' TITLE SCREEN SUBROUTINES
' =====================================================

draw_title_screen:
    CLS

    ' Sky gradient
    FOR y = 0 TO 100
        c = 1
        IF y > 30 THEN c = 9
        IF y > 60 THEN c = 11
        LINE (0, y)-(SCREEN_W, y), c
    NEXT y

    ' Ground
    LINE (0, 100)-(SCREEN_W, SCREEN_H), 6, BF
    LINE (0, 100)-(SCREEN_W, 100), 2

    ' Draw title text with shadow
    LOCATE 3, 6
    COLOR 0
    PRINT "ANGRY AND FURIOUS BIRDS"
    LOCATE 2, 5
    COLOR 4
    PRINT "ANGRY AND FURIOUS BIRDS"

    ' Draw subtitle
    LOCATE 5, 10
    COLOR 14
    PRINT "- Enhanced Edition -"

    ' Draw decorative birds on title
    GOSUB draw_title_birds

    ' Draw menu options
    LOCATE 12, 14
    IF menu_choice = 1 THEN COLOR 15 ELSE COLOR 7
    PRINT "> START GAME <"

    LOCATE 14, 13
    IF menu_choice = 2 THEN COLOR 15 ELSE COLOR 7
    PRINT "> HOW TO PLAY <"

    LOCATE 16, 16
    IF menu_choice = 3 THEN COLOR 15 ELSE COLOR 7
    PRINT "> EXIT <"

    ' Draw high score
    LOCATE 20, 10
    COLOR 14
    PRINT "HIGH SCORE: "; high_score

    ' Controls hint
    LOCATE 23, 5
    COLOR 8
    PRINT "Use UP/DOWN to select, SPACE to confirm"

    COLOR 15
RETURN

draw_title_birds:
    ' Angry bird on left
    CIRCLE (60, 75), 15, 4, , , , F
    CIRCLE (60, 75), 15, 12
    CIRCLE (65, 70), 5, 15, , , , F
    PSET (66, 70), 0
    LINE (55, 65)-(70, 68), 0
    LINE (75, 72)-(85, 75), 14
    LINE (75, 78)-(85, 75), 14
    ' Feathers
    LINE (50, 60)-(55, 55), 4
    LINE (55, 58)-(60, 52), 4
    LINE (60, 58)-(65, 54), 4

    ' Green pig on right
    CIRCLE (260, 80), 18, 10, , , , F
    CIRCLE (260, 80), 18, 2
    ' Snout
    CIRCLE (272, 85), 8, 10, , , , F
    CIRCLE (272, 85), 8, 2
    PSET (270, 83), 2
    PSET (274, 87), 2
    ' Eyes
    CIRCLE (252, 73), 5, 15, , , , F
    CIRCLE (265, 73), 5, 15, , , , F
    PSET (253, 73), 0
    PSET (266, 73), 0
    ' Crown
    LINE (245, 62)-(275, 62), 14
    LINE (245, 62)-(248, 55), 14
    LINE (260, 62)-(260, 52), 14
    LINE (275, 62)-(272, 55), 14
RETURN

animate_title:
    ' Animate floating effect on title characters
    yoff = SIN(title_frame / 10) * 3

    ' Redraw menu selection indicator with animation
    pulse = ABS(SIN(title_frame / 8)) * 2

    ' Small animated bird flying across
    wrap_width = SCREEN_W + 40
    bx = (title_frame * 2) MOD wrap_width - 20
    by = 25 + SIN(title_frame / 5) * 5

    ' Draw mini flying bird
    CIRCLE (bx, by), 4, 4, , , , F
    LINE (bx - 5, by)-(bx - 8, by - 2), 4
    LINE (bx - 5, by)-(bx - 8, by + 2), 4

    ' Redraw menu with current selection
    LOCATE 12, 14
    IF menu_choice = 1 THEN COLOR 15 ELSE COLOR 7
    PRINT "> START GAME <"

    LOCATE 14, 13
    IF menu_choice = 2 THEN COLOR 15 ELSE COLOR 7
    PRINT "> HOW TO PLAY <"

    LOCATE 16, 16
    IF menu_choice = 3 THEN COLOR 15 ELSE COLOR 7
    PRINT "> EXIT <"

    COLOR 15
RETURN

show_instructions:
    CLS
    LINE (20, 15)-(300, 185), 1, BF
    LINE (20, 15)-(300, 185), 9

    LOCATE 3, 13
    COLOR 14
    PRINT "HOW TO PLAY"

    COLOR 15
    LOCATE 5, 4
    PRINT "OBJECTIVE:"
    COLOR 7
    LOCATE 6, 4
    PRINT "Destroy all the green pigs by"
    LOCATE 7, 4
    PRINT "launching birds at their structures!"

    COLOR 15
    LOCATE 9, 4
    PRINT "CONTROLS:"
    COLOR 7
    LOCATE 10, 4
    PRINT "UP/DOWN - Adjust aim angle"
    LOCATE 11, 4
    PRINT "SPACE   - Start power meter"
    LOCATE 12, 4
    PRINT "SPACE   - Launch bird (while charging)"
    LOCATE 13, 4
    PRINT "ESC     - Pause menu"

    COLOR 15
    LOCATE 15, 4
    PRINT "SCORING:"
    COLOR 7
    LOCATE 16, 4
    PRINT "Wood Block: 50 pts  Stone: 100 pts"
    LOCATE 17, 4
    PRINT "Pig: 500 pts  Bonus per bird left"

    COLOR 15
    LOCATE 19, 4
    PRINT "TIPS:"
    COLOR 7
    LOCATE 20, 4
    PRINT "- Aim for weak points in structures"
    LOCATE 21, 4
    PRINT "- Falling blocks can crush pigs!"

    LOCATE 23, 10
    COLOR 8
    PRINT "Press SPACE to return"

    DO
        k$ = INKEY$
        _DELAY 0.016
    LOOP UNTIL k$ = " " OR k$ = CHR$(27)
    COLOR 15
RETURN

' =====================================================
' SOUND SUBROUTINES
' =====================================================

play_title_music:
    IF sound_on = 0 THEN RETURN
    ' Heroic fanfare
    PLAY "T150O4L8CEGL4>CL8<BAGL2G"
RETURN

play_menu_beep:
    IF sound_on = 0 THEN RETURN
    SOUND 600, 1
RETURN

play_select_sound:
    IF sound_on = 0 THEN RETURN
    PLAY "T200O5L16CEG"
RETURN

play_launch_sound:
    IF sound_on = 0 THEN RETURN
    ' Whoosh sound - descending then ascending
    SOUND 800, 1
    SOUND 600, 1
    SOUND 400, 1
    SOUND 500, 1
RETURN

play_block_hit_sound:
    IF sound_on = 0 THEN RETURN
    ' Crash sound
    SOUND 200, 1
    SOUND 150, 1
RETURN

play_pig_death_sound:
    IF sound_on = 0 THEN RETURN
    ' Squeal and pop
    PLAY "T200O5L32EFGAGFEDCL16C"
    SOUND 100, 1
RETURN

play_thud_sound:
    IF sound_on = 0 THEN RETURN
    SOUND 80, 2
RETURN

play_victory_music:
    IF sound_on = 0 THEN RETURN
    ' Victory fanfare
    PLAY "T180O4L8CCL4EL8EL4GL2>C"
    PLAY "T180O4L8GL4>CL8<BL4>CL8DL2E"
RETURN

play_gameover_music:
    IF sound_on = 0 THEN RETURN
    ' Sad trombone
    PLAY "T100O3L4BAG#L1G"
RETURN

play_level_start:
    IF sound_on = 0 THEN RETURN
    PLAY "T150O4L16CEGCE>C"
RETURN

' =====================================================
' LEVEL INITIALIZATION
' =====================================================

init_level:
    bird_x = SLING_X
    bird_y = SLING_Y
    bird_vx = 0
    bird_vy = 0
    bird_flying = 0
    bird_done = 0
    aiming = 1
    setting_power = 0
    aim_angle = 45
    num_debris = 0
    num_stars = 0

    GOSUB play_level_start

    IF level = 1 THEN
        GOSUB create_level_1
    ELSEIF level = 2 THEN
        GOSUB create_level_2
    ELSEIF level = 3 THEN
        GOSUB create_level_3
    ELSEIF level = 4 THEN
        GOSUB create_level_4
    ELSE
        GOSUB create_level_5
    END IF
RETURN

' Level 1 - Tutorial: Simple tower
create_level_1:
    num_blocks = 0
    num_pigs = 0

    ' Ground blocks (wood)
    block_x(0) = 200: block_y(0) = 175: block_w(0) = 20: block_h(0) = 10
    block_alive(0) = 1: block_type(0) = 1: block_hits(0) = 1

    block_x(1) = 230: block_y(1) = 175: block_w(1) = 20: block_h(1) = 10
    block_alive(1) = 1: block_type(1) = 1: block_hits(1) = 1

    ' Vertical supports
    block_x(2) = 200: block_y(2) = 150: block_w(2) = 8: block_h(2) = 25
    block_alive(2) = 1: block_type(2) = 1: block_hits(2) = 1

    block_x(3) = 242: block_y(3) = 150: block_w(3) = 8: block_h(3) = 25
    block_alive(3) = 1: block_type(3) = 1: block_hits(3) = 1

    ' Roof
    block_x(4) = 195: block_y(4) = 140: block_w(4) = 60: block_h(4) = 8
    block_alive(4) = 1: block_type(4) = 1: block_hits(4) = 1

    num_blocks = 5

    ' One pig
    pig_x(0) = 225: pig_y(0) = 168: pig_alive(0) = 1
    num_pigs = 1
RETURN

' Level 2 - Two towers
create_level_2:
    num_blocks = 0
    num_pigs = 0

    ' First tower
    block_x(0) = 160: block_y(0) = 175: block_w(0) = 18: block_h(0) = 10
    block_alive(0) = 1: block_type(0) = 1: block_hits(0) = 1

    block_x(1) = 160: block_y(1) = 150: block_w(1) = 8: block_h(1) = 25
    block_alive(1) = 1: block_type(1) = 2: block_hits(1) = 2

    block_x(2) = 155: block_y(2) = 138: block_w(2) = 25: block_h(2) = 8
    block_alive(2) = 1: block_type(2) = 1: block_hits(2) = 1

    ' Second tower
    block_x(3) = 250: block_y(3) = 175: block_w(3) = 18: block_h(3) = 10
    block_alive(3) = 1: block_type(3) = 1: block_hits(3) = 1

    block_x(4) = 250: block_y(4) = 150: block_w(4) = 8: block_h(4) = 25
    block_alive(4) = 1: block_type(4) = 2: block_hits(4) = 2

    block_x(5) = 245: block_y(5) = 138: block_w(5) = 25: block_h(5) = 8
    block_alive(5) = 1: block_type(5) = 1: block_hits(5) = 1

    ' Bridge
    block_x(6) = 178: block_y(6) = 128: block_w(6) = 70: block_h(6) = 6
    block_alive(6) = 1: block_type(6) = 1: block_hits(6) = 1

    num_blocks = 7

    ' Two pigs
    pig_x(0) = 168: pig_y(0) = 168: pig_alive(0) = 1
    pig_x(1) = 258: pig_y(1) = 168: pig_alive(1) = 1
    num_pigs = 2
RETURN

' Level 3 - Fortress
create_level_3:
    num_blocks = 0
    num_pigs = 0

    ' Base - 4 stone blocks
    block_x(0) = 150: block_y(0) = 175: block_w(0) = 25: block_h(0) = 10
    block_alive(0) = 1: block_type(0) = 2: block_hits(0) = 2

    block_x(1) = 185: block_y(1) = 175: block_w(1) = 25: block_h(1) = 10
    block_alive(1) = 1: block_type(1) = 2: block_hits(1) = 2

    block_x(2) = 220: block_y(2) = 175: block_w(2) = 25: block_h(2) = 10
    block_alive(2) = 1: block_type(2) = 2: block_hits(2) = 2

    block_x(3) = 255: block_y(3) = 175: block_w(3) = 25: block_h(3) = 10
    block_alive(3) = 1: block_type(3) = 2: block_hits(3) = 2

    ' Pillars
    block_x(4) = 155: block_y(4) = 145: block_w(4) = 8: block_h(4) = 30
    block_alive(4) = 1: block_type(4) = 1: block_hits(4) = 1

    block_x(5) = 200: block_y(5) = 145: block_w(5) = 8: block_h(5) = 30
    block_alive(5) = 1: block_type(5) = 1: block_hits(5) = 1

    block_x(6) = 245: block_y(6) = 145: block_w(6) = 8: block_h(6) = 30
    block_alive(6) = 1: block_type(6) = 1: block_hits(6) = 1

    ' Upper platform
    block_x(7) = 150: block_y(7) = 130: block_w(7) = 60: block_h(7) = 8
    block_alive(7) = 1: block_type(7) = 2: block_hits(7) = 2

    block_x(8) = 210: block_y(8) = 130: block_w(8) = 60: block_h(8) = 8
    block_alive(8) = 1: block_type(8) = 2: block_hits(8) = 2

    ' Top structure
    block_x(9) = 180: block_y(9) = 110: block_w(9) = 8: block_h(9) = 20
    block_alive(9) = 1: block_type(9) = 1: block_hits(9) = 1

    block_x(10) = 235: block_y(10) = 110: block_w(10) = 8: block_h(10) = 20
    block_alive(10) = 1: block_type(10) = 1: block_hits(10) = 1

    block_x(11) = 175: block_y(11) = 98: block_w(11) = 75: block_h(11) = 8
    block_alive(11) = 1: block_type(11) = 1: block_hits(11) = 1

    num_blocks = 12

    ' Three pigs
    pig_x(0) = 175: pig_y(0) = 168: pig_alive(0) = 1
    pig_x(1) = 235: pig_y(1) = 168: pig_alive(1) = 1
    pig_x(2) = 210: pig_y(2) = 120: pig_alive(2) = 1
    num_pigs = 3
RETURN

' Level 4 - The Wall
create_level_4:
    num_blocks = 0
    num_pigs = 0

    ' Stone wall
    FOR row = 0 TO 3
        FOR col = 0 TO 2
            idx = row * 3 + col
            block_x(idx) = 200 + col * 25
            block_y(idx) = 175 - row * 20
            block_w(idx) = 22
            block_h(idx) = 18
            block_alive(idx) = 1
            block_type(idx) = 2
            block_hits(idx) = 2
        NEXT col
    NEXT row
    num_blocks = 12

    ' Pigs behind wall
    pig_x(0) = 290: pig_y(0) = 168: pig_alive(0) = 1
    pig_x(1) = 290: pig_y(1) = 140: pig_alive(1) = 1
    pig_x(2) = 290: pig_y(2) = 112: pig_alive(2) = 1
    num_pigs = 3
RETURN

' Level 5 - Final Challenge
create_level_5:
    num_blocks = 0
    num_pigs = 0

    ' Complex structure
    ' Base platform
    block_x(0) = 140: block_y(0) = 175: block_w(0) = 140: block_h(0) = 10
    block_alive(0) = 1: block_type(0) = 2: block_hits(0) = 3

    ' Left tower
    block_x(1) = 145: block_y(1) = 140: block_w(1) = 8: block_h(1) = 35
    block_alive(1) = 1: block_type(1) = 2: block_hits(1) = 2

    block_x(2) = 140: block_y(2) = 125: block_w(2) = 30: block_h(2) = 8
    block_alive(2) = 1: block_type(2) = 1: block_hits(2) = 1

    ' Right tower
    block_x(3) = 265: block_y(3) = 140: block_w(3) = 8: block_h(3) = 35
    block_alive(3) = 1: block_type(3) = 2: block_hits(3) = 2

    block_x(4) = 250: block_y(4) = 125: block_w(4) = 30: block_h(4) = 8
    block_alive(4) = 1: block_type(4) = 1: block_hits(4) = 1

    ' Center structure
    block_x(5) = 180: block_y(5) = 155: block_w(5) = 60: block_h(5) = 20
    block_alive(5) = 1: block_type(5) = 2: block_hits(5) = 2

    block_x(6) = 190: block_y(6) = 130: block_w(6) = 8: block_h(6) = 25
    block_alive(6) = 1: block_type(6) = 1: block_hits(6) = 1

    block_x(7) = 222: block_y(7) = 130: block_w(7) = 8: block_h(7) = 25
    block_alive(7) = 1: block_type(7) = 1: block_hits(7) = 1

    block_x(8) = 185: block_y(8) = 115: block_w(8) = 50: block_h(8) = 10
    block_alive(8) = 1: block_type(8) = 2: block_hits(8) = 2

    ' Top tower
    block_x(9) = 200: block_y(9) = 90: block_w(9) = 8: block_h(9) = 25
    block_alive(9) = 1: block_type(9) = 1: block_hits(9) = 1

    block_x(10) = 212: block_y(10) = 90: block_w(10) = 8: block_h(10) = 25
    block_alive(10) = 1: block_type(10) = 1: block_hits(10) = 1

    block_x(11) = 195: block_y(11) = 78: block_w(11) = 30: block_h(11) = 8
    block_alive(11) = 1: block_type(11) = 1: block_hits(11) = 1

    num_blocks = 12

    ' Four pigs - the king and guards
    pig_x(0) = 155: pig_y(0) = 168: pig_alive(0) = 1
    pig_x(1) = 265: pig_y(1) = 168: pig_alive(1) = 1
    pig_x(2) = 210: pig_y(2) = 145: pig_alive(2) = 1
    pig_x(3) = 210: pig_y(3) = 100: pig_alive(3) = 1
    num_pigs = 4
RETURN

' =====================================================
' UPDATE SUBROUTINES
' =====================================================

update_clouds:
    FOR i = 0 TO 4
        cloud_x(i) = cloud_x(i) + 0.2
        IF cloud_x(i) > SCREEN_W + 30 THEN
            cloud_x(i) = -30
            cloud_y(i) = 15 + RND * 50
        END IF
    NEXT i
RETURN

update_debris:
    FOR i = 0 TO num_debris - 1
        IF debris_life(i) > 0 THEN
            debris_vy(i) = debris_vy(i) + GRAVITY
            debris_x(i) = debris_x(i) + debris_vx(i)
            debris_y(i) = debris_y(i) + debris_vy(i)
            debris_life(i) = debris_life(i) - 1

            IF debris_y(i) > GROUND_Y THEN
                debris_life(i) = 0
            END IF
        END IF
    NEXT i
RETURN

update_stars:
    FOR i = 0 TO num_stars - 1
        IF star_life(i) > 0 THEN
            star_y(i) = star_y(i) - 1
            star_life(i) = star_life(i) - 1
        END IF
    NEXT i
RETURN

' =====================================================
' DRAWING SUBROUTINES
' =====================================================

draw_scene:
    ' Draw sky gradient
    LINE (0, 0)-(SCREEN_W, 40), 1, BF
    LINE (0, 40)-(SCREEN_W, 80), 9, BF
    LINE (0, 80)-(SCREEN_W, GROUND_Y), 11, BF

    ' Draw clouds
    FOR i = 0 TO 4
        cx = cloud_x(i)
        cy = cloud_y(i)
        CIRCLE (cx, cy), 12, 15, , , , F
        CIRCLE (cx + 15, cy + 3), 10, 15, , , , F
        CIRCLE (cx - 12, cy + 2), 8, 15, , , , F
        CIRCLE (cx + 5, cy - 5), 8, 15, , , , F
    NEXT i

    ' Draw hills in background
    CIRCLE (280, GROUND_Y + 30), 50, 2, , , 0.5, F
    CIRCLE (50, GROUND_Y + 40), 60, 2, , , 0.5, F
    CIRCLE (160, GROUND_Y + 35), 45, 2, , , 0.5, F

    ' Draw ground
    LINE (0, GROUND_Y)-(SCREEN_W, SCREEN_H), 6, BF
    LINE (0, GROUND_Y)-(SCREEN_W, GROUND_Y), 2

    ' Draw grass tufts
    FOR i = 0 TO 20
        gx = i * 16 + 3
        LINE (gx, GROUND_Y)-(gx - 2, GROUND_Y - 4), 2
        LINE (gx, GROUND_Y)-(gx, GROUND_Y - 5), 10
        LINE (gx, GROUND_Y)-(gx + 2, GROUND_Y - 4), 2
    NEXT i

    ' Draw slingshot with better detail
    ' Base
    LINE (SLING_X - 3, GROUND_Y)-(SLING_X + 3, GROUND_Y - 10), 6, BF

    ' Fork posts
    LINE (SLING_X - 10, GROUND_Y - 5)-(SLING_X - 6, SLING_Y - 25), 6
    LINE (SLING_X + 10, GROUND_Y - 5)-(SLING_X + 6, SLING_Y - 25), 6

    ' Fork tips
    LINE (SLING_X - 6, SLING_Y - 25)-(SLING_X - 10, SLING_Y - 32), 20
    LINE (SLING_X + 6, SLING_Y - 25)-(SLING_X + 10, SLING_Y - 32), 20

    ' Draw rubber band if aiming
    IF bird_flying = 0 AND bird_done = 0 THEN
        ' Back rubber band (behind bird)
        LINE (SLING_X + 10, SLING_Y - 32)-(bird_x, bird_y), 4

        ' Draw bird first
        GOSUB draw_bird_at_sling

        ' Front rubber band
        LINE (SLING_X - 10, SLING_Y - 32)-(bird_x, bird_y), 4

        ' Draw aim trajectory preview
        IF aiming = 1 OR setting_power = 1 THEN
            GOSUB draw_trajectory
        END IF
    END IF

    ' Draw blocks
    FOR i = 0 TO num_blocks - 1
        IF block_alive(i) = 1 THEN
            GOSUB draw_block
        END IF
    NEXT i

    ' Draw pigs
    FOR i = 0 TO num_pigs - 1
        IF pig_alive(i) = 1 THEN
            GOSUB draw_pig
        END IF
    NEXT i

    ' Draw debris particles
    FOR i = 0 TO num_debris - 1
        IF debris_life(i) > 0 THEN
            PSET (debris_x(i), debris_y(i)), debris_color(i)
            PSET (debris_x(i) + 1, debris_y(i)), debris_color(i)
        END IF
    NEXT i

    ' Draw star particles
    FOR i = 0 TO num_stars - 1
        IF star_life(i) > 0 THEN
            c = 14
            IF star_life(i) < 10 THEN c = 6
            PSET (star_x(i), star_y(i)), c
            PSET (star_x(i) - 1, star_y(i)), c
            PSET (star_x(i) + 1, star_y(i)), c
            PSET (star_x(i), star_y(i) - 1), c
            PSET (star_x(i), star_y(i) + 1), c
        END IF
    NEXT i

    ' Draw flying bird
    IF bird_flying = 1 THEN
        GOSUB draw_flying_bird
    END IF
RETURN

draw_bird_at_sling:
    bx = bird_x
    by = bird_y

    ' Bird body (red)
    CIRCLE (bx, by), BIRD_RADIUS, 4, , , , F
    CIRCLE (bx, by), BIRD_RADIUS, 12

    ' Belly highlight
    CIRCLE (bx - 1, by + 2), 2, 12, , , , F

    ' Eye
    CIRCLE (bx + 2, by - 1), 2, 15, , , , F
    PSET (bx + 2, by - 1), 0

    ' Beak
    LINE (bx + 4, by)-(bx + 9, by + 1), 14
    LINE (bx + 4, by + 2)-(bx + 9, by + 1), 6

    ' Angry eyebrow
    LINE (bx - 2, by - 4)-(bx + 4, by - 2), 0

    ' Tail feathers
    LINE (bx - 5, by - 2)-(bx - 9, by - 5), 4
    LINE (bx - 5, by)-(bx - 10, by - 2), 4
    LINE (bx - 5, by + 2)-(bx - 9, by + 1), 4
RETURN

draw_flying_bird:
    bx = bird_x
    by = bird_y

    ' Bird body (red)
    CIRCLE (bx, by), BIRD_RADIUS, 4, , , , F
    CIRCLE (bx, by), BIRD_RADIUS, 12

    ' Calculate rotation based on velocity
    IF bird_vx <> 0 THEN
        rot = ATN(bird_vy / bird_vx)
    ELSE
        rot = 0
    END IF

    ' Eye (rotated forward)
    ex = bx + COS(rot) * 2
    ey = by + SIN(rot) * 2 - 1
    CIRCLE (ex, ey), 2, 15, , , , F
    PSET (ex, ey), 0

    ' Beak
    bkx = bx + COS(rot) * 6
    bky = by + SIN(rot) * 6
    LINE (bx + 3, by)-(bkx, bky), 14

    ' Tail feathers (opposite direction of movement)
    tx = bx - COS(rot) * 7
    ty = by - SIN(rot) * 7
    LINE (bx - 4, by - 1)-(tx, ty - 3), 4
    LINE (bx - 4, by)-(tx - 2, ty), 4
    LINE (bx - 4, by + 1)-(tx, ty + 3), 4
RETURN

draw_trajectory:
    rad = aim_angle * 3.14159 / 180
    IF setting_power = 1 THEN
        pf = aim_power / 100
    ELSE
        pf = 0.5
    END IF

    tx = SLING_X
    ty = SLING_Y
    tvx = COS(rad) * (5 + pf * 7)
    tvy = -SIN(rad) * (5 + pf * 7)

    FOR t = 1 TO 30
        tx = tx + tvx
        ty = ty + tvy
        tvy = tvy + GRAVITY

        IF ty < GROUND_Y AND tx < SCREEN_W AND tx > 0 THEN
            IF t MOD 3 = 0 THEN
                CIRCLE (tx, ty), 1, 15
            END IF
        END IF
    NEXT t
RETURN

draw_block:
    bx = block_x(i)
    by = block_y(i)
    bw = block_w(i)
    bh = block_h(i)

    IF block_type(i) = 1 THEN
        ' Wood block (brown with grain)
        LINE (bx, by)-(bx + bw, by + bh), 6, BF
        LINE (bx, by)-(bx + bw, by + bh), 20

        ' Wood grain lines
        FOR g = 2 TO bh - 2 STEP 4
            LINE (bx + 1, by + g)-(bx + bw - 1, by + g), 20
        NEXT g

        ' Damage cracks if hit
        IF block_hits(i) < 1 THEN
            LINE (bx + bw / 2, by)-(bx + bw / 3, by + bh), 0
        END IF
    ELSE
        ' Stone block (gray with texture)
        LINE (bx, by)-(bx + bw, by + bh), 8, BF
        LINE (bx, by)-(bx + bw, by + bh), 7

        ' Stone texture
        PSET (bx + 3, by + 3), 7
        PSET (bx + bw - 4, by + bh - 4), 7
        PSET (bx + bw / 2, by + bh / 2), 23

        ' Damage cracks
        IF block_hits(i) < 2 THEN
            LINE (bx + 2, by + 2)-(bx + bw - 2, by + bh - 2), 0
        END IF
    END IF
RETURN

draw_pig:
    px = pig_x(i)
    py = pig_y(i)

    ' Pig body (green)
    CIRCLE (px, py), 10, 10, , , , F
    CIRCLE (px, py), 10, 2

    ' Ears
    CIRCLE (px - 7, py - 7), 4, 10, , , , F
    CIRCLE (px + 7, py - 7), 4, 10, , , , F
    CIRCLE (px - 7, py - 7), 4, 2
    CIRCLE (px + 7, py - 7), 4, 2

    ' Snout
    CIRCLE (px + 6, py + 2), 5, 10, , , , F
    CIRCLE (px + 6, py + 2), 5, 2
    ' Nostrils
    CIRCLE (px + 5, py + 1), 1, 2, , , , F
    CIRCLE (px + 8, py + 3), 1, 2, , , , F

    ' Eyes
    CIRCLE (px - 3, py - 3), 3, 15, , , , F
    CIRCLE (px + 2, py - 3), 3, 15, , , , F
    ' Pupils
    PSET (px - 3, py - 3), 0
    PSET (px + 2, py - 3), 0

    ' Eyebrows (worried look)
    LINE (px - 6, py - 7)-(px - 1, py - 5), 2
    LINE (px + 5, py - 7)-(px, py - 5), 2
RETURN

draw_ui:
    ' Semi-transparent UI bar at top
    LINE (0, 0)-(SCREEN_W, 12), 0, BF

    ' Score
    LOCATE 1, 1
    COLOR 15
    PRINT "SCORE:"; score;

    ' Birds left (draw small bird icons)
    LOCATE 1, 17
    PRINT "x"; birds_left;

    ' Level
    LOCATE 1, 32
    PRINT "LVL"; level;

    ' Power meter
    IF setting_power = 1 THEN
        ' Power bar background
        LINE (5, 20)-(15, 80), 0, BF
        LINE (5, 20)-(15, 80), 7

        ' Power bar fill
        bar_height = aim_power * 0.6
        IF bar_height > 0 THEN
            bar_color = 10
            IF aim_power > 33 THEN bar_color = 14
            IF aim_power > 66 THEN bar_color = 4
            LINE (6, 79)-(14, 79 - bar_height), bar_color, BF
        END IF

        LOCATE 12, 1
        COLOR bar_color
        PRINT "PWR"
    END IF

    ' Angle indicator
    IF aiming = 1 THEN
        LOCATE 11, 1
        COLOR 14
        PRINT aim_angle; CHR$(248)
    END IF

    COLOR 15
RETURN

' =====================================================
' COLLISION SUBROUTINES
' =====================================================

check_block_collision:
    FOR i = 0 TO num_blocks - 1
        IF block_alive(i) = 1 THEN
            bx = block_x(i)
            by = block_y(i)
            bw = block_w(i)
            bh = block_h(i)

            ' AABB collision with some tolerance
            IF bird_x + BIRD_RADIUS > bx AND bird_x - BIRD_RADIUS < bx + bw THEN
                IF bird_y + BIRD_RADIUS > by AND bird_y - BIRD_RADIUS < by + bh THEN
                    ' Collision detected!
                    block_hits(i) = block_hits(i) - 1

                    IF block_hits(i) <= 0 THEN
                        block_alive(i) = 0
                        IF block_type(i) = 1 THEN
                            score = score + 50
                        ELSE
                            score = score + 100
                        END IF
                        GOSUB spawn_block_debris
                        GOSUB play_block_hit_sound
                    ELSE
                        ' Block damaged but not destroyed
                        SOUND 300, 1
                    END IF

                    ' Reduce bird velocity based on block type
                    IF block_type(i) = 1 THEN
                        bird_vx = bird_vx * 0.5
                        bird_vy = bird_vy * 0.5
                    ELSE
                        bird_vx = bird_vx * 0.3
                        bird_vy = bird_vy * 0.3
                    END IF

                    ' Check for chain reactions
                    GOSUB check_falling_blocks
                END IF
            END IF
        END IF
    NEXT i
RETURN

check_pig_collision:
    FOR i = 0 TO num_pigs - 1
        IF pig_alive(i) = 1 THEN
            px = pig_x(i)
            py = pig_y(i)

            ' Circle collision
            dx = bird_x - px
            dy = bird_y - py
            dist = SQR(dx * dx + dy * dy)

            IF dist < BIRD_RADIUS + 10 THEN
                ' Pig destroyed!
                pig_alive(i) = 0
                score = score + 500
                GOSUB spawn_pig_stars
                GOSUB play_pig_death_sound

                ' Bounce bird
                bird_vx = bird_vx * 0.4
                bird_vy = bird_vy * 0.4
            END IF
        END IF
    NEXT i
RETURN

spawn_block_debris:
    bc = 6
    IF block_type(i) = 2 THEN bc = 8

    FOR d = 0 TO 7
        IF num_debris < 30 THEN
            debris_x(num_debris) = block_x(i) + RND * block_w(i)
            debris_y(num_debris) = block_y(i) + RND * block_h(i)
            debris_vx(num_debris) = RND * 6 - 3
            debris_vy(num_debris) = -RND * 4 - 2
            debris_life(num_debris) = 40 + RND * 20
            debris_color(num_debris) = bc
            num_debris = num_debris + 1
        END IF
    NEXT d
RETURN

spawn_pig_stars:
    ' Spawn victory stars
    FOR s = 0 TO 4
        IF num_stars < 20 THEN
            star_x(num_stars) = pig_x(i) + RND * 20 - 10
            star_y(num_stars) = pig_y(i)
            star_life(num_stars) = 30 + RND * 20
            num_stars = num_stars + 1
        END IF
    NEXT s
RETURN

check_falling_blocks:
    ' Check each block for support
    FOR j = 0 TO num_blocks - 1
        IF block_alive(j) = 1 THEN
            has_support = 0
            bx = block_x(j)
            by = block_y(j)
            bw = block_w(j)
            bh = block_h(j)

            ' On ground?
            IF by + bh >= GROUND_Y - 2 THEN
                has_support = 1
            END IF

            ' Supported by another block?
            IF has_support = 0 THEN
                FOR k = 0 TO num_blocks - 1
                    IF k <> j AND block_alive(k) = 1 THEN
                        ' Check if block k is below block j
                        IF block_y(k) > by THEN
                            IF block_y(k) - (by + bh) < 5 THEN
                                ' Check horizontal overlap
                                IF bx + bw > block_x(k) AND bx < block_x(k) + block_w(k) THEN
                                    has_support = 1
                                END IF
                            END IF
                        END IF
                    END IF
                NEXT k
            END IF

            ' No support - destroy block
            IF has_support = 0 THEN
                block_alive(j) = 0
                IF block_type(j) = 1 THEN
                    score = score + 25
                ELSE
                    score = score + 50
                END IF
                GOSUB spawn_falling_debris
            END IF
        END IF
    NEXT j

    ' Check pigs for support
    FOR j = 0 TO num_pigs - 1
        IF pig_alive(j) = 1 THEN
            px = pig_x(j)
            py = pig_y(j)
            has_support = 0

            ' On ground?
            IF py >= GROUND_Y - 12 THEN
                has_support = 1
            END IF

            ' On a block?
            IF has_support = 0 THEN
                FOR k = 0 TO num_blocks - 1
                    IF block_alive(k) = 1 THEN
                        IF px > block_x(k) - 5 AND px < block_x(k) + block_w(k) + 5 THEN
                            IF block_y(k) > py THEN
                                IF block_y(k) - py < 20 THEN
                                    has_support = 1
                                END IF
                            END IF
                        END IF
                    END IF
                NEXT k
            END IF

            ' Pig falls!
            IF has_support = 0 THEN
                pig_alive(j) = 0
                score = score + 500
                GOSUB play_pig_death_sound
            END IF
        END IF
    NEXT j
RETURN

spawn_falling_debris:
    IF num_debris < 28 THEN
        debris_x(num_debris) = block_x(j) + block_w(j) / 2
        debris_y(num_debris) = block_y(j) + block_h(j) / 2
        debris_vx(num_debris) = RND * 2 - 1
        debris_vy(num_debris) = -2
        debris_life(num_debris) = 30
        IF block_type(j) = 1 THEN
            debris_color(num_debris) = 6
        ELSE
            debris_color(num_debris) = 8
        END IF
        num_debris = num_debris + 1
    END IF
RETURN

' =====================================================
' SCREEN SUBROUTINES
' =====================================================

show_pause_menu:
    pause_quit = 0

    ' Darken screen
    LINE (80, 60)-(240, 140), 0, BF
    LINE (80, 60)-(240, 140), 7

    LOCATE 9, 14
    COLOR 15
    PRINT "PAUSED"

    LOCATE 12, 11
    COLOR 7
    PRINT "SPACE - Resume"
    LOCATE 14, 11
    PRINT "Q - Quit to Title"

    DO
        k$ = INKEY$
        IF k$ = " " THEN
            EXIT DO
        END IF
        IF k$ = "q" OR k$ = "Q" THEN
            pause_quit = 1
            EXIT DO
        END IF
        _DELAY 0.016
    LOOP

    COLOR 15
RETURN

show_level_complete:
    CLS

    ' Fireworks effect
    FOR fw = 1 TO 20
        fx = 50 + RND * 220
        fy = 30 + RND * 80
        fc = 12 + INT(RND * 4)
        FOR r = 1 TO 8
            CIRCLE (fx, fy), r * 3, fc
        NEXT r
        SOUND 400 + RND * 400, 1
        _DELAY 0.05
    NEXT fw

    LINE (60, 60)-(260, 140), 2, BF
    LINE (60, 60)-(260, 140), 10

    LOCATE 9, 10
    COLOR 14
    PRINT "LEVEL "; level; " COMPLETE!"

    LOCATE 11, 13
    COLOR 15
    PRINT "Score: "; score

    bonus = birds_left * 500
    LOCATE 13, 10
    COLOR 10
    PRINT "Bird Bonus: +"; bonus

    LOCATE 16, 9
    COLOR 7
    PRINT "Press SPACE to continue"

    DO
        k$ = INKEY$
        _DELAY 0.016
    LOOP UNTIL k$ = " "

    COLOR 15
RETURN

show_victory:
    CLS

    ' Epic fireworks
    FOR fw = 1 TO 40
        fx = RND * SCREEN_W
        fy = RND * 120
        fc = 9 + INT(RND * 7)
        FOR r = 1 TO 10
            CIRCLE (fx, fy), r * 2, fc
        NEXT r
        IF fw MOD 5 = 0 THEN
            SOUND 300 + RND * 500, 1
        END IF
        _DELAY 0.03
    NEXT fw

    LINE (40, 40)-(280, 160), 2, BF
    LINE (40, 40)-(280, 160), 14

    LOCATE 6, 10
    COLOR 14
    PRINT "CONGRATULATIONS!"

    LOCATE 8, 7
    COLOR 15
    PRINT "You defeated all the pigs!"

    LOCATE 10, 11
    COLOR 14
    PRINT "FINAL SCORE: "; score

    IF score > high_score THEN
        high_score = score
        LOCATE 12, 10
        COLOR 10
        PRINT "NEW HIGH SCORE!"
        PLAY "T200O5L8CEGCEG>C"
    END IF

    LOCATE 16, 8
    COLOR 7
    PRINT "Press SPACE to continue"

    DO
        k$ = INKEY$
        _DELAY 0.016
    LOOP UNTIL k$ = " "

    COLOR 15
RETURN

show_game_over:
    CLS

    ' Sad animation
    FOR sa = 1 TO 30
        LINE (0, 0)-(SCREEN_W, SCREEN_H), 0, BF
        py = 100 + SIN(sa / 3) * 10

        ' Sad bird
        CIRCLE (160, py), 20, 4, , , , F
        CIRCLE (160, py), 20, 12

        ' Sad eyes
        CIRCLE (152, py - 5), 5, 15, , , , F
        CIRCLE (168, py - 5), 5, 15, , , , F
        PSET (152, py - 3), 0
        PSET (168, py - 3), 0

        ' Tears
        IF sa MOD 5 < 3 THEN
            LINE (152, py + 2)-(150, py + 10), 9
            LINE (168, py + 2)-(170, py + 10), 9
        END IF

        ' Sad mouth
        LINE (155, py + 10)-(165, py + 10), 0
        LINE (155, py + 10)-(158, py + 13), 0
        LINE (165, py + 10)-(162, py + 13), 0

        _DELAY 0.05
    NEXT sa

    LINE (60, 50)-(260, 150), 4, BF
    LINE (60, 50)-(260, 150), 12

    LOCATE 8, 14
    COLOR 15
    PRINT "GAME OVER"

    LOCATE 11, 11
    COLOR 7
    PRINT "Final Score: "; score

    IF score > high_score THEN
        high_score = score
        LOCATE 13, 10
        COLOR 14
        PRINT "NEW HIGH SCORE!"
    END IF

    LOCATE 16, 8
    COLOR 8
    PRINT "SPACE - Play Again"
    LOCATE 17, 8
    PRINT "ESC - Back to Title"

    DO
        k$ = INKEY$
        IF k$ = " " THEN
            score = 0
            birds_left = 3
            level = 1
            game_over = 0
            GOSUB init_level
            GOTO main_loop
        END IF
        IF k$ = CHR$(27) THEN
            EXIT DO
        END IF
        _DELAY 0.016
    LOOP

    COLOR 15
RETURN
