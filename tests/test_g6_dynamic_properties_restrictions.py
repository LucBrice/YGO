"""G6 — Dynamic material properties + persistent restrictions (T6,
REQ-CR-021).

Run: python3 -m unittest tests.test_g6_dynamic_properties_restrictions -v
"""
from __future__ import annotations

import unittest

from _bootstrap import use_worktree_source

use_worktree_source()

import validator  # noqa: E402
from contracts import CanonicalAction, Certainty, MechanicalConsequenceBinding  # noqa: E402
from _fixtures import make_facts  # noqa: E402


class RedDynamicPropertyLeak(unittest.TestCase):
    """RED-DYNAMIC-PROPERTY, now closed: a level/tuner override must apply
    only while its owner remains on FIELD, and must never leak onto a later
    arrival of a same-named card once the overridden copy has left."""

    def test_level_override_reverts_once_the_card_leaves_field(self):
        facts = {"Morphing Card": make_facts("Morphing Card", "Normal Monster", level=4)}
        state = validator._LineState()
        state.zones["FIELD"]["Morphing Card"] = 1
        state.properties[("Morphing Card", "level")] = 99
        self.assertEqual(validator._effective_level(state, "Morphing Card", facts), 99)
        # the card is sent to the graveyard
        self.assertTrue(validator._move(state, "Morphing Card", "FIELD", "GRAVEYARD", 1))
        self.assertEqual(
            validator._effective_level(state, "Morphing Card", facts), 4,
            "stale override must not leak after the card left FIELD",
        )

    def test_tuner_override_reverts_once_the_card_leaves_field(self):
        facts = {"Card": make_facts("Card", "Normal Monster", level=4)}
        state = validator._LineState()
        state.zones["FIELD"]["Card"] = 1
        state.properties[("Card", "tuner")] = True
        self.assertTrue(validator._effective_tuner(state, "Card", facts))
        self.assertTrue(validator._move(state, "Card", "FIELD", "HAND", 1))
        self.assertFalse(validator._effective_tuner(state, "Card", facts))

    def test_a_fresh_copy_of_the_same_name_does_not_inherit_a_stale_override(self):
        """The scenario the leak made dangerous: card leaves field with an
        override set, a second copy of the identically-named card later
        arrives on field -- it must read base facts, not the stale override.
        Uses validator._move (the engine's own mutation primitive), not raw
        Counter writes, so the departure hook actually fires."""
        facts = {"Card": make_facts("Card", "Normal Monster", level=4)}
        state = validator._LineState()
        state.zones["FIELD"]["Card"] = 1
        state.properties[("Card", "level")] = 99
        self.assertEqual(validator._effective_level(state, "Card", facts), 99)
        self.assertTrue(validator._move(state, "Card", "FIELD", "GRAVEYARD", 1))
        # a second, unrelated copy of the same name arrives on field later
        state.zones["DECK"]["Card"] = 1
        self.assertTrue(validator._move(state, "Card", "DECK", "FIELD", 1))
        self.assertEqual(validator._effective_level(state, "Card", facts), 4)


class GreenEffectiveNameHelper(unittest.TestCase):
    def test_effective_name_override_follows_the_same_lifecycle(self):
        facts = {"Card": make_facts("Card", "Normal Monster", level=4)}
        state = validator._LineState()
        state.zones["FIELD"]["Card"] = 1
        state.properties[("Card", "effective_name")] = "Renamed Card"
        self.assertEqual(validator._effective_name(state, "Card", facts), "Renamed Card")
        self.assertTrue(validator._move(state, "Card", "FIELD", "GRAVEYARD", 1))
        self.assertEqual(validator._effective_name(state, "Card", facts), "Card")


def _restriction_action(action_id, op, mechanics):
    return CanonicalAction(
        action_id=action_id, label=action_id, kind="ACTIVATE_EFFECT", card_name=None,
        materials=(), certainty=Certainty.GUARANTEED,
        consequences=(MechanicalConsequenceBinding(operator=op, params={"forbid_mechanics": mechanics}),),
    )


class GreenRestrictionLifecycle(unittest.TestCase):
    """Newly materialized regression guard (REQ-CR-021): restriction
    apply/block/release/unblock round-trip. Never previously covered by any
    test in this workspace."""

    def test_apply_blocks_then_release_unblocks(self):
        target = make_facts("Target Synchro", "Synchro Effect Monster", level=4, effect_text="1 Tuner + 1+ non-Tuner monsters")
        facts = {target.canonical_name: target}
        state = validator._LineState()
        apply_issue = validator._apply_consequence(
            state, MechanicalConsequenceBinding(operator="RESTRICTION_APPLY", params={"forbid_mechanics": ["SYNCHRO"]}),
            facts, "line-r",
        )
        self.assertIsNone(apply_issue)
        self.assertIn("SYNCHRO", state.restrictions)

        action = CanonicalAction(
            action_id="a", label="try-synchro", kind="SYNCHRO_SUMMON", card_name=target.canonical_name,
            materials=(), consequences=(), certainty=Certainty.GUARANTEED,
        )
        blocked = validator._execute_action(state, action, facts, {}, "line-r")
        self.assertIsNotNone(blocked)
        self.assertEqual(blocked.code, "SUMMON_RESTRICTED")

        release_issue = validator._apply_consequence(
            state, MechanicalConsequenceBinding(operator="RESTRICTION_RELEASE", params={"forbid_mechanics": ["SYNCHRO"]}),
            facts, "line-r",
        )
        self.assertIsNone(release_issue)
        self.assertNotIn("SYNCHRO", state.restrictions)

    def test_restrictions_do_not_leak_across_lines(self):
        from contracts import (
            CanonicalCardEntry, CanonicalDeck, CompiledLine, DeckSection,
        )
        from _fixtures import entry_for, make_context

        card = make_facts("Target Monster", "Synchro Effect Monster", level=4, effect_text="1 Tuner + 1+ non-Tuner monsters")
        entries = [entry_for(card, qty=1, section=DeckSection.EXTRA)]
        restrict_action = _restriction_action("restrict", "RESTRICTION_APPLY", ["SYNCHRO"])
        line_a = CompiledLine(
            line_id="line-a", title="A", starters=(), actions=(restrict_action,),
            claim="applies a restriction", certainty=Certainty.GUARANTEED, essential=True,
        )
        synchro_action = CanonicalAction(
            action_id="try", label="try", kind="SYNCHRO_SUMMON", card_name=card.canonical_name,
            materials=(), consequences=(), certainty=Certainty.GUARANTEED,
        )
        line_b = CompiledLine(
            line_id="line-b", title="B", starters=(), actions=(synchro_action,),
            claim="unaffected by line A's restriction", certainty=Certainty.GUARANTEED, essential=False,
        )
        deck = CanonicalDeck(
            deck_id="d", source_hash="0" * 64, context=make_context(), direction="Canonique",
            concept="c", entries=tuple(entries), lines=(line_a, line_b), axes=("c",), narrative_summary="",
        )
        report = validator.validate_combo_lines(deck)
        line_b_issues = [i for i in report.issues if i.line_id == "line-b"]
        self.assertFalse(
            any(i.code == "SUMMON_RESTRICTED" for i in line_b_issues),
            "a restriction applied in one line must not leak into another line's fresh state",
        )


if __name__ == "__main__":
    unittest.main()
