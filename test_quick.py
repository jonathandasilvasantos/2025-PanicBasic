"""Quick unit tests for BASIC interpreter."""

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
    _expr_cache.clear()
    _compiled_expr_cache.clear()
    font = pygame.font.Font(None, 16)
    return BasicInterpreter(font, 800, 600)

def test_expression_conversion():
    """Test expression conversion."""
    print("Testing expression conversion...")

    assert convert_basic_expr("x", None) == "X"
    assert convert_basic_expr("name$", None) == "NAME_STR"
    assert convert_basic_expr("INKEY$", None) == "INKEY()"
    assert convert_basic_expr("x OR y", None).count(" or ") == 1
    assert '"Score: 100"' in convert_basic_expr('"Score: 100"', None)

    print("  Expression conversion: PASSED")

def test_string_protection():
    """Test string literal protection."""
    print("Testing string protection...")

    expr, strings = _protect_strings('"hello"')
    assert len(strings) == 1
    assert strings[0] == '"hello"'

    restored = _restore_strings(expr, strings)
    assert restored == '"hello"'

    print("  String protection: PASSED")

def test_variable_assignment():
    """Test variable assignment."""
    print("Testing variable assignment...")

    interp = setup()
    interp.reset(["x = 42"])
    interp.step()
    assert interp.variables.get("X") == 42

    print("  Variable assignment: PASSED")

def test_for_loop():
    """Test FOR loop."""
    print("Testing FOR loop...")

    interp = setup()
    interp.reset([
        "sum = 0",
        "FOR i = 1 TO 5",
        "sum = sum + i",
        "NEXT i"
    ])
    while interp.running:
        interp.step()
    assert interp.variables.get("SUM") == 15

    print("  FOR loop: PASSED")

def test_do_loop():
    """Test DO LOOP."""
    print("Testing DO LOOP...")

    interp = setup()
    interp.reset([
        "x = 0",
        "DO WHILE x < 5",
        "x = x + 1",
        "LOOP"
    ])
    while interp.running:
        interp.step()
    assert interp.variables.get("X") == 5

    print("  DO LOOP: PASSED")

def test_delay():
    """Test DELAY doesn't freeze."""
    print("Testing DELAY...")

    import time
    interp = setup()
    interp.reset([
        "SCREEN 13",
        "x = 0",
        "DO",
        "x = x + 1",
        "_DELAY 0.001",
        "LOOP WHILE x < 3"
    ])

    start = time.time()
    steps = 0
    while interp.running and steps < 100 and (time.time() - start) < 2:
        interp.step()
        steps += 1
        time.sleep(0.01)

    assert interp.variables.get("X") == 3, f"Expected X=3, got X={interp.variables.get('X')}"

    print("  DELAY: PASSED")

def test_graphics():
    """Test graphics commands."""
    print("Testing graphics...")

    interp = setup()
    interp.reset(["SCREEN 13", "PSET (100, 100), 15"])
    interp.step()
    interp.step()

    color = interp.surface.get_at((100, 100))[:3]
    assert color == (255, 255, 255), f"Expected white, got {color}"

    print("  Graphics: PASSED")

def test_string_with_colon():
    """Test string with colon doesn't split incorrectly."""
    print("Testing string with colon...")

    interp = setup()
    # This used to fail - the colon inside the string was treated as statement separator
    # Add a loop to keep program running so we can verify no error occurred
    interp.reset(['SCREEN 13', 'x = 1', 'PRINT "Score: 100"', 'x = 2'])
    while interp.running:
        interp.step()
    # If colon in string was mishandled, we'd get an error and x wouldn't be 2
    assert interp.variables.get("X") == 2, f"Expected X=2, got X={interp.variables.get('X')}"

    print("  String with colon: PASSED")

def test_if_then():
    """Test IF THEN."""
    print("Testing IF THEN...")

    interp = setup()
    interp.reset([
        "x = 10",
        "IF x > 5 THEN y = 1"
    ])
    interp.step()
    interp.step()
    assert interp.variables.get("Y") == 1

    print("  IF THEN: PASSED")

def test_gosub_return():
    """Test GOSUB/RETURN."""
    print("Testing GOSUB/RETURN...")

    interp = setup()
    interp.reset([
        "x = 1",
        "GOSUB adder",
        "x = x + 100",
        "END",
        "adder:",
        "x = x + 10",
        "RETURN"
    ])
    while interp.running:
        interp.step()
    assert interp.variables.get("X") == 111

    print("  GOSUB/RETURN: PASSED")

def run_all_tests():
    print("=" * 50)
    print("Running BASIC Interpreter Unit Tests")
    print("=" * 50)

    try:
        test_expression_conversion()
        test_string_protection()
        test_variable_assignment()
        test_for_loop()
        test_do_loop()
        test_delay()
        test_graphics()
        test_string_with_colon()
        test_if_then()
        test_gosub_return()

        print("=" * 50)
        print("ALL TESTS PASSED!")
        print("=" * 50)
        return True
    except AssertionError as e:
        print(f"TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
