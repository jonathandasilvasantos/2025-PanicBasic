"""
Unit tests for worms.bas game functionality.
Tests the interpreter's handling of game-specific patterns.
"""
import unittest
import sys
import os

# Set SDL to use dummy video driver for headless testing
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
from interpreter import BasicInterpreter, convert_basic_expr, _split_args

class TestWormsGamePatterns(unittest.TestCase):
    """Test patterns used in worms.bas"""

    @classmethod
    def setUpClass(cls):
        """Initialize pygame for tests"""
        pygame.init()
        pygame.font.init()
        # Create a display surface for tests
        cls.screen = pygame.display.set_mode((320, 200))

    @classmethod
    def tearDownClass(cls):
        """Clean up pygame"""
        pygame.quit()

    def setUp(self):
        """Set up interpreter for each test"""
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 320, 200)

    def run_program(self, max_steps=100):
        """Helper to run program for given number of steps"""
        steps = 0
        while self.interp.running and steps < max_steps:
            self.interp.step_line()
            steps += 1
        return steps

    def test_const_declaration(self):
        """Test CONST declarations work correctly"""
        program = [
            "CONST GRIDW = 20",
            "CONST GRIDH = 12",
            "x = GRIDW * 2",
            "y = GRIDH + 5"
        ]
        self.interp.reset(program)
        self.run_program(100)
        self.assertEqual(self.interp.constants.get("GRIDW"), 20)
        self.assertEqual(self.interp.constants.get("GRIDH"), 12)
        self.assertEqual(self.interp.variables.get("X"), 40)
        self.assertEqual(self.interp.variables.get("Y"), 17)

    def test_array_declaration(self):
        """Test DIM array declarations"""
        program = [
            "CONST MAXLEN = 100",
            "DIM snakeX(MAXLEN)",
            "DIM snakeY(MAXLEN)",
            "snakeX(0) = 10",
            "snakeX(50) = 25",
            "snakeY(99) = 5"
        ]
        self.interp.reset(program)
        self.run_program(100)
        self.assertEqual(self.interp.variables["SNAKEX"][0], 10)
        self.assertEqual(self.interp.variables["SNAKEX"][50], 25)
        self.assertEqual(self.interp.variables["SNAKEY"][99], 5)

    def test_for_loop_array_init(self):
        """Test FOR loop initializing arrays (snake body init pattern)"""
        program = [
            "DIM snakeX(10)",
            "DIM snakeY(10)",
            "headX = 5",
            "headY = 6",
            "snakeLen = 3",
            "FOR i = 0 TO snakeLen - 1",
            "    snakeX(i) = headX - i",
            "    snakeY(i) = headY",
            "NEXT i"
        ]
        self.interp.reset(program)
        self.run_program(200)
        self.assertEqual(self.interp.variables["SNAKEX"][0], 5)
        self.assertEqual(self.interp.variables["SNAKEX"][1], 4)
        self.assertEqual(self.interp.variables["SNAKEX"][2], 3)
        self.assertEqual(self.interp.variables["SNAKEY"][0], 6)

    def test_reverse_for_loop(self):
        """Test FOR loop with STEP -1 (snake body shift pattern)"""
        program = [
            "DIM arr(5)",
            "arr(0) = 10",
            "arr(1) = 20",
            "arr(2) = 30",
            "FOR i = 4 TO 1 STEP -1",
            "    arr(i) = arr(i - 1)",
            "NEXT i",
            "arr(0) = 99"
        ]
        self.interp.reset(program)
        self.run_program(200)
        self.assertEqual(self.interp.variables["ARR"][0], 99)
        self.assertEqual(self.interp.variables["ARR"][1], 10)
        self.assertEqual(self.interp.variables["ARR"][2], 20)
        self.assertEqual(self.interp.variables["ARR"][3], 30)

    def test_collision_detection_pattern(self):
        """Test collision detection logic (self-collision)"""
        program = [
            "DIM snakeX(5)",
            "DIM snakeY(5)",
            "snakeX(0) = 5: snakeY(0) = 5",
            "snakeX(1) = 4: snakeY(1) = 5",
            "snakeX(2) = 3: snakeY(2) = 5",
            "snakeLen = 3",
            "newX = 4: newY = 5",
            "collision = 0",
            "FOR i = 0 TO snakeLen - 1",
            "    IF snakeX(i) = newX AND snakeY(i) = newY THEN",
            "        collision = 1",
            "    END IF",
            "NEXT i"
        ]
        self.interp.reset(program)
        self.run_program(200)
        self.assertEqual(self.interp.variables["COLLISION"], 1)

    def test_wall_collision(self):
        """Test wall boundary collision logic"""
        program = [
            "CONST GRIDW = 20",
            "CONST GRIDH = 12",
            "newX = -1",
            "newY = 5",
            "gameOver = 0",
            "IF newX < 0 OR newX >= GRIDW OR newY < 0 OR newY >= GRIDH THEN",
            "    gameOver = 1",
            "END IF"
        ]
        self.interp.reset(program)
        self.run_program(100)
        self.assertEqual(self.interp.variables["GAMEOVER"], 1)

    def test_food_collision(self):
        """Test food eating logic"""
        program = [
            "newX = 10",
            "newY = 7",
            "foodX = 10",
            "foodY = 7",
            "score = 0",
            "snakeLen = 3",
            "IF newX = foodX AND newY = foodY THEN",
            "    snakeLen = snakeLen + 1",
            "    score = score + 10",
            "END IF"
        ]
        self.interp.reset(program)
        self.run_program(100)
        self.assertEqual(self.interp.variables["SNAKELEN"], 4)
        self.assertEqual(self.interp.variables["SCORE"], 10)

    def test_gosub_return(self):
        """Test GOSUB/RETURN pattern used for game subroutines"""
        program = [
            "result = 0",
            "GOSUB Calculate",
            "GOTO Done",
            "Calculate:",
            "result = 42",
            "RETURN",
            "Done:",
            "final = result"
        ]
        self.interp.reset(program)
        self.run_program(100)
        self.assertEqual(self.interp.variables["FINAL"], 42)

    def test_speed_adjustment(self):
        """Test speed decrease pattern"""
        program = [
            "speed = 0.15",
            "IF speed > 0.05 THEN speed = speed - 0.005"
        ]
        self.interp.reset(program)
        self.run_program(50)
        self.assertAlmostEqual(self.interp.variables["SPEED"], 0.145, places=5)

    def test_int_rnd_pattern(self):
        """Test INT(RND * n) pattern for random positions"""
        program = [
            "RANDOMIZE 12345",
            "CONST GRIDW = 20",
            "foodX = INT(RND * GRIDW)"
        ]
        self.interp.reset(program)
        self.run_program(50)
        food_x = self.interp.variables["FOODX"]
        self.assertGreaterEqual(food_x, 0)
        self.assertLess(food_x, 20)

    def test_chr_comparison(self):
        """Test CHR$ comparison for key handling"""
        # This tests the expression conversion
        expr = 'k$ = CHR$(27)'
        converted = convert_basic_expr(expr, set())
        self.assertIn("CHR(27)", converted)

    def test_multiline_if_collision(self):
        """Test multi-line IF for boundary check"""
        program = [
            "x = 25",
            "CONST GRIDW = 20",
            "result = 0",
            "IF x < 0 OR x >= GRIDW THEN",
            "    result = 1",
            "END IF"
        ]
        self.interp.reset(program)
        self.run_program(100)
        self.assertEqual(self.interp.variables["RESULT"], 1)


class TestExpressionPatterns(unittest.TestCase):
    """Test expression conversion patterns used in worms.bas"""

    def test_grid_calculation(self):
        """Test grid position calculation expressions"""
        expr = "OFFSETX + snakeX(i) * CELLSIZE"
        converted = convert_basic_expr(expr, set())
        self.assertIn("OFFSETX", converted)
        self.assertIn("CELLSIZE", converted)

    def test_division_expression(self):
        """Test division in expressions"""
        expr = "GRIDW / 2"
        converted = convert_basic_expr(expr, set())
        self.assertIn("/", converted)

    def test_compound_condition(self):
        """Test compound OR condition"""
        expr = "newX < 0 OR newX >= GRIDW"
        converted = convert_basic_expr(expr, set())
        self.assertIn(" or ", converted)

    def test_and_condition(self):
        """Test AND condition for collision"""
        expr = "snakeX(i) = newX AND snakeY(i) = newY"
        converted = convert_basic_expr(expr, set())
        self.assertIn(" and ", converted)


class TestSplitArgs(unittest.TestCase):
    """Test argument splitting used in various statements"""

    def test_simple_args(self):
        """Test simple comma-separated args"""
        result = _split_args("10, 20, 30")
        self.assertEqual(result, ["10", "20", "30"])

    def test_nested_parens(self):
        """Test args with nested parentheses"""
        result = _split_args("snakeX(i), snakeY(i)")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].strip(), "snakeX(i)")

    def test_expression_args(self):
        """Test args with expressions"""
        result = _split_args("OFFSETX + x * 15, OFFSETY + y * 15")
        self.assertEqual(len(result), 2)


class TestGameLoop(unittest.TestCase):
    """Test game loop patterns"""

    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.font.init()
        cls.screen = pygame.display.set_mode((320, 200))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 320, 200)

    def run_program(self, max_steps=100):
        """Helper to run program for given number of steps"""
        steps = 0
        while self.interp.running and steps < max_steps:
            self.interp.step_line()
            steps += 1
        return steps

    def test_timer_pattern(self):
        """Test TIMER usage for movement timing"""
        program = [
            "lastMove = TIMER",
            "speed = 0.1",
            "diff = TIMER - lastMove"
        ]
        self.interp.reset(program)
        self.run_program(50)
        self.assertIn("LASTMOVE", self.interp.variables)
        self.assertIn("DIFF", self.interp.variables)

    def test_direction_change(self):
        """Test direction change logic"""
        program = [
            "dirX = 1",
            "dirY = 0",
            "' Simulate pressing up when not going down",
            "IF dirY <> 1 THEN",
            "    dirX = 0",
            "    dirY = -1",
            "END IF"
        ]
        self.interp.reset(program)
        self.run_program(100)
        self.assertEqual(self.interp.variables["DIRX"], 0)
        self.assertEqual(self.interp.variables["DIRY"], -1)

    def test_prevent_reverse(self):
        """Test preventing snake from reversing into itself"""
        program = [
            "dirX = 1",
            "dirY = 0",
            "' Try to go left while going right - should be blocked",
            "IF dirX <> 1 THEN",
            "    dirX = -1",
            "    dirY = 0",
            "END IF"
        ]
        self.interp.reset(program)
        self.run_program(100)
        # Direction should NOT change because we're already going right
        self.assertEqual(self.interp.variables["DIRX"], 1)
        self.assertEqual(self.interp.variables["DIRY"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
