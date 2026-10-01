"""Deterministic, network-free fixtures for G0..G9 tests. tests/** is MAY-TOUCH."""
from __future__ import annotations

from _bootstrap import use_worktree_source

use_worktree_source()

from contracts import (  # noqa: E402
    BuildContext, BuildRequest, CanonicalAction, CanonicalCardEntry, CanonicalDeck,
    CardFacts, Certainty, CompiledLine, DeckSection,
)
from compiler import build_summon_material_binding  # noqa: E402


def make_facts(
    name: str,
    card_type: str,
    *,
    level: int | None = None,
    rank: int | None = None,
    linkval: int | None = None,
    scale: int | None = None,
    effect_text: str = "",
    atk: int | None = None,
    defense: int | None = None,
) -> CardFacts:
    return CardFacts(
        canonical_name=name,
        external_id=None,
        card_type=card_type,
        level=level,
        rank=rank,
        linkval=linkval,
        scale=scale,
        atk=atk,
        defense=defense,
        effect_text=effect_text,
        provider="FIXTURE",
        source_locator="fixture://g0",
        fetched_at="2026-10-01T00:00:00+00:00",
        payload_sha256="0" * 64,
        environment_compatibility="CURRENT_TEXT_UNCHECKED",
    )


# ---- Quasar fixture set (RED-QUASAR-UNSUPPORTED / RED-QUASAR-INVALID) -----
# Shooting Quasar Dragon's real material clause is NOT the generic
# "1 Tuner + 1+ non-Tuner monsters" header: it requires the non-Tuner
# materials to themselves be Synchro Monsters, and allows 2 or more of them.
QUASAR_FACTS = make_facts(
    "Shooting Quasar Dragon",
    "Synchro Effect Monster",
    level=12,
    atk=4000,
    defense=4000,
    effect_text=(
        "1 Tuner + 2 or more non-Tuner Synchro Monsters\n"
        "(While face-up on the field, equip effects negated.)"
    ),
)
FORMULA_SYNCHRON_FACTS = make_facts(
    "Formula Synchron", "Synchro Tuner Effect Monster", level=2, atk=200, defense=1500,
    effect_text="When this card is Synchro Summoned: Draw 1 card.",
)
CLEAR_WING_FACTS = make_facts(
    "Clear Wing Synchro Dragon", "Synchro Effect Monster", level=7, atk=2500, defense=2000,
    effect_text="Once per turn, this card gains the ability to negate a trap.",
)
CRYSTAL_WING_FACTS = make_facts(
    "Crystal Wing Synchro Dragon", "Synchro Effect Monster", level=3, atk=2000, defense=2100,
    effect_text="Once per turn, this card can destroy a Spell/Trap Card.",
)
# A non-Synchro, non-Tuner monster: would satisfy the OLD unqualified generic
# pattern but must NOT satisfy Quasar's "non-Tuner Synchro Monsters" predicate.
PLAIN_NON_TUNER_FACTS = make_facts(
    "Plain Beater", "Normal Monster", level=10, atk=2400, defense=2000,
    effect_text="A vanilla beatstick.",
)

QUASAR_MATERIAL_FACTS = {
    f.canonical_name: f
    for f in (QUASAR_FACTS, FORMULA_SYNCHRON_FACTS, CLEAR_WING_FACTS, CRYSTAL_WING_FACTS, PLAIN_NON_TUNER_FACTS)
}


def quasar_synchro_action(materials: tuple[str, ...]) -> CanonicalAction:
    binding = build_summon_material_binding(
        QUASAR_FACTS.canonical_name, "SYNCHRO_SUMMON", {QUASAR_FACTS.canonical_name: QUASAR_FACTS},
    )
    return CanonicalAction(
        action_id="action-quasar-synchro",
        label="Synchro Summon Shooting Quasar Dragon",
        kind="SYNCHRO_SUMMON",
        card_name="Shooting Quasar Dragon",
        materials=materials,
        consequences=(),
        certainty=Certainty.GUARANTEED,
        summon_binding=binding,
    )


def make_context(
    *,
    direction: str | None = "Canonique",
    forbidden_mode: bool = False,
    allowed_mechanics: tuple[str, ...] = ("Synchro", "Xyz", "Link", "Pendulum"),
    forbidden_mechanics: tuple[str, ...] = (),
) -> BuildContext:
    request = BuildRequest(
        user_prompt="fixture",
        character="Fixture",
        era="VRAINS",
        direction=direction,
        forbidden_mode=forbidden_mode,
    )
    return BuildContext(
        request=request,
        environment_id="link_evolution_2020",
        allowed_mechanics=allowed_mechanics,
        forbidden_mechanics=forbidden_mechanics,
        policy_source_sha256="0" * 64,
    )


def entry_for(facts: CardFacts, *, qty: int, section: DeckSection, banlist_limit: int = 3) -> CanonicalCardEntry:
    return CanonicalCardEntry(
        card_id=f"card-fixture-{facts.canonical_name}",
        facts=facts,
        qty=qty,
        section=section,
        banlist_limit=banlist_limit,
    )


def build_quasar_deck(
    *,
    materials: tuple[str, ...],
    context: BuildContext | None = None,
    essential: bool = True,
) -> CanonicalDeck:
    """One essential line whose single action is a direct Synchro Summon of
    Shooting Quasar Dragon. Materials are assumed already present on FIELD
    (this fixture isolates the summon-material-binding defect; full
    bring-materials-to-field E2E combo lines are exercised separately at
    G5/G8)."""
    context = context or make_context()
    main_entries = [
        entry_for(FORMULA_SYNCHRON_FACTS, qty=1, section=DeckSection.MAIN),
        entry_for(CLEAR_WING_FACTS, qty=1, section=DeckSection.MAIN),
        entry_for(CRYSTAL_WING_FACTS, qty=1, section=DeckSection.MAIN),
        entry_for(PLAIN_NON_TUNER_FACTS, qty=1, section=DeckSection.MAIN),
    ]
    filler = make_facts("Filler Vanilla", "Normal Monster", level=4, atk=1200, defense=1200)
    for i in range(36):
        main_entries.append(CanonicalCardEntry(
            card_id=f"card-fixture-filler-{i}", facts=filler, qty=1, section=DeckSection.MAIN, banlist_limit=3,
        ))
    extra_entries = [entry_for(QUASAR_FACTS, qty=1, section=DeckSection.EXTRA)]

    line = CompiledLine(
        line_id="line-quasar",
        title="Quasar line",
        starters=(),
        actions=(quasar_synchro_action(materials),),
        claim="Shooting Quasar Dragon is Synchro Summoned.",
        certainty=Certainty.GUARANTEED,
        essential=essential,
    )
    return CanonicalDeck(
        deck_id="deck-fixture-quasar",
        source_hash="0" * 64,
        context=context,
        direction=context.request.direction or "Canonique",
        concept="Quasar fixture",
        entries=tuple(main_entries + extra_entries),
        lines=(line,),
        axes=("Synchro",),
        narrative_summary="fixture",
    )
