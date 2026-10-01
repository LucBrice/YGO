# DATA ARCHITECTURE — Corrective on V5 V1

## 0. But

Définir **qui possède chaque donnée**, où elle naît, comment elle est dérivée, quand elle devient stale et quelles données peuvent être vues/écrites par l'IA.

Principe : **une information métier = une source sémantique ; toute projection dérivable = compiler/runtime.**

## 1. Couches de données

| Layer | Données | Writer unique | Lecteurs | Persistance | Modèle peut écrire ? |
|---|---|---|---|---|---|
| A Authorities | pool, banlist, game rules, narrative/style/validation sources | package maintenu hors run | runtime/compiler/validator/AI context | permanent | non |
| B Request/Context | `BuildRequest`, environnement, choix user | API/runtime | resolver, AI, compiler | run | seulement user-owned fields via API |
| C Evidence | `CardFacts`, `EvidenceRef`, provenance, raw hash, conflicts | CardFactsResolver | AI/compiler/validator | cache + run | non |
| D Semantic source | deck intent, cards/ratios choisis, ordered semantic actions, targets/material choices, semantic interpretations | AI / user authority | compiler, cold audit | run | **oui, uniquement ici** |
| E Compiled proof | canonical IDs, copies, ResourceLedger seed, Fact/Constraint bindings, MCB, Summon bindings, topology, dependency hashes | compiler | validator/runtime | regenerable | non |
| F Replay state | BEFORE/AFTER snapshots, active restrictions, property state, action proof | validator | validator/runtime/cold audit | regenerable / trace | non |
| G Derived proof | ReplayTrace, DerivedClaims, BackwardRequirements, CriticalDecisions, ValidationReport | validator/runtime | runtime/render | regenerable / proof | non |
| H Run control | RunState, phase, attempts, route attempts, issue fingerprints, progress, terminal status, publication auth | runtime controller | api/runtime | ephemeral/minimal checkpoint | non |
| I Publication | final deck/render model, proof refs, final status | runtime only | user | output | non |
| J Dev evidence | fixtures, test results, coverage, mutants, hashes | dev process | dev/audit | chantier only | non-runtime |

## 2. Entités normatives

### `BuildRequest`
Source : user/API. Contient demande métier, environnement, contraintes explicitement user-owned. Ne contient aucun statut de preuve.

### `BuildContext`
Runtime-derived : autorités applicables, progression narrative, pool/banlist identity, direction state, config resolver/controller. Content-addressed si nécessaire.

### `CardFacts`
Normalisé depuis le web/provider :
- canonical name ;
- type/subtypes ;
- level/rank/link/scale si applicable ;
- effect/material text ;
- metadata nécessaire ;
- `source_locator`, `provider/route`, `retrieved_at`, `raw_payload_hash` ;
- environment compatibility note lorsque pertinent.

### `EvidenceSet`
Ensemble ordonné/content-addressed des preuves réellement utilisées par une interprétation/ProofPlan. Un changement matériel de preuve change `evidence_set_hash`.

### `SemanticDeckDraft`
**Seule surface métier principale écrite par l'IA** :
- concept/direction ;
- deck entries/ratios ;
- axes/starters ;
- ordered combo lines ;
- actions sémantiques ;
- targets/material selections ;
- interpretations sémantiques evidence-bound ;
- conditions/certainty sémantiques.

Interdit ici : MCB, IDs techniques, ledgers, snapshots, flow control, PASS/publish.

### `CanonicalDeck`
Compiler-derived : sections normalisées, counts, IDs/hashes, bindings, source hash, semantic revision.

### `ProofPlan`
Compiler-derived, content-addressed par au minimum :
`semantic_hash + evidence_set_hash + authority/context hash + compiler schema/version`.

Contient :
- resource/copy identities ;
- initial resource state ;
- action topology ;
- FactBindings ;
- ConstraintBindings ;
- MechanicalConsequenceBindings ;
- SummonMaterialBindings ;
- output/claim dependencies ;
- backward dependency targets.

### `ResourceLedger`
Projection déterministe des ressources : identity/copy, quantity, zone, producer/consumer edges. Jamais écrit à la main par le modèle.

### `StateSnapshot`
Immutable : `BEFORE:<action_id>` et `AFTER:<action_id>`. Contient au minimum resource positions/quantities, effective properties nécessaires, restrictions actives et state counters requis.

### `ActionLegalityProof`
Résultat d'évaluation des constraints liées à une action contre son BEFORE exact. Référence bindings + evidence, mais ne réinterprète pas le texte brut.

### `ReplayTrace`
Suite ordonnée des snapshots/actions/proofs + résultat forward replay. Hashé pour attacher derived claims et publication.

### `DerivedClaim`
Claim calculable dérivé du ReplayTrace. Ne peut être déclaré `GUARANTEED` si une dépendance est conditional/unresolved.

### `BackwardRequirement` / `CriticalDecision`
Dépendance future remontée vers des choix amont. Une décision n'est critique que si des options légales ont des effets différents sur une exigence future.

### `ValidationIssue`
Typed : owner (`MODEL|DATA|RUNTIME|USER_REQUIRED`), code, severity, semantic/action refs, evidence refs, blocking, repairability.

### `ValidationReport`
Agrège legality/combo/certainty/cold audit et blocking issues pour les exactes revisions courantes.

### `RunState`
Runtime-only :
- `run_id` ;
- phase ;
- semantic/evidence/proof/replay hashes ;
- model/repair/data attempts ;
- route history ;
- issue fingerprint history ;
- progress fingerprint ;
- user gate ;
- terminal status ;
- publication authorization.

Aucun champ n'est model-writable.

## 3. Flux de données nominal

```text
BuildRequest
  + Authorities
      -> BuildContext
          -> CardFactsResolver -> EvidenceSet
          -> AI -> SemanticDeckDraft
          -> compiler
                -> CanonicalDeck
                -> ProofPlan
                     -> validator
                          -> StateSnapshots
                          -> ActionLegalityProofs
                          -> ReplayTrace
                          -> DerivedClaims
                          -> Backward/Critical
                          -> ValidationReport
                               -> runtime routing
                               -> repair/re-resolve/recompile OR publication
```

## 4. Dependency / staleness model

```text
BuildRequest/context change
  -> SemanticDeckDraft applicability STALE
  -> downstream STALE

CardFacts/EvidenceSet change
  -> semantic interpretation potentially STALE
  -> ProofPlan STALE
  -> ReplayTrace STALE
  -> Claims/report/publication STALE

SemanticDeckDraft change
  -> CanonicalDeck/ProofPlan STALE
  -> ReplayTrace/claims/report/publication STALE

ProofPlan/compiler-schema change
  -> ReplayTrace/claims/report/publication STALE

ReplayTrace change
  -> claims/backward/report/publication STALE
```

**Jamais de patch manuel d'un artefact dérivé stale.** Recompile/replay depuis la source amont correcte.

## 5. Single source rules

- Nom/ratio/choix stratégique : `SemanticDeckDraft`.
- Card text/fact : `CardFacts` + `EvidenceRef`.
- Pool/banlist : autorités packagées.
- IDs/hashes/copies : compiler.
- Conséquences mécaniques : compiler MCB.
- État à un instant : `StateSnapshot` produit par validator.
- Validité mécanique : validator.
- Owner/routing : runtime deterministic classification.
- Publication status : runtime uniquement.

Aucune duplication model-authored de ces responsabilités.

## 6. CardFacts route/provenance data

Une tentative de route produit un objet technique `ResolutionAttempt` runtime/data-owned : route, outcome, error class, timestamp, locator. Il ne devient pas une instruction utilisateur.

Résolution :

```text
cache hit valid -> use
else provider A -> normalize/verify
else provider B -> normalize/verify
else official/direct -> normalize/verify
else host web search/fetch -> normalize/verify
else admissible fallback
else DATA_UNRESOLVED
```

Conflit matériel entre sources : conserver les candidates + provenance, classer DATA conflict, ne pas choisir par mémoire modèle.

## 7. Semantic interpretation data

Si un texte/ruling demande un jugement non dérivable, runtime fournit au modèle :
- semantic question minimale ;
- EvidenceSet exact ;
- contexte applicable.

Le résultat est `SemanticInterpretation` evidence-bound, avec scope précis. Le compiler transforme cette interprétation en constraints/MCB. Le modèle ne remplit pas directement ces bindings.

## 8. Summon/material binding data

Representation générique, pas card-specific :
- groupes de matériaux ;
- exact/min/max count ;
- predicates (Tuner/non-Tuner, Synchro/etc.) ;
- named/effective-name constraints ;
- level/rank/link aggregate constraints ;
- relation/set predicates ;
- source semantic/evidence refs.

Le validator applique le binding aux matériaux réellement présents dans `BEFORE`.

## 9. Persistence policy

### Permanent product data
Authorities packagées + code.

### Cache persistant admissible
CardFacts/provenance avec invalidation/freshness claire. Cache = optimisation, jamais autorité supérieure au package pour pool/banlist.

### Run-ephemeral/regenerable
CanonicalDeck, ProofPlan, ledgers, snapshots, ReplayTrace, claims, RunState. Peuvent être conservés comme trace si utile, mais doivent être reconstructibles.

### Dev-only
fixtures, mutation outputs, coverage, differential evidence, package hashes.

## 10. Serialization / hashing

- serialization canonique stable pour tout artefact content-addressed ;
- ordre des maps/lists défini lorsque l'ordre n'est pas sémantique ;
- hash inclut les dépendances pertinentes ;
- hash d'un artefact dérivé ne doit pas dépendre d'un champ volatile non sémantique (`retrieved_at` seulement si freshness contract l'exige) ;
- publication référence les hashes exacts courants.

## 11. Data security against AI secretariat

Le schema modèle rejette/ignore au minimum :
`run_id`, `phase`, `next_stage`, `retry`, `provider`, `route`, `publication_authorized`, `proof_status`, `resource_ledger`, `before`, `after`, `mcb`, `bindings`, `hashes`, `cache_status`, `stale`, `derived_claim_pass`.

## 12. Data architecture acceptance

PASS seulement si :
- ownership tests prouvent qu'aucun writer illégitime ne peut modifier une couche ;
- same semantic+evidence => same compiled identities ;
- changement amont rend les descendants stale/rebuilt ;
- aucune duplication manuelle obligatoire entre semantic data et proof data ;
- publication est liée aux hashes exacts du graphe courant.
