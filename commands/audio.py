"""
PASIC Audio Command Handlers

This module provides the AudioCommandsMixin class which contains handlers
for audio-related BASIC commands: BEEP, SOUND, and PLAY.
"""

import array
import math
import time
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from interpreter import BasicInterpreter


class AudioCommandsMixin:
    """Mixin class providing audio command handlers.

    This mixin is designed to be inherited by BasicInterpreter and provides
    implementations for BEEP, SOUND, and PLAY commands.

    Required attributes from BasicInterpreter:
    - eval_expr: Method to evaluate BASIC expressions
    - running: Boolean indicating if program is running
    """

    def _do_beep(self: 'BasicInterpreter') -> None:
        """Execute BEEP command - plays a short beep sound."""
        try:
            # Generate a simple beep using pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1)

            # Create a simple sine wave beep (800 Hz, 0.2 seconds)
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

    def _do_sound(self: 'BasicInterpreter', freq_expr: str, duration_expr: str, pc: int) -> None:
        """Execute SOUND command - generates tone with specified frequency and duration.

        Args:
            freq_expr: Expression for frequency in Hz.
            duration_expr: Expression for duration in clock ticks (18.2 ticks/second).
            pc: Current program counter for error reporting.
        """
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

    def _do_play(self: 'BasicInterpreter', mml_expr: str, pc: int) -> None:
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

        Args:
            mml_expr: Expression that evaluates to MML string.
            pc: Current program counter for error reporting.
        """
        try:
            # Evaluate the MML string expression
            mml_string = str(self.eval_expr(mml_expr))
            if not self.running:
                return

            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1)

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

    def _play_note(self: 'BasicInterpreter', frequency: float, duration: float) -> None:
        """Helper to play a single note.

        Args:
            frequency: Note frequency in Hz.
            duration: Note duration in seconds.
        """
        try:
            if frequency <= 0 or duration <= 0:
                return

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
            pass  # Silently fail if audio not available
