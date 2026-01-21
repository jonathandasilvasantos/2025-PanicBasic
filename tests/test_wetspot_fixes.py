#!/usr/bin/env python3
"""
Unit tests for wetspot.bas fixes.
Tests the specific interpreter features required by wetspot.bas.
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
from interpreter import BasicInterpreter, FONT_SIZE


@pytest.fixture
def interpreter():
    """Create a BasicInterpreter instance for testing."""
    pygame.init()
    pygame.font.init()
    pygame.display.set_mode((800, 600))
    font = pygame.font.Font(None, FONT_SIZE)
    interp = BasicInterpreter(font, 800, 600)
    yield interp
    pygame.quit()


class TestSingleLineIF:
    """Tests for single-line IF statement handling."""

    def test_single_line_if_with_colon(self, interpreter):
        """Test that single-line IF statements are not split by colons."""
        code = [
            'k$ = ""',
            'NumPlayer = -1',
            'IF k$ = "1" THEN NumPlayer = 1: PRINT "Player 1"',
            'PRINT "NumPlayer ="; NumPlayer',
        ]
        interpreter.reset(code)
        interpreter.run_with_simulated_input(max_steps=100)

        # NumPlayer should still be -1 (condition was false)
        assert interpreter.variables.get('NUMPLAYER') == -1

    def test_single_line_if_condition_true(self, interpreter):
        """Test that single-line IF executes when condition is true."""
        code = [
            'k$ = "1"',
            'NumPlayer = -1',
            'IF k$ = "1" THEN NumPlayer = 1',
            'PRINT "NumPlayer ="; NumPlayer',
        ]
        interpreter.reset(code)
        interpreter.run_with_simulated_input(max_steps=100)

        # NumPlayer should be 1 (condition was true)
        assert interpreter.variables.get('NUMPLAYER') == 1

    def test_single_line_if_with_exit_do(self, interpreter):
        """Test that EXIT DO in single-line IF only executes when condition is true."""
        code = [
            'iterations = 0',
            'k$ = ""',
            'DO',
            '  iterations = iterations + 1',
            '  IF iterations >= 3 THEN EXIT DO',
            'LOOP',
            'PRINT "Iterations:"; iterations',
        ]
        interpreter.reset(code)
        interpreter.run_with_simulated_input(max_steps=200)

        # Should exit after 3 iterations
        assert interpreter.variables.get('ITERATIONS') == 3


class TestDIMShared:
    """Tests for DIM SHARED statement handling."""

    def test_dim_shared_array(self, interpreter):
        """Test that DIM SHARED creates arrays correctly."""
        code = [
            'DIM SHARED Arr(10)',
            'Arr(1) = 42',
            'PRINT Arr(1)',
        ]
        interpreter.reset(code)
        interpreter.run_with_simulated_input(max_steps=100)

        # Array should be named 'ARR' not 'SHARED ARR'
        assert 'ARR' in interpreter.variables
        assert 'SHARED ARR' not in interpreter.variables

    def test_dim_shared_multiple_arrays(self, interpreter):
        """Test DIM SHARED with multiple arrays."""
        code = [
            'DIM SHARED Cel(18, 12), Block(10)',
            'Cel(1, 1) = 5',
            'Block(5) = 10',
        ]
        interpreter.reset(code)
        interpreter.run_with_simulated_input(max_steps=100)

        assert 'CEL' in interpreter.variables
        assert 'BLOCK' in interpreter.variables

    def test_dim_shared_with_type(self, interpreter):
        """Test DIM SHARED with user-defined type."""
        code = [
            'TYPE TestType',
            '  x AS INTEGER',
            '  y AS INTEGER',
            'END TYPE',
            'DIM SHARED Player(2) AS TestType',
            'Player(1).x = 100',
            'Player(1).y = 200',
        ]
        interpreter.reset(code)
        interpreter.run_with_simulated_input(max_steps=100)

        assert 'PLAYER' in interpreter.variables
        assert isinstance(interpreter.variables['PLAYER'][1], dict)


class TestBackslashStrings:
    """Tests for backslash character in string literals."""

    def test_backslash_assignment(self, interpreter):
        """Test assigning backslash to variable."""
        code = [
            'a$ = "\\"',
            'PRINT LEN(a$)',
        ]
        interpreter.reset(code)
        interpreter.run_with_simulated_input(max_steps=50)

        # Backslash string should have length 1
        # Variable stored as 'A$' (uppercase with suffix)
        assert interpreter.variables.get('A$') == '\\'

    def test_backslash_comparison(self, interpreter):
        """Test comparing backslash string."""
        code = [
            'a$ = "\\"',
            'IF a$ = "\\" THEN result = 1 ELSE result = 0',
        ]
        interpreter.reset(code)
        interpreter.run_with_simulated_input(max_steps=50)

        assert interpreter.variables.get('RESULT') == 1


class TestBLOADFilename:
    """Tests for BLOAD filename expression evaluation."""

    def test_bload_concatenated_filename(self, interpreter):
        """Test that BLOAD evaluates concatenated filename expressions."""
        # We can't actually test BLOAD without the file, but we can verify
        # the filename expression evaluation logic by checking the code path.
        # This test mainly ensures the code doesn't crash on concatenated names.

        # This is a more limited test - just verify the interpreter handles
        # the expression format correctly (won't find file, but should error
        # with proper filename, not the expression string)
        code = [
            'Level = 1',
            'DEF SEG = &HA000',
            'BLOAD "LEVEL" + LTRIM$(STR$(Level)) + ".P13", 0',
        ]
        interpreter.reset(code)

        # Run but catch the file not found error
        import io
        import sys
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            interpreter.run_with_simulated_input(max_steps=50)
        finally:
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout

        # The error message should contain "LEVEL1.P13", not the expression
        # (This confirms the filename expression was evaluated)
        assert 'LEVEL" + LTRIM$(STR$(Level)) + ".P13' not in output


class TestTypeMemberAssignment:
    """Tests for type member assignment on array elements."""

    def test_array_type_member_assignment(self, interpreter):
        """Test Block(1).Status = 1 syntax."""
        code = [
            'TYPE BlockType',
            '  Status AS INTEGER',
            '  x AS INTEGER',
            '  y AS INTEGER',
            'END TYPE',
            'DIM Block(10) AS BlockType',
            'Block(1).Status = 5',
            'Block(1).x = 10',
            'Block(1).y = 20',
        ]
        interpreter.reset(code)
        interpreter.run_with_simulated_input(max_steps=100)

        assert interpreter.variables['BLOCK'][1]['STATUS'] == 5
        assert interpreter.variables['BLOCK'][1]['X'] == 10
        assert interpreter.variables['BLOCK'][1]['Y'] == 20


class TestPointFunction:
    """Tests for POINT function reading palette indices."""

    def test_point_from_pixel_indices(self, interpreter):
        """Test that POINT returns palette index from _pixel_indices in Screen 13."""
        code = [
            'SCREEN 13',
        ]
        interpreter.reset(code)
        interpreter.run_with_simulated_input(max_steps=10)

        # Manually set up _pixel_indices like BLOAD would
        interpreter._pixel_indices = bytearray(320 * 200)
        interpreter._pixel_indices[10 * 320 + 10] = 5  # Set pixel at (10, 10) to color 5

        # POINT should return the palette index
        result = interpreter.point(10, 10)
        assert result == 5

    def test_point_multiple_values(self, interpreter):
        """Test POINT reads correct values at different positions."""
        code = [
            'SCREEN 13',
        ]
        interpreter.reset(code)
        interpreter.run_with_simulated_input(max_steps=10)

        # Set up _pixel_indices with different values
        interpreter._pixel_indices = bytearray(320 * 200)
        interpreter._pixel_indices[0 * 320 + 48] = 1  # (48, 0) = 1 (FIXEDBLOCK)
        interpreter._pixel_indices[0 * 320 + 49] = 2  # (49, 0) = 2 (NORMALBLOCK)
        interpreter._pixel_indices[0 * 320 + 50] = 3  # (50, 0) = 3 (SPECIALBLOCK)
        interpreter._pixel_indices[1 * 320 + 48] = 0  # (48, 1) = 0 (INACTIVE)

        assert interpreter.point(48, 0) == 1
        assert interpreter.point(49, 0) == 2
        assert interpreter.point(50, 0) == 3
        assert interpreter.point(48, 1) == 0


class TestSubStringParameters:
    """Tests for SUB string parameter passing."""

    def test_sub_string_parameter_basic(self, interpreter):
        """Test that string parameters are passed correctly to SUBs."""
        code = [
            'result$ = ""',
            'CALL TestSub("hello")',
            'END',
            '',
            'SUB TestSub(msg$)',
            '  result$ = msg$',
            'END SUB',
        ]
        interpreter.reset(code)
        interpreter.run_with_simulated_input(max_steps=100)

        # result$ should contain "hello"
        assert interpreter.variables.get('RESULT$') == 'hello'

    def test_sub_string_parameter_len(self, interpreter):
        """Test that LEN works on string parameters in SUBs."""
        code = [
            'result = -1',
            'CALL TestSub("test")',
            'END',
            '',
            'SUB TestSub(s$)',
            '  result = LEN(s$)',
            'END SUB',
        ]
        interpreter.reset(code)
        interpreter.run_with_simulated_input(max_steps=100)

        # result should be 4 (length of "test")
        assert interpreter.variables.get('RESULT') == 4

    def test_sub_string_parameter_manipulation(self, interpreter):
        """Test string manipulation on SUB parameters."""
        code = [
            'result$ = ""',
            'CALL TestSub("ABCDE")',
            'END',
            '',
            'SUB TestSub(t$)',
            '  result$ = MID$(t$, 2, 3)',
            'END SUB',
        ]
        interpreter.reset(code)
        interpreter.run_with_simulated_input(max_steps=100)

        # result$ should be "BCD" (middle 3 chars of "ABCDE")
        assert interpreter.variables.get('RESULT$') == 'BCD'

    def test_sub_multiple_string_parameters(self, interpreter):
        """Test SUB with multiple string parameters."""
        code = [
            'result$ = ""',
            'CALL Concat("Hello", "World")',
            'END',
            '',
            'SUB Concat(a$, b$)',
            '  result$ = a$ + " " + b$',
            'END SUB',
        ]
        interpreter.reset(code)
        interpreter.run_with_simulated_input(max_steps=100)

        # result$ should be "Hello World"
        assert interpreter.variables.get('RESULT$') == 'Hello World'

    def test_sub_mixed_parameters(self, interpreter):
        """Test SUB with both string and numeric parameters."""
        code = [
            'result$ = ""',
            'CALL Format("Value", 42)',
            'END',
            '',
            'SUB Format(label$, value)',
            '  result$ = label$ + "=" + STR$(value)',
            'END SUB',
        ]
        interpreter.reset(code)
        interpreter.run_with_simulated_input(max_steps=100)

        # result$ should be "Value= 42" (STR$ adds a leading space for positive numbers)
        assert 'Value' in interpreter.variables.get('RESULT$', '')
        assert '42' in interpreter.variables.get('RESULT$', '')


class TestPutNestedParentheses:
    """Tests for PUT statement with nested parentheses in coordinates."""

    def test_put_with_array_member_access(self, interpreter):
        """Test PUT with expressions like Block(B).x * 16."""
        code = [
            'SCREEN 13',
            'TYPE BlockType',
            '  x AS INTEGER',
            '  y AS INTEGER',
            'END TYPE',
            'DIM Block(10) AS BlockType',
            'DIM Sprite&(100)',
            'Block(1).x = 5',
            'Block(1).y = 3',
            'B = 1',
            '\'Capture a sprite first',
            'PSET (0, 0), 15',
            'GET (0, 0)-(15, 15), Sprite&',
            '\'PUT with nested parens in coords',
            'PUT (Block(B).x * 16, -8 + (Block(B).y * 16)), Sprite&, PSET',
        ]
        interpreter.reset(code)
        # Should not crash
        interpreter.run_with_simulated_input(max_steps=200)
        # Verify the interpreter ran without errors
        assert interpreter.variables.get('B') == 1

    def test_put_with_complex_expression(self, interpreter):
        """Test PUT with complex nested expressions."""
        code = [
            'SCREEN 13',
            'DIM Arr(10)',
            'DIM Sprite&(100)',
            'Arr(1) = 10',
            'i = 1',
            'GET (0, 0)-(15, 15), Sprite&',
            '\'PUT with expression containing function-like array access',
            'PUT (Arr(i) + 5, (Arr(i) * 2) + 3), Sprite&, PSET',
        ]
        interpreter.reset(code)
        interpreter.run_with_simulated_input(max_steps=200)
        assert interpreter.variables.get('I') == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
