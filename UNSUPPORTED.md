# Unsupported QBasic 4.5 Instructions

This document lists QBasic 4.5 features and instructions that are **not currently supported** by this interpreter.

---

## Graphics Commands

**NOW SUPPORTED:**
- `PCOPY` - Copy video pages
- `GET (graphics)` - Capture screen region to array
- `PUT (graphics)` - Display array as sprite on screen
- `PALETTE` / `PALETTE USING` - Modify color palette entries
- `VIEW PRINT` - Define text viewport
- `SCREEN` modes 0, 1, 2, 7, 8, 9, 10, 11, 12, 13
- `PRESET` and `DRAW`
- `VIEW` - Define graphics viewport
- `WINDOW` - Define logical coordinate system

---

## Sound Commands

**NOW SUPPORTED:**
- `SOUND` - Generate sound frequency
- `BEEP` - System beep
- `PLAY` - Play MML music strings

---

## File I/O

**NOW SUPPORTED:**
- `OPEN` - Open file for INPUT, OUTPUT, APPEND, BINARY, RANDOM
- `CLOSE` - Close file
- `INPUT #` - Read from file
- `LINE INPUT #` - Read line from file
- `PRINT #` - Write to file
- `WRITE #` - Write delimited data to file
- `LOF` - Get file length
- `EOF` - Check for end of file
- `FREEFILE` - Get next available file number
- `SEEK` - Set file position
- `LOC` - Get current file position
- `KILL` - Delete file
- `NAME` - Rename file
- `FILES` - List directory contents
- `CHDIR` - Change directory
- `MKDIR` - Create directory
- `RMDIR` - Remove directory
- `GET #` - Read binary record from file
- `PUT #` - Write binary record to file

---

## User Input

**NOW SUPPORTED:**
- `INPUT` - Read keyboard input
- `LINE INPUT` - Read entire line from keyboard
- `INPUT$(n)` - Read n characters from keyboard
- `INPUT$(n, #filenum)` - Read n characters from file

---

## Procedures and Functions

**NOW SUPPORTED:**
- `SUB...END SUB` - Define subroutine
- `FUNCTION...END FUNCTION` - Define function
- `DECLARE SUB` / `DECLARE FUNCTION` - Declare procedures
- `CALL` - Call subroutine
- Implicit SUB calls (without CALL keyword)
- `SHARED` - Share variables with main program
- `STATIC` - Declare static local variables
- `DEF FN` - Inline functions
- Array parameters `arr() AS TYPE` - Pass arrays to procedures
- Function calls with/without type suffix (e.g., `Max%` or `Max`)

---

## Advanced Control Flow

**NOW SUPPORTED:**
- `ON ERROR GOTO` - Error handler
- `RESUME` / `RESUME NEXT` - Resume after error
- `ERROR` - Trigger runtime error
- `ON...GOTO` and `ON...GOSUB` - Computed branching
- Single-line `IF...THEN...ELSE` statements
- Nested `SELECT CASE` blocks

---

## Math Functions

| Function | Description |
|----------|-------------|
| `ASIN(x)` | Arcsine (not in standard QBasic) |
| `ACOS(x)` | Arccosine (not in standard QBasic) |

**NOW SUPPORTED:**
- `CLNG`, `CSNG`, `CDBL` - Type conversion
- `CINT`, `FIX`, `INT` - Integer conversion
- All standard trig functions (SIN, COS, TAN, ATN)

---

## Memory and System

**NOW SUPPORTED:**
- `PEEK` / `POKE` - Read/write emulated memory
- `DEF SEG` - Set memory segment (emulated)
- `FRE` - Get free memory (returns mock value)
- `ERASE` - Clear arrays
- `LBOUND`, `UBOUND` - Array bounds
- `REDIM` - Resize arrays
- `OPTION BASE` - Set default array base
- `CLEAR` - Clear variables and reset stacks
- `VARPTR` - Get variable address (emulated)
- `VARSEG` - Get variable segment (emulated)
- `SADD` - Get string address (emulated)

---

## Program Execution

**NOW SUPPORTED:**
- `STOP` - Stop program execution
- `END` - End program
- `SHELL` - Execute shell command
- `SYSTEM` - Exit to operating system
- `RUN` - Run/restart program (from label or beginning)
- `CHAIN` - Load and run another program (preserves variables)
- `CONT` - Continue after STOP
- `TRON` / `TROFF` - Trace debugging (prints line numbers)

---

## Date and Time

| Function | Description |
|----------|-------------|
| `DATE$ = value` | Set system date |
| `TIME$ = value` | Set system time |

**NOW SUPPORTED:**
- `TIMER` - Get seconds since midnight
- `DATE$` (read) - Get current date
- `TIME$` (read) - Get current time

---

## Printing and Screen

**NOW SUPPORTED:**
- `WIDTH` - Set screen width
- `PRINT USING` - Formatted output
- `CSRLIN`, `POS(0)` - Cursor position
- `TAB(n)`, `SPC(n)` - Print spacing
- `LOCATE` - Position cursor
- `LPRINT` - Print to printer (outputs to console)
- `LPRINT USING` - Formatted printer output (outputs to console)

---

## User-Defined Types

**NOW SUPPORTED:**
- `TYPE...END TYPE` - Define record structure
- `DIM var AS typename` - Declare typed variable
- Array of TYPE support

---

## Binary/Random File Operations

**NOW SUPPORTED:**
- `MKI$`, `MKL$`, `MKS$`, `MKD$` - Convert number to binary string
- `CVI`, `CVL`, `CVS`, `CVD` - Convert binary string to number
- `FIELD` - Define record fields for random access files
- `LSET` / `RSET` - Justify string in field variable

---

## Environment

**NOW SUPPORTED:**
- `ENVIRON$` - Read environment variable
- `COMMAND$` - Get command line arguments
- `ENVIRON` - Set environment variable

---

## Hardware I/O

| Command | Description |
|---------|-------------|
| `INP` / `OUT` | Port I/O (stubbed, no-op) |
| `WAIT` | Wait for port condition (stubbed) |

Note: These are stubbed for compatibility but don't perform actual port I/O.

---

## Miscellaneous

| Command | Description |
|---------|-------------|
| `COMMON` | Share variables between modules (use COMMON SHARED instead) |
| `STRIG` / `STICK` | Joystick functions |
| `ON STRIG GOSUB` | Joystick event handler |
| `PEN` / `ON PEN GOSUB` | Light pen input |
| `ON PLAY GOSUB` | Music event handler |

**NOW SUPPORTED:**
- `DEF type` (DEFINT, DEFSNG, etc.) - Ignored, uses dynamic typing
- `COMMON SHARED` / `DIM SHARED` - Declare shared variables
- `ON TIMER GOSUB` - Timer event handler
- `TIMER ON/OFF/STOP` - Enable/disable timer events
- `$INCLUDE` - Include external file (accepted, parsed during loading)
- `$DYNAMIC` / `$STATIC` - Array storage declarations (accepted, Python handles automatically)
- `KEY n, string$` - Define function key string
- `KEY(n) ON/OFF/STOP` - Enable/disable key events
- `ON KEY(n) GOSUB` - Key event handler
- `PLAY(n)` - Get background music queue count (returns 0)

---

## Notes on Compatibility

The interpreter aims to support the most commonly used QBasic features, particularly those needed for running classic games like:
- Gorillas
- Nibbles
- QBlocks
- Various third-party BASIC games

Some hardware-specific features (PEEK/POKE, port I/O) are emulated or stubbed for compatibility but don't provide actual hardware access.

---

## Summary

### Fully Supported Features (Highlights)
- All standard control flow (IF/THEN/ELSE, FOR/NEXT, DO/LOOP, WHILE/WEND, SELECT CASE)
- Single-line IF...THEN...ELSE statements
- Nested SELECT CASE blocks
- GOSUB/RETURN and SUB/FUNCTION procedures
- Array parameters to procedures (arr() syntax)
- Graphics: SCREEN modes, LINE, CIRCLE, PSET, GET/PUT sprites, PALETTE, VIEW, WINDOW
- Sound: SOUND, BEEP, PLAY (MML)
- File I/O: OPEN, CLOSE, INPUT#, PRINT#, WRITE#, EOF, LOF, FIELD, LSET, RSET
- User-defined types (TYPE...END TYPE)
- Error handling (ON ERROR GOTO, RESUME)
- Integer division operator (\)
- Hex/octal/binary literals (&H, &O, &B)
- Numeric labels with colons (1:, 100:)
- Program control: SHELL, SYSTEM, CLEAR, RUN, CHAIN
- Environment: ENVIRON (set), ENVIRON$ (read)
- Timer events: ON TIMER GOSUB, TIMER ON/OFF/STOP
- Printer output: LPRINT, LPRINT USING (outputs to console)
- Debugging: TRON/TROFF trace mode, CONT to continue after STOP
- Memory functions: VARPTR, VARSEG, SADD (emulated addresses)
- Function key handling: KEY, KEY(n) ON/OFF, ON KEY(n) GOSUB
- Metacommands: $INCLUDE, $DYNAMIC, $STATIC
