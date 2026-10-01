from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Sequence


class DeckSection(str, Enum):
    MAIN = "MAIN"
    EXTRA = "EXTRA"
    SIDE = "SIDE"


class Certainty(str, Enum):
    GUARANTEED = "GUARANTEED"
    CONDITIONAL = "CONDITIONAL"
    RANGE = "RANGE"
    RANDOM = "RANDOM"
    UNKNOWN = "UNKNOWN"


_CERTAINTY_RANK = {
    Certainty.GUARANTEED: 4,
    Certainty.RANGE: 3,
    Certainty.CONDITIONAL: 2,
    Certainty.RANDOM: 1,
    Certainty.UNKNOWN: 0,
}


def certainty_at_least_as_strong(value: Certainty, floor: Certainty) -> bool:
    """True if `value` is at least as strong/certain as `floor`."""
    return _CERTAINTY_RANK[value] >= _CERTAINTY_RANK[floor]


class ProofStatus(str, Enum):
    PROVED = "PROVED"
    UNVERIFIED = "UNVERIFIED"
    FAILED = "FAILED"


class IssueOwner(str, Enum):
    MODEL = "MODEL"
    DATA = "DATA"
    RUNTIME = "RUNTIME"


class IssueSeverity(str, Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"


# ---- Model-facing semantic effect interpretation (REQ-CR-003/020) ---------
#
# The model never authors a raw mechanical operator, zone, or technical
# routing field directly. It picks one closed `interpretation_kind`, names
# the semantic subject/qty/evidence-bound parameters, and the compiler
# (compiler.py) deterministically projects that into a
# MechanicalConsequenceBinding (operator/source/destination/...). This is
# the only way REQUIRE/MOVE/CONSUME/PRODUCE/PROPERTY_UPDATE/RESTRICTION_*
# /DAMAGE_EVENT-shaped data can enter the system: compiler-owned, never
# model-writable.
class EffectInterpretationKind(str, Enum):
    # Zone(s) are baked into the kind name itself: the model picks *what
    # happens semantically*, never a free-form source/destination zone.
    REQUIRE_PRESENT_FIELD = "REQUIRE_PRESENT_FIELD"
    REQUIRE_PRESENT_HAND = "REQUIRE_PRESENT_HAND"
    REQUIRE_PRESENT_GRAVEYARD = "REQUIRE_PRESENT_GRAVEYARD"
    OBTAIN_NAMED_FROM_DECK = "OBTAIN_NAMED_FROM_DECK"              # DECK -> HAND
    SPECIAL_SUMMON_FROM_GY = "SPECIAL_SUMMON_FROM_GY"              # GRAVEYARD -> FIELD
    SPECIAL_SUMMON_FROM_HAND = "SPECIAL_SUMMON_FROM_HAND"          # HAND -> FIELD
    SPECIAL_SUMMON_FROM_DECK = "SPECIAL_SUMMON_FROM_DECK"          # DECK -> FIELD
    RETURN_TO_HAND_FROM_FIELD = "RETURN_TO_HAND_FROM_FIELD"        # FIELD -> HAND
    SEND_TO_GRAVEYARD_FROM_FIELD = "SEND_TO_GRAVEYARD_FROM_FIELD"  # FIELD -> GRAVEYARD
    SEND_TO_GRAVEYARD_FROM_HAND = "SEND_TO_GRAVEYARD_FROM_HAND"    # HAND -> GRAVEYARD
    BANISH_FROM_FIELD = "BANISH_FROM_FIELD"                        # FIELD -> BANISHED
    BANISH_FROM_GRAVEYARD = "BANISH_FROM_GRAVEYARD"                # GRAVEYARD -> BANISHED
    MILL_FROM_DECK = "MILL_FROM_DECK"                              # DECK -> GRAVEYARD
    SET_EFFECTIVE_LEVEL = "SET_EFFECTIVE_LEVEL"
    SET_EFFECTIVE_TUNER = "SET_EFFECTIVE_TUNER"
    SET_EFFECTIVE_NAME = "SET_EFFECTIVE_NAME"
    RESTRICT_MECHANIC = "RESTRICT_MECHANIC"
    RELEASE_MECHANIC_RESTRICTION = "RELEASE_MECHANIC_RESTRICTION"
    INFLICT_DAMAGE = "INFLICT_DAMAGE"


@dataclass(frozen=True)
class BuildRequest:
    user_prompt: str
    character: str = ""
    era: str = "VRAINS"
    direction: str | None = None
    forbidden_mode: bool = False
    max_repairs: int = 2
    metadata: Mapping[str, str] = field(default_factory=lambda: MappingProxyType({}))


@dataclass(frozen=True)
class BuildContext:
    request: BuildRequest
    environment_id: str
    allowed_mechanics: tuple[str, ...]
    forbidden_mechanics: tuple[str, ...]
    policy_source_sha256: str


@dataclass(frozen=True)
class CardChoice:
    name: str
    qty: int
    side: bool = False


@dataclass(frozen=True)
class SemanticEffectInterpretation:
    """Model-writable. No operator/source/destination/zone field exists here
    on purpose: those are compiler-derived (see contracts.MechanicalConsequenceBinding
    and compiler.project_mechanical_consequences)."""
    kind: str
    subject: str = ""
    qty: int = 1
    property_name: str | None = None
    value: int | str | bool | None = None
    mechanics: tuple[str, ...] = ()


@dataclass(frozen=True)
class SemanticAction:
    label: str
    kind: str
    card: str | None = None
    materials: tuple[str, ...] = ()
    effects: tuple[SemanticEffectInterpretation, ...] = ()
    certainty: Certainty = Certainty.GUARANTEED


@dataclass(frozen=True)
class SemanticLine:
    title: str
    starters: tuple[str, ...]
    actions: tuple[SemanticAction, ...]
    claim: str
    certainty: Certainty = Certainty.GUARANTEED
    essential: bool = True
    visual_cards: tuple[str, ...] = ()
    # Semantic-only numeric assertion the line's claim makes (e.g. an OTK
    # damage threshold). Recomputed as a DerivedClaim at validation time;
    # the model declares the number, it never declares whether it holds.
    asserted_damage_threshold: int | None = None


@dataclass(frozen=True)
class SemanticDeckDraft:
    direction: str
    concept: str
    cards: tuple[CardChoice, ...]
    lines: tuple[SemanticLine, ...] = ()
    axes: tuple[str, ...] = ()
    narrative_summary: str = ""
    mastered_functions: tuple[str, ...] = ()
    limited_functions: tuple[str, ...] = ()
    potential: int | None = None
    development_level: str = ""
    pilotage_guide: tuple[str, ...] = ()
    breakpoint: str = ""
    signature_cards: tuple[str, ...] = ()
    terminal_quote: str | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class CardFacts:
    canonical_name: str
    external_id: int | None
    card_type: str
    race: str | None = None
    attribute: str | None = None
    level: int | None = None
    rank: int | None = None
    linkval: int | None = None
    scale: int | None = None
    atk: int | None = None
    defense: int | None = None
    effect_text: str = ""
    provider: str = ""
    source_locator: str = ""
    fetched_at: str = ""
    payload_sha256: str = ""
    environment_compatibility: str = "CURRENT_TEXT_UNCHECKED"


@dataclass(frozen=True)
class CanonicalCardEntry:
    card_id: str
    facts: CardFacts
    qty: int
    section: DeckSection
    banlist_limit: int


# ---- Compiler-owned proof data (never model-writable) ----------------------

@dataclass(frozen=True)
class MechanicalConsequenceBinding:
    """MCB. Compiler-owned projection of a SemanticEffectInterpretation.
    Structurally what used to be model-authored; now only compiler.py may
    construct one."""
    operator: str
    subject: str = ""
    source: str | None = None
    destination: str | None = None
    qty: int = 1
    scope: str = "SINGLE"
    property_name: str | None = None
    value: int | str | bool | None = None
    params: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))


@dataclass(frozen=True)
class MaterialPredicate:
    """Generic, card-name-free material requirement predicate."""
    kind: str  # "TUNER" | "NON_TUNER" | "ANY"
    type_qualifier: str | None = None  # e.g. "Synchro", "Effect"; None = unqualified
    exact_level: int | None = None     # Xyz-style: all group members share this Level/Rank


@dataclass(frozen=True)
class MaterialGroup:
    predicate: MaterialPredicate
    min_count: int
    max_count: int | None  # None = unbounded ("or more")


@dataclass(frozen=True)
class SummonMaterialBinding:
    """Generic summon/material binding (REQ-CR-019). No named-card branch:
    `target_card` and `groups` are the only card-specific data, and they are
    always derived from evidence (CardFacts.effect_text), never hardcoded."""
    target_card: str
    summon_kind: str
    groups: tuple[MaterialGroup, ...]
    aggregate_level_equals_target: bool = False
    source_evidence_locator: str = ""
    interpretation_origin: str = "DERIVED_GENERIC_GRAMMAR"


@dataclass(frozen=True)
class CanonicalAction:
    action_id: str
    label: str
    kind: str
    card_name: str | None
    materials: tuple[str, ...]
    # Compiler-derived MechanicalConsequenceBinding tuple. Field name kept as
    # `consequences` (not renamed) so validator.py's existing attribute
    # access stays valid untouched: validator.py is NO-TOUCH for T1 per
    # governance/CHANGE_SURFACE_CONTRACT_CORRECTIVE_ON_V5_V1.md. Only the
    # *model-facing* name changed (SemanticAction.effects); the element type
    # here is MechanicalConsequenceBinding, never model-authored.
    consequences: tuple[MechanicalConsequenceBinding, ...]
    certainty: Certainty
    summon_binding: SummonMaterialBinding | None = None


@dataclass(frozen=True)
class CompiledLine:
    line_id: str
    title: str
    starters: tuple[str, ...]
    actions: tuple[CanonicalAction, ...]
    claim: str
    certainty: Certainty
    essential: bool
    visual_cards: tuple[str, ...] = ()
    asserted_damage_threshold: int | None = None


@dataclass(frozen=True)
class ProofPlan:
    """REQ-CR-016. Content-addressed by semantic_hash + evidence_set_hash +
    context_hash + compiler_schema_version (compiler.PROOF_PLAN_HASH_PARTS
    composes proof_plan_hash from exactly these four). Same semantic source
    and same evidence always yield the same ProofPlan identity; any upstream
    change (semantic edit, CardFacts update, context/authority change, or a
    compiler schema bump) is visible as a hash change, never silently
    absorbed."""
    proof_plan_hash: str
    semantic_hash: str
    evidence_set_hash: str
    context_hash: str
    compiler_schema_version: str
    evidence_refs: tuple[tuple[str, str], ...]  # sorted (canonical_name, payload_sha256)


@dataclass(frozen=True)
class CanonicalDeck:
    deck_id: str
    source_hash: str
    context: BuildContext
    direction: str
    concept: str
    entries: tuple[CanonicalCardEntry, ...]
    lines: tuple[CompiledLine, ...]
    axes: tuple[str, ...]
    narrative_summary: str
    mastered_functions: tuple[str, ...] = ()
    limited_functions: tuple[str, ...] = ()
    potential: int | None = None
    development_level: str = ""
    pilotage_guide: tuple[str, ...] = ()
    breakpoint: str = ""
    signature_cards: tuple[str, ...] = ()
    terminal_quote: str | None = None
    notes: tuple[str, ...] = ()
    proof_plan: ProofPlan | None = None


@dataclass(frozen=True)
class StateSnapshot:
    """Immutable BEFORE/AFTER snapshot (REQ-CR-017)."""
    label: str  # "BEFORE:<action_id>" or "AFTER:<action_id>"
    action_id: str
    zones: Mapping[str, Mapping[str, int]]
    properties: Mapping[str, Any]
    restrictions: tuple[str, ...]
    damage: int


@dataclass(frozen=True)
class ActionLegalityProof:
    """REQ-CR-018. Generic: references bindings/evidence, never re-interprets
    raw card text itself."""
    action_id: str
    binding_signature: str
    participants: tuple[str, ...]
    satisfied: bool
    evaluated_against: str  # BEFORE snapshot label


@dataclass(frozen=True)
class DerivedClaim:
    """REQ-CR-023. Certainty can never exceed the line's declared certainty
    (contracts.certainty_at_least_as_strong enforces monotonicity at the
    validator boundary, not here)."""
    claim_id: str
    line_id: str
    description: str
    value: Any
    certainty: Certainty
    computed_from: tuple[str, ...]


@dataclass(frozen=True)
class BackwardRequirement:
    """REQ-CR-022: an upstream action's resource consumption would make a
    later required action infeasible."""
    line_id: str
    blocking_action_id: str
    future_action_id: str
    resource_name: str
    message: str


@dataclass(frozen=True)
class CriticalDecision:
    """A BackwardRequirement promoted to Critical only when a legal
    alternative at `blocking_action_id` would have preserved future
    viability (REQ-CR-022)."""
    line_id: str
    action_id: str
    reason: str


@dataclass(frozen=True)
class ColdAuditResult:
    """REQ-CR-024: independent recomputation, hash-compared to the primary
    binding; never trusts the primary status."""
    line_id: str
    action_id: str
    primary_signature: str
    cold_signature: str
    agrees: bool


@dataclass(frozen=True)
class ResolutionAttempt:
    """REQ-CR-025 provenance. Runtime/data-owned technical record, never a
    user-facing instruction."""
    route: str
    outcome: str  # "SUCCESS" | "FAILURE"
    error_class: str | None
    timestamp: str
    locator: str | None = None


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    owner: IssueOwner
    proof_status: ProofStatus = ProofStatus.FAILED
    severity: IssueSeverity = IssueSeverity.ERROR
    line_id: str | None = None
    card_name: str | None = None
    data: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))


@dataclass(frozen=True)
class ValidationReport:
    status: ProofStatus
    issues: tuple[ValidationIssue, ...]
    legality_passed: bool
    combos_passed: bool
    publication_allowed: bool
    derived_claims: tuple[DerivedClaim, ...] = ()
    critical_decisions: tuple[CriticalDecision, ...] = ()
    cold_audit: tuple[ColdAuditResult, ...] = ()


@dataclass(frozen=True)
class DeckResult:
    status: ProofStatus
    final_text: str
    deck: CanonicalDeck | None
    report: ValidationReport
    presentation_plan: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))


# ---- Deterministic continuous-run control plane (REQ-CR-027) --------------
# Runtime-only. No field here is ever model-writable; semantic_draft_from_mapping
# never parses or produces a RunState.

class RunPhase(str, Enum):
    RESOLVE_CONTEXT = "RESOLVE_CONTEXT"
    RESOLVE_DATA = "RESOLVE_DATA"
    MODEL_BUILD = "MODEL_BUILD"
    COMPILE = "COMPILE"
    VALIDATE = "VALIDATE"
    ROUTE = "ROUTE"
    MODEL_REPAIR = "MODEL_REPAIR"
    DATA_RECOVER = "DATA_RECOVER"
    BLOCK = "BLOCK"
    PAUSE_FOR_USER = "PAUSE_FOR_USER"
    COLD_AUDIT = "COLD_AUDIT"
    PUBLISH = "PUBLISH"
    TERMINAL = "TERMINAL"


class ModelCallReason(str, Enum):
    INITIAL_SEMANTIC_BUILD = "INITIAL_SEMANTIC_BUILD"
    SEMANTIC_INTERPRETATION_REQUIRED = "SEMANTIC_INTERPRETATION_REQUIRED"
    MODEL_REPAIR_REQUIRED = "MODEL_REPAIR_REQUIRED"
    COLD_SEMANTIC_AUDIT_REQUIRED = "COLD_SEMANTIC_AUDIT_REQUIRED"


@dataclass(frozen=True)
class RunState:
    run_id: str
    phase: RunPhase
    semantic_hash: str | None = None
    evidence_set_hash: str | None = None
    proof_plan_hash: str | None = None
    replay_hash: str | None = None
    model_attempts: int = 0
    data_route_attempts: int = 0
    progress_fingerprint: str | None = None
    issue_fingerprint_history: tuple[str, ...] = ()
    terminal_status: ProofStatus | None = None
    publication_authorized: bool = False
    user_gate: bool = False


_TOP_LEVEL_DRAFT_FIELDS = {
    "direction", "concept", "cards", "lines", "axes", "narrative_summary",
    "mastered_functions", "limited_functions", "potential", "development_level",
    "pilotage_guide", "breakpoint", "signature_cards", "terminal_quote", "notes"
}
_CARD_FIELDS = {"name", "qty", "side"}
_LINE_FIELDS = {
    "title", "starters", "actions", "claim", "certainty", "essential",
    "visual_cards", "asserted_damage_threshold",
}
_ACTION_FIELDS = {"label", "kind", "card", "materials", "effects", "certainty"}
_EFFECT_FIELDS = {"kind", "subject", "qty", "property_name", "value", "mechanics"}

_VALID_EFFECT_KINDS = frozenset(k.value for k in EffectInterpretationKind)

# If any of these appear in model output, the architecture has regressed into
# secretariat: either low-level proof/flow data, or raw mechanical routing
# (operator/source/destination) that must instead be compiler-derived from a
# closed SemanticEffectInterpretation kind. Union of the D3/REQ-CR-020
# anti-secretariat set and the Data Architecture V1 §11 run-control set.
FORBIDDEN_MODEL_FIELDS = frozenset({
    "id", "run_id", "card_id", "line_id", "action_id", "fact_id", "constraint_id",
    "binding", "bindings", "binding_id", "hash", "sha256", "snapshot_sha256",
    "main_count", "extra_count", "side_count", "banlist_status", "legality_status",
    "proof_status", "validation_status", "stale", "freshness", "cache_key",
    "provider_payload_hash", "route", "routing", "publication_allowed",
    # Data Architecture V1 §11
    "phase", "next_stage", "retry", "provider", "publication_authorized",
    "resource_ledger", "before", "after", "mcb", "cache_status",
    "derived_claim_pass",
    # raw mechanical routing (now compiler-owned MCB projection only)
    "operator", "source", "destination", "consequences", "scope", "params",
})


def _as_mapping(value: Any, where: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{where} must be an object")
    return value


def _reject_fields(data: Mapping[str, Any], allowed: set[str], where: str) -> None:
    forbidden = set(data).intersection(FORBIDDEN_MODEL_FIELDS)
    if forbidden:
        raise ValueError(f"{where} contains compiler/runtime-owned fields: {sorted(forbidden)}")
    unknown = set(data) - allowed
    if unknown:
        raise ValueError(f"{where} contains unsupported fields: {sorted(unknown)}")


def _certainty(value: Any) -> Certainty:
    if value is None:
        return Certainty.GUARANTEED
    try:
        return Certainty(str(value).upper())
    except ValueError as exc:
        raise ValueError(f"unsupported certainty: {value!r}") from exc


def _tuple_of_strings(value: Any, where: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str) or not isinstance(value, Sequence):
        raise ValueError(f"{where} must be an array of strings")
    out = tuple(str(item).strip() for item in value)
    if any(not item for item in out):
        raise ValueError(f"{where} contains an empty value")
    return out


def _parse_effect(raw: Any, where: str) -> SemanticEffectInterpretation:
    effect = _as_mapping(raw, where)
    _reject_fields(effect, _EFFECT_FIELDS, where)
    kind = str(effect.get("kind", "")).strip().upper()
    if kind not in _VALID_EFFECT_KINDS:
        raise ValueError(f"{where}.kind must be one of {sorted(_VALID_EFFECT_KINDS)}")
    mechanics = _tuple_of_strings(effect.get("mechanics"), f"{where}.mechanics")
    qty = effect.get("qty", 1)
    if not isinstance(qty, int) or isinstance(qty, bool) or qty < 1:
        raise ValueError(f"{where}.qty must be a positive integer")
    return SemanticEffectInterpretation(
        kind=kind,
        subject=str(effect.get("subject", "")).strip(),
        qty=qty,
        property_name=(str(effect["property_name"]).strip() if effect.get("property_name") is not None else None),
        value=effect.get("value"),
        mechanics=tuple(m.upper() for m in mechanics),
    )


def semantic_draft_from_mapping(raw: Mapping[str, Any]) -> SemanticDeckDraft:
    """Strict model boundary. Unknown/administrative fields fail closed."""
    data = _as_mapping(raw, "draft")
    _reject_fields(data, _TOP_LEVEL_DRAFT_FIELDS, "draft")

    direction = str(data.get("direction", "")).strip()
    concept = str(data.get("concept", "")).strip()
    if not direction or not concept:
        raise ValueError("draft.direction and draft.concept are required")

    cards_raw = data.get("cards")
    if isinstance(cards_raw, (str, bytes)) or not isinstance(cards_raw, Sequence):
        raise ValueError("draft.cards must be an array")
    cards: list[CardChoice] = []
    for idx, item in enumerate(cards_raw):
        card = _as_mapping(item, f"draft.cards[{idx}]")
        _reject_fields(card, _CARD_FIELDS, f"draft.cards[{idx}]")
        name = str(card.get("name", "")).strip()
        qty = card.get("qty")
        if not name or not isinstance(qty, int) or isinstance(qty, bool) or qty < 1 or qty > 3:
            raise ValueError(f"draft.cards[{idx}] requires name and qty 1..3")
        cards.append(CardChoice(name=name, qty=qty, side=bool(card.get("side", False))))

    lines: list[SemanticLine] = []
    lines_raw = data.get("lines", ())
    if isinstance(lines_raw, (str, bytes)) or not isinstance(lines_raw, Sequence):
        raise ValueError("draft.lines must be an array")
    for li, item in enumerate(lines_raw):
        line = _as_mapping(item, f"draft.lines[{li}]")
        _reject_fields(line, _LINE_FIELDS, f"draft.lines[{li}]")
        actions: list[SemanticAction] = []
        actions_raw = line.get("actions", ())
        if isinstance(actions_raw, (str, bytes)) or not isinstance(actions_raw, Sequence):
            raise ValueError(f"draft.lines[{li}].actions must be an array")
        for ai, action_item in enumerate(actions_raw):
            action = _as_mapping(action_item, f"draft.lines[{li}].actions[{ai}]")
            _reject_fields(action, _ACTION_FIELDS, f"draft.lines[{li}].actions[{ai}]")
            effects_raw = action.get("effects", ())
            if isinstance(effects_raw, (str, bytes)) or not isinstance(effects_raw, Sequence):
                raise ValueError(f"draft.lines[{li}].actions[{ai}].effects must be an array")
            effects = tuple(
                _parse_effect(item, f"draft.lines[{li}].actions[{ai}].effects[{ei}]")
                for ei, item in enumerate(effects_raw)
            )
            actions.append(SemanticAction(
                label=str(action.get("label", "")).strip(),
                kind=str(action.get("kind", "")).strip().upper(),
                card=(str(action["card"]).strip() if action.get("card") is not None else None),
                materials=_tuple_of_strings(action.get("materials"), "action.materials"),
                effects=effects,
                certainty=_certainty(action.get("certainty")),
            ))
        asserted_threshold = line.get("asserted_damage_threshold")
        if asserted_threshold is not None and (
            not isinstance(asserted_threshold, int) or isinstance(asserted_threshold, bool) or asserted_threshold < 0
        ):
            raise ValueError(f"draft.lines[{li}].asserted_damage_threshold must be a non-negative integer")
        lines.append(SemanticLine(
            title=str(line.get("title", "")).strip(),
            starters=_tuple_of_strings(line.get("starters"), "line.starters"),
            actions=tuple(actions),
            claim=str(line.get("claim", "")).strip(),
            certainty=_certainty(line.get("certainty")),
            essential=bool(line.get("essential", True)),
            visual_cards=_tuple_of_strings(line.get("visual_cards"), "line.visual_cards"),
            asserted_damage_threshold=asserted_threshold,
        ))

    potential = data.get("potential")
    if potential is not None and (not isinstance(potential, int) or isinstance(potential, bool) or not 1 <= potential <= 10):
        raise ValueError("draft.potential must be an integer 1..10")
    terminal_quote = data.get("terminal_quote")
    if terminal_quote is not None:
        terminal_quote = str(terminal_quote).strip() or None
    return SemanticDeckDraft(
        direction=direction,
        concept=concept,
        cards=tuple(cards),
        lines=tuple(lines),
        axes=_tuple_of_strings(data.get("axes"), "draft.axes"),
        narrative_summary=str(data.get("narrative_summary", "")).strip(),
        mastered_functions=_tuple_of_strings(data.get("mastered_functions"), "draft.mastered_functions"),
        limited_functions=_tuple_of_strings(data.get("limited_functions"), "draft.limited_functions"),
        potential=potential,
        development_level=str(data.get("development_level", "")).strip(),
        pilotage_guide=_tuple_of_strings(data.get("pilotage_guide"), "draft.pilotage_guide"),
        breakpoint=str(data.get("breakpoint", "")).strip(),
        signature_cards=_tuple_of_strings(data.get("signature_cards"), "draft.signature_cards"),
        terminal_quote=terminal_quote,
        notes=_tuple_of_strings(data.get("notes"), "draft.notes"),
    )
