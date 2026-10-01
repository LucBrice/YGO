# Hook d’exploration conceptuelle — Decks personnages

**Version : V7-L2 / V4 Lean RC4**

## AUTHORITY

Génère et diversifie les concepts avant sélection. Ne fixe ni classification finale, ni potentiel, ni viabilité multi-systèmes.

## INPUT

Lorsque l’utilisateur a explicitement attribué une fonction à un système ajouté, consommer le `functional_intent.json` gelé par `VALIDATION_CANONIQUE_REMIXE` **avant** l’exploration.

Un rôle `USER_EXPLICIT` n’est pas une cible à améliorer pour sauver une étiquette : il borne la piste courante. Une idée qui exige de le transformer en véritable seconde architecture doit être exposée comme **nouvelle piste** et ne peut être sélectionnée silencieusement dans le même run.


Personnage, stade narratif, direction si déjà fixée, contraintes de pool/banlist/mécaniques.

## GATE — divergence obligatoire

Avant de retenir une piste, explorer intérieurement des concepts provenant d’au moins **4 origines différentes** parmi :

- cartes/archétype canoniques ;
- boss / finisher ;
- condition de victoire ;
- mécanique d’Invocation/conversion ;
- interaction précise ;
- loop / lock / OTK / FTK / burn / contrôle / grind ;
- économie/boucle de ressources ;
- moteur extérieur ;
- propriété de règle exploitable.

Ne pas arrêter l’idéation à la première variante fonctionnelle « archétype canonique + moteur X ».

### Boss / condition de victoire

Lorsqu’une possibilité crédible existe dans le pool et l’époque, tester au moins une piste née d’un boss/finisher/condition de victoire inhabituelle. Boss tardif ≠ automatiquement prématuré : la progression juge les compétences nécessaires.

## Contrat minimal d’un candidat

Chaque candidat doit pouvoir être résumé par :

- **Style** : 1–3 tags ;
- **Mécanique / concept** : structure qui organise réellement le deck ;
- **Fonction** : ce que cette structure produit/contrôle/convertit/menace ;
- **Boss / finisher** : conversion terminale éventuelle.

« Fonction = invoquer le boss plus vite » est insuffisant.

## Préfiltre multi-systèmes

Pour un candidat multi-systèmes, vérifier seulement qu’une relation fonctionnelle crédible existe : accès, conversion, payoff, économie commune, lock, résidu, séquençage, vraie double motorisation, etc.

Une ressource commune seule (Attribut/Type/Niveau/zone/matériau) n’est pas une preuve.

La viabilité réelle appartient ensuite à `HOOK_ANCRAGE_REFACTOR_MULTI_SYSTEMES`.

## STOP SELECTION

Avant sélection :

1. 4+ origines réellement explorées ?
2. piste boss/condition testée lorsque pertinente ?
3. au moins une idée hors supports naturels du canonique ?
4. pistes différentes par mécanique/fonction/économie/condition/payoff, pas seulement par moteur secondaire ?
5. pas de répétition « canonique + X » ?
6. multi-systèmes manifestement injouables éliminés sans prétendre valider les autres ?

Si non → refaire l’exploration.

Puis seulement : filtrer par identité + progression → sélectionner → classifier. Si Canonique remixé envisagé, exécuter son autorité spécialisée.

Ne pas fabriquer un boss/payoff propre à un système explicitement décrit comme facilitateur/module dans le seul but de rendre `Hybride`, `Intégré` ou une taille de package plus défendable. Cette transformation est `CONCEPT_DRIFT` et doit retourner à la sélection de concept.

## OUTPUT

Candidats filtrés et sélectionnés, chacun avec Style / Mécanique / Fonction / Boss.

## DO_NOT_DECIDE

Classification détaillée, stade final, ratios, viabilité multi-systèmes, rendu.
