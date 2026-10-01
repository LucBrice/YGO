# V4 → Candidate 12-Capability Differential Map (G0 characterization)

Materialized at G0, no product mutation. Updated as each gate closes a guard.
Normative source: `governance/REGISTRE_REQUIREMENTS_CORRECTIVE_ON_V5_V2.md` REQ-CR-026,
`governance/TEST_PROOF_MATRIX_CORRECTIVE_ON_V5_V2.md` §7, `proofs/RECONCILIATION_ETAT_V4_V5_2026-10-01.md`.

V4 reference package: `YGO_V4_RC16_23_8_TERMINAL_CLOSURE_SOURCES(1).zip`,
SHA-256 `90cb9f90c78e86725bb24a27c054f3603df20b670e961267bd62357b764dfb3e`.
V4 is read as behavioral reference only (`reference_v4/source/harness_runtime_v1.py`,
NO-TOUCH, never imported into product). Historical V4 manifest evidence: targeted
12/12 PASS, Red-Team 9/9 PASS, mutants 5/5 killed, differential candidate 25/25
with 0 protected loss (per RECONCILIATION §V4).

| # | Capability | V4 reference anchor (harness_runtime_v1.py) | Candidate guard (this chantier) | Status |
|---|---|---|---|---|
| 1 | Proof-Carrying Line | `validate_execution_replay`, `_validate_rc16_semantic_inputs` | `ProofPlan` content-addressed by semantic_hash+evidence_set_hash (T3/G3) | PLANNED |
| 2 | Resource / copy ledger | `_mcb_resource_move`, `_clone_replay_state` | `ResourceLedger` zone/copy tracking + double-spend guard tests (T4/G4) | PLANNED |
| 3 | BEFORE/AFTER snapshots | `_eval_state_precondition`, `_validate_step_state_preconditions` | Explicit `StateSnapshot` BEFORE/AFTER per action (T4/G4) | PLANNED |
| 4 | Action Legality Proof | `_validate_action_legality` | `ActionLegalityProof` generic evaluation vs BEFORE (T5/G5) | PLANNED |
| 5 | Compiler MCB | `_apply_mcb_action`, `_validate_mcb_bindings` | `MechanicalConsequenceBinding` compiler-owned projection (T3/G3) | PLANNED |
| 6 | Summon/material binding | (RC16 participant/constraint inventories, generalized here) | `SummonMaterialBinding` generic grammar, Quasar guard (T5/G5) | **CLOSED G5** — `tests/test_g5_summon_material_binding.py` 10/10 PASS, Quasar valid PROVED / invalid FAILED / E2E PROVED |
| 7 | Dynamic material properties | `_apply_property_updates` | effective level/tuner/name bound to exact state (T6/G6) | **CLOSED G6** — real leak found+fixed, `tests/test_g6_*` 6/6 PASS |
| 8 | Persistent restrictions | restriction/active-constraint inventories | restriction apply/release lifecycle guard (T6/G6) | **CLOSED G6** — apply/block/release/unblock + no cross-line leak |
| 9 | Derived Claims | `_validate_derived_claims`, `_eval_derived_expr` | `DerivedClaim` recomputed from replay, certainty monotonic (T7/G7) | PLANNED |
| 10 | Backward Proof | `_validate_rc16_backward_proof` | upstream-consumption-breaks-future-requirement check (T7/G7) | PLANNED |
| 11 | Critical Decisions | (derived from backward proof divergence) | flagged only when legal alternatives diverge in future viability (T7/G7) | PLANNED |
| 12 | Cold Audit | `_project_unified_cold_audit`, `_compare_mcb_cold_projection` | independent recomputation hash-compared to primary binding (T7/G7) | PLANNED |

## V5 parent preserve guards (must stay green, not part of the 12 V4 capabilities)

six-module/thin API, canonical compile/stale, issue ownership (MODEL/DATA/RUNTIME),
pool/banlist environment separation, narrative/direction gate, certainty monotonicity
(parent), single publication gate, legacy isolation. Tracked via G9 full regression
against the existing `tests/` suite plus this chantier's additions.

## Explicit non-restoration

V4's RC16 CLI/session/lease/receipt bureaucracy (`cmd_pilotage_*`, continuation
leases, bootstrap capability tokens, journal/checkpoint files) is intentionally
NOT restored — forbidden by `governance/ENGINEERING_INTENT_CORRECTIVE_ON_V5_V2.md`
§7 Non-goals and `authority/METHODOLOGIE_DEV_YGO_V1.md` §12. Only the structural
proof *invariants* are carried forward into clean V5-native modules.
