"""G5 — Action legality + generic summon/material binding + Quasar (T5,
REQ-CR-015/018/019). This is the chantier's headline fix: Shooting Quasar
Dragon's real material clause ("1 Tuner + 2 or more non-Tuner Synchro
Monsters") must be PROVED when materials are legitimate and FAILED when
they are not -- through the generic binding path only, with zero
Quasar-named branch anywhere in compiler.py/validator.py.

Run: python3 -m unittest tests.test_g5_summon_material_binding -v
"""
from __future__ import annotations

import unittest

from _bootstrap import use_worktree_source

use_worktree_source()

import validator  # noqa: E402
import compiler  # noqa: E402
from contracts import (  # noqa: E402
    CanonicalAction, CanonicalDeck, Certainty, CompiledLine, DeckSection,
    MechanicalConsequenceBinding, ProofStatus,
)
from _fixtures import (  # noqa: E402
    CLEAR_WING_FACTS, CRYSTAL_WING_FACTS, FORMULA_SYNCHRON_FACTS, PLAIN_NON_TUNER_FACTS,
    QUASAR_FACTS, entry_for, make_context, make_facts, quasar_synchro_action,
)


def _state_with_materials(materials):
    state = validator._LineState()
    for facts in materials:
        state.zones["FIELD"][facts.canonical_name] += 1
    state.zones["EXTRA"][QUASAR_FACTS.canonical_name] += 1
    return state


def _facts_map(*extra):
    out = {f.canonical_name: f for f in (QUASAR_FACTS, FORMULA_SYNCHRON_FACTS, CLEAR_WING_FACTS, CRYSTAL_WING_FACTS, PLAIN_NON_TUNER_FACTS)}
    for f in extra:
        out[f.canonical_name] = f
    return out


class GreenQuasarValidIsProved(unittest.TestCase):
    """REQ-CR-019 mandatory GREEN: 1 Tuner (Formula Synchron, Lv2) + 2
    non-Tuner Synchro Monsters (Clear Wing Lv7, Crystal Wing Lv3; sum=12)
    satisfies Shooting Quasar Dragon's real clause and is PROVED."""

    def test_valid_quasar_line_is_proved_with_no_hardcoded_card_branch(self):
        materials = (
            FORMULA_SYNCHRON_FACTS.canonical_name,
            CLEAR_WING_FACTS.canonical_name,
            CRYSTAL_WING_FACTS.canonical_name,
        )
        state = _state_with_materials([FORMULA_SYNCHRON_FACTS, CLEAR_WING_FACTS, CRYSTAL_WING_FACTS])
        action = quasar_synchro_action(materials)
        self.assertIsNotNone(action.summon_binding, "compiler must have derived a binding from the real clause")
        self.assertEqual(action.summon_binding.interpretation_origin, "DERIVED_GENERIC_GRAMMAR")
        issue = validator._evaluate_summon_material_binding(state, action, _facts_map(), "line-quasar")
        self.assertIsNone(issue, f"expected PROVED, got {issue}")
        self.assertEqual(state.zones["FIELD"][QUASAR_FACTS.canonical_name], 1)

    def test_no_quasar_named_branch_exists_in_source(self):
        import pathlib
        for path in (
            pathlib.Path(__file__).resolve().parents[1] / "worktree" / "source" / "validator.py",
            pathlib.Path(__file__).resolve().parents[1] / "worktree" / "source" / "compiler.py",
        ):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("quasar", text.lower(), f"{path.name} must contain no Quasar-specific logic")


class RedQuasarInvalidFails(unittest.TestCase):
    """REQ-CR-019 mandatory RED (symmetric positive control): materials that
    do NOT satisfy the real clause must FAIL, not silently pass."""

    def test_non_synchro_non_tuner_material_is_rejected(self):
        materials = (
            FORMULA_SYNCHRON_FACTS.canonical_name,
            CLEAR_WING_FACTS.canonical_name,
            PLAIN_NON_TUNER_FACTS.canonical_name,  # not a Synchro Monster
        )
        state = _state_with_materials([FORMULA_SYNCHRON_FACTS, CLEAR_WING_FACTS, PLAIN_NON_TUNER_FACTS])
        action = quasar_synchro_action(materials)
        issue = validator._evaluate_summon_material_binding(state, action, _facts_map(), "line-quasar")
        self.assertIsNotNone(issue)
        self.assertEqual(issue.code, "SUMMON_MATERIAL_RULE")
        self.assertNotEqual(issue.code, "SYNCHRO_REQUIREMENT_UNSUPPORTED", "must fail on the rule, not on parsing")

    def test_insufficient_non_tuner_count_is_rejected(self):
        materials = (FORMULA_SYNCHRON_FACTS.canonical_name, CLEAR_WING_FACTS.canonical_name)  # only 1 non-Tuner, need 2+
        state = _state_with_materials([FORMULA_SYNCHRON_FACTS, CLEAR_WING_FACTS])
        action = quasar_synchro_action(materials)
        issue = validator._evaluate_summon_material_binding(state, action, _facts_map(), "line-quasar")
        self.assertIsNotNone(issue)
        self.assertEqual(issue.code, "SUMMON_MATERIAL_RULE")

    def test_wrong_level_sum_is_rejected(self):
        wrong_level_card = make_facts("Off Level Synchro", "Synchro Effect Monster", level=1)
        materials = (FORMULA_SYNCHRON_FACTS.canonical_name, CLEAR_WING_FACTS.canonical_name, wrong_level_card.canonical_name)
        state = _state_with_materials([FORMULA_SYNCHRON_FACTS, CLEAR_WING_FACTS, wrong_level_card])
        action = quasar_synchro_action(materials)
        issue = validator._evaluate_summon_material_binding(
            state, action, _facts_map(wrong_level_card), "line-quasar",
        )
        self.assertIsNotNone(issue)
        self.assertEqual(issue.code, "SYNCHRO_LEVEL_SUM")


class GreenGenericGrammarCoversXyzAndLink(unittest.TestCase):
    """The same generic evaluator must still correctly prove Xyz/Link summons
    that worked before the refactor (regression guard, no capability lost)."""

    def test_xyz_summon_still_works(self):
        target = make_facts("Rank Four Xyz", "Xyz Effect Monster", rank=4, effect_text="2 Level 4 monsters")
        mat_a = make_facts("Xyz Mat A", "Normal Monster", level=4)
        mat_b = make_facts("Xyz Mat B", "Normal Monster", level=4)
        facts = {f.canonical_name: f for f in (target, mat_a, mat_b)}
        binding = compiler.build_summon_material_binding(target.canonical_name, "XYZ_SUMMON", facts)
        state = validator._LineState()
        state.zones["FIELD"][mat_a.canonical_name] += 1
        state.zones["FIELD"][mat_b.canonical_name] += 1
        state.zones["EXTRA"][target.canonical_name] += 1
        action = CanonicalAction(
            action_id="a", label="xyz", kind="XYZ_SUMMON", card_name=target.canonical_name,
            materials=(mat_a.canonical_name, mat_b.canonical_name), consequences=(),
            certainty=Certainty.GUARANTEED, summon_binding=binding,
        )
        issue = validator._evaluate_summon_material_binding(state, action, facts, "line-x")
        self.assertIsNone(issue)
        self.assertEqual(state.zones[f"OVERLAY:{target.canonical_name.upper()}"][mat_a.canonical_name], 1)

    def test_link_summon_with_effect_qualifier_still_works(self):
        target = make_facts("Two Effect Link", "Link Effect Monster", linkval=2, effect_text="2 Effect monsters")
        mat_a = make_facts("Link Mat A", "Effect Monster", level=4)
        mat_b = make_facts("Link Mat B", "Effect Monster", level=4)
        facts = {f.canonical_name: f for f in (target, mat_a, mat_b)}
        binding = compiler.build_summon_material_binding(target.canonical_name, "LINK_SUMMON", facts)
        state = validator._LineState()
        state.zones["FIELD"][mat_a.canonical_name] += 1
        state.zones["FIELD"][mat_b.canonical_name] += 1
        state.zones["EXTRA"][target.canonical_name] += 1
        action = CanonicalAction(
            action_id="a", label="link", kind="LINK_SUMMON", card_name=target.canonical_name,
            materials=(mat_a.canonical_name, mat_b.canonical_name), consequences=(),
            certainty=Certainty.GUARANTEED, summon_binding=binding,
        )
        issue = validator._evaluate_summon_material_binding(state, action, facts, "line-l")
        self.assertIsNone(issue)

    def test_link_material_requiring_non_effect_type_is_rejected(self):
        target = make_facts("Two Effect Link", "Link Effect Monster", linkval=2, effect_text="2 Effect monsters")
        mat_a = make_facts("Link Mat A", "Effect Monster", level=4)
        mat_b = make_facts("Vanilla Mat", "Normal Monster", level=4)  # not an Effect Monster
        facts = {f.canonical_name: f for f in (target, mat_a, mat_b)}
        binding = compiler.build_summon_material_binding(target.canonical_name, "LINK_SUMMON", facts)
        state = validator._LineState()
        state.zones["FIELD"][mat_a.canonical_name] += 1
        state.zones["FIELD"][mat_b.canonical_name] += 1
        state.zones["EXTRA"][target.canonical_name] += 1
        action = CanonicalAction(
            action_id="a", label="link", kind="LINK_SUMMON", card_name=target.canonical_name,
            materials=(mat_a.canonical_name, mat_b.canonical_name), consequences=(),
            certainty=Certainty.GUARANTEED, summon_binding=binding,
        )
        issue = validator._evaluate_summon_material_binding(state, action, facts, "line-l")
        self.assertIsNotNone(issue)
        self.assertEqual(issue.code, "SUMMON_MATERIAL_RULE")


class RedUnparseableClauseIsRuntimeNotIllegal(unittest.TestCase):
    """A clause the generic grammar genuinely cannot parse must surface as
    RUNTIME/UNVERIFIED (room for semantic interpretation later), never as a
    MODEL/FAILED business illegality."""

    def test_unparseable_clause_yields_runtime_unverified(self):
        target = make_facts(
            "Exotic Synchro", "Synchro Effect Monster", level=8,
            effect_text="You can Synchro Summon this card using any monsters you control as material.",
        )
        binding = compiler.build_summon_material_binding(
            target.canonical_name, "SYNCHRO_SUMMON", {target.canonical_name: target},
        )
        self.assertIsNone(binding, "grammar must not guess an unknown clause shape")
        mat = make_facts("Any Mat", "Normal Monster", level=8)
        state = validator._LineState()
        state.zones["FIELD"][mat.canonical_name] += 1
        state.zones["EXTRA"][target.canonical_name] += 1
        action = CanonicalAction(
            action_id="a", label="s", kind="SYNCHRO_SUMMON", card_name=target.canonical_name,
            materials=(mat.canonical_name,), consequences=(), certainty=Certainty.GUARANTEED,
            summon_binding=binding,
        )
        issue = validator._evaluate_summon_material_binding(
            state, action, {target.canonical_name: target, mat.canonical_name: mat}, "line-x",
        )
        self.assertIsNotNone(issue)
        self.assertEqual(issue.code, "SUMMON_MATERIAL_BINDING_UNRESOLVED")
        self.assertEqual(issue.owner.value, "RUNTIME")
        self.assertEqual(issue.proof_status.value, "UNVERIFIED")


class GreenQuasarEndToEnd(unittest.TestCase):
    """G5/G8 mandatory E2E: the full validate_combo_lines pipeline, from
    starters through material-arrival effects to the Synchro Summon action,
    proves a legitimate Quasar line end to end."""

    def test_full_line_proves_quasar_through_validate_combo_lines(self):
        filler = make_facts("Filler Vanilla", "Normal Monster", level=4, effect_text="")
        entries = [
            entry_for(FORMULA_SYNCHRON_FACTS, qty=1, section=DeckSection.MAIN),
            entry_for(CLEAR_WING_FACTS, qty=1, section=DeckSection.MAIN),
            entry_for(CRYSTAL_WING_FACTS, qty=1, section=DeckSection.MAIN),
            entry_for(QUASAR_FACTS, qty=1, section=DeckSection.EXTRA),
        ]
        materials = (
            FORMULA_SYNCHRON_FACTS.canonical_name, CLEAR_WING_FACTS.canonical_name, CRYSTAL_WING_FACTS.canonical_name,
        )

        def _arrive_on_field(name: str, action_id: str) -> CanonicalAction:
            return CanonicalAction(
                action_id=action_id, label=f"{name} arrives", kind="ACTIVATE_EFFECT", card_name=name,
                materials=(), certainty=Certainty.GUARANTEED,
                consequences=(MechanicalConsequenceBinding(operator="MOVE", subject=name, source="HAND", destination="FIELD", qty=1),),
            )

        actions = [_arrive_on_field(name, f"arrive-{i}") for i, name in enumerate(materials)]
        actions.append(quasar_synchro_action(materials))
        line = CompiledLine(
            line_id="line-quasar-e2e", title="Quasar E2E", starters=materials, actions=tuple(actions),
            claim="Shooting Quasar Dragon is Synchro Summoned.", certainty=Certainty.GUARANTEED, essential=True,
        )
        # effect_text must be non-empty for the audit gate; these fixtures already carry one.
        deck = CanonicalDeck(
            deck_id="d", source_hash="0" * 64, context=make_context(), direction="Canonique",
            concept="c", entries=tuple(entries), lines=(line,), axes=("Synchro",), narrative_summary="",
        )
        semantic_audit = {a.action_id: True for a in actions}
        report = validator.validate_combo_lines(deck, semantic_audit=semantic_audit)
        self.assertEqual(report.status, ProofStatus.PROVED, report.issues)
        self.assertTrue(report.combos_passed)


if __name__ == "__main__":
    unittest.main()
