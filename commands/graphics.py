"""
PASIC Graphics Command Handlers

This module provides the GraphicsCommandsMixin class which contains handlers
for graphics-related BASIC commands: DRAW, GET (graphics), PUT (graphics),
and helper methods like _scanline_fill.
"""

import math
from collections import deque
from typing import TYPE_CHECKING, Tuple, Any

import pygame

from constants import VGA_256_PALETTE

if TYPE_CHECKING:
    from interpreter import BasicInterpreter


class GraphicsCommandsMixin:
    """Mixin class providing graphics command handlers.

    This mixin is designed to be inherited by BasicInterpreter and provides
    implementations for DRAW, GET (graphics), PUT (graphics), and related helpers.

    Required attributes from BasicInterpreter:
    - eval_expr: Method to evaluate BASIC expressions
    - running: Boolean indicating if program is running
    - surface: pygame Surface for drawing
    - screen_width, screen_height: Screen dimensions
    - draw_x, draw_y, draw_angle: Turtle graphics state
    - current_fg_color: Current foreground color
    - basic_color: Method to convert color index to RGB
    - mark_dirty: Method to mark surface as needing redraw
    - variables: Dictionary of BASIC variables
    """

    def _scanline_fill(self: 'BasicInterpreter', x: int, y: int,
                       fill_color: Tuple, border_color: Tuple,
                       target_color: Tuple) -> None:
        """Optimized scanline flood fill algorithm.

        Args:
            x: Starting X coordinate.
            y: Starting Y coordinate.
            fill_color: RGB tuple for fill color.
            border_color: RGB tuple for border color.
            target_color: RGB tuple for the color being replaced.
        """
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

    def _do_draw(self: 'BasicInterpreter', draw_expr: str, pc: int) -> None:
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

        Args:
            draw_expr: Expression that evaluates to DRAW string.
            pc: Current program counter for error reporting.
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

    def _do_get_graphics(self: 'BasicInterpreter', match: Any, pc: int) -> bool:
        """Handle GET (x1, y1)-(x2, y2), array[(index)] - capture screen region to array.

        Args:
            match: Regex match object with coordinate and array groups.
            pc: Current program counter for error reporting.

        Returns:
            False (does not change PC).
        """
        try:
            x1 = int(self.eval_expr(match.group(1).strip()))
            y1 = int(self.eval_expr(match.group(2).strip()))
            x2 = int(self.eval_expr(match.group(3).strip()))
            y2 = int(self.eval_expr(match.group(4).strip()))
            array_ref = match.group(5).strip()

            if not self.running:
                return False

            # Parse array reference to get base name and optional index
            # Format: ArrayName[(index)] or ArrayName&[(index)]
            paren_pos = array_ref.find('(')
            if paren_pos != -1:
                # Has index - evaluate to get unique key
                array_name = array_ref[:paren_pos].upper()
                index_expr = array_ref[paren_pos+1:-1]  # Remove outer parens
                index = int(self.eval_expr(index_expr))
                if not self.running:
                    return False
                sprite_key = f"{array_name}_{index}"
            else:
                array_name = array_ref.upper()
                sprite_key = array_name

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

            # Capture the screen region
            if self.surface:
                # Initialize sprites dict if not exists
                if not hasattr(self, '_sprites'):
                    self._sprites = {}

                # Capture palette indices if available (Screen 13 mode)
                indices = None
                if hasattr(self, '_pixel_indices') and self._pixel_indices is not None:
                    indices = bytearray(width * height)
                    for py in range(height):
                        for px in range(width):
                            src_idx = (y1 + py) * self.screen_width + (x1 + px)
                            if src_idx < len(self._pixel_indices):
                                indices[py * width + px] = self._pixel_indices[src_idx]

                # Also capture the current surface (for fallback/non-indexed modes)
                captured = self.surface.subsurface((x1, y1, width, height)).copy()

                # Store sprite with unique key based on array name and index
                self._sprites[sprite_key] = {
                    '_sprite': True,
                    'width': width,
                    'height': height,
                    'surface': captured,
                    'indices': indices  # Palette indices for Screen 13
                }
                # Also store in variables for simple array name lookups
                if paren_pos == -1:
                    self.variables[array_name] = self._sprites[sprite_key]

            return False
        except Exception as e:
            print(f"Error in GET at PC {pc}: {e}")
            return False

    def _do_put_graphics(self: 'BasicInterpreter', match: Any, pc: int) -> bool:
        """Handle PUT (x, y), array[(index)][, mode] - display sprite from array.

        Modes:
        - PSET: Copy sprite directly
        - PRESET: Copy with inverted colors
        - AND: Combine with destination using AND
        - OR: Combine with destination using OR
        - XOR: Combine with destination using XOR (default)

        Args:
            match: Regex match object with coordinate, array, and mode groups.
            pc: Current program counter for error reporting.

        Returns:
            False (does not change PC).
        """
        try:
            x = int(self.eval_expr(match.group(1).strip()))
            y = int(self.eval_expr(match.group(2).strip()))
            array_ref = match.group(3).strip()
            mode = (match.group(4) or "XOR").upper()

            if not self.running:
                return False

            # Parse array reference to get base name and optional index
            paren_pos = array_ref.find('(')
            if paren_pos != -1:
                # Has index - evaluate to get unique key
                array_name = array_ref[:paren_pos].upper()
                index_expr = array_ref[paren_pos+1:-1]  # Remove outer parens
                index = int(self.eval_expr(index_expr))
                if not self.running:
                    return False
                sprite_key = f"{array_name}_{index}"
            else:
                array_name = array_ref.upper()
                sprite_key = array_name

            # Get the sprite data from _sprites dict or variables
            sprite_data = None
            if hasattr(self, '_sprites') and sprite_key in self._sprites:
                sprite_data = self._sprites[sprite_key]
            else:
                sprite_data = self.variables.get(array_name)

            if not sprite_data or not isinstance(sprite_data, dict) or not sprite_data.get('_sprite'):
                # Silently skip if no sprite (common in games during initialization)
                return False

            width = sprite_data['width']
            height = sprite_data['height']
            sprite_indices = sprite_data.get('indices')

            # If we have palette indices, convert them to RGB using current palette
            # This allows sprites captured at one palette state to display correctly
            # when the palette has been changed (e.g., after PALETTE reset)
            if sprite_indices is not None and self.surface:
                # Create a fresh surface using current palette colors
                sprite_surface = pygame.Surface((width, height)).convert()
                sprite_surface.fill((0, 0, 0))  # Fill with transparent/black

                for py in range(height):
                    for px in range(width):
                        idx = py * width + px
                        if idx < len(sprite_indices):
                            palette_idx = sprite_indices[idx]
                            # Use current colors dict, fall back to VGA_256_PALETTE
                            color = self.colors.get(palette_idx, VGA_256_PALETTE.get(palette_idx, (palette_idx, palette_idx, palette_idx)))
                            sprite_surface.set_at((px, py), color)
            else:
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
                    # Check bounds to avoid errors
                    if x >= 0 and y >= 0 and x + width <= self.screen_width and y + height <= self.screen_height:
                        temp = self.surface.subsurface((x, y, width, height)).copy()
                        arr1 = pygame.surfarray.pixels3d(temp)
                        arr2 = pygame.surfarray.pixels3d(sprite_surface)
                        arr1 ^= arr2
                        del arr1, arr2
                        self.surface.blit(temp, (x, y))
                    else:
                        # Fallback to simple blit for out-of-bounds
                        self.surface.blit(sprite_surface, (x, y))
                self.mark_dirty()

            return False
        except Exception as e:
            print(f"Error in PUT at PC {pc}: {e}")
            return False
