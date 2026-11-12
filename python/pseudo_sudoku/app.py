"""Windows-ready Tkinter desktop app (and headless CLI fallback) for Pseudo Sudoku."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import sys
import time
from typing import Dict, List, Optional, Set, Tuple

from .engine import Hint, SolveStep, clone_board, find_logical_hint, format_board, solve, solve_steps
from .generator import DIFFICULTY_TARGET_CLUES, generate_puzzle


@dataclass
class MoveRecord:
    row: int
    col: int
    prev_val: int
    prev_notes: Set[int]


def run_cli(difficulty: str = "medium", seed: Optional[int] = None) -> int:
    generated = generate_puzzle(difficulty=difficulty, seed=seed)
    print(f"Pseudo Sudoku ({difficulty.upper()}, {generated.clues} clues, unique solution)\n")
    print(format_board(generated.puzzle))
    hint = find_logical_hint(generated.puzzle, generated.solution)
    if hint:
        print(f"\nFirst logical hint [{hint.strategy}]: {hint.reason}")
    t0 = time.perf_counter()
    solved = solve(generated.puzzle)
    dt_ms = (time.perf_counter() - t0) * 1000
    print(f"\nSolved in {dt_ms:.2f} ms:\n")
    if solved is not None:
        print(format_board(solved))
    return 0


def run_gui() -> int:
    try:
        import tkinter as tk
        from tkinter import messagebox
    except ImportError as exc:
        print(
            "Tkinter is not available in this Python environment.\n"
            "On Windows/macOS, use the official Python installer (includes Tkinter).\n"
            "Run with --cli for terminal mode.",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc

    CELL = 56
    GRID = CELL * 9

    BG = "#FAF6F0"
    CARD = "#FFFFFF"
    BORDER = "#CBD5E1"
    BOX_BORDER = "#334155"
    GIVEN_FG = "#0F172A"
    USER_FG = "#059669"
    PEER_BG = "#EEF6F0"
    SAME_BG = "#D1FAE5"
    SEL_BG = "#A7F3D0"
    ERR_BG = "#FECDD3"
    TRY_BG = "#FEF3C7"
    PLACE_BG = "#D1FAE5"
    BACKTRACK_BG = "#FFE4E6"
    NOTE_FG = "#64748B"

    class SudokuApp:
        def __init__(self, root: tk.Tk) -> None:
            self.root = root
            self.root.title("Pseudo Sudoku — Python Desktop & MRV Visualizer")
            self.root.configure(bg=BG)
            self.root.resizable(False, False)

            self.difficulty = "medium"
            self.puzzle = [[0] * 9 for _ in range(9)]
            self.solution = [[0] * 9 for _ in range(9)]
            self.board = [[0] * 9 for _ in range(9)]
            self.notes: List[List[Set[int]]] = [[set() for _ in range(9)] for _ in range(9)]
            self.history: List[MoveRecord] = []
            self.selected: Optional[Tuple[int, int]] = (4, 4)
            self.mistakes = 0
            self.max_mistakes = 3
            self.notes_mode = False
            self.elapsed_sec = 0
            self.timer_job: Optional[str] = None
            self.flash_cell: Optional[Tuple[int, int]] = None

            # Visualizer state
            self.vis_running = False
            self.vis_paused = False
            self.vis_gen = None
            self.vis_job: Optional[str] = None
            self.vis_nodes = 0
            self.vis_backtracks = 0
            self.vis_cell_state: Dict[Tuple[int, int], str] = {}

            self._build_ui()
            self._bind_keys()
            self.new_game("medium")

        def _build_ui(self) -> None:
            header = tk.Frame(self.root, bg=BG, padx=16, pady=10)
            header.pack(fill="x")

            tk.Label(
                header,
                text="Pseudo Sudoku",
                font=("Segoe UI", 16, "bold"),
                bg=BG,
                fg="#0F172A",
            ).pack(side="left")

            self.status_lbl = tk.Label(
                header,
                text="Select a cell or press Watch Solve",
                font=("Segoe UI", 10),
                bg=BG,
                fg="#475569",
            )
            self.status_lbl.pack(side="right")

            body = tk.Frame(self.root, bg=BG, padx=16, pady=4)
            body.pack()

            # Left: Board + Controls
            left = tk.Frame(body, bg=CARD, bd=1, relief="solid", padx=12, pady=12)
            left.pack(side="left", padx=(0, 14))

            info_bar = tk.Frame(left, bg=CARD)
            info_bar.pack(fill="x", pady=(0, 8))
            self.diff_lbl = tk.Label(info_bar, text="MEDIUM", font=("Segoe UI", 9, "bold"), bg="#ECFDF5", fg="#065F46", padx=8, pady=2)
            self.diff_lbl.pack(side="left")
            self.timer_lbl = tk.Label(info_bar, text="00:00", font=("Consolas", 11, "bold"), bg=CARD, fg="#334155")
            self.timer_lbl.pack(side="right")
            self.mistake_lbl = tk.Label(info_bar, text="Mistakes: 0 / 3", font=("Segoe UI", 9, "bold"), bg=CARD, fg="#E11D48", padx=12)
            self.mistake_lbl.pack(side="right")

            self.canvas = tk.Canvas(left, width=GRID + 2, height=GRID + 2, bg=CARD, highlightthickness=0)
            self.canvas.pack()
            self.canvas.bind("<Button-1>", self._on_canvas_click)

            # Action row
            actions = tk.Frame(left, bg=CARD, pady=8)
            actions.pack(fill="x")
            self.undo_btn = tk.Button(actions, text="Undo", command=self.undo, width=8, bg="#F1F5F9", relief="flat")
            self.undo_btn.pack(side="left", padx=2)
            self.erase_btn = tk.Button(actions, text="Erase", command=self.erase, width=8, bg="#F1F5F9", relief="flat")
            self.erase_btn.pack(side="left", padx=2)
            self.notes_btn = tk.Button(actions, text="Notes: OFF", command=self.toggle_notes, width=10, bg="#F1F5F9", relief="flat")
            self.notes_btn.pack(side="left", padx=2)
            self.hint_btn = tk.Button(actions, text="Logical Hint", command=self.give_hint, width=12, bg="#FEF3C7", fg="#92400E", relief="flat")
            self.hint_btn.pack(side="right", padx=2)

            # Number pad
            pad = tk.Frame(left, bg=CARD)
            pad.pack(fill="x", pady=(2, 0))
            for n in range(1, 10):
                btn = tk.Button(
                    pad,
                    text=str(n),
                    font=("Segoe UI", 11, "bold"),
                    width=3,
                    bg="#F8FAFC",
                    fg="#0F172A",
                    relief="groove",
                    command=lambda d=n: self.enter_digit(d),
                )
                btn.pack(side="left", expand=True, fill="x", padx=2)

            # Right: Telemetry, Visualizer & New Puzzle
            right = tk.Frame(body, bg=BG, width=250)
            right.pack(side="left", fill="y")

            vis_card = tk.Frame(right, bg=CARD, bd=1, relief="solid", padx=12, pady=12)
            vis_card.pack(fill="x", pady=(0, 12))
            tk.Label(vis_card, text="MRV Backtracking Visualizer", font=("Segoe UI", 10, "bold"), bg=CARD, fg="#0F172A").pack(anchor="w")

            stats = tk.Frame(vis_card, bg=CARD, pady=6)
            stats.pack(fill="x")
            self.nodes_lbl = tk.Label(stats, text="Nodes: 0", font=("Consolas", 10), bg=CARD, fg="#334155")
            self.nodes_lbl.pack(anchor="w")
            self.backtracks_lbl = tk.Label(stats, text="Backtracks: 0", font=("Consolas", 10), bg=CARD, fg="#D97706")
            self.backtracks_lbl.pack(anchor="w")
            self.solved_lbl = tk.Label(stats, text="Filled: 0 / 81", font=("Consolas", 10), bg=CARD, fg="#059669")
            self.solved_lbl.pack(anchor="w")

            speed_row = tk.Frame(vis_card, bg=CARD, pady=4)
            speed_row.pack(fill="x")
            tk.Label(speed_row, text="Speed:", font=("Segoe UI", 9), bg=CARD, fg="#475569").pack(side="left")
            self.speed_var = tk.StringVar(value="Normal (40ms)")
            self.speed_map = {
                "Gentle (160ms)": 160,
                "Normal (40ms)": 40,
                "Swift (8ms)": 8,
                "Instant": 0,
            }
            tk.OptionMenu(speed_row, self.speed_var, *self.speed_map.keys()).pack(side="right")

            vis_btns = tk.Frame(vis_card, bg=CARD, pady=4)
            vis_btns.pack(fill="x")
            self.watch_btn = tk.Button(vis_btns, text="Watch Solve", command=self.start_visualizer, bg="#059669", fg="white", font=("Segoe UI", 9, "bold"), relief="flat")
            self.watch_btn.pack(fill="x", pady=2)
            sub_btns = tk.Frame(vis_btns, bg=CARD)
            sub_btns.pack(fill="x")
            self.pause_btn = tk.Button(sub_btns, text="Pause", command=self.pause_visualizer, state="disabled", bg="#F1F5F9", relief="flat")
            self.pause_btn.pack(side="left", expand=True, fill="x", padx=(0, 2))
            self.step_btn = tk.Button(sub_btns, text="Step", command=self.step_visualizer, bg="#F1F5F9", relief="flat")
            self.step_btn.pack(side="left", expand=True, fill="x", padx=(2, 0))

            puzzle_card = tk.Frame(right, bg=CARD, bd=1, relief="solid", padx=12, pady=12)
            puzzle_card.pack(fill="x")
            tk.Label(puzzle_card, text="New Unique Puzzle", font=("Segoe UI", 10, "bold"), bg=CARD, fg="#0F172A").pack(anchor="w", pady=(0, 6))
            for diff in DIFFICULTY_TARGET_CLUES:
                tk.Button(
                    puzzle_card,
                    text=diff.capitalize(),
                    command=lambda d=diff: self.new_game(d),
                    bg="#F8FAFC",
                    relief="groove",
                    pady=3,
                ).pack(fill="x", pady=2)

            tk.Button(puzzle_card, text="Restart Current", command=self.restart_current, bg="#F1F5F9", relief="flat", pady=3).pack(fill="x", pady=(8, 0))

        def _bind_keys(self) -> None:
            for d in range(1, 10):
                self.root.bind(str(d), lambda e, val=d: self.enter_digit(val))
            self.root.bind("<BackSpace>", lambda e: self.erase())
            self.root.bind("<Delete>", lambda e: self.erase())
            self.root.bind("<Control-z>", lambda e: self.undo())
            self.root.bind("n", lambda e: self.toggle_notes())
            self.root.bind("h", lambda e: self.give_hint())
            self.root.bind("<Up>", lambda e: self._move_sel(-1, 0))
            self.root.bind("<Down>", lambda e: self._move_sel(1, 0))
            self.root.bind("<Left>", lambda e: self._move_sel(0, -1))
            self.root.bind("<Right>", lambda e: self._move_sel(0, 1))

        def _move_sel(self, dr: int, dc: int) -> None:
            if self.vis_running:
                return
            r, c = self.selected or (4, 4)
            self.selected = (max(0, min(8, r + dr)), max(0, min(8, c + dc)))
            self.draw_board()

        def new_game(self, difficulty: str) -> None:
            self._stop_visualizer()
            self.difficulty = difficulty
            gen = generate_puzzle(difficulty)
            self.puzzle = gen.puzzle
            self.solution = gen.solution
            self.board = clone_board(self.puzzle)
            self.notes = [[set() for _ in range(9)] for _ in range(9)]
            self.history.clear()
            self.mistakes = 0
            self.selected = (4, 4)
            self.vis_nodes = 0
            self.vis_backtracks = 0
            self.vis_cell_state.clear()

            self.diff_lbl.config(text=f"{difficulty.upper()} ({gen.clues} clues)")
            self.mistake_lbl.config(text=f"Mistakes: 0 / {self.max_mistakes}")
            self.nodes_lbl.config(text="Nodes: 0")
            self.backtracks_lbl.config(text="Backtracks: 0")
            self.status_lbl.config(text="Unique-solution puzzle ready")
            self._start_timer()
            self.draw_board()

        def restart_current(self) -> None:
            self._stop_visualizer()
            self.board = clone_board(self.puzzle)
            self.notes = [[set() for _ in range(9)] for _ in range(9)]
            self.history.clear()
            self.mistakes = 0
            self.vis_cell_state.clear()
            self.mistake_lbl.config(text=f"Mistakes: 0 / {self.max_mistakes}")
            self.status_lbl.config(text="Board reset")
            self._start_timer()
            self.draw_board()

        def _start_timer(self) -> None:
            if self.timer_job is not None:
                self.root.after_cancel(self.timer_job)
            self.elapsed_sec = 0
            self.timer_lbl.config(text="00:00")
            self._tick_timer()

        def _tick_timer(self) -> None:
            m, s = divmod(self.elapsed_sec, 60)
            self.timer_lbl.config(text=f"{m:02d}:{s:02d}")
            self.elapsed_sec += 1
            self.timer_job = self.root.after(1000, self._tick_timer)

        def _stop_timer(self) -> None:
            if self.timer_job is not None:
                self.root.after_cancel(self.timer_job)
                self.timer_job = None

        def _on_canvas_click(self, event: tk.Event) -> None:
            if self.vis_running:
                return
            c = min(8, max(0, event.x // CELL))
            r = min(8, max(0, event.y // CELL))
            self.selected = (r, c)
            self.draw_board()

        def toggle_notes(self) -> None:
            self.notes_mode = not self.notes_mode
            self.notes_btn.config(
                text=f"Notes: {'ON' if self.notes_mode else 'OFF'}",
                bg="#D1FAE5" if self.notes_mode else "#F1F5F9",
            )

        def enter_digit(self, digit: int) -> None:
            if self.vis_running or self.selected is None:
                return
            r, c = self.selected
            if self.puzzle[r][c] != 0:
                return

            if self.notes_mode:
                if digit in self.notes[r][c]:
                    self.notes[r][c].remove(digit)
                else:
                    self.notes[r][c].add(digit)
                self.draw_board()
                return

            self.history.append(MoveRecord(r, c, self.board[r][c], set(self.notes[r][c])))
            self.notes[r][c].clear()
            self.board[r][c] = digit

            if digit != self.solution[r][c]:
                self.mistakes += 1
                self.mistake_lbl.config(text=f"Mistakes: {self.mistakes} / {self.max_mistakes}")
                self.flash_cell = (r, c)
                self.root.after(600, self._clear_flash)
                self.status_lbl.config(text=f"Conflict at R{r+1}C{c+1}")
                if self.mistakes >= self.max_mistakes:
                    self._stop_timer()
                    self.draw_board()
                    messagebox.showinfo("Game Over", "Reached 3 mistakes. Starting a fresh puzzle.")
                    self.new_game(self.difficulty)
                    return
            else:
                self.status_lbl.config(text=f"Placed {digit} at R{r+1}C{c+1}")
                if self.board == self.solution:
                    self._stop_timer()
                    self.draw_board()
                    messagebox.showinfo("Solved!", f"Completed {self.difficulty.upper()} in {self.timer_lbl.cget('text')}!")
                    return

            self.draw_board()

        def _clear_flash(self) -> None:
            self.flash_cell = None
            self.draw_board()

        def erase(self) -> None:
            if self.vis_running or self.selected is None:
                return
            r, c = self.selected
            if self.puzzle[r][c] != 0:
                return
            if self.board[r][c] != 0 or self.notes[r][c]:
                self.history.append(MoveRecord(r, c, self.board[r][c], set(self.notes[r][c])))
                self.board[r][c] = 0
                self.notes[r][c].clear()
                self.draw_board()

        def undo(self) -> None:
            if self.vis_running or not self.history:
                return
            rec = self.history.pop()
            self.board[rec.row][rec.col] = rec.prev_val
            self.notes[rec.row][rec.col] = rec.prev_notes
            self.selected = (rec.row, rec.col)
            self.draw_board()

        def give_hint(self) -> None:
            if self.vis_running:
                return
            hint: Optional[Hint] = find_logical_hint(self.board, self.solution)
            if hint is None:
                return
            self.history.append(MoveRecord(hint.row, hint.col, self.board[hint.row][hint.col], set(self.notes[hint.row][hint.col])))
            self.board[hint.row][hint.col] = hint.value
            self.notes[hint.row][hint.col].clear()
            self.selected = (hint.row, hint.col)
            self.status_lbl.config(text=f"[{hint.strategy}] {hint.reason}")
            self.draw_board()

        # --- Visualizer ---
        def start_visualizer(self) -> None:
            if self.vis_running and not self.vis_paused:
                return
            if self.vis_paused:
                self.vis_paused = False
                self.pause_btn.config(state="normal")
                self._vis_loop()
                return

            self.board = clone_board(self.puzzle)
            self.notes = [[set() for _ in range(9)] for _ in range(9)]
            self.vis_cell_state.clear()
            self.vis_nodes = 0
            self.vis_backtracks = 0
            self.vis_running = True
            self.vis_paused = False
            self.vis_gen = solve_steps(self.board)
            self.pause_btn.config(state="normal")
            self.status_lbl.config(text="Running MRV backtracking visualizer...")
            self._vis_loop()

        def pause_visualizer(self) -> None:
            if not self.vis_running:
                return
            self.vis_paused = True
            if self.vis_job is not None:
                self.root.after_cancel(self.vis_job)
                self.vis_job = None
            self.pause_btn.config(state="disabled")
            self.status_lbl.config(text="Visualizer paused")

        def step_visualizer(self) -> None:
            if not self.vis_running:
                self.start_visualizer()
                self.pause_visualizer()
                return
            self.pause_visualizer()
            self._vis_step()

        def _stop_visualizer(self) -> None:
            self.vis_running = False
            self.vis_paused = False
            self.vis_gen = None
            if self.vis_job is not None:
                self.root.after_cancel(self.vis_job)
                self.vis_job = None
            self.pause_btn.config(state="disabled")

        def _vis_step(self) -> bool:
            if self.vis_gen is None:
                return False
            try:
                ev: SolveStep = next(self.vis_gen)
            except StopIteration:
                self._finish_visualizer()
                return False

            if ev.kind == "complete":
                self._finish_visualizer()
                return False

            self.vis_nodes += 1
            if ev.kind == "backtrack":
                self.vis_backtracks += 1
            self.vis_cell_state[(ev.row, ev.col)] = ev.kind
            self.nodes_lbl.config(text=f"Nodes: {self.vis_nodes}")
            self.backtracks_lbl.config(text=f"Backtracks: {self.vis_backtracks}")
            self.draw_board()
            return True

        def _vis_loop(self) -> None:
            if not self.vis_running or self.vis_paused:
                return
            delay = self.speed_map.get(self.speed_var.get(), 40)
            if delay == 0:
                while self._vis_step():
                    pass
                return
            if self._vis_step():
                self.vis_job = self.root.after(delay, self._vis_loop)

        def _finish_visualizer(self) -> None:
            self._stop_visualizer()
            self._stop_timer()
            self.vis_cell_state.clear()
            self.status_lbl.config(text=f"Solved in {self.vis_nodes} nodes ({self.vis_backtracks} backtracks)")
            self.draw_board()

        def draw_board(self) -> None:
            self.canvas.delete("all")
            sel_val = 0
            if self.selected is not None:
                sr, sc = self.selected
                sel_val = self.board[sr][sc]

            filled = 0
            for r in range(9):
                for c in range(9):
                    x0, y0 = c * CELL + 1, r * CELL + 1
                    x1, y1 = x0 + CELL, y0 + CELL
                    val = self.board[r][c]
                    if val != 0:
                        filled += 1

                    bg = CARD
                    if self.vis_running and (r, c) in self.vis_cell_state:
                        st = self.vis_cell_state[(r, c)]
                        bg = TRY_BG if st == "try" else (PLACE_BG if st == "place" else BACKTRACK_BG)
                    elif self.flash_cell == (r, c):
                        bg = ERR_BG
                    elif self.selected == (r, c):
                        bg = SEL_BG
                    elif self.selected is not None:
                        sr, sc = self.selected
                        if sel_val != 0 and val == sel_val:
                            bg = SAME_BG
                        elif r == sr or c == sc or (r // 3 == sr // 3 and c // 3 == sc // 3):
                            bg = PEER_BG

                    self.canvas.create_rectangle(x0, y0, x1, y1, fill=bg, outline=BORDER, width=1)

                    if val != 0:
                        is_given = self.puzzle[r][c] != 0
                        self.canvas.create_text(
                            x0 + CELL / 2,
                            y0 + CELL / 2,
                            text=str(val),
                            font=("Segoe UI", 18, "bold" if is_given else "normal"),
                            fill=GIVEN_FG if is_given else USER_FG,
                        )
                    elif self.notes[r][c]:
                        for n in self.notes[r][c]:
                            nr, nc = divmod(n - 1, 3)
                            nx = x0 + (nc + 0.5) * (CELL / 3)
                            ny = y0 + (nr + 0.5) * (CELL / 3)
                            self.canvas.create_text(nx, ny, text=str(n), font=("Segoe UI", 8), fill=NOTE_FG)

            # Crisp 3x3 box borders
            for i in range(0, 10, 3):
                pos = i * CELL + 1
                self.canvas.create_line(1, pos, GRID + 1, pos, fill=BOX_BORDER, width=2)
                self.canvas.create_line(pos, 1, pos, GRID + 1, fill=BOX_BORDER, width=2)

            self.solved_lbl.config(text=f"Filled: {filled} / 81")

    root = tk.Tk()
    SudokuApp(root)
    root.mainloop()
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Pseudo Sudoku — Python Desktop & CLI")
    parser.add_argument("--cli", action="store_true", help="Run in terminal mode instead of Tkinter GUI")
    parser.add_argument("--difficulty", choices=list(DIFFICULTY_TARGET_CLUES), default="medium")
    parser.add_argument("--seed", type=int, default=None, help="Optional RNG seed for CLI mode")
    args = parser.parse_args(argv)

    if args.cli:
        return run_cli(difficulty=args.difficulty, seed=args.seed)
    return run_gui()


if __name__ == "__main__":
    raise SystemExit(main())
