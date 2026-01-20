"""
Unit tests for the BASIC interpreter.
Tests expression parsing, command execution, and rendering.
"""

import unittest
import sys
import os

# Initialize pygame with dummy video driver for headless testing
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
pygame.init()
pygame.font.init()

# Create a dummy display for tests that need it
pygame.display.set_mode((800, 600))

from interpreter import (
    BasicInterpreter, convert_basic_expr, _protect_strings,
    _restore_strings, _basic_to_python_identifier,
    _expr_cache, _compiled_expr_cache
)


class TestExpressionConversion(unittest.TestCase):
    """Test BASIC to Python expression conversion."""

    def setUp(self):
        """Clear caches before each test."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()

    def test_simple_variable(self):
        """Test simple variable conversion."""
        result = convert_basic_expr("x", None)
        self.assertEqual(result, "X")

    def test_string_variable(self):
        """Test string variable with $ suffix."""
        result = convert_basic_expr("name$", None)
        self.assertEqual(result, "NAME_STR")

    def test_integer_variable(self):
        """Test integer variable with % suffix."""
        result = convert_basic_expr("count%", None)
        self.assertEqual(result, "COUNT_INT")

    def test_arithmetic(self):
        """Test arithmetic expressions."""
        result = convert_basic_expr("x + y * 2", None)
        self.assertEqual(result, "X + Y * 2")

    def test_comparison_equal(self):
        """Test = converted to ==."""
        result = convert_basic_expr("x = 5", None)
        self.assertEqual(result, "X  ==  5")

    def test_comparison_not_equal(self):
        """Test <> converted to !=."""
        result = convert_basic_expr("x <> 5", None)
        self.assertEqual(result, "X  !=  5")

    def test_logical_and(self):
        """Test AND converted to and."""
        result = convert_basic_expr("x AND y", None)
        self.assertIn(" and ", result)

    def test_logical_or(self):
        """Test OR converted to or."""
        result = convert_basic_expr("x OR y", None)
        self.assertIn(" or ", result)

    def test_logical_not(self):
        """Test NOT converted to not."""
        result = convert_basic_expr("NOT x", None)
        self.assertIn(" not ", result)

    def test_mod_operator(self):
        """Test MOD converted to %."""
        result = convert_basic_expr("x MOD 5", None)
        self.assertIn(" % ", result)

    def test_inkey_function(self):
        """Test INKEY$ converted to INKEY()."""
        result = convert_basic_expr("INKEY$", None)
        self.assertEqual(result, "INKEY()")

    def test_timer_function(self):
        """Test TIMER converted to TIMER()."""
        result = convert_basic_expr("TIMER", None)
        self.assertEqual(result, "TIMER()")

    def test_rnd_function(self):
        """Test RND converted to RND()."""
        result = convert_basic_expr("RND", None)
        self.assertEqual(result, "RND()")

    def test_chr_function(self):
        """Test CHR$ function."""
        result = convert_basic_expr("CHR$(65)", None)
        self.assertIn("CHR(65)", result)

    def test_string_literal_preserved(self):
        """Test that string literals are not modified."""
        result = convert_basic_expr('"Hello World"', None)
        self.assertEqual(result, '"Hello World"')

    def test_string_with_colon_preserved(self):
        """Test string with colon inside is preserved."""
        result = convert_basic_expr('"Score: 100"', None)
        self.assertEqual(result, '"Score: 100"')

    def test_mixed_string_and_variable(self):
        """Test expression with string and variable."""
        result = convert_basic_expr('"Value: " + x', None)
        self.assertIn('"Value: "', result)
        self.assertIn("X", result)

    def test_python_keywords_preserved(self):
        """Test that Python keywords (and, or, not) stay lowercase."""
        # After conversion, 'or' should stay as 'or', not become 'OR'
        result = convert_basic_expr("x OR y", None)
        self.assertIn(" or ", result)
        self.assertNotIn(" OR ", result)


class TestStringProtection(unittest.TestCase):
    """Test string literal protection functions."""

    def test_protect_simple_string(self):
        """Test protecting a simple string."""
        expr, strings = _protect_strings('"hello"')
        self.assertEqual(len(strings), 1)
        self.assertEqual(strings[0], '"hello"')
        self.assertIn("__STR0__", expr)

    def test_protect_multiple_strings(self):
        """Test protecting multiple strings."""
        expr, strings = _protect_strings('"a" + "b"')
        self.assertEqual(len(strings), 2)
        self.assertIn("__STR0__", expr)
        self.assertIn("__STR1__", expr)

    def test_restore_strings(self):
        """Test restoring strings."""
        expr, strings = _protect_strings('"test"')
        restored = _restore_strings(expr, strings)
        self.assertEqual(restored, '"test"')

    def test_protect_string_with_special_chars(self):
        """Test string with special characters."""
        expr, strings = _protect_strings('"Score: 100"')
        self.assertEqual(strings[0], '"Score: 100"')


class TestIdentifierConversion(unittest.TestCase):
    """Test BASIC identifier to Python identifier conversion."""

    def test_simple_name(self):
        """Test simple variable name."""
        result = _basic_to_python_identifier("score")
        self.assertEqual(result, "SCORE")

    def test_string_suffix(self):
        """Test $ suffix conversion."""
        result = _basic_to_python_identifier("name$")
        self.assertEqual(result, "NAME_STR")

    def test_integer_suffix(self):
        """Test % suffix conversion."""
        result = _basic_to_python_identifier("count%")
        self.assertEqual(result, "COUNT_INT")


class TestInterpreterBasics(unittest.TestCase):
    """Test basic interpreter functionality."""

    def setUp(self):
        """Create interpreter instance for testing."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)

    def test_init(self):
        """Test interpreter initialization."""
        self.assertIsNotNone(self.interp)
        self.assertEqual(self.interp.screen_width, 320)
        self.assertEqual(self.interp.screen_height, 200)
        self.assertTrue(self.interp.running)

    def test_reset_with_empty_program(self):
        """Test reset with empty program."""
        self.interp.reset([])
        self.assertEqual(len(self.interp.program_lines), 0)
        self.assertEqual(self.interp.pc, 0)

    def test_reset_with_simple_program(self):
        """Test reset with simple program."""
        program = ["SCREEN 13", "CLS", "END"]
        self.interp.reset(program)
        self.assertEqual(len(self.interp.program_lines), 3)

    def test_basic_color(self):
        """Test color palette lookup."""
        self.assertEqual(self.interp.basic_color(0), (0, 0, 0))  # Black
        self.assertEqual(self.interp.basic_color(15), (255, 255, 255))  # White
        self.assertEqual(self.interp.basic_color(4), (170, 0, 0))  # Red

    def test_eval_simple_number(self):
        """Test evaluating simple number."""
        result = self.interp.eval_expr("42")
        self.assertEqual(result, 42)

    def test_eval_arithmetic(self):
        """Test evaluating arithmetic."""
        result = self.interp.eval_expr("10 + 5")
        self.assertEqual(result, 15)

    def test_eval_with_variable(self):
        """Test evaluating expression with variable."""
        self.interp.variables["X"] = 10
        result = self.interp.eval_expr("x + 5")
        self.assertEqual(result, 15)

    def test_eval_string(self):
        """Test evaluating string literal."""
        result = self.interp.eval_expr('"hello"')
        self.assertEqual(result, "hello")

    def test_eval_chr_function(self):
        """Test CHR$ function."""
        result = self.interp.eval_expr("CHR$(65)")
        self.assertEqual(result, "A")

    def test_eval_len_function(self):
        """Test LEN function."""
        result = self.interp.eval_expr('LEN("hello")')
        self.assertEqual(result, 5)

    def test_eval_int_function(self):
        """Test INT function."""
        result = self.interp.eval_expr("INT(3.7)")
        self.assertEqual(result, 3)

    def test_eval_abs_function(self):
        """Test ABS function."""
        result = self.interp.eval_expr("ABS(-5)")
        self.assertEqual(result, 5)

    def test_eval_sqr_function(self):
        """Test SQR function."""
        result = self.interp.eval_expr("SQR(16)")
        self.assertEqual(result, 4)

    def test_eval_sgn_function(self):
        """Test SGN function."""
        self.assertEqual(self.interp.eval_expr("SGN(10)"), 1)
        self.assertEqual(self.interp.eval_expr("SGN(-10)"), -1)
        self.assertEqual(self.interp.eval_expr("SGN(0)"), 0)


class TestCommandExecution(unittest.TestCase):
    """Test BASIC command execution."""

    def setUp(self):
        """Create interpreter and reset."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)

    def test_screen_command(self):
        """Test SCREEN 13 command."""
        self.interp.reset(["SCREEN 13"])
        self.interp.step()
        self.assertEqual(self.interp.screen_width, 320)
        self.assertEqual(self.interp.screen_height, 200)
        self.assertIsNotNone(self.interp.surface)

    def test_cls_command(self):
        """Test CLS command."""
        self.interp.reset(["SCREEN 13", "CLS"])
        self.interp.step()  # SCREEN
        self.interp.step()  # CLS
        self.assertEqual(self.interp.text_cursor, (1, 1))

    def test_variable_assignment(self):
        """Test variable assignment."""
        self.interp.reset(["x = 42"])
        self.interp.step()
        self.assertEqual(self.interp.variables.get("X"), 42)

    def test_let_assignment(self):
        """Test LET assignment."""
        self.interp.reset(["LET y = 100"])
        self.interp.step()
        self.assertEqual(self.interp.variables.get("Y"), 100)

    def test_const_definition(self):
        """Test CONST definition."""
        self.interp.reset(["CONST PI = 3.14"])
        self.interp.step()
        self.assertAlmostEqual(self.interp.constants.get("PI"), 3.14)

    def test_dim_1d_array(self):
        """Test DIM for 1D array."""
        self.interp.reset(["DIM arr(10)"])
        self.interp.step()
        self.assertIn("ARR", self.interp.variables)
        self.assertEqual(len(self.interp.variables["ARR"]), 11)  # 0-10

    def test_dim_2d_array(self):
        """Test DIM for 2D array."""
        self.interp.reset(["DIM grid(5, 5)"])
        self.interp.step()
        self.assertIn("GRID", self.interp.variables)
        self.assertEqual(len(self.interp.variables["GRID"]), 6)
        self.assertEqual(len(self.interp.variables["GRID"][0]), 6)

    def test_for_loop(self):
        """Test FOR loop execution."""
        self.interp.reset([
            "sum = 0",
            "FOR i = 1 TO 5",
            "sum = sum + i",
            "NEXT i"
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()
        self.assertEqual(self.interp.variables.get("SUM"), 15)

    def test_for_loop_with_step(self):
        """Test FOR loop with STEP."""
        self.interp.reset([
            "sum = 0",
            "FOR i = 0 TO 10 STEP 2",
            "sum = sum + i",
            "NEXT i"
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()
        self.assertEqual(self.interp.variables.get("SUM"), 30)  # 0+2+4+6+8+10

    def test_if_then_true(self):
        """Test IF THEN when condition is true."""
        self.interp.reset([
            "x = 10",
            "IF x > 5 THEN y = 1"
        ])
        self.interp.step()  # x = 10
        self.interp.step()  # IF
        self.assertEqual(self.interp.variables.get("Y"), 1)

    def test_if_then_false(self):
        """Test IF THEN when condition is false."""
        self.interp.reset([
            "x = 3",
            "y = 0",
            "IF x > 5 THEN y = 1"
        ])
        self.interp.step()  # x = 3
        self.interp.step()  # y = 0
        self.interp.step()  # IF (should not execute)
        self.assertEqual(self.interp.variables.get("Y"), 0)

    def test_if_else_block(self):
        """Test IF/ELSE/END IF block."""
        self.interp.reset([
            "x = 3",
            "IF x > 5 THEN",
            "y = 1",
            "ELSE",
            "y = 2",
            "END IF"
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()
        self.assertEqual(self.interp.variables.get("Y"), 2)

    def test_do_loop(self):
        """Test DO LOOP."""
        self.interp.reset([
            "x = 0",
            "DO",
            "x = x + 1",
            "LOOP WHILE x < 5"
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()
        self.assertEqual(self.interp.variables.get("X"), 5)

    def test_do_while_loop(self):
        """Test DO WHILE LOOP."""
        self.interp.reset([
            "x = 0",
            "DO WHILE x < 3",
            "x = x + 1",
            "LOOP"
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()
        self.assertEqual(self.interp.variables.get("X"), 3)

    def test_exit_for(self):
        """Test EXIT FOR."""
        self.interp.reset([
            "result = 0",
            "FOR i = 1 TO 100",
            "IF i = 5 THEN EXIT FOR",
            "result = i",
            "NEXT i"
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()
        self.assertEqual(self.interp.variables.get("RESULT"), 4)

    def test_exit_do(self):
        """Test EXIT DO."""
        self.interp.reset([
            "x = 0",
            "DO",
            "x = x + 1",
            "IF x = 3 THEN EXIT DO",
            "LOOP"
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()
        self.assertEqual(self.interp.variables.get("X"), 3)

    def test_goto(self):
        """Test GOTO."""
        self.interp.reset([
            "x = 1",
            "GOTO skip",
            "x = 2",
            "skip:",
            "x = x + 10"
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()
        self.assertEqual(self.interp.variables.get("X"), 11)

    def test_gosub_return(self):
        """Test GOSUB and RETURN."""
        self.interp.reset([
            "x = 1",
            "GOSUB adder",
            "x = x + 100",
            "END",
            "adder:",
            "x = x + 10",
            "RETURN"
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()
        self.assertEqual(self.interp.variables.get("X"), 111)

    def test_color_command(self):
        """Test COLOR command."""
        self.interp.reset(["COLOR 14, 1"])
        self.interp.step()
        self.assertEqual(self.interp.current_fg_color, 14)
        self.assertEqual(self.interp.current_bg_color, 1)

    def test_locate_command(self):
        """Test LOCATE command."""
        self.interp.reset(["SCREEN 13", "LOCATE 5, 10"])
        self.interp.step()  # SCREEN
        self.interp.step()  # LOCATE
        self.assertEqual(self.interp.text_cursor, (10, 5))

    def test_end_command(self):
        """Test END command."""
        self.interp.reset(["x = 1", "END", "x = 2"])
        self.interp.step()  # x = 1
        self.interp.step()  # END
        self.assertFalse(self.interp.running)
        self.assertEqual(self.interp.variables.get("X"), 1)


class TestGraphicsCommands(unittest.TestCase):
    """Test graphics commands."""

    def setUp(self):
        """Create interpreter with surface."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)
        self.interp.reset(["SCREEN 13"])
        self.interp.step()

    def test_pset(self):
        """Test PSET command."""
        self.interp.reset(["SCREEN 13", "PSET (100, 100), 15"])
        self.interp.step()  # SCREEN
        self.interp.step()  # PSET
        # Check pixel was set
        color = self.interp.surface.get_at((100, 100))[:3]
        self.assertEqual(color, (255, 255, 255))

    def test_line(self):
        """Test LINE command."""
        self.interp.reset(["SCREEN 13", "LINE (0, 0)-(100, 100), 15"])
        self.interp.step()  # SCREEN
        self.interp.step()  # LINE
        # Check endpoint pixel
        color = self.interp.surface.get_at((100, 100))[:3]
        self.assertEqual(color, (255, 255, 255))

    def test_line_box(self):
        """Test LINE with B option (box)."""
        self.interp.reset(["SCREEN 13", "LINE (10, 10)-(50, 50), 15, B"])
        self.interp.step()  # SCREEN
        self.interp.step()  # LINE
        # Check corner pixels
        color = self.interp.surface.get_at((10, 10))[:3]
        self.assertEqual(color, (255, 255, 255))

    def test_line_filled_box(self):
        """Test LINE with BF option (filled box)."""
        self.interp.reset(["SCREEN 13", "LINE (10, 10)-(50, 50), 4, BF"])
        self.interp.step()  # SCREEN
        self.interp.step()  # LINE
        # Check center pixel
        color = self.interp.surface.get_at((30, 30))[:3]
        self.assertEqual(color, (170, 0, 0))  # Red

    def test_circle(self):
        """Test CIRCLE command."""
        self.interp.reset(["SCREEN 13", "CIRCLE (100, 100), 20, 15"])
        self.interp.step()  # SCREEN
        self.interp.step()  # CIRCLE
        # Check that LPR was updated
        self.assertEqual(self.interp.lpr, (100, 100))

    def test_circle_filled(self):
        """Test filled CIRCLE command."""
        self.interp.reset(["SCREEN 13", "CIRCLE (100, 100), 20, 4, , , , F"])
        self.interp.step()  # SCREEN
        self.interp.step()  # CIRCLE
        # Check center pixel is filled
        color = self.interp.surface.get_at((100, 100))[:3]
        self.assertEqual(color, (170, 0, 0))  # Red

    def test_point(self):
        """Test POINT function."""
        self.interp.reset(["SCREEN 13", "PSET (50, 50), 4", "c = POINT(50, 50)"])
        self.interp.step()  # SCREEN
        self.interp.step()  # PSET
        self.interp.step()  # c = POINT
        self.assertEqual(self.interp.variables.get("C"), 4)


class TestStringHandling(unittest.TestCase):
    """Test string operations in statements."""

    def setUp(self):
        """Create interpreter."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)

    def test_string_with_colon_in_print(self):
        """Test PRINT with string containing colon."""
        # This should not split at the colon inside the string
        self.interp.reset(['SCREEN 13', 'PRINT "Score: 100"'])
        self.interp.step()  # SCREEN
        self.interp.step()  # PRINT - should not error
        self.assertTrue(self.interp.running)

    def test_string_variable_assignment(self):
        """Test string variable assignment."""
        self.interp.reset(['name$ = "Hello"'])
        self.interp.step()
        self.assertEqual(self.interp.variables.get("NAME$"), "Hello")

    def test_string_concatenation(self):
        """Test string concatenation."""
        self.interp.reset([
            'a$ = "Hello"',
            'b$ = " World"',
            'c$ = a$ + b$'
        ])
        self.interp.step()
        self.interp.step()
        self.interp.step()
        self.assertEqual(self.interp.variables.get("C$"), "Hello World")

    def test_left_function(self):
        """Test LEFT$ function."""
        result = self.interp.eval_expr('LEFT$("Hello", 2)')
        self.assertEqual(result, "He")

    def test_right_function(self):
        """Test RIGHT$ function."""
        result = self.interp.eval_expr('RIGHT$("Hello", 2)')
        self.assertEqual(result, "lo")

    def test_mid_function(self):
        """Test MID$ function."""
        result = self.interp.eval_expr('MID$("Hello", 2, 3)')
        self.assertEqual(result, "ell")

    def test_val_function(self):
        """Test VAL function."""
        result = self.interp.eval_expr('VAL("42")')
        self.assertEqual(result, 42)

    def test_str_function(self):
        """Test STR$ function."""
        result = self.interp.eval_expr('STR$(42)')
        self.assertEqual(result, "42")


class TestStatementSplitting(unittest.TestCase):
    """Test that statement splitting respects string literals."""

    def setUp(self):
        """Create interpreter."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)

    def test_split_simple(self):
        """Test simple colon split."""
        result = self.interp._split_statements("a = 1: b = 2")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].strip(), "a = 1")
        self.assertEqual(result[1].strip(), "b = 2")

    def test_split_with_string_colon(self):
        """Test that colon inside string is not split."""
        result = self.interp._split_statements('PRINT "a:b"')
        self.assertEqual(len(result), 1)
        self.assertIn('"a:b"', result[0])

    def test_split_multiple_strings(self):
        """Test multiple strings with colons."""
        result = self.interp._split_statements('a$ = "x:y": b$ = "1:2"')
        self.assertEqual(len(result), 2)


class TestGameLoop(unittest.TestCase):
    """Test game loop execution."""

    def setUp(self):
        """Create interpreter."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)

    def test_simple_loop_executes(self):
        """Test that a simple loop executes multiple iterations."""
        self.interp.reset([
            "SCREEN 13",
            "x = 0",
            "DO WHILE x < 10",
            "x = x + 1",
            "LOOP"
        ])

        # Execute until done
        max_iterations = 1000
        iterations = 0
        while self.interp.running and iterations < max_iterations:
            self.interp.step()
            iterations += 1

        self.assertEqual(self.interp.variables.get("X"), 10)

    def test_nested_loops(self):
        """Test nested loops."""
        self.interp.reset([
            "sum = 0",
            "FOR i = 1 TO 3",
            "FOR j = 1 TO 3",
            "sum = sum + 1",
            "NEXT j",
            "NEXT i"
        ])

        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()

        self.assertEqual(self.interp.variables.get("SUM"), 9)

    def test_rendering_updates(self):
        """Test that rendering surface is updated."""
        self.interp.reset([
            "SCREEN 13",
            "PSET (50, 50), 15",
            "PSET (100, 100), 4"
        ])

        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()

        # Verify pixels
        color1 = self.interp.surface.get_at((50, 50))[:3]
        color2 = self.interp.surface.get_at((100, 100))[:3]

        self.assertEqual(color1, (255, 255, 255))  # White
        self.assertEqual(color2, (170, 0, 0))  # Red


class TestRenderingPerformance(unittest.TestCase):
    """Test rendering and performance."""

    def setUp(self):
        """Create interpreter."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)

    def test_dirty_flag_set_on_draw(self):
        """Test that dirty flag is set when drawing."""
        self.interp.reset(["SCREEN 13"])
        self.interp.step()
        self.interp._dirty = False  # Reset

        self.interp.reset(["SCREEN 13", "PSET (50, 50), 15"])
        self.interp.step()
        self.interp.step()

        self.assertTrue(self.interp._dirty)

    def test_expression_caching(self):
        """Test that expressions are cached."""
        _expr_cache.clear()

        self.interp.eval_expr("x + 5")
        self.interp.eval_expr("x + 5")  # Same expression

        # Should be cached
        self.assertIn("x + 5", _expr_cache)


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)
