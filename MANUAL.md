# PASIC - BASIC Interpreter Manual

A QBasic-compatible BASIC interpreter with graphics support, built with Python and Pygame.

## Running Programs

```bash
python interpreter.py <filename.bas>
```

Example:
```bash
python interpreter.py examples/pinball.bas
```

## Screen Modes

| Command | Resolution | Description |
|---------|------------|-------------|
| `SCREEN 13` | 320x200 | Standard graphics mode (16 colors) |

The default screen resolution is 320x200 pixels.

## Color Palette

The interpreter uses a 16-color CGA/EGA palette:

| Index | Color | RGB |
|-------|-------|-----|
| 0 | Black | (0, 0, 0) |
| 1 | Blue | (0, 0, 170) |
| 2 | Green | (0, 170, 0) |
| 3 | Cyan | (0, 170, 170) |
| 4 | Red | (170, 0, 0) |
| 5 | Magenta | (170, 0, 170) |
| 6 | Brown | (170, 85, 0) |
| 7 | Light Gray | (170, 170, 170) |
| 8 | Dark Gray | (85, 85, 85) |
| 9 | Light Blue | (85, 85, 255) |
| 10 | Light Green | (85, 255, 85) |
| 11 | Light Cyan | (85, 255, 255) |
| 12 | Light Red | (255, 85, 85) |
| 13 | Light Magenta | (255, 85, 255) |
| 14 | Yellow | (255, 255, 85) |
| 15 | White | (255, 255, 255) |

---

## Statements

### Variable Assignment

```basic
LET x = 10        ' LET is optional
x = 10            ' Same as above
name$ = "Hello"   ' String variable (ends with $)
count% = 42       ' Integer variable (ends with %)
```

### Constants

```basic
CONST PI = 3.14159
CONST TITLE$ = "My Game"
```

### Arrays

```basic
DIM scores(10)           ' 1D array with 11 elements (0-10)
DIM grid(10, 20)         ' 2D array
scores(5) = 100          ' Array assignment
```

---

## Control Flow

### IF-THEN

```basic
' Single-line IF
IF x > 10 THEN y = 1
IF score > 100 THEN PRINT "Winner!" : bonus = 50

' Multi-line IF block
IF x = 1 THEN
    result = 10
ELSEIF x = 2 THEN
    result = 20
ELSEIF x = 3 THEN
    result = 30
ELSE
    result = 0
END IF
```

### FOR-NEXT Loop

```basic
FOR i = 1 TO 10
    PRINT i
NEXT i

FOR i = 10 TO 1 STEP -1   ' Count backwards
    PRINT i
NEXT i

EXIT FOR                   ' Break out of loop early
```

### DO-LOOP

```basic
' Pre-condition loop
DO WHILE x < 10
    x = x + 1
LOOP

' Post-condition loop
DO
    x = x + 1
LOOP WHILE x < 10

' UNTIL variant
DO UNTIL x >= 10
    x = x + 1
LOOP

EXIT DO                    ' Break out of loop early
```

### GOTO

```basic
GOTO start

start:
    PRINT "Hello"
```

### GOSUB-RETURN

```basic
GOSUB drawPlayer
' ... continues here after RETURN

drawPlayer:
    PSET (x, y), 15
    RETURN
```

### END

```basic
END                        ' Terminates program execution
```

---

## Graphics Commands

### SCREEN

```basic
SCREEN 13                  ' Set 320x200 graphics mode
```

### CLS

```basic
CLS                        ' Clear screen with background color
```

### COLOR

```basic
COLOR 15                   ' Set foreground color to white
COLOR 15, 1                ' Set foreground to white, background to blue
```

### PSET (Plot Point)

```basic
PSET (x, y), color         ' Draw a single pixel
PSET (100, 50), 15         ' Draw white pixel at (100, 50)
```

### LINE

```basic
LINE (x1, y1)-(x2, y2), color       ' Draw line
LINE (0, 0)-(100, 100), 15          ' White diagonal line

LINE (x1, y1)-(x2, y2), color, B    ' Draw rectangle (box)
LINE (10, 10)-(50, 50), 14, B       ' Yellow rectangle outline

LINE (x1, y1)-(x2, y2), color, BF   ' Draw filled rectangle
LINE (10, 10)-(50, 50), 4, BF       ' Filled red rectangle
```

### CIRCLE

```basic
CIRCLE (x, y), radius, color                    ' Draw circle
CIRCLE (160, 100), 50, 15                       ' White circle

CIRCLE (x, y), radius, color, , , , F           ' Filled circle
CIRCLE (160, 100), 30, 4, , , , F               ' Filled red circle
```

### PAINT (Flood Fill)

```basic
PAINT (x, y), fillColor, borderColor
PAINT (100, 100), 4, 15            ' Fill with red, stop at white border
```

### LOCATE

```basic
LOCATE row, col            ' Position text cursor
LOCATE 10, 5               ' Move cursor to row 10, column 5
```

### PRINT

```basic
PRINT "Hello World"
PRINT x; y; z              ' Print multiple values (semicolon = no space)
PRINT "Score:"; score
PRINT                      ' Print blank line
```

---

## Built-in Functions

### Math Functions

| Function | Description | Example |
|----------|-------------|---------|
| `ABS(x)` | Absolute value | `ABS(-5)` returns `5` |
| `INT(x)` | Floor (round down) | `INT(3.7)` returns `3` |
| `FIX(x)` | Truncate towards zero | `FIX(-3.7)` returns `-3` |
| `SGN(x)` | Sign (-1, 0, or 1) | `SGN(-5)` returns `-1` |
| `SQR(x)` | Square root | `SQR(16)` returns `4` |
| `SIN(x)` | Sine (radians) | `SIN(3.14159/2)` returns `1` |
| `COS(x)` | Cosine (radians) | `COS(0)` returns `1` |
| `TAN(x)` | Tangent (radians) | `TAN(0)` returns `0` |
| `ATN(x)` | Arctangent (radians) | `ATN(1)` returns `0.785...` |
| `RND` | Random number (0-1) | `RND` returns `0.xxxxx` |
| `RND(n)` | Random with seed hint | `RND(1)` |

### String Functions

| Function | Description | Example |
|----------|-------------|---------|
| `LEN(s$)` | String length | `LEN("Hello")` returns `5` |
| `LEFT$(s$, n)` | Left substring | `LEFT$("Hello", 2)` returns `"He"` |
| `RIGHT$(s$, n)` | Right substring | `RIGHT$("Hello", 2)` returns `"lo"` |
| `MID$(s$, start, len)` | Middle substring | `MID$("Hello", 2, 3)` returns `"ell"` |
| `CHR$(n)` | ASCII to character | `CHR$(65)` returns `"A"` |
| `STR$(n)` | Number to string | `STR$(42)` returns `"42"` |
| `VAL(s$)` | String to number | `VAL("42")` returns `42` |

### Input/Timing Functions

| Function | Description | Example |
|----------|-------------|---------|
| `INKEY$` | Get pressed key (non-blocking) | `k$ = INKEY$` |
| `TIMER` | Seconds since midnight | `t = TIMER` |
| `POINT(x, y)` | Get pixel color at position | `c = POINT(100, 50)` |

---

## Timing Commands

### _DELAY / SLEEP

```basic
_DELAY 0.016               ' Pause for ~16ms (60 FPS)
SLEEP 1                    ' Pause for 1 second
```

### RANDOMIZE

```basic
RANDOMIZE TIMER            ' Seed random number generator with current time
RANDOMIZE 12345            ' Seed with specific value
```

---

## Operators

### Arithmetic

| Operator | Description | Example |
|----------|-------------|---------|
| `+` | Addition | `x + y` |
| `-` | Subtraction | `x - y` |
| `*` | Multiplication | `x * y` |
| `/` | Division | `x / y` |
| `^` | Exponentiation | `x ^ 2` |
| `MOD` | Modulo (remainder) | `x MOD 5` |

### Comparison

| Operator | Description | Example |
|----------|-------------|---------|
| `=` | Equal | `x = 5` |
| `<>` | Not equal | `x <> 5` |
| `<` | Less than | `x < 5` |
| `>` | Greater than | `x > 5` |
| `<=` | Less than or equal | `x <= 5` |
| `>=` | Greater than or equal | `x >= 5` |

### Logical

| Operator | Description | Example |
|----------|-------------|---------|
| `AND` | Logical AND | `x > 0 AND x < 10` |
| `OR` | Logical OR | `x < 0 OR x > 10` |
| `NOT` | Logical NOT | `NOT gameOver` |

---

## Comments

```basic
REM This is a comment
' This is also a comment (apostrophe style)
x = 10 ' Inline comment
```

---

## Labels

Labels can be numeric (QBasic line numbers) or named:

```basic
100 PRINT "Line 100"
200 GOTO 100

start:
    PRINT "Start"
    GOTO start
```

---

## Multi-Statement Lines

Multiple statements can be placed on one line using colons:

```basic
x = 1 : y = 2 : PRINT x + y
```

---

## Example Programs

### Hello World

```basic
SCREEN 13
CLS
COLOR 15
LOCATE 12, 15
PRINT "Hello, World!"
END
```

### Simple Animation

```basic
SCREEN 13
RANDOMIZE TIMER

x = 160
y = 100
dx = 2
dy = 1

DO
    CLS
    CIRCLE (x, y), 10, 15, , , , F

    x = x + dx
    y = y + dy

    IF x < 10 OR x > 310 THEN dx = -dx
    IF y < 10 OR y > 190 THEN dy = -dy

    _DELAY 0.016
LOOP
```

### Keyboard Input

```basic
SCREEN 13
x = 160
y = 100

DO
    k$ = INKEY$

    IF k$ = "w" THEN y = y - 2
    IF k$ = "s" THEN y = y + 2
    IF k$ = "a" THEN x = x - 2
    IF k$ = "d" THEN x = x + 2

    CLS
    CIRCLE (x, y), 5, 14, , , , F
    _DELAY 0.016
LOOP WHILE k$ <> CHR$(27)  ' ESC to exit
```

---

## Included Example Games

The `examples/` folder contains several complete games:

- **pong.bas** - Classic Pong game
- **pinball.bas** - Pinball with flippers and bumpers
- **runner.bas** - Infinite runner game
- **tetris.bas** - Tetris with ghost piece, next preview, levels
- **car.bas** - Car racing game
- **star.bas** - Starfield animation

---

## Technical Notes

- Screen coordinates: (0,0) is top-left
- Text rows and columns are 1-based (LOCATE 1,1 is top-left)
- Variable names are case-insensitive (X and x are the same)
- String variables must end with $ (e.g., `name$`)
- Integer variables can end with % (e.g., `count%`)
- Maximum execution: 2000 BASIC lines per frame for performance
