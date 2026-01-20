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

' Single-line IF with ELSE
IF x > 10 THEN y = 1 ELSE y = 0
IF r = 4 THEN r = 1 ELSE r = r + 1

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

### WHILE-WEND

```basic
x = 0
WHILE x < 10
    x = x + 1
WEND
```

### SELECT CASE

```basic
SELECT CASE score
    CASE 100
        PRINT "Perfect!"
    CASE 90 TO 99
        PRINT "Excellent"
    CASE IS >= 70
        PRINT "Passing"
    CASE ELSE
        PRINT "Try again"
END SELECT
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

### SUB...END SUB

```basic
' Define a subroutine
SUB DrawBox (x1, y1, x2, y2, c)
    LINE (x1, y1)-(x2, y2), c, B
END SUB

' Call the subroutine
CALL DrawBox(10, 10, 50, 50, 15)
DrawBox 10, 10, 50, 50, 15         ' CALL keyword is optional

' Passing arrays to subroutines
SUB ProcessArray (arr() AS INTEGER, size AS INTEGER)
    FOR i = 0 TO size
        arr(i) = arr(i) * 2
    NEXT i
END SUB

DIM myArray(10) AS INTEGER
CALL ProcessArray(myArray(), 10)   ' Use () to pass entire array
```

### FUNCTION...END FUNCTION

```basic
' Define a function that returns a value
FUNCTION Square% (n AS INTEGER)
    Square = n * n
END FUNCTION

' Call the function
result = Square(5)                 ' result = 25

' Function with type suffix (% for integer)
FUNCTION Max% (a AS INTEGER, b AS INTEGER)
    IF a > b THEN Max = a ELSE Max = b
END FUNCTION

' Can call with or without type suffix
x = Max%(10, 20)                   ' With suffix
x = Max(10, 20)                    ' Without suffix (also works)
```

### DECLARE

```basic
' Forward declaration of procedures (optional but recommended)
DECLARE SUB DrawBox (x1, y1, x2, y2, c)
DECLARE FUNCTION Square% (n AS INTEGER)

' Allows calling procedures before their definition
result = Square(5)

' ... later in code ...
FUNCTION Square% (n AS INTEGER)
    Square = n * n
END FUNCTION
```

### END

```basic
END                        ' Terminates program execution
```

### STOP

```basic
STOP                       ' Break execution (for debugging)
' Sets stopped=True, running=False
' Unlike END, STOP is intended for debugging purposes
```

### DATA-READ-RESTORE

```basic
DATA 10, 20, 30, "Hello"
DATA 40, 50, 60

' Read values into variables
READ A, B, C
READ msg$

' Reset data pointer to re-read
RESTORE

' Read from specific label
RESTORE myData
myData:
DATA 100, 200
```

### SWAP

```basic
A = 10
B = 20
SWAP A, B          ' Now A=20, B=10

' Works with arrays too
SWAP arr(0), arr(1)
```

### INPUT

```basic
INPUT x                        ' Prompt with "? " and read into x
INPUT "Enter name: "; name$    ' Custom prompt with "? "
INPUT "Value", n               ' Custom prompt without "? " (uses comma)
INPUT "Values: "; a, b, c      ' Read multiple values separated by commas
```

### LINE INPUT

```basic
LINE INPUT text$               ' Read entire line into text$
LINE INPUT "Enter text: "; s$  ' With prompt, reads line including commas
' Unlike INPUT, LINE INPUT does not parse commas or quotes
' It reads the entire line exactly as typed
```

### ERASE

```basic
DIM arr(10)
ERASE arr                      ' Remove array from memory
ERASE a, b, c                  ' Remove multiple arrays
```

### DEF FN

```basic
' Define inline function with one parameter
DEF FN double(x) = x * 2
result = FN double(5)          ' result = 10

' Multiple parameters
DEF FN add(a, b) = a + b
result = FN add(3, 7)          ' result = 10

' No parameters (uses global variables)
multiplier = 10
DEF FN scale(x) = x * multiplier
result = FN scale(5)           ' result = 50

' String function
DEF FN greet$(name$) = "Hello " + name$
msg$ = FN greet$("World")      ' msg$ = "Hello World"
```

### OPTION BASE

```basic
' Set default array lower bound
OPTION BASE 0                  ' Arrays start at 0 (default)
DIM arr(5)                     ' Indices 0-5 (6 elements)

OPTION BASE 1                  ' Arrays start at 1
DIM arr(5)                     ' Indices 1-5 (5 elements)
```

### REDIM

```basic
' Redimension dynamic array (clears existing data)
DIM arr(5)
arr(3) = 100
REDIM arr(10)                  ' Now arr has 11 elements, all reset to 0

' Works with multi-dimensional arrays
REDIM grid(10, 20)

' Works with string arrays
REDIM names$(5)
```

### PRINT USING

```basic
' Formatted numeric output
PRINT USING "###"; 42          ' Prints "  42"
PRINT USING "##.##"; 3.14      ' Prints " 3.14"
PRINT USING "#,###"; 1234      ' Prints "1,234"
PRINT USING "+##.##"; -5.5     ' Prints "- 5.50"

' String formatting
PRINT USING "!"; "Hello"       ' Prints "H" (first char only)
PRINT USING "&"; "Hi"          ' Prints "Hi" (entire string)
PRINT USING "\  \"; "Hello"    ' Prints "Hell" (fixed width)

' Multiple values
PRINT USING "## + ## = ##"; 2, 3, 5
```

### ON...GOTO / ON...GOSUB

```basic
' Computed GOTO - jump based on expression value
ON choice GOTO opt1, opt2, opt3
' If choice=1, goes to opt1; if choice=2, goes to opt2; etc.
' If choice < 1 or > number of labels, continues to next line

opt1:
    PRINT "Option 1"
    GOTO done
opt2:
    PRINT "Option 2"
    GOTO done
opt3:
    PRINT "Option 3"
done:

' Computed GOSUB - same but with RETURN
ON n GOSUB sub1, sub2
PRINT "Returned from subroutine"
GOTO skip
sub1:
    PRINT "Subroutine 1"
    RETURN
sub2:
    PRINT "Subroutine 2"
    RETURN
skip:
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

### PRESET (Plot Point with Background Color)

```basic
PRESET (x, y)              ' Draw pixel using background color
PRESET (x, y), color       ' Draw pixel with specified color
' PRESET defaults to background color, PSET defaults to foreground
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

### DRAW (Turtle Graphics)

```basic
' Draw using turtle graphics commands
DRAW "R100"                        ' Move right 100 pixels
DRAW "D50L100U50"                  ' Draw a rectangle

' DRAW Commands:
' U[n]: Up n pixels
' D[n]: Down n pixels
' L[n]: Left n pixels
' R[n]: Right n pixels
' E[n]: Diagonal up-right
' F[n]: Diagonal down-right
' G[n]: Diagonal down-left
' H[n]: Diagonal up-left
' M[+/-]x,y: Move to position (+ or - for relative)
' A[n]: Set angle (0-3, n*90 degrees)
' TA[n]: Turn angle in degrees
' C[n]: Set color (0-15)
' B: Prefix - move without drawing
' N: Prefix - return to start after command
' S[n]: Scale factor (default 4, n/4 multiplier)
' P fill,border: Paint fill at current position
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
| `CINT(x)` | Round to nearest integer | `CINT(3.6)` returns `4` |
| `CLNG(x)` | Round to long integer | `CLNG(3.7)` returns `4` |
| `CSNG(x)` | Convert to single precision | `CSNG(42)` returns `42.0` |
| `CDBL(x)` | Convert to double precision | `CDBL(3.14)` returns `3.14` |
| `SGN(x)` | Sign (-1, 0, or 1) | `SGN(-5)` returns `-1` |
| `SQR(x)` | Square root | `SQR(16)` returns `4` |
| `LOG(x)` | Natural logarithm | `LOG(2.718)` returns `1` |
| `EXP(x)` | Exponential (e^x) | `EXP(1)` returns `2.718...` |
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
| `ASC(s$)` | Get ASCII code of first char | `ASC("A")` returns `65` |
| `STR$(n)` | Number to string | `STR$(42)` returns `"42"` |
| `VAL(s$)` | String to number | `VAL("42")` returns `42` |
| `INSTR([start,] s$, find$)` | Find substring position | `INSTR("Hello", "l")` returns `3` |
| `LCASE$(s$)` | Convert to lowercase | `LCASE$("HELLO")` returns `"hello"` |
| `UCASE$(s$)` | Convert to uppercase | `UCASE$("hello")` returns `"HELLO"` |
| `LTRIM$(s$)` | Remove leading spaces | `LTRIM$("  Hi")` returns `"Hi"` |
| `RTRIM$(s$)` | Remove trailing spaces | `RTRIM$("Hi  ")` returns `"Hi"` |
| `SPACE$(n)` | Create n spaces | `SPACE$(5)` returns `"     "` |
| `STRING$(n, char)` | Repeat character n times | `STRING$(3, "*")` returns `"***"` |
| `HEX$(n)` | Convert to hexadecimal | `HEX$(255)` returns `"FF"` |
| `OCT$(n)` | Convert to octal | `OCT$(64)` returns `"100"` |

### Input/Timing/Date Functions

| Function | Description | Example |
|----------|-------------|---------|
| `INKEY$` | Get pressed key (non-blocking) | `k$ = INKEY$` |
| `INPUT$(n)` | Get n characters from keyboard | `c$ = INPUT$(1)` |
| `TIMER` | Seconds since midnight | `t = TIMER` |
| `DATE$` | Current date (MM-DD-YYYY) | `d$ = DATE$` |
| `TIME$` | Current time (HH:MM:SS) | `t$ = TIME$` |
| `POINT(x, y)` | Get pixel color at position | `c = POINT(100, 50)` |
| `ENVIRON$(name$)` | Get environment variable | `p$ = ENVIRON$("PATH")` |
| `COMMAND$` | Get command line arguments | `args$ = COMMAND$` |

### Cursor/Screen Functions

| Function | Description | Example |
|----------|-------------|---------|
| `CSRLIN` | Get current cursor row (1-based) | `r = CSRLIN` |
| `POS(0)` | Get current cursor column (1-based) | `c = POS(0)` |
| `TAB(n)` | Move to column n in PRINT (returns spaces) | `PRINT TAB(10); "Hello"` |
| `SPC(n)` | Generate n spaces for use in PRINT | `PRINT "A"; SPC(5); "B"` |

### Array Functions

| Function | Description | Example |
|----------|-------------|---------|
| `LBOUND(arr, dim)` | Get lower bound of array dimension | `L = LBOUND("arr", 1)` returns `0` |
| `UBOUND(arr, dim)` | Get upper bound of array dimension | `U = UBOUND("arr", 1)` |

Note: Array names must be passed as strings. Arrays are 0-based.

---

## Sound Commands

### BEEP

```basic
BEEP                       ' Play a short beep sound (800 Hz, 0.2 seconds)
```

### SOUND

```basic
SOUND frequency, duration  ' Play tone with frequency (Hz) and duration (clock ticks)
SOUND 440, 18              ' Play 440 Hz (A4 note) for ~1 second
SOUND 880, 9               ' Play 880 Hz (A5 note) for ~0.5 seconds
' Duration is in clock ticks (18.2 ticks per second in QBasic)
' Frequency range: 37-32767 Hz
```

### PLAY

```basic
' Play music using Music Macro Language (MML)
PLAY "CDEFGAB"             ' Play C major scale
PLAY "O4L4CDEFGAB"         ' Set octave 4, quarter notes, play scale
PLAY "T120O4L8CDEC"        ' Tempo 120, octave 4, eighth notes

' MML Commands:
' A-G: Notes (add # or + for sharp, - for flat)
' O: Set octave (0-6, default 4)
' L: Set default note length (1=whole, 4=quarter, 8=eighth, etc.)
' T: Set tempo (32-255 quarter notes per minute, default 120)
' P/R: Pause/Rest
' >: Increase octave
' <: Decrease octave
' MN: Music Normal (7/8 note length)
' ML: Music Legato (full note length)
' MS: Music Staccato (3/4 note length)
```

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

' Numeric labels with colons also work
1:
FOR i = 1 TO 10
    PRINT i
NEXT i
GOTO 1
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
