# CHANGE SURFACE CONTRACT — Corrective on V5 V1

## 0. Statut

**FROZEN PRE-GO — no product mutation.**
Parent : V5 exact. Target : NOT_ASSIGNED. GO : NO.

Global rule : `Actual Changed Surface ⊆ Authorized Diff Surface` et `NO_TOUCH ∩ Actual = ∅`.

## 1. Global surface

### MUST-TOUCH
- `source/contracts.py`
- `source/card_data.py`
- `source/compiler.py`
- `source/validator.py`
- `source/runtime.py`

### MAY-TOUCH
- `source/api.py` uniquement pour extension compatible du controller/resume ;
- `tests/**`
- `fixtures/**`

### INTEGRATION-ONLY MAY-TOUCH (G9)
- `source/INSTRUCTION_GENERALE_RC16_23.md`
- `source/SYSTEM_MANIFEST_V4.json`

### NO-TOUCH business authorities sauf amendement PRE-GO explicite
- banlist, contexte, game rules, card pool ;
- hooks/style/structure/validation spécialisées ;
- `SEMANTIC_RULING_CONTRACT_V1.md` ;
- `VALIDATION_PILOTAGE_LIGNES_DECKS_PERSONNAGES_V1.md`.

### IMMUTABLE workspace references
- `baseline_v5/source/**`
- `reference_v4/source/**`
- `authority/**`

## 2. Contrat par tâche

### T1 — Contracts / ownership
- MUST: `contracts.py`
- MAY: `compiler.py`, `runtime.py`
- PRESERVE: V5 public semantic request/deck fields utiles ; serialization stable compatible lorsque possible.
- NO-TOUCH: card resolver/validator logic.
- NON-GOALS: redesign complet API.
- INVARIANTS: proof/flow/data-admin fields non model-writable.
- DEPENDENCIES: compiler/runtime schemas/tests.
- PROOFS MADE STALE: schema/anti-secretariat parent proofs.

### T2 — CardFactsResolver
- MUST: `card_data.py`
- MAY: `contracts.py`, `runtime.py`
- PRESERVE: packaged pool/banlist precedence, cache provenance.
- NO-TOUCH: business authority files.
- NON-GOALS: remplacer les autorités Link Evolution par web current.
- INVARIANTS: one route failure non terminal ; conflict fail-closed ; no model-memory substitute.
- DEPENDENCIES: runtime DATA routing, EvidenceSet.
- PROOFS STALE: card-data/runtime integration proofs.

### T3 — Proof compiler / MCB
- MUST: `compiler.py`
- MAY: `contracts.py`
- PRESERVE: canonical IDs/hashes/counts/stale behavior.
- NO-TOUCH: semantic authorities.
- NON-GOALS: model-authored proof DSL.
- INVARIANTS: same semantic+evidence => same compiled proof identities ; derivable data system-owned.
- DEPENDENCIES: validator/runtime.
- PROOFS STALE: compile/stale/anti-secretariat.

### T4 — Forward replay
- MUST: `validator.py`
- MAY: `contracts.py`,`compiler.py`
- PRESERVE: fail-closed and certainty behavior.
- NO-TOUCH: card-specific authority sources.
- NON-GOALS: full card engine.
- INVARIANTS: exact resource continuity, immutable snapshots, no double-spend/use-before-produce.
- DEPENDENCIES: ProofPlan/ResourceLedger.
- PROOFS STALE: combo validation/certainty.

### T5 — Action legality / summon material
- MUST: `validator.py`,`compiler.py`
- MAY: `contracts.py`,`card_data.py`
- PRESERVE: generic validator architecture.
- NO-TOUCH: no named-card source edits.
- NON-GOALS: special-case Quasar.
- INVARIANTS: semantic/evidence binding determines constraints ; validator only evaluates generic constraints.
- DEPENDENCIES: CardFacts/EvidenceSet/ProofPlan.
- PROOFS STALE: combo/action legality/summon proofs.

### T6 — Dynamic properties / restrictions
- MUST: `validator.py`,`compiler.py`
- MAY: `contracts.py`
- PRESERVE: T4/T5 replay semantics.
- NO-TOUCH: runtime flow.
- NON-GOALS: encode every effect in validator.
- INVARIANTS: effective property evaluated at exact state ; restriction lifecycle explicit.
- DEPENDENCIES: snapshots/bindings.
- PROOFS STALE: combo higher-order proof.

### T7 — Backward / claims / cold audit
- MUST: `validator.py`,`compiler.py`
- MAY: `runtime.py`,`contracts.py`
- PRESERVE: certainty monotonicity/presentation semantics.
- NO-TOUCH: publication UI semantics except binding.
- NON-GOALS: restore V4 bureaucracy.
- INVARIANTS: future dependencies traceable ; claims derived ; cold audit independent of primary PASS.
- DEPENDENCIES: ReplayTrace/EvidenceSet.
- PROOFS STALE: certainty/claims/pilotage/cold audit.

### T8 — Continuous run controller
- MUST: `runtime.py`
- MAY: `api.py`,`card_data.py`,`compiler.py`,`contracts.py`
- PRESERVE: thin API, MODEL/DATA/RUNTIME ownership, single publication gate, quiet execution.
- NO-TOUCH: business authority files.
- NON-GOALS: workflow framework/event bus.
- INVARIANTS: runtime-only flow control ; closed model-call policy ; DATA/RUNTIME zero repair-AI calls ; bounded progress-aware MODEL repair ; no recoverable handoff.
- DEPENDENCIES: all core modules.
- PROOFS STALE: runtime integration/E2E/publication.

### T9 — Closure/integration
- MUST: none normally.
- MAY integration-only: instruction/manifest if exact packaging requires status/wiring update.
- PRESERVE: all product/business capabilities.
- NO-TOUCH: authorities unless separate amended PRE-GO.
- NON-GOALS: opportunistic refactor.
- INVARIANTS: complete differential, exact package replay, no legacy dependency.
- DEPENDENCIES: all tests/proofs.
- PROOFS STALE: any changed package bytes require new package replay/hash.

## 3. Forbidden changes

- restore/import/call legacy harness ;
- hardcode named-card validation fixes ;
- make provider A mandatory business dependency ;
- make MCB/ledger/snapshots/flow fields model-writable ;
- allow model next-stage/retry/provider/PASS/publish ;
- require user `continue/reprend` for recoverable MODEL/DATA issue ;
- route DATA/RUNTIME issue into semantic repair ;
- modify baseline/reference copies ;
- add product file/module without PRE-GO amendment.

## 4. Escalation rule

Si une correction correcte exige une surface non autorisée : **STOP, mark BLOCKED, amend PRE-GO before touching it.** Pas de refactor opportuniste.
