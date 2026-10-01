from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from contracts import (
    BackwardRequirement, CanonicalDeck, Certainty, ColdAuditResult, CriticalDecision,
    DeckSection, DerivedClaim, IssueOwner, IssueSeverity, ProofStatus, StateSnapshot,
    ValidationIssue, ValidationReport, certainty_at_least_as_strong,
)
from types import MappingProxyType as _MappingProxyType
import hashlib

import compiler as _compiler


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


def _purge_properties_if_left_field(state: _LineState, name: str, src: str) -> None:
    """REQ-CR-021: a dynamic property override is scoped to the exact
    instance/placement that earned it. Once the last copy of `name` leaves
    FIELD, any stored override for it is dropped so a later, unrelated
    arrival of a same-named card starts from its base facts instead of
    inheriting a stale value."""
    if src == "FIELD" and state.zones["FIELD"][name] <= 0:
        for key in [k for k in state.properties if k[0] == name]:
            del state.properties[key]


def _move(state: _LineState, name: str, src: str, dst: str, qty: int) -> bool:
    if qty < 1 or state.zones[src][name] < qty:
        return False
    state.zones[src][name] -= qty
    state.zones[dst][name] += qty
    _purge_properties_if_left_field(state, name, src)
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
    if _has(state, name, "FIELD", 1):
        override = state.properties.get((name, "level"))
        if isinstance(override, int):
            return override
    return facts[name].level


def _effective_tuner(state, name, facts):
    if _has(state, name, "FIELD", 1):
        override = state.properties.get((name, "tuner"))
        if isinstance(override, bool):
            return override
    return "tuner" in facts[name].card_type.casefold()


def _effective_name(state, name, facts):
    """REQ-CR-021 completeness: effective_name overrides follow the same
    while-on-field lifecycle as level/tuner, even though no predicate
    currently consumes it (reserved for a future PRE-GO amendment)."""
    if _has(state, name, "FIELD", 1):
        override = state.properties.get((name, "effective_name"))
        if isinstance(override, str) and override:
            return override
    return name


# ---- Generic summon/material legality (REQ-CR-018/019) --------------------
#
# One generic evaluator for Synchro/Xyz/Link: the material clause itself was
# already parsed into a card-name-free SummonMaterialBinding by the compiler
# (compiler.parse_summon_material_clause); this function only evaluates that
# binding against the actual BEFORE state. There is no branch here for any
# specific named monster -- every Synchro/Xyz/Link summon, however unusual
# its material clause, is proved or refused exclusively through this generic
# path.

_TYPE_MARKER_BY_KIND = {"SYNCHRO_SUMMON": "synchro", "XYZ_SUMMON": "xyz", "LINK_SUMMON": "link"}
_RESTRICTION_BY_KIND = {"SYNCHRO_SUMMON": "SYNCHRO", "XYZ_SUMMON": "XYZ", "LINK_SUMMON": "LINK"}


def _matches_material_predicate(state, name, facts, predicate) -> bool:
    is_tuner = _effective_tuner(state, name, facts)
    if predicate.kind == "TUNER" and not is_tuner:
        return False
    if predicate.kind == "NON_TUNER" and is_tuner:
        return False
    if predicate.exact_level is not None and _effective_level(state, name, facts) != predicate.exact_level:
        return False
    if predicate.type_qualifier and predicate.type_qualifier.casefold() not in facts[name].card_type.casefold():
        return False
    return True


def _evaluate_summon_material_binding(state, action, facts, line_id):
    target = action.card_name
    kind = action.kind
    marker = _TYPE_MARKER_BY_KIND[kind]
    if target not in facts or marker not in facts[target].card_type.casefold():
        return _issue(
            f"{marker.upper()}_TARGET_INVALID", f"{target} is not a known {marker.title()} monster",
            IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id, card_name=target,
        )
    restriction = _RESTRICTION_BY_KIND[kind]
    if restriction in state.restrictions:
        return _issue(
            "SUMMON_RESTRICTED", f"{restriction.title()} Summon is currently restricted",
            IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id,
        )

    binding = action.summon_binding
    if binding is None:
        return _issue(
            "SUMMON_MATERIAL_BINDING_UNRESOLVED",
            f"cannot mechanically close material clause for {target} from the compiled binding",
            IssueOwner.RUNTIME, ProofStatus.UNVERIFIED, line_id=line_id, card_name=target,
        )

    mats = list(action.materials)
    if not mats or any(m not in facts or not _has(state, m, "FIELD") for m in mats):
        return _issue(
            "SUMMON_MATERIAL_MISSING", f"declared materials for {target} are not all available on field",
            IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id, card_name=target,
        )
    if kind == "LINK_SUMMON" and any("link" in facts[m].card_type.casefold() for m in mats):
        return _issue(
            "LINK_RATING_CONTRIBUTION_UNSUPPORTED",
            "Link monsters as Link material require explicit contribution handling",
            IssueOwner.RUNTIME, ProofStatus.UNVERIFIED, line_id=line_id, card_name=target,
        )

    remaining = list(mats)
    assigned: list[list[str]] = []
    for group in binding.groups:
        bucket = [m for m in remaining if _matches_material_predicate(state, m, facts, group.predicate)]
        assigned.append(bucket)
        for m in bucket:
            remaining.remove(m)
    if remaining:
        return _issue(
            "SUMMON_MATERIAL_RULE",
            f"material(s) {remaining} do not satisfy any required group for {target}",
            IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id, card_name=target,
        )
    for group, bucket in zip(binding.groups, assigned):
        count = len(bucket)
        if count < group.min_count or (group.max_count is not None and count > group.max_count):
            upper = "or more" if group.max_count is None else str(group.max_count)
            return _issue(
                "SUMMON_MATERIAL_RULE",
                f"{target} requires {group.min_count}..{upper} matching materials for one group, got {count}",
                IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id, card_name=target,
            )

    if binding.aggregate_level_equals_target:
        levels = [_effective_level(state, m, facts) for m in mats]
        if any(level is None for level in levels):
            return _issue(
                "SUMMON_MATERIAL_RULE", f"not all material levels are known for {target}",
                IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id, card_name=target,
            )
        total = sum(levels)
        if total != facts[target].level:
            return _issue(
                "SYNCHRO_LEVEL_SUM", f"material levels sum to {total} but target level is {facts[target].level}",
                IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id, card_name=target,
            )

    if kind == "LINK_SUMMON" and (facts[target].linkval is None or len(mats) != facts[target].linkval):
        return _issue(
            "LINK_RATING_RULE",
            f"non-Link material count must equal target Link Rating {facts[target].linkval}",
            IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id, card_name=target,
        )

    if not _has(state, target, "EXTRA"):
        return _issue(
            "EXTRA_TARGET_MISSING", f"{target} is not available in Extra Deck",
            IssueOwner.MODEL, ProofStatus.FAILED, line_id=line_id, card_name=target,
        )

    overlay_zone = f"OVERLAY:{target.upper()}" if kind == "XYZ_SUMMON" else None
    for m in mats:
        _move(state, m, "FIELD", overlay_zone or "GRAVEYARD", 1)
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
    elif kind in {"SYNCHRO_SUMMON", "XYZ_SUMMON", "LINK_SUMMON"}:
        issue = _evaluate_summon_material_binding(state, action, facts, line_id)
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


# ---- Derived Claims (REQ-CR-023) -------------------------------------------

def _derived_claim_for_line(line, state: "_LineState") -> tuple[DerivedClaim | None, ValidationIssue | None]:
    """Recomputes the line's numeric damage claim from the replay itself
    (never trusts a model-asserted boolean). Certainty is bound to the
    line's own declared certainty, never strengthened."""
    if line.asserted_damage_threshold is None:
        return None, None
    met = state.damage >= line.asserted_damage_threshold
    claim = DerivedClaim(
        claim_id=f"damage-threshold:{line.line_id}",
        line_id=line.line_id,
        description=f"accumulated damage >= {line.asserted_damage_threshold}",
        value=met,
        certainty=line.certainty,
        computed_from=(f"replay:{line.line_id}",),
    )
    if not met:
        return claim, _issue(
            "DERIVED_CLAIM_NOT_MET",
            f"line asserts damage >= {line.asserted_damage_threshold} but replay only reaches {state.damage}",
            IssueOwner.MODEL, ProofStatus.FAILED, line_id=line.line_id,
        )
    return claim, None


def _claim_certainty_issue(claim: DerivedClaim, line) -> ValidationIssue | None:
    """Guards REQ-CR-023 monotonicity: a derived claim can never be reported
    more certain than the line that produced it declared itself to be."""
    if not certainty_at_least_as_strong(line.certainty, claim.certainty):
        return _issue(
            "DERIVED_CLAIM_CERTAINTY_UPGRADE",
            f"claim {claim.claim_id} certainty {claim.certainty.value} exceeds line certainty {line.certainty.value}",
            IssueOwner.RUNTIME, ProofStatus.FAILED, line_id=line.line_id,
        )
    return None


# ---- Backward Proof / Critical Decisions (REQ-CR-022) ---------------------

def compute_backward_requirements(deck: CanonicalDeck) -> tuple[BackwardRequirement, ...]:
    """Static, card-name-free lookahead: if a line's cumulative demand for a
    named resource (CONSUME/REQUIRE consequences plus summon materials)
    exceeds the deck's total compiled copies of it, the action that tips
    demand past supply has a *future* requirement broken by an *earlier*
    demanding action's choice. Flagging this here -- rather than leaving it
    as an undifferentiated forward-replay failure -- is what makes the
    violation backward-traceable to the action that caused it."""
    supply: Counter = Counter()
    for entry in deck.entries:
        supply[entry.facts.canonical_name] += entry.qty

    out: list[BackwardRequirement] = []
    for line in deck.lines:
        demanders: dict[str, list[str]] = defaultdict(list)
        cumulative: Counter = Counter()
        for action in line.actions:
            demanded_this_action: Counter = Counter()
            for mcb in action.consequences:
                if mcb.operator in {"CONSUME", "REQUIRE"} and mcb.subject:
                    demanded_this_action[mcb.subject] += mcb.qty
            if action.kind in {"SYNCHRO_SUMMON", "XYZ_SUMMON", "LINK_SUMMON"}:
                for m in action.materials:
                    demanded_this_action[m] += 1
            for name, qty in demanded_this_action.items():
                cumulative[name] += qty
                demanders[name].append(action.action_id)
                total_supply = supply.get(name, 0)
                if total_supply > 0 and cumulative[name] > total_supply:
                    blocking = demanders[name][-2] if len(demanders[name]) >= 2 else demanders[name][0]
                    out.append(BackwardRequirement(
                        line_id=line.line_id,
                        blocking_action_id=blocking,
                        future_action_id=action.action_id,
                        resource_name=name,
                        message=(
                            f"{name} is demanded {cumulative[name]} time(s) across line {line.line_id} "
                            f"but only {total_supply} copie(s) exist in the deck"
                        ),
                    ))
    return tuple(out)


def compute_critical_decisions(backward: tuple[BackwardRequirement, ...]) -> tuple[CriticalDecision, ...]:
    """Every BackwardRequirement found above is Critical by construction: a
    legal alternative at `blocking_action_id` (demanding less, or a
    different resource) would have changed whether `future_action_id`'s
    requirement can be met."""
    return tuple(
        CriticalDecision(
            line_id=b.line_id, action_id=b.blocking_action_id,
            reason=f"consuming {b.resource_name} here breaks a later requirement in action {b.future_action_id}",
        )
        for b in backward
    )


# ---- Cold Audit (REQ-CR-024) -----------------------------------------------

def _binding_signature(binding) -> str:
    if binding is None:
        return "NONE"
    payload = (
        binding.target_card, binding.summon_kind, binding.aggregate_level_equals_target,
        tuple(
            (g.predicate.kind, g.predicate.type_qualifier, g.predicate.exact_level, g.min_count, g.max_count)
            for g in binding.groups
        ),
    )
    return hashlib.sha256(repr(payload).encode("utf-8")).hexdigest()


def cold_audit_summon_bindings(deck: CanonicalDeck) -> tuple[ColdAuditResult, ...]:
    """Independently re-derives each summon's material binding straight from
    evidence (bypassing the already-compiled action.summon_binding) and
    compares signatures. Never trusts the primary binding's own status."""
    facts = _facts_map(deck)
    out: list[ColdAuditResult] = []
    for line in deck.lines:
        for action in line.actions:
            if action.kind not in {"SYNCHRO_SUMMON", "XYZ_SUMMON", "LINK_SUMMON"} or not action.card_name:
                continue
            cold = _compiler.build_summon_material_binding(action.card_name, action.kind, facts)
            primary_sig = _binding_signature(action.summon_binding)
            cold_sig = _binding_signature(cold)
            out.append(ColdAuditResult(
                line_id=line.line_id, action_id=action.action_id,
                primary_signature=primary_sig, cold_signature=cold_sig,
                agrees=(primary_sig == cold_sig),
            ))
    return tuple(out)


def validate_combo_lines(deck: CanonicalDeck, *, semantic_audit: Mapping[str, bool] | None = None) -> ValidationReport:
    semantic_audit = semantic_audit or {}
    facts = _facts_map(deck)
    issues: list[ValidationIssue] = []
    trace: list[StateSnapshot] = []
    derived_claims: list[DerivedClaim] = []

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
        line_failed = False
        for action in line.actions:
            before = _snapshot(state, label=f"BEFORE:{action.action_id}", action_id=action.action_id)
            issue = _execute_action(state, action, facts, semantic_audit, line.line_id)
            after = _snapshot(state, label=f"AFTER:{action.action_id}", action_id=action.action_id)
            trace.append(before)
            trace.append(after)
            if issue is not None:
                issues.append(issue)
                line_failed = True
                break
        if not line_failed:
            claim, claim_issue = _derived_claim_for_line(line, state)
            if claim is not None:
                derived_claims.append(claim)
                certainty_violation = _claim_certainty_issue(claim, line)
                if certainty_violation is not None:
                    issues.append(certainty_violation)
                elif claim_issue is not None:
                    issues.append(claim_issue)

    backward_requirements = compute_backward_requirements(deck)
    critical_decisions = compute_critical_decisions(backward_requirements)
    for backward in backward_requirements:
        issues.append(_issue(
            "BACKWARD_REQUIREMENT_VIOLATION", backward.message,
            IssueOwner.MODEL, ProofStatus.FAILED, line_id=backward.line_id,
        ))

    cold_audit = cold_audit_summon_bindings(deck)
    for cold_result in cold_audit:
        if not cold_result.agrees:
            issues.append(_issue(
                "COLD_AUDIT_DIVERGENCE",
                f"cold recomputation diverges from the primary binding for action {cold_result.action_id}",
                IssueOwner.RUNTIME, ProofStatus.UNVERIFIED, line_id=cold_result.line_id,
            ))

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
        derived_claims=tuple(derived_claims),
        critical_decisions=critical_decisions,
        cold_audit=cold_audit,
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
        derived_claims=combos.derived_claims,
        critical_decisions=combos.critical_decisions,
        cold_audit=combos.cold_audit,
    )
