# Unsupported QBasic 4.5 Features

This document lists QBasic 4.5 features that are **not currently supported** by this interpreter.

---

## Not Planned (Non-Standard Extensions)

These functions are not part of standard QBasic 4.5:

| Function | Description | Notes |
|----------|-------------|-------|
| `ASIN(x)` | Arcsine | PowerBASIC/FreeBASIC extension |
| `ACOS(x)` | Arccosine | PowerBASIC/FreeBASIC extension |

**Workaround:** Use `ATN` to compute these:
```basic
' ASIN(x) = ATN(x / SQR(1 - x * x))
' ACOS(x) = ATN(SQR(1 - x * x) / x)  ' for x > 0
```

---

## Known Limitations

### Emulated Features
These features are implemented for compatibility but have limitations:

| Feature | Limitation |
|---------|------------|
| `PEEK`/`POKE` | Emulated memory, no real hardware access |
| `INP`/`OUT` | Emulated port I/O, values stored internally |
| `DEF SEG` | Segment changes tracked but memory is emulated |
| `PEN` | Light pen emulated via mouse input |
| `STICK`/`STRIG` | Requires physical joystick connected |
| `ON PLAY GOSUB` | Stub only, never triggers (no background music queue) |

### Stub Implementations
These are accepted for compatibility but have no effect:

| Feature | Behavior |
|---------|----------|
| `DEFINT`, `DEFSNG`, `DEFLNG`, `DEFDBL`, `DEFSTR` | Ignored, uses dynamic typing |
| `$DYNAMIC`, `$STATIC` | Accepted, Python handles array storage |
| `WAIT` | No-op (returns immediately) |

---

## Full Compatibility Status

This interpreter supports **all standard QBasic 4.5 features** including:

- All control flow (IF/THEN/ELSE, FOR/NEXT, DO/LOOP, WHILE/WEND, SELECT CASE)
- All graphics commands (SCREEN modes 0-13, LINE, CIRCLE, PSET, GET/PUT, PALETTE, VIEW, WINDOW)
- All sound commands (SOUND, BEEP, PLAY with MML)
- All file I/O (sequential, random, binary access)
- All string functions (LEFT$, RIGHT$, MID$, INSTR, etc.)
- All math functions (standard QBasic set)
- SUB/FUNCTION procedures with SHARED, STATIC, array parameters
- User-defined types (TYPE...END TYPE)
- Error handling (ON ERROR GOTO, RESUME)
- Event handling (ON KEY, ON TIMER, ON STRIG, ON PEN)
- Program control (RUN, CHAIN, SHELL, SYSTEM)
- Memory functions (VARPTR, VARSEG, SADD - emulated)
- Environment access (ENVIRON, ENVIRON$, COMMAND$)
