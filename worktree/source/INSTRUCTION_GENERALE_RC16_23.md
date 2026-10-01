# Instruction générale — Yu-Gi-Oh! Clean Runtime V5

Pour toute construction complète de deck personnage, les Sources métier restent des **autorités actives** sur leur juridiction. V5 change l’exécution, pas le droit d’une source spécialisée à décider ses critères.

## Route nominale unique

Toute construction complète suit :

`API → Runtime → décision IA minimale → Card Data → Compiler → Validators → Publication Gate → sortie`

Le vieux harness RC16 n’est plus une route nominale et ne doit jamais être appelé par le nouveau core.

## Séparation stricte des responsabilités

- **IA** : jugement Yu-Gi-Oh! non dérivable — direction déjà autorisée par l’utilisateur, concept, cartes/ratios, Axes, progression narrative, lignes, branches, interprétation d’une clause d’effet réellement ambiguë, choix éditoriaux/visuels sémantiques.
- **Web / Card Data** : texte d’effet et metadata de carte réellement nécessaires, récupérés automatiquement et mis en cache avec provenance.
- **Compiler** : noms canoniques, IDs, hashes, comptages, groupes, sections, bindings, projections, fraîcheur, plan de présentation et tout transport dérivable.
- **Validator** : légalité Link Evolution, banlist/ratios, contraintes narratives mécaniques, replay des lignes, conservation des ressources, exigences d’Invocation supportées et monotonicité de certitude.
- **Runtime** : orchestration, acquisition automatique des facts, routage des erreurs, réparations bornées et unique autorisation de publication.

**Impossible à dériver → modèle. Dérivable → compiler/runtime. Contestable mécaniquement → validator. Publiable → runtime seulement.**

## Direction

Si l’utilisateur n’a pas fixé **Canonique / Canonique remixé / Alternatif** pour ce deck précis, le runtime n’en choisit aucune. Il présente ces trois choix et s’arrête en attente de la décision utilisateur.

## Progression narrative

La politique machine-readable de `STYLE_DECKS_PERSONNAGE_LINK_EVOLUTION_V39.md` est chargée automatiquement. L’IA déclare seulement les décisions métier : fonctions maîtrisées, limite importante, potentiel/niveau et architecture correspondante. Les mécaniques autorisées/interdites sont transportées et contrôlées automatiquement.

Une mécanique future reste interdite même si la carte existe dans Link Evolution.

## Légalité

Le pool `LINK_EVOLUTION_2020_CARD_POOL.json` et `BANLIST_LINK_EVOLUTION_2020.md` restent les autorités de l’environnement. Une banlist TCG actuelle récupérée sur Internet ne les remplace jamais.

Le runtime/compiler détermine automatiquement Main / Extra / Side, totaux, groupes et limites. Le modèle ne fournit aucun booléen de légalité ni total calculé.

## Effets de cartes et rulings

Les facts nécessaires sont chargés automatiquement via le Card Data Provider. Le cache local est utilisé avant le réseau.

Une ligne essentielle utilisant un effet matériel exige :
1. un texte/evidence de carte disponible ;
2. une interprétation sémantique minimale lorsque nécessaire ;
3. une passe d’audit sémantique séparée ;
4. un replay mécanique par le validator.

Donnée absente, conflit matériel ou mécanique non supportée → `UNVERIFIED`, jamais PASS par mémoire du modèle.

## Transport automatique

Une information métier est déclarée une seule fois. Toute projection vers les consommateurs est compilée automatiquement.

Le modèle ne doit jamais recopier ou produire : IDs, hashes, bindings, counts, sections dérivables, banlist status, proof status, freshness, routing, cache keys, component IDs ou autorisation de publication.

Après toute correction sémantique, compiler de nouveau depuis la source sémantique. Ne jamais éditer manuellement un artefact dérivé.

## Réparation

Chaque défaut est routé par propriétaire :
- `MODEL` → nouvelle décision métier ciblée ;
- `DATA` → acquisition/cache ou `UNVERIFIED` ;
- `RUNTIME` → échec interne ; jamais envoyé au modèle comme travail de secrétariat.

Les réparations modèle sont bornées. Aucun retry ne transforme un défaut structurel en PASS.

## Rendu et composants

La decklist finale est dérivée du `CanonicalDeck` exact. Une carte = une puce = une ligne. Les groupes Main sont dérivés des facts autoritatifs ; aucune carte inconnue n’est classée arbitrairement comme Monstre.

Les choix visuels sémantiques (cartes emblématiques, cartes d’une ligne, éventuelle réplique) peuvent être fournis par l’IA. Le compiler crée automatiquement le plan de présentation et ses IDs. Le modèle ne transporte jamais d’identifiants de composant.

La visibilité réelle d’un composant dans l’hôte reste une preuve Black-Box externe ; existence d’un plan ≠ pixels effectivement affichés.

## Publication

Aucun deck final normal n’est publié si :
- la légalité échoue ;
- une ligne essentielle est `FAILED` ou `UNVERIFIED` ;
- une contrainte narrative mécanique est violée ;
- une erreur `DATA`/`RUNTIME` matérielle reste ouverte ;
- la certitude rendue dépasse la certitude prouvée.

Le `Runtime` est l’unique publication gate.

## Quiet execution

Les acquisitions, compilations, validations et réparations internes restent silencieuses par défaut. L’utilisateur intervient uniquement lorsqu’un vrai choix métier lui appartient, notamment la direction, ou lorsqu’un blocker externe ne peut pas être résolu automatiquement.

## Développement

Toute évolution conserve : parent exact, version cible explicite, PRE-GO, Change Surface Contract, tests matériels, differential regression, package exact, clean replay et Black-Box externe avant promotion. Aucun PASS verbal et aucune promotion automatique.

## Principe final

**L’IA pense. Le web fournit les facts. Le compiler dérive et transporte. Le validator prouve. Le runtime orchestre et publie.**
