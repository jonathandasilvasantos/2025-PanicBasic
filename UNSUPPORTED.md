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
| `PRESET` | Plot point (like PSET but inverts) |
| `SCREEN` (modes other than 13) | Only SCREEN 13 (320x200) is supported |

---

## Sound Commands

| Command | Description |
|---------|-------------|
| `SOUND` | Generate tone (frequency, duration) |
| `PLAY` | Play music using MML strings |
| `BEEP` | System beep |

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
| `INPUT` | Prompt user for keyboard input |
| `LINE INPUT` | Input entire line from keyboard |
| `INPUT$` | Read specific number of characters |
| `INPUT$(n, #filenum)` | Read characters from file |

---

## Data Statements

| Command | Description |
|---------|-------------|
| `DATA` | Define inline data values |
| `READ` | Read values from DATA statements |
| `RESTORE` | Reset DATA pointer |

---

## Procedures and Functions

| Command | Description |
|---------|-------------|
| `SUB...END SUB` | Define subroutine |
| `FUNCTION...END FUNCTION` | Define function |
| `DECLARE` | Declare SUB or FUNCTION |
| `CALL` | Call subroutine |
| `DEF FN` | Define inline function |
| `SHARED` | Share variables with main program |
| `STATIC` | Declare static local variables |

---

## Advanced Control Flow

| Command | Description |
|---------|-------------|
| `SELECT CASE...END SELECT` | Multi-way branching |
| `CASE` | Case clause in SELECT |
| `CASE ELSE` | Default case |
| `WHILE...WEND` | While loop (use DO WHILE instead) |
| `ON...GOTO` | Computed GOTO |
| `ON...GOSUB` | Computed GOSUB |
| `ON ERROR GOTO` | Error handler |
| `RESUME` | Resume after error |
| `ERROR` | Trigger error |

---

## String Functions

| Function | Description |
|----------|-------------|
| `ASC(s$)` | Get ASCII code of first character |
| `INSTR(s$, find$)` | Find substring position |
| `LCASE$(s$)` | Convert to lowercase |
| `UCASE$(s$)` | Convert to uppercase |
| `LTRIM$(s$)` | Remove leading spaces |
| `RTRIM$(s$)` | Remove trailing spaces |
| `SPACE$(n)` | Create string of n spaces |
| `STRING$(n, char)` | Create string of n characters |
| `HEX$(n)` | Convert to hexadecimal string |
| `OCT$(n)` | Convert to octal string |

---

## Math Functions

| Function | Description |
|----------|-------------|
| `LOG(x)` | Natural logarithm |
| `EXP(x)` | Exponential (e^x) |
| `CINT(x)` | Convert to integer (round) |
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
| `SWAP` | Exchange two variables |
| `ERASE` | Erase arrays |
| `REDIM` | Redimension dynamic array |
| `LBOUND` | Get array lower bound |
| `UBOUND` | Get array upper bound |
| `VARPTR` | Get variable address |
| `VARSEG` | Get variable segment |
| `SADD` | Get string address |
| `FRE` | Get free memory |

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
| `DATE$` | Get/set system date |
| `TIME$` | Get/set system time |

Note: `TIMER` IS supported (returns seconds since midnight).

---

## Printing and Screen

| Command | Description |
|---------|-------------|
| `LPRINT` | Print to printer |
| `WIDTH` | Set screen/printer width |
| `CSRLIN` | Get cursor row |
| `POS(0)` | Get cursor column |
| `TAB(n)` | Tab to column in PRINT |
| `SPC(n)` | Print n spaces |
| `PRINT USING` | Formatted output |
| `LPRINT USING` | Formatted printer output |

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
| `ENVIRON$` | Get environment variable |
| `ENVIRON` | Set environment variable |
| `COMMAND$` | Get command line arguments |

---

## Miscellaneous

| Command | Description |
|---------|-------------|
| `DEF type` | Set default variable type (DEFINT, DEFSNG, etc.) |
| `OPTION BASE` | Set default array lower bound |
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
| `WHILE...WEND` | Use `DO WHILE...LOOP` |
| `INPUT` | Use `INKEY$` in a loop |
| `SELECT CASE` | Use multiple `IF...THEN` |
| `SUB/FUNCTION` | Use `GOSUB...RETURN` |
| `ASC(s$)` | Not available - consider adding to interpreter |
| `INSTR` | Not available - implement with MID$ loop |

---

## Priority Features for Future Implementation

These features would have high impact if added:

1. **ASC(s$)** - Get ASCII code (common need)
2. **INSTR** - Find substring (very useful)
3. **SELECT CASE** - Cleaner multi-way branching
4. **SOUND/PLAY** - Audio support
5. **GET/PUT** - Sprite graphics
6. **INPUT** - User text input
7. **DATA/READ** - Inline data storage
8. **LCASE$/UCASE$** - String case conversion
