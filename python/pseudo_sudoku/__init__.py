"""Pseudo Sudoku — Python engine & Windows-ready desktop app."""

from .engine import Hint, SolveStep, count_solutions, find_logical_hint, format_board, solve, solve_steps, validate_board
from .generator import GeneratedPuzzle, generate_puzzle

__all__ = [
    "GeneratedPuzzle",
    "Hint",
    "SolveStep",
    "count_solutions",
    "find_logical_hint",
    "format_board",
    "generate_puzzle",
    "solve",
    "solve_steps",
    "validate_board",
]
