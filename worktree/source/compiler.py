from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any

from card_data import CardDataService, normalize_name
from contracts import (
    BuildContext, CanonicalAction, CanonicalCardEntry, CanonicalDeck, CardChoice,
    CompiledLine, DeckSection, SemanticDeckDraft,
)


EXTRA_TYPE_MARKERS = ("fusion", "synchro", "xyz", "link")


def _stable_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _consequence_payload(consequence) -> dict[str, Any]:
    return {
        "operator": consequence.operator,
        "subject": consequence.subject,
        "source": consequence.source,
        "destination": consequence.destination,
        "qty": consequence.qty,
        "scope": consequence.scope,
        "property_name": consequence.property_name,
        "value": consequence.value,
        "params": dict(consequence.params),
    }


def semantic_source_payload(draft: SemanticDeckDraft, context: BuildContext) -> dict[str, Any]:
    return {
        "context": {
            "environment_id": context.environment_id,
            "era": context.request.era,
            "direction_requested": context.request.direction,
            "forbidden_mode": context.request.forbidden_mode,
            "allowed_mechanics": list(context.allowed_mechanics),
            "forbidden_mechanics": list(context.forbidden_mechanics),
            "policy_source_sha256": context.policy_source_sha256,
        },
        "draft": {
            "direction": draft.direction,
            "concept": draft.concept,
            "cards": [{"name": c.name, "qty": c.qty, "side": c.side} for c in draft.cards],
            "axes": list(draft.axes),
            "narrative_summary": draft.narrative_summary,
            "mastered_functions": list(draft.mastered_functions),
            "limited_functions": list(draft.limited_functions),
            "potential": draft.potential,
            "development_level": draft.development_level,
            "pilotage_guide": list(draft.pilotage_guide),
            "breakpoint": draft.breakpoint,
            "signature_cards": list(draft.signature_cards),
            "terminal_quote": draft.terminal_quote,
            "notes": list(draft.notes),
            "lines": [
                {
                    "title": line.title,
                    "starters": list(line.starters),
                    "claim": line.claim,
                    "certainty": line.certainty.value,
                    "essential": line.essential,
                    "visual_cards": list(line.visual_cards),
                    "actions": [
                        {
                            "label": action.label,
                            "kind": action.kind,
                            "card": action.card,
                            "materials": list(action.materials),
                            "certainty": action.certainty.value,
                            "consequences": [_consequence_payload(c) for c in action.consequences],
                        }
                        for action in line.actions
                    ],
                }
                for line in draft.lines
            ],
        },
    }


def semantic_source_hash(draft: SemanticDeckDraft, context: BuildContext) -> str:
    return hashlib.sha256(_stable_json(semantic_source_payload(draft, context)).encode("utf-8")).hexdigest()


def _technical_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()[:16]
    return f"{prefix}-{digest}"


def _section_for(card: CardChoice, card_type: str) -> DeckSection:
    if card.side:
        return DeckSection.SIDE
    lowered = card_type.casefold()
    if any(marker in lowered for marker in EXTRA_TYPE_MARKERS):
        return DeckSection.EXTRA
    return DeckSection.MAIN


def _canonical_line_name(name: str, service: CardDataService) -> str:
    return service.canonical_name(name)


def compile_draft(draft: SemanticDeckDraft, context: BuildContext, service: CardDataService) -> CanonicalDeck:
    """Compile semantic choices into one canonical, deterministic technical state."""
    source_hash = semantic_source_hash(draft, context)
    deck_id = f"deck-{source_hash[:16]}"

    merged: dict[tuple[str, DeckSection], tuple[Any, int]] = {}
    for choice in draft.cards:
        canonical_name = service.canonical_name(choice.name)
        facts = service.get_facts(canonical_name)
        section = _section_for(choice, facts.card_type)
        key = (canonical_name, section)
        previous = merged.get(key)
        if previous is None:
            merged[key] = (facts, choice.qty)
        else:
            merged[key] = (facts, previous[1] + choice.qty)

    entries: list[CanonicalCardEntry] = []
    for (canonical_name, section), (facts, qty) in sorted(
        merged.items(), key=lambda item: (item[0][1].value, normalize_name(item[0][0]))
    ):
        card_id = _technical_id("card", deck_id, section.value, normalize_name(canonical_name))
        entries.append(CanonicalCardEntry(
            card_id=card_id,
            facts=facts,
            qty=qty,
            section=section,
            banlist_limit=service.banlist_limit(canonical_name),
        ))

    lines: list[CompiledLine] = []
    for line_index, line in enumerate(draft.lines):
        line_seed = _stable_json({
            "deck": deck_id,
            "index": line_index,
            "title": line.title,
            "starters": list(line.starters),
            "claim": line.claim,
        })
        line_id = _technical_id("line", line_seed)
        actions: list[CanonicalAction] = []
        for action_index, action in enumerate(line.actions):
            action_seed = _stable_json({
                "line": line_id,
                "index": action_index,
                "label": action.label,
                "kind": action.kind,
            })
            action_id = _technical_id("action", action_seed)
            canonical_card = _canonical_line_name(action.card, service) if action.card else None
            canonical_materials = tuple(_canonical_line_name(name, service) for name in action.materials)
            actions.append(CanonicalAction(
                action_id=action_id,
                label=action.label,
                kind=action.kind,
                card_name=canonical_card,
                materials=canonical_materials,
                consequences=action.consequences,
                certainty=action.certainty,
            ))
        lines.append(CompiledLine(
            line_id=line_id,
            title=line.title,
            starters=tuple(_canonical_line_name(name, service) for name in line.starters),
            actions=tuple(actions),
            claim=line.claim,
            certainty=line.certainty,
            essential=line.essential,
            visual_cards=tuple(_canonical_line_name(name, service) for name in line.visual_cards),
        ))

    return CanonicalDeck(
        deck_id=deck_id,
        source_hash=source_hash,
        context=context,
        direction=draft.direction,
        concept=draft.concept,
        entries=tuple(entries),
        lines=tuple(lines),
        axes=draft.axes,
        narrative_summary=draft.narrative_summary,
        mastered_functions=draft.mastered_functions,
        limited_functions=draft.limited_functions,
        potential=draft.potential,
        development_level=draft.development_level,
        pilotage_guide=draft.pilotage_guide,
        breakpoint=draft.breakpoint,
        signature_cards=tuple(_canonical_line_name(name, service) for name in draft.signature_cards),
        terminal_quote=draft.terminal_quote,
        notes=draft.notes,
    )


def is_fresh(compiled: CanonicalDeck, draft: SemanticDeckDraft, context: BuildContext) -> bool:
    return compiled.source_hash == semantic_source_hash(draft, context)


def compile_presentation_plan(deck: CanonicalDeck) -> dict[str, Any]:
    """Derive technical component identities from semantic presentation intent."""
    components=[]
    if deck.signature_cards:
        components.append({
            "component_id": _technical_id("component", deck.deck_id, "signature"),
            "type": "CARD_CAROUSEL",
            "parent": "deck",
            "card_names": list(deck.signature_cards),
        })
    for line in deck.lines:
        if line.visual_cards:
            components.append({
                "component_id": _technical_id("component", deck.deck_id, line.line_id, "line-cards"),
                "type": "MINI_CARD_CAROUSEL",
                "parent": line.line_id,
                "card_names": list(line.visual_cards),
            })
    if deck.terminal_quote:
        components.append({
            "component_id": _technical_id("component", deck.deck_id, "terminal-quote"),
            "type": "TERMINAL_QUOTE",
            "parent": "deck",
            "text": deck.terminal_quote,
        })
    payload={"deck_id":deck.deck_id,"components":components}
    payload["plan_sha256"]=hashlib.sha256(_stable_json(payload).encode("utf-8")).hexdigest()
    return payload
