# TARGET ARCHITECTURE — Corrective on V5 V2

## 0. Principe

**Conserver le squelette V5, restaurer les invariants Combo Proof V4, automatiser le workflow.**

Architecture physique cible : **six modules produit**, pas davantage sans amendement PRE-GO.

```text
api.py
contracts.py
card_data.py
compiler.py
validator.py
runtime.py
```

L'architecture est logiquement riche mais le déploiement Sources reste plat.

## 1. Vue composants

```text
                         +------------------+
User / host ------------>|      api.py      |
                         +--------+---------+
                                  |
                                  v
                     +------------+-------------+
                     | runtime.py / Controller  |
                     | RunState + call policy   |
                     +--+--------+--------+------+
                        |        |        |
              DATA path |        |        | semantic call only
                        v        |        v
                 +------+----+   |   +----+----------------+
                 | card_data |   |   | AI semantic boundary|
                 | Resolver  |   |   +----+----------------+
                 +------+----+   |        |
                        |        |        v
                        +------->|  +-----+------+
                                 +->| compiler.py |
                                    +-----+------+
                                          |
                                          v
                                    +-----+------+
                                    |validator.py|
                                    | proof shell|
                                    +-----+------+
                                          |
                                          v
                                 report/issues/trace
                                          |
                                          v
                                  runtime routing
                              MODEL / DATA / RUNTIME
                                          |
                               recover / block / pass
                                          |
                                          v
                                  publication gate
```

## 2. Module ownership

### `api.py` — thin boundary
Responsabilités :
- accepter `BuildRequest` ;
- démarrer/reprendre le controller ;
- retourner résultat terminal ou vrai `USER_REQUIRED` ;
- aucune logique Yu-Gi-Oh!, aucun routing, aucun retry.

### `contracts.py` — schémas et invariants de frontière
Responsabilités :
- types sémantiques ;
- types data/evidence/proof/run ;
- enums fermés ownership/status/phase ;
- interdiction de champs model-owned prohibés ;
- serialization stable.

Doit rendre impossible/visible toute tentative du modèle d'écrire : flow control, IDs/hashes, MCB, ledger, snapshots, proof status, publication.

### `card_data.py` — CardFactsResolver
Responsabilités :
- pool local + banlist environnement ;
- cache facts web ;
- routes structurées injectables ;
- route officielle/directe ;
- WebLookupAdapter host ;
- normalisation `CardFacts` ;
- provenance, conflict detection, route exhaustion ;
- aucune interprétation stratégique.

### `compiler.py` — deterministic projection
Responsabilités :
- canonical deck ;
- IDs/hashes/counts ;
- copy/resource allocation ;
- ProofPlan ;
- facts/constraints ;
- Mechanical Consequence Binding ;
- summon/material constraint binding à partir d'une sémantique/evidence autoritative ;
- dependency/staleness graph ;
- bindings de rendu ;
- aucune décision stratégique.

### `validator.py` — generic proof shell
Responsabilités :
- forward replay ;
- immutable BEFORE/AFTER snapshots ;
- quantité/zone/availability ;
- no-double-spend/use-before-produce ;
- generic predicate/cardinality/sum/set constraints ;
- dynamic property evaluation ;
- persistent restrictions ;
- Action Legality Proof ;
- Derived Claims ;
- Backward Proof / Critical Decisions ;
- cold mechanical comparison ;
- certainty monotonicity.

Interdit :
- parser une mécanique entière comme autorité ;
- hardcoder une carte ;
- traiter `unsupported wording` comme illégalité YGO.

### `runtime.py` — deterministic control plane
Responsabilités :
- `DeckBuildController` ;
- `RunState` ;
- phase transitions ;
- closed model-call policy ;
- resolver orchestration ;
- compile/recompile ;
- validation/replay ;
- issue routing ;
- bounded repair ;
- progress/no-progress detection ;
- resume after genuine USER_REQUIRED ;
- publication gate.

## 3. Continuous-run state machine

```text
START
  -> RESOLVE_CONTEXT
  -> RESOLVE_DATA
  -> MODEL_BUILD             [AI allowed]
  -> COMPILE
  -> VALIDATE
  -> ROUTE
       MODEL -> MODEL_REPAIR [AI allowed, bounded] -> COMPILE
       DATA  -> DATA_RECOVER [AI forbidden]        -> RESOLVE_DATA/COMPILE
       RUNTIME -> BLOCK      [AI forbidden]
       USER_REQUIRED -> PAUSE_FOR_USER
       PASS -> COLD_AUDIT? -> PUBLISH
```

Allowed model-call reasons are a closed set :
- `INITIAL_SEMANTIC_BUILD`
- `SEMANTIC_INTERPRETATION_REQUIRED`
- `MODEL_REPAIR_REQUIRED`
- `COLD_SEMANTIC_AUDIT_REQUIRED`

Tout autre état => pas d'appel modèle.

## 4. Combo proof architecture

```text
SemanticLine
   + EvidenceSet
        |
        v
compiler
   |
   +--> ResourceLedger
   +--> FactBindings
   +--> ConstraintBindings
   +--> MCB
   +--> SummonMaterialBindings
   +--> ProofTopology
        |
        v
ProofPlan
        |
        v
validator
   |
   +--> BEFORE/AFTER snapshots
   +--> ActionLegalityProof
   +--> ForwardReplay
   +--> RestrictionState
   +--> DerivedClaims
   +--> BackwardRequirements/CriticalDecisions
        |
        v
ReplayTrace + ValidationReport
```

Le V4 est une référence comportementale pour ces invariants, pas une librairie importée.

## 5. Cas Quasar — architecture attendue

Mauvais :
`validator regex -> connaît seulement "1 Tuner + 1+ non-Tuner monsters" -> UNSUPPORTED`.

Cible :

```text
Evidence + semantic interpretation
     -> compiler
     -> generic SummonMaterialBinding
        exact/min counts
        predicates: tuner, synchro, non-tuner
        aggregate level constraint
     -> validator
     -> evaluate actual materials from BEFORE state
```

Le validator n'a aucune branche nommée Quasar.

## 6. Card data architecture fonctionnelle

```text
need CardFacts(name)
   -> cache exact/current-enough
   -> structured provider A
   -> structured provider B (si configuré)
   -> official/direct lookup
   -> host WebLookupAdapter search/fetch
   -> admissible fallback
   -> unresolved/conflict only after applicable routes exhausted
```

L'ordre précis est configurable/injectable mais le principe est normatif : **route failure != information failure**.

Pool/banlist Link Evolution restent des autorités locales distinctes.

## 7. Issue ownership

### MODEL
Défaut sémantique/règle/choix qui nécessite compréhension YGO. Runtime envoie un payload minimal de réparation avec evidence nécessaire.

### DATA
Fact manquant, source indisponible, conflit. Runtime continue les routes ; aucun appel modèle comme secrétaire.

### RUNTIME
Primitive interne absente, invariant technique cassé, schema/compiler bug. Fail closed technique ; aucune invention YGO.

### USER_REQUIRED
Uniquement décision réellement humaine/non dérivable (ex. direction explicitement user-owned).

## 8. Progress and repair guard

`progress_fingerprint = H(semantic_hash, evidence_set_hash, blocking_issue_fingerprints, proof_plan_hash/replay_status)`.

Si le même état bloquant revient sans progrès matériel : stop typed `MODEL_REPAIR_NO_PROGRESS`/équivalent. Pas de boucle infinie, pas de `continue` utilisateur artificiel.

## 9. Publication gate

Publication seulement si :
- canonical deck current ;
- required CardFacts/evidence current ;
- ProofPlan current ;
- ReplayTrace current ;
- legality PASS ;
- essential lines PROVED selon contrat ;
- certainty non renforcée ;
- cold audit requis PASS ;
- aucun issue blocking ;
- `publication_authorized` calculé par runtime.

## 10. Architecture des données

La définition normative détaillée est dans `DATA_ARCHITECTURE_CORRECTIVE_ON_V5_V1.md`.

Principe résumé :

`authorities -> evidence -> semantic source -> compiled proof data -> replay state -> derived proof -> publication`

Chaque donnée a un owner unique et une politique de staleness explicite.

## 11. Déploiement et dépendances

- aucune dépendance runtime vers `reference_v4/` ;
- aucune importation du harness legacy ;
- pas de DB/service externe obligatoire pour fonctionner hors web lookup ;
- cache local simple admissible ;
- providers/adapters injectables pour test ;
- sources produit plates.

## 12. Non-goals architecture

Pas de microservices, orchestration framework, generic DAG, event bus, queue, workflow engine, nouveau DSL complet Yu-Gi-Oh!, ou plugin runtime permanent non justifié.
