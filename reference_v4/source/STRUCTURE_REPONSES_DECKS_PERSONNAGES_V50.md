# Structure des réponses — Decks personnages

**Version : V55 / RC16.14**

## 1. Rôle du document

Cette source définit uniquement **le front-end des réponses** pour les decks de personnages.

Elle ne décide pas :
- comment construire le deck ;
- comment valider la progression narrative ;
- comment classifier Canonique / Canonique remixé / Alternatif ;
- comment valider Hybride / Intégré.

Ces éléments sont traités par les autres sources du projet et doivent être appliqués **avant affichage**.

**Garde-fou : la présentation doit décrire la construction déjà validée ; elle ne doit jamais ajouter de contrainte de construction ni influencer le choix des cartes, moteurs, boss ou lignes.**

### Juridiction

Cette source est l’autorité du **front-end global** : routage d’affichage, ordre des blocs, densité générale et structure de la réponse complète. La mise en forme spécialisée des Axes / Starters / Branches / Combos, des mini-carrousels de combo et de la voix dans ces lignes est déléguée exclusivement à `STRUCTURE_AXES_COMBOS_DECKS_PERSONNAGES`. STRUCTURE décrit ce qui doit être montré ; elle ne décide pas ce que le deck doit être.

### Principe central

**La réponse doit être immédiatement lisible, utile en jeu et courte par défaut.**

L’utilisateur doit pouvoir comprendre rapidement :
1. quelle direction est utilisée ;
2. quel est le style du deck ;
3. comment il fonctionne ;
4. quelles ressources démarrent ses lignes ;
5. comment elles sont converties ;
6. comment le deck gagne ;
7. où il casse.

---

# 2. ROUTAGE OBLIGATOIRE — choisir le bon format

Avant d’écrire la réponse, identifier le cas.

## CAS A — Direction non fixée

Si l’utilisateur donne seulement un personnage, un duel, un adversaire ou un moment narratif, la direction n’est **pas** considérée comme choisie.

Afficher brièvement :
- **Canonique** ;
- **Canonique remixé** ;
- **Alternatif**.

Ne pas produire automatiquement une decklist complète.

Le gate `DIRECTION_RESOLVED` ne peut être fermé que par un `direction_contract.json` indiquant `USER_EXPLICIT` ou `USER_SELECTED_AFTER_OPTIONS`. **`INFERRED` n’est jamais un mode valide.** Si aucun choix utilisateur n’existe, afficher les trois directions puis STOP avant la construction.

## CAS B — Direction ou concept déjà choisi

Si l’utilisateur a explicitement choisi :
- Canonique ;
- Canonique remixé ;
- Alternatif ;
- ou un concept précis déjà proposé ;

alors développer directement cette piste.

**Ne pas répéter les trois directions.**

## CAS C — L’utilisateur demande seulement plus d’idées

Exemples :
- « propose d’autres canoniques » ;
- « donne-moi d’autres remixés » ;
- « encore d’autres alternatives ».

Afficher uniquement plusieurs concepts courts dans la direction demandée.

**Ne pas construire de decklist complète sauf demande explicite.**

## CAS D — Commande `/fresh`

Si l’utilisateur envoie simplement **`/fresh`** après une decklist complète :

- déclencher `FRESH_REPLAY_FINAL_GATE` ;
- prendre la dernière decklist complète de la conversation comme artefact existant ;
- ne pas relancer l’idéation ni reproposer les trois directions ;
- afficher la trace compacte, la **Recommandation finale** et la conclusion prévues par ce gate ;
- rendre **Recommandation finale** comme un bloc visuellement autonome, dans cet ordre : **Refactor appliqué → Ce que le refactor améliore → Impact sur les combos → Résultat** ;
- afficher les deltas du refactor sur une ligne compacte avec séparateurs `·` lorsque cela reste lisible ;
- présenter **Ce que le refactor améliore** en quelques puces courtes centrées sur les bénéfices observables transmis par `FRESH_REPLAY_FINAL_GATE`, sans transformer ces bénéfices en nouveaux critères métier ;
- dans **Impact sur les combos**, privilégier une phrase compacte ou un `avant → après` seulement lorsqu'un Axe a réellement changé ; sinon afficher explicitement **aucun Axe essentiel modifié** ;
- terminer ce bloc par **Résultat**, une phrase de synthèse courte, puis afficher séparément **Version finale exacte**, **Statut** et **Confiance terminale**, avant la conclusion terminale du gate ;
- ne pas reconstruire localement la causalité du refactor, ne pas déduire un avantage supplémentaire et ne pas inventer de combo modifié : STRUCTURE affiche uniquement ce que `FRESH_REPLAY_FINAL_GATE` transmet ;
- ne pas réafficher toute la decklist sauf demande explicite.

`/fresh` est une convention de commande du projet, pas une commande native de l’interface ChatGPT.

---


## 2 bis. TRACE D’EXÉCUTION EN COURS — OBLIGATOIRE POUR TOUTE DECKLIST CONSTRUITE

Lorsqu’une decklist complète est construite ou reconstruite, émettre **pendant l’exécution**, dans les messages intermédiaires adressés à l’utilisateur, une trace compacte montrant les gates réellement franchis.

Cette trace est **systématique** : elle ne dépend pas d’une demande explicite de l’utilisateur.

Elle montre uniquement des **résultats de contrôle et actions prises**, jamais la chaîne de pensée interne détaillée.

### Cadence obligatoire — trace séquentielle, pas rétrospective

Chaque gate majeur applicable doit devenir visible **après son exécution réelle et avant que la chaîne ne progresse trop loin vers les gates suivants**.

Il est interdit d’attendre la fin de la construction puis de reconstituer en une seule fois une liste rétrospective de statuts juste avant la decklist finale. Une telle accumulation ne satisfait pas l’obligation de trace, même si les statuts eux-mêmes sont corrects.

Pour rester compacte, une même mise à jour intermédiaire peut regrouper **au plus quelques gates adjacents qui viennent réellement d’être exécutés**, mais elle ne doit jamais résumer après coup l’ensemble du pipeline.

La trace doit donc fonctionner comme un **journal séquentiel de progression** : l’utilisateur doit pouvoir voir où se trouve la chaîne avant qu’elle n’atteigne la sortie finale.

### Format canonique obligatoire des checkpoints

Pour les gates prescrits par la présente source, utiliser un **libellé canonique reconnaissable**. La formulation peut rester compacte, mais elle doit nommer explicitement le gate et son statut.

Formes attendues lorsqu’elles sont applicables :

- `Progression narrative : définie` ou `Progression narrative : réévaluée` ;
- `Exploration : effectuée` ;
- `Style → Axes : PASS` ou `Style → Axes : REFACTOR` ;
- `Viabilité multi-systèmes : test en cours` ;
- `Viabilité multi-systèmes : refactor en cours` ;
- `deck-vN → refactor → deck-vN+1` lorsqu’une nouvelle version est réellement matérialisée ;
- `Viabilité multi-systèmes : PASS_DIRECT`, `PASS_REFACTOR` ou `FAIL_ABANDON` uniquement lorsque l’autorité compétente a réellement émis ce statut ;
- `Compression terminale : FERMÉE` ou le statut réellement renvoyé par l’autorité compétente ;
- `Snapshot : figé → replay terminal : FERMÉE` lorsque ce replay est requis et effectivement fermé ;
- `Validation mécanique des lignes : PASS` ou le statut réel ;
- `Validation mécanique : PASS` uniquement si le validateur applicable a réellement produit ce résultat ;
- `Reçu : vérifié` uniquement après vérification mécanique réelle lorsqu’elle est requise ;
- `Validation finale : PASS` ou le statut réel ;
- `Confiance terminale : ÉLEVÉE|MOYENNE|FAIBLE` ;
- `STOP OUTPUT : PASS` uniquement lorsque les conditions prévues par l’autorité compétente sont satisfaites.

Ces libellés sont des **formes de trace**, pas de nouveaux critères métier. STRUCTURE n’attribue jamais elle-même les statuts : elle affiche ceux réellement produits par les autorités ou instruments compétents.

**Un message d’activité générique ne remplace jamais un checkpoint canonique.** Des formulations comme `évalué l’architecture`, `validé les lignes`, `affiné les combos`, `stabilisant le moteur`, `vérifié les finishers` ou toute reformulation libre équivalente peuvent accompagner le travail, mais elles ne satisfont pas à elles seules l’obligation de trace d’un gate prescrit.

Lorsqu’un gate obligatoire a été exécuté, son checkpoint canonique doit apparaître même si une interface ou un outil affiche déjà parallèlement un résumé d’activité générique.

### Contenu minimal

Pour toute decklist complète, les gates universels suivants doivent toujours apparaître lorsqu’ils sont réellement franchis :

- progression narrative : définie / réévaluée ;
- exploration : effectuée ;
- Style → Axes : `PASS` / `REFACTOR` ;
- validation mécanique des lignes ;
- validation finale ;
- **confiance d’exécution terminale : ÉLEVÉE / MOYENNE / FAIBLE** ;
- STOP OUTPUT : `PASS` uniquement si cette confiance est **ÉLEVÉE**.

Les gates conditionnels doivent apparaître dès qu’ils deviennent applicables :

- viabilité multi-systèmes : pendant le cycle, statut compact `test en cours` / `refactor en cours` si nécessaire ; puis seulement à fermeture complète du hook spécialisé, statut final `PASS_DIRECT` / `PASS_REFACTOR` / `FAIL_ABANDON` ;
- lorsqu’un PASS multi-systèmes est effectivement émis, afficher seulement son statut métier `PASS_DIRECT` / `PASS_REFACTOR` à ce stade ; **ne pas afficher encore de confiance d’exécution** ;
- reclassification finale lorsqu’elle est déclenchée ;
- validation mécanique du registre / reçu lorsque cet instrument est applicable.

Si un refactor est nécessaire pendant une génération normale, rendre visible la séquence réellement exécutée sans ajouter de Fresh Replay automatique.

Lors d’une commande `/fresh`, utiliser la trace compacte spécifique de `FRESH_REPLAY_FINAL_GATE`, qui commence par `reset → deck-v1`.

Si le refactor change la relation réelle entre les systèmes, la trace peut signaler sobrement : `rôle modifié → reroutage → retest`, sans détailler les critères internes.

Lorsque le registre d’exécution matérialisé est utilisé, la trace peut afficher uniquement la chaîne de versions utile, par exemple : `deck-v1 → refactor → deck-v2 → retest → PASS_REFACTOR`, et éventuellement un delta compact comme `package secondaire : 11 → 7 slots`. Le registre détaillé reste invisible par défaut.

STRUCTURE ne définit ni le schéma du registre ni ses règles de fraîcheur : cette juridiction appartient exclusivement à `REGISTRE_EXECUTION_ARTEFACTS`.
Lorsque le registre fournit une **trace chronologique matérialisée**, la trace utilisateur peut en refléter les événements pertinents sous forme compacte. Elle ne doit jamais inventer un événement absent du registre ou de la trace instrumentale.

En cas d’échec, afficher si utile uniquement le **premier point de rupture factuel** transmis par la validation finale, par exemple `refactor non matérialisé`, `retest sur version obsolète`, `validateur non exécuté` ou `snapshot final différent`. Ne pas exposer la trace interne complète sauf demande d’audit.

Sans détailler le raisonnement privé, la trace peut préciser brièvement **la nature observable du défaut corrigé** : conflit de Normal Summon, cartes mortes, dépendance à des mains presque pures, restriction de branche, Axe non reproductible, etc.

### Garde-fous

- Ne jamais afficher des étapes qui n’ont pas réellement été exécutées.
- Ne jamais reconstruire rétrospectivement la trace complète à la fin : les statuts doivent avoir été émis au fil de la progression réelle, conformément à la cadence obligatoire ci-dessus.
- Ne jamais considérer un libellé d’activité générique comme substitut au checkpoint canonique d’un gate obligatoire.
- Ne jamais inventer un `PASS` pour résumer une validation supposée.
- Lorsque la trace affiche `validation mécanique : PASS`, cette mention doit provenir d’un **résultat réel du validateur** sur le registre courant et, si l’instrument le prévoit, d’un reçu mécanique frais. Si le validateur n’a pas été exécuté, afficher au mieux `validation mécanique : non exécutée` et ne jamais promouvoir ce statut en PASS.
- Lorsque le validateur permet de vérifier son propre reçu, la trace ne peut afficher `reçu vérifié` ou permettre la confiance terminale `ÉLEVÉE` qu’après **exécution réelle de cette vérification** sur le registre et le reçu courants. Une phrase antérieure disant que le reçu existe ne compte pas comme exécution.
- Lorsque l’instrumentation fournit une trace mécanique, les mentions `validation mécanique : PASS` et `reçu vérifié` doivent correspondre aux événements matériels du validateur pour les hashes courants ; aucune reformulation conversationnelle ne peut les créer.
- Les statuts de la trace décrivent uniquement des actions déjà accomplies. Il est interdit d’annoncer un PASS comme résumé anticipé d’une opération qui doit encore être matérialisée ou exécutée par un instrument.
- Ne jamais afficher `PASS_REFACTOR` si le registre ne matérialise pas une version avant, une version après et un retest sur la version après.
- Une decklist multi-systèmes ne peut annoncer `PASS_DIRECT` ou `PASS_REFACTOR` que lorsque `HOOK_ANCRAGE_REFACTOR_MULTI_SYSTEMES` a **fermé entièrement son cycle sur la version exacte concernée**. Une relation crédible, un Axe mixte réussi ou un test encore en cours ne peuvent jamais être résumés prématurément par un PASS.
- Lorsque le hook exige son replay terminal à froid, la trace compacte doit montrer sobrement `snapshot figé → replay terminal : FERMÉE` avant le PASS. Si le replay renvoie `COMPRESSION_TROUVÉE`, afficher `replay terminal → compression trouvée → refactor` et ne jamais annoncer de PASS sur cette version.
- STRUCTURE ne calcule jamais la confiance d’exécution terminale : elle affiche seulement le résultat transmis par `VALIDATION_FINALE_DECKS_PERSONNAGES`. En mode `/fresh`, les anciens statuts sont ignorés et seule la confiance recalculée dans ce nouveau tour est affichée pour le contre-audit.
- Une confiance MOYENNE ou FAIBLE n'est jamais un quasi-PASS : elle suspend l'affichage et doit déclencher le retour vers l'autorité dont la fermeture manque.
- Si le statut final est `FAIL_ABANDON`, ne pas afficher la decklist comme construction valide ; revenir à l’exploration ou présenter l’abandon de la piste.
- Garder chaque mise à jour compacte : c’est un **journal d’exécution**, pas un audit détaillé.

### Règle de séparation avec la réponse finale

La trace **ne fait pas partie de la réponse finale structurée** et ne doit pas y être répétée.

Elle existe uniquement dans les messages intermédiaires émis pendant la construction. Une fois les gates franchis, la réponse finale suit normalement la structure de deck sans bloc `Trace d’exécution`.

### Source matérielle de la decklist affichée

Lorsqu’un protocole a produit un **snapshot terminal validé** via `REGISTRE_EXECUTION_ARTEFACTS`, la section Decklist de la réponse finale doit être rendue **à partir de ce snapshot exact**.

STRUCTURE ne décide pas du contenu du snapshot et ne le valide pas. Elle interdit seulement au front-end de reconstruire, compléter, corriger ou retaper librement une autre composition après la fermeture du pipeline.

Si une modification structurelle devient nécessaire pendant la rédaction finale, ne pas l’appliquer directement : créer une nouvelle version d’artefact et renvoyer la construction vers les autorités requises.

# 3. AFFICHAGE DES CLASSIFICATIONS

Afficher simplement :

- **Direction : Canonique**
- **Direction : Canonique remixé — Hybride**
- **Direction : Canonique remixé — Intégré**
- **Direction : Alternatif**

## Interdiction

Ne pas expliquer spontanément :
- pourquoi cette classification est correcte ;
- pourquoi le remix est Hybride ou Intégré ;
- quels tests ou hooks ont été réussis ;
- quelles cartes « prouvent » la classification ;
- que la réponse respecte les sources du projet.

Ces validations sont du **back-end invisible**.

Les expliquer uniquement si l’utilisateur demande :
- une justification ;
- un audit ;
- une vérification de conformité ;
- une discussion sur la classification elle-même.

---

# 4. BLOC CONCEPT — format unique obligatoire

Dans toute proposition ou decklist développée, utiliser toujours cet ordre :

**Style → Mécanique / concept → Fonction → Boss / finisher**

## Style

- 1 à 3 tags courts ;
- lecture instantanée du plan ;
- tout tag fonctionnel important doit être réellement démontré par les Axes de jeu.

Exemples :
- `Swarm / OTK`
- `Control / Lock`
- `Synchro Climb / Combo`
- `Grind / Reanimation`
- `FTK / Combo`

## Mécanique / concept

Explique **comment le deck fonctionne techniquement** en une phrase claire.

## Fonction

Explique **ce que cette mécanique permet concrètement de faire pendant le duel**.

La Fonction ne doit pas se réduire à :
- « invoquer le boss » ;
- « sortir X plus vite » ;
- « accéder à X ».

## Boss / finisher

Indiquer le boss, la famille de finishers ou la condition de victoire, avec son rôle terminal en quelques mots.

Si le deck n’a pas de boss central, le dire simplement.

### Identité du deck — facultative

Une phrase-pitch peut conclure le bloc Concept, en proposition comme en decklist détaillée, si elle aide à mémoriser la personnalité de la construction.

Elle reste **facultative**, limitée à une phrase et ne remplace aucun des quatre champs obligatoires.

---

# 5. FORMAT — PROPOSITION AVANT DECKLIST

Quand la direction n’est pas encore choisie, afficher d’abord :

- **Potentiel du personnage : X/10** ;
- puis **un bloc visuellement autonome par direction** dans l’ordre Canonique → Canonique remixé → Alternatif ;
- puis laisser l’utilisateur choisir.

## Gabarit visuel compact

Chaque piste suit cette hiérarchie :

**DIRECTION — [nom court]**  
**Style**  
`1 à 3 tags`

**Mécanique / concept**  
Une explication courte de la structure du deck.

**Fonction**  
Ce que cette structure permet concrètement pendant le duel.

**Boss / finisher**  
Boss, famille de finishers ou condition de victoire.

**Identité du deck** *(facultatif)*  
Une seule phrase-pitch si elle apporte une image claire ou du caractère au concept.

Séparer chaque direction par `---` afin qu’elle puisse être lue indépendamment. Pour le Canonique remixé, afficher directement **Hybride** ou **Intégré** dans le titre du bloc.

### Règle de lisibilité

Ne pas compacter `Style`, `Mécanique / concept`, `Fonction` et `Boss / finisher` dans un même paragraphe. Chacun doit rester immédiatement repérable au scan.

### Contraintes

Les trois pistes doivent être :
- courtes ;
- réellement distinctes ;
- différentes par leur mécanique, leur fonction, leur économie de ressources ou leur condition de victoire.

### Interdictions

Ne pas :
- proposer trois variantes du même deck avec seulement un moteur différent ;
- transformer **Identité du deck** en nouvelle analyse obligatoire ou en justification de classification ;
- expliquer les validations internes ;
- construire une decklist complète sans demande explicite.

---

# 6. FORMAT — DECKLIST COMPLÈTE

Lorsqu’une piste est développée, utiliser cet ordre et **ne pas le réorganiser sans raison**.

## 1. Contexte + Direction

Afficher brièvement :
- personnage ;
- duel ou moment narratif si pertinent ;
- direction finale.

## 2. Progression narrative

Afficher :
- **Potentiel du personnage : X/10** ;
- **Développement de la stratégie :** rudimentaire / en développement / solide / avancé / très avancé / quasi optimal.

Puis ajouter **1 à 3 phrases maximum** expliquant :
- ce que le personnage maîtrise déjà ;
- ce qu’il ne maîtrise pas encore ;
- ou ce qui caractérise son stade actuel.

### Interdiction

Ne pas transformer cette section en audit technique de la decklist.

## 3. Concept du deck

Afficher obligatoirement :

- **Style :**
- **Mécanique / concept :**
- **Fonction :**
- **Boss / finisher :**

Ajouter **Identité du deck** en une phrase si elle apporte une vraie personnalité ou une image claire de la construction.

Garder ce bloc court : généralement **2 à 4 phrases utiles** au total.

## 4. Cartes emblématiques — visuel conditionnel

Dans une **decklist complète**, si des images en ligne pertinentes sont accessibles et que la construction possède au moins **2 cartes réellement représentatives de son fonctionnement**, afficher ici un petit bloc visuel de **2 à 4 cartes maximum**.

Choisir en priorité parmi :
- boss / finisher principal ;
- starter ou moteur central ;
- carte de combo signature ;
- second boss uniquement s'il représente réellement une autre branche.

Privilégier les cartes qui racontent le deck visuellement. Éviter les staples génériques sauf si elles définissent réellement son concept.

**Ne pas omettre ce bloc simplement parce qu'il n'est pas nécessaire au fonctionnement technique du deck.** L'omettre seulement si les images pertinentes ne sont pas accessibles, sont inutilisables, ou si aucune sélection de 2 à 4 cartes n'apporte de vraie valeur visuelle.

L’indisponibilité technique des images ne réécrit pas rétroactivement une décision d’applicabilité déjà positive : elle devient une information d’availability distincte. Si un contrôle Black-Box exige la présence hôte du composant, cette indisponibilité produit `UNVERIFIED/BLOCKED`, jamais un `PRESENTATION_PASS` artificiel.

Une micro-légende courte peut préciser le rôle de chaque carte : `Boss`, `Starter`, `Combo`, `Plan B`.

### Mini-schéma — facultatif

Si cela améliore la compréhension immédiate, ajouter juste sous le visuel **1 à 3 lignes maximum** sous la forme :

`moteur → conversion → boss / résultat`

Ce schéma résume le fonctionnement ; il ne remplace ni le Concept ni les Axes de jeu.

## 5. Decklist

### Construction normale / nouvelle decklist

Afficher la decklist complète avec séparation stable et totaux visibles :

- **Main Deck — total exact** ;
  - **Monstres — total exact** ;
  - **Magies — total exact** ;
  - **Pièges — total exact** ;
- **Extra Deck — total exact** ;
- **Side Deck — total exact**, y compris `0` si aucun Side Deck n'est utilisé.

Chaque carte reste verticale : **une carte = une puce = une ligne**. Les totaux Monstres + Magies + Pièges doivent égaler le total Main Deck.

Gabarit :

`### Main Deck — 40`

`#### Monstres — 24`

`- 3× ...`

`#### Magies — 13`

`- 3× ...`

`#### Pièges — 3`

`- 2× ...`

`### Extra Deck — 15`

`### Side Deck — 0`

### Refactor explicitement demandé par l'utilisateur

Lorsqu'un deck déjà affiché est matériellement modifié **à la demande explicite de l'utilisateur** (`corrige`, `remplace`, `refactor`, `/fresh`, etc.), ne pas réafficher automatiquement toute la decklist. Le mode par défaut devient **`DIFF_ONLY`**.

Afficher seulement `## Diff deck-vN → deck-vN+1`, groupé par les catégories réellement touchées : **Monstres / Magies / Pièges / Extra Deck / Side Deck**. Le titre de chaque catégorie touchée affiche son total `avant → après`.

Format d'une carte modifiée :

- `Carte A : 3 → 2`
- `Carte B : 0 → 1 (NOUVEAU)`
- `Carte C : 1 → 0 (RETIRÉ)`

Ne pas lister les cartes inchangées. Conserver ensuite `Impact sur les combos` selon l'autorité spécialisée.

Exceptions :
- si l'utilisateur demande explicitement la decklist complète après le refactor, rendre la version complète groupée ;
- un refactor interne au pipeline avant la première sortie terminale n'active pas `DIFF_ONLY`;

### Interdictions

Ne pas :
- répéter ensuite toutes les cartes une par une ;
- ajouter une explication carte par carte sans demande ;
- remplir artificiellement l’Extra ou le Side Deck pour atteindre un nombre maximal ;
- utiliser `DIFF_ONLY` lors d'une construction normale ;
- réafficher silencieusement toute la decklist lors d'un refactor utilisateur lorsque la version complète n'a pas été demandée.

## 6. Axes de jeu — délégation obligatoire

La section **Axes de jeu / Starters / Branches / Combos / lignes situationnelles** doit être rendue intégralement selon :

**`STRUCTURE_AXES_COMBOS_DECKS_PERSONNAGES`**

Cette source spécialisée est l’unique autorité sur la présentation interne de cette section : hiérarchie Axe → Starter → Branche → Combo, flèches, densité des lignes, guide situationnel, restrictions, mini-carrousels de combo, ponctuations de personnalité, répliques terminales et traitement des climax.

`STRUCTURE_REPONSES_DECKS_PERSONNAGES` conserve uniquement l’autorité sur **l’emplacement de la section dans la réponse complète** et sur le routage global. Il est interdit de recréer localement une seconde version des règles Axes / Combos.

## 8. Point de rupture

Indiquer brièvement :
- ce qui casse ;
- ce qui ralentit ;
- ce qui oblige à changer de branche.

Ajouter une évolution future seulement si elle est réellement utile à la campagne.

## 9. Fun fact — facultatif

Ajouter seulement s’il existe un détail :
- amusant ;
- thématique ;
- mécanique ;
- mémorable en jeu.

Maximum recommandé : **1 à 3 phrases**.

Si rien d’intéressant n’existe, omettre la section.

---

# 7. RÈGLES SPÉCIALES — AXES DE JEU / PILOTAGE SITUATIONNEL

Toutes les règles spécialisées concernant :

- Axe / Starter / Branche / Combo ;
- lignes situationnelles et guide de décision ;
- restrictions, choke points et erreurs fréquentes ;
- densité et langage en flèches ;
- mini-carrousels de combo ;
- ponctuations de personnalité ;
- répliques terminales et climax ;

sont définies **exclusivement** par `STRUCTURE_AXES_COMBOS_DECKS_PERSONNAGES`.

La présente source ne conserve ici aucune seconde définition. Elle impose seulement d’insérer cette section au bon endroit dans la réponse globale.

---

# 8. INTERDICTIONS GLOBALES — STOP OUTPUT

Avant affichage, vérifier qu’aucune de ces erreurs n’apparaît.

## Ne jamais :

1. choisir silencieusement Canonique lorsqu’aucune direction n’est fixée ;
2. répéter les trois directions après que l’utilisateur en a choisi une ;
3. donner une decklist complète alors que l’utilisateur demandait seulement des idées ;
4. expliquer spontanément les hooks, gates, validations ou tests internes ;
5. défendre la classification dans une réponse normale ;
6. remplacer la Fonction par « invoquer le boss » ;
7. placer Boss / finisher avant Mécanique et Fonction ;
8. répéter les mêmes informations dans plusieurs sections ;
9. expliquer chaque carte individuellement sans demande ;
10. ajouter des sections facultatives qui n’apportent rien ;
11. produire une réponse bureaucratique qui masque le plan de jeu ;
12. transformer le bloc visuel principal en galerie exhaustive ou montrer une image pour chaque carte ;
13. répéter dans la légende ou le mini-schéma ce qui est déjà expliqué longuement ailleurs ;
14. omettre le bloc **Cartes emblématiques** dans une decklist complète lorsque ses conditions définies par la présente source sont remplies ;
15. recréer localement une règle spécialisée appartenant à `STRUCTURE_AXES_COMBOS_DECKS_PERSONNAGES`.

---

# 9. INFORMATIONS FACULTATIVES

Ajouter seulement si demandé ou réellement utile :

- forces / faiblesses détaillées ;
- plan spécifique contre l’adversaire ;
- variantes de ratios ;
- cartes alternatives ;
- hands tests ;
- combos secondaires très marginaux ;
- explication carte par carte ;
- justification de classification ;
- audit de conformité ;
- simulation de duel.

---

# 10. RÈGLE FINALE DE PRIORITÉ

En cas de doute sur la forme, appliquer cet ordre :

**1. Lisibilité**  
**2. Utilité en jeu**  
**3. Compréhension de la mécanique**  
**4. Rythme**  
**5. Fun / personnalité**  
**6. Détail supplémentaire**

Si une information n’aide pas l’un de ces objectifs, elle peut probablement être retirée.

### Formule courte

**Choisir le bon mode de réponse → afficher seulement ce qui sert le joueur → garder les validations en back-end → présenter Style → Mécanique → Fonction → Boss → ajouter si utile Identité + mini-schéma → afficher le visuel lorsqu'il remplit ses conditions → déléguer intégralement Axes / Starters / Branches / Combos et leurs climax à `STRUCTURE_AXES_COMBOS_DECKS_PERSONNAGES` → terminer avec les blocs globaux prévus.**


---

# 11. Sortie contractuelle de rendu — exécutable

Pour toute decklist complète, la présente autorité doit produire avant rédaction finale les exigences globales applicables du `RENDER_CONTRACT_FROZEN`.

Chaque exigence doit contenir au moins une assertion mécanique vérifiable sur le rendu exact. Le harness exécute ces assertions mais **n'en choisit jamais les critères**.

Assertions autorisées : présence de motif, ordre de marqueurs, comptage minimal, **comptage exact scoped (`regex_exact_count`)**, longueur maximale de ligne, nombre maximal d'occurrences d'un motif par ligne, ou présence de composants UI déclarés.

## Lisibilité de la decklist complète

Pour une decklist complète, la lisibilité prime sur la compression horizontale. Une catégorie contenant plusieurs cartes ne doit pas être transformée en une longue phrase séparée par `·`, `;` ou équivalent.

Le contrat global doit donc inclure une exigence d’identifiant exact **`decklist-vertical`** contenant une assertion mécanique empêchant plus d’**une entrée de carte `N× Nom` par ligne physique**.

Format attendu : **une carte = une puce = une ligne physique**.

Exemple conforme :

- `3× Junk Synchron`
- `3× Junk Converter`
- `2× Jet Synchron`

Exemple interdit :

`3 Junk Synchron · 3 Junk Converter · 2 Jet Synchron`

Cette règle vaut pour Main / Extra / Side lorsqu’ils sont affichés. Une compaction horizontale de plusieurs cartes est un échec de rendu, même si les totaux restent exacts.

### Groupes et totaux — policy compilée RC16.3

En rendu complet, la policy globale déclare un requirement dérivé via `compile: DECKLIST_MODE_FROM_STATE`. STRUCTURE décide que les groupes/totaux doivent être visibles ; elle **ne saisit jamais leurs valeurs**. Le runtime calcule depuis le snapshot exact + la conformité narrative `Main Deck`, `Monstres`, `Magies`, `Pièges`, `Extra Deck` et `Side Deck`, puis compile l'exigence réelle `decklist-groups`.

En `DIFF_ONLY`, le même marqueur compile automatiquement `refactor-diff` à partir de l'état de refactor courant. STRUCTURE ne choisit pas manuellement entre FULL et DIFF_ONLY lorsqu'un état autoritaire existe.

## Liaison de la direction affichée

La policy globale contient `direction-binding` avec `compile: FINAL_DIRECTION_FROM_CLASSIFICATION`. La classification finale exacte est injectée depuis `FINAL_CLASSIFICATION_CLOSED`; aucune ancienne étiquette ni copie manuelle n'est admise.

## Ordre global

Les blocs obligatoires réellement applicables doivent être traduits en `ordered_regex` afin qu'une reformulation ne puisse pas déplacer ou fusionner silencieusement les grandes sections.

**Règle courte : les exigences globales de STRUCTURE doivent devenir des assertions du contrat avant la rédaction, puis être exécutées sur le rendu exact.**


### RC16.3 — policy choisie, faits compilés

Avant `RENDER_CONTRACT_FROZEN`, cette autorité produit ses règles applicables dans `render_policy.json`. Les assertions éditoriales non dérivables restent écrites ici ; les bindings déjà connus du système utilisent uniquement un marqueur `compile`. Le fichier `render_contract.json` final est produit par `compile-render-contract` et ne doit jamais être réécrit manuellement.

**Règle courte : STRUCTURE choisit le critère ; le runtime injecte le fait.**

### Primitive générique RC16.15 — `regex_exact_count`

Lorsqu’une autorité STRUCTURE spécialisée exige une cardinalité exacte dans une zone précise du rendu, la policy peut émettre :

```json
{
  "type": "regex_exact_count",
  "pattern": "...",
  "exact": 1,
  "scope_start": "...",
  "scope_end": "..."
}
```

Cette primitive est purement mécanique : le runtime valide sa forme, isole le scope fourni, compte les matches du `pattern` et exige `observed == exact`. Il ne choisit ni la valeur métier, ni le motif, ni les limites du scope. Pour `signature-terminal-quote`, ces décisions appartiennent exclusivement à `STRUCTURE_AXES_COMBOS_DECKS_PERSONNAGES`, qui impose son binding spécialisé.

### RC16.2 — contrat gelé et réparation bornée

Une fois `RENDER_CONTRACT_FROZEN` fermé, la présente autorité ne modifie plus aucune exigence, regex, seuil ou ordre du contrat pour faire passer un rendu. Un FAIL de `render-check` entraîne uniquement une correction du rendu/composant fautif sous le **même `render-vN`**.

Le runtime agrège les défauts déterministes et génère le manifest canonique seulement sur PASS. `presentation-change` n’est utilisé qu’après un vrai `FINAL_RENDER_PREPARED`; un brouillon raté n’est jamais une nouvelle version de rendu. Si le contrat gelé semble lui-même erroné, arrêter en `CONTRACT_DEFECT_SUSPECTED` au lieu de réécrire son juge.

---

# 12. Persistance des composants visuels lors d’une mutation de présentation

Lorsqu’un rendu déjà validé contient un composant visuel réellement matérialisé — notamment le carrousel principal des cartes emblématiques — une demande purement éditoriale comme « plus compact », « plus lisible », « reformate » ou « améliore la présentation » ne rend pas ce composant facultatif.

Si le deck, les Axes et les combos ne changent pas, le nouveau contrat de rendu doit traiter chaque composant requis du rendu précédent selon l’un des deux modes suivants :

- `PRESERVE` — le même composant matérialisé est transporté dans `render-vN+1` avec la même identité et le même artefact ;
- `REGENERATE` — le composant est recréé parce que la nouvelle mise en forme l’exige, mais il reste explicitement lié au composant précédent et conserve sa fonction, son parent et ses tags structuraux.

Une mutation éditoriale ne peut pas utiliser `DROP` pour supprimer silencieusement un composant déjà requis. Si l’utilisateur demande explicitement de retirer une couche visuelle ou si son applicabilité métier change, l’autorité de structure doit traiter cela comme une nouvelle décision de rendu explicite, pas comme une conséquence implicite de la compaction.

Le composant doit être matérialisé dans un artefact identifiable (`component_id`, type, fichier/enveloppe, hash). Une simple mention textuelle ou un emoji de remplacement ne prouve pas la présence du composant UI réel.

**Règle courte : reformater le texte ≠ reconstruire librement les composants visuels. Les composants requis survivent par défaut à toute mutation purement éditoriale.**

## RC5 — invariants globaux de restitution

### Pilotage visible

Pour toute decklist complète dont le rendu contient au moins deux titres `Axe N`, le rendu final doit contenir un bloc visible `Guide de pilotage`. Le contenu peut être très court, mais il doit permettre de choisir la branche utile sans relire toutes les lignes.

**Interdit :** considérer que des décisions dispersées sous les Axes suffisent à matérialiser le guide lorsque plusieurs Axes existent.

### Impact après changement matériel

Après `deck-vN → refactor → deck-vN+1`, le rendu de `deck-vN+1` doit contenir `Impact sur les combos` avant toute autorisation terminale. Le statut visible doit correspondre au `combo_impact.json` validé par l’autorité de pilotage :

- `UNCHANGED` → `Aucun Axe essentiel modifié` ;
- `MODIFIED` → lignes/Axes touchés réaffichés ;
- `REMOVED` → anciennes lignes invalidées nommées.

La decklist seule ne constitue jamais une restitution suffisante d’un refactor matériel.

## RC9 — rendu post-refactor déterministe

Pour un refactor post-sortie en `DIFF_ONLY`, STRUCTURE **ne rédige plus la partie decklist**. Elle consomme l'artefact `refactor_diff.md` généré par le runtime et le matérialise tel quel dans le composant `refactor-diff`. Aucun ratio supplémentaire ni carte inchangée ne doit être ajouté autour de cet artefact.

Le reste du rendu (impact sur les combos, guide utile, voix, visuels) peut être régénéré par les autorités compétentes, mais le front-end final est le bundle exact validé. Après `STOP_OUTPUT_ALLOWED`, ne jamais reconstruire une decklist complète depuis le contexte conversationnel.

### Continuité des visuels après changement matériel

Un refactor de cartes n'efface pas automatiquement les carrousels du rendu précédent. Pour chaque carrousel matérialisé :

- `PRESERVE` si son contenu reste exact ;
- `REGENERATE` si les cartes, refs, Axe ou parent ont changé mais que le composant reste applicable ;
- `DROP_EXPLICIT` uniquement si la nouvelle applicabilité STRUCTURE est réellement fermée à `false`, avec raison.

La même logique s'applique à la réplique terminale précédemment requise. Changer de deck-vN ne suffit jamais, à lui seul, à justifier sa disparition.


---

# 13. RC16.14 — Assemblage terminal de présentation

La présente autorité ferme désormais explicitement la frontière entre le **rendu textuel validé** et les **composants UI déjà décidés et matérialisés**. Elle ne redéfinit jamais leur applicabilité : le carrousel principal reste décidé ici selon les règles globales existantes, tandis que les mini-carrousels, Axes signature, climax et répliques restent exclusivement sous `STRUCTURE_AXES_COMBOS_DECKS_PERSONNAGES`.

Après `PILOTAGE_VALIDATED` et avant `FINAL_VALIDATION_PASS`, le bundle déjà validé doit être projeté dans un artefact de pré-émission :

`render exact + render_manifest exact + component inventory exact → terminal_presentation_plan.json`.

Ce plan doit contenir :
- l'identité exacte `run_id / deck-vN / render-vN` ;
- le fichier texte exact et son SHA ;
- le render manifest exact et son SHA ;
- le component manifest exact lorsqu'il existe ;
- le hash d'inventaire des composants ;
- chaque composant autorisé exactement une fois, avec `component_id`, primitive `type`, `parent`, payload/hash et `image_refs`.

Le runtime peut compiler et vérifier cette projection, mais il **ne crée aucun composant absent du bundle**, ne choisit aucune image, ne change aucun parent et ne décide jamais qu'un mini-carrousel ou une réplique est applicable. Un inventaire vide reste une sortie valide lorsqu'aucun composant n'est applicable.

La vérification mécanique produit `terminal_presentation.receipt.json`. Son PASS signifie uniquement :

**« le plan pré-émission contient exactement le texte et les composants autorisés du bundle courant »**.

Ce receipt ne peut jamais prétendre que le client ChatGPT a réellement peint les composants à l'écran. La visibilité réelle reste une propriété black-box vérifiée après émission.

## Règle d'émission

Après autorisation terminale :
- si `component_count = 0`, émettre le texte validé sans inventer de composant ;
- si `component_count > 0`, ne jamais réduire la sortie à `terminal_payload.md` seul ;
- émettre le Markdown validé **et tous les composants du plan**, au parent déjà décidé ;
- utiliser les payloads et `image_refs` exacts ;
- ne jamais reconstruire librement un carrousel depuis la conversation ;
- ne jamais omettre silencieusement un composant présent dans le plan ;
- ne jamais ajouter un composant absent du plan.

Après `deck-vN → deck-vN+1`, seul le plan terminal de la version courante peut être émis. Toute ancienne projection devient `STALE`; les règles `PRESERVE / REGENERATE / DROP_EXPLICIT` restent celles du pipeline de rendu existant.

**Règle courte : composant applicable → matérialisé → validé → présent dans le plan terminal → émis ; composant non applicable → jamais synthétisé par le runtime.**

---
## RC16.23 — Compilation déterministe du front-end

STRUCTURE conserve seule la décision sur **ce qui doit être affiché**. Le Render Compiler peut seulement matérialiser cette décision : ordre technique, anchors, composants, cardinalité d'une quote déjà fournie, binding des carrousels et terminal presentation payload.

Le modèle fournit le contenu éditorial utile ; il ne doit pas recopier des IDs de composants ni reconstruire manuellement un carrousel déjà déclaré applicable. Si `applicable=true`, sa matérialisation est une obligation du compilateur. Si `applicable=false`, le compilateur n'invente aucun composant.

## Addendum RC16.23.3 — survie terminale du rendu

Un composant obligatoire n'est pas affiché parce qu'un payload/manifest existe : sa survie jusqu'au plan terminal et son anchor d'émission exact doivent être prouvés. `component_exists ≠ component_emitted`. La decklist finale est dérivée du snapshot terminal ; si le type autoritatif d'une carte Main Deck manque, ne jamais la classer par défaut comme Monstre : rendu Main Deck plat ou blocage selon le contrat runtime.
