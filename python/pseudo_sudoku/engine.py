"""Core Sudoku bitmask + MRV solver, step generator, and logical hint engine."""
from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Generator, Iterable, List, Optional, Sequence, Tuple

Board = List[List[int]]

ALL_DIGITS_MASK = 0b1111111110  # bits 1..9 set
_POPCOUNT = tuple(bin(i).count("1") for i in range(1024))


@dataclass(frozen=True)
class SolveStep:
    kind: str  # "try" | "place" | "backtrack" | "complete"
    row: int
    col: int
    value: int


@dataclass(frozen=True)
class Hint:
    row: int
    col: int
    value: int
    strategy: str
    reason: str


def clone_board(board: Sequence[Sequence[int]]) -> Board:
    return [list(row) for row in board]


def _box_index(row: int, col: int) -> int:
    return (row // 3) * 3 + (col // 3)


def validate_board(board: Sequence[Sequence[int]]) -> Tuple[bool, Optional[str]]:
    if len(board) != 9 or any(len(r) != 9 for r in board):
        return False, "Board must be 9x9."

    rows = [0] * 9
    cols = [0] * 9
    boxes = [0] * 9

    for r in range(9):
        for c in range(9):
            val = board[r][c]
            if not isinstance(val, int) or val < 0 or val > 9:
                return False, f"Invalid cell value {val!r} at ({r}, {c})."
            if val == 0:
                continue
            bit = 1 << val
            b = _box_index(r, c)
            if (rows[r] & bit) or (cols[c] & bit) or (boxes[b] & bit):
                return False, f"Duplicate digit {val} at ({r}, {c})."
            rows[r] |= bit
            cols[c] |= bit
            boxes[b] |= bit
    return True, None


def _init_masks(board: Sequence[Sequence[int]]) -> Tuple[List[int], List[int], List[int], List[Tuple[int, int]]]:
    rows = [0] * 9
    cols = [0] * 9
    boxes = [0] * 9
    empties: List[Tuple[int, int]] = []

    for r in range(9):
        for c in range(9):
            val = board[r][c]
            if val == 0:
                empties.append((r, c))
            else:
                bit = 1 << val
                rows[r] |= bit
                cols[c] |= bit
                boxes[_box_index(r, c)] |= bit
    return rows, cols, boxes, empties


def _candidates_mask(rows: List[int], cols: List[int], boxes: List[int], r: int, c: int) -> int:
    used = rows[r] | cols[c] | boxes[_box_index(r, c)]
    return ALL_DIGITS_MASK & ~used


def _iter_digits(mask: int, rng: Optional[random.Random] = None) -> Iterable[int]:
    digits = [d for d in range(1, 10) if mask & (1 << d)]
    if rng is not None:
        rng.shuffle(digits)
    return digits


def solve(board: Sequence[Sequence[int]], rng: Optional[random.Random] = None) -> Optional[Board]:
    """Solve a Sudoku board using MRV + bitmask backtracking. Returns a new solved board or None."""
    valid, _ = validate_board(board)
    if not valid:
        return None

    work = clone_board(board)
    rows, cols, boxes, empties = _init_masks(work)

    def backtrack(idx: int) -> bool:
        if idx == len(empties):
            return True

        # MRV: swap the empty cell with fewest legal candidates into position `idx`
        best_pos = -1
        best_mask = 0
        best_count = 10
        for i in range(idx, len(empties)):
            r, c = empties[i]
            mask = _candidates_mask(rows, cols, boxes, r, c)
            count = _POPCOUNT[mask]
            if count == 0:
                return False
            if count < best_count:
                best_count = count
                best_pos = i
                best_mask = mask
                if count == 1:
                    break

        empties[idx], empties[best_pos] = empties[best_pos], empties[idx]
        r, c = empties[idx]
        b = _box_index(r, c)

        for d in _iter_digits(best_mask, rng):
            bit = 1 << d
            work[r][c] = d
            rows[r] |= bit
            cols[c] |= bit
            boxes[b] |= bit

            if backtrack(idx + 1):
                return True

            work[r][c] = 0
            rows[r] &= ~bit
            cols[c] &= ~bit
            boxes[b] &= ~bit

        empties[idx], empties[best_pos] = empties[best_pos], empties[idx]
        return False

    return work if backtrack(0) else None


def count_solutions(board: Sequence[Sequence[int]], limit: int = 2) -> int:
    """Count solutions up to `limit` (used to verify puzzle uniqueness)."""
    valid, _ = validate_board(board)
    if not valid:
        return 0

    work = clone_board(board)
    rows, cols, boxes, empties = _init_masks(work)
    found = 0

    def backtrack(idx: int) -> None:
        nonlocal found
        if found >= limit:
            return
        if idx == len(empties):
            found += 1
            return

        best_pos = -1
        best_mask = 0
        best_count = 10
        for i in range(idx, len(empties)):
            r, c = empties[i]
            mask = _candidates_mask(rows, cols, boxes, r, c)
            count = _POPCOUNT[mask]
            if count == 0:
                return
            if count < best_count:
                best_count = count
                best_pos = i
                best_mask = mask
                if count == 1:
                    break

        empties[idx], empties[best_pos] = empties[best_pos], empties[idx]
        r, c = empties[idx]
        b = _box_index(r, c)

        for d in range(1, 10):
            bit = 1 << d
            if not (best_mask & bit):
                continue
            rows[r] |= bit
            cols[c] |= bit
            boxes[b] |= bit
            backtrack(idx + 1)
            rows[r] &= ~bit
            cols[c] &= ~bit
            boxes[b] &= ~bit
            if found >= limit:
                break

        empties[idx], empties[best_pos] = empties[best_pos], empties[idx]

    backtrack(0)
    return found


def solve_steps(board: Board) -> Generator[SolveStep, None, bool]:
    """Yield step-by-step MRV backtracking events for live GUI/CLI visualization."""
    valid, _ = validate_board(board)
    if not valid:
        return False

    rows, cols, boxes, empties = _init_masks(board)

    def backtrack(idx: int) -> Generator[SolveStep, None, bool]:
        if idx == len(empties):
            yield SolveStep("complete", -1, -1, 0)
            return True

        best_pos = -1
        best_mask = 0
        best_count = 10
        for i in range(idx, len(empties)):
            r, c = empties[i]
            mask = _candidates_mask(rows, cols, boxes, r, c)
            count = _POPCOUNT[mask]
            if count == 0:
                return False
            if count < best_count:
                best_count = count
                best_pos = i
                best_mask = mask
                if count == 1:
                    break

        empties[idx], empties[best_pos] = empties[best_pos], empties[idx]
        r, c = empties[idx]
        b = _box_index(r, c)

        for d in range(1, 10):
            bit = 1 << d
            if not (best_mask & bit):
                continue
            yield SolveStep("try", r, c, d)
            board[r][c] = d
            rows[r] |= bit
            cols[c] |= bit
            boxes[b] |= bit
            yield SolveStep("place", r, c, d)

            solved = yield from backtrack(idx + 1)
            if solved:
                return True

            board[r][c] = 0
            rows[r] &= ~bit
            cols[c] &= ~bit
            boxes[b] &= ~bit
            yield SolveStep("backtrack", r, c, d)

        empties[idx], empties[best_pos] = empties[best_pos], empties[idx]
        return False

    return (yield from backtrack(0))


def find_logical_hint(board: Sequence[Sequence[int]], solution: Optional[Sequence[Sequence[int]]] = None) -> Optional[Hint]:
    """Find a human-understandable next step (Naked Single or Hidden Single), with solver fallback."""
    rows, cols, boxes, empties = _init_masks(board)
    if not empties:
        return None

    # 1. Naked Single: cell with exactly 1 candidate
    cand_map = {}
    for r, c in empties:
        mask = _candidates_mask(rows, cols, boxes, r, c)
        cand_map[(r, c)] = mask
        if _POPCOUNT[mask] == 1:
            val = mask.bit_length() - 1
            return Hint(
                r,
                c,
                val,
                "Naked Single",
                f"R{r + 1}C{c + 1} can only be {val} — all other digits conflict with its row, column, or box.",
            )

    # 2. Hidden Single in rows, columns, and boxes
    for r in range(9):
        for d in range(1, 10):
            bit = 1 << d
            if rows[r] & bit:
                continue
            spots = [(r, c) for c in range(9) if board[r][c] == 0 and (cand_map[(r, c)] & bit)]
            if len(spots) == 1:
                sr, sc = spots[0]
                return Hint(
                    sr,
                    sc,
                    d,
                    "Hidden Single (Row)",
                    f"In row {sr + 1}, {d} can only go in R{sr + 1}C{sc + 1}.",
                )

    for c in range(9):
        for d in range(1, 10):
            bit = 1 << d
            if cols[c] & bit:
                continue
            spots = [(r, c) for r in range(9) if board[r][c] == 0 and (cand_map[(r, c)] & bit)]
            if len(spots) == 1:
                sr, sc = spots[0]
                return Hint(
                    sr,
                    sc,
                    d,
                    "Hidden Single (Column)",
                    f"In column {sc + 1}, {d} can only go in R{sr + 1}C{sc + 1}.",
                )

    for box in range(9):
        br, bc = (box // 3) * 3, (box % 3) * 3
        for d in range(1, 10):
            bit = 1 << d
            if boxes[box] & bit:
                continue
            spots = [
                (r, c)
                for r in range(br, br + 3)
                for c in range(bc, bc + 3)
                if board[r][c] == 0 and (cand_map[(r, c)] & bit)
            ]
            if len(spots) == 1:
                sr, sc = spots[0]
                return Hint(
                    sr,
                    sc,
                    d,
                    "Hidden Single (Box)",
                    f"In box {box + 1}, {d} can only go in R{sr + 1}C{sc + 1}.",
                )

    # 3. Fallback: pick the most constrained empty cell from a verified solution
    solved = solution if solution is not None else solve(board)
    if solved is None:
        return None
    r, c = min(empties, key=lambda pos: _POPCOUNT[cand_map[pos]])
    val = solved[r][c]
    return Hint(
        r,
        c,
        val,
        "Solver Deduction",
        f"R{r + 1}C{c + 1} must be {val} (determined by deeper lookahead).",
    )


def format_board(board: Sequence[Sequence[int]]) -> str:
    lines = []
    for r in range(9):
        if r % 3 == 0 and r != 0:
            lines.append("------+-------+------")
        row_parts = []
        for c in range(9):
            if c % 3 == 0 and c != 0:
                row_parts.append("|")
            val = board[r][c]
            row_parts.append(str(val) if val != 0 else ".")
        lines.append(" ".join(row_parts))
    return "\n".join(lines)
