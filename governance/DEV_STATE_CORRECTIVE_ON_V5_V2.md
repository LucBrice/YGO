# DEV_STATE — Corrective on V5 V2

## Current

- Date : 2026-10-01
- Parent : V5 exact
- Parent SHA-256 : `87d4c297b82fb1aab1c5e3dc598dca400fb4e3e3325496d08325b12af818ac2a`
- Combo functional reference : V4 RC16.23.8 exact
- V4 SHA-256 : `90cb9f90c78e86725bb24a27c054f3603df20b670e961267bd62357b764dfb3e`
- Stable baseline : V3.6 STABLE
- Target : **V5.1** (assigned via explicit `/go V5.1`)
- PRE-GO : superseded by GO
- GO : YES
- Current gate : G0 CLOSED → entering G1
- Promotion : FORBIDDEN until G9 PASS

## G0 — Characterization (CLOSED, no product mutation)

Command executed: `python3 tools/verify_workspace.py --require-go` →
`workspace_status=PASS`, `worktree_changed=[]` (worktree still byte-identical
to `baseline_v5/source` after G0).

Command executed: `python3 tests/test_g0_characterization.py -v` → `OK`, 4/4
tests, against the exact unmutated worktree:

- `RedQuasarUnsupported.test_valid_quasar_materials_are_rejected_as_unsupported_today`
  — EXECUTED_PASS (RED reproduced: `SYNCHRO_REQUIREMENT_UNSUPPORTED`,
  owner RUNTIME, UNVERIFIED).
- `GreenSynchroParentControl.test_plain_generic_synchro_header_still_resolves`
  — EXECUTED_PASS (positive control: already-supported literal header still
  resolves, proving the defect is isolated to the qualified clause).
- `RedProviderFallback.test_single_provider_outage_blocks_with_no_fallback`
  — EXECUTED_PASS (RED reproduced: single provider outage raises
  `CARD_PROVIDER_UNAVAILABLE` with no alternate route attempted).
- `RedModelMcbSecretariat.test_model_can_author_raw_mechanical_consequence_today`
  — EXECUTED_PASS (RED reproduced: model-authored `operator/source/destination`
  consequence fields are currently accepted by `semantic_draft_from_mapping`).

12-capability V4↔candidate differential map materialized:
`fixtures/V4_CAPABILITY_DIFFERENTIAL_MAP.md` (all 12 rows PLANNED, no PASS
claimed yet — guards close per-gate at G3/G4/G5/G6/G7).

RED-CONTINUOUS-HANDOFF (mandatory defect #4, D5/REQ-CR-027) is deliberately
NOT characterized at G0: per `TEST_PROOF_MATRIX_CORRECTIVE_ON_V5_V2.md` §2 it
is a G8 integration-level RED (continuous-run controller), not a unit-level
one; materializing it requires the controller harness built at G8.

## Reconciled parent evidence

V5 exact historical evidence remains real : 52/52 full regression PASS after legacy retirement, 5/5 targeted mutants killed, 87% branch-aware coverage, exact package replay 52/52 PASS. Global qualification is stale for future candidate because Combo Proof differential coverage was incomplete.

## OPEN / REGRESSED

1. Combo Proof conservation V4→V5.
2. Runtime semantic overreach / Quasar canonical defect.
3. Model-authored low-level consequences.
4. Single-provider Card Data blocking.
5. Missing complete V4 capability differential baseline.
6. Continuous-run orchestration not yet enforced in code.

## Governance DONE

- Engineering Intent V2 materialized.
- Target Architecture V2 materialized.
- Data Architecture V1 materialized as standalone normative document.
- Requirements Registry V2 materialized.
- Test/Proof Matrix V2 expanded with every required test level + timing/gate/scope/cost policy.
- Change Surface Contract V1 materialized in human-readable + JSON forms.
- PRE-GO V2 updated to G0..G9.
- V4↔V5 reconciliation retained.
- No product file mutated.

## Product state

`worktree/source` must remain byte-identical to exact V5 while gate is PRE_GO.

## G1 — Contracts/ownership (CLOSED)

`current_gate=G1`. `worktree_changed=["compiler.py","contracts.py","runtime.py"]`
(⊆ T1 Authorized Diff Surface; `validator.py`/`card_data.py`/`api.py`
untouched, matching T1 NO-TOUCH). REQ-CR-020 CLOSED. REQ-CR-003 PARTIAL
(secretariat removed for mechanical consequences; flow-control part of 003
still depends on REQ-CR-027 at G8).

Schema changes: `SemanticAction.consequences` → `SemanticAction.effects`
(model-facing, closed `EffectInterpretationKind`, zero operator/zone
fields); `compiler.project_mechanical_consequences` deterministically
projects effects into compiler-owned `MechanicalConsequenceBinding`
(`CanonicalAction.consequences`, field name kept to respect validator.py
NO-TOUCH). `FORBIDDEN_MODEL_FIELDS` extended with the Data Architecture V1
§11 run-control set. RunState/StateSnapshot/ActionLegalityProof/
SummonMaterialBinding/DerivedClaim/BackwardRequirement/CriticalDecision/
ColdAuditResult/ResolutionAttempt dataclasses added to contracts.py as
forward schema for G2..G8 (all currently unused-by-validator, so no
validator.py change required yet — additive, backward compatible).

Proofs made stale (per PRE-GO §7): `tests/test_g0_characterization.py::RedModelMcbSecretariat`
(intentionally, documented in its own header).

## G2 — CardFactsResolver multi-route (CLOSED)

`current_gate=G2`. `worktree_changed=["card_data.py","compiler.py","contracts.py","runtime.py"]`.
REQ-CR-025 CLOSED, REQ-CR-004 CLOSED. `CardFactsResolver` tries ordered
injectable routes, cache-first, provenance via `ResolutionAttempt`,
`CARD_FACTS_UNRESOLVED` only after exhaustion, `CARD_FACTS_CONFLICT` in
`verify=True` mode. `CardDataService(routes=[...])` and
`Runtime(card_routes=[...])` are the new multi-route entry points;
single-route `provider=`/`card_provider=` stay backward compatible.

Proofs made stale: `tests/test_g0_characterization.py::RedProviderFallback`
(documented in its header; error code intentionally changed from
`CARD_PROVIDER_UNAVAILABLE` to `CARD_FACTS_UNRESOLVED` once routes are
exhausted rather than propagating the first route's raw error).

## G3 — Proof compiler / ProofPlan / lineage (CLOSED)

`current_gate=G3`. REQ-CR-016 PARTIAL/CLOSED-for-identity (see registry).
`compiler.build_proof_plan` content-addresses `ProofPlan` by
semantic_hash+evidence_set_hash+context_hash+compiler_schema_version;
`compiler.proof_plan_is_fresh` detects staleness from either a semantic OR
an evidence (CardFacts) change — closing a real gap in the pre-existing
`is_fresh()` helper, which only ever checked the semantic hash. `compile_draft`
now attaches `proof_plan` to every `CanonicalDeck` it returns.

## G4 — Resource replay / BEFORE-AFTER snapshots (CLOSED)

`current_gate=G4`. `worktree_changed` adds `validator.py` for the first
time (T4 MUST-TOUCH). REQ-CR-017 CLOSED. `validator._snapshot` + the new
`ValidationReport.replay_trace` field formalize immutable BEFORE/AFTER
`StateSnapshot`s around every material action; the pre-existing zone-Counter
engine already enforced no-double-spend/use-before-produce structurally —
G4 adds the explicit regression-guard proof plus the replay artifact G5/G7
will consume.

## G5 — Generic summon/material binding + Quasar (CLOSED) — headline defect fixed

`current_gate=G5`. REQ-CR-019 CLOSED, REQ-CR-015/018 PARTIAL (summon path
closed). `compiler.parse_summon_material_clause` is a single generic,
card-name-free grammar for Synchro/Xyz/Link material headers (predicates:
TUNER/NON_TUNER/ANY, optional type qualifier, exact/min/max counts).
`compiler.build_summon_material_binding` attaches the derived
`SummonMaterialBinding` to each `CanonicalAction` at compile time.
`validator._evaluate_summon_material_binding` replaces the old
`_synchro_summon`/`_xyz_summon`/`_link_summon` (three near-duplicated
regex functions) with one evaluator that only ever reads the pre-compiled
binding against the BEFORE state.

Mandatory defect #1 from `00_START_HERE.md` ("Shooting Quasar Dragon valid
line blocked by runtime-specific Synchro wording support") is CLOSED: a
real Quasar clause ("1 Tuner + 2 or more non-Tuner Synchro Monsters")
previously failed with `SYNCHRO_REQUIREMENT_UNSUPPORTED` purely because the
old regex matched one literal string; it now resolves generically. No
"Quasar" token exists in `validator.py`/`compiler.py` (grep-verified by a
test). Invalid Quasar materials still fail, as required by the symmetric
positive control.

Proofs made stale: `tests/test_g0_characterization.py::RedQuasarUnsupported`
and `::GreenSynchroParentControl` (documented in the G0 file's header; both
called the now-removed `validator._synchro_summon`).

## G6 — Dynamic properties + persistent restrictions (CLOSED)

`current_gate=G6`. REQ-CR-021 CLOSED. A real latent defect was found and
fixed: `_effective_level`/`_effective_tuner` read a property override keyed
only by card name, with no scoping to the exact instance/placement that
earned it and no purge on departure -- a later, unrelated copy of the same
card name arriving on FIELD would silently inherit a stale override from an
earlier copy. Fixed via a while-on-FIELD gate plus `_purge_properties_if_left_field`
invoked from `_move` on every departure. `_effective_name` added for
REQ-CR-021 completeness (same lifecycle; no consumer yet, documented as
reserved). Restriction apply/block/release/unblock lifecycle and no
cross-line leakage materialized as new regression guards (already correct
structurally; never previously tested in this workspace).

## G7 — Derived Claims / Backward Proof / Critical Decisions / Cold Audit (CLOSED, bounded scope)

`current_gate=G7`. REQ-CR-022/023/024 CLOSED within the scope implemented
(see `fixtures/V4_CAPABILITY_DIFFERENTIAL_MAP.md` for exact boundaries —
honestly marked PARTIAL where a fuller V4-parity implementation remains
possible: unified ProofPlan object graph, first-class ActionLegalityProof
artifact, cold audit beyond summon bindings). 9 of 12 V4 combo capabilities
are now CLOSED; 3 are PARTIAL (not OPEN/REGRESSED).

`validator._derived_claim_for_line` recomputes a line's numeric claim from
its own replay damage accumulator, never from a model assertion;
`validator._claim_certainty_issue` enforces REQ-CR-023 monotonicity via the
G1 `certainty_at_least_as_strong` helper (finally consumed).
`validator.compute_backward_requirements` is a bounded, static,
card-name-free lookahead: total per-resource demand across a line vs. the
deck's total copies, attributing the violation to the action that tips
demand past supply. Every such finding is promoted to a `CriticalDecision`.
`validator.cold_audit_summon_bindings` independently re-derives each
summon's binding straight from `CardFacts.effect_text` (bypassing the
already-compiled `action.summon_binding`) and flags any signature
divergence.

## G8 — Deterministic continuous-run controller (CLOSED) — all 4 mandatory defects now fixed

`current_gate=G8`. REQ-CR-027 CLOSED. REQ-CR-003 fully CLOSED (mechanical
consequences G1 + flow control G8). All 4 mandatory defects from
`00_START_HERE.md` are now closed:
1. Quasar valid-line-blocked-by-wording — CLOSED G5.
2. Single-provider blocking — CLOSED G2.
3. Model-authored mechanical consequences — CLOSED G1.
4. Unnecessary handoff / model orchestration — CLOSED G8.

`runtime._should_repair`/`_issue_fingerprint` add a genuine progress guard
(a repair that reproduces the identical blocking issue set stops the run
immediately instead of exhausting `max_repairs` uselessly). A final
`compiler.proof_plan_is_fresh` check guards the single publication gate
defensively before any `PROVED` result is returned. The DATA-fallback and
single-call-auto-repair invariants were already structurally correct
(G2's `CardFactsResolver` already exhausts routes internally; only
`owner=MODEL` issues ever trigger `self.model(...)`) and are now proven
materially rather than assumed.

## NEXT_STEP

Proceed to G9: differential closure. Fill the remaining honest gaps in the
12-capability map (unified ProofPlan object graph, first-class
ActionLegalityProof artifact, cold audit beyond summon bindings) only if a
failing proof demands it; otherwise run full cumulative regression, verify
the Authorized Diff Surface end to end, package `worktree/source` as flat
Sources, extract clean, and replay the full suite on the packaged bytes.
