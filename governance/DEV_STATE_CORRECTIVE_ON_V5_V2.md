# DEV_STATE — Corrective on V5 V2

## Current

- Date : 2026-10-01
- Parent : V5 exact
- Parent SHA-256 : `87d4c297b82fb1aab1c5e3dc598dca400fb4e3e3325496d08325b12af818ac2a`
- Combo functional reference : V4 RC16.23.8 exact
- V4 SHA-256 : `90cb9f90c78e86725bb24a27c054f3603df20b670e961267bd62357b764dfb3e`
- Stable baseline : V3.6 STABLE
- Target : NOT_ASSIGNED
- PRE-GO : FROZEN
- GO : NO
- Current gate : PRE_GO
- Promotion : FORBIDDEN

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

User must assign exact target via `GO <version>`. Then enter G0; do not patch before Quasar/provider/secretariat/control REDs + complete V4 12-capability characterization are materialized.
