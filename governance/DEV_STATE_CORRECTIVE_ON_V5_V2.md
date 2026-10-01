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

## NEXT_STEP

G0 closed materially. Proceed to G1 (`contracts.py` ownership/schema) per
`governance/PRE_GO_CORRECTIVE_ON_V5_V2.md` §3 and
`governance/CHANGE_SURFACE_CONTRACT_CORRECTIVE_ON_V5_V1.md` T1. Do not patch
`validator.py`/`compiler.py` combo logic (T3..T7) before T1 ownership
boundaries are closed, per the gate order.
