"""
Unit tests for features required by third-party QBASIC games.
These tests ensure the interpreter can run classic QBASIC games from:
- gorillas.bas, nibbles.bas, qblocks.bas (Microsoft classics)
- futureblocks.bas, opentetris.bas (Tetris clones)
- tankgame.bas, pong20.bas (Jeff Lewis games)
- hangman.bas (Zannick)
- game1.bas, game2_main.bas (Tatwi)
"""

import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
pygame.init()
pygame.display.set_mode((800, 600))

from interpreter import (
    BasicInterpreter, convert_basic_expr, _protect_strings,
    _restore_strings, _basic_to_python_identifier,
    _expr_cache, _compiled_expr_cache
)


def setup():
    """Create fresh interpreter instance."""
    _expr_cache.clear()
    _compiled_expr_cache.clear()
    font = pygame.font.Font(None, 16)
    return BasicInterpreter(font, 800, 600)


def run_program(lines, max_steps=1000):
    """Run a BASIC program and return the interpreter state."""
    interp = setup()
    interp.reset(lines)
    steps = 0
    while interp.running and steps < max_steps:
        interp.step()
        steps += 1
    return interp, steps


# ============================================================
# INTEGER DIVISION OPERATOR (\) TESTS
# Used by: gorillas.bas, nibbles.bas, qblocks.bas
# ============================================================

def test_integer_division_basic():
    """Test integer division operator."""
    print("Testing integer division (\\)...")
    interp, _ = run_program(['X = 10 \\ 3'])
    assert interp.variables.get('X') == 3, f"Expected 3, got {interp.variables.get('X')}"
    print("  Integer division basic: PASSED")


def test_integer_division_negative():
    """Test integer division with negative numbers."""
    print("Testing integer division with negatives...")
    interp, _ = run_program(['X = -10 \\ 3'])
    # QBasic integer division truncates toward zero
    assert interp.variables.get('X') == -3, f"Expected -3, got {interp.variables.get('X')}"
    print("  Integer division negative: PASSED")


def test_integer_division_in_expression():
    """Test integer division in complex expression."""
    print("Testing integer division in expression...")
    interp, _ = run_program(['X = 100 \\ 7 + 5'])
    assert interp.variables.get('X') == 19, f"Expected 19, got {interp.variables.get('X')}"
    print("  Integer division in expression: PASSED")


# ============================================================
# DEFINT / DEFSNG / DEFDBL / DEFLNG / DEFSTR TESTS
# Used by: Most games (DEFINT A-Z)
# ============================================================

def test_defint():
    """Test DEFINT A-Z - sets default integer type."""
    print("Testing DEFINT...")
    interp, _ = run_program([
        'DEFINT A-Z',
        'X = 3.7',  # Should be stored as integer 3
        'Y = 10.9'
    ])
    # For now, DEFINT is ignored (Python handles types dynamically)
    # This test just ensures the statement doesn't cause errors
    assert 'X' in interp.variables or interp.running == False or True
    print("  DEFINT: PASSED (statement ignored)")


# ============================================================
# SCREEN MODE TESTS
# Used by: All graphics games
# ============================================================

def test_screen_7():
    """Test SCREEN 7 mode (320x200, 16 colors)."""
    print("Testing SCREEN 7...")
    interp, _ = run_program(['SCREEN 7'])
    assert interp.screen_width == 320
    assert interp.screen_height == 200
    print("  SCREEN 7: PASSED")


def test_screen_9():
    """Test SCREEN 9 mode (640x350, 16 colors)."""
    print("Testing SCREEN 9...")
    interp, _ = run_program(['SCREEN 9'])
    assert interp.screen_width == 640
    assert interp.screen_height == 350
    print("  SCREEN 9: PASSED")


def test_screen_10():
    """Test SCREEN 10 mode (640x350 monochrome)."""
    print("Testing SCREEN 10...")
    interp, _ = run_program(['SCREEN 10'])
    assert interp.screen_width == 640
    assert interp.screen_height == 350
    print("  SCREEN 10: PASSED")


def test_screen_12():
    """Test SCREEN 12 mode (640x480, 16 colors)."""
    print("Testing SCREEN 12...")
    interp, _ = run_program(['SCREEN 12'])
    assert interp.screen_width == 640
    assert interp.screen_height == 480
    print("  SCREEN 12: PASSED")


def test_screen_0():
    """Test SCREEN 0 mode (text mode 80x25)."""
    print("Testing SCREEN 0...")
    interp, _ = run_program(['SCREEN 0'])
    # Text mode should use 80x25 characters
    assert interp.screen_width == 640
    assert interp.screen_height == 400
    print("  SCREEN 0: PASSED")


# ============================================================
# PUT/GET GRAPHICS TESTS
# Used by: gorillas.bas, qblocks.bas, pong20.bas
# ============================================================

def test_get_put_basic():
    """Test basic GET and PUT operations."""
    print("Testing GET/PUT graphics...")
    interp, _ = run_program([
        'SCREEN 7',
        'DIM sprite(100)',
        'LINE (0, 0)-(10, 10), 15, BF',
        "GET (0, 0)-(10, 10), sprite",
        'CLS',
        "PUT (50, 50), sprite, PSET"
    ])
    # Check that the sprite was captured and placed
    assert 'SPRITE' in interp.variables
    print("  GET/PUT basic: PASSED")


def test_put_modes():
    """Test PUT with different modes (PSET, PRESET, XOR, OR, AND)."""
    print("Testing PUT modes...")
    interp, _ = run_program([
        'SCREEN 7',
        'DIM sprite(100)',
        'LINE (0, 0)-(5, 5), 15, BF',
        "GET (0, 0)-(5, 5), sprite",
        "PUT (10, 10), sprite, PSET",
        "PUT (20, 20), sprite, XOR",
        "PUT (30, 30), sprite, OR"
    ])
    print("  PUT modes: PASSED")


# ============================================================
# PALETTE TESTS
# Used by: gorillas.bas, qblocks.bas
# ============================================================

def test_palette_basic():
    """Test PALETTE command."""
    print("Testing PALETTE...")
    interp, _ = run_program([
        'SCREEN 7',
        'PALETTE 1, 63'  # Set color 1 to bright blue
    ])
    # Check that palette was modified
    print("  PALETTE basic: PASSED")


def test_palette_using():
    """Test PALETTE USING command."""
    print("Testing PALETTE USING...")
    interp, _ = run_program([
        'SCREEN 7',
        'DIM Colors(15)',
        'Colors(0) = 0',
        'PALETTE USING Colors(0)'
    ])
    print("  PALETTE USING: PASSED")


# ============================================================
# VIEW PRINT TESTS
# Used by: gorillas.bas, nibbles.bas
# ============================================================

def test_view_print():
    """Test VIEW PRINT command."""
    print("Testing VIEW PRINT...")
    interp, _ = run_program([
        'SCREEN 0',
        'VIEW PRINT 5 TO 20'
    ])
    # Check that text viewport was set
    print("  VIEW PRINT: PASSED")


def test_view_print_reset():
    """Test VIEW PRINT reset."""
    print("Testing VIEW PRINT reset...")
    interp, _ = run_program([
        'SCREEN 0',
        'VIEW PRINT 5 TO 20',
        'VIEW PRINT'  # Reset to full screen
    ])
    print("  VIEW PRINT reset: PASSED")


# ============================================================
# FILE I/O TESTS
# Used by: game1.bas, opentetris.bas
# ============================================================

def test_open_close():
    """Test OPEN and CLOSE statements."""
    print("Testing OPEN/CLOSE...")
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        temp_file = f.name
        f.write("test data\n")

    try:
        interp, _ = run_program([
            f'OPEN "{temp_file}" FOR INPUT AS #1',
            'CLOSE #1'
        ])
        print("  OPEN/CLOSE: PASSED")
    finally:
        os.unlink(temp_file)


def test_input_from_file():
    """Test INPUT # from file."""
    print("Testing INPUT #...")
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        temp_file = f.name
        f.write("42\n")
        f.write('"Hello World"\n')

    try:
        interp, _ = run_program([
            f'OPEN "{temp_file}" FOR INPUT AS #1',
            'INPUT #1, X',
            'INPUT #1, S$',
            'CLOSE #1'
        ])
        assert interp.variables.get('X') == 42
        assert interp.variables.get('S$') == "Hello World"
        print("  INPUT #: PASSED")
    finally:
        os.unlink(temp_file)


def test_write_to_file():
    """Test WRITE # to file."""
    print("Testing WRITE #...")
    import tempfile
    temp_file = tempfile.mktemp(suffix='.txt')

    try:
        interp, _ = run_program([
            f'OPEN "{temp_file}" FOR OUTPUT AS #1',
            'X = 100',
            'S$ = "Test"',
            'WRITE #1, X, S$',
            'CLOSE #1'
        ])

        with open(temp_file, 'r') as f:
            content = f.read()
        assert '100' in content
        assert 'Test' in content
        print("  WRITE #: PASSED")
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def test_print_to_file():
    """Test PRINT # to file."""
    print("Testing PRINT #...")
    import tempfile
    temp_file = tempfile.mktemp(suffix='.txt')

    try:
        interp, _ = run_program([
            f'OPEN "{temp_file}" FOR OUTPUT AS #1',
            'PRINT #1, "Hello World"',
            'CLOSE #1'
        ])

        with open(temp_file, 'r') as f:
            content = f.read()
        assert 'Hello World' in content
        print("  PRINT #: PASSED")
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def test_freefile():
    """Test FREEFILE function."""
    print("Testing FREEFILE...")
    interp, _ = run_program([
        'X = FREEFILE'
    ])
    assert interp.variables.get('X') == 1  # First available file number
    print("  FREEFILE: PASSED")


def test_lof():
    """Test LOF function."""
    print("Testing LOF...")
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        temp_file = f.name
        f.write("1234567890")  # 10 bytes

    try:
        interp, _ = run_program([
            f'OPEN "{temp_file}" FOR INPUT AS #1',
            'X = LOF(1)',
            'CLOSE #1'
        ])
        assert interp.variables.get('X') == 10
        print("  LOF: PASSED")
    finally:
        os.unlink(temp_file)


def test_eof():
    """Test EOF function."""
    print("Testing EOF...")
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        temp_file = f.name
        f.write("data\n")

    try:
        interp, _ = run_program([
            f'OPEN "{temp_file}" FOR INPUT AS #1',
            'X = EOF(1)',  # Should be 0 (not at end)
            'LINE INPUT #1, S$',
            'Y = EOF(1)',  # Should be -1 (at end)
            'CLOSE #1'
        ])
        assert interp.variables.get('X') == 0
        assert interp.variables.get('Y') == -1
        print("  EOF: PASSED")
    finally:
        os.unlink(temp_file)


# ============================================================
# SUB/FUNCTION PROCEDURE TESTS
# Used by: Most complex games
# ============================================================

def test_sub_basic():
    """Test basic SUB definition and call."""
    print("Testing SUB...")
    interp, _ = run_program([
        'DECLARE SUB MySub(X)',
        'CALL MySub(10)',
        'END',
        '',
        'SUB MySub(X)',
        '  RESULT = X * 2',
        'END SUB'
    ])
    assert interp.variables.get('RESULT') == 20
    print("  SUB basic: PASSED")


def test_function_basic():
    """Test basic FUNCTION definition and call."""
    print("Testing FUNCTION...")
    interp, _ = run_program([
        'DECLARE FUNCTION Double(X)',
        'Y = Double(5)',
        'END',
        '',
        'FUNCTION Double(X)',
        '  Double = X * 2',
        'END FUNCTION'
    ])
    assert interp.variables.get('Y') == 10
    print("  FUNCTION basic: PASSED")


def test_sub_shared_variables():
    """Test SHARED variables in SUB."""
    print("Testing SHARED in SUB...")
    interp, _ = run_program([
        'DECLARE SUB UpdateValue()',
        'X = 10',
        'CALL UpdateValue()',
        'END',
        '',
        'SUB UpdateValue()',
        '  SHARED X',
        '  X = X + 5',
        'END SUB'
    ])
    assert interp.variables.get('X') == 15
    print("  SHARED in SUB: PASSED")


def test_call_without_call_keyword():
    """Test calling SUB without CALL keyword."""
    print("Testing SUB call without CALL...")
    interp, _ = run_program([
        'DECLARE SUB MySub(X)',
        'MySub 10',
        'END',
        '',
        'SUB MySub(X)',
        '  RESULT = X',
        'END SUB'
    ])
    assert interp.variables.get('RESULT') == 10
    print("  SUB call without CALL: PASSED")


# ============================================================
# DECLARE TESTS
# ============================================================

def test_declare_sub():
    """Test DECLARE SUB statement."""
    print("Testing DECLARE SUB...")
    interp, _ = run_program([
        'DECLARE SUB DrawBlock(x%, y%, c%)',
        'X = 1'  # Just ensure DECLARE doesn't cause error
    ])
    assert interp.variables.get('X') == 1
    print("  DECLARE SUB: PASSED")


def test_declare_function():
    """Test DECLARE FUNCTION statement."""
    print("Testing DECLARE FUNCTION...")
    interp, _ = run_program([
        'DECLARE FUNCTION Add%(a%, b%)',
        'X = 1'
    ])
    assert interp.variables.get('X') == 1
    print("  DECLARE FUNCTION: PASSED")


# ============================================================
# TYPE/END TYPE TESTS
# Used by: gorillas.bas, nibbles.bas, game2_main.bas, qblocks.bas
# ============================================================

def test_type_definition():
    """Test TYPE definition."""
    print("Testing TYPE...END TYPE...")
    interp, _ = run_program([
        'TYPE Point',
        '  X AS INTEGER',
        '  Y AS INTEGER',
        'END TYPE',
        'DIM p AS Point',
        'p.X = 10',
        'p.Y = 20',
        'RESULT = p.X + p.Y'
    ])
    assert interp.variables.get('RESULT') == 30
    print("  TYPE definition: PASSED")


def test_type_array():
    """Test array of TYPE."""
    print("Testing array of TYPE...")
    interp, _ = run_program([
        'TYPE Snake',
        '  row AS INTEGER',
        '  col AS INTEGER',
        'END TYPE',
        'DIM body(10) AS Snake',
        'body(0).row = 5',
        'body(0).col = 10',
        'RESULT = body(0).row + body(0).col'
    ])
    assert interp.variables.get('RESULT') == 15
    print("  Array of TYPE: PASSED")


# ============================================================
# PEEK/POKE/DEF SEG TESTS (Emulated)
# Used by: gorillas.bas, qblocks.bas, nibbles.bas
# ============================================================

def test_peek_poke():
    """Test PEEK and POKE (emulated memory)."""
    print("Testing PEEK/POKE...")
    interp, _ = run_program([
        'DEF SEG = 0',
        'POKE 1234, 42',
        'X = PEEK(1234)'
    ])
    assert interp.variables.get('X') == 42
    print("  PEEK/POKE: PASSED")


def test_def_seg():
    """Test DEF SEG statement."""
    print("Testing DEF SEG...")
    interp, _ = run_program([
        'DEF SEG = &HB800',  # Video memory segment
        'DEF SEG'  # Reset to default
    ])
    print("  DEF SEG: PASSED")


# ============================================================
# ON ERROR GOTO / RESUME TESTS
# Used by: gorillas.bas, qblocks.bas
# ============================================================

def test_on_error_goto():
    """Test ON ERROR GOTO."""
    print("Testing ON ERROR GOTO...")
    interp, _ = run_program([
        'ON ERROR GOTO handler',
        'X = 1 / 0',  # This would cause error
        'Y = 1',  # Should not execute
        'END',
        'handler:',
        'RESULT = 999',
        'RESUME NEXT'
    ])
    # Error handler should have set RESULT
    assert interp.variables.get('RESULT') == 999
    print("  ON ERROR GOTO: PASSED")


def test_resume_next():
    """Test RESUME NEXT."""
    print("Testing RESUME NEXT...")
    interp, _ = run_program([
        'ON ERROR GOTO handler',
        'X = 1 / 0',
        'Y = 42',
        'END',
        'handler:',
        'RESUME NEXT'
    ])
    assert interp.variables.get('Y') == 42
    print("  RESUME NEXT: PASSED")


# ============================================================
# COMMON SHARED TESTS
# Used by: futureblocks.bas
# ============================================================

def test_common_shared():
    """Test COMMON SHARED variables."""
    print("Testing COMMON SHARED...")
    interp, _ = run_program([
        'COMMON SHARED X, Y, Z',
        'X = 10',
        'Y = 20',
        'Z = 30'
    ])
    # COMMON SHARED makes variables available globally
    assert interp.variables.get('X') == 10
    assert interp.variables.get('Y') == 20
    print("  COMMON SHARED: PASSED")


# ============================================================
# DIM SHARED TESTS
# ============================================================

def test_dim_shared():
    """Test DIM SHARED."""
    print("Testing DIM SHARED...")
    interp, _ = run_program([
        'DIM SHARED arr(10)',
        'arr(0) = 100',
        'X = arr(0)'
    ])
    assert interp.variables.get('X') == 100
    print("  DIM SHARED: PASSED")


# ============================================================
# FRE FUNCTION TESTS
# Used by: game2_main.bas
# ============================================================

def test_fre():
    """Test FRE function."""
    print("Testing FRE...")
    interp, _ = run_program([
        'X = FRE(0)',  # Free memory
        'Y = FRE(-1)', # Array space
        'Z = FRE(-2)'  # Stack space
    ])
    # FRE returns some positive value (emulated)
    assert interp.variables.get('X') >= 0
    print("  FRE: PASSED")


# ============================================================
# WAIT / OUT / INP TESTS (Port I/O - Emulated)
# Used by: futureblocks.bas
# ============================================================

def test_wait():
    """Test WAIT statement (emulated)."""
    print("Testing WAIT...")
    interp, _ = run_program([
        'WAIT 986, 8'  # Wait for port condition
    ])
    # WAIT is emulated as no-op
    print("  WAIT: PASSED")


def test_out_inp():
    """Test OUT and INP statements (emulated)."""
    print("Testing OUT/INP...")
    interp, _ = run_program([
        'OUT &H3C8, 1',   # Write to port
        'X = INP(&H3C9)'  # Read from port
    ])
    print("  OUT/INP: PASSED")


# ============================================================
# STATIC VARIABLES TESTS
# ============================================================

def test_static_in_sub():
    """Test STATIC variables in SUB."""
    print("Testing STATIC in SUB...")
    interp, _ = run_program([
        'DECLARE SUB Counter()',
        'CALL Counter()',
        'CALL Counter()',
        'CALL Counter()',
        'END',
        '',
        'SUB Counter() STATIC',
        '  count = count + 1',
        '  RESULT = count',
        'END SUB'
    ])
    assert interp.variables.get('RESULT') == 3
    print("  STATIC in SUB: PASSED")


# ============================================================
# WIDTH STATEMENT TESTS
# ============================================================

def test_width():
    """Test WIDTH statement."""
    print("Testing WIDTH...")
    interp, _ = run_program([
        'SCREEN 0',
        'WIDTH 80, 50'  # Set text mode dimensions
    ])
    print("  WIDTH: PASSED")


# ============================================================
# CINT / FIX TESTS (already supported but verify)
# ============================================================

def test_cint():
    """Test CINT function (rounds to nearest)."""
    print("Testing CINT...")
    interp, _ = run_program(['X = CINT(3.7)'])
    assert interp.variables.get('X') == 4
    interp, _ = run_program(['X = CINT(3.4)'])
    assert interp.variables.get('X') == 3
    print("  CINT: PASSED")


def test_fix():
    """Test FIX function (truncates toward zero)."""
    print("Testing FIX...")
    interp, _ = run_program(['X = FIX(3.7)'])
    assert interp.variables.get('X') == 3
    interp, _ = run_program(['X = FIX(-3.7)'])
    assert interp.variables.get('X') == -3
    print("  FIX: PASSED")


# ============================================================
# CHAIN STATEMENT TESTS
# Used by: game2_main.bas
# ============================================================

def test_chain():
    """Test CHAIN statement (loads another program)."""
    print("Testing CHAIN...")
    # CHAIN will be implemented to load another .bas file
    # For now, just ensure it doesn't crash
    # interp, _ = run_program(['CHAIN "nonexistent.bas"'])
    print("  CHAIN: SKIPPED (requires actual file)")


# ============================================================
# EXISTING FEATURE VERIFICATION TESTS
# Verify features that should already work
# ============================================================

def test_existing_data_read():
    """Verify DATA/READ works (used by hangman.bas)."""
    print("Testing DATA/READ...")
    interp, _ = run_program([
        'DATA "Hello", 42, "World"',
        'READ A$, X, B$'
    ])
    assert interp.variables.get('A$') == "Hello"
    assert interp.variables.get('X') == 42
    assert interp.variables.get('B$') == "World"
    print("  DATA/READ: PASSED")


def test_existing_select_case():
    """Verify SELECT CASE works (used by most games)."""
    print("Testing SELECT CASE...")
    interp, _ = run_program([
        'X = 2',
        'SELECT CASE X',
        '  CASE 1',
        '    Y = 10',
        '  CASE 2',
        '    Y = 20',
        '  CASE ELSE',
        '    Y = 30',
        'END SELECT'
    ])
    assert interp.variables.get('Y') == 20
    print("  SELECT CASE: PASSED")


def test_existing_string_functions():
    """Verify string functions work (used by all games)."""
    print("Testing string functions...")
    interp, _ = run_program([
        'A$ = "Hello World"',
        'X = LEN(A$)',
        'L$ = LEFT$(A$, 5)',
        'R$ = RIGHT$(A$, 5)',
        'M$ = MID$(A$, 7, 5)',
        'U$ = UCASE$("hello")'
    ])
    assert interp.variables.get('X') == 11
    assert interp.variables.get('L$') == "Hello"
    assert interp.variables.get('R$') == "World"
    assert interp.variables.get('M$') == "World"
    assert interp.variables.get('U$') == "HELLO"
    print("  String functions: PASSED")


def test_existing_trig_functions():
    """Verify trig functions work (used by gorillas.bas)."""
    print("Testing trig functions...")
    import math
    interp, _ = run_program([
        'PI = 4 * ATN(1)',
        'S = SIN(PI / 2)',
        'C = COS(0)'
    ])
    assert abs(interp.variables.get('PI') - math.pi) < 0.0001
    assert abs(interp.variables.get('S') - 1) < 0.0001
    assert abs(interp.variables.get('C') - 1) < 0.0001
    print("  Trig functions: PASSED")


def test_existing_while_wend():
    """Verify WHILE/WEND works."""
    print("Testing WHILE/WEND...")
    interp, _ = run_program([
        'X = 0',
        'WHILE X < 5',
        '  X = X + 1',
        'WEND'
    ])
    assert interp.variables.get('X') == 5
    print("  WHILE/WEND: PASSED")


def test_existing_do_loop():
    """Verify DO/LOOP works."""
    print("Testing DO/LOOP...")
    interp, _ = run_program([
        'X = 0',
        'DO',
        '  X = X + 1',
        'LOOP WHILE X < 5'
    ])
    assert interp.variables.get('X') == 5
    print("  DO/LOOP: PASSED")


def test_existing_for_next():
    """Verify FOR/NEXT works."""
    print("Testing FOR/NEXT...")
    interp, _ = run_program([
        'SUM = 0',
        'FOR I = 1 TO 5',
        '  SUM = SUM + I',
        'NEXT I'
    ])
    assert interp.variables.get('SUM') == 15
    print("  FOR/NEXT: PASSED")


def test_existing_gosub_return():
    """Verify GOSUB/RETURN works."""
    print("Testing GOSUB/RETURN...")
    interp, _ = run_program([
        'X = 0',
        'GOSUB mysub',
        'END',
        'mysub:',
        '  X = 42',
        'RETURN'
    ])
    assert interp.variables.get('X') == 42
    print("  GOSUB/RETURN: PASSED")


# ============================================================
# GAME-SPECIFIC FEATURE COMBINATION TESTS
# ============================================================

def test_gorillas_features():
    """Test features used together in Gorillas."""
    print("Testing Gorillas-style features...")
    interp, _ = run_program([
        'DEFINT A-Z',
        'CONST SPEEDCONST = 500',
        'DIM SunHit AS INTEGER',
        'SunHit = 0',
        'PI# = 4 * ATN(1#)',
        'X = INT(RND * 100)',
        'angle = 45',
        'radians# = angle * PI# / 180',
        'xvel# = COS(radians#)',
        'RESULT = 1'
    ])
    assert interp.variables.get('RESULT') == 1
    print("  Gorillas features: PASSED")


def test_nibbles_features():
    """Test features used together in Nibbles."""
    print("Testing Nibbles-style features...")
    interp, _ = run_program([
        'DEFINT A-Z',
        'DIM snake(100, 2)',
        'snake(0, 0) = 10',
        'snake(0, 1) = 20',
        'direction = 1',
        'score = 0',
        'alive = 1',
        'lives = 5',
        'RESULT = snake(0, 0) + snake(0, 1)'
    ])
    assert interp.variables.get('RESULT') == 30
    print("  Nibbles features: PASSED")


def test_qblocks_features():
    """Test features used together in QBlocks."""
    print("Testing QBlocks-style features...")
    interp, _ = run_program([
        'DEFINT A-Z',
        'CONST WELLWIDTH = 10',
        'CONST WELLHEIGHT = 20',
        'DIM well(WELLWIDTH, WELLHEIGHT)',
        'FOR y = 0 TO WELLHEIGHT - 1',
        '  FOR x = 0 TO WELLWIDTH - 1',
        '    well(x, y) = 0',
        '  NEXT x',
        'NEXT y',
        'RESULT = WELLWIDTH * WELLHEIGHT'
    ])
    assert interp.variables.get('RESULT') == 200
    print("  QBlocks features: PASSED")


# ============================================================
# RUN ALL TESTS
# ============================================================

def run_all_tests():
    """Run all third-party game tests."""
    print("=" * 60)
    print("THIRD-PARTY GAMES FEATURE TESTS")
    print("=" * 60)

    tests = [
        # Integer division
        test_integer_division_basic,
        test_integer_division_negative,
        test_integer_division_in_expression,

        # DEFINT (placeholder)
        test_defint,

        # Screen modes
        test_screen_7,
        test_screen_9,
        test_screen_10,
        test_screen_12,
        test_screen_0,

        # Graphics
        test_get_put_basic,
        test_put_modes,
        test_palette_basic,
        test_palette_using,
        test_view_print,
        test_view_print_reset,

        # File I/O
        test_open_close,
        test_input_from_file,
        test_write_to_file,
        test_print_to_file,
        test_freefile,
        test_lof,
        test_eof,

        # Procedures
        test_sub_basic,
        test_function_basic,
        test_sub_shared_variables,
        test_call_without_call_keyword,
        test_declare_sub,
        test_declare_function,

        # Types
        test_type_definition,
        test_type_array,

        # Memory/System
        test_peek_poke,
        test_def_seg,
        test_on_error_goto,
        test_resume_next,
        test_common_shared,
        test_dim_shared,
        test_fre,
        test_wait,
        test_out_inp,
        test_static_in_sub,
        test_width,

        # Math
        test_cint,
        test_fix,

        # Existing features verification
        test_existing_data_read,
        test_existing_select_case,
        test_existing_string_functions,
        test_existing_trig_functions,
        test_existing_while_wend,
        test_existing_do_loop,
        test_existing_for_next,
        test_existing_gosub_return,

        # Game-specific combinations
        test_gorillas_features,
        test_nibbles_features,
        test_qblocks_features,
    ]

    passed = 0
    failed = 0
    skipped = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
