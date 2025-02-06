SCREEN 13
CLS

CONST SCREEN_WIDTH = 320
CONST SCREEN_HEIGHT = 200
CONST GRID_WIDTH = 10
CONST GRID_HEIGHT = 20
CONST BLOCK_SIZE = 10
CONST BORDER_COLOR = 7
CONST EMPTY_COLOR = 0
CONST FALL_SPEED = 2

CONST COLOR_I = 11
CONST COLOR_J = 4
CONST COLOR_L = 6
CONST COLOR_O = 14
CONST COLOR_S = 10
CONST COLOR_T = 13
CONST COLOR_Z = 12

DIM grid(GRID_HEIGHT, GRID_WIDTH)
currentPiece = 0
currentRotation = 0
currentX = 0
currentY = 0
score = 0
gameOver = 0

DIM pieces(7, 4, 4, 4)

pieces(1, 1, 1, 1) = 1: pieces(1, 1, 1, 2) = 1: pieces(1, 1, 1, 3) = 1: pieces(1, 1, 1, 4) = 1
pieces(1, 2, 1, 1) = 1: pieces(1, 2, 2, 1) = 1: pieces(1, 2, 3, 1) = 1: pieces(1, 2, 4, 1) = 1
pieces(1, 3, 1, 1) = 1: pieces(1, 3, 1, 2) = 1: pieces(1, 3, 1, 3) = 1: pieces(1, 3, 1, 4) = 1
pieces(1, 4, 1, 1) = 1: pieces(1, 4, 2, 1) = 1: pieces(1, 4, 3, 1) = 1: pieces(1, 4, 4, 1) = 1

pieces(2, 1, 1, 1) = 1: pieces(2, 1, 2, 1) = 1: pieces(2, 1, 3, 1) = 1: pieces(2, 1, 3, 2) = 1
pieces(2, 2, 1, 2) = 1: pieces(2, 2, 2, 2) = 1: pieces(2, 2, 2, 1) = 1: pieces(2, 2, 3, 1) = 1
pieces(2, 3, 1, 1) = 1: pieces(2, 3, 1, 2) = 1: pieces(2, 3, 2, 2) = 1: pieces(2, 3, 3, 2) = 1
pieces(2, 4, 1, 2) = 1: pieces(2, 4, 1, 3) = 1: pieces(2, 4, 2, 3) = 1: pieces(2, 4, 2, 2) = 1

pieces(3, 1, 1, 2) = 1: pieces(3, 1, 2, 2) = 1: pieces(3, 1, 3, 2) = 1: pieces(3, 1, 3, 1) = 1
pieces(3, 2, 1, 1) = 1: pieces(3, 2, 2, 1) = 1: pieces(3, 2, 3, 1) = 1: pieces(3, 2, 1, 2) = 1
pieces(3, 3, 1, 1) = 1: pieces(3, 3, 1, 2) = 1: pieces(3, 3, 2, 1) = 1: pieces(3, 3, 3, 1) = 1
pieces(3, 4, 2, 1) = 1: pieces(3, 4, 2, 2) = 1: pieces(3, 4, 1, 3) = 1: pieces(3, 4, 2, 3) = 1

pieces(4, 1, 1, 1) = 1: pieces(4, 1, 1, 2) = 1: pieces(4, 1, 2, 1) = 1: pieces(4, 1, 2, 2) = 1
pieces(4, 2, 1, 1) = 1: pieces(4, 2, 1, 2) = 1: pieces(4, 2, 2, 1) = 1: pieces(4, 2, 2, 2) = 1
pieces(4, 3, 1, 1) = 1: pieces(4, 3, 1, 2) = 1: pieces(4, 3, 2, 1) = 1: pieces(4, 3, 2, 2) = 1
pieces(4, 4, 1, 1) = 1: pieces(4, 4, 1, 2) = 1: pieces(4, 4, 2, 1) = 1: pieces(4, 4, 2, 2) = 1

pieces(5, 1, 1, 2) = 1: pieces(5, 1, 1, 3) = 1: pieces(5, 1, 2, 1) = 1: pieces(5, 1, 2, 2) = 1
pieces(5, 2, 1, 1) = 1: pieces(5, 2, 2, 1) = 1: pieces(5, 2, 2, 2) = 1: pieces(5, 2, 3, 2) = 1
pieces(5, 3, 1, 2) = 1: pieces(5, 3, 1, 3) = 1: pieces(5, 3, 2, 1) = 1: pieces(5, 3, 2, 2) = 1
pieces(5, 4, 1, 1) = 1: pieces(5, 4, 2, 1) = 1: pieces(5, 4, 2, 2) = 1: pieces(5, 4, 3, 2) = 1

pieces(6, 1, 1, 2) = 1: pieces(6, 1, 2, 1) = 1: pieces(6, 1, 2, 2) = 1: pieces(6, 1, 2, 3) = 1
pieces(6, 2, 1, 1) = 1: pieces(6, 2, 2, 1) = 1: pieces(6, 2, 2, 2) = 1: pieces(6, 2, 3, 1) = 1
pieces(6, 3, 1, 1) = 1: pieces(6, 3, 1, 2) = 1: pieces(6, 3, 1, 3) = 1: pieces(6, 3, 2, 2) = 1
pieces(6, 4, 1, 2) = 1: pieces(6, 4, 2, 1) = 1: pieces(6, 4, 2, 2) = 1: pieces(6, 4, 3, 2) = 1

pieces(7, 1, 1, 1) = 1: pieces(7, 1, 1, 2) = 1: pieces(7, 1, 2, 2) = 1: pieces(7, 1, 2, 3) = 1
pieces(7, 2, 1, 2) = 1: pieces(7, 2, 2, 1) = 1: pieces(7, 2, 2, 2) = 1: pieces(7, 2, 3, 1) = 1
pieces(7, 3, 1, 1) = 1: pieces(7, 3, 1, 2) = 1: pieces(7, 3, 2, 2) = 1: pieces(7, 3, 2, 3) = 1
pieces(7, 4, 1, 2) = 1: pieces(7, 4, 2, 1) = 1: pieces(7, 4, 2, 2) = 1: pieces(7, 4, 3, 1) = 1

SUB DrawBlock(x, y, color)
    LINE (x * BLOCK_SIZE, y * BLOCK_SIZE)-(x * BLOCK_SIZE + BLOCK_SIZE - 1, y * BLOCK_SIZE + BLOCK_SIZE - 1), color, BF
END SUB

SUB DrawGrid()
    FOR y = 1 TO GRID_HEIGHT
        FOR x = 1 TO GRID_WIDTH
            IF grid(y, x) > 0 THEN
                DrawBlock x - 1, y - 1, grid(y, x)
            END IF
        NEXT x
    NEXT y
END SUB

SUB ClearGrid()
    FOR y = 1 TO GRID_HEIGHT
        FOR x = 1 TO GRID_WIDTH
            grid(y, x) = 0
        NEXT x
    NEXT y
END SUB

SUB DrawPiece()
    color = 0
    SELECT CASE currentPiece
        CASE 1: color = COLOR_I
        CASE 2: color = COLOR_J
        CASE 3: color = COLOR_L
        CASE 4: color = COLOR_O
        CASE 5: color = COLOR_S
        CASE 6: color = COLOR_T
        CASE 7: color = COLOR_Z
    END SELECT

    FOR row = 1 TO 4
        FOR col = 1 TO 4
            IF pieces(currentPiece, currentRotation, row, col) = 1 THEN
                blockX = currentX + col - 1
                blockY = currentY + row - 1
                IF blockX >= 0 AND blockX < GRID_WIDTH AND blockY >= 0 AND blockY < GRID_HEIGHT THEN
                   DrawBlock blockX, blockY, color
                END IF
            END IF
        NEXT col
    NEXT row
END SUB

SUB ErasePiece()
    FOR row = 1 TO 4
        FOR col = 1 TO 4
            IF pieces(currentPiece, currentRotation, row, col) = 1 THEN
                blockX = currentX + col - 1
                blockY = currentY + row - 1
                IF blockX >= 0 AND blockX < GRID_WIDTH AND blockY >= 0 AND blockY < GRID_HEIGHT THEN
                   LINE (blockX * BLOCK_SIZE, blockY * BLOCK_SIZE)-(blockX * BLOCK_SIZE + BLOCK_SIZE - 1, blockY * BLOCK_SIZE + BLOCK_SIZE - 1), EMPTY_COLOR, BF
                END IF
            END IF
        NEXT col
    NEXT row
END SUB

SUB CheckCollision()
    CheckCollision = 0
    FOR row = 1 TO 4
        FOR col = 1 TO 4
            IF pieces(currentPiece, currentRotation, row, col) = 1 THEN
                blockX = currentX + col
                blockY = currentY + row

                IF blockX > 0 AND blockX <= GRID_WIDTH AND blockY > 0 AND blockY <= GRID_HEIGHT THEN
                   IF  blockY > GRID_HEIGHT OR  grid(blockY, blockX) > 0 THEN
                       CheckCollision = 1
                       EXIT SUB
                   END IF
                ELSEIF blockY > GRID_HEIGHT THEN
                     CheckCollision = 1
                     EXIT SUB
                END IF

            END IF
        NEXT col
    NEXT row
END SUB

SUB LockPiece()
    FOR row = 1 TO 4
        FOR col = 1 TO 4
            IF pieces(currentPiece, currentRotation, row, col) = 1 THEN
                blockX = currentX + col
                blockY = currentY + row
                IF blockX > 0 AND blockX <= GRID_WIDTH AND blockY > 0 AND blockY <= GRID_HEIGHT THEN
                    SELECT CASE currentPiece
                        CASE 1: grid(blockY, blockX) = COLOR_I
                        CASE 2: grid(blockY, blockX) = COLOR_J
                        CASE 3: grid(blockY, blockX) = COLOR_L
                        CASE 4: grid(blockY, blockX) = COLOR_O
                        CASE 5: grid(blockY, blockX) = COLOR_S
                        CASE 6: grid(blockY, blockX) = COLOR_T
                        CASE 7: grid(blockY, blockX) = COLOR_Z
                    END SELECT

                END IF
            END IF
        NEXT col
    NEXT row
END SUB

SUB CheckRows()
    FOR y = 1 TO GRID_HEIGHT
        fullRow = 1
        FOR x = 1 TO GRID_WIDTH
            IF grid(y, x) = 0 THEN
                fullRow = 0
                EXIT FOR
            END IF
        NEXT x

        IF fullRow = 1 THEN
            FOR k = y TO 2 STEP -1
                FOR x = 1 TO GRID_WIDTH
                    grid(k, x) = grid(k - 1, x)
                NEXT x
            NEXT k
            FOR x = 1 TO GRID_WIDTH
                grid(1, x) = 0
            NEXT x
            score = score + 100
        END IF
    NEXT y
END SUB

SUB NewPiece()
    currentPiece = INT(RND * 7) + 1
    currentRotation = INT(RND * 4) + 1
    currentX = GRID_WIDTH / 2 - 2
    currentY = 1

    IF CheckCollision() THEN
        gameOver = 1
    END IF
END SUB

SUB MoveLeft()
    ErasePiece()
    currentX = currentX - 1
    IF currentX < 0 THEN
        currentX = 0
    END IF

    IF CheckCollision() THEN
       currentX = currentX + 1
    END IF
    DrawPiece()
END SUB

SUB MoveRight()
    ErasePiece()
    currentX = currentX + 1
    IF currentX + 4 > GRID_WIDTH THEN
        currentX = GRID_WIDTH - 4
    END IF

    IF CheckCollision() THEN
       currentX = currentX - 1
    END IF
    DrawPiece()

END SUB

SUB RotatePiece()
  ErasePiece()
  newRotation = currentRotation + 1
  IF newRotation > 4 THEN newRotation = 1
  oldRotation = currentRotation
  currentRotation = newRotation

  IF CheckCollision() THEN
     currentRotation = oldRotation
  END IF

  DrawPiece()
END SUB

ClearGrid()
NewPiece()
fallCounter = 0

DO UNTIL gameOver = 1
    a$ = INKEY$
    IF a$ = "a" OR a$ = "A" OR a$ = CHR$(0) + "K" THEN
       MoveLeft()
    END IF
    IF a$ = "d" OR a$ = "D" OR a$ = CHR$(0) + "M" THEN
        MoveRight()
    END IF
    IF a$ = " " THEN
      RotatePiece()
    END IF

    fallCounter = fallCounter + 1
    IF fallCounter > (30 - score/100) THEN
      ErasePiece()
      currentY = currentY + 1
      IF CheckCollision() THEN
          currentY = currentY - 1
          LockPiece()
          CheckRows()
          NewPiece()
      END IF
      DrawPiece()
      fallCounter = 0
    END IF

    CLS
    DrawGrid()
    DrawPiece()

    LOCATE 1, 1
    PRINT "Score: "; score
    _DELAY 0.02
LOOP

CLS
LOCATE 10, 10
PRINT "Game Over! Your Score: "; score
LOCATE 12, 8
PRINT "Press any key to exit"
DO UNTIL INKEY$ <> "": LOOP
END