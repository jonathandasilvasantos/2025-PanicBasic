# PanicBasic

PanicBasic is an experimental, retro-style BASIC environment combined with a code editor, interpreter, and console — all in one application. It is written in Python using [pygame](https://www.pygame.org/).

## Features

1. **Integrated Editor**  
   - A custom text editor with line numbering, basic editing commands (undo, redo, cut, copy, paste), and a simple drawing layer.  
   - Automatically loads a sample BASIC game (Pong) when no file is provided.  
   - Allows you to load your own `.bas` files for editing.

2. **BASIC Interpreter**  
   - A custom BASIC interpreter that supports classic commands such as `SCREEN`, `CLS`, `PRINT`, `LINE`, `CIRCLE`, `PAINT`, loops (`DO ... LOOP`, `FOR ... NEXT`), conditionals (`IF ... THEN`), and more.  
   - Supports array and two-dimensional array variables (`DIM x(10)`, `DIM y(20, 10)`).  
   - Includes special commands like `_DELAY` and `SLEEP` to control timing.  
   - Allows you to run simple, retro-inspired games (like Pong or Catch the Star).

3. **Console**  
   - A basic shell-like console that can run system commands within the same pygame window.  
   - Supports command history navigation (`↑/↓` arrows), clearing the console (`clear` or `cls`), and handling of standard output and errors.

4. **Footer Bar for Mode Switching**  
   - Switch between the **Text** editor, **Run** mode (the BASIC interpreter), or the **Console** at any time by clicking on the corresponding buttons in the bottom footer bar.

5. **Direct Interpreter Run**  
   - You can bypass the editor entirely and run a `.bas` file from the command line with `--run`.


## Project Structure

```
.
├── main.py             # Entry point that merges the editor and interpreter
├── editor.py           # The text editor (with basic painting capability)
├── interpreter.py      # The BASIC interpreter logic
├── examples
│   ├── star.bas        # Example 'Catch the Star' game
│   └── pong.bas        # Example Pong game
└── README.md           # This file
```

### `main.py`
- **Description**: The main entry point of PanicBasic.  
- **Usage**:
  - Without arguments: Launches the integrated environment with the editor open.  
    ```bash
    ./main.py
    ```
  - With `--run <file>`: Runs a BASIC file directly in interpreter mode (without the editor).  
    ```bash
    ./main.py --run ./examples/star.bas
    ```

### `editor.py`
- **Description**: Implements a simple text editor with line numbering, a drawing surface, undo/redo, cut/copy/paste, etc.  
- **Features**:
  - **Selection & Editing**: Supports arrow keys, `Ctrl+Z`/`Ctrl+Shift+Z` (undo/redo), `Ctrl+X`/`Ctrl+C`/`Ctrl+V` (cut, copy, paste), etc.  
  - **Drawing Layer**: Left-click draws with white lines, right-click erases.  
  - **Scrolling & Resizing**: Automatically adjusts to the pygame window size.

### `interpreter.py`
- **Description**: A custom BASIC interpreter supporting a subset of classic syntax.  
- **Graphics**:
  - Uses a 320×200 software surface by default (`SCREEN 13`).  
  - Commands like `CLS`, `LINE`, `CIRCLE`, `PAINT`, `LOCATE`, `PRINT` for rendering text and shapes.  
- **Flow Control**: Supports `FOR ... NEXT`, `DO ... LOOP`, `IF ... THEN ... ELSE` (single-line or block), `SELECT CASE`, and subroutine blocks `SUB ... END SUB`.  
- **Extra Commands**:
  - `_DELAY seconds` or `SLEEP seconds`: Wait for a specified duration (non-blocking or blocking).  
  - `CONST`, `DIM`, array indexing.  
- **Run**:
  - The `run_interpreter(...)` function starts a pygame loop that executes the BASIC program until it ends or quits.

### `examples` Folder
- **`pong.bas`**: A simple Pong game demonstrating paddle movement, ball collision, scoring, and speed-up mechanics.  
- **`star.bas`**: A "Catch the Star" game where you move a basket left and right to catch falling stars.

## How to Use

1. **Install Requirements**  
   - [Python 3.x](https://www.python.org/downloads/)  
   - [pygame](https://www.pygame.org/)  
   - [pyperclip](https://pypi.org/project/pyperclip/) (for clipboard operations)

   You can install these via:
   ```bash
   pip install pygame pyperclip
   ```

2. **Run the Editor/Interpreter**  
   ```bash
   ./main.py
   ```
   - The editor will open by default.  
   - If you provided a file path as a positional argument, the editor will attempt to load that file’s contents.

3. **Run a BASIC File Directly**  
   ```bash
   ./main.py --run ./examples/pong.bas
   ```
   - This launches the interpreter in a window and runs `pong.bas`.

4. **Editor Usage**  
   - Text mode is displayed by default (or click **Text** in the bottom footer).  
   - Use arrow keys or mouse scroll to navigate.  
   - **Drawing**: Left-click to draw, right-click to erase.  
   - **Keyboard Shortcuts**:
     - `Ctrl+Z`: Undo  
     - `Ctrl+Shift+Z`: Redo  
     - `Ctrl+X`: Cut  
     - `Ctrl+C`: Copy  
     - `Ctrl+V`: Paste  
     - `Ctrl+S`: Save file  
   - To switch to **Run** or **Console**, click their buttons at the bottom.

5. **Run Mode**  
   - Click **Run** in the footer bar to execute your code.  
   - The screen will scale a 320×200 surface to fit your current window.  
   - Press <kbd>Esc</kbd> (depending on the BASIC program’s code) to exit back to the editor mode, or simply click **Text** or **Console**.

6. **Console**  
   - Click **Console** in the footer bar.  
   - Type shell commands (e.g. `ls`, `dir`, `python --version`) to see their output.  
   - Scroll with the arrow keys or clear output with `clear` or `cls`.

## Example Screenshots (Conceptual)

- **Editor Mode**  
  Displays lines of BASIC code, a drawing surface behind them, and a footer with three buttons (Text, Run, Console).

- **Run Mode**  
  Shows the 320×200 retro-style graphics scaled to your window. For example, a Pong ball and paddles.

- **Console Mode**  
  A text console at the top, your current command line at the bottom.

## Contributing

- Feel free to submit pull requests or file issues.  
- This code is primarily for educational/demonstration purposes.

## License

This project is provided under an MIT License. See [LICENSE](https://opensource.org/licenses/MIT) for details. 

Enjoy exploring retro BASIC in Python! If you have any questions or suggestions, please let us know. Have fun coding!