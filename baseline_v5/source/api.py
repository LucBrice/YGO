from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from contracts import BuildRequest, DeckResult
from runtime import ModelCallable, Runtime
from validator import validate_combo_lines, validate_deck_legality


def build_deck(
    request: BuildRequest,
    *,
    model: ModelCallable,
    source_dir: str | Path | None = None,
    card_provider: Any = None,
    cache_dir: str | Path | None = None,
) -> DeckResult:
    source = Path(source_dir) if source_dir is not None else Path(__file__).resolve().parent
    return Runtime(
        model=model,
        source_dir=source,
        card_provider=card_provider,
        cache_dir=cache_dir,
    ).build_deck(request)


def validate_deck(deck):
    return validate_deck_legality(deck)


def validate_combo(deck, *, semantic_audit: Mapping[str, bool] | None = None):
    return validate_combo_lines(deck, semantic_audit=semantic_audit)
