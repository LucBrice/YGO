# ENGINEERING INTENT — Corrective on V5 V2

## 0. Statut et verrou

**FROZEN — PRE-GO. Aucune mutation produit autorisée.**

- Parent produit exact : `YGO_V5_SOURCES.zip`
- SHA-256 parent : `87d4c297b82fb1aab1c5e3dc598dca400fb4e3e3325496d08325b12af818ac2a`
- Version déclarée par le parent : `V5`
- Baseline stable globale : `V3.6 STABLE`
- Référence fonctionnelle combo / last-known-good de capacité : `V4 RC16.23.8`
- SHA-256 V4 : `90cb9f90c78e86725bb24a27c054f3603df20b670e961267bd62357b764dfb3e`
- Cible corrective : `NOT_ASSIGNED`
- GO : `NO`
- Promotion : `FORBIDDEN`

Les preuves V5 déjà exécutées (52/52, mutants ciblés, coverage, package replay) restent des preuves historiques exactes du parent. Elles ne suffisent plus à qualifier une future candidate car l'audit V4↔V5 a exposé des capacités combo héritées absentes de la baseline différentielle V5.

## 1. Intent

Construire une correction **sur V5**, sans retour au monolithe V4, afin d'obtenir simultanément :

1. **architecture V5** : six modules plats, API mince, contracts typés, transport canonique, ownership MODEL/DATA/RUNTIME, publication unique ;
2. **fiabilité combo V4** : Proof-Carrying Line, Resource Ledger, états BEFORE/AFTER, Action Legality Proof, Mechanical Consequence Binding compilé, bindings de matériaux génériques, propriétés effectives, restrictions persistantes, Backward Proof, Derived Claims, Critical Decisions, Cold Audit ;
3. **Card Data résilient** : le système cherche les faits de carte sur Internet par plusieurs routes et ne confond jamais panne d'un fournisseur avec absence de l'information ;
4. **orchestration réellement automatique** : un programme déterministe possède le workflow complet et n'appelle l'IA qu'aux frontières sémantiques nécessaires.

Formule cible :

`V5 architecture + V4 combo-proof invariants + multi-route CardFactsResolver + deterministic continuous-run controller`

## 2. Défauts observés servant de RED

### D1 — Régression Combo Proof
V5 a perdu/réduit des garanties présentes en V4 : ledger exact, snapshots explicites, Action Legality Proof, MCB compilé, summon binding générique, Backward Proof, Derived Claims, Critical Decisions, Cold Audit complet.

### D2 — Runtime qui joue Yu-Gi-Oh! (cas Quasar)
`validator.py` interprète directement des mécaniques via des implémentations spécialisées/regex. Une Invocation Synchro légitime avec une clause non standard peut produire `SYNCHRO_REQUIREMENT_UNSUPPORTED`. Le cas canonique est **Shooting Quasar Dragon**.

La correction n'est pas d'ajouter un cas Quasar. La correction est :

`autorité sémantique/evidence → compiler binding générique → validator générique`

### D3 — Secrétariat mécanique réintroduit
Le modèle peut encore être amené à produire des `consequences` bas niveau (`REQUIRE`, `MOVE`, `CONSUME`, etc.). Ces projections sont dérivables et doivent redevenir compiler-owned.

### D4 — Card Data bloqué par un provider
Cache vide + `YGOPRODeckProvider` indisponible peut arrêter la preuve. Le besoin métier est **résoudre le CardFact sur Internet**, pas dépendre d'un endpoint particulier.

### D5 — Orchestration encore trop implicite
Sans contrôleur déterministe explicite, l'IA peut reprendre la main pour enchaîner des étapes, décider d'un retry ou provoquer un handoff utilisateur inutile. Le programme doit posséder le workflow.

### D6 — Differential Gate incomplet
La fermeture V5 n'avait pas importé toute la surface Combo Proof V4 comme regression guards. Une future candidate ne peut être qualifiée sans inventaire différentiel complet.

## 3. User stories

### Utilisateur
Je demande un deck une fois. Le système doit chercher automatiquement les cartes nécessaires, laisser l'IA construire/jouer la ligne, compiler automatiquement les conséquences mécaniques, rejouer l'état exact des ressources à chaque étape, corriger automatiquement les frictions MODEL/DATA récupérables, et ne me redonner la main que pour une vraie décision utilisateur ou un blocker terminal.

### IA
Je suis appelée pour comprendre/jouer Yu-Gi-Oh!, interpréter une preuve sémantique non dérivable ou réparer un défaut MODEL. Je ne transporte pas les données, ne choisis pas le provider, ne construis pas les IDs/hashes/ledgers, ne choisis pas la phase suivante, ne décide pas du retry, ne déclare pas PASS et ne publie pas.

### Runtime
Je possède le run : contexte, data resolution, policy d'appel modèle, compile/recompile, validation/replay, routing, repair budget, no-progress guard, staleness et publication.

## 4. Frontière d'autorité

### IA / autorité sémantique Yu-Gi-Oh!
Autorisé :
- choix du deck, ratios et stratégie ;
- ordre des actions, targets, matériaux, branches ;
- interprétation d'effet/ruling lorsqu'elle n'est pas mécaniquement dérivable ;
- correction d'une erreur sémantique MODEL ;
- cold semantic audit lorsqu'il est requis.

Interdit :
- IDs, hashes, counts dérivables, bindings techniques ;
- ResourceLedger, snapshots, MCB, proof status ;
- route DATA, cache metadata, freshness ;
- phase runtime, retry, provider, PASS, publication.

### Card/evidence layer
Résout automatiquement CardFacts + evidence + provenance. Les autorités Link Evolution packagées restent distinctes du web courant.

### Compiler
Transforme **une seule source sémantique** en données dérivées : canonical deck, resource identities, proof plan, facts/constraints, MCB, summon bindings, topology, dependency hashes et render bindings.

### Validator / proof shell
Ne comprend pas librement Yu-Gi-Oh!. Il évalue des obligations structurées génériques : disponibilité, quantité, transitions, prédicats, cardinalités, sommes, restrictions, snapshots, derived claims, forward/backward consistency.

### Runtime / controller
Possède l'état du run et est la seule autorité de flow control. Il décide si l'IA doit être appelée selon une policy fermée.

## 5. Requirements cumulatifs

Les REQ `REQ-CR-001..014` restent cumulatifs. Les correctifs `REQ-CR-015..027` sont détaillés dans le registre courant.

REQ structurants du chantier :
- `015` frontière sémantique/proof shell ;
- `016` Proof-Carrying Line ;
- `017` ledger + BEFORE/AFTER ;
- `018` Action Legality Proof ;
- `019` summon/material binding générique + Quasar ;
- `020` MCB compiler-owned ;
- `021` propriétés dynamiques + restrictions ;
- `022` Backward Proof + Critical Decisions ;
- `023` Derived Claims ;
- `024` Cold Audit ;
- `025` CardFactsResolver multi-route ;
- `026` differential V4 complet ;
- `027` Deterministic Continuous Run Orchestrator.

## 6. Invariants

1. Une information sémantique est déclarée une fois puis projetée automatiquement.
2. Aucun champ dérivable de preuve/orchestration n'est model-writable.
3. Le runtime ne transforme jamais une limitation d'implémentation en règle Yu-Gi-Oh!.
4. Aucune correction nommée `if Quasar` ou équivalent.
5. Chaque ligne essentielle possède un ProofPlan lié à son semantic hash + evidence-set hash.
6. Chaque étape matérielle possède `BEFORE` et `AFTER` explicites.
7. Une ressource ne peut être consommée deux fois ni utilisée avant production.
8. Une propriété effective est évaluée au moment exact de l'usage.
9. Une restriction persiste jusqu'à libération structurée.
10. Un claim garanti ne peut pas dépasser la certitude de ses dépendances.
11. Une panne provider unique est non terminale tant qu'une autre route admissible existe.
12. DATA et RUNTIME n'appellent jamais l'IA pour se faire réparer.
13. MODEL repair est borné et progress-aware.
14. Le modèle ne contrôle jamais phase/retry/provider/pass/publish.
15. Aucun handoff `continue/reprend` tant qu'une récupération interne valide existe.
16. Publication seulement sur les exactes révisions semantic/evidence/proof/replay courantes.
17. Le core produit reste physiquement plat et minimal.
18. Le harness V4 reste référence/oracle, jamais dépendance de production.

## 7. Non-goals

- Restaurer `harness_runtime_v1.py`.
- Restaurer 58 commandes CLI, leases, receipts ou bureaucratie RC16.
- Construire un simulateur complet Yu-Gi-Oh! par carte.
- Hardcoder Quasar ou une autre carte.
- Déplacer pool/banlist Link Evolution vers une banlist web actuelle.
- Créer microservices, event bus, generic DAG ou framework de workflow.
- Ajouter un nouveau fichier produit permanent sans amendement PRE-GO.
- Promouvoir automatiquement la candidate.

## 8. Architecture logique cible

Voir :
- `TARGET_ARCHITECTURE_CORRECTIVE_ON_V5_V2.md`
- `DATA_ARCHITECTURE_CORRECTIVE_ON_V5_V1.md`

Résumé :

```text
User
  |
  v
api.py
  |
  v
Deterministic DeckBuildController (runtime.py)
  |
  +--> authorities/context
  +--> CardFactsResolver (card_data.py)
  +--> AI semantic boundary (only when policy authorizes)
  +--> compiler.py -> canonical/proof data
  +--> validator.py -> generic deterministic replay/proof
  +--> issue routing + bounded recovery
  `--> publication gate
```

## 9. Surface de changement pressentie

Normative : `CHANGE_SURFACE_CONTRACT_CORRECTIVE_ON_V5_V1.md` et JSON homologue.

MUST-TOUCH : `contracts.py`, `card_data.py`, `compiler.py`, `validator.py`, `runtime.py`.
MAY-TOUCH : `api.py`, tests, fixtures.
Integration-only : instruction générale + manifest si requis.
Business authorities : NO-TOUCH par défaut.

## 10. Condition de réussite engineering

Le chantier est techniquement clos seulement si :
- Quasar valide n'est plus bloqué par wording runtime ;
- Quasar invalide est refusé par la preuve déterministe ;
- provider A down + route B available continue automatiquement ;
- aucune conséquence/ledger/flow-control dérivable n'est confiée au modèle ;
- les 12 capacités combo V4 sont mappées et vertes ;
- les acquis V5 restent verts ;
- un run nominal complet ne requiert aucun `continue/reprend` ;
- exact packaged bytes repassent les preuves prévues ;
- Black-Box indépendant reste séparé de la qualification déterministe.
