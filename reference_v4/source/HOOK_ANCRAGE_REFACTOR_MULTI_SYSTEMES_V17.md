# Hook d’ancrage et refactor de viabilité multi-systèmes

**Version : V17-L3 / V4 Lean RC4**

## AUTHORITY

Seule autorité métier sur la viabilité pratique des architectures comportant plusieurs moteurs, archétypes, packages, économies, modules ou branches structurels.

Elle décide **quoi tester, quel défaut corriger et si la correction est suffisante**. Le registre/validateur matérialisent versions, deltas, fraîcheur, snapshot et preuves ; ils ne jugent jamais la viabilité.

## INPUT

Direction/classification déjà retenue, concept, Style, 1–2 Axes identitaires, systèmes structurels, première decklist provisoire **et `functional_intent.json` gelé lorsqu’un rôle utilisateur explicite existe**.

# 1. Ancrage

Avant optimisation, fixer :

- concept exact ;
- Style ;
- 1–2 Axes identitaires indispensables ;
- systèmes structurels ;
- relation fonctionnelle attendue ;
- ce qui ne peut disparaître sans dénaturer le concept.

**L’ancrage protège l’idée, pas la première liste.**

### Contraintes utilisateur non protégées par défaut

Une taille de package, un ratio arbitraire, un nombre minimal de cartes d’un second système ou une étiquette `Hybride / Intégré` demandés par l’utilisateur ne deviennent pas automatiquement des invariants de l’ancrage.

Ordre obligatoire :

`rôle fonctionnel réel → test adapté → coût d’intégration → taille/ratios justifiés`

et jamais :

`taille demandée → construction forcée → justification après coup`.

Une contrainte quantitative n’est protégée que si la retirer détruit réellement l’identité/concept choisi ; sinon elle reste négociable et peut être compressée ou rejetée pour préserver la viabilité.

# 2. Routage par relation réelle

Identifier le rôle réel des systèmes avant tout test.

### A — Vrai double moteur

Deux systèmes possèdent chacun starters/lignes/économies assez autonomes et doivent régulièrement cohabiter dans les mains.

→ stress test des mains mixtes.

### B — Moteur principal + module spécialisé

Second système = convertisseur, payoff/boss, accès, lock, reprise, branche ciblée, etc.

→ test fonctionnel du module.

### C — Systèmes convergents

Plusieurs systèmes alimentent réellement une économie/condition/payoff/infrastructure commune.

→ test de convergence.

### D — Architecture séquentielle / branches

A prépare B, combo→grind, starter commun→branche, A laisse des résidus que B monétise, etc.

→ test de séquençage.

Une architecture peut nécessiter plusieurs tests, mais ne jamais imposer artificiellement la symétrie A+B.

### Contrôle de dérive par rapport à l’intention gelée

Avant le routage, comparer le rôle réellement construit au rôle `USER_EXPLICIT` du contrat :

- même rôle/fonctions → continuer ;
- simple spécialisation interne compatible → continuer ;
- ajout d’un payoff/axe indépendant qui transforme un `FACILITATOR` ou `MODULE` en seconde architecture → **CONCEPT_DRIFT**.

`CONCEPT_DRIFT` n’est pas un refactor réussi : revenir à la sélection du concept et obtenir une nouvelle intention avant de poursuivre. Il est interdit d’utiliser cette dérive pour protéger une taille de package ou une étiquette demandée.

**Rôle avant volume :** si le système ajouté est principalement décrit ou utilisé comme extenders, corps, matériaux, défausse, pioche, accès Extra Deck ou autre fonction de facilitation, le routage initial est **B — moteur principal + module spécialisé**, sauf preuve fonctionnelle concrète d’une architecture supplémentaire. Le nombre de cartes du package ne peut jamais promouvoir à lui seul un module en second moteur.

# 3. Tests adaptés

## A — Double moteur

Tester plusieurs familles représentatives : A dominant+B mineur, inverse, équilibré, starter A+ressources B, starter B+ressources A.

Bloquer si :

- une moitié devient régulièrement morte ;
- starters se neutralisent ;
- Normal Summon/zones/GY/banish/Extra Deck sont disputés sans bénéfice suffisant ;
- les meilleures mains sont presque toujours « A pur » ou « B pur » ;
- une seule belle main mixte masque deux decks séparés.

Au moins un Axe central réellement mixte et reproductible doit exister si le concept revendique un vrai double moteur.

## B — Module spécialisé

Tester :

1. accessibilité depuis le moteur principal ;
2. traversée naturelle A→B ;
3. coût en slots/cartes mortes ;
4. fonction réellement accomplie ;
5. autonomie du moteur principal quand B n’est pas vu ;
6. valeur ajoutée réelle.

Le module n’a pas besoin de démarrer seul.

## C — Convergence

Une ressource commune passive n’est pas une preuve. Elle devient structurelle si plusieurs systèmes la produisent/accumulent/consomment/convertissent vers le même plan.

Tester contribution régulière, addition réelle, seuil atteint, coût de deckbuilding et utilité des cartes avant le payoff.

## D — Séquençage / branches

Vérifier passage accessible entre étapes, absence de seconde main idéale indépendante, résidus réellement exploitables, coûts critiques compatibles et vraie valeur de la seconde branche.

# 4. Critère universel — coût d’intégration

Question bloquante :

**« Le système ajouté apporte-t-il régulièrement plus de valeur jouable qu’il n’ajoute de cartes mortes, conflits de ressources, dépendances ou exigences de deckbuilding ? »**

Cohésion trouvée ≠ viabilité validée.

# 5. Couverture fonctionnelle ciblée

Pour chaque système, examiner uniquement les fonctions réellement revendiquées par l’ancrage/Axes : starter/autonomie, accès, conversion, payoff, reprise si revendiquée.

Si une fonction est faible/absente/trop conditionnelle, rechercher **une substitution directe crédible** dans le pool qui l’améliore sans coût équivalent ou supérieur.

Tester d’abord :

`slot périphérique actuel → candidat fonctionnel`

Si amélioration matérielle + ancrage préservé → nouvelle version via le registre puis retest.

Arrêter dès que les fonctions revendiquées sont correctement couvertes ; pas de quête du meilleur slot absolu.

# 6. Compression et refactor métier

Avant tout PASS, tenter de réduire plusieurs cartes propres au système secondaire sans perdre presque toute sa valeur structurelle/accès/Axes.

- compression évidente possible → PASS_DIRECT interdit ;
- compression détruit l’ancrage/fonction → concept à réévaluer/abandonner ;
- aucune compression substantielle acceptable → fermeture possible si les autres tests passent.

Si correction nécessaire :

**PROTÉGER → CLASSER → COUVRIR/SUBSTITUER → COMPRESSER → RETESTER**

### PROTÉGER

Isoler pièces qui portent relation, Axes identitaires, accès et conversion définissant le concept.

### CLASSER

Rôle des cartes/packages : accès / conversion / payoff / redondance utile / interne / conditionnelle.

Les internes/conditionnelles périphériques sont candidates prioritaires à la réduction.

### COUVRIR/SUBSTITUER

Corriger une mauvaise allocation de slots avant de seulement couper.

### COMPRESSER

Réduire en priorité : internes marginaux, conditionnelles surjouées, redondances sans route/résilience, infrastructure trop étroite, second archétype complet lorsque son rôle réel n’exige qu’un module.

### RETESTER

Retester la relation réelle et le coût d’intégration sur la **nouvelle version matérialisée par le registre**. Si la relation a changé, rerouter avant le retest.

# 7. Fermeture terminale métier

Sur la version candidate finale :

1. effectuer une tentative concrète de compression avec plusieurs réductions candidates ;
2. identifier les fonctions protégées perdues/dégradées par ces réductions ;
3. conclure métier `FERMÉE` seulement si les réductions acceptables restantes dégradent réellement les fonctions protégées ou l’ancrage ;
4. effectuer le replay terminal à froid exigé par le protocole sur le snapshot figé, en recherchant de nouveaux candidats indépendamment du premier résultat.

Le registre et le validateur sont seuls responsables de matérialiser l’ordre, les versions, candidats, snapshot, hash, replay et reçu. Le présent hook fournit seulement les **jugements métier** nécessaires à ces champs.

# 8. Statuts métier

### PASS_DIRECT

Première version testée ferme le test adapté + coût d’intégration + couverture + compression terminale, sans modification matérielle nécessaire.

### PASS_REFACTOR

Un défaut a nécessité une modification matérielle ; la nouvelle version ferme ensuite tous les contrôles et la compression terminale.

### FAIL_ABANDON

Réussir exigerait de supprimer l’ancrage, ou le budget de refactor autorisé est épuisé sans fermeture.

# 9. Arrêt anti-sur-optimisation

Le hook cherche une construction viable et proportionnée, pas l’optimum mathématique absolu. Une fois les fonctions revendiquées correctement couvertes, le coût acceptable et la compression terminale fermée, arrêter.

## OUTPUT MÉTIER

Pour la version exacte transmise au registre :

- `status: PASS_DIRECT | PASS_REFACTOR | FAIL_ABANDON` ;
- `relation_final` ;
- `test_applied` ;
- `refactor_materialized` ;
- `compression_terminal` ;
- `rerouting_after_refactor` ;
- `exact_version` ;
- `user_constraint_disposition: PRESERVED | REDUCED | REJECTED | NOT_APPLICABLE` ;
- `functional_intent_sha256` ;
- `concept_drift: NONE | DETECTED` ;
- défaut ciblé + deltas métier si refactor ;
- candidats/pertes fonctionnelles pour tentative terminale et replay à froid.

## DO_NOT_DECIDE

Classification, progression, rendu, versioning, fraîcheur, hash, preuve mécanique ou confiance terminale.
