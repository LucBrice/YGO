# Structure spécialisée — Axes / Starters / Branches / Combos — Decks personnages

**Version : V10 / RC16.12**

## Rôle

Cette source est l’**autorité front-end spécialisée** pour le rendu des Axes de jeu, Starters, Branches, Combos / lignes, lignes situationnelles, guides de décision, restrictions de pilotage, mini-carrousels de combo, ponctuations de personnalité et répliques terminales dans les decklists de personnages.

Elle reçoit une construction déjà produite par les autorités métier. Elle ne choisit aucune carte, ne crée aucun Axe, ne décide pas de la viabilité, de la progression narrative, de la classification ou de la légalité.

`STRUCTURE_REPONSES_DECKS_PERSONNAGES` reste l’autorité du **routage global, de l’ordre des blocs et de la réponse complète**. Dès que la réponse atteint la section Axes / Combos, la présente source devient l’unique source de vérité sur sa mise en forme spécialisée.

### Juridiction

- contenu fonctionnel des Axes, starters et lignes → `HOOK_STYLE_AXES_CONSTRUCTION_DECKS_PERSONNAGES` ;
- viabilité multi-systèmes → `HOOK_ANCRAGE_REFACTOR_MULTI_SYSTEMES` lorsqu’applicable ;
- rendu Axes / Starters / Branches / Combos et couches visuelles associées → **présente source** ;
- validation de survie et de lisibilité du pilotage avant sortie → `VALIDATION_PILOTAGE_LIGNES_DECKS_PERSONNAGES`.

**Principe : la présente source rend lisible ce qui existe déjà ; elle ne fabrique jamais une Branche, un Starter, un climax ou une résilience pour améliorer la présentation.**

---

## 6. Axes de jeu

Présenter **2 à 4 axes stratégiques** par défaut.

Un axe peut contenir plusieurs lignes ou variantes si elles appartiennent au même rôle.

### Format obligatoire de chaque axe

**Titre court et fonctionnel**

Une phrase directe expliquant immédiatement ce que cet axe accomplit.

La **flèche reste le langage principal** des Axes : ne pas convertir les combos en longues listes numérotées ou en paragraphes procéduraux lorsque la chaîne peut rester lisible. La numérotation est autorisée seulement lorsqu'elle rend un ordre réellement déterminant plus facile à suivre.

Format minimal pour une interaction simple :

`ressource → action → conversion → résultat / finisher`

Pour un **Axe central, signature, OTK / FTK / Lock, un Climb important ou toute ligne dont l'ordre des actions compte réellement**, rendre visible le contrat de pilotage produit par `HOOK_STYLE_AXES_CONSTRUCTION_DECKS_PERSONNAGES`. La présentation peut utiliser plusieurs sous-chaînes courtes :

**Départ :** `main / ressources réellement suffisantes`

`première action → recherche / cible prioritaire`

`ordre des conversions → ressource à conserver`

`embranchement éventuel → payoff → état final / lethal`

Le joueur doit pouvoir suivre la ligne sans inventer lui-même les décisions essentielles. Afficher, lorsqu'ils sont pertinents :
- le **Départ** réel ;
- la **première action** ;
- l'**ordre** des activations / Invocations lorsque cet ordre change la ligne ;
- la **recherche / cible** prioritaire ;
- **À conserver :** une ressource nécessaire plus tard ;
- **Branche :** un choix important selon la main, le terrain ou la disponibilité du payoff ;
- le **payoff** concret ;
- **Résultat :** l'état final réel : board, interruptions, lock, boucle, dégâts, condition de victoire ou ressources restantes.

Ajouter seulement si cela change réellement le pilotage :
- **Restriction :** si la ligne ferme ou retarde une branche importante ;
- **Choke point :** si une interruption précise casse réellement la séquence ;
- **Erreur fréquente :** si une action légale compromet inutilement le payoff ou consomme trop tôt une ressource nécessaire.

Ne pas imposer artificiellement tous ces éléments à chaque petit Axe : le niveau de détail suit la difficulté réelle de reproduction. Une interaction évidente reste une chaîne courte ; une ligne centrale ou complexe reçoit le détail nécessaire.

### Séparation obligatoire — Axe ≠ Starter ≠ Branche ≠ Combo / ligne

Les **Axes** décrivent les grands plans structurels. Ils ne doivent pas être artificiellement transformés en `Axe 1 = combo 1`, `Axe 2 = combo 2`, etc.

Dans le rendu de pilotage, distinguer explicitement les niveaux réellement présents :

- **Axe** — le plan structurel général : ce que le deck cherche à accomplir ;
- **Starter / ouverture** — la carte ou les ressources réelles qui permettent d'entrer dans cet Axe ;
- **Branche** — un choix alternatif à l'intérieur du même Axe lorsque, après une ouverture ou un tronc commun, plusieurs routes importantes conduisent à des payoffs, fonctions ou états finaux différents ;
- **Combo / ligne** — la séquence exécutable elle-même : `ressources → actions → conversions → payoff → résultat`.

Ces niveaux ne sont **pas tous obligatoires dans chaque Axe**. Ne pas créer un label `Branche` lorsqu'il n'existe qu'une seule route, ni un label `Starter` artificiel lorsqu'une simple ressource générique suffit. Le but est de rendre visible la structure réelle, pas d'ajouter des rubriques.

Lorsqu'un Axe possède plusieurs starters, les afficher comme **portes d'entrée distinctes** avant le tronc commun ou la ligne correspondante. Lorsqu'un même starter ouvre plusieurs routes significatives, afficher ensuite les **Branches** séparément. Si plusieurs starters convergent vers exactement le même tronc commun, le dire clairement puis éviter de répéter inutilement tout le combo.

Un même Axe peut aussi être suivi de plusieurs lignes situationnelles si plusieurs mains ou états de partie exigent réellement un pilotage différent. Inversement, plusieurs petits starters qui reproduisent la même décision ne justifient pas plusieurs Axes.

### Rendu des starters importants — sans tableau obligatoire

Lorsque `HOOK_STYLE_AXES_CONSTRUCTION_DECKS_PERSONNAGES` a identifié plusieurs **starters structurellement importants**, les rendre visibles à travers des lignes concrètes rattachées à l'Axe concerné ou au guide situationnel.

Format visuel recommandé lorsqu'un Axe possède plusieurs portes d'entrée importantes :

**Starter — [nom / ouverture]**
`starter + ressource minimale → première action → conversion`

Si la ligne continue sans embranchement :

`→ payoff → résultat`

Si elle se divise réellement :

**Branche — [fonction / payoff]**
`tronc commun → conversion propre à la branche → payoff → résultat`

**Branche — [autre fonction / payoff]**
`tronc commun → autre conversion → payoff → résultat`

Puis, si un autre starter possède un séquençage réellement différent :

**Starter — [autre ouverture]**
`starter → séquençage distinct → branche éventuelle → payoff / résultat`

Ne pas imposer de tableau récapitulatif des starters. Ne pas créer une rubrique autonome si les lignes restent naturellement lisibles sous leurs Axes.

Regrouper plusieurs starters dans une même ligne lorsqu'ils reproduisent réellement le même pilotage. Les séparer lorsque le starter change l'ordre, les cibles, les ressources conservées, la branche, une restriction importante ou le payoff.

Le but visuel est : **exhaustivité sur les starters structurels importants, sans inflation du nombre d'Axes ni duplication de combos équivalents.**

### Starter strict — RC7

Le libellé visible du Starter doit couvrir toutes les ressources initiales réellement indispensables à la ligne. Ne pas écrire une classe générique (`Tuner Niveau 1`, `Dragon`, `extender`) si la séquence affichée dépend ensuite d'une carte précise non obtenue par la ligne. Dans ce cas, nommer la carte précise ou séparer les variantes en Branches.

STRUCTURE rend fidèlement le `pilotage_contract.json` validé ; elle ne décide pas elle-même quelles ressources sont obligatoires.


### Propriétés et checkpoints physiques — RC10

Lorsque `pilotage_contract.json` ferme une propriété de starter par `render_token`, la ligne affichée doit reprendre cette contrainte sans l’élargir (`Tuner Niveau 1` ne redevient pas `Tuner`). Pour un starter générique, les variantes non couvertes doivent être sorties du libellé commun ou rendues comme Branches explicites.

Pour toute ligne `COMPLEX`, rendre aux points utiles les `state_render_token` validés et, lorsqu’un placement est obligatoire, son `placement_render_token`. Le lecteur doit voir l’état déterminant **avant** l’action qui en dépend : zones libres/occupées pertinentes, placement imposé, Token ou monstre à conserver.

STRUCTURE ne recalcule ni les Niveaux ni les zones : elle transporte fidèlement les fermetures de `VALIDATION_PILOTAGE_LIGNES_DECKS_PERSONNAGES` dans le rendu exact.

### RC12 — préserver les portes d’entrée et rendre les conditions critiques visibles

Le rendu ne doit jamais réduire artificiellement plusieurs starters structurels à un seul « starter principal » pour simplifier la lecture ou la validation. Lorsque plusieurs portes d’entrée ont été retenues par le hook métier, elles restent visibles ; celles qui convergent réellement peuvent partager un tronc commun sans dupliquer tout le combo.

Les preuves backend de replay symbolique restent invisibles. En revanche, toute condition qui change réellement le pilotage doit survivre dans le texte joueur : exception d’un starter générique, carte à conserver, ressource qui doit encore être au Deck/Main/GY, placement critique, restriction active ou caractère conditionnel/aléatoire d’un payoff.

Le rendu n’affiche jamais les objets JSON, comptes internes ou identifiants de replay. Il affiche seulement l’information de jeu utile produite par l’autorité métier.

## 7. Guide de pilotage situationnel

Après les Axes, afficher les **lignes situationnelles réellement utiles** dérivées de la decklist finale. Leur nombre n'est pas fixé : il dépend de la richesse réelle du deck et de la valeur pédagogique de chaque situation.

La couverture des **starters structurellement importants** transmise par `HOOK_STYLE_AXES_CONSTRUCTION_DECKS_PERSONNAGES` est obligatoire, mais elle peut déjà être satisfaite par les lignes affichées directement sous les Axes. Le guide situationnel complète ensuite cette couverture avec les situations qui ajoutent une décision réellement différente.

Rechercher activement les familles transmises par le hook — starter naturel important, main forte, main mixte, main imparfaite, boss déjà établi, milieu de duel, finisher accessible, jeu en second, après interruption — puis **n'afficher, au-delà de la couverture obligatoire des starters structurels, que celles qui apportent une décision de pilotage distincte**.

Ne jamais remplir un quota. Une ligne supplémentaire doit enseigner au moins un nouvel élément utile : choix de branche, cible, ordre, conversion, conservation de ressource, recovery réelle, lethal, board breaking ou timing de finisher.

### Format d'une ligne situationnelle

**Situation / Main de départ**
Indiquer les cartes et ressources réellement disponibles.

**Objectif**
Dire en une phrase ce que la ligne cherche à accomplir.

**Pilotage**

La flèche reste privilégiée lorsque la ligne reste claire. La numérotation est autorisée lorsqu'elle améliore réellement un séquençage important.

`première action → cible / recherche précise → conversion → ressource conservée → adaptation → payoff`

**Résultat**
Décrire l'état concret obtenu et, lorsque pertinent, ce qu'il prépare ensuite.

Ajouter seulement lorsque utile :
- **À conserver :** ressource à ne pas consommer trop tôt ;
- **Branche :** décision importante selon la main / terrain ;
- **Restriction :** option fermée ou retardée ;
- **Choke point :** interruption réellement critique ;
- **Erreur fréquente :** séquençage légal mais mauvais ;
- **Plan suivant :** ce que la ligne prépare pour la suite.

### Ressources explicites obligatoires

Toute carte indispensable doit être soit visible dans **Situation / Main de départ**, soit réellement obtenue pendant la ligne. Il est interdit d'écrire une chaîne qui suppose silencieusement une troisième carte, un monstre déjà présent ou une ressource de Cimetière non annoncée.

### Finisher ≠ starter

Lorsqu'un boss est surtout un payoff de milieu / fin de duel, l'afficher comme tel :

`développement initial → accumulation / condition → accès au finisher → payoff`

Ne pas présenter artificiellement un finisher tardif comme une ligne d'ouverture.

### Guide de décision — matérialisation visible RC5

Lorsqu’une decklist complète affiche **au moins deux Axes numérotés**, matérialiser après les Axes un bloc visible **`## Guide de pilotage`**. Ce bloc reste compact : il ne répète pas les combos, il extrait seulement les décisions réellement utiles déjà produites par les Axes.

À l’intérieur, utiliser **Choix de branche** lorsque plusieurs Axes, moteurs ou boss se concurrencent réellement. Si les Axes ne se concurrencent pas, le guide peut se limiter à 2–4 règles courtes du type `situation → plan`.

La présence d’un bloc `Choix de branche` isolé à l’intérieur des Axes ne remplace pas ce `Guide de pilotage` visible quand il existe au moins deux Axes.

Lorsqu'un deck possède plusieurs Axes, moteurs ou boss réellement concurrents, terminer le guide par un bloc compact **Choix de branche**.

Format possible en flèches :

`ressources / état observé → plan conseillé`

ou, si plusieurs cas rendent le scan nettement plus clair, par un petit tableau à deux colonnes **Situation observée | Plan conseillé**.

Ce guide n'est pas un classement de puissance. Il répond uniquement : **« Avec ma main / mon état actuel, quelle branche dois-je essayer de jouer ? »**

Ne pas l'ajouter si le choix est évident ou si le deck est essentiellement mono-ligne.

### Garde-fou de densité

**Combos utiles > combos spectaculaires.** Privilégier les mains fréquentes, décisions ambiguës, erreurs de séquençage, lignes de lethal, conversions importantes, recovery lines réelles et usages non évidents des ressources.

Une situation « après interruption » ne doit jamais être inventée lorsque le deck n'a pas de continuation réelle. Une main imparfaite sans sortie utile peut être omise plutôt que transformée artificiellement en combo.


### Après refactor matériel — restitution obligatoire de l’impact combos

Lorsqu’un `material-change` a créé `deck-vN+1`, le rendu de la nouvelle version doit contenir un bloc visible **`## Impact sur les combos`** alimenté par `combo_impact.json`.

- `UNCHANGED` → écrire explicitement **`Statut des combos : UNCHANGED`** puis une phrase contenant **`Aucun Axe essentiel modifié`** ;
- `MODIFIED` → écrire **`Statut des combos : MODIFIED`** et réafficher au minimum les Axes/lignes réellement touchés dans leur version actuelle ;
- `REMOVED` → écrire **`Statut des combos : REMOVED`** et nommer les anciennes lignes devenues invalides.

Ce bloc est une restitution de delta, pas une duplication complète du guide. Il est interdit d’afficher seulement la nouvelle decklist après un changement matériel touchant starters, ratios structurels, ressources, restrictions ou Extra Deck utilisé par une ligne sans informer explicitement le joueur de l’impact sur les combos.

### Préservation des autres couches de présentation

Le renforcement du pilotage **ne remplace et ne réduit aucune autre règle de STRUCTURE**. Les cartes emblématiques, mini-schémas, mini-carrousels de combo, ponctuations de personnalité, répliques terminales, traitement visuel des Axes signature et climax continuent de s'appliquer exactement selon leurs sections respectives.

Le guide de pilotage enrichit la **lecture pratique des Axes et de leurs situations dérivées** ; il ne remplace aucune couche visuelle ou de personnalité et ne devient pas un nouveau format global de réponse.

### Climax / Axe signature — traitement visuel du Style

Un **Axe signature** est un Axe qui matérialise particulièrement bien le **Style annoncé** et en représente le climax mécanique le plus lisible.

Repères principaux :
- `OTK / FTK` → ligne qui ferme réellement la victoire ;
- `Control / Lock` → ligne qui installe ou ferme le contrôle décisif ;
- `Burn` → boucle ou conversion qui ferme les LP ;
- `Synchro Climb / Combo` → chaîne signature menant au payoff terminal ;
- autre Style fonctionnel → Axe qui exprime le plus clairement son accomplissement.

#### Mini-carrousel de combo

Si des images pertinentes sont accessibles, un Axe signature peut recevoir **un mini-carrousel de 3 à 4 cartes maximum** montrant les pièces essentielles de la conversion jusqu’au payoff. Si le climax appartient à une **Branche** ou à une **ligne** précise de cet Axe, placer le mini-carrousel au niveau de cette branche / ligne afin qu'il illustre le combo réellement concerné ; la nouvelle séparation Axe / Starter / Branche / Combo ne doit jamais faire disparaître ou déplacer hors contexte un carrousel requis.

**Cas obligatoire :** lorsqu’un Axe réunit **un payoff majeur qui accomplit directement le Style** et **une réplique terminale du personnage**, il doit recevoir ce mini-carrousel si les images pertinentes sont accessibles.

Formule courte :

**payoff majeur + réplique terminale + images accessibles → mini-carrousel obligatoire.**

### Préflight visuel obligatoire — matérialisé

Avant `RENDER_CONTRACT_FROZEN`, produire `visual_assets.json` puis fermer `VISUAL_ASSETS_BOUND`.

Ce fichier doit être dérivé des deux autorités STRUCTURE et préciser :

- `image_lookup_attempted: true` pour toute decklist complète ;
- `image_capability_status: AVAILABLE | UNAVAILABLE` ;
- les **références réellement retournées par l’outil d’images** lorsque disponible (`turn…image…`) ;
- l’applicabilité du carrousel principal ;
- l’existence éventuelle d’un finisher spectaculaire ;
- l’obligation de réplique terminale ;
- l’applicabilité du mini-carrousel signature ;
- les cartes sélectionnées et le parent Axe/Branche du climax.

**Interdiction absolue : inventer une référence d’image ou déclarer une recherche effectuée sans l’avoir réellement exécutée.** Si l’outil n’est pas disponible ou échoue réellement, `UNAVAILABLE` doit porter une raison factuelle et le système continue sans carrousel.

Lorsque les refs sont disponibles, un carrousel n’est considéré comme matérialisé que si le `render manifest` contient le composant correspondant avec ces refs et si la réponse Chat l’insère réellement comme composant visuel ; un fichier placeholder ou une simple ligne de texte ne suffit pas.

Le harness valide les liaisons et la présence ; la présente source décide toujours quelles cartes illustrent le climax.

### Décision visuelle obligatoire

Pour une decklist complète, l’autorité doit **décider explicitement** avant `RENDER_CONTRACT_FROZEN` :

- quel Axe/Branche porte le climax signature ;
- s’il existe un finisher spectaculaire → réplique terminale requise ;
- si `payoff majeur + réplique terminale` est vrai → vérifier activement l’accès aux images pertinentes ;
- si la capacité d’image est disponible et fournit les cartes pertinentes → mini-carrousel requis ;
- si la capacité d’image est réellement indisponible/échoue → conserver séparément la décision d’applicabilité du carrousel et l’état d’indisponibilité ; le composant peut être omis de la surface faute d’assets, mais un Black-Box exigeant ce composant reste `UNVERIFIED/BLOCKED` et ne devient jamais `PRESENTATION_PASS` par simple absence d’images.

**Ne pas avoir recherché les images ne signifie jamais “images inaccessibles”.** Lorsqu’une capacité d’image existe dans l’environnement, elle doit être tentée pour le climax qui satisfait les conditions ci-dessus.

Pour tout finisher spectaculaire identifié, la réplique terminale doit entrer dans le contrat sous l’identifiant **`signature-terminal-quote`** ; lorsqu’un mini-carrousel devient applicable, il doit entrer sous l’identifiant **`signature-mini-carousel`** avec `component_min_count`.

### RC16.15 — Cardinalité exacte de la réplique terminale signature

Lorsque `signature-terminal-quote` est applicable, cette autorité doit produire **une seule assertion native `regex_exact_count`**. Elle fixe elle-même :
- le `pattern` correspondant à la réplique terminale canonique et couvrant toutes ses formes de rendu terminal possibles dans ce climax ;
- `exact = 1` ;
- `scope_start` et `scope_end` délimitant l’Axe, la Branche ou la ligne de climax concernée.

Le pattern ne doit pas compter les ponctuations de personnalité étrangères au climax et le scope ne doit pas englober arbitrairement toute la decklist. Une même réplique terminale matérialisée deux fois dans ce scope — par exemple une fois en heading canonique puis une seconde fois en blockquote — est un échec de rendu. Une autre réplique située dans un climax réellement distinct hors scope reste indépendante.

Le runtime ne décide jamais qu’une quote est applicable et ne choisit ni son texte, ni son pattern, ni son scope. Il vérifie uniquement le binding spécialisé `signature-terminal-quote → regex_exact_count / exact=1 / scope présent`, puis exécute l’assertion compilée. `terminal_quote_required=false` n’impose aucune quote. La règle du mini-carrousel reste indépendante.

### Binding contractuel du mini-carrousel signature — V10 / RC16.12

L’identifiant spécialisé et la primitive physique sont deux dimensions distinctes. Lorsqu’un mini-carrousel signature est applicable, conserver **`signature-mini-carousel`** comme identité normative du requirement et du composant, mais utiliser la primitive physique canonique **`mini-carousel`** pour le renderer.

Le requirement spécialisé doit donc porter exactement :

- `id = signature-mini-carousel` ;
- une assertion `component_min_count` ;
- `component_type = mini-carousel` ;
- `parent = <Axe/Branche du climax décidé ici>` ;
- `min = 1`.

Le `component_plan.json` correspondant doit porter :

- `component_id = signature-mini-carousel` ;
- `type = mini-carousel` ;
- le **même `parent`** ;
- les cartes et `image_refs` issues de la décision visuelle de cette autorité.

`component_id` conserve l’identité sémantique spécialisée ; `type` décrit uniquement la primitive physique de rendu. Ne jamais utiliser `signature-mini-carousel` comme `type` de renderer et ne jamais renommer le requirement spécialisé en simple `mini-carousel`. Le harness vérifie ce binding sans choisir l’applicabilité, le parent, les cartes ou les images.

Lorsque le carrousel principal **Cartes emblématiques** est applicable, utiliser l’identifiant **`main-card-carousel`** avec `component_min_count` de type `main-carousel`. Le harness ne choisit toujours pas l’applicabilité : il exécute la décision prise ici.

Certains Styles comme `Control`, `Lock` ou `Grind` peuvent posséder un Axe signature sans cri de finisher ; dans ce cas, le mini-carrousel reste facultatif mais prioritaire s’il améliore réellement la compréhension du mécanisme décisif.

### Quantité

Généralement, **1 Axe signature visualisé** suffit. Un second mini-carrousel est légitime lorsqu’un second Axe accomplit réellement le Style par une **route, une conversion ou un payoff différent** et gagne clairement à être visualisé.

Ne jamais ajouter un mini-carrousel pour atteindre un quota.

Le mini-carrousel de combo :
- illustre une ligne déjà construite et validée ;
- montre prioritairement les **3 à 4 pièces essentielles** de la conversion jusqu’au payoff ;
- ne remplace ni la chaîne technique ni l’explication de l’axe ;
- ne doit pas être utilisé pour chaque combo ;
- ne doit pas répéter inutilement le carrousel principal des **Cartes emblématiques** ;
- ne doit jamais influencer la sélection des cartes ou la construction du deck.

### Voix du personnage dans l’axe

Deux usages sont distincts :

- **Ponctuation de personnalité — facultative par axe, attendue globalement lorsqu’elle est naturelle :** une courte réplique peut apparaître pendant une interaction, conversion, résurrection, retournement, découverte de solution, bluff, prise de risque ou autre action fortement caractéristique. Sur une decklist développée avec plusieurs axes, rechercher naturellement **1 à 3 ponctuations au total** lorsque de vrais moments de personnalité existent. Ne jamais les répartir artificiellement par quota. Elles restent intégrées à l’axe et visuellement discrètes.
- **Réplique de finisher — obligatoire lorsqu’il existe :** si l’axe aboutit à un **véritable finisher spectaculaire clairement identifiable**, placer la réplique directe du personnage **au moment exact du payoff final**. Elle représente **l’accomplissement du Style** et doit être plus ample et spectaculaire qu’une ponctuation intermédiaire, généralement en **1 à 4 phrases courtes**.

Format attendu lorsque le finisher spectaculaire existe :

`ressource → action → conversion → finisher`

### **PERSONNAGE — « Réplique de climax adaptée au finisher. »**

Sur une decklist complète possédant au moins un finisher spectaculaire, **au moins une réplique terminale doit être matérialisée dans le rendu exact** ; une simple mention du boss dans Concept/Decklist ne satisfait pas cette obligation.

Le titre Markdown + gras constitue le traitement visuel normal de la réplique terminale : **plus grande, grasse et isolée** de la chaîne technique. Ne pas ajouter un label décoratif supplémentaire comme `Moment`, `Spectacle`, `Payoff` ou `Finisher`.

Une réplique utilisée plus tôt dans l’axe **ne remplace pas** la réplique du finisher.

Ne pas ajouter artificiellement une réplique terminale si l’axe ne possède pas de climax clairement identifiable.

### Cohérence Style → Axes

Chaque tag fonctionnel majeur annoncé dans **Style** doit être matérialisé par les Axes conformément à `HOOK_STYLE_AXES_CONSTRUCTION_DECKS_PERSONNAGES`.

Lorsqu’un Style fonctionnel est **central**, afficher normalement **au moins deux Axes distincts** qui l’expriment sous des angles réellement différents. Ne pas compter comme second Axe une simple variation de starter ou la même chaîne légèrement modifiée. Si le hook reconnaît une architecture légitimement mono-ligne, un seul Axe central peut suffire.

- `OTK / FTK` → montrer la ou les lignes de victoire explicites retenues par le hook ; pour l’OTK, rendre lisible le total de dégâts ou la fermeture du kill ;
- `Control / Lock` → montrer concrètement les interruptions, retraits de ressources ou restrictions qui prennent le contrôle ;
- `Burn / Grind / Swarm / Toolbox / Climb` → montrer respectivement la conversion en dégâts, la boucle de ressources, la génération de corps, les embranchements ou la chaîne de conversions.

Si aucun axe ne démontre le tag, **retirer le tag ou corriger la construction**.

### Règle de densité

**Tous les combos utiles peuvent être montrés ; ce qui doit rester court est la narration.**

Une ligne de 15 actions peut être longue techniquement mais doit rester visuellement scannable. Si une seule chaîne devient illisible, la découper en **2 à 5 sous-chaînes fonctionnelles** (`Départ`, `Développement`, `Conversion`, `Finisher`, par exemple) plutôt que la transformer en pavé ou en tutoriel numéroté.

**La compacité ne doit jamais supprimer l'information nécessaire au pilotage.** Sur un Axe central, si le joueur sait ce que le combo produit mais ne sait pas **avec quelle main le commencer, quoi chercher, quoi garder ou comment atteindre effectivement le payoff**, l'Axe est trop abstrait et doit être détaillé.

Les mini-carrousels de combo sont des **accents visuels du climax mécanique**, pas une nouvelle couche systématique : ils servent d’abord à rendre visible l’accomplissement du Style. S’ils ralentissent le scan ou n’ajoutent aucune compréhension du payoff, les omettre.

---

## Formule courte

**Recevoir les Axes et lignes validés → distinguer Axe / Starter / Branche / Combo lorsqu’ils existent réellement → garder les flèches comme langage principal → préserver lignes situationnelles, restrictions, choke points et erreurs utiles → attacher mini-carrousel et voix au payoff exact → rester compact et scannable.**


---

# 8. Sortie contractuelle de rendu — scannabilité exécutable

Pour une decklist complète, la présente autorité doit traduire ses obligations réellement applicables en exigences du `RENDER_CONTRACT_FROZEN` avant la rédaction finale.

Le harness n'invente aucun critère de densité : il exécute uniquement les assertions émises ici.

## Garde-fou mécanique de densité

La règle existante « découper une chaîne illisible en 2 à 5 sous-chaînes fonctionnelles » devient matérialisable ainsi :

- dans les sections Axes / Pilotage, **une ligne physique ne doit normalement pas porter plus de 4 transitions `→`** ;
- au-delà, découper la séquence en sous-chaînes fonctionnelles ;
- une exception n'est possible que si la présente autorité marque explicitement la ligne comme interaction simple et scannable dans le contrat.

Pour éviter qu'une ligne sans beaucoup de flèches devienne malgré tout un pavé, ajouter également sur cette zone une limite de **220 caractères par ligne physique**, sauf exception explicitement justifiée par la présente autorité.

### RC16.10 — binding natif obligatoire de `axis-line-length`

Cette contrainte de longueur reste **source-owned** : la présente autorité décide du seuil, du scope et des exceptions. Sa représentation mécanique est désormais contractuellement fixée afin d'empêcher une traduction regex sémantiquement différente.

Le requirement doit être :

```json
{
  "id": "axis-line-length",
  "source": "STRUCTURE_AXES_COMBOS_DECKS_PERSONNAGES",
  "applicable": true,
  "description": "axis line length",
  "assertions": [
    {
      "type": "max_line_length",
      "max": 220,
      "scope_start": "^##\\s+6\\.\\s+Axes de jeu\\b.*$",
      "scope_end": "^##\\s+8\\.\\s+Point de rupture\\b.*$"
    }
  ]
}
```

Pour `axis-line-length`, `contains_regex`, `regex_min_count` ou toute regex simulant une limite de longueur sont interdits. Le runtime peut vérifier que le type natif et un scope existent, mais il ne redéfinit jamais la valeur `220` : cette valeur appartient exclusivement à la présente autorité.

## Hiérarchie et composants visuels

Le `RENDER_CONTRACT_FROZEN` doit refléter le préflight visuel, pas seulement la forme textuelle obtenue après rédaction. Pour chaque climax spectaculaire applicable :

- assertion native `regex_exact_count` pour la réplique terminale, avec `exact = 1` et un scope limité au climax signature concerné ;
- `component_min_count` pour le mini-carrousel lorsque l’accès actif aux images a réussi.

Un contrat qui omet une obligation déclarée applicable au préflight est incomplet et ne doit pas être gelé.


### RC16.3 — sortie policy, pas copie des faits

Avant freeze, cette autorité contribue à `render_policy.json`. Elle continue de choisir ses exigences spécialisées (densité, Starter/Résultat, climax, mini-carrousel), mais ne recopie aucun fait autoritaire déjà connu. Les bindings dérivables sont compilés par `compile-render-contract`; seul le contrat compilé peut ensuite devenir `RENDER_CONTRACT_FROZEN`.

La présente autorité ne modifie ni les totaux de decklist, ni la direction finale, ni les IDs/hashes de version pour satisfaire un rendu.

### RC16.2 — immutabilité et anti-boucle

Avant freeze, corriger librement un contrat incomplet. Après `RENDER_CONTRACT_FROZEN`, son contenu exact est immuable : une erreur de longueur, densité de flèches, Starter/Résultat, mini-carrousel ou autre assertion se répare dans le rendu, **jamais en affaiblissant ou remplaçant l’assertion**.

`render-check` doit recevoir le rendu candidat et les composants matérialisés, agréger les défauts déterministes et, sur PASS seulement, produire le manifest canonique. Tant que `FINAL_RENDER_PREPARED` n’est pas fermé, les corrections restent des attempts du même `render-vN`. Les retries sont bornés par le runtime ; une stagnation ou un budget épuisé impose STOP fail-closed.


Lorsque la construction transmet un Starter, une Branche, un Résultat, une restriction ou un climax comme élément distinct nécessaire au pilotage, le contrat doit contenir l'assertion de présence correspondante dans le rendu exact.

Lorsqu'un carrousel principal ou mini-carrousel est obligatoire selon les règles déjà définies dans cette source, l'exigence contractuelle doit utiliser `component_min_count` avec son type et, lorsque pertinent, son parent afin qu'un composant déplacé ou supprimé ne puisse pas satisfaire artificiellement le contrat.

**Règle courte : présence + hiérarchie + scannabilité doivent survivre matériellement au rendu, pas seulement être affirmées dans son manifest.**

---

# 9. Continuité matérielle des mini-carrousels et composants de climax

Lorsqu’un mini-carrousel ou autre composant visuel spécialisé a été requis et matérialisé sur un Axe, une Branche ou un climax, une mutation de présentation qui ne change ni le deck ni les combos doit préserver cette couche.

Le contrat de `render-vN+1` doit déclarer pour chaque composant provenant de `render-vN` :

- `PRESERVE` si le composant peut être transporté tel quel ;
- `REGENERATE` si sa représentation doit être recréée pour le nouveau rendu.

En cas de `REGENERATE`, le nouveau composant doit nommer le composant qu’il remplace, conserver le même type fonctionnel, rester rattaché au même Axe / Branche / climax et conserver les tags structuraux pertinents.

Une ligne Markdown du type `🃏 A → B → C` n’est pas un mini-carrousel matérialisé.

Chaque composant doit posséder un artefact matérialisé et hashé dans le render manifest. Cette règle ne décide pas quand le carrousel est obligatoire : elle empêche seulement qu’un composant déjà requis disparaisse lors d’une réécriture éditoriale.

**Règle courte : composant requis sur render-vN → PRESERVE ou REGENERATE sur render-vN+1 ; disparition silencieuse interdite.**


## RC8 — fidélité de résolution des effets

Quand `VALIDATION_PILOTAGE_LIGNES_DECKS_PERSONNAGES` a fermé une résolution d'effet dans `pilotage_contract.json`, le rendu de l'Axe doit préserver cette résolution sans la simplifier en un choix plus favorable. Une résolution validée `ALL_POSSIBLE`, `UP_TO_N`, `EXACT_N` ou une activation optionnelle doit rester lisible comme telle dans la ligne affichée lorsque cette distinction conditionne la continuation.

STRUCTURE ne redécide jamais le texte de carte ; elle interdit seulement qu'une reformulation de présentation réintroduise une liberté que la validation spécialisée n'a pas accordée.

## RC9 — continuité du climax lors d'un refactor matériel

Quand un deck déjà rendu est refactoré, les mini-carrousels et la voix attachés à un Axe / Branche / climax ne sont pas remis à zéro par défaut.

Après revalidation des Axes :

- conserver le composant s'il reste exact (`PRESERVE`) ;
- le recréer s'il reste applicable mais que la ligne, les cartes ou le parent ont changé (`REGENERATE`) ;
- ne le supprimer que si l'autorité STRUCTURE conclut explicitement que le climax correspondant n'est plus applicable (`DROP_EXPLICIT` + raison).

Cette règle ne protège pas artificiellement un ancien combo : elle protège uniquement la **continuité du rendu encore applicable** sur la nouvelle version validée.

## Couverture des Axes — RC11

Tout bloc rendu sous un heading `Axe N ...` est une ligne essentielle destinée au joueur et doit être fermé individuellement par `VALIDATION_PILOTAGE_LIGNES_DECKS_PERSONNAGES` sur le rendu exact.

Ne pas utiliser un heading `Axe N` pour une idée seulement situationnelle, une orientation vague ou une suite non reproductible. Ces éléments vont dans le `Guide de pilotage`, `Choix de branche`, `Point de rupture` ou une branche explicitement situationnelle.

Le rendu spécialisé doit donc préserver une correspondance claire : **1 Axe numéroté affiché = 1 ligne de pilotage validable**.


## RC13 — survie visible des conditions de légalité

Le rendu ne montre jamais les Fact/Constraint Catalogs ni le cold sweep. En revanche, lorsqu'une condition de légalité validée par `VALIDATION_PILOTAGE_LIGNES_DECKS_PERSONNAGES` change ce que le joueur doit réellement faire, elle doit survivre dans la ligne sous une forme courte et jouable : exception de matériau, cible nécessaire, ressource à conserver, restriction active, placement précis, condition de timing ou autre garde-fou déterminant.

Ne pas transformer cette règle en commentaire juridique carte par carte. Afficher uniquement les conditions dont l'omission ferait raisonnablement exécuter une action illégale ou casserait la ligne validée.

Un `placement_binding` critique doit être rendu au moment de l'action qui choisit la zone ; il ne peut pas être déplacé après coup vers un simple commentaire d'état.


## RC14 — rendu des résultats calculés et du placement

Lorsqu'un résultat matériel/chiffré est fourni par les `derived_claims` validées, **rendre la valeur calculée**, sans la recalculer ou l'arrondir librement : nombre de cartes dans une zone, cibles/destructions, ATK, dégâts, zones libres, etc.

Pour une claim `CONDITIONAL` ou `RANGE`, conserver dans le rendu les conditions/bornes qui empêchent d'interpréter la valeur comme garantie.

Lorsque le contexte autorise plusieurs placements Extra Deck et que le choix modifie la suite, rendre la décision au moment de l'action, par exemple sous forme concise `→ placer en Main Monster Zone` ou `→ placer en Extra Monster Zone`. Ne pas déplacer cette information vers un commentaire ultérieur d'état.

La présente source ne calcule aucune valeur et ne choisit aucune zone : elle affiche exactement la sortie transmise par la validation de pilotage.

## RC15 — placement spatial reproductible

Quand `VALIDATION_PILOTAGE_LIGNES_DECKS_PERSONNAGES` marque un placement comme matériel à une relation spatiale nécessaire à la suite, le rendu doit donner l'instruction **au moment de l'action**.

Il ne suffit pas d'écrire qu'un monstre est « sur le Terrain » ou qu'une zone est libre. Si la continuation dépend de la position relative à une ressource déjà placée, le joueur doit pouvoir reproduire ce choix sans l'inférer lui-même.

Exemples de forme autorisée :

- `→ placer X dans la MMZ pointée par L` ;
- `→ utiliser l'EMZ gauche afin d'ouvrir la zone nécessaire à Y` ;
- autre formulation courte équivalente transmise par Pilotage.

STRUCTURE ne calcule jamais la topologie et ne choisit aucune position. Elle préserve uniquement dans le rendu les placements critiques déjà fermés par Pilotage.

### RC15 — slot visible = slot validé

Lorsqu'un placement spatial est matériel, STRUCTURE doit rendre le **même slot** que celui validé par Pilotage. Une reformulation peut être naturelle, mais elle ne peut pas déplacer la carte vers une autre MMZ/EMZ ni supprimer l'information positionnelle nécessaire à la continuation.

---

## Addendum RC16.23 — ancres de survie structurelle

Lorsque Style → Axes transmet un inventaire structurel au Pilotage, le rendu doit préserver des ancres textuelles stables permettant de retrouver chaque Axe, starter et branche / ligne requise sans faire du rendu la source de vérité de leur existence. Ces ancres servent uniquement au contrôle de survie ; elles ne changent ni la sélection métier des starters ni les règles visuelles de la présente source.

---
## RC16.23 — Rendu compilé des Axes / climax

Les décisions de cette source sur Axe, Starter, Branche, climax, mini-carrousel et réplique restent normatives. Leur **plomberie de rendu** ne l'est pas : lorsque l'applicabilité et le contenu sont déjà décidés, le runtime matérialise automatiquement les ancres, composants, parent du mini-carrousel et cardinalité de la réplique.

Une disparition de ces éléments après leur déclaration est un défaut `PRESENTATION_RENDER`/compiler et ne doit pas être renvoyée à l'IA comme tâche de secrétariat.
