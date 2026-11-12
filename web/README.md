# Pseudo Sudoku — Web Edition

A tactile, cozy browser-based Sudoku puzzle game and real-time backtracking visualizer built as a single, self-contained web app.

**Live Demo:** [https://pseudo-sudoku.vercel.app/](https://pseudo-sudoku.vercel.app/)

---

## Features

- **Cozy & Tactile UI:** Warm Japanese-inspired aesthetic with Plus Jakarta Sans and Kiwi Maru typography, custom icons, and fluid animations.
- **Four Difficulty Levels:**
  - **Easy:** 34 cells removed (~47 clues remaining)
  - **Medium:** 42 cells removed (~39 clues remaining)
  - **Hard:** 50 cells removed (~31 clues remaining)
  - **Expert:** 56 cells removed (~25 clues remaining)
- **Player Tools:**
  - **Pencil Notes:** Jot down candidate digits per cell.
  - **Mistake Limit:** 3-strike threshold with live mistake indicators.
  - **Undo Stack:** Reverse past moves (`Ctrl+Z` / `Cmd+Z`).
  - **Timer:** Tracks puzzle solving duration.
  - **Logical Hints:** Reveals cell entries when stuck.
- **Backtracking Visualizer:**
  - Watch the recursive solver test digits, encounter conflicts, and backtrack.
  - Live counters for **Steps**, **Backtracks**, **Cells Solved**, and **Elapsed Time**.
  - Interactive playback: **Solve**, **Pause**, and step-by-step **Step** button.
  - Four speed presets: Gentle (200 ms), Normal (50 ms), Swift (12 ms), or Instant Solve.
- **Audio & Sound Effects:**
  - Relaxing synthesized ambient melody.
  - Tactile pop and tile sound effects for cell placement, toggled with the **Melody** button.

---

## Keyboard Controls

| Key | Action |
| --- | --- |
| `1`–`9` | Enter digit in selected cell (or toggle note in pencil mode) |
| `Backspace` / `Delete` | Clear selected cell |
| `Arrow Keys` | Move grid selection |
| `Ctrl + Z` / `Cmd + Z` | Undo last move |
| `Space` | Pause / resume visualizer |

*Keyboard input is temporarily locked while the visualizer is actively running.*

---

## Running Locally

`index.html` is a self-contained file (Tailwind CSS and Google Fonts are loaded via CDN):

```bash
# Option 1: Open directly in your browser
start web/index.html   # Windows
open web/index.html    # macOS
xdg-open web/index.html # Linux

# Option 2: Serve using Python's built-in HTTP server
python -m http.server 8000
# Then navigate to http://localhost:8000/web/
```
