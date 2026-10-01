# Game Rules — Yu-Gi-Oh! Legacy of the Duelist: Link Evolution — profil 2020

**Version : V1 / RC16 + MCB1 (durcissement post-RC16.22.1)**

## Rôle

Cette source est l'autorité unique du projet sur les **règles générales implicites du jeu** nécessaires aux lignes de decks dans l'environnement Link Evolution 2020.

`CONTEXTE_DECKS_YUGIOH_LINK_EVOLUTION_2020` sélectionne cet environnement et ce profil ; il ne redéfinit pas localement les règles ci-dessous.

Les textes propres aux cartes et rulings spécifiques appartiennent à `SEMANTIC_RULING_CONTRACT`.

Le harness ne crée aucune doctrine de ces mécaniques : il reçoit les faits, contraintes, profils et, lorsque nécessaire, les obligations mécaniques normalisées (MCB) déjà décidées par les autorités métier, puis en dérive seulement les conséquences déterministes.

## Sources de référence

- Konami — Master Rule, révision du 1er avril 2020 : `https://www.yugioh-card.com/japan/howto/masterrule2020/`
- Konami — Official Yu-Gi-Oh! TCG Rulebook : `https://www.yugioh-card.com/en/rulebook/`

Lorsqu'une interaction précise n'est pas couverte sans ambiguïté par ces règles générales, utiliser une preuve/ruling spécifique et la traiter comme `CARD_RULE_SOURCE` ou signaler `UNRESOLVED` ; ne pas inventer.

---

# 1. Profils

Les règles sont organisées dans une seule autorité avec des profils :

- `COMMON`
- `EXTRA_DECK`
- `FUSION`
- `SYNCHRO`
- `XYZ`
- `PENDULUM`
- `LINK`

Le profil applicable est sélectionné par Pilotage selon l'action réelle. Un profil n'est jamais appliqué simplement parce qu'une carte de ce type existe dans la decklist.

---

# 2. COMMON

### GR-COMMON-001 — état physique des cartes
Une carte ne peut satisfaire une condition de zone, position, relation ou matériau qu'à partir de son état réel au snapshot pertinent. Une présence abstraite « sur le Terrain » ne remplace pas une zone ou propriété exacte lorsqu'elle est matérielle.

### GR-COMMON-002 — décision de placement matérielle
Lorsque plusieurs placements sont légaux mais qu'ils ne préservent pas les mêmes actions futures, le choix de placement est une décision matérielle de pilotage.


### GR-COMMON-003 — conservation d'une source physique
Lorsqu'une action utilise matériellement une carte ou ressource physique et que sa disponibilité ultérieure dépend de cette utilisation, la transition correspondante doit être matérialisée. Une même copie ne peut pas être consommée une seconde fois tant qu'une transition explicite ne l'a pas rendue de nouveau disponible dans la zone requise. La destination exacte propre à un texte particulier reste sourcée par SRC lorsqu'elle n'est pas déductible de la règle générale applicable.

### GR-COMMON-004 — conséquence portant sur un ensemble
Lorsqu'une règle ou un texte normalisé impose une conséquence à **toutes** les ressources satisfaisant un predicate au snapshot courant, la portée est `ALL_MATCHING`. Le set est déterminé sur l'état courant ; il n'est pas légal de remplacer silencieusement cette portée par une sélection partielle. Les exceptions propres à une carte restent sous SRC.

### GR-COMMON-005 — dégâts et fermeture létale
Lorsqu'une ligne revendique `OTK`, `FTK` ou `lethal`, les contributions de dégâts matérielles doivent être comptabilisées comme événements. Une fermeture `GUARANTEED` n'est valide que si les dégâts garantis matérialisés atteignent au moins les LP adverses restant à la référence utilisée. Des dégâts conditionnels ne peuvent pas, seuls, ouvrir une fermeture `GUARANTEED`.

---

# 3. EXTRA_DECK — révision 2020

### GR-EXTRA-2020-001 — Fusion / Synchro / Xyz depuis l'Extra
Un Monstre Fusion, Synchro ou Xyz Invoqué Spécialement depuis l'Extra Deck peut être placé dans une Main Monster Zone libre ou dans une Extra Monster Zone utilisable.

### GR-EXTRA-2020-002 — Link / Pendule face recto depuis l'Extra
Un Monstre Link Invoqué depuis l'Extra Deck, ainsi qu'un Monstre Pendule Invoqué depuis l'Extra Deck face recto, doit utiliser une Extra Monster Zone utilisable ou une Main Monster Zone vers laquelle pointe un Monstre Link applicable.

### GR-EXTRA-2020-003 — hybrides Pendule dans l'Extra
Pour un monstre Fusion/Pendule, Synchro/Pendule ou Xyz/Pendule dans l'Extra Deck, le choix de zone dépend notamment de son état face recto / face verso dans l'Extra Deck conformément au profil 2020. Si cette distinction devient matérielle, elle doit être fermée explicitement dans le Line Contract.

---

# 4. FUSION

### GR-FUSION-001 — matériaux
Une Fusion Summon utilise les matériaux exigés par le Monstre Fusion et/ou par l'effet qui réalise l'Invocation. Les exigences propres au texte de carte restent des clauses SRC ; Pilotage doit fermer la présence, l'éligibilité, la provenance et la destination des matériaux lorsqu'elles sont matérielles.

---

# 5. SYNCHRO

### GR-SYNCHRO-001 — somme de Niveaux
Sauf texte/ruling qui modifie la procédure, une Synchro Summon doit satisfaire les exigences de matériaux du Synchro et la somme de Niveaux requise. Les propriétés Tuner/non-Tuner et autres qualifications matérielles doivent être vraies au moment de l'Invocation.

---

# 6. XYZ

### GR-XYZ-001 — matériaux attachés
Les monstres utilisés comme Matériels Xyz deviennent attachés au Monstre Xyz au lieu de rester des monstres séparés sur le Terrain. Lorsqu'un coût/effect détache un matériau, l'attachment correspondant doit réellement disparaître avant toute utilisation ultérieure.

### GR-XYZ-002 — matériau Xyz et « quitte le Terrain »
Devenir Matériel Xyz n'est pas traité comme une carte qui « quitte le Terrain » pour les effets qui se déclenchent spécifiquement lorsqu'elle quitte le Terrain. Cette distinction doit être appliquée lorsqu'elle est matérielle à la ligne.

---

# 7. PENDULUM

### GR-PENDULUM-001 — double mode
Un Monstre Pendule peut avoir un contexte d'effet Monstre et un contexte d'effet Pendule distincts. L'effet utilisé doit correspondre à l'état/zone réel de la carte.

### GR-PENDULUM-002 — Invocation depuis l'Extra face recto
Les Monstres Pendule Invoqués depuis l'Extra Deck face recto suivent `GR-EXTRA-2020-002` pour leur destination légale.

### GR-PENDULUM-003 — destination face-up Extra lorsqu'elle est applicable
Lorsqu'une règle générale Pendule remplace une destination vers le Cimetière par le placement face recto dans l'Extra Deck, cette transition doit être matérialisée si elle influence une ressource ultérieure. Les exceptions ou interactions spécifiques doivent être sourcées ; ne pas les déduire par analogie.

---

# 8. LINK

### GR-LINK-001 — destination depuis l'Extra
Une Link Summon depuis l'Extra Deck suit `GR-EXTRA-2020-002`.

### GR-LINK-002 — topologie des Link Markers
Les Link Markers créent des relations spatiales dépendant du **slot exact occupé par le Link**. Une relation « zone pointée » n'existe que si la topologie correspondant au slot courant la produit au snapshot concerné.

### GR-LINK-003 — déplacement / disparition du Link
Si la source Link change de slot ou quitte la zone qui fondait une relation spatiale, cette relation doit être recalculée ; elle ne peut pas être réutilisée depuis un ancien snapshot.

### GR-LINK-004 — propriétés de matériau
Les exigences de matériaux et de Link Rating doivent être fermées selon le texte du Monstre Link et les règles générales applicables. Lorsqu'un Link Monster est utilisé comme matériau et que sa valeur de Link est matérielle, Pilotage doit expliciter la valeur retenue dans le calcul.

---

# 9. Règle de matérialité

GAME RULES n'impose pas de recopier toutes ces règles dans chaque combo.

Pour chaque action critique :

1. sélectionner les profils applicables ;
2. ne lier que les `game_rule_id` matériellement nécessaires ;
3. rattacher chaque règle à un fait, une contrainte, une précondition d'état, un attachment ou une relation topologique du contrat existant.

En RC16.1, l'unique `unified_cold_audit` de Pilotage produit ensuite sa section `game_rules` sans consulter l'inventaire primaire des bindings. Le runtime compare exactement les IDs redécouverts aux bindings matériels. Règle oubliée ou binding initial non retrouvé → **FAIL**.

Les anciens `cold_game_rule_sweep` séparés restent acceptés uniquement pour régression RC16.

Règle non matérielle à la ligne → aucune inflation du contrat ou du rendu.

# Extension MCB1 — sortie mécanique des règles générales

Lorsqu'une règle générale ci-dessus est matériellement utilisée dans une ligne essentielle, Pilotage peut la lier à un MCB avec `source_kind = GAME_RULE`, `source_id = game_rule_id`, l'`action_id` concerné et un `RULEBOOK_SOURCE` déjà présent dans les preuves.

Le `unified_cold_audit` doit redécouvrir indépendamment les bindings GAME RULE matériels et leur projection mécanique attendue. Le runtime compare ces projections ; il ne décide jamais lui-même qu'une règle générale supplémentaire doit s'appliquer.

Interaction générale nécessaire mais non couverte sans ambiguïté par la présente source : preuve/ruling ciblé ou `UNRESOLVED` → **FAIL CLOSED**.

