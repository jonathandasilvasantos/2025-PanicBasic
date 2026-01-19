' TETRIS.BAS - Tetris game for PASIC interpreter
' Controls: A=left, D=right, W=rotate, S=soft drop, Space=hard drop, ESC=quit

SCREEN 13
RANDOMIZE TIMER
CLS

' Game constants
CONST COLS = 10
CONST ROWS = 20
CONST CELLSIZE = 9
CONST BOARDLEFT = 105
CONST BOARDTOP = 5

' Game board array (0 = empty, >0 = color)
DIM BOARD(19, 9)

' Current piece blocks (4 blocks per piece)
DIM PX(3)
DIM PY(3)

' Next piece blocks
DIM NX(3)
DIM NY(3)

' Initialize variables
SCORE = 0
LINES = 0
LEVEL = 1
GAMEOVER = 0
PIECEX = 4
PIECEY = 0
PIECECOLOR = 0
NEXTCOLOR = 0
FALLDELAY = 30
FALLCOUNT = 0

' Generate first piece
GOSUB MAKEPIECE
FOR I = 0 TO 3
    PX(I) = NX(I)
    PY(I) = NY(I)
NEXT I
PIECECOLOR = NEXTCOLOR

' Generate next piece
GOSUB MAKEPIECE

' ==================== MAIN GAME LOOP ====================
MAINLOOP:
IF GAMEOVER = 1 THEN GOTO ENDGAME

' Get input
K$ = INKEY$
IF K$ = CHR$(27) THEN END

' Move left
IF K$ = "a" OR K$ = "A" THEN
    MOVEX = -1
    MOVEY = 0
    GOSUB TRYMOVE
END IF

' Move right
IF K$ = "d" OR K$ = "D" THEN
    MOVEX = 1
    MOVEY = 0
    GOSUB TRYMOVE
END IF

' Rotate
IF K$ = "w" OR K$ = "W" THEN
    GOSUB TRYROTATE
END IF

' Soft drop
IF K$ = "s" OR K$ = "S" THEN
    MOVEX = 0
    MOVEY = 1
    GOSUB TRYMOVE
    IF MOVED = 1 THEN SCORE = SCORE + 1
END IF

' Hard drop
IF K$ = " " THEN
    GOSUB HARDDROP
END IF

' Gravity
FALLCOUNT = FALLCOUNT + 1
IF FALLCOUNT >= FALLDELAY THEN
    FALLCOUNT = 0
    MOVEX = 0
    MOVEY = 1
    GOSUB TRYMOVE
    IF MOVED = 0 THEN
        GOSUB LOCKPIECE
    END IF
END IF

' Draw game
GOSUB DRAWBOARD

_DELAY 0.02
GOTO MAINLOOP

' ==================== MAKE NEW PIECE ====================
MAKEPIECE:
PTYPE = INT(RND * 7)

IF PTYPE = 0 THEN
    ' I piece - horizontal line
    NX(0) = -1 : NY(0) = 0
    NX(1) = 0 : NY(1) = 0
    NX(2) = 1 : NY(2) = 0
    NX(3) = 2 : NY(3) = 0
    NEXTCOLOR = 11
ELSEIF PTYPE = 1 THEN
    ' O piece - square
    NX(0) = 0 : NY(0) = 0
    NX(1) = 1 : NY(1) = 0
    NX(2) = 0 : NY(2) = 1
    NX(3) = 1 : NY(3) = 1
    NEXTCOLOR = 14
ELSEIF PTYPE = 2 THEN
    ' T piece
    NX(0) = -1 : NY(0) = 0
    NX(1) = 0 : NY(1) = 0
    NX(2) = 1 : NY(2) = 0
    NX(3) = 0 : NY(3) = 1
    NEXTCOLOR = 13
ELSEIF PTYPE = 3 THEN
    ' S piece
    NX(0) = 0 : NY(0) = 0
    NX(1) = 1 : NY(1) = 0
    NX(2) = -1 : NY(2) = 1
    NX(3) = 0 : NY(3) = 1
    NEXTCOLOR = 10
ELSEIF PTYPE = 4 THEN
    ' Z piece
    NX(0) = -1 : NY(0) = 0
    NX(1) = 0 : NY(1) = 0
    NX(2) = 0 : NY(2) = 1
    NX(3) = 1 : NY(3) = 1
    NEXTCOLOR = 4
ELSEIF PTYPE = 5 THEN
    ' J piece
    NX(0) = -1 : NY(0) = 0
    NX(1) = 0 : NY(1) = 0
    NX(2) = 1 : NY(2) = 0
    NX(3) = -1 : NY(3) = 1
    NEXTCOLOR = 9
ELSE
    ' L piece
    NX(0) = -1 : NY(0) = 0
    NX(1) = 0 : NY(1) = 0
    NX(2) = 1 : NY(2) = 0
    NX(3) = 1 : NY(3) = 1
    NEXTCOLOR = 6
END IF
RETURN

' ==================== TRY MOVE ====================
TRYMOVE:
MOVED = 0
NEWX = PIECEX + MOVEX
NEWY = PIECEY + MOVEY

' Check collision
CANCOLLIDE = 0
FOR I = 0 TO 3
    TX = NEWX + PX(I)
    TY = NEWY + PY(I)
    IF TX < 0 OR TX >= COLS THEN CANCOLLIDE = 1
    IF TY >= ROWS THEN CANCOLLIDE = 1
    IF TY >= 0 AND TY < ROWS AND TX >= 0 AND TX < COLS THEN
        IF BOARD(TY, TX) > 0 THEN CANCOLLIDE = 1
    END IF
NEXT I

IF CANCOLLIDE = 0 THEN
    PIECEX = NEWX
    PIECEY = NEWY
    MOVED = 1
END IF
RETURN

' ==================== TRY ROTATE ====================
TRYROTATE:
' Save old positions
DIM OX(3)
DIM OY(3)
FOR I = 0 TO 3
    OX(I) = PX(I)
    OY(I) = PY(I)
NEXT I

' Rotate 90 degrees clockwise
FOR I = 0 TO 3
    TEMPX = PX(I)
    PX(I) = -PY(I)
    PY(I) = TEMPX
NEXT I

' Check collision
CANCOLLIDE = 0
FOR I = 0 TO 3
    TX = PIECEX + PX(I)
    TY = PIECEY + PY(I)
    IF TX < 0 OR TX >= COLS THEN CANCOLLIDE = 1
    IF TY >= ROWS THEN CANCOLLIDE = 1
    IF TY >= 0 AND TY < ROWS AND TX >= 0 AND TX < COLS THEN
        IF BOARD(TY, TX) > 0 THEN CANCOLLIDE = 1
    END IF
NEXT I

' Revert if collision
IF CANCOLLIDE = 1 THEN
    FOR I = 0 TO 3
        PX(I) = OX(I)
        PY(I) = OY(I)
    NEXT I
END IF
RETURN

' ==================== HARD DROP ====================
HARDDROP:
DROPCOUNT = 0
DROPLOOP:
MOVEX = 0
MOVEY = 1
GOSUB TRYMOVE
IF MOVED = 1 THEN
    DROPCOUNT = DROPCOUNT + 1
    GOTO DROPLOOP
END IF
SCORE = SCORE + DROPCOUNT * 2
GOSUB LOCKPIECE
RETURN

' ==================== LOCK PIECE ====================
LOCKPIECE:
' Place piece on board
FOR I = 0 TO 3
    TX = PIECEX + PX(I)
    TY = PIECEY + PY(I)
    IF TY >= 0 AND TY < ROWS AND TX >= 0 AND TX < COLS THEN
        BOARD(TY, TX) = PIECECOLOR
    END IF
    IF TY < 0 THEN GAMEOVER = 1
NEXT I

' Check for completed lines
GOSUB CLEARLINES

' Get next piece
FOR I = 0 TO 3
    PX(I) = NX(I)
    PY(I) = NY(I)
NEXT I
PIECECOLOR = NEXTCOLOR
PIECEX = 4
PIECEY = 0
FALLCOUNT = 0

' Generate new next piece
GOSUB MAKEPIECE

' Check if new piece collides (game over)
FOR I = 0 TO 3
    TX = PIECEX + PX(I)
    TY = PIECEY + PY(I)
    IF TY >= 0 AND TY < ROWS AND TX >= 0 AND TX < COLS THEN
        IF BOARD(TY, TX) > 0 THEN GAMEOVER = 1
    END IF
NEXT I
RETURN

' ==================== CLEAR LINES ====================
CLEARLINES:
LINESCLEARED = 0
ROW = ROWS - 1

CHECKROW:
IF ROW < 0 THEN GOTO DONECLEARING

' Check if row is full
FULL = 1
FOR C = 0 TO COLS - 1
    IF BOARD(ROW, C) = 0 THEN FULL = 0
NEXT C

IF FULL = 1 THEN
    LINESCLEARED = LINESCLEARED + 1
    ' Move all rows above down
    FOR R = ROW TO 1 STEP -1
        FOR C = 0 TO COLS - 1
            BOARD(R, C) = BOARD(R - 1, C)
        NEXT C
    NEXT R
    ' Clear top row
    FOR C = 0 TO COLS - 1
        BOARD(0, C) = 0
    NEXT C
    ' Don't decrement ROW, check same row again
ELSE
    ROW = ROW - 1
END IF
GOTO CHECKROW

DONECLEARING:
IF LINESCLEARED > 0 THEN
    LINES = LINES + LINESCLEARED
    ' Scoring
    IF LINESCLEARED = 1 THEN SCORE = SCORE + 100 * LEVEL
    IF LINESCLEARED = 2 THEN SCORE = SCORE + 300 * LEVEL
    IF LINESCLEARED = 3 THEN SCORE = SCORE + 500 * LEVEL
    IF LINESCLEARED = 4 THEN SCORE = SCORE + 800 * LEVEL
    ' Level up
    NEWLEVEL = INT(LINES / 10) + 1
    IF NEWLEVEL > LEVEL THEN
        LEVEL = NEWLEVEL
        FALLDELAY = 30 - LEVEL * 2
        IF FALLDELAY < 5 THEN FALLDELAY = 5
    END IF
END IF
RETURN

' ==================== DRAW BOARD ====================
DRAWBOARD:
CLS

' Draw board border
LINE (BOARDLEFT - 2, BOARDTOP - 2)-(BOARDLEFT + COLS * CELLSIZE + 1, BOARDTOP + ROWS * CELLSIZE + 1), 7, B

' Draw placed blocks
FOR R = 0 TO ROWS - 1
    FOR C = 0 TO COLS - 1
        IF BOARD(R, C) > 0 THEN
            X1 = BOARDLEFT + C * CELLSIZE
            Y1 = BOARDTOP + R * CELLSIZE
            LINE (X1, Y1)-(X1 + CELLSIZE - 2, Y1 + CELLSIZE - 2), BOARD(R, C), BF
            LINE (X1, Y1)-(X1 + CELLSIZE - 2, Y1 + CELLSIZE - 2), 15, B
        END IF
    NEXT C
NEXT R

' Draw ghost piece (where piece will land)
GHOSTY = PIECEY
GHOSTCHECK:
GHOSTCOL = 0
FOR I = 0 TO 3
    TX = PIECEX + PX(I)
    TY = GHOSTY + 1 + PY(I)
    IF TX < 0 OR TX >= COLS THEN GHOSTCOL = 1
    IF TY >= ROWS THEN GHOSTCOL = 1
    IF TY >= 0 AND TY < ROWS AND TX >= 0 AND TX < COLS THEN
        IF BOARD(TY, TX) > 0 THEN GHOSTCOL = 1
    END IF
NEXT I
IF GHOSTCOL = 0 THEN
    GHOSTY = GHOSTY + 1
    GOTO GHOSTCHECK
END IF

' Draw ghost
FOR I = 0 TO 3
    GX = PIECEX + PX(I)
    GY = GHOSTY + PY(I)
    IF GY >= 0 THEN
        X1 = BOARDLEFT + GX * CELLSIZE
        Y1 = BOARDTOP + GY * CELLSIZE
        LINE (X1 + 1, Y1 + 1)-(X1 + CELLSIZE - 3, Y1 + CELLSIZE - 3), 8, B
    END IF
NEXT I

' Draw current piece
FOR I = 0 TO 3
    BX = PIECEX + PX(I)
    BY = PIECEY + PY(I)
    IF BY >= 0 THEN
        X1 = BOARDLEFT + BX * CELLSIZE
        Y1 = BOARDTOP + BY * CELLSIZE
        LINE (X1, Y1)-(X1 + CELLSIZE - 2, Y1 + CELLSIZE - 2), PIECECOLOR, BF
        LINE (X1, Y1)-(X1 + CELLSIZE - 2, Y1 + CELLSIZE - 2), 15, B
    END IF
NEXT I

' Draw next piece preview
LOCATE 2, 28
PRINT "NEXT"
FOR I = 0 TO 3
    X1 = 230 + NX(I) * 8
    Y1 = 30 + NY(I) * 8
    LINE (X1, Y1)-(X1 + 6, Y1 + 6), NEXTCOLOR, BF
NEXT I

' Draw score info
LOCATE 7, 28
PRINT "SCORE"
LOCATE 8, 28
PRINT SCORE

LOCATE 10, 28
PRINT "LINES"
LOCATE 11, 28
PRINT LINES

LOCATE 13, 28
PRINT "LEVEL"
LOCATE 14, 28
PRINT LEVEL

' Draw controls
LOCATE 17, 27
PRINT "CONTROLS"
LOCATE 18, 27
PRINT "A D Move"
LOCATE 19, 27
PRINT "W Rotate"
LOCATE 20, 27
PRINT "S Drop"
LOCATE 21, 27
PRINT "SPC Hard"

RETURN

' ==================== GAME OVER ====================
ENDGAME:
CLS
LOCATE 9, 12
PRINT "GAME OVER"
LOCATE 11, 11
PRINT "SCORE: "; SCORE
LOCATE 12, 11
PRINT "LINES: "; LINES
LOCATE 13, 11
PRINT "LEVEL: "; LEVEL
LOCATE 16, 8
PRINT "Press ESC to exit"

WAITKEY:
K$ = INKEY$
IF K$ = CHR$(27) THEN END
_DELAY 0.1
GOTO WAITKEY
