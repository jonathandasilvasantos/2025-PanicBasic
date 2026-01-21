#!/usr/bin/env python3
"""Run a BASIC test file and show its output.

This script runs BASIC programs and displays LPRINT output to console.
Use LPRINT instead of PRINT in your test files to see console output.
"""
import os
import sys

os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
pygame.init()
pygame.font.init()
pygame.display.set_mode((800, 600))
font = pygame.font.Font(None, 16)

from interpreter import BasicInterpreter

MAX_STEPS = 50000

def run_test(bas_file):
    """Run a BASIC test file - LPRINT output goes to console."""
    print(f"=== Running: {bas_file} ===\n")

    interp = BasicInterpreter(font, 800, 600)

    # Read file
    with open(bas_file, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    interp.reset(lines, source_path=bas_file)

    # Run the program - LPRINT statements will output to console
    for step in range(MAX_STEPS):
        if not interp.running:
            break
        interp.step()

    print(f"\n=== Completed after {step} steps ===")
    return 0

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: run_bas_test.py <bas_file>")
        sys.exit(1)
    sys.exit(run_test(sys.argv[1]))
