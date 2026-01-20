# Unsupported QBasic 4.5 Instructions

This document lists QBasic 4.5 features and instructions that are **not currently supported** by this interpreter.

---

## Graphics Commands

| Command | Description |
|---------|-------------|
| `PCOPY` | Copy video pages |
| `VIEW` | Define graphics viewport |
| `WINDOW` | Define logical coordinate system |

**NOW SUPPORTED:**
- `GET (graphics)` - Capture screen region to array
- `PUT (graphics)` - Display array as sprite on screen
- `PALETTE` / `PALETTE USING` - Modify color palette entries
- `VIEW PRINT` - Define text viewport
- `SCREEN` modes 0, 1, 2, 7, 8, 9, 10, 11, 12, 13
- `PRESET` and `DRAW`

---

## Sound Commands

**NOW SUPPORTED:**
- `SOUND` - Generate sound frequency
- `BEEP` - System beep
- `PLAY` - Play MML music strings

---

## File I/O

| Command | Description |
|---------|-------------|
| `GET #` | Read binary record from file (sequential only) |
| `PUT #` | Write binary record to file (sequential only) |
| `SEEK` | Set file position |
| `LOC` | Get current file position |
| `KILL` | Delete file |
| `NAME` | Rename file |
| `FILES` | List directory contents |
| `CHDIR` | Change directory |
| `MKDIR` | Create directory |
| `RMDIR` | Remove directory |

**NOW SUPPORTED:**
- `OPEN` - Open file for INPUT, OUTPUT, APPEND
- `CLOSE` - Close file
- `INPUT #` - Read from file
- `LINE INPUT #` - Read line from file
- `PRINT #` - Write to file
- `WRITE #` - Write delimited data to file
- `LOF` - Get file length
- `EOF` - Check for end of file
- `FREEFILE` - Get next available file number

---

## User Input

| Command | Description |
|---------|-------------|
| `INPUT$(n, #filenum)` | Read characters from file (only file form) |

**NOW SUPPORTED:**
- `INPUT` - Read keyboard input
- `LINE INPUT` - Read entire line from keyboard
- `INPUT$(n)` - Read n characters from keyboard

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

---

## Advanced Control Flow

| Command | Description |
|---------|-------------|
| `ERROR` | Trigger runtime error |

**NOW SUPPORTED:**
- `ON ERROR GOTO` - Error handler
- `RESUME` / `RESUME NEXT` - Resume after error
- `ON...GOTO` and `ON...GOSUB` - Computed branching

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

| Command | Description |
|---------|-------------|
| `CLEAR` | Clear variables and set stack |
| `VARPTR` | Get variable address |
| `VARSEG` | Get variable segment |
| `SADD` | Get string address |

**NOW SUPPORTED:**
- `PEEK` / `POKE` - Read/write emulated memory
- `DEF SEG` - Set memory segment (emulated)
- `FRE` - Get free memory (returns mock value)
- `ERASE` - Clear arrays
- `LBOUND`, `UBOUND` - Array bounds
- `REDIM` - Resize arrays
- `OPTION BASE` - Set default array base

---

## Program Execution

| Command | Description |
|---------|-------------|
| `RUN` | Run program |
| `CHAIN` | Load and run another program |
| `SHELL` | Execute DOS command |
| `SYSTEM` | Exit to operating system |
| `CONT` | Continue after STOP |
| `TRON` / `TROFF` | Trace debugging |

**NOW SUPPORTED:**
- `STOP` - Stop program execution
- `END` - End program

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

| Command | Description |
|---------|-------------|
| `LPRINT` | Print to printer |
| `LPRINT USING` | Formatted printer output |

**NOW SUPPORTED:**
- `WIDTH` - Set screen width
- `PRINT USING` - Formatted output
- `CSRLIN`, `POS(0)` - Cursor position
- `TAB(n)`, `SPC(n)` - Print spacing
- `LOCATE` - Position cursor

---

## User-Defined Types

**NOW SUPPORTED:**
- `TYPE...END TYPE` - Define record structure
- `DIM var AS typename` - Declare typed variable
- Array of TYPE support

---

## Binary/Random File Operations

| Command | Description |
|----------|-------------|
| `FIELD` | Define record fields |
| `LSET` / `RSET` | Justify string in field |
| `MKI$`, `MKL$`, `MKS$`, `MKD$` | Convert number to string |
| `CVI`, `CVL`, `CVS`, `CVD` | Convert string to number |

---

## Environment

**NOW SUPPORTED:**
- `ENVIRON$` - Read environment variable
- `COMMAND$` - Get command line arguments

| Command | Description |
|---------|-------------|
| `ENVIRON` | Set environment variable |

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
| `$INCLUDE` | Include external file |
| `$DYNAMIC` / `$STATIC` | Array storage declarations |
| `KEY` / `KEY(n) ON/OFF` | Function key handling |
| `ON KEY(n) GOSUB` | Key event handler |
| `STRIG` / `STICK` | Joystick functions |
| `ON STRIG GOSUB` | Joystick event handler |
| `PEN` / `ON PEN GOSUB` | Light pen input |
| `ON TIMER GOSUB` | Timer event handler |
| `TIMER ON/OFF` | Enable/disable timer events |
| `PLAY(n)` | Get background music queue |
| `ON PLAY GOSUB` | Music event handler |

**NOW SUPPORTED:**
- `DEF type` (DEFINT, DEFSNG, etc.) - Ignored, uses dynamic typing
- `COMMON SHARED` / `DIM SHARED` - Declare shared variables

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
- GOSUB/RETURN and SUB/FUNCTION procedures
- Graphics: SCREEN modes, LINE, CIRCLE, PSET, GET/PUT sprites, PALETTE
- Sound: SOUND, BEEP, PLAY (MML)
- File I/O: OPEN, CLOSE, INPUT#, PRINT#, WRITE#, EOF, LOF
- User-defined types (TYPE...END TYPE)
- Error handling (ON ERROR GOTO, RESUME)
- Integer division operator (\)
- Hex/octal/binary literals (&H, &O, &B)
