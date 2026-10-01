# TEST / PROOF MATRIX — Corrective on V5 V2

## 0. Règles de lecture

Aucun test corrective n'est marqué exécuté avant GO. `PARENT_PASS` ne signifie que preuve historique sur V5 exact. `REFERENCE` signifie capacité observée dans V4 exact. `PLANNED` = exigé à son gate.

### Gates / timing

- `G0` Characterization — zéro mutation produit.
- `G1` Contracts / ownership.
- `G2` CardFactsResolver.
- `G3` Proof compiler / MCB / lineage.
- `G4` Resource replay + snapshots.
- `G5` Action legality + summon/material + Quasar.
- `G6` Dynamic properties + restrictions.
- `G7` Backward / claims / cold audit.
- `G8` Continuous-run controller + full integration.
- `G9` Differential/full regression/package replay ; Black-Box seulement après déterministic closure.

## 1. REQ → tâche → change surface

| Task | REQ principaux | But | MUST-TOUCH | MAY-TOUCH | Exit local |
|---|---|---|---|---|---|
| T0 | 001,003,004,008,014,015-027 | matérialiser parent/reference, REDs et 12-capability map | aucun produit | tests, fixtures, governance | aucune mutation avant RED + controls |
| T1 | 002,003,015,020,027 | contracts ownership, model schema, run-control schema | `contracts.py` | `compiler.py`,`runtime.py` | model ne peut écrire proof/flow data |
| T2 | 004,005,007,025,027 | resolver multi-route + provenance/conflict | `card_data.py` | `contracts.py`,`runtime.py` | provider failure non terminal si route restante |
| T3 | 002,003,006,016,020 | ProofPlan, ledger seed, MCB, lineage/stale | `compiler.py` | `contracts.py` | same source=>same compile; no model MCB |
| T4 | 001,008,016,017 | forward replay, exact copies/zones, snapshots | `validator.py` | `contracts.py`,`compiler.py` | no double-spend/use-before-produce |
| T5 | 015,018,019 | action legality + generic summon/material proof | `validator.py`,`compiler.py` | `contracts.py`,`card_data.py` | Quasar valid PASS / invalid FAIL sans hardcode |
| T6 | 018,021 | effective properties + persistent restrictions | `validator.py`,`compiler.py` | `contracts.py` | state-exact properties/restrictions |
| T7 | 009,022,023,024 | backward, critical decisions, claims, cold audit | `validator.py`,`compiler.py` | `runtime.py`,`contracts.py` | higher-order proof restored |
| T8 | 001,004,007,010,011,027 | deterministic controller, routing, auto recovery, publication | `runtime.py` | `api.py`,`card_data.py`,`compiler.py`,`contracts.py` | one call continuous run; AI only when policy permits |
| T9 | 014,026 + all preserve | integration/differential/closure | normalement aucun core | instruction/manifest integration-only | all guards + exact package replay |

## 2. Mandatory RED / KILL inventory

| ID | REQ | Gate | Expected RED before patch |
|---|---|---|---|
| RED-PROVIDER-FALLBACK | 025/027 | G0/G2 | provider A down stops instead of route B |
| RED-PROVIDER-EXHAUSTION | 025 | G0/G2 | unresolved semantics incorrect |
| RED-DATA-CONFLICT | 004/025 | G2 | conflict silently chosen |
| RED-MODEL-MCB-SECRETARIAT | 003/020 | G0/G1 | model can author low-level consequence/proof fields |
| RED-QUASAR-UNSUPPORTED | 015/019 | G0/G5 | valid Quasar rejected due wording support |
| RED-QUASAR-INVALID | 019 | G5 | invalid materials accepted |
| RED-DOUBLE-SPEND | 017 | G4 | same resource consumed twice |
| RED-USE-BEFORE-PRODUCE | 017 | G4 | output used before producer |
| RED-BEFORE-AFTER | 017/018 | G4 | state timing conflated |
| RED-ACTION-CONSTRAINT | 018 | G5 | bound predicate violation passes |
| RED-DYNAMIC-PROPERTY | 021 | G6 | effective property timing wrong |
| RED-RESTRICTION-PERSISTENCE | 021 | G6 | restriction disappears/leaks incorrectly |
| RED-BACKWARD-FUTURE | 022 | G7 | upstream choice kills future resource undetected |
| RED-DERIVED-CLAIM | 023 | G7 | false guaranteed/numeric claim passes |
| RED-COLD-DIVERGENCE | 024 | G7 | primary/cold mismatch ignored |
| RED-CERTAINTY | 009/023 | G7 | conditional strengthens to guaranteed |
| RED-CONTINUOUS-HANDOFF | 027 | G8 | recoverable issue requires user continue |
| RED-MODEL-FLOW-CONTROL | 003/027 | G1/G8 | model can choose phase/retry/publish |
| RED-DATA-CALLS-MODEL | 007/025/027 | G8 | DATA recovery invokes AI |
| RED-RUNTIME-CALLS-MODEL | 007/027 | G8 | RUNTIME blocker invokes AI repair |
| RED-NO-PROGRESS-LOOP | 027 | G8 | identical repair state loops |
| RED-PUBLICATION-BYPASS | 010/027 | G8 | output published with stale/blocking proof |
| RED-DIFFERENTIAL-MISSING | 014/026 | G9 | green suite with missing V4 capability mapping qualifies |
| RED-LEGACY-DEPENDENCY | 013 | G9 | core imports/calls legacy harness |

## 3. Test-level matrix — tous les types + timing

Cell format : `GATE / scope / preuve`. `—` = non requis pour cette tâche, justifié par portée.

| Task | UNIT | RED/FAILURE | GREEN/HAPPY | LINE COVERAGE | BRANCH COVERAGE | INTEGRATION | MUTATION | E2E | DIFFERENTIAL | FULL REGRESSION | PACKAGE REPLAY | BLACK-BOX |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0 | G0 / fixture parsers / hashes exacts | G0 / Quasar+provider+secretariat characterization | G0 / parent valid controls | — | — | G0 / V4+V5 fixture readability | — | — | G0 / capability inventory only | — | — | — |
| T1 | G1 / contracts / reject forbidden fields | G1 / model flow+MCB fields accepted | G1 / semantic-only payload accepted | G1 / modified contract lines | G1 / reject/accept branches | G1 / model adapter→contracts | G1 / remove forbidden-field guard => test fails | — | G9 / preserve V5 schema behavior | G9 | G9 | post-G9 / anti-secretariat prompts |
| T2 | G2 / route order/cache/normalize/conflict | G2 / provider down, exhaustion, conflict | G2 / alternate route succeeds | G2 / resolver modified lines | G2 / every route/failure branch | G2 / runtime↔resolver with injected adapters | G2 / skip fallback/conflict guard mutants | G8 / one real/injected full DATA recovery path | G9 / parent pool-banlist behavior | G9 | G9 / packaged resolver fixtures + real route where available | post-G9 / provider outage campaign |
| T3 | G3 / compile identities/MCB/stale | G3 / manual MCB/stale reuse | G3 / deterministic recompile | G3 / compiler changed lines | G3 / stale/dependency branches | G3 / semantic+evidence→ProofPlan | G3 / bypass hash/MCB derivation mutant | G8 / through runtime | G9 / V4 MCB capability + V5 canonical compile | G9 | G9 | post-G9 / weird semantic lines |
| T4 | G4 / ledger/snapshot primitives | G4 / double spend/use-before-produce/timing | G4 / valid move/consume/produce | G4 / replay lines | G4 / consume/produce/zone/error branches | G4 / ProofPlan→ReplayTrace | G4 / disable quantity/timing guards | G8 / essential combo replay | G9 / V4 ledger+snapshots | G9 | G9 | post-G9 / adversarial long lines |
| T5 | G5 / predicates/cardinality/sum/summon bindings | G5 / Quasar unsupported + invalid material | G5 / valid Quasar proved | G5 / legality/summon lines | G5 / valid/invalid/unsupported-runtime branches | G5 / evidence→binding→replay | G5 / remove tuner/count/property check | G5 then G8 / Quasar end-to-end | G9 / V4 Action Legality + summon binding | G9 | G9 | post-G9 / non-standard summons |
| T6 | G6 / effective properties/restriction lifecycle | G6 / wrong timing/leak/release | G6 / modifier/restriction valid cases | G6 / changed lines | G6 / applies/not-applies/release branches | G6 / compiler bindings→replay state | G6 / ignore modifier/restriction mutant | G8 / combo with modifier+restriction | G9 / V4 dynamic property+restriction | G9 | G9 | post-G9 / edge interactions |
| T7 | G7 / backward/claims/cold primitives | G7 / future resource/false claim/divergence | G7 / correct critical decision/claim/cold agreement | G7 / changed lines | G7 / conditional/range/divergence branches | G7 / replay→backward+claims+cold | G7 / strengthen certainty/skip backward/cold mutant | G7/G8 / high-risk combo | G9 / V4 backward+claims+critical+cold | G9 | G9 | post-G9 / false-PASS campaign |
| T8 | G8 / state machine/call policy/progress guard | G8 / handoff, DATA/RUNTIME AI calls, model flow control, loop | G8 / automatic MODEL repair + DATA fallback + USER_REQUIRED resume | G8 / runtime changed lines | G8 / all owner/terminal/retry branches | G8 / API→controller→resolver/model/compiler/validator | G8 / route owner/publish/progress mutants | G8 / one-call full deck workflow | G9 / V5 thin API/routing/publication | G9 | G9 | post-G9 / unwanted handoff/retry masking |
| T9 | targeted only if closure tooling changes | G9 / missing guard/package divergence | G9 / complete capability map + clean replay | G9 / cumulative report | G9 / cumulative report | G9 / whole product | G9 / mandatory critical mutants all killed | G9 / representative deck flows | G9 / **mandatory 12 V4 + V5 parent guards** | G9 / **mandatory** | G9 / **mandatory exact bytes** | **after deterministic G9 only**, independent |

## 4. Timing / cost policy

| Test type | Earliest timing | Re-run timing | Cost | Rule |
|---|---|---|---|---|
| Characterization | G0 | if parent/reference changes | LOW/MED | before product mutation |
| UNIT | task gate G1-G8 | after local code change | LOW | fastest proof of local behavior |
| RED/FAILURE | before patch at each task gate | after patch as regression guard | LOW/MED | defect must be materialized first |
| GREEN/HAPPY | same gate as RED closure | whenever affected | LOW/MED | symmetric positive control mandatory where applicable |
| LINE COVERAGE | after local GREEN | after material local changes | LOW/MED | changed critical lines only first |
| BRANCH COVERAGE | after local GREEN | after branch changes | MED | failure branches included |
| INTEGRATION | once involved components individually green | G8 and affected changes | MED/HIGH | component interaction proof |
| MUTATION | after assertions stable | G9 critical cumulative | MED/HIGH | only critical guards/logic |
| E2E | first gate where behavior crosses full path (G5/G7/G8) | G9 representative suite | HIGH | not after every micro-patch |
| DIFFERENTIAL | characterization mapping G0; execution G9 after features stable | candidate closure | HIGH | V4 capability + V5 parent preservation |
| FULL REGRESSION | G9 only | before repackage after any fix | HIGH | cumulative candidate result |
| PACKAGE REPLAY | after full regression green at G9 | every exact final package | HIGH | bytes delivered, clean extract |
| BLACK-BOX | **after** deterministic closure/package replay | campaign rounds as planned | EXTERNAL/HIGH | independent; never substitutes deterministic proof |

## 5. Coverage contract

No global 100% requirement. Required:
- modified critical lines materially exercised ;
- relevant branches including failure paths exercised ;
- uncovered branch on critical modified surface must be justified or blocks closure ;
- cumulative coverage reported at G9 but not used as sole PASS criterion.

## 6. Mutation contract

Mandatory mutant families :
- anti-secretariat schema disabled ;
- provider fallback skipped ;
- conflict fail-closed disabled ;
- MCB manually trusted/model-owned ;
- double-spend guard removed ;
- action predicate skipped ;
- Quasar tuner/count/property check weakened through generic binding ;
- restriction persistence ignored ;
- backward dependency ignored ;
- certainty strengthened ;
- cold divergence ignored ;
- DATA/RUNTIME rerouted to MODEL ;
- publication gate bypassed ;
- progress guard disabled.

All mandatory critical mutants must be killed before G9 PASS.

## 7. Differential inventory

Each row must have fixture, V4 reference characterization, candidate guard and executed G9 result :
1. Proof-Carrying Line ; 2. Resource/copy ledger ; 3. BEFORE/AFTER ; 4. Action Legality ; 5. compiler MCB ; 6. summon/material binding ; 7. dynamic properties ; 8. persistent restrictions ; 9. Derived Claims ; 10. Backward Proof ; 11. Critical Decisions ; 12. Cold Audit.

Also replay V5 parent guards : six-module/thin API, canonical compile/stale, issue ownership, pool/banlist, narrative/direction, certainty, publication, legacy isolation.

## 8. Current execution status

Target `V5.1`, GO `YES` (explicit `/go V5.1`). Historical V5 exact : 52/52
parent regression PASS, 5/5 targeted mutants killed, 87% branch-aware
coverage, exact package replay 52/52 PASS. These remain parent evidence only.

### G0 — EXECUTED (no product mutation)

| Entry | Gate | Command | Result |
|---|---|---|---|
| RED-QUASAR-UNSUPPORTED | G0 | `python3 tests/test_g0_characterization.py -v` (`RedQuasarUnsupported`) | EXECUTED_PASS — defect reproduced |
| GREEN synchro parent control | G0 | same run (`GreenSynchroParentControl`) | EXECUTED_PASS |
| RED-PROVIDER-FALLBACK | G0 | same run (`RedProviderFallback`) | EXECUTED_PASS — defect reproduced |
| RED-MODEL-MCB-SECRETARIAT | G0 | same run (`RedModelMcbSecretariat`) | EXECUTED_PASS — defect reproduced |
| 12-capability map | G0 | `fixtures/V4_CAPABILITY_DIFFERENTIAL_MAP.md` materialized | EXECUTED_PASS (inventory only, rows PLANNED) |
| workspace diff | G0 | `python3 tools/verify_workspace.py --require-go` | EXECUTED_PASS — `worktree_changed=[]`, no product mutation |

G1..G9 entries remain `PLANNED` until their gate executes; this table is
updated in place per META-REQ-TEST-EVIDENCE (no verbal PASS).
