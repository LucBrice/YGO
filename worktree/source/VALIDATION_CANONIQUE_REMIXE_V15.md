# Validation du Canonique remixé

**Version : V15-L3 / V4 Lean RC4**

## AUTHORITY

Seule autorité détaillée sur la frontière Canonique ↔ Canonique remixé ↔ Alternatif et, pour un Remixé, Hybride ↔ Intégré.

Exécuter avant construction d’une piste Remixée puis reclasser sur la decklist finale.

## Définitions

- **Canonique** : même architecture fondamentale ; optimisation, spécialisation ou support du même plan.
- **Canonique remixé — Hybride** : identité canonique structurelle + seconde architecture structurelle significative, encore partiellement séparable.
- **Canonique remixé — Intégré** : même base, mais les deux architectures se transforment/conditionnent mutuellement dans les lignes habituelles.
- **Alternatif** : l’identité canonique n’est plus structurelle.

Hybride et Intégré ne sont pas des niveaux de qualité.

## Contrat d’intention fonctionnelle — AVANT exploration

Une demande utilisateur peut contenir simultanément :

- une **étiquette souhaitée** (`Canonique remixé`, `Hybride`, `Intégré`) ;
- une description concrète de ce que doit faire le système ajouté (`corps gratuits`, `défausse`, `pioche`, `matériaux`, `accès Extra Deck`, etc.).

Ces deux informations n’ont pas la même autorité.

**La description fonctionnelle explicite prime sur l’étiquette souhaitée.**

Avant l’exploration, matérialiser `functional_intent.json` avec les systèmes explicitement cités par l’utilisateur et, pour chacun :

- `name` ;
- `position: PRIMARY | SECONDARY` ;
- `role: PRIMARY | FACILITATOR | MODULE | SECONDARY_ARCHITECTURE | OPEN` ;
- `role_basis: USER_EXPLICIT | OPEN` ;
- `functions` — fonctions effectivement demandées, sans en inventer de nouvelles ;
- éventuelles contraintes quantitatives (`package_size`, ratios, etc.) avec `protection: UNPROTECTED_BY_DEFAULT` sauf exigence identitaire indépendante démontrée.

### Gel d’un rôle explicite

Si `role_basis = USER_EXPLICIT`, ce rôle est **figé pour le run courant**.

L’exploration peut découvrir une autre idée intéressante, mais elle ne peut pas transformer silencieusement un facilitateur/module explicitement demandé en `SECONDARY_ARCHITECTURE` uniquement pour sauver :

- une étiquette Remixée ;
- une taille de package ;
- un payoff ajouté après coup ;
- ou une classification souhaitée.

Si une exploration propose réellement une autre architecture qui change ce rôle explicite, elle devient **une nouvelle piste/concept à faire sélectionner par l’utilisateur avant construction**. Elle ne sert pas de justification rétroactive dans le même run.

### Anti-rationalisation créative

Un payoff, boss, branche, carte-pont ou moteur ajouté principalement pour rendre vraie l’étiquette demandée ne peut pas être utilisé comme preuve que l’intention fonctionnelle initiale était déjà une seconde architecture.

Exemple abstrait :

`utilisateur : système B sert surtout de corps/pioche/défausse`  
`construction : on ajoute artificiellement un payoff B pour sauver Hybride`  
`→ CONCEPT_DRIFT, pas preuve de Remixé`.

Le harness gèle seulement ce contrat ; **la présente autorité reste seule responsable du choix du rôle**.

<!-- CLASSIFICATION_ROLE_POLICY_JSON:BEGIN -->
```json
{
  "schema_version": "1.0",
  "roles": ["PRIMARY", "FACILITATOR", "MODULE", "SECONDARY_ARCHITECTURE", "OPEN"],
  "directions": ["Canonique", "Canonique remixé", "Alternatif"],
  "remixed_requires_secondary_role": "SECONDARY_ARCHITECTURE",
  "user_explicit_role_immutable_within_run": true,
  "requested_label_is_non_authoritative": true,
  "direction_conflict_requires_user_selection": true
}
```
<!-- CLASSIFICATION_ROLE_POLICY_JSON:END -->

## Conditions obligatoires du Remixé

### A — Identité canonique structurelle

Elle doit contribuer significativement à plusieurs éléments du fonctionnement : moteur, ressources, extensions, matériaux, recherches, interruptions, conditions de victoire ou lignes principales.

Si elle peut être retirée sans changer substantiellement le fonctionnement → Alternatif.

### B — Seconde architecture structurelle significative

Elle doit créer au moins une vraie branche récurrente, famille de finishers, économie de ressources ou plan qui modifie sensiblement la construction.

Elle ne peut pas se réduire à « le même plan, mais plus rapide/régulier/puissant ».

## Gate positif — architecture secondaire prouvée

Une étiquette fournie par l’utilisateur (`Canonique remixé`, `Hybride`, `Intégré`) est une **hypothèse de direction**, jamais une preuve à protéger.

Avant d’autoriser **Canonique remixé**, vérifier d’abord que le `functional_intent.json` autorise réellement un rôle `SECONDARY_ARCHITECTURE`, puis produire intérieurement une preuve positive avec trois réponses concrètes tirées de la liste et des lignes finales :

1. **Fonction/branche/payoff propre** — quelle fonction récurrente du système ajouté dépasse l’apport de corps, matériaux, pioche, défausse, recherche, protection, accès ou consistance ?
2. **Retrait destructif** — quelle architecture ou branche disparaît réellement si ce système est retiré, au-delà d’une baisse de vitesse/puissance/régularité ?
3. **Substitution impossible** — pourquoi un fournisseur générique des mêmes ressources ne préserverait-il pas l’essentiel des lignes et finishers ?

Si l’une de ces trois réponses manque ou ne décrit que des ressources/facilitateurs, **Remixé est interdit sur cet artefact** : reclasser **Canonique** ou reconstruire réellement une seconde architecture.

Une quantité élevée de cartes du second système, une synergie spectaculaire ou une interaction mixte ne remplacent jamais cette preuve.

## Faux positifs bloquants

Reste normalement **Canonique** si le système extérieur ne fait principalement que :

- rechercher/pioche/protéger ;
- fournir matériaux, Attribut, Type, corps, Tributs ou défausse ;
- accélérer les mêmes boss ;
- recycler les mêmes ressources ;
- élargir une fonction déjà naturelle ;
- changer surtout la zone de transit des mêmes ressources ;
- rendre le même plan plus régulier sans créer de seconde architecture.

Une carte-pont générique prouve au mieux la compatibilité, pas l’intégration.

## Tests obligatoires

### 1. Nouveauté intrinsèque

La fonction présentée comme nouvelle existait-elle déjà naturellement dans les cartes/boss canoniques ?

Oui + seulement plus accessible/fréquente/large → Canonique, sauf architecture nouvelle démontrée séparément.

### 2. Retrait

Retirer le système extérieur :

- si seule la puissance/consistance/vitesse baisse mais que la logique reste la même → Canonique ;
- si une seconde architecture disparaît → Remixé possible.

### 3. Substitution

Remplacer le système extérieur par un fournisseur générique des mêmes ressources :

- mêmes lignes/fonctions/finishers → facilitateur → Canonique ;
- logique stratégique nouvelle détruite → poursuivre.

### 4. Différence fonctionnelle

Pouvoir répondre précisément :

**« Qu’est-ce que ce deck fait structurellement que sa version canonique optimisée ne ferait pas de la même manière ? »**

La réponse ne peut pas être seulement vitesse, puissance, consistance ou changement de zone.

### 5. Hybride vs Intégré

- deux architectures significatives mais surtout parallèles → **Hybride** ;
- plusieurs lignes principales où A transforme/conditionne B et B acquiert une fonction à cause de A (ou inversement) → **Intégré**.

Le simple partage/conflit d’une ressource ne suffit pas à prouver Intégré.

## RED / GREEN / REFACTOR

### RED

Avant la liste, écrire intérieurement : identité canonique conservée + transformation/architecture nouvelle attendue + sous-type provisoire.

### GREEN

Ne construire comme Remixé que si A+B et les tests de nouveauté/retrait/substitution/différence fonctionnelle sont plausiblement satisfaits.

### REFACTOR / FINAL

Construire puis **effacer le sous-type provisoire** et reclasser depuis la liste/lignes réelles.

La reclassification peut **diagnostiquer** qu’une direction demandée ne survit pas aux preuves (par exemple Remixée → Canonique), mais ce résultat ne devient jamais silencieusement la nouvelle direction du run. Une divergence avec `direction_contract.json` produit `DIRECTION_CONFLICT` : arrêter avant l’étape suivante, présenter la piste réellement soutenue, puis attendre un nouveau choix utilisateur. La poursuite se fait dans un nouveau run avec une nouvelle direction explicitement sélectionnée.

Elle ne peut pas **promouvoir** un système `USER_EXPLICIT` figé comme `FACILITATOR` ou `MODULE` en seconde architecture dans le même run.

Une telle promotion impose `CONCEPT_DRIFT → retour à sélection du concept`, jamais une rationalisation terminale.

Questions finales :

1. l’identité canonique reste structurelle ?
2. le second système est réellement structurel ?
3. le plan extérieur fait plus que faciliter le même plan ?
4. retrait/substitution détruisent-ils réellement l’architecture nouvelle ?
5. les lignes habituelles sont-elles parallèles ou transformatrices ?
6. le Remix organise-t-il le fonctionnement habituel plutôt que rester option secondaire ?
7. la liste finale démontre-t-elle réellement la classification sans rhétorique ?
8. la preuve positive `fonction propre / retrait destructif / substitution impossible` est-elle complète sur l’artefact final ?

### Décision

- facilitateur du même plan → **Canonique** ;
- seconde architecture structurelle parallèle → **Canonique remixé — Hybride** ;
- transformation croisée récurrente → **Canonique remixé — Intégré** ;
- canonique non structurel → **Alternatif**.

Ne jamais forcer une piste Remixée pour remplir une catégorie et ne jamais « monter » artificiellement Hybride en Intégré.

## OUTPUT

Deux sorties matérialisées sont attendues :

1. **avant exploration** : `functional_intent.json` ;
2. **classification / reclassification finale** : résultat lié par hash à ce contrat.

Classification finale + preuve interne compacte :

- `secondary_architecture_function` ;
- `withdrawal_effect` ;
- `generic_substitution_effect` ;
- `secondary_architecture_proof: PASS | FAIL` ;
- `functional_intent_sha256` ;
- `effective_roles` par système ;
- `canonical_identity_structural: true | false` : décision métier explicite de cette autorité indiquant si l’identité canonique reste structurelle dans l’artefact évalué ;
- `canonical_identity_withdrawal_result: PRESERVED | DESTROYED_OR_SUBSTANTIALLY_CHANGED` : résultat structuré du test de retrait appliqué spécifiquement à l’identité canonique ; `false` exige `PRESERVED`, `true` exige `DESTROYED_OR_SUBSTANTIALLY_CHANGED` ;
- `identity_structure_basis` : justification métier compacte et non vide, fondée sur les moteurs/lignes/rôles réellement observés ;
- `phase: PROVISIONAL | FINAL` ;
- en phase finale, `snapshot_sha256`.

Pour une piste `Alternatif`, le test de retrait porte obligatoirement sur **l’identité canonique**, pas sur le nouvel axe alternatif : si retirer l’identité canonique détruit encore l’architecture du deck, `Alternatif` est contradictoire et doit être reclassé.

`canonical_identity_structural` n’est jamais inféré par le runtime. Cette autorité le décide à partir des preuves métier ci-dessus. Le runtime peut seulement vérifier la cohérence mécanique du couple résultat/preuve : `Canonique` ou `Canonique remixé` exigent `true`, tandis que `Alternatif` exige `false`. Une contradiction bloque la fermeture de classification ; elle ne permet jamais au runtime de choisir une autre classification à la place de cette autorité.

`FAIL` interdit une sortie Remixée. La justification détaillée reste invisible sauf audit demandé.

## DO_NOT_DECIDE

Viabilité pratique multi-systèmes, progression narrative, ratios, rendu, preuves/versioning du harness.
