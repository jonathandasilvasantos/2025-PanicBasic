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

# --- Custom Exceptions ---
class BasicRuntimeError(Exception):
    """Exception raised during BASIC runtime that can be caught by ON ERROR GOTO."""
    def __init__(self, message, error_type="runtime"):
        super().__init__(message)
        self.error_type = error_type


# --- Custom dict for eval that returns 0 for undefined numeric variables ---
class BasicEvalLocals(dict):
    """Dict subclass that returns 0 for undefined numeric variables (ending with _INT, _SNG, etc.)
    and "" for undefined string variables (ending with _STR) in BASIC expressions.

    This implements QBasic's behavior where undefined variables default to 0 or "".
    """
    def __missing__(self, key):
        # Check if it's a string variable (ends with _STR)
        if key.endswith('_STR'):
            return ""
        # All other undefined variables default to 0
        return 0

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
_intdiv_re = re.compile(r'\\')  # BASIC integer division operator

# Specific function keywords that are parameterless or have unique syntax
_inkey_re = re.compile(r'\bINKEY\$', re.IGNORECASE)  # INKEY$ -> INKEY() (no trailing \b as $ is not a word char)
_timer_re = re.compile(r'\bTIMER\b(?!\s*\()', re.IGNORECASE)  # TIMER -> TIMER()
_date_re = re.compile(r'\bDATE\$', re.IGNORECASE)  # DATE$ -> DATE()
_time_re = re.compile(r'\bTIME\$', re.IGNORECASE)  # TIME$ -> TIME()
_rnd_bare_re = re.compile(r'\bRND\b(?!\s*\()', re.IGNORECASE)  # RND -> RND()
_csrlin_re = re.compile(r'\bCSRLIN\b(?!\s*\()', re.IGNORECASE)  # CSRLIN -> CSRLIN()
_command_re = re.compile(r'\bCOMMAND\$', re.IGNORECASE)  # COMMAND$ -> COMMAND()
_freefile_re = re.compile(r'\bFREEFILE\b(?!\s*\()', re.IGNORECASE)  # FREEFILE -> FREEFILE()

# General pattern for NAME(...) or NAME$(...) which could be a function call or array access
# Uses nested paren pattern to handle cases like func(a(), b) or arr(func(x))
_func_or_array_re = re.compile(
    r'\b([a-zA-Z_][a-zA-Z0-9_]*[\$%!#&]?)\s*\(((?:[^()]|\((?:[^()]|\([^()]*\))*\))*)\)',
    re.IGNORECASE
)

# General identifier pattern (variables, constants)
# It should run after specific function/array patterns have transformed their part of the string.
# Note: No trailing \b because $ and % are not word characters
_identifier_re = re.compile(r'\b([a-zA-Z_][a-zA-Z0-9_]*[\$%#!&]?)')  # Match identifiers with optional type suffix


# --- Command Parsing Patterns (mostly unchanged but reviewed) ---
# Labels: numeric (100 PRINT), numeric with colon (1:), or identifier with colon (Start:)
_label_re = re.compile(r"^\s*(\d+:?|[a-zA-Z_][a-zA-Z0-9_]*:)")
_label_strip_re = re.compile(r"^\s*(\d+:?\s*|[a-zA-Z_][a-zA-Z0-9_]*:)\s*")
_for_re = re.compile(
    r'FOR\s+([a-zA-Z_][a-zA-Z0-9_]*[\$%!#&]?)\s*=\s*(.+?)\s+TO\s+(.+?)(?:\s+STEP\s+(.+))?$', re.IGNORECASE)
_dim_re = re.compile(r'DIM\s+([a-zA-Z_][a-zA-Z0-9_]*[\$%!#&]?)\s*\(([^)]+)\)(?:\s+AS\s+(\w+))?', re.IGNORECASE)
# DIM var AS type (simple variable with type, no array)
_dim_as_re = re.compile(r'DIM\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+AS\s+(\w+)', re.IGNORECASE)
# DIM var (simple scalar variable declaration without AS type or array)
_dim_scalar_re = re.compile(r'DIM\s+([a-zA-Z_][a-zA-Z0-9_]*[\$%!#&]?)(?:\s*,\s*([a-zA-Z_][a-zA-Z0-9_]*[\$%!#&]?))*$', re.IGNORECASE)
# Match: var = expr, var$ = expr, arr(i) = expr, p.X = expr, arr(i).X = expr, var# = expr
_assign_re = re.compile(r'^(?:LET\s+)?([a-zA-Z_][a-zA-Z0-9_]*[\$%!#&]?(?:\s*\([^)]+\))?(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?)\s*=(.*)$', re.IGNORECASE)
# Pattern to extract array name and indices from LHS like "ARR(1, 2)"
_assign_lhs_array_re = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*[\$%!#&]?)\s*\(([^)]+)\)')


# LINE regex - use balanced parens matching for nested expressions like enemyX(i)
_line_re = re.compile(
    r"LINE\s*(?:\(((?:[^()]|\((?:[^()]|\([^()]*\))*\))*)\))?\s*-\s*\(((?:[^()]|\((?:[^()]|\([^()]*\))*\))*)\)\s*(?:,(.*))?$", re.IGNORECASE)
# CIRCLE regex - capture coordinates with balanced parens, then rest of options
_circle_re = re.compile(
    r"CIRCLE\s*\(((?:[^()]|\((?:[^()]|\([^()]*\))*\))*)\)\s*,\s*(.+)$", re.IGNORECASE)
# PAINT regex - capture coordinates with balanced parens
_paint_re = re.compile(r"PAINT\s*\(((?:[^()]|\((?:[^()]|\([^()]*\))*\))*)\)\s*(?:,\s*(.+))?$", re.IGNORECASE)
# PSET regex - match PSET(...), optionally with color - use balanced parens matching
_pset_re = re.compile(
    r"PSET\s*\(\s*((?:[^()]|\((?:[^()]|\([^()]*\))*\))*)\s*\)\s*(?:,\s*(.+))?$", re.IGNORECASE)
_locate_re = re.compile(r"LOCATE\s*(\d+|\S[^,]*?)?(?:,\s*(\d+|\S[^,]*?))?", re.IGNORECASE) # Allow expressions for row/col
_print_re = re.compile(r"PRINT\s?(.*)", re.IGNORECASE)
_if_re = re.compile(r"IF\s+(.+?)\s+THEN(.*)", re.IGNORECASE)
_goto_re = re.compile(r"GOTO\s+([a-zA-Z0-9_]+)", re.IGNORECASE)
_gosub_re = re.compile(r"GOSUB\s+([a-zA-Z0-9_]+)", re.IGNORECASE)
_return_re = re.compile(r"RETURN", re.IGNORECASE)
_screen_re = re.compile(r"SCREEN\s+(.+)", re.IGNORECASE)
_cls_re = re.compile(r"CLS", re.IGNORECASE)
_end_re = re.compile(r"END", re.IGNORECASE)
_randomize_re = re.compile(r"RANDOMIZE(?:\s+(.*))?", re.IGNORECASE)
_next_re = re.compile(r"NEXT(?:\s+([a-zA-Z_][a-zA-Z0-9_]*[\$%!#&]?))?", re.IGNORECASE)
_delay_re = re.compile(r"(?:_DELAY|SLEEP)\s+(.*)", re.IGNORECASE)
_do_re = re.compile(r"DO(?:\s+(WHILE|UNTIL)\s+(.+))?", re.IGNORECASE)
_loop_re = re.compile(r"LOOP(?:\s+(WHILE|UNTIL)\s+(.+))?", re.IGNORECASE)
_const_re = re.compile(r"CONST\s+([a-zA-Z_][a-zA-Z0-9_]*\$?)\s*=(.*)", re.IGNORECASE)
_color_re = re.compile(r"COLOR(?:\s*([^,]+))?(?:\s*,\s*(.+))?", re.IGNORECASE)
_rem_re = re.compile(r"REM\b.*", re.IGNORECASE)
_exit_do_re = re.compile(r"EXIT\s+DO", re.IGNORECASE)
_exit_for_re = re.compile(r"EXIT\s+FOR", re.IGNORECASE)

# New statement patterns
_swap_re = re.compile(r"SWAP\s+([a-zA-Z_][a-zA-Z0-9_]*[\$%!#&]?(?:\s*\([^)]+\))?)\s*,\s*([a-zA-Z_][a-zA-Z0-9_]*[\$%!#&]?(?:\s*\([^)]+\))?)", re.IGNORECASE)
_while_re = re.compile(r"WHILE\s+(.+)", re.IGNORECASE)
_wend_re = re.compile(r"WEND", re.IGNORECASE)
_select_case_re = re.compile(r"SELECT\s+CASE\s+(.+)", re.IGNORECASE)
_case_re = re.compile(r"CASE\s+(.*)", re.IGNORECASE)
_end_select_re = re.compile(r"END\s+SELECT", re.IGNORECASE)
_data_re = re.compile(r"DATA\s+(.*)", re.IGNORECASE)
_read_re = re.compile(r"READ\s+(.*)", re.IGNORECASE)
_restore_re = re.compile(r"RESTORE(?:\s+([a-zA-Z0-9_]+))?", re.IGNORECASE)

# INPUT statement: INPUT ["prompt"{;|,}] variable[, variable...]
_input_re = re.compile(r"INPUT\s+(.*)", re.IGNORECASE)
# LINE INPUT statement: LINE INPUT ["prompt"{;|,}] variable$
_line_input_re = re.compile(r"LINE\s+INPUT\s+(.*)", re.IGNORECASE)

# ON...GOTO and ON...GOSUB for computed branches
_on_goto_re = re.compile(r"ON\s+(.+?)\s+GOTO\s+(.+)", re.IGNORECASE)
_on_gosub_re = re.compile(r"ON\s+(.+?)\s+GOSUB\s+(.+)", re.IGNORECASE)

# Sound commands
_beep_re = re.compile(r"BEEP", re.IGNORECASE)
_sound_re = re.compile(r"SOUND\s+([^,]+)\s*,\s*(.+)", re.IGNORECASE)

# PRESET - like PSET but uses background color by default - use balanced parens matching
_preset_re = re.compile(
    r"PRESET\s*\(\s*((?:[^()]|\((?:[^()]|\([^()]*\))*\))*)\s*\)\s*(?:,\s*(.+))?$", re.IGNORECASE)

# ERASE - erase arrays
_erase_re = re.compile(r"ERASE\s+(.+)", re.IGNORECASE)

# FN function call pattern: FN name(args) or FNname(args)
_fn_call_re = re.compile(r'\bFN\s*([a-zA-Z_][a-zA-Z0-9_]*\$?)\s*\(([^)]*)\)', re.IGNORECASE)

# DEF FN - define inline function
_def_fn_re = re.compile(r"DEF\s+FN\s*([a-zA-Z_][a-zA-Z0-9_]*\$?)\s*(?:\(([^)]*)\))?\s*=\s*(.+)", re.IGNORECASE)

# OPTION BASE - set default array lower bound
_option_base_re = re.compile(r"OPTION\s+BASE\s+([01])", re.IGNORECASE)

# REDIM - redimension dynamic array (supports type suffixes)
_redim_re = re.compile(r"REDIM\s+([a-zA-Z_][a-zA-Z0-9_]*[\$%!#&]?)\s*\(([^)]+)\)", re.IGNORECASE)

# PRINT USING - formatted output
_print_using_re = re.compile(r"PRINT\s+USING\s+(.+?)\s*;\s*(.+)", re.IGNORECASE)

# PLAY - Music Macro Language
_play_re = re.compile(r"PLAY\s+(.+)", re.IGNORECASE)

# DRAW - Turtle graphics
_draw_re = re.compile(r"DRAW\s+(.+)", re.IGNORECASE)

# STOP - Break execution
_stop_re = re.compile(r"STOP", re.IGNORECASE)

# TRON/TROFF - Trace debugging
_tron_re = re.compile(r"TRON", re.IGNORECASE)
_troff_re = re.compile(r"TROFF", re.IGNORECASE)

# RUN - Run/restart program
_run_re = re.compile(r"RUN(?:\s+(.+))?", re.IGNORECASE)

# CONT - Continue after STOP
_cont_re = re.compile(r"CONT", re.IGNORECASE)

# CHAIN - Load and run another program
_chain_re = re.compile(r"CHAIN\s+(.+)", re.IGNORECASE)

# $INCLUDE metacommand
_include_re = re.compile(r"\$INCLUDE\s*:\s*['\"](.+?)['\"]", re.IGNORECASE)

# $DYNAMIC/$STATIC metacommands
_dynamic_re = re.compile(r"\$DYNAMIC", re.IGNORECASE)
_static_re = re.compile(r"\$STATIC", re.IGNORECASE)

# KEY statement for function key handling
_key_re = re.compile(r"KEY\s+(\d+)\s*,\s*(.+)", re.IGNORECASE)
_key_on_off_re = re.compile(r"KEY\s*\((\d+)\)\s+(ON|OFF|STOP)", re.IGNORECASE)
_key_list_re = re.compile(r"KEY\s+(ON|OFF|LIST)", re.IGNORECASE)

# ON KEY(n) GOSUB
_on_key_re = re.compile(r"ON\s+KEY\s*\((\d+)\)\s+GOSUB\s+([a-zA-Z0-9_]+)", re.IGNORECASE)

# DEFINT/DEFSNG/DEFDBL/DEFLNG/DEFSTR - Default type declarations (ignored)
_deftype_re = re.compile(r"DEF(INT|SNG|DBL|LNG|STR)\s+[A-Za-z](?:\s*-\s*[A-Za-z])?", re.IGNORECASE)

# PALETTE - Color palette
_palette_re = re.compile(r"PALETTE(?:\s+USING\s+(.+)|\s+(\d+)\s*,\s*(.+))?", re.IGNORECASE)

# PCOPY - Copy video pages
_pcopy_re = re.compile(r"PCOPY\s+(\d+)\s*,\s*(\d+)", re.IGNORECASE)

# VIEW PRINT - Text viewport
_view_print_re = re.compile(r"VIEW\s+PRINT(?:\s+(\d+)\s+TO\s+(\d+))?", re.IGNORECASE)

# WIDTH - Screen/printer width
_width_re = re.compile(r"WIDTH\s+(\d+)(?:\s*,\s*(\d+))?", re.IGNORECASE)

# WAIT - Wait for port condition (emulated as no-op)
_wait_re = re.compile(r"WAIT\s+([^,]+)\s*,\s*([^,]+)(?:\s*,\s*(.+))?", re.IGNORECASE)

# TIMER ON/OFF - Enable/disable timer events (no-op, for compatibility)
_timer_on_off_re = re.compile(r"TIMER\s+(ON|OFF|STOP)", re.IGNORECASE)

# OUT - Write to I/O port (emulated)
_out_re = re.compile(r"OUT\s+([^,]+)\s*,\s*(.+)", re.IGNORECASE)

# DEF SEG - Set memory segment (emulated)
_def_seg_re = re.compile(r"DEF\s+SEG(?:\s*=\s*(.+))?", re.IGNORECASE)

# POKE - Write to memory (emulated)
_poke_re = re.compile(r"POKE\s+([^,]+)\s*,\s*(.+)", re.IGNORECASE)

# COMMON SHARED - Global variable declaration
_common_shared_re = re.compile(r"COMMON\s+SHARED\s+(.+)", re.IGNORECASE)

# DIM SHARED - Shared array declaration
_dim_shared_re = re.compile(r"DIM\s+SHARED\s+(.+)", re.IGNORECASE)

# GET (graphics) - Capture screen region
_get_gfx_re = re.compile(r"GET\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)\s*-\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)\s*,\s*([a-zA-Z_][a-zA-Z0-9_]*)", re.IGNORECASE)

# PUT (graphics) - Display sprite
_put_gfx_re = re.compile(r"PUT\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)\s*,\s*([a-zA-Z_][a-zA-Z0-9_]*)(?:\s*,\s*(PSET|PRESET|AND|OR|XOR))?", re.IGNORECASE)

# ON ERROR GOTO - Error handler
_on_error_re = re.compile(r"ON\s+ERROR\s+GOTO\s+([a-zA-Z0-9_]+)", re.IGNORECASE)

# RESUME - Resume after error
_resume_re = re.compile(r"RESUME(?:\s+(NEXT|[a-zA-Z0-9_]+))?", re.IGNORECASE)

# DECLARE SUB/FUNCTION - Procedure declaration (ignored, we parse at runtime)
# Pattern allows array parameters like BCoor() AS ANY or arr() AS INTEGER
_declare_re = re.compile(r"DECLARE\s+(SUB|FUNCTION)\s+([a-zA-Z_][a-zA-Z0-9_]*[\$%!#&]?)(?:\s*\(((?:[^()]*|\([^()]*\))*)\))?", re.IGNORECASE)

# SUB - Subroutine definition (allows array parameters)
_sub_re = re.compile(r"SUB\s+([a-zA-Z_][a-zA-Z0-9_]*)(?:\s*\(((?:[^()]*|\([^()]*\))*)\))?(?:\s+STATIC)?", re.IGNORECASE)

# END SUB - End of subroutine
_end_sub_re = re.compile(r"END\s+SUB", re.IGNORECASE)

# FUNCTION - Function definition (allows array parameters and type suffixes like %)
_function_re = re.compile(r"FUNCTION\s+([a-zA-Z_][a-zA-Z0-9_]*[\$%!#&]?)(?:\s*\(((?:[^()]*|\([^()]*\))*)\))?(?:\s+STATIC)?", re.IGNORECASE)

# END FUNCTION - End of function
_end_function_re = re.compile(r"END\s+FUNCTION", re.IGNORECASE)

# EXIT SUB/FUNCTION
_exit_sub_re = re.compile(r"EXIT\s+SUB", re.IGNORECASE)
_exit_function_re = re.compile(r"EXIT\s+FUNCTION", re.IGNORECASE)

# SHARED - Share variables with main program
_shared_re = re.compile(r"SHARED\s+(.+)", re.IGNORECASE)

# CALL - Call subroutine (allows nested parentheses for array args like cities())
_call_re = re.compile(r"CALL\s+([a-zA-Z_][a-zA-Z0-9_]*)(?:\s*\(((?:[^()]*|\([^()]*\))*)\))?", re.IGNORECASE)

# TYPE - User-defined type
_type_re = re.compile(r"TYPE\s+([a-zA-Z_][a-zA-Z0-9_]*)", re.IGNORECASE)

# END TYPE
_end_type_re = re.compile(r"END\s+TYPE", re.IGNORECASE)

# File I/O patterns
# File I/O patterns - file number can be a literal or variable expression
_open_re = re.compile(r'OPEN\s+("[^"]+"|[^\s]+)\s+FOR\s+(INPUT|OUTPUT|APPEND|BINARY|RANDOM)\s+AS\s+#?([^\s,]+)(?:\s+LEN\s*=\s*(\d+))?', re.IGNORECASE)
_close_re = re.compile(r"CLOSE(?:\s+#?([^\s,]+))?", re.IGNORECASE)
_input_file_re = re.compile(r"INPUT\s+#([^\s,]+)\s*,\s*(.+)", re.IGNORECASE)
_line_input_file_re = re.compile(r"LINE\s+INPUT\s+#([^\s,]+)\s*,\s*(.+)", re.IGNORECASE)
_print_file_re = re.compile(r"PRINT\s+#([^\s,]+)\s*,?\s*(.*)", re.IGNORECASE)
_write_file_re = re.compile(r"WRITE\s+#([^\s,]+)\s*,?\s*(.*)", re.IGNORECASE)

# Binary file GET/PUT (must come before graphics GET/PUT)
# GET #filenum[, recordnum], variable
# PUT #filenum[, recordnum], variable
_get_file_re = re.compile(r"GET\s+#(\d+)(?:\s*,\s*(\d+))?\s*,\s*([a-zA-Z_][a-zA-Z0-9_]*\$?)", re.IGNORECASE)
_put_file_re = re.compile(r"PUT\s+#(\d+)(?:\s*,\s*(\d+))?\s*,\s*([a-zA-Z_][a-zA-Z0-9_]*\$?)", re.IGNORECASE)

# File system commands
_kill_re = re.compile(r"KILL\s+(.+)", re.IGNORECASE)
_name_re = re.compile(r"NAME\s+(.+?)\s+AS\s+(.+)", re.IGNORECASE)
_mkdir_re = re.compile(r"MKDIR\s+(.+)", re.IGNORECASE)
_rmdir_re = re.compile(r"RMDIR\s+(.+)", re.IGNORECASE)
_chdir_re = re.compile(r"CHDIR\s+(.+)", re.IGNORECASE)
_files_re = re.compile(r"FILES(?:\s+(.+))?", re.IGNORECASE)

# File positioning
_seek_re = re.compile(r"SEEK\s+#?(\d+)\s*,\s*(.+)", re.IGNORECASE)

# ERROR statement
_error_re = re.compile(r"ERROR\s+(.+)", re.IGNORECASE)

# CLEAR statement - clear variables and set stack/heap
_clear_re = re.compile(r"CLEAR(?:\s*,\s*(\d+))?(?:\s*,\s*(\d+))?", re.IGNORECASE)

# SYSTEM/END - exit to operating system
_system_re = re.compile(r"SYSTEM(?:\s+(.+))?", re.IGNORECASE)

# SHELL - execute shell command
_shell_re = re.compile(r"SHELL(?:\s+(.+))?", re.IGNORECASE)

# VIEW - define graphics viewport
_view_re = re.compile(r"VIEW(?:\s*\(([^)]+)\)\s*-\s*\(([^)]+)\)(?:\s*,\s*(\d+))?(?:\s*,\s*(\d+))?)?", re.IGNORECASE)

# WINDOW - define logical coordinate system
_window_re = re.compile(r"WINDOW(?:\s+SCREEN)?(?:\s*\(([^)]+)\)\s*-\s*\(([^)]+)\))?", re.IGNORECASE)

# LPRINT - print to printer (console)
_lprint_using_re = re.compile(r"LPRINT\s+USING\s+(.+?)\s*;\s*(.+)", re.IGNORECASE)
_lprint_re = re.compile(r"LPRINT(?:\s+(.*))?", re.IGNORECASE)

# FIELD - define random access record fields
_field_re = re.compile(r"FIELD\s+#?(\d+)\s*,\s*(.+)", re.IGNORECASE)

# LSET/RSET - justify string in field
_lset_re = re.compile(r"LSET\s+([a-zA-Z_][a-zA-Z0-9_]*\$?)\s*=\s*(.+)", re.IGNORECASE)
_rset_re = re.compile(r"RSET\s+([a-zA-Z_][a-zA-Z0-9_]*\$?)\s*=\s*(.+)", re.IGNORECASE)

# ENVIRON - set environment variable
_environ_set_re = re.compile(r"ENVIRON\s+(.+)", re.IGNORECASE)

# ON TIMER GOSUB - timer event handler
_on_timer_re = re.compile(r"ON\s+TIMER\s*\(([^)]+)\)\s+GOSUB\s+([a-zA-Z0-9_]+)", re.IGNORECASE)

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
    'LOG', 'EXP', 'CINT', 'CLNG', 'CSNG', 'CDBL',
    # Date/time functions
    'DATE', 'TIME',
    # Cursor/screen functions
    'CSRLIN', 'POS', 'TAB', 'SPC',
    # Array functions
    'LBOUND', 'UBOUND',
    # Environment/Input functions
    'ENVIRON', 'INPUT', 'COMMAND',
    # Memory/System functions
    'FRE', 'PEEK', 'INP', 'FREEFILE', 'LOF', 'EOF', 'LOC',
    # Binary conversion functions
    'MKI', 'MKL', 'MKS', 'MKD', 'CVI', 'CVL', 'CVS', 'CVD',
    # Memory address functions (emulated)
    'VARPTR', 'VARSEG', 'SADD',
    # Music function (as callable)
    'PLAY'
}

# --- Expression Conversion Logic ---

def _basic_to_python_identifier(basic_name_str: str) -> str:
    """Converts a BASIC identifier to a Python-compatible identifier for eval."""
    name_upper = basic_name_str.upper()
    if name_upper.endswith('$'):
        return name_upper[:-1] + "_STR"
    elif name_upper.endswith('%'):
        return name_upper[:-1] + "_INT"
    elif name_upper.endswith('#'):
        return name_upper[:-1] + "_DBL"  # Double precision
    elif name_upper.endswith('!'):
        return name_upper[:-1] + "_SNG"  # Single precision
    elif name_upper.endswith('&'):
        return name_upper[:-1] + "_LNG"  # Long integer
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
    Splits an argument string by commas, respecting parentheses and string quotes.
    This is a simplified parser; a full tokenizer/parser would be more robust.
    """
    if not args_str.strip():
        return []
    if args_str in _memoized_arg_splits:
        return _memoized_arg_splits[args_str]

    args = []
    current_arg = ""
    paren_level = 0
    in_string = False
    for char in args_str:
        if char == '"' and not in_string:
            in_string = True
            current_arg += char
        elif char == '"' and in_string:
            in_string = False
            current_arg += char
        elif char == ',' and paren_level == 0 and not in_string:
            args.append(current_arg.strip())
            current_arg = ""
        else:
            current_arg += char
            if not in_string:
                if char == '(':
                    paren_level += 1
                elif char == ')':
                    paren_level -= 1
    args.append(current_arg.strip())
    _memoized_arg_splits[args_str] = args
    return args


def _replace_fn_call(match: re.Match) -> str:
    """
    Callback for _fn_call_re.sub.
    Converts FN funcname(args) to FN_FUNCNAME(args) for user-defined functions.
    """
    func_name = match.group(1).upper()
    # Convert to Python-compatible name (e.g., GREET$ -> GREET_STR)
    py_func_name = _basic_to_python_identifier(func_name)
    args_str = match.group(2)
    arg_parts = _split_args(args_str)
    processed_args = [convert_basic_expr(arg, set()) for arg in arg_parts]
    return f"FN_{py_func_name}({', '.join(processed_args)})"


def _replace_func_or_array_access(match: re.Match) -> str:
    """
    Callback for _func_or_array_re.sub.
    Determines if NAME(...) is a function call or array access and converts accordingly.
    """
    name_basic = match.group(1)  # e.g., "MYARRAY", "MYARRAY$", "CHR$", "LEFT$"
    args_str = match.group(2)    # Content between parentheses

    name_base_upper = name_basic.rstrip('$%!#&').upper()  # Strip all type suffixes

    # Skip FN_ prefixed names (user-defined function calls already converted)
    if name_base_upper.startswith('FN_'):
        # Preserve as-is (already converted by _replace_fn_call)
        return match.group(0)

    if name_base_upper in _basic_function_names:  # It's a function call
        arg_parts = _split_args(args_str)
        # Recursively call convert_basic_expr for each argument
        # Pass dummy known_identifiers as it's not strictly needed by new logic path
        processed_args = [convert_basic_expr(arg, set()) for arg in arg_parts]
        return f"{name_base_upper}({', '.join(processed_args)})"
    else:  # It's an array access
        py_array_name = _basic_to_python_identifier(name_basic)
        arg_parts = _split_args(args_str)
        if not arg_parts:
            # Empty parentheses (e.g., "a()") means the whole array - return just the name
            # This is used when passing arrays as arguments to SUB/FUNCTION
            return py_array_name

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
    expr = _csrlin_re.sub("CSRLIN()", expr)
    expr = _command_re.sub("COMMAND()", expr)
    expr = _freefile_re.sub("FREEFILE()", expr)

    # 1b. User-defined FN function calls: FN name(args) or FNname(args)
    expr = _fn_call_re.sub(_replace_fn_call, expr)

    # 2. General function calls OR array access: NAME(...) / NAME$(...)
    expr = _func_or_array_re.sub(_replace_func_or_array_access, expr)

    # 3. Operators
    expr = _and_re.sub(" and ", expr)
    expr = _or_re.sub(" or ", expr)
    expr = _not_re.sub(" not ", expr)
    expr = _mod_re.sub(" % ", expr)
    expr = _exp_re.sub(" ** ", expr)  # BASIC ^ to Python **
    # BASIC \ integer division - needs to truncate toward zero
    # Replace a \ b with _INTDIV_(a, b)
    while '\\' in expr:
        # Find the backslash and extract operands
        expr = re.sub(r'(\([^()]+\)|[^\s\\+\-*/()]+)\s*\\\s*(\([^()]+\)|[^\s\\+\-*/()]+)', r'_INTDIV_(\1, \2)', expr, count=1)
    expr = _eq_re.sub(" == ", expr)
    expr = _neq_re.sub(" != ", expr)

    # Convert BASIC hex/octal/binary literals
    expr = re.sub(r'&H([0-9A-Fa-f]+)', r'0x\1', expr, flags=re.IGNORECASE)
    expr = re.sub(r'&O([0-7]+)', r'0o\1', expr, flags=re.IGNORECASE)
    expr = re.sub(r'&B([01]+)', r'0b\1', expr, flags=re.IGNORECASE)

    # Remove type suffix from numeric literals (1#, 3.14!, 5&, etc.)
    expr = re.sub(r'(\d+\.?\d*)[#!&]', r'\1', expr)

    # Clean up any leading/trailing whitespace that might cause syntax errors
    expr = expr.strip()

    # 3.5 Handle type member access
    # First handle array element member access: arr[i].member -> arr[i]['MEMBER']
    # After array conversion, we have square brackets, not parentheses
    expr = re.sub(r'\]\.([a-zA-Z_][a-zA-Z0-9_]*)',
                  lambda m: f"]['{m.group(1).upper()}']", expr)
    # Also handle unconverted form (with parentheses): arr(i).member -> arr(i)['MEMBER']
    expr = re.sub(r'\)\.([a-zA-Z_][a-zA-Z0-9_]*)',
                  lambda m: f")['{m.group(1).upper()}']", expr)
    # Then handle simple type member access: p.X -> P['X']
    expr = re.sub(r'([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)',
                  lambda m: f"{m.group(1).upper()}['{m.group(2).upper()}']", expr)

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
        # Video pages for PCOPY (up to 8 pages for mode 13, more for others)
        self.video_pages: Dict[int, Optional[pygame.Surface]] = {}
        self.active_page: int = 0  # Current drawing page
        self.visual_page: int = 0  # Current display page
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

        # INPUT statement state
        self.input_mode: bool = False
        self.input_buffer: str = ""
        self.input_prompt: str = ""
        self.input_variables: List[str] = []
        self.input_cursor_pos: int = 0
        self._line_input_mode: bool = False  # True for LINE INPUT (no comma parsing)

        # DEF FN user-defined functions: name -> (params, expression)
        self.user_functions: Dict[str, Tuple[List[str], str]] = {}

        # OPTION BASE setting (0 or 1)
        self.option_base: int = 0

        # INPUT$ key buffer for multi-character reads
        self._input_dollar_buffer: str = ""

        # Command line arguments (set externally)
        self.command_line_args: str = ""

        # File I/O state
        self.file_handles: Dict[int, Any] = {}  # file_number -> file object
        self.next_file_number: int = 1

        # Emulated memory for PEEK/POKE
        self.memory_segment: int = 0
        self.emulated_memory: Dict[int, int] = {}  # address -> byte value

        # I/O port emulation
        self.io_ports: Dict[int, int] = {}  # port -> value

        # Error handling
        self.error_handler_label: Optional[str] = None
        self.error_resume_pc: int = -1
        self.in_error_handler: bool = False

        # SUB/FUNCTION definitions: name -> (params, body_start_pc, body_end_pc, is_static)
        self.procedures: Dict[str, Dict[str, Any]] = {}
        self.procedure_stack: List[Dict[str, Any]] = []  # Stack for nested calls
        self.current_procedure: Optional[str] = None

        # TYPE definitions: type_name -> {field_name: field_type}
        self.type_definitions: Dict[str, Dict[str, str]] = {}
        self.current_type: Optional[str] = None

        # VIEW PRINT viewport (row range)
        self.view_print_top: int = 1
        self.view_print_bottom: int = 25  # Default for SCREEN 0

        # STOP/debugging state
        self.stopped: bool = False
        self.trace_mode: bool = False  # TRON/TROFF trace debugging

        # KEY event handlers: key_number (1-10) -> label
        self.key_handlers: Dict[int, str] = {}
        self.key_enabled: Dict[int, bool] = {}  # KEY(n) ON/OFF state
        self.key_definitions: Dict[int, str] = {  # Default F-key definitions
            1: "", 2: "", 3: "", 4: "", 5: "",
            6: "", 7: "", 8: "", 9: "", 10: ""
        }

        # DRAW turtle graphics state
        self.draw_x: float = 0
        self.draw_y: float = 0
        self.draw_angle: int = 0  # 0=right, 90=down, 180=left, 270=up
        self.draw_pen_down: bool = True

        # VIEW - graphics viewport (physical screen coordinates)
        self.view_x1: int = 0
        self.view_y1: int = 0
        self.view_x2: Optional[int] = None  # None means full screen
        self.view_y2: Optional[int] = None
        self.view_fill_color: Optional[int] = None
        self.view_border_color: Optional[int] = None

        # WINDOW - logical coordinate system
        self.window_x1: Optional[float] = None  # None means physical coordinates
        self.window_y1: Optional[float] = None
        self.window_x2: Optional[float] = None
        self.window_y2: Optional[float] = None
        self.window_screen_mode: bool = False  # True for WINDOW SCREEN (y increases down)

        # FIELD - field variables for random access files
        self.field_defs: Dict[int, List[Tuple[int, str]]] = {}  # file_num -> [(width, varname), ...]
        self.field_buffers: Dict[int, str] = {}  # file_num -> buffer string

        # ON TIMER GOSUB - timer event handling
        self.timer_interval: float = 0  # Timer interval in seconds
        self.timer_label: Optional[str] = None  # Label to GOSUB to
        self.timer_enabled: bool = False  # TIMER ON/OFF state
        self.timer_last_trigger: float = 0  # Last trigger time

        # Environment for eval() - functions available to BASIC expressions
        self.eval_env_funcs = {
            # Integer division that truncates toward zero (QBasic behavior)
            "_INTDIV_": lambda a, b: int(float(a) / float(b)),
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
            "CLNG": lambda x: int(round(float(x))),  # Round to long integer
            "CSNG": lambda x: float(x),  # Convert to single precision (float in Python)
            "CDBL": lambda x: float(x),  # Convert to double precision (float in Python)
            # Date/time functions
            "DATE": self._basic_date,  # Current date string
            "TIME": self._basic_time,  # Current time string
            # Cursor/screen functions
            "CSRLIN": self._basic_csrlin,  # Get current cursor row
            "POS": self._basic_pos,  # Get current cursor column
            "TAB": self._basic_tab,  # Tab to column (returns spaces)
            "SPC": self._basic_spc,  # Generate n spaces (same as SPACE)
            # Array functions
            "LBOUND": self._basic_lbound,  # Get array lower bound
            "UBOUND": self._basic_ubound,  # Get array upper bound
            # Environment/Input functions
            "ENVIRON": self._basic_environ,  # Get environment variable
            "INPUT": self._basic_input_dollar,  # INPUT$(n) - read n characters
            "COMMAND": self._basic_command,  # Get command line arguments
            # Memory/System functions
            "FRE": self._basic_fre,  # Get free memory (emulated)
            "PEEK": self._basic_peek,  # Read from memory (emulated)
            "INP": self._basic_inp,  # Read from I/O port (emulated)
            # File functions
            "FREEFILE": self._basic_freefile,  # Get next available file number
            "LOF": self._basic_lof,  # Get file length
            "EOF": self._basic_eof,  # Check for end of file
            "LOC": self._basic_loc,  # Get current file position
            # Binary conversion functions
            "MKI": self._basic_mki,  # Convert integer to 2-byte string
            "MKL": self._basic_mkl,  # Convert long to 4-byte string
            "MKS": self._basic_mks,  # Convert single to 4-byte string
            "MKD": self._basic_mkd,  # Convert double to 8-byte string
            "CVI": self._basic_cvi,  # Convert 2-byte string to integer
            "CVL": self._basic_cvl,  # Convert 4-byte string to long
            "CVS": self._basic_cvs,  # Convert 4-byte string to single
            "CVD": self._basic_cvd,  # Convert 8-byte string to double
            # Memory address functions (emulated)
            "VARPTR": self._basic_varptr,  # Get variable address
            "VARSEG": self._basic_varseg,  # Get variable segment
            "SADD": self._basic_sadd,  # Get string address
            # Music function
            "PLAY": self._basic_play_func,  # Get background music queue count
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

    def _basic_csrlin(self) -> int:
        """CSRLIN - Returns current cursor row (1-based)."""
        return self.text_cursor[1]

    def _basic_pos(self, dummy: Any = 0) -> int:
        """POS(0) - Returns current cursor column (1-based)."""
        return self.text_cursor[0]

    def _basic_tab(self, col: int) -> str:
        """TAB(n) - Returns spaces to move to column n in PRINT."""
        target_col = int(col)
        current_col = self.text_cursor[0]
        if target_col > current_col:
            return " " * (target_col - current_col)
        return ""

    def _basic_spc(self, n: int) -> str:
        """SPC(n) - Returns n spaces for use in PRINT."""
        return " " * max(0, int(n))

    def _basic_lbound(self, array_name: str, dimension: int = 1) -> int:
        """LBOUND(array, dimension) - Returns lower bound of array dimension.
        In QBasic, arrays default to 0-based unless OPTION BASE 1 is used."""
        # Array names are stored in uppercase
        name = str(array_name).upper()
        # Also try without type suffix
        if name not in self.variables:
            name = name.rstrip('$%')
        if name in self.variables and isinstance(self.variables[name], list):
            # Our arrays are 0-based
            return 0
        return 0  # Default for non-existent arrays

    def _basic_ubound(self, array_name: str, dimension: int = 1) -> int:
        """UBOUND(array, dimension) - Returns upper bound of array dimension."""
        name = str(array_name).upper()
        # Also try without type suffix
        if name not in self.variables:
            name = name.rstrip('$%')
        if name in self.variables:
            arr = self.variables[name]
            dim = int(dimension)
            if hasattr(arr, 'shape'):  # numpy array
                if dim <= len(arr.shape):
                    return arr.shape[dim - 1] - 1
            elif isinstance(arr, list):
                if dim == 1:
                    return len(arr) - 1
                elif dim == 2 and arr and isinstance(arr[0], list):
                    return len(arr[0]) - 1
        return -1  # Return -1 for non-existent arrays or invalid dimension

    def _basic_environ(self, var_name: str) -> str:
        """ENVIRON$(varname) - Returns the value of an environment variable."""
        import os
        return os.environ.get(str(var_name), "")

    def _basic_input_dollar(self, *args) -> str:
        """INPUT$(n[, #filenum]) - Returns n characters from keyboard or file.
        INPUT$(n) - Read n characters from keyboard (non-blocking)
        INPUT$(n, filenum) - Read n bytes from file #filenum
        In QBasic keyboard form is blocking, but here we return what's available."""
        if len(args) == 0:
            return ""

        n = int(args[0])
        if n <= 0:
            return ""

        # Check if file number is provided
        if len(args) >= 2:
            # INPUT$(n, #filenum) - read from file
            file_num = int(args[1])
            if file_num in self.file_handles:
                fh = self.file_handles[file_num]
                try:
                    data = fh.read(n)
                    if isinstance(data, bytes):
                        data = data.decode('latin-1')  # Use latin-1 for binary compatibility
                    return data
                except Exception:
                    return ""
            return ""

        # INPUT$(n) - read from keyboard buffer
        result = ""
        if self.last_key:
            result = self.last_key[:n]
            self.last_key = ""

        # Pad with empty if not enough characters (non-blocking behavior)
        # In real QBasic this would block until n characters are typed
        return result

    def _basic_command(self) -> str:
        """COMMAND$ - Returns command line arguments passed to the program."""
        return self.command_line_args

    def _basic_fre(self, arg: Any = 0) -> int:
        """FRE(n) - Returns free memory (emulated, returns large value)."""
        # FRE(0) = free string space, FRE(-1) = array space, FRE(-2) = stack
        return 64000  # Return a reasonable emulated value

    def _basic_peek(self, address: int) -> int:
        """PEEK(address) - Read from emulated memory."""
        addr = int(address)
        full_addr = (self.memory_segment << 4) + addr
        return self.emulated_memory.get(full_addr, 0)

    def _basic_inp(self, port: int) -> int:
        """INP(port) - Read from I/O port (emulated)."""
        return self.io_ports.get(int(port), 0)

    def _basic_freefile(self) -> int:
        """FREEFILE - Returns next available file number."""
        return self.next_file_number

    def _basic_lof(self, file_num: int) -> int:
        """LOF(n) - Returns length of file."""
        fnum = int(file_num)
        if fnum in self.file_handles:
            fh = self.file_handles[fnum]
            if hasattr(fh, 'file_path'):
                try:
                    import os
                    return os.path.getsize(fh.file_path)
                except:
                    pass
            # Try to get size from file object
            try:
                pos = fh.tell()
                fh.seek(0, 2)  # Seek to end
                size = fh.tell()
                fh.seek(pos)  # Restore position
                return size
            except:
                pass
        return 0

    def _basic_eof(self, file_num: int) -> int:
        """EOF(n) - Returns -1 if at end of file, 0 otherwise."""
        fnum = int(file_num)
        if fnum in self.file_handles:
            fh = self.file_handles[fnum]
            try:
                pos = fh.tell()
                fh.seek(0, 2)
                end_pos = fh.tell()
                fh.seek(pos)
                return -1 if pos >= end_pos else 0
            except:
                pass
        return -1  # Default to EOF if file not found

    def _basic_loc(self, file_num: int) -> int:
        """LOC(n) - Returns current file position (1-based byte position for binary files,
        record number for random access files, or line position for sequential files).
        For simplicity, we return the byte position (1-based like QBasic)."""
        fnum = int(file_num)
        if fnum in self.file_handles:
            fh = self.file_handles[fnum]
            try:
                pos = fh.tell()
                return pos + 1  # QBasic uses 1-based positions
            except:
                pass
        return 0

    def _basic_mki(self, value: int) -> str:
        """MKI$(n) - Convert integer to 2-byte string."""
        import struct
        return struct.pack('<h', int(value)).decode('latin-1')

    def _basic_mkl(self, value: int) -> str:
        """MKL$(n) - Convert long integer to 4-byte string."""
        import struct
        return struct.pack('<i', int(value)).decode('latin-1')

    def _basic_mks(self, value: float) -> str:
        """MKS$(n) - Convert single-precision float to 4-byte string."""
        import struct
        return struct.pack('<f', float(value)).decode('latin-1')

    def _basic_mkd(self, value: float) -> str:
        """MKD$(n) - Convert double-precision float to 8-byte string."""
        import struct
        return struct.pack('<d', float(value)).decode('latin-1')

    def _basic_cvi(self, s: str) -> int:
        """CVI(s$) - Convert 2-byte string to integer."""
        import struct
        if len(s) < 2:
            s = s + '\0' * (2 - len(s))
        return struct.unpack('<h', s[:2].encode('latin-1'))[0]

    def _basic_cvl(self, s: str) -> int:
        """CVL(s$) - Convert 4-byte string to long integer."""
        import struct
        if len(s) < 4:
            s = s + '\0' * (4 - len(s))
        return struct.unpack('<i', s[:4].encode('latin-1'))[0]

    def _basic_cvs(self, s: str) -> float:
        """CVS(s$) - Convert 4-byte string to single-precision float."""
        import struct
        if len(s) < 4:
            s = s + '\0' * (4 - len(s))
        return struct.unpack('<f', s[:4].encode('latin-1'))[0]

    def _basic_cvd(self, s: str) -> float:
        """CVD(s$) - Convert 8-byte string to double-precision float."""
        import struct
        if len(s) < 8:
            s = s + '\0' * (8 - len(s))
        return struct.unpack('<d', s[:8].encode('latin-1'))[0]

    def _basic_varptr(self, var_name: Any) -> int:
        """VARPTR(variable) - Get variable address (emulated).
        Returns a unique emulated address for the variable."""
        # In QBasic, VARPTR returns the offset address of a variable
        # We emulate this by returning a hash-based address
        name = str(var_name).upper()
        # Use hash to generate a consistent "address" for each variable
        return abs(hash(name)) % 65536

    def _basic_varseg(self, var_name: Any) -> int:
        """VARSEG(variable) - Get variable segment (emulated).
        Returns an emulated segment address."""
        # In QBasic, VARSEG returns the segment address of a variable
        # We return a fixed emulated segment for all variables
        return self.memory_segment if self.memory_segment else 0x4000

    def _basic_sadd(self, s: str) -> int:
        """SADD(string$) - Get string address (emulated).
        Returns an emulated address for the string data."""
        # SADD returns the offset address of a string's character data
        # We emulate this by returning a hash-based address
        return abs(hash(str(s))) % 65536

    def _basic_play_func(self, n: int = 0) -> int:
        """PLAY(n) - Get background music queue count.
        n=0: notes remaining in background music queue
        Since we don't have background music queue, always returns 0."""
        # In QBasic, PLAY(n) returns the number of notes in the background
        # music buffer. We don't implement background music, so return 0.
        return 0

    def _call_user_function(self, func_name: str, args: List[Any]) -> Any:
        """Call a user-defined function (DEF FN)."""
        func_name_upper = func_name.upper()
        if func_name_upper not in self.user_functions:
            print(f"Error: Undefined function FN{func_name}")
            self.running = False
            return 0

        params, expr = self.user_functions[func_name_upper]

        # Save current variable values for parameters
        saved_vars = {}
        for i, param in enumerate(params):
            param_upper = param.upper()
            if param_upper in self.variables:
                saved_vars[param_upper] = self.variables[param_upper]
            # Set parameter to argument value
            if i < len(args):
                self.variables[param_upper] = args[i]
            else:
                self.variables[param_upper] = 0  # Default value

        # Evaluate the function expression
        result = self.eval_expr(expr)

        # Restore saved variables
        for param in params:
            param_upper = param.upper()
            if param_upper in saved_vars:
                self.variables[param_upper] = saved_vars[param_upper]
            elif param_upper in self.variables:
                del self.variables[param_upper]

        return result

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
        # Reset user-defined functions and option base
        self.user_functions.clear()
        self.option_base = 0
        # Reset STOP/debugging state
        self.stopped = False
        self.trace_mode = False
        # Reset KEY event handlers
        self.key_handlers.clear()
        self.key_enabled.clear()
        # Reset procedures (SUB/FUNCTION definitions)
        self.procedures.clear()
        self.procedure_stack.clear()
        # Reset DRAW turtle graphics state
        self.draw_x = self.screen_width / 2
        self.draw_y = self.screen_height / 2
        self.draw_angle = 0
        self.draw_pen_down = True

        # Reset VIEW/WINDOW state
        self.view_x1 = 0
        self.view_y1 = 0
        self.view_x2 = None
        self.view_y2 = None
        self.view_fill_color = None
        self.view_border_color = None
        self.window_x1 = None
        self.window_y1 = None
        self.window_x2 = None
        self.window_y2 = None
        self.window_screen_mode = False

        # Reset FIELD state
        self.field_defs.clear()
        self.field_buffers.clear()

        # Reset timer event state
        self.timer_interval = 0
        self.timer_label = None
        self.timer_enabled = False
        self.timer_last_trigger = 0

        # Reset error handling state
        self.error_handler_label = None
        self.error_resume_pc = -1
        self.in_error_handler = False

        # Close any open files
        for fh in self.file_handles.values():
            try:
                fh.close()
            except:
                pass
        self.file_handles.clear()
        self.next_file_number = 1

        self._dirty = True
        self._cached_scaled_surface = None

        # First pass: collect DATA statements and labels
        pending_label = None
        for i, line_content in enumerate(program_lines):
            stripped = line_content.strip()

            # Strip comments for DATA label detection
            if "'" in stripped:
                stripped = stripped.split("'", 1)[0].strip()

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
                # Parse DATA values
                data_content = stripped[5:].strip()  # Remove "DATA "
                self._parse_data_values(data_content)
                # Don't clear pending_label here - there might be more DATA following
            elif stripped and not stripped.upper().startswith("REM"):
                # Only reset pending_label if there's actual non-DATA, non-comment content
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

        # Third pass: pre-parse SUB and FUNCTION definitions
        self._preparse_procedures()

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

        # Temporarily add FUNCTION procedure names to known functions
        # so they get converted as function calls, not array accesses
        # Add both the full name (with suffix like CANDOWN%) and base name (CANDOWN)
        func_names_added = set()
        for name, proc in self.procedures.items():
            if proc['type'] == 'FUNCTION':
                if name not in _basic_function_names:
                    _basic_function_names.add(name)
                    func_names_added.add(name)
                # Also add base name without type suffix for calls like CanDown vs CanDown%
                base_name = name.rstrip('$%!#&')
                if base_name != name and base_name not in _basic_function_names:
                    _basic_function_names.add(base_name)
                    func_names_added.add(base_name)

        try:
            conv_expr = convert_basic_expr(expr_str, None)
        except Exception as e:
            print(f"Error converting BASIC expr '{expr_str}': {e}")
            self.running = False
            # Remove temporarily added names
            for name in func_names_added:
                _basic_function_names.discard(name)
            return 0
        finally:
            # Remove temporarily added names
            for name in func_names_added:
                _basic_function_names.discard(name)

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

        # Add user-defined FN functions to eval locals
        for fn_name in self.user_functions:
            # Convert function name to Python-compatible format (e.g., GREET$ -> GREET_STR)
            py_fn_name = _basic_to_python_identifier(fn_name)
            fn_key = f"FN_{py_fn_name}"
            # Create a closure to capture the current fn_name
            def make_fn_caller(name):
                return lambda *args: self._call_user_function(name, list(args))
            eval_locals[fn_key] = make_fn_caller(fn_name)

        # Add FUNCTION procedures to eval locals so they can be called in expressions
        for proc_name, proc in self.procedures.items():
            if proc['type'] == 'FUNCTION':
                py_name = _basic_to_python_identifier(proc_name)
                def make_proc_caller(name):
                    return lambda *args: self._call_function_procedure(name, args)
                eval_locals[py_name] = make_proc_caller(proc_name)
                # Also add under base name (without suffix) for calls like CanDown vs CanDown%
                base_name = proc_name.rstrip('$%!#&')
                if base_name != proc_name:
                    eval_locals[base_name] = make_proc_caller(proc_name)

        # QBasic treats undefined numeric variables as 0 and undefined string variables as ""
        # Retry evaluation up to 10 times, adding undefined variables as we encounter them
        max_retries = 10
        for retry in range(max_retries):
            try:
                result = eval(_compiled_expr_cache[conv_expr], self.eval_env_funcs, eval_locals)
                return result
            except NameError as e:
                # Extract the undefined variable name from the error message
                # Format: "name 'VARNAME' is not defined"
                import re
                match = re.search(r"name '([^']+)' is not defined", str(e))
                if match:
                    undefined_var = match.group(1)
                    # Set default value based on type suffix
                    if undefined_var.endswith('_STR'):
                        eval_locals[undefined_var] = ""
                    else:
                        eval_locals[undefined_var] = 0
                    continue  # Retry with the variable defined
                # If we can't extract the name, fall through to error handling
                if self.error_handler_label:
                    raise BasicRuntimeError(str(e))
                print(f"Error evaluating BASIC expr '{expr_str}' (py: '{conv_expr}'): {e}")
                return 0
            except Exception as e:
                if self.error_handler_label:
                    # Raise to be caught by step() which will jump to error handler
                    raise BasicRuntimeError(str(e))
                print(f"Error evaluating BASIC expr '{expr_str}' (py: '{conv_expr}'): {e}")
                return 0

        # If we exceeded max retries, something is wrong
        print(f"Error: Too many undefined variables in '{expr_str}'")
        return 0


    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == KEYDOWN:
            # Handle INPUT mode - route key presses to input handler
            if self.input_mode:
                key = ""
                if event.key == pygame.K_RETURN:
                    key = chr(13)
                elif event.key == pygame.K_BACKSPACE:
                    key = chr(8)
                elif event.key == pygame.K_ESCAPE:
                    key = chr(27)
                elif event.unicode:
                    key = event.unicode
                if key:
                    self._process_input_key(key)
                return  # Don't process other keys in input mode

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
                    # Check for ELSE in single-line IF (outside of strings)
                    else_part = None
                    in_string = False
                    else_pos = -1
                    i = 0
                    while i < len(then_part):
                        if then_part[i] == '"':
                            in_string = not in_string
                        elif not in_string and then_part[i:i+5].upper() == ' ELSE':
                            else_pos = i
                            break
                        i += 1
                    if else_pos >= 0:
                        else_part = then_part[else_pos + 5:].strip()
                        then_part = then_part[:else_pos].strip()

                    if currently_executing:
                        part_to_execute = then_part if condition_met else else_part
                        if part_to_execute:
                            # Execute the appropriate part as a new mini-line
                            # Need to handle GOTO/GOSUB specially
                            if _goto_re.match(part_to_execute):
                                return self._do_goto(_goto_re.match(part_to_execute).group(1).upper())
                            if _gosub_re.match(part_to_execute):
                                return self._do_gosub(_gosub_re.match(part_to_execute).group(1).upper())
                            # Otherwise, execute it as potentially multiple statements
                            return self.execute_logical_line(part_to_execute, current_pc_num)
                    return False # Not executing this block
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

        # If we are in SELECT CASE skip mode, still need to process CASE, END SELECT, and nested SELECT CASE
        if self.select_stack and self.select_stack[-1].get("skip_remaining"):
            # Handle nested SELECT CASE - push placeholder onto stack
            m_select = _select_case_re.fullmatch(statement)
            if m_select:
                self.select_stack.append({"placeholder": True, "skip_remaining": True})
                return False

            # Process CASE statements - only for the current (top) SELECT CASE block
            m_case = _case_re.fullmatch(statement)
            if m_case:
                select_info = self.select_stack[-1]
                # If this is a placeholder from nested SELECT CASE being skipped, ignore
                if select_info.get("placeholder"):
                    return False

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
            mode = int(self.eval_expr(m_screen.group(1).strip()))  # Evaluate expression for mode
            if not self.running: return False
            # QBasic screen modes
            screen_modes = {
                0: (640, 400),   # Text mode 80x25 (simulated)
                1: (320, 200),   # CGA 4-color
                2: (640, 200),   # CGA 2-color
                7: (320, 200),   # EGA 16-color
                8: (640, 200),   # EGA 16-color
                9: (640, 350),   # EGA 16-color
                10: (640, 350),  # EGA mono
                11: (640, 480),  # VGA 2-color
                12: (640, 480),  # VGA 16-color
                13: (320, 200),  # VGA 256-color
            }
            if mode in screen_modes:
                self.screen_width, self.screen_height = screen_modes[mode]
            else:
                self.screen_width, self.screen_height = 320, 200  # Default

            # Update view print bottom for text modes
            if self.font:
                font_h = self.font.get_height()
                if font_h > 0:
                    self.view_print_bottom = self.screen_height // font_h

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

        # --- DIM statement handler (handles all DIM forms including complex expressions) ---
        # Use smart parser that can handle nested parentheses
        if up_stmt.startswith("DIM "):
            dim_content = statement[4:].strip()  # Remove "DIM "
            return self._handle_multi_dim(dim_content, current_pc_num)

        # --- DIM var AS type (simple typed variable or user-defined type) ---
        m_dim_as = _dim_as_re.fullmatch(statement)
        if m_dim_as:
            var_name = m_dim_as.group(1).upper()
            type_name = m_dim_as.group(2).upper()
            # Check if it's a user-defined type
            if type_name in self.type_definitions:
                # Create an instance of the user-defined type
                instance = {}
                for field_name, field_type in self.type_definitions[type_name].items():
                    if field_type == 'STRING':
                        instance[field_name] = ""
                    else:
                        instance[field_name] = 0
                instance['_type'] = type_name
                self.variables[var_name] = instance
            else:
                # Built-in type (INTEGER, LONG, SINGLE, DOUBLE, STRING)
                if type_name == 'STRING':
                    self.variables[var_name] = ""
                else:
                    self.variables[var_name] = 0
            return False

        # Handle scalar DIM (no array dimensions, no AS type): DIM var or DIM var, var2, ...
        m_dim_scalar = _dim_scalar_re.fullmatch(statement)
        if m_dim_scalar:
            # Extract all variable names from the match (captures are just the first and last)
            # Re-parse manually to get all comma-separated variables
            dim_content = statement[3:].strip()  # Remove "DIM "
            for var_spec in dim_content.split(','):
                var_name = var_spec.strip().upper()
                if var_name:
                    if var_name in self.constants:
                        print(f"Error: Cannot DIM constant '{var_name}' at PC {current_pc_num}")
                        self.running = False
                        return False
                    # Initialize with default value based on type suffix
                    if var_name.endswith('$'):
                        self.variables[var_name] = ""
                    else:
                        self.variables[var_name] = 0
            return False

        m_dim = _dim_re.fullmatch(statement)
        if m_dim:
            var_name_orig, idx_str = m_dim.group(1).strip(), m_dim.group(2).strip()
            type_name = (m_dim.group(3) or "").upper().strip()
            var_name = var_name_orig.upper()
            if var_name in self.constants:
                print(f"Error: Cannot DIM constant '{var_name}' at PC {current_pc_num}"); self.running = False; return False

            try:
                # Parse array dimensions - supports both "DIM A(10)" and "DIM A(0 TO 10)" syntax
                dims = []
                for idx_spec in _split_args(idx_str):
                    idx_spec = idx_spec.strip()
                    # Check for "lower TO upper" syntax (case-insensitive)
                    to_match = re.match(r'(.+?)\s+TO\s+(.+)', idx_spec, re.IGNORECASE)
                    if to_match:
                        lower_bound = int(self.eval_expr(to_match.group(1).strip()))
                        upper_bound = int(self.eval_expr(to_match.group(2).strip()))
                        if not self.running: return False
                        dims.append(upper_bound - lower_bound + 1)  # Size based on explicit bounds
                    else:
                        # Simple "DIM A(10)" means indices 0-10 (or 1-10 with OPTION BASE 1)
                        upper_bound = int(self.eval_expr(idx_spec))
                        if not self.running: return False
                        dims.append(upper_bound + 1 - self.option_base)
                if not self.running: return False

                # Determine default value based on type
                def create_default():
                    if type_name and type_name in self.type_definitions:
                        # Create an instance of user-defined type
                        instance = {'_type': type_name}
                        for field_name, field_type in self.type_definitions[type_name].items():
                            instance[field_name] = "" if field_type == 'STRING' else 0
                        return instance
                    elif var_name.endswith("$") or type_name == 'STRING':
                        return ""
                    else:
                        return 0

                # Create N-dimensional array using recursive nested lists
                def create_nd_array(dimensions, default_factory):
                    if len(dimensions) == 1:
                        return [default_factory() for _ in range(dimensions[0])]
                    return [create_nd_array(dimensions[1:], default_factory) for _ in range(dimensions[0])]

                self.variables[var_name] = create_nd_array(dims, create_default)
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
            elif '.' in lhs:
                # Type member assignment: p.X = value or body(0).row = value
                # Check for array element member access (body(0).row)
                arr_member_match = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\(([^)]+)\)\.([a-zA-Z_][a-zA-Z0-9_]*)', lhs, re.IGNORECASE)
                if arr_member_match:
                    var_name = arr_member_match.group(1).upper()
                    idx_str = arr_member_match.group(2)
                    member_name = arr_member_match.group(3).upper()
                    if var_name in self.variables and isinstance(self.variables[var_name], list):
                        try:
                            indices_list = _split_args(idx_str)
                            indices = [int(round(float(self.eval_expr(idx.strip())))) for idx in indices_list]
                            if not self.running: return False
                            # Navigate to the array element
                            target = self.variables[var_name]
                            for idx in indices:
                                target = target[idx]
                            # Now target should be a dict (type instance)
                            if isinstance(target, dict):
                                target[member_name] = val_to_assign
                            else:
                                print(f"Error: Array element is not a user-defined type at PC {current_pc_num}"); self.running = False; return False
                        except Exception as e:
                            print(f"Error in array member access '{lhs}': {e} at PC {current_pc_num}"); self.running = False; return False
                    else:
                        print(f"Error: '{var_name}' is not an array at PC {current_pc_num}"); self.running = False; return False
                else:
                    # Simple type member assignment (p.X = value)
                    parts = lhs.upper().split('.', 1)
                    var_name = parts[0]
                    member_name = parts[1]
                    if var_name in self.variables and isinstance(self.variables[var_name], dict):
                        self.variables[var_name][member_name] = val_to_assign
                    else:
                        print(f"Error: '{var_name}' is not a user-defined type at PC {current_pc_num}"); self.running = False; return False
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

        # --- PRINT USING statement (must come before regular PRINT) ---
        m_print_using = _print_using_re.fullmatch(statement)
        if m_print_using:
            return self._do_print_using(m_print_using.group(1).strip(), m_print_using.group(2).strip(), current_pc_num)

        # --- File I/O: PRINT # statement (must come before regular PRINT) ---
        m_print_file = _print_file_re.fullmatch(statement)
        if m_print_file:
            return self._handle_print_file(m_print_file, current_pc_num)

        m_print = _print_re.fullmatch(statement)
        if m_print:
            content = m_print.group(1).strip() if m_print.group(1) else ""

            # Split content by print separators (',' and ';') while respecting quotes and parentheses
            parts = []
            current_part = ""
            in_string_literal = False
            paren_depth = 0
            for char in content:
                if char == '"' and paren_depth == 0:
                    in_string_literal = not in_string_literal

                if not in_string_literal:
                    if char == '(':
                        paren_depth += 1
                    elif char == ')':
                        paren_depth -= 1

                if not in_string_literal and paren_depth == 0 and (char == ';' or char == ','):
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
                start_coords_str = m_line.group(1)  # "x, y" or None
                end_coords_str = m_line.group(2)    # "x, y"
                options_str = m_line.group(3)

                start_x, start_y = self.lpr # Default to last point referenced (LPR)
                if start_coords_str is not None:
                    start_parts = _split_args(start_coords_str)
                    if len(start_parts) >= 2:
                        start_x = int(self.eval_expr(start_parts[0].strip()))
                        start_y = int(self.eval_expr(start_parts[1].strip()))
                        if not self.running: return False

                end_parts = _split_args(end_coords_str)
                if len(end_parts) < 2:
                    print(f"Error in LINE: invalid end coordinates '{end_coords_str}' at PC {current_pc_num}")
                    self.running = False
                    return False
                end_x = int(self.eval_expr(end_parts[0].strip()))
                end_y = int(self.eval_expr(end_parts[1].strip()))
                if not self.running: return False

                color_index = self.current_fg_color
                box_mode = None # None, "B", or "BF"

                if options_str:
                    # Use _split_args to correctly handle commas inside parentheses (e.g., BOARD(R, C))
                    opts_parts_raw = _split_args(options_str)
                    opts_parts = [opt.strip().upper() for opt in opts_parts_raw]
                    # First part could be color
                    if opts_parts[0] and not opts_parts[0] in ("B", "BF"):
                        # Need to eval original case for expression
                        original_color_expr = opts_parts_raw[0].strip()
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
                coords_str = m_circle.group(1)
                options_str = m_circle.group(2)

                # Parse coordinates using _split_args for nested parens
                coords = _split_args(coords_str)
                if len(coords) < 2:
                    print(f"Error in CIRCLE: expected 2 coordinates, got {len(coords)}"); self.running = False; return False
                cx_e, cy_e = coords[0], coords[1]

                # Parse options: radius, color, start, end, aspect, fill
                opts = _split_args(options_str)
                r_e = opts[0] if len(opts) > 0 else "0"
                color_e = opts[1] if len(opts) > 1 else None
                start_e = opts[2] if len(opts) > 2 else None
                end_e = opts[3] if len(opts) > 3 else None
                aspect_e = opts[4] if len(opts) > 4 else None
                fill_e = opts[5] if len(opts) > 5 else None

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
                coords_str = m_paint.group(1)
                options_str = m_paint.group(2)

                # Parse coordinates using _split_args for nested parens
                coords = _split_args(coords_str)
                if len(coords) < 2:
                    print(f"Error in PAINT: expected 2 coordinates, got {len(coords)}"); self.running = False; return False
                px_e, py_e = coords[0], coords[1]

                # Parse options: fill_color, border_color
                fill_color_e, border_color_e = None, None
                if options_str:
                    opts = _split_args(options_str)
                    fill_color_e = opts[0] if len(opts) > 0 else None
                    border_color_e = opts[1] if len(opts) > 1 else None

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
                coords_str = m_pset.group(1)
                color_e = m_pset.group(2)

                # Split coordinates using _split_args to handle nested parentheses
                coords = _split_args(coords_str)
                if len(coords) < 2:
                    print(f"Error in PSET: expected 2 coordinates, got {len(coords)}"); self.running = False; return False
                px_e, py_e = coords[0], coords[1]

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

        # PRESET - like PSET but defaults to background color
        m_preset = _preset_re.match(statement)
        if m_preset and self.surface:
            try:
                coords_str = m_preset.group(1)
                color_e = m_preset.group(2)

                # Split coordinates using _split_args to handle nested parentheses
                coords = _split_args(coords_str)
                if len(coords) < 2:
                    print(f"Error in PRESET: expected 2 coordinates, got {len(coords)}"); self.running = False; return False
                px_e, py_e = coords[0], coords[1]

                px = int(self.eval_expr(px_e.strip()))
                py = int(self.eval_expr(py_e.strip()))
                if not self.running: return False

                # PRESET defaults to background color (unlike PSET which uses foreground)
                color_idx = self.current_bg_color
                if color_e and color_e.strip():
                    color_idx = int(self.eval_expr(color_e.strip()))
                    if not self.running: return False

                if 0 <= px < self.screen_width and 0 <= py < self.screen_height:
                    self.surface.set_at((px, py), self.basic_color(color_idx))
                    self.lpr = (px, py) # Update LPR
                    self.mark_dirty()
            except Exception as e:
                print(f"Error in PRESET statement '{statement}': {e} at PC {current_pc_num}"); self.running = False
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

        # --- File I/O: LINE INPUT # statement (must come before LINE INPUT) ---
        m_line_input_file = _line_input_file_re.fullmatch(statement)
        if m_line_input_file:
            return self._handle_line_input_file(m_line_input_file, current_pc_num)

        # --- LINE INPUT statement (must come before INPUT) ---
        m_line_input = _line_input_re.fullmatch(statement)
        if m_line_input:
            return self._handle_line_input(m_line_input.group(1).strip(), current_pc_num)

        # --- File I/O: INPUT # statement (must come before regular INPUT) ---
        m_input_file = _input_file_re.fullmatch(statement)
        if m_input_file:
            return self._handle_input_file(m_input_file, current_pc_num)

        # --- INPUT statement ---
        m_input = _input_re.fullmatch(statement)
        if m_input:
            return self._handle_input(m_input.group(1).strip(), current_pc_num)

        # --- ON ERROR GOTO statement (must come before ON...GOTO) ---
        m_on_error = _on_error_re.fullmatch(statement)
        if m_on_error:
            label = m_on_error.group(1).upper()
            if label == "0":
                self.error_handler_label = None  # Disable error handling
            else:
                self.error_handler_label = label
            return False

        # --- ON...GOTO statement ---
        m_on_goto = _on_goto_re.fullmatch(statement)
        if m_on_goto:
            return self._handle_on_goto_gosub(m_on_goto.group(1), m_on_goto.group(2), "GOTO", current_pc_num)

        # --- ON TIMER GOSUB statement (must come before general ON...GOSUB) ---
        m_on_timer = _on_timer_re.fullmatch(statement)
        if m_on_timer:
            return self._handle_on_timer(m_on_timer, current_pc_num)

        # --- ON KEY(n) GOSUB statement (must come before general ON...GOSUB) ---
        m_on_key = _on_key_re.fullmatch(statement)
        if m_on_key:
            key_num = int(m_on_key.group(1))
            label = m_on_key.group(2).upper()
            if 1 <= key_num <= 10:
                self.key_handlers[key_num] = label
            return False

        # --- ON...GOSUB statement ---
        m_on_gosub = _on_gosub_re.fullmatch(statement)
        if m_on_gosub:
            return self._handle_on_goto_gosub(m_on_gosub.group(1), m_on_gosub.group(2), "GOSUB", current_pc_num)

        # --- BEEP statement ---
        if _beep_re.fullmatch(up_stmt):
            self._do_beep()
            return False

        # --- SOUND statement ---
        m_sound = _sound_re.fullmatch(statement)
        if m_sound:
            self._do_sound(m_sound.group(1).strip(), m_sound.group(2).strip(), current_pc_num)
            return False

        # --- ERASE statement ---
        m_erase = _erase_re.fullmatch(statement)
        if m_erase:
            self._do_erase(m_erase.group(1).strip(), current_pc_num)
            return False

        # --- DEF FN statement ---
        m_def_fn = _def_fn_re.fullmatch(statement)
        if m_def_fn:
            func_name = m_def_fn.group(1).upper()
            params_str = m_def_fn.group(2)
            expr = m_def_fn.group(3).strip()
            params = []
            if params_str:
                params = [p.strip().upper() for p in params_str.split(',') if p.strip()]
            self.user_functions[func_name] = (params, expr)
            return False

        # --- OPTION BASE statement ---
        m_option_base = _option_base_re.fullmatch(statement)
        if m_option_base:
            self.option_base = int(m_option_base.group(1))
            return False

        # --- REDIM statement (supports multiple arrays: REDIM a(10), b(20)) ---
        if up_stmt.startswith("REDIM "):
            redim_content = statement[6:].strip()  # Remove "REDIM "
            # Check if there are commas outside parentheses (multiple arrays)
            paren_depth = 0
            has_outer_comma = False
            for char in redim_content:
                if char == '(':
                    paren_depth += 1
                elif char == ')':
                    paren_depth -= 1
                elif char == ',' and paren_depth == 0:
                    has_outer_comma = True
                    break
            if has_outer_comma:
                # Split by commas outside parentheses
                declarations = []
                current = ""
                paren_depth = 0
                for char in redim_content:
                    if char == '(':
                        paren_depth += 1
                        current += char
                    elif char == ')':
                        paren_depth -= 1
                        current += char
                    elif char == ',' and paren_depth == 0:
                        if current.strip():
                            declarations.append(current.strip())
                        current = ""
                    else:
                        current += char
                if current.strip():
                    declarations.append(current.strip())
                # Process each declaration
                for decl in declarations:
                    # Match array pattern
                    match = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*[\$%!#&]?)\s*\(([^)]+)\)', decl)
                    if match:
                        self._do_redim(match.group(1).strip(), match.group(2).strip(), current_pc_num)
                        if not self.running:
                            return False
                return False

        m_redim = _redim_re.fullmatch(statement)
        if m_redim:
            self._do_redim(m_redim.group(1).strip(), m_redim.group(2).strip(), current_pc_num)
            return False

        # --- PLAY statement (Music Macro Language) ---
        m_play = _play_re.fullmatch(statement)
        if m_play:
            self._do_play(m_play.group(1).strip(), current_pc_num)
            return False

        # --- DRAW statement (turtle graphics) ---
        m_draw = _draw_re.fullmatch(statement)
        if m_draw:
            self._do_draw(m_draw.group(1).strip(), current_pc_num)
            return False

        # --- STOP statement ---
        if _stop_re.fullmatch(up_stmt):
            self.stopped = True
            self.running = False
            print(f"STOP at PC {current_pc_num}")
            return False

        # --- TRON statement (trace on) ---
        if _tron_re.fullmatch(up_stmt):
            self.trace_mode = True
            return False

        # --- TROFF statement (trace off) ---
        if _troff_re.fullmatch(up_stmt):
            self.trace_mode = False
            return False

        # --- RUN statement ---
        m_run = _run_re.fullmatch(statement)
        if m_run:
            # RUN without argument restarts current program
            # RUN with line number starts at that line (not supported - we use labels)
            # RUN with filename loads and runs that file (simplified - restart)
            target = m_run.group(1)
            if target:
                target = target.strip()
                # Try as label first
                if target.upper() in self.labels:
                    self.pc = self.labels[target.upper()]
                    # Clear variables for fresh run
                    self.variables.clear()
                    self.gosub_stack.clear()
                    self.for_stack.clear()
                    self.loop_stack.clear()
                    return True
                # Otherwise treat as line number
                try:
                    line_num = int(target)
                    if str(line_num) in self.labels:
                        self.pc = self.labels[str(line_num)]
                        self.variables.clear()
                        self.gosub_stack.clear()
                        self.for_stack.clear()
                        self.loop_stack.clear()
                        return True
                except ValueError:
                    pass
                print(f"Error: RUN target '{target}' not found at PC {current_pc_num}")
                self.running = False
                return False
            else:
                # RUN without argument - restart from beginning
                self.pc = 0
                self.variables.clear()
                self.gosub_stack.clear()
                self.for_stack.clear()
                self.loop_stack.clear()
                self.data_pointer = 0
                return True

        # --- CONT statement (continue after STOP) ---
        if _cont_re.fullmatch(up_stmt):
            if self.stopped:
                self.stopped = False
                self.running = True
                # Continue from current PC (already pointing to next statement)
                return False
            else:
                print(f"Error: CONT without STOP at PC {current_pc_num}")
                # Just continue execution
                return False

        # --- CHAIN statement (load and run another program) ---
        m_chain = _chain_re.fullmatch(statement)
        if m_chain:
            filename_expr = m_chain.group(1).strip()
            filename = str(self.eval_expr(filename_expr))
            if not self.running:
                return False
            try:
                with open(filename, 'r') as f:
                    new_program = f.read().splitlines()
                # Keep COMMON SHARED variables (simplified - keep all)
                saved_vars = dict(self.variables)
                self.reset(new_program)
                # Restore variables (CHAIN preserves COMMON variables)
                self.variables.update(saved_vars)
                return True
            except FileNotFoundError:
                print(f"Error: CHAIN file '{filename}' not found at PC {current_pc_num}")
                self.running = False
                return False
            except Exception as e:
                print(f"Error: CHAIN failed: {e} at PC {current_pc_num}")
                self.running = False
                return False

        # --- KEY n, string$ statement (define function key) ---
        m_key = _key_re.fullmatch(statement)
        if m_key:
            key_num = int(m_key.group(1))
            key_str = str(self.eval_expr(m_key.group(2).strip()))
            if not self.running:
                return False
            if 1 <= key_num <= 10:
                self.key_definitions[key_num] = key_str
            return False

        # --- KEY(n) ON/OFF/STOP statement ---
        m_key_on_off = _key_on_off_re.fullmatch(statement)
        if m_key_on_off:
            key_num = int(m_key_on_off.group(1))
            mode = m_key_on_off.group(2).upper()
            if 1 <= key_num <= 10:
                if mode == "ON":
                    self.key_enabled[key_num] = True
                elif mode == "OFF":
                    self.key_enabled[key_num] = False
                elif mode == "STOP":
                    self.key_enabled[key_num] = False  # Suspend events
            return False

        # --- KEY ON/OFF/LIST statement ---
        m_key_list = _key_list_re.fullmatch(statement)
        if m_key_list:
            mode = m_key_list.group(1).upper()
            if mode == "LIST":
                # Display key assignments (simplified output)
                for i in range(1, 11):
                    defn = self.key_definitions.get(i, "")
                    print(f"F{i}: {defn}")
            # KEY ON/OFF affects display of key line at bottom (ignored in this impl)
            return False

        # --- $INCLUDE metacommand (handled during parsing, but accept here) ---
        if _include_re.match(statement):
            # Already processed during file loading, skip here
            return False

        # --- $DYNAMIC/$STATIC metacommands (array storage - informational only) ---
        if _dynamic_re.match(statement) or _static_re.match(statement):
            # These affect array allocation strategy, but Python handles this automatically
            return False

        if _end_re.fullmatch(up_stmt):
            self.running = False
            return False # END statement, stop execution

        # --- DEFINT/DEFSNG/DEFDBL/DEFLNG/DEFSTR (ignored, Python handles types dynamically) ---
        if _deftype_re.fullmatch(statement):
            return False  # Silently ignore type declarations

        # --- PALETTE statement ---
        m_palette = _palette_re.fullmatch(statement)
        if m_palette:
            # For now, just accept and ignore palette changes
            # Full implementation would modify self.colors
            return False

        # --- PCOPY statement (copy video pages) ---
        m_pcopy = _pcopy_re.fullmatch(statement)
        if m_pcopy:
            return self._handle_pcopy(int(m_pcopy.group(1)), int(m_pcopy.group(2)), current_pc_num)

        # --- VIEW PRINT statement ---
        m_view_print = _view_print_re.fullmatch(statement)
        if m_view_print:
            if m_view_print.group(1) and m_view_print.group(2):
                self.view_print_top = int(m_view_print.group(1))
                self.view_print_bottom = int(m_view_print.group(2))
            else:
                # Reset to full screen
                font_h = self.font.get_height() if self.font else FONT_SIZE
                if font_h > 0:
                    self.view_print_top = 1
                    self.view_print_bottom = self.screen_height // font_h
            return False

        # --- WIDTH statement ---
        m_width = _width_re.fullmatch(statement)
        if m_width:
            # WIDTH columns[, rows] - ignored for now (display is fixed)
            return False

        # --- WAIT statement (port I/O emulated as no-op) ---
        m_wait = _wait_re.fullmatch(statement)
        if m_wait:
            return False  # Emulated as no-op

        # --- TIMER ON/OFF statement ---
        m_timer_on_off = _timer_on_off_re.fullmatch(statement)
        if m_timer_on_off:
            mode = m_timer_on_off.group(1).upper()
            if mode == "ON":
                self.timer_enabled = True
                self.timer_last_trigger = time.time()
            elif mode == "OFF":
                self.timer_enabled = False
            # STOP suspends timer events until ON is used again
            elif mode == "STOP":
                self.timer_enabled = False
            return False

        # --- OUT statement (port I/O emulated) ---
        m_out = _out_re.fullmatch(statement)
        if m_out:
            port = int(self.eval_expr(m_out.group(1).strip()))
            value = int(self.eval_expr(m_out.group(2).strip()))
            self.io_ports[port] = value & 0xFF
            return False

        # --- DEF SEG statement (memory segment emulated) ---
        m_def_seg = _def_seg_re.fullmatch(statement)
        if m_def_seg:
            if m_def_seg.group(1):
                self.memory_segment = int(self.eval_expr(m_def_seg.group(1).strip()))
            else:
                self.memory_segment = 0  # Reset to default
            return False

        # --- POKE statement (memory emulated) ---
        m_poke = _poke_re.fullmatch(statement)
        if m_poke:
            address = int(self.eval_expr(m_poke.group(1).strip()))
            value = int(self.eval_expr(m_poke.group(2).strip()))
            full_addr = (self.memory_segment << 4) + address
            self.emulated_memory[full_addr] = value & 0xFF
            return False

        # --- COMMON SHARED statement ---
        m_common_shared = _common_shared_re.fullmatch(statement)
        if m_common_shared:
            # Variables listed are already global in our implementation
            return False

        # --- DIM SHARED statement ---
        m_dim_shared = _dim_shared_re.fullmatch(statement)
        if m_dim_shared:
            # Parse as regular DIM, just ignore SHARED keyword
            dim_content = m_dim_shared.group(1).strip()
            # Handle multiple DIM declarations separated by commas
            # e.g., "DIM SHARED LBan&(x), RBan&(x)" -> handle each array separately
            return self._handle_multi_dim(dim_content, current_pc_num)

        # --- GET (graphics) statement ---
        m_get_gfx = _get_gfx_re.fullmatch(statement)
        if m_get_gfx:
            return self._do_get_graphics(m_get_gfx, current_pc_num)

        # --- PUT (graphics) statement ---
        m_put_gfx = _put_gfx_re.fullmatch(statement)
        if m_put_gfx:
            return self._do_put_graphics(m_put_gfx, current_pc_num)

        # --- RESUME statement ---
        m_resume = _resume_re.fullmatch(statement)
        if m_resume:
            if not self.in_error_handler:
                print(f"Error: RESUME without error at PC {current_pc_num}")
                self.running = False
                return False
            self.in_error_handler = False
            target = m_resume.group(1)
            if target:
                if target.upper() == "NEXT":
                    self.pc = self.error_resume_pc + 1
                else:
                    return self._do_goto(target.upper())
            else:
                self.pc = self.error_resume_pc
            return True

        # --- DECLARE statement (ignored, we parse SUB/FUNCTION at runtime) ---
        m_declare = _declare_re.fullmatch(statement)
        if m_declare:
            return False  # Declarations are informational only

        # --- SUB definition ---
        m_sub = _sub_re.fullmatch(statement)
        if m_sub:
            return self._handle_sub_definition(m_sub, current_pc_num)

        # --- END SUB ---
        if _end_sub_re.fullmatch(up_stmt):
            return self._handle_end_sub(current_pc_num)

        # --- FUNCTION definition ---
        m_function = _function_re.fullmatch(statement)
        if m_function:
            return self._handle_function_definition(m_function, current_pc_num)

        # --- END FUNCTION ---
        if _end_function_re.fullmatch(up_stmt):
            return self._handle_end_function(current_pc_num)

        # --- EXIT SUB ---
        if _exit_sub_re.fullmatch(up_stmt):
            return self._handle_exit_sub(current_pc_num)

        # --- EXIT FUNCTION ---
        if _exit_function_re.fullmatch(up_stmt):
            return self._handle_exit_function(current_pc_num)

        # --- SHARED statement (in SUB/FUNCTION) ---
        m_shared = _shared_re.fullmatch(statement)
        if m_shared:
            # Variables are already global in our simple implementation
            return False

        # --- CALL statement ---
        m_call = _call_re.fullmatch(statement)
        if m_call:
            return self._handle_call(m_call, current_pc_num)

        # --- TYPE definition ---
        m_type = _type_re.fullmatch(statement)
        if m_type:
            self.current_type = m_type.group(1).upper()
            self.type_definitions[self.current_type] = {}
            return False

        # --- END TYPE ---
        if _end_type_re.fullmatch(up_stmt):
            self.current_type = None
            return False

        # --- Type field definition (inside TYPE block) ---
        if self.current_type:
            # Parse field definition: fieldname AS type
            field_match = re.match(r"([a-zA-Z_][a-zA-Z0-9_]*)\s+AS\s+(INTEGER|LONG|SINGLE|DOUBLE|STRING)", statement, re.IGNORECASE)
            if field_match:
                field_name = field_match.group(1).upper()
                field_type = field_match.group(2).upper()
                self.type_definitions[self.current_type][field_name] = field_type
                return False

        # --- File I/O: OPEN statement ---
        m_open = _open_re.fullmatch(statement)
        if m_open:
            return self._handle_open(m_open, current_pc_num)

        # --- File I/O: CLOSE statement ---
        m_close = _close_re.fullmatch(statement)
        if m_close:
            return self._handle_close(m_close, current_pc_num)

        # --- File I/O: WRITE # statement ---
        m_write_file = _write_file_re.fullmatch(statement)
        if m_write_file:
            return self._handle_write_file(m_write_file, current_pc_num)

        # --- File I/O: GET # statement (binary read) ---
        m_get_file = _get_file_re.fullmatch(statement)
        if m_get_file:
            return self._handle_get_file(m_get_file, current_pc_num)

        # --- File I/O: PUT # statement (binary write) ---
        m_put_file = _put_file_re.fullmatch(statement)
        if m_put_file:
            return self._handle_put_file(m_put_file, current_pc_num)

        # --- File system: KILL (delete file) ---
        m_kill = _kill_re.fullmatch(statement)
        if m_kill:
            return self._handle_kill(m_kill.group(1).strip(), current_pc_num)

        # --- File system: NAME (rename file) ---
        m_name = _name_re.fullmatch(statement)
        if m_name:
            return self._handle_name(m_name.group(1).strip(), m_name.group(2).strip(), current_pc_num)

        # --- File system: MKDIR (create directory) ---
        m_mkdir = _mkdir_re.fullmatch(statement)
        if m_mkdir:
            return self._handle_mkdir(m_mkdir.group(1).strip(), current_pc_num)

        # --- File system: RMDIR (remove directory) ---
        m_rmdir = _rmdir_re.fullmatch(statement)
        if m_rmdir:
            return self._handle_rmdir(m_rmdir.group(1).strip(), current_pc_num)

        # --- File system: CHDIR (change directory) ---
        m_chdir = _chdir_re.fullmatch(statement)
        if m_chdir:
            return self._handle_chdir(m_chdir.group(1).strip(), current_pc_num)

        # --- File system: FILES (list directory) ---
        m_files = _files_re.fullmatch(statement)
        if m_files:
            return self._handle_files(m_files.group(1), current_pc_num)

        # --- File positioning: SEEK ---
        m_seek = _seek_re.fullmatch(statement)
        if m_seek:
            return self._handle_seek(m_seek.group(1), m_seek.group(2).strip(), current_pc_num)

        # --- ERROR statement (trigger runtime error) ---
        m_error = _error_re.fullmatch(statement)
        if m_error:
            return self._handle_error(m_error.group(1).strip(), current_pc_num)

        # --- CLEAR statement ---
        m_clear = _clear_re.fullmatch(statement)
        if m_clear:
            return self._handle_clear(current_pc_num)

        # --- SYSTEM statement (exit to OS) ---
        m_system = _system_re.fullmatch(statement)
        if m_system:
            self.running = False
            return False

        # --- SHELL statement (execute shell command) ---
        m_shell = _shell_re.fullmatch(statement)
        if m_shell:
            return self._handle_shell(m_shell.group(1), current_pc_num)

        # --- VIEW statement (graphics viewport) ---
        m_view = _view_re.fullmatch(statement)
        if m_view:
            return self._handle_view(m_view, current_pc_num)

        # --- WINDOW statement (logical coordinates) ---
        m_window = _window_re.fullmatch(statement)
        if m_window:
            return self._handle_window(m_window, statement, current_pc_num)

        # --- LPRINT USING statement (formatted printer output) ---
        m_lprint_using = _lprint_using_re.fullmatch(statement)
        if m_lprint_using:
            return self._handle_lprint_using(m_lprint_using.group(1).strip(), m_lprint_using.group(2).strip(), current_pc_num)

        # --- LPRINT statement (print to console) ---
        m_lprint = _lprint_re.fullmatch(statement)
        if m_lprint:
            return self._handle_lprint(m_lprint.group(1), current_pc_num)

        # --- FIELD statement (random access file fields) ---
        m_field = _field_re.fullmatch(statement)
        if m_field:
            return self._handle_field(m_field, current_pc_num)

        # --- LSET statement (left-justify string in field) ---
        m_lset = _lset_re.fullmatch(statement)
        if m_lset:
            return self._handle_lset(m_lset.group(1), m_lset.group(2), current_pc_num)

        # --- RSET statement (right-justify string in field) ---
        m_rset = _rset_re.fullmatch(statement)
        if m_rset:
            return self._handle_rset(m_rset.group(1), m_rset.group(2), current_pc_num)

        # --- ENVIRON statement (set environment variable) ---
        m_environ = _environ_set_re.fullmatch(statement)
        if m_environ:
            return self._handle_environ_set(m_environ.group(1).strip(), current_pc_num)

        # --- Implicit SUB/FUNCTION call (without CALL keyword) ---
        # Check if statement starts with a known procedure name
        implicit_call_match = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*(.*)', statement)
        if implicit_call_match:
            proc_name = implicit_call_match.group(1).upper()
            args_str = implicit_call_match.group(2).strip()
            if proc_name in self.procedures:
                # Treat as a SUB call: MySub arg1, arg2 -> CALL MySub(arg1, arg2)
                return self._handle_call_sub(proc_name, args_str, current_pc_num)

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

    def _handle_input(self, input_content: str, pc: int) -> bool:
        """Handle INPUT statement. QBasic 4.5 format: INPUT ["prompt"{;|,}] var[, var...]"""
        # Parse the INPUT statement content
        prompt = ""
        show_question = True  # Show "?" by default

        content = input_content.strip()

        # Check for prompt string
        if content.startswith('"'):
            # Find end of string
            end_quote = content.find('"', 1)
            if end_quote > 0:
                prompt = content[1:end_quote]
                content = content[end_quote + 1:].strip()
                # Check separator after prompt
                if content.startswith(';'):
                    show_question = True
                    content = content[1:].strip()
                elif content.startswith(','):
                    show_question = False
                    content = content[1:].strip()

        # Parse variable names
        var_names = [v.strip() for v in content.split(',') if v.strip()]
        if not var_names:
            print(f"Error: INPUT statement requires at least one variable at PC {pc}")
            self.running = False
            return False

        # Set up input mode
        self.input_mode = True
        self.input_buffer = ""
        self.input_prompt = prompt + ("? " if show_question else "")
        self.input_variables = var_names
        self.input_cursor_pos = 0

        # Display prompt
        if self.surface and self.font and self.input_prompt:
            self._draw_input_prompt()

        return True  # Indicates interpreter should pause for input

    def _draw_input_prompt(self) -> None:
        """Draw the input prompt and current buffer."""
        if not self.surface or not self.font:
            return

        f_w = self.font.size(" ")[0] if self.font.size(" ")[0] > 0 else 8
        f_h = self.font.get_height()

        x_pos = (self.text_cursor[0] - 1) * f_w
        y_pos = (self.text_cursor[1] - 1) * f_h

        # Draw prompt + buffer
        display_text = self.input_prompt + self.input_buffer + "_"
        try:
            text_surface = self.font.render(display_text, True,
                                           self.basic_color(self.current_fg_color),
                                           self.basic_color(self.current_bg_color))
            self.surface.blit(text_surface, (x_pos, y_pos))
            self.mark_dirty()
        except pygame.error:
            pass

    def _process_input_key(self, key: str) -> bool:
        """Process a key press during input mode. Returns True when input is complete."""
        if key == chr(13):  # Enter
            return self._complete_input()
        elif key == chr(8):  # Backspace
            if self.input_buffer:
                self.input_buffer = self.input_buffer[:-1]
                self._redraw_input_line()
        elif key == chr(27):  # Escape - cancel input
            self.input_buffer = ""
            return self._complete_input()
        elif len(key) == 1 and ord(key) >= 32:  # Printable character
            self.input_buffer += key
            self._redraw_input_line()
        return False

    def _redraw_input_line(self) -> None:
        """Redraw the input line (clear and redraw)."""
        if not self.surface or not self.font:
            return

        f_w = self.font.size(" ")[0] if self.font.size(" ")[0] > 0 else 8
        f_h = self.font.get_height()

        x_pos = (self.text_cursor[0] - 1) * f_w
        y_pos = (self.text_cursor[1] - 1) * f_h

        # Clear the line
        clear_width = self.screen_width - x_pos
        pygame.draw.rect(self.surface, self.basic_color(self.current_bg_color),
                        (x_pos, y_pos, clear_width, f_h))

        # Redraw
        self._draw_input_prompt()

    def _complete_input(self) -> bool:
        """Complete input processing and assign values to variables."""
        self.input_mode = False
        is_line_input = getattr(self, '_line_input_mode', False)
        self._line_input_mode = False  # Reset for next input

        # Parse input values
        input_values = []
        if self.input_buffer:
            if is_line_input:
                # LINE INPUT: take entire line as single value, no comma parsing
                input_values = [self.input_buffer]
            else:
                # Regular INPUT: Split by comma, respecting quoted strings
                current = ""
                in_string = False
                for char in self.input_buffer:
                    if char == '"':
                        in_string = not in_string
                    elif char == ',' and not in_string:
                        input_values.append(current.strip())
                        current = ""
                        continue
                    current += char
                if current:
                    input_values.append(current.strip())

        # Assign values to variables
        for i, var_name in enumerate(self.input_variables):
            if i < len(input_values):
                value = input_values[i]
                # Determine type based on variable name
                var_upper = var_name.upper()
                if var_upper.endswith('$'):
                    # String variable - remove quotes if present (only for regular INPUT)
                    if not is_line_input and value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                else:
                    # Numeric variable - try to convert
                    try:
                        if '.' in value or 'E' in value.upper():
                            value = float(value)
                        else:
                            value = int(value)
                    except ValueError:
                        value = 0  # Default to 0 for invalid numeric input
                self._assign_variable(var_name, value, self.pc - 1)
            else:
                # No more input values - use defaults
                var_upper = var_name.upper()
                if var_upper.endswith('$'):
                    self._assign_variable(var_name, "", self.pc - 1)
                else:
                    self._assign_variable(var_name, 0, self.pc - 1)

        # Move cursor to next line
        self.text_cursor = (1, self.text_cursor[1] + 1)
        return True

    def _handle_on_goto_gosub(self, expr: str, labels_str: str, branch_type: str, pc: int) -> bool:
        """Handle ON...GOTO and ON...GOSUB statements."""
        # Evaluate the selector expression
        selector = self.eval_expr(expr.strip())
        if not self.running:
            return False

        try:
            index = int(selector)
        except (ValueError, TypeError):
            print(f"Error: ON {branch_type} selector must be numeric at PC {pc}")
            self.running = False
            return False

        # Parse label list
        labels = [l.strip().upper() for l in labels_str.split(',')]

        # QBasic: if index < 1 or index > number of labels, continue to next statement
        if index < 1 or index > len(labels):
            return False  # Continue to next statement

        target_label = labels[index - 1]  # 1-based indexing

        if branch_type == "GOTO":
            return self._do_goto(target_label)
        else:  # GOSUB
            return self._do_gosub(target_label)

    def _handle_line_input(self, input_content: str, pc: int) -> bool:
        """Handle LINE INPUT statement. QBasic 4.5 format: LINE INPUT ["prompt"{;|,}] var$
        Unlike INPUT, LINE INPUT reads the entire line without parsing commas."""
        prompt = ""
        show_question = False  # LINE INPUT doesn't show "?" by default

        content = input_content.strip()

        # Check for prompt string
        if content.startswith('"'):
            end_quote = content.find('"', 1)
            if end_quote > 0:
                prompt = content[1:end_quote]
                content = content[end_quote + 1:].strip()
                # Check separator after prompt
                if content.startswith(';'):
                    content = content[1:].strip()
                elif content.startswith(','):
                    content = content[1:].strip()

        # LINE INPUT only accepts one variable (must be string)
        var_name = content.strip()
        if not var_name:
            print(f"Error: LINE INPUT statement requires a variable at PC {pc}")
            self.running = False
            return False

        # Set up input mode (reuse INPUT mode infrastructure)
        self.input_mode = True
        self.input_buffer = ""
        self.input_prompt = prompt
        self.input_variables = [var_name]
        self.input_cursor_pos = 0
        # Mark as LINE INPUT mode to skip comma parsing
        self._line_input_mode = True

        # Display prompt
        if self.surface and self.font and self.input_prompt:
            self._draw_input_prompt()

        return True

    def _do_beep(self) -> None:
        """Execute BEEP command - plays a short beep sound."""
        try:
            # Generate a simple beep using pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1)

            # Create a simple sine wave beep (800 Hz, 0.2 seconds)
            import array
            sample_rate = 22050
            frequency = 800
            duration = 0.2
            n_samples = int(sample_rate * duration)

            # Generate sine wave
            samples = array.array('h', [0] * n_samples)
            for i in range(n_samples):
                t = i / sample_rate
                samples[i] = int(32767 * 0.5 * math.sin(2 * math.pi * frequency * t))

            # Create and play sound
            sound = pygame.mixer.Sound(buffer=samples)
            sound.play()
        except Exception:
            pass  # Silently fail if audio not available

    def _do_sound(self, freq_expr: str, duration_expr: str, pc: int) -> None:
        """Execute SOUND command - generates tone with specified frequency and duration.
        SOUND frequency, duration (duration in clock ticks, 18.2 ticks per second)"""
        try:
            frequency = float(self.eval_expr(freq_expr))
            duration_ticks = float(self.eval_expr(duration_expr))
            if not self.running:
                return

            # Convert duration from clock ticks to seconds (18.2 ticks per second in QBasic)
            duration = duration_ticks / 18.2

            # Limit duration to reasonable value
            duration = min(duration, 10.0)

            # Frequency must be between 37 and 32767 Hz in QBasic
            if frequency < 37 or frequency > 32767:
                return

            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1)

            import array
            sample_rate = 22050
            n_samples = int(sample_rate * duration)

            # Generate sine wave
            samples = array.array('h', [0] * n_samples)
            for i in range(n_samples):
                t = i / sample_rate
                samples[i] = int(32767 * 0.5 * math.sin(2 * math.pi * frequency * t))

            # Create and play sound
            sound = pygame.mixer.Sound(buffer=samples)
            sound.play()
        except Exception as e:
            print(f"Error in SOUND statement at PC {pc}: {e}")

    def _do_erase(self, array_list: str, pc: int) -> None:
        """Execute ERASE command - erases (clears) specified arrays."""
        array_names = [name.strip().upper() for name in array_list.split(',')]

        for name in array_names:
            # Try the name as-is first
            if name in self.variables and isinstance(self.variables[name], list):
                del self.variables[name]
            else:
                # Try without type suffix
                base_name = name.rstrip('$%')
                if base_name in self.variables and isinstance(self.variables[base_name], list):
                    del self.variables[base_name]

    def _do_print_using(self, format_expr: str, values_expr: str, pc: int) -> bool:
        """Execute PRINT USING statement - formatted output.
        Format specifiers:
        # - digit position
        . - decimal point position
        , - thousands separator
        + - print sign
        - - trailing minus for negative
        $$ - floating dollar sign
        ** - fill leading with asterisks
        ! - first character of string
        & - entire string
        \\ \\ - string field width (spaces between backslashes)
        """
        try:
            # Evaluate the format string
            format_str = str(self.eval_expr(format_expr))
            if not self.running:
                return False

            # Parse and evaluate the values (comma-separated)
            value_parts = []
            current = ""
            paren_level = 0
            in_string = False
            for char in values_expr:
                if char == '"':
                    in_string = not in_string
                    current += char
                elif char == '(' and not in_string:
                    paren_level += 1
                    current += char
                elif char == ')' and not in_string:
                    paren_level -= 1
                    current += char
                elif char == ',' and paren_level == 0 and not in_string:
                    if current.strip():
                        value_parts.append(current.strip())
                    current = ""
                else:
                    current += char
            if current.strip():
                value_parts.append(current.strip())

            values = []
            for part in value_parts:
                val = self.eval_expr(part)
                if not self.running:
                    return False
                values.append(val)

            # Format the output
            output = self._format_using(format_str, values)

            # Print the formatted output
            x_render_pos = (self.text_cursor[0] - 1) * (self.font.size(" ")[0] if self.font else FONT_SIZE // 2)
            y_render_pos = (self.text_cursor[1] - 1) * (self.font.get_height() if self.font else FONT_SIZE)

            if self.surface and self.font:
                fg_color = self.basic_color(self.current_fg_color)
                text_surface = self.font.render(output, True, fg_color)
                self.surface.blit(text_surface, (x_render_pos, y_render_pos))
                self.mark_dirty()

            # Move cursor
            char_width = self.font.size(" ")[0] if self.font else FONT_SIZE // 2
            self.text_cursor = (self.text_cursor[0] + len(output), self.text_cursor[1])

            # Newline at end
            self.text_cursor = (1, self.text_cursor[1] + 1)

            return False
        except Exception as e:
            print(f"Error in PRINT USING at PC {pc}: {e}")
            self.running = False
            return False

    def _format_using(self, format_str: str, values: List[Any]) -> str:
        """Format values according to QBasic PRINT USING format string."""
        result = ""
        val_idx = 0
        i = 0

        while i < len(format_str):
            ch = format_str[i]

            # Check for numeric format
            if ch in '#+-*$':
                # Find the extent of the numeric format
                num_format = ""
                while i < len(format_str) and format_str[i] in '#.,+-*$':
                    num_format += format_str[i]
                    i += 1
                # Handle exponential notation
                if i < len(format_str) and format_str[i:i+4] in ['^^^^', '^^^^']:
                    num_format += format_str[i:i+4]
                    i += 4

                if val_idx < len(values):
                    result += self._format_numeric(num_format, values[val_idx])
                    val_idx += 1
                continue

            # String format: ! (first char)
            if ch == '!':
                if val_idx < len(values):
                    s = str(values[val_idx])
                    result += s[0] if s else " "
                    val_idx += 1
                i += 1
                continue

            # String format: & (entire string)
            if ch == '&':
                if val_idx < len(values):
                    result += str(values[val_idx])
                    val_idx += 1
                i += 1
                continue

            # String format: \  \ (fixed width, spaces between backslashes)
            if ch == '\\':
                # Count characters between backslashes (inclusive)
                field_width = 2  # Minimum width including backslashes
                j = i + 1
                while j < len(format_str) and format_str[j] != '\\':
                    field_width += 1
                    j += 1
                if j < len(format_str):
                    field_width += 1  # Include closing backslash
                    j += 1

                if val_idx < len(values):
                    s = str(values[val_idx])
                    # Left-justify in field, truncate or pad
                    if len(s) >= field_width:
                        result += s[:field_width]
                    else:
                        result += s.ljust(field_width)
                    val_idx += 1

                i = j
                continue

            # Underscore escapes the next character (literal)
            if ch == '_' and i + 1 < len(format_str):
                result += format_str[i + 1]
                i += 2
                continue

            # Regular character
            result += ch
            i += 1

        return result

    def _format_numeric(self, fmt: str, value: Any) -> str:
        """Format a numeric value according to QBasic numeric format string."""
        try:
            num = float(value)
        except (ValueError, TypeError):
            num = 0.0

        # Count format components
        has_sign = '+' in fmt or '-' in fmt
        has_dollar = '$$' in fmt or '$' in fmt
        has_asterisk = '**' in fmt
        has_comma = ',' in fmt
        has_decimal = '.' in fmt

        # Determine field width and decimal places
        # Count # signs and decimal point position
        hash_count = fmt.count('#')
        if has_dollar:
            hash_count += 1
        if has_asterisk:
            hash_count += 2

        decimal_places = 0
        if has_decimal:
            # Count # after decimal point
            dot_pos = fmt.find('.')
            decimal_places = fmt[dot_pos:].count('#')

        # Format the number
        if decimal_places > 0:
            formatted = f"{abs(num):.{decimal_places}f}"
        else:
            formatted = f"{int(abs(num))}"

        # Add commas if requested
        if has_comma:
            parts = formatted.split('.')
            int_part = parts[0]
            # Insert commas every 3 digits from the right
            new_int_part = ""
            for i, c in enumerate(reversed(int_part)):
                if i > 0 and i % 3 == 0:
                    new_int_part = ',' + new_int_part
                new_int_part = c + new_int_part
            formatted = new_int_part + ('.' + parts[1] if len(parts) > 1 else '')

        # Handle sign
        sign = ""
        if num < 0:
            sign = "-"
        elif has_sign and '+' in fmt:
            sign = "+"

        # Handle trailing minus
        trailing_minus = ""
        if '-' in fmt and fmt.endswith('-'):
            if num < 0:
                trailing_minus = "-"
                sign = ""  # Don't add leading sign
            else:
                trailing_minus = " "

        # Build result with fill characters
        result = sign + formatted + trailing_minus

        # Handle dollar sign
        if has_dollar:
            result = "$" + result

        # Pad or fill to width
        total_width = hash_count + (1 if has_decimal else 0) + (1 if has_sign or num < 0 else 0)
        if has_dollar:
            total_width += 1

        if has_asterisk:
            # Fill with asterisks
            while len(result) < total_width:
                result = "*" + result
        else:
            # Fill with spaces
            while len(result) < total_width:
                result = " " + result

        return result

    def _do_redim(self, var_name: str, dims_str: str, pc: int) -> None:
        """Execute REDIM command - redimension a dynamic array."""
        var_name_upper = var_name.upper()

        try:
            # Parse dimensions - supports both "REDIM A(10)" and "REDIM A(0 TO 10)" syntax
            dims = []
            for dim_expr in _split_args(dims_str):
                dim_expr = dim_expr.strip()
                # Check for "lower TO upper" syntax (case-insensitive)
                to_match = re.match(r'(.+?)\s+TO\s+(.+)', dim_expr, re.IGNORECASE)
                if to_match:
                    lower_bound = int(self.eval_expr(to_match.group(1).strip()))
                    upper_bound = int(self.eval_expr(to_match.group(2).strip()))
                    if not self.running:
                        return
                    dims.append(upper_bound - lower_bound + 1)
                else:
                    dim_val = self.eval_expr(dim_expr)
                    if not self.running:
                        return
                    dims.append(int(dim_val) + 1 - self.option_base)  # QBasic uses inclusive upper bound

            # Determine default value based on variable type
            default_val = "" if var_name.endswith("$") else 0

            # Create new array (overwrite any existing)
            if len(dims) == 1:
                self.variables[var_name_upper] = [default_val] * dims[0]
            elif len(dims) == 2:
                self.variables[var_name_upper] = [[default_val] * dims[1] for _ in range(dims[0])]
            else:
                # For higher dimensions, create nested lists
                def create_nd_list(dims, default):
                    if len(dims) == 1:
                        return [default] * dims[0]
                    return [create_nd_list(dims[1:], default) for _ in range(dims[0])]
                self.variables[var_name_upper] = create_nd_list(dims, default_val)

        except Exception as e:
            print(f"Error in REDIM at PC {pc}: {e}")
            self.running = False

    def _handle_multi_dim(self, dim_content: str, pc: int) -> bool:
        """Handle DIM statement with multiple declarations.

        Supports:
        - DIM a, b, c (multiple scalars)
        - DIM a AS INTEGER, b AS STRING (multiple with types)
        - DIM a(10), b(20) (multiple arrays)
        - DIM a(10) AS INTEGER, b(20) AS STRING (multiple arrays with types)
        - DIM a((expr * 2) + 1) AS INTEGER (complex expressions in bounds)
        """
        # Split by commas, but respect parentheses for array dimensions
        declarations = []
        current = ""
        paren_depth = 0
        for char in dim_content:
            if char == '(':
                paren_depth += 1
                current += char
            elif char == ')':
                paren_depth -= 1
                current += char
            elif char == ',' and paren_depth == 0:
                if current.strip():
                    declarations.append(current.strip())
                current = ""
            else:
                current += char
        if current.strip():
            declarations.append(current.strip())

        # Process each declaration directly
        for decl in declarations:
            if not self._handle_single_dim(decl, pc):
                if not self.running:
                    return False
        return False

    def _handle_single_dim(self, decl: str, pc: int) -> bool:
        """Handle a single DIM declaration (scalar or array).

        Formats:
        - varname (scalar)
        - varname AS type (scalar with type)
        - varname(bounds) (array)
        - varname(bounds) AS type (array with type)
        """
        decl = decl.strip()

        # Check for AS clause at the end
        type_name = None
        as_match = re.search(r'\s+AS\s+(\w+)\s*$', decl, re.IGNORECASE)
        if as_match:
            type_name = as_match.group(1).upper()
            decl = decl[:as_match.start()].strip()

        # Check if this is an array declaration (has parentheses)
        # Need to find the opening paren that belongs to the array bounds
        paren_start = -1
        for i, char in enumerate(decl):
            if char == '(':
                paren_start = i
                break

        if paren_start > 0:
            # Array declaration
            var_name = decl[:paren_start].strip().upper()
            # Extract bounds - find matching closing paren
            paren_depth = 0
            bounds_str = ""
            for i in range(paren_start, len(decl)):
                char = decl[i]
                if char == '(':
                    paren_depth += 1
                    if paren_depth > 1:  # Don't include outermost parens
                        bounds_str += char
                elif char == ')':
                    paren_depth -= 1
                    if paren_depth > 0:  # Don't include outermost parens
                        bounds_str += char
                elif paren_depth > 0:
                    bounds_str += char

            if var_name in self.constants:
                print(f"Error: Cannot DIM constant '{var_name}' at PC {pc}")
                self.running = False
                return False

            try:
                # Parse array dimensions
                dims = []
                for idx_spec in _split_args(bounds_str):
                    idx_spec = idx_spec.strip()
                    # Check for "lower TO upper" syntax
                    to_match = re.match(r'(.+?)\s+TO\s+(.+)', idx_spec, re.IGNORECASE)
                    if to_match:
                        lower_bound = int(self.eval_expr(to_match.group(1).strip()))
                        upper_bound = int(self.eval_expr(to_match.group(2).strip()))
                        if not self.running: return False
                        dims.append(upper_bound - lower_bound + 1)
                    else:
                        upper_bound = int(self.eval_expr(idx_spec))
                        if not self.running: return False
                        dims.append(upper_bound + 1 - self.option_base)

                # Determine default value
                def create_default():
                    if type_name and type_name in self.type_definitions:
                        instance = {'_type': type_name}
                        for field_name, field_type in self.type_definitions[type_name].items():
                            instance[field_name] = "" if field_type == 'STRING' else 0
                        return instance
                    elif var_name.endswith("$") or type_name == 'STRING':
                        return ""
                    else:
                        return 0

                # Create N-dimensional array
                def create_nd_array(dimensions, default_factory):
                    if len(dimensions) == 1:
                        return [default_factory() for _ in range(dimensions[0])]
                    return [create_nd_array(dimensions[1:], default_factory) for _ in range(dimensions[0])]

                self.variables[var_name] = create_nd_array(dims, create_default)
            except Exception as e:
                print(f"Error in DIM statement for '{decl}': {e} at PC {pc}")
                self.running = False
                return False
        else:
            # Scalar declaration
            var_name = decl.strip().upper()
            if var_name in self.constants:
                print(f"Error: Cannot DIM constant '{var_name}' at PC {pc}")
                self.running = False
                return False

            if type_name and type_name in self.type_definitions:
                instance = {'_type': type_name}
                for field_name, field_type in self.type_definitions[type_name].items():
                    instance[field_name] = "" if field_type == 'STRING' else 0
                self.variables[var_name] = instance
            elif var_name.endswith('$') or type_name == 'STRING':
                self.variables[var_name] = ""
            else:
                self.variables[var_name] = 0

        return True

    def _do_play(self, mml_expr: str, pc: int) -> None:
        """Execute PLAY command - Music Macro Language.
        MML commands:
        A-G: Notes (with optional # or + for sharp, - for flat)
        O: Set octave (0-6, default 4)
        L: Set default note length (1-64, 1=whole, 4=quarter, etc.)
        T: Set tempo in quarter notes per minute (32-255, default 120)
        N: Play note by number (0-84, 0=rest)
        P/R: Pause/Rest (1-64)
        >: Increase octave
        <: Decrease octave
        MN: Music Normal (7/8 note length)
        ML: Music Legato (full note length)
        MS: Music Staccato (3/4 note length)
        """
        try:
            # Evaluate the MML string expression
            mml_string = str(self.eval_expr(mml_expr))
            if not self.running:
                return

            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1)

            import array

            # MML parsing state
            octave = 4
            default_length = 4  # Quarter note
            tempo = 120  # Quarter notes per minute
            articulation = 7 / 8  # MN by default

            # Note frequencies for octave 0 (C0 to B0)
            note_base_freqs = {
                'C': 16.35, 'D': 18.35, 'E': 20.60, 'F': 21.83,
                'G': 24.50, 'A': 27.50, 'B': 30.87
            }

            i = 0
            mml_upper = mml_string.upper()

            while i < len(mml_upper):
                ch = mml_upper[i]
                i += 1

                # Note commands A-G
                if ch in 'ABCDEFG':
                    note = ch
                    # Check for sharp/flat
                    modifier = 0
                    if i < len(mml_upper) and mml_upper[i] in '#+':
                        modifier = 1
                        i += 1
                    elif i < len(mml_upper) and mml_upper[i] == '-':
                        modifier = -1
                        i += 1

                    # Check for length
                    length = default_length
                    num_str = ""
                    while i < len(mml_upper) and mml_upper[i].isdigit():
                        num_str += mml_upper[i]
                        i += 1
                    if num_str:
                        length = int(num_str)

                    # Check for dot (adds half the note length)
                    dot_mult = 1.0
                    while i < len(mml_upper) and mml_upper[i] == '.':
                        dot_mult += 0.5 * dot_mult
                        i += 1

                    # Calculate frequency
                    base_freq = note_base_freqs[note]
                    # Apply sharp/flat (semitone = 2^(1/12))
                    freq = base_freq * (2 ** octave) * (2 ** (modifier / 12.0))

                    # Calculate duration: (60 / tempo) * (4 / length) * dot_mult
                    duration = (60.0 / tempo) * (4.0 / length) * dot_mult

                    # Play the note
                    self._play_note(freq, duration * articulation)

                # Rest/Pause
                elif ch in 'PR':
                    length = default_length
                    num_str = ""
                    while i < len(mml_upper) and mml_upper[i].isdigit():
                        num_str += mml_upper[i]
                        i += 1
                    if num_str:
                        length = int(num_str)

                    dot_mult = 1.0
                    while i < len(mml_upper) and mml_upper[i] == '.':
                        dot_mult += 0.5 * dot_mult
                        i += 1

                    duration = (60.0 / tempo) * (4.0 / length) * dot_mult
                    time.sleep(duration)

                # Octave command
                elif ch == 'O':
                    num_str = ""
                    while i < len(mml_upper) and mml_upper[i].isdigit():
                        num_str += mml_upper[i]
                        i += 1
                    if num_str:
                        octave = max(0, min(6, int(num_str)))

                # Increase octave
                elif ch == '>':
                    octave = min(6, octave + 1)

                # Decrease octave
                elif ch == '<':
                    octave = max(0, octave - 1)

                # Length command
                elif ch == 'L':
                    num_str = ""
                    while i < len(mml_upper) and mml_upper[i].isdigit():
                        num_str += mml_upper[i]
                        i += 1
                    if num_str:
                        default_length = max(1, min(64, int(num_str)))

                # Tempo command
                elif ch == 'T':
                    num_str = ""
                    while i < len(mml_upper) and mml_upper[i].isdigit():
                        num_str += mml_upper[i]
                        i += 1
                    if num_str:
                        tempo = max(32, min(255, int(num_str)))

                # Note by number
                elif ch == 'N':
                    num_str = ""
                    while i < len(mml_upper) and mml_upper[i].isdigit():
                        num_str += mml_upper[i]
                        i += 1
                    if num_str:
                        note_num = int(num_str)
                        if note_num == 0:
                            # Rest
                            duration = (60.0 / tempo) * (4.0 / default_length)
                            time.sleep(duration)
                        elif 1 <= note_num <= 84:
                            # Note number to frequency (N1 = C0)
                            freq = 16.35 * (2 ** ((note_num - 1) / 12.0))
                            duration = (60.0 / tempo) * (4.0 / default_length)
                            self._play_note(freq, duration * articulation)

                # Music articulation
                elif ch == 'M':
                    if i < len(mml_upper):
                        art_ch = mml_upper[i]
                        i += 1
                        if art_ch == 'N':
                            articulation = 7 / 8  # Normal
                        elif art_ch == 'L':
                            articulation = 1.0  # Legato
                        elif art_ch == 'S':
                            articulation = 3 / 4  # Staccato

                # Skip spaces and unknown characters
                elif ch in ' \t\n':
                    pass

        except Exception as e:
            print(f"Error in PLAY at PC {pc}: {e}")

    def _play_note(self, frequency: float, duration: float) -> None:
        """Helper to play a single note."""
        try:
            if frequency <= 0 or duration <= 0:
                return

            import array
            sample_rate = 22050
            n_samples = int(sample_rate * duration)
            if n_samples <= 0:
                return

            # Generate sine wave
            samples = array.array('h', [0] * n_samples)
            for i in range(n_samples):
                t = i / sample_rate
                # Apply envelope (attack/decay) to avoid clicks
                envelope = 1.0
                attack_samples = int(0.01 * sample_rate)  # 10ms attack
                decay_samples = int(0.05 * sample_rate)   # 50ms decay
                if i < attack_samples:
                    envelope = i / attack_samples
                elif i > n_samples - decay_samples:
                    envelope = (n_samples - i) / decay_samples
                samples[i] = int(32767 * 0.5 * envelope * math.sin(2 * math.pi * frequency * t))

            sound = pygame.mixer.Sound(buffer=samples)
            sound.play()
            time.sleep(duration)  # Wait for note to finish
        except Exception:
            pass

    def _do_draw(self, draw_expr: str, pc: int) -> None:
        """Execute DRAW command - turtle graphics.
        Commands:
        U[n]: Move up n pixels
        D[n]: Move down n pixels
        L[n]: Move left n pixels
        R[n]: Move right n pixels
        E[n]: Move diagonally up-right
        F[n]: Move diagonally down-right
        G[n]: Move diagonally down-left
        H[n]: Move diagonally up-left
        M[+/-]x,y: Move to absolute (or relative with +/-) position
        A[n]: Set angle (0-3, n*90 degrees)
        TA[n]: Turn angle in degrees
        C[n]: Set color
        B: Move without drawing (prefix)
        N: Return to original position after command (prefix)
        P paint,border: Paint fill
        S[n]: Scale factor (1-255, default 4, n/4 is the multiplier)
        """
        try:
            # Evaluate the DRAW string expression
            draw_string = str(self.eval_expr(draw_expr))
            if not self.running:
                return

            i = 0
            draw_upper = draw_string.upper()
            scale = 4  # Default scale (1 pixel per unit)
            color = self.current_fg_color

            while i < len(draw_upper):
                ch = draw_upper[i]
                i += 1

                # Prefix modifiers
                blank_move = False
                return_after = False

                while ch in 'BN':
                    if ch == 'B':
                        blank_move = True
                    elif ch == 'N':
                        return_after = True
                    if i < len(draw_upper):
                        ch = draw_upper[i]
                        i += 1
                    else:
                        break

                # Parse number after command
                def parse_number():
                    nonlocal i
                    num_str = ""
                    negative = False
                    if i < len(draw_upper) and draw_upper[i] in '+-':
                        if draw_upper[i] == '-':
                            negative = True
                        i += 1
                    while i < len(draw_upper) and draw_upper[i].isdigit():
                        num_str += draw_upper[i]
                        i += 1
                    if num_str:
                        val = int(num_str)
                        return -val if negative else val
                    return 1  # Default distance

                # Direction commands
                save_x, save_y = self.draw_x, self.draw_y
                dx, dy = 0, 0

                if ch == 'U':  # Up
                    n = parse_number()
                    dy = -n * (scale / 4)
                elif ch == 'D':  # Down
                    n = parse_number()
                    dy = n * (scale / 4)
                elif ch == 'L':  # Left
                    n = parse_number()
                    dx = -n * (scale / 4)
                elif ch == 'R':  # Right
                    n = parse_number()
                    dx = n * (scale / 4)
                elif ch == 'E':  # Up-right diagonal
                    n = parse_number()
                    dx = n * (scale / 4)
                    dy = -n * (scale / 4)
                elif ch == 'F':  # Down-right diagonal
                    n = parse_number()
                    dx = n * (scale / 4)
                    dy = n * (scale / 4)
                elif ch == 'G':  # Down-left diagonal
                    n = parse_number()
                    dx = -n * (scale / 4)
                    dy = n * (scale / 4)
                elif ch == 'H':  # Up-left diagonal
                    n = parse_number()
                    dx = -n * (scale / 4)
                    dy = -n * (scale / 4)
                elif ch == 'M':  # Move to position
                    # Check for relative movement
                    relative = False
                    if i < len(draw_upper) and draw_upper[i] in '+-':
                        relative = True
                    x = parse_number()
                    # Skip comma
                    if i < len(draw_upper) and draw_upper[i] == ',':
                        i += 1
                    y = parse_number()
                    if relative:
                        dx = x * (scale / 4)
                        dy = y * (scale / 4)
                    else:
                        # Absolute movement
                        new_x, new_y = x, y
                        if not blank_move and self.surface:
                            pygame.draw.line(self.surface, self.basic_color(color),
                                           (int(self.draw_x), int(self.draw_y)),
                                           (int(new_x), int(new_y)))
                            self.mark_dirty()
                        if not return_after:
                            self.draw_x, self.draw_y = new_x, new_y
                        continue
                elif ch == 'A':  # Set angle (0-3)
                    n = parse_number()
                    self.draw_angle = (n % 4) * 90
                    continue
                elif ch == 'T':  # Turn angle
                    if i < len(draw_upper) and draw_upper[i] == 'A':
                        i += 1
                        n = parse_number()
                        self.draw_angle = (self.draw_angle + n) % 360
                    continue
                elif ch == 'C':  # Set color
                    n = parse_number()
                    color = n % 16
                    continue
                elif ch == 'S':  # Set scale
                    n = parse_number()
                    scale = max(1, min(255, n))
                    continue
                elif ch == 'P':  # Paint (fill)
                    fill_color = parse_number()
                    if i < len(draw_upper) and draw_upper[i] == ',':
                        i += 1
                    border_color = parse_number()
                    # Perform flood fill at current position
                    if self.surface:
                        self._scanline_fill(int(self.draw_x), int(self.draw_y),
                                          self.basic_color(fill_color),
                                          self.basic_color(border_color),
                                          self.surface.get_at((int(self.draw_x), int(self.draw_y)))[:3])
                        self.mark_dirty()
                    continue
                elif ch in ' \t\n':
                    continue
                else:
                    continue  # Skip unknown commands

                # Apply rotation based on draw_angle
                if self.draw_angle != 0:
                    rad = math.radians(self.draw_angle)
                    new_dx = dx * math.cos(rad) - dy * math.sin(rad)
                    new_dy = dx * math.sin(rad) + dy * math.cos(rad)
                    dx, dy = new_dx, new_dy

                # Calculate new position
                new_x = self.draw_x + dx
                new_y = self.draw_y + dy

                # Draw line if not blank move
                if not blank_move and self.surface:
                    pygame.draw.line(self.surface, self.basic_color(color),
                                   (int(self.draw_x), int(self.draw_y)),
                                   (int(new_x), int(new_y)))
                    self.mark_dirty()

                # Update position (or return to original)
                if return_after:
                    self.draw_x, self.draw_y = save_x, save_y
                else:
                    self.draw_x, self.draw_y = new_x, new_y

        except Exception as e:
            print(f"Error in DRAW at PC {pc}: {e}")

    def _do_get_graphics(self, match, pc: int) -> bool:
        """Handle GET (x1, y1)-(x2, y2), array - capture screen region to array."""
        try:
            x1 = int(self.eval_expr(match.group(1).strip()))
            y1 = int(self.eval_expr(match.group(2).strip()))
            x2 = int(self.eval_expr(match.group(3).strip()))
            y2 = int(self.eval_expr(match.group(4).strip()))
            array_name = match.group(5).upper()

            if not self.running:
                return False

            # Ensure coordinates are in order
            if x1 > x2:
                x1, x2 = x2, x1
            if y1 > y2:
                y1, y2 = y2, y1

            # Clip to screen bounds
            x1 = max(0, min(x1, self.screen_width - 1))
            x2 = max(0, min(x2, self.screen_width - 1))
            y1 = max(0, min(y1, self.screen_height - 1))
            y2 = max(0, min(y2, self.screen_height - 1))

            width = x2 - x1 + 1
            height = y2 - y1 + 1

            # Capture the screen region as a pygame surface
            if self.surface:
                captured = self.surface.subsurface((x1, y1, width, height)).copy()
                # Store metadata and surface in a special format
                self.variables[array_name] = {
                    '_sprite': True,
                    'width': width,
                    'height': height,
                    'surface': captured
                }

            return False
        except Exception as e:
            print(f"Error in GET at PC {pc}: {e}")
            return False

    def _do_put_graphics(self, match, pc: int) -> bool:
        """Handle PUT (x, y), array[, mode] - display sprite from array."""
        try:
            x = int(self.eval_expr(match.group(1).strip()))
            y = int(self.eval_expr(match.group(2).strip()))
            array_name = match.group(3).upper()
            mode = (match.group(4) or "XOR").upper()

            if not self.running:
                return False

            # Get the sprite data
            sprite_data = self.variables.get(array_name)
            if not sprite_data or not isinstance(sprite_data, dict) or not sprite_data.get('_sprite'):
                print(f"Error: Array '{array_name}' does not contain sprite data at PC {pc}")
                return False

            sprite_surface = sprite_data['surface']

            if self.surface and sprite_surface:
                if mode == "PSET":
                    self.surface.blit(sprite_surface, (x, y))
                elif mode == "PRESET":
                    # Invert colors (simplified)
                    inverted = sprite_surface.copy()
                    inverted.fill((255, 255, 255))
                    inverted.blit(sprite_surface, (0, 0), special_flags=pygame.BLEND_RGB_SUB)
                    self.surface.blit(inverted, (x, y))
                elif mode == "AND":
                    self.surface.blit(sprite_surface, (x, y), special_flags=pygame.BLEND_RGB_MULT)
                elif mode == "OR":
                    self.surface.blit(sprite_surface, (x, y), special_flags=pygame.BLEND_RGB_ADD)
                elif mode == "XOR":
                    # XOR mode - need to implement manually
                    temp = self.surface.subsurface((x, y, sprite_data['width'], sprite_data['height'])).copy()
                    arr1 = pygame.surfarray.pixels3d(temp)
                    arr2 = pygame.surfarray.pixels3d(sprite_surface)
                    arr1 ^= arr2
                    del arr1, arr2
                    self.surface.blit(temp, (x, y))
                self.mark_dirty()

            return False
        except Exception as e:
            print(f"Error in PUT at PC {pc}: {e}")
            return False

    def _parse_procedure_params(self, params_str: str) -> List[str]:
        """Parse procedure parameter string, handling AS TYPE syntax.

        Handles parameters like:
        - X
        - X AS INTEGER
        - arr() AS ANY
        - arr() AS typename

        Returns list of parameter names (without type info).
        """
        if not params_str.strip():
            return []

        params = []
        # Split by comma, but be careful with nested parentheses
        current_param = ""
        paren_depth = 0
        for char in params_str:
            if char == '(':
                paren_depth += 1
                current_param += char
            elif char == ')':
                paren_depth -= 1
                current_param += char
            elif char == ',' and paren_depth == 0:
                if current_param.strip():
                    params.append(current_param.strip())
                current_param = ""
            else:
                current_param += char
        if current_param.strip():
            params.append(current_param.strip())

        # Extract just the parameter name from each param (strip AS TYPE)
        result = []
        for param in params:
            # Handle "name AS TYPE" or "name() AS TYPE"
            param_upper = param.upper()
            as_pos = param_upper.find(' AS ')
            if as_pos != -1:
                param_name = param[:as_pos].strip()
            else:
                param_name = param.strip()
            # Keep the name with array indicator () if present
            result.append(param_name.upper())

        return result

    def _preparse_procedures(self) -> None:
        """Pre-parse SUB and FUNCTION definitions during reset.

        This allows calling procedures before their definition in the source code.
        """
        # Patterns for SUB and FUNCTION definitions (supports array params like arr() AS TYPE)
        sub_re = re.compile(r"SUB\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:\(((?:[^()]*|\([^()]*\))*)\))?\s*(STATIC)?", re.IGNORECASE)
        func_re = re.compile(r"FUNCTION\s+([a-zA-Z_][a-zA-Z0-9_\$%#!&]*)\s*(?:\(((?:[^()]*|\([^()]*\))*)\))?\s*(STATIC)?", re.IGNORECASE)
        end_sub_re = re.compile(r"END\s+SUB", re.IGNORECASE)
        end_func_re = re.compile(r"END\s+FUNCTION", re.IGNORECASE)

        pc = 0
        while pc < len(self.program_lines):
            _, _, line_content = self.program_lines[pc]

            # Check for SUB definition
            sub_match = sub_re.fullmatch(line_content.strip())
            if sub_match:
                sub_name = sub_match.group(1).upper()
                params_str = sub_match.group(2) or ""
                params = self._parse_procedure_params(params_str)
                is_static = bool(sub_match.group(3))

                # Find END SUB
                end_pc = pc + 1
                depth = 1
                while end_pc < len(self.program_lines) and depth > 0:
                    _, _, end_line = self.program_lines[end_pc]
                    end_line = end_line.strip()
                    if sub_re.fullmatch(end_line):
                        depth += 1
                    elif end_sub_re.fullmatch(end_line):
                        depth -= 1
                    end_pc += 1
                end_pc -= 1  # Back up to the END SUB line

                if depth == 0:
                    self.procedures[sub_name] = {
                        'type': 'SUB',
                        'params': params,
                        'start_pc': pc + 1,  # First line inside SUB
                        'end_pc': end_pc,    # END SUB line
                        'is_static': is_static
                    }
                pc = end_pc + 1
                continue

            # Check for FUNCTION definition
            func_match = func_re.fullmatch(line_content.strip())
            if func_match:
                func_name = func_match.group(1).upper()
                params_str = func_match.group(2) or ""
                params = self._parse_procedure_params(params_str)
                is_static = bool(func_match.group(3))

                # Find END FUNCTION
                end_pc = pc + 1
                depth = 1
                while end_pc < len(self.program_lines) and depth > 0:
                    _, _, end_line = self.program_lines[end_pc]
                    end_line = end_line.strip()
                    if func_re.fullmatch(end_line):
                        depth += 1
                    elif end_func_re.fullmatch(end_line):
                        depth -= 1
                    end_pc += 1
                end_pc -= 1  # Back up to the END FUNCTION line

                if depth == 0:
                    self.procedures[func_name] = {
                        'type': 'FUNCTION',
                        'params': params,
                        'start_pc': pc + 1,  # First line inside FUNCTION
                        'end_pc': end_pc,    # END FUNCTION line
                        'is_static': is_static
                    }
                pc = end_pc + 1
                continue

            pc += 1

    def _handle_sub_definition(self, match, pc: int) -> bool:
        """Handle SUB name[(params)] [STATIC] - skip to END SUB during normal execution."""
        sub_name = match.group(1).upper()
        params_str = match.group(2) or ""

        # Parse parameters using helper that handles AS TYPE syntax
        params = self._parse_procedure_params(params_str)

        # Find END SUB to determine body range
        end_pc = self._find_end_of_block(pc, "SUB", "END SUB")
        if end_pc == -1:
            print(f"Error: SUB without END SUB at PC {pc}")
            self.running = False
            return False

        # Store procedure definition (may already exist from pre-parsing)
        self.procedures[sub_name] = {
            'type': 'SUB',
            'params': params,
            'start_pc': pc + 1,
            'end_pc': end_pc,
            'is_static': 'STATIC' in (match.group(0) or '').upper()
        }

        # Skip past the SUB body during normal execution
        self.pc = end_pc + 1
        return True

    def _handle_end_sub(self, pc: int) -> bool:
        """Handle END SUB - return from subroutine."""
        if self.procedure_stack:
            return self._return_from_procedure(pc)
        return False

    def _handle_function_definition(self, match, pc: int) -> bool:
        """Handle FUNCTION name[(params)] [STATIC] - skip to END FUNCTION during normal execution."""
        func_name = match.group(1).upper()
        params_str = match.group(2) or ""

        # Parse parameters using helper that handles AS TYPE syntax
        params = self._parse_procedure_params(params_str)

        # Find END FUNCTION to determine body range
        end_pc = self._find_end_of_block(pc, "FUNCTION", "END FUNCTION")
        if end_pc == -1:
            print(f"Error: FUNCTION without END FUNCTION at PC {pc}")
            self.running = False
            return False

        # Store procedure definition (may already exist from pre-parsing)
        self.procedures[func_name] = {
            'type': 'FUNCTION',
            'params': params,
            'start_pc': pc + 1,
            'end_pc': end_pc,
            'is_static': 'STATIC' in (match.group(0) or '').upper()
        }

        # Skip past the FUNCTION body during normal execution
        self.pc = end_pc + 1
        return True

    def _handle_end_function(self, pc: int) -> bool:
        """Handle END FUNCTION - return from function."""
        if self.procedure_stack:
            return self._return_from_procedure(pc)
        return False

    def _handle_exit_sub(self, pc: int) -> bool:
        """Handle EXIT SUB - early return from subroutine."""
        if self.procedure_stack:
            return self._return_from_procedure(pc)
        print(f"Error: EXIT SUB outside of SUB at PC {pc}")
        return False

    def _handle_exit_function(self, pc: int) -> bool:
        """Handle EXIT FUNCTION - early return from function."""
        if self.procedure_stack:
            return self._return_from_procedure(pc)
        print(f"Error: EXIT FUNCTION outside of FUNCTION at PC {pc}")
        return False

    def _handle_call(self, match, pc: int) -> bool:
        """Handle CALL subname[(args)] - call a subroutine."""
        sub_name = match.group(1).upper()
        args_str = match.group(2) or ""
        return self._handle_call_sub(sub_name, args_str, pc)

    def _handle_call_sub(self, sub_name: str, args_str: str, pc: int) -> bool:
        """Handle calling a SUB (with or without CALL keyword)."""
        # Check if procedure exists
        if sub_name not in self.procedures:
            print(f"Error: Undefined SUB '{sub_name}' at PC {pc}")
            self.running = False
            return False

        proc = self.procedures[sub_name]
        if proc['type'] != 'SUB':
            print(f"Error: '{sub_name}' is a FUNCTION, use it in an expression at PC {pc}")
            self.running = False
            return False

        return self._call_procedure(sub_name, args_str, pc)

    def _call_procedure(self, name: str, args_str: str, pc: int) -> bool:
        """Call a SUB or FUNCTION."""
        proc = self.procedures[name]

        # Parse arguments - handle array references specially
        args = []
        array_refs = {}  # Maps param index to array name for pass-by-reference
        if args_str.strip():
            split_args = _split_args(args_str)
            for i, arg in enumerate(split_args):
                arg = arg.strip()
                # Check if this is an array reference like "cities()" or "arr%()"
                array_ref_match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*[\$%!#&]?)\s*\(\s*\)$', arg)
                if array_ref_match:
                    # This is an array being passed by reference
                    array_name = array_ref_match.group(1).upper()
                    # Normalize array name (remove type suffix for lookup)
                    array_name_base = re.sub(r'[\$%!#&]$', '', array_name)
                    array_refs[i] = array_name_base
                    args.append(None)  # Placeholder, will handle specially below
                else:
                    args.append(self.eval_expr(arg))
                    if not self.running:
                        return False

        # Save current state
        saved_vars = {}
        saved_arrays = {}  # For array references
        for i, param in enumerate(proc['params']):
            # Check if parameter is an array parameter (ends with "()")
            is_array_param = param.endswith('()')
            if is_array_param:
                param_clean = re.sub(r'\(\)$', '', param)
                param_clean = re.sub(r'[\$%!#&]$', '', param_clean).upper()
            else:
                # Strip type suffix from parameter
                param_clean = re.sub(r'[\$%!#&]$', '', param).upper()

            if is_array_param and i in array_refs:
                # Array parameter: create alias to the passed array (stored in variables as list)
                source_array = array_refs[i]
                # Save current state of param array if it exists
                if param_clean in self.variables:
                    saved_arrays[param_clean] = self.variables[param_clean]
                # Create reference to source array (Python lists are passed by reference)
                if source_array in self.variables:
                    self.variables[param_clean] = self.variables[source_array]
                else:
                    # Array doesn't exist, create empty one
                    self.variables[param_clean] = [0] * 11  # Default 0-10 dimensions
            else:
                if param_clean in self.variables:
                    saved_vars[param_clean] = self.variables[param_clean]
                # Set parameter to argument value
                if i < len(args):
                    self.variables[param_clean] = args[i]
                else:
                    # Default value based on type
                    if param.endswith('$'):
                        self.variables[param_clean] = ""
                    else:
                        self.variables[param_clean] = 0

        # Push return info onto stack
        self.procedure_stack.append({
            'name': name,
            'return_pc': self.pc,
            'saved_vars': saved_vars,
            'saved_arrays': saved_arrays,
            'params': proc['params'],
            'array_refs': array_refs
        })

        # Jump to procedure body
        self.pc = proc['start_pc']
        return True

    def _return_from_procedure(self, pc: int) -> bool:
        """Return from a SUB or FUNCTION."""
        if not self.procedure_stack:
            return False

        call_info = self.procedure_stack.pop()

        # Restore saved variables
        for i, param in enumerate(call_info['params']):
            is_array_param = param.endswith('()')
            if is_array_param:
                param_clean = re.sub(r'\(\)$', '', param)
                param_clean = re.sub(r'[\$%!#&]$', '', param_clean).upper()
                # Restore saved array state if any
                saved_arrays = call_info.get('saved_arrays', {})
                if param_clean in saved_arrays:
                    self.variables[param_clean] = saved_arrays[param_clean]
                elif param_clean in self.variables and i not in call_info.get('array_refs', {}):
                    # Only delete if it wasn't an alias
                    del self.variables[param_clean]
            else:
                param_clean = re.sub(r'[\$%!#&]$', '', param).upper()
                if param_clean in call_info['saved_vars']:
                    self.variables[param_clean] = call_info['saved_vars'][param_clean]
                elif param_clean in self.variables:
                    del self.variables[param_clean]

        # Return to caller
        self.pc = call_info['return_pc']
        return True

    def _call_function_procedure(self, name: str, args: tuple) -> Any:
        """Execute a FUNCTION procedure synchronously and return its value.

        This is used when FUNCTION is called from within an expression.
        """
        if name not in self.procedures:
            raise BasicRuntimeError(f"Undefined FUNCTION '{name}'")

        proc = self.procedures[name]
        if proc['type'] != 'FUNCTION':
            raise BasicRuntimeError(f"'{name}' is a SUB, not a FUNCTION")

        # Save current execution state
        saved_pc = self.pc
        saved_procedure_stack = list(self.procedure_stack)

        # Save and set parameters
        saved_vars = {}
        for i, param in enumerate(proc['params']):
            param_clean = re.sub(r'[\$%!#&]$', '', param).upper()
            if param_clean in self.variables:
                saved_vars[param_clean] = self.variables[param_clean]
            if i < len(args):
                self.variables[param_clean] = args[i]
            else:
                self.variables[param_clean] = "" if param.endswith('$') else 0

        # Initialize function return variable
        func_name_clean = re.sub(r'[\$%!#&]$', '', name).upper()
        if func_name_clean in self.variables:
            saved_vars[func_name_clean] = self.variables[func_name_clean]
        self.variables[func_name_clean] = "" if name.endswith('$') else 0

        # Execute function body
        self.pc = proc['start_pc']
        max_steps = 10000  # Safety limit
        steps = 0
        while self.running and self.pc < len(self.program_lines) and steps < max_steps:
            _, _, line = self.program_lines[self.pc]
            line_upper = line.strip().upper()

            # Check for END FUNCTION
            if line_upper == "END FUNCTION" or line_upper.startswith("END FUNCTION"):
                break

            # Check for EXIT FUNCTION
            if line_upper == "EXIT FUNCTION" or line_upper.startswith("EXIT FUNCTION"):
                break

            self.pc += 1
            try:
                self.execute_logical_line(line, self.pc - 1)
            except BasicRuntimeError:
                # Re-raise for error handling
                raise
            steps += 1

        # Get return value (function name holds the result)
        result = self.variables.get(func_name_clean, 0)

        # Restore execution state
        self.pc = saved_pc
        self.procedure_stack = saved_procedure_stack

        # Restore variables
        for param in proc['params']:
            param_clean = re.sub(r'[\$%!#&]$', '', param).upper()
            if param_clean in saved_vars:
                self.variables[param_clean] = saved_vars[param_clean]
            elif param_clean in self.variables:
                del self.variables[param_clean]

        if func_name_clean in saved_vars:
            self.variables[func_name_clean] = saved_vars[func_name_clean]
        elif func_name_clean in self.variables:
            del self.variables[func_name_clean]

        return result

    def _find_end_of_block(self, start_pc: int, start_kw: str, end_kw: str) -> int:
        """Find the PC of the END statement for a block."""
        depth = 1
        for i in range(start_pc + 1, len(self.program_lines)):
            line = self.program_lines[i][1].strip().upper()
            if line.startswith(start_kw + " ") or line == start_kw:
                depth += 1
            elif line.startswith(end_kw) or line == end_kw:
                depth -= 1
                if depth == 0:
                    return i
        return -1

    def _handle_open(self, match, pc: int) -> bool:
        """Handle OPEN filename FOR mode AS #n."""
        try:
            filename_expr = match.group(1).strip()
            # Evaluate filename if it's a variable, otherwise use as literal
            if filename_expr.startswith('"') and filename_expr.endswith('"'):
                filename = filename_expr[1:-1]
            else:
                filename = str(self.eval_expr(filename_expr))
                if not self.running: return False
            mode = match.group(2).upper()
            # File number can be an expression (e.g., f% variable)
            file_num_expr = match.group(3).strip()
            file_num = int(self.eval_expr(file_num_expr))
            if not self.running: return False

            # Map QBasic modes to Python modes
            mode_map = {
                'INPUT': 'r',
                'OUTPUT': 'w',
                'APPEND': 'a',
                'BINARY': 'rb',
                'RANDOM': 'r+b'
            }

            py_mode = mode_map.get(mode, 'r')

            # Handle output modes - create file if doesn't exist
            if mode in ('OUTPUT', 'APPEND'):
                fh = open(filename, py_mode, encoding='utf-8' if 'b' not in py_mode else None)
            elif mode == 'INPUT':
                fh = open(filename, py_mode, encoding='utf-8')
            else:
                # Binary/Random - create if doesn't exist
                try:
                    fh = open(filename, py_mode)
                except FileNotFoundError:
                    fh = open(filename, 'w+b')

            fh.file_path = filename  # Store for LOF
            self.file_handles[file_num] = fh

            # Update next_file_number
            if file_num >= self.next_file_number:
                self.next_file_number = file_num + 1

            return False
        except Exception as e:
            print(f"Error in OPEN at PC {pc}: {e}")
            self.running = False
            return False

    def _handle_close(self, match, pc: int) -> bool:
        """Handle CLOSE [#n]."""
        try:
            if match.group(1):
                file_num = int(self.eval_expr(match.group(1).strip()))
                if not self.running: return False
                if file_num in self.file_handles:
                    self.file_handles[file_num].close()
                    del self.file_handles[file_num]
            else:
                # Close all files
                for fh in self.file_handles.values():
                    fh.close()
                self.file_handles.clear()
                self.next_file_number = 1
            return False
        except Exception as e:
            print(f"Error in CLOSE at PC {pc}: {e}")
            return False

    def _handle_input_file(self, match, pc: int) -> bool:
        """Handle INPUT #n, vars."""
        try:
            file_num = int(self.eval_expr(match.group(1).strip()))
            if not self.running: return False
            vars_str = match.group(2)

            if file_num not in self.file_handles:
                print(f"Error: File #{file_num} not open at PC {pc}")
                self.running = False
                return False

            fh = self.file_handles[file_num]
            var_names = [v.strip() for v in vars_str.split(',')]

            for var_name in var_names:
                # Read next value from file
                value = ""
                in_quotes = False
                while True:
                    ch = fh.read(1)
                    if not ch:
                        break
                    if ch == '"':
                        in_quotes = not in_quotes
                    elif ch in ',\n' and not in_quotes:
                        break
                    else:
                        value += ch

                # Convert and assign
                var_upper = var_name.upper()
                if var_upper.endswith('$'):
                    self.variables[var_upper] = value.strip().strip('"')
                else:
                    try:
                        if '.' in value:
                            self.variables[var_upper] = float(value)
                        else:
                            self.variables[var_upper] = int(value)
                    except ValueError:
                        self.variables[var_upper] = 0

            return False
        except Exception as e:
            print(f"Error in INPUT # at PC {pc}: {e}")
            return False

    def _handle_line_input_file(self, match, pc: int) -> bool:
        """Handle LINE INPUT #n, var$."""
        try:
            file_num = int(self.eval_expr(match.group(1).strip()))
            if not self.running: return False
            var_name = match.group(2).strip().upper()

            if file_num not in self.file_handles:
                print(f"Error: File #{file_num} not open at PC {pc}")
                self.running = False
                return False

            fh = self.file_handles[file_num]
            line = fh.readline()
            if line.endswith('\n'):
                line = line[:-1]
            self.variables[var_name] = line

            return False
        except Exception as e:
            print(f"Error in LINE INPUT # at PC {pc}: {e}")
            return False

    def _handle_print_file(self, match, pc: int) -> bool:
        """Handle PRINT #n, expressions."""
        try:
            file_num = int(self.eval_expr(match.group(1).strip()))
            if not self.running: return False
            expr_str = match.group(2) or ""

            if file_num not in self.file_handles:
                print(f"Error: File #{file_num} not open at PC {pc}")
                self.running = False
                return False

            fh = self.file_handles[file_num]

            if expr_str.strip():
                # Evaluate and write expressions
                parts = _split_args(expr_str)
                output = ""
                for part in parts:
                    part = part.strip()
                    if part == ';':
                        continue
                    elif part == ',':
                        output += "\t"
                    else:
                        val = self.eval_expr(part)
                        if not self.running:
                            return False
                        output += str(val)
                fh.write(output + "\n")
            else:
                fh.write("\n")

            return False
        except Exception as e:
            print(f"Error in PRINT # at PC {pc}: {e}")
            return False

    def _handle_write_file(self, match, pc: int) -> bool:
        """Handle WRITE #n, expressions (comma-separated with quotes around strings)."""
        try:
            file_num = int(self.eval_expr(match.group(1).strip()))
            if not self.running: return False
            expr_str = match.group(2) or ""

            if file_num not in self.file_handles:
                print(f"Error: File #{file_num} not open at PC {pc}")
                self.running = False
                return False

            fh = self.file_handles[file_num]

            if expr_str.strip():
                parts = _split_args(expr_str)
                values = []
                for part in parts:
                    part = part.strip()
                    if part in (';', ','):
                        continue
                    val = self.eval_expr(part)
                    if not self.running:
                        return False
                    if isinstance(val, str):
                        values.append(f'"{val}"')
                    else:
                        values.append(str(val))
                fh.write(','.join(values) + "\n")
            else:
                fh.write("\n")

            return False
        except Exception as e:
            print(f"Error in WRITE # at PC {pc}: {e}")
            return False

    def _handle_get_file(self, match, pc: int) -> bool:
        """Handle GET #filenum[, recordnum], variable - read binary data from file."""
        import struct
        try:
            file_num = int(match.group(1))
            record_num = match.group(2)
            var_name = match.group(3).strip().upper()

            if file_num not in self.file_handles:
                print(f"Error: File #{file_num} not open at PC {pc}")
                self.running = False
                return False

            fh = self.file_handles[file_num]

            # If record number is specified, seek to that position
            # (record number is 1-based in QBasic)
            if record_num:
                record_num = int(record_num)
                # For simplicity, use byte position (real QBasic uses record length)
                fh.seek(record_num - 1)

            # Read data based on variable type
            if var_name.endswith('$') or var_name.endswith('_STR'):
                # String variable - read until null or newline
                data = b''
                while True:
                    byte = fh.read(1)
                    if not byte or byte == b'\0' or byte == b'\n':
                        break
                    data += byte
                self.variables[var_name] = data.decode('latin-1')
            elif var_name.endswith('_INT') or var_name.endswith('%'):
                # Integer - read 2 bytes
                data = fh.read(2)
                if len(data) == 2:
                    self.variables[var_name] = struct.unpack('<h', data)[0]
                else:
                    self.variables[var_name] = 0
            elif var_name.endswith('_LNG') or var_name.endswith('&'):
                # Long - read 4 bytes
                data = fh.read(4)
                if len(data) == 4:
                    self.variables[var_name] = struct.unpack('<i', data)[0]
                else:
                    self.variables[var_name] = 0
            elif var_name.endswith('_SNG') or var_name.endswith('!'):
                # Single - read 4 bytes
                data = fh.read(4)
                if len(data) == 4:
                    self.variables[var_name] = struct.unpack('<f', data)[0]
                else:
                    self.variables[var_name] = 0.0
            elif var_name.endswith('_DBL') or var_name.endswith('#'):
                # Double - read 8 bytes
                data = fh.read(8)
                if len(data) == 8:
                    self.variables[var_name] = struct.unpack('<d', data)[0]
                else:
                    self.variables[var_name] = 0.0
            else:
                # Default: try to read as integer
                data = fh.read(2)
                if len(data) >= 2:
                    self.variables[var_name] = struct.unpack('<h', data)[0]
                else:
                    self.variables[var_name] = 0

            return False
        except Exception as e:
            print(f"Error in GET # at PC {pc}: {e}")
            self.running = False
            return False

    def _handle_put_file(self, match, pc: int) -> bool:
        """Handle PUT #filenum[, recordnum], variable - write binary data to file."""
        import struct
        try:
            file_num = int(match.group(1))
            record_num = match.group(2)
            var_name = match.group(3).strip().upper()

            if file_num not in self.file_handles:
                print(f"Error: File #{file_num} not open at PC {pc}")
                self.running = False
                return False

            fh = self.file_handles[file_num]

            # If record number is specified, seek to that position
            if record_num:
                record_num = int(record_num)
                fh.seek(record_num - 1)

            # Get variable value
            value = self.variables.get(var_name, 0)

            # Write data based on variable type
            if var_name.endswith('$') or var_name.endswith('_STR'):
                # String variable
                data = str(value).encode('latin-1')
                fh.write(data)
            elif var_name.endswith('_INT') or var_name.endswith('%'):
                # Integer - write 2 bytes
                fh.write(struct.pack('<h', int(value)))
            elif var_name.endswith('_LNG') or var_name.endswith('&'):
                # Long - write 4 bytes
                fh.write(struct.pack('<i', int(value)))
            elif var_name.endswith('_SNG') or var_name.endswith('!'):
                # Single - write 4 bytes
                fh.write(struct.pack('<f', float(value)))
            elif var_name.endswith('_DBL') or var_name.endswith('#'):
                # Double - write 8 bytes
                fh.write(struct.pack('<d', float(value)))
            else:
                # Default: write as integer
                fh.write(struct.pack('<h', int(value)))

            return False
        except Exception as e:
            print(f"Error in PUT # at PC {pc}: {e}")
            self.running = False
            return False

    def _handle_kill(self, filename_expr: str, pc: int) -> bool:
        """Handle KILL filename - delete a file."""
        import os
        try:
            # Evaluate filename
            if filename_expr.startswith('"') and filename_expr.endswith('"'):
                filename = filename_expr[1:-1]
            else:
                filename = str(self.eval_expr(filename_expr))
                if not self.running: return False

            os.remove(filename)
            return False
        except FileNotFoundError:
            print(f"Error in KILL at PC {pc}: File not found '{filename}'")
            self.running = False
            return False
        except Exception as e:
            print(f"Error in KILL at PC {pc}: {e}")
            self.running = False
            return False

    def _handle_name(self, old_name_expr: str, new_name_expr: str, pc: int) -> bool:
        """Handle NAME oldname AS newname - rename a file."""
        import os
        try:
            # Evaluate old filename
            if old_name_expr.startswith('"') and old_name_expr.endswith('"'):
                old_name = old_name_expr[1:-1]
            else:
                old_name = str(self.eval_expr(old_name_expr))
                if not self.running: return False

            # Evaluate new filename
            if new_name_expr.startswith('"') and new_name_expr.endswith('"'):
                new_name = new_name_expr[1:-1]
            else:
                new_name = str(self.eval_expr(new_name_expr))
                if not self.running: return False

            os.rename(old_name, new_name)
            return False
        except FileNotFoundError:
            print(f"Error in NAME at PC {pc}: File not found '{old_name}'")
            self.running = False
            return False
        except Exception as e:
            print(f"Error in NAME at PC {pc}: {e}")
            self.running = False
            return False

    def _handle_mkdir(self, dir_expr: str, pc: int) -> bool:
        """Handle MKDIR dirname - create a directory."""
        import os
        try:
            # Evaluate directory name
            if dir_expr.startswith('"') and dir_expr.endswith('"'):
                dirname = dir_expr[1:-1]
            else:
                dirname = str(self.eval_expr(dir_expr))
                if not self.running: return False

            os.mkdir(dirname)
            return False
        except FileExistsError:
            print(f"Error in MKDIR at PC {pc}: Directory already exists '{dirname}'")
            self.running = False
            return False
        except Exception as e:
            print(f"Error in MKDIR at PC {pc}: {e}")
            self.running = False
            return False

    def _handle_rmdir(self, dir_expr: str, pc: int) -> bool:
        """Handle RMDIR dirname - remove a directory."""
        import os
        try:
            # Evaluate directory name
            if dir_expr.startswith('"') and dir_expr.endswith('"'):
                dirname = dir_expr[1:-1]
            else:
                dirname = str(self.eval_expr(dir_expr))
                if not self.running: return False

            os.rmdir(dirname)
            return False
        except FileNotFoundError:
            print(f"Error in RMDIR at PC {pc}: Directory not found '{dirname}'")
            self.running = False
            return False
        except OSError as e:
            print(f"Error in RMDIR at PC {pc}: {e}")
            self.running = False
            return False
        except Exception as e:
            print(f"Error in RMDIR at PC {pc}: {e}")
            self.running = False
            return False

    def _handle_chdir(self, dir_expr: str, pc: int) -> bool:
        """Handle CHDIR dirname - change current directory."""
        import os
        try:
            # Evaluate directory name
            if dir_expr.startswith('"') and dir_expr.endswith('"'):
                dirname = dir_expr[1:-1]
            else:
                dirname = str(self.eval_expr(dir_expr))
                if not self.running: return False

            os.chdir(dirname)
            return False
        except FileNotFoundError:
            print(f"Error in CHDIR at PC {pc}: Directory not found '{dirname}'")
            self.running = False
            return False
        except Exception as e:
            print(f"Error in CHDIR at PC {pc}: {e}")
            self.running = False
            return False

    def _handle_files(self, pattern_expr: Optional[str], pc: int) -> bool:
        """Handle FILES [pattern] - list directory contents."""
        import os
        import glob
        try:
            # Evaluate pattern if provided
            if pattern_expr:
                pattern_expr = pattern_expr.strip()
                if pattern_expr.startswith('"') and pattern_expr.endswith('"'):
                    pattern = pattern_expr[1:-1]
                else:
                    pattern = str(self.eval_expr(pattern_expr))
                    if not self.running: return False
            else:
                pattern = "*.*"

            # Get matching files
            files = glob.glob(pattern)
            if not files:
                files = glob.glob(os.path.join(pattern, "*")) if os.path.isdir(pattern) else []

            # Print files in QBasic-like format (always to console for simplicity)
            # In QBasic, FILES prints to the screen, but for this interpreter
            # we print to stdout for easier debugging
            for f in sorted(files):
                print(os.path.basename(f), end="  ")
            print()

            return False
        except Exception as e:
            print(f"Error in FILES at PC {pc}: {e}")
            return False

    def _handle_seek(self, file_num_str: str, position_expr: str, pc: int) -> bool:
        """Handle SEEK #n, position - set file position."""
        try:
            file_num = int(file_num_str)
            position = int(self.eval_expr(position_expr))
            if not self.running: return False

            if file_num not in self.file_handles:
                print(f"Error: File #{file_num} not open at PC {pc}")
                self.running = False
                return False

            fh = self.file_handles[file_num]
            # QBasic SEEK uses 1-based byte positions, Python uses 0-based
            fh.seek(position - 1)
            return False
        except Exception as e:
            print(f"Error in SEEK at PC {pc}: {e}")
            self.running = False
            return False

    def _handle_error(self, error_num_expr: str, pc: int) -> bool:
        """Handle ERROR n - trigger a runtime error."""
        try:
            error_num = int(self.eval_expr(error_num_expr))
            if not self.running: return False

            # Raise a runtime error that can be caught by ON ERROR GOTO
            raise BasicRuntimeError(f"Error {error_num} triggered by ERROR statement", "user")
        except BasicRuntimeError:
            raise  # Re-raise to be caught by step_line
        except Exception as e:
            print(f"Error in ERROR statement at PC {pc}: {e}")
            self.running = False
            return False

    def _handle_clear(self, pc: int) -> bool:
        """Handle CLEAR statement - clears all variables.
        CLEAR [,stack_size][,heap_size] - stack/heap sizes ignored (Python manages memory)."""
        # Clear all variables (keep constants)
        self.variables.clear()
        # Reset arrays
        self.data_pointer = 0
        # Reset FOR/GOSUB stacks
        self.for_stack.clear()
        self.gosub_stack.clear()
        self.loop_stack.clear()
        # Clear user-defined functions
        self.user_functions.clear()
        # Reset error handler
        self.error_handler_label = None
        self.error_resume_pc = -1
        self.in_error_handler = False
        return False

    def _handle_shell(self, cmd_expr: Optional[str], pc: int) -> bool:
        """Handle SHELL statement - execute shell command.
        SHELL ["command"] - executes the command or opens an interactive shell."""
        import subprocess
        import shlex
        try:
            if cmd_expr and cmd_expr.strip():
                cmd = str(self.eval_expr(cmd_expr.strip()))
                if not self.running:
                    return False
                # Execute the command
                try:
                    # Use shell=True to allow shell commands
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                    # Print output to console (simulating QBasic behavior)
                    if result.stdout:
                        print(result.stdout, end='')
                    if result.stderr:
                        print(result.stderr, end='')
                except subprocess.TimeoutExpired:
                    print(f"SHELL command timed out at PC {pc}")
                except Exception as e:
                    print(f"SHELL command failed at PC {pc}: {e}")
            # If no command, QBasic would open interactive shell - skip in this implementation
            return False
        except Exception as e:
            print(f"Error in SHELL statement at PC {pc}: {e}")
            return False

    def _handle_view(self, match: re.Match, pc: int) -> bool:
        """Handle VIEW statement - define graphics viewport.
        VIEW [(x1,y1)-(x2,y2)[,fill_color][,border_color]]
        Without coordinates, resets to full screen."""
        try:
            if match.group(1) is None:
                # VIEW without arguments - reset to full screen
                self.view_x1 = 0
                self.view_y1 = 0
                self.view_x2 = None
                self.view_y2 = None
                self.view_fill_color = None
                self.view_border_color = None
                return False

            # Parse coordinates
            coords1 = _split_args(match.group(1))
            coords2 = _split_args(match.group(2))
            if len(coords1) >= 2 and len(coords2) >= 2:
                self.view_x1 = int(self.eval_expr(coords1[0].strip()))
                self.view_y1 = int(self.eval_expr(coords1[1].strip()))
                self.view_x2 = int(self.eval_expr(coords2[0].strip()))
                self.view_y2 = int(self.eval_expr(coords2[1].strip()))
                if not self.running:
                    return False

                # Optional fill and border colors
                if match.group(3):
                    self.view_fill_color = int(match.group(3))
                    # Fill the viewport with the fill color
                    if self.surface and self.view_fill_color is not None:
                        rect = pygame.Rect(self.view_x1, self.view_y1,
                                          self.view_x2 - self.view_x1 + 1,
                                          self.view_y2 - self.view_y1 + 1)
                        self.surface.fill(self.basic_color(self.view_fill_color), rect)
                        self.mark_dirty()

                if match.group(4):
                    self.view_border_color = int(match.group(4))
                    # Draw border around viewport
                    if self.surface and self.view_border_color is not None:
                        rect = pygame.Rect(self.view_x1, self.view_y1,
                                          self.view_x2 - self.view_x1 + 1,
                                          self.view_y2 - self.view_y1 + 1)
                        pygame.draw.rect(self.surface, self.basic_color(self.view_border_color), rect, 1)
                        self.mark_dirty()

            return False
        except Exception as e:
            print(f"Error in VIEW statement at PC {pc}: {e}")
            self.running = False
            return False

    def _handle_window(self, match: re.Match, statement: str, pc: int) -> bool:
        """Handle WINDOW statement - define logical coordinate system.
        WINDOW [(x1,y1)-(x2,y2)] - y increases upward (Cartesian)
        WINDOW SCREEN [(x1,y1)-(x2,y2)] - y increases downward (screen coords)
        Without coordinates, resets to physical coordinates."""
        try:
            # Check for SCREEN modifier
            self.window_screen_mode = 'SCREEN' in statement.upper().split('(')[0] if '(' in statement else 'SCREEN' in statement.upper()

            if match.group(1) is None:
                # WINDOW without coordinates - reset to physical coordinates
                self.window_x1 = None
                self.window_y1 = None
                self.window_x2 = None
                self.window_y2 = None
                return False

            # Parse coordinates
            coords1 = _split_args(match.group(1))
            coords2 = _split_args(match.group(2))
            if len(coords1) >= 2 and len(coords2) >= 2:
                self.window_x1 = float(self.eval_expr(coords1[0].strip()))
                self.window_y1 = float(self.eval_expr(coords1[1].strip()))
                self.window_x2 = float(self.eval_expr(coords2[0].strip()))
                self.window_y2 = float(self.eval_expr(coords2[1].strip()))
                if not self.running:
                    return False

            return False
        except Exception as e:
            print(f"Error in WINDOW statement at PC {pc}: {e}")
            self.running = False
            return False

    def _logical_to_physical(self, lx: float, ly: float) -> Tuple[int, int]:
        """Convert logical (WINDOW) coordinates to physical screen coordinates."""
        if self.window_x1 is None:
            # No WINDOW set, use physical coordinates directly
            return (int(lx), int(ly))

        # Get viewport bounds
        vx1 = self.view_x1
        vy1 = self.view_y1
        vx2 = self.view_x2 if self.view_x2 is not None else self.screen_width - 1
        vy2 = self.view_y2 if self.view_y2 is not None else self.screen_height - 1

        # Map logical to physical
        vw = vx2 - vx1
        vh = vy2 - vy1
        ww = self.window_x2 - self.window_x1
        wh = self.window_y2 - self.window_y1

        if ww == 0 or wh == 0:
            return (int(lx), int(ly))

        px = vx1 + (lx - self.window_x1) * vw / ww

        if self.window_screen_mode:
            # WINDOW SCREEN - y increases downward
            py = vy1 + (ly - self.window_y1) * vh / wh
        else:
            # Regular WINDOW - y increases upward (Cartesian)
            py = vy2 - (ly - self.window_y1) * vh / wh

        return (int(px), int(py))

    def _handle_lprint(self, content: Optional[str], pc: int) -> bool:
        """Handle LPRINT statement - print to console (simulating printer).
        LPRINT [expression][;|,]..."""
        output = ""
        if content and content.strip():
            # Parse similar to PRINT but output to console
            parts = []
            current_part = ""
            in_string = False
            paren_depth = 0
            for char in content:
                if char == '"' and paren_depth == 0:
                    in_string = not in_string
                if not in_string:
                    if char == '(':
                        paren_depth += 1
                    elif char == ')':
                        paren_depth -= 1
                if not in_string and paren_depth == 0 and (char == ';' or char == ','):
                    if current_part:
                        parts.append(current_part.strip())
                    parts.append(char)
                    current_part = ""
                else:
                    current_part += char
            if current_part:
                parts.append(current_part.strip())

            for i, part in enumerate(parts):
                if part == ';':
                    pass  # No space
                elif part == ',':
                    output += '\t'  # Tab separator
                else:
                    val = self.eval_expr(part)
                    if not self.running:
                        return False
                    s_val = str(val)
                    if isinstance(val, (int, float)):
                        s_val = (" " if val >= 0 else "") + s_val + " "
                    output += s_val

        # Print to console (simulating printer output)
        ends_with_sep = content and (content.strip().endswith(';') or content.strip().endswith(','))
        if ends_with_sep:
            print(output, end='')
        else:
            print(output)
        return False

    def _handle_lprint_using(self, format_expr: str, values_expr: str, pc: int) -> bool:
        """Handle LPRINT USING statement - formatted printer output.
        Uses same format specifiers as PRINT USING but outputs to console."""
        try:
            # Evaluate format string
            format_str = str(self.eval_expr(format_expr))
            if not self.running:
                return False

            # Parse values
            value_parts = []
            current = ""
            paren_level = 0
            in_string = False
            for char in values_expr:
                if char == '"':
                    in_string = not in_string
                    current += char
                elif char == '(' and not in_string:
                    paren_level += 1
                    current += char
                elif char == ')' and not in_string:
                    paren_level -= 1
                    current += char
                elif char == ',' and paren_level == 0 and not in_string:
                    if current.strip():
                        value_parts.append(current.strip())
                    current = ""
                else:
                    current += char
            if current.strip():
                value_parts.append(current.strip())

            values = []
            for part in value_parts:
                val = self.eval_expr(part)
                if not self.running:
                    return False
                values.append(val)

            # Format and print
            output = self._format_using(format_str, values)
            print(output)
            return False
        except Exception as e:
            print(f"Error in LPRINT USING at PC {pc}: {e}")
            return False

    def _handle_field(self, match: re.Match, pc: int) -> bool:
        """Handle FIELD statement - define record fields for random access files.
        FIELD #filenum, width AS var$, width AS var$, ..."""
        try:
            file_num = int(match.group(1))
            fields_str = match.group(2)

            # Parse field definitions: width AS varname
            fields = []
            field_pattern = re.compile(r'(\d+)\s+AS\s+([a-zA-Z_][a-zA-Z0-9_]*\$?)', re.IGNORECASE)
            for field_match in field_pattern.finditer(fields_str):
                width = int(field_match.group(1))
                var_name = field_match.group(2).upper()
                fields.append((width, var_name))
                # Initialize the variable as empty string of the specified width
                self.variables[var_name] = " " * width

            self.field_defs[file_num] = fields
            # Initialize buffer
            total_width = sum(w for w, _ in fields)
            self.field_buffers[file_num] = " " * total_width

            return False
        except Exception as e:
            print(f"Error in FIELD statement at PC {pc}: {e}")
            self.running = False
            return False

    def _handle_lset(self, var_name: str, value_expr: str, pc: int) -> bool:
        """Handle LSET statement - left-justify string in field variable.
        LSET var$ = expression$"""
        try:
            var_upper = var_name.upper()
            value = str(self.eval_expr(value_expr))
            if not self.running:
                return False

            # Get current field width
            if var_upper in self.variables and isinstance(self.variables[var_upper], str):
                field_width = len(self.variables[var_upper])
                # Left-justify: truncate or pad with spaces
                if len(value) >= field_width:
                    self.variables[var_upper] = value[:field_width]
                else:
                    self.variables[var_upper] = value + " " * (field_width - len(value))
            else:
                # If not a field variable, just assign
                self.variables[var_upper] = value

            return False
        except Exception as e:
            print(f"Error in LSET statement at PC {pc}: {e}")
            self.running = False
            return False

    def _handle_rset(self, var_name: str, value_expr: str, pc: int) -> bool:
        """Handle RSET statement - right-justify string in field variable.
        RSET var$ = expression$"""
        try:
            var_upper = var_name.upper()
            value = str(self.eval_expr(value_expr))
            if not self.running:
                return False

            # Get current field width
            if var_upper in self.variables and isinstance(self.variables[var_upper], str):
                field_width = len(self.variables[var_upper])
                # Right-justify: truncate from left or pad with spaces on left
                if len(value) >= field_width:
                    self.variables[var_upper] = value[-field_width:]
                else:
                    self.variables[var_upper] = " " * (field_width - len(value)) + value
            else:
                # If not a field variable, just assign
                self.variables[var_upper] = value

            return False
        except Exception as e:
            print(f"Error in RSET statement at PC {pc}: {e}")
            self.running = False
            return False

    def _handle_environ_set(self, expr: str, pc: int) -> bool:
        """Handle ENVIRON statement - set environment variable.
        ENVIRON "NAME=VALUE" or ENVIRON name$ where name$ contains "NAME=VALUE"."""
        import os
        try:
            env_str = str(self.eval_expr(expr))
            if not self.running:
                return False

            # Parse NAME=VALUE format
            if '=' in env_str:
                name, value = env_str.split('=', 1)
                os.environ[name.strip()] = value
            else:
                print(f"Warning: ENVIRON requires NAME=VALUE format at PC {pc}")

            return False
        except Exception as e:
            print(f"Error in ENVIRON statement at PC {pc}: {e}")
            return False

    def _handle_on_timer(self, match: re.Match, pc: int) -> bool:
        """Handle ON TIMER(n) GOSUB label - set up timer event handler.
        n is the interval in seconds."""
        try:
            interval_expr = match.group(1)
            label = match.group(2).upper()

            self.timer_interval = float(self.eval_expr(interval_expr))
            if not self.running:
                return False

            self.timer_label = label
            self.timer_last_trigger = time.time()
            # Note: Timer is not enabled until TIMER ON is executed

            return False
        except Exception as e:
            print(f"Error in ON TIMER statement at PC {pc}: {e}")
            return False

    def _handle_pcopy(self, source_page: int, dest_page: int, pc: int) -> bool:
        """Handle PCOPY source, dest - copy video page contents.
        PCOPY copies the contents of one video page to another.
        Page 0 is the main display surface."""
        try:
            # Ensure we have a surface
            if self.surface is None:
                return False

            # Get or create source page
            if source_page == 0:
                source_surface = self.surface
            else:
                if source_page not in self.video_pages or self.video_pages[source_page] is None:
                    # Create empty page
                    self.video_pages[source_page] = pygame.Surface(
                        (self.screen_width, self.screen_height)).convert()
                    self.video_pages[source_page].fill(self.basic_color(self.current_bg_color))
                source_surface = self.video_pages[source_page]

            # Copy to destination page
            if dest_page == 0:
                # Copy to main surface
                self.surface.blit(source_surface, (0, 0))
                self.mark_dirty()
            else:
                # Create dest page if needed
                if dest_page not in self.video_pages or self.video_pages[dest_page] is None:
                    self.video_pages[dest_page] = pygame.Surface(
                        (self.screen_width, self.screen_height)).convert()
                self.video_pages[dest_page].blit(source_surface, (0, 0))

            return False
        except Exception as e:
            print(f"Error in PCOPY at PC {pc}: {e}")
            return False

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

        # TRON trace output - print line number being executed
        if self.trace_mode:
            print(f"[{pc_of_this_line}]", end=" ")

        # Execute the logical line (which might contain multiple statements separated by ':')
        # The return value of execute_logical_line indicates if a GOTO, GOSUB, or DELAY happened.
        try:
            return self.execute_logical_line(logical_line_content, pc_of_this_line)
        except BasicRuntimeError as e:
            # Handle runtime error with ON ERROR GOTO handler
            if self.error_handler_label:
                self.error_resume_pc = pc_of_this_line
                self.in_error_handler = True
                # Jump to error handler
                if self.error_handler_label in self.labels:
                    self.pc = self.labels[self.error_handler_label]
                    return True  # PC jumped
                else:
                    print(f"Error: Label '{self.error_handler_label}' not found for ON ERROR GOTO")
                    self.running = False
                    return False
            else:
                print(f"Unhandled runtime error at PC {pc_of_this_line}: {e}")
                self.running = False
                return False


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
        # Don't execute BASIC code while waiting for INPUT
        if self.input_mode:
            return

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