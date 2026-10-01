# RECONCILIATION ETAT V4 ↔ V5 — 2026-10-01

## Autorité courante

- Stable baseline globale : **V3.6 STABLE**.
- V4 exact audité : **RC16.23.8**.
- V5 exact audité : **YGO_V5_SOURCES.zip**.
- Aucun des deux n'est promu stable.
- La prochaine version/candidate corrective n'est **pas assignée**.

## V4 — état réconcilié

Statut global : **NON PROMOTABLE / REFERENCE DE CAPACITES**.

Preuves matérielles connues du manifest V4 :
- targeted 12/12 PASS ;
- Red-Team 9/9 PASS ;
- mutants 5/5 killed ;
- differential candidate 25/25 avec 0 protected loss ;
- inherited nominal regression 13/13 PASS ;
- historical mutants 96/96 killed.

Limites :
- exact package replay était encore pending ;
- fresh external Black-Box était pending ;
- runtime monolithique et très couplé.

Rôle actuel :
- **last-known-good de référence pour le sous-système combo proof**, pas baseline stable globale ;
- oracle pour restaurer les invariants combo dans l'architecture V5.

Capacités combo V4 à protéger :
- Proof-Carrying Line ;
- Resource Ledger / allocation des copies ;
- BEFORE/AFTER par step ;
- Action Legality Proof ;
- Mechanical Consequence Binding compilé ;
- Summon Rule / exact material binding ;
- dynamic material properties ;
- restrictions persistantes ;
- Derived Claims ;
- Backward Proof ;
- Critical Decisions ;
- Unified Cold Audit.

## V5 — état réconcilié

Ancien statut matériel enregistré :
- G8 deterministic complete ;
- 52/52 tests PASS ;
- 87% branch-aware coverage ;
- 5/5 mutants ciblés killed ;
- exact package replay 52/52 PASS ;
- promotion interdite / Black-Box pending.

Ces exécutions restent **réellement exécutées** et ne sont pas annulées.

Mais leur portée est désormais insuffisante pour qualifier V5, car l'audit postérieur a révélé des capacités héritées V4 non couvertes par les regression guards V5.

### Statut global courant V5

**REGRESSED / CORRECTIVE REQUIRED / NON PROMOTABLE**

### Capacités V5 conservées comme acquises matérielles

- architecture six modules ;
- API interne mince ;
- contracts typés ;
- IDs / hashes / counts / bindings techniques dérivés ;
- canonical compile et stale detection ;
- séparation MODEL / DATA / RUNTIME ;
- publication gate unique ;
- legacy harness retiré du chemin nominal ;
- package exact extrait et rejoué ;
- banlist / pool / contraintes narratives de base.

### Régressions / défauts ouverts

#### REG-V5-COMBO-PROOF
Last-known-good de capacité : **V4 RC16.23.8**.

V5 a perdu ou réduit :
- Proof-Carrying Line complète ;
- snapshots BEFORE/AFTER explicites ;
- Action Legality Proof générique ;
- Backward Proof ;
- Critical Decisions dérivées ;
- Derived Claims génériques ;
- Unified Cold Audit complet ;
- MCB/Summon material binding générique.

Symptôme observé :
- `SYNCHRO_REQUIREMENT_UNSUPPORTED` pour Shooting Quasar Dragon parce que V5 hardcode une forme Synchro standard.

#### REG-V5-NO-SECRETARIAT-MECHANICAL
V5 demande encore au modèle de produire des `consequences` structurées (`REQUIRE`, `MOVE`, `CONSUME`, etc.).
V4 final compilait ces projections mécaniques depuis la sémantique autoritative.

#### REG-V5-CARD-DATA-RESOLUTION
V5 confond l'échec de `YGOPRODeckProvider` avec l'indisponibilité de l'information.
Le besoin est un **CardFactsResolver multi-route** : cache → source structurée → recherche web / source officielle → UNRESOLVED seulement après épuisement réel.

#### REG-V5-DIFFERENTIAL-COVERAGE
Le G0 / Differential Gate V5 n'avait pas matérialisé toute la baseline combo V4 comme regression guards.
Les 52 tests V5 PASS restent vrais mais ne couvrent pas la totalité des invariants hérités.


## ANOMALIES CRITIQUES A NE PAS PERDRE

### ANOMALIE-A — Runtime V5 joue Yu-Gi-Oh! au lieu de vérifier une preuve structurée

**Statut : OPEN / REGRESSION REELLE**

Cas observé : **Shooting Quasar Dragon**.

Symptôme :
- `validator.py` tente d'interpréter directement les conditions Synchro ;
- il accepte une forme standard hardcodée/regex ;
- une condition différente mais légitime devient `SYNCHRO_REQUIREMENT_UNSUPPORTED`.

Diagnostic :
- le runtime ne doit pas décider lui-même comment fonctionne une Invocation Synchro/Xyz/Link/Pendulum ;
- l'autorité IA / sémantique doit fournir la compréhension Yu-Gi-Oh! pertinente ;
- le compiler doit transformer cette compréhension en bindings/contraintes mécaniques dérivées ;
- le validator doit seulement vérifier déterministement les matériaux, propriétés, ressources et états.

REQ de correction :
- restaurer le modèle V4 `semantic authority -> compiled mechanical binding -> deterministic replay` ;
- restaurer les Summon Rule / Exact Material bindings génériques ;
- interdire les validations de type `if card == ...` ou regex représentant une mécanique entière ;
- conserver le replay déterministe des ressources et états.

RED/KILL obligatoire :
- une ligne valide invoquant Shooting Quasar Dragon avec ses matériaux requis ne doit pas échouer uniquement parce que sa clause de matériaux n'est pas la forme Synchro standard connue du runtime.

Positive control :
- une ligne Quasar avec matériaux réellement insuffisants/incompatibles doit échouer au replay déterministe.

### ANOMALIE-B — Card Data bloque sur l'indisponibilité d'un provider

**Statut : OPEN / DEFAUT D'ARCHITECTURE**

Symptôme :
- cache local vide ;
- `YGOPRODeckProvider` indisponible / DNS failure ;
- V5 produit `CARD_FACTS_UNAVAILABLE` / UNVERIFIED et arrête la preuve.

Diagnostic :
- le besoin métier est `résoudre les faits de la carte sur Internet`, pas `faire répondre YGOPRODeck` ;
- l'échec d'une source individuelle ne doit pas être assimilé à l'absence de l'information.

REQ de correction :
- remplacer la dépendance provider unique par un **CardFactsResolver multi-route** ;
- stratégie minimale : cache -> source structurée -> recherche web -> source officielle/admissible -> UNRESOLVED seulement après épuisement réel ;
- conserver provenance, hash, date/source et fail-closed sur conflit matériel ;
- ne jamais transformer une panne de provider en travail pour l'IA secrétaire.

RED/KILL obligatoire :
- provider principal indisponible mais une autre source web fournit les facts -> résolution doit continuer et réussir.

Positive control :
- aucune source admissible ou conflit matériel non résolu -> `CARD_FACTS_UNRESOLVED` / `UNVERIFIED`.

### Impact qualification

Ces deux anomalies font partie des blockers de promotion de V5.

Aucune future candidate corrective ne peut être considérée qualifiée si :
- le runtime continue à interpréter directement des règles Yu-Gi-Oh! spécifiques comme autorité métier ;
- une panne d'un provider unique bloque la résolution alors que des routes web alternatives existent.


## REQ réconciliés

| REQ | Etat actuel |
|---|---|
| Reliable deck / legality | PARTIAL — légalité structurelle OK, fiabilité combo REGRESSED |
| Automatic information transport | VERIFIED sur V5 actuel |
| No AI secretariat | PARTIAL / REGRESSED sur les consequences mécaniques |
| Automatic web card facts | REGRESSED / provider unique trop rigide |
| Canonical compile | VERIFIED pour projections techniques ; à étendre au MCB restauré |
| Combo proof conservation | REGRESSED |
| Certainty monotonicity | VERIFIED actuellement mais preuve à rejouer après correction combo |
| Single publication gate | VERIFIED |
| Thin internal API | VERIFIED |
| Flat minimal source | VERIFIED |
| Legacy isolation | VERIFIED |
| Evidence-bound qualification | STALE au niveau global : characterization/differential incomplets |

## Parent et références pour le prochain chantier

- **Parent produit à corriger : V5 exact** — pour conserver sa nouvelle architecture.
- **Reference / last-known-good combo : V4 RC16.23.8** — pour restaurer les invariants sans restaurer le monolithe.
- **Stable baseline globale : V3.6 STABLE**.
- **Target corrective : NOT_ASSIGNED**.

## Direction de correction

Ne pas revenir au V4 complet.

Construire :

**V5 architecture + V4 Proof-Carrying Line invariants**

Conserver :
- API / contracts / compiler / runtime / validator / card-data ;
- transport canonique ;
- anti-secrétariat administratif ;
- issue ownership ;
- publication gate.

Restaurer depuis V4 :
- Resource Ledger ;
- BEFORE/AFTER ;
- Action Legality Proof ;
- MCB compilé ;
- Summon Rule binding générique ;
- dynamic material properties ;
- restrictions persistantes ;
- Derived Claims ;
- Backward Proof ;
- Critical Decisions ;
- Cold Audit proportionné.

Corriger Card Data :
- provider unique → resolver multi-route.

## Prochain pas

Aucune mutation autorisée par cette réconciliation.

Préparer un **nouveau Engineering Intent / Matrix / PRE-GO corrective** avec :
- parent = V5 exact ;
- reference combo = V4 RC16.23.8 ;
- target = NOT_ASSIGNED jusqu'à choix utilisateur ;
- nouveaux RED/KILL incluant Quasar et panne provider ;
- Differential Gate enrichi de tous les invariants combo V4 listés ci-dessus.
