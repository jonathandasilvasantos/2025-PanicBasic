"""
PASIC Interpreter Constants

This module contains constant values used throughout the BASIC interpreter.
These constants define screen modes, color palettes, default values, and
other configuration parameters.

All constants are meant to be imported and used instead of magic numbers
throughout the codebase.
"""

from typing import Dict, Tuple

# --- Display Constants ---
FONT_SIZE: int = 16
INITIAL_WINDOW_WIDTH: int = 800
INITIAL_WINDOW_HEIGHT: int = 600
DEFAULT_SCREEN_WIDTH: int = 320
DEFAULT_SCREEN_HEIGHT: int = 200

# --- Performance Constants ---
MAX_STEPS_PER_FRAME: int = 2000  # Maximum BASIC statements per frame
PRINT_TAB_WIDTH: int = 14  # Width of tab stops for PRINT statement

# --- Cache Configuration ---
EXPR_CACHE_MAX_SIZE: int = 10000  # Maximum entries in expression cache
COMPILED_CACHE_MAX_SIZE: int = 10000  # Maximum entries in compiled expression cache
IDENTIFIER_CACHE_MAX_SIZE: int = 5000  # Maximum entries in identifier cache

# --- Screen Mode Definitions ---
# Maps QBasic screen mode numbers to (width, height) tuples
SCREEN_MODES: Dict[int, Tuple[int, int]] = {
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

# --- Default Color Palette ---
# Standard QBasic 16-color palette (color number -> RGB tuple)
DEFAULT_COLORS: Dict[int, Tuple[int, int, int]] = {
    0: (0, 0, 0),         # Black
    1: (0, 0, 170),       # Blue
    2: (0, 170, 0),       # Green
    3: (0, 170, 170),     # Cyan
    4: (170, 0, 0),       # Red
    5: (170, 0, 170),     # Magenta
    6: (170, 85, 0),      # Brown
    7: (170, 170, 170),   # Light Gray
    8: (85, 85, 85),      # Dark Gray
    9: (85, 85, 255),     # Light Blue
    10: (85, 255, 85),    # Light Green
    11: (85, 255, 255),   # Light Cyan
    12: (255, 85, 85),    # Light Red
    13: (255, 85, 255),   # Light Magenta
    14: (255, 255, 85),   # Yellow
    15: (255, 255, 255),  # White
}

# --- Default Foreground/Background Colors ---
DEFAULT_FG_COLOR: int = 7  # Light Gray
DEFAULT_BG_COLOR: int = 0  # Black

# --- Text Mode Constants ---
DEFAULT_TEXT_ROWS: int = 25  # Default number of text rows
DEFAULT_TEXT_COLS: int = 80  # Default number of text columns

# --- Array Constants ---
DEFAULT_ARRAY_SIZE: int = 10  # Default upper bound for undimensioned arrays

# --- Key Scan Code Mappings ---
# Maps QBasic extended key codes to their meanings
# These are returned by INKEY$ for special keys
SCAN_CODES: Dict[str, int] = {
    'UP': 72,
    'DOWN': 80,
    'LEFT': 75,
    'RIGHT': 77,
    'HOME': 71,
    'END': 79,
    'PGUP': 73,
    'PGDN': 81,
    'INSERT': 82,
    'DELETE': 83,
    'F1': 59,
    'F2': 60,
    'F3': 61,
    'F4': 62,
    'F5': 63,
    'F6': 64,
    'F7': 65,
    'F8': 66,
    'F9': 67,
    'F10': 68,
}

# --- Error Codes ---
# Standard QBasic error codes
ERROR_CODES: Dict[int, str] = {
    1: "NEXT without FOR",
    2: "Syntax error",
    3: "RETURN without GOSUB",
    4: "Out of DATA",
    5: "Illegal function call",
    6: "Overflow",
    7: "Out of memory",
    8: "Label not defined",
    9: "Subscript out of range",
    10: "Duplicate definition",
    11: "Division by zero",
    14: "Out of string space",
    19: "No RESUME",
    20: "RESUME without error",
    50: "FIELD overflow",
    51: "Internal error",
    52: "Bad file name or number",
    53: "File not found",
    54: "Bad file mode",
    55: "File already open",
    57: "Device I/O error",
    58: "File already exists",
    61: "Disk full",
    62: "Input past end of file",
    63: "Bad record number",
    64: "Bad file name",
    67: "Too many files",
    68: "Device unavailable",
    70: "Permission denied",
    71: "Disk not ready",
    74: "Rename across disks",
    75: "Path/File access error",
    76: "Path not found",
}
