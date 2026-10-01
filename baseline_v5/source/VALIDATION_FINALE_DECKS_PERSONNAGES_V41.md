# Validation finale des decks personnages

**Version : V48 / RC16.14**

## Rôle de cette source

Cette source est un **hook final transversal et bloquant**.

Elle ne remplace ni :

- `STYLE_DECKS_PERSONNAGE_LINK_EVOLUTION` ;
- `VALIDATION_PROGRESSION_NARRATIVE` ;
- `VALIDATION_CANONIQUE_REMIXE` ;
- `STRUCTURE_REPONSES_DECKS_PERSONNAGES`.

Elle intervient **après la construction et juste avant l'affichage de toute decklist de personnage** afin d'empêcher qu'une bonne intention conceptuelle soit conservée malgré une decklist finale qui démontre autre chose.

### Juridiction

Cette source est un **auditeur transversal**, pas une seconde spécification. Elle peut **vérifier, bloquer et demander la réexécution** d’une autorité spécialisée sur l’artefact final, mais elle ne redéfinit jamais elle-même les critères de classification, progression ou présentation.

- classification → `VALIDATION_CANONIQUE_REMIXE` lorsque concerné, sous la taxonomie de STYLE ;
- progression → `VALIDATION_PROGRESSION_NARRATIVE` ;
- présentation globale → `STRUCTURE_REPONSES_DECKS_PERSONNAGES` ;
- présentation spécialisée des Axes / Combos → `STRUCTURE_AXES_COMBOS_DECKS_PERSONNAGES` ;
- pilotage et faisabilité des lignes → `VALIDATION_PILOTAGE_LIGNES_DECKS_PERSONNAGES` ;
- légalité → contexte + banlist ;
- **confiance d’exécution terminale → présente source**, exclusivement comme certificat de complétude de la chaîne après fermeture de tous les contrôles spécialisés.

---

## Principe central

**La réponse finale doit être validée à partir de ce qui a réellement été construit, pas à partir de ce qui était prévu.**

### Mode normal et commande `/fresh`

En génération normale, la présente validation s’exécute comme STOP OUTPUT sur la dernière version exacte produite par le pipeline courant.

Lorsque l’utilisateur déclenche ensuite **`/fresh`**, tous les anciens PASS et anciennes confiances sont ignorés pour ce contre-audit. La présente validation est alors réexécutée à la fin de `FRESH_REPLAY_FINAL_GATE` sur la dernière version exacte produite pendant ce nouveau tour.

`/fresh` ne crée aucun critère supplémentaire : il impose seulement une nouvelle exécution des critères existants.

L'intention initiale, la classification provisoire, le potentiel provisoire et le niveau de développement provisoire peuvent tous être corrigés à ce stade.

Si un contrôle final échoue, ChatGPT ne doit pas défendre le concept initial. Il doit corriger avant affichage.

---


## Binding du rendu compilé RC16.3

La fermeture finale accepte uniquement le bundle provenant d'un `render_contract.json` compilé par le runtime depuis la policy STRUCTURE et les artefacts autoritaires courants. La validation finale ne recalcule pas les totaux ni la direction : elle vérifie que `RENDER_CONTRACT_FROZEN`, `FINAL_RENDER_PREPARED` et les validations terminales référencent le même contrat canonique exact.

Un contrat librement rédigé, un contrat compilé devenu STALE ou une divergence de provenance bloque STOP OUTPUT.

# STOP OUTPUT — contrôle binaire obligatoire

Avant d'afficher la réponse, répondre intérieurement par **OUI / NON** aux onze contrôles suivants.

## 1. Classification finale

**« La classification affichée correspond-elle au `FINAL_CLASSIFICATION_CLOSED` de la version exacte, lui-même lié au `functional_intent.json` gelé avant exploration et au snapshot final ? »**

Une classification finale ne peut pas utiliser un payoff ajouté après coup pour promouvoir un rôle `USER_EXPLICIT` de facilitateur/module en seconde architecture. Une telle divergence est `CONCEPT_DRIFT` et renvoie à la sélection du concept.

Pour une piste Canonique remixé, relancer `VALIDATION_CANONIQUE_REMIXE` sur la liste et les lignes réellement produites.

Si **NON** → renvoyer la construction vers cette autorité pour reclassification ou reconstruction avant affichage.

## 2. Contrôle spécifique du sous-type

Si le deck doit être affiché comme **Canonique remixé — Intégré**, vérifier que le sous-type final est bien celui renvoyé par `VALIDATION_CANONIQUE_REMIXE` après lecture de l’artefact final.

L’audit ne possède pas de définition autonome de Hybride / Intégré. En cas d’ambiguïté ou de doute, **réexécuter le classifier spécialisé** au lieu de trancher localement.

Si **NON** → corriger la classification ou la construction avant affichage.

## 3. Progression narrative finale

**« Le potentiel, le développement et les limites affichés correspondent-ils au résultat obtenu en réexécutant `VALIDATION_PROGRESSION_NARRATIVE` sur la decklist et les lignes finales ? »**

L’audit ne crée pas sa propre doctrine de progression. Il vérifie seulement que le stade final n’a pas été préservé par inertie malgré une construction qui démontre autre chose.

Si **NON** → renvoyer vers la validation narrative pour simplifier la liste ou réévaluer le stade avant affichage.

## 4. Invisibilité des validations + visibilité de la progression

**« La réponse finale respecte-t-elle la séparation back-end / front-end définie par STYLE et STRUCTURE ? »**

Vérifier que les validations techniques restent invisibles par défaut, tandis que la progression narrative visible respecte exactement le format imposé par `STRUCTURE_REPONSES_DECKS_PERSONNAGES`.

Si **NON** → corriger la présentation selon STRUCTURE puis refaire le contrôle.

## 5. Structure de la réponse

**« La réponse respecte-t-elle intégralement le mode, l’ordre, les blocs obligatoires, les règles de densité et les règles de personnalité actuellement définis par `STRUCTURE_REPONSES_DECKS_PERSONNAGES` ? »**

Ne recopier ici aucune version locale de cette structure : la source de vérité est STRUCTURE.

Si **NON** → reformater selon STRUCTURE avant affichage.

## 6. Visuel des cartes emblématiques

**« Le traitement du bloc visuel est-il conforme aux conditions actuellement définies par `STRUCTURE_REPONSES_DECKS_PERSONNAGES` ? »**

Ne pas recopier ici les critères de sélection, le nombre de cartes ou l’emplacement du bloc : **STRUCTURE en est l’unique source de vérité**.

Si **NON** → corriger l’affichage selon STRUCTURE puis refaire le contrôle.

## 7. Validation spécialisée du pilotage et des lignes

**Entrée obligatoire : sortie de `VALIDATION_PILOTAGE_LIGNES_DECKS_PERSONNAGES` sur la version exacte qui va être affichée.**

La validation finale ne réexécute plus localement les critères de faisabilité, reproductibilité, couverture des starters, lisibilité Axe / Starter / Branche / Combo, couverture situationnelle, restrictions de branche ou traitement spécialisé des climax.

Elle vérifie seulement que :

- l’autorité spécialisée a réellement été exécutée après construction des lignes et préparation de leur rendu ;
- son statut vaut `PASS` ;
- ce PASS concerne la version exacte de la decklist et les lignes réellement destinées à l’affichage ;
- aucune modification structurelle ultérieure n’a rendu ce PASS obsolète.

Si le statut est absent, `FAIL` ou obsolète, **STOP OUTPUT reste bloqué** et la réponse retourne vers `VALIDATION_PILOTAGE_LIGNES_DECKS_PERSONNAGES`, qui reroute ensuite vers l’autorité compétente.

---

## 8. Viabilité finale des architectures multi-systèmes

**Entrée obligatoire : statut de sortie de `HOOK_ANCRAGE_REFACTOR_MULTI_SYSTEMES`.**

Si plusieurs systèmes, archétypes, packages ou architectures sont structurels, la validation finale doit recevoir pour la **version exacte** auditée l’un des statuts suivants :

- `PASS_DIRECT` ;
- `PASS_REFACTOR`.

L’absence de statut, `FAIL_ABANDON`, ou un PASS rattaché à une version matériellement différente constitue un **échec bloquant immédiat**. Il est interdit de supposer que le cycle a probablement été exécuté à partir de la seule qualité apparente de la decklist.

L’audit final ne possède aucun protocole local concurrent et **ne doit pas être le premier endroit où un défaut multi-systèmes est découvert**. La construction doit avoir déjà exécuté l’ancrage, identifié la relation fonctionnelle entre systèmes, appliqué le test adapté défini par le hook spécialisé et, si nécessaire, le refactor invisible avant d’arriver ici.

Vérifier seulement que :

- un **registre d’exécution matérialisé** conforme à `REGISTRE_EXECUTION_ARTEFACTS` existe pour l’artefact courant ;
- le statut de sortie formel existe ;
- il vaut `PASS_DIRECT` ou `PASS_REFACTOR` ;
- le PASS est accompagné du **paquet de preuve compact** émis par le hook spécialisé pour cette version exacte : relation finale, test appliqué, statut de refactor matérialisé, compression terminale fermée, **tentative terminale matérialisée**, **replay terminal à froid matérialisé sur le snapshot figé**, statut de reroutage après refactor et confirmation de version exacte ; l’audit final vérifie uniquement sa présence, sa cohérence formelle et sa fraîcheur, sans recalculer aucun de ces critères ;
- si la relation finale a changé après refactor, le paquet indique bien que le **reroutage a été effectué** avant le retest qui a produit le PASS ;
- ce statut a été émis **après fermeture complète du cycle du hook spécialisé**, et non pendant une simple phase de relation crédible, de test en cours ou avant son contrôle terminal du coût d'intégration ;
- si le statut est `PASS_REFACTOR`, le paquet indique **Refactor matérialisé = OUI** avec un delta compact avant/après portant sur le défaut corrigé ; l’audit ne décide pas si ce delta est « assez grand », il vérifie seulement que le hook spécialisé a bien produit une nouvelle version concrète et attaché sa propre matérialisation au PASS ;
- si le statut est `PASS_REFACTOR`, il a été émis **après cette matérialisation**, après la dernière reconstruction, après éventuel reroutage de la relation fonctionnelle, après le retest complet adapté et après le **test de compression terminal** de cette version exacte ;
- ce PASS constitue le **dernier événement structurel de construction** avant les validations finales ;
- la decklist finale correspond bien à la version exacte qui a obtenu ce PASS ;
- un **snapshot terminal complet** de cette decklist existe et son `artifact_id` correspond à `output_artifact` ;
- le hash de ce snapshot correspond à `artifact_snapshot_sha256` dans le registre ;
- `output_artifact` du registre correspond à la version courante de la decklist ;
- pour `PASS_REFACTOR`, le registre contient réellement `before_artifact != after_artifact`, un delta observable et `retest_artifact == after_artifact` ;
- lorsqu’un validateur déterministe du registre est disponible, **son exécution réelle est obligatoire** avant d’accepter la fraîcheur du statut ; la validation finale exige le reçu mécanique défini par `REGISTRE_EXECUTION_ARTEFACTS`, vérifie que son `ledger_sha256` correspond au registre courant, que son `artifact_snapshot_sha256` correspond au snapshot terminal courant et que `output_artifact` + `status` correspondent exactement au PASS reçu ; elle ne peut jamais remplacer ce reçu par une mention textuelle « validation mécanique : PASS » ;
- la `execution_trace` du registre existe, est monotone et rattache chaque étape réellement requise à la bonne version ; pour un `PASS_REFACTOR`, elle montre notamment le test initial, la matérialisation du refactor, le retest sur `after_artifact`, la tentative terminale et le gel du snapshot terminal dans cet ordre ;
- la trace instrumentale du validateur contient des événements mécaniques concordants `VALIDATOR_RUN_PASS`, `RECEIPT_WRITTEN` et `RECEIPT_VERIFY_PASS` sur les mêmes hashes et la même version ;
- lorsque ce validateur possède un mode de vérification du reçu, **la validation finale doit l’exécuter réellement elle-même sur le registre, le snapshot terminal et le reçu exacts avant d’attribuer une confiance ÉLEVÉE** ; la simple lecture, citation ou existence supposée du reçu est insuffisante ;
- la réussite de cette vérification doit provenir d’un résultat d’exécution mécanique courant ; un `PASS`, un hash ou un contenu de reçu écrits par le modèle ne constituent pas cette preuve ;
- le validateur doit notamment confirmer, lorsque le hook multi-systèmes l'exige, que la `terminal_compression_attempt` existe sur `output_artifact`, contient plusieurs candidats concrets et possède une sortie formellement compatible avec le PASS ;
- il doit également confirmer la présence d'un `terminal_compression_replay` distinct, exécuté **après gel du snapshot**, rattaché au même hash, marqué comme ignorant le premier résultat et ses candidats, et formellement compatible avec le PASS ; la validation finale ne juge pas la pertinence métier de ses candidats ;
- aucune modification matérielle ultérieure des cartes d'accès, de conversion, de payoff, des garnets / cartes conditionnelles, des Axes centraux, ressources structurantes ou de l'Extra Deck nécessaire aux lignes n’a invalidé ce PASS ;
- aucune modification ultérieure n’a réintroduit le défaut que le test adapté avait corrigé : briques, inaccessibilité du module, conflits de ressources, dépendance à des mains idéales, rupture de convergence, disparition de l’ancrage ou autre échec relevant du hook spécialisé.

### Diagnostic du premier point de rupture

Avant de conclure qu’une chaîne est simplement « incomplète », la validation finale doit identifier le **premier événement matériel requis qui manque, est hors ordre ou vise un autre artefact**. Elle ne doit pas inventer la cause.

Exemples de diagnostic factuel :

- `COMPRESSION_TROUVÉE` puis absence de `REFACTOR_MATERIALIZED` → refactor non matérialisé ;
- `REFACTOR_MATERIALIZED deck-v1→deck-v2` puis retest sur `deck-v1` → retest sur mauvaise version ;
- absence de `TERMINAL_COMPRESSION_ATTEMPT_COMPLETED` avant snapshot/PASS → première fermeture terminale non matérialisée ;
- `TERMINAL_SNAPSHOT_FROZEN` sans `TERMINAL_COMPRESSION_REPLAY_COMPLETED` → fermeture non challengée à froid avant transmission ;
- `TERMINAL_COMPRESSION_REPLAY_COMPLETED` avec `COMPRESSION_TROUVÉE` puis PASS → PASS invalide, retour obligatoire au hook spécialisé ;
- replay rattaché à un autre hash de snapshot → replay `STALE` / mauvaise version ;
- absence de `VALIDATOR_RUN_PASS` → validateur non exécuté ;
- `RECEIPT_WRITTEN` sans `RECEIPT_VERIFY_PASS` → reçu non vérifié ;
- hashes de la trace instrumentale différents du snapshot/registre courants → instrument exécuté sur un autre artefact ;
- snapshot hashé correct mais contenu destiné à l’affichage différent → rupture entre validation et rendu.

Ce diagnostic reste structurel. Il ne réévalue aucun critère métier et ne transforme pas une hypothèse en fait.

**Verrou de fraîcheur du PASS :** si la validation finale ne peut pas établir par le registre que le PASS multi-systèmes est attaché à la version courante et postérieur à la dernière modification structurelle de la liste, elle ne doit pas l'accepter par inertie. Elle renvoie la version courante vers `HOOK_ANCRAGE_REFACTOR_MULTI_SYSTEMES`, sans recréer localement ses critères.

**Verrou de preuve d’exécution :** lorsqu’un validateur est disponible, l’absence de reçu mécanique frais, un hash différent, un reçu attaché à une autre version, l’absence d’une **vérification mécanique réellement exécutée dans la chaîne courante** lorsque le validateur la supporte, ou un résultat autre que `PASS` implique automatiquement que la chaîne n’est pas fermée. Dans ce cas, la confiance terminale ne peut pas être ÉLEVÉE.

**Interdiction d’auto-attestation :** la validation finale ne peut jamais transformer en preuve une phrase précédente de la conversation affirmant que le registre, le validateur ou le reçu ont été exécutés. Elle doit s’appuyer sur les artefacts matériels et, lorsque disponible, sur l’exécution effective de leur vérification mécanique.

### Verrou terminal d’identité de l’artefact affiché

Juste avant `STOP OUTPUT`, la validation finale doit traiter le **snapshot terminal validé comme source matérielle unique de la decklist**.

Elle vérifie une dernière fois :

`deck affiché == contenu du snapshot terminal validé == output_artifact du registre == artefact du PASS == artefact du reçu vérifié`

Cette égalité porte sur la composition et les ratios de Main / Extra / Side Deck, pas seulement sur le nom `deck-vN`.

Toute modification structurelle après cette vérification — même une simple retranscription différente pendant la rédaction finale — crée un nouvel artefact : PASS, reçu et confiance deviennent immédiatement `STALE`, et `STOP OUTPUT` redevient bloqué.

Ce verrou n’ajoute aucun critère métier. Il empêche uniquement qu’une version validée soit remplacée au moment de l’affichage par une autre liste.

La validation finale ne juge jamais si le delta du refactor était suffisant ni si les pertes fonctionnelles invoquées dans la tentative terminale justifient réellement la fermeture : cela reste la juridiction du hook spécialisé. Elle vérifie seulement que le delta, la nouvelle version, le retest et la tentative terminale exigée existent matériellement sur la bonne version et que le PASS reçu n'est pas obsolète.

Avant STOP OUTPUT, vérifier également que `VISUAL_ASSETS_BOUND` est lié au même run/deck et que les exigences de rendu dérivées ont été satisfaites sur le rendu exact. Une decklist horizontale, une réplique terminale obligatoire absente ou un composant carrousel requis non matérialisé constitue un FAIL de rendu.

Si le statut est absent, invalide, si le registre ou le paquet de preuve compact est absent/incomplet — notamment si `PASS_REFACTOR` ne contient pas de chaîne avant/après/retest matérialisée, ou si la preuve de tentative de compression terminale exigée par le hook manque sur la version finale — ou si un doute apparaît sur l’identité entre la version passée et l’artefact final, **réexécuter `HOOK_ANCRAGE_REFACTOR_MULTI_SYSTEMES` sur l’artefact final**.

La validation finale ne doit jamais accepter comme substitut au paquet de preuve : un Axe spectaculaire, une interaction mixte convaincante, une bonne impression de cohérence ou une ressource commune. Ces éléments peuvent expliquer le concept, mais ils ne prouvent pas que le hook spécialisé a fermé son test adapté et son coût d’intégration.

- s’il confirme la sortie → poursuivre ;
- s’il détecte une régression → renvoyer une seule fois la construction vers ce hook dans les limites de son budget de refactor déjà défini ;
- si son budget est épuisé ou si réussir exige de détruire l’ancrage → abandonner la piste avant affichage.

La validation finale ne doit jamais lancer une troisième, quatrième ou boucle indéfinie d’optimisation.

## 9. Trace d’exécution émise pendant la construction

**« La trace d’exécution obligatoire définie par `STRUCTURE_REPONSES_DECKS_PERSONNAGES` a-t-elle bien été émise dans les messages intermédiaires pendant cette construction, sans être reportée dans la réponse finale ? »**

Vérifier que :

- les étapes importantes ont été signalées au moment où elles ont réellement été exécutées ;
- les statuts annoncés correspondent aux sorties réelles des modules ;
- pour une architecture multi-systèmes, `PASS_DIRECT` / `PASS_REFACTOR` / `FAIL_ABANDON` correspond exactement au statut renvoyé par `HOOK_ANCRAGE_REFACTOR_MULTI_SYSTEMES` ;
- si un refactor a eu lieu, l’utilisateur a vu pendant l’exécution la séquence `brouillon interne → test adapté → échec / compression nécessaire → refactor → retest → PASS` ;
- aucune validation supposée ou non exécutée n’a été présentée comme `PASS` ;
- la réponse finale **ne répète pas** ce journal d’exécution sous forme de section dédiée.

Si **NON** → corriger le comportement d’exécution ou le front-end avant affichage final.

## 10. Confiance d’exécution terminale — certificat de fin de chaîne

**Juridiction exclusive : `VALIDATION_FINALE_DECKS_PERSONNAGES`.**

La confiance d’exécution n’est plus produite par un hook intermédiaire. Elle est attribuée **uniquement après** que les neuf contrôles précédents ont été exécutés sur l’artefact final exact et que toutes les autorités spécialisées requises ont renvoyé leurs sorties valides.

Elle mesure seulement :

**« La chaîne obligatoire applicable à cette réponse a-t-elle réellement été exécutée et fermée sur la version qui va être affichée ? »**

Elle ne mesure ni la puissance du deck, ni sa qualité compétitive, ni une probabilité de victoire, ni la pertinence subjective du concept. Elle ne possède aucun critère métier autonome.

Attribuer :

- **ÉLEVÉE** — tous les contrôles obligatoires applicables sont fermés sur la version exacte ; les statuts spécialisés requis existent, sont frais et cohérents ; aucun point matériel obligatoire ne reste implicite ou non vérifié ;
- **MOYENNE** — la construction semble converger mais au moins une fermeture, preuve, fraîcheur de statut ou réexécution obligatoire reste incomplète ; **STOP OUTPUT reste bloqué** et la réponse doit être renvoyée vers l’autorité concernée ;
- **FAIBLE** — plusieurs éléments obligatoires restent absents, incertains ou non exécutés ; **STOP OUTPUT reste bloqué**.

**Seule une confiance d’exécution terminale ÉLEVÉE autorise l’affichage final.**

Lorsqu’une exécution est déclenchée par **`/fresh`**, seule la confiance recalculée dans ce nouveau tour sur sa dernière version exacte est pertinente pour ce contre-audit ; toute confiance antérieure est ignorée.

### Garde-fous

- La confiance terminale ne peut jamais transformer `FAIL_ABANDON`, un échec narratif, une classification invalide ou une ligne mécaniquement impossible en succès.
- Elle ne recalcule jamais les critères de `HOOK_ANCRAGE_REFACTOR_MULTI_SYSTEMES`, `VALIDATION_CANONIQUE_REMIXE`, `VALIDATION_PROGRESSION_NARRATIVE` ou `STRUCTURE`.
- Pour une architecture multi-systèmes, elle exige simplement un `PASS_DIRECT` ou `PASS_REFACTOR` frais et son paquet de preuve compact, déjà émis par le hook spécialisé.
- Si un validateur mécanique du registre est disponible, elle exige en plus son **reçu frais lié au registre exact** ; sans ce reçu, la confiance terminale est au maximum **MOYENNE** et STOP OUTPUT reste bloqué.
- Si la trace chronologique ou la trace instrumentale présente un événement requis manquant, hors ordre, `STALE` ou lié à un autre artefact, la confiance terminale ne peut pas être ÉLEVÉE ; la chaîne doit revenir au premier point de rupture identifié.
- Pour une architecture multi-systèmes, un `FERMÉE` unique n'est plus suffisant à la transmissibilité : la confiance ÉLEVÉE exige le **replay terminal à froid `FERMÉE` sur le snapshot exact**, émis par le même hook spécialisé.
- Si la version de la decklist, les Axes, la classification, le stade narratif ou tout autre artefact matériel change après attribution de la confiance, **la confiance terminale est immédiatement invalidée** et doit être réattribuée après les contrôles concernés.
- La confiance n’est jamais utilisée pour décider d’arrêter un refactor. L’arrêt appartient à l’autorité métier concernée ; la confiance ne vient qu’après.

**Règle courte : aucun contrôle ne se ferme grâce à la confiance ; la confiance n’existe qu’une fois tous les contrôles déjà fermés.**

# Règle de correction

Si au moins un contrôle essentiel échoue :

1. **ne pas afficher la réponse encore** ;
2. corriger la decklist ou renvoyer la décision concernée vers son autorité spécialisée ;
3. refaire les onze contrôles ;
4. n’afficher qu’après obtention d’une **confiance d’exécution terminale ÉLEVÉE**.

Il est interdit de conserver une contradiction et de l'expliquer après coup.

---

## Formule courte

**Auditer la dernière version exacte → réexécuter les autorités spécialisées compétentes → confirmer que la viabilité multi-systèmes possède une sortie métier fraîche du hook spécialisé sans relancer une optimisation infinie → signaler les restrictions de branche importantes → vérifier le front-end exclusivement selon STRUCTURE → seulement après fermeture de tous les contrôles, attribuer la confiance d’exécution terminale → afficher uniquement si elle est ÉLEVÉE. En mode `/fresh`, appliquer exactement cette chaîne après reset des anciens PASS.**


---

# Entrée terminale obligatoire — conformité narrative matérialisée

Avant son PASS, la présente validation doit recevoir, pour le `run_id` et le `deck-vN` exacts :

- le `narrative_contract.json` frais ;
- son hash ;
- le `narrative_conformance.json` post-construction ;
- le hash du snapshot audité ;
- un statut `PASS` de `VALIDATION_PROGRESSION_NARRATIVE` sur cette version exacte.

Elle ne recalcule pas la chronologie et ne décide pas quelles mécaniques sont autorisées. Elle vérifie seulement que :

- le contrat provient de l'autorité narrative et de la politique STYLE courante ;
- le rapport couvre le snapshot final exact ;
- aucune modification matérielle n'a rendu ce rapport obsolète ;
- la conformité narrative a été fermée **avant** les tests de viabilité utilisant cette decklist ;
- lors d'un `/fresh`, contrat et rapport appartiennent au nouveau run.

Si cette preuve est absente, obsolète ou rattachée à un autre snapshot/run : **STOP OUTPUT = FAIL** et retour à `VALIDATION_PROGRESSION_NARRATIVE`.

**La validation finale reste un backstop ; elle ne doit jamais être le premier endroit où une mécanique future est découverte.**

## RC5 — fermeture pilotage / refactor

Avant STOP OUTPUT :

1. si le rendu contient au moins deux Axes numérotés, vérifier la présence du bloc visible `Guide de pilotage` ;
2. si le run a subi un `material-change`, vérifier qu’un `combo_impact.json` frais sur la version exacte a été validé par `VALIDATION_PILOTAGE_LIGNES_DECKS_PERSONNAGES` ;
3. vérifier que le rendu contient `Impact sur les combos` et le statut correspondant ;
4. pour `UNCHANGED`, la phrase `Aucun Axe essentiel modifié` doit être visible ;
5. pour `MODIFIED` ou `REMOVED`, les Axes/lignes affectés doivent être nommés.

Une nouvelle decklist certifiée sans information visible sur l’impact combos après refactor matériel constitue un FAIL terminal.


## RC7 — fermeture des nouveaux artefacts

Avant fermeture terminale, vérifier seulement l'existence et la liaison à la version/rendu courant des sorties suivantes lorsqu'elles sont applicables :

- `pilotage_contract.json` validé par `VALIDATION_PILOTAGE_LIGNES_DECKS_PERSONNAGES` ;
- pour RC10, ce contrat doit aussi fermer les propriétés de starter pertinentes et les checkpoints d’état physique des lignes complexes sur le même render hash ;
- exigence `decklist-groups` en rendu complet ;
- exigence `refactor-diff` lorsqu'un refactor utilisateur est en `DIFF_ONLY`.

La présente autorité ne recrée ni les critères de starter, ni les critères de présentation : elle vérifie que leurs autorités compétentes les ont fermés sur l'artefact exact.


## RC8 — fermeture terminale du pilotage et du refactor post-sortie

Avant PASS final, vérifier l'existence d'un `PILOTAGE_VALIDATED` frais sur la version/rendu exact contenant le contrat de starter **et**, lorsqu'applicable, la fermeture de résolution des effets. La validation finale ne réinterprète aucun texte de carte ; elle vérifie seulement que l'autorité spécialisée a produit sa sortie requise et que le harness l'a acceptée.

Pour une version issue d'un refactor post-sortie, vérifier que le mode terminal correspond à celui fixé par le runtime : `DIFF_ONLY` par défaut, ou `FULL` uniquement après demande explicite de decklist complète.

## RC9 — fermeture exacte du bundle post-refactor

Pour un refactor post-sortie :

- en `DIFF_ONLY`, exiger le `refactor_diff.md` canonique généré depuis les deux snapshots et le composant `refactor-diff` lié au même hash ;
- refuser toute decklist complète lorsque l'override FULL n'a pas été explicitement demandé ;
- vérifier que chaque composant visuel transporté depuis le rendu précédent possède une transition `PRESERVE`, `REGENERATE` ou `DROP_EXPLICIT` valide ;
- vérifier la continuité de la réplique terminale précédemment requise ;
- considérer `terminal_payload.md` comme texte terminal autorisé : son hash doit être celui du render validé.

La validation finale ne décide ni l'applicabilité des visuels ni les cartes du diff. Elle vérifie seulement que le runtime et STRUCTURE ont produit et lié les artefacts requis sur la version exacte.

`FINAL_RENDER_PREPARED`, `PILOTAGE_VALIDATED` et `FINAL_VALIDATION_PASS` doivent tous viser le **même bundle exact**. Une divergence de render/manifest/contract entre ces trois fermetures interdit `STOP_OUTPUT_ALLOWED`.

## Fermeture RC11 — tous les Axes du rendu

Avant PASS final, vérifier que `PILOTAGE_VALIDATED` porte `axis_coverage_status=PASS` sur le même render hash et que tous les Axes numérotés effectivement affichés sont couverts individuellement par le contrat de pilotage. Un PASS partiel (un Axe fermé, un autre non couvert) interdit la validation finale.


## Fermeture RC12 — preuve d’exécution des lignes

Avant PASS final, vérifier uniquement que `PILOTAGE_VALIDATED` est frais sur le deck/rendu exact et que le harness a accepté l’inventaire multi-starters et les `execution_replays` requis par l’autorité spécialisée.

La validation finale **ne rejoue pas** les ressources, ne redéfinit pas les coûts/cibles/timings, ne choisit pas les starters et ne juge pas la certitude d’un payoff : ces critères appartiennent à `VALIDATION_PILOTAGE_LIGNES_DECKS_PERSONNAGES`. Elle ferme seulement la chaîne lorsque cette sortie spécialisée existe et correspond à la version exacte.


## Fermeture RC13 — légalité structurée des actions

Avant PASS final, vérifier seulement que le `PILOTAGE_VALIDATED` frais a été accepté par le runtime v1.16 avec les `action_legality_proof` requis pour les execution replays de la version exacte.

La validation finale ne réévalue aucun predicate, ne relit aucun texte de carte et ne recrée aucune contrainte. Elle vérifie uniquement que la sortie spécialisée acceptée existe, correspond au même deck/render et n'est pas STALE.

Un bare `legality_checks=PASS`, une preuve de ressource RC12 seule, ou un ancien contrat de pilotage sans Action Legality Proof ne peut pas ouvrir STOP OUTPUT sur RC13.


## Fermeture RC14 — résultats dérivés

Avant PASS final, vérifier seulement que le `PILOTAGE_VALIDATED` frais a été accepté par le runtime v1.17 avec :

- snapshots de replay ;
- inventaire de derived claims fermé ;
- valeurs calculées liées au rendu exact ;
- cold derived sweep fermé ;
- checkpoints physiques dérivés lorsque pertinents ;
- placement critique matérialisé lorsque requis.

La validation finale ne recalcule aucun compte, aucune ATK, aucun dégât et aucune zone. Elle ne connaît pas la règle MMZ/EMZ : elle vérifie seulement que les autorités compétentes et le runtime ont fermé ces sorties sur le même deck/render exact.

Un ancien contrat RC13 sans fermeture des résultats dérivés ne peut pas ouvrir STOP OUTPUT sur RC14.

## Fermeture RC15 — State-at-Time, certitude et STALE

Avant PASS final, vérifier seulement que le `PILOTAGE_VALIDATED` frais a été accepté par le runtime v1.18 avec le contrat RC15 :

- snapshots `BEFORE/AFTER` exacts ;
- préconditions d'état et cold state sweep fermés ;
- attachments cohérents lorsque pertinents ;
- topologie/relations spatiales fermées lorsque pertinentes ;
- placements critiques rendus au joueur ;
- external-condition inventory + cold certainty sweep fermés ;
- outcome `GUARANTEED` uniquement lorsque les conditions matérielles nécessaires sont fermées.

La validation finale ne redécouvre aucune flèche Link, propriété de carte, attachment ni condition adverse. Elle vérifie uniquement que Pilotage et le harness ont fermé ces sorties sur la version/rendu exacts.

Après refactor matériel, vérifier également que l'invalidation STALE a été matérialisée avant le retest de la nouvelle version. Une chaîne `v1 → v2 → PASS` sans événement STALE requis ne peut pas ouvrir STOP OUTPUT.

---

# Extension terminale RC16 — preuve sémantique fraîche

Lorsque des lignes essentielles sont affichées, la validation finale exige désormais que le `pilotage_contract` frais de la version exacte porte `execution_contract_version: RC16` et que ses replays essentiels aient fermé :

- les SRC lazy réellement applicables ;
- le `cold_semantic_sweep` ;
- les bindings GAME RULES matériels ;
- le `cold_game_rule_sweep` ;
- le backward proof ;
- le `cold_backward_sweep` ;
- les décisions critiques requises ;
- le cross-check vers les structures RC13–RC15.

La présente validation ne relit pas les textes de cartes, ne recalcule pas les règles de jeu et ne refait pas le backward proof. Elle vérifie seulement que `VALIDATION_PILOTAGE_LIGNES_DECKS_PERSONNAGES` a produit un PASS frais avec le contrat RC16 exigé avant `STOP_OUTPUT_ALLOWED`.

# Extension terminale RC16.1 — exécution compilée (compatibilité historique)

Pour les contrats historiques RC16.1, avant `STOP_OUTPUT_ALLOWED`, vérifier que le `PILOTAGE_VALIDATED` frais du bundle exact a été accepté avec `execution_contract_version=RC16.1` et que chaque replay requis portait son `unified_cold_audit`. Le chemin nominal post-RC16.22.1 est remplacé par la fermeture MCB1 définie plus bas.

Cette autorité ne réexécute pas les huit audits spécialisés : le runtime v1.21 projette l’audit froid unique vers leurs validateurs mécaniques respectifs. La validation finale vérifie seulement la présence, la fraîcheur et l’identité du PASS Pilotage sur le deck/rendu exacts.

Un contrat RC16 legacy peut rester valide pour régression, mais une candidate déclarée RC16.1 ne doit pas revenir silencieusement aux cold sweeps séparés.

# Extension terminale RC16.2 — fermeture déterministe du rendu

Avant PASS final, vérifier uniquement que `FINAL_RENDER_PREPARED` a consommé le **PASS exact de `render-check`** : même `render-vN`, même SHA du contrat gelé, même render SHA, même manifest canonique et même inventaire de composants.

La validation finale ne réexécute pas les assertions de mise en forme et ne corrige jamais le contrat. Une mutation du contrat après freeze, un `CONTRACT_DEFECT_SUSPECTED`, un budget de réparation épuisé ou l’absence de manifest canonique interdit `STOP_OUTPUT_ALLOWED`.

`presentation-change` n’est une transition valide qu’à partir d’un rendu déjà `FINAL_RENDER_PREPARED` et doit préserver le fingerprint de politique de rendu. Les attempts pré-PREPARED ne sont pas des versions.



# Extension terminale RC16.14 — assemblage pré-émission exact

Avant `FINAL_VALIDATION_PASS`, la présente autorité exige un **receipt frais d'assemblage terminal** pour le bundle exact déjà fermé par STRUCTURE et Pilotage.

Elle vérifie uniquement que :
- `terminal_presentation_plan.json` existe ;
- `terminal_presentation.receipt.json` porte `PASS` ;
- `run_id`, `deck-vN` et `render-vN` correspondent au run courant ;
- le SHA du texte correspond au rendu exact déjà validé ;
- le SHA du render manifest correspond au manifest exact déjà validé ;
- le hash d'inventaire des composants correspond au même bundle ;
- lorsque des composants existent, leurs payloads/manifestes restent liés à ces hashes ;
- le plan et le receipt n'ont pas été modifiés après leur vérification.

La présente autorité **ne décide jamais** qu'un carrousel principal, un mini-carrousel, un Axe signature, un climax ou une réplique terminale doit exister. Ces décisions restent exclusivement aux autorités STRUCTURE compétentes. Elle accepte donc aussi un inventaire explicitement vide lorsqu'il est le résultat exact du pipeline spécialisé.

Un PASS du receipt signifie seulement que le **plan pré-émission** est complet et frais. Il ne constitue pas une preuve que l'interface utilisateur a effectivement affiché les composants après l'envoi de la réponse. Cette dernière propriété reste soumise aux tests black-box.

Si le plan/receipt manque, est `STALE`, si le texte diverge, si l'inventaire diverge ou si un payload autorisé manque, `FINAL_VALIDATION_PASS` est bloqué. `STOP_OUTPUT_ALLOWED` ne peut être ouvert qu'après fermeture de ce contrôle sur la version exacte.

# Fermeture post-RC16.22.1 — Pilotage compilé MCB1

Pour le chemin nominal durci, la présente autorité accepte uniquement un `PILOTAGE_VALIDATED` frais lié au bundle exact et provenant de `wire_schema=ygo-pilotage-contract-v3` avec `execution_contract_version=RC16.2`. Ici `RC16.2` est la version du contrat d'exécution Pilotage, distincte de toute étiquette de release système.

Elle vérifie seulement que le PASS spécialisé exact atteste la fermeture des sorties suivantes sur le même contrat/rendu :

- SRC / GAME RULES matériels fermés ;
- MCB matériels fermés ;
- projection mécanique froide indépendante concordante ;
- projection compilée liée par hash et recalculée par le runtime ;
- replay déterministe accepté ;
- fermeture létale par ledger lorsque `LETHAL` est revendiqué ;
- receipt Pilotage frais après FULL_SHARED_VALIDATOR.

La validation finale **ne relit pas les textes de cartes, ne choisit aucun MCB, ne recalcule aucun set `ALL_MATCHING` et ne recompte aucun dégât**. Ces opérations appartiennent respectivement aux autorités sémantiques/Pilotage et au Deterministic Shell. Elle vérifie uniquement la présence, l'identité, la fraîcheur et le PASS de leur sortie exacte.

Si Pilotage a épuisé son budget same-model, si une projection est `UNRESOLVED`, si un receipt/hash est obsolète ou si le rendu diffère de celui validé : `FINAL_VALIDATION_PASS` et `STOP_OUTPUT_ALLOWED` restent bloqués. La conclusion est **FAIL / NON CERTIFIÉ** ; aucune escalade de modèle n'est autorisée.

## Fermeture candidat post-MCB1 — authoritative dry-run et proof floor

Le chemin nominal conserve `wire_schema=ygo-pilotage-contract-v3` et `execution_contract_version=RC16.2`. Aucune nouvelle autorité métier n'est créée.

Le harness interdit désormais le commit Pilotage avant un `authoritative dry-run` PASS lié aux hashes exacts deck/rendu/business. Les défauts `PRESENTATION_RENDER` et `PROOF_SCHEMA_ADMIN` sont réparés en amont sans consommer le budget métier ; seules les issues `BUSINESS_SEMANTIC_MECHANICAL` peuvent consommer ce budget.

La validation finale ne recrée ni cette taxonomie ni les règles du proof floor. Elle exige seulement un `PILOTAGE_VALIDATED` frais, issu du chemin nominal exact. Puisque le commit est bloqué par construction si le proof floor ou le dry-run échoue, leur fermeture est une précondition instrumentale du PASS Pilotage, pas une seconde doctrine finale.

Si le dry-run est obsolète, si le proof floor échoue, si le budget métier est épuisé, si le budget non métier atteint `NON_BUSINESS_REPAIR_EXHAUSTED`, ou si le rendu/deck diverge après validation : `FINAL_VALIDATION_PASS` et `STOP_OUTPUT_ALLOWED` restent bloqués.


## Fermeture candidat post-MCB1-V2 — payload Pilotage construit par le shell

Le chemin nominal exige désormais que le payload métier ayant conduit au `PILOTAGE_VALIDATED` provienne d'un merge frais du Pilotage Business Payload Builder sur le deck/rendu exacts. Cette exigence est instrumentale : elle garantit seulement que les identités de lignes/starters/replays et leurs ancres de rendu n'ont pas été réécrites ou supprimées pendant les corrections.

La validation finale ne reconstruit pas le squelette, ne rejoue pas le merge et ne décide aucun champ métier. Elle vérifie uniquement le `PILOTAGE_VALIDATED` frais déjà obtenu par le chemin nominal. Si le reçu builder/merge est absent ou obsolète, si une réparation viole le scope local, ou si le payload/rendu/deck change après le dry-run PASS, `FINAL_VALIDATION_PASS` et `STOP_OUTPUT_ALLOWED` restent bloqués.

---

## Addendum RC16.23 — fraîcheur structurelle terminale

Avant `STOP OUTPUT`, la validation finale vérifie également que le contrat Pilotage est toujours lié au **même inventaire structurel Style → Axes** que celui de la version courante et que cet inventaire survit encore dans le rendu exact autorisé.

Un changement de l'inventaire, du contrat Pilotage ou du rendu après leur validation rend leurs dépendances non fraîches. La validation finale ne reconstitue pas les starters ni les branches : elle vérifie seulement l'existence et la fraîcheur des sorties des autorités compétentes.

Un run en état `BLOCKED_FATAL` ne peut recevoir ni `FINAL_VALIDATION_PASS` ni `STOP OUTPUT`.

### Émission terminale vérifiée — RC16.23

Après `STOP OUTPUT` autorisé, le texte destiné au joueur est matérialisé dans un payload terminal content-addressed. La sortie conversationnelle doit provenir de la lecture vérifiée de ce payload exact : le runtime recalcule son hash immédiatement avant émission et le compare au hash du rendu autorisé.

Une mutation du fichier après autorisation ne révoque pas magiquement un message déjà émis, mais elle interdit toute nouvelle lecture terminale de ce payload tant que le hash diverge. L'alias ergonomique non autoritatif n'est jamais utilisé comme preuve de fraîcheur.

## Addendum RC16.23 Black-Box Corrective — survie visuelle et sortie terminale

Avant `FINAL_VALIDATION_PASS`, lorsque `VISUAL_ASSETS_BOUND` déclare `main_carousel.applicable=true` ou `signature_climax.mini_carousel_applicable=true`, la validation finale exige que l'obligation correspondante survive dans le plan terminal exact : identité de composant, primitive de rendu et parent de climax lorsqu'il est applicable. La validation finale ne décide jamais qu'un carrousel est applicable ; elle vérifie uniquement la survie de la décision déjà prise par STRUCTURE.

Une obligation visuelle applicable absente, stale ou rebound produit un défaut de présentation bloquant. `STOP OUTPUT` reste interdit tant que le plan terminal exact ne matérialise pas les composants requis.

La sortie finale n'est transmissible que lorsque la politique runtime autorise `FINAL_ARTIFACT`. Un run `IN_PROGRESS`, `BLOCKED_FATAL`, un blocage FastPath non rerouté, l'absence de `FINAL_VALIDATION_PASS`, l'absence du payload terminal ou `stop_output_allowed=false` imposent une réponse de statut uniquement ; aucune decklist complète ne peut être reconstruite depuis le contexte conversationnel ou un artefact provisoire.

---
## RC16.23 — Fermeture après compilation sémantique

La validation finale distingue désormais explicitement :

- **information métier absente ou contradictoire** → retour à l'autorité compétente ;
- **contradiction mécanique calculable** → FAIL du validateur compétent ;
- **information administrative/dérivable absente** alors que son parent autoritatif existe → défaut de compiler/runtime, jamais demande de recopie au modèle.

Aucun PASS final ne peut masquer un défaut `ADMIN_DERIVABLE`. Inversement, ce défaut ne constitue pas un échec stratégique du deck et ne doit pas consommer un budget de réparation métier.

## Addendum RC16.23.3 — fermeture terminale 4D

`COMPLETED` n'est pas une réussite globale. La validation finale vérifie l'existence fraîche des sorties compétentes sur la version exacte : Pilotage/ruling pour la vérité sémantique, plan/receipt terminal pour la présentation émise, preuve mécanique persistée lorsqu'applicable, et continuité sans handoff récupérable non résolu. Elle ne recrée aucun de leurs critères. Toute dimension manquante bloque `FULL_PASS`.
