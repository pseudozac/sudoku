# Pseudo Sudoku

A sudoku game that can also solve itself. You can play a puzzle yourself, or press **Solve** and watch a backtracking algorithm work through the board one cell at a time.

**Live demo:** https://pseudo-sudoku.vercel.app/

The repo has two parts:

| Path | What it is |
| --- | --- |
| `index.html` | The playable web app: a single self-contained file (HTML, CSS and JavaScript). |
| `bin/primaryCode.py` | The original command-line solver, a short Python script that solves one hard-coded board. |

## Features (web app)

- **Four difficulty levels:** Easy, Medium, Hard and Expert. Each new game generates a fresh random puzzle (34, 42, 50 or 56 cells removed from a solved board).
- **Play tools:** number pad, erase, pencil notes, undo and hints.
- **Mistake limit:** three wrong entries end the game. A timer tracks how long you take.
- **Backtracking visualizer:** watch the solver try digits, hit conflicts and backtrack. Live counters show steps, backtracks, cells solved and elapsed time.
  - Controls: Solve, Pause and Step (one move at a time).
  - Speed: Gentle (200 ms), Normal (50 ms), Swift (12 ms) or Instant Solve.
- **Sound:** an optional background melody and tile sound effects, toggled with the Melody button. Browsers only allow audio after your first click or tap.

### Keyboard shortcuts

| Key | Action |
| --- | --- |
| `1`–`9` | Enter a number in the selected cell |
| `Backspace` / `Delete` | Erase the selected cell |
| Arrow keys | Move the selection |
| `Ctrl/Cmd + Z` | Undo |

Keyboard input is disabled while the visualizer is running.

## Running it

**Web app:** open `index.html` in a browser, or use the live demo above. There is no build step and no install. It loads Tailwind CSS and Google Fonts from a CDN, so it needs an internet connection to look right.

**Python solver:** requires Python 3 and no extra packages.

```bash
python3 bin/primaryCode.py
```

It prints the starting board, then the solved board. To solve a different puzzle, edit the `board` list at the top of the file (`0` marks an empty cell).

```
7 8 0 | 4 0 0 | 1 2 0
6 0 0 | 0 7 5 | 0 0 9
...
```

## How the solver works

Both the Python script and the web app use the same backtracking approach:

1. Find the first empty cell, scanning left to right and top to bottom.
2. Try the digits 1 to 9 in that cell.
3. A digit is allowed only if it does not already appear in the cell's row, column or 3×3 box.
4. If the digit is allowed, place it and recursively solve the rest of the board.
5. If the rest of the board can't be solved, remove the digit (backtrack) and try the next one.
6. If no digit fits, return failure to the previous cell. If no empty cells remain, the puzzle is solved.

Backtracking is simple and always finds a solution if one exists, but it can take many steps on hard boards because it tries digits in order without any extra logic. The visualizer's step and backtrack counters make that cost visible.

## Known limitations

- Generated puzzles are made by deleting random cells from a solved board. The generator does not check that the result has exactly one solution, so some puzzles may have more than one valid answer.
- The Hint button fills in a random incorrect or empty cell rather than pointing to the next logical step.
