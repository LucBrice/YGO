# COMMANDES_DEV_YGO — V1

## Rôle

Commandes conventionnelles réutilisables du projet de développement.
Elles ne sont pas des commandes natives de ChatGPT : elles décrivent un protocole que ChatGPT doit appliquer.

---

## /status

But :
Afficher l'état réel du chantier courant.

Inclure :
- version / parent / candidate connus ;
- promotion autorisée ou non ;
- REQ OPEN / STALE / REGRESSED / VERIFIED ;
- blockers ;
- prochain pas ;
- dernier état matériel connu des tests/preuves lorsque pertinent.

Ne rien inventer si les artefacts de chantier ne sont pas disponibles.

---

## /engineering
Alias : `/intent`

But :
Créer ou mettre à jour l'Engineering Intent à partir des défauts réellement observés.

Sortie :
- intent ;
- user story utilisateur ;
- user story IA ;
- architecture logique ;
- REQ nouveaux / mis à jour ;
- invariants ;
- non-goals ;
- surfaces de changement pressenties lorsque le chantier implique une mutation.

Mettre à jour l'intent existant si le problème appartient au même chantier.

---

## /matrix

But :
Produire ou mettre à jour la matrice cumulative de changement et de preuve :

`REQ → tâche → RED/KILL → MUST-TOUCH → MAY-TOUCH → PRESERVE → NO-TOUCH → NON-GOALS → INVARIANTS → DEPENDENCIES → PROOFS MADE STALE → AUTHORIZED DIFF SURFACE → UNIT → RED/FAILURE → GREEN/HAPPY → LINE COVERAGE → BRANCH COVERAGE → INTEGRATION → MUTATION → E2E → Differential Parent/Candidate → full regression → preuve → PASS`

Pour chaque niveau de test, enregistrer lorsque pertinent : `REQUIRED?`, `SCOPE`, `GATE/TIMING`, `COST CLASS`, `EXPECTED PROOF`, et s'il est différé, `DEFERRED UNTIL GATE`.

Après exécution, enregistrer l’état réel : `PLANNED`, `EXECUTED_PASS`, `EXECUTED_FAIL`, `SKIPPED`, `DEFERRED` ou `BLOCKED`, avec la commande/test exécuté et la preuve matérielle utile. Ne jamais convertir automatiquement un test planifié en test exécuté.

Toujours partir des REQ existants lorsqu'ils sont disponibles.

Les localisations de code doivent privilégier `fichier → symbole/fonction/classe → responsabilité → call path`. Les numéros de lignes ne sont qu'une aide de localisation sur le parent exact.

---

## /coverage

But :
Auditer la couverture réelle.

Vérifier :
- REQ sans test ;
- test sans REQ ;
- REQ STALE ;
- REGRESSED ;
- dernière version VERIFIED ;
- last-known-good ;
- tests réellement exécutés ;
- preuves manquantes ;
- capacité VERIFIED sans regression guard/golden fixture applicable ;
- regression guard/golden fixture supprimé ou non mappé ;
- divergence Parent → Candidate non autorisée ;
- tâche de mutation sans Change Surface Contract ;
- Actual Diff Surface hors Authorized Diff Surface ;
- violation NO-TOUCH ;
- preuve matériellement affectée mais non marquée STALE ;
- surface modifiée sans unit tests lorsque la logique est testable isolément ;
- RED/failure-path manquant pour un défaut ou refus matériel ;
- GREEN/happy-path symétrique manquant lorsque applicable ;
- interaction multi-composants sans integration test pertinent ;
- line coverage insuffisante sur les lignes modifiées critiques ;
- branch coverage insuffisante sur les branches modifiées et failure paths critiques ;
- mutation test absent lorsque la solidité des assertions doit être démontrée ;
- E2E absent alors que le comportement traverse plusieurs couches critiques ;
- test coûteux exécuté trop tôt sans bénéfice de preuve, à signaler comme inefficience ;
- test coûteux différé au-delà du gate où il devient obligatoire ;
- PASS fondé uniquement sur un pourcentage de coverage ;
- test marqué exécuté sans preuve matérielle suffisante ;
- divergence entre matrice, registre REQ, DEV_STATE et résultats réellement disponibles ;
- dépendance à la mémoire du chat pour connaître un PASS, un FAIL ou le NEXT_STEP.

---

## /prego

But :
Préparer le chantier avant implémentation.

Doit matérialiser :
- parent exact ;
- cible si déjà donnée, sinon NOT_ASSIGNED ;
- scope REQ ;
- tâches ;
- RED/KILL ;
- positive controls ;
- pour chaque tâche de mutation : MUST-TOUCH, MAY-TOUCH, PRESERVE, NO-TOUCH, NON-GOALS, INVARIANTS, DEPENDENCIES, PROOFS MADE STALE et AUTHORIZED DIFF SURFACE ;
- pour chaque tâche : TEST LEVELS REQUIRED parmi UNIT, RED/FAILURE-PATH, GREEN/HAPPY-PATH, INTEGRATION, LINE COVERAGE, BRANCH COVERAGE, MUTATION, E2E, DIFFERENTIAL, FULL REGRESSION ;
- TEST TIMING/GATE pour chaque niveau ;
- TEST SCOPE : local / affected / cumulative / packaged ;
- COST CLASS ou coût relatif ;
- LINE COVERAGE SCOPE et BRANCH COVERAGE SCOPE ;
- MUTATION SCOPE ;
- INTEGRATION SCOPE ;
- E2E REQUIRED? avec justification ;
- DEFERRED UNTIL GATE pour les tests coûteux reportés ;
- baseline des capacités VERIFIED/protégées applicable au chantier ;
- golden fixtures/regression guards à rejouer ;
- stratégie Differential Regression Gate Parent → Candidate lorsque applicable ;
- mutants, y compris mutants de la barrière anti-régression lorsque pertinent ;
- Red-Team ;
- End-to-End requis et son gate d'exécution ;
- full regression cumulative ;
- coverage technique cumulative prévue lorsque pertinente, sans utiliser le pourcentage seul comme preuve de correction ;
- packaging/replay ;
- conditions de PASS/FAIL/BLOCKED ;
- stratégie de persistance minimale des preuves : ce qui sera conservé dans la matrice/DEV_STATE et quelles preuves dédiées sont réellement nécessaires ;
- NEXT_STEP.

Aucune mutation.

Si la version cible n'est pas connue, demander à l'utilisateur avant GO.

---

## /go <version>

But :
Autoriser l'implémentation sur la version explicitement donnée.

Préconditions :
- PRE-GO courant ;
- parent identifié ;
- version fournie par l'utilisateur ;
- Change Surface Contract figé pour toute tâche de mutation ;
- baseline/regression guards applicables identifiés ;
- plan de test risk/cost-aware figé par tâche, avec tests chers positionnés à leur gate approprié ;
- artefacts de chantier suffisants pour enregistrer l’exécution réelle sans dépendre du chat.

Le GO n'autorise que les tâches, REQ et surfaces explicitement figés dans le PRE-GO courant.

Interdit :
- inventer la version ;
- élargir silencieusement le scope ;
- toucher une surface NO-TOUCH ;
- modifier une surface hors Authorized Diff Surface sans amendement PRE-GO ;
- effectuer un refactor opportuniste non requis ;
- supprimer silencieusement un regression guard/golden fixture ;
- promouvoir automatiquement.

---


## Règle d'exécution matérielle des tests

Quand une commande de développement conduit à exécuter des tests :
- utiliser directement les outils disponibles ;
- ne pas créer d'orchestrateur dédié sauf besoin explicitement démontré ;
- exécuter uniquement les niveaux prévus au gate courant par le PRE-GO ;
- enregistrer dans la matrice/DEV_STATE ce qui a réellement été exécuté ;
- conserver une preuve dédiée seulement si elle est nécessaire à l'audit, au package, au Black-Box, à une transition ou à la reproduction d'un défaut ;
- en cas de FAIL/BLOCKED, ne pas lancer automatiquement les tests plus coûteux qui dépendent de ce gate.

---

## /kill <nom>

But :
Auditer un Black-Box/KILL.

Pour chaque plainte :
- régression réelle ;
- défaut encore ouvert ;
- friction normale ;
- recommandation redondante ;
- recommandation hors juridiction/dangereuse.

Mettre à jour les REQ existants avant d'en créer de nouveaux.

Ne pas patcher automatiquement pendant une campagne d'observation.

---

## /blackbox

But :
Préparer une campagne Black-Box sur une candidate qualifiée déterministement.

Produire séparément :
- campagne ;
- prompts de cas ;
- consigne générale de la version ;
- rappel des KILL/positive controls.

---

## /package

But :
Construire la livraison exacte de la candidate.

Vérifier :
- package plat ;
- hashes ;
- extraction propre ;
- replay des bytes exacts ;
- cohérence des fichiers livrés ;
- présence des regression guards/golden fixtures exigés par le PRE-GO ;
- absence de suppression silencieuse d'une capacité protégée ;
- cohérence de l'Actual Diff Surface avec l'Authorized Diff Surface lorsque ces preuves font partie de la candidate.

---

# Commandes de continuité de discussion

## /fin-session
Alias : `/transition`

### Usage
Pour un **changement de discussion planifié**.

### But
Terminer proprement le chat courant et produire uniquement ce qu'il faut transporter vers le suivant.

### Obligations

Avant de répondre :
1. réconcilier l'état réel du chantier ;
2. mettre à jour le registre REQ réel ;
3. matérialiser le DEV_STATE / état courant ;
4. réconcilier les tests réellement exécutés avec la matrice et les preuves disponibles ;
5. enregistrer :
   - DONE ;
   - ACTIVE ;
   - TODO ;
   - BLOCKED ;
   - tests réellement exécutés ;
   - versions/hashes utiles ;
   - fichiers nécessaires ;
   - NEXT_STEP unique ;
6. produire un prompt de continuation.

### Livrables

Produire un petit bundle contenant au minimum :
- `DEV_STATE_...`
- `REGISTRE_REQUIREMENTS_...`
- PRE-GO actif si nécessaire ;
- matrice active si nécessaire ;
- fichiers de preuve explicitement indispensables au NEXT_STEP ;
- `PROMPT_CONTINUATION_SESSION.md`

Ne pas embarquer automatiquement tout l'historique.

### Prompt final attendu

Le prompt doit dire au nouveau chat :
- quels fichiers sont joints ;
- dans quel ordre les lire ;
- quel est le NEXT_STEP ;
- ce qui est interdit ;
- qu'il ne doit pas recréer l'historique ni changer de version.

---

## /continuer-session

### Usage
Dans le **nouveau chat après une transition planifiée**.

### Entrée
L'utilisateur joint le bundle produit par `/fin-session`, puis écrit `/continuer-session`.

### Procédure
1. lire les fichiers joints ;
2. vérifier leur cohérence ;
3. identifier le NEXT_STEP ;
4. ne pas rejouer ce qui est DONE ;
5. ne pas changer la version ;
6. poursuivre directement.

Si une donnée indispensable manque, demander uniquement cette donnée.

---

## /reprise

### Usage principal
Pour une **coupure involontaire de ChatGPT dans la même discussion ou juste après une interruption**, pas comme workflow normal de changement de chat.

Exemples :
- réponse coupée ;
- exécution interrompue ;
- contexte runtime partiellement avancé ;
- l'utilisateur écrit "reprend".

### Procédure
1. rechercher le dernier DEV_STATE / checkpoint / artefact matériel ;
2. vérifier si le workspace a avancé plus loin que l'état enregistré ;
3. réconcilier avant de rejouer ;
4. reprendre au premier point réellement incomplet ;
5. ne jamais créer un nouveau run/version si le même run peut être repris ;
6. ne pas répéter les milestones déjà DONE.

### Interdit
Utiliser `/reprise` pour masquer une mauvaise coupure récurrente du système.
Une coupure sans USER_REQUIRED/FATAL reste un défaut de continuité à enregistrer.
