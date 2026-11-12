"""Unique-solution Sudoku puzzle generator."""
from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Dict, Optional

from .engine import Board, clone_board, count_solutions, solve

DIFFICULTY_TARGET_CLUES: Dict[str, int] = {
    "easy": 44,
    "medium": 36,
    "hard": 30,
    "expert": 25,
}


@dataclass(frozen=True)
class GeneratedPuzzle:
    puzzle: Board
    solution: Board
    difficulty: str
    clues: int


def generate_puzzle(difficulty: str = "medium", seed: Optional[int] = None) -> GeneratedPuzzle:
    """Generate a valid Sudoku puzzle guaranteed to have a unique solution."""
    if difficulty not in DIFFICULTY_TARGET_CLUES:
        raise ValueError(f"Unknown difficulty {difficulty!r}; choose from {list(DIFFICULTY_TARGET_CLUES)}")

    rng = random.Random(seed)
    target_clues = DIFFICULTY_TARGET_CLUES[difficulty]

    empty: Board = [[0] * 9 for _ in range(9)]
    # Seed the three diagonal 3x3 boxes randomly first for fast, varied generation
    for box_start in (0, 3, 6):
        digits = list(range(1, 10))
        rng.shuffle(digits)
        idx = 0
        for r in range(box_start, box_start + 3):
            for c in range(box_start, box_start + 3):
                empty[r][c] = digits[idx]
                idx += 1

    solution = solve(empty, rng=rng)
    if solution is None:
        raise RuntimeError("Failed to generate solved Sudoku board.")

    puzzle = clone_board(solution)
    positions = [(r, c) for r in range(9) for c in range(9)]
    rng.shuffle(positions)

    clues = 81
    for r, c in positions:
        if clues <= target_clues:
            break
        saved = puzzle[r][c]
        puzzle[r][c] = 0
        if count_solutions(puzzle, limit=2) != 1:
            puzzle[r][c] = saved
        else:
            clues -= 1

    return GeneratedPuzzle(puzzle=puzzle, solution=solution, difficulty=difficulty, clues=clues)
