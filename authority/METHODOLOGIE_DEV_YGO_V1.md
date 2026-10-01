# METHODOLOGIE_DEV_YGO — V1

## Rôle

Cette source définit uniquement notre manière permanente de développer le système Yu-Gi-Oh!.
Elle est générique et ne contient aucun état courant, aucune version active, aucun hash, aucun NEXT_STEP ni aucun résultat de test.

---

# Principes de développement

## 1. Pas d'escalade de modèle. Escalade de preuve.

Quand un résultat est douteux, augmenter la qualité de la preuve avant d'ajouter de nouvelles règles.

Ordre préféré :
1. reproduire ;
2. caractériser ;
3. matérialiser un RED/KILL ;
4. protéger un GREEN/positive control ;
5. figer le Change Surface Contract ;
6. patcher ;
7. comparer Actual Diff Surface à Authorized Diff Surface ;
8. targeted tests proportionnés au risque : unit + RED/failure-path + GREEN/happy-path ;
9. coverage technique ciblée ligne/branche sur la surface modifiée lorsque pertinent ;
10. integration tests ciblés ;
11. mutation tests ciblés ;
12. Red-Team ;
13. End-to-End lorsque la responsabilité traverse plusieurs couches ou avant fermeture de candidate ;
14. Differential Regression Gate parent → candidate lorsque applicable ;
15. full regression cumulative ;
16. coverage technique cumulative selon le seuil/contrat prévu ;
17. package ;
18. extraction propre ;
19. replay des bytes packagés ;
20. Black-Box réel.

## 2. Le modèle décide seulement ce qui n'est pas dérivable.

Le modèle peut fournir :
- jugement métier non dérivable ;
- choix stratégiques ;
- interprétation spécialisée lorsqu'une autorité l'exige ;
- arbitrages explicitement laissés au modèle.

Le runtime/compiler doit posséder ce qui est dérivable :
- IDs ;
- hashes ;
- versions ;
- bindings ;
- comptages ;
- sommes ;
- statuts STALE calculables ;
- routage calculable ;
- applicabilité calculable ;
- structure de rendu calculable ;
- preuves techniques ;
- cohérence formelle.

Le validator contrôle les invariants mécaniques de sa juridiction.
Il ne remplace jamais une autorité métier.

## 3. Une information métier, une source sémantique.

Ne pas demander au modèle de recopier la même décision dans plusieurs payloads.

Une décision sémantique doit être déclarée une fois puis projetée automatiquement vers :
- bindings ;
- tokens ;
- render ;
- coverage ;
- traces ;
- receipts ;
- validations mécaniques.

## 4. Version exacte avant mutation.

Aucune mutation de produit sans version cible explicitement choisie par l'utilisateur.

Ne jamais :
- inventer une RC ;
- incrémenter automatiquement ;
- promouvoir automatiquement ;
- changer de target en cours de chantier sans nouveau verrou explicite.

## 5. PRE-GO avant GO.

Le PRE-GO prépare :
- scope ;
- REQ ;
- tâches ;
- RED/KILL ;
- positive controls ;
- stratégie de tests par tâche : unit, RED/failure-path, GREEN/happy-path, integration, line/branch coverage, mutation, End-to-End, differential et regression selon pertinence ;
- moment d’exécution de chaque niveau de test ;
- portée ciblée ou cumulative ;
- coût relatif et justification des tests coûteux ;
- critères de coverage technique pertinents ;
- mutants ;
- Red-Team ;
- packaging ;
- condition de sortie.

Le PRE-GO n'autorise aucune mutation.

Le GO explicite autorise uniquement le scope déjà préparé sur la version explicitement donnée.

## 6. Requirements cumulatifs.

Les exigences du système ne repartent jamais de zéro à chaque version.

Un REQ :
- reste visible dans l'historique ;
- devient regression guard après fermeture ;
- peut devenir STALE après changement matériel ;
- devient REGRESSED si une capacité précédemment fermée échoue de nouveau ;
- conserve son last-known-good.

## 7. Un PASS doit être matériel.

Un PASS textuel ne remplace jamais :
- exécution ;
- test ;
- validateur ;
- receipt ;
- snapshot ;
- replay ;
- preuve Black-Box.

Toute preuve est liée à la version exacte et, lorsque pertinent, aux bytes exacts.

## 8. Les packages doivent être testés comme produits livrés.

Un workspace vert ne suffit pas.

Après packaging :
- extraire dans un environnement propre ;
- rejouer les tests sur les bytes packagés ;
- vérifier flat-source / installabilité ;
- seulement ensuite considérer la candidate déterministement qualifiée.

## 9. Les Black-Box cherchent les faux PASS.

Le Black-Box doit notamment chercher :
- run final propre après tentatives abandonnées ;
- coupure nécessitant un "reprend" sans USER_REQUIRED ;
- payload correct mais surface finale fausse ;
- bon total mais mauvais groupage ;
- proof stale ;
- conditional transformé en guaranteed ;
- retry masquant une faiblesse ;
- AUTO_RECOVERABLE sans route réelle ;
- responsabilité dérivable encore laissée au modèle.

Les recommandations de l'IA Black-Box ne sont jamais appliquées automatiquement.
Elles doivent être auditées : défaut réel, régression, friction normale, redondance ou recommandation dangereuse.

## 10. Quiet execution.

Les détails runtime restent internes par défaut.

L'utilisateur ne doit voir que :
- quelques checkpoints utiles ;
- USER_REQUIRED réel ;
- FATAL réel ;
- sortie finale ;
- trace de statut compacte si demandée ou prévue.

Ne pas transformer la conversation en journal d'exécution.

## 11. Continuité.

Un vrai besoin utilisateur peut interrompre le run.
Une coupure technique ou conversationnelle inutile ne doit pas être normalisée.

Distinguer :
- USER_REQUIRED ;
- NOMINAL_CONTINUATION ;
- RECOVERY ;
- UNWANTED_HANDOFF ;
- FATAL.

## 12. Architecture logique riche, déploiement physique minimal.

Ne pas créer un fichier permanent par responsabilité logique.

Préférer :
- peu de Sources ;
- fichiers plats ;
- responsabilités internes claires ;
- artefacts de chantier produits à la demande.

## 13. Differential Regression Gate — Parent → Candidate.

Une candidate ne doit pas silencieusement perdre une capacité déjà VERIFIED/fermée de son parent exact.

Principe :

`VERIFIED(parent) ∧ degraded(candidate) => BUILD_FAIL`

Lorsqu'une capacité fermée est applicable à la candidate :
- conserver un regression guard ou golden fixture rejouable ;
- identifier les invariants structurés réellement protégés ;
- rejouer le scénario sur le parent exact et la candidate exacte lorsque le replay différentiel est pertinent ;
- comparer les invariants protégés, pas du texte libre ou des différences purement cosmétiques ;
- bloquer toute dégradation non explicitement autorisée ;
- ne jamais transformer un comportement accidentel du parent en requirement sans autorité ;
- ne jamais supprimer silencieusement un regression guard, une fixture ou son mapping vers le REQ ;
- si la préservation ne peut pas être établie fiablement, produire UNVERIFIED / STALE / BLOCKED selon la juridiction au lieu d'inventer un PASS.

Un comportement jamais suffisamment couvert auparavant n'est pas qualifié artificiellement de régression.
Après découverte, reproduction, correction et GREEN matériel, il devient un regression guard permanent.

Le Differential Regression Gate ne remplace ni les targeted tests, ni les mutants, ni le Red-Team, ni la full regression, ni le package replay, ni le Black-Box réel.

## 14. Change Surface Contract — Minimal Necessary Change.

Avant toute mutation, chaque tâche corrective doit définir sa surface de changement autorisée.

Le contrat distingue au minimum :
- `MUST-TOUCH` : responsabilités où la correction doit normalement vivre ;
- `MAY-TOUCH` : dépendances modifiables seulement si la caractérisation démontre leur nécessité ;
- `PRESERVE` : comportements/invariants présents dans une surface modifiée qui doivent rester vrais ;
- `NO-TOUCH` : surfaces explicitement hors blast radius ;
- `NON-GOALS` : comportements que le chantier ne cherche pas à modifier ;
- `INVARIANTS` : propriétés qui doivent rester vraies pendant et après le patch ;
- `DEPENDENCIES` : responsabilités dépendantes susceptibles d'être affectées ;
- `PROOFS MADE STALE` : preuves à invalider/rejouer si la surface change ;
- `AUTHORIZED DIFF SURFACE` : ensemble de fichiers/symboles/responsabilités que le PRE-GO autorise à modifier.

La localisation doit privilégier :

`fichier → symbole/fonction/classe → responsabilité → call path`

Les numéros de lignes peuvent aider à localiser le code sur le parent exact mais ne sont pas l'identité normative de la surface, car ils peuvent bouger pendant le patch.

Principe :

`actual_changed_surface ⊆ authorized_change_surface`

et

`actual_changed_surface ∩ NO_TOUCH = ∅`

Toute sortie de la surface autorisée bloque l'implémentation et exige un amendement du PRE-GO avant de poursuivre.

Un refactor opportuniste, un nettoyage adjacent ou une amélioration non nécessaire au REQ actif est interdit pendant un corrective closure.
Le patch recherché est le plus petit changement architecturalement correct capable de satisfaire le REQ actif et ses regression guards.

Après patch, la surface réellement modifiée doit être comparée à la surface autorisée avant qu'une candidate puisse atteindre DEVELOPMENT PASS.

## 15. Risk- and Cost-Aware Test Escalation.

Les tests doivent être planifiés et exécutés au niveau le moins coûteux capable de fournir la preuve nécessaire, puis escaladés selon le risque, le blast radius et le niveau de qualification recherché.

Le PRE-GO doit décider explicitement, pour chaque tâche, lesquels des niveaux suivants sont requis et à quel moment :
- `UNIT` : fonction, règle ou composant isolé ;
- `RED / FAILURE-PATH` : démontrer le défaut, le refus attendu ou le fail-closed ;
- `GREEN / HAPPY-PATH` : protéger le comportement légitime symétrique ;
- `INTEGRATION` : vérifier l’interaction entre plusieurs responsabilités ;
- `LINE COVERAGE` : vérifier que les lignes pertinentes de la surface modifiée sont réellement exercées ;
- `BRANCH COVERAGE` : vérifier que les branches décisionnelles pertinentes, y compris les chemins d’échec, sont exercées ;
- `MUTATION` : vérifier que les tests échouent lorsqu’un invariant est volontairement cassé ;
- `END-TO-END` : vérifier le workflow complet à travers les couches réelles ;
- `DIFFERENTIAL REGRESSION` : vérifier la préservation des capacités protégées du parent ;
- `FULL CUMULATIVE REGRESSION` : protéger l’ensemble des acquis au gate final ;
- `PACKAGE REPLAY` : vérifier les bytes réellement livrés ;
- `BLACK-BOX` : chercher les faux PASS et comportements non couverts par les preuves déterministes.

Ordre de coût préféré lorsque pertinent :

`unit / RED / GREEN → coverage local ligne/branche → integration ciblée → mutation ciblée → E2E pertinent → differential affecté → full regression → package replay → Black-Box`

Cet ordre est un principe d’escalade, pas une obligation d’exécuter tous les niveaux après chaque modification.

Le PRE-GO doit matérialiser pour chaque tâche :
- `TEST LEVELS REQUIRED` ;
- `TEST TIMING / GATE` ;
- `TEST SCOPE` : local, affected, cumulative ou packaged ;
- `LINE COVERAGE SCOPE` ;
- `BRANCH COVERAGE SCOPE` ;
- `MUTATION SCOPE` ;
- `INTEGRATION SCOPE` ;
- `E2E REQUIRED` et sa justification ;
- `DIFFERENTIAL REQUIRED` et les capacités protégées concernées ;
- `COST CLASS` : low / medium / high / external, ou équivalent ;
- `DEFERRED UNTIL GATE` pour les preuves volontairement reportées à une barrière plus tardive.

Le coût n’autorise jamais à supprimer une preuve nécessaire. Il autorise seulement à différer un test coûteux jusqu’au gate où cette preuve devient nécessaire.

### Coverage technique.

Le coverage ligne/branche est un indicateur de chemins exécutés, jamais une preuve suffisante de correction.

Il doit être combiné avec :
- assertions métier ;
- RED/failure paths ;
- GREEN/happy paths ;
- mutation testing lorsque pertinent ;
- regression guards ;
- preuves d’intégration ou E2E si la responsabilité traverse plusieurs couches.

Ne pas imposer artificiellement `100 %` à tout le code à chaque micro-patch.

Préférer :
- forte couverture de la surface réellement modifiée ;
- couverture des branches critiques et des failure paths ;
- seuils cumulatifs définis explicitement lorsque le projet en exige ;
- justification matérielle lorsqu’une branche pertinente ne peut pas être couverte ;
- aucun PASS fondé uniquement sur un pourcentage global.

Une zone critique nouvellement modifiée ne doit pas être considérée couverte si le chemin nominal seul est exercé alors qu’un failure path matériel existe.

### Placement des tests.

Les tests chers ne sont exécutés qu’au moment où ils apportent une preuve nouvelle nécessaire :
- pendant l’itération locale : unit, RED/GREEN, coverage ciblée, integration ciblée, mutation ciblée ;
- après stabilisation de la tâche : E2E pertinent et differential affecté ;
- à la fermeture déterministe de la candidate : full regression, coverage cumulative prévue, package replay ;
- après qualification déterministe : Black-Box réel.

Le PRE-GO doit empêcher deux erreurs symétriques :
- sous-tester une surface risquée ;
- sur-tester systématiquement toute la plateforme alors qu’une preuve locale moins coûteuse suffit au stade courant.

---

## 16. Persistance minimale des artefacts et preuve matérielle des tests.

Le chat n'est pas la source d'autorité de l'état du chantier. Les informations nécessaires à une reprise fiable doivent être matérialisées dans les artefacts de chantier existants, sans créer un runtime de développement dédié.

Le protocole minimal repose sur :
- un `DEV_STATE` courant ;
- le `PRE-GO` actif ;
- la matrice cumulative active ;
- le registre cumulatif des REQ ;
- les preuves de tests réellement utiles au chantier ;
- les hashes/version/parent nécessaires pour rattacher une preuve aux bons artefacts.

Principe :

`non matérialisé dans l'artefact autoritaire approprié => non acquis pour la reprise`

Il n'est pas nécessaire de construire un orchestrateur ou un runtime de développement. Les tests peuvent être lancés directement avec les outils disponibles, à condition que l'IA :
- exécute réellement la commande prévue ;
- conserve le résultat matériel utile : commande, portée, résultat, exit code lorsqu'il existe, tests PASS/FAIL/SKIP lorsque disponible, coverage utile, version/bytes concernés ;
- mette à jour la matrice et le DEV_STATE avec ce qui a réellement été exécuté ;
- ne transforme jamais une intention de test en preuve d'exécution ;
- distingue `PLANNED`, `EXECUTED_PASS`, `EXECUTED_FAIL`, `SKIPPED`, `DEFERRED` et `BLOCKED` lorsque ces états sont pertinents.

Les sorties brutes volumineuses n'ont pas à être persistées intégralement si une preuve compacte suffit. En revanche, les éléments nécessaires pour démontrer le PASS/FAIL, reproduire le test ou comprendre un blocker doivent être conservés.

À chaque jalon important, avant changement de discussion et avant toute qualification/promotion, l'IA doit réconcilier :

`PRE-GO / matrice / registre REQ / tests réellement exécutés / DEV_STATE / fichiers effectivement présents`

En cas de divergence, l'état matériel prime sur le souvenir du chat jusqu'à réconciliation.

### Persistance proportionnée.

Ne pas créer un fichier permanent ou un receipt séparé pour chaque commande par principe.

Préférer :
- mise à jour du `TEST_PROOF_MATRIX` pour les preuves courantes ;
- preuve dédiée uniquement lorsqu'un résultat est important, volumineux, terminal, externe, difficile à reproduire ou nécessaire à une transition ;
- `DEV_STATE` pour l'état opérationnel courant ;
- bundle de transition minimal pour transporter uniquement les artefacts nécessaires à la reprise.

La persistance doit être suffisante pour reprendre et auditer le chantier, mais rester simple et proportionnée.

### Exécution des tests.

Le PRE-GO planifie les tests ; l'IA les exécute au gate prévu avec l'outil disponible le plus direct.

Aucune abstraction supplémentaire n'est requise si elle n'apporte pas de preuve nouvelle.

Après chaque gate de test exécuté :
1. enregistrer le résultat réel ;
2. mettre à jour les REQ/preuves affectés ;
3. marquer les preuves devenues STALE ;
4. décider du prochain gate selon le PRE-GO ;
5. arrêter immédiatement si un FAIL/BLOCKED empêche légitimement l'escalade vers des tests plus coûteux.

---

# Bonnes pratiques

- partir d'un défaut réel ;
- matérialiser RED + GREEN ;
- conserver les regression guards ;
- matérialiser une baseline de capacités protégées pour les REQ VERIFIED ;
- définir un Change Surface Contract avant mutation ;
- planifier par tâche les niveaux de tests nécessaires, leur timing, leur portée et leur coût ;
- exécuter d’abord les preuves ciblées les moins coûteuses capables de détecter le défaut ;
- couvrir les lignes et branches pertinentes de la surface modifiée sans confondre coverage et correction ;
- comparer Actual Diff Surface à Authorized Diff Surface après patch ;
- rejouer les invariants parent → candidate lorsque le Differential Regression Gate est applicable ;
- lier REQ → tâche → test → preuve → PASS ;
- enregistrer le last-known-good ;
- mettre à jour l'état avant une longue phase ;
- vérifier le workspace avant de rejouer ce qui est déjà DONE ;
- en cas de divergence, réconcilier les artefacts avant de rollback ;
- corriger au niveau le plus bas capable de garantir l'invariant ;
- préférer la compilation déterministe à la recopie par le modèle ;
- tester le package réellement livré ;
- séparer développement déterministe et promotion ;
- attendre une décision utilisateur pour toute nouvelle version ;
- produire un handoff matériel avant un changement de discussion planifié ;
- matérialiser dans la matrice/DEV_STATE les tests réellement exécutés et leur résultat ;
- conserver seulement les preuves dédiées réellement nécessaires à la reprise ou à l’audit ;
- utiliser le chat comme opérateur du protocole, jamais comme unique mémoire de l’état du chantier.

---

# Mauvaises pratiques

- nouvelle matrice vide à chaque RC ;
- nouveau hook pour une amélioration théorique ;
- PASS déclaré parce que "ça semble bon" ;
- patch avant reproduction du défaut ;
- patch sans positive control ;
- lancer systématiquement toutes les suites coûteuses après chaque micro-changement sans justification ;
- considérer un pourcentage de line coverage comme preuve suffisante de correction ;
- couvrir uniquement le happy path lorsqu’un failure path critique existe ;
- reporter indéfiniment un test coûteux au-delà du gate où sa preuve devient nécessaire ;
- vérifier seulement le dernier run réussi ;
- ignorer les tentatives abandonnées ;
- prendre `resume_count > 0` comme définition universelle d'un échec ;
- laisser le modèle produire IDs/hashes/bindings calculables ;
- modifier plusieurs juridictions pour un défaut local ;
- refactorer opportunistement une zone adjacente pendant un corrective closure ;
- toucher une surface NO-TOUCH ou non autorisée sans amendement PRE-GO ;
- supprimer silencieusement un regression guard, une golden fixture ou son mapping vers un REQ ;
- considérer une simple absence de différence textuelle comme preuve de non-régression ;
- ajouter des fichiers permanents pour chaque sous-composant ;
- utiliser le workspace vert comme preuve du ZIP ;
- créer automatiquement une version ;
- dépendre de la mémoire de la conversation pour reprendre un chantier ;
- déclarer un test exécuté sans commande/résultat matériel correspondant ;
- créer un runtime de développement ou une couche d’orchestration complexe lorsque le protocole et les outils directs suffisent ;
- produire un fichier de preuve séparé pour chaque micro-test sans nécessité ;
- continuer à parler à l'utilisateur pendant des réparations purement internes.
