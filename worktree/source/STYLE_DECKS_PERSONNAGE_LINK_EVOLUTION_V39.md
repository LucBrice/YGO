# Philosophie de construction des decks — Link Evolution

**Version : V40-L1 / V4 Lean**

## AUTHORITY

Source générale de philosophie et de routage métier pour les decks de personnages.  
Elle définit l’identité du personnage, les trois directions, la philosophie générale, l’échelle de potentiel et la chronologie des mécaniques.  
Elle ne recrée jamais les critères des autorités spécialisées.

## Référence de jeu

Contexte par défaut : **Yu-Gi-Oh! Legacy of the Duelist: Link Evolution**, pool et banlist du projet, sauf demande explicite contraire.

## 1. Identité du personnage

Le deck doit ressembler à quelque chose que le personnage pourrait réellement construire à ce stade, sans l’obliger à conserver son archétype canonique.

Trois directions seulement :

- **Canonique** : identité/archétype canonique structurel, optimisé ou spécialisé sans seconde architecture significative ;
- **Canonique remixé** : identité canonique structurelle + seconde architecture significative ; Hybride/Intégré appartient à `VALIDATION_CANONIQUE_REMIXE` ;
- **Alternatif** : autre architecture cohérente avec la personnalité, la manière de gagner et l’évolution du personnage.

Le Canonique n’est jamais choisi par défaut simplement parce qu’il est historique.

### Direction non fixée

Personnage, adversaire, duel ou arc ne suffisent pas à fixer une direction.  
Si l’utilisateur n’a pas choisi pour ce deck précis : présenter brièvement Canonique / Canonique remixé / Alternatif ou demander son choix selon STRUCTURE.

## 2. Philosophie

Chercher des stratégies fortes, ingénieuses ou broken lorsque le contexte les permet : OTK/FTK, locks, burn, contrôle, loops, moteurs de ressources, toolbox, anti-méta ou exploitation intelligente des règles.

La puissance seule ne suffit pas : la construction doit exprimer le personnage et son stade.

L’identité est un **filtre de cohérence**, pas l’unique point de départ.

Avant sélection : `HOOK_EXPLORATION_CONCEPTUELLE_DECKS_PERSONNAGES`.  
Avant decklist : `HOOK_STYLE_AXES_CONSTRUCTION_DECKS_PERSONNAGES`.

Un boss/finisher ne doit pas dicter seul tout le concept : partir de la fonction et de la structure recherchées, puis vérifier si le boss est un payoff adapté.

## 3. Chronologie des mécaniques — source de vérité

Une mécanique future reste interdite même si ses cartes existent dans Link Evolution.

Lecture humaine :

- Duel Monsters : Rituel, Fusion ;
- GX : Rituel, Fusion ;
- 5D's : + Synchro ;
- ZEXAL : + Xyz ;
- ARC-V : + Pendulum ;
- VRAINS : + Link et mécaniques antérieures.

Une carte imprimée plus tard peut être utilisée si elle est dans le pool, légale, n’introduit aucune mécanique future et reste appropriée au stade narratif.

**Support moderne autorisé ≠ fonction moderne automatiquement maîtrisée.**

Climax / potentiel élevé ≠ changement d’époque.

Le runtime ne doit jamais hardcoder cette chronologie : la projection machine-readable ci-dessous est la source exécutable qu’il lit.

<!-- NARRATIVE_MECHANICS_POLICY_JSON:BEGIN -->
```json
{
  "schema_version": 1,
  "mechanic_universe": [
    "Ritual",
    "Fusion",
    "Synchro",
    "Xyz",
    "Pendulum",
    "Link"
  ],
  "eras": {
    "Duel Monsters": {
      "allowed": [
        "Ritual",
        "Fusion"
      ],
      "forbidden": [
        "Synchro",
        "Xyz",
        "Pendulum",
        "Link"
      ]
    },
    "GX": {
      "allowed": [
        "Ritual",
        "Fusion"
      ],
      "forbidden": [
        "Synchro",
        "Xyz",
        "Pendulum",
        "Link"
      ]
    },
    "5D's": {
      "allowed": [
        "Ritual",
        "Fusion",
        "Synchro"
      ],
      "forbidden": [
        "Xyz",
        "Pendulum",
        "Link"
      ]
    },
    "ZEXAL": {
      "allowed": [
        "Ritual",
        "Fusion",
        "Synchro",
        "Xyz"
      ],
      "forbidden": [
        "Pendulum",
        "Link"
      ]
    },
    "ARC-V": {
      "allowed": [
        "Ritual",
        "Fusion",
        "Synchro",
        "Xyz",
        "Pendulum"
      ],
      "forbidden": [
        "Link"
      ]
    },
    "VRAINS": {
      "allowed": [
        "Ritual",
        "Fusion",
        "Synchro",
        "Xyz",
        "Pendulum",
        "Link"
      ],
      "forbidden": []
    }
  }
}
```
<!-- NARRATIVE_MECHANICS_POLICY_JSON:END -->

## 4. Progression et potentiel

Question directrice :

**« Quel deck ce personnage pourrait-il réellement avoir construit à ce stade de son évolution ? »**

La progression opérationnelle et la cohérence finale appartiennent exclusivement à `VALIDATION_PROGRESSION_NARRATIVE`.

Une victoire/défaite n’augmente pas automatiquement le potentiel : progression seulement si le personnage apprend et intègre réellement une capacité dans son deckbuilding/pilotage.

Échelle de potentiel :

- **1–2** : embryonnaire ;
- **3–4** : identité claire mais rigide ;
- **5–6** : maîtrise réelle du style ;
- **7–8** : très abouti, adaptation et couches cohérentes ;
- **9** : quasi-accomplissement personnel ;
- **10** : potentiel personnel pleinement réalisé dans le cadre choisi.

Niveau stratégique séparé : rudimentaire / en développement / solide / avancé / très avancé / quasi optimal.

La valeur finale de ces métriques appartient à `VALIDATION_PROGRESSION_NARRATIVE`.

## 5. Routage spécialisé

- piste Remixée → `VALIDATION_CANONIQUE_REMIXE` ;
- plusieurs systèmes/packages/économies structurels → `HOOK_ANCRAGE_REFACTOR_MULTI_SYSTEMES` ;
- Style fonctionnel → `HOOK_STYLE_AXES_CONSTRUCTION_DECKS_PERSONNAGES` ;
- lignes destinées au joueur → `VALIDATION_PILOTAGE_LIGNES_DECKS_PERSONNAGES` ;
- rendu → sources STRUCTURE uniquement après fermeture métier.

Classification ≠ viabilité.

Hybride / Intégré sont descriptifs, jamais des niveaux de qualité.

## OUTPUT

- direction résolue ou trois directions à présenter ;
- chronologie/mécaniques disponibles via la politique ci-dessus ;
- routage vers les autorités spécialisées.

## DO_NOT_DECIDE

Critères détaillés de Canonique remixé, stade narratif final, viabilité multi-systèmes, contenu fonctionnel des Axes, rendu, versioning ou preuves mécaniques.
