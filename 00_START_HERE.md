# START HERE — YGO Corrective on V5 PRE-GO V3

This workspace is governance-ready and **not authorized for product mutation**.

## Authority order
1. Current explicit user instruction.
2. Current corrective governance in `governance/` + `control/`.
3. Permanent META-REQ / methodology / commands in `authority/`.
4. Exact V5 parent in `baseline_v5/source/`.
5. Exact V4 functional reference in `reference_v4/source/`.

## Current lock
- Parent: V5 exact
- Functional combo reference: V4 RC16.23.8 exact
- Target: **V5.1** (GO given 2026-10-01)
- GO: YES
- Gate: see `control/CURRENT_GATE.txt` (progressing G0→G9; see `governance/DEV_STATE_CORRECTIVE_ON_V5_V2.md` for live status)
- Worktree tracked in `worktree/source/`; diverges from parent only within the Authorized Diff Surface (`governance/CHANGE_SURFACE_CONTRACT_CORRECTIVE_ON_V5_V1.md`), verified at each gate via `tools/verify_workspace.py`.

## Read before any GO
1. `governance/ENGINEERING_INTENT_CORRECTIVE_ON_V5_V2.md`
2. `governance/TARGET_ARCHITECTURE_CORRECTIVE_ON_V5_V2.md`
3. `governance/DATA_ARCHITECTURE_CORRECTIVE_ON_V5_V1.md`
4. `governance/REGISTRE_REQUIREMENTS_CORRECTIVE_ON_V5_V2.md`
5. `governance/TEST_PROOF_MATRIX_CORRECTIVE_ON_V5_V2.md`
6. `governance/CHANGE_SURFACE_CONTRACT_CORRECTIVE_ON_V5_V1.md`
7. `governance/PRE_GO_CORRECTIVE_ON_V5_V2.md`
8. `governance/DEV_STATE_CORRECTIVE_ON_V5_V2.md`
9. `proofs/RECONCILIATION_ETAT_V4_V5_2026-10-01.md`

## Core intent
Keep V5's small six-module architecture, restore V4 combo-proof guarantees, make card lookup multi-route, and put the entire run under a deterministic controller so the AI is called only when semantic Yu-Gi-Oh! judgment is actually required.

## Mandatory defects (tracked; see governance/DEV_STATE_CORRECTIVE_ON_V5_V2.md for live status)
- Shooting Quasar Dragon valid line blocked by runtime-specific Synchro wording support. — **CLOSED G5**
- primary data provider unavailable blocks although web alternatives may exist. — **CLOSED G2**
- model can be asked to author low-level mechanical consequences. — **CLOSED G1**
- internal recoverable friction can cause an unnecessary handoff / model orchestration. — **CLOSED G8**

## Before GO
Run:
`python tools/verify_workspace.py`

Expected: target NOT_ASSIGNED, GO NO, PRE_GO, no worktree diff, PASS.

## On explicit `GO <version>`
Only then:
1. write exact target to `control/TARGET_VERSION.txt`;
2. set `GO_AUTHORIZATION.txt` to `YES`;
3. verify workspace;
4. enter **G0 characterization only**;
5. follow matrix timing; no opportunistic refactor or early expensive closure tests.
