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

## File I/O

### OPEN / CLOSE

```basic
OPEN "data.txt" FOR INPUT AS #1      ' Open for reading
OPEN "out.txt" FOR OUTPUT AS #2      ' Open for writing (creates/overwrites)
OPEN "log.txt" FOR APPEND AS #3      ' Open for appending
OPEN "data.bin" FOR BINARY AS #4     ' Open for binary access
CLOSE #1                              ' Close file #1
CLOSE                                 ' Close all open files
```

### INPUT # / LINE INPUT #

```basic
INPUT #1, a, b$, c                    ' Read comma-separated values from file
LINE INPUT #1, text$                  ' Read entire line from file
```

### PRINT # / WRITE #

```basic
PRINT #1, "Hello"; x; y               ' Write formatted output to file
WRITE #1, a, b$, c                    ' Write comma-delimited data with quotes
```

### File Functions

```basic
n = FREEFILE                          ' Get next available file number
length = LOF(1)                       ' Get length of file #1
atEnd = EOF(1)                        ' Check if at end of file (-1 if true)
pos = LOC(1)                          ' Get current file position (1-based)
```

### SEEK

```basic
SEEK #1, 100                          ' Set file position to byte 100 (1-based)
```

### GET # / PUT # (Binary File Access)

```basic
' Open file for binary access
OPEN "data.bin" FOR BINARY AS #1

' Write binary data
x% = 12345
PUT #1, 1, x%                         ' Write integer at position 1

' Read binary data
GET #1, 1, y%                         ' Read integer from position 1

CLOSE #1
```

### Binary Conversion Functions

```basic
' Convert numbers to binary strings (for random-access files)
a$ = MKI$(12345)                      ' Integer to 2-byte string
b$ = MKL$(123456789)                  ' Long to 4-byte string
c$ = MKS$(3.14)                       ' Single to 4-byte string
d$ = MKD$(3.14159265359)              ' Double to 8-byte string

' Convert binary strings back to numbers
i% = CVI(a$)                          ' 2-byte string to integer
l& = CVL(b$)                          ' 4-byte string to long
s! = CVS(c$)                          ' 4-byte string to single
d# = CVD(d$)                          ' 8-byte string to double
```

### FIELD / LSET / RSET (Random Access Files)

```basic
' FIELD defines record structure for random-access files
OPEN "data.dat" FOR RANDOM AS #1 LEN = 30
FIELD #1, 20 AS Name$, 10 AS Phone$

' LSET left-justifies a string in a field variable
LSET Name$ = "John Doe"               ' Pads with spaces on right

' RSET right-justifies a string in a field variable
RSET Phone$ = "555-1234"              ' Pads with spaces on left

' Write the record
PUT #1, 1

' Read the record back
GET #1, 1

CLOSE #1
```

### INPUT$ (Read Characters)

```basic
' Read from keyboard
c$ = INPUT$(1)                        ' Read 1 character from keyboard

' Read from file
OPEN "data.txt" FOR BINARY AS #1
data$ = INPUT$(10, 1)                 ' Read 10 bytes from file #1
CLOSE #1
```

### KILL / NAME

```basic
KILL "oldfile.txt"                    ' Delete a file
NAME "old.txt" AS "new.txt"           ' Rename a file
```

### Directory Commands

```basic
MKDIR "newdir"                        ' Create a directory
RMDIR "olddir"                        ' Remove an empty directory
CHDIR "subdir"                        ' Change current directory
FILES "*.txt"                         ' List files matching pattern
FILES                                 ' List all files in current directory
```

---

## Error Handling

### ON ERROR GOTO

```basic
ON ERROR GOTO handler                 ' Set error handler
ON ERROR GOTO 0                       ' Disable error handling

' ... code that might error ...
END

handler:
    PRINT "An error occurred!"
    RESUME NEXT                       ' Continue at next statement
```

### ERROR

```basic
ERROR 5                               ' Trigger runtime error #5
' Can be caught by ON ERROR GOTO handler
```

### RESUME

```basic
RESUME                                ' Retry the statement that caused error
RESUME NEXT                           ' Continue at statement after error
RESUME label                          ' Continue at specified label
```

---

## Program Control

### CLEAR

```basic
CLEAR                                 ' Clear all variables and reset stacks
' Note: Stack and heap size parameters are ignored (Python manages memory)
```

### SHELL

```basic
SHELL "dir"                           ' Execute shell command (DOS: dir, Unix: ls)
SHELL "echo Hello"                    ' Run any shell command
SHELL                                 ' Without arguments, does nothing
```

Note: Shell commands have a 30-second timeout for safety.

### SYSTEM

```basic
SYSTEM                                ' Exit program and return to operating system
' Equivalent to END, stops program execution
```

### END / STOP

```basic
END                                   ' End program execution
STOP                                  ' Stop program (can be continued with CONT)
```

### RUN

```basic
RUN                                   ' Restart program from beginning
RUN label                             ' Restart from specified label
' Variables are cleared when RUN is executed
```

### CHAIN

```basic
CHAIN "other.bas"                     ' Load and run another BASIC program
' Variables declared with COMMON are preserved across CHAIN calls
```

### COMMON

```basic
' Declare variables to share between CHAINed programs
COMMON x, y, z                        ' Simple variables
COMMON name$, count%                  ' Variables with type suffixes
COMMON value AS INTEGER               ' With type declaration
COMMON SHARED a, b                    ' Also shared with SUBs/FUNCTIONs

' Example: main.bas
COMMON score, lives
score = 100
lives = 3
CHAIN "level2.bas"

' Example: level2.bas
COMMON score, lives                   ' Must declare COMMON in both files
PRINT "Score:"; score                 ' Will print 100
```

Note: Variables declared with COMMON are preserved when using CHAIN. Both the calling program and the CHAINed program must declare the same COMMON variables.

### CONT (Continue After STOP)

```basic
' After STOP has paused execution, use CONT to resume
' Note: In the interpreter, CONT is primarily for interactive debugging
STOP                                  ' Pause here
' ... later, CONT would resume
```

### TRON / TROFF (Trace Debugging)

```basic
TRON                                  ' Turn on trace mode
' When trace is ON, line numbers are printed as they execute
' Output looks like: [0] [1] [2] ...

TROFF                                 ' Turn off trace mode
' Useful for debugging program flow
```

---

## Memory Functions

### VARPTR / VARSEG / SADD

```basic
' Get emulated memory addresses of variables
x = 100
addr = VARPTR(x)                      ' Get offset address of variable
seg = VARSEG(x)                       ' Get segment address of variable

s$ = "Hello"
saddr = SADD(s$)                      ' Get address of string data

' Note: These return emulated addresses, not actual memory locations
' Useful for compatibility with programs that use these functions
```

---

## Hardware I/O (Emulated)

### INP / OUT

```basic
' Write to I/O port (emulated)
OUT &H3C8, 0                          ' Write 0 to port 0x3C8

' Read from I/O port (emulated)
value = INP(&H3C9)                    ' Read from port 0x3C9

' Values written with OUT can be read back with INP
OUT 100, 255                          ' Write 255 to port 100
x = INP(100)                          ' x = 255
```

Note: Port I/O is emulated for compatibility. Values written with OUT are stored and can be read back with INP. This allows programs that use port I/O for internal state to function correctly.

### WAIT

```basic
' Wait for port condition (emulated as no-op)
WAIT &H3DA, 8                         ' Wait until bit 3 is set
WAIT &H3DA, 8, 8                      ' Wait until bit 3 is clear
```

Note: WAIT is accepted for compatibility but does nothing since actual port I/O is not available.

---

## Function Key Handling

### KEY (Define Function Key)

```basic
KEY 1, "HELP"                         ' Define F1 to type "HELP"
KEY 2, "RUN" + CHR$(13)              ' Define F2 to type "RUN" and Enter
' Key numbers 1-10 correspond to F1-F10
```

### KEY(n) ON/OFF/STOP

```basic
KEY(1) ON                             ' Enable F1 key event trapping
KEY(1) OFF                            ' Disable F1 key event trapping
KEY(1) STOP                           ' Suspend F1 key events
```

### ON KEY(n) GOSUB

```basic
ON KEY(1) GOSUB helpHandler           ' Set F1 to call helpHandler
KEY(1) ON                             ' Enable the key trap

' ... program continues ...

helpHandler:
    PRINT "Help requested!"
    RETURN
```

### KEY ON/OFF/LIST

```basic
KEY ON                                ' Display function key definitions at bottom
KEY OFF                               ' Hide function key display
KEY LIST                              ' List all function key definitions
```

---

## Metacommands

### $INCLUDE

```basic
'$INCLUDE: 'common.bi'                ' Include another BASIC file
'$INCLUDE: "utils.bas"                ' Quotes or apostrophes work
' Note: The interpreter accepts this but actual file inclusion
' should be done during the file loading phase
```

### $DYNAMIC / $STATIC

```basic
'$DYNAMIC                             ' Arrays can be resized with REDIM
'$STATIC                              ' Arrays have fixed size (default)
' Note: Python handles array resizing automatically,
' so these are accepted for compatibility but have no effect
```

---

## Music Function

### PLAY(n)

```basic
notes = PLAY(0)                       ' Get count of notes in background queue
' Returns 0 since background music queue is not implemented
' Useful for checking if background music is still playing
```

### ON PLAY GOSUB / PLAY ON/OFF

```basic
' Set up background music event handler
ON PLAY(5) GOSUB musicHandler         ' Call when queue drops below 5 notes
PLAY ON                               ' Enable the event trap

' Enable/disable music events
PLAY ON                               ' Enable music events
PLAY OFF                              ' Disable music events
PLAY STOP                             ' Suspend events (same as OFF)

musicHandler:
    PLAY "CDEFGAB"                    ' Add more notes to queue
    RETURN
```

Note: These statements are accepted for compatibility but the handler never triggers since background music playback is not implemented. PLAY(n) always returns 0.

---

## Joystick Functions

### STICK

```basic
' Get joystick position (0-255, center=127)
x = STICK(0)                          ' X coordinate of joystick A
y = STICK(1)                          ' Y coordinate of joystick A
x2 = STICK(2)                         ' X coordinate of joystick B
y2 = STICK(3)                         ' Y coordinate of joystick B

' Example: Simple joystick control
DO
    x = STICK(0)
    y = STICK(1)
    IF x < 64 THEN dx = -1
    IF x > 192 THEN dx = 1
    IF y < 64 THEN dy = -1
    IF y > 192 THEN dy = 1
    _DELAY 0.016
LOOP
```

Note: Returns center position (127) when no joystick is connected.

### STRIG

```basic
' Get joystick button status (-1 if pressed, 0 otherwise)
' Even numbers: "pressed since last STRIG call" (cleared after read)
' Odd numbers: current button state

' Joystick A, Button 1:
b1pressed = STRIG(0)                  ' -1 if pressed since last check
b1down = STRIG(1)                     ' -1 if currently down

' Joystick A, Button 2:
b2pressed = STRIG(2)                  ' -1 if pressed since last check
b2down = STRIG(3)                     ' -1 if currently down

' Joystick B, Button 1:
b3pressed = STRIG(4)                  ' -1 if pressed since last check
b3down = STRIG(5)                     ' -1 if currently down

' Joystick B, Button 2:
b4pressed = STRIG(6)                  ' -1 if pressed since last check
b4down = STRIG(7)                     ' -1 if currently down

' Example: Check for fire button
IF STRIG(0) = -1 THEN PRINT "Fire!"
```

Note: Returns 0 when no joystick is connected.

### ON STRIG GOSUB / STRIG ON/OFF

```basic
' Set up joystick button event handler
ON STRIG(0) GOSUB fireHandler         ' Call fireHandler when button A1 pressed
STRIG(0) ON                           ' Enable the event trap

' Enable/disable joystick events
STRIG(0) ON                           ' Enable STRIG(0) events
STRIG(0) OFF                          ' Disable STRIG(0) events
STRIG(0) STOP                         ' Suspend events (same as OFF)

' Main program loop
DO
    ' Program logic
    _DELAY 0.016
LOOP

fireHandler:
    PRINT "Fire!"
    RETURN
```

Note: Button event numbers correspond to STRIG numbers (0, 2, 4, 6 for the four buttons).

---

## Light Pen Functions (Mouse Emulated)

### PEN

```basic
' Get light pen information (emulated with mouse click/movement)
p = PEN(0)                            ' -1 if pen activated since last PEN(0), 0 otherwise
x = PEN(1)                            ' X coordinate where pen was activated
y = PEN(2)                            ' Y coordinate where pen was activated
d = PEN(3)                            ' -1 if pen currently down, 0 otherwise
cx = PEN(4)                           ' Current X coordinate
cy = PEN(5)                           ' Current Y coordinate
row = PEN(6)                          ' Text row where activated (1-based)
col = PEN(7)                          ' Text column where activated (1-based)
crow = PEN(8)                         ' Current text row (1-based)
ccol = PEN(9)                         ' Current text column (1-based)

' Example: Get click position
DO
    IF PEN(0) = -1 THEN
        PRINT "Clicked at"; PEN(1); ","; PEN(2)
    END IF
    _DELAY 0.016
LOOP
```

Note: Light pen is emulated using the mouse. Left click = pen activation, mouse position = pen position.

### ON PEN GOSUB / PEN ON/OFF

```basic
' Set up light pen event handler
ON PEN GOSUB clickHandler             ' Call clickHandler when mouse clicked
PEN ON                                ' Enable the event trap

' Enable/disable pen events
PEN ON                                ' Enable pen events
PEN OFF                               ' Disable pen events
PEN STOP                              ' Suspend events (same as OFF)

' Main program loop
DO
    _DELAY 0.016
LOOP

clickHandler:
    PRINT "Clicked at"; PEN(1); ","; PEN(2)
    RETURN
```

---

## Environment

### ENVIRON$ (Read Environment Variable)

```basic
path$ = ENVIRON$("PATH")              ' Get value of PATH environment variable
user$ = ENVIRON$("USER")              ' Get value of USER
```

### ENVIRON (Set Environment Variable)

```basic
ENVIRON "MY_VAR=hello"                ' Set environment variable
ENVIRON name$ + "=" + value$          ' Use expression
```

---

## Timer Events

### ON TIMER GOSUB

```basic
' Set up timer event handler
ON TIMER(5) GOSUB updateClock         ' Call updateClock every 5 seconds

' Enable/disable timer
TIMER ON                              ' Enable timer events
TIMER OFF                             ' Disable timer events
TIMER STOP                            ' Suspend timer events

' Main program loop
DO
    ' Program logic
LOOP

updateClock:
    LOCATE 1, 70
    PRINT TIME$
    RETURN
```

Note: Timer events are triggered during program execution when the specified interval has elapsed.

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

### PCOPY (Video Page Copy)

```basic
' Copy video page contents
' Page 0 is the main display, pages 1-7 are offscreen buffers
PCOPY 0, 1                 ' Copy display to page 1 (save screen)
PCOPY 1, 0                 ' Copy page 1 to display (restore screen)

' Useful for double-buffering:
' Draw to page 1, then PCOPY 1, 0 to display
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

### LPRINT (Printer Output)

```basic
LPRINT "Hello World"       ' Print to printer (outputs to console)
LPRINT x; y; z             ' Same format specifiers as PRINT
LPRINT USING "##.##"; 3.14 ' Formatted printer output
```

Note: LPRINT statements output to the console (stdout) since most systems don't have line printers.

### VIEW (Graphics Viewport)

```basic
' Define a graphics viewport (clipping region)
VIEW (x1, y1)-(x2, y2)
VIEW (10, 10)-(100, 100)   ' Drawing clipped to this rectangle

' With fill and border colors
VIEW (x1, y1)-(x2, y2), fillColor, borderColor
VIEW (10, 10)-(100, 100), 1, 15    ' Fill with blue, white border

' Reset to full screen
VIEW
```

### WINDOW (Logical Coordinates)

```basic
' Define a logical coordinate system
WINDOW (x1, y1)-(x2, y2)
WINDOW (-100, -100)-(100, 100)     ' Cartesian coordinates (y up)

' WINDOW SCREEN - y increases downward
WINDOW SCREEN (0, 0)-(320, 200)    ' Top-left origin

' Reset to physical coordinates
WINDOW
```

Note: WINDOW maps logical coordinates to physical screen coordinates within the VIEW viewport.

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

### DATE$ / TIME$ Assignment

```basic
' Set custom date (overrides system date for program use)
DATE$ = "12-25-2025"                  ' Set to December 25, 2025
PRINT DATE$                           ' Prints "12-25-2025"

' Set custom time (overrides system time for program use)
TIME$ = "14:30:00"                    ' Set to 2:30 PM
PRINT TIME$                           ' Prints "14:30:00"

' Use expressions
myDate$ = "01-01-2020"
DATE$ = myDate$
```

Note: These assignments store custom values that override the system date/time for program use. They do not modify the actual system clock.

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
