import unittest

from pseudo_sudoku.engine import (
    count_solutions,
    find_logical_hint,
    format_board,
    solve,
    solve_steps,
    validate_board,
)
from pseudo_sudoku.generator import DIFFICULTY_TARGET_CLUES, generate_puzzle


ORIGINAL_BOARD = [
    [7, 8, 0, 4, 0, 0, 1, 2, 0],
    [6, 0, 0, 0, 7, 5, 0, 0, 9],
    [0, 0, 0, 6, 0, 1, 0, 7, 8],
    [0, 0, 7, 0, 4, 0, 2, 6, 0],
    [0, 0, 1, 0, 5, 0, 9, 3, 0],
    [9, 0, 4, 0, 6, 0, 0, 0, 5],
    [0, 7, 0, 3, 0, 0, 0, 1, 2],
    [1, 2, 0, 0, 0, 7, 4, 0, 0],
    [0, 4, 9, 2, 0, 6, 0, 0, 7],
]

# Arto Inkala's famous hard Sudoku
HARD_BOARD = [
    [8, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 3, 6, 0, 0, 0, 0, 0],
    [0, 7, 0, 0, 9, 0, 2, 0, 0],
    [0, 5, 0, 0, 0, 7, 0, 0, 0],
    [0, 0, 0, 0, 4, 5, 7, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 3, 0],
    [0, 0, 1, 0, 0, 0, 0, 6, 8],
    [0, 0, 8, 5, 0, 0, 0, 1, 0],
    [0, 9, 0, 0, 0, 0, 4, 0, 0],
]


class TestSudokuEngine(unittest.TestCase):
    def test_solve_original_board(self):
        solved = solve(ORIGINAL_BOARD)
        self.assertIsNotNone(solved)
        valid, err = validate_board(solved)
        self.assertTrue(valid, err)
        self.assertEqual(sum(cell == 0 for row in solved for cell in row), 0)
        self.assertEqual(count_solutions(ORIGINAL_BOARD, limit=2), 1)

    def test_solve_hard_board_fast(self):
        solved = solve(HARD_BOARD)
        self.assertIsNotNone(solved)
        valid, err = validate_board(solved)
        self.assertTrue(valid, err)
        self.assertEqual(sum(cell == 0 for row in solved for cell in row), 0)

    def test_solve_steps_matches_solution(self):
        work = [list(r) for r in ORIGINAL_BOARD]
        steps = list(solve_steps(work))
        self.assertTrue(any(s.kind == "place" for s in steps))
        self.assertEqual(steps[-1].kind, "complete")
        self.assertEqual(work, solve(ORIGINAL_BOARD))

    def test_invalid_board_rejected(self):
        bad = [list(r) for r in ORIGINAL_BOARD]
        bad[0][2] = 7  # duplicate 7 in row 0
        valid, err = validate_board(bad)
        self.assertFalse(valid)
        self.assertIn("Duplicate", err)
        self.assertIsNone(solve(bad))
        self.assertEqual(count_solutions(bad), 0)

    def test_generate_unique_puzzles_all_difficulties(self):
        for diff, target in DIFFICULTY_TARGET_CLUES.items():
            gen = generate_puzzle(diff, seed=42)
            self.assertEqual(gen.difficulty, diff)
            self.assertEqual(count_solutions(gen.puzzle, limit=2), 1, f"{diff} not unique")
            self.assertGreaterEqual(gen.clues, target)
            self.assertEqual(solve(gen.puzzle), gen.solution)

    def test_logical_hint_finds_valid_move(self):
        hint = find_logical_hint(ORIGINAL_BOARD)
        self.assertIsNotNone(hint)
        solved = solve(ORIGINAL_BOARD)
        self.assertEqual(solved[hint.row][hint.col], hint.value)
        self.assertTrue(hint.strategy)
        self.assertTrue(hint.reason)

    def test_format_board(self):
        rendered = format_board(ORIGINAL_BOARD)
        self.assertIn("------+-------+------", rendered)
        self.assertIn("|", rendered)


if __name__ == "__main__":
    unittest.main()
