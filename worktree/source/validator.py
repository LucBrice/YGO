from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from contracts import (
    CanonicalDeck, Certainty, DeckSection, IssueOwner, IssueSeverity,
    ProofStatus, StateSnapshot, ValidationIssue, ValidationReport,
)
from types import MappingProxyType as _MappingProxyType


def mechanics_for_card_type(card_type: str) -> set[str]:
    lowered = card_type.casefold()
    mechanics = set()
    for label in ("Ritual", "Fusion", "Synchro", "Pendulum", "Link"):
        if label.casefold() in lowered:
            mechanics.add(label)
    if "xyz" in lowered:
        mechanics.add("Xyz")
    return mechanics


def validate_deck_legality(deck: CanonicalDeck) -> ValidationReport:
    issues: list[ValidationIssue] = []
    counts = defaultdict(int)
    totals = {DeckSection.MAIN: 0, DeckSection.EXTRA: 0, DeckSection.SIDE: 0}

    for entry in deck.entries:
        totals[entry.section] += entry.qty
        counts[entry.facts.canonical_name] += entry.qty
        if entry.qty < 1:
            issues.append(ValidationIssue(
                code="INVALID_COMPILED_QUANTITY",
                message=f"compiled quantity must be positive for {entry.facts.canonical_name}",
                owner=IssueOwner.RUNTIME,
                card_name=entry.facts.canonical_name,
            ))
        forbidden = set(deck.context.forbidden_mechanics)
        used = mechanics_for_card_type(entry.facts.card_type)
        illegal_mechanics = sorted(used.intersection(forbidden))
        if illegal_mechanics:
            issues.append(ValidationIssue(
                code="NARRATIVE_MECHANIC_FORBIDDEN",
                message=f"{entry.facts.canonical_name} introduces forbidden mechanic(s): {', '.join(illegal_mechanics)}",
                owner=IssueOwner.MODEL,
                card_name=entry.facts.canonical_name,
                data={"mechanics": illegal_mechanics},
            ))

    main_count = totals[DeckSection.MAIN]
    extra_count = totals[DeckSection.EXTRA]
    side_count = totals[DeckSection.SIDE]
    if not 40 <= main_count <= 60:
        issues.append(ValidationIssue(
            code="MAIN_DECK_COUNT",
            message=f"Main Deck must contain 40..60 cards; got {main_count}",
            owner=IssueOwner.MODEL,
            data={"actual": main_count, "min": 40, "max": 60},
        ))
    if extra_count > 15:
        issues.append(ValidationIssue(
            code="EXTRA_DECK_COUNT",
            message=f"Extra Deck must contain at most 15 cards; got {extra_count}",
            owner=IssueOwner.MODEL,
            data={"actual": extra_count, "max": 15},
        ))
    if side_count > 15:
        issues.append(ValidationIssue(
            code="SIDE_DECK_COUNT",
            message=f"Side Deck must contain at most 15 cards; got {side_count}",
            owner=IssueOwner.MODEL,
            data={"actual": side_count, "max": 15},
        ))

    limits: dict[str, int] = {}
    for entry in deck.entries:
        name = entry.facts.canonical_name
        limits[name] = min(limits.get(name, 3), entry.banlist_limit)
    for name, qty in counts.items():
        if qty > 3:
            issues.append(ValidationIssue(
                code="COPY_LIMIT_EXCEEDED",
                message=f"{name} appears {qty} times across Main/Extra/Side; maximum is 3",
                owner=IssueOwner.MODEL,
                card_name=name,
                data={"actual": qty, "max": 3},
            ))
        if not deck.context.request.forbidden_mode and qty > limits[name]:
            issues.append(ValidationIssue(
                code="BANLIST_LIMIT_EXCEEDED",
                message=f"{name} appears {qty} times; Link Evolution project limit is {limits[name]}",
                owner=IssueOwner.MODEL,
                card_name=name,
                data={"actual": qty, "max": limits[name]},
            ))

    if deck.context.request.direction and deck.direction.casefold() != deck.context.request.direction.casefold():
        issues.append(ValidationIssue(
            code="DIRECTION_MISMATCH",
            message=f"requested direction {deck.context.request.direction!r} but draft selected {deck.direction!r}",
            owner=IssueOwner.MODEL,
        ))

    selected_names={entry.facts.canonical_name for entry in deck.entries}
    for name in deck.signature_cards:
        if name not in selected_names:
            issues.append(ValidationIssue(
                code="PRESENTATION_CARD_NOT_IN_DECK",
                message=f"signature visual card {name} is not in the compiled deck",
                owner=IssueOwner.MODEL, card_name=name,
            ))
    for line in deck.lines:
        for name in line.visual_cards:
            if name not in selected_names:
                issues.append(ValidationIssue(
                    code="PRESENTATION_CARD_NOT_IN_DECK",
                    message=f"line visual card {name} is not in the compiled deck",
                    owner=IssueOwner.MODEL, line_id=line.line_id, card_name=name,
                ))

    failed = any(issue.severity == IssueSeverity.ERROR for issue in issues)
    return ValidationReport(
        status=ProofStatus.FAILED if failed else ProofStatus.PROVED,
        issues=tuple(issues),
        legality_passed=not failed,
        combos_passed=False,
        publication_allowed=False,
    )

# ---- Combo proof engine ---------------------------------------------------

from collections import Counter
from dataclasses import dataclass, field
import re
from typing import Mapping, Any


@dataclass
class _LineState:
    zones: dict[str, Counter] = field(default_factory=lambda: defaultdict(Counter))
    properties: dict[tuple[str, str], Any] = field(default_factory=dict)
    restrictions: set[str] = field(default_factory=set)
    damage: int = 0
    normal_summon_used: bool = False


_ZONE_ALIASES = {
    "DECK": "DECK", "HAND": "HAND", "FIELD": "FIELD", "GRAVE": "GRAVEYARD",
    "GY": "GRAVEYARD", "GRAVEYARD": "GRAVEYARD", "BANISHED": "BANISHED",
    "EXTRA": "EXTRA", "EXTRA_DECK": "EXTRA", "PZONE": "PZONE", "PENDULUM_ZONE": "PZONE",
}


def _zone(value: str | None) -> str | None:
    if value is None:
        return None
    raw = str(value).strip().upper()
    if raw.startswith("OVERLAY:"):
        return raw
    return _ZONE_ALIASES.get(raw)


def _facts_map(deck: CanonicalDeck):
    return {entry.facts.canonical_name: entry.facts for entry in deck.entries}


def _entry_map(deck: CanonicalDeck):
    return {entry.facts.canonical_name: entry for entry in deck.entries}


def _resolve_selected_name(name: str, facts: Mapping[str, Any]) -> str | None:
    folded = name.casefold().strip()
    matches = [canonical for canonical in facts if canonical.casefold() == folded]
    return matches[0] if len(matches) == 1 else None


def _move(state: _LineState, name: str, src: str, dst: str, qty: int) -> bool:
    if qty < 1 or state.zones[src][name] < qty:
        return False
    state.zones[src][name] -= qty
    state.zones[dst][name] += qty
    return True


def _has(state: _LineState, name: str, zone: str, qty: int = 1) -> bool:
    if zone == "OVERLAY":
        return sum(counter[name] for key, counter in state.zones.items() if key.startswith("OVERLAY:")) >= qty
    return state.zones[zone][name] >= qty


def _take_overlay(state: _LineState, name: str, qty: int, destination: str) -> bool:
    remaining = qty
    for key in sorted(k for k in state.zones if k.startswith("OVERLAY:")):
        available = state.zones[key][name]
        take = min(available, remaining)
        if take:
            state.zones[key][name] -= take
            state.zones[destination][name] += take
            remaining -= take
        if remaining == 0:
            return True
    return False


def _snapshot(state: "_LineState", *, label: str, action_id: str) -> StateSnapshot:
    """Immutable BEFORE/AFTER snapshot (REQ-CR-017). Captured by value: later
    mutation of `state` can never retroactively change an already-returned
    snapshot, so BEFORE and AFTER can never be conflated into the same
    object."""
    zones = _MappingProxyType({
        zone: _MappingProxyType(dict(counter))
        for zone, counter in state.zones.items()
        if any(counter.values())
    })
    properties = _MappingProxyType({
        f"{name}\x1f{prop}": value for (name, prop), value in state.properties.items()
    })
    return StateSnapshot(
        label=label,
        action_id=action_id,
        zones=zones,
        properties=properties,
        restrictions=tuple(sorted(state.restrictions)),
        damage=state.damage,
    )


def _issue(code, message, owner, status, *, line_id=None, card_name=None, data=None):
    return ValidationIssue(
        code=code, message=message, owner=owner, proof_status=status,
        line_id=line_id, card_name=card_name, data=data or {},
    )


def _card_effect_audit_issue(action, facts, semantic_audit, line_id):
    if not action.consequences:
        return None
    if not action.card_name:
        return _issue(
            "SEMANTIC_SOURCE_MISSING",
            f"action {action.label!r} has effect consequences without a source card",
            IssueOwner.RUNTIME, ProofStatus.UNVERIFIED, line_id=line_id,
        )
    card_facts = facts.get(action.card_name)
    if card_facts is None or not card_facts.effect_text.strip():
        return _issue(
            "CARD_EFFECT_EVIDENCE_MISSING",
            f"material effect text is unavailable for {action.card_name}",
            IssueOwner.DATA, ProofStatus.UNVERIFIED, line_id=line_id, card_name=action.card_name,
        )
    audit_value = semantic_audit.get(action.action_id)
    if audit_value is None:
        return _issue(
            "SEMANTIC_AUDIT_REQUIRED",
            f"material interpretation for {action.card_name} has not been independently audited",
            IssueOwner.RUNTIME, ProofStatus.UNVERIFIED, line_id=line_id, card_name=action.card_name,
        )
    if audit_value is not True:
        return _issue(
            "SEMANTIC_AUDIT_REJECTED",
            f"material interpretation for {action.card_name} was not supported by the supplied card text",
            IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id, card_name=action.card_name,
        )
    return None


def _apply_consequence(state, consequence, facts, line_id):
    op = consequence.operator.upper()
    name = _resolve_selected_name(consequence.subject, facts) if consequence.subject else None
    params = dict(consequence.params)
    qty = consequence.qty

    if op == "REQUIRE":
        if name is None:
            return _issue("REQUIRE_SUBJECT_UNKNOWN", f"unknown required subject {consequence.subject!r}", IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id)
        z = _zone(consequence.source or params.get("zone"))
        if z is None:
            return _issue("REQUIRE_ZONE_UNSUPPORTED", "REQUIRE needs a supported source/zone", IssueOwner.RUNTIME, ProofStatus.UNVERIFIED, line_id=line_id, card_name=name)
        if not _has(state, name, z, qty):
            return _issue("REQUIREMENT_NOT_MET", f"requires {qty} {name} in {z}", IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id, card_name=name)
        return None

    if op in {"MOVE", "CONSUME", "OBTAIN", "PRODUCE"}:
        if name is None:
            return _issue("TRANSITION_SUBJECT_UNKNOWN", f"unknown transition subject {consequence.subject!r}", IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id)
        default_src = {"OBTAIN": "DECK", "PRODUCE": "DECK"}.get(op)
        default_dst = {"CONSUME": "GRAVEYARD", "OBTAIN": "HAND", "PRODUCE": "FIELD"}.get(op)
        src = _zone(consequence.source or params.get("from_zone") or default_src)
        dst = _zone(consequence.destination or params.get("to_zone") or default_dst)
        if src is None or dst is None:
            return _issue("TRANSITION_ZONE_UNSUPPORTED", f"{op} needs supported source/destination zones", IssueOwner.RUNTIME, ProofStatus.UNVERIFIED, line_id=line_id, card_name=name)
        ok = _take_overlay(state, name, qty, dst) if src == "OVERLAY" else _move(state, name, src, dst, qty)
        if not ok:
            return _issue("RESOURCE_CONSERVATION", f"cannot {op} {qty} {name} from {src} to {dst}; resource is unavailable", IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id, card_name=name)
        return None

    if op == "PROPERTY_UPDATE":
        if name is None or consequence.property_name not in {"level", "tuner", "effective_name"}:
            return _issue("PROPERTY_UPDATE_UNSUPPORTED", "unsupported property update", IssueOwner.RUNTIME, ProofStatus.UNVERIFIED, line_id=line_id, card_name=name)
        if not _has(state, name, "FIELD", 1):
            return _issue("PROPERTY_TARGET_NOT_ON_FIELD", f"cannot update {name}; it is not on field", IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id, card_name=name)
        state.properties[(name, consequence.property_name)] = consequence.value
        return None

    if op == "RESTRICTION_APPLY":
        values = params.get("forbid_mechanics")
        if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
            return _issue("RESTRICTION_UNSUPPORTED", "restriction cannot be mechanically represented", IssueOwner.RUNTIME, ProofStatus.UNVERIFIED, line_id=line_id)
        state.restrictions.update(v.upper() for v in values)
        return None

    if op == "RESTRICTION_RELEASE":
        values = params.get("forbid_mechanics")
        if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
            return _issue("RESTRICTION_RELEASE_UNSUPPORTED", "restriction release cannot be mechanically represented", IssueOwner.RUNTIME, ProofStatus.UNVERIFIED, line_id=line_id)
        for value in values:
            state.restrictions.discard(value.upper())
        return None

    if op == "DAMAGE_EVENT":
        try:
            amount = int(consequence.value if consequence.value is not None else params.get("amount"))
        except (TypeError, ValueError):
            return _issue("DAMAGE_VALUE_UNSUPPORTED", "damage event needs an integer amount", IssueOwner.RUNTIME, ProofStatus.UNVERIFIED, line_id=line_id)
        if amount < 0:
            return _issue("DAMAGE_VALUE_INVALID", "damage cannot be negative", IssueOwner.RUNTIME, ProofStatus.FAILED, line_id=line_id)
        state.damage += amount
        return None

    if op == "LETHAL_CHECK":
        threshold = int(params.get("threshold", 8000))
        if state.damage < threshold:
            return _issue("LETHAL_NOT_REACHED", f"damage {state.damage} is below lethal threshold {threshold}", IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id)
        return None

    return _issue("OPERATOR_UNSUPPORTED", f"unsupported mechanical operator {op}", IssueOwner.RUNTIME, ProofStatus.UNVERIFIED, line_id=line_id)


def _effective_level(state, name, facts):
    override = state.properties.get((name, "level"))
    if isinstance(override, int):
        return override
    return facts[name].level


def _effective_tuner(state, name, facts):
    override = state.properties.get((name, "tuner"))
    if isinstance(override, bool):
        return override
    return "tuner" in facts[name].card_type.casefold()


def _material_header(effect_text: str) -> str:
    return effect_text.strip().splitlines()[0].strip() if effect_text.strip() else ""


def _synchro_summon(state, action, facts, line_id):
    target = action.card_name
    if target not in facts or "synchro" not in facts[target].card_type.casefold():
        return _issue("SYNCHRO_TARGET_INVALID", f"{target} is not a known Synchro monster", IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id, card_name=target)
    if "SYNCHRO" in state.restrictions:
        return _issue("SUMMON_RESTRICTED", "Synchro Summon is currently restricted", IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id)
    header = _material_header(facts[target].effect_text)
    if not re.fullmatch(r"1 Tuner \+ 1\+ non-Tuner monsters", header, flags=re.I):
        return _issue("SYNCHRO_REQUIREMENT_UNSUPPORTED", f"cannot mechanically close material clause: {header!r}", IssueOwner.RUNTIME, ProofStatus.UNVERIFIED, line_id=line_id, card_name=target)
    mats = list(action.materials)
    if len(mats) < 2 or any(m not in facts or not _has(state, m, "FIELD") for m in mats):
        return _issue("SYNCHRO_MATERIAL_MISSING", "Synchro materials are not all available on field", IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id)
    tuners = [_effective_tuner(state, m, facts) for m in mats]
    levels = [_effective_level(state, m, facts) for m in mats]
    if tuners.count(True) != 1 or any(level is None for level in levels):
        return _issue("SYNCHRO_MATERIAL_RULE", "Synchro requires exactly one known Tuner and known material levels", IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id)
    if sum(levels) != facts[target].level:
        return _issue("SYNCHRO_LEVEL_SUM", f"material levels sum to {sum(levels)} but target level is {facts[target].level}", IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id, card_name=target)
    if not _has(state, target, "EXTRA"):
        return _issue("EXTRA_TARGET_MISSING", f"{target} is not available in Extra Deck", IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id, card_name=target)
    for m in mats:
        _move(state, m, "FIELD", "GRAVEYARD", 1)
    _move(state, target, "EXTRA", "FIELD", 1)
    return None


def _xyz_summon(state, action, facts, line_id):
    target = action.card_name
    if target not in facts or "xyz" not in facts[target].card_type.casefold():
        return _issue("XYZ_TARGET_INVALID", f"{target} is not a known Xyz monster", IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id, card_name=target)
    if "XYZ" in state.restrictions:
        return _issue("SUMMON_RESTRICTED", "Xyz Summon is currently restricted", IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id)
    header = _material_header(facts[target].effect_text)
    match = re.fullmatch(r"(\d+) Level (\d+) monsters", header, flags=re.I)
    if not match:
        return _issue("XYZ_REQUIREMENT_UNSUPPORTED", f"cannot mechanically close material clause: {header!r}", IssueOwner.RUNTIME, ProofStatus.UNVERIFIED, line_id=line_id, card_name=target)
    required, level = int(match.group(1)), int(match.group(2))
    mats = list(action.materials)
    if len(mats) != required or any(m not in facts or not _has(state, m, "FIELD") for m in mats):
        return _issue("XYZ_MATERIAL_MISSING", f"Xyz target requires exactly {required} available materials", IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id)
    if any(_effective_level(state, m, facts) != level for m in mats):
        return _issue("XYZ_LEVEL_RULE", f"all Xyz materials must be Level {level}", IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id)
    if not _has(state, target, "EXTRA"):
        return _issue("EXTRA_TARGET_MISSING", f"{target} is not available in Extra Deck", IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id, card_name=target)
    overlay_zone = f"OVERLAY:{target.upper()}"
    for m in mats:
        _move(state, m, "FIELD", overlay_zone, 1)
    _move(state, target, "EXTRA", "FIELD", 1)
    return None


def _link_summon(state, action, facts, line_id):
    target = action.card_name
    if target not in facts or "link" not in facts[target].card_type.casefold():
        return _issue("LINK_TARGET_INVALID", f"{target} is not a known Link monster", IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id, card_name=target)
    if "LINK" in state.restrictions:
        return _issue("SUMMON_RESTRICTED", "Link Summon is currently restricted", IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id)
    header = _material_header(facts[target].effect_text)
    match = re.fullmatch(r"(\d+)(\+)? (.+) monsters", header, flags=re.I)
    if not match:
        return _issue("LINK_REQUIREMENT_UNSUPPORTED", f"cannot mechanically close material clause: {header!r}", IssueOwner.RUNTIME, ProofStatus.UNVERIFIED, line_id=line_id, card_name=target)
    minimum = int(match.group(1)); qualifier = match.group(3).strip().casefold()
    mats = list(action.materials)
    if len(mats) < minimum or any(m not in facts or not _has(state, m, "FIELD") for m in mats):
        return _issue("LINK_MATERIAL_MISSING", f"Link target requires at least {minimum} available materials", IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id)
    if any("link" in facts[m].card_type.casefold() for m in mats):
        return _issue("LINK_RATING_CONTRIBUTION_UNSUPPORTED", "Link monsters as Link material require explicit contribution handling", IssueOwner.RUNTIME, ProofStatus.UNVERIFIED, line_id=line_id)
    if facts[target].linkval is None or len(mats) != facts[target].linkval:
        return _issue("LINK_RATING_RULE", f"non-Link material count must equal target Link Rating {facts[target].linkval}", IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id)
    if qualifier == "effect" and any("effect" not in facts[m].card_type.casefold() for m in mats):
        return _issue("LINK_MATERIAL_TYPE", "target requires Effect Monsters", IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id)
    if qualifier not in {"effect", ""}:
        return _issue("LINK_QUALIFIER_UNSUPPORTED", f"unsupported Link material qualifier {qualifier!r}", IssueOwner.RUNTIME, ProofStatus.UNVERIFIED, line_id=line_id)
    if not _has(state, target, "EXTRA"):
        return _issue("EXTRA_TARGET_MISSING", f"{target} is not available in Extra Deck", IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id, card_name=target)
    for m in mats:
        _move(state, m, "FIELD", "GRAVEYARD", 1)
    _move(state, target, "EXTRA", "FIELD", 1)
    return None


def _pendulum_summon_from_hand(state, action, facts, line_id):
    if "PENDULUM" in state.restrictions:
        return _issue("SUMMON_RESTRICTED", "Pendulum Summon is currently restricted", IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id)
    scales=[]
    for name, qty in state.zones["PZONE"].items():
        if qty and name in facts and facts[name].scale is not None:
            scales.extend([facts[name].scale] * qty)
    if len(scales) < 2:
        return _issue("PENDULUM_SCALES_MISSING", "Pendulum Summon needs two known scales", IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id)
    low, high = min(scales), max(scales)
    if low == high:
        return _issue("PENDULUM_SCALE_RANGE", "Pendulum scales do not create a summon range", IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id)
    for name in action.materials:
        if name not in facts or not _has(state, name, "HAND"):
            return _issue("PENDULUM_MATERIAL_MISSING", f"{name} is not available in hand", IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id)
        level = _effective_level(state, name, facts)
        if level is None or not low < level < high:
            return _issue("PENDULUM_LEVEL_RANGE", f"{name} Level {level} is outside scales {low}/{high}", IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id)
    for name in action.materials:
        _move(state, name, "HAND", "FIELD", 1)
    return None


def _execute_action(state, action, facts, semantic_audit, line_id):
    kind = action.kind.upper()
    if kind in state.restrictions:
        return _issue("SUMMON_RESTRICTED", f"{kind} is currently restricted", IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id)

    audit_issue = _card_effect_audit_issue(action, facts, semantic_audit, line_id)
    if audit_issue is not None:
        return audit_issue

    if kind == "NORMAL_SUMMON":
        name = action.card_name
        if name not in facts or "monster" not in facts[name].card_type.casefold():
            return _issue("NORMAL_SUMMON_TARGET_INVALID", f"{name} is not a known monster", IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id, card_name=name)
        if state.normal_summon_used:
            return _issue("NORMAL_SUMMON_ALREADY_USED", "a second Normal Summon needs an explicit permission not represented here", IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id)
        if not _move(state, name, "HAND", "FIELD", 1):
            return _issue("NORMAL_SUMMON_RESOURCE", f"{name} is not in hand", IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id, card_name=name)
        state.normal_summon_used = True
    elif kind == "SET_SCALE":
        name = action.card_name
        if name not in facts or facts[name].scale is None:
            return _issue("PENDULUM_SCALE_INVALID", f"{name} has no known Pendulum Scale", IssueOwner.DATA, ProofStatus.UNVERIFIED, line_id=line_id, card_name=name)
        if not _move(state, name, "HAND", "PZONE", 1):
            return _issue("PENDULUM_SCALE_RESOURCE", f"{name} is not in hand", IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id, card_name=name)
    elif kind == "SYNCHRO_SUMMON":
        issue = _synchro_summon(state, action, facts, line_id)
        if issue: return issue
    elif kind == "XYZ_SUMMON":
        issue = _xyz_summon(state, action, facts, line_id)
        if issue: return issue
    elif kind == "LINK_SUMMON":
        issue = _link_summon(state, action, facts, line_id)
        if issue: return issue
    elif kind == "PENDULUM_SUMMON":
        issue = _pendulum_summon_from_hand(state, action, facts, line_id)
        if issue: return issue
    elif kind in {"ACTIVATE_EFFECT", "EFFECT"}:
        # The mechanical meaning is entirely in audited consequences below.
        if not action.consequences:
            return _issue("EFFECT_WITHOUT_CONSEQUENCE", "effect action has no mechanical consequence", IssueOwner.RUNTIME, ProofStatus.UNVERIFIED, line_id=line_id)
    else:
        return _issue("ACTION_KIND_UNSUPPORTED", f"unsupported action kind {kind}", IssueOwner.RUNTIME, ProofStatus.UNVERIFIED, line_id=line_id)

    for consequence in action.consequences:
        issue = _apply_consequence(state, consequence, facts, line_id)
        if issue is not None:
            return issue
    return None


def _initial_state(deck: CanonicalDeck, line) -> tuple[_LineState, list[ValidationIssue]]:
    state = _LineState()
    issues=[]
    facts=_facts_map(deck)
    for entry in deck.entries:
        if entry.section == DeckSection.MAIN:
            state.zones["DECK"][entry.facts.canonical_name] += entry.qty
        elif entry.section == DeckSection.EXTRA:
            state.zones["EXTRA"][entry.facts.canonical_name] += entry.qty
    for starter in line.starters:
        if starter not in facts:
            issues.append(_issue("STARTER_UNKNOWN", f"starter {starter} is not in compiled deck facts", IssueOwner.MODEL, ProofStatus.FAILED, line_id=line.line_id, card_name=starter))
            continue
        if not _move(state, starter, "DECK", "HAND", 1):
            issues.append(_issue("STARTER_NOT_IN_MAIN", f"starter {starter} is not available in Main Deck", IssueOwner.MODEL, ProofStatus.FAILED, line_id=line.line_id, card_name=starter))
    return state, issues


def _certainty_issue(line):
    if line.certainty == Certainty.GUARANTEED:
        return None
    if re.search(r"\bguaranteed\b|\bgaranti(?:e|es|s)?\b", line.claim, flags=re.I):
        return _issue(
            "CERTAINTY_UPGRADE",
            f"{line.certainty.value} line uses guaranteed wording",
            IssueOwner.MODEL, ProofStatus.FAILED, line_id=line.line_id,
        )
    return None


def validate_combo_lines(deck: CanonicalDeck, *, semantic_audit: Mapping[str, bool] | None = None) -> ValidationReport:
    semantic_audit = semantic_audit or {}
    facts = _facts_map(deck)
    issues: list[ValidationIssue] = []
    trace: list[StateSnapshot] = []

    for line in deck.lines:
        certainty_issue = _certainty_issue(line)
        if certainty_issue:
            issues.append(certainty_issue)
            if line.essential:
                continue
        state, start_issues = _initial_state(deck, line)
        issues.extend(start_issues)
        if start_issues and line.essential:
            continue
        for action in line.actions:
            before = _snapshot(state, label=f"BEFORE:{action.action_id}", action_id=action.action_id)
            issue = _execute_action(state, action, facts, semantic_audit, line.line_id)
            after = _snapshot(state, label=f"AFTER:{action.action_id}", action_id=action.action_id)
            trace.append(before)
            trace.append(after)
            if issue is not None:
                issues.append(issue)
                break

    essential_line_ids = {line.line_id for line in deck.lines if line.essential}
    essential_issues = [i for i in issues if i.line_id in essential_line_ids]
    if any(i.proof_status == ProofStatus.FAILED for i in essential_issues):
        status = ProofStatus.FAILED
    elif any(i.proof_status == ProofStatus.UNVERIFIED for i in essential_issues):
        status = ProofStatus.UNVERIFIED
    else:
        status = ProofStatus.PROVED
    return ValidationReport(
        status=status,
        issues=tuple(issues),
        legality_passed=False,
        combos_passed=(status == ProofStatus.PROVED),
        publication_allowed=False,
        replay_trace=tuple(trace),
    )


def combine_validation(legality: ValidationReport, combos: ValidationReport) -> ValidationReport:
    issues = legality.issues + combos.issues
    if legality.status == ProofStatus.FAILED or combos.status == ProofStatus.FAILED:
        status = ProofStatus.FAILED
    elif legality.status == ProofStatus.UNVERIFIED or combos.status == ProofStatus.UNVERIFIED:
        status = ProofStatus.UNVERIFIED
    else:
        status = ProofStatus.PROVED
    allowed = legality.legality_passed and combos.combos_passed and status == ProofStatus.PROVED
    return ValidationReport(
        status=status,
        issues=issues,
        legality_passed=legality.legality_passed,
        combos_passed=combos.combos_passed,
        publication_allowed=allowed,
        replay_trace=combos.replay_trace,
    )
