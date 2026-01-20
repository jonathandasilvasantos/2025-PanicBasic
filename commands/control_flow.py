"""
PASIC Control Flow Command Handlers

This module provides the ControlFlowMixin class which contains handlers
for control flow-related BASIC commands: GOTO, GOSUB, ON GOTO/GOSUB,
and block skipping utilities.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from interpreter import BasicInterpreter


class ControlFlowMixin:
    """Mixin class providing control flow command handlers.

    This mixin is designed to be inherited by BasicInterpreter and provides
    implementations for GOTO, GOSUB, ON GOTO/GOSUB, and block skipping.

    Required attributes from BasicInterpreter:
    - labels: Dictionary mapping label names to PC indices
    - pc: Current program counter
    - running: Boolean indicating if program is running
    - gosub_stack: Stack for GOSUB return addresses
    - for_stack: Stack for FOR loop state
    - loop_stack: Stack for DO/WHILE loop state
    - program_lines: List of program lines
    - eval_expr: Method to evaluate BASIC expressions
    """

    def _do_goto(self: 'BasicInterpreter', label: str) -> bool:
        """Execute GOTO statement - unconditional jump to label.

        Args:
            label: Target label name (uppercase).

        Returns:
            True if jump succeeded (PC changed), False if label not found.
        """
        target_pc_idx = self.labels.get(label)
        if target_pc_idx is not None:
            self.pc = target_pc_idx
            return True
        print(f"Error: Label '{label}' not found for GOTO at PC {self.pc-1}.")
        self.running = False
        return False

    def _do_gosub(self: 'BasicInterpreter', label: str) -> bool:
        """Execute GOSUB statement - subroutine call with return address.

        Args:
            label: Target label name (uppercase).

        Returns:
            True if call succeeded (PC changed), False if label not found.
        """
        target_pc_idx = self.labels.get(label)
        if target_pc_idx is not None:
            self.gosub_stack.append(self.pc)
            self.pc = target_pc_idx
            return True
        print(f"Error: Label '{label}' not found for GOSUB at PC {self.pc-1}.")
        self.running = False
        return False

    def _handle_on_goto_gosub(self: 'BasicInterpreter', expr: str, labels_str: str,
                              branch_type: str, pc: int) -> bool:
        """Handle ON...GOTO and ON...GOSUB statements.

        Args:
            expr: Expression that evaluates to the selector index.
            labels_str: Comma-separated list of target labels.
            branch_type: Either "GOTO" or "GOSUB".
            pc: Current program counter for error reporting.

        Returns:
            True if branch taken (PC changed), False otherwise.
        """
        selector = self.eval_expr(expr.strip())
        if not self.running:
            return False

        try:
            index = int(selector)
        except (ValueError, TypeError):
            print(f"Error: ON {branch_type} selector must be numeric at PC {pc}")
            self.running = False
            return False

        labels = [l.strip().upper() for l in labels_str.split(',')]

        # QBasic: if index < 1 or index > number of labels, continue to next statement
        if index < 1 or index > len(labels):
            return False

        target_label = labels[index - 1]  # 1-based indexing

        if branch_type == "GOTO":
            return self._do_goto(target_label)
        else:  # GOSUB
            return self._do_gosub(target_label)

    def _skip_block(self: 'BasicInterpreter', start_kw_upper: str,
                    end_kw_upper: str, pc_of_block_start: int) -> None:
        """Skip a block of code by advancing PC to after the end keyword.

        Used to skip FOR/NEXT, DO/LOOP, WHILE/WEND blocks when their
        condition is not met.

        Args:
            start_kw_upper: Starting keyword (e.g., "FOR", "DO", "WHILE").
            end_kw_upper: Ending keyword (e.g., "NEXT", "LOOP", "WEND").
            pc_of_block_start: PC where block started (for error reporting).
        """
        # Import here to avoid circular dependency at module level
        from interpreter import _next_re

        nesting_level = 1
        search_pc = self.pc
        is_first_line = True

        while search_pc < len(self.program_lines) and nesting_level > 0:
            _, _, line_to_scan = self.program_lines[search_pc]
            # Check ALL statements on the line, not just the first one
            # This handles cases like "WHILE condition: WEND" on a single line
            statements = self._split_statements(line_to_scan)

            skipped_first_start = False
            for stmt in statements:
                cmd_upper = stmt.strip().upper()

                if cmd_upper.startswith(start_kw_upper):
                    # On the first line, skip the first start keyword since
                    # that's the block we're already inside (nesting_level=1)
                    if is_first_line and not skipped_first_start:
                        skipped_first_start = True
                    else:
                        nesting_level += 1
                elif cmd_upper.startswith(end_kw_upper):
                    # For NEXT [var], ensure it's a NEXT, not something like NEXTPAGE
                    if end_kw_upper == "NEXT" and not _next_re.match(cmd_upper):
                        pass  # Not a true NEXT statement
                    else:
                        nesting_level -= 1

                if nesting_level == 0:
                    self.pc = search_pc + 1
                    return

            search_pc += 1
            is_first_line = False

        # EOF reached before block end
        print(f"Warning: EOF reached while skipping '{start_kw_upper}' block started at PC {pc_of_block_start}.")
        self.running = False
        self.pc = len(self.program_lines)

    def _skip_while_block(self: 'BasicInterpreter', start_pc_num: int) -> None:
        """Skip to the matching WEND statement.

        Args:
            start_pc_num: PC where WHILE started (for error reporting).
        """
        if self.loop_stack and self.loop_stack[-1].get("type") == "WHILE":
            self.loop_stack.pop()
        self._skip_block("WHILE", "WEND", start_pc_num)

    def _skip_for_block(self: 'BasicInterpreter', start_pc_num: int) -> None:
        """Skip to the matching NEXT statement for a FOR loop.

        Args:
            start_pc_num: PC where FOR started (for error reporting).
        """
        if self.for_stack and self.for_stack[-1]["loop_pc"] == self.pc:
            if not self.for_stack[-1].get("placeholder"):
                self.for_stack.pop()
        self._skip_block("FOR", "NEXT", start_pc_num)

    def _skip_loop_block(self: 'BasicInterpreter', start_pc_num: int) -> None:
        """Skip to the matching LOOP statement for a DO loop.

        Args:
            start_pc_num: PC where DO started (for error reporting).
        """
        if self.loop_stack and self.loop_stack[-1]["start_pc"] == self.pc:
            if not self.loop_stack[-1].get("placeholder"):
                self.loop_stack.pop()
        self._skip_block("DO", "LOOP", start_pc_num)

    def _skip_to_next(self: 'BasicInterpreter', start_pc_num: int) -> None:
        """Skip to the matching NEXT statement for EXIT FOR.

        Args:
            start_pc_num: PC where FOR started (for error reporting).
        """
        self._skip_block("FOR", "NEXT", start_pc_num)

    def _skip_to_loop(self: 'BasicInterpreter', start_pc_num: int) -> None:
        """Skip to the matching LOOP statement for EXIT DO.

        Args:
            start_pc_num: PC where DO started (for error reporting).
        """
        self._skip_block("DO", "LOOP", start_pc_num)
