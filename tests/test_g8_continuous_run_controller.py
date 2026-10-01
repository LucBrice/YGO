"""G8 — Deterministic continuous-run controller (T8, REQ-CR-027). Closes
mandatory defect #4 from 00_START_HERE.md: internal recoverable friction
must never force a user `continue`/handoff.

Run: python3 -m unittest tests.test_g8_continuous_run_controller -v
"""
from __future__ import annotations

import tempfile
import unittest
from unittest import mock

from _bootstrap import use_worktree_source

use_worktree_source()

import runtime  # noqa: E402
from card_data import CardDataError  # noqa: E402
from contracts import BuildRequest, CardFacts, IssueOwner, ProofStatus, ValidationIssue  # noqa: E402

SOURCE_DIR = str(use_worktree_source())

_FILLER = [
    '"A" Cell Breeding Device', '"A" Cell Incubator', '"A" Cell Recombination Device',
    '"A" Cell Scatter Burst', '1st Movement Solo', '3-Hump Lacooda', '30,000-Year White Turtle',
    '4-Starred Ladybug of Doom', '7', '7 Colored Fish', '7 Completed', '8-Claws Scorpion', 'A Cat of Ill Omen',
]


def _valid_draft_payload():
    cards = [{"name": "Dark Magician", "qty": 1}] + [{"name": n, "qty": 3} for n in _FILLER]
    return {
        "direction": "Canonique", "concept": "deck", "cards": cards, "axes": ["control"],
        "narrative_summary": "s", "mastered_functions": ["a", "b"], "limited_functions": ["c"],
        "potential": 5, "development_level": "solide", "breakpoint": "bp",
        "lines": [{"title": "L", "starters": ["Dark Magician"], "claim": "c", "essential": True, "actions": []}],
    }


class _WorkingProvider:
    def fetch_exact(self, canonical_name):
        return CardFacts(
            canonical_name=canonical_name, external_id=1, card_type="Normal Monster",
            level=7, atk=2500, defense=2100, effect_text="",
            provider="FAKE", source_locator="fake://", fetched_at="2026-10-01T00:00:00Z",
            payload_sha256="0" * 64,
        )


class _DownProvider:
    def fetch_exact(self, canonical_name):
        raise CardDataError("CARD_PROVIDER_UNAVAILABLE", f"outage for {canonical_name}")


class UnitFingerprintAndRepairDecision(unittest.TestCase):
    def test_same_issue_set_yields_same_fingerprint_regardless_of_order(self):
        a = [ValidationIssue("X", "m", IssueOwner.MODEL), ValidationIssue("Y", "m2", IssueOwner.MODEL)]
        b = [ValidationIssue("Y", "m2", IssueOwner.MODEL), ValidationIssue("X", "m", IssueOwner.MODEL)]
        self.assertEqual(runtime._issue_fingerprint(a), runtime._issue_fingerprint(b))

    def test_different_issue_set_yields_different_fingerprint(self):
        a = [ValidationIssue("X", "m", IssueOwner.MODEL)]
        b = [ValidationIssue("Z", "m", IssueOwner.MODEL)]
        self.assertNotEqual(runtime._issue_fingerprint(a), runtime._issue_fingerprint(b))

    def test_should_repair_allows_first_then_blocks_repeat(self):
        seen: set[str] = set()
        issues = [ValidationIssue("X", "m", IssueOwner.MODEL)]
        self.assertEqual(runtime._should_repair(issues, seen, 0, 3), (True, False))
        self.assertEqual(runtime._should_repair(issues, seen, 1, 3), (False, True))

    def test_should_repair_respects_budget_first(self):
        seen: set[str] = set()
        issues = [ValidationIssue("X", "m", IssueOwner.MODEL)]
        self.assertEqual(runtime._should_repair(issues, seen, 3, 3), (False, False))


class GreenOneCallAutoRepair(unittest.TestCase):
    """REQ-CR-027 positive control #17: one API invocation auto-repairs a
    MODEL issue and reaches a terminal result without any user continue."""

    def test_structural_defect_is_auto_repaired_in_one_build_deck_call(self):
        calls = {"n": 0}

        def model(request):
            calls["n"] += 1
            if request["task"] == "semantic_audit":
                return {"supported": True, "reason": "ok"}
            if calls["n"] == 1:
                payload = _valid_draft_payload()
                payload["axes"] = []  # structurally invalid: AXES_MISSING
                return payload
            return _valid_draft_payload()

        with tempfile.TemporaryDirectory() as tmp:
            rt = runtime.Runtime(model=model, source_dir=SOURCE_DIR, card_provider=_WorkingProvider(), cache_dir=tmp)
            result = rt.build_deck(BuildRequest(user_prompt="t", character="c", direction="Canonique"))
        self.assertEqual(result.status, ProofStatus.PROVED)
        self.assertEqual(calls["n"], 2, "exactly one build call + one repair call, zero handoff")


class RedNoProgressLoopStopsEarly(unittest.TestCase):
    """RED-NO-PROGRESS-LOOP, closed: a MODEL that always returns the exact
    same defective draft must not exhaust the full repair budget uselessly
    -- it stops as soon as the identical blocker recurs."""

    def test_permanently_stuck_model_terminates_before_exhausting_budget(self):
        calls = {"n": 0}

        def model(request):
            calls["n"] += 1
            payload = _valid_draft_payload()
            payload["axes"] = []  # always the same structural defect
            return payload

        with tempfile.TemporaryDirectory() as tmp:
            rt = runtime.Runtime(model=model, source_dir=SOURCE_DIR, card_provider=_WorkingProvider(), cache_dir=tmp)
            request = BuildRequest(user_prompt="t", character="c", direction="Canonique", max_repairs=5)
            result = rt.build_deck(request)
        self.assertEqual(result.status, ProofStatus.FAILED)
        self.assertIn("MODEL_REPAIR_NO_PROGRESS", [i.code for i in result.report.issues])
        # budget was 5 repairs (6 build calls total if exhausted); no-progress
        # must stop strictly before that.
        self.assertLess(calls["n"], 6)


class GreenDataFallbackZeroAiCalls(unittest.TestCase):
    """REQ-CR-027 positive control #18: DATA fallback causes zero semantic
    repair calls -- the resolver's own route exhaustion/fallback happens
    entirely inside card_data, never by asking the model to retry."""

    def test_provider_outage_with_working_fallback_calls_model_exactly_once(self):
        calls = {"n": 0}

        def model(request):
            calls["n"] += 1
            if request["task"] == "semantic_audit":
                return {"supported": True, "reason": "ok"}
            return _valid_draft_payload()

        with tempfile.TemporaryDirectory() as tmp:
            rt = runtime.Runtime(
                model=model, source_dir=SOURCE_DIR,
                card_routes=[_DownProvider(), _WorkingProvider()], cache_dir=tmp,
            )
            result = rt.build_deck(BuildRequest(user_prompt="t", character="c", direction="Canonique"))
        self.assertEqual(result.status, ProofStatus.PROVED)
        self.assertEqual(calls["n"], 1, "DATA route fallback must never trigger a MODEL repair call")

    def test_all_routes_down_is_terminal_with_zero_repair_calls(self):
        calls = {"n": 0}

        def model(request):
            calls["n"] += 1
            return _valid_draft_payload()

        with tempfile.TemporaryDirectory() as tmp:
            rt = runtime.Runtime(model=model, source_dir=SOURCE_DIR, card_routes=[_DownProvider()], cache_dir=tmp)
            result = rt.build_deck(BuildRequest(user_prompt="t", character="c", direction="Canonique"))
        self.assertEqual(result.status, ProofStatus.UNVERIFIED)
        self.assertEqual(calls["n"], 1, "a terminal DATA failure must not trigger any MODEL repair call")


class GreenPublicationGateIntegration(unittest.TestCase):
    """RED-PUBLICATION-BYPASS, closed: build_deck never returns PROVED when
    the final proof_plan freshness check fails, even if every earlier gate
    passed."""

    def test_stale_proof_plan_blocks_publication(self):
        def model(request):
            if request["task"] == "semantic_audit":
                return {"supported": True, "reason": "ok"}
            return _valid_draft_payload()

        with tempfile.TemporaryDirectory() as tmp:
            rt = runtime.Runtime(model=model, source_dir=SOURCE_DIR, card_provider=_WorkingProvider(), cache_dir=tmp)
            with mock.patch.object(runtime, "proof_plan_is_fresh", return_value=False):
                result = rt.build_deck(BuildRequest(user_prompt="t", character="c", direction="Canonique"))
        self.assertEqual(result.status, ProofStatus.FAILED)
        self.assertIn("PUBLICATION_PROOF_STALE", [i.code for i in result.report.issues])


if __name__ == "__main__":
    unittest.main()
