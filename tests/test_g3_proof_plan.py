"""G3 — Proof compiler / ProofPlan / lineage (T3, REQ-CR-016/006).

Run: python3 -m unittest tests.test_g3_proof_plan -v
"""
from __future__ import annotations

import dataclasses
import tempfile
import unittest
from pathlib import Path

from _bootstrap import use_worktree_source

use_worktree_source()

from card_data import CardDataService  # noqa: E402
from compiler import compile_draft, evidence_set_hash, proof_plan_is_fresh  # noqa: E402
from contracts import BuildContext, BuildRequest, CardFacts, semantic_draft_from_mapping  # noqa: E402

SOURCE_DIR = Path(__file__).resolve().parents[1] / "worktree" / "source"


class FakeProvider:
    def __init__(self, level: int = 7):
        self.level = level

    def fetch_exact(self, canonical_name: str) -> CardFacts:
        return CardFacts(
            canonical_name=canonical_name, external_id=1, card_type="Normal Monster",
            level=self.level, atk=2500, defense=2100, effect_text="",
            provider="FAKE", source_locator="fake://", fetched_at="2026-10-01T00:00:00Z",
            payload_sha256=f"sha-for-level-{self.level}".ljust(64, "0"),
        )


def _draft_raw():
    return {
        "direction": "Canonique",
        "concept": "fixture",
        "cards": [{"name": "Dark Magician", "qty": 1}],
        "axes": ["control"],
        "lines": [],
    }


def _context():
    request = BuildRequest(user_prompt="t", character="c", direction="Canonique")
    return BuildContext(
        request=request, environment_id="link_evolution_2020",
        allowed_mechanics=(), forbidden_mechanics=(), policy_source_sha256="0" * 64,
    )


def _service(provider):
    tmp = tempfile.mkdtemp()
    return CardDataService(source_dir=SOURCE_DIR, routes=[provider], cache_dir=tmp)


class GreenProofPlanDeterminism(unittest.TestCase):
    def test_same_semantic_and_evidence_yield_same_proof_plan_hash(self):
        draft = semantic_draft_from_mapping(_draft_raw())
        context = _context()
        deck1 = compile_draft(draft, context, _service(FakeProvider(level=7)))
        deck2 = compile_draft(draft, context, _service(FakeProvider(level=7)))
        self.assertEqual(deck1.proof_plan.proof_plan_hash, deck2.proof_plan.proof_plan_hash)
        self.assertEqual(deck1.proof_plan.semantic_hash, deck1.source_hash)


class RedEvidenceChangeMustInvalidate(unittest.TestCase):
    """REQ-CR-016/Data Architecture Sec.4: an evidence (CardFacts) change must
    change the ProofPlan identity even when the semantic source is byte
    identical, and must mark a previously-compiled deck STALE."""

    def test_different_card_facts_yield_different_proof_plan_hash(self):
        draft = semantic_draft_from_mapping(_draft_raw())
        context = _context()
        deck_level7 = compile_draft(draft, context, _service(FakeProvider(level=7)))
        deck_level8 = compile_draft(draft, context, _service(FakeProvider(level=8)))
        self.assertEqual(deck_level7.source_hash, deck_level8.source_hash, "semantic source is identical")
        self.assertNotEqual(
            deck_level7.proof_plan.evidence_set_hash, deck_level8.proof_plan.evidence_set_hash,
            "evidence changed but the old is_fresh() check would have missed it",
        )
        self.assertNotEqual(deck_level7.proof_plan.proof_plan_hash, deck_level8.proof_plan.proof_plan_hash)

    def test_stale_evidence_detected_by_proof_plan_is_fresh(self):
        draft = semantic_draft_from_mapping(_draft_raw())
        context = _context()
        deck = compile_draft(draft, context, _service(FakeProvider(level=7)))
        self.assertTrue(proof_plan_is_fresh(deck, draft, context))
        # Simulate a provider update changing the underlying facts for the
        # exact same semantic draft: the old compiled deck's entries are
        # swapped for "refreshed" ones with a different payload hash.
        refreshed_entry = dataclasses.replace(
            deck.entries[0], facts=dataclasses.replace(deck.entries[0].facts, payload_sha256="changed" * 10)
        )
        stale_deck = dataclasses.replace(deck, entries=(refreshed_entry,))
        self.assertFalse(proof_plan_is_fresh(stale_deck, draft, context))

    def test_semantic_change_detected_by_proof_plan_is_fresh(self):
        draft = semantic_draft_from_mapping(_draft_raw())
        context = _context()
        deck = compile_draft(draft, context, _service(FakeProvider(level=7)))
        other_raw = _draft_raw()
        other_raw["concept"] = "a different concept"
        other_draft = semantic_draft_from_mapping(other_raw)
        self.assertFalse(proof_plan_is_fresh(deck, other_draft, context))


class GreenEvidenceSetHashUnit(unittest.TestCase):
    def test_evidence_set_hash_is_order_independent(self):
        from contracts import CanonicalCardEntry, DeckSection
        a = CanonicalCardEntry(card_id="1", facts=FakeProvider(4).fetch_exact("A"), qty=1, section=DeckSection.MAIN, banlist_limit=3)
        b = CanonicalCardEntry(card_id="2", facts=FakeProvider(5).fetch_exact("B"), qty=1, section=DeckSection.MAIN, banlist_limit=3)
        h1, refs1 = evidence_set_hash([a, b])
        h2, refs2 = evidence_set_hash([b, a])
        self.assertEqual(h1, h2)
        self.assertEqual(refs1, refs2)


if __name__ == "__main__":
    unittest.main()
