"""G1 — Contracts/ownership (T1). Regression guards for the schema boundary
closed against REQ-CR-003/020 model-secretariat.

Run: python3 -m unittest tests.test_g1_contracts_ownership -v
"""
from __future__ import annotations

import unittest

from _bootstrap import use_worktree_source

use_worktree_source()

from contracts import (  # noqa: E402
    EffectInterpretationKind, FORBIDDEN_MODEL_FIELDS, certainty_at_least_as_strong,
    Certainty, semantic_draft_from_mapping,
)
from compiler import project_mechanical_consequences  # noqa: E402


def _base_draft(line_extra=None, action_extra=None):
    action = {
        "label": "a",
        "kind": "ACTIVATE_EFFECT",
        "card": "Dark Magician",
        "effects": [{
            "kind": "OBTAIN_NAMED_FROM_DECK",
            "subject": "Dark Magician",
            "qty": 1,
        }],
    }
    if action_extra:
        action.update(action_extra)
    line = {
        "title": "L",
        "starters": ["Dark Magician"],
        "claim": "claim",
        "essential": True,
        "actions": [action],
    }
    if line_extra:
        line.update(line_extra)
    return {
        "direction": "Canonique",
        "concept": "fixture",
        "cards": [{"name": "Dark Magician", "qty": 1}],
        "axes": ["control"],
        "lines": [line],
    }


class RedModelMcbSecretariatFixed(unittest.TestCase):
    """RED-MODEL-MCB-SECRETARIAT, now closed: the raw operator/source/
    destination vocabulary the model used to be able to author directly is
    rejected outright."""

    def test_raw_operator_field_on_effect_is_rejected(self):
        raw = _base_draft(action_extra={"effects": [{
            "operator": "MOVE", "subject": "Dark Magician", "source": "DECK", "destination": "HAND", "qty": 1,
        }]})
        with self.assertRaises(ValueError) as ctx:
            semantic_draft_from_mapping(raw)
        self.assertIn("compiler/runtime-owned", str(ctx.exception))

    def test_old_consequences_field_name_is_rejected(self):
        raw = _base_draft(action_extra={"consequences": [{"operator": "MOVE"}]})
        del raw["lines"][0]["actions"][0]["effects"]
        with self.assertRaises(ValueError):
            semantic_draft_from_mapping(raw)

    def test_unknown_effect_kind_is_rejected(self):
        raw = _base_draft(action_extra={"effects": [{"kind": "DO_ANYTHING", "subject": "X"}]})
        with self.assertRaises(ValueError):
            semantic_draft_from_mapping(raw)

    def test_data_architecture_run_control_fields_are_rejected_at_draft_root(self):
        for field_name in ("phase", "mcb", "before", "after", "resource_ledger", "publication_authorized"):
            raw = _base_draft()
            raw[field_name] = "x"
            with self.assertRaises(ValueError, msg=field_name):
                semantic_draft_from_mapping(raw)


class GreenEffectInterpretationAccepted(unittest.TestCase):
    """Symmetric positive control: the closed, zone-free effect-interpretation
    schema is accepted and round-trips into a SemanticEffectInterpretation."""

    def test_closed_kind_catalog_accepted(self):
        draft = semantic_draft_from_mapping(_base_draft())
        effect = draft.lines[0].actions[0].effects[0]
        self.assertEqual(effect.kind, "OBTAIN_NAMED_FROM_DECK")
        self.assertEqual(effect.subject, "Dark Magician")
        self.assertFalse(hasattr(effect, "operator"))
        self.assertFalse(hasattr(effect, "source"))

    def test_asserted_damage_threshold_accepted(self):
        draft = semantic_draft_from_mapping(_base_draft(line_extra={"asserted_damage_threshold": 8000}))
        self.assertEqual(draft.lines[0].asserted_damage_threshold, 8000)


class CompilerMcbProjectionDeterminism(unittest.TestCase):
    """REQ-CR-020: same semantic input -> same compiled MCB, every closed
    kind maps through the template table (no model-chosen zone)."""

    def test_all_kinds_have_a_template(self):
        from compiler import _MCB_TEMPLATES
        for kind in EffectInterpretationKind:
            self.assertIn(kind.value, _MCB_TEMPLATES, kind.value)

    def test_special_summon_from_gy_derives_graveyard_to_field(self):
        draft = semantic_draft_from_mapping(_base_draft(action_extra={"effects": [{
            "kind": "SPECIAL_SUMMON_FROM_GY", "subject": "Dark Magician", "qty": 1,
        }]}))
        effect = draft.lines[0].actions[0].effects
        mcb = project_mechanical_consequences(effect)
        self.assertEqual(len(mcb), 1)
        self.assertEqual(mcb[0].operator, "MOVE")
        self.assertEqual(mcb[0].source, "GRAVEYARD")
        self.assertEqual(mcb[0].destination, "FIELD")

    def test_determinism_same_input_same_output(self):
        draft = semantic_draft_from_mapping(_base_draft())
        a = project_mechanical_consequences(draft.lines[0].actions[0].effects)
        b = project_mechanical_consequences(draft.lines[0].actions[0].effects)
        self.assertEqual(a, b)

    def test_restrict_mechanic_projects_params(self):
        draft = semantic_draft_from_mapping(_base_draft(action_extra={"effects": [{
            "kind": "RESTRICT_MECHANIC", "mechanics": ["SYNCHRO"],
        }]}))
        mcb = project_mechanical_consequences(draft.lines[0].actions[0].effects)
        self.assertEqual(mcb[0].operator, "RESTRICTION_APPLY")
        self.assertEqual(mcb[0].params["forbid_mechanics"], ["SYNCHRO"])


class CertaintyMonotonicityHelper(unittest.TestCase):
    def test_guaranteed_is_at_least_as_strong_as_conditional(self):
        self.assertTrue(certainty_at_least_as_strong(Certainty.GUARANTEED, Certainty.CONDITIONAL))

    def test_conditional_is_not_at_least_as_strong_as_guaranteed(self):
        self.assertFalse(certainty_at_least_as_strong(Certainty.CONDITIONAL, Certainty.GUARANTEED))


if __name__ == "__main__":
    unittest.main()
