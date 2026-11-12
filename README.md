# Pseudo Sudoku

A logic-driven Sudoku game, puzzle generator, and backtracking solver visualizer available in two distinct editions: a **browser-based Web App** and a native **Python Desktop & CLI Suite**.

Play puzzles yourself, request human-readable logical hints, or toggle the solver to watch backtracking algorithms work through boards in real time.

- **Web Live Demo:** [https://pseudo-sudoku.vercel.app/](https://pseudo-sudoku.vercel.app/)
- **Repository Structure:** The codebase separates the **Web Edition** (`web/`) from the **Python Desktop & Engine** (`python/`), with the original prototype preserved in `bin/`.

---

## Editions Overview

| Feature | Web Edition (`web/`) | Python Desktop & CLI (`python/`) | Original Prototype (`bin/`) |
| :--- | :--- | :--- | :--- |
| **Interface** | Responsive Web App (HTML/Tailwind/JS) | Native Tkinter Desktop GUI + Headless CLI | Terminal output |
| **Dependencies** | None (CDN for Tailwind & Google Fonts) | Zero dependencies (Python 3.8+ standard library) | None (Standard Python 3) |
| **Solver Algorithm** | Recursive backtracking (left-to-right) | **MRV Bitmask Backtracking** (fastest-first) | Simple recursive backtracking |
| **Visualizer** | Animated grid with live telemetry & speed presets | Step-by-step visualizer with node/backtrack metrics | None (instant solve) |
| **Puzzle Generator** | Random cell removal across 4 difficulties | **Guaranteed unique** puzzles across 4 difficulties | Single hard-coded board |
| **Hint System** | Direct cell reveal | **Logical hints** (Naked Singles & Hidden Singles) | None |
| **Audio** | Tactile sound effects & relaxing melody | Silent / native desktop | None |
| **Platform Target** | Any modern browser / mobile browser | Windows, macOS, Linux (plus standalone `.exe`) | Python CLI |

---

## Directory Structure

```
sudoku/
├── .gitignore             # Git ignore rules for Python, caches, and build artifacts
├── index.html             # Web entry point & redirect to web/index.html
├── vercel.json            # Vercel deployment configuration & routing
├── README.md              # Project documentation (this file)
│
├── web/                   # Web Edition (Browser)
│   ├── index.html         # Complete self-contained web game & visualizer
│   └── README.md          # Web documentation & controls
│
├── python/                # Python Desktop Edition & Solver Engine
│   ├── pseudo_sudoku/
│   │   ├── __init__.py    # Package exports
│   │   ├── __main__.py    # python -m pseudo_sudoku entry point
│   │   ├── app.py         # Tkinter desktop GUI & CLI runner
│   │   ├── engine.py      # Bitmask + MRV solver, step generator, and hints
│   │   └── generator.py   # Unique puzzle generator across 4 difficulties
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_sudoku.py # Unit test suite (7 tests)
│   ├── build_windows.bat  # Standalone Windows .exe builder (PyInstaller)
│   ├── main.py            # Main application launcher
│   ├── pyproject.toml     # Packaging metadata (pip install -e .)
│   └── README.md          # Python documentation & build instructions
│
└── bin/                   # Legacy Prototype
    └── primaryCode.py     # The original 78-line backtracking script
```

---

## 1. Web Edition

Play directly in your browser or run locally with zero installation.

- **Online Demo:** [https://pseudo-sudoku.vercel.app/](https://pseudo-sudoku.vercel.app/)
- **Local Run:** Double-click `web/index.html` or serve via:
  ```bash
  python -m http.server 8000
  # Open http://localhost:8000/web/
  ```

### Web Highlights
- **Tactile Cozy UI:** Japanese typography accents, soothing palette, custom icons.
- **Difficulty Tiers:** Easy, Medium, Hard, and Expert.
- **Interactive Tools:** Pencil notes, 3-strike mistake counter, undo stack (`Ctrl+Z`), timer.
- **Backtracking Visualizer:**
  - Watch the solver try digits, encounter conflicts, and backtrack.
  - Live counters for steps, backtracks, filled cells, and elapsed time.
  - Controls: **Solve**, **Pause**, and single-move **Step**.
  - Four speeds: Gentle (200 ms), Normal (50 ms), Swift (12 ms), and Instant.
- **Sound Effects & Music:** Ambient background melody and tile click sounds (toggle via the Melody button).

---

## 2. Python Desktop Edition

A full-featured native desktop application, command-line solver, and algorithmic engine built entirely with Python standard libraries (`tkinter` for GUI).

### Quickstart

#### Launch the Tkinter Desktop GUI:
```bash
# From within the python/ folder:
cd python
python main.py

# Or directly from the repository root:
python python/main.py
```

#### Run in Headless CLI Mode:
Generate a board, show the first logical deduction hint, and benchmark solving time in milliseconds:
```bash
# Default medium puzzle
python python/main.py --cli

# Specify difficulty (easy, medium, hard, expert) and reproducible seed
python python/main.py --cli --difficulty hard --seed 1234
```

#### Run the Unit Test Suite:
```bash
# Run 7 automated tests covering validation, MRV solver, uniqueness, hints:
python -m unittest discover -s python/tests -t python -v
```

#### Build Standalone Windows Executable:
A pre-configured batch script packages the application into a single `.exe` using PyInstaller:
1. Double-click `python/build_windows.bat` or run:
   ```cmd
   cd python
   build_windows.bat
   ```
2. The resulting binary will be located in `python/dist/PseudoSudoku.exe`.

---

## 3. Original Prototype Script

The repository originated from a lightweight 78-line terminal backtracking solver. It solves a hard-coded matrix and prints the before-and-after board:

```bash
python bin/primaryCode.py
```

---

## How the Solvers Work

### Standard Backtracking (Web Edition & Prototype)
1. Locates the next empty cell (left-to-right, top-to-bottom).
2. Tests digits 1 through 9.
3. Checks if the digit is valid in the current row, column, and 3×3 subgrid.
4. If valid, recursively proceeds to the next empty cell.
5. If a dead end is encountered, erases the candidate (backtracks) and tries the next number.

### MRV Bitmask Backtracking (Python Edition)
The Python engine implements an optimized constraint satisfaction solver:
- **Bitmask State Tracking:** Rows, columns, and 3×3 boxes are represented as 9-bit integers. Checking if a digit is valid or placing a digit requires only bitwise operations (`&`, `|`, `^`), which executes in nanoseconds.
- **Minimum Remaining Values (MRV):** Instead of scanning cells in reading order, the solver always selects the cell with the **fewest possible candidates**. If a cell has only 1 legal candidate, it is solved immediately. This prunes exponential branches and solves even diabolical boards (e.g. Arto Inkala's puzzle) in less than 2 milliseconds.
- **Uniqueness Verification:** The puzzle generator uses `count_solutions(board, limit=2)` with early termination to verify that generated puzzles possess exactly one valid solution.
- **Logical Deductions:** The hint engine analyzes the board state for **Naked Singles** (cells where all other 8 digits are blocked) and **Hidden Singles** (digits that can only fit in one location within a row, column, or box), explaining the logical step clearly to the player.

---

## License

MIT License. Feel free to explore, modify, and build upon this project.
