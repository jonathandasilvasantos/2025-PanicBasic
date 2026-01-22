#!/usr/bin/env python3
"""
Diagnostic tests for single-line DO: LOOP WHILE construct.
Tests the specific issue where DO: LOOP WHILE on a single line may not loop correctly.
"""
import pytest
import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up headless pygame
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
pygame.init()
pygame.display.set_mode((800, 600))

from interpreter import BasicInterpreter, FONT_SIZE


@pytest.fixture
def interpreter():
    """Create a BasicInterpreter instance for testing."""
    font = pygame.font.Font(None, FONT_SIZE)
    interp = BasicInterpreter(font, 800, 600)
    yield interp


class TestSingleLineDoLoop:
    """Tests for single-line DO: LOOP WHILE construct."""

    def test_multiline_do_loop_while(self, interpreter):
        """Test traditional multi-line DO...LOOP WHILE works correctly."""
        code = [
            'counter = 0',
            'DO',
            '  counter = counter + 1',
            'LOOP WHILE counter < 5',
            'result = counter',
        ]
        interpreter.reset(code)
        interpreter.run_with_simulated_input(max_steps=200)

        # Counter should reach 5 before exiting
        assert interpreter.variables.get('COUNTER') == 5
        assert interpreter.variables.get('RESULT') == 5

    def test_single_line_do_loop_while_counter(self, interpreter):
        """Test single-line DO: LOOP WHILE counter < N construct."""
        code = [
            'counter = 0',
            'DO: counter = counter + 1: LOOP WHILE counter < 5',
            'result = counter',
        ]
        interpreter.reset(code)
        interpreter.run_with_simulated_input(max_steps=200)

        # Counter should reach 5 before exiting
        # This tests if the single-line construct works correctly
        assert interpreter.variables.get('COUNTER') == 5, \
            f"Expected counter=5, got {interpreter.variables.get('COUNTER')}"

    def test_single_line_do_loop_only(self, interpreter):
        """Test simplest single-line DO: LOOP WHILE construct."""
        code = [
            'x = 0',
            'DO: x = x + 1: LOOP WHILE x < 3',
            'finalx = x',
        ]
        interpreter.reset(code)
        interpreter.run_with_simulated_input(max_steps=100)

        # x should reach 3
        assert interpreter.variables.get('X') == 3, \
            f"Expected x=3, got {interpreter.variables.get('X')}"
        assert interpreter.variables.get('FINALX') == 3

    def test_empty_single_line_do_loop(self, interpreter):
        """Test DO: LOOP WHILE with no body (busy wait).

        This is similar to: DO: LOOP WHILE TIMER < StartT! + .001
        from WetSpot game (line 1600).
        """
        code = [
            'loopcount = 0',
            'maxi = 3',
            'DO: loopcount = loopcount + 1: LOOP WHILE loopcount < maxi',
            'finalcount = loopcount',
        ]
        interpreter.reset(code)
        interpreter.run_with_simulated_input(max_steps=100)

        # loopcount should be 3
        assert interpreter.variables.get('LOOPCOUNT') == 3, \
            f"Expected loopcount=3, got {interpreter.variables.get('LOOPCOUNT')}"

    def test_nested_do_loops(self, interpreter):
        """Test that nested DO loops still work when using single-line inner loop."""
        code = [
            'outer = 0',
            'total = 0',
            'DO',
            '  outer = outer + 1',
            '  inner = 0',
            '  DO: inner = inner + 1: total = total + 1: LOOP WHILE inner < 3',
            'LOOP WHILE outer < 2',
            'result = total',
        ]
        interpreter.reset(code)
        interpreter.run_with_simulated_input(max_steps=200)

        # outer should be 2, each outer iteration runs inner 3 times
        # total should be 6 (2 outer iterations * 3 inner iterations)
        assert interpreter.variables.get('OUTER') == 2
        assert interpreter.variables.get('TOTAL') == 6

    def test_game_timing_loop_pattern(self, interpreter):
        """Test pattern similar to WetSpot's timing loop:
        DO: LOOP WHILE TIMER < StartT! + .001

        This pattern uses DO: LOOP WHILE with a condition that starts true
        and eventually becomes false.
        """
        code = [
            'iterations = 0',
            'flag = 1',  # Start true
            'DO: iterations = iterations + 1: IF iterations >= 5 THEN flag = 0: LOOP WHILE flag = 1',
            'result = iterations',
        ]
        interpreter.reset(code)
        interpreter.run_with_simulated_input(max_steps=200)

        # Should loop 5 times
        assert interpreter.variables.get('ITERATIONS') == 5, \
            f"Expected iterations=5, got {interpreter.variables.get('ITERATIONS')}"


class TestDoLoopWithEmptyBody:
    """Test DO: LOOP constructs that are essentially busy-waits."""

    def test_do_loop_while_immediate_exit(self, interpreter):
        """Test DO: LOOP WHILE that exits immediately when condition is false."""
        code = [
            'x = 5',  # Condition starts false
            'DO: x = x + 1: LOOP WHILE x < 5',  # x >= 5, should exit after one iteration
            'result = x',
        ]
        interpreter.reset(code)
        interpreter.run_with_simulated_input(max_steps=50)

        # DO executes once, then LOOP WHILE checks condition (5 < 5 is false) and exits
        # Actually, x becomes 6 after one iteration, then check 6 < 5 is false
        assert interpreter.variables.get('X') == 6, \
            f"Expected x=6, got {interpreter.variables.get('X')}"


class TestKeywordNotLabel:
    """Tests to ensure BASIC keywords aren't parsed as labels."""

    def test_do_not_parsed_as_label(self, interpreter):
        """Test that DO: is not parsed as label 'DO'."""
        code = [
            'x = 0',
            'DO: x = x + 1: LOOP WHILE x < 3',
            'result = x',
        ]
        interpreter.reset(code)
        interpreter.run_with_simulated_input(max_steps=100)

        # If DO: was wrongly parsed as label, x would only reach 1
        assert interpreter.variables.get('X') == 3
        # Verify 'DO' is not in labels
        assert 'DO' not in interpreter.labels

    def test_for_not_parsed_as_label(self, interpreter):
        """Test that FOR: style patterns work correctly."""
        # This tests that FOR isn't confused for a label
        code = [
            'sum = 0',
            'FOR i = 1 TO 3: sum = sum + i: NEXT i',
            'result = sum',
        ]
        interpreter.reset(code)
        interpreter.run_with_simulated_input(max_steps=100)

        assert interpreter.variables.get('SUM') == 6
        assert 'FOR' not in interpreter.labels

    def test_actual_label_still_works(self, interpreter):
        """Test that actual labels still work correctly."""
        code = [
            'x = 0',
            'GOTO skip',
            'x = 999',
            'skip:',
            'x = 42',
        ]
        interpreter.reset(code)
        interpreter.run_with_simulated_input(max_steps=100)

        # Should skip to 'skip:' label and set x to 42
        assert interpreter.variables.get('X') == 42
        assert 'SKIP' in interpreter.labels


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
