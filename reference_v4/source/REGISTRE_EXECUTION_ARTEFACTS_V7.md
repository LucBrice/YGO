# Registre d’exécution matérialisé — Artefacts de decks personnages

**Version : V7**

## Rôle

Cette source définit uniquement l’**instrument de preuve d’exécution** utilisé par les autorités du projet lorsqu’une décision doit être rattachée à une version concrète d’un artefact.

Elle ne contient **aucun critère métier de deckbuilding**. Elle ne décide ni de la viabilité multi-systèmes, ni de la classification, ni de la progression narrative, ni de la structure d’affichage.

Sa fonction est de rendre vérifiable qu’une autorité spécialisée a réellement travaillé sur **la version exacte** qu’elle prétend avoir validée.

### Juridiction

Le présent registre est l’unique source de vérité sur :

- l’identification d’une version d’artefact ;
- la forme minimale d’un enregistrement d’exécution ;
- la représentation d’un avant/après ;
- la fraîcheur d’un statut par rapport à la dernière version ;
- l’invalidation mécanique d’un statut lorsqu’une version matérielle change ;
- la distinction entre **preuve d’exécution** et **critère métier**.

Les autorités spécialisées restent seules juges de leurs critères. Le registre ne peut jamais déclarer qu’un deck est viable, canonique, cohérent narrativement ou correctement présenté.

---

# 1. Principe central

**Pas de statut sans artefact identifié. Pas de refactor sans version avant et version après. Pas de PASS frais si l’artefact a changé.**

Un statut comme `PASS_REFACTOR` ou `PASS_DIRECT` n’est transmissible que s’il est attaché à un enregistrement structuré correspondant à la version exacte du deck transmise à l’étape suivante.

Le registre empêche ainsi la séquence invalide :

`intention de correction → déclaration de PASS`

et impose une séquence matérialisée :

`artefact v1 → défaut détecté → artefact v2 → delta observé → retest sur v2 → statut attaché à v2`.

---

# 2. Identifiant de version d’artefact

Chaque version structurellement distincte de la decklist reçoit un identifiant interne simple et monotone :

- `deck-v1`
- `deck-v2`
- `deck-v3`

Une nouvelle version est obligatoire dès qu’une modification matérielle touche notamment :

- identité ou nombre de cartes ;
- ratio d’une carte structurelle ;
- Extra Deck nécessaire aux lignes ;
- Axe central ;
- carte d’accès, de conversion, de payoff ou garnet ;
- ressource structurante ;
- relation fonctionnelle entre systèmes.

Les modifications purement éditoriales de présentation n’incrémentent pas la version du deck.

---

# 3. Schéma minimal du registre

Pour chaque autorité qui émet un statut bloquant, conserver intérieurement un enregistrement structuré de cette forme :

```yaml
authority: NOM_AUTORITE
input_artifact: deck-vN
output_artifact: deck-vN_ou_vNplus1
status: STATUT_EMIS
material_change: true|false
```

Lorsqu’un refactor est impliqué, ajouter obligatoirement :

```yaml
before_artifact: deck-vN
after_artifact: deck-vNplus1
defect_targeted: description_courte_observable
delta:
  - changement_observable_1
  - changement_observable_2
retest_artifact: deck-vNplus1
```

Puis les champs propres au statut métier restent fournis par l’autorité spécialisée concernée.

**Le registre ne définit jamais leur valeur correcte.** Il exige seulement qu’elles existent et soient rattachées à la bonne version lorsque cette autorité les requiert.

---

# 4. Snapshot matériel d’une decklist

Pour empêcher qu’une version soit une simple étiquette verbale, chaque `deck-vN` doit correspondre à un snapshot identifiable.

Pour les versions intermédiaires, ce snapshot peut rester compact mais doit permettre de vérifier les deltas concernés.

Pour toute version candidate à un `PASS_DIRECT` ou `PASS_REFACTOR`, la **decklist complète destinée à être transmise puis affichée doit être sérialisée dans un artefact machine-lisible distinct** avant validation mécanique. Ce snapshot terminal contient au minimum :

- `artifact_id` égal à `deck-vN` ;
- Main Deck complet sous forme `nom + quantité` ;
- Extra Deck complet sous forme `nom + quantité` ;
- Side Deck complet s’il existe ;
- totaux calculables à partir de ces listes.

Le registre terminal doit alors contenir au minimum :

```yaml
artifact_snapshot_file: deck-vN.snapshot.json
artifact_snapshot_sha256: empreinte_du_snapshot_exact
```

Le hash ne constitue aucun jugement métier. Il lie simplement le statut au **contenu matériel exact** de la decklist.

**Verrou de rendu :** la decklist affichée doit être rendue à partir de ce snapshot terminal validé. Une reconstitution libre ou une modification structurelle entre le snapshot validé et l’affichage crée un nouvel artefact et rend le PASS ainsi que son reçu `STALE`.

---

# 5. Delta matérialisé

Un delta n’est valide que s’il décrit une différence effectivement présente entre `before_artifact` et `after_artifact`.

Exemples valides :

```text
package Speedroid : 11 → 7 cartes
Double Yoyo : 1 → 0
Horse Stilts : 1 → 0
Speed Recovery : 2 → 1
Normal Summons secondaires structurelles : 2 cartes → 0 carte
```

Exemples invalides :

```text
package optimisé
meilleure cohésion
moins de briques
refactor effectué
```

Ces formulations peuvent accompagner une analyse, mais ne constituent pas un delta matérialisé.

---

# 6. Fraîcheur et invalidation

Un statut spécialisé est **frais** uniquement si :

`status.output_artifact == current_deck_artifact`

et, lorsqu’un snapshot terminal hashé est requis :

`hash(snapshot_courant) == artifact_snapshot_sha256 == hash_snapshot_du_reçu`

Si le deck passe de `deck-v2` à `deck-v3` après un PASS :

- le PASS attaché à `deck-v2` devient immédiatement **STALE** ;
- aucune autorité en aval ne peut le réutiliser ;
- l’autorité métier compétente doit être réexécutée sur `deck-v3` lorsque la modification relève de sa juridiction.

Le registre ne décide pas si cette réexécution donnera PASS ou FAIL.

---

# 7. Preuve structurée d'un contrôle terminal exigé par une autorité

Lorsqu'une autorité métier exige qu'un contrôle terminal soit **réellement tenté** avant son PASS, le registre peut matérialiser cette exécution sans juger son résultat.

Pour le test de compression terminale de `HOOK_ANCRAGE_REFACTOR_MULTI_SYSTEMES`, enregistrer sur la version exacte :

```yaml
terminal_compression_attempt:
  artifact: deck-vN
  candidate_changes:
    - réduction_candidate_1
    - réduction_candidate_2
  protected_function_losses:
    - perte_ou_dégradation_observée_1
  outcome: FERMÉE|COMPRESSION_TROUVÉE
```

Le registre impose seulement les invariants factuels suivants :

- `artifact` correspond à la version qui reçoit le statut ;
- plusieurs `candidate_changes` concrets ont été enregistrés ;
- `protected_function_losses` existe comme sortie de l'autorité métier ;
- un PASS ne peut être structurellement cohérent qu'avec `outcome: FERMÉE`.

Le registre **ne décide jamais** si les pertes décrites suffisent réellement à justifier `FERMEE`, ni si les candidats choisis sont les meilleurs. Cette décision appartient exclusivement au hook métier.

Cette preuve sert à empêcher la séquence invalide :

`test terminal mentionné → FERMEE déclarée`

et impose :

`version exacte → réductions candidates nommées → fonctions protégées examinées → sortie métier enregistrée`.

## 7 bis. Preuve du replay terminal à froid

Lorsque `HOOK_ANCRAGE_REFACTOR_MULTI_SYSTEMES` exige son replay terminal à froid, enregistrer séparément sur le snapshot exact :

```yaml
terminal_compression_replay:
  artifact: deck-vN
  artifact_snapshot_sha256: empreinte_du_snapshot_exact
  ignored_prior_outcome: true
  ignored_prior_candidates: true
  candidate_changes:
    - nouvelle_reduction_candidate_1
    - nouvelle_reduction_candidate_2
  protected_function_losses:
    - perte_ou_degradation_observee_1
  outcome: FERMÉE|COMPRESSION_TROUVÉE
```

Le registre vérifie uniquement que :

- `artifact` correspond à `output_artifact` ;
- `artifact_snapshot_sha256` correspond au snapshot terminal figé ;
- `ignored_prior_outcome` et `ignored_prior_candidates` valent réellement `true` ;
- plusieurs candidats concrets et distincts sont enregistrés ;
- aucun candidat du replay ne recopie textuellement un candidat de `terminal_compression_attempt` ; cette vérification matérialise uniquement le fait que le premier jeu de candidats a bien été écarté, sans juger la qualité des nouveaux ;
- la sortie de l'autorité métier est présente ;
- un PASS n'est structurellement cohérent qu'avec `outcome: FERMÉE`.

Le registre ne décide toujours **pas** si les nouveaux candidats sont les meilleurs ni si la perte fonctionnelle invoquée justifie substantiellement `FERMÉE`. Il prouve seulement qu'une seconde exécution indépendante du même test a eu lieu sur le snapshot exact au lieu de recopier la première conclusion.

**Fraîcheur :** toute modification du snapshot après ce replay rend `terminal_compression_replay` immédiatement `STALE`.

# 8. Verrou spécifique au refactor

Aucun statut présenté comme succès après refactor ne peut être enregistré si l’un des éléments suivants manque :

- `before_artifact` ;
- `after_artifact` ;
- `before_artifact != after_artifact` ;
- `defect_targeted` ;
- au moins un `delta` observable ;
- `retest_artifact == after_artifact` ;
- le statut métier émis par l’autorité spécialisée sur `after_artifact`.

Ce verrou ne juge pas si le delta est suffisant. Cette décision reste exclusivement métier.

---


# 9. Trace chronologique matérialisée — diagnostic d’exécution

Le registre contient désormais une **trace chronologique interne append-only** destinée à localiser le premier point où la chaîne d’exécution s’est rompue. Cette trace n’est pas une chaîne de pensée et ne crée aucun critère métier. Elle enregistre uniquement des événements factuels déjà produits par les autorités ou les instruments.

Le champ minimal est :

```yaml
execution_trace:
  - seq: 1
    event: ARTIFACT_CREATED
    artifact: deck-v1
  - seq: 2
    event: VIABILITY_TEST_COMPLETED
    artifact: deck-v1
    result: COMPRESSION_TROUVÉE
  - seq: 3
    event: REFACTOR_MATERIALIZED
    before_artifact: deck-v1
    after_artifact: deck-v2
  - seq: 4
    event: RETEST_COMPLETED
    artifact: deck-v2
    result: PASS_REFACTOR
  - seq: 5
    event: TERMINAL_COMPRESSION_ATTEMPT_COMPLETED
    artifact: deck-v2
    result: FERMÉE
  - seq: 6
    event: TERMINAL_SNAPSHOT_FROZEN
    artifact: deck-v2
    snapshot_file: deck-v2.snapshot.json
    snapshot_sha256: ...
  - seq: 7
    event: TERMINAL_COMPRESSION_REPLAY_COMPLETED
    artifact: deck-v2
    snapshot_sha256: ...
    result: FERMÉE
```

### Invariants de la trace

- `seq` est strictement croissant, unique et contigu ;
- chaque événement portant sur un artefact nomme explicitement cet artefact ;
- `REFACTOR_MATERIALIZED` doit nommer deux versions différentes ;
- un `RETEST_COMPLETED` après refactor doit viser `after_artifact` ;
- un événement de compression terminale doit viser la version qui recevrait le PASS ;
- `TERMINAL_SNAPSHOT_FROZEN` doit viser `output_artifact` et contenir le même fichier/hash que le registre terminal ;
- `TERMINAL_COMPRESSION_REPLAY_COMPLETED` doit venir **après** le gel du snapshot, viser `output_artifact`, porter le même hash et, pour un PASS, contenir `result: FERMÉE` ;
- aucun événement de succès ne peut précéder l’événement qui matérialise son prérequis ;
- une nouvelle version créée après un événement terminal rend les événements terminaux antérieurs obsolètes pour la version courante.

La trace doit permettre d’identifier le **premier événement absent, hors ordre ou rattaché au mauvais artefact**. Elle ne décide jamais si `COMPRESSION_TROUVÉE`, `FERMÉE`, `PASS_REFACTOR` ou tout autre résultat métier est substantivement correct.

## 9 bis. Trace instrumentale produite par le validateur

Les actions du validateur ne doivent pas être auto-déclarées dans `execution_trace`. Lorsque le validateur est disponible, il écrit lui-même un fichier append-only distinct, par exemple :

```text
execution.instrument.jsonl
```

Chaque ligne est un objet JSON. Le validateur y enregistre au minimum :

- `VALIDATOR_RUN_PASS` après validation réussie du registre + snapshot exacts ;
- `RECEIPT_WRITTEN` lorsque le reçu est matériellement créé ;
- `RECEIPT_VERIFY_PASS` lorsque la vérification mécanique du reçu réussit.

Chaque événement instrumental contient les hashes du registre et du snapshot, `output_artifact`, `status` et un numéro de séquence instrumental.

Une phrase conversationnelle « validateur exécuté » ne peut jamais remplacer ces événements. La validation finale peut ainsi distinguer précisément :

- cycle métier incomplet ;
- snapshot non figé ;
- validateur jamais lancé ;
- reçu créé mais jamais vérifié ;
- instrument exécuté sur un autre registre ou un autre snapshot.

---

# 9. Contrôle déterministe optionnel mais prioritaire lorsqu’un runtime est disponible

Lorsqu’un environnement d’exécution permet de comparer des structures de données ou des fichiers, utiliser un contrôle déterministe pour les invariants suivants :

- présence des champs obligatoires du registre ;
- différence réelle entre `before_artifact` et `after_artifact` ;
- cohérence des identifiants de version ;
- égalité entre `retest_artifact`, `output_artifact` et la version transmise lorsque le protocole l’exige ;
- détection d’un PASS devenu `STALE` après création d’une nouvelle version ;
- calcul des deltas simples de quantité lorsque les snapshots sont structurés ;
- lorsqu'une preuve `terminal_compression_attempt` est requise par l'autorité, présence de cette preuve, rattachement à `output_artifact`, pluralité des candidats enregistrés et cohérence formelle entre un PASS et `outcome: FERMÉE` ;
- lorsqu'un `terminal_compression_replay` est requis, présence de cette seconde preuve sur le snapshot exact, indépendance déclarée vis-à-vis du premier résultat/candidats, pluralité de nouveaux candidats et cohérence formelle entre un PASS et `outcome: FERMÉE`.

Ce contrôle déterministe **ne remplace jamais le jugement métier** de l’autorité spécialisée. Il empêche uniquement l’auto-certification incohérente de faits structurels vérifiables.

---


# 9 ter. Reçu mécanique obligatoire lorsqu’un validateur est disponible

Lorsqu’un validateur déterministe du registre est disponible dans le runtime, son exécution n’est plus une simple recommandation : elle devient une **condition de transmissibilité de tout PASS** relevant d’un protocole qui l’exige.

Le contrôle doit produire un **reçu mécanique distinct du registre**, lié au contenu exact du fichier de registre **et au snapshot terminal réellement validé**. Ce reçu contient au minimum :

```yaml
validator: validate_execution_ledger_vN.py
validator_version: vN
ledger_file: nom_du_registre.json
ledger_sha256: empreinte_du_fichier_exact
artifact_snapshot_file: deck-vN.snapshot.json
artifact_snapshot_sha256: empreinte_du_snapshot_exact
output_artifact: deck-vN
status: PASS_DIRECT|PASS_REFACTOR
result: PASS
```

Le reçu ne crée aucun critère métier. Il prouve seulement qu’un programme déterministe a effectivement lu **ce registre exact** et que ses invariants structurels ont passé.

### Verrous

- Un texte du type `validation mécanique : PASS` sans reçu matériel n’est pas une preuve d’exécution.
- Un reçu dont `ledger_sha256` ne correspond plus au registre courant est **STALE**.
- Un reçu dont `output_artifact` ou `status` diffère du registre courant est invalide.
- Un reçu dont `artifact_snapshot_sha256` ne correspond plus au snapshot terminal courant est **STALE**, même si `deck-vN` n’a pas été renommé.
- Toute modification du registre **ou du snapshot terminal** après validation impose de **réexécuter le validateur** et de produire un nouveau reçu.
- La validation finale peut vérifier le reçu et sa fraîcheur, mais ne doit jamais déduire elle-même qu’un validateur a « probablement » été exécuté.
- **L’existence d’un fichier de reçu ne suffit pas à elle seule.** Lorsque le validateur fournit un mode de vérification du reçu, la validation finale doit l’exécuter réellement sur le registre et le reçu courants ; seul un résultat mécanique réussi dans l’exécution courante autorise la chaîne à considérer le reçu comme vérifié.
- Un hash, un contenu de reçu ou une sortie `PASS` reproduits dans le texte de la réponse ne constituent jamais une exécution de l’instrument.

### Séquence mécanique de référence

Lorsque le validateur fourni par le projet supporte la création puis la vérification du reçu, la séquence instrumentale attendue est :

`snapshot terminal réel + registre réel → validateur → reçu réel lié aux deux hashes → vérification mécanique du reçu sur le registre et le snapshot exacts → transmission`

La seconde exécution ne crée aucun critère métier supplémentaire. Elle empêche uniquement qu’un reçu inventé, obsolète ou appartenant à une autre version soit accepté par déclaration.

**Règle courte : validateur disponible + PASS requis → exécution réelle → reçu hashé → vérification réelle du reçu → seulement ensuite transmission.**

# 10. Visibilité

Le registre complet reste **interne** par défaut.

La trace utilisateur peut afficher seulement des éléments compacts déjà autorisés par `STRUCTURE_REPONSES_DECKS_PERSONNAGES`, par exemple :

`deck-v1 → refactor → deck-v2 → retest → PASS_REFACTOR`

ou :

`package secondaire : 11 → 7 slots`

si cette information aide à comprendre qu’un refactor matériel a réellement eu lieu.

La réponse finale ne contient pas le registre sauf demande explicite d’audit.

---

# 11. Frontière avec les autorités métier

- `HOOK_ANCRAGE_REFACTOR_MULTI_SYSTEMES` décide **quoi tester**, si la correction est suffisante et quel statut métier émettre.
- `VALIDATION_FINALE_DECKS_PERSONNAGES` vérifie que le statut reçu est frais et rattaché à la version exacte ; elle ne recalcule pas les critères du hook.
- `STRUCTURE_REPONSES_DECKS_PERSONNAGES` décide ce qui est visible dans la trace ; elle ne définit pas le registre.
- `STYLE_DECKS_PERSONNAGE_LINK_EVOLUTION` orchestre l’utilisation du registre sans en redéfinir le schéma.

---

## Formule courte

**Versionner l’artefact → enregistrer les événements matériels dans une trace chronologique append-only → matérialiser la decklist terminale dans un snapshot complet → enregistrer toute nouvelle version, delta, retest et tentative terminale sur l’artefact exact → figer le snapshot → exécuter le validateur qui écrit sa propre trace instrumentale → produire puis vérifier le reçu → diagnostiquer tout échec au premier événement absent/contradictoire → transmettre puis afficher uniquement le snapshot validé → laisser les critères métier à leur source spécialisée.**

## RC15 — invalidation STALE matérialisée

Après toute modification matérielle d'un artefact déjà porteur de statuts :

`ancienne version → modification matérielle → statuts dépendants STALE → nouvelle version → retest`.

L'existence de la nouvelle version ne remplace pas l'événement d'invalidation.

Pour un `PASS_REFACTOR`, l'`execution_trace` doit contenir, entre `REFACTOR_MATERIALIZED` et `RETEST_COMPLETED`, un événement :

```yaml
event: DEPENDENT_STATUSES_STALE
artifact: deck-vN
caused_by_artifact: deck-vNplus1
stale_status_ids:
  - statut_dépendant_1
```

Le registre ne décide pas quels statuts doivent être invalidés : cette dépendance vient de l'architecture/autorité compétente. Il vérifie seulement que la sortie d'invalidation existe, vise la bonne transition de versions et précède le retest.

**Règle courte : nouvelle version ≠ preuve de STALE. Le STALE doit exister comme transition matérialisée.**

---

# Addendum RC16.23 — causalité, immutabilité et single-writer

Le registre matérialise désormais également la causalité des corrections Pilotage. Pour une réparation, la chaîne minimale est :

`dry-run FAIL exact → hash du payload parent → hash de l'issue-set → hash du scope → hash du patch → hash du payload enfant`.

Un receipt ancien, un parent obsolète ou un hash divergent ne peut pas être utilisé pour autoriser une nouvelle correction.

## État bloqué

Lorsqu'un contrôle fail-closed ne possède aucun routage reconnu, l'état `BLOCKED_FATAL` est persistant. Les mutations ordinaires sont interdites tant qu'une récupération explicite et journalisée n'a pas été effectuée par l'autorité compétente.

## Artefacts autoritatifs

Les artefacts autoritatifs produits par le runtime sont confinés au run qui les crée et ne doivent pas être réécrits avec un contenu différent. Un alias ergonomique peut rester mutable, mais il ne constitue pas une preuve historique. Toute preuve transmissible est liée à son contenu exact par hash.

## Single-writer

Un run possède un seul writer de mutation à la fois. Les écritures de journal sont sérialisées afin que `seq` reste strictement croissant, unique et contigu, y compris en présence de deux invocations concurrentes. Les écritures critiques utilisent une stratégie atomique : une interruption ne doit pas remplacer un artefact valide par un fichier partiellement écrit. À la reprise, le hash de `harness_state` doit correspondre au `run_state_sha256` du checkpoint et ce checkpoint doit posséder son événement `CHECKPOINT_WRITTEN` correspondant dans le journal ; toute divergence est bloquante.

## Payload terminal content-addressed — RC16.23

L'autorisation terminale crée un payload texte plat dont le nom contient un préfixe de son SHA-256. Le registre/état terminal lie `terminal_payload_file` et `terminal_payload_sha256` à `authorized_render_sha256`.

Une lecture terminale ultérieure doit revérifier cette égalité avant émission. Un alias mutable peut exister pour ergonomie, mais il ne remplace jamais l'artefact content-addressed lié au statut terminal.

---
## RC16.23 — Artefacts dérivés du Semantic Compiler

Les sorties du Semantic Compiler sont des **artefacts dérivés**, jamais des autorités métier. Le registre peut lier leur fichier/hash au payload sémantique parent, au snapshot deck, au rendu et à l'inventaire Style→Axes.

Le runtime possède exclusivement la génération des IDs, hashes, versions, diffs et invalidations `STALE`. Une donnée déjà autoritative n'est jamais re-saisie par le modèle uniquement pour la transporter.

Toute modification du payload sémantique parent, du snapshot deck, de l'inventaire structurel ou du rendu lié invalide les dérivations correspondantes selon les dépendances existantes. Une correction de plomberie ne doit pas être enregistrée comme refactor métier.
