"""
Unit tests for Tetris game interpretation.
Tests the specific BASIC constructs used in tetris.bas to identify
issues with piece locking, collision detection, and game loop behavior.
"""

import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
pygame.init()
pygame.display.set_mode((800, 600))

from interpreter import (
    BasicInterpreter, convert_basic_expr,
    _expr_cache, _compiled_expr_cache
)

def setup():
    """Create fresh interpreter instance."""
    _expr_cache.clear()
    _compiled_expr_cache.clear()
    font = pygame.font.Font(None, 16)
    return BasicInterpreter(font, 800, 600)

def run_program(lines, max_steps=10000):
    """Run a BASIC program and return the interpreter state."""
    interp = setup()
    interp.reset(lines)
    steps = 0
    while interp.running and steps < max_steps:
        interp.step()
        steps += 1
    return interp, steps

# ============================================================
# TEST 2D ARRAY OPERATIONS (Critical for BOARD array)
# ============================================================

def test_2d_array_basic():
    """Test basic 2D array declaration and access."""
    print("Testing 2D array basic operations...")
    interp, _ = run_program([
        'DIM BOARD(19, 9)',
        'BOARD(0, 0) = 5',
        'BOARD(19, 9) = 10',
        'X = BOARD(0, 0)',
        'Y = BOARD(19, 9)'
    ])
    assert interp.variables.get('X') == 5, f"Expected 5, got {interp.variables.get('X')}"
    assert interp.variables.get('Y') == 10, f"Expected 10, got {interp.variables.get('Y')}"
    print("  2D array basic: PASSED")

def test_2d_array_variable_indices():
    """Test 2D array access with variable indices."""
    print("Testing 2D array with variable indices...")
    interp, _ = run_program([
        'DIM BOARD(19, 9)',
        'R = 5',
        'C = 3',
        'BOARD(R, C) = 42',
        'X = BOARD(R, C)',
        'Y = BOARD(5, 3)'
    ])
    assert interp.variables.get('X') == 42, f"Expected 42, got {interp.variables.get('X')}"
    assert interp.variables.get('Y') == 42, f"Expected 42, got {interp.variables.get('Y')}"
    print("  2D array variable indices: PASSED")

def test_2d_array_expression_indices():
    """Test 2D array access with expression indices (like TY, TX in Tetris)."""
    print("Testing 2D array with expression indices...")
    interp, _ = run_program([
        'DIM BOARD(19, 9)',
        'PIECEX = 4',
        'PIECEY = 0',
        'DIM PX(3)',
        'DIM PY(3)',
        'PX(0) = 0',
        'PY(0) = 0',
        'TX = PIECEX + PX(0)',
        'TY = PIECEY + PY(0)',
        'BOARD(TY, TX) = 11',
        'X = BOARD(TY, TX)'
    ])
    assert interp.variables.get('TX') == 4, f"Expected TX=4, got {interp.variables.get('TX')}"
    assert interp.variables.get('TY') == 0, f"Expected TY=0, got {interp.variables.get('TY')}"
    assert interp.variables.get('X') == 11, f"Expected X=11, got {interp.variables.get('X')}"
    print("  2D array expression indices: PASSED")

# ============================================================
# TEST FOR LOOPS WITH ARRAYS (Critical for piece manipulation)
# ============================================================

def test_for_loop_array_copy():
    """Test FOR loop copying array elements (like copying NX to PX)."""
    print("Testing FOR loop array copy...")
    interp, _ = run_program([
        'DIM PX(3)',
        'DIM PY(3)',
        'DIM NX(3)',
        'DIM NY(3)',
        'NX(0) = -1 : NY(0) = 0',
        'NX(1) = 0 : NY(1) = 0',
        'NX(2) = 1 : NY(2) = 0',
        'NX(3) = 2 : NY(3) = 0',
        'FOR I = 0 TO 3',
        '    PX(I) = NX(I)',
        '    PY(I) = NY(I)',
        'NEXT I',
        'X0 = PX(0)',
        'X1 = PX(1)',
        'X2 = PX(2)',
        'X3 = PX(3)'
    ])
    assert interp.variables.get('X0') == -1, f"Expected PX(0)=-1, got {interp.variables.get('X0')}"
    assert interp.variables.get('X1') == 0, f"Expected PX(1)=0, got {interp.variables.get('X1')}"
    assert interp.variables.get('X2') == 1, f"Expected PX(2)=1, got {interp.variables.get('X2')}"
    assert interp.variables.get('X3') == 2, f"Expected PX(3)=2, got {interp.variables.get('X3')}"
    print("  FOR loop array copy: PASSED")

def test_for_loop_2d_array_assignment():
    """Test FOR loop assigning to 2D array (like LOCKPIECE)."""
    print("Testing FOR loop 2D array assignment...")
    interp, _ = run_program([
        'DIM BOARD(19, 9)',
        'DIM PX(3)',
        'DIM PY(3)',
        'PIECEX = 4',
        'PIECEY = 18',
        'PIECECOLOR = 11',
        'PX(0) = 0 : PY(0) = 0',
        'PX(1) = 1 : PY(1) = 0',
        'PX(2) = 0 : PY(2) = 1',
        'PX(3) = 1 : PY(3) = 1',
        'FOR I = 0 TO 3',
        '    TX = PIECEX + PX(I)',
        '    TY = PIECEY + PY(I)',
        '    IF TY >= 0 AND TY < 20 AND TX >= 0 AND TX < 10 THEN',
        '        BOARD(TY, TX) = PIECECOLOR',
        '    END IF',
        'NEXT I',
        'V1 = BOARD(18, 4)',
        'V2 = BOARD(18, 5)',
        'V3 = BOARD(19, 4)',
        'V4 = BOARD(19, 5)'
    ])
    assert interp.variables.get('V1') == 11, f"Expected BOARD(18,4)=11, got {interp.variables.get('V1')}"
    assert interp.variables.get('V2') == 11, f"Expected BOARD(18,5)=11, got {interp.variables.get('V2')}"
    assert interp.variables.get('V3') == 11, f"Expected BOARD(19,4)=11, got {interp.variables.get('V3')}"
    assert interp.variables.get('V4') == 11, f"Expected BOARD(19,5)=11, got {interp.variables.get('V4')}"
    print("  FOR loop 2D array assignment: PASSED")

# ============================================================
# TEST GOSUB/RETURN (Critical for subroutine calls)
# ============================================================

def test_simple_gosub():
    """Test basic GOSUB/RETURN."""
    print("Testing simple GOSUB...")
    interp, _ = run_program([
        'X = 0',
        'GOSUB SETSEVEN',
        'Y = X',
        'END',
        'SETSEVEN:',
        'X = 7',
        'RETURN'
    ])
    assert interp.variables.get('Y') == 7, f"Expected Y=7, got {interp.variables.get('Y')}"
    print("  Simple GOSUB: PASSED")

def test_nested_gosub():
    """Test nested GOSUB calls (like LOCKPIECE calling CLEARLINES and MAKEPIECE)."""
    print("Testing nested GOSUB...")
    interp, _ = run_program([
        'X = 0',
        'GOSUB OUTER',
        'RESULT = X',
        'END',
        'OUTER:',
        'X = X + 10',
        'GOSUB INNER',
        'X = X + 10',
        'RETURN',
        'INNER:',
        'X = X + 5',
        'RETURN'
    ])
    assert interp.variables.get('RESULT') == 25, f"Expected RESULT=25, got {interp.variables.get('RESULT')}"
    print("  Nested GOSUB: PASSED")

def test_multiple_gosub_calls():
    """Test multiple GOSUB calls in sequence."""
    print("Testing multiple GOSUB calls...")
    interp, _ = run_program([
        'COUNT = 0',
        'GOSUB INCREMENT',
        'GOSUB INCREMENT',
        'GOSUB INCREMENT',
        'RESULT = COUNT',
        'END',
        'INCREMENT:',
        'COUNT = COUNT + 1',
        'RETURN'
    ])
    assert interp.variables.get('RESULT') == 3, f"Expected RESULT=3, got {interp.variables.get('RESULT')}"
    print("  Multiple GOSUB calls: PASSED")

# ============================================================
# TEST COLLISION DETECTION LOGIC (TRYMOVE equivalent)
# ============================================================

def test_collision_detection_floor():
    """Test collision detection at floor (TY >= ROWS)."""
    print("Testing collision detection at floor...")
    interp, _ = run_program([
        'CONST COLS = 10',
        'CONST ROWS = 20',
        'DIM BOARD(19, 9)',
        'DIM PX(3)',
        'DIM PY(3)',
        'PIECEX = 4',
        'PIECEY = 19',
        'MOVEY = 1',
        'PX(0) = 0 : PY(0) = 0',
        'PX(1) = 1 : PY(1) = 0',
        'PX(2) = 0 : PY(2) = 1',
        'PX(3) = 1 : PY(3) = 1',
        'NEWY = PIECEY + MOVEY',
        'CANCOLLIDE = 0',
        'FOR I = 0 TO 3',
        '    TX = PIECEX + PX(I)',
        '    TY = NEWY + PY(I)',
        '    IF TY >= ROWS THEN CANCOLLIDE = 1',
        'NEXT I',
        'RESULT = CANCOLLIDE'
    ])
    assert interp.variables.get('RESULT') == 1, f"Expected collision=1 at floor, got {interp.variables.get('RESULT')}"
    print("  Collision detection at floor: PASSED")

def test_collision_detection_no_collision():
    """Test collision detection when no collision."""
    print("Testing collision detection no collision...")
    interp, _ = run_program([
        'CONST COLS = 10',
        'CONST ROWS = 20',
        'DIM BOARD(19, 9)',
        'DIM PX(3)',
        'DIM PY(3)',
        'PIECEX = 4',
        'PIECEY = 5',
        'MOVEY = 1',
        'PX(0) = 0 : PY(0) = 0',
        'PX(1) = 1 : PY(1) = 0',
        'PX(2) = 0 : PY(2) = 1',
        'PX(3) = 1 : PY(3) = 1',
        'NEWY = PIECEY + MOVEY',
        'CANCOLLIDE = 0',
        'FOR I = 0 TO 3',
        '    TX = PIECEX + PX(I)',
        '    TY = NEWY + PY(I)',
        '    IF TY >= ROWS THEN CANCOLLIDE = 1',
        '    IF TY >= 0 AND TY < ROWS AND TX >= 0 AND TX < COLS THEN',
        '        IF BOARD(TY, TX) > 0 THEN CANCOLLIDE = 1',
        '    END IF',
        'NEXT I',
        'RESULT = CANCOLLIDE'
    ])
    assert interp.variables.get('RESULT') == 0, f"Expected no collision=0, got {interp.variables.get('RESULT')}"
    print("  Collision detection no collision: PASSED")

def test_collision_detection_with_board():
    """Test collision detection with existing blocks on board."""
    print("Testing collision detection with board blocks...")
    interp, _ = run_program([
        'CONST COLS = 10',
        'CONST ROWS = 20',
        'DIM BOARD(19, 9)',
        'DIM PX(3)',
        'DIM PY(3)',
        'BOARD(10, 4) = 11',
        'PIECEX = 4',
        'PIECEY = 9',
        'MOVEY = 1',
        'PX(0) = 0 : PY(0) = 0',
        'PX(1) = 1 : PY(1) = 0',
        'PX(2) = 0 : PY(2) = 1',
        'PX(3) = 1 : PY(3) = 1',
        'NEWY = PIECEY + MOVEY',
        'CANCOLLIDE = 0',
        'FOR I = 0 TO 3',
        '    TX = PIECEX + PX(I)',
        '    TY = NEWY + PY(I)',
        '    IF TY >= ROWS THEN CANCOLLIDE = 1',
        '    IF TY >= 0 AND TY < ROWS AND TX >= 0 AND TX < COLS THEN',
        '        IF BOARD(TY, TX) > 0 THEN CANCOLLIDE = 1',
        '    END IF',
        'NEXT I',
        'RESULT = CANCOLLIDE'
    ])
    assert interp.variables.get('RESULT') == 1, f"Expected collision=1 with board, got {interp.variables.get('RESULT')}"
    print("  Collision detection with board: PASSED")

# ============================================================
# TEST LOCKPIECE LOGIC
# ============================================================

def test_lockpiece_basic():
    """Test basic LOCKPIECE functionality."""
    print("Testing LOCKPIECE basic...")
    interp, _ = run_program([
        'CONST COLS = 10',
        'CONST ROWS = 20',
        'DIM BOARD(19, 9)',
        'DIM PX(3)',
        'DIM PY(3)',
        'DIM NX(3)',
        'DIM NY(3)',
        'PIECEX = 4',
        'PIECEY = 18',
        'PIECECOLOR = 11',
        'PX(0) = 0 : PY(0) = 0',
        'PX(1) = 1 : PY(1) = 0',
        'PX(2) = 0 : PY(2) = 1',
        'PX(3) = 1 : PY(3) = 1',
        'GAMEOVER = 0',
        'GOSUB LOCKPIECE',
        'V1 = BOARD(18, 4)',
        'V2 = BOARD(18, 5)',
        'V3 = BOARD(19, 4)',
        'V4 = BOARD(19, 5)',
        'END',
        'LOCKPIECE:',
        'FOR I = 0 TO 3',
        '    TX = PIECEX + PX(I)',
        '    TY = PIECEY + PY(I)',
        '    IF TY >= 0 AND TY < ROWS AND TX >= 0 AND TX < COLS THEN',
        '        BOARD(TY, TX) = PIECECOLOR',
        '    END IF',
        '    IF TY < 0 THEN GAMEOVER = 1',
        'NEXT I',
        'RETURN'
    ])
    assert interp.variables.get('V1') == 11, f"Expected BOARD(18,4)=11, got {interp.variables.get('V1')}"
    assert interp.variables.get('V2') == 11, f"Expected BOARD(18,5)=11, got {interp.variables.get('V2')}"
    assert interp.variables.get('V3') == 11, f"Expected BOARD(19,4)=11, got {interp.variables.get('V3')}"
    assert interp.variables.get('V4') == 11, f"Expected BOARD(19,5)=11, got {interp.variables.get('V4')}"
    assert interp.variables.get('GAMEOVER') == 0, f"Expected GAMEOVER=0, got {interp.variables.get('GAMEOVER')}"
    print("  LOCKPIECE basic: PASSED")

# ============================================================
# TEST TRYMOVE SUBROUTINE PATTERN
# ============================================================

def test_trymove_pattern():
    """Test TRYMOVE subroutine pattern with MOVED flag."""
    print("Testing TRYMOVE pattern...")
    interp, _ = run_program([
        'CONST COLS = 10',
        'CONST ROWS = 20',
        'DIM BOARD(19, 9)',
        'DIM PX(3)',
        'DIM PY(3)',
        'PIECEX = 4',
        'PIECEY = 5',
        'PX(0) = 0 : PY(0) = 0',
        'PX(1) = 1 : PY(1) = 0',
        'PX(2) = 0 : PY(2) = 1',
        'PX(3) = 1 : PY(3) = 1',
        'MOVEX = 0',
        'MOVEY = 1',
        'GOSUB TRYMOVE',
        'RESULT_MOVED = MOVED',
        'RESULT_Y = PIECEY',
        'END',
        'TRYMOVE:',
        'MOVED = 0',
        'NEWX = PIECEX + MOVEX',
        'NEWY = PIECEY + MOVEY',
        'CANCOLLIDE = 0',
        'FOR I = 0 TO 3',
        '    TX = NEWX + PX(I)',
        '    TY = NEWY + PY(I)',
        '    IF TX < 0 OR TX >= COLS THEN CANCOLLIDE = 1',
        '    IF TY >= ROWS THEN CANCOLLIDE = 1',
        '    IF TY >= 0 AND TY < ROWS AND TX >= 0 AND TX < COLS THEN',
        '        IF BOARD(TY, TX) > 0 THEN CANCOLLIDE = 1',
        '    END IF',
        'NEXT I',
        'IF CANCOLLIDE = 0 THEN',
        '    PIECEX = NEWX',
        '    PIECEY = NEWY',
        '    MOVED = 1',
        'END IF',
        'RETURN'
    ])
    assert interp.variables.get('RESULT_MOVED') == 1, f"Expected MOVED=1, got {interp.variables.get('RESULT_MOVED')}"
    assert interp.variables.get('RESULT_Y') == 6, f"Expected PIECEY=6, got {interp.variables.get('RESULT_Y')}"
    print("  TRYMOVE pattern: PASSED")

def test_trymove_collision_stops_piece():
    """Test TRYMOVE returns MOVED=0 when collision occurs."""
    print("Testing TRYMOVE collision stops piece...")
    interp, _ = run_program([
        'CONST COLS = 10',
        'CONST ROWS = 20',
        'DIM BOARD(19, 9)',
        'DIM PX(3)',
        'DIM PY(3)',
        'PIECEX = 4',
        'PIECEY = 18',
        'PX(0) = 0 : PY(0) = 0',
        'PX(1) = 1 : PY(1) = 0',
        'PX(2) = 0 : PY(2) = 1',
        'PX(3) = 1 : PY(3) = 1',
        'MOVEX = 0',
        'MOVEY = 1',
        'GOSUB TRYMOVE',
        'RESULT_MOVED = MOVED',
        'RESULT_Y = PIECEY',
        'END',
        'TRYMOVE:',
        'MOVED = 0',
        'NEWX = PIECEX + MOVEX',
        'NEWY = PIECEY + MOVEY',
        'CANCOLLIDE = 0',
        'FOR I = 0 TO 3',
        '    TX = NEWX + PX(I)',
        '    TY = NEWY + PY(I)',
        '    IF TX < 0 OR TX >= COLS THEN CANCOLLIDE = 1',
        '    IF TY >= ROWS THEN CANCOLLIDE = 1',
        '    IF TY >= 0 AND TY < ROWS AND TX >= 0 AND TX < COLS THEN',
        '        IF BOARD(TY, TX) > 0 THEN CANCOLLIDE = 1',
        '    END IF',
        'NEXT I',
        'IF CANCOLLIDE = 0 THEN',
        '    PIECEX = NEWX',
        '    PIECEY = NEWY',
        '    MOVED = 1',
        'END IF',
        'RETURN'
    ])
    assert interp.variables.get('RESULT_MOVED') == 0, f"Expected MOVED=0 at floor, got {interp.variables.get('RESULT_MOVED')}"
    assert interp.variables.get('RESULT_Y') == 18, f"Expected PIECEY unchanged=18, got {interp.variables.get('RESULT_Y')}"
    print("  TRYMOVE collision stops piece: PASSED")

# ============================================================
# TEST GRAVITY AND LOCK SEQUENCE
# ============================================================

def test_gravity_then_lock():
    """Test the gravity -> lock sequence (the core game loop issue)."""
    print("Testing gravity then lock sequence...")
    interp, _ = run_program([
        'CONST COLS = 10',
        'CONST ROWS = 20',
        'DIM BOARD(19, 9)',
        'DIM PX(3)',
        'DIM PY(3)',
        'DIM NX(3)',
        'DIM NY(3)',
        'PIECEX = 4',
        'PIECEY = 18',
        'PIECECOLOR = 11',
        'NEXTCOLOR = 14',
        'PX(0) = 0 : PY(0) = 0',
        'PX(1) = 1 : PY(1) = 0',
        'PX(2) = 0 : PY(2) = 1',
        'PX(3) = 1 : PY(3) = 1',
        'NX(0) = 0 : NY(0) = 0',
        'NX(1) = 1 : NY(1) = 0',
        'NX(2) = 0 : NY(2) = 1',
        'NX(3) = 1 : NY(3) = 1',
        'GAMEOVER = 0',
        'MOVEX = 0',
        'MOVEY = 1',
        'GOSUB TRYMOVE',
        'IF MOVED = 0 THEN',
        '    GOSUB LOCKPIECE',
        'END IF',
        'BOARD_18_4 = BOARD(18, 4)',
        'BOARD_18_5 = BOARD(18, 5)',
        'BOARD_19_4 = BOARD(19, 4)',
        'BOARD_19_5 = BOARD(19, 5)',
        'FINAL_PIECEY = PIECEY',
        'FINAL_PIECECOLOR = PIECECOLOR',
        'END',
        'TRYMOVE:',
        'MOVED = 0',
        'NEWX = PIECEX + MOVEX',
        'NEWY = PIECEY + MOVEY',
        'CANCOLLIDE = 0',
        'FOR I = 0 TO 3',
        '    TX = NEWX + PX(I)',
        '    TY = NEWY + PY(I)',
        '    IF TX < 0 OR TX >= COLS THEN CANCOLLIDE = 1',
        '    IF TY >= ROWS THEN CANCOLLIDE = 1',
        '    IF TY >= 0 AND TY < ROWS AND TX >= 0 AND TX < COLS THEN',
        '        IF BOARD(TY, TX) > 0 THEN CANCOLLIDE = 1',
        '    END IF',
        'NEXT I',
        'IF CANCOLLIDE = 0 THEN',
        '    PIECEX = NEWX',
        '    PIECEY = NEWY',
        '    MOVED = 1',
        'END IF',
        'RETURN',
        'LOCKPIECE:',
        'FOR I = 0 TO 3',
        '    TX = PIECEX + PX(I)',
        '    TY = PIECEY + PY(I)',
        '    IF TY >= 0 AND TY < ROWS AND TX >= 0 AND TX < COLS THEN',
        '        BOARD(TY, TX) = PIECECOLOR',
        '    END IF',
        '    IF TY < 0 THEN GAMEOVER = 1',
        'NEXT I',
        'FOR I = 0 TO 3',
        '    PX(I) = NX(I)',
        '    PY(I) = NY(I)',
        'NEXT I',
        'PIECECOLOR = NEXTCOLOR',
        'PIECEX = 4',
        'PIECEY = 0',
        'RETURN'
    ])
    # Piece should be locked onto the board
    assert interp.variables.get('BOARD_18_4') == 11, f"Expected BOARD(18,4)=11, got {interp.variables.get('BOARD_18_4')}"
    assert interp.variables.get('BOARD_18_5') == 11, f"Expected BOARD(18,5)=11, got {interp.variables.get('BOARD_18_5')}"
    assert interp.variables.get('BOARD_19_4') == 11, f"Expected BOARD(19,4)=11, got {interp.variables.get('BOARD_19_4')}"
    assert interp.variables.get('BOARD_19_5') == 11, f"Expected BOARD(19,5)=11, got {interp.variables.get('BOARD_19_5')}"
    # New piece should be spawned
    assert interp.variables.get('FINAL_PIECEY') == 0, f"Expected new piece at Y=0, got {interp.variables.get('FINAL_PIECEY')}"
    assert interp.variables.get('FINAL_PIECECOLOR') == 14, f"Expected new color=14, got {interp.variables.get('FINAL_PIECECOLOR')}"
    print("  Gravity then lock sequence: PASSED")

# ============================================================
# TEST GOTO WITH LABELS
# ============================================================

def test_goto_label():
    """Test GOTO with labels."""
    print("Testing GOTO with labels...")
    interp, _ = run_program([
        'X = 0',
        'MAINLOOP:',
        'X = X + 1',
        'IF X < 5 THEN GOTO MAINLOOP',
        'RESULT = X'
    ])
    assert interp.variables.get('RESULT') == 5, f"Expected RESULT=5, got {interp.variables.get('RESULT')}"
    print("  GOTO with labels: PASSED")

def test_conditional_goto():
    """Test conditional GOTO (IF condition THEN GOTO label)."""
    print("Testing conditional GOTO...")
    interp, _ = run_program([
        'GAMEOVER = 0',
        'X = 0',
        'MAINLOOP:',
        'IF GAMEOVER = 1 THEN GOTO ENDGAME',
        'X = X + 1',
        'IF X >= 3 THEN GAMEOVER = 1',
        'GOTO MAINLOOP',
        'ENDGAME:',
        'RESULT = X'
    ])
    assert interp.variables.get('RESULT') == 3, f"Expected RESULT=3, got {interp.variables.get('RESULT')}"
    print("  Conditional GOTO: PASSED")

# ============================================================
# TEST LINE CLEARING LOGIC
# ============================================================

def test_line_check_full():
    """Test checking if a row is full."""
    print("Testing line check full...")
    interp, _ = run_program([
        'CONST COLS = 10',
        'DIM BOARD(19, 9)',
        'ROW = 19',
        'FOR C = 0 TO 9',
        '    BOARD(ROW, C) = 11',
        'NEXT C',
        'FULL = 1',
        'FOR C = 0 TO COLS - 1',
        '    IF BOARD(ROW, C) = 0 THEN FULL = 0',
        'NEXT C',
        'RESULT = FULL'
    ])
    assert interp.variables.get('RESULT') == 1, f"Expected FULL=1, got {interp.variables.get('RESULT')}"
    print("  Line check full: PASSED")

def test_line_check_not_full():
    """Test checking if a row is not full."""
    print("Testing line check not full...")
    interp, _ = run_program([
        'CONST COLS = 10',
        'DIM BOARD(19, 9)',
        'ROW = 19',
        'FOR C = 0 TO 8',
        '    BOARD(ROW, C) = 11',
        'NEXT C',
        'FULL = 1',
        'FOR C = 0 TO COLS - 1',
        '    IF BOARD(ROW, C) = 0 THEN FULL = 0',
        'NEXT C',
        'RESULT = FULL'
    ])
    assert interp.variables.get('RESULT') == 0, f"Expected FULL=0 (missing one block), got {interp.variables.get('RESULT')}"
    print("  Line check not full: PASSED")

# ============================================================
# TEST PIECE ROTATION
# ============================================================

def test_rotation_clockwise():
    """Test 90 degree clockwise rotation."""
    print("Testing clockwise rotation...")
    interp, _ = run_program([
        'DIM PX(3)',
        'DIM PY(3)',
        'PX(0) = -1 : PY(0) = 0',
        'PX(1) = 0 : PY(1) = 0',
        'PX(2) = 1 : PY(2) = 0',
        'PX(3) = 0 : PY(3) = 1',
        'FOR I = 0 TO 3',
        '    TEMPX = PX(I)',
        '    PX(I) = -PY(I)',
        '    PY(I) = TEMPX',
        'NEXT I',
        'RX0 = PX(0) : RY0 = PY(0)',
        'RX1 = PX(1) : RY1 = PY(1)',
        'RX2 = PX(2) : RY2 = PY(2)',
        'RX3 = PX(3) : RY3 = PY(3)'
    ])
    # T piece horizontal: (-1,0), (0,0), (1,0), (0,1)
    # After rotation: (0,-1), (0,0), (0,1), (-1,0)
    assert interp.variables.get('RX0') == 0, f"Expected RX0=0, got {interp.variables.get('RX0')}"
    assert interp.variables.get('RY0') == -1, f"Expected RY0=-1, got {interp.variables.get('RY0')}"
    assert interp.variables.get('RX1') == 0, f"Expected RX1=0, got {interp.variables.get('RX1')}"
    assert interp.variables.get('RY1') == 0, f"Expected RY1=0, got {interp.variables.get('RY1')}"
    print("  Clockwise rotation: PASSED")

# ============================================================
# TEST MULTI-STATEMENT LINES (colon separator)
# ============================================================

def test_colon_statements():
    """Test multiple statements on one line with colon."""
    print("Testing colon-separated statements...")
    interp, _ = run_program([
        'X = 1 : Y = 2 : Z = 3',
        'A = X + Y + Z'
    ])
    assert interp.variables.get('A') == 6, f"Expected A=6, got {interp.variables.get('A')}"
    print("  Colon-separated statements: PASSED")

def test_colon_array_assignments():
    """Test array assignments with colon (like NX(0) = -1 : NY(0) = 0)."""
    print("Testing colon array assignments...")
    interp, _ = run_program([
        'DIM NX(3)',
        'DIM NY(3)',
        'NX(0) = -1 : NY(0) = 0',
        'NX(1) = 0 : NY(1) = 0',
        'A = NX(0)',
        'B = NY(0)',
        'C = NX(1)',
        'D = NY(1)'
    ])
    assert interp.variables.get('A') == -1, f"Expected A=-1, got {interp.variables.get('A')}"
    assert interp.variables.get('B') == 0, f"Expected B=0, got {interp.variables.get('B')}"
    assert interp.variables.get('C') == 0, f"Expected C=0, got {interp.variables.get('C')}"
    assert interp.variables.get('D') == 0, f"Expected D=0, got {interp.variables.get('D')}"
    print("  Colon array assignments: PASSED")

# ============================================================
# TEST INTEGER DIVISION AND EXPRESSIONS
# ============================================================

def test_int_function():
    """Test INT function for floor division."""
    print("Testing INT function...")
    interp, _ = run_program([
        'X = INT(7 / 3)',
        'Y = INT(RND * 7)'
    ])
    assert interp.variables.get('X') == 2, f"Expected INT(7/3)=2, got {interp.variables.get('X')}"
    assert 0 <= interp.variables.get('Y') < 7, f"Expected 0<=Y<7, got {interp.variables.get('Y')}"
    print("  INT function: PASSED")

# ============================================================
# TEST COMPLEX TETRIS-LIKE SCENARIO
# ============================================================

def test_full_game_cycle():
    """Test a complete game cycle: piece falls, locks, new piece spawns."""
    print("Testing full game cycle...")
    interp, steps = run_program([
        'CONST COLS = 10',
        'CONST ROWS = 20',
        'DIM BOARD(19, 9)',
        'DIM PX(3)',
        'DIM PY(3)',
        'DIM NX(3)',
        'DIM NY(3)',
        'GAMEOVER = 0',
        'PIECEX = 4',
        'PIECEY = 17',
        'PIECECOLOR = 11',
        'NEXTCOLOR = 14',
        'PX(0) = 0 : PY(0) = 0',
        'PX(1) = 1 : PY(1) = 0',
        'PX(2) = 0 : PY(2) = 1',
        'PX(3) = 1 : PY(3) = 1',
        'NX(0) = -1 : NY(0) = 0',
        'NX(1) = 0 : NY(1) = 0',
        'NX(2) = 1 : NY(2) = 0',
        'NX(3) = 0 : NY(3) = 1',
        'LOCKCOUNT = 0',
        'MAINLOOP:',
        'IF GAMEOVER = 1 THEN GOTO ENDGAME',
        'IF LOCKCOUNT >= 3 THEN GOTO ENDGAME',
        'MOVEX = 0',
        'MOVEY = 1',
        'GOSUB TRYMOVE',
        'IF MOVED = 0 THEN',
        '    GOSUB LOCKPIECE',
        '    LOCKCOUNT = LOCKCOUNT + 1',
        'END IF',
        'GOTO MAINLOOP',
        'ENDGAME:',
        'FINALCOUNT = LOCKCOUNT',
        'FINALBOARD_18_4 = BOARD(18, 4)',
        'FINALBOARD_19_4 = BOARD(19, 4)',
        'END',
        'TRYMOVE:',
        'MOVED = 0',
        'NEWX = PIECEX + MOVEX',
        'NEWY = PIECEY + MOVEY',
        'CANCOLLIDE = 0',
        'FOR I = 0 TO 3',
        '    TX = NEWX + PX(I)',
        '    TY = NEWY + PY(I)',
        '    IF TX < 0 OR TX >= COLS THEN CANCOLLIDE = 1',
        '    IF TY >= ROWS THEN CANCOLLIDE = 1',
        '    IF TY >= 0 AND TY < ROWS AND TX >= 0 AND TX < COLS THEN',
        '        IF BOARD(TY, TX) > 0 THEN CANCOLLIDE = 1',
        '    END IF',
        'NEXT I',
        'IF CANCOLLIDE = 0 THEN',
        '    PIECEX = NEWX',
        '    PIECEY = NEWY',
        '    MOVED = 1',
        'END IF',
        'RETURN',
        'LOCKPIECE:',
        'FOR I = 0 TO 3',
        '    TX = PIECEX + PX(I)',
        '    TY = PIECEY + PY(I)',
        '    IF TY >= 0 AND TY < ROWS AND TX >= 0 AND TX < COLS THEN',
        '        BOARD(TY, TX) = PIECECOLOR',
        '    END IF',
        '    IF TY < 0 THEN GAMEOVER = 1',
        'NEXT I',
        'FOR I = 0 TO 3',
        '    PX(I) = NX(I)',
        '    PY(I) = NY(I)',
        'NEXT I',
        'PIECECOLOR = NEXTCOLOR',
        'PIECEX = 4',
        'PIECEY = 0',
        'RETURN'
    ], max_steps=50000)

    # First lock should have happened
    assert interp.variables.get('FINALCOUNT') >= 1, f"Expected at least 1 lock, got {interp.variables.get('FINALCOUNT')}"
    # Board should have blocks
    assert interp.variables.get('FINALBOARD_18_4') == 11 or interp.variables.get('FINALBOARD_19_4') == 11, \
        f"Expected blocks on board, got B(18,4)={interp.variables.get('FINALBOARD_18_4')}, B(19,4)={interp.variables.get('FINALBOARD_19_4')}"
    print(f"  Full game cycle: PASSED (locks={interp.variables.get('FINALCOUNT')}, steps={steps})")

# ============================================================
# TEST EDGE CASES
# ============================================================

def test_piece_at_top_gameover():
    """Test game over when piece locks at top."""
    print("Testing game over at top...")
    interp, _ = run_program([
        'CONST COLS = 10',
        'CONST ROWS = 20',
        'DIM BOARD(19, 9)',
        'DIM PX(3)',
        'DIM PY(3)',
        'PIECEX = 4',
        'PIECEY = -1',
        'PIECECOLOR = 11',
        'PX(0) = 0 : PY(0) = 0',
        'PX(1) = 1 : PY(1) = 0',
        'PX(2) = 0 : PY(2) = 1',
        'PX(3) = 1 : PY(3) = 1',
        'GAMEOVER = 0',
        'FOR I = 0 TO 3',
        '    TX = PIECEX + PX(I)',
        '    TY = PIECEY + PY(I)',
        '    IF TY >= 0 AND TY < ROWS AND TX >= 0 AND TX < COLS THEN',
        '        BOARD(TY, TX) = PIECECOLOR',
        '    END IF',
        '    IF TY < 0 THEN GAMEOVER = 1',
        'NEXT I',
        'RESULT = GAMEOVER'
    ])
    assert interp.variables.get('RESULT') == 1, f"Expected GAMEOVER=1, got {interp.variables.get('RESULT')}"
    print("  Game over at top: PASSED")

def test_for_step_negative():
    """Test FOR loop with negative STEP (used in line clearing)."""
    print("Testing FOR with negative STEP...")
    interp, _ = run_program([
        'DIM arr(5)',
        'arr(0) = 100',
        'arr(1) = 200',
        'arr(2) = 300',
        'FOR R = 2 TO 1 STEP -1',
        '    arr(R) = arr(R - 1)',
        'NEXT R',
        'arr(0) = 0',
        'V0 = arr(0)',
        'V1 = arr(1)',
        'V2 = arr(2)'
    ])
    assert interp.variables.get('V0') == 0, f"Expected arr(0)=0, got {interp.variables.get('V0')}"
    assert interp.variables.get('V1') == 100, f"Expected arr(1)=100, got {interp.variables.get('V1')}"
    assert interp.variables.get('V2') == 200, f"Expected arr(2)=200, got {interp.variables.get('V2')}"
    print("  FOR with negative STEP: PASSED")

def test_nested_for_loops():
    """Test nested FOR loops (used in line clearing with 2D array)."""
    print("Testing nested FOR loops...")
    interp, _ = run_program([
        'DIM BOARD(4, 4)',
        'FOR R = 0 TO 4',
        '    FOR C = 0 TO 4',
        '        BOARD(R, C) = R * 10 + C',
        '    NEXT C',
        'NEXT R',
        'V00 = BOARD(0, 0)',
        'V12 = BOARD(1, 2)',
        'V44 = BOARD(4, 4)'
    ])
    assert interp.variables.get('V00') == 0, f"Expected BOARD(0,0)=0, got {interp.variables.get('V00')}"
    assert interp.variables.get('V12') == 12, f"Expected BOARD(1,2)=12, got {interp.variables.get('V12')}"
    assert interp.variables.get('V44') == 44, f"Expected BOARD(4,4)=44, got {interp.variables.get('V44')}"
    print("  Nested FOR loops: PASSED")

# ============================================================
# TEST CLEARLINES SUBROUTINE
# ============================================================

def test_clearlines_goto_loop():
    """Test the GOTO-based loop pattern used in CLEARLINES."""
    print("Testing CLEARLINES GOTO loop pattern...")
    interp, steps = run_program([
        'CONST COLS = 10',
        'CONST ROWS = 20',
        'DIM BOARD(19, 9)',
        'ROW = ROWS - 1',
        'ITERATIONS = 0',
        'CHECKROW:',
        'IF ROW < 0 THEN GOTO DONECLEARING',
        'ITERATIONS = ITERATIONS + 1',
        'IF ITERATIONS > 25 THEN GOTO DONECLEARING',
        'ROW = ROW - 1',
        'GOTO CHECKROW',
        'DONECLEARING:',
        'RESULT = ITERATIONS'
    ], max_steps=1000)
    assert interp.variables.get('RESULT') == 20, f"Expected 20 iterations, got {interp.variables.get('RESULT')}"
    print(f"  CLEARLINES GOTO loop pattern: PASSED (iterations={interp.variables.get('RESULT')}, steps={steps})")

def test_clearlines_with_full_row():
    """Test CLEARLINES logic when a row is full."""
    print("Testing CLEARLINES with full row...")
    interp, steps = run_program([
        'CONST COLS = 10',
        'CONST ROWS = 20',
        'DIM BOARD(19, 9)',
        'FOR C = 0 TO 9',
        '    BOARD(19, C) = 11',
        'NEXT C',
        'BOARD(18, 0) = 5',
        'LINESCLEARED = 0',
        'ROW = ROWS - 1',
        'CHECKROW:',
        'IF ROW < 0 THEN GOTO DONECLEARING',
        'FULL = 1',
        'FOR C = 0 TO COLS - 1',
        '    IF BOARD(ROW, C) = 0 THEN FULL = 0',
        'NEXT C',
        'IF FULL = 1 THEN',
        '    LINESCLEARED = LINESCLEARED + 1',
        '    FOR R = ROW TO 1 STEP -1',
        '        FOR C = 0 TO COLS - 1',
        '            BOARD(R, C) = BOARD(R - 1, C)',
        '        NEXT C',
        '    NEXT R',
        '    FOR C = 0 TO COLS - 1',
        '        BOARD(0, C) = 0',
        '    NEXT C',
        'ELSE',
        '    ROW = ROW - 1',
        'END IF',
        'GOTO CHECKROW',
        'DONECLEARING:',
        'RESULT_LINES = LINESCLEARED',
        'RESULT_18_0 = BOARD(18, 0)',
        'RESULT_19_0 = BOARD(19, 0)'
    ], max_steps=5000)
    assert interp.variables.get('RESULT_LINES') == 1, f"Expected 1 line cleared, got {interp.variables.get('RESULT_LINES')}"
    assert interp.variables.get('RESULT_19_0') == 5, f"Expected BOARD(19,0)=5 (shifted down), got {interp.variables.get('RESULT_19_0')}"
    print(f"  CLEARLINES with full row: PASSED (steps={steps})")

def test_clearlines_full_subroutine():
    """Test the full CLEARLINES subroutine as used in Tetris."""
    print("Testing full CLEARLINES subroutine...")
    interp, steps = run_program([
        'CONST COLS = 10',
        'CONST ROWS = 20',
        'DIM BOARD(19, 9)',
        'SCORE = 0',
        'LINES = 0',
        'LEVEL = 1',
        'FOR C = 0 TO 9',
        '    BOARD(19, C) = 11',
        'NEXT C',
        'GOSUB CLEARLINES',
        'FINAL_LINES = LINES',
        'FINAL_SCORE = SCORE',
        'END',
        'CLEARLINES:',
        'LINESCLEARED = 0',
        'ROW = ROWS - 1',
        'CHECKROW:',
        'IF ROW < 0 THEN GOTO DONECLEARING',
        'FULL = 1',
        'FOR C = 0 TO COLS - 1',
        '    IF BOARD(ROW, C) = 0 THEN FULL = 0',
        'NEXT C',
        'IF FULL = 1 THEN',
        '    LINESCLEARED = LINESCLEARED + 1',
        '    FOR R = ROW TO 1 STEP -1',
        '        FOR C = 0 TO COLS - 1',
        '            BOARD(R, C) = BOARD(R - 1, C)',
        '        NEXT C',
        '    NEXT R',
        '    FOR C = 0 TO COLS - 1',
        '        BOARD(0, C) = 0',
        '    NEXT C',
        'ELSE',
        '    ROW = ROW - 1',
        'END IF',
        'GOTO CHECKROW',
        'DONECLEARING:',
        'IF LINESCLEARED > 0 THEN',
        '    LINES = LINES + LINESCLEARED',
        '    IF LINESCLEARED = 1 THEN SCORE = SCORE + 100 * LEVEL',
        '    IF LINESCLEARED = 2 THEN SCORE = SCORE + 300 * LEVEL',
        '    IF LINESCLEARED = 3 THEN SCORE = SCORE + 500 * LEVEL',
        '    IF LINESCLEARED = 4 THEN SCORE = SCORE + 800 * LEVEL',
        'END IF',
        'RETURN'
    ], max_steps=10000)
    assert interp.variables.get('FINAL_LINES') == 1, f"Expected 1 line, got {interp.variables.get('FINAL_LINES')}"
    assert interp.variables.get('FINAL_SCORE') == 100, f"Expected score=100, got {interp.variables.get('FINAL_SCORE')}"
    print(f"  Full CLEARLINES subroutine: PASSED (steps={steps})")

def test_complete_lockpiece_with_clearlines():
    """Test LOCKPIECE calling CLEARLINES."""
    print("Testing LOCKPIECE with CLEARLINES...")
    interp, steps = run_program([
        'CONST COLS = 10',
        'CONST ROWS = 20',
        'DIM BOARD(19, 9)',
        'DIM PX(3)',
        'DIM PY(3)',
        'DIM NX(3)',
        'DIM NY(3)',
        'SCORE = 0',
        'LINES = 0',
        'LEVEL = 1',
        'GAMEOVER = 0',
        'PIECEX = 0',
        'PIECEY = 18',
        'PIECECOLOR = 11',
        'NEXTCOLOR = 14',
        'PX(0) = 0 : PY(0) = 0',
        'PX(1) = 1 : PY(1) = 0',
        'PX(2) = 0 : PY(2) = 1',
        'PX(3) = 1 : PY(3) = 1',
        'NX(0) = 0 : NY(0) = 0',
        'NX(1) = 1 : NY(1) = 0',
        'NX(2) = 0 : NY(2) = 1',
        'NX(3) = 1 : NY(3) = 1',
        'FOR C = 2 TO 9',
        '    BOARD(19, C) = 5',
        'NEXT C',
        'GOSUB LOCKPIECE',
        'FINAL_LINES = LINES',
        'FINAL_BOARD_19_0 = BOARD(19, 0)',
        'FINAL_BOARD_19_1 = BOARD(19, 1)',
        'FINAL_PIECEY = PIECEY',
        'END',
        'LOCKPIECE:',
        'FOR I = 0 TO 3',
        '    TX = PIECEX + PX(I)',
        '    TY = PIECEY + PY(I)',
        '    IF TY >= 0 AND TY < ROWS AND TX >= 0 AND TX < COLS THEN',
        '        BOARD(TY, TX) = PIECECOLOR',
        '    END IF',
        '    IF TY < 0 THEN GAMEOVER = 1',
        'NEXT I',
        'GOSUB CLEARLINES',
        'FOR I = 0 TO 3',
        '    PX(I) = NX(I)',
        '    PY(I) = NY(I)',
        'NEXT I',
        'PIECECOLOR = NEXTCOLOR',
        'PIECEX = 4',
        'PIECEY = 0',
        'RETURN',
        'CLEARLINES:',
        'LINESCLEARED = 0',
        'ROW = ROWS - 1',
        'CHECKROW:',
        'IF ROW < 0 THEN GOTO DONECLEARING',
        'FULL = 1',
        'FOR C = 0 TO COLS - 1',
        '    IF BOARD(ROW, C) = 0 THEN FULL = 0',
        'NEXT C',
        'IF FULL = 1 THEN',
        '    LINESCLEARED = LINESCLEARED + 1',
        '    FOR R = ROW TO 1 STEP -1',
        '        FOR C = 0 TO COLS - 1',
        '            BOARD(R, C) = BOARD(R - 1, C)',
        '        NEXT C',
        '    NEXT R',
        '    FOR C = 0 TO COLS - 1',
        '        BOARD(0, C) = 0',
        '    NEXT C',
        'ELSE',
        '    ROW = ROW - 1',
        'END IF',
        'GOTO CHECKROW',
        'DONECLEARING:',
        'IF LINESCLEARED > 0 THEN',
        '    LINES = LINES + LINESCLEARED',
        '    IF LINESCLEARED = 1 THEN SCORE = SCORE + 100 * LEVEL',
        'END IF',
        'RETURN'
    ], max_steps=20000)
    assert interp.variables.get('FINAL_LINES') == 1, f"Expected 1 line cleared, got {interp.variables.get('FINAL_LINES')}"
    assert interp.variables.get('FINAL_PIECEY') == 0, f"Expected new piece at Y=0, got {interp.variables.get('FINAL_PIECEY')}"
    print(f"  LOCKPIECE with CLEARLINES: PASSED (steps={steps})")

def test_dim_inside_subroutine():
    """Test DIM statement called inside a subroutine (like TRYROTATE)."""
    print("Testing DIM inside subroutine...")
    interp, steps = run_program([
        'DIM PX(3)',
        'DIM PY(3)',
        'PX(0) = -1 : PY(0) = 0',
        'PX(1) = 0 : PY(1) = 0',
        'PX(2) = 1 : PY(2) = 0',
        'PX(3) = 0 : PY(3) = 1',
        'GOSUB TRYROTATE',
        'R1X0 = PX(0)',
        'R1Y0 = PY(0)',
        'GOSUB TRYROTATE',
        'R2X0 = PX(0)',
        'R2Y0 = PY(0)',
        'END',
        'TRYROTATE:',
        'DIM OX(3)',
        'DIM OY(3)',
        'FOR I = 0 TO 3',
        '    OX(I) = PX(I)',
        '    OY(I) = PY(I)',
        'NEXT I',
        'FOR I = 0 TO 3',
        '    TEMPX = PX(I)',
        '    PX(I) = -PY(I)',
        '    PY(I) = TEMPX',
        'NEXT I',
        'RETURN'
    ], max_steps=5000)
    # After first rotation: T piece (-1,0), (0,0), (1,0), (0,1) -> (0,-1), (0,0), (0,1), (-1,0)
    assert interp.variables.get('R1X0') == 0, f"Expected R1X0=0, got {interp.variables.get('R1X0')}"
    assert interp.variables.get('R1Y0') == -1, f"Expected R1Y0=-1, got {interp.variables.get('R1Y0')}"
    # After second rotation: (0,-1), (0,0), (0,1), (-1,0) -> (1,0), (0,0), (-1,0), (0,-1)
    assert interp.variables.get('R2X0') == 1, f"Expected R2X0=1, got {interp.variables.get('R2X0')}"
    assert interp.variables.get('R2Y0') == 0, f"Expected R2Y0=0, got {interp.variables.get('R2Y0')}"
    print(f"  DIM inside subroutine: PASSED (steps={steps})")

def test_repeated_dim_in_loop():
    """Test DIM being called multiple times in a loop (should reset array)."""
    print("Testing repeated DIM in loop...")
    interp, steps = run_program([
        'TOTAL = 0',
        'FOR J = 1 TO 3',
        '    DIM ARR(2)',
        '    ARR(0) = J',
        '    ARR(1) = J * 10',
        '    ARR(2) = J * 100',
        '    TOTAL = TOTAL + ARR(0) + ARR(1) + ARR(2)',
        'NEXT J',
        'RESULT = TOTAL'
    ], max_steps=1000)
    # J=1: 1+10+100=111, J=2: 2+20+200=222, J=3: 3+30+300=333 = 666
    assert interp.variables.get('RESULT') == 666, f"Expected 666, got {interp.variables.get('RESULT')}"
    print(f"  Repeated DIM in loop: PASSED (steps={steps})")

def test_board_persistence_after_multiple_locks():
    """Test that BOARD array keeps blocks after multiple piece locks."""
    print("Testing board persistence after multiple locks...")
    interp, steps = run_program([
        'CONST COLS = 10',
        'CONST ROWS = 20',
        'DIM BOARD(19, 9)',
        'DIM PX(3)',
        'DIM PY(3)',
        'DIM NX(3)',
        'DIM NY(3)',
        'GAMEOVER = 0',
        'LOCKCOUNT = 0',
        'NX(0) = 0 : NY(0) = 0',
        'NX(1) = 1 : NY(1) = 0',
        'NX(2) = 0 : NY(2) = 1',
        'NX(3) = 1 : NY(3) = 1',
        'NEXTCOLOR = 14',
        'PIECECOLOR = 11',
        'PX(0) = 0 : PY(0) = 0',
        'PX(1) = 1 : PY(1) = 0',
        'PX(2) = 0 : PY(2) = 1',
        'PX(3) = 1 : PY(3) = 1',
        'PIECEX = 0',
        'PIECEY = 18',
        'GOSUB LOCKPIECE',
        'FIRST_BOARD_19_0 = BOARD(19, 0)',
        'FIRST_BOARD_19_1 = BOARD(19, 1)',
        'PIECEX = 2',
        'PIECEY = 18',
        'GOSUB LOCKPIECE',
        'SECOND_BOARD_19_2 = BOARD(19, 2)',
        'SECOND_BOARD_19_3 = BOARD(19, 3)',
        'STILL_BOARD_19_0 = BOARD(19, 0)',
        'STILL_BOARD_19_1 = BOARD(19, 1)',
        'PIECEX = 4',
        'PIECEY = 18',
        'GOSUB LOCKPIECE',
        'THIRD_BOARD_19_4 = BOARD(19, 4)',
        'FINAL_BOARD_19_0 = BOARD(19, 0)',
        'FINAL_BOARD_19_2 = BOARD(19, 2)',
        'END',
        'LOCKPIECE:',
        'FOR I = 0 TO 3',
        '    TX = PIECEX + PX(I)',
        '    TY = PIECEY + PY(I)',
        '    IF TY >= 0 AND TY < ROWS AND TX >= 0 AND TX < COLS THEN',
        '        BOARD(TY, TX) = PIECECOLOR',
        '    END IF',
        '    IF TY < 0 THEN GAMEOVER = 1',
        'NEXT I',
        'FOR I = 0 TO 3',
        '    PX(I) = NX(I)',
        '    PY(I) = NY(I)',
        'NEXT I',
        'PIECECOLOR = NEXTCOLOR',
        'PIECEX = 4',
        'PIECEY = 0',
        'LOCKCOUNT = LOCKCOUNT + 1',
        'RETURN'
    ], max_steps=10000)

    # First lock at (0,18) - blocks at (0,18), (1,18), (0,19), (1,19)
    assert interp.variables.get('FIRST_BOARD_19_0') == 11, f"First lock failed: expected 11, got {interp.variables.get('FIRST_BOARD_19_0')}"
    assert interp.variables.get('FIRST_BOARD_19_1') == 11, f"First lock failed"

    # Second lock at (2,18) - blocks at (2,18), (3,18), (2,19), (3,19)
    assert interp.variables.get('SECOND_BOARD_19_2') == 14, f"Second lock failed: expected 14, got {interp.variables.get('SECOND_BOARD_19_2')}"
    assert interp.variables.get('SECOND_BOARD_19_3') == 14, f"Second lock failed"

    # First blocks should still be there
    assert interp.variables.get('STILL_BOARD_19_0') == 11, f"First blocks lost after second lock"
    assert interp.variables.get('STILL_BOARD_19_1') == 11, f"First blocks lost after second lock"

    # After third lock, all previous blocks should still be there
    assert interp.variables.get('FINAL_BOARD_19_0') == 11, f"First blocks lost after third lock"
    assert interp.variables.get('FINAL_BOARD_19_2') == 14, f"Second blocks lost after third lock"
    assert interp.variables.get('THIRD_BOARD_19_4') == 14, f"Third lock failed"

    print(f"  Board persistence after multiple locks: PASSED (steps={steps})")

def test_game_over_detection():
    """Test game over is properly detected when piece can't spawn."""
    print("Testing game over detection...")
    interp, steps = run_program([
        'CONST COLS = 10',
        'CONST ROWS = 20',
        'DIM BOARD(19, 9)',
        'DIM PX(3)',
        'DIM PY(3)',
        'DIM NX(3)',
        'DIM NY(3)',
        'GAMEOVER = 0',
        'NX(0) = 0 : NY(0) = 0',
        'NX(1) = 1 : NY(1) = 0',
        'NX(2) = 0 : NY(2) = 1',
        'NX(3) = 1 : NY(3) = 1',
        'NEXTCOLOR = 14',
        'PIECECOLOR = 11',
        'PX(0) = 0 : PY(0) = 0',
        'PX(1) = 1 : PY(1) = 0',
        'PX(2) = 0 : PY(2) = 1',
        'PX(3) = 1 : PY(3) = 1',
        'BOARD(0, 4) = 5',
        'BOARD(1, 4) = 5',
        'PIECEX = 4',
        'PIECEY = 18',
        'GOSUB LOCKPIECE',
        'RESULT_GAMEOVER = GAMEOVER',
        'END',
        'LOCKPIECE:',
        'FOR I = 0 TO 3',
        '    TX = PIECEX + PX(I)',
        '    TY = PIECEY + PY(I)',
        '    IF TY >= 0 AND TY < ROWS AND TX >= 0 AND TX < COLS THEN',
        '        BOARD(TY, TX) = PIECECOLOR',
        '    END IF',
        '    IF TY < 0 THEN GAMEOVER = 1',
        'NEXT I',
        'FOR I = 0 TO 3',
        '    PX(I) = NX(I)',
        '    PY(I) = NY(I)',
        'NEXT I',
        'PIECECOLOR = NEXTCOLOR',
        'PIECEX = 4',
        'PIECEY = 0',
        'FOR I = 0 TO 3',
        '    TX = PIECEX + PX(I)',
        '    TY = PIECEY + PY(I)',
        '    IF TY >= 0 AND TY < ROWS AND TX >= 0 AND TX < COLS THEN',
        '        IF BOARD(TY, TX) > 0 THEN GAMEOVER = 1',
        '    END IF',
        'NEXT I',
        'RETURN'
    ], max_steps=5000)

    assert interp.variables.get('RESULT_GAMEOVER') == 1, f"Expected GAMEOVER=1 when spawn blocked, got {interp.variables.get('RESULT_GAMEOVER')}"
    print(f"  Game over detection: PASSED (steps={steps})")

def test_line_with_array_color():
    """Test LINE statement with array access in color parameter (bug regression test)."""
    print("Testing LINE with array color...")
    interp, steps = run_program([
        'SCREEN 13',
        'DIM BOARD(19, 9)',
        'BOARD(5, 3) = 11',
        'R = 5',
        'C = 3',
        'X1 = 10',
        'Y1 = 20',
        'LINE (X1, Y1)-(X1 + 8, Y1 + 8), BOARD(R, C), BF',
        'RESULT = 1'
    ], max_steps=1000)
    assert interp.variables.get('RESULT') == 1, f"Expected RESULT=1 (program completed), got {interp.variables.get('RESULT')}"
    assert interp.running == False, "Expected program to complete"
    print(f"  LINE with array color: PASSED (steps={steps})")

def test_simulate_piece_fall_and_lock():
    """Simulate a piece falling from top to bottom and locking."""
    print("Testing simulated piece fall and lock...")
    interp, steps = run_program([
        'CONST COLS = 10',
        'CONST ROWS = 20',
        'DIM BOARD(19, 9)',
        'DIM PX(3)',
        'DIM PY(3)',
        'DIM NX(3)',
        'DIM NY(3)',
        'GAMEOVER = 0',
        'SCORE = 0',
        'LINES = 0',
        'LEVEL = 1',
        'FALLDELAY = 2',
        'FALLCOUNT = 0',
        'PIECEX = 4',
        'PIECEY = 0',
        'PIECECOLOR = 11',
        'NEXTCOLOR = 14',
        'PX(0) = 0 : PY(0) = 0',
        'PX(1) = 1 : PY(1) = 0',
        'PX(2) = 0 : PY(2) = 1',
        'PX(3) = 1 : PY(3) = 1',
        'NX(0) = -1 : NY(0) = 0',
        'NX(1) = 0 : NY(1) = 0',
        'NX(2) = 1 : NY(2) = 0',
        'NX(3) = 0 : NY(3) = 1',
        'LOCKCOUNT = 0',
        'ITERCOUNT = 0',
        'MAINLOOP:',
        'IF GAMEOVER = 1 THEN GOTO ENDGAME',
        'IF LOCKCOUNT >= 2 THEN GOTO ENDGAME',
        'ITERCOUNT = ITERCOUNT + 1',
        'IF ITERCOUNT > 1000 THEN GOTO ENDGAME',
        'FALLCOUNT = FALLCOUNT + 1',
        'IF FALLCOUNT >= FALLDELAY THEN',
        '    FALLCOUNT = 0',
        '    MOVEX = 0',
        '    MOVEY = 1',
        '    GOSUB TRYMOVE',
        '    IF MOVED = 0 THEN',
        '        GOSUB LOCKPIECE',
        '    END IF',
        'END IF',
        'GOTO MAINLOOP',
        'ENDGAME:',
        'FINAL_ITERCOUNT = ITERCOUNT',
        'FINAL_LOCKCOUNT = LOCKCOUNT',
        'FINAL_GAMEOVER = GAMEOVER',
        'FINAL_BOARD_19_4 = BOARD(19, 4)',
        'FINAL_BOARD_19_5 = BOARD(19, 5)',
        'FINAL_BOARD_18_4 = BOARD(18, 4)',
        'FINAL_PIECEY = PIECEY',
        'FINAL_PIECECOLOR = PIECECOLOR',
        'END',
        'TRYMOVE:',
        'MOVED = 0',
        'NEWX = PIECEX + MOVEX',
        'NEWY = PIECEY + MOVEY',
        'CANCOLLIDE = 0',
        'FOR I = 0 TO 3',
        '    TX = NEWX + PX(I)',
        '    TY = NEWY + PY(I)',
        '    IF TX < 0 OR TX >= COLS THEN CANCOLLIDE = 1',
        '    IF TY >= ROWS THEN CANCOLLIDE = 1',
        '    IF TY >= 0 AND TY < ROWS AND TX >= 0 AND TX < COLS THEN',
        '        IF BOARD(TY, TX) > 0 THEN CANCOLLIDE = 1',
        '    END IF',
        'NEXT I',
        'IF CANCOLLIDE = 0 THEN',
        '    PIECEX = NEWX',
        '    PIECEY = NEWY',
        '    MOVED = 1',
        'END IF',
        'RETURN',
        'LOCKPIECE:',
        'FOR I = 0 TO 3',
        '    TX = PIECEX + PX(I)',
        '    TY = PIECEY + PY(I)',
        '    IF TY >= 0 AND TY < ROWS AND TX >= 0 AND TX < COLS THEN',
        '        BOARD(TY, TX) = PIECECOLOR',
        '    END IF',
        '    IF TY < 0 THEN GAMEOVER = 1',
        'NEXT I',
        'FOR I = 0 TO 3',
        '    PX(I) = NX(I)',
        '    PY(I) = NY(I)',
        'NEXT I',
        'PIECECOLOR = NEXTCOLOR',
        'PIECEX = 4',
        'PIECEY = 0',
        'FALLCOUNT = 0',
        'LOCKCOUNT = LOCKCOUNT + 1',
        'FOR I = 0 TO 3',
        '    TX = PIECEX + PX(I)',
        '    TY = PIECEY + PY(I)',
        '    IF TY >= 0 AND TY < ROWS AND TX >= 0 AND TX < COLS THEN',
        '        IF BOARD(TY, TX) > 0 THEN GAMEOVER = 1',
        '    END IF',
        'NEXT I',
        'RETURN'
    ], max_steps=100000)

    print(f"    Iterations: {interp.variables.get('FINAL_ITERCOUNT')}")
    print(f"    Locks: {interp.variables.get('FINAL_LOCKCOUNT')}")
    print(f"    Game Over: {interp.variables.get('FINAL_GAMEOVER')}")
    print(f"    Board(19,4): {interp.variables.get('FINAL_BOARD_19_4')}")
    print(f"    Board(19,5): {interp.variables.get('FINAL_BOARD_19_5')}")
    print(f"    Board(18,4): {interp.variables.get('FINAL_BOARD_18_4')}")
    print(f"    Final PIECEY: {interp.variables.get('FINAL_PIECEY')}")
    print(f"    Final PIECECOLOR: {interp.variables.get('FINAL_PIECECOLOR')}")

    # Should have locked at least 2 pieces
    assert interp.variables.get('FINAL_LOCKCOUNT') == 2, f"Expected 2 locks, got {interp.variables.get('FINAL_LOCKCOUNT')}"

    # First piece should have blocks at bottom (O piece at position 4)
    assert interp.variables.get('FINAL_BOARD_19_4') == 11, f"Expected BOARD(19,4)=11, got {interp.variables.get('FINAL_BOARD_19_4')}"
    assert interp.variables.get('FINAL_BOARD_19_5') == 11, f"Expected BOARD(19,5)=11, got {interp.variables.get('FINAL_BOARD_19_5')}"
    assert interp.variables.get('FINAL_BOARD_18_4') == 11, f"Expected BOARD(18,4)=11, got {interp.variables.get('FINAL_BOARD_18_4')}"

    # After second lock, new piece should be ready (T piece, color 14)
    assert interp.variables.get('FINAL_PIECECOLOR') == 14, f"Expected PIECECOLOR=14 after second lock, got {interp.variables.get('FINAL_PIECECOLOR')}"
    assert interp.variables.get('FINAL_PIECEY') == 0, f"Expected PIECEY=0 after lock, got {interp.variables.get('FINAL_PIECEY')}"

    print(f"  Simulated piece fall and lock: PASSED (steps={steps})")

def test_actual_tetris_file():
    """Test loading and running the actual tetris.bas file."""
    print("Testing actual tetris.bas file...")
    import os
    tetris_path = os.path.join(os.path.dirname(__file__), 'examples', 'tetris.bas')

    with open(tetris_path, 'r') as f:
        lines = f.read().splitlines()

    interp = setup()
    interp.reset(lines)

    # Run for a limited number of steps to simulate game startup
    # The game has _DELAY which will pause it, so we run many steps
    max_steps = 50000
    steps = 0
    while interp.running and steps < max_steps:
        interp.step()
        steps += 1

    # Check that the game initialized correctly
    assert 'BOARD' in interp.variables, "BOARD array not created"
    assert 'PX' in interp.variables, "PX array not created"
    assert 'PY' in interp.variables, "PY array not created"
    assert 'NX' in interp.variables, "NX array not created"
    assert 'NY' in interp.variables, "NY array not created"
    assert 'PIECECOLOR' in interp.variables, "PIECECOLOR not set"
    assert 'NEXTCOLOR' in interp.variables, "NEXTCOLOR not set"
    assert 'PIECEX' in interp.variables, "PIECEX not set"
    assert 'PIECEY' in interp.variables, "PIECEY not set"
    assert 'SCORE' in interp.variables, "SCORE not set"
    assert 'LINES' in interp.variables, "LINES not set"
    assert 'LEVEL' in interp.variables, "LEVEL not set"
    assert 'GAMEOVER' in interp.variables, "GAMEOVER not set"

    # The game should still be running (no errors)
    # Note: it might have stopped due to reaching ENDGAME via GAMEOVER
    # or due to reaching max_steps
    print(f"  Actual tetris.bas file: PASSED (steps={steps}, running={interp.running})")
    print(f"    Variables set: SCORE={interp.variables.get('SCORE')}, LINES={interp.variables.get('LINES')}, LEVEL={interp.variables.get('LEVEL')}")
    print(f"    PIECEX={interp.variables.get('PIECEX')}, PIECEY={interp.variables.get('PIECEY')}, GAMEOVER={interp.variables.get('GAMEOVER')}")
    print(f"    PIECECOLOR={interp.variables.get('PIECECOLOR')}, NEXTCOLOR={interp.variables.get('NEXTCOLOR')}")

def test_spawning_new_piece_after_lock():
    """Test that new piece spawns correctly after locking."""
    print("Testing spawning new piece after lock...")
    interp, steps = run_program([
        'CONST COLS = 10',
        'CONST ROWS = 20',
        'DIM BOARD(19, 9)',
        'DIM PX(3)',
        'DIM PY(3)',
        'DIM NX(3)',
        'DIM NY(3)',
        'GAMEOVER = 0',
        'NX(0) = -1 : NY(0) = 0',
        'NX(1) = 0 : NY(1) = 0',
        'NX(2) = 1 : NY(2) = 0',
        'NX(3) = 0 : NY(3) = 1',
        'NEXTCOLOR = 13',
        'PIECECOLOR = 11',
        'PX(0) = 0 : PY(0) = 0',
        'PX(1) = 1 : PY(1) = 0',
        'PX(2) = 0 : PY(2) = 1',
        'PX(3) = 1 : PY(3) = 1',
        'PIECEX = 4',
        'PIECEY = 18',
        'GOSUB LOCKPIECE',
        'FINAL_PX0 = PX(0)',
        'FINAL_PX1 = PX(1)',
        'FINAL_PX2 = PX(2)',
        'FINAL_PX3 = PX(3)',
        'FINAL_PY0 = PY(0)',
        'FINAL_PY3 = PY(3)',
        'FINAL_PIECEX = PIECEX',
        'FINAL_PIECEY = PIECEY',
        'FINAL_PIECECOLOR = PIECECOLOR',
        'END',
        'LOCKPIECE:',
        'FOR I = 0 TO 3',
        '    TX = PIECEX + PX(I)',
        '    TY = PIECEY + PY(I)',
        '    IF TY >= 0 AND TY < ROWS AND TX >= 0 AND TX < COLS THEN',
        '        BOARD(TY, TX) = PIECECOLOR',
        '    END IF',
        '    IF TY < 0 THEN GAMEOVER = 1',
        'NEXT I',
        'FOR I = 0 TO 3',
        '    PX(I) = NX(I)',
        '    PY(I) = NY(I)',
        'NEXT I',
        'PIECECOLOR = NEXTCOLOR',
        'PIECEX = 4',
        'PIECEY = 0',
        'RETURN'
    ], max_steps=5000)

    # New piece should have the T-piece shape from NX/NY
    assert interp.variables.get('FINAL_PX0') == -1, f"Expected PX(0)=-1, got {interp.variables.get('FINAL_PX0')}"
    assert interp.variables.get('FINAL_PX1') == 0, f"Expected PX(1)=0, got {interp.variables.get('FINAL_PX1')}"
    assert interp.variables.get('FINAL_PX2') == 1, f"Expected PX(2)=1, got {interp.variables.get('FINAL_PX2')}"
    assert interp.variables.get('FINAL_PX3') == 0, f"Expected PX(3)=0, got {interp.variables.get('FINAL_PX3')}"
    assert interp.variables.get('FINAL_PY0') == 0, f"Expected PY(0)=0, got {interp.variables.get('FINAL_PY0')}"
    assert interp.variables.get('FINAL_PY3') == 1, f"Expected PY(3)=1, got {interp.variables.get('FINAL_PY3')}"
    assert interp.variables.get('FINAL_PIECEX') == 4, f"Expected PIECEX=4, got {interp.variables.get('FINAL_PIECEX')}"
    assert interp.variables.get('FINAL_PIECEY') == 0, f"Expected PIECEY=0, got {interp.variables.get('FINAL_PIECEY')}"
    assert interp.variables.get('FINAL_PIECECOLOR') == 13, f"Expected PIECECOLOR=13, got {interp.variables.get('FINAL_PIECECOLOR')}"

    print(f"  Spawning new piece after lock: PASSED (steps={steps})")

def test_repeated_game_loop_cycles():
    """Test multiple game loop cycles with locking and spawning."""
    print("Testing repeated game loop cycles...")
    interp, steps = run_program([
        'CONST COLS = 10',
        'CONST ROWS = 20',
        'DIM BOARD(19, 9)',
        'DIM PX(3)',
        'DIM PY(3)',
        'DIM NX(3)',
        'DIM NY(3)',
        'GAMEOVER = 0',
        'LOCKCOUNT = 0',
        'PIECEX = 4',
        'PIECEY = 16',
        'PIECECOLOR = 11',
        'NEXTCOLOR = 14',
        'PX(0) = 0 : PY(0) = 0',
        'PX(1) = 1 : PY(1) = 0',
        'PX(2) = 0 : PY(2) = 1',
        'PX(3) = 1 : PY(3) = 1',
        'NX(0) = -1 : NY(0) = 0',
        'NX(1) = 0 : NY(1) = 0',
        'NX(2) = 1 : NY(2) = 0',
        'NX(3) = 0 : NY(3) = 1',
        'ITERATIONS = 0',
        'MAINLOOP:',
        'IF GAMEOVER = 1 THEN GOTO ENDGAME',
        'IF LOCKCOUNT >= 5 THEN GOTO ENDGAME',
        'ITERATIONS = ITERATIONS + 1',
        'IF ITERATIONS > 500 THEN GOTO ENDGAME',
        'MOVEX = 0',
        'MOVEY = 1',
        'GOSUB TRYMOVE',
        'IF MOVED = 0 THEN',
        '    GOSUB LOCKPIECE',
        '    LOCKCOUNT = LOCKCOUNT + 1',
        'END IF',
        'GOTO MAINLOOP',
        'ENDGAME:',
        'FINALCOUNT = LOCKCOUNT',
        'FINALITER = ITERATIONS',
        'END',
        'TRYMOVE:',
        'MOVED = 0',
        'NEWX = PIECEX + MOVEX',
        'NEWY = PIECEY + MOVEY',
        'CANCOLLIDE = 0',
        'FOR I = 0 TO 3',
        '    TX = NEWX + PX(I)',
        '    TY = NEWY + PY(I)',
        '    IF TX < 0 OR TX >= COLS THEN CANCOLLIDE = 1',
        '    IF TY >= ROWS THEN CANCOLLIDE = 1',
        '    IF TY >= 0 AND TY < ROWS AND TX >= 0 AND TX < COLS THEN',
        '        IF BOARD(TY, TX) > 0 THEN CANCOLLIDE = 1',
        '    END IF',
        'NEXT I',
        'IF CANCOLLIDE = 0 THEN',
        '    PIECEX = NEWX',
        '    PIECEY = NEWY',
        '    MOVED = 1',
        'END IF',
        'RETURN',
        'LOCKPIECE:',
        'FOR I = 0 TO 3',
        '    TX = PIECEX + PX(I)',
        '    TY = PIECEY + PY(I)',
        '    IF TY >= 0 AND TY < ROWS AND TX >= 0 AND TX < COLS THEN',
        '        BOARD(TY, TX) = PIECECOLOR',
        '    END IF',
        '    IF TY < 0 THEN GAMEOVER = 1',
        'NEXT I',
        'FOR I = 0 TO 3',
        '    PX(I) = NX(I)',
        '    PY(I) = NY(I)',
        'NEXT I',
        'PIECECOLOR = NEXTCOLOR',
        'PIECEX = 4',
        'PIECEY = 0',
        'FOR I = 0 TO 3',
        '    TX = PIECEX + PX(I)',
        '    TY = PIECEY + PY(I)',
        '    IF TY >= 0 AND TY < ROWS AND TX >= 0 AND TX < COLS THEN',
        '        IF BOARD(TY, TX) > 0 THEN GAMEOVER = 1',
        '    END IF',
        'NEXT I',
        'RETURN'
    ], max_steps=100000)
    assert interp.variables.get('FINALCOUNT') >= 2, f"Expected at least 2 locks, got {interp.variables.get('FINALCOUNT')}"
    print(f"  Repeated game loop cycles: PASSED (locks={interp.variables.get('FINALCOUNT')}, iterations={interp.variables.get('FINALITER')}, steps={steps})")

# ============================================================
# RUN ALL TESTS
# ============================================================

def run_all_tests():
    """Run all Tetris-related tests."""
    print("=" * 60)
    print("TETRIS INTERPRETER TEST SUITE")
    print("=" * 60)

    tests = [
        # 2D Arrays
        test_2d_array_basic,
        test_2d_array_variable_indices,
        test_2d_array_expression_indices,

        # FOR loops with arrays
        test_for_loop_array_copy,
        test_for_loop_2d_array_assignment,

        # GOSUB/RETURN
        test_simple_gosub,
        test_nested_gosub,
        test_multiple_gosub_calls,

        # Collision detection
        test_collision_detection_floor,
        test_collision_detection_no_collision,
        test_collision_detection_with_board,

        # LOCKPIECE
        test_lockpiece_basic,

        # TRYMOVE
        test_trymove_pattern,
        test_trymove_collision_stops_piece,

        # Gravity and Lock
        test_gravity_then_lock,

        # GOTO
        test_goto_label,
        test_conditional_goto,

        # Line clearing
        test_line_check_full,
        test_line_check_not_full,

        # Rotation
        test_rotation_clockwise,

        # Multi-statement lines
        test_colon_statements,
        test_colon_array_assignments,

        # Expressions
        test_int_function,

        # Complex scenarios
        test_full_game_cycle,

        # Edge cases
        test_piece_at_top_gameover,
        test_for_step_negative,
        test_nested_for_loops,

        # CLEARLINES tests
        test_clearlines_goto_loop,
        test_clearlines_with_full_row,
        test_clearlines_full_subroutine,
        test_complete_lockpiece_with_clearlines,
        test_repeated_game_loop_cycles,

        # DIM inside subroutine tests
        test_dim_inside_subroutine,
        test_repeated_dim_in_loop,

        # Board persistence tests
        test_board_persistence_after_multiple_locks,
        test_game_over_detection,
        test_spawning_new_piece_after_lock,

        # Actual Tetris file test
        test_actual_tetris_file,

        # Full simulation tests
        test_simulate_piece_fall_and_lock,

        # Bug regression tests
        test_line_with_array_color,
    ]

    passed = 0
    failed = 0

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

    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 60)

    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
