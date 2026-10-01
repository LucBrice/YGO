# META_REQ_SYSTEM_DEV_YGO — V1

## Rôle

Cette source contient uniquement les META-REQ permanents de développement.
Ils s'appliquent à tous les chantiers, toutes les versions et toutes les discussions.

---

## META-REQ-VERSION-LOCK
Toute implémentation exige une version cible explicitement fixée avant mutation.

## META-REQ-NO-AUTO-VERSION
Aucun numéro de version ou promotion ne peut être créé automatiquement.

## META-REQ-PREGO-GO
PRE-GO prépare et fige le scope ; GO explicite autorise l'implémentation.

## META-REQ-DEVSTATE
Tout chantier actif doit pouvoir être repris à partir d'un état matériel courant.
L'état est mis à jour aux jalons importants et avant toute transition planifiée.

## META-REQ-CUMULATIVE-REQ
Les requirements sont cumulatifs.
Un REQ fermé devient regression guard ; il n'est pas supprimé.

## META-REQ-REGRESSION-VISIBILITY
Toute régression doit indiquer au minimum :
- REQ concerné ;
- version actuelle ;
- last-known-good ;
- test/KILL qui la démontre.

## META-REQ-EXACT-BINDING
Toute preuve, PASS, receipt et validation est liée à la version exacte et aux artefacts exacts.

## META-REQ-NO-VERBAL-PASS
Aucun PASS textuel ne remplace une exécution obligatoire.

## META-REQ-POSITIVE-CONTROL
Tout RED/KILL important possède, lorsque applicable, un GREEN/positive control symétrique.

## META-REQ-TEST-LADDER
Ordre nominal, adapté au risque et au coût :
characterization → RED/KILL → Change Surface Contract → patch → Actual Diff check → unit + RED/GREEN ciblés → line/branch coverage ciblée lorsque pertinente → integration ciblée → mutation ciblée → Red-Team → End-to-End lorsque pertinent → Differential Regression Gate lorsque applicable → full regression → coverage cumulative prévue → package → clean replay → Black-Box.

Tous les niveaux ne sont pas exécutés après chaque micro-patch. Le PRE-GO doit définir le niveau de preuve requis et le gate auquel chaque test coûteux devient obligatoire.

## META-REQ-RISK-COST-AWARE-TESTING
Chaque tâche de mutation doit posséder un plan de test proportionné au risque, au blast radius et au coût.
Le PRE-GO doit préciser, lorsque pertinent : unit tests, RED/failure-path, GREEN/happy-path, integration tests, line coverage, branch coverage, mutation tests, End-to-End, Differential Regression et full regression.
Il doit également préciser le timing/gate, la portée et le coût relatif de ces preuves.
Un test coûteux peut être différé jusqu'au gate approprié, mais jamais supprimé lorsque sa preuve est nécessaire à la qualification.

## META-REQ-CODE-COVERAGE
Le line coverage et le branch coverage sont des preuves de chemins exécutés, pas des preuves suffisantes de correction.
La surface modifiée critique et ses failure paths pertinents doivent être couverts selon le contrat défini au PRE-GO.
Aucun PASS ne peut être fondé uniquement sur un pourcentage global de coverage.
Une couverture globale à 100 % n'est pas une exigence universelle ; les seuils et portées doivent être justifiés par le risque et la juridiction.

## META-REQ-NO-SECRETARIAT
Impossible à dériver → modèle.
Dérivable → compiler/runtime.
Contestable mécaniquement → validator.
Publiable → runtime seulement.

## META-REQ-FLAT-SOURCE
Architecture logique riche, déploiement Source plat et minimal.
Tout nouveau fichier Source permanent doit être justifié.

## META-REQ-NO-REGRESSION
Les capacités déjà fermées restent des regression guards et doivent rester vertes.

## META-REQ-DIFFERENTIAL-REGRESSION
Toute capacité VERIFIED/fermée applicable du parent exact doit rester protégée sur la candidate.
Lorsqu'un replay différentiel est applicable, toute dégradation non explicitement autorisée d'un invariant protégé bloque la candidate.
La suppression silencieuse d'un regression guard, d'une golden fixture ou de son mapping vers le REQ est un échec.
Un défaut nouveau, une fois reproduit, corrigé et fermé par une preuve matérielle, devient un regression guard permanent.
Si la préservation d'une capacité VERIFIED ne peut pas être établie fiablement, aucun PASS ne peut être inventé.

## META-REQ-CHANGE-SURFACE
Toute mutation produit doit être rattachée à une surface de changement explicitement autorisée par le PRE-GO.
Chaque tâche de mutation définit au minimum MUST-TOUCH, MAY-TOUCH, PRESERVE, NO-TOUCH, NON-GOALS, INVARIANTS, DEPENDENCIES, PROOFS MADE STALE et AUTHORIZED DIFF SURFACE.
Toute modification hors surface autorisée, toute violation NO-TOUCH ou tout refactor opportuniste non nécessaire bloque la candidate jusqu'à amendement explicite du PRE-GO.
Après patch, la surface réellement modifiée doit être comparée à la surface autorisée.


## META-REQ-ARTIFACT-PERSISTENCE
L'état critique du chantier ne doit pas dépendre uniquement du chat.
Le DEV_STATE, le PRE-GO actif, la matrice cumulative, le registre REQ et les preuves matérielles nécessaires doivent suffire à reprendre et auditer le chantier.
La persistance reste proportionnée : aucun runtime de développement, orchestrateur ou fichier de receipt par micro-test n'est obligatoire si les artefacts existants suffisent.

## META-REQ-TEST-EVIDENCE
Tout test revendiqué comme exécuté doit correspondre à une exécution réelle et à une preuve matérielle suffisante.
La preuve doit permettre d'identifier au minimum, lorsque disponible et pertinent : commande ou test exécuté, portée, résultat PASS/FAIL/SKIP, exit code, version/artefacts concernés et métriques utiles telles que coverage.
Les états PLANNED, EXECUTED_PASS, EXECUTED_FAIL, SKIPPED, DEFERRED et BLOCKED ne doivent pas être confondus.

## META-REQ-PACKAGE-REPLAY
Une candidate n'est pas qualifiée tant que les bytes packagés exacts n'ont pas été rejoués dans un environnement propre lorsque le protocole le requiert.

## META-REQ-BLACKBOX-INDEPENDENCE
Le Black-Box évalue la candidate telle qu'elle est livrée.
Il ne doit pas être remplacé par l'auto-évaluation du chantier d'implémentation.

## META-REQ-QUIET-EXECUTION
Les opérations internes ne doivent pas produire de bavardage inutile ni de handoff utilisateur sans raison réelle.

## META-REQ-TRANSITION
Avant une transition planifiée de discussion, produire un handoff matériel suffisant pour reprendre sans relire l'ancien chat.

## META-REQ-RECOVERY
Après une coupure involontaire de ChatGPT, la reprise doit utiliser les derniers artefacts matériels disponibles avant toute reconstruction ou répétition.

## META-REQ-DELIVERY
Toute version remise doit fournir séparément, lorsque applicable :
- package Sources ;
- Full Install ;
- consigne générale ;
- prompts/campagne Black-Box ;
- état de développement utile à la reprise.
