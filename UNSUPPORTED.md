# Unsupported QBasic 4.5 Instructions

This document lists QBasic 4.5 features and instructions that are **not currently supported** by this interpreter.

---

## Graphics Commands

| Command | Description |
|---------|-------------|
| `GET (graphics)` | Capture screen region to array |
| `PUT (graphics)` | Display array as sprite on screen |
| `DRAW` | Turtle graphics drawing language |
| `PALETTE` | Modify color palette entries |
| `PALETTE USING` | Set entire palette from array |
| `PCOPY` | Copy video pages |
| `VIEW` | Define graphics viewport |
| `VIEW PRINT` | Define text viewport |
| `WINDOW` | Define logical coordinate system |
| `SCREEN` (modes other than 13) | Only SCREEN 13 (320x200) is supported |

Note: `PRESET` IS now supported.

---

## Sound Commands

| Command | Description |
|---------|-------------|
| `PLAY` | Play music using MML strings |

Note: `SOUND` and `BEEP` ARE now supported.

---

## File I/O

| Command | Description |
|---------|-------------|
| `OPEN` | Open file for reading/writing |
| `CLOSE` | Close file |
| `INPUT #` | Read from file |
| `LINE INPUT #` | Read line from file |
| `PRINT #` | Write to file |
| `WRITE #` | Write delimited data to file |
| `GET #` | Read binary record from file |
| `PUT #` | Write binary record to file |
| `SEEK` | Set file position |
| `LOC` | Get current file position |
| `LOF` | Get file length |
| `EOF` | Check for end of file |
| `FREEFILE` | Get next available file number |
| `KILL` | Delete file |
| `NAME` | Rename file |
| `FILES` | List directory contents |
| `CHDIR` | Change directory |
| `MKDIR` | Create directory |
| `RMDIR` | Remove directory |

---

## User Input

| Command | Description |
|---------|-------------|
| `INPUT$(n, #filenum)` | Read characters from file (only file form) |

Note: `INPUT`, `LINE INPUT`, and `INPUT$(n)` (keyboard) ARE now supported.

---

## Procedures and Functions

| Command | Description |
|---------|-------------|
| `SUB...END SUB` | Define subroutine |
| `FUNCTION...END FUNCTION` | Define function |
| `DECLARE` | Declare SUB or FUNCTION |
| `CALL` | Call subroutine |
| `SHARED` | Share variables with main program |
| `STATIC` | Declare static local variables |

Note: `DEF FN` (inline functions) IS now supported.

---

## Advanced Control Flow

| Command | Description |
|---------|-------------|
| `ON ERROR GOTO` | Error handler |
| `RESUME` | Resume after error |
| `ERROR` | Trigger error |

Note: `ON...GOTO` and `ON...GOSUB` ARE now supported.

---

## Math Functions

| Function | Description |
|----------|-------------|
| `CLNG(x)` | Convert to long integer |
| `CSNG(x)` | Convert to single precision |
| `CDBL(x)` | Convert to double precision |
| `ASIN(x)` | Arcsine (not in QBasic, but common) |
| `ACOS(x)` | Arccosine (not in QBasic, but common) |

---

## Memory and System

| Command | Description |
|---------|-------------|
| `PEEK` | Read memory byte |
| `POKE` | Write memory byte |
| `DEF SEG` | Set memory segment |
| `CLEAR` | Clear variables and set stack |
| `VARPTR` | Get variable address |
| `VARSEG` | Get variable segment |
| `SADD` | Get string address |
| `FRE` | Get free memory |

Note: `ERASE`, `LBOUND`, `UBOUND`, `REDIM`, and `OPTION BASE` ARE now supported.

---

## Program Execution

| Command | Description |
|---------|-------------|
| `RUN` | Run program |
| `CHAIN` | Load and run another program |
| `SHELL` | Execute DOS command |
| `SYSTEM` | Exit to operating system |
| `STOP` | Break execution (for debugging) |
| `CONT` | Continue after STOP |
| `TRON` | Trace on (debugging) |
| `TROFF` | Trace off |

---

## Date and Time

| Function | Description |
|----------|-------------|
| `DATE$ = value` | Set system date (reading IS supported) |
| `TIME$ = value` | Set system time (reading IS supported) |

Note: `TIMER`, `DATE$` (read), and `TIME$` (read) ARE supported.

---

## Printing and Screen

| Command | Description |
|---------|-------------|
| `LPRINT` | Print to printer |
| `WIDTH` | Set screen/printer width |
| `LPRINT USING` | Formatted printer output |

Note: `CSRLIN`, `POS(0)`, `TAB(n)`, `SPC(n)`, and `PRINT USING` ARE now supported.

---

## User-Defined Types

| Command | Description |
|---------|-------------|
| `TYPE...END TYPE` | Define record structure |
| `DIM var AS typename` | Declare typed variable |

---

## Binary/Random File Operations

| Command | Description |
|----------|-------------|
| `FIELD` | Define record fields |
| `LSET` | Left-justify string in field |
| `RSET` | Right-justify string in field |
| `MKI$` | Convert integer to string |
| `MKL$` | Convert long to string |
| `MKS$` | Convert single to string |
| `MKD$` | Convert double to string |
| `CVI` | Convert string to integer |
| `CVL` | Convert string to long |
| `CVS` | Convert string to single |
| `CVD` | Convert string to double |

---

## Environment

| Function | Description |
|----------|-------------|
| `ENVIRON` | Set environment variable |
| `COMMAND$` | Get command line arguments |

Note: `ENVIRON$` (read environment variable) IS now supported.

---

## Miscellaneous

| Command | Description |
|---------|-------------|
| `DEF type` | Set default variable type (DEFINT, DEFSNG, etc.) |
| `COMMON` | Share variables between modules |
| `$INCLUDE` | Include external file |
| `$DYNAMIC` | Declare dynamic arrays |
| `$STATIC` | Declare static arrays |
| `KEY` | Function key handling |
| `KEY(n) ON/OFF` | Enable/disable key trapping |
| `ON KEY(n) GOSUB` | Key event handler |
| `STRIG` | Joystick trigger |
| `STICK` | Joystick position |
| `ON STRIG GOSUB` | Joystick event handler |
| `PEN` | Light pen input |
| `ON PEN GOSUB` | Light pen event handler |
| `ON TIMER GOSUB` | Timer event handler |
| `TIMER ON/OFF` | Enable/disable timer events |
| `PLAY(n)` | Get background music queue |
| `ON PLAY GOSUB` | Music event handler |

---

## Supported Alternatives

Some unsupported features have workarounds:

| Unsupported | Alternative |
|-------------|-------------|
| `SUB/FUNCTION` | Use `GOSUB...RETURN` |

---

## Priority Features for Future Implementation

These features would have high impact if added:

1. **PLAY** - Music Macro Language (MML) support
2. **GET/PUT** - Sprite graphics
3. **SUB/FUNCTION** - User-defined procedures
