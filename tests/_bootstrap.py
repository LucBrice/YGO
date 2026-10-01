"""Test-only import bootstrap. Not a product module (tests/** is MAY-TOUCH)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKTREE_SOURCE = ROOT / "worktree" / "source"
BASELINE_SOURCE = ROOT / "baseline_v5" / "source"


def use_worktree_source() -> Path:
    """Point bare module imports (contracts/card_data/compiler/validator/runtime/api)
    at the candidate product tree under test."""
    path = str(WORKTREE_SOURCE)
    if path not in sys.path:
        sys.path.insert(0, path)
    return WORKTREE_SOURCE
