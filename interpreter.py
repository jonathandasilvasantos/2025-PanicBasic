#!/usr/bin/env python3
"""Refactored BASIC interpreter module with two-dimensional array support."""

import pygame
import re
import random
import time
from typing import List, Optional, Tuple
from pygame.locals import KEYDOWN

FONT_SIZE = 24

def replace_array_access(match: re.Match) -> str:
    """Replacement function for converting array access from BASIC style."""
    name = match.group(1)
    indices = match.group(2)
    if ',' in indices:
        parts = [p.strip() for p in indices.split(',')]
        return f"{name}[int({parts[0]})][int({parts[1]})]"
    else:
        return f"{name}[int({indices.strip()})]"

def convert_basic_expr(expr: str, variables: dict) -> str:
    """Convert a BASIC expression to valid Python."""
    expr = expr.replace(" OR ", " or ")
    expr = expr.replace(" AND ", " and ")
    expr = re.sub(r'(?<![<>!])=(?![=<>])', '==', expr)
    expr = expr.replace("<>", "!=")
    expr = re.sub(r'([A-Za-z]+)\$', r'\1', expr)
    expr = re.sub(r'\b(?!CHR\b|INKEY\b|RND\b|INT\b|POINT\b)([A-Za-z]+)\s*\(\s*([^)]+)\s*\)', replace_array_access, expr)
    expr = re.sub(r'\bRND\b(?!\()', 'RND()', expr)
    expr = re.sub(r'\bINKEY\b(?!\s*\()', 'INKEY()', expr)
    return expr

class BasicInterpreter:
    """A simple BASIC interpreter."""

    def __init__(self, font: pygame.font.Font, width: int, height: int) -> None:
        self.font = font
        self.width = width
        self.height = height
        self.program_lines: List[str] = []
        self.pc: int = 0
        self.variables: dict = {}
        self.loop_stack: List[int] = []
        self.for_stack: List[dict] = []
        self.running: bool = True
        self.text_cursor: Tuple[int, int] = (0, 1)
        self.surface: Optional[pygame.Surface] = None
        self.screen_width: int = 320
        self.screen_height: int = 200
        self.last_key: str = ""
        self.colors = {
            0: (0, 0, 0),
            1: (0, 0, 170),
            2: (0, 170, 0),
            3: (0, 170, 170),
            4: (170, 0, 0),
            5: (170, 0, 170),
            6: (170, 85, 0),
            7: (170, 170, 170),
            8: (85, 85, 85),
            9: (85, 85, 255),
            10: (85, 255, 85),
            11: (85, 255, 255),
            12: (255, 85, 85),
            13: (255, 85, 255),
            14: (255, 255, 85),
            15: (255, 255, 255)
        }
        self.subroutines: dict = {}
        self.delay_until: int = 0
        self.labels: dict = {}  # Store labels and their corresponding line numbers

    def reset(self, program_lines: List[str]) -> None:
        self.subroutines = {}
        self.labels = {}
        main_program = []
        i = 0
        while i < len(program_lines):
            line = program_lines[i]
            clean_line = line.strip()
            if clean_line.endswith(":"):
                self.labels[clean_line[:-1].upper()] = len(main_program)  # Store label and line number
                i += 1
                continue
            if clean_line.upper().startswith("SUB"):
                parts = clean_line.split()
                if len(parts) >= 2:
                    sub_name = parts[1].upper()
                    sub_lines = []
                    i += 1
                    while i < len(program_lines) and program_lines[i].strip().upper() != "END SUB":
                        sub_lines.append(program_lines[i])
                        i += 1
                    self.subroutines[sub_name] = sub_lines
                    i += 1
                    continue
            else:
                main_program.append(line)
            i += 1
        self.program_lines = main_program
        self.pc = 0
        self.variables = {}
        self.loop_stack = []
        self.for_stack = []
        self.running = True
        self.text_cursor = (0, 1)
        self.delay_until = 0
        if self.surface is None:
            self.surface = pygame.Surface((self.screen_width, self.screen_height))
            self.surface.fill((0, 0, 0))

    def basic_color(self, c: int) -> Tuple[int, int, int]:
        return self.colors.get(c, (255, 255, 255))

    def inkey(self):
        k = self.last_key
        self.last_key = ""
        return k

    def eval_expr(self, expr: str):
        conv_expr = convert_basic_expr(expr, self.variables)
        env = {"CHR": lambda x: chr(int(x)),
               "INKEY": self.inkey,
               "INT": lambda x: int(float(x)),
               "RND": lambda: random.random(),
               "POINT": self.point}
        env.update(self.variables)  # Add user variables
        try:
            return eval(conv_expr, {}, env)
        except Exception as e:
            print(f"Error evaluating '{expr}' -> '{conv_expr}': {e}")
            return 0

    def point(self, x, y):
        if self.surface:
            try:
                pixel = self.surface.get_at((int(x), int(y)))[:3]
                for num, col in self.colors.items():
                    if col == pixel:
                        return num
                return -1
            except Exception:
                return -1
        return -1

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == KEYDOWN:
            if event.key == pygame.K_UP:
                self.last_key = chr(0) + "H"
            elif event.key == pygame.K_DOWN:
                self.last_key = chr(0) + "P"
            elif event.key == pygame.K_ESCAPE:
                self.last_key = chr(27)
            else:
                self.last_key = event.unicode

    def skip_block(self, end_marker: str) -> None:
        nesting = 0
        while self.pc < len(self.program_lines):
            line = self.program_lines[self.pc].strip().upper()
            self.pc += 1
            if line.startswith(end_marker):
                if nesting == 0:
                    break
                else:
                    nesting -= 1
            elif line.startswith(end_marker.split()[0]):
                nesting += 1

    def skip_loop_block(self) -> None:
        nesting = 1
        while self.pc < len(self.program_lines):
            current_line = self.program_lines[self.pc].strip().upper()
            if current_line.startswith("DO"):
                nesting += 1
            elif current_line.startswith("LOOP"):
                nesting -= 1
                if nesting == 0:
                    self.pc += 1
                    break
            self.pc += 1

    def execute_select_case(self, select_expr_value):
        block_lines = []
        while self.pc < len(self.program_lines):
            line = self.program_lines[self.pc]
            self.pc += 1
            if line.strip().upper() == "END SELECT":
                break
            block_lines.append(line)
        i = 0
        while i < len(block_lines):
            line = block_lines[i].strip()
            if line.upper().startswith("CASE"):
                rest = line[4:].strip()
                if ":" in rest:
                    case_expr, inline_command = rest.split(":", 1)
                    case_expr = case_expr.strip()
                    inline_command = inline_command.strip()
                else:
                    case_expr = rest
                    inline_command = ""
                try:
                    case_val = self.eval_expr(case_expr)
                except Exception:
                    case_val = case_expr
                if case_val == select_expr_value:
                    if inline_command:
                        self.execute_line(inline_command)
                    i += 1
                    while i < len(block_lines):
                        next_line = block_lines[i].strip()
                        if next_line.upper().startswith("CASE"):
                            break
                        self.execute_line(next_line)
                        i += 1
                    return
            i += 1

    def run_subroutine(self, sub_name: str):
        sub_lines = self.subroutines.get(sub_name.upper())
        if sub_lines is None:
            print(f"Subroutine {sub_name} not found.")
            return
        saved_pc = self.pc
        saved_program = self.program_lines
        self.program_lines = sub_lines
        self.pc = 0
        while self.pc < len(self.program_lines) and self.running:
            self.step_line()
        self.program_lines = saved_program
        self.pc = saved_pc

    def step_line(self) -> bool:
        if self.pc >= len(self.program_lines):
            return False
        line = self.program_lines[self.pc].strip()
        self.pc += 1
        if "'" in line:
            line = line.split("'", 1)[0].strip()
        if not line:
            return False

        up_line = line.upper()

        if up_line == "END IF" or up_line == "END SELECT":
            return False

        if line.upper() in self.subroutines:
            self.run_subroutine(line.strip())
            return False

        if up_line.startswith("IF"):
            if "THEN" in up_line:
                parts = re.split(r'\bTHEN\b', line, maxsplit=1, flags=re.IGNORECASE)
                condition_part = parts[0][2:].strip()
                then_part = parts[1].strip()
                cond = self.eval_expr(condition_part)
                if then_part:
                    if cond:
                        self.execute_line(then_part)
                else:
                    if not cond:
                        self.skip_block("END IF")
                return False

        if up_line.startswith("SELECT CASE"):
            expr = line[len("SELECT CASE"):].strip()
            select_value = self.eval_expr(expr)
            self.execute_select_case(select_value)
            return False

        if up_line.startswith("FOR"):
            m = re.match(r'FOR\s+([A-Za-z]+)\s*=\s*(.+?)\s+TO\s+(.+?)(\s+STEP\s+(.+))?$', line, re.IGNORECASE)
            if m:
                var = m.group(1).strip()
                start_expr = m.group(2).strip()
                end_expr = m.group(3).strip()
                step_expr = m.group(5).strip() if m.group(5) else "1"
                start_val = self.eval_expr(start_expr)
                end_val = self.eval_expr(end_expr)
                step_val = self.eval_expr(step_expr)
                self.variables[var] = start_val
                self.for_stack.append({"var": var, "end": end_val, "step": step_val, "loop_line": self.pc})
            return False

        if up_line.startswith("NEXT"):
            if self.for_stack:
                loop_info = self.for_stack[-1]
                var = loop_info["var"]
                self.variables[var] = self.variables[var] + loop_info["step"]
                if loop_info["step"] >= 0:
                    if self.variables[var] <= loop_info["end"]:
                        self.pc = loop_info["loop_line"]
                    else:
                        self.for_stack.pop()
                else:
                    if self.variables[var] >= loop_info["end"]:
                        self.pc = loop_info["loop_line"]
                    else:
                        self.for_stack.pop()
            return False

        if up_line.startswith("RANDOMIZE"):
            if "TIMER" in up_line:
                random.seed(time.time())
            return False

        if up_line.startswith("DIM"):
            m = re.match(r'DIM\s+([A-Za-z]+)\(\s*(\d+)\s*,\s*(\d+)\s*\)', line, re.IGNORECASE)
            if m:
                var = m.group(1).strip()
                size1 = int(m.group(2).strip())
                size2 = int(m.group(3).strip())
                self.variables[var] = [[0]*(size2+1) for _ in range(size1+1)]
                return False

            m = re.match(r'DIM\s+([A-Za-z]+)\(\s*(\d+)\s*\)', line, re.IGNORECASE)
            if m:
                var = m.group(1).strip()
                size = int(m.group(2).strip())
                self.variables[var] = [0] * (size + 1)
                return False

        if "=" in line:
            if up_line.startswith("CONST"):
                content = line[5:].strip()
                if "=" in content:
                    var, expr = content.split("=", 1)
                    var_name = var.strip().replace("$", "")
                    self.variables[var_name] = self.eval_expr(expr.strip())
                return False

            parts = line.split("=", 1)
            lhs = parts[0].strip()
            rhs = parts[1].strip()
            value = self.eval_expr(rhs)

            m = re.match(r'([A-Za-z]+)\(\s*([^,]+)\s*,\s*([^)]+)\s*\)', lhs)
            if m:
                var = m.group(1).strip()
                index1_expr = m.group(2).strip()
                index2_expr = m.group(3).strip()
                index1 = self.eval_expr(index1_expr)
                index2 = self.eval_expr(index2_expr)


                if var in self.variables and isinstance(self.variables[var], list):
                    try:
                        self.variables[var][int(index1)][int(index2)] = value
                    except Exception as e:
                        print(f"Error assigning to two-dimensional array {var}: {e}")
                else:
                    print(f"Error: variable {var} is not a two-dimensional array.")
                return False

            m = re.match(r'([A-Za-z]+)\(\s*([^)]+)\s*\)', lhs)
            if m:
                var = m.group(1).strip()
                index_expr = m.group(2).strip()
                index = self.eval_expr(index_expr)

                if var in self.variables and isinstance(self.variables[var], list):
                    try:
                        self.variables[var][int(index)] = value
                    except Exception as e:
                        print(f"Error assigning to array {var}: {e}")
                else:
                    print(f"Error: variable {var} is not an array.")
                return False

            else:
                var_name = lhs.replace("$", "")
                self.variables[var_name] = value
            return False

        if up_line == "CLS":
            if self.surface:
                self.surface.fill((0, 0, 0))
            return False

        if up_line.startswith("SCREEN"):
            parts = line.split()
            if len(parts) >= 2 and parts[1] == "13":
                self.screen_width = 320
                self.screen_height = 200
                self.surface = pygame.Surface((self.screen_width, self.screen_height))
                self.surface.fill((0, 0, 0))
            return False

        if up_line.startswith("LOCATE"):
            params = line[6:].strip()
            if "," in params:
                parts = params.split(",")
                row = int(self.eval_expr(parts[0].strip()))
                col = int(self.eval_expr(parts[1].strip()))
                self.text_cursor = (col, row)
            return False

        if up_line.startswith("PRINT"):
            content = line[5:].strip()
            parts = content.split(";")
            out_text = ""
            for part in parts:
                part = part.strip()
                if part:
                    out_text += str(self.eval_expr(part))
            if self.surface:
                txt_surf = self.font.render(out_text, True, (255, 255, 255))
                cell_w = self.font.size("A")[0]
                x = self.text_cursor[0] * cell_w
                y = (self.text_cursor[1] - 1) * self.font.get_height()
                self.surface.blit(txt_surf, (x, y))
                self.text_cursor = (0, self.text_cursor[1] + 1)
            return False

        if up_line.startswith("LINE"):
            m = re.search(r"\(([^,]+),([^)]+)\)-\(([^,]+),([^)]+)\),([^,]+)(?:,\s*(BF))?", line, re.IGNORECASE)
            if m and self.surface:
                x1 = self.eval_expr(m.group(1).strip())
                y1 = self.eval_expr(m.group(2).strip())
                x2 = self.eval_expr(m.group(3).strip())
                y2 = self.eval_expr(m.group(4).strip())
                color = int(self.eval_expr(m.group(5).strip()))
                fill = m.group(6)
                rect = pygame.Rect(int(x1), int(y1), int(x2 - x1), int(y2 - y1))
                if fill and fill.upper() == "BF":
                    pygame.draw.rect(self.surface, self.basic_color(color), rect, 0)
                else:
                    pygame.draw.rect(self.surface, self.basic_color(color), rect, 1)
            return False

        if up_line.startswith("CIRCLE"):
            m = re.search(r"\(([^,]+),([^)]+)\),([^,]+),(.+)", line)
            if m and self.surface:
                x = self.eval_expr(m.group(1).strip())
                y = self.eval_expr(m.group(2).strip())
                radius = self.eval_expr(m.group(3).strip())
                color = int(self.eval_expr(m.group(4).strip()))
                pygame.draw.circle(self.surface, self.basic_color(color), (int(x), int(y)), int(radius), 1)
            return False

        if up_line.startswith("PAINT"):
            m = re.search(r"\(([^,]+),([^)]+)\),(.+)", line)
            if m and self.surface:
                x = self.eval_expr(m.group(1).strip())
                y = self.eval_expr(m.group(2).strip())
                color = int(self.eval_expr(m.group(3).strip()))
                pygame.draw.circle(self.surface, self.basic_color(color), (int(x), int(y)), 3, 0)
            return False

        if up_line.startswith("PSET"):
            m = re.search(r"PSET\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)\s*,\s*(.+)", line, re.IGNORECASE)
            if m and self.surface:
                x = self.eval_expr(m.group(1).strip())
                y = self.eval_expr(m.group(2).strip())
                color = int(self.eval_expr(m.group(3).strip()))
                self.surface.set_at((int(x), int(y)), self.basic_color(color))
            return False

        if up_line.startswith("_DELAY"):
            expr = line[6:].strip()
            try:
                delay_val = float(self.eval_expr(expr))
            except Exception:
                delay_val = 0
            self.delay_until = pygame.time.get_ticks() + int(delay_val * 1000)
            return True

        if up_line.startswith("SLEEP"):
            expr = line[5:].strip()
            try:
                sleep_val = float(self.eval_expr(expr))
            except Exception:
                sleep_val = 0
            self.delay_until = pygame.time.get_ticks() + int(sleep_val * 1000)
            return True

        if up_line.startswith("DO"):
            tokens = line.split()
            if len(tokens) > 1:
                if tokens[1].upper() == "WHILE":
                    condition = line[line.upper().find("WHILE") + 5:].strip()
                    if not self.eval_expr(condition):
                        self.skip_loop_block()
                    else:
                        self.loop_stack.append(self.pc)
                elif tokens[1].upper() == "UNTIL":
                    condition = line[line.upper().find("UNTIL") + 5:].strip()
                    if self.eval_expr(condition):
                        self.skip_loop_block()
                    else:
                        self.loop_stack.append(self.pc)
                else:
                    self.loop_stack.append(self.pc)
            else:
                self.loop_stack.append(self.pc)
            return False

        if up_line.startswith("LOOP"):
            if up_line.startswith("LOOP WHILE"):
                condition = line[10:].strip()
                if self.eval_expr(condition):
                    if self.loop_stack:
                        self.pc = self.loop_stack[-1]
                else:
                    if self.loop_stack:
                        self.loop_stack.pop()
            elif up_line.startswith("LOOP UNTIL"):
                condition = line[10:].strip()
                if not self.eval_expr(condition):
                    if self.loop_stack:
                        self.pc = self.loop_stack[-1]
                else:
                    if self.loop_stack:
                        self.loop_stack.pop()
            else:
                if self.loop_stack:
                    self.pc = self.loop_stack[-1]
            return False

        if up_line == "END":
            self.running = False
            return False
        
        if up_line.startswith("GOTO"):
            label = line[4:].strip().upper()
            if label in self.labels:
                self.pc = self.labels[label]
            else:
                print(f"Error: Label '{label}' not found.")
            return False


        try:
            self.eval_expr(line)
        except Exception as e:
            print(f"Unrecognized command: {line}")
        return False

    def execute_line(self, line: str) -> bool:
        saved_lines = self.program_lines
        saved_pc = self.pc
        self.program_lines = [line]
        self.pc = 0
        while self.pc < len(self.program_lines) and self.running:
            self.step_line()
        self.program_lines = saved_lines
        self.pc = saved_pc
        return False

    def step(self) -> None:
        current_time = pygame.time.get_ticks()
        if self.delay_until and current_time < self.delay_until:
            return
        else:
            self.delay_until = 0

        while self.running and self.pc < len(self.program_lines):
            delay_hit = self.step_line()
            if delay_hit:
                break

    def draw(self, target_surface: pygame.Surface) -> None:
        if self.surface:
            scaled = pygame.transform.scale(self.surface, (self.width, self.height))
            target_surface.blit(scaled, (0, 0))

def run_interpreter(filename: str) -> None:
    pygame.init()
    screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
    pygame.display.set_caption(f"BASIC Interpreter - {filename}")
    font = pygame.font.SysFont("monospace", FONT_SIZE)
    interpreter = BasicInterpreter(font, 800, 600)
    try:
        with open(filename, "r") as f:
            lines = f.read().splitlines()
    except Exception as e:
        print(f"Error reading file {filename}: {e}")
        return
    interpreter.reset(lines)
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                interpreter.handle_event(event)
        if interpreter.running:
            interpreter.step()
        screen.fill((0, 0, 0))
        interpreter.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()