# Hook Style → Axes → Construction — Decks personnages

**Version : V19-L2 / V4 Lean RC12**

## AUTHORITY

Matérialise le Style par des Axes fonctionnels puis construit la decklist autour de ces Axes. Produit aussi le contenu de pilotage transmis au rendu.

## Principe

**Style = promesse de fonctionnement. Axes = preuve fonctionnelle. Decklist = support matériel de cette preuve.**

Ne jamais construire une « bonne liste » puis inventer après coup des combos qui justifient son Style.

## INPUT

Concept sélectionné, Style, contraintes de progression/direction/contexte, relation multi-systèmes éventuelle.


# Entrée obligatoire — contrat narratif frais

Avant tout Axe ou première decklist, recevoir le `narrative_contract.json` frais du `run_id` courant.

Appliquer sans redéfinir la chronologie :

- aucune carte, moteur, conversion, payoff ou ligne ne peut employer une mécanique dans `forbidden_mechanics` ;
- toute mécanique proposée dans un Axe doit appartenir à `allowed_mechanics` ;
- support moderne seulement s’il respecte le contrat et les autres limites de progression ;
- climax / très avancé / potentiel élevé ne contourne jamais le contrat.

Le premier `deck-vN` doit être sérialisé en snapshot complet avant transmission au contrôle narratif post-construction.

Aucun argument de viabilité multi-systèmes ne peut utiliser positivement une carte/ligne tant que `NARRATIVE_CONFORMANCE_CLOSED` n’est pas frais sur ce snapshot exact.

**Le contrat narratif est une entrée de construction, pas un souvenir conversationnel.**

# 1. Style → résultat recherché

Pour chaque tag fonctionnel central, définir ce que le deck doit réellement accomplir puis concevoir les interactions capables de le produire.

Exemples :

- OTK : lethal dans le même tour ;
- FTK : condition de victoire fermée T1 ;
- Control : interruptions/épuisement renouvelables ;
- Lock : actions adverses effectivement indisponibles ;
- Burn : conversion mesurable en dégâts d’effet ;
- Grind/Reanimation : récupération/boucle répétée d’avantage ;
- Swarm : plusieurs corps générés dans la séquence ;
- Toolbox : embranchements vers des réponses réellement différentes ;
- Climb/Combo : vraie chaîne de conversions.

Un Style fonctionnel **central** cherche normalement au moins **2 Axes distincts** qui l’accomplissent par routes/conversions/payoffs différents.

Ne comptent pas comme second Axe : autre starter vers la même chaîne, extender équivalent, boss de rôle identique ou variante cosmétique.

Exception : architecture intrinsèquement mono-ligne si un second Axe dégraderait réellement le concept.

## 2. OTK / FTK

Avant la decklist, identifier au moins une ligne théorique valide ; si OTK/FTK est central, chercher deux lignes distinctes lorsque l’architecture le permet.

Après construction, vérifier les pièces/ratios.

- OTK : dégâts/attaques/burn doivent fermer le lethal annoncé ;
- FTK : condition de victoire et chaîne T1 explicites.

Sinon retirer le tag ou reconstruire.

## 3. Contrat de reproductibilité d’un Axe important

Pour chaque Axe central/signature/OTK/FTK/Lock/Climb ou ordre critique :

`ressources réelles → première action → cible/recherche → ordre des conversions → ressource à conserver → branche éventuelle → payoff → état final`

Une décision essentielle ne peut pas rester implicite.

Ajouter seulement lorsqu’ils changent réellement le pilotage : restriction, choke point, erreur fréquente.

Test : avec seulement la main/ressource annoncée et l’Axe, l’utilisateur peut-il conduire la ligne jusqu’au résultat sans inventer une étape ? Non → ligne incomplète.

### Fermeture de l’état physique

Pour toute ligne complexe où la continuation dépend de l’état du Terrain, fermer explicitement les contraintes physiques pertinentes :

- occupation et libération des zones ;
- destination légale d’une Invocation Extra Deck lorsqu’elle change la suite ;
- Tokens/corps qui consomment une zone ;
- Niveaux/Rangs/Link Ratings et statut Tuner/non-Tuner réellement disponibles ;
- restrictions actives au moment exact de la conversion.

Si une ligne ne fonctionne que lorsque le joueur place un monstre dans une zone précise, **ce placement est une décision essentielle et doit apparaître dans la ligne**.

Une séquence qui n’est légale que sous un placement implicite non indiqué est incomplète et ne peut pas être transmise comme ligne reproductible.

## 4. Axe / Starter / Branche / Combo

Transmettre explicitement la hiérarchie réelle :

- **Axe** = plan structurel ;
- **Starter** = porte d’entrée ;
- **Branche** = choix alternatif significatif dans le même Axe ;
- **Combo/ligne** = séquence exécutable.

Ne jamais créer artificiellement une Branche ou un nouvel Axe pour le rendu.

### Couverture starters

Identifier tous les starters structurellement importants de la **decklist finale**. Chacun doit avoir au moins une ligne concrète d’entrée dans son Axe.

Regrouper uniquement les starters fonctionnellement interchangeables. Séparer si l’ouverture change ordre, cible, ressource conservée, restriction, branche, payoff ou état final.

### RC12 — exploration multi-starters à préserver

La discipline du harness ne réduit jamais la recherche au premier starter évident. **Avant de fermer la construction, rechercher activement les différentes portes d’entrée structurelles réellement présentes dans la decklist finale.**

- plusieurs starters utiles vers le même Axe restent plusieurs portes d’entrée ;
- ils peuvent partager un même tronc commun lorsqu’ils sont réellement équivalents de bout en bout, mais cette équivalence doit être explicitement transmise ;
- ils restent séparés dès que séquençage, cible, ressource conservée, restriction, branche, payoff ou état final diffère ;
- ne jamais supprimer un starter structurel valable uniquement pour simplifier la validation mécanique ;
- inversement, ne pas créer des starters ou combos artificiels lorsqu’ils reproduisent exactement le même pilotage.

Transmettre à `VALIDATION_PILOTAGE_LIGNES_DECKS_PERSONNAGES` un **inventaire explicite des starters structurels retenus**, avec leur Axe et les lignes qui les couvrent. L’autorité de pilotage le réévalue sur la decklist finale. Le harness vérifie seulement que cet inventaire déclaré est intégralement couvert ; il ne choisit jamais les starters.

## 5. Lignes situationnelles

Après la construction, rechercher activement les situations qui produisent une décision réellement différente : starter naturel, main forte/mixte/imparfaite encore jouable, milieu de duel, finisher disponible après setup, going second, continuation après interruption si elle existe réellement.

**Utilité marginale > quota.** Ne retenir que les situations qui enseignent une décision/conversion/séquençage supplémentaire.

Toute ressource indispensable doit être présente au départ ou légalement obtenue pendant la ligne. Un finisher tardif ne doit pas devenir un faux starter.

Si plusieurs plans concurrents existent réellement, transmettre une règle simple `situation observable → plan`.

Ne jamais inventer de résilience pour remplir une rubrique.

## 6. Construction autour des Axes

Les ratios doivent servir les fonctions : starters, extenders, converters, payoffs/finishers et protections/contrôles structurels.

## 7. Multi-systèmes

Si plusieurs systèmes/économies/packages sont structurels, suspendre la promotion de la liste et exécuter `HOOK_ANCRAGE_REFACTOR_MULTI_SYSTEMES`.

Un Axe convaincant ≠ PASS de viabilité.

## STOP

Avant transmission :

1. chaque tag fonctionnel majeur est démontré ?
2. deux Axes distincts existent quand le Style central le permet ?
3. les Axes sont réellement différents ?
4. ratios et cartes soutiennent les lignes ?
5. ressources annoncées sont réalistes ?
6. starters structurels sont couverts ?
7. multi-systèmes : statut valide sur la version exacte ?

Sinon reconstruire Axe/ratios ou retirer le tag.

## OUTPUT

- Axes fonctionnels ;
- starters structurels + inventaire multi-starters explicite ;
- branches réelles ;
- lignes reproductibles ;
- contraintes physiques/placement explicités lorsqu’ils conditionnent une ligne ;
- restrictions/choke points/erreurs importantes ;
- guide de décision si nécessaire ;
- decklist construite autour de ces sorties.

## DO_NOT_DECIDE

Progression narrative, classification détaillée, viabilité multi-systèmes, présentation visuelle, versioning/preuves du harness.

---

## Addendum RC16.23 — inventaire structurel matérialisé

Lorsque les Axes sont fermés pour une decklist complète destinée au Pilotage, la sortie de la présente autorité doit matérialiser un **inventaire structurel indépendant du rendu**. Cet artefact reste une simple matérialisation de décisions déjà prises ici ; il ne crée aucune nouvelle autorité.

L'inventaire transmet au minimum, pour chaque ligne requise :

- l'Axe auquel elle appartient et une ancre de rendu stable ;
- les starters structurels déjà identifiés par le présent hook ;
- les branches / replays distincts réellement requis ;
- lorsque plusieurs starters partagent une même ligne, une déclaration explicite d'équivalence de pilotage et sa base métier.

Le shell peut attribuer des identifiants techniques manquants, mais il lui est interdit de décider qu'un starter est valide, que deux starters sont équivalents, qu'une branche est inutile ou qu'un replay unique suffit.

**Même Axe ≠ même pilotage.** Les starters restent distincts lorsqu'ils modifient matériellement le séquençage, la cible, la ressource conservée, la restriction, la branche, le payoff ou l'état final.

Cette sortie est ensuite consommée par le Builder et comparée au rendu par `VALIDATION_PILOTAGE_LIGNES_DECKS_PERSONNAGES`. Le rendu ne peut jamais devenir la source de vérité de l'inventaire qu'il doit préserver.
\n\n### Sérialisation minimale obligatoire de l'inventaire\n\nPour éviter qu'une décision métier correcte reste inutilisable par les instruments, la sortie structurée de `STYLE_AXES_CLOSED` matérialise l'inventaire sous la forme suivante :\n\n```json\n{\n  "structural_inventory": {\n    "schema": "ygo-style-axes-structural-inventory-v1",\n    "lines": [\n      {\n        "line_id": "identifiant_technique_optionnel",\n        "axis_heading": "titre exact de l'Axe",\n        "render_token": "ancre stable devant survivre au rendu",\n        "starters": [\n          {\n            "starter_id": "identifiant_technique_optionnel",\n            "display": "starter structurel déjà décidé",\n            "render_token": "texte/ancre devant survivre au rendu"\n          }\n        ],\n        "replays": [\n          {"replay_id": "identifiant_technique_optionnel"}\n        ]\n      }\n    ]\n  }\n}\n```\n\nSi plusieurs starters sont réellement équivalents et partagent la même ligne, cette ligne ajoute obligatoirement :\n\n```json\n"starter_grouping": {\n  "equivalent": true,\n  "basis": "raison métier explicite déjà décidée par le présent hook"\n}\n```\n\nSinon, les starters dont le pilotage diffère sont matérialisés dans des lignes distinctes. Le shell peut compléter uniquement les identifiants techniques absents ; il ne peut jamais inventer `equivalent: true`, une branche, un replay ou un starter.\n\nUne sortie `STYLE_AXES_CLOSED` dépourvue de cet inventaire transmissible est **incomplète et ne doit pas recevoir PASS/REFACTOR**.\n

---
## RC16.23 — Single Semantic Entry des starters

Lorsqu'un starter structurel est matérialisé pour le runtime, l'autorité transmet **une seule fois** les ressources métier minimales qui le composent (`resources` : noms de cartes/ressources lisibles). Cette liste appartient à Style→Axes parce qu'elle exprime ce qu'est réellement le starter ; elle n'est pas un ledger mécanique.

Le runtime peut ensuite dériver IDs, allocations de copies, labels, bindings, couverture et représentations Pilotage. Il est interdit de demander au modèle de recopier ces mêmes ressources dans plusieurs inventaires techniques. Si la donnée amont existe mais disparaît en aval, le défaut appartient au compilateur/runtime, pas à la construction métier.
