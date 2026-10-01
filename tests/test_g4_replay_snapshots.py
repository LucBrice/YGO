"""G4 — Resource replay / BEFORE-AFTER snapshots (T4, REQ-CR-017).

Run: python3 -m unittest tests.test_g4_replay_snapshots -v
"""
from __future__ import annotations

import unittest

from _bootstrap import use_worktree_source

use_worktree_source()

import validator  # noqa: E402
from contracts import (  # noqa: E402
    CanonicalAction, Certainty, MechanicalConsequenceBinding, ProofStatus,
)
from _fixtures import make_context, make_facts  # noqa: E402
from contracts import CanonicalDeck, CompiledLine  # noqa: E402


def _obtain_action(action_id: str, subject: str, *, src="DECK", dst="HAND", qty=1) -> CanonicalAction:
    return CanonicalAction(
        action_id=action_id, label=action_id, kind="ACTIVATE_EFFECT", card_name=subject,
        materials=(), certainty=Certainty.GUARANTEED,
        consequences=(MechanicalConsequenceBinding(
            operator="MOVE", subject=subject, source=src, destination=dst, qty=qty,
        ),),
    )


def _deck_with_single_line(actions, *, starters=()):
    from _fixtures import entry_for
    from contracts import DeckSection
    card = make_facts("Combo Card", "Normal Monster", level=4, effect_text="Draw 1 card.")
    entries = [entry_for(card, qty=1, section=DeckSection.MAIN)]
    line = CompiledLine(
        line_id="line-1", title="L", starters=starters, actions=tuple(actions),
        claim="c", certainty=Certainty.GUARANTEED, essential=True,
    )
    return CanonicalDeck(
        deck_id="d", source_hash="0" * 64, context=make_context(), direction="Canonique",
        concept="c", entries=tuple(entries), lines=(line,), axes=("control",), narrative_summary="",
    )


class RedDoubleSpend(unittest.TestCase):
    def test_consuming_the_same_resource_twice_is_rejected(self):
        card = make_facts("Combo Card", "Normal Monster", level=4)
        deck = _deck_with_single_line([
            _obtain_action("a1", card.canonical_name, src="DECK", dst="HAND", qty=1),
            _obtain_action("a2", card.canonical_name, src="DECK", dst="HAND", qty=1),
        ])
        report = validator.validate_combo_lines(deck, semantic_audit={"a1": True, "a2": True})
        self.assertEqual(report.status, ProofStatus.FAILED)
        codes = [i.code for i in report.issues]
        self.assertIn("RESOURCE_CONSERVATION", codes)


class RedUseBeforeProduce(unittest.TestCase):
    def test_consuming_a_resource_before_it_is_produced_is_rejected(self):
        card = make_facts("Combo Card", "Normal Monster", level=4)
        deck = _deck_with_single_line([
            # try to move it FIELD->HAND before anything ever put it on FIELD
            _obtain_action("a1", card.canonical_name, src="FIELD", dst="HAND", qty=1),
        ])
        report = validator.validate_combo_lines(deck, semantic_audit={"a1": True, "a2": True})
        self.assertEqual(report.status, ProofStatus.FAILED)
        self.assertEqual(report.issues[0].code, "RESOURCE_CONSERVATION")


class GreenBeforeAfterNotConflated(unittest.TestCase):
    """RED-BEFORE-AFTER positive control: the BEFORE snapshot taken for an
    action must never already reflect that action's own effect."""

    def test_before_snapshot_precedes_the_mutation_it_captures(self):
        card = make_facts("Combo Card", "Normal Monster", level=4)
        deck = _deck_with_single_line([
            _obtain_action("a1", card.canonical_name, src="DECK", dst="HAND", qty=1),
        ])
        report = validator.validate_combo_lines(deck, semantic_audit={"a1": True, "a2": True})
        self.assertEqual(report.status, ProofStatus.PROVED)
        before = next(s for s in report.replay_trace if s.label == "BEFORE:a1")
        after = next(s for s in report.replay_trace if s.label == "AFTER:a1")
        self.assertEqual(before.zones.get("DECK", {}).get(card.canonical_name), 1)
        self.assertEqual(before.zones.get("HAND", {}).get(card.canonical_name, 0), 0)
        self.assertEqual(after.zones.get("DECK", {}).get(card.canonical_name, 0), 0)
        self.assertEqual(after.zones.get("HAND", {}).get(card.canonical_name), 1)

    def test_snapshots_are_immutable_mappingproxy(self):
        from types import MappingProxyType
        card = make_facts("Combo Card", "Normal Monster", level=4)
        deck = _deck_with_single_line([
            _obtain_action("a1", card.canonical_name, src="DECK", dst="HAND", qty=1),
        ])
        report = validator.validate_combo_lines(deck, semantic_audit={"a1": True, "a2": True})
        before = report.replay_trace[0]
        self.assertIsInstance(before.zones, MappingProxyType)
        with self.assertRaises(TypeError):
            before.zones["HACK"] = {}


class GreenTraceCoversWholeLine(unittest.TestCase):
    def test_two_actions_produce_four_snapshots(self):
        card = make_facts("Combo Card", "Normal Monster", level=4)
        card2 = make_facts("Second Combo Card", "Normal Monster", level=4)
        from _fixtures import entry_for
        from contracts import DeckSection
        deck = _deck_with_single_line([
            _obtain_action("a1", card.canonical_name, src="DECK", dst="HAND", qty=1),
            CanonicalAction(
                action_id="a2", label="a2", kind="ACTIVATE_EFFECT", card_name=card.canonical_name,
                materials=(), certainty=Certainty.GUARANTEED,
                consequences=(MechanicalConsequenceBinding(
                    operator="DAMAGE_EVENT", subject="", qty=1, value=500,
                ),),
            ),
        ])
        report = validator.validate_combo_lines(deck, semantic_audit={"a1": True, "a2": True})
        self.assertEqual(report.status, ProofStatus.PROVED)
        self.assertEqual(len(report.replay_trace), 4)
        self.assertEqual([s.label for s in report.replay_trace], [
            "BEFORE:a1", "AFTER:a1", "BEFORE:a2", "AFTER:a2",
        ])
        self.assertEqual(report.replay_trace[-1].damage, 500)


if __name__ == "__main__":
    unittest.main()
