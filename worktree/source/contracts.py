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
class SemanticConsequence:
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
class SemanticAction:
    label: str
    kind: str
    card: str | None = None
    materials: tuple[str, ...] = ()
    consequences: tuple[SemanticConsequence, ...] = ()
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


@dataclass(frozen=True)
class CanonicalAction:
    action_id: str
    label: str
    kind: str
    card_name: str | None
    materials: tuple[str, ...]
    consequences: tuple[SemanticConsequence, ...]
    certainty: Certainty


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


@dataclass(frozen=True)
class DeckResult:
    status: ProofStatus
    final_text: str
    deck: CanonicalDeck | None
    report: ValidationReport
    presentation_plan: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))


_TOP_LEVEL_DRAFT_FIELDS = {
    "direction", "concept", "cards", "lines", "axes", "narrative_summary",
    "mastered_functions", "limited_functions", "potential", "development_level",
    "pilotage_guide", "breakpoint", "signature_cards", "terminal_quote", "notes"
}
_CARD_FIELDS = {"name", "qty", "side"}
_LINE_FIELDS = {"title", "starters", "actions", "claim", "certainty", "essential", "visual_cards"}
_ACTION_FIELDS = {"label", "kind", "card", "materials", "consequences", "certainty"}
_CONSEQUENCE_FIELDS = {
    "operator", "subject", "source", "destination", "qty", "scope",
    "property_name", "value", "params"
}

# If any of these appear in model output, the architecture has regressed into secretariat.
FORBIDDEN_MODEL_FIELDS = frozenset({
    "id", "run_id", "card_id", "line_id", "action_id", "fact_id", "constraint_id",
    "binding", "bindings", "binding_id", "hash", "sha256", "snapshot_sha256",
    "main_count", "extra_count", "side_count", "banlist_status", "legality_status",
    "proof_status", "validation_status", "stale", "freshness", "cache_key",
    "provider_payload_hash", "route", "routing", "publication_allowed",
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
            consequences: list[SemanticConsequence] = []
            cons_raw = action.get("consequences", ())
            if isinstance(cons_raw, (str, bytes)) or not isinstance(cons_raw, Sequence):
                raise ValueError(f"draft.lines[{li}].actions[{ai}].consequences must be an array")
            for ci, consequence_item in enumerate(cons_raw):
                consequence = _as_mapping(
                    consequence_item,
                    f"draft.lines[{li}].actions[{ai}].consequences[{ci}]",
                )
                _reject_fields(
                    consequence,
                    _CONSEQUENCE_FIELDS,
                    f"draft.lines[{li}].actions[{ai}].consequences[{ci}]",
                )
                params = consequence.get("params", {})
                if not isinstance(params, Mapping):
                    raise ValueError("consequence.params must be an object")
                consequences.append(SemanticConsequence(
                    operator=str(consequence.get("operator", "")).strip().upper(),
                    subject=str(consequence.get("subject", "")).strip(),
                    source=(str(consequence["source"]).strip() if consequence.get("source") is not None else None),
                    destination=(str(consequence["destination"]).strip() if consequence.get("destination") is not None else None),
                    qty=int(consequence.get("qty", 1)),
                    scope=str(consequence.get("scope", "SINGLE")).strip().upper(),
                    property_name=(str(consequence["property_name"]).strip() if consequence.get("property_name") is not None else None),
                    value=consequence.get("value"),
                    params=MappingProxyType(dict(params)),
                ))
            actions.append(SemanticAction(
                label=str(action.get("label", "")).strip(),
                kind=str(action.get("kind", "")).strip().upper(),
                card=(str(action["card"]).strip() if action.get("card") is not None else None),
                materials=_tuple_of_strings(action.get("materials"), "action.materials"),
                consequences=tuple(consequences),
                certainty=_certainty(action.get("certainty")),
            ))
        lines.append(SemanticLine(
            title=str(line.get("title", "")).strip(),
            starters=_tuple_of_strings(line.get("starters"), "line.starters"),
            actions=tuple(actions),
            claim=str(line.get("claim", "")).strip(),
            certainty=_certainty(line.get("certainty")),
            essential=bool(line.get("essential", True)),
            visual_cards=_tuple_of_strings(line.get("visual_cards"), "line.visual_cards"),
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
