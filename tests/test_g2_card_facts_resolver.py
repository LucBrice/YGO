"""G2 — CardFactsResolver multi-route (T2, REQ-CR-004/025).

Run: python3 -m unittest tests.test_g2_card_facts_resolver -v
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from _bootstrap import use_worktree_source

use_worktree_source()

from card_data import CardDataError, CardDataService, CardFactsResolver, CardFactsCache  # noqa: E402
from contracts import CardFacts  # noqa: E402

SOURCE_DIR = Path(__file__).resolve().parents[1] / "worktree" / "source"


def _facts(name: str, **kw) -> CardFacts:
    base = dict(
        canonical_name=name, external_id=1, card_type="Normal Monster", level=4,
        effect_text="", provider="FAKE", source_locator="fake://route",
        fetched_at="2026-10-01T00:00:00Z", payload_sha256="0" * 64,
    )
    base.update(kw)
    return CardFacts(**base)


class DownRoute:
    route_name = "ROUTE_A_DOWN"

    def fetch_exact(self, canonical_name: str) -> CardFacts:
        raise CardDataError("CARD_PROVIDER_UNAVAILABLE", f"simulated outage for {canonical_name}")


class WorkingRoute:
    route_name = "ROUTE_B_WEB"

    def __init__(self, facts_by_name):
        self._facts = facts_by_name

    def fetch_exact(self, canonical_name: str) -> CardFacts:
        return self._facts[canonical_name]


class ConflictingRoute:
    def __init__(self, route_name: str, facts_by_name):
        self.route_name = route_name
        self._facts = facts_by_name

    def fetch_exact(self, canonical_name: str) -> CardFacts:
        return self._facts[canonical_name]


class GreenProviderFallback(unittest.TestCase):
    """RED-PROVIDER-FALLBACK, now closed: a down route no longer stops
    resolution while an alternate admissible route remains."""

    def test_provider_a_down_provider_b_resolves(self):
        working = WorkingRoute({"Dark Magician": _facts("Dark Magician")})
        with tempfile.TemporaryDirectory() as tmp:
            service = CardDataService(
                source_dir=SOURCE_DIR, routes=[DownRoute(), working], cache_dir=tmp,
            )
            facts = service.get_facts("Dark Magician")
            self.assertEqual(facts.canonical_name, "Dark Magician")
            routes_tried = [a.route for a in service.last_resolution_attempts]
            self.assertEqual(routes_tried, ["ROUTE_A_DOWN", "ROUTE_B_WEB"])
            self.assertEqual(service.last_resolution_attempts[0].outcome, "FAILURE")
            self.assertEqual(service.last_resolution_attempts[1].outcome, "SUCCESS")


class GreenRouteExhaustion(unittest.TestCase):
    """Positive control: only after every admissible route is exhausted does
    resolution fail, as CARD_FACTS_UNRESOLVED (never silently)."""

    def test_all_routes_down_raises_unresolved_with_attempts(self):
        with tempfile.TemporaryDirectory() as tmp:
            service = CardDataService(source_dir=SOURCE_DIR, routes=[DownRoute(), DownRoute()], cache_dir=tmp)
            with self.assertRaises(CardDataError) as ctx:
                service.get_facts("Dark Magician")
            self.assertEqual(ctx.exception.code, "CARD_FACTS_UNRESOLVED")
            self.assertEqual(len(ctx.exception.attempts), 2)
            self.assertTrue(all(a.outcome == "FAILURE" for a in ctx.exception.attempts))

    def test_no_routes_configured_raises_unresolved(self):
        with tempfile.TemporaryDirectory() as tmp:
            service = CardDataService(source_dir=SOURCE_DIR, routes=[], cache_dir=tmp)
            with self.assertRaises(CardDataError) as ctx:
                service.get_facts("Dark Magician")
            self.assertEqual(ctx.exception.code, "CARD_FACTS_UNRESOLVED")


class GreenConflictDetection(unittest.TestCase):
    """Positive control: a material conflict between two independently
    verified routes fails closed instead of guessing by model memory."""

    def test_conflicting_routes_raise_conflict(self):
        route_a = ConflictingRoute("A", {"X": _facts("X", level=4)})
        route_b = ConflictingRoute("B", {"X": _facts("X", level=8)})
        with tempfile.TemporaryDirectory() as tmp:
            resolver = CardFactsResolver([route_a, route_b], cache=CardFactsCache(tmp))
            with self.assertRaises(CardDataError) as ctx:
                resolver.resolve("X", verify=True)
            self.assertEqual(ctx.exception.code, "CARD_FACTS_CONFLICT")
            self.assertEqual(len(ctx.exception.candidates), 2)

    def test_agreeing_routes_pass_verification(self):
        route_a = ConflictingRoute("A", {"X": _facts("X", level=4)})
        route_b = ConflictingRoute("B", {"X": _facts("X", level=4)})
        with tempfile.TemporaryDirectory() as tmp:
            resolver = CardFactsResolver([route_a, route_b], cache=CardFactsCache(tmp))
            facts, attempts = resolver.resolve("X", verify=True)
            self.assertEqual(facts.level, 4)
            self.assertEqual(len(attempts), 2)


class GreenCacheShortCircuit(unittest.TestCase):
    def test_cache_hit_skips_all_routes(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = CardFactsCache(tmp)
            cache.put(_facts("Dark Magician"))
            resolver = CardFactsResolver([DownRoute()], cache=cache)
            facts, attempts = resolver.resolve("Dark Magician")
            self.assertEqual(facts.canonical_name, "Dark Magician")
            self.assertEqual(len(attempts), 1)
            self.assertEqual(attempts[0].route, "CACHE")


if __name__ == "__main__":
    unittest.main()
