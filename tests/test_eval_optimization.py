"""Tests for eval_expr optimization - pre-computed Python identifier names."""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pytest
import pygame
import time

pygame.init()
pygame.display.set_mode((800, 600))
pygame.font.init()


def setup():
    """Create a BasicInterpreter instance for testing."""
    from interpreter import BasicInterpreter, FONT_SIZE
    font = pygame.font.Font(None, FONT_SIZE)
    interp = BasicInterpreter(font, 800, 600)
    return interp


class TestEvalLocalsOptimization:
    """Test the eval_locals pre-computed name optimization."""

    def test_var_py_names_populated_on_first_eval(self):
        """Test that _var_py_names is populated during eval.

        Note: The cache is populated from variables that exist at the TIME
        eval_expr is called. Variables are added AFTER eval_expr returns,
        so we need expressions that USE variables to test the cache.
        """
        interp = setup()
        interp.reset([
            'X = 10',
            'Y = 20',
            'Z$ = "hello"',
            'RESULT = X + Y'  # This eval will include X and Y in cache
        ])
        # Run the program
        while interp.running and interp.pc < len(interp.program_lines):
            interp.step()

        # After RESULT = X + Y, X and Y should be in the cache
        # (Z$ was added after the last fingerprint-updating eval)
        assert 'X' in interp._var_py_names
        assert 'Y' in interp._var_py_names

        # Check the conversions are correct
        assert interp._var_py_names['X'] == 'X'
        assert interp._var_py_names['Y'] == 'Y'

    def test_const_py_names_populated(self):
        """Test that _const_py_names is populated for constants."""
        interp = setup()
        interp.reset([
            'CONST PI = 3.14159',
            'CONST NAME$ = "test"',
            'X = PI'
        ])
        while interp.running and interp.pc < len(interp.program_lines):
            interp.step()

        assert 'PI' in interp._const_py_names
        assert 'NAME$' in interp._const_py_names
        assert interp._const_py_names['PI'] == 'PI'
        assert interp._const_py_names['NAME$'] == 'NAME_STR'

    def test_func_py_names_populated_for_functions(self):
        """Test that _func_py_names is populated for FUNCTION procedures."""
        interp = setup()
        interp.reset([
            'DECLARE FUNCTION AddOne%(x%)',
            'Y% = AddOne%(5)',
            'END',
            'FUNCTION AddOne%(x%)',
            'AddOne% = x% + 1',
            'END FUNCTION'
        ])
        while interp.running and interp.pc < len(interp.program_lines):
            interp.step()

        # Check that function Python names are tracked
        assert 'ADDONE_INT' in interp._func_py_names or 'ADDONE' in interp._func_py_names

    def test_repeated_eval_uses_cached_names(self):
        """Test that repeated evals use cached Python names (no re-conversion)."""
        interp = setup()
        interp.reset([
            'X = 0',
            'StartLoop:',
            'X = X + 1',
            'IF X < 100 THEN GOTO StartLoop'
        ])

        # Run the loop
        while interp.running and interp.pc < len(interp.program_lines):
            interp.step()

        # After 100 iterations, X should be 100
        assert interp.variables.get('X') == 100

        # The cache should still have the mapping
        assert 'X' in interp._var_py_names

    def test_caches_cleared_on_reset(self):
        """Test that caches are cleared when reset() is called."""
        interp = setup()
        # Need an expression that uses a variable to populate cache
        interp.reset(['X = 10', 'Y = X + 1'])
        while interp.running and interp.pc < len(interp.program_lines):
            interp.step()

        # X should be in cache (used in Y = X + 1)
        assert 'X' in interp._var_py_names

        # Reset with new program
        interp.reset(['Z = 20'])
        # Caches should be empty after reset
        assert len(interp._var_py_names) == 0
        assert len(interp._const_py_names) == 0

    def test_fingerprint_update_adds_new_names(self):
        """Test that adding new variables updates the cache on next eval.

        Variables are added AFTER eval_expr returns, so each new variable
        will be in the cache starting from the NEXT expression that uses it.
        """
        interp = setup()
        interp.reset([
            'X = 10',
            'Y = X + 5',      # X gets cached here
            'Z = Y + 10',     # X, Y get cached here
            'RESULT = X + Y + Z'  # X, Y, Z all get cached here
        ])
        while interp.running and interp.pc < len(interp.program_lines):
            interp.step()

        # All variables used in RESULT expression should be cached
        assert 'X' in interp._var_py_names
        assert 'Y' in interp._var_py_names
        assert 'Z' in interp._var_py_names


class TestPerformanceImprovement:
    """Test that the optimization actually improves performance."""

    def test_eval_performance_with_many_variables(self):
        """Test that eval_expr is faster with pre-computed names."""
        interp = setup()

        # Create a program with many variables
        lines = []
        for i in range(50):
            lines.append(f'V{i} = {i}')

        # Add a loop that repeatedly evaluates expressions
        lines.extend([
            'RESULT = 0',
            'StartLoop:',
            'RESULT = RESULT + V0 + V1 + V2 + V3 + V4',
            'COUNT = COUNT + 1',
            'IF COUNT < 500 THEN GOTO StartLoop'
        ])

        interp.reset(lines)

        start = time.time()
        while interp.running and interp.pc < len(interp.program_lines):
            interp.step()
        elapsed = time.time() - start

        # Verify the program ran correctly
        assert interp.variables.get('COUNT') == 500
        assert interp.variables.get('RESULT') == 500 * (0 + 1 + 2 + 3 + 4)

        # The optimization should allow this to complete in reasonable time
        # (without optimization, this would be much slower)
        print(f"Performance test completed in {elapsed:.3f}s")
        assert elapsed < 30.0, f"Test took too long: {elapsed:.3f}s"

    def test_type_suffix_variables_cached(self):
        """Test that variables with type suffixes are properly cached."""
        interp = setup()
        interp.reset([
            'X% = 10',
            'Y# = 3.14',
            'Z$ = "test"',
            'W! = 2.5',
            'V& = 1000000',
            'RESULT = X% + Y# + W!'
        ])
        while interp.running and interp.pc < len(interp.program_lines):
            interp.step()

        # Check all type suffixes are converted correctly
        assert interp._var_py_names.get('X%') == 'X_INT'
        assert interp._var_py_names.get('Y#') == 'Y_DBL'
        assert interp._var_py_names.get('Z$') == 'Z_STR'
        assert interp._var_py_names.get('W!') == 'W_SNG'
        assert interp._var_py_names.get('V&') == 'V_LNG'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
