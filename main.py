#!/usr/bin/env python3
import sys
import argparse
from editor import run_editor
from interpreter import run_interpreter

def main():
    parser = argparse.ArgumentParser(
        description="Merged App: Code Wizard, Run & Console\n"
                    "Without any option the editor is shown. Use --run <file> to run a BASIC file directly."
    )
    parser.add_argument("--run", action="store_true", help="Run BASIC interpreter directly (without editor).")
    parser.add_argument("file", nargs="?", help="File to load (for the editor or interpreter).")
    args = parser.parse_args()

    if args.run:
        if not args.file:
            print("Error: You must supply a BASIC file to run (e.g. pong.bas).")
            sys.exit(1)
        run_interpreter(args.file)
    else:
        run_editor(args.file)

if __name__ == '__main__':
    main()

