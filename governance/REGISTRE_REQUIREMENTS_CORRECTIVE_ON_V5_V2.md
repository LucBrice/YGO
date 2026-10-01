# REGISTRE REQUIREMENTS — Corrective on V5 V2

## Statut

- Parent produit : **V5 exact**
- Référence Combo Proof : **V4 RC16.23.8 exact**
- Target : **NOT_ASSIGNED**
- PRE-GO : **FROZEN**
- GO : **NO**
- Promotion : **FORBIDDEN**

Les IDs sont cumulatifs ; aucune renumérotation.

## REQ-CR-001..014 — état réconcilié

| REQ | Exigence | Etat parent V5 | Traitement corrective |
|---|---|---|---|
| 001 | Reliable deck product | REGRESSED | restaurer preuve combo + data resolver |
| 002 | Automatic information transport | VERIFIED_PARENT | préserver + étendre data lineage |
| 003 | No AI secretariat | PARTIAL/REGRESSED | retirer consequences/flow control model-owned |
| 004 | Automatic web card facts | REGRESSED | resolver multi-route |
| 005 | Environment authority separation | VERIFIED_PARENT | preserve |
| 006 | Canonical compile | PARTIAL | étendre aux proof bindings/MCB |
| 007 | Issue ownership/routing | VERIFIED_PARENT | preserve + controller policy |
| 008 | Combo proof conservation | REGRESSED | restaurer V4 invariants |
| 009 | Certainty monotonicity | VERIFIED_PARENT / STALE_ON_CHANGE | rejouer après proof changes |
| 010 | Single publication gate | VERIFIED_PARENT | preserve |
| 011 | Thin internal API | VERIFIED_PARENT | preserve |
| 012 | Flat minimal source | VERIFIED_PARENT | preserve six modules |
| 013 | Legacy isolation | VERIFIED_PARENT | preserve, V4 reference only |
| 014 | Evidence-bound qualification | STALE/REGRESSED | reconstruire differential complet |

## REQ correctifs 015..027

### REQ-CR-015 — Semantic authority / deterministic proof boundary — OPEN
L'IA comprend le Yu-Gi-Oh! non dérivable ; compiler/validator n'inventent pas de règles card-specific. Unsupported runtime != illégalité métier.

### REQ-CR-016 — Proof-Carrying Line restoration — OPEN
Toute ligne essentielle possède un ProofPlan content-addressed liant semantic line, evidence, resources, constraints, replay et claims.

### REQ-CR-017 — Exact ResourceLedger + BEFORE/AFTER — OPEN
Replay séquentiel avec quantité/zone/copies exactes, no double-spend, use-after-produce et snapshots immuables à chaque action matérielle.

### REQ-CR-018 — Generic Action Legality Proof — OPEN
Chaque action matérielle est évaluée contre son BEFORE exact via facts/constraints liés ; pas de réinterprétation de texte par le proof shell.

### REQ-CR-019 — Generic summon/material binding — OPEN
Les exigences de matériaux deviennent des bindings génériques. **Quasar valide** doit être prouvable ; **Quasar invalide** doit échouer ; aucun hardcode Quasar.

### REQ-CR-020 — Compiler-owned Mechanical Consequence Binding — OPEN
`REQUIRE/MOVE/CONSUME/PRODUCE/...` et équivalents dérivables sont compiler-owned et interdits dans le payload normal du modèle.

### REQ-CR-021 — Dynamic material properties + persistent restrictions — OPEN
Effective level/name/type/Tuner et restrictions actives sont évalués dans l'état exact et persistent/release selon bindings.

### REQ-CR-022 — Backward Proof + Critical Decisions — OPEN
Les exigences futures sont remontées vers les choix amont ; seules les décisions qui changent la viabilité future sont Critical Decisions.

### REQ-CR-023 — Derived Claims — OPEN
Claims numériques/booléens/ensembles dérivables sont calculés depuis replay ; la certitude finale ne peut être renforcée.

### REQ-CR-024 — Independent Cold Audit — OPEN
Une passe froide ne fait pas confiance aux statuts/bindings primaires et cherche divergence sémantique/mécanique sur les lignes matérielles.

### REQ-CR-025 — Multi-route CardFactsResolver — OPEN
Route failure != information failure. Cache/provider(s)/official/direct/web adapter/fallback ; UNRESOLVED seulement après épuisement ou conflit matériel non résolu.

### REQ-CR-026 — Complete V4→candidate combo differential baseline — OPEN
Les 12 capacités V4 suivantes doivent chacune avoir fixture + guard + résultat différentiel : PCL, ledger, snapshots, action legality, MCB, summon binding, dynamic properties, restrictions, claims, backward, critical decisions, cold audit.

### REQ-CR-027 — Deterministic Continuous Run Orchestrator — OPEN
Un seul controller runtime possède le run complet. AI-call policy fermée ; DATA/RUNTIME ne déclenchent pas repair AI ; MODEL repair borné/progress-aware ; aucun `continue/reprend` pour friction interne récupérable ; publication runtime-only.

## Acceptance globale des REQ

Une candidate ne peut fermer 001/008/014 si un des 015..027 applicable reste OPEN/REGRESSED. Un PASS de test local ne ferme que les REQ explicitement couverts par sa preuve.

## Parent capabilities à préserver

- six modules plats ; thin API ; typed contracts ; canonical IDs/hashes/counts ; stale detection ; MODEL/DATA/RUNTIME ownership ; pool/banlist environment separation ; narrative mechanics ; direction gate ; presentation plan ; publication gate ; legacy isolation ; exact package replay discipline.

## Business authorities NO-TOUCH

Les sources spécialisées packagées restent autoritaires. Le chantier implémente leur comportement sans les réécrire pour s'adapter au code, sauf amendement PRE-GO explicite avant mutation.
