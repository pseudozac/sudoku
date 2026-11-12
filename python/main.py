"""PyInstaller-friendly entry point for Pseudo Sudoku."""
import sys
from pathlib import Path

# Ensure pseudo_sudoku package is discoverable regardless of invocation directory
pkg_root = Path(__file__).resolve().parent
if str(pkg_root) not in sys.path:
    sys.path.insert(0, str(pkg_root))

from pseudo_sudoku.app import main

if __name__ == "__main__":
    raise SystemExit(main())
