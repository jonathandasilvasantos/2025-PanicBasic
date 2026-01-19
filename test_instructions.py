"""
Comprehensive unit tests for BASIC interpreter instructions.
Reference: QBasic 4.5 behavior
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

def run_program(lines):
    """Run a BASIC program and return the interpreter state."""
    interp = setup()
    interp.reset(lines)
    max_steps = 1000
    steps = 0
    while interp.running and steps < max_steps:
        interp.step()
        steps += 1
    return interp, steps

# ============================================================
# VARIABLE ASSIGNMENT TESTS
# ============================================================

def test_simple_assignment():
    """Test simple variable assignment."""
    print("Testing simple assignment...")
    interp, _ = run_program(['X = 42'])
    assert interp.variables.get('X') == 42, f"Expected 42, got {interp.variables.get('X')}"
    print("  Simple assignment: PASSED")

def test_let_assignment():
    """Test LET keyword assignment."""
    print("Testing LET assignment...")
    interp, _ = run_program(['LET X = 100'])
    assert interp.variables.get('X') == 100
    print("  LET assignment: PASSED")

def test_string_variable():
    """Test string variable assignment."""
    print("Testing string variable...")
    interp, _ = run_program(['name$ = "Hello"'])
    assert interp.variables.get('NAME$') == "Hello", f"Expected 'Hello', got {interp.variables.get('NAME$')}"
    print("  String variable: PASSED")

def test_expression_assignment():
    """Test assignment with expression."""
    print("Testing expression assignment...")
    interp, _ = run_program(['X = 10 + 5 * 2'])
    assert interp.variables.get('X') == 20
    print("  Expression assignment: PASSED")

def test_variable_in_expression():
    """Test using variable in expression."""
    print("Testing variable in expression...")
    interp, _ = run_program(['X = 10', 'Y = X + 5'])
    assert interp.variables.get('Y') == 15
    print("  Variable in expression: PASSED")

# ============================================================
# CONST TESTS
# ============================================================

def test_const():
    """Test CONST declaration."""
    print("Testing CONST...")
    interp, _ = run_program(['CONST PI = 3.14159', 'X = PI * 2'])
    assert abs(interp.variables.get('X') - 6.28318) < 0.001
    print("  CONST: PASSED")

# ============================================================
# ARRAY (DIM) TESTS
# ============================================================

def test_dim_1d():
    """Test 1D array declaration."""
    print("Testing DIM 1D array...")
    interp, _ = run_program([
        'DIM arr(5)',
        'arr(0) = 10',
        'arr(1) = 20',
        'X = arr(0) + arr(1)'
    ])
    assert interp.variables.get('X') == 30
    print("  DIM 1D array: PASSED")

def test_dim_2d():
    """Test 2D array declaration."""
    print("Testing DIM 2D array...")
    interp, _ = run_program([
        'DIM grid(3, 3)',
        'grid(0, 0) = 1',
        'grid(1, 1) = 5',
        'X = grid(0, 0) + grid(1, 1)'
    ])
    assert interp.variables.get('X') == 6
    print("  DIM 2D array: PASSED")

def test_array_with_variable_index():
    """Test array access with variable index."""
    print("Testing array with variable index...")
    interp, _ = run_program([
        'DIM arr(5)',
        'arr(0) = 100',
        'I = 0',
        'X = arr(I)'
    ])
    assert interp.variables.get('X') == 100
    print("  Array with variable index: PASSED")

# ============================================================
# ARITHMETIC OPERATORS TESTS
# ============================================================

def test_addition():
    """Test addition operator."""
    print("Testing addition...")
    interp, _ = run_program(['X = 5 + 3'])
    assert interp.variables.get('X') == 8
    print("  Addition: PASSED")

def test_subtraction():
    """Test subtraction operator."""
    print("Testing subtraction...")
    interp, _ = run_program(['X = 10 - 3'])
    assert interp.variables.get('X') == 7
    print("  Subtraction: PASSED")

def test_multiplication():
    """Test multiplication operator."""
    print("Testing multiplication...")
    interp, _ = run_program(['X = 4 * 5'])
    assert interp.variables.get('X') == 20
    print("  Multiplication: PASSED")

def test_division():
    """Test division operator."""
    print("Testing division...")
    interp, _ = run_program(['X = 20 / 4'])
    assert interp.variables.get('X') == 5
    print("  Division: PASSED")

def test_exponentiation():
    """Test exponentiation operator."""
    print("Testing exponentiation...")
    interp, _ = run_program(['X = 2 ^ 3'])
    assert interp.variables.get('X') == 8
    print("  Exponentiation: PASSED")

def test_mod_operator():
    """Test MOD operator."""
    print("Testing MOD...")
    interp, _ = run_program(['X = 17 MOD 5'])
    assert interp.variables.get('X') == 2
    print("  MOD: PASSED")

def test_negative_numbers():
    """Test negative numbers."""
    print("Testing negative numbers...")
    interp, _ = run_program(['X = -5', 'Y = X + 10'])
    assert interp.variables.get('Y') == 5
    print("  Negative numbers: PASSED")

# ============================================================
# COMPARISON OPERATORS TESTS
# ============================================================

def test_equal():
    """Test equality comparison."""
    print("Testing equality...")
    interp, _ = run_program(['X = 5', 'IF X = 5 THEN Y = 1'])
    assert interp.variables.get('Y') == 1
    print("  Equality: PASSED")

def test_not_equal():
    """Test inequality comparison."""
    print("Testing inequality...")
    interp, _ = run_program(['X = 5', 'IF X <> 3 THEN Y = 1'])
    assert interp.variables.get('Y') == 1
    print("  Inequality: PASSED")

def test_less_than():
    """Test less than comparison."""
    print("Testing less than...")
    interp, _ = run_program(['X = 3', 'IF X < 5 THEN Y = 1'])
    assert interp.variables.get('Y') == 1
    print("  Less than: PASSED")

def test_greater_than():
    """Test greater than comparison."""
    print("Testing greater than...")
    interp, _ = run_program(['X = 10', 'IF X > 5 THEN Y = 1'])
    assert interp.variables.get('Y') == 1
    print("  Greater than: PASSED")

def test_less_equal():
    """Test less than or equal comparison."""
    print("Testing less than or equal...")
    interp, _ = run_program(['X = 5', 'IF X <= 5 THEN Y = 1'])
    assert interp.variables.get('Y') == 1
    print("  Less than or equal: PASSED")

def test_greater_equal():
    """Test greater than or equal comparison."""
    print("Testing greater than or equal...")
    interp, _ = run_program(['X = 5', 'IF X >= 5 THEN Y = 1'])
    assert interp.variables.get('Y') == 1
    print("  Greater than or equal: PASSED")

# ============================================================
# LOGICAL OPERATORS TESTS
# ============================================================

def test_and_operator():
    """Test AND operator."""
    print("Testing AND...")
    interp, _ = run_program(['X = 5', 'IF X > 3 AND X < 10 THEN Y = 1'])
    assert interp.variables.get('Y') == 1
    print("  AND: PASSED")

def test_or_operator():
    """Test OR operator."""
    print("Testing OR...")
    interp, _ = run_program(['X = 15', 'IF X < 3 OR X > 10 THEN Y = 1'])
    assert interp.variables.get('Y') == 1
    print("  OR: PASSED")

def test_not_operator():
    """Test NOT operator."""
    print("Testing NOT...")
    interp, _ = run_program(['X = 0', 'IF NOT X THEN Y = 1'])
    assert interp.variables.get('Y') == 1
    print("  NOT: PASSED")

# ============================================================
# IF-THEN TESTS
# ============================================================

def test_if_then_single_line():
    """Test single-line IF THEN."""
    print("Testing IF THEN single line...")
    interp, _ = run_program(['X = 10', 'IF X > 5 THEN Y = 1'])
    assert interp.variables.get('Y') == 1
    print("  IF THEN single line: PASSED")

def test_if_then_false():
    """Test IF THEN when condition is false."""
    print("Testing IF THEN false...")
    interp, _ = run_program(['X = 3', 'Y = 0', 'IF X > 5 THEN Y = 1'])
    assert interp.variables.get('Y') == 0
    print("  IF THEN false: PASSED")

def test_if_then_else_block():
    """Test multi-line IF THEN ELSE END IF."""
    print("Testing IF THEN ELSE block...")
    interp, _ = run_program([
        'X = 3',
        'IF X > 5 THEN',
        '  Y = 1',
        'ELSE',
        '  Y = 2',
        'END IF'
    ])
    assert interp.variables.get('Y') == 2
    print("  IF THEN ELSE block: PASSED")

def test_elseif():
    """Test ELSEIF."""
    print("Testing ELSEIF...")
    interp, _ = run_program([
        'X = 2',
        'IF X = 1 THEN',
        '  Y = 10',
        'ELSEIF X = 2 THEN',
        '  Y = 20',
        'ELSE',
        '  Y = 30',
        'END IF'
    ])
    assert interp.variables.get('Y') == 20
    print("  ELSEIF: PASSED")

def test_nested_if():
    """Test nested IF blocks."""
    print("Testing nested IF...")
    interp, _ = run_program([
        'X = 5',
        'Y = 10',
        'IF X > 3 THEN',
        '  IF Y > 5 THEN',
        '    Z = 1',
        '  END IF',
        'END IF'
    ])
    assert interp.variables.get('Z') == 1
    print("  Nested IF: PASSED")

# ============================================================
# FOR-NEXT TESTS
# ============================================================

def test_for_next_basic():
    """Test basic FOR NEXT loop."""
    print("Testing FOR NEXT basic...")
    interp, _ = run_program([
        'total = 0',
        'FOR i = 1 TO 5',
        '  total = total + i',
        'NEXT i'
    ])
    assert interp.variables.get('TOTAL') == 15  # 1+2+3+4+5
    print("  FOR NEXT basic: PASSED")

def test_for_next_step():
    """Test FOR NEXT with STEP."""
    print("Testing FOR NEXT STEP...")
    interp, _ = run_program([
        'total = 0',
        'FOR i = 2 TO 10 STEP 2',
        '  total = total + i',
        'NEXT i'
    ])
    assert interp.variables.get('TOTAL') == 30  # 2+4+6+8+10
    print("  FOR NEXT STEP: PASSED")

def test_for_next_step_negative():
    """Test FOR NEXT with negative STEP."""
    print("Testing FOR NEXT negative STEP...")
    interp, _ = run_program([
        'total = 0',
        'FOR i = 5 TO 1 STEP -1',
        '  total = total + i',
        'NEXT i'
    ])
    assert interp.variables.get('TOTAL') == 15  # 5+4+3+2+1
    print("  FOR NEXT negative STEP: PASSED")

def test_for_next_nested():
    """Test nested FOR loops."""
    print("Testing nested FOR loops...")
    interp, _ = run_program([
        'total = 0',
        'FOR i = 1 TO 3',
        '  FOR j = 1 TO 2',
        '    total = total + 1',
        '  NEXT j',
        'NEXT i'
    ])
    assert interp.variables.get('TOTAL') == 6  # 3*2
    print("  Nested FOR loops: PASSED")

def test_exit_for():
    """Test EXIT FOR."""
    print("Testing EXIT FOR...")
    interp, _ = run_program([
        'total = 0',
        'FOR i = 1 TO 10',
        '  total = total + i',
        '  IF i = 5 THEN EXIT FOR',
        'NEXT i'
    ])
    assert interp.variables.get('TOTAL') == 15  # 1+2+3+4+5
    print("  EXIT FOR: PASSED")

# ============================================================
# DO-LOOP TESTS
# ============================================================

def test_do_while():
    """Test DO WHILE loop."""
    print("Testing DO WHILE...")
    interp, _ = run_program([
        'X = 0',
        'DO WHILE X < 5',
        '  X = X + 1',
        'LOOP'
    ])
    assert interp.variables.get('X') == 5
    print("  DO WHILE: PASSED")

def test_do_until():
    """Test DO UNTIL loop."""
    print("Testing DO UNTIL...")
    interp, _ = run_program([
        'X = 0',
        'DO UNTIL X >= 5',
        '  X = X + 1',
        'LOOP'
    ])
    assert interp.variables.get('X') == 5
    print("  DO UNTIL: PASSED")

def test_do_loop_while():
    """Test DO LOOP WHILE (post-condition)."""
    print("Testing DO LOOP WHILE...")
    interp, _ = run_program([
        'X = 0',
        'DO',
        '  X = X + 1',
        'LOOP WHILE X < 5'
    ])
    assert interp.variables.get('X') == 5
    print("  DO LOOP WHILE: PASSED")

def test_do_loop_until():
    """Test DO LOOP UNTIL (post-condition)."""
    print("Testing DO LOOP UNTIL...")
    interp, _ = run_program([
        'X = 0',
        'DO',
        '  X = X + 1',
        'LOOP UNTIL X >= 5'
    ])
    assert interp.variables.get('X') == 5
    print("  DO LOOP UNTIL: PASSED")

def test_exit_do():
    """Test EXIT DO."""
    print("Testing EXIT DO...")
    interp, _ = run_program([
        'X = 0',
        'DO',
        '  X = X + 1',
        '  IF X = 3 THEN EXIT DO',
        'LOOP WHILE X < 10'
    ])
    assert interp.variables.get('X') == 3
    print("  EXIT DO: PASSED")

# ============================================================
# GOTO TESTS
# ============================================================

def test_goto_label():
    """Test GOTO with label."""
    print("Testing GOTO label...")
    interp, _ = run_program([
        'X = 1',
        'GOTO skip',
        'X = 2',
        'skip:',
        'Y = X'
    ])
    assert interp.variables.get('Y') == 1
    print("  GOTO label: PASSED")

def test_goto_line_number():
    """Test GOTO with line number."""
    print("Testing GOTO line number...")
    interp, _ = run_program([
        '10 X = 1',
        '20 GOTO 40',
        '30 X = 2',
        '40 Y = X'
    ])
    assert interp.variables.get('Y') == 1
    print("  GOTO line number: PASSED")

# ============================================================
# GOSUB-RETURN TESTS
# ============================================================

def test_gosub_return():
    """Test GOSUB and RETURN."""
    print("Testing GOSUB RETURN...")
    interp, _ = run_program([
        'X = 1',
        'GOSUB adder',
        'X = X + 100',
        'END',
        'adder:',
        'X = X + 10',
        'RETURN'
    ])
    assert interp.variables.get('X') == 111
    print("  GOSUB RETURN: PASSED")

def test_gosub_nested():
    """Test nested GOSUB calls."""
    print("Testing nested GOSUB...")
    interp, _ = run_program([
        'X = 0',
        'GOSUB sub1',
        'END',
        'sub1:',
        'X = X + 1',
        'GOSUB sub2',
        'X = X + 10',
        'RETURN',
        'sub2:',
        'X = X + 100',
        'RETURN'
    ])
    assert interp.variables.get('X') == 111
    print("  Nested GOSUB: PASSED")

# ============================================================
# MATH FUNCTIONS TESTS
# ============================================================

def test_abs():
    """Test ABS function."""
    print("Testing ABS...")
    interp, _ = run_program(['X = ABS(-5)'])
    assert interp.variables.get('X') == 5
    print("  ABS: PASSED")

def test_int():
    """Test INT function."""
    print("Testing INT...")
    interp, _ = run_program(['X = INT(3.7)'])
    assert interp.variables.get('X') == 3
    print("  INT: PASSED")

def test_int_negative():
    """Test INT with negative number (floors towards negative infinity)."""
    print("Testing INT negative...")
    interp, _ = run_program(['X = INT(-3.7)'])
    assert interp.variables.get('X') == -4  # QBasic floors towards -infinity
    print("  INT negative: PASSED")

def test_fix():
    """Test FIX function (truncates towards zero)."""
    print("Testing FIX...")
    interp, _ = run_program(['X = FIX(-3.7)'])
    assert interp.variables.get('X') == -3  # Truncates towards zero
    print("  FIX: PASSED")

def test_sgn():
    """Test SGN function."""
    print("Testing SGN...")
    interp, _ = run_program([
        'A = SGN(-5)',
        'B = SGN(0)',
        'C = SGN(5)'
    ])
    assert interp.variables.get('A') == -1
    assert interp.variables.get('B') == 0
    assert interp.variables.get('C') == 1
    print("  SGN: PASSED")

def test_sqr():
    """Test SQR function."""
    print("Testing SQR...")
    interp, _ = run_program(['X = SQR(16)'])
    assert interp.variables.get('X') == 4
    print("  SQR: PASSED")

def test_sin_cos():
    """Test SIN and COS functions."""
    print("Testing SIN COS...")
    interp, _ = run_program([
        'S = SIN(0)',
        'C = COS(0)'
    ])
    assert abs(interp.variables.get('S') - 0) < 0.001
    assert abs(interp.variables.get('C') - 1) < 0.001
    print("  SIN COS: PASSED")

def test_tan():
    """Test TAN function."""
    print("Testing TAN...")
    interp, _ = run_program(['X = TAN(0)'])
    assert abs(interp.variables.get('X') - 0) < 0.001
    print("  TAN: PASSED")

def test_atn():
    """Test ATN function."""
    print("Testing ATN...")
    interp, _ = run_program(['X = ATN(1)'])
    assert abs(interp.variables.get('X') - 0.7854) < 0.01  # pi/4
    print("  ATN: PASSED")

def test_rnd():
    """Test RND function."""
    print("Testing RND...")
    interp, _ = run_program(['X = RND'])
    x = interp.variables.get('X')
    assert 0 <= x < 1, f"RND should return 0-1, got {x}"
    print("  RND: PASSED")

# ============================================================
# STRING FUNCTIONS TESTS
# ============================================================

def test_len():
    """Test LEN function."""
    print("Testing LEN...")
    interp, _ = run_program(['X = LEN("Hello")'])
    assert interp.variables.get('X') == 5
    print("  LEN: PASSED")

def test_left():
    """Test LEFT$ function."""
    print("Testing LEFT$...")
    interp, _ = run_program(['X$ = LEFT$("Hello", 2)'])
    assert interp.variables.get('X$') == "He", f"Expected 'He', got {interp.variables.get('X$')}"
    print("  LEFT$: PASSED")

def test_right():
    """Test RIGHT$ function."""
    print("Testing RIGHT$...")
    interp, _ = run_program(['X$ = RIGHT$("Hello", 2)'])
    assert interp.variables.get('X$') == "lo", f"Expected 'lo', got {interp.variables.get('X$')}"
    print("  RIGHT$: PASSED")

def test_mid():
    """Test MID$ function."""
    print("Testing MID$...")
    interp, _ = run_program(['X$ = MID$("Hello", 2, 3)'])
    assert interp.variables.get('X$') == "ell", f"Expected 'ell', got {interp.variables.get('X$')}"
    print("  MID$: PASSED")

def test_chr():
    """Test CHR$ function."""
    print("Testing CHR$...")
    interp, _ = run_program(['X$ = CHR$(65)'])
    assert interp.variables.get('X$') == "A", f"Expected 'A', got {interp.variables.get('X$')}"
    print("  CHR$: PASSED")

def test_str():
    """Test STR$ function."""
    print("Testing STR$...")
    interp, _ = run_program(['X$ = STR$(42)'])
    assert interp.variables.get('X$') == "42", f"Expected '42', got {interp.variables.get('X$')}"
    print("  STR$: PASSED")

def test_val():
    """Test VAL function."""
    print("Testing VAL...")
    interp, _ = run_program(['X = VAL("42")'])
    assert interp.variables.get('X') == 42
    print("  VAL: PASSED")

# ============================================================
# OTHER FUNCTIONS TESTS
# ============================================================

def test_timer():
    """Test TIMER function."""
    print("Testing TIMER...")
    interp, _ = run_program(['X = TIMER'])
    x = interp.variables.get('X')
    assert 0 <= x < 86400, f"TIMER should be 0-86400, got {x}"
    print("  TIMER: PASSED")

# ============================================================
# GRAPHICS TESTS
# ============================================================

def test_screen():
    """Test SCREEN command."""
    print("Testing SCREEN...")
    interp, _ = run_program(['SCREEN 13'])
    assert interp.screen_width == 320
    assert interp.screen_height == 200
    assert interp.surface is not None
    print("  SCREEN: PASSED")

def test_pset():
    """Test PSET command."""
    print("Testing PSET...")
    interp, _ = run_program(['SCREEN 13', 'PSET (100, 50), 15'])
    color = interp.surface.get_at((100, 50))[:3]
    assert color == (255, 255, 255), f"Expected white, got {color}"
    print("  PSET: PASSED")

def test_line():
    """Test LINE command."""
    print("Testing LINE...")
    interp, _ = run_program(['SCREEN 13', 'LINE (0, 0)-(10, 0), 15'])
    color = interp.surface.get_at((5, 0))[:3]
    assert color == (255, 255, 255)
    print("  LINE: PASSED")

def test_line_box():
    """Test LINE with B (box) option."""
    print("Testing LINE box...")
    interp, _ = run_program(['SCREEN 13', 'LINE (10, 10)-(20, 20), 15, B'])
    # Check corners
    assert interp.surface.get_at((10, 10))[:3] == (255, 255, 255)
    assert interp.surface.get_at((20, 10))[:3] == (255, 255, 255)
    print("  LINE box: PASSED")

def test_line_filled_box():
    """Test LINE with BF (filled box) option."""
    print("Testing LINE filled box...")
    interp, _ = run_program(['SCREEN 13', 'LINE (10, 10)-(20, 20), 4, BF'])
    # Check center
    color = interp.surface.get_at((15, 15))[:3]
    assert color == (170, 0, 0), f"Expected red, got {color}"
    print("  LINE filled box: PASSED")

def test_circle():
    """Test CIRCLE command."""
    print("Testing CIRCLE...")
    interp, _ = run_program(['SCREEN 13', 'CIRCLE (100, 100), 10, 15'])
    # Just verify no error
    print("  CIRCLE: PASSED")

def test_cls():
    """Test CLS command."""
    print("Testing CLS...")
    interp, _ = run_program(['SCREEN 13', 'PSET (100, 100), 15', 'CLS'])
    color = interp.surface.get_at((100, 100))[:3]
    assert color == (0, 0, 0), f"Expected black after CLS, got {color}"
    print("  CLS: PASSED")

def test_color():
    """Test COLOR command."""
    print("Testing COLOR...")
    interp, _ = run_program(['SCREEN 13', 'COLOR 14, 1'])
    assert interp.current_fg_color == 14
    assert interp.current_bg_color == 1
    print("  COLOR: PASSED")

# ============================================================
# COMMENT TESTS
# ============================================================

def test_rem():
    """Test REM comment."""
    print("Testing REM...")
    interp, _ = run_program(['REM This is a comment', 'X = 5'])
    assert interp.variables.get('X') == 5
    print("  REM: PASSED")

def test_apostrophe_comment():
    """Test apostrophe comment."""
    print("Testing apostrophe comment...")
    interp, _ = run_program(["X = 5 ' This is a comment"])
    assert interp.variables.get('X') == 5
    print("  Apostrophe comment: PASSED")

# ============================================================
# MULTI-STATEMENT LINE TESTS
# ============================================================

def test_multi_statement():
    """Test multiple statements on one line."""
    print("Testing multi-statement line...")
    interp, _ = run_program(['X = 1 : Y = 2 : Z = X + Y'])
    assert interp.variables.get('Z') == 3
    print("  Multi-statement line: PASSED")

def test_colon_in_string():
    """Test colon inside string doesn't split."""
    print("Testing colon in string...")
    interp, _ = run_program([
        'X = 1',
        'msg$ = "Time: 12:00"',
        'Y = 2'
    ])
    assert interp.variables.get('MSG$') == "Time: 12:00", f"Expected 'Time: 12:00', got {interp.variables.get('MSG$')}"
    assert interp.variables.get('Y') == 2
    print("  Colon in string: PASSED")

# ============================================================
# END STATEMENT TEST
# ============================================================

def test_end():
    """Test END statement."""
    print("Testing END...")
    interp, _ = run_program([
        'X = 1',
        'END',
        'X = 2'
    ])
    assert interp.variables.get('X') == 1
    print("  END: PASSED")

# ============================================================
# DELAY TEST
# ============================================================

def test_delay():
    """Test _DELAY command."""
    print("Testing _DELAY...")
    interp = setup()
    interp.reset([
        'SCREEN 13',
        'X = 0',
        'DO',
        '  X = X + 1',
        '  _DELAY 0.001',
        'LOOP WHILE X < 3'
    ])

    import time
    start = time.time()
    max_steps = 500
    steps = 0
    while interp.running and steps < max_steps and (time.time() - start) < 5:
        interp.step()
        steps += 1
        time.sleep(0.01)

    assert interp.variables.get('X') == 3, f"Expected X=3, got X={interp.variables.get('X')}"
    print("  _DELAY: PASSED")

# ============================================================
# RANDOMIZE TEST
# ============================================================

def test_randomize():
    """Test RANDOMIZE command."""
    print("Testing RANDOMIZE...")
    interp, _ = run_program([
        'RANDOMIZE 12345',
        'X = RND'
    ])
    # Just verify no error and X is set
    assert interp.variables.get('X') is not None
    print("  RANDOMIZE: PASSED")

# ============================================================
# NEW STRING FUNCTIONS TESTS
# ============================================================

def test_asc():
    """Test ASC function."""
    print("Testing ASC...")
    interp, _ = run_program(['X = ASC("A")'])
    assert interp.variables.get('X') == 65, f"Expected 65, got {interp.variables.get('X')}"
    print("  ASC: PASSED")

def test_asc_string_var():
    """Test ASC with string variable."""
    print("Testing ASC with string var...")
    interp, _ = run_program(['s$ = "Hello"', 'X = ASC(s$)'])
    assert interp.variables.get('X') == 72, f"Expected 72 (H), got {interp.variables.get('X')}"
    print("  ASC with string var: PASSED")

def test_instr():
    """Test INSTR function."""
    print("Testing INSTR...")
    interp, _ = run_program(['X = INSTR("Hello World", "World")'])
    assert interp.variables.get('X') == 7, f"Expected 7, got {interp.variables.get('X')}"
    print("  INSTR: PASSED")

def test_instr_with_start():
    """Test INSTR with start position."""
    print("Testing INSTR with start...")
    # INSTR(5, ...) starts searching at position 5, which is 'o' in "Hello World"
    # So it finds 'o' immediately at position 5
    interp, _ = run_program(['X = INSTR(5, "Hello World", "o")'])
    assert interp.variables.get('X') == 5, f"Expected 5, got {interp.variables.get('X')}"
    # To find the SECOND 'o', start at position 6
    interp2, _ = run_program(['X = INSTR(6, "Hello World", "o")'])
    assert interp2.variables.get('X') == 8, f"Expected 8, got {interp2.variables.get('X')}"
    print("  INSTR with start: PASSED")

def test_instr_not_found():
    """Test INSTR when substring not found."""
    print("Testing INSTR not found...")
    interp, _ = run_program(['X = INSTR("Hello", "xyz")'])
    assert interp.variables.get('X') == 0, f"Expected 0, got {interp.variables.get('X')}"
    print("  INSTR not found: PASSED")

def test_lcase():
    """Test LCASE$ function."""
    print("Testing LCASE$...")
    interp, _ = run_program(['X$ = LCASE$("HELLO World")'])
    assert interp.variables.get('X$') == "hello world", f"Expected 'hello world', got {interp.variables.get('X$')}"
    print("  LCASE$: PASSED")

def test_ucase():
    """Test UCASE$ function."""
    print("Testing UCASE$...")
    interp, _ = run_program(['X$ = UCASE$("Hello World")'])
    assert interp.variables.get('X$') == "HELLO WORLD", f"Expected 'HELLO WORLD', got {interp.variables.get('X$')}"
    print("  UCASE$: PASSED")

def test_ltrim():
    """Test LTRIM$ function."""
    print("Testing LTRIM$...")
    interp, _ = run_program(['X$ = LTRIM$("   Hello")'])
    assert interp.variables.get('X$') == "Hello", f"Expected 'Hello', got '{interp.variables.get('X$')}'"
    print("  LTRIM$: PASSED")

def test_rtrim():
    """Test RTRIM$ function."""
    print("Testing RTRIM$...")
    interp, _ = run_program(['X$ = RTRIM$("Hello   ")'])
    assert interp.variables.get('X$') == "Hello", f"Expected 'Hello', got '{interp.variables.get('X$')}'"
    print("  RTRIM$: PASSED")

def test_space():
    """Test SPACE$ function."""
    print("Testing SPACE$...")
    interp, _ = run_program(['X$ = SPACE$(5)'])
    assert interp.variables.get('X$') == "     ", f"Expected 5 spaces, got '{interp.variables.get('X$')}'"
    print("  SPACE$: PASSED")

def test_string_char():
    """Test STRING$ function with character."""
    print("Testing STRING$ with char...")
    interp, _ = run_program(['X$ = STRING$(5, "*")'])
    assert interp.variables.get('X$') == "*****", f"Expected '*****', got '{interp.variables.get('X$')}'"
    print("  STRING$ with char: PASSED")

def test_string_code():
    """Test STRING$ function with ASCII code."""
    print("Testing STRING$ with code...")
    interp, _ = run_program(['X$ = STRING$(3, 65)'])
    assert interp.variables.get('X$') == "AAA", f"Expected 'AAA', got '{interp.variables.get('X$')}'"
    print("  STRING$ with code: PASSED")

def test_hex():
    """Test HEX$ function."""
    print("Testing HEX$...")
    interp, _ = run_program(['X$ = HEX$(255)'])
    assert interp.variables.get('X$') == "FF", f"Expected 'FF', got '{interp.variables.get('X$')}'"
    print("  HEX$: PASSED")

def test_oct():
    """Test OCT$ function."""
    print("Testing OCT$...")
    interp, _ = run_program(['X$ = OCT$(64)'])
    assert interp.variables.get('X$') == "100", f"Expected '100', got '{interp.variables.get('X$')}'"
    print("  OCT$: PASSED")

# ============================================================
# NEW MATH FUNCTIONS TESTS
# ============================================================

def test_log():
    """Test LOG function."""
    print("Testing LOG...")
    interp, _ = run_program(['X = LOG(2.718281828)'])
    assert abs(interp.variables.get('X') - 1.0) < 0.001, f"Expected ~1.0, got {interp.variables.get('X')}"
    print("  LOG: PASSED")

def test_exp():
    """Test EXP function."""
    print("Testing EXP...")
    interp, _ = run_program(['X = EXP(1)'])
    assert abs(interp.variables.get('X') - 2.718281828) < 0.001, f"Expected ~2.718, got {interp.variables.get('X')}"
    print("  EXP: PASSED")

def test_cint():
    """Test CINT function (round to nearest)."""
    print("Testing CINT...")
    interp, _ = run_program([
        'A = CINT(3.4)',
        'B = CINT(3.6)',
        'C = CINT(-3.6)'
    ])
    assert interp.variables.get('A') == 3, f"Expected 3, got {interp.variables.get('A')}"
    assert interp.variables.get('B') == 4, f"Expected 4, got {interp.variables.get('B')}"
    assert interp.variables.get('C') == -4, f"Expected -4, got {interp.variables.get('C')}"
    print("  CINT: PASSED")

# ============================================================
# DATE$ AND TIME$ TESTS
# ============================================================

def test_date_function():
    """Test DATE$ function."""
    print("Testing DATE$...")
    interp, _ = run_program(['X$ = DATE$'])
    date_val = interp.variables.get('X$')
    assert date_val is not None
    assert len(date_val) == 10  # MM-DD-YYYY format
    assert date_val[2] == '-' and date_val[5] == '-'
    print("  DATE$: PASSED")

def test_time_function():
    """Test TIME$ function."""
    print("Testing TIME$...")
    interp, _ = run_program(['X$ = TIME$'])
    time_val = interp.variables.get('X$')
    assert time_val is not None
    assert len(time_val) == 8  # HH:MM:SS format
    assert time_val[2] == ':' and time_val[5] == ':'
    print("  TIME$: PASSED")

# ============================================================
# SWAP STATEMENT TESTS
# ============================================================

def test_swap():
    """Test SWAP statement."""
    print("Testing SWAP...")
    interp, _ = run_program([
        'A = 10',
        'B = 20',
        'SWAP A, B'
    ])
    assert interp.variables.get('A') == 20, f"Expected A=20, got {interp.variables.get('A')}"
    assert interp.variables.get('B') == 10, f"Expected B=10, got {interp.variables.get('B')}"
    print("  SWAP: PASSED")

def test_swap_strings():
    """Test SWAP with string variables."""
    print("Testing SWAP strings...")
    interp, _ = run_program([
        'A$ = "Hello"',
        'B$ = "World"',
        'SWAP A$, B$'
    ])
    assert interp.variables.get('A$') == "World"
    assert interp.variables.get('B$') == "Hello"
    print("  SWAP strings: PASSED")

def test_swap_array_elements():
    """Test SWAP with array elements."""
    print("Testing SWAP array elements...")
    interp, _ = run_program([
        'DIM arr(5)',
        'arr(0) = 100',
        'arr(1) = 200',
        'SWAP arr(0), arr(1)',
        'X = arr(0)',
        'Y = arr(1)'
    ])
    assert interp.variables.get('X') == 200
    assert interp.variables.get('Y') == 100
    print("  SWAP array elements: PASSED")

# ============================================================
# WHILE...WEND TESTS
# ============================================================

def test_while_wend():
    """Test WHILE...WEND loop."""
    print("Testing WHILE...WEND...")
    interp, _ = run_program([
        'X = 0',
        'WHILE X < 5',
        '  X = X + 1',
        'WEND'
    ])
    assert interp.variables.get('X') == 5, f"Expected 5, got {interp.variables.get('X')}"
    print("  WHILE...WEND: PASSED")

def test_while_false_initially():
    """Test WHILE when condition is false initially."""
    print("Testing WHILE false initially...")
    interp, _ = run_program([
        'X = 10',
        'Y = 0',
        'WHILE X < 5',
        '  Y = Y + 1',
        'WEND'
    ])
    assert interp.variables.get('Y') == 0, f"Expected 0, got {interp.variables.get('Y')}"
    print("  WHILE false initially: PASSED")

def test_while_nested():
    """Test nested WHILE loops."""
    print("Testing nested WHILE...")
    interp, _ = run_program([
        'total = 0',
        'I = 0',
        'WHILE I < 3',
        '  J = 0',
        '  WHILE J < 2',
        '    total = total + 1',
        '    J = J + 1',
        '  WEND',
        '  I = I + 1',
        'WEND'
    ])
    assert interp.variables.get('TOTAL') == 6, f"Expected 6, got {interp.variables.get('TOTAL')}"
    print("  Nested WHILE: PASSED")

# ============================================================
# SELECT CASE TESTS
# ============================================================

def test_select_case_simple():
    """Test simple SELECT CASE."""
    print("Testing SELECT CASE simple...")
    interp, _ = run_program([
        'X = 2',
        'SELECT CASE X',
        '  CASE 1',
        '    Y = 10',
        '  CASE 2',
        '    Y = 20',
        '  CASE 3',
        '    Y = 30',
        'END SELECT'
    ])
    assert interp.variables.get('Y') == 20, f"Expected 20, got {interp.variables.get('Y')}"
    print("  SELECT CASE simple: PASSED")

def test_select_case_else():
    """Test SELECT CASE with CASE ELSE."""
    print("Testing SELECT CASE ELSE...")
    interp, _ = run_program([
        'X = 99',
        'SELECT CASE X',
        '  CASE 1',
        '    Y = 10',
        '  CASE 2',
        '    Y = 20',
        '  CASE ELSE',
        '    Y = 999',
        'END SELECT'
    ])
    assert interp.variables.get('Y') == 999, f"Expected 999, got {interp.variables.get('Y')}"
    print("  SELECT CASE ELSE: PASSED")

def test_select_case_range():
    """Test SELECT CASE with range (TO)."""
    print("Testing SELECT CASE range...")
    interp, _ = run_program([
        'X = 7',
        'SELECT CASE X',
        '  CASE 1 TO 5',
        '    Y = 1',
        '  CASE 6 TO 10',
        '    Y = 2',
        '  CASE ELSE',
        '    Y = 0',
        'END SELECT'
    ])
    assert interp.variables.get('Y') == 2, f"Expected 2, got {interp.variables.get('Y')}"
    print("  SELECT CASE range: PASSED")

def test_select_case_is():
    """Test SELECT CASE with IS comparison."""
    print("Testing SELECT CASE IS...")
    interp, _ = run_program([
        'X = 15',
        'SELECT CASE X',
        '  CASE IS < 5',
        '    Y = 1',
        '  CASE IS >= 10',
        '    Y = 2',
        '  CASE ELSE',
        '    Y = 0',
        'END SELECT'
    ])
    assert interp.variables.get('Y') == 2, f"Expected 2, got {interp.variables.get('Y')}"
    print("  SELECT CASE IS: PASSED")

def test_select_case_string():
    """Test SELECT CASE with strings."""
    print("Testing SELECT CASE strings...")
    interp, _ = run_program([
        's$ = "B"',
        'SELECT CASE s$',
        '  CASE "A"',
        '    Y = 1',
        '  CASE "B"',
        '    Y = 2',
        '  CASE "C"',
        '    Y = 3',
        'END SELECT'
    ])
    assert interp.variables.get('Y') == 2, f"Expected 2, got {interp.variables.get('Y')}"
    print("  SELECT CASE strings: PASSED")

# ============================================================
# DATA/READ/RESTORE TESTS
# ============================================================

def test_data_read():
    """Test DATA and READ statements."""
    print("Testing DATA/READ...")
    interp, _ = run_program([
        'DATA 10, 20, 30',
        'READ A',
        'READ B',
        'READ C'
    ])
    assert interp.variables.get('A') == 10
    assert interp.variables.get('B') == 20
    assert interp.variables.get('C') == 30
    print("  DATA/READ: PASSED")

def test_data_read_strings():
    """Test DATA and READ with strings."""
    print("Testing DATA/READ strings...")
    interp, _ = run_program([
        'DATA "Hello", "World"',
        'READ A$, B$'
    ])
    assert interp.variables.get('A$') == "Hello"
    assert interp.variables.get('B$') == "World"
    print("  DATA/READ strings: PASSED")

def test_data_multiple_lines():
    """Test DATA across multiple lines."""
    print("Testing DATA multiple lines...")
    interp, _ = run_program([
        'DATA 1, 2, 3',
        'DATA 4, 5, 6',
        'total = 0',
        'FOR i = 1 TO 6',
        '  READ X',
        '  total = total + X',
        'NEXT i'
    ])
    assert interp.variables.get('TOTAL') == 21, f"Expected 21, got {interp.variables.get('TOTAL')}"
    print("  DATA multiple lines: PASSED")

def test_restore():
    """Test RESTORE statement."""
    print("Testing RESTORE...")
    interp, _ = run_program([
        'DATA 10, 20',
        'READ A',
        'READ B',
        'RESTORE',
        'READ C',
        'READ D'
    ])
    assert interp.variables.get('A') == 10
    assert interp.variables.get('B') == 20
    assert interp.variables.get('C') == 10  # Re-read after RESTORE
    assert interp.variables.get('D') == 20
    print("  RESTORE: PASSED")

def test_restore_label():
    """Test RESTORE with label."""
    print("Testing RESTORE with label...")
    interp, _ = run_program([
        'GOTO start',
        'data1:',
        'DATA 1, 2, 3',
        'data2:',
        'DATA 10, 20, 30',
        'start:',
        'RESTORE data2',
        'READ A, B, C'
    ])
    assert interp.variables.get('A') == 10
    assert interp.variables.get('B') == 20
    assert interp.variables.get('C') == 30
    print("  RESTORE with label: PASSED")

# ============================================================
# ON...GOTO / ON...GOSUB TESTS
# ============================================================

def test_on_goto_basic():
    """Test basic ON...GOTO computed branch."""
    print("Testing ON...GOTO basic...")
    interp, _ = run_program([
        'X = 2',
        'ON X GOTO label1, label2, label3',
        'R = 0',
        'GOTO done',
        'label1:',
        '  R = 10',
        '  GOTO done',
        'label2:',
        '  R = 20',
        '  GOTO done',
        'label3:',
        '  R = 30',
        '  GOTO done',
        'done:'
    ])
    assert interp.variables.get('R') == 20, f"Expected R=20, got R={interp.variables.get('R')}"
    print("  ON...GOTO basic: PASSED")

def test_on_goto_first():
    """Test ON...GOTO with index 1."""
    print("Testing ON...GOTO first...")
    interp, _ = run_program([
        'X = 1',
        'ON X GOTO a, b, c',
        'R = 0',
        'GOTO done',
        'a:',
        '  R = 1',
        '  GOTO done',
        'b:',
        '  R = 2',
        '  GOTO done',
        'c:',
        '  R = 3',
        '  GOTO done',
        'done:'
    ])
    assert interp.variables.get('R') == 1
    print("  ON...GOTO first: PASSED")

def test_on_goto_out_of_range():
    """Test ON...GOTO with out-of-range index (should continue)."""
    print("Testing ON...GOTO out of range...")
    interp, _ = run_program([
        'X = 5',  # Out of range (only 3 labels)
        'ON X GOTO a, b, c',
        'R = 99',  # Should execute this since index is out of range
        'GOTO done',
        'a:',
        '  R = 1',
        '  GOTO done',
        'b:',
        '  R = 2',
        '  GOTO done',
        'c:',
        '  R = 3',
        '  GOTO done',
        'done:'
    ])
    assert interp.variables.get('R') == 99, f"Expected R=99, got R={interp.variables.get('R')}"
    print("  ON...GOTO out of range: PASSED")

def test_on_goto_zero_index():
    """Test ON...GOTO with index 0 (should continue)."""
    print("Testing ON...GOTO zero index...")
    interp, _ = run_program([
        'X = 0',
        'ON X GOTO a, b, c',
        'R = 99',
        'GOTO done',
        'a:',
        '  R = 1',
        '  GOTO done',
        'b:',
        '  R = 2',
        '  GOTO done',
        'c:',
        '  R = 3',
        '  GOTO done',
        'done:'
    ])
    assert interp.variables.get('R') == 99
    print("  ON...GOTO zero index: PASSED")

def test_on_gosub_basic():
    """Test basic ON...GOSUB computed branch."""
    print("Testing ON...GOSUB basic...")
    interp, _ = run_program([
        'R = 0',
        'X = 2',
        'ON X GOSUB sub1, sub2, sub3',
        'GOTO done',
        'sub1:',
        '  R = 10',
        '  RETURN',
        'sub2:',
        '  R = 20',
        '  RETURN',
        'sub3:',
        '  R = 30',
        '  RETURN',
        'done:'
    ])
    assert interp.variables.get('R') == 20, f"Expected R=20, got R={interp.variables.get('R')}"
    print("  ON...GOSUB basic: PASSED")

def test_on_gosub_returns():
    """Test ON...GOSUB properly returns to next statement."""
    print("Testing ON...GOSUB returns...")
    interp, _ = run_program([
        'A = 0',
        'B = 0',
        'X = 1',
        'ON X GOSUB addTen, addTwenty',
        'B = 100',  # This should execute after RETURN
        'GOTO done',
        'addTen:',
        '  A = 10',
        '  RETURN',
        'addTwenty:',
        '  A = 20',
        '  RETURN',
        'done:'
    ])
    assert interp.variables.get('A') == 10
    assert interp.variables.get('B') == 100, f"Expected B=100 (returned), got B={interp.variables.get('B')}"
    print("  ON...GOSUB returns: PASSED")

def test_on_goto_expression():
    """Test ON...GOTO with expression as selector."""
    print("Testing ON...GOTO expression...")
    interp, _ = run_program([
        'A = 1',
        'B = 1',
        'ON A + B GOTO first, second, third',
        'R = 0',
        'GOTO done',
        'first:',
        '  R = 1',
        '  GOTO done',
        'second:',
        '  R = 2',
        '  GOTO done',
        'third:',
        '  R = 3',
        '  GOTO done',
        'done:'
    ])
    # A + B = 2, so should go to second
    assert interp.variables.get('R') == 2
    print("  ON...GOTO expression: PASSED")

# ============================================================
# CSRLIN AND POS TESTS
# ============================================================

def test_csrlin():
    """Test CSRLIN function (cursor row)."""
    print("Testing CSRLIN...")
    interp, _ = run_program([
        'SCREEN 13',
        'LOCATE 5, 10',
        'R = CSRLIN'
    ])
    assert interp.variables.get('R') == 5, f"Expected row 5, got {interp.variables.get('R')}"
    print("  CSRLIN: PASSED")

def test_pos():
    """Test POS(0) function (cursor column)."""
    print("Testing POS...")
    interp, _ = run_program([
        'SCREEN 13',
        'LOCATE 5, 10',
        'C = POS(0)'
    ])
    assert interp.variables.get('C') == 10, f"Expected column 10, got {interp.variables.get('C')}"
    print("  POS: PASSED")

def test_csrlin_after_print():
    """Test CSRLIN after PRINT advances row."""
    print("Testing CSRLIN after PRINT...")
    interp, _ = run_program([
        'SCREEN 13',
        'LOCATE 1, 1',
        'PRINT "Line 1"',
        'PRINT "Line 2"',
        'R = CSRLIN'
    ])
    # After two PRINTs starting at row 1, cursor should be at row 3
    assert interp.variables.get('R') == 3, f"Expected row 3, got {interp.variables.get('R')}"
    print("  CSRLIN after PRINT: PASSED")

# ============================================================
# TAB AND SPC TESTS
# ============================================================

def test_tab():
    """Test TAB function in PRINT."""
    print("Testing TAB...")
    interp = setup()
    interp.reset([
        'SCREEN 13',
        'LOCATE 1, 1',
        'X$ = TAB(10)'
    ])
    # Run until complete
    max_steps = 100
    steps = 0
    while interp.running and steps < max_steps:
        interp.step()
        steps += 1
    # TAB(10) when at column 1 should return 9 spaces
    result = interp.variables.get('X$')
    assert result == "         ", f"Expected 9 spaces, got '{result}' (len={len(result) if result else 0})"
    print("  TAB: PASSED")

def test_spc():
    """Test SPC function."""
    print("Testing SPC...")
    interp, _ = run_program([
        'X$ = SPC(5)'
    ])
    result = interp.variables.get('X$')
    assert result == "     ", f"Expected 5 spaces, got '{result}' (len={len(result) if result else 0})"
    print("  SPC: PASSED")

def test_spc_zero():
    """Test SPC(0) returns empty string."""
    print("Testing SPC zero...")
    interp, _ = run_program([
        'X$ = SPC(0)'
    ])
    result = interp.variables.get('X$')
    assert result == "", f"Expected empty string, got '{result}'"
    print("  SPC zero: PASSED")

def test_spc_negative():
    """Test SPC with negative returns empty string."""
    print("Testing SPC negative...")
    interp, _ = run_program([
        'X$ = SPC(-5)'
    ])
    result = interp.variables.get('X$')
    assert result == "", f"Expected empty string, got '{result}'"
    print("  SPC negative: PASSED")

# ============================================================
# INPUT STATEMENT TESTS (state setup verification)
# ============================================================

def test_input_state_setup():
    """Test INPUT statement sets up input mode correctly."""
    print("Testing INPUT state setup...")
    interp = setup()
    interp.reset([
        'SCREEN 13',
        'INPUT "Enter name: "; name$'
    ])
    # Run one step to hit the INPUT statement
    interp.step()
    # Check that input mode was activated
    assert interp.input_mode == True, "Expected input_mode to be True"
    assert interp.input_prompt == "Enter name: ? ", f"Expected prompt 'Enter name: ? ', got '{interp.input_prompt}'"
    assert interp.input_variables == ['name$'], f"Expected variables ['name$'], got {interp.input_variables}"
    print("  INPUT state setup: PASSED")

def test_input_prompt_no_question():
    """Test INPUT with comma separator (no question mark)."""
    print("Testing INPUT no question mark...")
    interp = setup()
    interp.reset([
        'SCREEN 13',
        'INPUT "Name", name$'
    ])
    interp.step()
    assert interp.input_mode == True
    assert interp.input_prompt == "Name", f"Expected prompt 'Name', got '{interp.input_prompt}'"
    print("  INPUT no question mark: PASSED")

def test_input_multiple_variables():
    """Test INPUT with multiple variables."""
    print("Testing INPUT multiple vars...")
    interp = setup()
    interp.reset([
        'SCREEN 13',
        'INPUT "Values: "; a, b, c'
    ])
    interp.step()
    assert interp.input_mode == True
    assert interp.input_variables == ['a', 'b', 'c'], f"Expected ['a', 'b', 'c'], got {interp.input_variables}"
    print("  INPUT multiple vars: PASSED")

def test_input_no_prompt():
    """Test INPUT without prompt string."""
    print("Testing INPUT no prompt...")
    interp = setup()
    interp.reset([
        'SCREEN 13',
        'INPUT x'
    ])
    interp.step()
    assert interp.input_mode == True
    assert interp.input_prompt == "? ", f"Expected prompt '? ', got '{interp.input_prompt}'"
    assert interp.input_variables == ['x']
    print("  INPUT no prompt: PASSED")

def test_input_complete_numeric():
    """Test INPUT completion assigns numeric value."""
    print("Testing INPUT complete numeric...")
    interp = setup()
    interp.reset([
        'SCREEN 13',
        'INPUT "Value: "; x'
    ])
    interp.step()  # Enter input mode
    assert interp.input_mode == True

    # Simulate typing "42" and pressing Enter
    interp.input_buffer = "42"
    interp._complete_input()

    assert interp.input_mode == False, "Expected input_mode to be False after completion"
    assert interp.variables.get('X') == 42, f"Expected X=42, got X={interp.variables.get('X')}"
    print("  INPUT complete numeric: PASSED")

def test_input_complete_string():
    """Test INPUT completion assigns string value."""
    print("Testing INPUT complete string...")
    interp = setup()
    interp.reset([
        'SCREEN 13',
        'INPUT "Name: "; name$'
    ])
    interp.step()  # Enter input mode

    # Simulate typing "Hello" and pressing Enter
    interp.input_buffer = "Hello"
    interp._complete_input()

    assert interp.input_mode == False
    assert interp.variables.get('NAME$') == "Hello", f"Expected NAME$='Hello', got NAME$={interp.variables.get('NAME$')}"
    print("  INPUT complete string: PASSED")

def test_input_complete_multiple():
    """Test INPUT completion assigns multiple values."""
    print("Testing INPUT complete multiple...")
    interp = setup()
    interp.reset([
        'SCREEN 13',
        'INPUT "Values: "; a, b, c'
    ])
    interp.step()

    # Simulate typing "10, 20, 30" and pressing Enter
    interp.input_buffer = "10, 20, 30"
    interp._complete_input()

    assert interp.variables.get('A') == 10
    assert interp.variables.get('B') == 20
    assert interp.variables.get('C') == 30
    print("  INPUT complete multiple: PASSED")

# ============================================================
# RUN ALL TESTS
# ============================================================

def run_all_tests():
    print("=" * 60)
    print("BASIC Interpreter Instruction Tests")
    print("Reference: QBasic 4.5")
    print("=" * 60)

    tests = [
        # Variables
        test_simple_assignment,
        test_let_assignment,
        test_string_variable,
        test_expression_assignment,
        test_variable_in_expression,
        test_const,

        # Arrays
        test_dim_1d,
        test_dim_2d,
        test_array_with_variable_index,

        # Arithmetic
        test_addition,
        test_subtraction,
        test_multiplication,
        test_division,
        test_exponentiation,
        test_mod_operator,
        test_negative_numbers,

        # Comparison
        test_equal,
        test_not_equal,
        test_less_than,
        test_greater_than,
        test_less_equal,
        test_greater_equal,

        # Logical
        test_and_operator,
        test_or_operator,
        test_not_operator,

        # IF-THEN
        test_if_then_single_line,
        test_if_then_false,
        test_if_then_else_block,
        test_elseif,
        test_nested_if,

        # FOR-NEXT
        test_for_next_basic,
        test_for_next_step,
        test_for_next_step_negative,
        test_for_next_nested,
        test_exit_for,

        # DO-LOOP
        test_do_while,
        test_do_until,
        test_do_loop_while,
        test_do_loop_until,
        test_exit_do,

        # GOTO
        test_goto_label,
        test_goto_line_number,

        # GOSUB-RETURN
        test_gosub_return,
        test_gosub_nested,

        # Math functions
        test_abs,
        test_int,
        test_int_negative,
        test_fix,
        test_sgn,
        test_sqr,
        test_sin_cos,
        test_tan,
        test_atn,
        test_rnd,

        # String functions
        test_len,
        test_left,
        test_right,
        test_mid,
        test_chr,
        test_str,
        test_val,

        # Other functions
        test_timer,

        # Graphics
        test_screen,
        test_pset,
        test_line,
        test_line_box,
        test_line_filled_box,
        test_circle,
        test_cls,
        test_color,

        # Comments
        test_rem,
        test_apostrophe_comment,

        # Multi-statement
        test_multi_statement,
        test_colon_in_string,

        # Other
        test_end,
        test_delay,
        test_randomize,

        # New string functions
        test_asc,
        test_asc_string_var,
        test_instr,
        test_instr_with_start,
        test_instr_not_found,
        test_lcase,
        test_ucase,
        test_ltrim,
        test_rtrim,
        test_space,
        test_string_char,
        test_string_code,
        test_hex,
        test_oct,

        # New math functions
        test_log,
        test_exp,
        test_cint,

        # Date/time functions
        test_date_function,
        test_time_function,

        # SWAP
        test_swap,
        test_swap_strings,
        test_swap_array_elements,

        # WHILE...WEND
        test_while_wend,
        test_while_false_initially,
        test_while_nested,

        # SELECT CASE
        test_select_case_simple,
        test_select_case_else,
        test_select_case_range,
        test_select_case_is,
        test_select_case_string,

        # DATA/READ/RESTORE
        test_data_read,
        test_data_read_strings,
        test_data_multiple_lines,
        test_restore,
        test_restore_label,

        # ON...GOTO / ON...GOSUB
        test_on_goto_basic,
        test_on_goto_first,
        test_on_goto_out_of_range,
        test_on_goto_zero_index,
        test_on_gosub_basic,
        test_on_gosub_returns,
        test_on_goto_expression,

        # CSRLIN and POS
        test_csrlin,
        test_pos,
        test_csrlin_after_print,

        # TAB and SPC
        test_tab,
        test_spc,
        test_spc_zero,
        test_spc_negative,

        # INPUT statement
        test_input_state_setup,
        test_input_prompt_no_question,
        test_input_multiple_variables,
        test_input_no_prompt,
        test_input_complete_numeric,
        test_input_complete_string,
        test_input_complete_multiple,
    ]

    passed = 0
    failed = 0
    failed_tests = []

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            failed += 1
            failed_tests.append((test.__name__, str(e)))
            print(f"  FAILED: {e}")
        except Exception as e:
            failed += 1
            failed_tests.append((test.__name__, str(e)))
            print(f"  ERROR: {e}")

    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed_tests:
        print("\nFailed tests:")
        for name, error in failed_tests:
            print(f"  - {name}: {error}")

    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
