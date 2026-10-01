from __future__ import annotations

import hashlib
import json
import re
import unicodedata
import urllib.parse
import urllib.request
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol, Sequence

from contracts import CardFacts, ResolutionAttempt


YGOPRODECK_CARDINFO_URL = "https://db.ygoprodeck.com/api/v7/cardinfo.php"


class CardDataError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def normalize_name(value: str) -> str:
    text = unicodedata.normalize("NFKC", value)
    return " ".join(text.casefold().split())


class LocalCardCatalog:
    def __init__(self, names: list[str], *, environment_id: str, names_sha256: str):
        self.names = tuple(names)
        self.environment_id = environment_id
        self.names_sha256 = names_sha256
        self._by_normalized: dict[str, list[str]] = {}
        for name in self.names:
            self._by_normalized.setdefault(normalize_name(name), []).append(name)

    @classmethod
    def from_source(cls, source_dir: str | Path) -> "LocalCardCatalog":
        path = Path(source_dir) / "LINK_EVOLUTION_2020_CARD_POOL.json"
        doc = json.loads(path.read_text(encoding="utf-8"))
        cards = doc.get("cards")
        if not isinstance(cards, list) or not all(isinstance(x, str) for x in cards):
            raise CardDataError("CATALOG_SCHEMA_INVALID", "card pool does not expose a string cards array")
        declared_count = doc.get("catalog_card_count")
        if declared_count != len(cards):
            raise CardDataError("CATALOG_COUNT_MISMATCH", f"declared={declared_count} actual={len(cards)}")
        canonical_blob = "\n".join(cards).encode("utf-8")
        computed = hashlib.sha256(canonical_blob).hexdigest()
        declared_hash = str(doc.get("catalog_names_sha256", ""))
        # Historical packages may define the hash over a slightly different canonical byte form.
        # Preserve the declared binding but never silently replace a non-empty value.
        if not declared_hash:
            declared_hash = computed
        return cls(cards, environment_id=str(doc.get("environment_id", "link_evolution_2020")), names_sha256=declared_hash)

    def resolve(self, name: str) -> str:
        candidates = self._by_normalized.get(normalize_name(name), [])
        if not candidates:
            raise CardDataError("CATALOG_CARD_NOT_FOUND", f"card not present in Link Evolution pool: {name}")
        if len(candidates) != 1:
            raise CardDataError("CATALOG_CARD_AMBIGUOUS", f"ambiguous canonical card name: {name}")
        return candidates[0]

    def contains(self, name: str) -> bool:
        try:
            self.resolve(name)
            return True
        except CardDataError:
            return False


class Banlist:
    def __init__(self, limits: Mapping[str, int]):
        self._limits = dict(limits)

    @classmethod
    def from_source(cls, source_dir: str | Path) -> "Banlist":
        path = Path(source_dir) / "BANLIST_LINK_EVOLUTION_2020.md"
        limits: dict[str, int] = {}
        current_limit: int | None = None
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if line.startswith("# INTERDITES"):
                current_limit = 0
                continue
            if line.startswith("# LIMITÉES"):
                current_limit = 1
                continue
            if line.startswith("# SEMI-LIMITÉES"):
                current_limit = 2
                continue
            if line.startswith("# ") and not line.startswith("## "):
                if not any(line.startswith(prefix) for prefix in ("# INTERDITES", "# LIMITÉES", "# SEMI-LIMITÉES")):
                    current_limit = None
                continue
            if current_limit is not None and line.startswith("- "):
                name = line[2:].strip()
                if name:
                    limits[normalize_name(name)] = current_limit
        return cls(limits)

    def limit_for(self, canonical_name: str) -> int:
        return self._limits.get(normalize_name(canonical_name), 3)


class CardFactsProvider(Protocol):
    def fetch_exact(self, canonical_name: str) -> CardFacts:
        ...


class YGOPRODeckProvider:
    """Machine-readable current card facts provider. Never supplies Link Evolution legality."""

    def __init__(
        self,
        *,
        endpoint: str = YGOPRODECK_CARDINFO_URL,
        timeout: float = 8.0,
        opener: Callable[..., Any] | None = None,
    ):
        self.endpoint = endpoint
        self.timeout = timeout
        self._opener = opener or urllib.request.urlopen

    def fetch_exact(self, canonical_name: str) -> CardFacts:
        query = urllib.parse.urlencode({"name": canonical_name})
        locator = f"{self.endpoint}?{query}"
        request = urllib.request.Request(locator, headers={"User-Agent": "YGO-Clean-Runtime/5"})
        try:
            with self._opener(request, timeout=self.timeout) as response:
                status = getattr(response, "status", 200)
                payload = response.read()
        except Exception as exc:  # network boundary, converted to DATA issue upstream
            raise CardDataError("CARD_PROVIDER_UNAVAILABLE", f"card provider failed for {canonical_name}: {exc}") from exc
        if status != 200:
            raise CardDataError("CARD_PROVIDER_HTTP", f"card provider returned HTTP {status} for {canonical_name}")
        try:
            doc = json.loads(payload.decode("utf-8"))
            rows = doc["data"]
            if not isinstance(rows, list) or len(rows) != 1:
                raise ValueError("expected one exact card row")
            row = rows[0]
        except Exception as exc:
            raise CardDataError("CARD_PROVIDER_SCHEMA", f"malformed provider payload for {canonical_name}") from exc
        if normalize_name(str(row.get("name", ""))) != normalize_name(canonical_name):
            raise CardDataError("CARD_PROVIDER_NAME_MISMATCH", f"provider returned a different card for {canonical_name}")
        return facts_from_ygoprodeck_row(row, locator=locator)


def facts_from_ygoprodeck_row(row: Mapping[str, Any], *, locator: str) -> CardFacts:
    canonical_payload = json.dumps(dict(row), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    card_type = str(row.get("type", "")).strip()
    raw_level = row.get("level")
    level = int(raw_level) if isinstance(raw_level, int) and "xyz" not in card_type.casefold() else None
    rank = int(raw_level) if isinstance(raw_level, int) and "xyz" in card_type.casefold() else None
    return CardFacts(
        canonical_name=str(row.get("name", "")).strip(),
        external_id=(int(row["id"]) if isinstance(row.get("id"), int) else None),
        card_type=card_type,
        race=(str(row["race"]).strip() if row.get("race") is not None else None),
        attribute=(str(row["attribute"]).strip() if row.get("attribute") is not None else None),
        level=level,
        rank=rank,
        linkval=(int(row["linkval"]) if isinstance(row.get("linkval"), int) else None),
        scale=(int(row["scale"]) if isinstance(row.get("scale"), int) else None),
        atk=(int(row["atk"]) if isinstance(row.get("atk"), int) else None),
        defense=(int(row["def"]) if isinstance(row.get("def"), int) else None),
        effect_text=str(row.get("desc", "")),
        provider="YGOPRODeck-v7",
        source_locator=locator,
        fetched_at=datetime.now(timezone.utc).isoformat(),
        payload_sha256=hashlib.sha256(canonical_payload).hexdigest(),
        environment_compatibility="CURRENT_TEXT_UNCHECKED",
    )


class CardFactsCache:
    def __init__(self, directory: str | Path):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def _path(self, canonical_name: str) -> Path:
        key = hashlib.sha256(normalize_name(canonical_name).encode("utf-8")).hexdigest()
        return self.directory / f"{key}.json"

    def get(self, canonical_name: str) -> CardFacts | None:
        path = self._path(canonical_name)
        if not path.exists():
            return None
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
            facts = CardFacts(**doc)
        except Exception as exc:
            raise CardDataError("CARD_CACHE_CORRUPT", f"invalid cache entry for {canonical_name}") from exc
        if normalize_name(facts.canonical_name) != normalize_name(canonical_name):
            raise CardDataError("CARD_CACHE_IDENTITY_MISMATCH", f"cache identity mismatch for {canonical_name}")
        return facts

    def put(self, facts: CardFacts) -> None:
        path = self._path(facts.canonical_name)
        temp = path.with_suffix(".tmp")
        temp.write_text(json.dumps(asdict(facts), ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        temp.replace(path)


def _attempt(route: str, outcome: str, error_class: str | None, *, locator: str | None = None) -> ResolutionAttempt:
    return ResolutionAttempt(
        route=route, outcome=outcome, error_class=error_class,
        timestamp=datetime.now(timezone.utc).isoformat(), locator=locator,
    )


def _route_name(route: CardFactsProvider) -> str:
    return getattr(route, "route_name", route.__class__.__name__)


class CardFactsResolver:
    """Multi-route CardFacts resolution (REQ-CR-025). Route failure != info
    failure: one admissible route's outage never stops resolution while
    another admissible route remains unexhausted. Cache is checked first;
    routes are then tried in the given order; CARD_FACTS_UNRESOLVED is only
    raised once every configured route has failed (route exhaustion), never
    on a single route's failure."""

    def __init__(self, routes: Sequence[CardFactsProvider], *, cache: "CardFactsCache"):
        self.routes = list(routes)
        self.cache = cache

    def resolve(self, canonical_name: str, *, verify: bool = False) -> tuple[CardFacts, tuple[ResolutionAttempt, ...]]:
        attempts: list[ResolutionAttempt] = []
        cached = self.cache.get(canonical_name)
        if cached is not None and not verify:
            attempts.append(_attempt("CACHE", "SUCCESS", None, locator=cached.source_locator))
            return cached, tuple(attempts)

        resolved: list[CardFacts] = []
        if cached is not None:
            attempts.append(_attempt("CACHE", "SUCCESS", None, locator=cached.source_locator))
            resolved.append(cached)

        for route in self.routes:
            route_name = _route_name(route)
            try:
                facts = route.fetch_exact(canonical_name)
            except CardDataError as exc:
                attempts.append(_attempt(route_name, "FAILURE", exc.code))
                continue
            if normalize_name(facts.canonical_name) != normalize_name(canonical_name):
                attempts.append(_attempt(route_name, "FAILURE", "CARD_PROVIDER_NAME_MISMATCH"))
                continue
            attempts.append(_attempt(route_name, "SUCCESS", None, locator=facts.source_locator))
            resolved.append(facts)
            if not verify or len(resolved) >= 2:
                break

        if not resolved:
            error = CardDataError(
                "CARD_FACTS_UNRESOLVED",
                f"all admissible routes exhausted for {canonical_name} "
                f"({len(attempts)} attempt(s): {[a.route for a in attempts]})",
            )
            error.attempts = tuple(attempts)  # type: ignore[attr-defined]
            raise error

        if len(resolved) > 1:
            conflict_fields = ("card_type", "level", "rank", "linkval", "scale")
            first = resolved[0]
            for other in resolved[1:]:
                if any(getattr(first, f) != getattr(other, f) for f in conflict_fields):
                    error = CardDataError(
                        "CARD_FACTS_CONFLICT",
                        f"material conflict between independent routes for {canonical_name}",
                    )
                    error.attempts = tuple(attempts)  # type: ignore[attr-defined]
                    error.candidates = tuple(resolved)  # type: ignore[attr-defined]
                    raise error

        facts = resolved[0]
        if cached is None or facts is not cached:
            self.cache.put(facts)
        return facts, tuple(attempts)


class CardDataService:
    def __init__(
        self,
        *,
        source_dir: str | Path,
        provider: CardFactsProvider | None = None,
        routes: Sequence[CardFactsProvider] | None = None,
        cache_dir: str | Path,
    ):
        self.source_dir = Path(source_dir)
        self.catalog = LocalCardCatalog.from_source(source_dir)
        self.banlist = Banlist.from_source(source_dir)
        self.cache = CardFactsCache(cache_dir)
        if routes is not None:
            configured_routes = list(routes)
        elif provider is not None:
            configured_routes = [provider]
        else:
            configured_routes = []
        self.resolver = CardFactsResolver(configured_routes, cache=self.cache)
        self.last_resolution_attempts: tuple[ResolutionAttempt, ...] = ()

    def canonical_name(self, name: str) -> str:
        return self.catalog.resolve(name)

    def banlist_limit(self, canonical_name: str) -> int:
        return self.banlist.limit_for(canonical_name)

    def get_facts(self, name: str) -> CardFacts:
        canonical = self.canonical_name(name)
        facts, attempts = self.resolver.resolve(canonical)
        self.last_resolution_attempts = attempts
        return facts


def load_narrative_mechanics_policy(source_dir: str | Path) -> tuple[dict[str, Any], str]:
    path = Path(source_dir) / "STYLE_DECKS_PERSONNAGE_LINK_EVOLUTION_V39.md"
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    match = re.search(
        r"<!-- NARRATIVE_MECHANICS_POLICY_JSON:BEGIN -->\s*```json\s*(\{.*?\})\s*```",
        text,
        re.DOTALL,
    )
    if not match:
        raise CardDataError("NARRATIVE_POLICY_MISSING", "machine-readable narrative mechanics policy is missing")
    try:
        policy = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise CardDataError("NARRATIVE_POLICY_INVALID", "narrative mechanics policy JSON is invalid") from exc
    return policy, hashlib.sha256(raw).hexdigest()
