# PRE-GO — Corrective on V5 V2

## 0. Lock

- Parent exact : V5 (`87d4c297...18ac2a`)
- Functional combo reference : V4 RC16.23.8 (`90cb9f90...4dfb3e`)
- Stable baseline : V3.6 STABLE
- Target : `NOT_ASSIGNED`
- GO : `NO`
- Gate courant : `PRE_GO`
- Product mutation : **FORBIDDEN**

Ce PRE-GO supersède le PRE-GO corrective V1/V2 pour le prochain GO.

## 1. Scope REQ

Cumulatif : `REQ-CR-001..027`.
Actifs principaux : 001,003,004,006,008,014-027.
PRESERVE principaux : 002,005,007,009-013.

Documents normatifs chantier :
- Engineering Intent V2 ;
- Target Architecture V2 ;
- Data Architecture V1 ;
- Requirements Registry V2 ;
- Test/Proof Matrix V2 ;
- Change Surface Contract V1 ;
- Reconciliation V4↔V5.

## 2. Architecture target lock

Produit physique : six modules V5 uniquement.

- AI = semantic YGO authority when non-derivable.
- CardData = automatic evidence/facts acquisition.
- Compiler = all derivable technical/mechanical projection.
- Validator = generic deterministic proof shell.
- Runtime = deterministic controller/routing/recovery/publication.
- API = thin entry/resume boundary.

V4 est référence de capacités, jamais dépendance runtime.

## 3. Gates et tâches

### G0 — Characterization / RED baseline — NO PRODUCT MUTATION
Materialize :
- exact V5/V4 identities ;
- Quasar valid/invalid fixtures ;
- provider-fallback/exhaustion/conflict fixtures ;
- anti-secretariat/model-flow RED ;
- 12-capability V4 combo map ;
- V5 preserve guards inventory.

Tests : characterization + RED + GREEN controls only. Exit : tous les défauts importants reproduits ou BLOCKED.

### G1 — Contracts / ownership
Task T1. Fermer schema boundaries : semantic-only model output, runtime-only flow, typed RunState/Issue/Proof contracts.
Tests : unit, RED/GREEN, line/branch targeted, anti-secretariat/control mutation, integration adapter→contract.

### G2 — CardFactsResolver
Task T2. Multi-route resolver, provenance, conflicts, route exhaustion.
Tests : unit/failure/happy, line+branch, integration injected adapters, mutation. Live external route deferred jusqu'à G8/G9 si environnement bloque réseau direct.

### G3 — Proof compiler / MCB / data lineage
Task T3. ProofPlan, resources, MCB, summon bindings structure, dependency hashes/stale.
Tests : unit/RED/GREEN, line+branch, integration semantic+evidence→proof, mutation, deterministic recompile.

### G4 — Resource replay / snapshots
Task T4. Forward replay, copies/zones, BEFORE/AFTER, double spend/use-before-produce.
Tests : unit/RED/GREEN, line+branch, integration ProofPlan→ReplayTrace, mutation.

### G5 — Action legality + summon/material / Quasar
Task T5. Generic predicates/cardinality/sums/material bindings. **Quasar is mandatory RED/GREEN**, no named-card patch.
Tests : targeted unit, RED/GREEN, line+branch, integration evidence→binding→replay, mutants, Quasar E2E.

### G6 — Dynamic properties / persistent restrictions
Task T6. Effective properties at exact state + restriction lifecycle.
Tests : unit/RED/GREEN, line+branch, integration, mutation, combo E2E affected.

### G7 — Backward Proof / Critical Decisions / Derived Claims / Cold Audit
Task T7.
Tests : unit/RED/GREEN, line+branch, integration replay→higher-order proof, mutation, high-risk combo E2E.

### G8 — Continuous Run Controller / integration
Task T8. One deterministic controller from API request to terminal outcome.
Mandatory behaviors :
- DATA fallback automatic, zero DATA-induced AI repair calls ;
- MODEL repair minimal/bounded/progress-aware ;
- RUNTIME blocker zero AI repair calls ;
- model cannot choose stage/retry/provider/pass/publish ;
- genuine USER_REQUIRED only ; resume same logical run ;
- no `continue/reprend` for recoverable internal friction ;
- single publication gate exact/stale-safe.

Tests : controller unit state machine, RED/GREEN, line+branch, multi-component integration, owner/control/progress mutants, full workflow E2E, one real available web route if environment permits.

### G9 — Differential / full closure / package replay
No new feature patch unless a failing proof sends work back to earlier gate.

Required :
1. all targeted guards green ;
2. all mandatory critical mutants killed ;
3. complete 12-capability V4 differential executed PASS ;
4. V5 parent preserve guards PASS ;
5. cumulative line/branch report ;
6. full regression ;
7. actual diff ⊆ authorized diff ;
8. no NO-TOUCH violation ;
9. exact flat Sources package ;
10. clean extraction ;
11. replay exact packaged bytes ;
12. at least one real card-resolution route when technically available ;
13. independent external Black-Box only after deterministic closure ;
14. no auto-promotion.

## 4. Test plan complet et timing

La matrice normative détaillée est `TEST_PROOF_MATRIX_CORRECTIVE_ON_V5_V2.md`.

Ordre risk/cost-aware :
`characterization → RED/GREEN → local coverage → integration → mutation → relevant E2E → differential → full regression → package replay → Black-Box`.

Tous les niveaux ne sont pas relancés à chaque micro-patch. Le timing par tâche est normatif dans la matrix.

## 5. Mandatory positive controls

1. Provider A fails + alternate route resolves exact facts/provenance.
2. All routes exhausted => DATA_UNRESOLVED, no model-memory PASS.
3. Same semantic+evidence => same ProofPlan identity.
4. Upstream semantic/evidence change => downstream stale/rebuilt.
5. Valid simple resource line exact BEFORE/AFTER.
6. Double use impossible sans reprodcution explicite.
7. Valid Quasar materials => PROVED.
8. Invalid Quasar material property/count => FAILED.
9. Dynamic property applies only at bound state.
10. Restriction persists until release.
11. Backward proof flags real future-breaking decision only.
12. Derived claim recomputes and certainty cannot strengthen.
13. Cold audit detects mutated primary binding.
14. Narrative-prohibited mechanic remains blocked.
15. Direction remains user-owned when required.
16. New core has no legacy dependency.
17. One API invocation auto-repairs MODEL issue and reaches terminal result without user continue.
18. DATA fallback causes zero semantic repair calls.
19. RUNTIME blocker causes zero semantic repair calls.
20. Model flow-control fields rejected/ignored.
21. Repeated identical MODEL failure trips no-progress/budget guard.
22. USER_REQUIRED pause/resume preserves completed deterministic work.

## 6. Authorized Change Surface

Normative : `CHANGE_SURFACE_CONTRACT_CORRECTIVE_ON_V5_V1.md` + JSON.

High level :
- MUST: contracts/card_data/compiler/validator/runtime ;
- MAY: api/tests/fixtures ;
- integration-only: instruction + manifest ;
- business authorities NO-TOUCH ;
- baseline/reference immutable ;
- no new product file without amended PRE-GO.

## 7. Proofs made stale by future mutation

Dès première mutation candidate :
- V5 combo/runtime integration proofs deviennent parent-only ;
- parent 52/52, 5/5 mutants, 87% coverage et package replay restent historiques mais ne qualifient pas candidate ;
- toute surface modifiée invalide ses targeted/integration/differential proofs ;
- tout changement package après replay impose nouveau package hash + replay.

## 8. PASS / FAIL / BLOCKED

### PASS G9
Uniquement si toutes preuves obligatoires sont matériellement exécutées, 12-capability differential complet, package exact replayé et aucune divergence non autorisée.

### FAIL examples
- Quasar valid still `UNSUPPORTED` à cause d'un wording ;
- invalid Quasar passes ;
- provider outage stops despite alternate route ;
- model writes proof/flow fields ;
- resource double spend/use-before-produce passes ;
- stale proof published ;
- DATA/RUNTIME sent to model repair ;
- recoverable friction requires user continue ;
- model controls retry/phase/publish ;
- no-progress loop persists ;
- V4 protected capability absent ;
- V5 parent preserve guard regresses.

### BLOCKED
- target/GO absent ;
- parent/reference mismatch ;
- key inherited capability impossible to characterize ;
- required out-of-surface change without PRE-GO amendment ;
- material external evidence impossible to obtain at gate where it is mandatory.

## 9. Current NEXT_STEP

**Aucun code produit.** Attendre `GO <version>` explicite. Après GO : écrire target + authorization, vérifier workspace, entrer G0 uniquement.
