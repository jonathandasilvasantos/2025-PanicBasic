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
