# Harness d’exécution — Chat — V3 + MCB1 + Proof Floor / Authoritative Dry-Run — candidat non nommé

## Rôle

Le harness impose l’ordre, la fraîcheur, l’identité des artefacts et les invariants mécaniques. Il ne juge jamais la qualité stratégique, la progression narrative, la classification, la viabilité multi-systèmes ni le sens d’un texte de carte.

**Le DAG impose le quand. Les autorités métier imposent le comment juger. Le harness autorise ou refuse la transition suivante.**

Runtime nominal de cette implémentation : `harness_runtime_v1.py` v1.43-proof-floor-dryrun. Cette mention ne crée ni RC système ni promotion stable.

---

## 1. Chaîne

Chemin normal :

`CONTEXT_RESOLVED`
→ `BANLIST_BOUND`
→ `DIRECTION_RESOLVED`
→ `NARRATIVE_RED_CLOSED`
→ `NARRATIVE_CONTRACT_FROZEN`
→ `FUNCTIONAL_INTENT_FROZEN`
→ `EXPLORATION_CLOSED`
→ `CONCEPT_SELECTED`
→ `CLASSIFICATION_CLOSED`
→ `STYLE_AXES_CLOSED`
→ `DECK_DRAFT_CREATED`
→ `NARRATIVE_CONFORMANCE_CLOSED`
→ gates multi-systèmes si routés
→ validation mécanique du registre si requise
→ `FINAL_CLASSIFICATION_CLOSED`
→ `VISUAL_ASSETS_BOUND`
→ `RENDER_CONTRACT_FROZEN`
→ `FINAL_RENDER_PREPARED`
→ `PILOTAGE_VALIDATED`
→ `FINAL_VALIDATION_PASS`
→ `authorize` / `STOP_OUTPUT_ALLOWED`.

Un gate ne peut être fermé que par son autorité autorisée, avec un statut autorisé et sur le `run_id`/artefact courant.

---

## 2. Chemin nominal RC16.23.4

Le LLM ne doit pas inspecter le code Python pour connaître le schéma.

0. Pour une nouvelle demande complète, matérialiser le texte exact de la demande puis exécuter `campaign-open --scope-dir <scope> --request-file <request>`. Tant qu’aucun attempt n’est enregistré, `prebootstrap-handoff-check` doit refuser toute fin de tour : le bootstrap est encore requis. Une continuation déjà active ne rouvre pas une campagne concurrente.
1. `dispatch-run` est l’unique entrée normale de run : il décide mécaniquement START vs RESUME à partir de l’index de session et des leases exacts et enregistre l’attempt dans la campagne active. `start` direct est capability-gated et réservé au bootstrap interne du dispatcher.
2. Les autorités produisent leurs artefacts selon les Sources.
3. Lorsque plusieurs gates séquentiels sont déjà prêts, `validate-bundle` est le chemin normal afin de réduire les round-trips sans fusionner ni sauter de gate.
4. Pour Pilotage : l’autorité produit `pilotage_business.json` avec `execution_contract_version=RC16.2`, SRC/GAME RULES et MCB primaires. Le harness exécute d’abord un `authoritative dry-run` read-only commit-equivalent ; les défauts Render/Admin sont reroutés sans budget métier, les défauts métier seuls consomment ce budget. `pilotage-commit` n’est autorisé qu’après PASS frais du dry-run, puis compile les conséquences MCB dans `pilotage_contract.json` (`wire_schema=ygo-pilotage-contract-v3`) et confirme le `FULL_SHARED_VALIDATOR` avant `PILOTAGE_VALIDATED`.
5. Le bundle est exécuté **séquentiellement** ; arrêt au premier FAIL ou `WAITING_USER_INPUT`.
6. `authorize` n’est possible qu’après fermeture exacte de tous les gates applicables.

Sous `FAST_ENFORCED`, le mode CLI direct `complete` n’est plus un chemin nominal ni diagnostique de production : il est refusé afin d’empêcher les BYPASS. Les transitions internes exactes restent exécutées par `advance-prepared`, `render-commit` et `pilotage-commit`; les tests peuvent appeler les primitives Python directement sans transformer cette possibilité en route CLI.

### Compilation puis fermeture de rendu RC16.3

Avant freeze, les autorités STRUCTURE produisent `render_policy.json` : elles choisissent les exigences non dérivables, mais ne recopient jamais les faits déjà autoritaires.

Le chemin nominal est :

RC16.22.1 : `rendu final candidat → render-commit → projection déterministe policy/contract/components/manifest → validation complète en staging → RENDER_CONTRACT_FROZEN + FINAL_RENDER_PREPARED`. Le modèle ne rédige plus `render_policy.json` ni le plan/manifest composants.

À l’intérieur de `render-commit`, la projection injecte mécaniquement `run_id`, `deck_artifact`, `render_id`, hashes autoritaires, direction finale, totaux de deck, requirements STRUCTURE et composants requis. Aucune copie manuelle équivalente n’est autorisée.

Au freeze, le runtime recharge la policy et les artefacts courants, recompile le contrat attendu et exige l'identité canonique exacte. Un contrat librement rédigé ou modifié reçoit `COMPILED_RENDER_CONTRACT_REQUIRED` ou `COMPILED_RENDER_CONTRACT_MISMATCH`.

Après `RENDER_CONTRACT_FROZEN`, le contrat est **immuable par hash**.

Sous RC16.22.1, ces assertions sont exécutées dans le staging de `render-commit` avant tout freeze autoritatif. En cas de FAIL, le LLM corrige uniquement le **rendu candidat** ; aucun gate Render n’est conservé comme fermé.

Avant le premier `FINAL_RENDER_PREPARED`, un retry reste un **attempt du même render-vN**. `presentation-change` est interdit sans rendu déjà préparé. Maximum nominal : 3 attempts en échec par contrat gelé ; duplicate/stagnation/budget épuisé arrêtent le run en fail-closed.

Sur PASS, `render-check --write-manifest` matérialise le manifest canonique. `FINAL_RENDER_PREPARED` n’accepte que ce bundle exact. Si le contrat/runtime paraît lui-même défectueux après freeze, utiliser le chemin `contract-defect` et arrêter ; ne jamais réécrire les critères pour sauver le run.

---


## 2 bis. Continuité d’orchestration — RC16.8

Depuis RC16.11, un `DIRECTION_CONFLICT_REQUIRES_USER_SELECTION` à `CLASSIFICATION_CLOSED` matérialise automatiquement `WAITING_USER_INPUT`. La réponse utilisateur doit reprendre **ce même run** par `resume-run --user-resolution-file <direction_contract.json>`. `start` est interdit comme continuation de cette attente. Le runtime valide le nouveau contrat de direction avec l’autorité STYLE existante, conserve contexte+banlist, invalide `DIRECTION_RESOLVED` et tout downstream lié à l’ancienne direction, referme la direction, incrémente `invocation_seq`/`resume_count`, puis journalise `RUN_RESUMED`. Aucun `deck-v2` ni material-change n’est créé.

Le checkpoint WAITING expose un `waiting_context` instrumental (gate, attempt, error code, fingerprint, `resolution_kind`). Une résolution rejouée après reprise est refusée par `RUN_NOT_WAITING_FOR_USER_INPUT`; un waiting non supporté ne peut pas consommer arbitrairement un direction contract.

Sous RC16.22.1, `compile-render-contract` reste une primitive interne/forensic. La route nominale est `render-commit`, qui dérive et valide toutes les dépendances Render sur l’état courant avant leur fermeture. Après invalidation, relancer `render-commit` sur le rendu candidat courant.

---

## RC16.15 — Continuity scope / lease

RC16.15 matérialise un **scope durable de continuation** afin qu’un run logique non terminal ne puisse plus être remplacé silencieusement par un nouveau bootstrap dans le même scope. Le runtime ne reçoit aucun identifiant natif de conversation ChatGPT : le Harness conserve donc le même `scope_dir` jusqu’à `COMPLETED`, `TERMINAL_FAILED` ou `/fresh` explicite. Des scopes distincts restent totalement indépendants et peuvent tourner en parallèle ; aucun lock global `/mnt/data` n’est autorisé.

Au niveau bas RC16.15, le bootstrap matérialise toujours un scope/lease. Depuis RC16.16, ce bootstrap est déclenché uniquement par `dispatch-run`; `start` direct normal est refusé. Le runtime crée atomiquement `<scope>/continuation_lease.json` et le lie à `scope_id`, `run_id`, `run_dir`, l’état courant, le checkpoint et le hash exact de `harness_state.json`. Le lease reste `ACTIVE` pour `IN_PROGRESS` et `WAITING_USER_INPUT`; il devient `CLOSED` uniquement pour `COMPLETED` ou `TERMINAL_FAILED`. Un checkpoint ne peut jamais réactiver un lease fermé.

Avant tout `start`, le runtime inspecte le lease du scope. Si un run `ACTIVE` existe, le bootstrap est refusé **avant création du nouvel état** avec `ACTIVE_LOGICAL_RUN_EXISTS` et expose `scope_id`, `active_run_id`, `active_run_dir`, `run_state`, `next_required_gate`, `waiting_context` et l’action recommandée `resume-run`. Un scope `CLOSED` permet un nouveau run logique ; deux scopes différents ne se bloquent jamais.

Commande d’inspection : `inspect-continuation --scope-dir <scope>`. Elle ne ferme aucun gate et renvoie seulement l’état instrumental et `recommended_action = RESUME | USER_RESOLUTION_REQUIRED | NEW_RUN_ALLOWED`. Après `WAITING_USER_INPUT`, l’ordre obligatoire est `inspect-continuation → matérialiser le user resolution file → resume-run --user-resolution-file ...`; après coupure/recovery d’un run `IN_PROGRESS`, `inspect-continuation → resume-run`. Dans les deux cas, le même `run_id` et le même scope sont conservés. Une simple résolution de direction ne crée aucune nouvelle version de deck.

Toute corruption du lease, divergence de hash, binding run/scope incohérent ou divergence lease/checkpoint est **fail-closed**. Un échec contrôlé de rendu, un stall ou `DUPLICATE_FAILED_RENDER` ne ferme jamais le lease tant que le run reste non terminal.



## RC16.16 — Session Dispatcher / Abort / Fault Injection / Fast Path

RC16.16 ajoute un index runtime-owned `session_continuation.json` au-dessus des scopes RC16.15. Il n’est jamais une source de vérité métier : à chaque routage actif, le runtime vérifie obligatoirement `session index → continuation_lease.json → run_checkpoint.json → harness_state.json`, avec hashes exacts et fail-closed sur toute divergence.

### Entrée unique de run

Chemin normal : `dispatch-run --scope-dir <candidate> --run-dir <candidate> --run-id <candidate>`.

- aucune session active → émission d’une capability bootstrap one-shot, puis création interne du run et binding de l’index ;
- session `IN_PROGRESS` → le dispatcher ignore tout nouveau scope candidat et reprend **le run indexé exact** ;
- session `WAITING_USER_INPUT` → `USER_RESOLUTION_REQUIRED`; avec `--user-resolution-file`, reprise du même run via la primitive RC16.8 ;
- session terminale → nouveau bootstrap autorisé.

`start` direct sans capability runtime-owned reçoit `DIRECT_START_FORBIDDEN` avant création de state ou `RUN_BOOTSTRAPPED`. La capability est liée à `run_id`, `run_dir`, `scope_dir`, mode et options, puis consommée une seule fois. Il est donc impossible de contourner une session active en inventant un second scope dans la même discussion. Le verrou reste sandbox-local : des discussions distinctes peuvent fonctionner en parallèle.

### Arrêt explicite et `/fresh`

`abort-run --reason <...>` journalise `RUN_ABORT_REQUESTED` puis `RUN_ABORTED`, conserve les artefacts, interdit toute sortie terminale, ferme lease + index et distingue `USER_ABORTED` d’un `contract-defect`. `/fresh` passe par `dispatch-run --mode fresh` : s’il existe un run actif, il est d’abord aborté avec `USER_REQUESTED_FRESH`, puis le nouveau run frais est bootstrapé. Aucun ancien run ne reste silencieusement ACTIVE.

### Interruption déterministe TEST_ONLY

`simulate-interruption` est strictement **TEST_ONLY**. Elle exige run/checkpoint/lease/index actifs, journalise `SIMULATED_INTERRUPTION`, ne ferme aucun gate, ne change ni `deck-vN` ni `render-vN`, ne ferme pas le lease et n’autorise aucune sortie. Le prochain `dispatch-run` doit reprendre le même run et produire `RUN_RESUMED`. Un vrai timeout plateforme reste une chaos evidence facultative, jamais une exigence de certification.

### FAST ≠ SKIP

RC16.16 n’enlève aucune autorité ni aucun gate. L’accélération vient uniquement de la réduction de plomberie et de round-trips :

- `validate-bundle` devient le chemin nominal dès que plusieurs gates successifs ont déjà leurs artefacts exacts ; chaque gate conserve son autorité, ses événements et son ordre ;
- le bootstrap matérialise une fois `source_inventory.json`; les hashes statiques déjà bindés sont réutilisés comme identité instrumentale ;
- `compile-pilotage-contract` injecte uniquement les bindings mécaniques dérivables (`run_id`, deck courant, render SHA, wire schema, source SHA, headings/count rendus) autour d’un **payload métier fourni par l’autorité Pilotage** ; il ne choisit aucun starter, légalité, ressource, reproductibilité ou PASS ;
- `pilotage-commit` exécute intérieurement le wire preflight et le **même FULL_SHARED_VALIDATOR** que le gate, sur le deck/render exacts. Le receipt d’exécution prouve ce passage mécanique exact-hash ; il ne prétend jamais être un oracle sémantique indépendant sur un fait de carte omis/mal interprété ;
- les artefacts dérivés peuvent être réutilisés uniquement à contenu/hashes d’entrées identiques. Les événements `DERIVED_CACHE_HIT/MISS` n’altèrent aucun historique de gate et aucun PASS métier n’est caché.

`inspect-run-state` expose aussi des métriques instrumentales (`duration_seconds_raw`, gate/preflight/render fails, resumes, bootstrap_count). La cible produit ≤15 min, idéalement ~10 min, n’autorise jamais un skip : si les invariants sont bons mais le wall-clock reste élevé, le résultat performance est `PARTIAL`.

## 2 quinquies. Pre-Pilotage Closure — RC16.11

Un conflit exact `CLASSIFICATION_CLOSED / DIRECTION_CONFLICT_REQUIRES_USER_SELECTION` matérialise désormais **automatiquement** `WAITING_USER_INPUT` dans le checkpoint courant, avec `waiting_context` et événement `WAITING_FOR_USER_INPUT`. Le runtime ne choisit jamais la direction : il rend durable le besoin de décision utilisateur.

Après le choix utilisateur, le seul chemin de continuation est `resume-run --user-resolution-file <direction_contract.json>` sur le **même run_id**. La reprise RC16.8 reste compétente pour valider le contrat STYLE, préserver contexte+banlist, invalider direction+downstream, refermer `DIRECTION_RESOLVED`, incrémenter `resume_count`/`invocation_seq` et journaliser `RUN_RESUMED`. Aucun nouveau bootstrap, deck-v2 ou material-change n'est créé par cette résolution.

Le binding dérivé `direction-binding` est validé par son **comportement de rendu** : son `contains_regex` doit matcher une ligne canonique portant la classification finale. Le runtime n'inspecte plus le texte source échappé de la regex et ne hardcode aucune direction ni sous-type. `integration_subtype` reste distinct de `classification`.

`compile-render-contract` est désormais une transaction durable :

`RENDER_CONTRACT_TRANSACTION_STARTED → compile vers candidat temporaire → PRE_FREEZE_VALIDATE → promotion atomique → DERIVED_DEPENDENCY_MATERIALIZED → GATE_REENTRY_TRIGGERED → RENDER_CONTRACT_FROZEN → RENDER_CONTRACT_TRANSACTION_SUCCEEDED`.

Un refus contrôlé produit `RENDER_CONTRACT_TRANSACTION_FAILED` avec phase/code/détail/hashes réels ; une exception Python réelle produit `RENDER_CONTRACT_TRANSACTION_EXCEPTION` avec traceback réelle/hashée. Un candidat invalide n'est pas promu comme nouveau contrat canonique et la transaction consomme **0 render retry**.

RC16.11 ferme la frontière pré-Pilotage jusqu'à `FINAL_RENDER_PREPARED`. Il ne modifie ni les critères de `PILOTAGE_VALIDATED`, ni ceux de `FINAL_VALIDATION_PASS`, ni les règles RC16.10 de `axis-line-length`.

---

## 2 ter. Render Attempt Observability — RC16.9

Les refus de `render-check` doivent être forensiquement lisibles sans dépendre de la conversation. Les preflights composants/contrat restent **avant** le retry accounting : un refus pre-attempt ne crée pas de vrai render attempt et consomme 0 retry.

Une tentative comptabilisée suit :

`RENDER_ATTEMPT_STARTED → validation déterministe → RENDER_ATTEMPT_SUCCEEDED | RENDER_ATTEMPT_FAILED | RENDER_ATTEMPT_EXCEPTION`.

`STARTED` lie `render_id`, deck, render/contract/component hashes, inventory hash, bundle SHA, compteur avant tentative et budget. `FAILED` persiste la **liste exacte** des failures observées, la signature, le compteur après tentative, `stalled`, `budget_exhausted`, checkpoint et state SHA. Si le runtime ajoute `RENDER_REPAIR_STALLED` ou `RENDER_REPAIR_BUDGET_EXHAUSTED`, ces codes doivent apparaître dans le receipt. `SUCCEEDED` lie le render/manifest/contract/component exacts. Une exception Python réelle après STARTED produit `RENDER_ATTEMPT_EXCEPTION` avec traceback réelle/hashée.

Un retry déjà bloqué par duplicate/stall/budget ne relance pas la validation et ne consomme rien de plus ; il peut être journalisé `RENDER_ATTEMPT_BLOCKED`. `inspect-run-state` expose `last_render_attempt`. RC16.9 **n’assouplit aucune règle de rendu/composant** et ne corrige aucune cause spécifique observée au black-box.

---

## 2 bis. Bootstrap durable et observabilité des gates — RC16.7

Pour toute **nouvelle** construction/reconstruction complète sans continuation active, `campaign-open` est la première matérialisation de la demande puis `dispatch-run` est la première action instrumentale de run : le run, `harness_state.json`, le premier checkpoint, le lease de continuation et `RUN_BOOTSTRAPPED` doivent exister avant exploration, recherche, construction ou validation coûteuse. Lorsqu’un scope possède déjà un run non terminal, aucun nouveau bootstrap n’est valide : inspecter puis reprendre le même run. Un besoin de choix utilisateur reste matérialisé dans `WAITING_USER_INPUT`; RC16.8 définit la reprise same-run pour le conflit de direction supporté.

Toute commande `complete` est observable comme une transaction :

`GATE_ATTEMPT_STARTED → validation existante → GATE_ATTEMPT_SUCCEEDED | GATE_ATTEMPT_FAILED | GATE_ATTEMPT_EXCEPTION`.

`GATE_ATTEMPT_STARTED` est journalisé et fsync avant la validation. Un `DENIED` produit un receipt `GATE_ATTEMPT_FAILED` avec code, détail disponible, fingerprint des inputs et signature. Une exception Python réelle produit `GATE_ATTEMPT_EXCEPTION` et une traceback matérialisée/hashée seulement si cette exception existe réellement. Les critères des autorités ne changent pas.

Si une invocation cesse après `STARTED` sans événement terminal, `resume-run` réconcilie la tentative : gate déjà fermée → `GATE_ATTEMPT_RECONCILED_SUCCESS`; gate encore ouverte → `GATE_ATTEMPT_OUTCOME_UNKNOWN`. Le runtime n’écrit jamais `HOST_INTERRUPTION`, timeout, crash ou cause réseau sans signal fiable.

Après un échec, une nouvelle tentative du même gate avec le même état et le même fingerprint d’inputs est refusée avant revalidation par `GATE_INPUT_UNCHANGED_AFTER_FAILURE` et journalisée `GATE_STALL_DETECTED`. Aucun render retry n’est consommé par ce guard. `inspect-run-state` expose un `progress_block` dérivé du journal ; un simple checkpoint ou `continue` ne l’efface pas.

`authorize` refuse toute tentative `STARTED` non réconciliée et tout `progress_block` actif.

RC16.7 **ne corrige aucun gate métier particulier**, notamment `VISUAL_ASSETS_BOUND` : il garantit seulement que le prochain échec laisse une cause structurée, ou que l’issue inconnue est explicitement matérialisée.

---

## 3. Durable checkpoint / resume RC16.4

RC16.4 considère qu’un run logique peut s’étendre sur plusieurs réponses ChatGPT. Une coupure conversationnelle ne vaut ni FAIL métier ni nouveau run.

Le runtime matérialise automatiquement après chaque transition persistée :
- `run_checkpoint.json` — index canonique de reprise lié au `harness_state.json`, aux artefacts et hashes autoritaires ;
- `run_journal.jsonl` — journal instrumental append-only des checkpoints et reprises.

Commandes :
- `checkpoint-run --run-state IN_PROGRESS|WAITING_USER_INPUT|TERMINAL_FAILED|COMPLETED` ;
- `inspect-run-state` ;
- `resume-run`.

Séquence nominale de reprise :

`checkpoint → nouvelle invocation → resume-run → vérification run_id + hash état + bindings autoritaires → restauration du prochain gate → poursuite`.

Le checkpoint ne crée aucun PASS métier et ne remplace jamais le Registre. Il ne recopie pas librement la decklist : il référence l’artefact courant, son snapshot/hash et les preuves déjà matérialisées.

États :
- `IN_PROGRESS` : reprise autorisée ;
- `WAITING_USER_INPUT` : un simple `continue` ne satisfait pas la gate et ne peut pas être effacé instrumentalement tant que l’état autoritaire n’a pas changé ;
- `TERMINAL_FAILED` : reprise refusée, budgets épuisés conservés ;
- `COMPLETED` : aucune seconde sortie terminale.

Les attempts de rendu restent bornés à 3 **à travers les reprises**. `resume-run` ne consomme aucun attempt. Un état terminal ne peut pas être rouvert par `checkpoint-run`.

Le runtime ne déclare jamais `HOST_INTERRUPTION` sans signal technique fiable. Il constate seulement qu’un run non terminal matérialisé est repris dans une nouvelle invocation.

La télémétrie RC16.4 (`invocation_seq`, `resume_count`, compteurs de retry/checkpoints) sert uniquement à préparer un futur chantier de performance ; elle n’influence aucun jugement métier.

---



## 2 quater. Native Line Assertion Binding — RC16.10

Les critères de rendu spécialisés restent définis par leurs autorités STRUCTURE. Lorsqu'une source prescrit explicitement un type d'assertion natif, `render_policy.json` doit employer ce type et ne doit pas le réencoder par regex.

Pour `STRUCTURE_AXES_COMBOS_DECKS_PERSONNAGES` / `axis-line-length`, la source impose désormais `max_line_length` avec son propre seuil et son propre scope. Le runtime vérifie uniquement la conformité structurelle du binding (type natif, forme, scope présent) et **ne choisit ni ne redéfinit le seuil métier**.

Une policy qui remplace ce requirement par `contains_regex`/`regex_min_count` est refusée avant `RENDER_CONTRACT_FROZEN` par `NATIVE_ASSERTION_BINDING_MISMATCH`, avec **0 render retry** consommé. Le compiler ne transforme pas une regex en assertion native et ne répare jamais un contrat déjà gelé.

Les autres assertions regex restent autorisées lorsqu'elles représentent réellement des contraintes regex. RC16.10 ne modifie ni les critères Pilotage/Final, ni les règles de retry, ni le chemin `contract-defect`.

---

## 3 bis. Component Payload Compilation — RC16.6

Pour `main-carousel` et `mini-carousel`, le payload fonctionnel n’est plus écrit librement. Le chemin obligatoire est :

Sous RC16.22.1, ce pipeline composants est interne à `render-commit` : `visual_assets autoritaire → plan dérivé → payloads canoniques → manifest dérivé → validation staging`.

Le runtime sérialise uniquement la forme déterministe `ui_type=image_group`, `layout=carousel` et les `image_refs` exactes déjà décidées par STRUCTURE. Le payload reste fonctionnel et stable : run/deck/render et provenance restent dans le manifest compilé afin que `PRESERVE` ne change pas de SHA sans changement visuel. Il ne choisit ni cartes, ni images, ni applicabilité. `refactor-diff` conserve son artefact canonique historique.

Avant tout retry de rendu, `render-check` recompile et vérifie payloads + manifest. Un payload freehand, altéré ou de provenance différente est refusé **avant** l’incrément de `render_attempts`. Les protections de stagnation, budget 3/3 et terminal fail restent inchangées.


## 3 ter. Specialized Component Binding Closure — RC16.12

Pour un mini-carrousel signature décidé par `STRUCTURE_AXES_COMBOS_DECKS_PERSONNAGES`, séparer strictement l'identité spécialisée de la primitive renderer : `component_id=signature-mini-carousel`, `type=mini-carousel`, avec le `parent` exact décidé par STRUCTURE. Le requirement conserve `id=signature-mini-carousel`, mais son `component_min_count` doit compter `component_type=mini-carousel` avec le même parent. Le runtime vérifie ce binding avant compilation/rendu ; il ne choisit ni l'applicabilité, ni l'Axe, ni les cartes, ni les images.

`compile-component-payloads` reste l'unique producteur des payloads `main-carousel|mini-carousel`; aucun payload freehand ni nouveau type renderer `signature-mini-carousel` n'est autorisé. `compile-component-manifest` doit préserver `component_id`, `type`, `parent`, cartes, refs et hash du payload exact.

Si le chemin `contract-defect` terminalise un run avant épuisement du budget de rendu, la décision doit être matérialisée par `CONTRACT_DEFECT_MATERIALIZED` avec la raison et les bindings réels. Ce receipt est observatif : il ne consomme aucun retry, ne change aucun critère métier et ne rend pas le run reprenable.

---

## 4. Artifact Identity Closure — RC16.5

RC16.5 ajoute deux fermetures instrumentales sans modifier les critères métier.

### Component Artifact Binding Compilation

Les composants visuels passent par un `component_plan.json` sémantique sans `artifact_file` ni `artifact_sha256`.

Sous RC16.22.1, `component_plan` et le manifest sont dérivés par `render-commit`; les primitives de compilation restent réservées aux tests/forensic et ne sont plus un chemin de production CLI.

Le compiler lie chaque `component_id` au fichier réellement matérialisé et calcule son SHA. `render-check` recompile ce manifest **avant** de consommer un attempt et refuse tout manifest libre, modifié ou lié à une provenance différente.

### Deck Artifact Identity Guard / Evidence Refresh

`material-change` exige un `--candidate-snapshot`. Le runtime calcule `deck_composition_sha256` depuis Main/Extra/Side (`nom + quantité`, indépendamment de `artifact_id`).

- composition différente : `deck-vN → deck-vN+1` reste disponible ;
- composition identique : nouvelle version uniquement avec `--material-proof` frais d’une autorité compétente ;
- correction de preuve/rapport : `evidence-refresh --from-gate ...` rejoue les gates concernés sur le même `deck-vN`.

Le runtime ne décide jamais qu’un Axe, une relation ou une ressource est stratégiquement matériel. Il vérifie la composition et la formalité de la preuve. Un evidence refresh conserve les budgets de rendu déjà consommés.

### Pilotage

L’ordre reste `FINAL_RENDER_PREPARED → PILOTAGE_VALIDATED → FINAL_VALIDATION_PASS`. RC16.5 ne déplace ni ne simplifie Pilotage.

## 5. Commande `template`

`template --kind pilotage --output <file>` génère le squelette nominal `wire_schema=ygo-pilotage-contract-v3` / `execution_contract_version=RC16.2` avec MCB1. Les anciens squelettes RC16.1 ne sont conservés que pour compatibilité/régression.

Le template :
- ne contient aucune carte ou règle Yu-Gi-Oh hardcodée ;
- ne remplace pas les Sources métier ;
- évite l’inspection de `harness_runtime_v1.py` ;
- doit être rempli avec les données du run réel avant validation.

---

## 6. Commande `validate-bundle`

Le fichier bundle contient un `run_id` et une liste ordonnée d’opérations `complete` avec les mêmes arguments qu’en mode unitaire.

Garanties :
- aucun parallélisme des gates métier ;
- ordre identique au mode unitaire ;
- même premier point de rupture ;
- aucune promotion d’un gate ultérieur si le précédent n’est pas fermé ;
- état persisté après chaque fermeture réussie.

La réduction d’appels CLI ne modifie donc pas la sémantique du DAG.

---

## 7. Pilotage RC16.1 — compatibilité historique

`PILOTAGE_VALIDATED` exige `pilotage_contract.json` lié au deck et au rendu exacts.

Le chemin historique RC16.1 accepte `execution_contract_version=RC16.1` et exige un `unified_cold_audit` par replay. Le chemin nominal post-RC16.22.1 est défini plus bas par le durcissement MCB1 (`execution_contract_version=RC16.2`). Le runtime projette cet audit en mémoire vers les validateurs historiques de :
- semantic/SRC ;
- GAME RULES ;
- legality ;
- state ;
- topology ;
- derived claims ;
- certainty ;
- backward proof.

Chaque domaine conserve son propre FAIL. Le runtime ne crée aucune règle métier.

Les anciens contrats `RC16` restent acceptés pour régression seulement.

---

## 8. Artefacts, hashes et fraîcheur

Chaque gate est rattaché au `run_id` et, lorsque pertinent, au `deck-vN`, au `render-vN` et aux hashes exacts des fichiers validés.

Une modification matérielle :
- crée `deck-vN+1` ;
- matérialise une transition `STALE` ;
- invalide les gates dépendants à partir du point prévu par le runtime ;
- impose les retests nécessaires sur la nouvelle version.

Une modification de présentation seule crée une nouvelle lignée de rendu sans modifier le deck mais invalide les gates de rendu nécessaires.

Aucun PASS antérieur ne peut être réutilisé sur un artefact différent sans règle explicite de fraîcheur.

---

## 9. Refactor et DIFF_ONLY

Après sortie déjà autorisée, un refactor matériel utilise par défaut `DIFF_ONLY`, sauf demande explicite de decklist complète. Le runtime matérialise le diff canonique, exige l’impact combos lorsque requis et maintient les contraintes de continuité visuelle.

---

## 10. Bundle final

`FINAL_RENDER_PREPARED`, `PILOTAGE_VALIDATED` et `FINAL_VALIDATION_PASS` doivent viser exactement le même render/manifest/contract/component inventory.

Depuis RC16.14, après `PILOTAGE_VALIDATED` et avant `FINAL_VALIDATION_PASS` :

`compile-terminal-presentation → terminal_presentation_plan.json → terminal-presentation-check → terminal_presentation.receipt.json`.

Le plan projette mécaniquement le texte exact et **tout l'inventaire de composants déjà autorisé**. Il ne choisit aucune applicabilité. `terminal-presentation-check` contrôle run/deck/render, hashes, exhaustivité, unicité, payloads, types, parents et refs ; son PASS reste mécanique et pré-émission.

`FINAL_VALIDATION_PASS` exige ce receipt frais. `authorize` le revérifie puis expose le plan terminal ; si `component_count > 0`, l'orchestrateur doit émettre le Markdown **et chaque composant du plan**. Il est interdit d'interpréter `terminal_payload.md` comme la réponse complète lorsqu'un inventaire UI non vide existe.

Le runtime ne journalise jamais `DISPLAYED=true` : l'affichage réel dans le client reste certifié par Fresh black-box.

`authorize` vérifie aussi :
- conformité narrative fraîche sur le deck courant ;
- STALE matérialisé après refactor matériel ;
- combo impact fermé si requis ;
- confiance terminale `HIGH` ;
- copie exacte du rendu dans `terminal_payload.md`.

Seulement alors : `STOP_OUTPUT_ALLOWED`.

---

## 11. Budget d’orchestration nominal

Sans `STALE` ni preuve non résolue :
- acquisition de preuves : une phase groupée ;
- construction de la Proof-Carrying Line : une passe ;
- `unified_cold_audit` : une passe indépendante ;
- validation harness/ledger : appels groupés lorsque possible ;
- finalisation/rendu : une phase.

Une autorité ne relit pas/reconstruit une ligne déjà fermée uniquement pour reproduire la même information sous un autre format.

---

## 12. Fail closed

Si un instrument requis ne peut pas être exécuté, si un hash/version diverge, si une sortie obligatoire manque ou si un gate échoue : ne pas déclarer PASS et ne pas produire la sortie terminale.

**PASS mécanique ≠ PASS métier.**

---

## RC16.13 — Pilotage Contract Materialization

Avant `PILOTAGE_VALIDATED`, le contrat spécialisé doit être matérialisé selon le wire schema publié par `pilotage-schema`. `VALIDATION_PILOTAGE_LIGNES_DECKS_PERSONNAGES` reste seule autorité sur les starters, lignes, propriétés, légalité, états, topologie, preuves et verdict métier ; le runtime ne possède que l'ABI JSON.

Chemin nominal RC16.16 :

`FINAL_RENDER_PREPARED → autorité Pilotage produit le payload métier → pilotage-commit → FULL_SHARED_VALIDATOR exact-hash → PILOTAGE_VALIDATED`.

`template` reste disponible pour diagnostic/compatibilité, mais la compilation canonique est privilégiée pour éviter la plomberie manuelle.

Règles :
- contrat historique RC16.13 : `wire_schema=ygo-pilotage-contract-v2` et `execution_contract_version=RC16.1` ; le chemin nominal MCB1 post-RC16.22.1 utilise v3 / RC16.2 ;
- avec Axes rendus : `starter_exploration_status=COMPLETE`, `starter_inventory_status=PASS` selon la sémantique définie par l'autorité Pilotage ;
- `template --kind pilotage --render-file ...` expose les Axes et toutes les clés de sérialisation mais ne choisit aucun starter ;
- le preflight Pilotage est exécuté à l’intérieur de `pilotage-commit`; les bindings deck/render/manifest/contract/combo-impact connus sont dérivés par le runtime et ne doivent pas être recopiés par le modèle ;
- les erreurs détectables dans une même passe sont renvoyées dans un receipt unique ;
- le preflight ne ferme aucun gate et son PASS n'est jamais un PASS métier ;
- **Aucun critère Pilotage nouveau** n'est inventé par HARNESS ou le runtime ; le full-preflight et le gate réutilisent la même implémentation spécialisée ;
- `PILOTAGE_VALIDATED` exige un receipt preflight PASS frais lié au hash exact du contrat, du rendu, du deck, du schema et de la source Pilotage ;
- toute modification du contrat après preflight rend le receipt `STALE` ;
- les contrôles métier/mécaniques RC16/RC16.1 existants restent exécutés ensuite sans assouplissement ;
- aucun budget Pilotage arbitraire n'est introduit par RC16.13 ; le budget same-model post-RC16.22.1 est une exigence ultérieure explicitement définie par le durcissement MCB1.

Événements : `PILOTAGE_PREFLIGHT_STARTED`, `PILOTAGE_PREFLIGHT_FAILED`, `PILOTAGE_PREFLIGHT_SUCCEEDED`, `PILOTAGE_PREFLIGHT_EXCEPTION`. `inspect-run-state` expose `last_pilotage_preflight`.

Le schema/scaffold ne doit contenir aucun nom de carte, starter ou Axe spécifique.


---

## RC16.14 — Terminal Presentation Assembly Closure

Le chemin terminal nominal devient :

`PILOTAGE_VALIDATED → compile-terminal-presentation → terminal-presentation-check PASS → FINAL_VALIDATION_PASS → authorize → STOP_OUTPUT_ALLOWED → émission du texte + composants du plan`.

Artefacts :
- `terminal_presentation_plan.json` — projection canonique du texte + inventaire UI ;
- `terminal_presentation.receipt.json` — preuve mécanique de fraîcheur et de complétude pré-émission.

Codes fail-closed principaux :
- `TERMINAL_PRESENTATION_PLAN_REQUIRED` ;
- `TERMINAL_PRESENTATION_RECEIPT_REQUIRED` ;
- `TERMINAL_PRESENTATION_PLAN_STALE` ;
- `TERMINAL_PRESENTATION_RECEIPT_STALE` ;
- `TERMINAL_PRESENTATION_INVENTORY_MISMATCH` ;
- `TERMINAL_COMPONENT_PAYLOAD_MISSING` ;
- `TERMINAL_COMPONENT_BINDING_MISMATCH` ;
- `TERMINAL_TEXT_PAYLOAD_MISMATCH`.

Un plan à zéro composant est valide si le pipeline STRUCTURE a réellement fermé l'applicabilité ainsi. Le runtime n'ajoute jamais une quote ou un mini-carrousel absent du contrat spécialisé.

---

## RC16.18 — SAFE BATCH TOP-3

RC16.18 accélère uniquement l’orchestration de RC16.16. **FAST ≠ SKIP** : aucune autorité, validation métier, validation Pilotage, Terminal Presentation ou Final Validation ne peut être omise pour gagner du temps.

### 1. Sequential Safe Batch

`execute-batch` reçoit plusieurs fermetures déjà préparées et les exécute **strictement dans `sequence(st)`**, une par une, via le même `cmd_complete` que le chemin parent. Chaque gate conserve ses propres événements et son checkpoint durable. Le batch s’arrête au premier FAIL et ne tente jamais la queue restante.

Un item déjà durablement fermé peut être ignoré lors d’une reprise seulement si son authority/status et, lorsqu’il est fourni, son evidence hash concordent. Il n’est jamais réexécuté ni synthétisé.

### 2. Direction USER_EXPLICIT

`bind-explicit-direction` et l’item batch `explicit-direction` ne sont autorisés que pour une direction effectivement fournie par l’utilisateur : `Canonique`, `Canonique remixé` ou `Alternatif`. Le binder normalise uniquement le wire contract `USER_EXPLICIT`, puis passe immédiatement par le validator parent de `DIRECTION_RESOLVED`. Le runtime ne choisit jamais une direction.

### 3. Fuse no-progress

Deux échecs consécutifs identiques sur le même gate, le même checkpoint, le même state hash et le même input fingerprint rendent la troisième tentative identique non exécutable. Elle est bloquée avant validator avec `REPEATED_GATE_ERROR_NO_PROGRESS`. Une modification réelle d’un binding ou du checkpoint réarme naturellement le fuse.

### 4. Mechanical preflight read-only

`mechanical-preflight --kind render|pilotage` agrège les défauts mécaniques détectables : fichiers, IDs, hashes, schéma, component bindings et `combo_impact` requis. Il ne journalise aucun PASS, ne modifie ni state ni checkpoint, ne produit aucune décision métier et ne ferme aucun gate. Après PASS, le vrai chemin Render/Pilotage parent reste obligatoire.

### 5. Evidence refresh sélectif

`evidence-refresh-selective` conserve un gate aval uniquement lorsque sa dépendance est explicitement connue et que son `dependency_fingerprint` demeure exact. Une dépendance inconnue, un fingerprint absent ou un input modifié déclenche soit STALE ciblé, soit le fallback **large RC16.16**. `material-change` n’est jamais optimisé par cette règle et conserve les règles STALE parent.

Le chemin parent `evidence-refresh` reste disponible et inchangé.

### 6. Verrous produit

RC16.18 ne modifie pas la juridiction ni la logique des sources métier. En particulier :

- les carrousels et mini-carrousels requis doivent survivre jusqu’au plan terminal ;
- un refactor post-sortie reste `DIFF_ONLY` par défaut, FULL seulement sur demande explicite/source compétente ;
- `PILOTAGE_VALIDATED` reste lié au rendu/receipt exacts ;
- `FINAL_VALIDATION_PASS` et `authorize` restent obligatoires sur le bundle courant ;
- aucun compiler métier Render/Pilotage supplémentaire n’est introduit.

### 7. Budget Black-Box

Mesure officielle : timestamps persistés `RUN_BOOTSTRAPPED → COMPLETED`.

- full build : objectif 6–9 min, PASS performance `<10:00`, FAIL `>=12:00` ;
- refactor ciblé : objectif 3–5 min, PASS performance `<6:30`, FAIL `>=8:00`.

Ces budgets n’autorisent jamais un skip, un auto-PASS ou une régression visible.


---

# RC16.19 — ENFORCED FASTPATH + TERMINAL REFACTOR FORK

RC16.19 conserve intégralement les autorités métier, validateurs, composants visuels, Pilotage, Terminal Presentation et Final Validation de RC16.18. La modification porte uniquement sur **le routage obligatoire du chemin rapide**, le fork de refactor depuis un run terminal, l'intégrité terminale et l'observabilité.

## 1. Profil nominal `FAST_ENFORCED`

Tout nouveau run créé par `dispatch-run` porte `fastpath_profile=FAST_ENFORCED`.

Pour les gates dont les artefacts sont déjà préparés, la commande nominale est :

`advance-prepared --run-dir ... --run-id ... --bundle-file ...`

Le bundle contient les artefacts déjà produits par les autorités compétentes. `advance-prepared` ne produit aucun contenu métier : il route les opérations contiguës vers le même chemin `cmd_complete`/validateurs que RC16.18, checkpoint après chaque gate et s'arrête au premier FAIL/WAITING.

Une direction utilisateur explicite peut être fournie au bundle sous `explicit_direction` ; le routeur matérialise alors le contrat `USER_EXPLICIT` via le binder parent. Le runtime ne choisit jamais la direction.

RC16.22.1 durcit `FAST_ENFORCED` : `complete`, `compile-render-contract`, `compile-component-payloads`, `compile-component-manifest`, `render-check`, `compile-pilotage-contract` et `pilotage-preflight` sont **bloqués comme commandes CLI de production**. Utiliser `advance-prepared` pour les gates sémantiques, `render-commit` pour Render et `pilotage-commit` pour Pilotage. `FASTPATH_BYPASS` nominal doit rester à 0.

**FAST = moins de frontières d'orchestration ; jamais moins de validations.**

## 2. Refactor après sortie terminale

Un run `COMPLETED` ou `TERMINAL_FAILED` est immuable. Il est interdit de le remettre `IN_PROGRESS` par `material-change`, `evidence-refresh`, `presentation-change` ou fermeture de gate.

Pour un refactor ciblé demandé après une sortie validée, utiliser :

`fork-refactor-from-terminal`

Le fork :

- exige un parent `COMPLETED`, `FINAL_VALIDATION_PASS=PASS` et Terminal Presentation PASS ;
- vérifie le snapshot terminal et la compatibilité de l'inventaire de sources ;
- crée toujours un **nouveau run_id / scope** ;
- enregistre le lineage vers le parent exact ;
- hérite uniquement les gates du préfixe indépendant du nouveau deck, marqués `INHERITED_EXACT` ;
- ne réexécute jamais ces gates comme de nouveaux PASS ;
- ne réutilise jamais comme frais Style→Axes, Deck Draft, Narrative Conformance finale, validation attachée au snapshot, classification finale, Visual Assets, Render, Pilotage ou Final ;
- démarre normalement le travail rejoué à `STYLE_AXES_CLOSED` lorsque le préfixe est prouvablement frais ;
- fixe `DIFF_ONLY` par défaut pour le refactor ciblé, sauf demande explicite de decklist complète ;
- fallback vers un bootstrap complet si la fraîcheur du préfixe ne peut pas être prouvée.

Erreur de mutation d'un terminal : `TERMINAL_RUN_IMMUTABLE_NEW_RUN_REQUIRED`.

## 3. Evidence refresh automatique

`evidence-refresh` devient la façade nominale :

1. tentative automatique de l'invalidation sélective par fingerprints exacts ;
2. conservation uniquement des descendants dont la fraîcheur est prouvée ;
3. fallback automatique vers l'invalidation large RC16.18 dès qu'une dépendance est inconnue ou non fingerprintée.

`material-change` reste toujours une invalidation matérielle ; aucune réutilisation sélective d'un PASS attaché à l'ancien deck n'est autorisée.

## 4. Preflight mécanique automatique

Le chemin nominal exécute un preflight mécanique agrégé :

- avant `render-check` ;
- avant le preflight Pilotage réel.

Le reçu `mechanical_preflight_<kind>.receipt.json` est **non autoritatif**, lié par hashes exacts aux inputs observés et ne ferme aucun gate. Un FAIL mécanique Render bloque `RENDER_ATTEMPT_STARTED`. En CLI de production, un FAIL mécanique Pilotage bloque aussi l'entrée dans le preflight métier complet.

Après PASS mécanique, les validateurs RC16.18 restent obligatoires. `mechanical preflight PASS ≠ Render/Pilotage PASS`.

## 5. Type safety Visual Assets

`image_refs` est vérifié comme `list[str]` avant toute opération d'unicité. Une valeur non-string produit le refus contrôlé `VISUAL_IMAGE_REFS_INVALID_TYPE` ; aucun traceback natif ne doit être créé pour cette erreur d'entrée.

## 6. Observabilité fast-path

Chaque invocation CLI mutante/transactionnelle journalise `COMMAND_TIMING` avec : commande, timestamps début/fin, temps local, checkpoint avant/après et route `BATCH`, `DIRECT_WHITELISTED` ou `BYPASS`.

`fastpath-metrics --run-dir ... [--run-id ...]` expose notamment :

- `fastpath_batches` ;
- `fastpath_items` ;
- `fastpath_bypasses` ;
- `mechanical_preflight_runs` ;
- `wide_refresh_count` ;
- `selective_refresh_count` ;
- `terminal_reopen_attempts_blocked` ;
- `local_runtime_seconds`.

`local_runtime_seconds` mesure uniquement le temps des commandes runtime instrumentées. Il ne doit jamais être présenté comme temps de raisonnement du modèle, temps web, temps outil externe ou attente utilisateur.

## 7. Black-Box compliance RC16.19

Un build Black-Box ne satisfait le fast-path que si :

- `FASTPATH_BYPASS=0` ;
- au moins un batch multi-item est observé ;
- les preflights mécaniques Render et Pilotage sont observés ;
- `evidence-refresh` utilise automatiquement le selective lorsque la fraîcheur est prouvable ;
- aucune régression produit n'est observée.

Un refactor Black-Box doit en plus montrer :

- `fork-refactor-from-terminal` ;
- parent terminal inchangé ;
- lineage exact ;
- premier gate métier rejoué = `STYLE_AXES_CLOSED` lorsque le préfixe est frais ;
- `DIFF_ONLY` par défaut.

Les budgets performance restent des critères Black-Box séparés de la conformité fonctionnelle et de la conformité fast-path.

---

# RC16.22 — SEMANTIC CORE / DETERMINISTIC SHELL

RC16.22 conserve les autorités, gates, validateurs métier, règles Pilotage, Terminal Presentation et Final Validation existants. Il change uniquement **qui écrit la plomberie mécanique**.

## 1. Règle nominale d’authoring

Pour les gates sémantiques supportés, ne plus fabriquer manuellement les enveloppes contenant `run_id`, `authority`, IDs d’artefacts, hashes, chemins, bindings ou provenance déjà connus du runtime.

Dans un bundle `advance-prepared` / `execute-batch`, utiliser l’opération :

`{"op":"semantic-complete","gate":"<GATE>","payload":{...contenu métier appartenant à l’autorité...}}`

Le runtime dérive alors l’identité mécanique et matérialise l’artefact attendu **avant de le transmettre au même validateur/gate parent**. `semantic-complete` ne crée aucun PASS et ne juge aucun contenu métier.

Gates supportés : `NARRATIVE_RED_CLOSED`, `NARRATIVE_CONTRACT_FROZEN`, `FUNCTIONAL_INTENT_FROZEN`, `EXPLORATION_CLOSED`, `CONCEPT_SELECTED`, `CLASSIFICATION_CLOSED`, `STYLE_AXES_CLOSED`, `DECK_DRAFT_CREATED`, `NARRATIVE_CONFORMANCE_CLOSED`, `FINAL_CLASSIFICATION_CLOSED`, `VISUAL_ASSETS_BOUND`.

Pour `STYLE_AXES_CLOSED`, le payload peut demander le statut métier déjà décidé `PASS` ou `REFACTOR`; aucun autre override de statut n’est autorisé.

**Règle courte : décision métier dans le payload ; identité/hashes/bindings dans le runtime.**

## 2. Combo impact après changement matériel

Lorsqu’un refactor matériel exige un `combo_impact`, fournir seulement son contenu sémantique dans le bundle sous `combo_impact`. Le runtime matérialise `combo_impact.compiled.json`, le lie au deck enfant exact et le réutilise automatiquement pour le preflight Pilotage puis `PILOTAGE_VALIDATED`.

Ne recopier manuellement ni son chemin, ni son hash, ni `run_id`, ni `from_artifact`, ni `deck_artifact` lorsqu’ils sont dérivables.

## 3. Render continuity et composants terminaux

Après `presentation-change`, la continuité des composants déjà autoritatifs est dérivée automatiquement. Après refactor matériel, la continuité des exigences portée par l’état autoritatif est également dérivée.

Un composant déclaré requis en amont par STRUCTURE doit exister dans l’inventaire terminal exact. En particulier, un carrousel principal ou mini-carrousel signature requis ne peut pas disparaître puis obtenir Terminal Presentation PASS.

Cette vérification est mécanique : elle ne décide jamais qu’un carrousel est applicable. Cette décision reste à STRUCTURE.

## 4. Atomicité Render

RC16.22.1 remplace ce chemin nominal par `render-commit` : policy/contract/composants/manifest et assertions déterministes sont validés en staging avant fermeture ; tout échec restaure exactement state/checkpoint/lease/session et les fichiers dérivés suivis. Le journal append-only conserve le diagnostic.

## 5. Recherche Internet et preuves

La politique cartes reste Internet. Aucune Card DB ni cache cartes dédié n’est introduit.

Lorsque les Axes sont stabilisés, acquérir si possible les preuves externes nécessaires en une phase groupée puis les réutiliser tant qu’elles restent fraîches et liées à la ligne/version exacte. Une preuve obsolète ou liée à une autre version ne peut pas être recyclée.

## 6. Fast-path RC16.22

Le batching reste secondaire : augmenter le nombre d’items dans un batch n’est utile que si cela réduit réellement les tours modèle et le wall-clock. Ne jamais créer un nouvel artefact ou preflight model-authored uniquement pour accélérer.

Le chemin nominal est donc :

`décisions sémantiques groupées → semantic-complete → render-commit → Pilotage métier structuré → pilotage-commit → Terminal Presentation / Final`

**FAST = moins d’authoring administratif et moins de voyages ; jamais moins de contrôles.**


# RC16.22.1 — Hardening Black-Box

Runtime historique testé pendant la campagne RC16.22.1 : `v1.41-semantic-shell-hardening`. MCB1 a introduit v1.42 ; V2 utilise v1.43 ; le candidat Pilotage Builder courant utilise v1.44, défini dans la section dédiée ci-dessous.

## Routage d’applicabilité

- `multi_system=false` : le run ne peut jamais entrer dans `MECHANICAL_VALIDATION_PASS` du registre multi-systèmes.
- `multi_system=true` : le runtime active lui-même la branche multi-systèmes et son validateur mécanique disponible ; ce bit n’est plus un choix du modèle.
- la combinaison historique `single-system + mechanical_validation=true` est refusée avant création du run.

## Chemin nominal obligatoire

1. Gates sémantiques contigus : `advance-prepared` + `semantic-complete`.
2. Rendu candidat final : `render-commit --render-file ...`. Le runtime dérive policy, contract, component plan/payloads/manifest, exécute les assertions pré-freeze puis ferme Render.
3. Pilotage : l’autorité spécialisée produit uniquement son contenu métier structuré ; `pilotage-commit --business-payload-file ...` dérive tous les bindings mécaniques, exécute `FULL_SHARED_VALIDATOR` et ferme `PILOTAGE_VALIDATED`.
4. Terminal Presentation et Final restent les autorités/contrôles existants.

Les commandes administratives bas niveau Render/Pilotage restent des primitives internes et de forensic, mais leur utilisation directe via CLI est refusée sous `FAST_ENFORCED`.

## Limite épistémique Pilotage

Le receipt de validation prouve que le FULL_SHARED_VALIDATOR a réellement été exécuté sur le contrat, le deck et le rendu exacts. Le runtime n'est toujours pas un oracle du langage naturel et ne crée aucune règle Yu-Gi-Oh absente de SRC/GAME RULES.

Le durcissement MCB réduit cependant la surface d'auto-certification : une fois une clause matérielle normalisée, le modèle ne choisit plus librement ses conséquences de ressources, propriétés, restrictions, sets globaux ou dégâts. Le `unified_cold_audit` redécouvre aussi la projection mécanique attendue sans lire les MCB primaires ; toute divergence bloque le PASS.

Si une clause nécessaire reste absente, ambiguë ou hors surface supportée, l'autorité doit produire `UNRESOLVED` et la chaîne termine **FAIL / NON CERTIFIÉ** — jamais par escalade de modèle.

## Durcissement post-RC16.22.1 — retry, fork et métriques

### Pilotage

Le chemin nominal devient :

`business payload → diagnostic business → authoritative dry-run read-only → classification des issues → réparation du domaine compétent → nouveau dry-run → pilotage-commit seulement si dry-run PASS → confirmation FULL_SHARED_VALIDATOR → PILOTAGE_VALIDATED`.

`pilotage-authoritative-dry-run` et le dry-run intégré à `pilotage-commit` utilisent la même compilation du contrat et la même surface mécanique + `FULL_SHARED_VALIDATOR` que le commit, sans fermer de gate ni muter state/checkpoint. Son receipt lie les hashes exacts deck/rendu/business ; toute modification rend ce PASS inutilisable pour le commit.

Les issues sont routées dans trois domaines :
- `PRESENTATION_RENDER` : retour STRUCTURE/Render, **0 tentative métier** ;
- `PROOF_SCHEMA_ADMIN` : réparation payload/preuve/binding, **0 tentative métier** ;
- `BUSINESS_SEMANTIC_MECHANICAL` : seule catégorie autorisée à consommer le budget métier.

Budget métier : **3 cycles maximum** (`1 initial + 2 corrections same-model`). Les corrections non métier possèdent un garde-fou séparé de 3 cycles consécutifs par domaine/version de deck ; au-delà : `NON_BUSINESS_REPAIR_EXHAUSTED`, jamais maquillé en épuisement métier. Un même fingerprint d'échec rejoué sans changement n'est pas recompté.

Le runtime impose aussi un **proof floor déterministe** : un claim structuré ne peut pas déclarer l'absence totale de preuve lorsqu'il crée lui-même une obligation mécanique minimale. En particulier, `LETHAL + GUARANTEED` exige des `DAMAGE_EVENT` et un `LETHAL_CHECK`; des ressources initiales matérielles annoncées doivent être suivies dans le replay; un scope `COMPLETE_NO_MATERIAL_BINDINGS` est refusé lorsque la surface structurée impose des MCB; un claim dérivé matériel ne peut pas être masqué par `COMPLETE_NO_MATERIAL_CLAIMS`. Le proof floor n'interprète aucun nom de carte et ne remplace ni SRC ni GAME RULES.

### Fork/refactor

`fork-refactor-from-terminal` conserve le parent immuable. Les preuves JSON héritables sont recopiées vers le child avec `run_id` enfant et rebinding déterministe des références de hash déjà remplacées. Si le préfixe n'est pas prouvable frais, le fallback reste un bootstrap complet fail-safe.

Pour la continuité de composants issue d'un refactor, `PRESERVE` peut être auto-matérialisé uniquement lorsque l'identité déterministe du composant (IDs/refs + hash du payload compilé) correspond exactement à l'artefact parent. Une divergence retombe sur le contrôle normal ; elle n'est jamais forcée en preserve.

### Métriques

Les inspections de run exposent notamment : `pilotage_commit_count`, `pilotage_rollback_count`, `pilotage_authoritative_dry_run_count`, `pilotage_authoritative_dry_run_failures`, `pilotage_business_attempt_count`, `pilotage_nonbusiness_repair_count`, `pilotage_nonbusiness_exhausted_count`, `pilotage_proof_floor_failure_count`, `semantic_unresolved_count`, `wide_fallback_count`, `grouped_evidence_compile_count` et `automatic_rebind_count`, en plus de la durée runtime locale existante.


# Durcissement Pilotage Builder — LEGACY / compatibilité post-MCB1-V2

Runtime de développement correspondant : `v1.44-pilotage-business-builder`.

Ce durcissement ne crée aucune autorité métier et ne modifie ni MCB1 ni le proof floor. Il retire seulement au modèle l'authoring administratif encore présent dans `pilotage_business`.

## Squelette Pilotage dérivé

Après `FINAL_RENDER_PREPARED`, le chemin nominal doit exécuter `pilotage-business-skeleton`. Le Deterministic Shell dérive du rendu exact les éléments qu'il connaît déjà : Axes, `line_id`, `starter_id`, `replay_id`, ancres/tokens de rendu et relations Axe → Starter → Ligne. Ces éléments sont `SHELL_OWNED`.

Le modèle ne doit pas recréer, supprimer ou renommer ces identités. Il fournit uniquement un patch métier par IDs stables. `pilotage-business-merge` applique ce patch sur le squelette ou, lors d'une réparation, sur le précédent payload métier valide, tout en vérifiant que l'identité shell-owned est inchangée.

Chemin nominal :

`skeleton shell-owned → patch métier Instant → merge local non destructif → authoritative dry-run → correction locale éventuelle → nouveau merge → dry-run PASS → pilotage-commit`.

Règle historique de la route Builder : un payload Builder remis au dry-run sans reçu de merge frais est refusé. **Cette exigence ne s’applique plus à la route nominale Semantic Compiler RC16.23**, qui possède sa propre provenance déterministe.

## Locality contract

Une correction ne peut modifier que les champs correspondant aux issues qu'elle répare. Une tentative de remplacer `lines[]`, de modifier `line_id`, `starter_id`, `replay_id`, les bindings Axe/rendu, les champs compilés, ou tout autre champ shell-owned produit `PILOTAGE_REPAIR_SCOPE_VIOLATION`.

Lors d'une réparation, le merge part du précédent payload métier afin de préserver les preuves déjà valides. Une correction locale ne doit jamais vider par inadvertance les autres lignes, starters ou preuves déjà fermés.

## Taxonomie fermée des codes observés

Les codes connus suivants ne peuvent plus retomber dans `UNRESOLVED_DOMAIN` :

- `PILOTAGE_LINES_REQUIRED`, `PILOTAGE_STRUCTURAL_STARTERS_REQUIRED` → `PROOF_SCHEMA_ADMIN` ;
- `PILOTAGE_LINE_NOT_RENDERED`, `PILOTAGE_STARTER_DISPLAY_NOT_RENDERED`, `STRUCTURAL_STARTER_NOT_RENDERED` → `PRESENTATION_RENDER` ;
- `ACTION_LEGALITY_EVIDENCE_MISSING`, `EXECUTION_RESOURCES_MISSING`, `UNIFIED_COLD_LEGALITY_ACTION_COVERAGE_MISMATCH` → `BUSINESS_SEMANTIC_MECHANICAL`.

`UNRESOLVED_DOMAIN` reste réservé aux codes réellement inconnus et demeure `FAIL_CLOSED`.

**Règle courte : le shell construit la structure ; le modèle apporte le jugement métier ; le merge protège la structure ; le dry-run décide si la preuve est transmissible au commit.**

---

# Addendum d'exécution RC16.23 — Architectural Hardening

RC16.23 conserve une surface de Sources **plate** et le runtime principal unique. Aucun arbre de modules n'est requis.

## Pilotage nominal

Après fermeture fraîche de Style → Axes et du rendu :

1. le Builder lit l'inventaire structurel de Style → Axes ;
2. il vérifie sa survie dans le rendu ;
3. il construit uniquement le scaffold technique, avec les décisions métier encore `UNSET` / non évaluées ;
4. le modèle remplit les slots métier autorisés ;
5. `pilotage-business-merge` lie le payload au deck, rendu et inventaire exacts ;
6. le dry-run retourne un diagnostic auto-descriptif et agrégé lorsque les défauts sont indépendants ; chaque validator émet lui-même `owner_authority`, `repair_domain`, `budget_class`, `blocking` et `repairable`, le routeur ne les déduit jamais du nom du code ;
7. une réparation utilise obligatoirement le payload parent exact et le receipt exact du FAIL ;
8. le commit n'est autorisé qu'après dry-run PASS sur les mêmes hashes.

Les sorties Pilotage autoritatives doivent rester dans le répertoire plat du run. Un chemin extérieur est refusé.

## Fail-closed

Un domaine inconnu produit `BLOCKED_FATAL`. Cet état interdit les mutations ordinaires. La commande `recover-fatal` constitue une transition explicite et auditée ; elle exige un `run_id`, une autorité compétente et une raison. Elle n'hérite pas comme fraîches les sorties Pilotage produites après le diagnostic bloquant.

## Concurrence

Les commandes mutantes sont sérialisées par run. Le journal append-only possède son propre verrou de processus. Les écritures de fichiers autoritatifs utilisent remplacement atomique et ne réécrivent pas un artefact autoritatif existant avec un contenu différent. Après reprise, `state`, checkpoint et événement `CHECKPOINT_WRITTEN` doivent encore porter le même hash d'état ; une coupure entre ces écritures est détectée et ferme l'exécution au lieu d'être masquée.

## Préconditions amont

Un prérequis d'orchestration connu, notamment un impact combo exigé après modification matérielle, bloque avant construction du scaffold Pilotage au lieu de consommer un budget de correction métier tardivement.

## Tests RC16.23

Aucun statut de développement PASS ne peut être émis uniquement sur la base du code modifié. Les tests unitaires, contrats, intégration, non-régression, KILL/mutation, concurrence, crash/recovery, fuzz borné, E2E CLI, Red-Team et packaging applicables doivent être réellement exécutés ; les Black-Box Instant restent une validation séparée après fermeture déterministe.

## Fermeture RC16.23 — budgets de rendu et émission terminale

Le budget `PRESENTATION_RENDER` est rattaché à la **lignée de rendu courante** : une correction qui produit `render-vN+1` n'hérite pas de la dette de présentation du rendu supplanté. Ce reset ne s'applique pas au budget métier, qui reste borné selon ses propres règles.

Après `authorize`, le runtime matérialise le texte terminal dans un artefact plat **content-addressed** lié au hash du rendu autorisé. L'alias ergonomique `terminal_payload.md` n'est pas une preuve autoritative.

La réponse terminale doit être lue via `terminal-output`, qui recalcule le hash de l'artefact autorisé immédiatement avant émission. Une modification extérieure entre autorisation et lecture produit `TERMINAL_PAYLOAD_STALE_AFTER_AUTHORIZE` et bloque la sortie.

## Addendum RC16.23 Black-Box Corrective — projection Render et barrière de sortie

La compatibilité de projection Render est distincte de l'intégrité physique des Sources. Le manifest et l'inventaire du run lient toujours le fichier exact par hash ; le runtime vérifie séparément un **contrat de projection déterministe** limité aux clauses de STRUCTURE qu'il consomme réellement. Une modification hors contrat ne doit pas rendre la projection incompatible ; une modification du contrat vers une forme non supportée reste fail-closed avec `RENDER_PROJECTION_SOURCE_VERSION_UNSUPPORTED`.

La commande read-only `output-policy` constitue la barrière d'émission conversationnelle. Elle renvoie `FINAL_ARTIFACT` uniquement si le run est `COMPLETED`, `stop_output_allowed=true`, `FINAL_VALIDATION_PASS` est présent et le payload terminal content-addressed est lié. Dans tous les autres cas — notamment `IN_PROGRESS`, `BLOCKED_FATAL` ou après `FASTPATH_LOW_LEVEL_BLOCKED` — le mode est `STATUS_ONLY` : aucune decklist finale, aucun Axe final et aucun composant terminal ne peuvent être reconstruits hors runtime.

`terminal-output` reste l'unique lecture du texte final autorisé. Le plan terminal et ses composants visuels restent liés aux hashes exacts issus de `VISUAL_ASSETS_BOUND` et du rendu validé.

---
## RC16.23 — Route nominale Semantic Compiler

Après `FINAL_RENDER_PREPARED`, la route nominale de Pilotage est désormais :

`pilotage-semantic-template → saisie métier minimale → pilotage-semantic-compile → pilotage-authoritative-dry-run → pilotage-commit`.

Le template est produit depuis l'inventaire Style→Axes. Le modèle complète uniquement les **actions Yu-Gi-Oh**, le **claim**, l'**outcome lisible** et, lorsqu'ils sont réellement nécessaires, les rulings/choix sémantiques matériels. Il ne doit pas ajouter d'IDs, hashes, bindings, resource ledgers, statuts MCB, cold audits, matrices de couverture ou champs de fraîcheur.

`pilotage-business-skeleton` / `pilotage-business-merge` restent disponibles pour compatibilité, tests et reprise d'anciens artefacts, mais ne constituent plus la route nominale d'une nouvelle construction lorsque le Semantic Compiler est disponible.

`pilotage-semantic-compile` matérialise obligatoirement un reçu de provenance content-addressed lié au run, deck snapshot, render courant, inventaire Style→Axes, saisie sémantique, payload business compilé et contrat/version du compilateur. Le dry-run vérifie une provenance fraîche et accepte soit **Semantic Compiler** (nominal), soit **Builder/Merge legacy** (compatibilité). Il ne peut plus exiger Builder/Merge lorsqu'une provenance Semantic Compiler exacte existe.

Le Render Contract gelé par `render-commit` est canonique pour le rendu courant. Les étapes aval relisent et vérifient ce contrat exact ; elles ne doivent pas reconstruire une variante depuis des champs de continuité mutables. `component_continuity` d'un rendu antérieur ne peut pas contaminer le contrat courant après `presentation-change`.

La commande read-only `continuation-policy` matérialise la règle **NO EARLY HANDOFF**. Ses sorties sont : `CONTINUE_NOMINAL`, `AUTO_RECOVERABLE`, `BUSINESS_REPAIRABLE`, `USER_REQUIRED`, `FATAL`, ou état terminal. Les trois premières ont `handoff_allowed=false` : l'orchestrateur doit continuer dans le même tour, dans les budgets existants. `USER_REQUIRED` et `FATAL` autorisent un handoff explicite. Un FAIL local, rollback, STALE ou défaut `ADMIN_DERIVABLE` n'est jamais terminal par lui-même.

Une information déjà produite par une autorité ne doit jamais être redemandée au modèle pour simple recopie. Une absence `ADMIN_DERIVABLE` est un défaut de compilation/runtime ; elle ne consomme pas un budget de correction métier et ne doit pas être réparée manuellement par le modèle.

Pour le rendu, lorsqu'un payload de présentation sémantique est utilisé, `render-semantic-compile` matérialise la cardinalité/placement des quotes et le plan des composants visuels ; STRUCTURE reste seule autorité sur leur applicabilité et leur contenu.

## Addendum RC16.23.3 — Black-Box Hardening

`handoff-check` est la barrière dure de fin de tour : `CONTINUE_REQUIRED` impose la poursuite du run. Le runtime applique un **Secretariat Freeze** : toute donnée dérivable (IDs, hashes, bindings, statuts, receipts, groupage decklist, émission composants, compteurs) reste compiler/runtime-owned ; une nouvelle entrée modèle exige un jugement non dérivable.

Le Render Compiler injecte des anchors déterministes pour les composants applicables. `compile-terminal-presentation` ne marque `EMITTED` que si l'anchor exact survit dans le rendu courant ; `terminal-presentation-check` refuse `EXISTS` sans émission.

Si la validation mécanique du registre est applicable, `mechanical-proof-check` exécute réellement le validateur, écrit puis vérifie le receipt et persiste les hashes exacts.

Le Black-Box agrège `TERMINAL_PASS`, `CONTINUITY_PASS`, `SEMANTIC_PASS`, `PRESENTATION_PASS`; `FULL_PASS` exige 4/4 et `COMPLETED` seul ne suffit pas.

## Addendum RC16.23.4 — Campaign / provenance / trace compilation

- **Run ≠ campaign.** Après les attempts d’une demande, exécuter `blackbox-campaign --scope-dir <scope>`. Un dernier run 4D `FULL_PASS` après des attempts `ABORTED/FAILED` donne `RECOVERED_NOT_CLEAN`, jamais `CAMPAIGN_PASS`. `CLEAN_PASS` exige une seule tentative propre liée à la demande exacte et la preuve pré-bootstrap.
- **Pré-bootstrap.** `prebootstrap-handoff-check` refuse le handoff tant que `dispatch-run` n’a pas enregistré un attempt. Cette barrière couvre le trou conversationnel antérieur à l’existence d’un run.
- **Types de cartes.** Le groupage Monstres/Magies/Pièges n’utilise plus `NARRATIVE_CONFORMANCE`. Il exige `bind-card-metadata` sur le snapshot exact avec provenance autoritative/explicitement vérifiée. Sans binding frais et complet, le renderer affiche un Main Deck plat plutôt que d’inventer des types.
- **Applicabilité dérivable.** Lorsque la capacité image est connue, le runtime compile l’applicabilité du carrousel principal et du mini-carrousel signature depuis les faits structurés applicables ; un booléen contradictoire fourni en amont ne fait pas autorité.
- **Lethal visible.** Chaque `DAMAGE` d’une ligne `LETHAL` doit être rattaché au contributeur explicite ou mécaniquement dérivé et ce contributeur doit rester identifiable dans l’étape rendue.
- **Trace utilisateur.** Utiliser `compile-user-trace` et n’afficher que les checkpoints issus du journal/état matériel courant. `Validation finale`, `Reçu : vérifié` et `STOP OUTPUT : PASS` ne peuvent pas être synthétisés par prose.
- **Black-Box externe.** Les KILL déterministes, y compris `Convulsion of Nature + Reversal Quiz`, ne remplacent pas le replay Black-Box externe frais demandé avant promotion.

## Addendum RC16.23.5 — Canonical Semantic Projection / Total Recovery / Final Controlled Emission

### Projection sémantique canonique

Une information métier non dérivable est déclarée une seule fois. Pour un outcome conditionnel, la saisie sémantique porte les conditions matérielles ; le compiler produit les champs de représentation et de preuve (`conditions`, `condition_render_tokens`, tokens de steps/outcome et bindings correspondants). Une condition qui ne peut pas être reliée à une représentation visible matérielle reste fail-closed.

Le compiler peut choisir comme `render_token` d'une étape une ligne visible contenant des termes sémantiques matériels (acteur/carte/cible/matériau) lorsque le texte d'action littéral n'existe pas dans le rendu. Les termes trop courts ne constituent pas une preuve suffisante de correspondance.

### Dependency rebinding

Lorsqu'une autorité amont change de manière explicite et autorisée, les projections dépendantes calculables sont invalidées/recompilées. En particulier, un `FUNCTIONAL_INTENT` canoniquement rattaché à une ancienne Direction peut être rebound par le runtime au contrat Direction courant ; une autorité métier incorrecte n'est jamais corrigée silencieusement.

### Total recoverability

`continuation-policy` enrichit toute sortie `AUTO_RECOVERABLE` avec `repair_routes` et `legal_repair_transition_count >= 1`. Les routes déterministes incluent notamment recompilation depuis la sémantique canonique, reconstruction de bundles de preuve et recompilation des refs de composants. Un état déclaré recoverable mais sans transition sûre est reclassifié fail-closed.

### Continuité typée

Le Black-Box distingue `USER_REQUIRED_RESUME`, `NOMINAL_RESUME`, `RECOVERY_RESUME` et `UNWANTED_HANDOFF`. Une reprise issue d'une résolution utilisateur réellement requise n'échoue pas la dimension Continuity à elle seule. Une reprise de recovery/interruption ou un handoff non requis empêche un clean pass.

### Visual refs et Final Validation bundle

Lorsque les assets visuels sont déjà liés et que l'applicabilité est déterminable, les refs de composants sont dérivées du binding autoritatif, dédupliquées et bornées ; les refs libres contradictoires ne font pas autorité.

Pour `FINAL_VALIDATION_PASS` / `authorize`, le runtime peut assembler les chemins exacts `render`, `render_manifest`, `render_contract`, plan et receipt de présentation déjà courants. L'absence d'un jugement métier ne peut pas être masquée, mais une donnée administrative dérivable n'est pas redemandée au modèle.

### Final controlled emission

`terminal-output` matérialise `final_emission.receipt.json` avant l'émission. Ce receipt lie :
- le payload terminal content-addressed exact ;
- son SHA-256 ;
- une signature structurelle du rendu contrôlé, incluant les groupages decklist lorsqu'ils sont présents ;
- le run et le render autorisés.

La vérification des groupes accepte les formes de quantité supportées par le renderer (dont `3x` et `3×`) et refuse un heading dont le total déclaré ne correspond pas aux cartes rendues dans ce groupe. Toute modification ultérieure du payload rend le receipt stale.

Le Black-Box 4D utilise le schéma `ygo-blackbox-4d-v2`; `PRESENTATION_PASS` exige à la fois la Terminal Presentation proof et une Final Controlled Emission proof fraîche. Cette preuve couvre la dernière structure encore contrôlée par le runtime ; elle ne prétend pas certifier les pixels ou transformations d'un frontend externe après émission.

### Quiet execution

Le journal append-only reste détaillé. La conversation, elle, ne doit pas refléter chaque retry/rebind/refresh interne. `compile-user-trace` et les checkpoints réellement utiles constituent la surface de statut ; aucune réparation interne ne justifie un handoff si la policy reste `CONTINUE_NOMINAL` ou `AUTO_RECOVERABLE`.


---

## RC16.23.6 — False-Pass Closure

### Environment Card-Pool Binding

Après `DECK_DRAFT_CREATED` et avant `NARRATIVE_CONFORMANCE_CLOSED`, exécuter `bind-card-pool`. Par défaut, le runtime utilise automatiquement `LINK_EVOLUTION_2020_CARD_POOL.json`, snapshot complet packagé et hashé du pool Link Evolution 2020 ; le modèle ne fournit ni booléens `available=true` ni liste ad hoc par deck. Un `--pool-file` explicite reste réservé aux tests/audits et doit satisfaire le même fingerprint complet. L'existence TCG globale ne vaut jamais appartenance au pool Link Evolution 2020. Carte inconnue/absente, mauvais environnement, catalogue incomplet ou fingerprint différent = fail-closed.

### Exact Summon-Material Binding

Après compilation de l'entrée sémantique Pilotage et avant le dry-run autoritatif, si une ligne contient `SYNCHRO_SUMMON` ou `FUSION_SUMMON`, matérialiser la règle de matériaux et les propriétés des matériaux depuis une source autoritative/projet vérifiée, puis exécuter `bind-summon-rules` sur **le fichier sémantique exact**. Le binding est lié au SHA sémantique ; toute modification le rend STALE. Le dry-run refuse niveau/compte corrects si un matériel nommé, un rôle Tuner/non-Tuner, une contrainte ou une substitution de nom applicable n'est pas satisfaite. Une règle inconnue bloque : le runtime n'invente jamais le texte d'une carte.

### USER_REQUIRED Same-Run

Un run `WAITING_USER_INPUT` ne peut pas être aborté pour une réparation interne. Après résolution utilisateur, utiliser la route de résolution/reprise du même run ; seuls `USER_REQUESTED_ABORT` ou `USER_REQUESTED_FRESH` autorisent l'abandon explicite. Direction et dépendances dérivées sont invalidées/recompilées sans créer silencieusement un run de remplacement.

### Controlled Component Emission vs Host Visibility

Un marker `YGO_COMPONENT_EMIT` est seulement un ancrage interne. Un composant requis est localement `INCLUDED_IN_CONTROLLED_EMISSION` uniquement si le token riche compiler-owned correspondant est attaché au bon ancrage dans le payload terminal. La visibilité du client ChatGPT reste distincte : sans preuve hôte liée au payload/final-emission exact, le statut est `HOST_VISIBLE_UNVERIFIED`. `blackbox-4d` ne peut pas produire `PRESENTATION_PASS/FULL_PASS` pour un composant requis tant que sa visibilité hôte n'est pas confirmée par preuve Black-Box/outil/utilisateur autorisée.

## RC16.23.7 — Differential false-pass hardening

### Banlist legality receipt

Toute validation d’un `deck-vN.snapshot.json` compile aussi la légalité quantitative depuis `BANLIST_LINK_EVOLUTION_2020.md`. Le runtime contrôle Main/Extra/Side, agrège les copies d’un même nom et applique `0/1/2/3` selon Forbidden/Limited/Semi-Limited/unrestricted. Un pool membership PASS ne vaut jamais banlist PASS. Le receipt `banlist_legality.receipt.json` est lié au snapshot et à la source de banlist exacts. Un mode Forbidden/solo fun doit être explicitement déclaré ; il ne peut pas être déduit pour sauver une liste.

### Effective-state summon materials

`bind-summon-rules` peut transporter des `material_property_modifiers` autoritatifs. Lors du contrôle d’une Fusion/Synchro, le runtime calcule niveau, rôle Tuner et nom effectifs au moment exact où la carte est utilisée comme matériel, puis applique le contrat du boss. Les valeurs imprimées restent persistées dans la preuve mais ne remplacent pas un modifier applicable. Modifier inconnu, mal formé ou sans provenance = fail-closed.

### Classification integrity

`VALIDATION_CANONIQUE_REMIXE` reste seule autorité de classification. Son artefact expose `canonical_identity_structural` et `identity_structure_basis`. Le runtime ne choisit pas Canonique/Remixé/Alternatif ; il refuse seulement une sortie auto-contradictoire (`Alternatif` avec identité canonique déclarée structurelle, ou classification canonique avec identité déclarée non structurelle). Une divergence avec la Direction explicite reste soumise au mécanisme `DIRECTION_CONFLICT_REQUIRES_USER_SELECTION` puis à la reprise du même run.

### Stable semantic-line lineage

Chaque ligne structurelle possède un `semantic_line_id` compiler-owned stable. Le Semantic Compiler projette cet ID vers Pilotage et le rendu sous un anchor `YGO_SEMANTIC_LINE:<id>`. Pilotage vérifie l’anchor exact ; il ne doit pas reconstruire l’identité d’une ligne par ressemblance de texte. Les IDs/hashes/anchors restent runtime-owned.

### Same-run administrative recovery

Un abort motivé par une réparation dérivable (`binding`, metadata, token, rendu, carousel/image refs, projection, formatting, etc.) est refusé avec `DERIVABLE_REPAIR_MUST_CONTINUE_SAME_RUN`. Les seuls abandons restent ceux déjà autorisés par le protocole (demande utilisateur explicite, fatal réel, test contrôlé). Un succès obtenu après création de runs administratifs de remplacement ne devient jamais `CLEAN_PASS`.

### Nominal CLI parity

L’entrypoint CLI doit être physiquement après toutes les définitions/overrides runtime de la version. Import et exécution CLI nominale doivent donc exposer la même implémentation finale, notamment pour les tokens riches de controlled component emission. Une capacité accessible uniquement par import/appel privé ne satisfait pas le produit livré.



## RC16.23.8 — Nominal binding / no wrapper
Une dépendance autoritative dérivable (banlist, manifest, source active) doit être résolue par le runtime depuis les Sources/manifest liés. Le modèle ne doit jamais injecter une constante Python, monkey-patcher le runtime, appeler un wrapper ad hoc ou modifier le process pour contourner un binding manquant. Si la source autoritative manque ou ne correspond pas au manifest : fail-closed explicite.
