"""Test-only import bootstrap. Not a product module (tests/** is MAY-TOUCH)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKTREE_SOURCE = ROOT / "worktree" / "source"
BASELINE_SOURCE = ROOT / "baseline_v5" / "source"


def use_worktree_source() -> Path:
    """Point bare module imports (contracts/card_data/compiler/validator/runtime/api)
    at the candidate product tree under test. Honors YGO_SOURCE_OVERRIDE
    (set by the G9 package-replay script) to run the exact same test suite
    against extracted packaged bytes instead of worktree/source, without
    duplicating every test file."""
    override = __import__("os").environ.get("YGO_SOURCE_OVERRIDE")
    source = Path(override) if override else WORKTREE_SOURCE
    path = str(source)
    if path not in sys.path:
        sys.path.insert(0, path)
    return source
