import pygame
import re
import random
import time
import math
from typing import List, Optional, Tuple, Dict, Any
from pygame.locals import KEYDOWN, QUIT, VIDEORESIZE
from collections import deque

# Try to import numpy for faster array operations
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# --- Constants ---
FONT_SIZE = 16
INITIAL_WIDTH = 800
INITIAL_HEIGHT = 600
DEFAULT_SCREEN_WIDTH = 320
DEFAULT_SCREEN_HEIGHT = 200
MAX_STEPS_PER_FRAME = 2000  # Increased from 500 for better performance
PRINT_TAB_WIDTH = 14

# --- Compiled Expression Cache ---
_compiled_expr_cache: Dict[str, Any] = {}  # Cache for compiled code objects

# --- Precompiled Regex Patterns ---

# --- Expression Conversion Patterns ---
_eq_re = re.compile(r'(?<![<>!=])=(?![=<>])') # Match = for comparison
_neq_re = re.compile(r'<>') # Match <> for inequality
_and_re = re.compile(r'\bAND\b', re.IGNORECASE)
_or_re = re.compile(r'\bOR\b', re.IGNORECASE)
_not_re = re.compile(r'\bNOT\b', re.IGNORECASE)
_mod_re = re.compile(r'\bMOD\b', re.IGNORECASE)
_exp_re = re.compile(r'\^')  # BASIC exponentiation operator

# Specific function keywords that are parameterless or have unique syntax
_inkey_re = re.compile(r'\bINKEY\$', re.IGNORECASE)  # INKEY$ -> INKEY() (no trailing \b as $ is not a word char)
_timer_re = re.compile(r'\bTIMER\b(?!\s*\()', re.IGNORECASE)  # TIMER -> TIMER()
_date_re = re.compile(r'\bDATE\$', re.IGNORECASE)  # DATE$ -> DATE()
_time_re = re.compile(r'\bTIME\$', re.IGNORECASE)  # TIME$ -> TIME()
_rnd_bare_re = re.compile(r'\bRND\b(?!\s*\()', re.IGNORECASE)  # RND -> RND()

# General pattern for NAME(...) or NAME$(...) which could be a function call or array access
_func_or_array_re = re.compile(
    r'\b([a-zA-Z_][a-zA-Z0-9_]*\$?)\s*\(([^)]*)\)', # name(args) - args can be empty
    re.IGNORECASE
)

# General identifier pattern (variables, constants)
# It should run after specific function/array patterns have transformed their part of the string.
# Note: No trailing \b because $ and % are not word characters
_identifier_re = re.compile(r'\b([a-zA-Z_][a-zA-Z0-9_]*[\$%]?)')  # Match identifiers with optional $ or % suffix


# --- Command Parsing Patterns (mostly unchanged but reviewed) ---
_label_re = re.compile(r"^\s*(\d+|[a-zA-Z_][a-zA-Z0-9_]*:)")
_label_strip_re = re.compile(r"^\s*(\d+\s+|[a-zA-Z_][a-zA-Z0-9_]*:)\s*")
_for_re = re.compile(
    r'FOR\s+([a-zA-Z_][a-zA-Z0-9_]*\$?)\s*=\s*(.+?)\s+TO\s+(.+?)(?:\s+STEP\s+(.+))?$', re.IGNORECASE)
_dim_re = re.compile(r'DIM\s+([a-zA-Z_][a-zA-Z0-9_]*\$?)\s*\(([^)]+)\)', re.IGNORECASE)
_assign_re = re.compile(r'^(?:LET\s+)?([a-zA-Z_][a-zA-Z0-9_]*\$?(?:\s*\([^)]+\))?)\s*=(.*)$', re.IGNORECASE)
# Pattern to extract array name and indices from LHS like "ARR(1, 2)"
_assign_lhs_array_re = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*\$?)\s*\(([^)]+)\)')


_line_re = re.compile(
    r"LINE\s*(?:\(\s*([^,]+)\s*,\s*([^)]+)\s*\))?\s*-\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)\s*(?:,(.*))?$", re.IGNORECASE)
_circle_re = re.compile(
    r"CIRCLE\s*\(([^,]+),([^)]+)\)\s*,\s*([^,]+)\s*(?:,\s*([^,]*))?\s*(?:,\s*([^,]*))?\s*(?:,\s*([^,]*))?\s*(?:,\s*([^,]*))?\s*(?:,\s*(F|BF))?", re.IGNORECASE)
_paint_re = re.compile(r"PAINT\s*\(([^,]+),([^)]+)\)\s*(?:,\s*([^,]+))?(?:,\s*([^,]+))?", re.IGNORECASE)
_pset_re = re.compile(
    r"PSET\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)\s*(?:,\s*(.+))?", re.IGNORECASE)
_locate_re = re.compile(r"LOCATE\s*(\d+|\S[^,]*?)?(?:,\s*(\d+|\S[^,]*?))?", re.IGNORECASE) # Allow expressions for row/col
_print_re = re.compile(r"PRINT\s?(.*)", re.IGNORECASE)
_if_re = re.compile(r"IF\s+(.+?)\s+THEN(.*)", re.IGNORECASE)
_goto_re = re.compile(r"GOTO\s+([a-zA-Z0-9_]+)", re.IGNORECASE)
_gosub_re = re.compile(r"GOSUB\s+([a-zA-Z0-9_]+)", re.IGNORECASE)
_return_re = re.compile(r"RETURN", re.IGNORECASE)
_screen_re = re.compile(r"SCREEN\s+(\d+)", re.IGNORECASE)
_cls_re = re.compile(r"CLS", re.IGNORECASE)
_end_re = re.compile(r"END", re.IGNORECASE)
_randomize_re = re.compile(r"RANDOMIZE(?:\s+(.*))?", re.IGNORECASE)
_next_re = re.compile(r"NEXT(?:\s+([a-zA-Z_][a-zA-Z0-9_]*\$?))?", re.IGNORECASE)
_delay_re = re.compile(r"(?:_DELAY|SLEEP)\s+(.*)", re.IGNORECASE)
_do_re = re.compile(r"DO(?:\s+(WHILE|UNTIL)\s+(.+))?", re.IGNORECASE)
_loop_re = re.compile(r"LOOP(?:\s+(WHILE|UNTIL)\s+(.+))?", re.IGNORECASE)
_const_re = re.compile(r"CONST\s+([a-zA-Z_][a-zA-Z0-9_]*\$?)\s*=(.*)", re.IGNORECASE)
_color_re = re.compile(r"COLOR(?:\s*([^,]+))?(?:\s*,\s*(.+))?", re.IGNORECASE)
_rem_re = re.compile(r"REM\b.*", re.IGNORECASE)
_exit_do_re = re.compile(r"EXIT\s+DO", re.IGNORECASE)
_exit_for_re = re.compile(r"EXIT\s+FOR", re.IGNORECASE)

# New statement patterns
_swap_re = re.compile(r"SWAP\s+([a-zA-Z_][a-zA-Z0-9_]*\$?(?:\s*\([^)]+\))?)\s*,\s*([a-zA-Z_][a-zA-Z0-9_]*\$?(?:\s*\([^)]+\))?)", re.IGNORECASE)
_while_re = re.compile(r"WHILE\s+(.+)", re.IGNORECASE)
_wend_re = re.compile(r"WEND", re.IGNORECASE)
_select_case_re = re.compile(r"SELECT\s+CASE\s+(.+)", re.IGNORECASE)
_case_re = re.compile(r"CASE\s+(.*)", re.IGNORECASE)
_end_select_re = re.compile(r"END\s+SELECT", re.IGNORECASE)
_data_re = re.compile(r"DATA\s+(.*)", re.IGNORECASE)
_read_re = re.compile(r"READ\s+(.*)", re.IGNORECASE)
_restore_re = re.compile(r"RESTORE(?:\s+([a-zA-Z0-9_]+))?", re.IGNORECASE)

_expr_cache: Dict[str, str] = {}
_python_keywords = {'and', 'or', 'not', 'in', 'is', 'lambda', 'if', 'else', 'elif', 'while', 'for', 'try', 'except', 'finally', 'with', 'as', 'def', 'class', 'import', 'from', 'pass', 'break', 'continue', 'return', 'yield', 'global', 'nonlocal', 'assert', 'del', 'True', 'False', 'None'}
# Python builtins used in generated code (for array indexing) - keep lowercase
_python_builtins_used = {'int'}
_basic_function_names = {
    'CHR', 'INKEY', 'RND', 'INT', 'POINT', 'TIMER', 'STR', 'VAL',
    'LEFT', 'RIGHT', 'MID', 'LEN', 'ABS', 'SQR', 'SIN', 'COS', 'TAN', 'ATN', 'SGN', 'FIX',
    # New string functions
    'ASC', 'INSTR', 'LCASE', 'UCASE', 'LTRIM', 'RTRIM', 'SPACE', 'STRING', 'HEX', 'OCT',
    # New math functions
    'LOG', 'EXP', 'CINT',
    # Date/time functions
    'DATE', 'TIME'
}

# --- Expression Conversion Logic ---

def _basic_to_python_identifier(basic_name_str: str) -> str:
    """Converts a BASIC identifier to a Python-compatible identifier for eval."""
    name_upper = basic_name_str.upper()
    if name_upper.endswith('$'):
        return name_upper[:-1] + "_STR"
    elif name_upper.endswith('%'):
        return name_upper[:-1] + "_INT"
    return name_upper

def _convert_identifier_in_expr(match: re.Match) -> str:
    """
    Callback for _identifier_re.sub.
    Converts a matched BASIC identifier (variable, constant, or bare function name)
    to its Python representation within an expression.
    """
    identifier = match.group(1)

    # Skip Python keywords (and, or, not, etc.) - they should not be converted
    if identifier.lower() in _python_keywords:
        return identifier

    # Skip Python builtins used in generated code (like 'int' for array indexing)
    if identifier.lower() in _python_builtins_used:
        return identifier

    base_name_upper = identifier.rstrip('$%').upper()

    if base_name_upper in _basic_function_names:
        # This implies a bare function name like RND, INKEY, TIMER was not converted
        # by earlier rules, or it's a function name that was already part of a call
        # like FOO in FOO(...). In either case, it should be the base function name.
        return base_name_upper

    # It's a variable or constant
    return _basic_to_python_identifier(identifier)

_memoized_arg_splits: Dict[str, List[str]] = {}

def _split_args(args_str: str) -> List[str]:
    """
    Splits an argument string by commas, respecting parentheses for nested calls.
    This is a simplified parser; a full tokenizer/parser would be more robust.
    """
    if not args_str.strip():
        return []
    if args_str in _memoized_arg_splits:
        return _memoized_arg_splits[args_str]

    args = []
    current_arg = ""
    paren_level = 0
    for char in args_str:
        if char == ',' and paren_level == 0:
            args.append(current_arg.strip())
            current_arg = ""
        else:
            current_arg += char
            if char == '(':
                paren_level += 1
            elif char == ')':
                paren_level -= 1
    args.append(current_arg.strip())
    _memoized_arg_splits[args_str] = args
    return args


def _replace_func_or_array_access(match: re.Match) -> str:
    """
    Callback for _func_or_array_re.sub.
    Determines if NAME(...) is a function call or array access and converts accordingly.
    """
    name_basic = match.group(1)  # e.g., "MYARRAY", "MYARRAY$", "CHR$", "LEFT$"
    args_str = match.group(2)    # Content between parentheses

    name_base_upper = name_basic.rstrip('$%').upper()

    if name_base_upper in _basic_function_names:  # It's a function call
        arg_parts = _split_args(args_str)
        # Recursively call convert_basic_expr for each argument
        # Pass dummy known_identifiers as it's not strictly needed by new logic path
        processed_args = [convert_basic_expr(arg, set()) for arg in arg_parts]
        return f"{name_base_upper}({', '.join(processed_args)})"
    else:  # It's an array access
        py_array_name = _basic_to_python_identifier(name_basic)
        arg_parts = _split_args(args_str)
        if not arg_parts: # Should not happen if args_str was not empty
             raise ValueError(f"Array access for '{name_basic}' with no indices.")

        # Array indices must be integers after evaluation
        # Use __int__, __round__, __float__ to avoid uppercase conversion issues
        processed_indices = [f"int({convert_basic_expr(idx, set())})" for idx in arg_parts]
        # For multi-dimensional arrays: array[idx1][idx2]...
        return f"{py_array_name}[{']['.join(processed_indices)}]"


def _protect_strings(expr: str) -> Tuple[str, List[str]]:
    """Extract string literals and replace with placeholders to protect them during conversion."""
    strings = []
    result = []
    i = 0
    while i < len(expr):
        if expr[i] == '"':
            # Find end of string
            j = i + 1
            while j < len(expr) and expr[j] != '"':
                j += 1
            if j < len(expr):
                j += 1  # Include closing quote
            strings.append(expr[i:j])
            result.append(f"__STR{len(strings) - 1}__")
            i = j
        else:
            result.append(expr[i])
            i += 1
    return ''.join(result), strings

def _restore_strings(expr: str, strings: List[str]) -> str:
    """Restore string literals from placeholders."""
    for i, s in enumerate(strings):
        expr = expr.replace(f"__STR{i}__", s)
    return expr

def convert_basic_expr(expr: str, known_identifiers: Optional[set] = None) -> str:
    """
    Converts a BASIC expression string to an equivalent Python expression string.
    """
    expr = expr.strip()
    if not expr:
        return ""

    original_expr_for_cache = expr
    if original_expr_for_cache in _expr_cache:
        return _expr_cache[original_expr_for_cache]

    # Protect string literals from modification
    expr, strings = _protect_strings(expr)

    # 1. Specific function keyword substitutions (parameterless or unique syntax)
    expr = _inkey_re.sub("INKEY()", expr)
    expr = _timer_re.sub("TIMER()", expr)
    expr = _date_re.sub("DATE()", expr)
    expr = _time_re.sub("TIME()", expr)
    expr = _rnd_bare_re.sub("RND()", expr)

    # 2. General function calls OR array access: NAME(...) / NAME$(...)
    expr = _func_or_array_re.sub(_replace_func_or_array_access, expr)

    # 3. Operators
    expr = _and_re.sub(" and ", expr)
    expr = _or_re.sub(" or ", expr)
    expr = _not_re.sub(" not ", expr)
    expr = _mod_re.sub(" % ", expr)
    expr = _exp_re.sub(" ** ", expr)  # BASIC ^ to Python **
    expr = _eq_re.sub(" == ", expr)
    expr = _neq_re.sub(" != ", expr)

    # Clean up any leading/trailing whitespace that might cause syntax errors
    expr = expr.strip()

    # 4. Remaining identifiers (variables, constants not part of function calls)
    expr = _identifier_re.sub(_convert_identifier_in_expr, expr)

    # Restore string literals
    expr = _restore_strings(expr, strings)

    _expr_cache[original_expr_for_cache] = expr
    return expr

class BasicInterpreter:
    def __init__(self, font: pygame.font.Font, width: int, height: int) -> None:
        self.font = font
        self.initial_width = width
        self.initial_height = height
        self.program_lines: List[Tuple[int, str, str]] = []
        self.pc: int = 0
        self.variables: Dict[str, Any] = {}
        self.constants: Dict[str, Any] = {}
        self.loop_stack: List[Dict[str, Any]] = []
        self.for_stack: List[Dict[str, Any]] = []
        self.gosub_stack: List[int] = []
        self.if_level: int = 0
        self.if_skip_level: int = -1
        self.if_executed: List[bool] = []  # Track if a branch was executed at each IF level
        self.running: bool = True
        # DATA/READ/RESTORE state
        self.data_values: List[Any] = []  # All DATA values in program order
        self.data_pointer: int = 0  # Current position in data_values
        self.data_labels: Dict[str, int] = {}  # Label -> index in data_values
        # SELECT CASE state
        self.select_stack: List[Dict[str, Any]] = []  # Stack of SELECT CASE blocks
        self.text_cursor: Tuple[int, int] = (1, 1)
        self.surface: Optional[pygame.Surface] = None
        self.screen_width: int = DEFAULT_SCREEN_WIDTH
        self.screen_height: int = DEFAULT_SCREEN_HEIGHT
        self.last_key: str = ""
        self.colors: Dict[int, Tuple[int, int, int]] = {
            0: (0,0,0), 1: (0,0,170), 2: (0,170,0), 3: (0,170,170),
            4: (170,0,0), 5: (170,0,170), 6: (170,85,0), 7: (170,170,170),
            8: (85,85,85), 9: (85,85,255), 10: (85,255,85), 11: (85,255,255),
            12: (255,85,85), 13: (255,85,255), 14: (255,255,85), 15: (255,255,255)
        }
        self.current_fg_color: int = 7
        self.current_bg_color: int = 0
        self.lpr: Tuple[int, int] = (0, 0) # Last Point Referenced
        self.delay_until: int = 0
        self.labels: Dict[str, int] = {}
        self.steps_per_frame: int = MAX_STEPS_PER_FRAME
        self.window_width = width
        self.window_height = height
        self._dirty = True
        self._cached_scaled_surface: Optional[pygame.Surface] = None
        self.last_rnd_value: Optional[float] = None
        
        # Environment for eval() - functions available to BASIC expressions
        self.eval_env_funcs = {
            # Original functions
            "CHR": lambda x: chr(int(x)), "INKEY": self.inkey, "RND": self._basic_rnd,
            "INT": lambda x: math.floor(float(x)), "POINT": self.point,
            "TIMER": lambda: time.time() % 86400, "ABS": lambda x: abs(float(x)),
            "SQR": lambda x: math.sqrt(float(x)), "STR": lambda x: str(x),
            "VAL": lambda x_str: self._basic_val(str(x_str)),
            "LEN": lambda s: len(str(s)),
            "LEFT": lambda s, n: str(s)[:int(n)],
            "RIGHT": lambda s, n: str(s)[-int(n):] if int(n) > 0 else "",
            "MID": lambda s, st, ln=None: str(s)[int(st)-1 : (int(st)-1 + int(ln)) if ln is not None else len(str(s))],
            "SIN": lambda x: math.sin(float(x)), "COS": lambda x: math.cos(float(x)),
            "TAN": lambda x: math.tan(float(x)), "ATN": lambda x: math.atan(float(x)),
            "SGN": lambda x: 0 if float(x) == 0 else (1 if float(x) > 0 else -1),
            "FIX": lambda x: int(float(x)),  # Truncate towards zero
            # New string functions
            "ASC": lambda s: ord(str(s)[0]) if s else 0,  # ASCII code of first char
            "INSTR": self._basic_instr,  # Find substring
            "LCASE": lambda s: str(s).lower(),  # Convert to lowercase
            "UCASE": lambda s: str(s).upper(),  # Convert to uppercase
            "LTRIM": lambda s: str(s).lstrip(),  # Remove leading spaces
            "RTRIM": lambda s: str(s).rstrip(),  # Remove trailing spaces
            "SPACE": lambda n: " " * int(n),  # Generate n spaces
            "STRING": self._basic_string,  # Generate repeated chars
            "HEX": lambda n: hex(int(n))[2:].upper(),  # Convert to hex string
            "OCT": lambda n: oct(int(n))[2:],  # Convert to octal string
            # New math functions
            "LOG": lambda x: math.log(float(x)),  # Natural logarithm
            "EXP": lambda x: math.exp(float(x)),  # e^x
            "CINT": lambda x: round(float(x)),  # Round to nearest integer
            # Date/time functions
            "DATE": self._basic_date,  # Current date string
            "TIME": self._basic_time,  # Current time string
        }

    def _basic_val(self, s_val: str) -> Any:
        s_val = s_val.strip()
        try:
            # Try to convert to int first if no decimal point or exponent
            if '.' not in s_val and 'E' not in s_val.upper() and 'e' not in s_val:
                return int(s_val)
            return float(s_val)
        except ValueError:
            # Handle cases like "123xyz" -> 123, or "xyz" -> 0
            match = re.match(r"([+-]?\d*\.?\d*(?:[Ee][+-]?\d+)?)", s_val)
            if match and match.group(1):
                num_part = match.group(1)
                try:
                    if '.' not in num_part and 'E' not in num_part.upper() and 'e' not in num_part:
                        return int(num_part)
                    return float(num_part)
                except ValueError:
                    return 0 # Should not happen if regex matched a number part
            return 0

    def _basic_rnd(self, x: Any = 1.0) -> float:
        # Mimics QB RND behavior:
        # RND / RND(>0): Next random number in sequence.
        # RND(0): Repeats the last number generated.
        # RND(<0): Reseeds the generator.
        num_x = 1.0 # Default for RND or RND()
        try:
            if x is not None: # RND function in eval_env_funcs will always pass an arg
                num_x = float(x)
        except (ValueError, TypeError):
            # If x cannot be converted to float, default to RND(1) behavior
            num_x = 1.0 
            
        if num_x < 0:
            random.seed(num_x) # Reseed
            self.last_rnd_value = random.random()
            return self.last_rnd_value
        elif num_x == 0:
            if self.last_rnd_value is None: # First call is RND(0)
                # QBasic's behavior for first RND(0) might differ slightly based on prior seed state
                # For simplicity, seed with a fixed value then generate if no last_rnd_value
                random.seed(0) # Or some other fixed seed for initial RND(0)
                self.last_rnd_value = random.random()
            return self.last_rnd_value # Return last generated
        else: # num_x > 0 or num_x was non-numeric
            self.last_rnd_value = random.random() # Next in sequence
            return self.last_rnd_value

    def _basic_instr(self, *args) -> int:
        """INSTR([start,] string1$, string2$) - Find substring position."""
        if len(args) == 2:
            start = 1
            string1, string2 = str(args[0]), str(args[1])
        elif len(args) == 3:
            start = int(args[0])
            string1, string2 = str(args[1]), str(args[2])
        else:
            return 0

        if start < 1:
            return 0
        if not string1 or start > len(string1):
            return 0
        if not string2:
            return start  # Empty search string returns start position

        # Convert to 0-based index for Python, then back to 1-based for BASIC
        pos = string1.find(string2, start - 1)
        return pos + 1 if pos >= 0 else 0

    def _basic_string(self, n, char_or_code) -> str:
        """STRING$(n, char$) or STRING$(n, code%) - Generate repeated character."""
        count = int(n)
        if count < 0:
            count = 0
        if isinstance(char_or_code, str):
            # Use first character of string
            char = char_or_code[0] if char_or_code else ""
        else:
            # Use ASCII code
            char = chr(int(char_or_code) % 256)
        return char * count

    def _basic_date(self) -> str:
        """DATE$ - Returns current date as MM-DD-YYYY."""
        from datetime import datetime
        return datetime.now().strftime("%m-%d-%Y")

    def _basic_time(self) -> str:
        """TIME$ - Returns current time as HH:MM:SS."""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")

    def _parse_data_values(self, data_str: str) -> None:
        """Parse DATA statement values and add to data_values list."""
        # Split by commas, respecting quoted strings
        values = []
        current = ""
        in_string = False
        for char in data_str:
            if char == '"':
                in_string = not in_string
                current += char
            elif char == ',' and not in_string:
                values.append(current.strip())
                current = ""
            else:
                current += char
        if current.strip():
            values.append(current.strip())

        # Convert values to appropriate types
        for val in values:
            val = val.strip()
            if val.startswith('"') and val.endswith('"'):
                # String literal
                self.data_values.append(val[1:-1])
            else:
                # Try to convert to number
                try:
                    if '.' in val or 'E' in val.upper():
                        self.data_values.append(float(val))
                    else:
                        self.data_values.append(int(val))
                except ValueError:
                    # Keep as string if not a valid number
                    self.data_values.append(val)

    def mark_dirty(self) -> None: self._dirty = True

    def reset(self, program_lines: List[str]) -> None:
        self.program_lines = []
        self.labels.clear()
        self.variables.clear()
        self.constants.clear()
        self.loop_stack.clear()
        self.for_stack.clear()
        self.gosub_stack.clear()
        _expr_cache.clear()
        _memoized_arg_splits.clear() # Clear arg split cache
        self.if_level = 0
        self.if_skip_level = -1
        self.if_executed.clear()
        self.pc = 0
        self.running = True
        self.text_cursor = (1, 1)
        self.delay_until = 0
        self.current_fg_color = 7 # Default QBasic white
        self.current_bg_color = 0 # Default QBasic black
        self.lpr = (self.screen_width // 2, self.screen_height // 2)
        self.last_key = ""
        self.last_rnd_value = None # Reset last RND value
        # Reset DATA/READ/RESTORE state
        self.data_values.clear()
        self.data_pointer = 0
        self.data_labels.clear()
        # Reset SELECT CASE state
        self.select_stack.clear()

        self._dirty = True
        self._cached_scaled_surface = None

        # First pass: collect DATA statements and labels
        pending_label = None
        for i, line_content in enumerate(program_lines):
            stripped = line_content.strip()
            # Check for label
            label_match = _label_re.match(stripped)
            if label_match:
                pending_label = label_match.group(1).strip().rstrip(':').upper()
                stripped = _label_strip_re.sub("", stripped, count=1).strip()

            # Check for DATA statement
            if stripped.upper().startswith("DATA "):
                # Record the label if there is one pending
                if pending_label and pending_label not in self.data_labels:
                    self.data_labels[pending_label] = len(self.data_values)
                    pending_label = None
                # Parse DATA values
                data_content = stripped[5:].strip()  # Remove "DATA "
                self._parse_data_values(data_content)
            elif stripped:  # Only reset pending_label if there's actual content (not just a label line)
                pending_label = None  # Label wasn't for a DATA statement

        current_pc_index = 0
        for i, line_content in enumerate(program_lines):
            original_line = line_content
            # Handle apostrophe comments on the physical line first
            if "'" in line_content:
                line_content = line_content.split("'", 1)[0]
            
            line_content = line_content.strip()
            if not line_content: continue

            # REM statement (if it's the first thing on the line after stripping)
            if _rem_re.match(line_content): # Check if the stripped line starts with REM
                 continue # Skip the rest of this physical line

            label_match = _label_re.match(line_content)
            if label_match:
                label = label_match.group(1).strip().rstrip(':').upper()
                if label: # Ensure label is not empty
                    if label in self.labels:
                        print(f"Warning: Duplicate label '{label}' at line {i+1}. Using first definition.")
                    else:
                        self.labels[label] = current_pc_index
                # Strip the label part to get the actual command
                line_content = _label_strip_re.sub("", line_content, count=1).strip()
                if not line_content: # Line might have only been a label
                    continue 
            
            self.program_lines.append((current_pc_index, original_line, line_content))
            current_pc_index += 1

        if self.surface is None or self.surface.get_size() != (self.screen_width, self.screen_height):
            self.surface = pygame.Surface((self.screen_width, self.screen_height)).convert()
        self.surface.fill(self.basic_color(self.current_bg_color))
        self.mark_dirty()

    def basic_color(self, c: int) -> Tuple[int, int, int]:
        return self.colors.get(c % 16, self.colors[15]) # Default to white if color out of range

    def inkey(self): 
        k = self.last_key
        self.last_key = ""
        return k

    def point(self, x_expr, y_expr):
        px, py = int(x_expr), int(y_expr)
        if self.surface:
            if 0 <= px < self.screen_width and 0 <= py < self.screen_height:
                pixel_tuple = self.surface.get_at((px, py))
                pixel_rgb = pixel_tuple[:3]
                for num, col_rgb in self.colors.items():
                    if col_rgb == pixel_rgb:
                        return num
                return -1
            return -1
        return -1

    def _scanline_fill(self, x: int, y: int, fill_color: Tuple, border_color: Tuple, target_color: Tuple) -> None:
        """Optimized scanline flood fill algorithm."""
        if not self.surface:
            return

        w, h = self.screen_width, self.screen_height
        get_at = self.surface.get_at
        set_at = self.surface.set_at

        # Use deque for faster pops from left
        stack = deque([(x, y)])
        filled = set()

        while stack:
            cx, cy = stack.pop()

            if (cx, cy) in filled:
                continue

            # Find leftmost point
            lx = cx
            while lx > 0:
                col = get_at((lx - 1, cy))[:3]
                if col == border_color or col == fill_color:
                    break
                lx -= 1

            # Find rightmost point
            rx = cx
            while rx < w - 1:
                col = get_at((rx + 1, cy))[:3]
                if col == border_color or col == fill_color:
                    break
                rx += 1

            # Fill the scanline using pygame.draw.line for speed
            pygame.draw.line(self.surface, fill_color, (lx, cy), (rx, cy))

            # Mark as filled
            for px in range(lx, rx + 1):
                filled.add((px, cy))

            # Check scanlines above and below
            for ny in [cy - 1, cy + 1]:
                if 0 <= ny < h:
                    span_start = None
                    for px in range(lx, rx + 1):
                        if (px, ny) not in filled:
                            col = get_at((px, ny))[:3]
                            if col != border_color and col != fill_color:
                                if span_start is None:
                                    span_start = px
                            else:
                                if span_start is not None:
                                    stack.append((span_start, ny))
                                    span_start = None
                        else:
                            if span_start is not None:
                                stack.append((span_start, ny))
                                span_start = None
                    if span_start is not None:
                        stack.append((span_start, ny))

    def eval_expr(self, expr_str: str):
        if not expr_str.strip():
            return ""

        try:
            conv_expr = convert_basic_expr(expr_str, None)
        except Exception as e:
            print(f"Error converting BASIC expr '{expr_str}': {e}")
            self.running = False
            return 0

        # Use compiled code cache for better performance
        if conv_expr not in _compiled_expr_cache:
            try:
                _compiled_expr_cache[conv_expr] = compile(conv_expr, '<expr>', 'eval')
            except SyntaxError as e:
                print(f"Syntax error compiling '{conv_expr}': {e}")
                self.running = False
                return 0

        # Prepare environment for eval - reuse cached locals dict
        if not hasattr(self, '_eval_locals'):
            self._eval_locals = {}

        eval_locals = self._eval_locals
        eval_locals.clear()

        # Map constants and variables using their Python-mangled names
        for name, value in self.constants.items():
            eval_locals[_basic_to_python_identifier(name)] = value
        for name, value in self.variables.items():
            eval_locals[_basic_to_python_identifier(name)] = value

        try:
            result = eval(_compiled_expr_cache[conv_expr], self.eval_env_funcs, eval_locals)
            return result
        except Exception as e:
            print(f"Error evaluating BASIC expr '{expr_str}' (py: '{conv_expr}'): {e}")
            return 0


    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == KEYDOWN:
            if event.key == pygame.K_UP: self.last_key = chr(0) + "H"
            elif event.key == pygame.K_DOWN: self.last_key = chr(0) + "P"
            elif event.key == pygame.K_LEFT: self.last_key = chr(0) + "K"
            elif event.key == pygame.K_RIGHT: self.last_key = chr(0) + "M"
            # Add more special keys if needed (F-keys, Insert, Delete, Home, End, PgUp, PgDn)
            elif event.key >= pygame.K_F1 and event.key <= pygame.K_F10:
                 self.last_key = chr(0) + chr(58 + (event.key - pygame.K_F1)) # F1=59,...F10=68
            elif event.key == pygame.K_ESCAPE: self.last_key = chr(27)
            elif event.key == pygame.K_RETURN: self.last_key = chr(13)
            elif event.key == pygame.K_TAB: self.last_key = chr(9)
            elif event.key == pygame.K_BACKSPACE: self.last_key = chr(8)
            # For other keys, use their unicode representation if available
            elif event.unicode: # This handles printable characters like 'w', 'S', '1', etc.
                self.last_key = event.unicode
        elif event.type == VIDEORESIZE:
             self.window_width, self.window_height = event.w, event.h
             self._cached_scaled_surface = None # Force redraw of scaled surface
             self.mark_dirty() # Mark main surface as needing redraw (though content hasn't changed)

    def _should_execute(self) -> bool:
        if self.if_skip_level != -1:
            return False
        # Also check SELECT CASE skip state
        if self.select_stack and self.select_stack[-1].get("skip_remaining"):
            return False
        return True

    def _execute_single_statement(self, statement: str, current_pc_num: int) -> bool: # Renamed current_pc to current_pc_num
        statement = statement.strip()
        if not statement: return False # Empty statement part
        
        original_statement_for_error = statement # Keep for error messages
        up_stmt = statement.upper() # For keyword matching

        # Handle apostrophe comments within a multi-statement line
        if statement.startswith("'"):
            return False # This part of the logical line is a comment

        # REM keyword (already handled if it's the first on physical line, but can be after ':')
        if _rem_re.match(statement): # Check if this segment starts with REM
            return False

        # --- IF/ELSE/ENDIF ---
        if up_stmt.startswith("IF "):
            m = _if_re.match(statement) # Use original case statement for regex
            if m:
                cond_part, then_part = m.group(1).strip(), m.group(2).strip()

                currently_executing = self._should_execute()
                condition_met = False
                if currently_executing:
                    eval_result = self.eval_expr(cond_part)
                    if not self.running: return False # Eval error stopped execution
                    condition_met = bool(eval_result)

                if then_part: # Single-line IF THEN statement_block
                    if currently_executing and condition_met:
                        # Execute the 'then_part' as a new mini-line
                        # Need to handle GOTO/GOSUB specially if they are the THEN part
                        if _goto_re.match(then_part):
                            return self._do_goto(_goto_re.match(then_part).group(1).upper())
                        if _gosub_re.match(then_part):
                            return self._do_gosub(_gosub_re.match(then_part).group(1).upper())
                        # Otherwise, execute it as potentially multiple statements
                        return self.execute_logical_line(then_part, current_pc_num) # Returns True if GOTO/GOSUB/DELAY happened
                    return False # Condition not met or not executing this block
                else: # Block IF
                    self.if_level += 1
                    self.if_executed.append(condition_met)  # Track if this IF's condition was true
                    if currently_executing and not condition_met:
                        self.if_skip_level = self.if_level
                    return False # Handled IF, continue to next statement/line
            # else: Malformed IF, will be caught by syntax error at the end

        elif up_stmt.startswith("ELSEIF ") or up_stmt.startswith("ELSE IF "):
            if self.if_level > 0 and len(self.if_executed) >= self.if_level:
                idx = self.if_level - 1
                if self.if_executed[idx]:
                    # Already executed a branch, skip this ELSEIF
                    self.if_skip_level = self.if_level
                elif self.if_skip_level == self.if_level:
                    # Was skipping, check ELSEIF condition
                    elseif_match = re.match(r"ELSE\s*IF\s+(.+?)\s+THEN", statement, re.IGNORECASE)
                    if elseif_match:
                        cond_part = elseif_match.group(1).strip()
                        eval_result = self.eval_expr(cond_part)
                        if not self.running: return False
                        if bool(eval_result):
                            self.if_skip_level = -1  # Start executing
                            self.if_executed[idx] = True  # Mark as executed
                        # else: keep skipping
                    else:
                        print(f"Error: Malformed ELSEIF at PC {current_pc_num}"); self.running = False
                # If if_skip_level is something else, means nested IF is skipping, continue that.
            else:
                print(f"Error: ELSEIF without IF at PC {current_pc_num}"); self.running = False
            return False

        elif up_stmt == "ELSE":
            if self.if_level > 0 and len(self.if_executed) >= self.if_level:
                idx = self.if_level - 1
                if self.if_executed[idx]:
                    # Already executed a branch, skip ELSE
                    self.if_skip_level = self.if_level
                elif self.if_skip_level == self.if_level:
                    # Was skipping, execute ELSE
                    self.if_skip_level = -1
                    self.if_executed[idx] = True
                # If if_skip_level is something else, means nested IF is skipping, continue that.
            else:
                print(f"Error: ELSE without IF at PC {current_pc_num}"); self.running = False
            return False

        elif up_stmt == "END IF":
            if self.if_level > 0:
                if self.if_skip_level == self.if_level: # Was skipping due to this IF level
                    self.if_skip_level = -1 # Stop skipping for this IF
                self.if_level -= 1
                if self.if_executed:
                    self.if_executed.pop()  # Remove the tracking for this IF level
                # If an outer IF was skipping, if_skip_level might be < self.if_level now.
                # Correct it if if_skip_level is now greater than current if_level
                if self.if_skip_level > self.if_level:
                    self.if_skip_level = -1

            else:
                print(f"Error: END IF without IF at PC {current_pc_num}"); self.running = False
            return False

        # If we are in a skipping state for IF blocks, only process control flow for nesting
        # But always process CASE and END SELECT for SELECT CASE blocks
        if self.if_skip_level != -1:
            # Minimal parsing to keep track of block nesting while skipping
            if up_stmt.startswith("FOR "): self.for_stack.append({"placeholder": True, "pc": current_pc_num})
            elif up_stmt.startswith("NEXT"):
                if self.for_stack and self.for_stack[-1].get("placeholder"): self.for_stack.pop()
            elif up_stmt.startswith("DO"): self.loop_stack.append({"placeholder": True, "pc": current_pc_num})
            elif up_stmt.startswith("LOOP"):
                if self.loop_stack and self.loop_stack[-1].get("placeholder"): self.loop_stack.pop()
            elif up_stmt.startswith("WHILE "): self.loop_stack.append({"placeholder": True, "type": "WHILE", "pc": current_pc_num})
            elif up_stmt == "WEND":
                if self.loop_stack and self.loop_stack[-1].get("placeholder") and self.loop_stack[-1].get("type") == "WHILE":
                    self.loop_stack.pop()
            elif up_stmt.startswith("SELECT CASE "): self.select_stack.append({"placeholder": True})
            elif up_stmt == "END SELECT":
                if self.select_stack and self.select_stack[-1].get("placeholder"):
                    self.select_stack.pop()
            # No other statements are processed
            return False

        # If we are in SELECT CASE skip mode, still need to process CASE and END SELECT
        if self.select_stack and self.select_stack[-1].get("skip_remaining"):
            # Process CASE statements
            m_case = _case_re.fullmatch(statement)
            if m_case:
                select_info = self.select_stack[-1]
                case_expr = m_case.group(1).strip()

                if select_info.get("case_matched"):
                    select_info["skip_remaining"] = True
                    return False

                select_info["skip_remaining"] = False
                if case_expr.upper() == "ELSE":
                    select_info["case_matched"] = True
                elif self._case_matches(select_info["test_value"], case_expr, current_pc_num):
                    select_info["case_matched"] = True
                else:
                    select_info["skip_remaining"] = True
                return False

            # Process END SELECT
            if _end_select_re.fullmatch(up_stmt):
                self.select_stack.pop()
                return False

            # Skip other statements
            return False


        # --- Actual commands if _should_execute() is true ---
        if _cls_re.fullmatch(up_stmt):
            if self.surface:
                self.surface.fill(self.basic_color(self.current_bg_color))
                self.mark_dirty()
                self.text_cursor = (1,1) # Reset cursor to top-left
            return False
        
        m_color = _color_re.fullmatch(statement)
        if m_color:
            fg_expr, bg_expr = m_color.group(1), m_color.group(2)
            if fg_expr and fg_expr.strip():
                val = self.eval_expr(fg_expr.strip())
                if not self.running: return False
                self.current_fg_color = int(val)
            if bg_expr and bg_expr.strip():
                val = self.eval_expr(bg_expr.strip())
                if not self.running: return False
                self.current_bg_color = int(val)
                # QBasic CLS after BG color change is implicit by some; here it's explicit
                # self.surface.fill(self.basic_color(self.current_bg_color)) 
                # self.mark_dirty()
            return False

        m_screen = _screen_re.fullmatch(statement) # Use fullmatch for commands like SCREEN
        if m_screen:
            mode = int(m_screen.group(1)) # Already number from regex
            # Simplified: SCREEN 13 is 320x200, other modes might map to initial or default
            if mode == 13:
                self.screen_width, self.screen_height = 320, 200
            # else: use default or other predefined modes
            
            if self.surface is None or self.surface.get_size() != (self.screen_width, self.screen_height):
                 self.surface = pygame.Surface((self.screen_width, self.screen_height)).convert()
                 self._cached_scaled_surface = None # Force rescale
            
            self.surface.fill(self.basic_color(self.current_bg_color)) #SCREEN implies CLS
            self.text_cursor = (1,1)
            self.lpr = (self.screen_width // 2, self.screen_height // 2) # Reset LPR
            self.mark_dirty()
            return False

        m_const = _const_re.fullmatch(statement)
        if m_const:
             var_name, val_expr = m_const.group(1).strip().upper(), m_const.group(2).strip()
             if var_name in self.variables or var_name in self.constants:
                 print(f"Error: Identifier '{var_name}' redefined at PC {current_pc_num}"); self.running = False; return False
             
             val = self.eval_expr(val_expr)
             if not self.running: return False # Eval error
             self.constants[var_name] = val
             return False

        m_dim = _dim_re.fullmatch(statement)
        if m_dim:
            var_name_orig, idx_str = m_dim.group(1).strip(), m_dim.group(2).strip()
            var_name = var_name_orig.upper()
            if var_name in self.constants:
                print(f"Error: Cannot DIM constant '{var_name}' at PC {current_pc_num}"); self.running = False; return False
            
            try:
                # DIM A(10) means indices 0-10. So size is N+1.
                dims = [int(self.eval_expr(idx.strip())) + 1 for idx in idx_str.split(',')]
                if not self.running: return False

                default_val = "" if var_name.endswith("$") else 0
                
                if len(dims) == 1:
                    self.variables[var_name] = [default_val] * dims[0]
                elif len(dims) == 2:
                    self.variables[var_name] = [[default_val] * dims[1] for _ in range(dims[0])]
                # Add more dimensions if needed
                else:
                    print(f"Error: Unsupported array dimensions ({len(dims)}) for '{var_name}' at PC {current_pc_num}"); self.running = False
            except Exception as e:
                print(f"Error in DIM statement for '{var_name_orig}': {e} at PC {current_pc_num}"); self.running = False
            return False

        m_for = _for_re.fullmatch(statement)
        if m_for:
            var_name_orig = m_for.group(1).strip()
            var_name = var_name_orig.upper()
            start_expr, end_expr = m_for.group(2).strip(), m_for.group(3).strip()
            step_expr = m_for.group(4).strip() if m_for.group(4) else "1"

            if var_name in self.constants:
                print(f"Error: Loop control variable '{var_name_orig}' is a constant at PC {current_pc_num}"); self.running = False; return False
            
            start_val = self.eval_expr(start_expr)
            if not self.running: return False
            end_val = self.eval_expr(end_expr)
            if not self.running: return False
            step_val = self.eval_expr(step_expr)
            if not self.running: return False

            self.variables[var_name] = start_val
            self.for_stack.append({
                "var": var_name, "end": end_val, "step": step_val,
                "loop_pc": self.pc  # PC of the line AFTER FOR (loop body start)
            })
            
            # Check if loop should be skipped entirely
            if (step_val > 0 and start_val > end_val) or \
               (step_val < 0 and start_val < end_val) or \
               (step_val == 0): # Step 0 would be infinite loop if condition met
                self._skip_for_block(current_pc_num) # This will advance self.pc
                return True # Indicates PC has been modified by skipping
            return False

        m_next = _next_re.fullmatch(statement)
        if m_next:
             next_var_orig = m_next.group(1).strip() if m_next.group(1) else None
             next_var = next_var_orig.upper() if next_var_orig else None

             if not self.for_stack:
                 print(f"Error: NEXT without FOR at PC {current_pc_num}"); self.running = False; return False
            
             loop_info = self.for_stack[-1]
             if loop_info.get("placeholder"): # Should not happen if _should_execute is true
                 print(f"Error: NEXT encountered placeholder FOR loop info at PC {current_pc_num}"); self.running = False; self.for_stack.pop(); return False

             active_for_var = loop_info["var"]
             if next_var and next_var != active_for_var:
                 print(f"Error: NEXT variable '{next_var_orig}' does not match FOR variable '{active_for_var}' at PC {current_pc_num}"); self.running = False; return False
            
             current_val = self.variables.get(active_for_var, 0) # Default to 0 if var somehow missing
             new_val = current_val + loop_info["step"]
             self.variables[active_for_var] = new_val

             continue_loop = False
             if loop_info["step"] > 0:
                 continue_loop = new_val <= loop_info["end"]
             elif loop_info["step"] < 0:
                 continue_loop = new_val >= loop_info["end"]
             # If step is 0, loop continues if it started (handled at FOR)

             if continue_loop:
                 self.pc = loop_info["loop_pc"] # Jump back to FOR statement's PC + 1 (handled by main loop)
                 return True # PC changed
             else:
                 self.for_stack.pop() # End of loop
             return False

        # EXIT FOR - break out of innermost FOR loop
        if _exit_for_re.fullmatch(statement):
            if not self.for_stack:
                print(f"Error: EXIT FOR without FOR at PC {current_pc_num}"); self.running = False; return False
            loop_info = self.for_stack[-1]
            if loop_info.get("placeholder"):
                print(f"Error: EXIT FOR encountered placeholder FOR info at PC {current_pc_num}"); self.running = False; self.for_stack.pop(); return False
            self.for_stack.pop()  # Remove the FOR loop from stack
            # Skip to the corresponding NEXT statement
            self._skip_to_next(current_pc_num)
            return True  # PC changed

        # EXIT DO - break out of innermost DO loop
        if _exit_do_re.fullmatch(statement):
            if not self.loop_stack:
                print(f"Error: EXIT DO without DO at PC {current_pc_num}"); self.running = False; return False
            loop_info = self.loop_stack[-1]
            if loop_info.get("placeholder"):
                print(f"Error: EXIT DO encountered placeholder DO info at PC {current_pc_num}"); self.running = False; self.loop_stack.pop(); return False
            self.loop_stack.pop()  # Remove the DO loop from stack
            # Skip to the corresponding LOOP statement
            self._skip_to_loop(current_pc_num)
            return True  # PC changed

        m_assign = _assign_re.fullmatch(statement)
        if m_assign:
            lhs, rhs_expr = m_assign.group(1).strip(), m_assign.group(2).strip()
            
            # Check if LHS is an array assignment
            lhs_array_match = _assign_lhs_array_re.fullmatch(lhs) # Check original LHS for array pattern

            val_to_assign = self.eval_expr(rhs_expr)
            if not self.running: return False # Eval error

            if lhs_array_match:
                var_name_orig, idx_str = lhs_array_match.group(1), lhs_array_match.group(2)
                var_name = var_name_orig.upper()

                if var_name in self.constants:
                    print(f"Error: Cannot assign to constant array '{var_name_orig}' at PC {current_pc_num}"); self.running = False; return False
                if var_name not in self.variables or not isinstance(self.variables[var_name], list):
                    print(f"Error: Array '{var_name_orig}' not DIMensioned or not an array at PC {current_pc_num}"); self.running = False; return False

                try:
                    indices_list = _split_args(idx_str)
                    indices = [int(round(float(self.eval_expr(idx.strip())))) for idx in indices_list]
                    if not self.running: return False

                    target_array_level = self.variables[var_name]
                    for i in range(len(indices) - 1):
                        target_array_level = target_array_level[indices[i]]
                    target_array_level[indices[-1]] = val_to_assign
                except IndexError:
                    print(f"Error: Array index out of bounds for '{lhs}' at PC {current_pc_num}"); self.running = False
                except TypeError: # e.g. trying to index a non-list (if multi-dim setup failed)
                    print(f"Error: Incorrect array dimension access for '{lhs}' at PC {current_pc_num}"); self.running = False
                except Exception as e:
                    print(f"Error during array assignment for '{lhs} = {rhs_expr}': {e} at PC {current_pc_num}"); self.running = False
            else: # Scalar assignment
                var_name = lhs.upper()
                if var_name in self.constants:
                    print(f"Error: Cannot assign to constant '{lhs}' at PC {current_pc_num}"); self.running = False; return False
                self.variables[var_name] = val_to_assign
            return False
            
        m_locate = _locate_re.fullmatch(statement)
        if m_locate:
             row_expr, col_expr = m_locate.group(1), m_locate.group(2)
             try:
                 font_h = self.font.get_height() if self.font else FONT_SIZE
                 font_w = self.font.size(" ")[0] if self.font and self.font.size(" ")[0] > 0 else (FONT_SIZE // 2)
                 
                 max_r = (self.screen_height // font_h) if font_h > 0 else 25
                 max_c = (self.screen_width // font_w) if font_w > 0 else 80

                 # If row_expr is present, evaluate it; otherwise, use current cursor row.
                 # If col_expr is present, evaluate it. If row_expr also present, use evaluated col.
                 # If col_expr present but row_expr not, use current cursor col (QB behavior is complex here, simplifying)
                 # QBasic: LOCATE ,C -> current R, new C. LOCATE R, -> new R, col 1. LOCATE R -> new R, current C (if prev output ended line).

                 new_row, new_col = self.text_cursor[1], self.text_cursor[0]

                 if row_expr and row_expr.strip():
                     val = self.eval_expr(row_expr.strip())
                     if not self.running: return False
                     new_row = int(val)
                     if not (col_expr and col_expr.strip()): # LOCATE R (implies col 1 or current col)
                         new_col = 1 # Common: LOCATE R implies LOCATE R,1 or uses previous column if line didn't wrap
                 
                 if col_expr and col_expr.strip():
                     val = self.eval_expr(col_expr.strip())
                     if not self.running: return False
                     new_col = int(val)

                 self.text_cursor = (max(1, min(new_col, max_c)), max(1, min(new_row, max_r)))
             except Exception as e:
                 print(f"Error in LOCATE parameters '{statement}': {e} at PC {current_pc_num}")
             return False

        m_print = _print_re.fullmatch(statement)
        if m_print:
            content = m_print.group(1).strip() if m_print.group(1) else ""
            
            # Split content by print separators (',' and ';') while respecting quotes
            parts = []
            current_part = ""
            in_string_literal = False
            for char in content:
                if char == '"':
                    in_string_literal = not in_string_literal
                
                if not in_string_literal and (char == ';' or char == ','):
                    if current_part: parts.append(current_part.strip())
                    parts.append(char) # Keep separator as a part
                    current_part = ""
                else:
                    current_part += char
            if current_part: parts.append(current_part.strip())

            output_buffer = ""
            x_render_pos = (self.text_cursor[0] - 1) * (self.font.size(" ")[0] if self.font else FONT_SIZE // 2)
            y_render_pos = (self.text_cursor[1] - 1) * (self.font.get_height() if self.font else FONT_SIZE)

            for i, part_expr_or_sep in enumerate(parts):
                is_last_part_in_print_stmt = (i == len(parts) - 1)

                if part_expr_or_sep == ';':
                    # Moves cursor directly after printed item. If buffer has space, remove it.
                    if output_buffer.endswith(" "):
                         output_buffer = output_buffer[:-1]
                elif part_expr_or_sep == ',':
                    # Move to next print zone (14 chars wide)
                    len_output_chars = len(output_buffer) # Approximate, as fixed-width font assumed
                    chars_in_current_zone = len_output_chars % PRINT_TAB_WIDTH
                    spaces_to_add = PRINT_TAB_WIDTH - chars_in_current_zone
                    if spaces_to_add == 0 and len_output_chars > 0 : spaces_to_add = PRINT_TAB_WIDTH # if exactly on boundary, jump to next
                    output_buffer += " " * spaces_to_add
                else: # It's an expression
                    val = self.eval_expr(part_expr_or_sep)
                    if not self.running: return False

                    s_val = str(val)
                    if isinstance(val, (int, float)): # Numbers: space if positive, then number, then space
                        s_val = (" " if val >= 0 else "") + s_val + " "
                    output_buffer += s_val
            
            # Actual rendering of the fully formed output_buffer
            if self.surface and self.font and output_buffer:
                f_w = self.font.size(" ")[0] if self.font.size(" ")[0] > 0 else FONT_SIZE //2
                f_h = self.font.get_height()

                # Render the text
                try:
                    text_surface = self.font.render(output_buffer, True, self.basic_color(self.current_fg_color), self.basic_color(self.current_bg_color))
                    # Ensure background is explicitly drawn for the text area, render() with bg_color does this.
                    
                    # Blit, respecting screen boundaries
                    blit_width = min(text_surface.get_width(), self.screen_width - x_render_pos)
                    blit_height = min(text_surface.get_height(), self.screen_height - y_render_pos)

                    if blit_width > 0 and blit_height > 0:
                         self.surface.blit(text_surface, (x_render_pos, y_render_pos), area=pygame.Rect(0,0,blit_width, blit_height))
                         self.mark_dirty()
                except pygame.error as e:
                     print(f"Font render error: {e} for text '{output_buffer}'")


            # Update text cursor position
            # Calculate new cursor column based on character width
            char_w = (self.font.size(" ")[0] if self.font and self.font.size(" ")[0] > 0 else FONT_SIZE // 2)
            char_h = (self.font.get_height() if self.font else FONT_SIZE)
            max_cols_on_screen = (self.screen_width // char_w) if char_w > 0 else 80
            max_rows_on_screen = (self.screen_height // char_h) if char_h > 0 else 25

            new_cursor_col = self.text_cursor[0] + len(output_buffer) # len() is char count
            new_cursor_row = self.text_cursor[1]

            ends_with_separator = content.endswith(';') or content.endswith(',')
            if not ends_with_separator: # No trailing separator, move to next line
                new_cursor_col = 1
                new_cursor_row += 1
            
            if new_cursor_col > max_cols_on_screen : # Wrap column if it exceeds screen width
                new_cursor_col = 1
                new_cursor_row +=1 # This might need to be smarter about screen scrolling

            if new_cursor_row > max_rows_on_screen: # Handle scrolling or clamp
                new_cursor_row = max_rows_on_screen # Simple clamp, QBasic would scroll
                # TODO: Implement screen scrolling if new_cursor_row > max_rows_on_screen
                # For now, just clamp it. If we were at max_rows_on_screen and wrapped,
                # new_cursor_col would be 1, new_cursor_row max_rows_on_screen.
                if not ends_with_separator: # If we were at max row and printed a full line
                    # Perform a simple scroll:
                    if self.surface and char_h > 0:
                        # Copy the area to scroll (subsurface locks parent, so copy first)
                        scroll_area = self.surface.subsurface((0, char_h, self.screen_width, self.screen_height - char_h)).copy()
                        self.surface.blit(scroll_area, (0,0))
                        self.surface.fill(self.basic_color(self.current_bg_color), (0, self.screen_height - char_h, self.screen_width, char_h))
                        self.mark_dirty()
                        new_cursor_row = max_rows_on_screen # Stay on the new last line


            self.text_cursor = (new_cursor_col, new_cursor_row)
            return False

        m_line = _line_re.match(statement)
        if m_line and self.surface:
            try:
                sx_e, sy_e, ex_e, ey_e = m_line.group(1), m_line.group(2), m_line.group(3), m_line.group(4)
                options_str = m_line.group(5)

                start_x, start_y = self.lpr # Default to last point referenced (LPR)
                if sx_e is not None and sy_e is not None: # sx_e can be None if (x,y)- form
                    start_x = int(self.eval_expr(sx_e.strip()))
                    start_y = int(self.eval_expr(sy_e.strip()))
                    if not self.running: return False
                
                end_x = int(self.eval_expr(ex_e.strip()))
                end_y = int(self.eval_expr(ey_e.strip()))
                if not self.running: return False

                color_index = self.current_fg_color
                box_mode = None # None, "B", or "BF"

                if options_str:
                    opts_parts = [opt.strip().upper() for opt in options_str.split(',')]
                    # First part could be color
                    if opts_parts[0] and not opts_parts[0] in ("B", "BF"):
                        # Need to eval original case for expression
                        original_color_expr = options_str.split(',')[0].strip()
                        color_index = int(self.eval_expr(original_color_expr))
                        if not self.running: return False
                        opts_parts.pop(0) # Color handled
                    
                    for opt_part in opts_parts:
                        if opt_part == "B": box_mode = "B"
                        elif opt_part == "BF": box_mode = "BF" # BF takes precedence over B
                
                py_color = self.basic_color(color_index)

                if box_mode == "BF":
                    rect = pygame.Rect(min(start_x, end_x), min(start_y, end_y), abs(end_x - start_x) + 1, abs(end_y - start_y) + 1)
                    pygame.draw.rect(self.surface, py_color, rect, 0) # 0 for filled
                elif box_mode == "B":
                    rect = pygame.Rect(min(start_x, end_x), min(start_y, end_y), abs(end_x - start_x) + 1, abs(end_y - start_y) + 1)
                    pygame.draw.rect(self.surface, py_color, rect, 1) # 1 for outline
                else: # Simple line
                    pygame.draw.line(self.surface, py_color, (start_x, start_y), (end_x, end_y), 1)
                
                self.lpr = (end_x, end_y) # Update LPR
                self.mark_dirty()
            except Exception as e:
                print(f"Error in LINE statement '{statement}': {e} at PC {current_pc_num}"); self.running = False
            return False

        m_circle = _circle_re.match(statement)
        if m_circle and self.surface:
            try:
                # CIRCLE (x,y), radius [,color [,start, end [,aspect [,F]]]]
                cx_e, cy_e, r_e = m_circle.group(1), m_circle.group(2), m_circle.group(3)
                color_e, start_e, end_e, aspect_e = m_circle.group(4), m_circle.group(5), m_circle.group(6), m_circle.group(7)
                fill_e = m_circle.group(8)  # "F" or "BF" for filled

                center_x = int(self.eval_expr(cx_e.strip()))
                center_y = int(self.eval_expr(cy_e.strip()))
                radius = int(self.eval_expr(r_e.strip()))
                if not self.running or radius < 0: return False

                color_idx = self.current_fg_color
                if color_e and color_e.strip():
                    color_idx = int(self.eval_expr(color_e.strip()))
                    if not self.running: return False

                py_color = self.basic_color(color_idx)

                # Check for fill parameter
                is_filled = fill_e and fill_e.strip().upper() in ("F", "BF")

                # Pygame draw.circle does not support start/end angles for arcs directly.
                # For simplicity, ignoring start, end, aspect for now.
                if radius > 0:  # Pygame needs positive radius
                    if is_filled:
                        pygame.draw.circle(self.surface, py_color, (center_x, center_y), radius, 0)  # 0 for filled
                    else:
                        pygame.draw.circle(self.surface, py_color, (center_x, center_y), radius, 1)  # 1 for outline
                elif radius == 0:  # Draw a single point
                     if 0 <= center_x < self.screen_width and 0 <= center_y < self.screen_height:
                        self.surface.set_at((center_x, center_y), py_color)

                self.lpr = (center_x, center_y)
                self.mark_dirty()
            except Exception as e:
                print(f"Error in CIRCLE statement '{statement}': {e} at PC {current_pc_num}"); self.running = False
            return False

        m_paint = _paint_re.match(statement)
        if m_paint and self.surface:
             try:
                px_e, py_e = m_paint.group(1), m_paint.group(2)
                fill_color_e, border_color_e = m_paint.group(3), m_paint.group(4)

                start_x = int(self.eval_expr(px_e.strip()))
                start_y = int(self.eval_expr(py_e.strip()))
                if not self.running: return False

                fill_color_idx = self.current_fg_color
                if fill_color_e and fill_color_e.strip():
                    fill_color_idx = int(self.eval_expr(fill_color_e.strip()))
                    if not self.running: return False

                border_color_idx = fill_color_idx
                if border_color_e and border_color_e.strip():
                    border_color_idx = int(self.eval_expr(border_color_e.strip()))
                    if not self.running: return False

                if not (0 <= start_x < self.screen_width and 0 <= start_y < self.screen_height):
                    return False

                py_fill_color = self.basic_color(fill_color_idx)
                py_border_color = self.basic_color(border_color_idx)

                target_color_tuple = self.surface.get_at((start_x, start_y))[:3]

                if target_color_tuple == py_border_color or target_color_tuple == py_fill_color:
                    return False

                # Optimized scanline flood fill algorithm
                self._scanline_fill(start_x, start_y, py_fill_color, py_border_color, target_color_tuple)
                self.mark_dirty()
             except Exception as e:
                 print(f"Error in PAINT statement '{statement}': {e} at PC {current_pc_num}"); self.running = False
             return False

        m_pset = _pset_re.match(statement)
        if m_pset and self.surface:
            try:
                px_e, py_e = m_pset.group(1), m_pset.group(2)
                color_e = m_pset.group(3)

                px = int(self.eval_expr(px_e.strip()))
                py = int(self.eval_expr(py_e.strip()))
                if not self.running: return False

                color_idx = self.current_fg_color
                if color_e and color_e.strip():
                    color_idx = int(self.eval_expr(color_e.strip()))
                    if not self.running: return False
                
                if 0 <= px < self.screen_width and 0 <= py < self.screen_height:
                    self.surface.set_at((px, py), self.basic_color(color_idx))
                    self.lpr = (px, py) # Update LPR
                    self.mark_dirty()
            except Exception as e:
                print(f"Error in PSET statement '{statement}': {e} at PC {current_pc_num}"); self.running = False
            return False

        if _goto_re.fullmatch(statement):
            return self._do_goto(_goto_re.fullmatch(statement).group(1).upper()) # PC changed
        
        if _gosub_re.fullmatch(statement):
            return self._do_gosub(_gosub_re.fullmatch(statement).group(1).upper()) # PC changed

        if _return_re.fullmatch(up_stmt):
            if not self.gosub_stack:
                print(f"Error: RETURN without GOSUB at PC {current_pc_num}"); self.running = False; return False
            self.pc = self.gosub_stack.pop() # Set PC for next iteration
            return True # PC changed

        m_do = _do_re.fullmatch(statement)
        if m_do:
            loop_type, cond_expr = (m_do.group(1).upper() if m_do.group(1) else None), \
                                   (m_do.group(2).strip() if m_do.group(2) else None)
            
            skip_loop_body = False
            if cond_expr: # DO WHILE or DO UNTIL (pre-condition)
                cond_met = bool(self.eval_expr(cond_expr))
                if not self.running: return False
                if loop_type == "WHILE" and not cond_met: skip_loop_body = True
                if loop_type == "UNTIL" and cond_met: skip_loop_body = True
            
            self.loop_stack.append({
                "type": "DO",
                "start_pc": self.pc,  # PC of the line AFTER DO (loop body start)
                "pre_cond_expr": cond_expr,
                "pre_cond_type": loop_type
            })

            if skip_loop_body:
                self._skip_loop_block(current_pc_num)
                return True # PC changed by skipping
            return False

        m_loop = _loop_re.fullmatch(statement)
        if m_loop:
            if not self.loop_stack or self.loop_stack[-1].get("type") != "DO":
                print(f"Error: LOOP without DO at PC {current_pc_num}"); self.running = False; return False
            
            loop_info = self.loop_stack[-1]
            if loop_info.get("placeholder"): # Should not happen if _should_execute is true
                 print(f"Error: LOOP encountered placeholder DO info at PC {current_pc_num}"); self.running = False; self.loop_stack.pop(); return False

            post_loop_type, post_cond_expr = (m_loop.group(1).upper() if m_loop.group(1) else None), \
                                             (m_loop.group(2).strip() if m_loop.group(2) else None)
            
            exit_this_loop = False
            if post_cond_expr: # LOOP WHILE or LOOP UNTIL (post-condition)
                cond_met = bool(self.eval_expr(post_cond_expr))
                if not self.running: return False
                if post_loop_type == "WHILE" and not cond_met: exit_this_loop = True
                if post_loop_type == "UNTIL" and cond_met: exit_this_loop = True
            
            if exit_this_loop:
                self.loop_stack.pop()
                return False

            # If not exiting due to post-condition, check pre-condition of DO if it exists
            continue_this_loop = True
            if loop_info["pre_cond_expr"]:
                pre_cond_met = bool(self.eval_expr(loop_info["pre_cond_expr"]))
                if not self.running: return False
                if loop_info["pre_cond_type"] == "WHILE" and not pre_cond_met: continue_this_loop = False
                if loop_info["pre_cond_type"] == "UNTIL" and pre_cond_met: continue_this_loop = False
            
            if continue_this_loop:
                self.pc = loop_info["start_pc"] # Jump to DO statement's PC
                return True # PC changed
            else:
                self.loop_stack.pop() # Loop terminates
            return False

        m_delay = _delay_re.fullmatch(statement)
        if m_delay:
            try:
                delay_seconds = float(self.eval_expr(m_delay.group(1).strip()))
                if not self.running: return False
                if delay_seconds > 0:
                    self.delay_until = pygame.time.get_ticks() + int(delay_seconds * 1000)
                    return True # Special return to indicate interpreter should pause till delay_until
            except ValueError:
                print(f"Error: Invalid _DELAY/SLEEP duration '{m_delay.group(1)}' at PC {current_pc_num}")
            return False # Continue if delay is zero or invalid

        m_randomize = _randomize_re.fullmatch(statement)
        if m_randomize:
            seed_expr = m_randomize.group(1).strip() if m_randomize.group(1) else None
            if seed_expr:
                if seed_expr.upper() == "TIMER":
                    random.seed(time.time())
                else:
                    seed_val = self.eval_expr(seed_expr)
                    if not self.running: return False
                    random.seed(seed_val)
            else: # RANDOMIZE without argument, QBasic often prompts user or uses fixed sequence start.
                  # Here, just re-seed with current time for some randomness.
                random.seed(time.time()) 
            self.last_rnd_value = None # RND sequence is reset
            return False

        # --- SWAP statement ---
        m_swap = _swap_re.fullmatch(statement)
        if m_swap:
            var1_str, var2_str = m_swap.group(1).strip(), m_swap.group(2).strip()
            try:
                # Get current values
                val1 = self.eval_expr(var1_str)
                val2 = self.eval_expr(var2_str)
                if not self.running: return False

                # Assign swapped values
                self._assign_variable(var1_str, val2, current_pc_num)
                self._assign_variable(var2_str, val1, current_pc_num)
            except Exception as e:
                print(f"Error in SWAP statement '{statement}': {e} at PC {current_pc_num}")
                self.running = False
            return False

        # --- WHILE statement ---
        m_while = _while_re.fullmatch(statement)
        if m_while:
            cond_expr = m_while.group(1).strip()
            cond_met = bool(self.eval_expr(cond_expr))
            if not self.running: return False

            self.loop_stack.append({
                "type": "WHILE",
                "start_pc": self.pc,  # PC of the line AFTER WHILE
                "cond_expr": cond_expr
            })

            if not cond_met:
                self._skip_while_block(current_pc_num)
                return True  # PC changed by skipping
            return False

        # --- WEND statement ---
        if _wend_re.fullmatch(up_stmt):
            if not self.loop_stack or self.loop_stack[-1].get("type") != "WHILE":
                print(f"Error: WEND without WHILE at PC {current_pc_num}")
                self.running = False
                return False

            loop_info = self.loop_stack[-1]
            cond_met = bool(self.eval_expr(loop_info["cond_expr"]))
            if not self.running: return False

            if cond_met:
                self.pc = loop_info["start_pc"]  # Jump back to start of WHILE body
                return True
            else:
                self.loop_stack.pop()
            return False

        # --- SELECT CASE statement ---
        m_select = _select_case_re.fullmatch(statement)
        if m_select:
            test_expr = m_select.group(1).strip()
            test_value = self.eval_expr(test_expr)
            if not self.running: return False

            self.select_stack.append({
                "test_value": test_value,
                "case_matched": False,
                "skip_remaining": False
            })
            return False

        # --- CASE statement ---
        m_case = _case_re.fullmatch(statement)
        if m_case:
            if not self.select_stack:
                print(f"Error: CASE without SELECT CASE at PC {current_pc_num}")
                self.running = False
                return False

            select_info = self.select_stack[-1]
            case_expr = m_case.group(1).strip()

            # If we already matched and executed a case, skip all remaining cases
            if select_info["case_matched"]:
                select_info["skip_remaining"] = True
                return False

            # Reset skip_remaining - we're at a new CASE
            select_info["skip_remaining"] = False

            # Handle CASE ELSE
            if case_expr.upper() == "ELSE":
                select_info["case_matched"] = True
                return False

            # Check if this case matches
            if self._case_matches(select_info["test_value"], case_expr, current_pc_num):
                select_info["case_matched"] = True
            else:
                select_info["skip_remaining"] = True
            return False

        # --- END SELECT statement ---
        if _end_select_re.fullmatch(up_stmt):
            if not self.select_stack:
                print(f"Error: END SELECT without SELECT CASE at PC {current_pc_num}")
                self.running = False
                return False
            self.select_stack.pop()
            return False

        # --- DATA statement (skip, already processed in reset) ---
        if up_stmt.startswith("DATA "):
            return False

        # --- READ statement ---
        m_read = _read_re.fullmatch(statement)
        if m_read:
            var_list = m_read.group(1).strip()
            var_names = [v.strip() for v in var_list.split(',')]
            for var_name in var_names:
                if self.data_pointer >= len(self.data_values):
                    print(f"Error: Out of DATA at PC {current_pc_num}")
                    self.running = False
                    return False
                value = self.data_values[self.data_pointer]
                self.data_pointer += 1
                self._assign_variable(var_name, value, current_pc_num)
                if not self.running: return False
            return False

        # --- RESTORE statement ---
        m_restore = _restore_re.fullmatch(statement)
        if m_restore:
            label = m_restore.group(1)
            if label:
                label = label.upper()
                if label in self.data_labels:
                    self.data_pointer = self.data_labels[label]
                else:
                    print(f"Error: DATA label '{label}' not found at PC {current_pc_num}")
                    self.running = False
            else:
                self.data_pointer = 0  # Reset to beginning
            return False

        if _end_re.fullmatch(up_stmt):
            self.running = False
            return False # END statement, stop execution

        # If no pattern matched, it's a syntax error or unrecognized command
        print(f"Syntax Error or Unrecognized Command: '{original_statement_for_error}' at PC {current_pc_num} (Original line: {self.program_lines[current_pc_num][1]})")
        self.running = False
        return False


    def _do_goto(self, label: str) -> bool:
        target_pc_idx = self.labels.get(label)
        if target_pc_idx is not None:
            self.pc = target_pc_idx # Set PC for the next line to be executed
            return True # Indicate PC has changed
        print(f"Error: Label '{label}' not found for GOTO at PC {self.pc-1}."); self.running = False; return False

    def _do_gosub(self, label: str) -> bool:
        target_pc_idx = self.labels.get(label)
        if target_pc_idx is not None:
            self.gosub_stack.append(self.pc) # Push current NEXT pc to stack
            self.pc = target_pc_idx # Set PC for GOSUB target
            return True # Indicate PC has changed
        print(f"Error: Label '{label}' not found for GOSUB at PC {self.pc-1}."); self.running = False; return False

    def _assign_variable(self, var_str: str, value: Any, pc: int) -> None:
        """Assign a value to a variable (scalar or array element)."""
        var_str = var_str.strip()
        # Check if it's an array assignment
        array_match = _assign_lhs_array_re.fullmatch(var_str)
        if array_match:
            var_name_orig, idx_str = array_match.group(1), array_match.group(2)
            var_name = var_name_orig.upper()
            if var_name in self.constants:
                print(f"Error: Cannot assign to constant array '{var_name_orig}' at PC {pc}")
                self.running = False
                return
            if var_name not in self.variables or not isinstance(self.variables[var_name], list):
                print(f"Error: Array '{var_name_orig}' not DIMensioned at PC {pc}")
                self.running = False
                return
            try:
                indices = [int(round(float(self.eval_expr(idx.strip())))) for idx in _split_args(idx_str)]
                if not self.running: return
                target = self.variables[var_name]
                for i in range(len(indices) - 1):
                    target = target[indices[i]]
                target[indices[-1]] = value
            except (IndexError, TypeError) as e:
                print(f"Error: Array index error for '{var_str}': {e} at PC {pc}")
                self.running = False
        else:
            # Scalar variable
            var_name = var_str.upper()
            if var_name in self.constants:
                print(f"Error: Cannot assign to constant '{var_str}' at PC {pc}")
                self.running = False
                return
            self.variables[var_name] = value

    def _case_matches(self, test_value: Any, case_expr: str, pc: int) -> bool:
        """Check if a CASE expression matches the test value."""
        case_expr = case_expr.strip()

        # Handle IS comparisons: CASE IS >= 10, CASE IS < 5, etc.
        is_match = re.match(r"IS\s*([<>=!]+)\s*(.+)", case_expr, re.IGNORECASE)
        if is_match:
            operator = is_match.group(1)
            compare_value = self.eval_expr(is_match.group(2).strip())
            if not self.running: return False
            if operator == ">":
                return test_value > compare_value
            elif operator == "<":
                return test_value < compare_value
            elif operator == ">=":
                return test_value >= compare_value
            elif operator == "<=":
                return test_value <= compare_value
            elif operator == "=" or operator == "==":
                return test_value == compare_value
            elif operator == "<>" or operator == "!=":
                return test_value != compare_value
            return False

        # Handle ranges: CASE 1 TO 5
        to_match = re.match(r"(.+)\s+TO\s+(.+)", case_expr, re.IGNORECASE)
        if to_match:
            low_value = self.eval_expr(to_match.group(1).strip())
            high_value = self.eval_expr(to_match.group(2).strip())
            if not self.running: return False
            return low_value <= test_value <= high_value

        # Handle comma-separated values: CASE 1, 3, 5
        if ',' in case_expr:
            values = [v.strip() for v in case_expr.split(',')]
            for val_expr in values:
                val = self.eval_expr(val_expr)
                if not self.running: return False
                if test_value == val:
                    return True
            return False

        # Simple value comparison
        case_value = self.eval_expr(case_expr)
        if not self.running: return False
        return test_value == case_value

    def _skip_while_block(self, start_pc_num: int) -> None:
        """Skip to the matching WEND statement."""
        if self.loop_stack and self.loop_stack[-1].get("type") == "WHILE":
            self.loop_stack.pop()
        self._skip_block("WHILE", "WEND", start_pc_num)

    def step_line(self) -> bool:
        """ Executes the current program line (self.pc) and advances self.pc.
            Returns True if execution should pause (e.g. DELAY) or PC jumped.
        """
        if self.pc >= len(self.program_lines):
            self.running = False
            return False
        
        pc_of_this_line, _, logical_line_content = self.program_lines[self.pc]
        self.pc += 1 # Advance PC for the next line BEFORE executing current one

        # Execute the logical line (which might contain multiple statements separated by ':')
        # The return value of execute_logical_line indicates if a GOTO, GOSUB, or DELAY happened.
        return self.execute_logical_line(logical_line_content, pc_of_this_line)


    def _split_statements(self, line_content: str) -> List[str]:
        """Split line by colons while respecting string literals."""
        statements = []
        current = []
        in_string = False
        for char in line_content:
            if char == '"':
                in_string = not in_string
                current.append(char)
            elif char == ':' and not in_string:
                statements.append(''.join(current))
                current = []
            else:
                current.append(char)
        if current:
            statements.append(''.join(current))
        return statements

    def execute_logical_line(self, line_content: str, pc_of_line: int) -> bool:
        """ Executes a logical line, which may contain multiple statements separated by colons.
            pc_of_line is the program counter index for this entire logical line.
            Returns True if a statement caused a GOTO, GOSUB, DELAY, or loop jump.
        """
        # Apostrophe comments - split while respecting strings
        if "'" in line_content:
            # Find apostrophe outside of strings
            in_string = False
            for i, char in enumerate(line_content):
                if char == '"':
                    in_string = not in_string
                elif char == "'" and not in_string:
                    line_content = line_content[:i]
                    break

        statements = self._split_statements(line_content)
        for stmt_text in statements:
            stmt_text = stmt_text.strip()
            if stmt_text:
                # _execute_single_statement returns True if GOTO, GOSUB, FOR/LOOP jump, or DELAY occurred
                if self._execute_single_statement(stmt_text, pc_of_line):
                    # If a DELAY occurred, just return True to pause execution
                    # PC has already been advanced, so after delay we continue to next line
                    return True
                if not self.running:
                    return False
        return False


    def _skip_block(self, start_kw_upper: str, end_kw_upper: str, pc_of_block_start: int) -> None:
        """ Skips a block of code (FOR/NEXT, DO/LOOP) by advancing self.pc. """
        nesting_level = 1
        # Start searching from the line *after* the current line (self.pc already advanced)
        search_pc = self.pc 
        
        while search_pc < len(self.program_lines) and nesting_level > 0:
            _, _, line_to_scan = self.program_lines[search_pc]
            # Check only the first command on the line for block start/end keywords for simplicity
            # This doesn't handle multi-statement lines perfectly for nested blocks while skipping,
            # but is a common simplification.
            first_cmd_on_line = line_to_scan.split(':')[0].strip().upper()

            if first_cmd_on_line.startswith(start_kw_upper):
                nesting_level += 1
            elif first_cmd_on_line.startswith(end_kw_upper):
                # For NEXT [var], ensure it's a NEXT, not something like NEXTPAGE
                if end_kw_upper == "NEXT" and not _next_re.match(first_cmd_on_line): # Check with regex
                    pass # Not a true NEXT statement
                else:
                    nesting_level -= 1
            
            if nesting_level == 0:
                self.pc = search_pc + 1 # PC for the line AFTER the block end
                return
            search_pc += 1
        
        # If loop falls through, EOF was reached before block end
        print(f"Warning: EOF reached while skipping '{start_kw_upper}' block started at PC {pc_of_block_start}.")
        self.running = False
        self.pc = len(self.program_lines) # Move PC to end to stop execution

    def _skip_for_block(self, start_pc_num: int) -> None:
        # The FOR that initiated the skip is on the stack. Pop it.
        if self.for_stack and self.for_stack[-1]["loop_pc"] == self.pc:  # Ensure it's the current FOR
            # If it was a placeholder from skipping an IF, that's handled differently
            if not self.for_stack[-1].get("placeholder"):
                self.for_stack.pop()
        self._skip_block("FOR", "NEXT", start_pc_num)


    def _skip_loop_block(self, start_pc_num: int) -> None:
        # The DO that initiated the skip is on the stack. Pop it.
        if self.loop_stack and self.loop_stack[-1]["start_pc"] == self.pc:
            if not self.loop_stack[-1].get("placeholder"):
                self.loop_stack.pop()
        self._skip_block("DO", "LOOP", start_pc_num)

    def _skip_to_next(self, start_pc_num: int) -> None:
        """Skip to the matching NEXT statement for EXIT FOR."""
        self._skip_block("FOR", "NEXT", start_pc_num)

    def _skip_to_loop(self, start_pc_num: int) -> None:
        """Skip to the matching LOOP statement for EXIT DO."""
        self._skip_block("DO", "LOOP", start_pc_num)

    def step(self) -> None:
        current_ticks = pygame.time.get_ticks()
        if self.delay_until > 0 and current_ticks < self.delay_until:
            return # Still delaying

        self.delay_until = 0 # Clear delay

        # Execute a certain number of BASIC program lines or until a natural pause (like DELAY)
        steps_this_frame = 0
        while self.running and self.pc < len(self.program_lines) and steps_this_frame < self.steps_per_frame:
            paused_or_jumped = self.step_line() # step_line executes one logical line
            steps_this_frame += 1
            if paused_or_jumped:
                # If DELAY occurred, delay_until will be set. step_line sets pc back.
                # If GOTO/GOSUB/LOOP/FOR jump, PC is already updated.
                # The outer loop will check delay_until again.
                if self.delay_until > pygame.time.get_ticks():
                    break # Break from step-batching if a delay was hit.
        
        if self.pc >= len(self.program_lines) and self.running:
            # print("Program reached end normally.") # Optional message
            self.running = False

    def draw(self, target_surface: pygame.Surface) -> None:
        if not self.surface:
            return

        target_w, target_h = target_surface.get_size()

        # Check if we can reuse cached surface
        if not self._dirty and self._cached_scaled_surface:
            cached_size = self._cached_scaled_surface.get_size()
            if cached_size == (target_w, target_h):
                target_surface.blit(self._cached_scaled_surface, (0, 0))
                return

        # Create scaled surface - use scale for pixel-perfect scaling
        # This is faster than smoothscale for retro graphics
        if self._cached_scaled_surface is None or self._cached_scaled_surface.get_size() != (target_w, target_h):
            self._cached_scaled_surface = pygame.Surface((target_w, target_h))

        # Use faster scale method
        pygame.transform.scale(self.surface, (target_w, target_h), self._cached_scaled_surface)
        target_surface.blit(self._cached_scaled_surface, (0, 0))
        self._dirty = False

# --- Main Program Execution ---
def run_interpreter(filename: str) -> None:
    pygame.init()
    pygame.font.init()

    # Try to enable OpenGL acceleration if available
    display_flags = pygame.RESIZABLE | pygame.DOUBLEBUF
    try:
        # Try hardware surface first
        screen = pygame.display.set_mode((INITIAL_WIDTH, INITIAL_HEIGHT), display_flags | pygame.HWSURFACE)
    except pygame.error:
        screen = pygame.display.set_mode((INITIAL_WIDTH, INITIAL_HEIGHT), display_flags)

    pygame.display.set_caption(f"PyBASIC Interpreter - {filename}")

    # Font selection with caching
    font_names = ['consolas', 'dejavusansmono', 'ubuntumono', 'lucidaconsole', 'couriernew', 'monospace']
    font = None
    for name in font_names:
        try:
            font = pygame.font.SysFont(name, FONT_SIZE)
            break
        except pygame.error:
            continue
    if not font:
        font = pygame.font.Font(None, FONT_SIZE)

    interpreter = BasicInterpreter(font, INITIAL_WIDTH, INITIAL_HEIGHT)

    try:
        with open(filename, "r", encoding='utf-8', errors='ignore') as f:
            lines = f.read().splitlines()
    except FileNotFoundError:
        print(f"Error: File not found '{filename}'")
        pygame.quit()
        return
    except Exception as e:
        print(f"Error reading file '{filename}': {e}")
        pygame.quit()
        return

    print(f"Loading file: {filename}")
    interpreter.reset(lines)

    clock = pygame.time.Clock()
    application_running = True
    bg_color = (30, 30, 30)

    while application_running:
        # Process events
        for event in pygame.event.get():
            if event.type == QUIT:
                application_running = False
                interpreter.running = False
            elif event.type == VIDEORESIZE:
                try:
                    screen = pygame.display.set_mode((event.w, event.h), display_flags | pygame.HWSURFACE)
                except pygame.error:
                    screen = pygame.display.set_mode((event.w, event.h), display_flags)
                interpreter.handle_event(event)
                interpreter.mark_dirty()
            else:
                interpreter.handle_event(event)

        # Execute BASIC instructions
        if interpreter.running:
            interpreter.step()

        # Always redraw
        screen.fill(bg_color)
        interpreter.draw(screen)
        pygame.display.flip()

        clock.tick(60)

    print("Exiting PyBASIC Interpreter.")
    pygame.quit()

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        run_interpreter(sys.argv[1])
    else:
        print("Usage: python interpreter.py <your_basic_file.bas>")