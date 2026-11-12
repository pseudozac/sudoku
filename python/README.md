# Pseudo Sudoku — Python Desktop Edition

A zero-dependency Python Sudoku game, command-line solver, and real-time Minimum Remaining Values (MRV) backtracking visualizer. Built using the Python standard library with a native `tkinter` desktop GUI.

---

## Key Highlights

- **Zero Third-Party Dependencies:** Runs on any standard Python 3.8+ installation using built-in modules (`tkinter`, `dataclasses`, `time`, `random`, `argparse`).
- **MRV Bitmask Solver (`engine.py`):** Uses bitwise digit masks (rows, columns, 3×3 boxes) and the Minimum Remaining Values (MRV / most constrained variable first) heuristic to solve standard puzzles in under **0.5 milliseconds** and expert puzzles in under **2 milliseconds**.
- **Unique Puzzle Generator (`generator.py`):** Generates puzzles with guaranteed single unique solutions across 4 difficulty tiers:
  - **Easy:** ~36–40 clues
  - **Medium:** ~30–34 clues
  - **Hard:** ~26–29 clues
  - **Expert:** ~22–25 clues
- **Logical Hint Engine:** Detects and explains logical deductions (e.g. *Naked Singles* and *Hidden Singles*) with human-readable reasoning instead of just guessing digits.
- **Interactive Visualizer:** Watch the MRV backtracking solver search cell states with live node counters, backtrack counters, filled counters, and four speed presets.
- **Windows Executable Ready:** Bundled with a one-click `build_windows.bat` to compile a standalone, windowed `dist/PseudoSudoku.exe` via PyInstaller.

---

## Directory Structure

```
python/
├── pseudo_sudoku/
│   ├── __init__.py         # Package exports
│   ├── __main__.py         # python -m pseudo_sudoku entry point
│   ├── app.py              # Tkinter GUI desktop interface and CLI runner
│   ├── engine.py           # Bitmask solver, MRV heuristic, hints, and step generator
│   └── generator.py        # Unique puzzle generator with difficulty scaling
├── tests/
│   ├── __init__.py
│   └── test_sudoku.py      # Complete unit test suite (7 tests)
├── build_windows.bat       # Windows PyInstaller build script
├── main.py                 # Direct application launcher
├── pyproject.toml          # PEP 517/621 packaging metadata
└── README.md               # This documentation
```

---

## How to Run

### 1. Launch the Desktop GUI

From within the `python/` directory:

```bash
python main.py
```

Or from the repository root:

```bash
python python/main.py
```

### 2. Run in Terminal / CLI Mode (Headless)

Generate a puzzle, print ASCII board, show the first logical hint, and solve in milliseconds:

```bash
# Default medium difficulty
python main.py --cli

# Specify difficulty and reproducible seed
python main.py --cli --difficulty expert --seed 42
```

CLI arguments:
- `--cli`: Run in terminal mode instead of Tkinter GUI.
- `--difficulty {easy,medium,hard,expert}`: Set puzzle difficulty (default: `medium`).
- `--seed SEED`: Optional integer RNG seed for deterministic puzzle generation.

### 3. Optional: Install as a Python Package

```bash
pip install -e .
```

Once installed, launch from any terminal via:

```bash
pseudo-sudoku
# or headless CLI:
pseudo-sudoku --cli --difficulty hard
```

---

## Running Unit Tests

The test suite covers board validation, step-by-step solving, uniqueness verification, logical hints, hard board benchmarks, and formatting:

```bash
# From within the python/ folder:
python -m unittest discover -s tests -v

# Or from repository root:
python -m unittest discover -s python/tests -t python -v
```

---

## Building a Standalone Windows `.exe`

To build an independent Windows executable that runs without requiring Python installed:

1. Double-click `build_windows.bat`, or run in PowerShell:
   ```cmd
   build_windows.bat
   ```
2. The compiled binary will be placed at:
   ```
   dist\PseudoSudoku.exe
   ```
