"""G0 — Characterization. NO product mutation performed by this file.

Materializes, against the exact unmutated V5 worktree (== baseline_v5):
- RED-QUASAR-UNSUPPORTED  (REQ-CR-015/019, mandatory defect #1 from 00_START_HERE.md)
- GREEN parent control for the Synchro path the current regex does support
- RED-PROVIDER-FALLBACK   (REQ-CR-025, mandatory defect #2)
- RED-MODEL-MCB-SECRETARIAT (REQ-CR-003/020, mandatory defect #3)

Run: python3 -m unittest tests.test_g0_characterization -v
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from _bootstrap import use_worktree_source

use_worktree_source()

import validator  # noqa: E402
from contracts import semantic_draft_from_mapping  # noqa: E402
from card_data import CardDataError, CardDataService  # noqa: E402

from _fixtures import (  # noqa: E402
    CLEAR_WING_FACTS, CRYSTAL_WING_FACTS, FORMULA_SYNCHRON_FACTS, PLAIN_NON_TUNER_FACTS,
    QUASAR_FACTS, quasar_synchro_action,
)


def _state_with_materials(materials) -> "validator._LineState":
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


class RedQuasarUnsupported(unittest.TestCase):
    """RED-QUASAR-UNSUPPORTED: a mechanically VALID Quasar line (1 Tuner +
    2 non-Tuner Synchro Monsters summing to exactly Level 12) is rejected
    today only because validator.py's Synchro header regex matches a single
    literal string and Quasar's real clause does not match it."""

    def test_valid_quasar_materials_are_rejected_as_unsupported_today(self):
        materials = (
            FORMULA_SYNCHRON_FACTS.canonical_name,  # Tuner, level 2
            CLEAR_WING_FACTS.canonical_name,        # non-Tuner Synchro, level 7
            CRYSTAL_WING_FACTS.canonical_name,      # non-Tuner Synchro, level 3  (sum=12)
        )
        state = _state_with_materials([FORMULA_SYNCHRON_FACTS, CLEAR_WING_FACTS, CRYSTAL_WING_FACTS])
        action = quasar_synchro_action(materials)
        issue = validator._synchro_summon(state, action, _facts_map(), "line-quasar")
        self.assertIsNotNone(issue, "expected the current defect to reproduce (issue must not be None)")
        self.assertEqual(issue.code, "SYNCHRO_REQUIREMENT_UNSUPPORTED")
        self.assertEqual(issue.owner.value, "RUNTIME")
        self.assertEqual(issue.proof_status.value, "UNVERIFIED")


class GreenSynchroParentControl(unittest.TestCase):
    """Positive control: the plain unqualified header the current regex DOES
    support still resolves correctly, proving the defect is isolated to the
    qualified-clause case and not a broken test harness."""

    def test_plain_generic_synchro_header_still_resolves(self):
        plain_target = validator.ValidationIssue  # sanity import only
        from _fixtures import make_facts
        target = make_facts(
            "Generic Synchro Target", "Synchro Effect Monster", level=5,
            effect_text="1 Tuner + 1+ non-Tuner monsters",
        )
        tuner = make_facts("Generic Tuner", "Synchro Tuner Effect Monster", level=2)
        nontuner = make_facts("Generic Beater", "Normal Monster", level=3)
        state = validator._LineState()
        state.zones["FIELD"][tuner.canonical_name] += 1
        state.zones["FIELD"][nontuner.canonical_name] += 1
        state.zones["EXTRA"][target.canonical_name] += 1
        action = quasar_synchro_action((tuner.canonical_name, nontuner.canonical_name))
        action = action.__class__(**{**action.__dict__, "card_name": target.canonical_name})
        facts = {f.canonical_name: f for f in (target, tuner, nontuner)}
        issue = validator._synchro_summon(state, action, facts, "line-generic")
        self.assertIsNone(issue, f"expected the already-supported generic path to PASS, got {issue}")


class RedProviderFallback(unittest.TestCase):
    """RED-PROVIDER-FALLBACK: a single provider outage currently stops the
    whole resolution with no alternate route attempted, even though the
    business need is 'resolve the fact', not 'make this one endpoint answer'."""

    def test_single_provider_outage_blocks_with_no_fallback(self):
        class DownProvider:
            def fetch_exact(self, canonical_name: str):
                raise CardDataError("CARD_PROVIDER_UNAVAILABLE", f"simulated outage for {canonical_name}")

        with tempfile.TemporaryDirectory() as tmp:
            service = CardDataService(
                source_dir=Path(__file__).resolve().parents[1] / "worktree" / "source",
                provider=DownProvider(),
                cache_dir=tmp,
            )
            with self.assertRaises(CardDataError) as ctx:
                service.get_facts("Dark Magician")
            self.assertEqual(ctx.exception.code, "CARD_PROVIDER_UNAVAILABLE")


class RedModelMcbSecretariat(unittest.TestCase):
    """RED-MODEL-MCB-SECRETARIAT: the model boundary currently ACCEPTS raw
    low-level mechanical consequence operators (REQUIRE/MOVE/CONSUME/...)
    authored directly by the model, instead of rejecting them as
    compiler/runtime-owned."""

    def test_model_can_author_raw_mechanical_consequence_today(self):
        raw = {
            "direction": "Canonique",
            "concept": "fixture",
            "cards": [{"name": "Dark Magician", "qty": 1}],
            "axes": ["control"],
            "lines": [{
                "title": "L",
                "starters": ["Dark Magician"],
                "claim": "claim",
                "essential": True,
                "actions": [{
                    "label": "a",
                    "kind": "ACTIVATE_EFFECT",
                    "card": "Dark Magician",
                    "consequences": [{
                        "operator": "MOVE",
                        "subject": "Dark Magician",
                        "source": "DECK",
                        "destination": "HAND",
                        "qty": 1,
                    }],
                }],
            }],
        }
        draft = semantic_draft_from_mapping(raw)
        consequence = draft.lines[0].actions[0].consequences[0]
        self.assertEqual(consequence.operator, "MOVE")
        self.assertEqual(consequence.source, "DECK")
        self.assertEqual(consequence.destination, "HAND")


if __name__ == "__main__":
    unittest.main()
