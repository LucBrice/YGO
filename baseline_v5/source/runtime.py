from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable, Mapping

from card_data import (
    CardDataError, CardDataService, YGOPRODeckProvider, load_narrative_mechanics_policy,
)
from compiler import compile_draft, compile_presentation_plan
from contracts import (
    BuildContext, BuildRequest, DeckResult, IssueOwner, ProofStatus,
    SemanticDeckDraft, ValidationIssue, ValidationReport, semantic_draft_from_mapping,
)
from validator import combine_validation, validate_combo_lines, validate_deck_legality

ModelCallable = Callable[[Mapping[str, Any]], Mapping[str, Any] | SemanticDeckDraft]

_BUSINESS_AUTHORITY_FILES = (
    "STYLE_DECKS_PERSONNAGE_LINK_EVOLUTION_V39.md",
    "VALIDATION_PROGRESSION_NARRATIVE_V5.md",
    "HOOK_STYLE_AXES_CONSTRUCTION_DECKS_PERSONNAGES_V17.md",
    "VALIDATION_CANONIQUE_REMIXE_V15.md",
    "STRUCTURE_AXES_COMBOS_DECKS_PERSONNAGES_V1.md",
    "SEMANTIC_RULING_CONTRACT_V1.md",
)


class Runtime:
    """Small orchestrator: context -> model -> compile -> validate -> publish."""

    def __init__(
        self,
        *,
        model: ModelCallable,
        source_dir: str | Path,
        card_provider: Any = None,
        cache_dir: str | Path | None = None,
    ):
        self.model = model
        self.source_dir = Path(source_dir)
        provider = card_provider if card_provider is not None else YGOPRODeckProvider()
        cache = Path(cache_dir) if cache_dir is not None else Path.home() / ".cache" / "ygo-clean-runtime" / "card_facts"
        self.card_data = CardDataService(source_dir=self.source_dir, provider=provider, cache_dir=cache)

    @staticmethod
    def parse_model_draft(raw: Mapping[str, Any] | SemanticDeckDraft) -> SemanticDeckDraft:
        if isinstance(raw, SemanticDeckDraft):
            return raw
        return semantic_draft_from_mapping(raw)

    def _build_context(self, request: BuildRequest) -> BuildContext:
        policy, source_sha = load_narrative_mechanics_policy(self.source_dir)
        eras = policy.get("eras", {})
        era = eras.get(request.era)
        if not isinstance(era, Mapping):
            raise CardDataError("NARRATIVE_ERA_UNKNOWN", f"unknown narrative era: {request.era}")
        return BuildContext(
            request=request,
            environment_id=self.card_data.catalog.environment_id,
            allowed_mechanics=tuple(era.get("allowed", ())),
            forbidden_mechanics=tuple(era.get("forbidden", ())),
            policy_source_sha256=source_sha,
        )

    def _authorities(self) -> dict[str, str]:
        out = {}
        for name in _BUSINESS_AUTHORITY_FILES:
            path = self.source_dir / name
            if path.exists():
                out[name] = path.read_text(encoding="utf-8")
        return out

    def _initial_model_request(self, context: BuildContext) -> dict[str, Any]:
        request = context.request
        return {
            "task": "build_deck",
            "user_request": request.user_prompt,
            "character": request.character,
            "era": request.era,
            "direction": request.direction,
            "environment": context.environment_id,
            "allowed_mechanics": list(context.allowed_mechanics),
            "forbidden_mechanics": list(context.forbidden_mechanics),
            "forbidden_mode": request.forbidden_mode,
            "authorities": self._authorities(),
            "output_contract": {
                "direction": "string",
                "concept": "string",
                "cards": [{"name": "string", "qty": "1..3", "side": "bool optional"}],
                "axes": ["semantic axis strings"],
                "narrative_summary": "string",
                "mastered_functions": ["2 to 4 mastered functions"],
                "limited_functions": ["at least one important limited/absent function"],
                "potential": "integer 1..10",
                "development_level": "rudimentaire|en développement|solide|avancé|très avancé|quasi optimal",
                "pilotage_guide": ["player-facing branch choice guidance; required when 2+ axes"],
                "breakpoint": "important weakness / point de rupture",
                "signature_cards": ["semantically chosen cards for main visual component, optional"],
                "terminal_quote": "optional character quote; semantic content only",
                "lines": [{
                    "title": "string",
                    "starters": ["card names"],
                    "claim": "string",
                    "certainty": "GUARANTEED|CONDITIONAL|RANGE|RANDOM|UNKNOWN",
                    "essential": "bool",
                    "visual_cards": ["semantically chosen cards for this line, optional"],
                    "actions": [{
                        "label": "human semantic step",
                        "kind": "NORMAL_SUMMON|SET_SCALE|SYNCHRO_SUMMON|XYZ_SUMMON|LINK_SUMMON|PENDULUM_SUMMON|ACTIVATE_EFFECT",
                        "card": "card name or null",
                        "materials": ["card names"],
                        "consequences": [{
                            "operator": "REQUIRE|MOVE|CONSUME|OBTAIN|PRODUCE|PROPERTY_UPDATE|RESTRICTION_APPLY|RESTRICTION_RELEASE|DAMAGE_EVENT|LETHAL_CHECK",
                            "subject": "card name when applicable",
                            "source": "zone optional",
                            "destination": "zone optional",
                            "qty": "integer optional",
                            "scope": "semantic scope optional",
                            "property_name": "optional",
                            "value": "optional",
                            "params": "semantic parameters only",
                        }],
                    }],
                }],
                "notes": ["optional semantic notes"],
            },
            "hard_boundary": "Do not output IDs, hashes, counts, bindings, legality/proof status, freshness, routing or publication fields.",
        }

    @staticmethod
    def _semantic_draft_view(draft: SemanticDeckDraft) -> dict[str, Any]:
        return {
            "direction": draft.direction,
            "concept": draft.concept,
            "cards": [{"name": c.name, "qty": c.qty, "side": c.side} for c in draft.cards],
            "axes": list(draft.axes),
            "narrative_summary": draft.narrative_summary,
            "mastered_functions": list(draft.mastered_functions),
            "limited_functions": list(draft.limited_functions),
            "potential": draft.potential,
            "development_level": draft.development_level,
            "pilotage_guide": list(draft.pilotage_guide),
            "breakpoint": draft.breakpoint,
            "signature_cards": list(draft.signature_cards),
            "terminal_quote": draft.terminal_quote,
            "notes": list(draft.notes),
            "lines": [{
                "title": line.title,
                "starters": list(line.starters),
                "claim": line.claim,
                "certainty": line.certainty.value,
                "essential": line.essential,
                "visual_cards": list(line.visual_cards),
                "actions": [{
                    "label": action.label,
                    "kind": action.kind,
                    "card": action.card,
                    "materials": list(action.materials),
                    "certainty": action.certainty.value,
                    "consequences": [{
                        "operator": c.operator,
                        "subject": c.subject,
                        "source": c.source,
                        "destination": c.destination,
                        "qty": c.qty,
                        "scope": c.scope,
                        "property_name": c.property_name,
                        "value": c.value,
                        "params": dict(c.params),
                    } for c in action.consequences],
                } for action in line.actions],
            } for line in draft.lines],
        }

    @staticmethod
    def _structural_issues(draft: SemanticDeckDraft) -> tuple[ValidationIssue, ...]:
        issues = []
        if not draft.cards:
            issues.append(ValidationIssue("DECK_EMPTY", "deck contains no semantic card choices", IssueOwner.MODEL))
        if not draft.axes:
            issues.append(ValidationIssue("AXES_MISSING", "at least one strategic axis is required", IssueOwner.MODEL))
        if not any(line.essential for line in draft.lines):
            issues.append(ValidationIssue("ESSENTIAL_LINE_MISSING", "at least one essential player-facing line is required", IssueOwner.MODEL))
        if not 2 <= len(draft.mastered_functions) <= 4:
            issues.append(ValidationIssue("NARRATIVE_MASTERED_FUNCTIONS", "progression narrative requires 2..4 mastered functions", IssueOwner.MODEL))
        if len(draft.limited_functions) < 1:
            issues.append(ValidationIssue("NARRATIVE_LIMIT_MISSING", "progression narrative requires at least one important limited/absent function", IssueOwner.MODEL))
        if draft.potential is None or not 1 <= draft.potential <= 10:
            issues.append(ValidationIssue("NARRATIVE_POTENTIAL_MISSING", "progression narrative requires potential 1..10", IssueOwner.MODEL))
        allowed_levels={"rudimentaire","en développement","solide","avancé","très avancé","quasi optimal"}
        if draft.development_level.casefold() not in {x.casefold() for x in allowed_levels}:
            issues.append(ValidationIssue("NARRATIVE_LEVEL_INVALID", "progression narrative requires an allowed development level", IssueOwner.MODEL))
        if len(draft.axes) >= 2 and not draft.pilotage_guide:
            issues.append(ValidationIssue("PILOTAGE_GUIDE_MISSING", "two or more axes require a visible pilotage guide", IssueOwner.MODEL))
        if not draft.breakpoint:
            issues.append(ValidationIssue("BREAKPOINT_MISSING", "a complete deck requires a visible point de rupture", IssueOwner.MODEL))
        return tuple(issues)

    def _repair_request(self, context: BuildContext, draft: SemanticDeckDraft, issues: list[ValidationIssue]) -> dict[str, Any]:
        return {
            "task": "repair_deck",
            "user_request": context.request.user_prompt,
            "character": context.request.character,
            "era": context.request.era,
            "allowed_mechanics": list(context.allowed_mechanics),
            "forbidden_mechanics": list(context.forbidden_mechanics),
            "current_semantic_draft": self._semantic_draft_view(draft),
            "business_issues": [
                {"code": issue.code, "message": issue.message, "card": issue.card_name}
                for issue in issues
            ],
            "instruction": "Return a complete revised semantic draft only. Do not add runtime/compiler/validator fields.",
        }

    def _audit_action(self, action, facts) -> tuple[bool | None, str]:
        card = facts.get(action.card_name) if action.card_name else None
        if card is None or not card.effect_text.strip():
            return None, "material card text unavailable"
        request = {
            "task": "semantic_audit",
            "card": card.canonical_name,
            "card_type": card.card_type,
            "effect_text": card.effect_text,
            "action": {
                "label": action.label,
                "kind": action.kind,
                "card": action.card_name,
                "materials": list(action.materials),
                "consequences": [{
                    "operator": c.operator,
                    "subject": c.subject,
                    "source": c.source,
                    "destination": c.destination,
                    "qty": c.qty,
                    "scope": c.scope,
                    "property_name": c.property_name,
                    "value": c.value,
                    "params": dict(c.params),
                } for c in action.consequences],
            },
            "instruction": "Independently judge whether the material consequences are supported by the supplied card text. Return only {supported: bool, reason: string}. Do not return IDs/hashes/bindings/status fields.",
        }
        raw = self.model(request)
        if not isinstance(raw, Mapping):
            return None, "semantic audit did not return an object"
        allowed = {"supported", "reason"}
        if set(raw) - allowed or not isinstance(raw.get("supported"), bool):
            return None, "semantic audit returned an invalid schema"
        return raw["supported"], str(raw.get("reason", ""))

    def _semantic_audit_map(self, deck) -> tuple[dict[str, bool], ValidationIssue | None]:
        facts = {entry.facts.canonical_name: entry.facts for entry in deck.entries}
        result: dict[str, bool] = {}
        for line in deck.lines:
            for action in line.actions:
                if not action.consequences:
                    continue
                supported, reason = self._audit_action(action, facts)
                if supported is None:
                    return result, ValidationIssue(
                        code="SEMANTIC_AUDIT_RUNTIME_FAILURE",
                        message=reason,
                        owner=IssueOwner.RUNTIME,
                        proof_status=ProofStatus.UNVERIFIED,
                        line_id=line.line_id,
                        card_name=action.card_name,
                    )
                result[action.action_id] = supported
        return result, None

    @staticmethod
    def _failure_result(status: ProofStatus, issues: list[ValidationIssue], deck=None) -> DeckResult:
        report = ValidationReport(
            status=status,
            issues=tuple(issues),
            legality_passed=False,
            combos_passed=False,
            publication_allowed=False,
        )
        summary = "Validation bloquée; aucun deck final publié.\n" + "\n".join(f"- {i.code}: {i.message}" for i in issues)
        return DeckResult(status=status, final_text=summary, deck=deck, report=report)

    @staticmethod
    def _render(deck) -> str:
        sections = {"MAIN": [], "EXTRA": [], "SIDE": []}
        totals = {"MAIN": 0, "EXTRA": 0, "SIDE": 0}
        main_groups = {"Monstres": [], "Magies": [], "Pièges": []}
        main_group_totals = {k: 0 for k in main_groups}
        for entry in deck.entries:
            key = entry.section.value
            totals[key] += entry.qty
            sections[key].append((entry.facts.canonical_name, entry.qty))
            if key == "MAIN":
                ctype=entry.facts.card_type.casefold()
                group="Magies" if "spell" in ctype else "Pièges" if "trap" in ctype else "Monstres"
                main_groups[group].append((entry.facts.canonical_name, entry.qty))
                main_group_totals[group] += entry.qty
        character = deck.context.request.character.strip() or "Deck"
        lines = [
            f"# {character} — {deck.concept}",
            "",
            f"**Direction :** {deck.direction}",
            f"**Progression narrative :** {deck.narrative_summary or 'Conforme au contrat du run.'}",
            f"**Potentiel :** {deck.potential}/10 · **Niveau :** {deck.development_level}",
            "**Maîtrisé :** " + "; ".join(deck.mastered_functions),
            "**Limité / absent :** " + "; ".join(deck.limited_functions),
            "",
            "## Concept du deck",
            deck.concept,
            "",
            "## Decklist",
            f"### Main Deck — {totals['MAIN']}",
        ]
        for group in ("Monstres","Magies","Pièges"):
            if main_groups[group]:
                lines.append(f"#### {group} — {main_group_totals[group]}")
                lines.extend(f"- {qty}× {name}" for name, qty in main_groups[group])
        lines.append("")
        for key, label in (("EXTRA", "Extra Deck"), ("SIDE", "Side Deck")):
            lines.append(f"### {label} — {totals[key]}")
            if sections[key]:
                lines.extend(f"- {qty}× {name}" for name, qty in sections[key])
            else:
                lines.append("- —")
            lines.append("")
        lines.append("## Axes de jeu")
        lines.extend(f"- {axis}" for axis in deck.axes)
        if deck.pilotage_guide:
            lines.extend(["", "## Guide de pilotage"] + [f"- {item}" for item in deck.pilotage_guide])
        lines.extend(["", "## Lignes vérifiées"])
        for line in deck.lines:
            lines.append(f"### {line.title} — {line.certainty.value}")
            if line.starters:
                lines.append("**Starters :** " + " + ".join(line.starters))
            for idx, action in enumerate(line.actions, 1):
                lines.append(f"{idx}. {action.label or action.kind}")
            lines.append(f"**Résultat :** {line.claim}")
            lines.append("")
        lines.extend(["## Point de rupture", deck.breakpoint, ""])
        if deck.terminal_quote:
            lines.extend(["## Réplique", deck.terminal_quote, ""])
        return "\n".join(lines).rstrip() + "\n"

    def build_deck(self, request: BuildRequest) -> DeckResult:
        try:
            context = self._build_context(request)
        except CardDataError as exc:
            return self._failure_result(ProofStatus.UNVERIFIED, [ValidationIssue(exc.code, str(exc), IssueOwner.DATA, ProofStatus.UNVERIFIED)])

        if request.direction is None:
            report = ValidationReport(ProofStatus.UNVERIFIED, (), False, False, False)
            message = (
                "Direction requise avant construction : choisissez **Canonique**, **Canonique remixé** ou **Alternatif**.\n"
                "Aucune direction n'a été choisie silencieusement par le runtime.\n"
            )
            return DeckResult(ProofStatus.UNVERIFIED, message, None, report)

        draft: SemanticDeckDraft | None = None
        repair_count = 0
        next_request = self._initial_model_request(context)

        while True:
            try:
                raw = self.model(next_request)
                draft = self.parse_model_draft(raw)
            except Exception as exc:
                return self._failure_result(ProofStatus.FAILED, [ValidationIssue("MODEL_CONTRACT_INVALID", str(exc), IssueOwner.MODEL)])

            structural = list(self._structural_issues(draft))
            if structural:
                if repair_count < request.max_repairs:
                    repair_count += 1
                    next_request = self._repair_request(context, draft, structural)
                    continue
                return self._failure_result(ProofStatus.FAILED, structural)

            try:
                compiled = compile_draft(draft, context, self.card_data)
            except CardDataError as exc:
                owner = IssueOwner.MODEL if exc.code in {"CATALOG_CARD_NOT_FOUND", "CATALOG_CARD_AMBIGUOUS"} else IssueOwner.DATA
                status = ProofStatus.FAILED if owner == IssueOwner.MODEL else ProofStatus.UNVERIFIED
                issue = ValidationIssue(exc.code, str(exc), owner, status)
                if owner == IssueOwner.MODEL and repair_count < request.max_repairs:
                    repair_count += 1
                    next_request = self._repair_request(context, draft, [issue])
                    continue
                return self._failure_result(status, [issue])

            legality = validate_deck_legality(compiled)
            non_model_blockers = [i for i in legality.issues if i.owner != IssueOwner.MODEL]
            model_issues = [i for i in legality.issues if i.owner == IssueOwner.MODEL]
            if non_model_blockers:
                status = ProofStatus.UNVERIFIED if any(i.proof_status == ProofStatus.UNVERIFIED for i in non_model_blockers) else ProofStatus.FAILED
                return self._failure_result(status, non_model_blockers, compiled)
            if model_issues:
                if repair_count < request.max_repairs:
                    repair_count += 1
                    next_request = self._repair_request(context, draft, model_issues)
                    continue
                return self._failure_result(ProofStatus.FAILED, model_issues, compiled)

            audit_map, audit_runtime_issue = self._semantic_audit_map(compiled)
            if audit_runtime_issue is not None:
                return self._failure_result(ProofStatus.UNVERIFIED, [audit_runtime_issue], compiled)

            combos = validate_combo_lines(compiled, semantic_audit=audit_map)
            combined = combine_validation(legality, combos)
            non_model_blockers = [i for i in combined.issues if i.owner != IssueOwner.MODEL]
            model_issues = [i for i in combined.issues if i.owner == IssueOwner.MODEL]
            if non_model_blockers:
                status = ProofStatus.UNVERIFIED if any(i.proof_status == ProofStatus.UNVERIFIED for i in non_model_blockers) else ProofStatus.FAILED
                return self._failure_result(status, non_model_blockers, compiled)
            if model_issues or not combined.publication_allowed:
                if model_issues and repair_count < request.max_repairs:
                    repair_count += 1
                    next_request = self._repair_request(context, draft, model_issues)
                    continue
                return DeckResult(status=combined.status, final_text="Validation échouée; aucun deck final publié.\n", deck=compiled, report=combined)

            return DeckResult(
                status=ProofStatus.PROVED,
                final_text=self._render(compiled),
                deck=compiled,
                report=combined,
                presentation_plan=compile_presentation_plan(compiled),
            )
