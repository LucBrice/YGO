# Validation du pilotage et des lignes — Decks personnages

**Version : V2 / RC16.13 + MCB1 + Proof Floor / Authoritative Dry-Run (candidat post-MCB1 non nommé)**

## Rôle

Autorité spécialisée terminale des lignes destinées au joueur. Elle ne construit pas le deck et ne choisit pas sa stratégie : elle certifie que chaque Axe affiché peut être exécuté, reproduit et compris sans inventer une ressource, une décision, une règle ou un placement essentiel.

Elle produit `pilotage_contract.json` sur le `deck-vN` et le rendu exacts. Le runtime vérifie mécaniquement ce contrat ; **PASS mécanique ≠ PASS métier**.

## Juridiction

Cette autorité décide seule :
- quels starters structurels et variantes doivent être couverts ;
- quelles propriétés, ressources, restrictions, états, relations ou résultats sont matériels ;
- quelles décisions du joueur sont critiques ;
- si une ligne est suffisamment explicite et reproductible.

Elle consomme : deck snapshot, rendu exact, sorties de construction, SRC, GAME RULES et preuves externes nécessaires. Elle ne redéfinit jamais les critères de ces autorités.

---


## Contrat de sortie canonique — RC16.13

Cette autorité possède également la sémantique des statuts de sortie qu'elle produit ; le runtime ne les invente pas. Le `pilotage_contract.json` nominal post-RC16.22.1 utilise `wire_schema = ygo-pilotage-contract-v3` et `execution_contract_version = RC16.2`. Ici `RC16.2` désigne la version du **contrat d’exécution Pilotage**, pas un nom de release candidate du système. Le wire schema décrit la sérialisation ; le contrat d’exécution décrit la Proof-Carrying Line avec MCB1.

Lorsque des Axes sont rendus :
- `axis_coverage_status = PASS` ;
- `starter_exploration_status = COMPLETE` signifie que l'exploration des starters structurels est terminée par cette autorité ;
- `starter_inventory_status = PASS` signifie que l'inventaire déclaré est fermé et couvert selon les critères de cette autorité ;
- `structural_starters` et `lines` sont non vides.

Lorsqu'aucun Axe n'est rendu :
- `axis_coverage_status = NO_RENDERED_AXES | PASS` ;
- `starter_exploration_status = NO_RENDERED_AXES` ;
- `starter_inventory_status = NO_RENDERED_AXES` ;
- `structural_starters = []`.

Pour ces deux champs top-level, `CLOSED` n'est **pas** une valeur wire valide. La fermeture métier reste exprimée par les critères spécialisés ci-dessous ; le wire format transporte cette décision sans la redéfinir.

Le contrat canonique expose explicitement les bindings mécaniques nécessaires au runtime :
- starter : `starter_id`, `display`, `render_token`, `axis_heading`, `line_ids`, `coverage_status` ;
- ligne : `line_id`, `render_axis_heading`, `axis_validation_status`, `starter_ids`, regroupement éventuel des starters, ressources initiales/obligatoires/obtenues/cachées, statuts de portée, `execution_replays` ;
- replay nominal RC16.2 : ressources, steps, budgets, restrictions, catalogues de preuve, claims, états, topologie, SRC, GAME RULES, MCB, backward proof, projection compilée liée par hash et exactement un `unified_cold_audit`.

La forme mécanique exhaustive est exposée par l'instrument `pilotage-schema` et le scaffold `template --kind pilotage`. Ces instruments ne choisissent jamais quels starters, variantes, propriétés ou lignes doivent être certifiés. Un `pilotage-preflight` peut vérifier la forme, les enums, les références internes et les bindings de hash ; **son PASS n'est jamais un PASS métier**.

---

## 1. Couverture du rendu

Chaque Axe numéroté affiché doit posséder **au moins une ligne certifiée** avec `axis_validation_status=PASS`. Un Axe incomplet ne peut pas être compensé par un autre Axe valide.

Un même Axe peut posséder plusieurs lignes certifiées lorsque l'inventaire structurel amont a réellement distingué plusieurs starters, branches ou replays dont le pilotage n'est pas équivalent. Cette pluralité ne constitue pas une double couverture invalide : chaque ligne doit conserver ses propres `starter_ids` / bindings et chaque starter doit être couvert exactement par les lignes déclarées dans l'inventaire amont.

Il reste interdit de dupliquer artificiellement une même ligne pour gonfler la couverture. Deux starters ne doivent être regroupés dans une seule ligne que si leur équivalence de pilotage a été explicitement décidée en amont.

Le contrat lie :
- `render_axis_heading` au titre réellement affiché ;
- `rendered_axis_count` au nombre d’Axes visibles ;
- `axis_coverage_status=PASS` lorsque des Axes existent.

Les routes secondaires non certifiées comme Axes restent dans le Guide de pilotage.

---

## 2. Starters

Réévaluer les starters sur la decklist finale, pas sur une version antérieure.

Pour chaque starter structurel :
- `starter_id`, affichage et Axe associés ;
- lignes couvertes ;
- `coverage_status=PASS`.

Pour chaque ligne :
- ressources initiales déclarées ;
- ressources obligatoires incluses dans ces ressources ;
- ressources obtenues pendant la ligne distinguées des ressources initiales ;
- `hidden_initial_resources=[]` ;
- `starter_contract_status=PASS`.

Un starter générique n’est valide que si toutes les variantes qu’il prétend couvrir sont rejouées ou explicitement branchées. Deux starters ne partagent une ligne que si leur exécution est réellement équivalente et que cette équivalence est déclarée.

### Propriétés du starter

Si Niveau, Type, Attribut, nom, statut Tuner ou toute autre propriété est nécessaire, elle doit être fermée explicitement. Un libellé plus large que ce que la ligne sait réellement exécuter est bloquant.

`starter_property_scope_status = PASS | NO_PROPERTY_SENSITIVE_STARTER`.

---

## 3. Résolution des effets

Pour chaque effet dont la résolution comporte un choix ou un compte matériel, fermer :
- caractère optionnel/obligatoire ;
- `ALL_POSSIBLE`, `UP_TO_N`, `EXACT_N` ou absence de sélection ;
- nombre éligible, limite et nombre réellement résolu ;
- absence de `hidden_choice_assumption`.

Une ligne échoue si elle suppose une liberté que le texte/ruling ne donne pas.

---

## 4. Proof-Carrying Line — représentation canonique

RC16.1 impose une construction unique de la ligne essentielle. Le même paquet porte les preuves utilisées par toutes les validations ; il ne faut pas reconstruire la ligne pour chaque domaine.

Le `pilotage_contract.json` reste l’artefact autoritaire. Pour chaque `execution_replay`, normaliser autour de :

### `line_core`
Conceptuellement : ressources, steps, transitions, budgets, restrictions et outcome. Les structures historiques correspondantes restent celles attendues par le runtime.

### `evidence_core`
- `legality_evidence` ;
- `fact_catalog` ;
- `constraint_catalog` ;
- `semantic_ruling_contracts` ;
- `action_game_rule_profiles` et `game_rule_bindings`.

Une donnée factuelle/normative est définie une fois et réutilisée par ID. Ne pas recopier la même contrainte dans plusieurs sous-contrats si une référence suffit.

### `proof_core`
Les steps, préconditions d’état, relations topologiques, claims, conditions externes, backward requirements et critical decisions référencent les catalogues communs.

---


## 4 bis. Mechanical Consequence Binding et propriété du replay

Pour chaque clause SRC ou binding GAME RULE matériel ayant une conséquence mécanique, Pilotage produit un MCB fermé : source, preuve, step, opérateur, portée et paramètres. Il décide **quelles conséquences sont matériellement exigées**, mais il ne rédige plus librement les transitions dérivables correspondantes.

Dans `pilotage_business.json`, les champs mécaniques dérivables des steps (`requires`, `moves`, `produces`, `property_updates`, `activate_restrictions`, `release_restrictions`) restent vides ou omis pour la surface MCB. Le runtime compile les MCB dans `pilotage_contract.json`, marque les steps `mechanically_compiled=true`, matérialise la projection et son hash, puis le validateur recalcule cette projection avant PASS.

Toute divergence entre projection persistée et recalculée, toute transition concurrente rédigée par le modèle, ou toute conséquence requise hors surface supportée bloque la ligne.

Le modèle reste responsable de la **normalisation sémantique** ; le Deterministic Shell devient responsable de l'**arithmétique de cette normalisation**.

## 5. Replay et conservation des ressources

Chaque ligne essentielle possède au moins un `execution_replay` PASS couvrant les variantes annoncées.

Le replay doit fermer de bout en bout :
- zone et quantité de chaque ressource ;
- coûts et consommations ;
- ressources produites/récupérées ;
- budgets d’action ;
- restrictions activées puis libérées ;
- absence de double dépense ;
- disponibilité réelle d’une copie au moment où elle est utilisée.

Une ressource consommée ne peut réapparaître sans transition explicite. Une carte singleton ne peut satisfaire deux usages simultanés. Une ressource générée n’existe pas avant son producteur.

---

## 6. Action Legality Proof

Chaque step du replay possède un `action_legality_proof`.

Les propriétés/règles utilisées sont sourcées via :
- `CARD_RULE_SOURCE` pour texte/ruling de carte ;
- `GAME_RULE`/`RULEBOOK_SOURCE` pour règle générale ;
- `DECK_SNAPSHOT`, `PILOTAGE_DERIVATION` ou autre origine autorisée lorsque pertinent.

Le `fact_catalog` décrit les faits ; le `constraint_catalog` décrit leurs predicates. Chaque action déclare les contraintes applicables, participants, sorties, restrictions actives et exigences de placement. Une contrainte violée bloque l’action.

Les restrictions persistantes restent actives jusqu’à leur libération explicite et doivent être testées sur les actions ultérieures concernées.

---

## 7. État exact, propriétés, attachments et topologie

Les préconditions se vérifient au snapshot exact `BEFORE:<step>` ou `AFTER:<step>`. Ne jamais mélanger deux instants.

Fermer lorsqu’ils sont matériels :
- propriété dynamique et mise à jour ;
- présence/quantité dans une zone ;
- position ;
- slot libre/occupé ;
- attachment/host, attach/detach/destination ;
- relations spatiales déclarées (`POINTS_TO`, `OCCUPIES`, `RELATED`, `CO_RELATED` ou équivalent contractuel).

Le runtime ne connaît pas la sémantique Yu-Gi-Oh : l’autorité déclare les propriétés, relations et obligations MCB nécessaires ; le runtime vérifie leur état, leur continuité et calcule les conséquences couvertes par ces obligations.

### Checkpoints physiques et rendu

Une ligne `COMPLEX` ne peut pas masquer un placement qui conditionne la suite. Si un placement est critique :
- le choix doit être relié au step correspondant ;
- le placement choisi doit être matérialisé dans le replay ;
- la même décision doit être visible dans le rendu exact.

Si tous les placements légaux préservent la suite, ne pas imposer d’instruction supplémentaire.

---

## 8. Derived Claims et certitude

Tout résultat matériel calculé ou affirmé — compte de zones, ATK, dégâts, nombre de ressources, etc. — doit être relié à un `derived_claim` reproductible depuis l’état et les entrées déclarées.

La certitude d’un outcome est `GUARANTEED`, `CONDITIONAL`, `RANGE` ou `UNKNOWN` selon les dépendances externes réellement fermées.

Une condition adverse/non contrôlée nécessaire au résultat interdit `GUARANTEED`. Les conditions d’un outcome conditionnel doivent survivre dans le rendu joueur.

---

## 9. SRC et GAME RULES

### SRC

Pour chaque effet matériel réellement utilisé, `SEMANTIC_RULING_CONTRACT` fournit uniquement les clauses issues du texte/ruling de cette carte : condition, coût, cible, quantité, provenance, destination, timing, propriété, permission, restriction ou transition lorsque nécessaire.

Chaque clause matérielle référence un fait/une contrainte existant et un `CARD_RULE_SOURCE`. `semantic_status` doit être `CLOSED`; une dépendance essentielle `PARTIAL`/`UNRESOLVED` bloque la ligne.

### GAME RULES

Pour chaque action, sélectionner les profils de règles générales applicables définis par `GAME_RULES_LINK_EVOLUTION_2020`. Les bindings matériels référencent un fait/une contrainte existant et un `RULEBOOK_SOURCE`.

Ne jamais recopier une règle générale dans les SRC.

---

## 10. Backward Proof

La construction primaire est bidirectionnelle : partir du payoff et de ses exigences futures pendant que la ligne forward est construite.

Pour chaque exigence future matérielle :
- `consumer_action_id` ;
- état requis `BEFORE:<consumer>` ;
- predicate déjà défini ;
- origine SRC, GAME RULE ou outcome ;
- actions antérieures pouvant établir ou casser l’exigence.

Si plusieurs choix antérieurs sont légaux mais que certains rendent la continuation impossible, produire une `critical_decision`. Le choix retenu doit appartenir aux options qui préservent la suite et, si le joueur doit le connaître, être rendu explicitement.

Si toutes les options légales sont équivalentes, aucune décision critique artificielle ne doit être créée.

---

## 11. Unified Cold Audit — RC16.1

RC16.1 remplace les multiples relectures froides nominales par **une seule relecture indépendante** de la ligne et de ses preuves.

Chaque `execution_replay` nominal RC16.2 contient exactement un `unified_cold_audit` avec :
- `status=PASS` ;
- `ignored_primary_inventories=true` ;
- `sweep_basis` non vide ;
- inventaire `semantic` ;
- inventaire `game_rules` ;
- `mechanical_projection` avec `status=PASS`, `ignored_primary_bindings=true`, une base de sweep explicite et les MCB redécouverts sans lecture des bindings primaires ;
- inventaire `legality` par action ;
- inventaires `derived`, `state`, `topology`, `certainty`, `backward`.

Cette passe ne consulte pas les inventaires primaires qu’elle audite. Elle peut lire la ligne, les preuves et les règles applicables une seule fois puis produire les huit inventaires.

Le runtime projette ces inventaires vers les validateurs spécialisés historiques et compare **chaque domaine séparément**. Une seule passe cognitive ne fusionne donc aucun critère de PASS.

Contrats RC16 / RC16.1 historiques : les anciens chemins restent acceptés uniquement pour compatibilité/régression. Chemin nominal post-RC16.22.1 : `execution_contract_version=RC16.2`, `unified_cold_audit` unique et projection mécanique froide obligatoire ; ne pas produire une seconde passe froide complète.

---

## 12. Evidence acquisition

Les preuves externes d’une ligne doivent être acquises en une phase groupée puis réutilisées par `evidence_id`.

Après gel du packet de preuves, ne pas relancer une recherche externe pour la même information. Nouvelle acquisition seulement si une preuve indispensable est `UNRESOLVED`, absente, ou rendue `STALE` par un changement matériel.

---


## 12 bis. Authoritative dry-run, proof floor et correction locale same-model

Avant tout `PILOTAGE_COMMIT_STARTED`, le harness doit exécuter un **authoritative dry-run read-only** sur le business payload exact. Cette passe compile le même contrat Pilotage, exécute le même preflight mécanique et le même `FULL_SHARED_VALIDATOR` que le commit. Elle doit lier les hashes deck/rendu/business et ne fermer aucun gate ni muter state/checkpoint.

Le dry-run agrège les défauts indépendants actuellement détectables et persiste pour chaque issue : code, domaine, chemin, IDs de ligne/replay/step/binding/ressource lorsqu'ils existent, attendu et observé lorsque disponible.

Routage obligatoire :
- `PRESENTATION_RENDER` → retour STRUCTURE/Render, sans consommation du budget métier ;
- `PROOF_SCHEMA_ADMIN` → réparation du payload/preuve/binding, sans consommation du budget métier ;
- `BUSINESS_SEMANTIC_MECHANICAL` → seule catégorie qui consomme une tentative métier ;
- `UNRESOLVED_DOMAIN` → FAIL closed.

Budget métier : **3 cycles maximum** (`1 initial + 2 corrections locales`) sous politique `SAME_MODEL_LOCAL_ONLY`. Les réparations non métier sont comptées séparément et bornées à 3 cycles consécutifs par domaine/version de deck. Un même input/fingerprint rejoué sans correction n'est pas recompté.

### Proof floor déterministe

Le runtime ne décide toujours pas de la sémantique Yu-Gi-Oh. Il peut toutefois refuser une absence de preuve qui contredit les claims structurés fournis par l'autorité :
- `victory_claim=LETHAL` + `certainty=GUARANTEED` exige un ledger mécanique contenant au moins `DAMAGE_EVENT` + `LETHAL_CHECK`;
- des ressources initiales matérielles annoncées doivent être suivies par `execution_replay.resources`;
- `COMPLETE_NO_MATERIAL_BINDINGS` est interdit lorsqu'une surface matérielle structurée impose des MCB ;
- un claim dérivé matériel garanti ne peut pas coexister avec `COMPLETE_NO_MATERIAL_CLAIMS` sans preuve correspondante.

Ces contrôles sont des invariants de représentation. Ils ne lisent pas les noms de cartes, n'inventent aucun effet et ne remplacent ni SRC ni GAME RULES.

Un `pilotage-commit` n'est autorisé que si le dry-run courant est `PASS` sur les hashes exacts. Après changement du deck, du rendu ou du business payload, le PASS dry-run est `STALE` et doit être rejoué.

## 13. Refactor matériel et combo impact

Après modification matérielle :
- anciennes validations dépendantes → `STALE` selon le registre/harness ;
- rejouer les lignes touchées sur la nouvelle version ;
- produire `combo_impact.json` lorsque requis ;
- préserver les lignes non touchées seulement si leurs dépendances restent fraîches.

Le rendu post-sortie respecte `DIFF_ONLY` lorsque le harness l’impose. Un backend corrigé sans restitution visible des impacts de pilotage n’est pas suffisant.

---

## 14. Rendu spécialisé

Avant PASS, vérifier sur le rendu exact :
- chaque Axe et starter annoncés sont visibles ;
- conditions d’outcome importantes visibles ;
- restrictions de branche utiles au joueur visibles ;
- placements/décisions critiques visibles au moment pertinent ;
- decklist/direction/visuels exigés par les autorités de structure présents.

Un défaut de présentation retourne à `STRUCTURE_AXES_COMBOS_DECKS_PERSONNAGES`; un défaut fonctionnel retourne à l’autorité de construction compétente.

---

## 15. PASS

`PASS` seulement si, sur le deck et le rendu exacts :
1. tous les Axes numérotés sont couverts ;
2. tous les starters structurels sont couverts ;
3. aucune ressource initiale cachée ;
4. effets et variantes sont fermés ;
5. replay de ressources et budgets cohérent ;
6. légalité de chaque action fermée ;
7. états, propriétés, attachments et topologie matériels fermés ;
8. derived claims et certitude fermés ;
9. SRC et GAME RULES matériels fermés ;
10. backward requirements et critical decisions fermés ;
11. SRC/GAME RULES matériels possèdent leurs MCB fermés lorsque leur conséquence mécanique est matérielle ;
12. la projection mécanique froide concorde exactement avec les MCB primaires ;
13. la projection compilée est fraîche, recalculable et cohérente avec les steps ;
14. toute revendication létale est fermée par le ledger de dégâts ;
15. `unified_cold_audit` concorde domaine par domaine ;
16. les décisions nécessaires survivent dans le rendu ;
17. le proof floor est fermé pour tout claim structuré matériel ;
18. le commit est précédé d’un authoritative dry-run PASS frais sur les hashes exacts.

Sinon : `FAIL` et retour vers l’autorité compétente.

**Formule courte : construire une seule Proof-Carrying Line → acquérir/figer ses preuves → SRC/GAME RULES → MCB → projection froide indépendante → compilation déterministe → replay + ledger → validation Pilotage sur le rendu exact → PASS ou correction locale same-model → sinon FAIL / NON CERTIFIÉ.**

# Extension d'interface — Pilotage Business Payload Builder

Cette extension ne change aucun critère métier de `VALIDATION_PILOTAGE_LIGNES_DECKS_PERSONNAGES`. Elle fixe uniquement l'interface nominale par laquelle le modèle faible transmet sa preuve à l'autorité et au runtime.

## Ownership

Le runtime dérive et protège :

- inventaire des Axes rendus ;
- identités des lignes ;
- identités des starters ;
- identités des replays ;
- liens Axe → Starter → Ligne ;
- tokens/ancres de rendu correspondants ;
- enveloppe mécanique liée au run/deck/rendu.

Le modèle conserve la responsabilité des contenus métier : ressources réellement nécessaires, preuves, faits/contraintes, règles applicables, séquençage, conditions, claims, décisions et MCB métier déjà prévus par MCB1. Le builder n'interprète aucun texte de carte et ne choisit aucune conséquence Yu-Gi-Oh à la place de l'autorité.

## Réparation locale non destructive

Après un dry-run FAIL, le runtime transmet les coordonnées de l'issue et limite le patch aux champs pertinents. Le précédent payload valide sert de base ; le patch ne remplace jamais l'ensemble de `lines[]` ou `structural_starters[]`.

Toute mutation d'un champ shell-owned ou toute écriture hors scope de réparation doit produire `PILOTAGE_REPAIR_SCOPE_VIOLATION` et rester hors budget métier tant qu'il s'agit d'un défaut administratif.

Les défauts de preuve métier connus `ACTION_LEGALITY_EVIDENCE_MISSING`, `EXECUTION_RESOURCES_MISSING` et `UNIFIED_COLD_LEGALITY_ACTION_COVERAGE_MISMATCH` appartiennent au domaine `BUSINESS_SEMANTIC_MECHANICAL`; ils peuvent donc déclencher une correction métier same-model bornée. Les absences de `lines` / `structural_starters` sont des défauts d'interface `PROOF_SCHEMA_ADMIN`, pas des échecs stratégiques.

Le PASS Pilotage reste défini exclusivement par les critères déjà présents dans cette source. Le builder et le merge ne créent jamais de PASS métier.

---

## Addendum RC16.23 — Builder neutre, diagnostic et réparation causale

### Inventaire amont obligatoire

Le Pilotage reçoit l'inventaire structurel matérialisé par `HOOK_STYLE_AXES_CONSTRUCTION_DECKS_PERSONNAGES` sur la version courante. Il compare cet inventaire au rendu exact. Il est interdit de reconstruire la liste des starters / lignes requises uniquement depuis ce même rendu.

### Builder neutre

Le Pilotage Business Builder est un instrument de scaffold technique. Il peut matérialiser IDs, relations, slots, hashes et ancres déjà décidés par les autorités compétentes. Il ne peut jamais préremplir à leur place un `PASS`, une équivalence de starters, une absence de propriété pertinente, ni un statut `COMPLETE_NO_MATERIAL_*` ou équivalent. Un champ métier non encore décidé reste explicitement non évalué.

### Issues auto-descriptives

Chaque issue produite par les contrôles Pilotage doit transporter avec elle son autorité propriétaire, son domaine de réparation, sa classe de budget, son caractère bloquant et sa réparabilité. Le routeur consomme ces métadonnées ; il ne doit pas transformer une erreur inconnue en permission de correction large.

Lorsque plusieurs défauts indépendants sont détectables sur le même payload, le dry-run les retourne ensemble. Lorsqu'un parent indispensable manque, les descendants non évaluables ne doivent pas créer artificiellement une cascade de faux défauts.

### Réparation causale exacte

Toute correction locale doit être rattachée au payload exact ayant produit le FAIL, à l'ensemble exact d'issues et au scope exact autorisé. Une correction ne peut ni repartir d'un parent obsolète, ni effacer silencieusement une preuve hors scope, ni modifier un champ shell-owned. Un patch sans changement utile ou un cycle de payload déjà vu est refusé.

### Fail-closed réel

Une issue sans domaine reconnu ferme le run dans un état bloquant persistant. Aucun nouveau merge, dry-run, commit, Final ou STOP OUTPUT n'est autorisé avant une transition explicite de récupération sous une autorité compétente ou un nouveau run propre.

### Budget non métier par lignée de rendu — RC16.23

Les corrections `PRESENTATION_RENDER` sont comptées sur le rendu exact qui les a déclenchées. Lorsqu'une correction de STRUCTURE produit une nouvelle version de rendu et invalide les artefacts Pilotage dépendants, le nouveau rendu démarre son propre budget non métier de présentation. Cette règle ne remet pas à zéro le budget métier de la decklist et ne transforme aucune correction en retry gratuit.

---
## RC16.23 — Frontière MODEL_OWNED / COMPILER_OWNED

La présente autorité reste seule juge du Pilotage. Le **Semantic Compiler** n'est qu'un instrument de matérialisation.

### MODEL_OWNED
Le modèle/autorité fournit uniquement ce qui exige un jugement : actions, cibles, ordre stratégique, branches, claim, outcome, restrictions/rulings matériels et décisions de conservation.

### COMPILER_OWNED
Le runtime dérive sans nouveau jugement : IDs, bindings, propagation des starters, allocation des copies, participants, resource ledger, BEFORE/AFTER, champs MCB dérivables, projection froide, couverture, hashes et provenance technique.

Une dérivation mécanique issue explicitement d'une action sémantique peut porter la provenance `COMPILER_DERIVATION` et une preuve `PILOTAGE_DERIVATION`. Cette provenance ne constitue jamais un ruling de carte et ne permet pas au compilateur d'inventer une action, une cible, une restriction ou un claim.

Si une information réellement sémantique manque : `COMPILER_NEEDS_SEMANTIC_INPUT` et retour ciblé à l'autorité compétente. Si une information déjà connue/derivable manque : défaut runtime/compiler ; ne pas renvoyer ce secrétariat au modèle.

### Provenance de payload compilé — RC16.23

Le dry-run autoritatif exige une provenance mécanique fraîche du payload business exact, mais **ne prescrit pas un producteur unique**. La route nominale Semantic Compiler satisfait cette exigence avec son reçu de compilation lié au deck, rendu, inventaire, entrée sémantique et payload compilé exacts. Builder/Merge ne reste qu'une provenance legacy de compatibilité. L'absence d'un reçu Builder/Merge ne constitue donc jamais un défaut lorsque le reçu Semantic Compiler exact et frais existe. Une provenance stale, liée à un autre render/deck/payload, reste bloquante.

### Continuité après diagnostic

Une issue `PROOF_SCHEMA_ADMIN` ou `PRESENTATION_RENDER` dérivable relève du runtime/compiler et ne doit pas provoquer un handoff utilisateur. Une issue métier retourne à l'autorité compétente, puis la chaîne reprend dans le même tour lorsque le budget le permet. Seuls un vrai besoin utilisateur, un fatal ou un budget épuisé autorisent l'arrêt conversationnel. Cette règle de routage ne change aucun critère de PASS Pilotage.

**Invariant :** une déclaration métier est saisie une fois ; ses copies techniques sont dérivées. Le validateur continue ensuite à rejeter toute contradiction mécanique, faux lethal, double dépense ou ligne non reproductible.

## Addendum RC16.23.3 — ruling et certitude des claims

Une ligne structurellement complète ne reçoit pas PASS si une interaction essentielle dépend d'un ruling matériel non démontré. Coût/résolution, effet continu, changement de zone, timing, cible ou information de jeu non triviale exigent la preuve/interprétation de l'autorité compétente ou `RULING_EVIDENCE_REQUIRED`; le compiler transporte cette preuve sans l'inventer.

Distinguer `DEMONSTRATED_DAMAGE`, `SCENARIO_LETHAL` et `GUARANTEED_LETHAL`. Une inconnue matérielle déclarée interdit de promouvoir un claim conditionnel en garanti uniquement pour fermer un gate.
