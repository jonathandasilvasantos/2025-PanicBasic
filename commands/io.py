"""
PASIC IO Command Handlers

This module provides the IOCommandsMixin class which contains handlers
for file I/O related BASIC commands: OPEN, CLOSE, INPUT#, PRINT#, etc.
"""

import os
import re
import glob
import struct
from typing import TYPE_CHECKING, Optional, Any

if TYPE_CHECKING:
    from interpreter import BasicInterpreter


class IOCommandsMixin:
    """Mixin class providing file I/O command handlers.

    This mixin is designed to be inherited by BasicInterpreter and provides
    implementations for file operations like OPEN, CLOSE, INPUT#, PRINT#, etc.

    Required attributes from BasicInterpreter:
    - eval_expr: Method to evaluate BASIC expressions
    - running: Boolean indicating if program is running
    - file_handles: Dictionary mapping file numbers to file handles
    - next_file_number: Next available file number
    - variables: Dictionary of BASIC variables
    - field_defs: Dictionary of FIELD definitions
    - field_buffers: Dictionary of FIELD buffers
    """

    def _handle_open(self: 'BasicInterpreter', match: Any, pc: int) -> bool:
        """Handle OPEN filename FOR mode AS #n.

        Args:
            match: Regex match object with filename, mode, and file number groups.
            pc: Current program counter for error reporting.

        Returns:
            False (does not change PC).
        """
        try:
            filename_expr = match.group(1).strip()
            if filename_expr.startswith('"') and filename_expr.endswith('"'):
                filename = filename_expr[1:-1]
            else:
                filename = str(self.eval_expr(filename_expr))
                if not self.running:
                    return False
            mode = match.group(2).upper()
            file_num_expr = match.group(3).strip()
            file_num = int(self.eval_expr(file_num_expr))
            if not self.running:
                return False

            mode_map = {
                'INPUT': 'r',
                'OUTPUT': 'w',
                'APPEND': 'a',
                'BINARY': 'rb',
                'RANDOM': 'r+b'
            }

            py_mode = mode_map.get(mode, 'r')

            if mode in ('OUTPUT', 'APPEND'):
                fh = open(filename, py_mode, encoding='utf-8' if 'b' not in py_mode else None)
            elif mode == 'INPUT':
                fh = open(filename, py_mode, encoding='utf-8')
            else:
                try:
                    fh = open(filename, py_mode)
                except FileNotFoundError:
                    fh = open(filename, 'w+b')

            fh.file_path = filename
            self.file_handles[file_num] = fh

            if file_num >= self.next_file_number:
                self.next_file_number = file_num + 1

            return False
        except Exception as e:
            print(f"Error in OPEN at PC {pc}: {e}")
            self.running = False
            return False

    def _handle_close(self: 'BasicInterpreter', match: Any, pc: int) -> bool:
        """Handle CLOSE [#n].

        Args:
            match: Regex match object with optional file number.
            pc: Current program counter for error reporting.

        Returns:
            False (does not change PC).
        """
        try:
            if match.group(1):
                file_num = int(self.eval_expr(match.group(1).strip()))
                if not self.running:
                    return False
                if file_num in self.file_handles:
                    self.file_handles[file_num].close()
                    del self.file_handles[file_num]
            else:
                for fh in self.file_handles.values():
                    fh.close()
                self.file_handles.clear()
                self.next_file_number = 1
            return False
        except Exception as e:
            print(f"Error in CLOSE at PC {pc}: {e}")
            return False

    def _handle_input_file(self: 'BasicInterpreter', match: Any, pc: int) -> bool:
        """Handle INPUT #n, vars.

        Args:
            match: Regex match object with file number and variable list.
            pc: Current program counter for error reporting.

        Returns:
            False (does not change PC).
        """
        try:
            file_num = int(self.eval_expr(match.group(1).strip()))
            if not self.running:
                return False
            vars_str = match.group(2)

            if file_num not in self.file_handles:
                print(f"Error: File #{file_num} not open at PC {pc}")
                self.running = False
                return False

            fh = self.file_handles[file_num]
            var_names = [v.strip() for v in vars_str.split(',')]

            for var_name in var_names:
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

    def _handle_line_input_file(self: 'BasicInterpreter', match: Any, pc: int) -> bool:
        """Handle LINE INPUT #n, var$.

        Args:
            match: Regex match object with file number and variable name.
            pc: Current program counter for error reporting.

        Returns:
            False (does not change PC).
        """
        try:
            file_num = int(self.eval_expr(match.group(1).strip()))
            if not self.running:
                return False
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

    def _handle_print_file(self: 'BasicInterpreter', match: Any, pc: int) -> bool:
        """Handle PRINT #n, expressions.

        Args:
            match: Regex match object with file number and expression string.
            pc: Current program counter for error reporting.

        Returns:
            False (does not change PC).
        """
        from interpreter import _split_args

        try:
            file_num = int(self.eval_expr(match.group(1).strip()))
            if not self.running:
                return False
            expr_str = match.group(2) or ""

            if file_num not in self.file_handles:
                print(f"Error: File #{file_num} not open at PC {pc}")
                self.running = False
                return False

            fh = self.file_handles[file_num]

            if expr_str.strip():
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

    def _handle_write_file(self: 'BasicInterpreter', match: Any, pc: int) -> bool:
        """Handle WRITE #n, expressions (comma-separated with quotes around strings).

        Args:
            match: Regex match object with file number and expression string.
            pc: Current program counter for error reporting.

        Returns:
            False (does not change PC).
        """
        from interpreter import _split_args

        try:
            file_num = int(self.eval_expr(match.group(1).strip()))
            if not self.running:
                return False
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

    def _handle_get_file(self: 'BasicInterpreter', match: Any, pc: int) -> bool:
        """Handle GET #filenum[, recordnum], variable - read binary data from file.

        Args:
            match: Regex match object with file number, optional record number, and variable.
            pc: Current program counter for error reporting.

        Returns:
            False (does not change PC).
        """
        try:
            file_num = int(match.group(1))
            record_num = match.group(2)
            var_name = match.group(3).strip().upper()

            if file_num not in self.file_handles:
                print(f"Error: File #{file_num} not open at PC {pc}")
                self.running = False
                return False

            fh = self.file_handles[file_num]

            if record_num:
                record_num = int(record_num)
                fh.seek(record_num - 1)

            if var_name.endswith('$') or var_name.endswith('_STR'):
                data = b''
                while True:
                    byte = fh.read(1)
                    if not byte or byte == b'\0' or byte == b'\n':
                        break
                    data += byte
                self.variables[var_name] = data.decode('latin-1')
            elif var_name.endswith('_INT') or var_name.endswith('%'):
                data = fh.read(2)
                if len(data) == 2:
                    self.variables[var_name] = struct.unpack('<h', data)[0]
                else:
                    self.variables[var_name] = 0
            elif var_name.endswith('_LNG') or var_name.endswith('&'):
                data = fh.read(4)
                if len(data) == 4:
                    self.variables[var_name] = struct.unpack('<i', data)[0]
                else:
                    self.variables[var_name] = 0
            elif var_name.endswith('_SNG') or var_name.endswith('!'):
                data = fh.read(4)
                if len(data) == 4:
                    self.variables[var_name] = struct.unpack('<f', data)[0]
                else:
                    self.variables[var_name] = 0.0
            elif var_name.endswith('_DBL') or var_name.endswith('#'):
                data = fh.read(8)
                if len(data) == 8:
                    self.variables[var_name] = struct.unpack('<d', data)[0]
                else:
                    self.variables[var_name] = 0.0
            else:
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

    def _handle_put_file(self: 'BasicInterpreter', match: Any, pc: int) -> bool:
        """Handle PUT #filenum[, recordnum], variable - write binary data to file.

        Args:
            match: Regex match object with file number, optional record number, and variable.
            pc: Current program counter for error reporting.

        Returns:
            False (does not change PC).
        """
        try:
            file_num = int(match.group(1))
            record_num = match.group(2)
            var_name = match.group(3).strip().upper()

            if file_num not in self.file_handles:
                print(f"Error: File #{file_num} not open at PC {pc}")
                self.running = False
                return False

            fh = self.file_handles[file_num]

            if record_num:
                record_num = int(record_num)
                fh.seek(record_num - 1)

            value = self.variables.get(var_name, 0)

            if var_name.endswith('$') or var_name.endswith('_STR'):
                data = str(value).encode('latin-1')
                fh.write(data)
            elif var_name.endswith('_INT') or var_name.endswith('%'):
                fh.write(struct.pack('<h', int(value)))
            elif var_name.endswith('_LNG') or var_name.endswith('&'):
                fh.write(struct.pack('<i', int(value)))
            elif var_name.endswith('_SNG') or var_name.endswith('!'):
                fh.write(struct.pack('<f', float(value)))
            elif var_name.endswith('_DBL') or var_name.endswith('#'):
                fh.write(struct.pack('<d', float(value)))
            else:
                fh.write(struct.pack('<h', int(value)))

            return False
        except Exception as e:
            print(f"Error in PUT # at PC {pc}: {e}")
            self.running = False
            return False

    def _handle_seek(self: 'BasicInterpreter', file_num_str: str, position_expr: str, pc: int) -> bool:
        """Handle SEEK #n, position - set file position.

        Args:
            file_num_str: File number as string.
            position_expr: Expression for position.
            pc: Current program counter for error reporting.

        Returns:
            False (does not change PC).
        """
        try:
            file_num = int(file_num_str)
            position = int(self.eval_expr(position_expr))
            if not self.running:
                return False

            if file_num not in self.file_handles:
                print(f"Error: File #{file_num} not open at PC {pc}")
                self.running = False
                return False

            fh = self.file_handles[file_num]
            fh.seek(position - 1)
            return False
        except Exception as e:
            print(f"Error in SEEK at PC {pc}: {e}")
            self.running = False
            return False

    def _handle_kill(self: 'BasicInterpreter', filename_expr: str, pc: int) -> bool:
        """Handle KILL filename - delete a file.

        Args:
            filename_expr: Expression for filename.
            pc: Current program counter for error reporting.

        Returns:
            False (does not change PC).
        """
        try:
            if filename_expr.startswith('"') and filename_expr.endswith('"'):
                filename = filename_expr[1:-1]
            else:
                filename = str(self.eval_expr(filename_expr))
                if not self.running:
                    return False

            os.remove(filename)
            return False
        except FileNotFoundError:
            print(f"Error in KILL at PC {pc}: File not found '{filename_expr}'")
            self.running = False
            return False
        except Exception as e:
            print(f"Error in KILL at PC {pc}: {e}")
            self.running = False
            return False

    def _handle_name(self: 'BasicInterpreter', old_name_expr: str, new_name_expr: str, pc: int) -> bool:
        """Handle NAME oldname AS newname - rename a file.

        Args:
            old_name_expr: Expression for old filename.
            new_name_expr: Expression for new filename.
            pc: Current program counter for error reporting.

        Returns:
            False (does not change PC).
        """
        try:
            if old_name_expr.startswith('"') and old_name_expr.endswith('"'):
                old_name = old_name_expr[1:-1]
            else:
                old_name = str(self.eval_expr(old_name_expr))
                if not self.running:
                    return False

            if new_name_expr.startswith('"') and new_name_expr.endswith('"'):
                new_name = new_name_expr[1:-1]
            else:
                new_name = str(self.eval_expr(new_name_expr))
                if not self.running:
                    return False

            os.rename(old_name, new_name)
            return False
        except FileNotFoundError:
            print(f"Error in NAME at PC {pc}: File not found '{old_name_expr}'")
            self.running = False
            return False
        except Exception as e:
            print(f"Error in NAME at PC {pc}: {e}")
            self.running = False
            return False

    def _handle_mkdir(self: 'BasicInterpreter', dir_expr: str, pc: int) -> bool:
        """Handle MKDIR dirname - create a directory.

        Args:
            dir_expr: Expression for directory name.
            pc: Current program counter for error reporting.

        Returns:
            False (does not change PC).
        """
        try:
            if dir_expr.startswith('"') and dir_expr.endswith('"'):
                dirname = dir_expr[1:-1]
            else:
                dirname = str(self.eval_expr(dir_expr))
                if not self.running:
                    return False

            os.mkdir(dirname)
            return False
        except FileExistsError:
            print(f"Error in MKDIR at PC {pc}: Directory already exists '{dir_expr}'")
            self.running = False
            return False
        except Exception as e:
            print(f"Error in MKDIR at PC {pc}: {e}")
            self.running = False
            return False

    def _handle_rmdir(self: 'BasicInterpreter', dir_expr: str, pc: int) -> bool:
        """Handle RMDIR dirname - remove a directory.

        Args:
            dir_expr: Expression for directory name.
            pc: Current program counter for error reporting.

        Returns:
            False (does not change PC).
        """
        try:
            if dir_expr.startswith('"') and dir_expr.endswith('"'):
                dirname = dir_expr[1:-1]
            else:
                dirname = str(self.eval_expr(dir_expr))
                if not self.running:
                    return False

            os.rmdir(dirname)
            return False
        except FileNotFoundError:
            print(f"Error in RMDIR at PC {pc}: Directory not found '{dir_expr}'")
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

    def _handle_chdir(self: 'BasicInterpreter', dir_expr: str, pc: int) -> bool:
        """Handle CHDIR dirname - change current directory.

        Args:
            dir_expr: Expression for directory name.
            pc: Current program counter for error reporting.

        Returns:
            False (does not change PC).
        """
        try:
            if dir_expr.startswith('"') and dir_expr.endswith('"'):
                dirname = dir_expr[1:-1]
            else:
                dirname = str(self.eval_expr(dir_expr))
                if not self.running:
                    return False

            os.chdir(dirname)
            return False
        except FileNotFoundError:
            print(f"Error in CHDIR at PC {pc}: Directory not found '{dir_expr}'")
            self.running = False
            return False
        except Exception as e:
            print(f"Error in CHDIR at PC {pc}: {e}")
            self.running = False
            return False

    def _handle_files(self: 'BasicInterpreter', pattern_expr: Optional[str], pc: int) -> bool:
        """Handle FILES [pattern] - list directory contents.

        Args:
            pattern_expr: Optional pattern expression.
            pc: Current program counter for error reporting.

        Returns:
            False (does not change PC).
        """
        try:
            if pattern_expr:
                pattern_expr = pattern_expr.strip()
                if pattern_expr.startswith('"') and pattern_expr.endswith('"'):
                    pattern = pattern_expr[1:-1]
                else:
                    pattern = str(self.eval_expr(pattern_expr))
                    if not self.running:
                        return False
            else:
                pattern = "*.*"

            files = glob.glob(pattern)
            if not files:
                files = glob.glob(os.path.join(pattern, "*")) if os.path.isdir(pattern) else []

            for f in sorted(files):
                print(os.path.basename(f), end="  ")
            print()

            return False
        except Exception as e:
            print(f"Error in FILES at PC {pc}: {e}")
            return False

    def _handle_field(self: 'BasicInterpreter', match: re.Match, pc: int) -> bool:
        """Handle FIELD statement - define record fields for random access files.

        FIELD #filenum, width AS var$, width AS var$, ...

        Args:
            match: Regex match object with file number and fields string.
            pc: Current program counter for error reporting.

        Returns:
            False (does not change PC).
        """
        try:
            file_num = int(match.group(1))
            fields_str = match.group(2)

            fields = []
            field_pattern = re.compile(r'(\d+)\s+AS\s+([a-zA-Z_][a-zA-Z0-9_]*\$?)', re.IGNORECASE)
            for field_match in field_pattern.finditer(fields_str):
                width = int(field_match.group(1))
                var_name = field_match.group(2).upper()
                fields.append((width, var_name))
                self.variables[var_name] = " " * width

            self.field_defs[file_num] = fields
            total_width = sum(w for w, _ in fields)
            self.field_buffers[file_num] = " " * total_width

            return False
        except Exception as e:
            print(f"Error in FIELD statement at PC {pc}: {e}")
            self.running = False
            return False

    def _handle_lset(self: 'BasicInterpreter', var_name: str, value_expr: str, pc: int) -> bool:
        """Handle LSET statement - left-justify string in field variable.

        LSET var$ = expression$

        Args:
            var_name: Variable name.
            value_expr: Value expression.
            pc: Current program counter for error reporting.

        Returns:
            False (does not change PC).
        """
        try:
            var_upper = var_name.upper()
            value = str(self.eval_expr(value_expr))
            if not self.running:
                return False

            if var_upper in self.variables and isinstance(self.variables[var_upper], str):
                field_width = len(self.variables[var_upper])
                if len(value) >= field_width:
                    self.variables[var_upper] = value[:field_width]
                else:
                    self.variables[var_upper] = value + " " * (field_width - len(value))
            else:
                self.variables[var_upper] = value

            return False
        except Exception as e:
            print(f"Error in LSET statement at PC {pc}: {e}")
            self.running = False
            return False

    def _handle_rset(self: 'BasicInterpreter', var_name: str, value_expr: str, pc: int) -> bool:
        """Handle RSET statement - right-justify string in field variable.

        RSET var$ = expression$

        Args:
            var_name: Variable name.
            value_expr: Value expression.
            pc: Current program counter for error reporting.

        Returns:
            False (does not change PC).
        """
        try:
            var_upper = var_name.upper()
            value = str(self.eval_expr(value_expr))
            if not self.running:
                return False

            if var_upper in self.variables and isinstance(self.variables[var_upper], str):
                field_width = len(self.variables[var_upper])
                if len(value) >= field_width:
                    self.variables[var_upper] = value[-field_width:]
                else:
                    self.variables[var_upper] = " " * (field_width - len(value)) + value
            else:
                self.variables[var_upper] = value

            return False
        except Exception as e:
            print(f"Error in RSET statement at PC {pc}: {e}")
            self.running = False
            return False
