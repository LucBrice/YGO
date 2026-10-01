"""G7 — Backward Proof / Critical Decisions / Derived Claims / Cold Audit
(T7, REQ-CR-022/023/024).

Run: python3 -m unittest tests.test_g7_claims_backward_cold_audit -v
"""
from __future__ import annotations

import dataclasses
import unittest

from _bootstrap import use_worktree_source

use_worktree_source()

import compiler  # noqa: E402
import validator  # noqa: E402
from contracts import (  # noqa: E402
    CanonicalAction, CanonicalDeck, Certainty, CompiledLine, DeckSection,
    DerivedClaim, MechanicalConsequenceBinding, ProofStatus,
)
from _fixtures import entry_for, make_context, make_facts  # noqa: E402


_DAMAGE_SOURCE = make_facts("Damage Source Card", "Spell Card", effect_text="Inflict damage to your opponent.")


def _damage_action(action_id: str, amount: int) -> CanonicalAction:
    return CanonicalAction(
        action_id=action_id, label=action_id, kind="ACTIVATE_EFFECT", card_name=_DAMAGE_SOURCE.canonical_name,
        materials=(), certainty=Certainty.GUARANTEED,
        consequences=(MechanicalConsequenceBinding(operator="DAMAGE_EVENT", value=amount),),
    )


def _deck_with_line(line: CompiledLine, entries) -> CanonicalDeck:
    entries = list(entries) + [entry_for(_DAMAGE_SOURCE, qty=1, section=DeckSection.MAIN)]
    return CanonicalDeck(
        deck_id="d", source_hash="0" * 64, context=make_context(), direction="Canonique",
        concept="c", entries=tuple(entries), lines=(line,), axes=("c",), narrative_summary="",
    )


class GreenDerivedClaimMet(unittest.TestCase):
    def test_damage_threshold_met_yields_true_claim_and_proved(self):
        line = CompiledLine(
            line_id="L", title="t", starters=(), actions=(_damage_action("a1", 500),),
            claim="deals 500", certainty=Certainty.GUARANTEED, essential=True,
            asserted_damage_threshold=500,
        )
        deck = _deck_with_line(line, [])
        report = validator.validate_combo_lines(deck, semantic_audit={"a1": True})
        self.assertEqual(report.status, ProofStatus.PROVED, report.issues)
        self.assertEqual(len(report.derived_claims), 1)
        claim = report.derived_claims[0]
        self.assertTrue(claim.value)
        self.assertEqual(claim.certainty, Certainty.GUARANTEED)


class RedCertaintyNotStrengthenedThroughFullWiring(unittest.TestCase):
    """Integration-level companion to RedCertaintyMonotonicity: a mutation
    check (disabling line.certainty binding in _derived_claim_for_line,
    forcing GUARANTEED unconditionally) proved the unit-level guard test
    alone does not exercise the real validate_combo_lines wiring end to
    end, since every other G7 fixture happened to use a GUARANTEED line.
    This closes that gap with a CONDITIONAL line."""

    def test_conditional_line_claim_stays_conditional_through_validate_combo_lines(self):
        line = CompiledLine(
            line_id="L", title="t", starters=(), actions=(_damage_action("a1", 500),),
            claim="probably reaches lethal", certainty=Certainty.CONDITIONAL, essential=True,
            asserted_damage_threshold=500,
        )
        deck = _deck_with_line(line, [])
        report = validator.validate_combo_lines(deck, semantic_audit={"a1": True})
        self.assertEqual(report.status, ProofStatus.PROVED, report.issues)
        self.assertEqual(len(report.derived_claims), 1)
        self.assertEqual(
            report.derived_claims[0].certainty, Certainty.CONDITIONAL,
            "a CONDITIONAL line's derived claim must never be reported as GUARANTEED",
        )


class RedDerivedClaimNotMet(unittest.TestCase):
    def test_damage_threshold_not_met_fails_closed(self):
        line = CompiledLine(
            line_id="L", title="t", starters=(), actions=(_damage_action("a1", 400),),
            claim="deals 1000", certainty=Certainty.GUARANTEED, essential=True,
            asserted_damage_threshold=1000,
        )
        deck = _deck_with_line(line, [])
        report = validator.validate_combo_lines(deck, semantic_audit={"a1": True})
        self.assertEqual(report.status, ProofStatus.FAILED)
        codes = [i.code for i in report.issues]
        self.assertIn("DERIVED_CLAIM_NOT_MET", codes)
        self.assertFalse(report.derived_claims[0].value)


class RedCertaintyMonotonicity(unittest.TestCase):
    """REQ-CR-023: a claim can never be reported more certain than the line
    that produced it declared itself to be."""

    def test_upgraded_certainty_is_rejected(self):
        line = CompiledLine(
            line_id="L", title="t", starters=(), actions=(), claim="c",
            certainty=Certainty.CONDITIONAL, essential=True,
        )
        bad_claim = DerivedClaim(
            claim_id="x", line_id="L", description="d", value=True,
            certainty=Certainty.GUARANTEED, computed_from=(),
        )
        issue = validator._claim_certainty_issue(bad_claim, line)
        self.assertIsNotNone(issue)
        self.assertEqual(issue.code, "DERIVED_CLAIM_CERTAINTY_UPGRADE")

    def test_matching_certainty_is_accepted(self):
        line = CompiledLine(
            line_id="L", title="t", starters=(), actions=(), claim="c",
            certainty=Certainty.CONDITIONAL, essential=True,
        )
        claim = DerivedClaim(
            claim_id="x", line_id="L", description="d", value=True,
            certainty=Certainty.CONDITIONAL, computed_from=(),
        )
        self.assertIsNone(validator._claim_certainty_issue(claim, line))


class RedBackwardRequirementUndetectedBefore(unittest.TestCase):
    """RED-BACKWARD-FUTURE: an upstream action's consumption silently kills a
    later action's requirement for the same resource. Flagged and attributed
    to the earlier action, promoted to a CriticalDecision."""

    def test_two_consumers_one_copy_flags_backward_requirement(self):
        card = make_facts("Single Copy Card", "Normal Monster", level=4, effect_text="x")
        entries = [entry_for(card, qty=1, section=DeckSection.MAIN)]

        def consume_action(action_id):
            return CanonicalAction(
                action_id=action_id, label=action_id, kind="ACTIVATE_EFFECT", card_name=card.canonical_name,
                materials=(), certainty=Certainty.GUARANTEED,
                consequences=(MechanicalConsequenceBinding(operator="CONSUME", subject=card.canonical_name, source="FIELD", destination="GRAVEYARD", qty=1),),
            )

        line = CompiledLine(
            line_id="L", title="t", starters=(), actions=(consume_action("a1"), consume_action("a2")),
            claim="c", certainty=Certainty.GUARANTEED, essential=True,
        )
        deck = _deck_with_line(line, entries)
        backward = validator.compute_backward_requirements(deck)
        self.assertEqual(len(backward), 1)
        self.assertEqual(backward[0].blocking_action_id, "a1")
        self.assertEqual(backward[0].future_action_id, "a2")
        self.assertEqual(backward[0].resource_name, card.canonical_name)

        critical = validator.compute_critical_decisions(backward)
        self.assertEqual(len(critical), 1)
        self.assertEqual(critical[0].action_id, "a1")

        report = validator.validate_combo_lines(deck, semantic_audit={"a1": True})
        self.assertEqual(report.status, ProofStatus.FAILED)
        self.assertIn("BACKWARD_REQUIREMENT_VIOLATION", [i.code for i in report.issues])


class GreenBackwardNoFalsePositive(unittest.TestCase):
    def test_sufficient_supply_raises_nothing(self):
        card = make_facts("Double Copy Card", "Normal Monster", level=4, effect_text="x")
        entries = [entry_for(card, qty=2, section=DeckSection.MAIN)]

        def consume_action(action_id):
            return CanonicalAction(
                action_id=action_id, label=action_id, kind="ACTIVATE_EFFECT", card_name=card.canonical_name,
                materials=(), certainty=Certainty.GUARANTEED,
                consequences=(MechanicalConsequenceBinding(operator="CONSUME", subject=card.canonical_name, source="FIELD", destination="GRAVEYARD", qty=1),),
            )

        line = CompiledLine(
            line_id="L", title="t", starters=(), actions=(consume_action("a1"), consume_action("a2")),
            claim="c", certainty=Certainty.GUARANTEED, essential=True,
        )
        deck = _deck_with_line(line, entries)
        backward = validator.compute_backward_requirements(deck)
        self.assertEqual(backward, ())


class GreenColdAuditAgrees(unittest.TestCase):
    def test_fresh_recomputation_matches_primary_for_a_real_quasar_line(self):
        from _fixtures import build_quasar_deck, FORMULA_SYNCHRON_FACTS, CLEAR_WING_FACTS, CRYSTAL_WING_FACTS
        materials = (FORMULA_SYNCHRON_FACTS.canonical_name, CLEAR_WING_FACTS.canonical_name, CRYSTAL_WING_FACTS.canonical_name)
        deck = build_quasar_deck(materials=materials)
        results = validator.cold_audit_summon_bindings(deck)
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].agrees)


class RedColdAuditDivergence(unittest.TestCase):
    """RED-COLD-DIVERGENCE: if the primary compiled binding were ever mutated
    out of sync with fresh evidence, cold audit must catch it rather than
    trusting the primary binding's own status."""

    def test_mutated_primary_binding_is_detected(self):
        from _fixtures import build_quasar_deck, FORMULA_SYNCHRON_FACTS, CLEAR_WING_FACTS, CRYSTAL_WING_FACTS
        materials = (FORMULA_SYNCHRON_FACTS.canonical_name, CLEAR_WING_FACTS.canonical_name, CRYSTAL_WING_FACTS.canonical_name)
        deck = build_quasar_deck(materials=materials)
        action = deck.lines[0].actions[0]
        corrupted_binding = dataclasses.replace(action.summon_binding, aggregate_level_equals_target=False)
        corrupted_action = dataclasses.replace(action, summon_binding=corrupted_binding)
        corrupted_line = dataclasses.replace(deck.lines[0], actions=(corrupted_action,))
        corrupted_deck = dataclasses.replace(deck, lines=(corrupted_line,))
        results = validator.cold_audit_summon_bindings(corrupted_deck)
        self.assertEqual(len(results), 1)
        self.assertFalse(results[0].agrees)


if __name__ == "__main__":
    unittest.main()
