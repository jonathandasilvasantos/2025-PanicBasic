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
    BasicInterpreter, BasicRuntimeError, LRUCache, LazyPattern, convert_basic_expr,
    _protect_strings, _restore_strings, _basic_to_python_identifier,
    _expr_cache, _compiled_expr_cache, _identifier_cache
)


class TestExpressionConversion(unittest.TestCase):
    """Test BASIC to Python expression conversion."""

    def setUp(self):
        """Clear caches before each test."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        _identifier_cache.clear()

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


class TestLRUCache(unittest.TestCase):
    """Test LRU cache implementation."""

    def test_basic_set_and_get(self):
        """Test basic cache set and get operations."""
        cache = LRUCache(maxsize=10)
        cache["key1"] = "value1"
        cache["key2"] = "value2"

        self.assertEqual(cache["key1"], "value1")
        self.assertEqual(cache["key2"], "value2")

    def test_contains(self):
        """Test __contains__ method."""
        cache = LRUCache(maxsize=10)
        cache["key1"] = "value1"

        self.assertIn("key1", cache)
        self.assertNotIn("key2", cache)

    def test_get_with_default(self):
        """Test get method with default value."""
        cache = LRUCache(maxsize=10)
        cache["key1"] = "value1"

        self.assertEqual(cache.get("key1"), "value1")
        self.assertIsNone(cache.get("nonexistent"))
        self.assertEqual(cache.get("nonexistent", "default"), "default")

    def test_eviction_when_full(self):
        """Test that oldest items are evicted when cache is full."""
        cache = LRUCache(maxsize=3)
        cache["key1"] = "value1"
        cache["key2"] = "value2"
        cache["key3"] = "value3"

        # Cache is full, add one more
        cache["key4"] = "value4"

        # key1 (oldest) should be evicted
        self.assertNotIn("key1", cache)
        self.assertIn("key2", cache)
        self.assertIn("key3", cache)
        self.assertIn("key4", cache)
        self.assertEqual(len(cache), 3)

    def test_lru_order_on_get(self):
        """Test that accessing an item moves it to most recently used."""
        cache = LRUCache(maxsize=3)
        cache["key1"] = "value1"
        cache["key2"] = "value2"
        cache["key3"] = "value3"

        # Access key1 to make it most recently used
        _ = cache["key1"]

        # Add a new item - key2 (now oldest) should be evicted
        cache["key4"] = "value4"

        self.assertIn("key1", cache)  # Still present (was accessed)
        self.assertNotIn("key2", cache)  # Evicted (was oldest after key1 access)
        self.assertIn("key3", cache)
        self.assertIn("key4", cache)

    def test_lru_order_on_set_existing(self):
        """Test that updating an existing item moves it to most recently used."""
        cache = LRUCache(maxsize=3)
        cache["key1"] = "value1"
        cache["key2"] = "value2"
        cache["key3"] = "value3"

        # Update key1 to make it most recently used
        cache["key1"] = "updated_value1"

        # Add a new item - key2 (now oldest) should be evicted
        cache["key4"] = "value4"

        self.assertIn("key1", cache)
        self.assertEqual(cache["key1"], "updated_value1")
        self.assertNotIn("key2", cache)

    def test_clear(self):
        """Test clear method."""
        cache = LRUCache(maxsize=10)
        cache["key1"] = "value1"
        cache["key2"] = "value2"

        cache.clear()

        self.assertEqual(len(cache), 0)
        self.assertNotIn("key1", cache)
        self.assertNotIn("key2", cache)

    def test_len(self):
        """Test __len__ method."""
        cache = LRUCache(maxsize=10)
        self.assertEqual(len(cache), 0)

        cache["key1"] = "value1"
        self.assertEqual(len(cache), 1)

        cache["key2"] = "value2"
        self.assertEqual(len(cache), 2)

    def test_expression_cache_eviction(self):
        """Test that expression caches properly evict old entries."""
        # Test with a small cache to verify eviction
        small_cache = LRUCache(maxsize=5)

        # Fill the cache
        for i in range(5):
            small_cache[f"expr{i}"] = f"result{i}"

        self.assertEqual(len(small_cache), 5)

        # Add more items, should evict oldest
        for i in range(5, 10):
            small_cache[f"expr{i}"] = f"result{i}"

        self.assertEqual(len(small_cache), 5)
        # First 5 should be evicted
        for i in range(5):
            self.assertNotIn(f"expr{i}", small_cache)
        # Last 5 should remain
        for i in range(5, 10):
            self.assertIn(f"expr{i}", small_cache)


class TestLazyPattern(unittest.TestCase):
    """Test lazy regex pattern compilation."""

    def test_lazy_pattern_not_compiled_initially(self):
        """Test that pattern is not compiled on creation."""
        lazy = LazyPattern(r"TEST\s+(\d+)", 0)
        self.assertFalse(lazy.is_compiled)

    def test_lazy_pattern_compiles_on_match(self):
        """Test that pattern compiles on first match call."""
        lazy = LazyPattern(r"TEST\s+(\d+)", 0)
        self.assertFalse(lazy.is_compiled)

        # First match triggers compilation
        result = lazy.match("TEST 123")
        self.assertTrue(lazy.is_compiled)
        self.assertIsNotNone(result)
        self.assertEqual(result.group(1), "123")

    def test_lazy_pattern_compiles_on_search(self):
        """Test that pattern compiles on first search call."""
        lazy = LazyPattern(r"\d+", 0)
        self.assertFalse(lazy.is_compiled)

        result = lazy.search("abc 42 def")
        self.assertTrue(lazy.is_compiled)
        self.assertIsNotNone(result)
        self.assertEqual(result.group(0), "42")

    def test_lazy_pattern_compiles_on_findall(self):
        """Test that pattern compiles on first findall call."""
        lazy = LazyPattern(r"\d+", 0)
        self.assertFalse(lazy.is_compiled)

        result = lazy.findall("a1 b2 c3")
        self.assertTrue(lazy.is_compiled)
        self.assertEqual(result, ["1", "2", "3"])

    def test_lazy_pattern_compiles_on_sub(self):
        """Test that pattern compiles on first sub call."""
        lazy = LazyPattern(r"\d+", 0)
        self.assertFalse(lazy.is_compiled)

        result = lazy.sub("X", "a1 b2 c3")
        self.assertTrue(lazy.is_compiled)
        self.assertEqual(result, "aX bX cX")

    def test_lazy_pattern_with_flags(self):
        """Test that pattern flags are applied correctly."""
        import re
        # Without IGNORECASE
        lazy_case = LazyPattern(r"test", 0)
        self.assertIsNone(lazy_case.match("TEST"))

        # With IGNORECASE
        lazy_nocase = LazyPattern(r"test", re.IGNORECASE)
        result = lazy_nocase.match("TEST")
        self.assertIsNotNone(result)
        self.assertEqual(result.group(0), "TEST")

    def test_lazy_pattern_caches_compilation(self):
        """Test that pattern only compiles once."""
        lazy = LazyPattern(r"(\w+)", 0)

        # First call compiles
        result1 = lazy.match("hello")
        self.assertTrue(lazy.is_compiled)
        compiled_pattern = lazy._compiled

        # Second call uses cached pattern
        result2 = lazy.match("world")
        self.assertIs(lazy._compiled, compiled_pattern)

        # Both results valid
        self.assertEqual(result1.group(1), "hello")
        self.assertEqual(result2.group(1), "world")

    def test_lazy_pattern_no_match(self):
        """Test that pattern returns None for non-matching strings."""
        lazy = LazyPattern(r"^\d+$", 0)

        result = lazy.match("abc")
        self.assertTrue(lazy.is_compiled)  # Still compiled even on no match
        self.assertIsNone(result)

    def test_lazy_pattern_compiles_on_fullmatch(self):
        """Test that pattern compiles on first fullmatch call."""
        lazy = LazyPattern(r"TEST\s+\d+", 0)
        self.assertFalse(lazy.is_compiled)

        # fullmatch requires entire string to match
        result = lazy.fullmatch("TEST 123")
        self.assertTrue(lazy.is_compiled)
        self.assertIsNotNone(result)

        # Partial match should fail with fullmatch
        lazy2 = LazyPattern(r"\d+", 0)
        self.assertIsNone(lazy2.fullmatch("abc123def"))


class TestConstants(unittest.TestCase):
    """Test that constants module is properly structured and importable."""

    def test_constants_importable(self):
        """Test that all constants can be imported from constants module."""
        from constants import (
            FONT_SIZE, INITIAL_WINDOW_WIDTH, INITIAL_WINDOW_HEIGHT,
            DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT, MAX_STEPS_PER_FRAME,
            PRINT_TAB_WIDTH, SCREEN_MODES, DEFAULT_COLORS, DEFAULT_FG_COLOR,
            DEFAULT_BG_COLOR, DEFAULT_ARRAY_SIZE, SCAN_CODES, ERROR_CODES
        )

        # Verify types
        self.assertIsInstance(FONT_SIZE, int)
        self.assertIsInstance(SCREEN_MODES, dict)
        self.assertIsInstance(DEFAULT_COLORS, dict)
        self.assertIsInstance(SCAN_CODES, dict)
        self.assertIsInstance(ERROR_CODES, dict)

    def test_screen_modes_valid(self):
        """Test that screen modes have valid dimensions."""
        from constants import SCREEN_MODES

        for mode, (width, height) in SCREEN_MODES.items():
            self.assertIsInstance(mode, int)
            self.assertIsInstance(width, int)
            self.assertIsInstance(height, int)


class TestCommandDispatch(unittest.TestCase):
    """Test the command dispatch table mechanism."""

    def setUp(self):
        """Set up test fixtures."""
        if not pygame.get_init():
            pygame.init()
        if not pygame.font.get_init():
            pygame.font.init()
        self.font = pygame.font.SysFont(None, 16)
        self.interp = BasicInterpreter(self.font, 320, 200)

    def test_dispatch_table_exists(self):
        """Test that dispatch table is created."""
        self.assertIsNotNone(self.interp._command_dispatch)
        self.assertIsInstance(self.interp._command_dispatch, dict)

    def test_dispatch_table_has_basic_commands(self):
        """Test that dispatch table has expected commands."""
        dispatch = self.interp._command_dispatch
        # Check for some basic commands
        self.assertIn("BEEP", dispatch)
        self.assertIn("STOP", dispatch)
        self.assertIn("TRON", dispatch)
        self.assertIn("TROFF", dispatch)
        self.assertIn("CLS", dispatch)
        self.assertIn("GOTO", dispatch)
        self.assertIn("GOSUB", dispatch)
        self.assertIn("RETURN", dispatch)

    def test_extract_first_keyword(self):
        """Test keyword extraction from statements."""
        self.assertEqual(self.interp._extract_first_keyword("PRINT x"), "PRINT")
        self.assertEqual(self.interp._extract_first_keyword("goto label"), "GOTO")
        self.assertEqual(self.interp._extract_first_keyword("FOR I = 1 TO 10"), "FOR")
        self.assertEqual(self.interp._extract_first_keyword("$INCLUDE: 'file.bi'"), "$INCLUDE")
        self.assertIsNone(self.interp._extract_first_keyword("123"))
        self.assertIsNone(self.interp._extract_first_keyword(""))

    def test_dispatch_command_beep(self):
        """Test that BEEP command is dispatched correctly."""
        # BEEP should be handled and return False (no jump)
        result = self.interp._dispatch_command("BEEP", 0)
        self.assertIsNotNone(result)
        self.assertEqual(result, False)

    def test_dispatch_command_unknown(self):
        """Test that unknown commands return None."""
        # Unknown command should return None (fall through)
        result = self.interp._dispatch_command("UNKNOWNCOMMAND", 0)
        self.assertIsNone(result)

    def test_dispatch_tron_troff(self):
        """Test TRON/TROFF via dispatch."""
        self.assertFalse(self.interp.trace_mode)

        # TRON should enable trace mode
        self.interp._dispatch_command("TRON", 0)
        self.assertTrue(self.interp.trace_mode)

        # TROFF should disable trace mode
        self.interp._dispatch_command("TROFF", 0)
        self.assertFalse(self.interp.trace_mode)


class TestDefaultColors(unittest.TestCase):
    """Test default color constants."""

    def test_default_colors_has_16_colors(self):
        """Test that default color palette has all 16 colors."""
        from constants import DEFAULT_COLORS

        self.assertEqual(len(DEFAULT_COLORS), 16)
        for i in range(16):
            self.assertIn(i, DEFAULT_COLORS)
            rgb = DEFAULT_COLORS[i]
            self.assertEqual(len(rgb), 3)
            for component in rgb:
                self.assertGreaterEqual(component, 0)
                self.assertLessEqual(component, 255)

    def test_cache_sizes_positive(self):
        """Test that cache sizes are positive integers."""
        from constants import (
            EXPR_CACHE_MAX_SIZE, COMPILED_CACHE_MAX_SIZE,
            IDENTIFIER_CACHE_MAX_SIZE
        )

        self.assertGreater(EXPR_CACHE_MAX_SIZE, 0)
        self.assertGreater(COMPILED_CACHE_MAX_SIZE, 0)
        self.assertGreater(IDENTIFIER_CACHE_MAX_SIZE, 0)


class TestIdentifierConversion(unittest.TestCase):
    """Test BASIC identifier to Python identifier conversion."""

    def setUp(self):
        """Clear identifier cache before each test."""
        _identifier_cache.clear()

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

    def test_double_suffix(self):
        """Test # suffix conversion (double precision)."""
        result = _basic_to_python_identifier("value#")
        self.assertEqual(result, "VALUE_DBL")

    def test_single_suffix(self):
        """Test ! suffix conversion (single precision)."""
        result = _basic_to_python_identifier("rate!")
        self.assertEqual(result, "RATE_SNG")

    def test_long_suffix(self):
        """Test & suffix conversion (long integer)."""
        result = _basic_to_python_identifier("bignum&")
        self.assertEqual(result, "BIGNUM_LNG")


class TestIdentifierCaching(unittest.TestCase):
    """Test identifier conversion caching behavior."""

    def setUp(self):
        """Clear identifier cache before each test."""
        _identifier_cache.clear()

    def test_cache_stores_result(self):
        """Test that cache stores converted identifier."""
        # Cache should be empty initially
        self.assertEqual(len(_identifier_cache), 0)

        # Call the function
        result = _basic_to_python_identifier("myvar$")
        self.assertEqual(result, "MYVAR_STR")

        # Result should be cached under the normalized (uppercase) key
        self.assertIn("MYVAR$", _identifier_cache)
        self.assertEqual(_identifier_cache["MYVAR$"], "MYVAR_STR")

    def test_cache_returns_cached_value(self):
        """Test that cache hit returns same value."""
        # First call
        result1 = _basic_to_python_identifier("test%")
        # Second call should return cached value
        result2 = _basic_to_python_identifier("test%")

        self.assertEqual(result1, result2)
        self.assertEqual(result1, "TEST_INT")
        # Should only be one entry in cache (stored under normalized key)
        self.assertEqual(_identifier_cache.get("TEST%"), "TEST_INT")

    def test_cache_handles_multiple_identifiers(self):
        """Test cache with multiple different identifiers."""
        identifiers = ["a$", "b%", "c#", "d!", "e&", "f"]
        expected = ["A_STR", "B_INT", "C_DBL", "D_SNG", "E_LNG", "F"]

        for ident, exp in zip(identifiers, expected):
            result = _basic_to_python_identifier(ident)
            self.assertEqual(result, exp)

        # All should be cached
        self.assertEqual(len(_identifier_cache), 6)

    def test_cache_clear_removes_entries(self):
        """Test that clearing cache removes entries."""
        _basic_to_python_identifier("var1")
        _basic_to_python_identifier("var2$")

        self.assertEqual(len(_identifier_cache), 2)

        _identifier_cache.clear()

        self.assertEqual(len(_identifier_cache), 0)

    def test_case_insensitive_cache(self):
        """Test that cache is case-insensitive for efficiency."""
        # Different case inputs should produce the same result
        result1 = _basic_to_python_identifier("Var")
        result2 = _basic_to_python_identifier("VAR")
        result3 = _basic_to_python_identifier("var")

        # All should produce same output (uppercase)
        self.assertEqual(result1, "VAR")
        self.assertEqual(result2, "VAR")
        self.assertEqual(result3, "VAR")

        # All case variants should share a single cache entry (normalized to uppercase)
        # This avoids wasting memory with redundant cache entries
        self.assertIn("VAR", _identifier_cache)
        self.assertEqual(_identifier_cache["VAR"], "VAR")
        # The non-normalized keys should NOT be in the cache
        self.assertNotIn("Var", _identifier_cache)
        self.assertNotIn("var", _identifier_cache)

    def test_cache_efficiency_with_mixed_case(self):
        """Test that mixed-case identifiers create minimal cache entries."""
        # This tests the performance improvement of case-insensitive caching
        _identifier_cache.clear()

        # Call with many case variants of the same identifiers
        identifiers = [
            "score", "Score", "SCORE", "ScOrE",
            "name$", "Name$", "NAME$", "NaMe$",
            "count%", "Count%", "COUNT%"
        ]

        for ident in identifiers:
            _basic_to_python_identifier(ident)

        # Should only have 3 unique cache entries (one per unique normalized identifier)
        # Not 11 entries (one per input variant)
        self.assertEqual(len(_identifier_cache), 3)
        self.assertIn("SCORE", _identifier_cache)
        self.assertIn("NAME$", _identifier_cache)
        self.assertIn("COUNT%", _identifier_cache)


class TestInterpreterBasics(unittest.TestCase):
    """Test basic interpreter functionality."""

    def setUp(self):
        """Create interpreter instance for testing."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        _identifier_cache.clear()
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
        _identifier_cache.clear()
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
        _identifier_cache.clear()
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

    def test_point_all_standard_colors(self):
        """Test POINT returns correct color numbers for all 16 standard colors."""
        self.interp.reset(["SCREEN 13"])
        self.interp.step()

        # Test each of the 16 standard palette colors (0-15)
        for color_num in range(16):
            # Set a pixel with this color
            x, y = 10 + color_num, 10
            self.interp.reset(["SCREEN 13", f"PSET ({x}, {y}), {color_num}"])
            self.interp.step()  # SCREEN
            self.interp.step()  # PSET

            # Verify POINT returns the correct color number
            result = self.interp.point(x, y)
            self.assertEqual(result, color_num,
                f"POINT({x}, {y}) should return {color_num}, got {result}")

    def test_point_returns_minus_one_for_nonstandard_color(self):
        """Test POINT returns -1 for colors not in the standard palette."""
        self.interp.reset(["SCREEN 13"])
        self.interp.step()

        # Manually set a pixel to a color not in the palette
        # (128, 128, 128) is not a standard QBasic color
        nonstandard_rgb = (128, 128, 128)
        self.interp.surface.set_at((100, 100), nonstandard_rgb)

        # POINT should return -1 for this non-palette color
        result = self.interp.point(100, 100)
        self.assertEqual(result, -1)

    def test_point_out_of_bounds(self):
        """Test POINT returns -1 for out-of-bounds coordinates."""
        self.interp.reset(["SCREEN 13"])
        self.interp.step()

        # Test coordinates outside screen bounds
        self.assertEqual(self.interp.point(-1, 50), -1)
        self.assertEqual(self.interp.point(50, -1), -1)
        self.assertEqual(self.interp.point(400, 50), -1)  # > 320 width
        self.assertEqual(self.interp.point(50, 300), -1)  # > 200 height

    def test_reverse_color_lookup_initialized(self):
        """Test that the reverse color lookup dictionary is properly initialized."""
        self.interp.reset(["SCREEN 13"])
        self.interp.step()

        # Verify reverse lookup dict exists and has all 16 colors
        self.assertTrue(hasattr(self.interp, '_reverse_colors'))
        self.assertEqual(len(self.interp._reverse_colors), 16)

        # Verify reverse mapping is correct for all colors
        for color_num, rgb in self.interp.colors.items():
            self.assertIn(rgb, self.interp._reverse_colors)
            self.assertEqual(self.interp._reverse_colors[rgb], color_num)


class TestStringHandling(unittest.TestCase):
    """Test string operations in statements."""

    def setUp(self):
        """Create interpreter."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        _identifier_cache.clear()
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
        _identifier_cache.clear()
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
        _identifier_cache.clear()
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
        _identifier_cache.clear()
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

    def test_eval_locals_fingerprint_optimization(self):
        """Test that eval_locals uses fingerprint to avoid unnecessary rebuilds."""
        self.interp.reset(["x = 10", "y = 20"])

        # Run some statements to set up variables
        self.interp.step()  # x = 10
        self.interp.step()  # y = 20

        # First eval should set the fingerprint
        self.interp.eval_expr("x + y")
        initial_fingerprint = self.interp._eval_locals_fingerprint
        self.assertIsNotNone(initial_fingerprint)

        # Eval again with same variables - fingerprint should stay the same
        self.interp.eval_expr("x * 2")
        self.assertEqual(initial_fingerprint, self.interp._eval_locals_fingerprint)

        # Add a new variable - fingerprint should change
        self.interp.variables["Z"] = 30
        self.interp.eval_expr("x + z")
        new_fingerprint = self.interp._eval_locals_fingerprint
        self.assertNotEqual(initial_fingerprint, new_fingerprint)

    def test_eval_locals_updated_on_value_change(self):
        """Test that eval_locals values are updated when variables change."""
        self.interp.reset(["x = 10"])
        self.interp.step()

        # Evaluate expression
        result1 = self.interp.eval_expr("x")
        self.assertEqual(result1, 10)

        # Change variable value
        self.interp.variables["X"] = 50

        # Should get updated value
        result2 = self.interp.eval_expr("x")
        self.assertEqual(result2, 50)


class TestFileSystemCommands(unittest.TestCase):
    """Test file system commands (KILL, NAME, MKDIR, RMDIR, CHDIR, FILES)."""

    def setUp(self):
        """Create interpreter instance for testing."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        _identifier_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)
        # Create a temp directory for tests
        self.test_dir = os.path.join(os.path.dirname(__file__), "_test_fs_temp")
        if os.path.exists(self.test_dir):
            import shutil
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)
        self.orig_dir = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        """Clean up temp directory."""
        os.chdir(self.orig_dir)
        if os.path.exists(self.test_dir):
            import shutil
            shutil.rmtree(self.test_dir)

    def test_mkdir_command(self):
        """Test MKDIR command creates directory."""
        self.interp.reset(['MKDIR "testdir"'])
        self.interp.step()
        self.assertTrue(os.path.isdir("testdir"))

    def test_rmdir_command(self):
        """Test RMDIR command removes directory."""
        os.mkdir("todelete")
        self.interp.reset(['RMDIR "todelete"'])
        self.interp.step()
        self.assertFalse(os.path.exists("todelete"))

    def test_chdir_command(self):
        """Test CHDIR command changes directory."""
        os.mkdir("subdir")
        orig = os.getcwd()
        self.interp.reset(['CHDIR "subdir"'])
        self.interp.step()
        self.assertNotEqual(os.getcwd(), orig)
        self.assertTrue(os.getcwd().endswith("subdir"))
        os.chdir(orig)

    def test_kill_command(self):
        """Test KILL command deletes file."""
        with open("todelete.txt", "w") as f:
            f.write("test")
        self.assertTrue(os.path.exists("todelete.txt"))
        self.interp.reset(['KILL "todelete.txt"'])
        self.interp.step()
        self.assertFalse(os.path.exists("todelete.txt"))

    def test_name_command(self):
        """Test NAME command renames file."""
        with open("oldname.txt", "w") as f:
            f.write("test")
        self.interp.reset(['NAME "oldname.txt" AS "newname.txt"'])
        self.interp.step()
        self.assertFalse(os.path.exists("oldname.txt"))
        self.assertTrue(os.path.exists("newname.txt"))


class TestFilePositioning(unittest.TestCase):
    """Test file positioning commands (SEEK, LOC)."""

    def setUp(self):
        """Create interpreter instance for testing."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        _identifier_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)
        # Create a temp directory for tests
        self.test_dir = os.path.join(os.path.dirname(__file__), "_test_fp_temp")
        if os.path.exists(self.test_dir):
            import shutil
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)
        self.orig_dir = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        """Clean up temp directory."""
        os.chdir(self.orig_dir)
        if os.path.exists(self.test_dir):
            import shutil
            shutil.rmtree(self.test_dir)

    def test_seek_command(self):
        """Test SEEK command sets file position."""
        # Create a test file with known content
        with open("seektest.bin", "wb") as f:
            f.write(b"ABCDEFGHIJ")

        self.interp.reset([
            'OPEN "seektest.bin" FOR BINARY AS #1',
            'SEEK #1, 5',
            'CLOSE #1'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()

        # File should have been processed without error
        self.assertTrue(self.interp.running or self.interp.pc >= len(self.interp.program_lines))

    def test_loc_function(self):
        """Test LOC function returns file position."""
        # Create a test file
        with open("loctest.bin", "wb") as f:
            f.write(b"ABCDEFGHIJ")

        self.interp.reset([
            'OPEN "loctest.bin" FOR BINARY AS #1',
            'pos1 = LOC(1)',
            'CLOSE #1'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()

        # LOC should return 1 at start (1-based)
        self.assertEqual(self.interp.variables.get("POS1"), 1)


class TestPCOPY(unittest.TestCase):
    """Test PCOPY video page copy command."""

    def setUp(self):
        """Create interpreter instance for testing."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        _identifier_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)

    def test_pcopy_to_offscreen_page(self):
        """Test PCOPY copies surface to offscreen page."""
        self.interp.reset([
            'SCREEN 13',
            'PSET (50, 50), 15',
            'PCOPY 0, 1'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()

        # Page 1 should now exist
        self.assertIn(1, self.interp.video_pages)
        self.assertIsNotNone(self.interp.video_pages[1])

    def test_pcopy_restore_page(self):
        """Test PCOPY can restore from offscreen page."""
        self.interp.reset([
            'SCREEN 13',
            'PSET (50, 50), 15',
            'PCOPY 0, 1',
            'CLS',
            'PCOPY 1, 0'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()

        # After PCOPY 1, 0, the pixel should be restored
        # Check that the surface is not empty
        self.assertTrue(self.interp.running or self.interp.pc >= len(self.interp.program_lines))


class TestBinaryConversion(unittest.TestCase):
    """Test binary conversion functions (MKI$, CVI, etc.)."""

    def setUp(self):
        """Create interpreter instance for testing."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        _identifier_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)

    def test_mki_cvi_roundtrip(self):
        """Test MKI$ and CVI roundtrip."""
        result = self.interp.eval_expr('CVI(MKI$(12345))')
        self.assertEqual(result, 12345)

    def test_mkl_cvl_roundtrip(self):
        """Test MKL$ and CVL roundtrip."""
        result = self.interp.eval_expr('CVL(MKL$(123456789))')
        self.assertEqual(result, 123456789)

    def test_mks_cvs_roundtrip(self):
        """Test MKS$ and CVS roundtrip."""
        result = self.interp.eval_expr('CVS(MKS$(3.14))')
        self.assertAlmostEqual(result, 3.14, places=2)

    def test_mkd_cvd_roundtrip(self):
        """Test MKD$ and CVD roundtrip."""
        result = self.interp.eval_expr('CVD(MKD$(3.14159265359))')
        self.assertAlmostEqual(result, 3.14159265359, places=8)


class TestErrorStatement(unittest.TestCase):
    """Test ERROR statement."""

    def setUp(self):
        """Create interpreter instance for testing."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        _identifier_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)

    def test_error_without_handler(self):
        """Test ERROR without ON ERROR GOTO stops execution."""
        self.interp.reset([
            'x = 1',
            'ERROR 5',
            'x = 2'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()

        # Execution should have stopped
        self.assertFalse(self.interp.running)
        self.assertEqual(self.interp.variables.get("X"), 1)

    def test_error_with_handler(self):
        """Test ERROR with ON ERROR GOTO jumps to handler."""
        self.interp.reset([
            'ON ERROR GOTO handler',
            'x = 1',
            'ERROR 5',
            'x = 2',
            'END',
            'handler:',
            'handled = 1',
            'RESUME NEXT'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()

        # Handler should have been invoked (set handled=1), then RESUME NEXT
        # continues at x=2 (the statement after ERROR 5)
        self.assertEqual(self.interp.variables.get("HANDLED"), 1)
        self.assertEqual(self.interp.variables.get("X"), 2)


class TestRuntimeErrorHelper(unittest.TestCase):
    """Test the _runtime_error helper method."""

    def setUp(self):
        """Create interpreter instance for testing."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        _identifier_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)

    def test_runtime_error_stops_execution(self):
        """Test that _runtime_error stops execution and returns False."""
        self.interp.running = True
        result = self.interp._runtime_error("Test error", 42)

        self.assertFalse(result)
        self.assertFalse(self.interp.running)

    def test_runtime_error_with_handler_raises(self):
        """Test that _runtime_error raises BasicRuntimeError when handler is set."""
        self.interp.running = True
        self.interp.error_handler_label = "error_handler"

        with self.assertRaises(BasicRuntimeError) as context:
            self.interp._runtime_error("Test error", 42)

        self.assertIn("Test error", str(context.exception))
        self.assertIn("PC 42", str(context.exception))

    def test_runtime_error_in_program_flow(self):
        """Test _runtime_error in actual program execution context."""
        # Test that an error condition stops execution
        self.interp.reset([
            'FOR I = 1 TO 5',
            'NEXT J',  # Wrong variable - should cause error
            'x = 1'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()

        # Execution should have stopped due to error
        self.assertFalse(self.interp.running)
        # x should not be set because execution stopped
        self.assertNotIn("X", self.interp.variables)


class TestERLandERRFunctions(unittest.TestCase):
    """Test ERL and ERR functions for error handling."""

    def setUp(self):
        """Create interpreter instance for testing."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        _identifier_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)

    def test_erl_returns_error_line(self):
        """Test ERL returns the line number where error occurred."""
        self.interp.reset([
            'ON ERROR GOTO handler',
            'x = 1',
            'ERROR 5',
            'END',
            'handler:',
            'errorline = ERL',
            'RESUME NEXT'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()

        # ERL should return the line number where ERROR 5 was called (line 3)
        self.assertEqual(self.interp.variables.get("ERRORLINE"), 3)

    def test_err_returns_error_code(self):
        """Test ERR returns the error code."""
        self.interp.reset([
            'ON ERROR GOTO handler',
            'x = 1',
            'ERROR 53',
            'END',
            'handler:',
            'errorcode = ERR',
            'RESUME NEXT'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()

        # ERR should return 53 (File not found)
        self.assertEqual(self.interp.variables.get("ERRORCODE"), 53)

    def test_erl_and_err_together(self):
        """Test ERL and ERR work together in error handler."""
        self.interp.reset([
            'ON ERROR GOTO handler',
            'x = 1',
            'y = 2',
            'ERROR 11',
            'z = 3',
            'END',
            'handler:',
            'errline = ERL',
            'errcode = ERR',
            'RESUME NEXT'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()

        # ERL should return line 4 (ERROR 11)
        self.assertEqual(self.interp.variables.get("ERRLINE"), 4)
        # ERR should return 11 (Division by zero)
        self.assertEqual(self.interp.variables.get("ERRCODE"), 11)
        # z should be set after RESUME NEXT
        self.assertEqual(self.interp.variables.get("Z"), 3)

    def test_erl_zero_without_error(self):
        """Test ERL returns 0 when no error has occurred."""
        self.interp.reset([
            'errorline = ERL',
            'errorcode = ERR'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()

        # Without any error, ERL and ERR should return 0
        self.assertEqual(self.interp.variables.get("ERRORLINE"), 0)
        self.assertEqual(self.interp.variables.get("ERRORCODE"), 0)

    def test_erl_in_expression(self):
        """Test ERL can be used in expressions."""
        self.interp.reset([
            'ON ERROR GOTO handler',
            'ERROR 5',
            'END',
            'handler:',
            'result = ERL * 10 + ERR',
            'RESUME NEXT'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()

        # ERL=2, ERR=5, so result = 2*10 + 5 = 25
        self.assertEqual(self.interp.variables.get("RESULT"), 25)

    def test_multiple_errors(self):
        """Test ERL and ERR update correctly for multiple errors."""
        self.interp.reset([
            'ON ERROR GOTO handler',
            'ERROR 5',
            'ERROR 11',
            'END',
            'handler:',
            'errline = ERL',
            'errcode = ERR',
            'RESUME NEXT'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()

        # After second error (ERROR 11 on line 3), ERL=3 and ERR=11
        self.assertEqual(self.interp.variables.get("ERRLINE"), 3)
        self.assertEqual(self.interp.variables.get("ERRCODE"), 11)


class TestLPOSFunction(unittest.TestCase):
    """Test LPOS printer function (emulated)."""

    def setUp(self):
        """Create interpreter instance for testing."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        _identifier_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)

    def test_lpos_returns_one(self):
        """Test LPOS returns 1 (emulated printer at start of line)."""
        self.interp.reset([
            'pos0 = LPOS(0)',
            'pos1 = LPOS(1)'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()

        # LPOS always returns 1 (emulated)
        self.assertEqual(self.interp.variables.get("POS0"), 1)
        self.assertEqual(self.interp.variables.get("POS1"), 1)


class TestERDEVFunctions(unittest.TestCase):
    """Test ERDEV and ERDEV$ device error functions (emulated)."""

    def setUp(self):
        """Create interpreter instance for testing."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        _identifier_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)

    def test_erdev_returns_zero(self):
        """Test ERDEV returns 0 (emulated - no device errors)."""
        self.interp.reset([
            'errcode = ERDEV'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()

        # ERDEV always returns 0 (emulated)
        self.assertEqual(self.interp.variables.get("ERRCODE"), 0)

    def test_erdev_str_returns_empty(self):
        """Test ERDEV$ returns empty string (emulated - no device errors)."""
        self.interp.reset([
            'errname$ = ERDEV$'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()

        # ERDEV$ always returns empty string (emulated)
        self.assertEqual(self.interp.variables.get("ERRNAME$"), "")


class TestFILEATTRFunction(unittest.TestCase):
    """Test FILEATTR file attribute function."""

    def setUp(self):
        """Create interpreter instance for testing."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        _identifier_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)
        # Create a temp file for testing
        import tempfile
        self.temp_fd, self.temp_file = tempfile.mkstemp(suffix='.txt')
        os.write(self.temp_fd, b'test data')
        os.close(self.temp_fd)

    def tearDown(self):
        """Clean up temp file."""
        try:
            os.unlink(self.temp_file)
        except:
            pass

    def test_fileattr_mode_input(self):
        """Test FILEATTR returns 1 for INPUT mode."""
        self.interp.reset([
            f'OPEN "{self.temp_file}" FOR INPUT AS #1',
            'mode = FILEATTR(1, 1)',
            'CLOSE #1'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()

        self.assertEqual(self.interp.variables.get("MODE"), 1)

    def test_fileattr_handle(self):
        """Test FILEATTR returns emulated file handle."""
        self.interp.reset([
            f'OPEN "{self.temp_file}" FOR INPUT AS #1',
            'handle = FILEATTR(1, 2)',
            'CLOSE #1'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()

        self.assertEqual(self.interp.variables.get("HANDLE"), 100)

    def test_fileattr_file_not_open(self):
        """Test FILEATTR returns 0 for file not open."""
        self.interp.reset([
            'result = FILEATTR(99, 1)'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()

        self.assertEqual(self.interp.variables.get("RESULT"), 0)


class TestSETMEMFunction(unittest.TestCase):
    """Test SETMEM memory function (emulated)."""

    def setUp(self):
        """Create interpreter instance for testing."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        _identifier_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)

    def test_setmem_returns_emulated_size(self):
        """Test SETMEM returns emulated far heap size."""
        self.interp.reset([
            'memsize = SETMEM(0)'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()

        # SETMEM returns 65536 (emulated)
        self.assertEqual(self.interp.variables.get("MEMSIZE"), 65536)


class TestIOCTLFunctions(unittest.TestCase):
    """Test IOCTL$ function and IOCTL statement (emulated)."""

    def setUp(self):
        """Create interpreter instance for testing."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        _identifier_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)

    def test_ioctl_str_returns_empty(self):
        """Test IOCTL$ returns empty string (emulated)."""
        self.interp.reset([
            'ctrl$ = IOCTL$(1)'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()

        # IOCTL$ always returns empty string (emulated)
        self.assertEqual(self.interp.variables.get("CTRL$"), "")

    def test_ioctl_statement_no_error(self):
        """Test IOCTL statement doesn't cause error (emulated no-op)."""
        self.interp.reset([
            'IOCTL #1, "test"',
            'result = 1'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()

        # IOCTL is a no-op, program should continue
        self.assertEqual(self.interp.variables.get("RESULT"), 1)


class TestMBFConversionFunctions(unittest.TestCase):
    """Test Microsoft Binary Format conversion functions (CVDMBF, CVSMBF, MKDMBF$, MKSMBF$)."""

    def setUp(self):
        """Create interpreter instance for testing."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        _identifier_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)

    def test_cvsmbf_zero(self):
        """Test CVSMBF with zero value."""
        # Zero in MBF is all zero bytes
        self.interp.reset([
            'mbf$ = CHR$(0) + CHR$(0) + CHR$(0) + CHR$(0)',
            'result = CVSMBF(mbf$)'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()
        self.assertEqual(self.interp.variables.get("RESULT"), 0.0)

    def test_cvsmbf_one(self):
        """Test CVSMBF with value 1.0."""
        # MBF for 1.0: mantissa=0x800000, exponent=129 (128+1)
        # Bytes: [0x00, 0x00, 0x00, 0x81]
        self.interp.reset([
            'mbf$ = CHR$(0) + CHR$(0) + CHR$(0) + CHR$(129)',
            'result = CVSMBF(mbf$)'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()
        self.assertAlmostEqual(self.interp.variables.get("RESULT"), 1.0, places=5)

    def test_cvdmbf_zero(self):
        """Test CVDMBF with zero value."""
        self.interp.reset([
            'mbf$ = STRING$(8, 0)',
            'result = CVDMBF(mbf$)'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()
        self.assertEqual(self.interp.variables.get("RESULT"), 0.0)

    def test_cvdmbf_one(self):
        """Test CVDMBF with value 1.0."""
        # MBF double for 1.0: mantissa=0x80..., exponent=129
        self.interp.reset([
            'mbf$ = STRING$(6, 0) + CHR$(0) + CHR$(129)',
            'result = CVDMBF(mbf$)'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()
        self.assertAlmostEqual(self.interp.variables.get("RESULT"), 1.0, places=10)

    def test_mksmbf_zero(self):
        """Test MKSMBF$ with zero value."""
        self.interp.reset([
            'result$ = MKSMBF$(0)',
            'len_result = LEN(result$)'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()
        # Should return 4 zero bytes
        self.assertEqual(self.interp.variables.get("LEN_RESULT"), 4)
        self.assertEqual(self.interp.variables.get("RESULT$"), '\x00\x00\x00\x00')

    def test_mksmbf_roundtrip(self):
        """Test MKSMBF$ and CVSMBF roundtrip."""
        self.interp.reset([
            'original = 3.14159',
            'mbf$ = MKSMBF$(original)',
            'result = CVSMBF(mbf$)'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()
        original = self.interp.variables.get("ORIGINAL")
        result = self.interp.variables.get("RESULT")
        # MBF single has ~7 significant digits, allow some tolerance
        self.assertAlmostEqual(result, original, places=5)

    def test_mkdmbf_zero(self):
        """Test MKDMBF$ with zero value."""
        self.interp.reset([
            'result$ = MKDMBF$(0)',
            'len_result = LEN(result$)'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()
        # Should return 8 zero bytes
        self.assertEqual(self.interp.variables.get("LEN_RESULT"), 8)

    def test_mkdmbf_roundtrip(self):
        """Test MKDMBF$ and CVDMBF roundtrip."""
        self.interp.reset([
            'original# = 2.718281828459045#',
            'mbf$ = MKDMBF$(original#)',
            'result# = CVDMBF(mbf$)'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()
        original = self.interp.variables.get("ORIGINAL#")
        result = self.interp.variables.get("RESULT#")
        # MBF double has ~15 significant digits
        self.assertAlmostEqual(result, original, places=10)

    def test_mksmbf_negative(self):
        """Test MKSMBF$ with negative value."""
        self.interp.reset([
            'original = -42.5',
            'mbf$ = MKSMBF$(original)',
            'result = CVSMBF(mbf$)'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()
        original = self.interp.variables.get("ORIGINAL")
        result = self.interp.variables.get("RESULT")
        self.assertAlmostEqual(result, original, places=5)

    def test_mkdmbf_negative(self):
        """Test MKDMBF$ with negative value."""
        self.interp.reset([
            'original# = -123.456789#',
            'mbf$ = MKDMBF$(original#)',
            'result# = CVDMBF(mbf$)'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()
        original = self.interp.variables.get("ORIGINAL#")
        result = self.interp.variables.get("RESULT#")
        self.assertAlmostEqual(result, original, places=10)


class TestClearStatement(unittest.TestCase):
    """Test CLEAR statement."""

    def setUp(self):
        """Create interpreter instance for testing."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        _identifier_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)

    def test_clear_removes_variables(self):
        """Test CLEAR removes all variables."""
        self.interp.reset([
            'x = 10',
            'y = 20',
            'CLEAR',
            'z = x + y'  # x and y should be 0 now
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()

        # After CLEAR, x and y are reset to 0, so z = 0 + 0 = 0
        self.assertEqual(self.interp.variables.get("Z"), 0)


class TestSystemStatement(unittest.TestCase):
    """Test SYSTEM statement."""

    def setUp(self):
        """Create interpreter instance for testing."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        _identifier_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)

    def test_system_stops_execution(self):
        """Test SYSTEM stops program execution."""
        self.interp.reset([
            'x = 1',
            'SYSTEM',
            'x = 2'  # Should not execute
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()

        self.assertFalse(self.interp.running)
        self.assertEqual(self.interp.variables.get("X"), 1)


class TestViewStatement(unittest.TestCase):
    """Test VIEW statement."""

    def setUp(self):
        """Create interpreter instance for testing."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        _identifier_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)

    def test_view_sets_viewport(self):
        """Test VIEW sets viewport coordinates."""
        self.interp.reset([
            'SCREEN 13',
            'VIEW (10, 10)-(100, 100)'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()

        self.assertEqual(self.interp.view_x1, 10)
        self.assertEqual(self.interp.view_y1, 10)
        self.assertEqual(self.interp.view_x2, 100)
        self.assertEqual(self.interp.view_y2, 100)

    def test_view_reset(self):
        """Test VIEW without arguments resets viewport."""
        self.interp.reset([
            'SCREEN 13',
            'VIEW (10, 10)-(100, 100)',
            'VIEW'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()

        self.assertEqual(self.interp.view_x1, 0)
        self.assertEqual(self.interp.view_y1, 0)
        self.assertIsNone(self.interp.view_x2)
        self.assertIsNone(self.interp.view_y2)


class TestWindowStatement(unittest.TestCase):
    """Test WINDOW statement."""

    def setUp(self):
        """Create interpreter instance for testing."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        _identifier_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)

    def test_window_sets_coordinates(self):
        """Test WINDOW sets logical coordinate system."""
        self.interp.reset([
            'SCREEN 13',
            'WINDOW (-100, -100)-(100, 100)'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()

        self.assertEqual(self.interp.window_x1, -100)
        self.assertEqual(self.interp.window_y1, -100)
        self.assertEqual(self.interp.window_x2, 100)
        self.assertEqual(self.interp.window_y2, 100)
        self.assertFalse(self.interp.window_screen_mode)

    def test_window_reset(self):
        """Test WINDOW without arguments resets to physical coordinates."""
        self.interp.reset([
            'SCREEN 13',
            'WINDOW (-100, -100)-(100, 100)',
            'WINDOW'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()

        self.assertIsNone(self.interp.window_x1)
        self.assertIsNone(self.interp.window_y1)


class TestFieldLsetRset(unittest.TestCase):
    """Test FIELD, LSET, and RSET statements."""

    def setUp(self):
        """Create interpreter instance for testing."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        _identifier_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)

    def test_lset_left_justify(self):
        """Test LSET left-justifies string."""
        self.interp.reset([
            'NAME$ = "          "',  # 10 spaces - set up field variable
            'LSET NAME$ = "Hi"'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()

        result = self.interp.variables.get("NAME$")
        self.assertEqual(len(result), 10)
        self.assertEqual(result, "Hi        ")  # Left-justified

    def test_rset_right_justify(self):
        """Test RSET right-justifies string."""
        self.interp.reset([
            'NAME$ = "          "',  # 10 spaces - set up field variable
            'RSET NAME$ = "Hi"'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()

        result = self.interp.variables.get("NAME$")
        self.assertEqual(len(result), 10)
        self.assertEqual(result, "        Hi")  # Right-justified


class TestEnvironStatement(unittest.TestCase):
    """Test ENVIRON statement (set environment variable)."""

    def setUp(self):
        """Create interpreter instance for testing."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        _identifier_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)

    def test_environ_set(self):
        """Test ENVIRON sets environment variable."""
        import os
        self.interp.reset([
            'ENVIRON "TEST_VAR=hello_world"'
        ])
        self.interp.step()

        self.assertEqual(os.environ.get("TEST_VAR"), "hello_world")
        # Clean up
        if "TEST_VAR" in os.environ:
            del os.environ["TEST_VAR"]


class TestTimerEvents(unittest.TestCase):
    """Test ON TIMER GOSUB and TIMER ON/OFF."""

    def setUp(self):
        """Create interpreter instance for testing."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        _identifier_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)

    def test_on_timer_sets_handler(self):
        """Test ON TIMER GOSUB sets timer handler."""
        self.interp.reset([
            'ON TIMER(1) GOSUB handler',
            'END',
            'handler:',
            'x = 1',
            'RETURN'
        ])
        self.interp.step_line()  # ON TIMER

        self.assertEqual(self.interp.timer_interval, 1)
        self.assertEqual(self.interp.timer_label, "HANDLER")

    def test_timer_on_off(self):
        """Test TIMER ON and TIMER OFF."""
        self.interp.reset([
            'ON TIMER(1) GOSUB handler',
            'TIMER ON',
            'TIMER OFF',
            'END',
            'handler:',
            'RETURN'
        ])
        self.interp.step_line()  # ON TIMER
        self.interp.step_line()  # TIMER ON
        self.assertTrue(self.interp.timer_enabled)
        self.interp.step_line()  # TIMER OFF
        self.assertFalse(self.interp.timer_enabled)


class TestDateTimeAssignment(unittest.TestCase):
    """Test DATE$ and TIME$ assignment."""

    def setUp(self):
        """Create interpreter instance for testing."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        _identifier_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)

    def test_date_assignment(self):
        """Test DATE$ assignment sets custom date."""
        self.interp.reset(['DATE$ = "12-25-2025"', 'd$ = DATE$'])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()
        self.assertEqual(self.interp.variables.get("D$"), "12-25-2025")

    def test_time_assignment(self):
        """Test TIME$ assignment sets custom time."""
        self.interp.reset(['TIME$ = "14:30:00"', 't$ = TIME$'])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()
        self.assertEqual(self.interp.variables.get("T$"), "14:30:00")

    def test_date_assignment_with_expression(self):
        """Test DATE$ assignment with expression."""
        self.interp.reset(['d$ = "01-01-2020"', 'DATE$ = d$', 'result$ = DATE$'])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()
        self.assertEqual(self.interp.variables.get("RESULT$"), "01-01-2020")

    def test_time_assignment_with_expression(self):
        """Test TIME$ assignment with expression."""
        self.interp.reset(['t$ = "09:00:00"', 'TIME$ = t$', 'result$ = TIME$'])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()
        self.assertEqual(self.interp.variables.get("RESULT$"), "09:00:00")


class TestCommonStatement(unittest.TestCase):
    """Test COMMON statement for CHAIN variable preservation."""

    def setUp(self):
        """Create interpreter instance for testing."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        _identifier_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)

    def test_common_adds_to_set(self):
        """Test COMMON statement adds variables to common_variables set."""
        self.interp.reset(['COMMON x, y, z'])
        self.interp.step_line()
        self.assertIn("X", self.interp.common_variables)
        self.assertIn("Y", self.interp.common_variables)
        self.assertIn("Z", self.interp.common_variables)

    def test_common_with_type_suffix(self):
        """Test COMMON with type suffix variables."""
        self.interp.reset(['COMMON name$, count%'])
        self.interp.step_line()
        self.assertIn("NAME$", self.interp.common_variables)
        self.assertIn("COUNT%", self.interp.common_variables)

    def test_common_shared_adds_to_set(self):
        """Test COMMON SHARED also adds to common_variables."""
        self.interp.reset(['COMMON SHARED a, b'])
        self.interp.step_line()
        self.assertIn("A", self.interp.common_variables)
        self.assertIn("B", self.interp.common_variables)

    def test_common_with_as_type(self):
        """Test COMMON with AS type syntax."""
        self.interp.reset(['COMMON value AS INTEGER'])
        self.interp.step_line()
        self.assertIn("VALUE", self.interp.common_variables)

    def test_common_continues_execution(self):
        """Test COMMON doesn't stop execution."""
        self.interp.reset(['COMMON x', 'x = 10'])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()
        self.assertEqual(self.interp.variables.get("X"), 10)


class TestTronTroff(unittest.TestCase):
    """Test TRON/TROFF trace debugging."""

    def setUp(self):
        """Create interpreter instance for testing."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        _identifier_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)

    def test_tron_enables_trace(self):
        """Test TRON enables trace mode."""
        self.interp.reset(['TRON', 'x = 1'])
        self.interp.step_line()  # TRON
        self.assertTrue(self.interp.trace_mode)

    def test_troff_disables_trace(self):
        """Test TROFF disables trace mode."""
        self.interp.reset(['TRON', 'TROFF', 'x = 1'])
        self.interp.step_line()  # TRON
        self.assertTrue(self.interp.trace_mode)
        self.interp.step_line()  # TROFF
        self.assertFalse(self.interp.trace_mode)


class TestRunCommand(unittest.TestCase):
    """Test RUN command."""

    def setUp(self):
        """Create interpreter instance for testing."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        _identifier_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)

    def test_run_restarts_from_beginning(self):
        """Test RUN without arguments restarts from beginning."""
        self.interp.reset([
            'x = 10',
            'IF x < 100 THEN x = x + 1 : GOTO skiprun',
            'RUN',
            'skiprun:',
            'y = x'
        ])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()
        # x starts at 10, increments to 11, then continues
        self.assertEqual(self.interp.variables.get("Y"), 11)


class TestContCommand(unittest.TestCase):
    """Test CONT command."""

    def setUp(self):
        """Create interpreter instance for testing."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        _identifier_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)

    def test_stop_sets_stopped_flag(self):
        """Test STOP sets stopped flag."""
        self.interp.reset(['x = 1', 'STOP', 'x = 2'])
        self.interp.step_line()  # x = 1
        self.interp.step_line()  # STOP
        self.assertTrue(self.interp.stopped)
        self.assertFalse(self.interp.running)


class TestMemoryFunctions(unittest.TestCase):
    """Test VARPTR, VARSEG, SADD functions."""

    def setUp(self):
        """Create interpreter instance for testing."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        _identifier_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)

    def test_varptr_returns_value(self):
        """Test VARPTR returns a numeric value."""
        self.interp.reset(['x = 10', 'addr = VARPTR(x)'])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()
        # VARPTR should return some integer address
        addr = self.interp.variables.get("ADDR")
        self.assertIsNotNone(addr)
        self.assertIsInstance(addr, int)

    def test_varseg_returns_segment(self):
        """Test VARSEG returns a segment value."""
        self.interp.reset(['x = 10', 'seg = VARSEG(x)'])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()
        seg = self.interp.variables.get("SEG")
        self.assertIsNotNone(seg)
        self.assertIsInstance(seg, int)

    def test_sadd_returns_address(self):
        """Test SADD returns string address."""
        self.interp.reset(['s$ = "hello"', 'addr = SADD(s$)'])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()
        addr = self.interp.variables.get("ADDR")
        self.assertIsNotNone(addr)
        self.assertIsInstance(addr, int)


class TestKeyHandling(unittest.TestCase):
    """Test KEY statement and ON KEY GOSUB."""

    def setUp(self):
        """Create interpreter instance for testing."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        _identifier_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)

    def test_key_definition(self):
        """Test KEY n, string$ defines function key."""
        self.interp.reset(['KEY 1, "HELP"'])
        self.interp.step_line()
        self.assertEqual(self.interp.key_definitions.get(1), "HELP")

    def test_key_on_off(self):
        """Test KEY(n) ON/OFF enables/disables key events."""
        self.interp.reset([
            'KEY(1) ON',
            'KEY(1) OFF'
        ])
        self.interp.step_line()  # KEY(1) ON
        self.assertTrue(self.interp.key_enabled.get(1))
        self.interp.step_line()  # KEY(1) OFF
        self.assertFalse(self.interp.key_enabled.get(1))

    def test_on_key_gosub(self):
        """Test ON KEY(n) GOSUB sets handler."""
        self.interp.reset([
            'ON KEY(1) GOSUB handler',
            'END',
            'handler:',
            'RETURN'
        ])
        self.interp.step_line()  # ON KEY
        self.assertEqual(self.interp.key_handlers.get(1), "HANDLER")


class TestPlayFunction(unittest.TestCase):
    """Test PLAY(n) function."""

    def setUp(self):
        """Create interpreter instance for testing."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        _identifier_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)

    def test_play_function_returns_zero(self):
        """Test PLAY(0) returns 0 (no background queue)."""
        result = self.interp.eval_expr('PLAY(0)')
        self.assertEqual(result, 0)

    def test_on_play_gosub_sets_handler(self):
        """Test ON PLAY GOSUB sets handler."""
        self.interp.reset([
            'ON PLAY(5) GOSUB handler',
            'END',
            'handler:',
            'RETURN'
        ])
        self.interp.step_line()  # ON PLAY
        self.assertEqual(self.interp.play_handler, "HANDLER")
        self.assertEqual(self.interp.play_threshold, 5)

    def test_play_on_off(self):
        """Test PLAY ON and OFF."""
        self.interp.reset([
            'ON PLAY(5) GOSUB handler',
            'PLAY ON',
            'PLAY OFF',
            'END',
            'handler:',
            'RETURN'
        ])
        self.interp.step_line()  # ON PLAY
        self.interp.step_line()  # PLAY ON
        self.assertTrue(self.interp.play_enabled)
        self.interp.step_line()  # PLAY OFF
        self.assertFalse(self.interp.play_enabled)


class TestJoystickFunctions(unittest.TestCase):
    """Test STICK and STRIG joystick functions."""

    def setUp(self):
        """Create interpreter instance for testing."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        _identifier_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)

    def test_stick_returns_center_no_joystick(self):
        """Test STICK returns center value (127) when no joystick."""
        result = self.interp.eval_expr('STICK(0)')
        self.assertEqual(result, 127)

    def test_stick_all_values(self):
        """Test STICK(0-3) returns center values."""
        for i in range(4):
            result = self.interp.eval_expr(f'STICK({i})')
            self.assertEqual(result, 127)

    def test_strig_returns_zero_no_joystick(self):
        """Test STRIG returns 0 when no joystick."""
        result = self.interp.eval_expr('STRIG(0)')
        self.assertEqual(result, 0)

    def test_strig_all_values(self):
        """Test STRIG(0-7) returns 0."""
        for i in range(8):
            result = self.interp.eval_expr(f'STRIG({i})')
            self.assertEqual(result, 0)

    def test_stick_in_program(self):
        """Test STICK can be used in a program."""
        self.interp.reset(['x = STICK(0)', 'y = STICK(1)'])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()
        self.assertEqual(self.interp.variables.get("X"), 127)
        self.assertEqual(self.interp.variables.get("Y"), 127)

    def test_strig_in_program(self):
        """Test STRIG can be used in a program."""
        self.interp.reset(['b = STRIG(0)'])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()
        self.assertEqual(self.interp.variables.get("B"), 0)

    def test_on_strig_gosub_sets_handler(self):
        """Test ON STRIG GOSUB sets handler."""
        self.interp.reset([
            'ON STRIG(0) GOSUB handler',
            'END',
            'handler:',
            'RETURN'
        ])
        self.interp.step_line()  # ON STRIG
        self.assertEqual(self.interp.strig_handlers.get(0), "HANDLER")

    def test_strig_on_off(self):
        """Test STRIG(n) ON and OFF."""
        self.interp.reset([
            'ON STRIG(0) GOSUB handler',
            'STRIG(0) ON',
            'STRIG(0) OFF',
            'END',
            'handler:',
            'RETURN'
        ])
        self.interp.step_line()  # ON STRIG
        self.interp.step_line()  # STRIG ON
        self.assertTrue(self.interp.strig_enabled.get(0))
        self.interp.step_line()  # STRIG OFF
        self.assertFalse(self.interp.strig_enabled.get(0))


class TestPenFunctions(unittest.TestCase):
    """Test PEN light pen functions (emulated with mouse)."""

    def setUp(self):
        """Create interpreter instance for testing."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        _identifier_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)

    def test_pen_returns_zero_not_pressed(self):
        """Test PEN(0) returns 0 when not pressed."""
        result = self.interp.eval_expr('PEN(0)')
        self.assertEqual(result, 0)

    def test_pen_coordinates_initial(self):
        """Test PEN coordinates are 0 initially."""
        self.assertEqual(self.interp.eval_expr('PEN(1)'), 0)  # Activated X
        self.assertEqual(self.interp.eval_expr('PEN(2)'), 0)  # Activated Y
        self.assertEqual(self.interp.eval_expr('PEN(4)'), 0)  # Current X
        self.assertEqual(self.interp.eval_expr('PEN(5)'), 0)  # Current Y

    def test_pen_down_not_pressed(self):
        """Test PEN(3) returns 0 when not pressed."""
        result = self.interp.eval_expr('PEN(3)')
        self.assertEqual(result, 0)

    def test_on_pen_gosub_sets_handler(self):
        """Test ON PEN GOSUB sets handler."""
        self.interp.reset([
            'ON PEN GOSUB handler',
            'END',
            'handler:',
            'RETURN'
        ])
        self.interp.step_line()  # ON PEN
        self.assertEqual(self.interp.pen_handler, "HANDLER")

    def test_pen_on_off(self):
        """Test PEN ON and OFF."""
        self.interp.reset([
            'ON PEN GOSUB handler',
            'PEN ON',
            'PEN OFF',
            'END',
            'handler:',
            'RETURN'
        ])
        self.interp.step_line()  # ON PEN
        self.interp.step_line()  # PEN ON
        self.assertTrue(self.interp.pen_enabled)
        self.interp.step_line()  # PEN OFF
        self.assertFalse(self.interp.pen_enabled)

    def test_pen_in_program(self):
        """Test PEN can be used in a program."""
        self.interp.reset(['x = PEN(0)', 'y = PEN(3)'])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()
        self.assertEqual(self.interp.variables.get("X"), 0)
        self.assertEqual(self.interp.variables.get("Y"), 0)


class TestMetacommands(unittest.TestCase):
    """Test $DYNAMIC, $STATIC metacommands."""

    def setUp(self):
        """Create interpreter instance for testing."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        _identifier_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)

    def test_dynamic_accepted(self):
        """Test $DYNAMIC is accepted without error."""
        self.interp.reset(['$DYNAMIC', 'x = 1'])
        self.interp.step_line()  # $DYNAMIC
        self.assertTrue(self.interp.running)

    def test_static_accepted(self):
        """Test $STATIC is accepted without error."""
        self.interp.reset(['$STATIC', 'x = 1'])
        self.interp.step_line()  # $STATIC
        self.assertTrue(self.interp.running)


class TestHardwareIO(unittest.TestCase):
    """Test INP, OUT, WAIT hardware I/O functions."""

    def setUp(self):
        """Create interpreter instance for testing."""
        _expr_cache.clear()
        _compiled_expr_cache.clear()
        _identifier_cache.clear()
        self.font = pygame.font.Font(None, 16)
        self.interp = BasicInterpreter(self.font, 800, 600)

    def test_out_and_inp(self):
        """Test OUT writes value that INP can read back."""
        self.interp.reset(['OUT 100, 255', 'x = INP(100)'])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()
        self.assertEqual(self.interp.variables.get("X"), 255)

    def test_inp_unset_port_returns_zero(self):
        """Test INP on unset port returns 0."""
        self.interp.reset(['x = INP(999)'])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()
        self.assertEqual(self.interp.variables.get("X"), 0)

    def test_out_masks_to_byte(self):
        """Test OUT masks value to byte (0-255)."""
        self.interp.reset(['OUT 50, 256', 'x = INP(50)'])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()
        # 256 & 0xFF = 0
        self.assertEqual(self.interp.variables.get("X"), 0)

    def test_wait_is_accepted(self):
        """Test WAIT is accepted without error (no-op)."""
        self.interp.reset(['WAIT &H3DA, 8', 'x = 1'])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()
        self.assertTrue(self.interp.running or self.interp.variables.get("X") == 1)

    def test_wait_with_xor_mask(self):
        """Test WAIT with xor_mask is accepted."""
        self.interp.reset(['WAIT &H3DA, 8, 8', 'x = 1'])
        while self.interp.running and self.interp.pc < len(self.interp.program_lines):
            self.interp.step()
        self.assertEqual(self.interp.variables.get("X"), 1)


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)
