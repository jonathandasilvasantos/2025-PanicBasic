#!/usr/bin/env python3
"""
Test that simulates the WetSpot game loop structure to verify
the timing loop fix works correctly.
"""
import pytest
import sys
import os

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


class TestWetSpotGameLoop:
    """Tests simulating WetSpot game structure."""

    def test_wetspot_main_menu_pattern(self, interpreter):
        """Test the MainMenu DO...LOOP pattern from WetSpot.

        From lines 832-837:
        DO
          k$ = INKEY$
          IF k$ = "1" THEN NumPlayer = 1: EXIT DO
          IF k$ = "2" THEN NumPlayer = 2: EXIT DO
          IF k$ = CHR$(27) THEN NumPlayer = 0: EXIT DO
        LOOP
        """
        code = [
            'NumPlayer = -1',
            'iterations = 0',
            'DO',
            '  iterations = iterations + 1',
            '  IF iterations >= 3 THEN NumPlayer = 1: EXIT DO',
            'LOOP',
            'result = NumPlayer',
        ]
        interpreter.reset(code)
        interpreter.run_with_simulated_input(max_steps=200)

        # Should exit with NumPlayer = 1 after 3 iterations
        assert interpreter.variables.get('NUMPLAYER') == 1
        assert interpreter.variables.get('ITERATIONS') == 3

    def test_wetspot_timing_loop_pattern(self, interpreter):
        """Test the timing loop pattern from WetSpot (line 1600).

        Original: DO: LOOP WHILE TIMER < StartT! + .001

        This pattern uses a single-line DO: LOOP to create a brief delay.
        """
        code = [
            'iterations = 0',
            'target = 5',
            'DO: iterations = iterations + 1: LOOP WHILE iterations < target',
            'result = iterations',
        ]
        interpreter.reset(code)
        interpreter.run_with_simulated_input(max_steps=100)

        # Should loop until iterations reaches target
        assert interpreter.variables.get('ITERATIONS') == 5

    def test_wetspot_game_loop_structure(self, interpreter):
        """Test the nested loop structure from WetSpot PlayGame (lines 1294-1601).

        Simplified version with nested DO loops and single-line timing loop.
        """
        code = [
            'level = 0',
            'total_ticks = 0',
            'DO',
            '  level = level + 1',
            '  ticks = 0',
            '  DO',
            '    ticks = ticks + 1',
            '    total_ticks = total_ticks + 1',
            '    delay_count = 0',
            '    DO: delay_count = delay_count + 1: LOOP WHILE delay_count < 2',  # Timing loop
            '    IF ticks >= 3 THEN EXIT DO',
            '  LOOP',
            '  IF level >= 2 THEN EXIT DO',
            'LOOP',
            'result = total_ticks',
        ]
        interpreter.reset(code)
        interpreter.run_with_simulated_input(max_steps=500)

        # 2 levels * 3 ticks each = 6 total ticks
        assert interpreter.variables.get('LEVEL') == 2
        assert interpreter.variables.get('TOTAL_TICKS') == 6
        assert interpreter.variables.get('DELAY_COUNT') == 2  # Last delay loop ran twice

    def test_select_case_in_game_loop(self, interpreter):
        """Test SELECT CASE handling similar to WetSpot input handling.

        From lines 1339-1413:
        SELECT CASE k$
        CASE "2": Player(1).dir = 1...
        CASE "6": Player(1).dir = 2...
        ...
        END SELECT
        """
        code = [
            'key$ = "2"',
            'direction = 0',
            'SELECT CASE key$',
            'CASE "2"',
            '  direction = 1',
            'CASE "6"',
            '  direction = 2',
            'CASE "8"',
            '  direction = 3',
            'CASE ELSE',
            '  direction = 0',
            'END SELECT',
            'result = direction',
        ]
        interpreter.reset(code)
        interpreter.run_with_simulated_input(max_steps=100)

        assert interpreter.variables.get('DIRECTION') == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
