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
| 004 | Automatic web card facts | CLOSED G2 (was REGRESSED) | multi-route resolver landed, see REQ-CR-025 |
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

### REQ-CR-015 — Semantic authority / deterministic proof boundary — PARTIAL (summon/material path CLOSED at G5)
L'IA comprend le Yu-Gi-Oh! non dérivable ; compiler/validator n'inventent pas de règles card-specific. Unsupported runtime != illégalité métier.
G5 : pour le chemin Synchro/Xyz/Link, un clause de matériaux non parsable par la grammaire générique produit
`SUMMON_MATERIAL_BINDING_UNRESOLVED` (owner RUNTIME, UNVERIFIED) — jamais un FAILED métier. La frontière sémantique
pour les autres mécaniques (consequences arbitraires, rulings de texte) reste à traiter au-delà de ce chantier.

### REQ-CR-016 — Proof-Carrying Line restoration — PARTIAL (ProofPlan identity CLOSED at G3; replay/claims binding pending G4/G7)
Toute ligne essentielle possède un ProofPlan content-addressed liant semantic line, evidence, resources, constraints, replay et claims.
G3 : `contracts.ProofPlan` + `compiler.build_proof_plan`/`proof_plan_is_fresh` ferment la partie identité :
`proof_plan_hash = H(semantic_hash, evidence_set_hash, context_hash, compiler_schema_version)`.
Une mise à jour de CardFacts (même sémantique inchangée) change désormais `evidence_set_hash` et rend le ProofPlan STALE —
ce que l'ancien `is_fresh()` (qui ne vérifiait que `source_hash`) ne détectait pas.
Preuve : `tests/test_g3_proof_plan.py` 5/5 EXECUTED_PASS.
Reste OPEN pour fermeture complète de 016 : liaison explicite resources/constraints/replay/claims (G4/G7).

### REQ-CR-017 — Exact ResourceLedger + BEFORE/AFTER — CLOSED (G4, 2026-10-01)
Replay séquentiel avec quantité/zone/copies exactes, no double-spend, use-after-produce et snapshots immuables à chaque action matérielle.
Fermé : `validator._snapshot` capture un `contracts.StateSnapshot` immuable (`MappingProxyType`) avant et après
chaque action matérielle (`validate_combo_lines` alimente `ValidationReport.replay_trace`). Le moteur de zones
(`_move`/`_has`, déjà présent) garantissait déjà structurellement l'absence de double-spend/use-before-produce
(vérification de quantité avant mutation) ; G4 matérialise cette garantie en preuve testée + en artefact de replay
exploitable par G5 (ActionLegalityProof.evaluated_against) et G7 (Cold Audit).
Preuve : `tests/test_g4_replay_snapshots.py` 5/5 EXECUTED_PASS (double-spend REJECTED, use-before-produce REJECTED,
BEFORE≠AFTER non conflaté, snapshots immuables, trace complète sur ligne multi-actions).

### REQ-CR-018 — Generic Action Legality Proof — PARTIAL (summon/material path CLOSED at G5)
Chaque action matérielle est évaluée contre son BEFORE exact via facts/constraints liés ; pas de réinterprétation de texte par le proof shell.
G5 : `validator._evaluate_summon_material_binding` évalue le `SummonMaterialBinding` compilé contre l'état FIELD
exact (via les snapshots BEFORE de G4) ; le texte brut n'est plus réinterprété au moment de la validation
(le parsing a lieu une seule fois, côté compiler, en G3/G5).

### REQ-CR-019 — Generic summon/material binding — CLOSED (G5, 2026-10-01) — MANDATORY DEFECT #1 FIXED
Les exigences de matériaux deviennent des bindings génériques. **Quasar valide** doit être prouvable ; **Quasar invalide** doit échouer ; aucun hardcode Quasar.
Fermé : `compiler.parse_summon_material_clause` (grammaire générique Synchro/Xyz/Link, `MaterialGroup`/`MaterialPredicate`,
qualificatifs de type génériques dont "Synchro"/"Effect") + `compiler.build_summon_material_binding` (compiler-owned,
attaché à `CanonicalAction.summon_binding`) + `validator._evaluate_summon_material_binding` (un seul évaluateur
générique remplaçant les 3 anciennes fonctions `_synchro_summon`/`_xyz_summon`/`_link_summon` à triple regex quasi dupliquée).
Shooting Quasar Dragon ("1 Tuner + 2 or more non-Tuner Synchro Monsters") n'est matché par aucune branche nommée :
il passe par la même grammaire générique que tout autre Synchro.
Preuve : `tests/test_g5_summon_material_binding.py` 10/10 EXECUTED_PASS, incluant :
- Quasar valide (1 Tuner Lv2 + 2 non-Tuner Synchro Lv7/Lv3, somme=12) → **PROVED**;
- Quasar invalide (matériau non-Synchro, compte insuffisant, somme de niveaux fausse) → **FAILED** avec code métier
  (jamais `*_UNSUPPORTED`);
- grep statique confirmant l'absence du mot "quasar" dans `validator.py`/`compiler.py` (aucun branchement nommé);
- Xyz et Link toujours prouvés via le même évaluateur générique (non-régression);
- clause non parsable → `SUMMON_MATERIAL_BINDING_UNRESOLVED` (RUNTIME/UNVERIFIED, jamais une illégalité métier);
- **Quasar end-to-end** : ligne complète (starters → matériaux amenés sur le terrain par effet → Synchro Summon)
  prouvée via `validate_combo_lines` (status PROVED).
Mutation test ad hoc (non committé, voir session) : désactiver le check de qualificatif de type fait échouer
2/10 tests — le mutant est tué.

### REQ-CR-020 — Compiler-owned Mechanical Consequence Binding — CLOSED (G1, 2026-10-01)
`REQUIRE/MOVE/CONSUME/PRODUCE/...` et équivalents dérivables sont compiler-owned et interdits dans le payload normal du modèle.
Fermé : `contracts.SemanticEffectInterpretation` (model-facing, kind fermé, zéro operator/source/destination) +
`compiler.project_mechanical_consequences` (déterministe, table de templates fermée `_MCB_TEMPLATES`) +
`contracts.CanonicalAction.consequences` reste compiler-owned (`MechanicalConsequenceBinding`).
Preuve : `tests/test_g1_contracts_ownership.py` 12/12 EXECUTED_PASS (RED old-schema rejected, GREEN new schema + determinism + template coverage).
Regression guard devient actif ; `tests/test_g0_characterization.py::RedModelMcbSecretariat` stale intentionnellement (voir son en-tête).

### REQ-CR-021 — Dynamic material properties + persistent restrictions — CLOSED (G6, 2026-10-01)
Effective level/name/type/Tuner et restrictions actives sont évalués dans l'état exact et persistent/release selon bindings.
Défaut réel découvert et corrigé à G6 : `_effective_level`/`_effective_tuner` lisaient un override `state.properties[(name, prop)]`
sans jamais le purger ni le scoper à la présence sur FIELD — un override posé sur une copie d'une carte restait lisible
indéfiniment, y compris après qu'une **copie différente du même nom** arrive plus tard sur le terrain (leak par nom).
Fermé par : gate "tant que sur FIELD" dans `_effective_level`/`_effective_tuner`/`_effective_name` (nouveau) +
`_purge_properties_if_left_field` appelé depuis `_move` (purge réelle dès que la dernière copie quitte FIELD).
Cycle de vie des restrictions (apply/bloque/release/débloque, pas de fuite inter-lignes) matérialisé comme nouveau
regression guard (déjà correct structurellement, jamais testé auparavant).
Preuve : `tests/test_g6_dynamic_properties_restrictions.py` 6/6 EXECUTED_PASS.

### REQ-CR-022 — Backward Proof + Critical Decisions — OPEN
Les exigences futures sont remontées vers les choix amont ; seules les décisions qui changent la viabilité future sont Critical Decisions.

### REQ-CR-023 — Derived Claims — OPEN
Claims numériques/booléens/ensembles dérivables sont calculés depuis replay ; la certitude finale ne peut être renforcée.

### REQ-CR-024 — Independent Cold Audit — OPEN
Une passe froide ne fait pas confiance aux statuts/bindings primaires et cherche divergence sémantique/mécanique sur les lignes matérielles.

### REQ-CR-025 — Multi-route CardFactsResolver — CLOSED (G2, 2026-10-01)
Route failure != information failure. Cache/provider(s)/official/direct/web adapter/fallback ; UNRESOLVED seulement après épuisement ou conflit matériel non résolu.
Fermé : `card_data.CardFactsResolver` (routes injectables ordonnées, cache-first, `ResolutionAttempt` provenance,
`CARD_FACTS_UNRESOLVED` seulement après épuisement, `CARD_FACTS_CONFLICT` en mode `verify=True` si désaccord matériel entre deux routes).
`CardDataService` accepte désormais `routes=[...]` (le `provider=` single-route reste rétro-compatible).
`Runtime.__init__` accepte `card_routes=[...]`.
Preuve : `tests/test_g2_card_facts_resolver.py` 6/6 EXECUTED_PASS.
`tests/test_g0_characterization.py::RedProviderFallback` stale intentionnellement (voir son en-tête).

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
