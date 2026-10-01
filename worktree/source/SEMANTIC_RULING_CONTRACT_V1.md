# Semantic Ruling Contract — Decks personnages

**Version : V1 / RC16 + MCB1 (durcissement post-RC16.22.1)**

## Rôle

`SEMANTIC_RULING_CONTRACT` est l'autorité spécialisée qui transforme **uniquement les clauses matériellement importantes d'un texte de carte ou d'un ruling spécifique réellement utilisé dans une ligne essentielle** en références structurées consommables par `VALIDATION_PILOTAGE_LIGNES_DECKS_PERSONNAGES` et le harness.

Il ne choisit aucune carte, aucun Axe, aucun starter, aucune stratégie et ne définit aucune règle générale du jeu.

**Règle courte : CARD TEXT / CARD RULING → SRC. Les règles implicites du jeu appartiennent à `GAME_RULES_LINK_EVOLUTION_2020`.**

---

## 1. Principe minimal

Pour chaque effet réellement utilisé dans une ligne essentielle, formaliser seulement ce qui est matériel sous la chaîne :

`BEFORE → ACTION/EVENT → SUBJECT → TRANSITION → AFTER → CONSEQUENCES`

Les dimensions suivantes sont optionnelles et ne sont présentes que si elles changent réellement la légalité, l'état ou la continuation de la ligne :

- `CONDITION` ;
- `COST` ;
- `TARGET` ;
- `COUNT` ;
- `SOURCE` ;
- `DESTINATION` ;
- `TIMING` ;
- `PROPERTY` ;
- `PERMISSION` ;
- `RESTRICTION` ;
- `TRANSITION`.

Ne pas traduire intégralement le texte lorsque des clauses ne sont pas matérielles à l'utilisation concrète.

---

## 2. Lazy SRC obligatoire

Aucun SRC exhaustif des 40 + 15 cartes n'est requis.

Créer un SRC uniquement lorsque :

- l'effet est réellement utilisé dans une ligne essentielle destinée à l'affichage ;
- ou une permission / restriction créée par cet effet reste active et matérielle plus tard dans cette ligne.

Une carte non utilisée dans les lignes affichées ne reçoit aucun SRC par défaut.

---

## 3. Liaison au catalogue RC13+

Le SRC **ne crée pas un second Fact Catalog ni un second Constraint Catalog**.

Chaque clause matérielle normalisée référence exactement un `fact_id` ou `constraint_id` déjà produit dans le contrat de Pilotage.

Chaque clause conserve :

- `src_id` ;
- `subject_id` ;
- `effect_id` / mode d'effet réellement utilisé ;
- `evidence_id` vers un `CARD_RULE_SOURCE` ;
- `clause_id` ;
- `category` ;
- `normalized_ref` ;
- `material_to_line: true`.

Les faits ou contraintes référencés conservent `semantic_origin: CARD_RULE` lorsqu'ils proviennent du texte/ruling de la carte.

---

## 4. Modes d'une même carte

Lorsqu'une carte possède plusieurs textes fonctionnels selon son état ou sa zone — par exemple effet Monstre / effet Pendule — le SRC lie **le mode réellement utilisé**.

Il est interdit de justifier une action avec le SRC d'un autre mode du même carton physique.

---

## 5. Semantic Closure — base RC16.1, conservée sous MCB1

Une extraction initiale ne suffit jamais à fermer une ligne essentielle.

La fermeture sémantique héritée de RC16.1 utilise l'unique `unified_cold_audit` de Pilotage ; le chemin nominal MCB1 conserve cette passe et lui ajoute la projection mécanique froide définie en 5 bis. Sa section `semantic` est produite sans consulter l'inventaire SRC primaire : elle relit les preuves de texte/ruling réellement utilisées et redécouvre les `clause_id` matériels. Le runtime compare ensuite exactement les deux ensembles.

Clause matérielle supplémentaire, clause primaire non retrouvée ou preuve incompatible → **FAIL**.

Si l'interprétation reste ambiguë ou contradictoire sur une clause nécessaire : `semantic_status: UNRESOLVED` et la ligne essentielle est **FAIL CLOSED**. `PARTIAL` n'est pas transmissible si la partie ouverte peut changer la ligne.

Les anciens `cold_semantic_sweep` séparés restent acceptés uniquement pour régression RC16 ; ils ne font pas partie du chemin nominal MCB1.

**PASS sémantique ≠ vérité absolue du langage naturel.** Une même mauvaise interprétation reproduite dans les deux lectures reste un risque épistémique résiduel.

---


## 5 bis. Mechanical Consequence Binding — MCB1

Pour toute clause SRC `material_to_line: true` dont la signification impose une conséquence mécanique sur la ligne, SRC doit transmettre un **Mechanical Consequence Binding (MCB)** consommable par Pilotage et le Deterministic Shell.

Le MCB n'est **pas une nouvelle autorité** et ne crée ni second Fact Catalog, ni second Constraint Catalog, ni seconde Proof-Carrying Line. Il relie une clause déjà normalisée à une obligation mécanique canonique.

Chaque binding matériel porte au minimum :

- `binding_id` unique ;
- `source_kind = SRC_CLAUSE` ;
- `source_id = clause_id` ;
- `action_id` du step concerné ;
- `evidence_id` identique à la preuve de la clause ;
- `operator` mécanique canonique ;
- `scope` lorsque la portée est matérielle ;
- `params` nécessaires au calcul ;
- `material_to_line: true`.

Les familles supportées par le runtime couvrent au minimum : `REQUIRE`, `MOVE`, `CONSUME`, `OBTAIN`, `PRODUCE`, `PROPERTY_UPDATE`, `RESTRICTION_APPLY`, `RESTRICTION_RELEASE`, `APPLY_TO_MATCHING_SET`, `DAMAGE_EVENT`, `LETHAL_CHECK`. Les portées supportées comprennent `SINGLE`, `EXACT_N`, `UP_TO_N`, `ALL_MATCHING` et `ALL_POSSIBLE`.

**Juridiction :** SRC décide ce que signifie la clause et quelle obligation mécanique elle implique. Le runtime ne choisit jamais cette signification ; il calcule seulement la conséquence de l'obligation reçue. Lorsqu'une clause matérielle ne peut pas être projetée sans ambiguïté sur la surface supportée : `semantic_status: UNRESOLVED` → **FAIL CLOSED**.

### Projection froide

Le `unified_cold_audit` nominal redécouvre également, à partir des mêmes preuves figées mais sans lire les MCB primaires, la projection mécanique attendue : source, action, opérateur, portée et paramètres matériels.

Le runtime compare exactement :

`MCB primaire ↔ projection mécanique froide`.

Omission, divergence de portée (`ALL_MATCHING → SINGLE`), paramètre matériel différent ou obligation supplémentaire redécouverte → **FAIL**. Une concordance ne transforme toujours pas le runtime en oracle sémantique ; elle interdit seulement l'auto-certification d'une projection primaire non challengée.

### État effectif d’un matériel au moment d’une Invocation

Lorsqu’un texte de carte autoritatif modifie une propriété **uniquement lorsqu’elle est utilisée comme matériel**, la preuve de propriétés liée par `bind-summon-rules` doit transporter cette conséquence sous forme structurée `material_property_modifiers`. Ce champ reste une transcription d’une source/ruling autoritatif ; le runtime ne l’invente pas.

Format minimal d’un modifier :

```json
{
  "property": "level | tuner | effective_name",
  "operation": "ADD | SET",
  "value": -2,
  "when": {
    "summon_kind": "SYNCHRO_SUMMON",
    "material_zone": "FIELD",
    "boss_names": ["..."],
    "except_boss_names": ["..."]
  },
  "source_locator": "..."
}
```

Les champs de `when` sont optionnels et cumulatifs lorsqu’ils existent. Une condition, propriété, opération ou provenance non supportée est **FAIL CLOSED**. Pilotage valide les contrats d’Invocation avec les propriétés **effectives au moment de l’utilisation comme matériel** (niveau, rôle Tuner/non-Tuner, noms effectifs), jamais avec la seule valeur imprimée si un modifier applicable existe.

## 6. Ce que SRC ne doit jamais contenir

Ne pas recopier dans les SRC :

- règles générales Fusion / Synchro / Xyz / Pendulum / Link ;
- géométrie générale des Link arrows ;
- règle générale des Extra Monster Zones ;
- fonctionnement général des matériaux Xyz ;
- règles globales de position, de chaîne ou de zone.

Ces éléments appartiennent exclusivement à `GAME_RULES_LINK_EVOLUTION_2020` lorsqu'ils sont matériels.

---

## 7. Sortie vers Pilotage

Un SRC `CLOSED` ne valide pas la ligne.

Il transmet seulement des clauses matérielles normalisées à `VALIDATION_PILOTAGE_LIGNES_DECKS_PERSONNAGES`, qui doit ensuite vérifier :

- leur couverture par le Line Execution Contract ;
- leur état concret au bon snapshot ;
- leur propagation éventuelle vers des actions ultérieures ;
- leur survie dans le rendu lorsqu'une décision joueur en dépend.

## Addendum RC16.23.3 — déclenchement minimal

Ce contrat n'est pas un formulaire généralisé. Il n'est requis que lorsqu'une interaction matérielle ne peut pas être dérivée mécaniquement avec certitude. Le modèle fournit seulement l'interprétation sémantique et son locator de preuve ; IDs, hashes, bindings, scopes, propagation et fraîcheur restent compiler-owned. Une interaction essentielle non couverte reste fail-closed.


## RC16.23.8 — Monotonicité de certitude
La projection vers Render/Pilotage ne peut jamais renforcer une certitude métier. Invariant : `render_certainty <= semantic_certainty`. Un claim `CONDITIONAL`, `RANDOM`, `RANGE` ou `UNKNOWN` ne peut contenir dans sa portée rendue une formulation `guaranteed/garanti(e)(s)` ; seul un claim `GUARANTEED` matériellement fermé peut employer cette formulation. Un total numérique peut rester visible sous condition, mais ne doit pas être présenté comme garanti si le replay séquentiel exact n’est pas fermé.
