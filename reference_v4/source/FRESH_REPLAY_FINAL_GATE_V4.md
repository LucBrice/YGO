# Fresh Replay — Commande manuelle de certification

**Version : V5**

## Rôle

Cette source est un **artefact d’exécution déclenché manuellement**. Elle ne définit aucun critère métier.

Elle sert uniquement à rejouer, dans un **nouveau message utilisateur**, le pipeline applicable sur la dernière decklist complète déjà produite dans la conversation.

Les critères de viabilité, progression, classification, refactor, compression, validation finale, registre, validation mécanique et présentation restent exclusivement ceux de leurs sources spécialisées.

## Commande

La commande utilisateur est :

`/fresh`

Lorsque l’utilisateur envoie `/fresh` après une decklist complète :

- déclencher la présente source ;
- ne pas relancer une nouvelle idéation ;
- prendre la dernière decklist complète produite comme **artefact final existant à auditer** ;
- ignorer tous les PASS et conclusions de certification antérieurs.

Cette commande est **manuelle**. Elle n’est jamais lancée automatiquement pendant la génération normale d’un deck.

## Reset obligatoire

Attribuer à la dernière decklist complète :

`deck-v1`

Ignorer tous les anciens :

- PASS ;
- statuts de viabilité ;
- conclusions de compression ;
- validations finales ;
- confiances d’exécution ;
- registres, snapshots, reçus et traces instrumentales attachés aux anciennes versions.

Aucun statut antérieur ne peut servir de preuve dans cette exécution.

## Exécution

À partir de `deck-v1` :

1. réexécuter réellement toutes les autorités applicables dans leur ordre normal ;
2. réidentifier la relation fonctionnelle réelle entre les systèmes lorsqu’une architecture multi-systèmes est présente ;
3. exécuter le test de viabilité correspondant à cette relation ;
4. si une autorité exige un refactor, matérialiser une nouvelle version (`deck-v1 → refactor → deck-v2`, puis versions suivantes si nécessaire) avec delta observable ;
5. invalider comme `STALE` tout statut attaché à une version matériellement modifiée ;
6. après chaque modification matérielle, retester uniquement la nouvelle version ;
7. exécuter réellement la compression terminale et les contrôles terminaux exigés par les sources spécialisées ;
8. utiliser réellement `REGISTRE_EXECUTION_ARTEFACTS` et le validateur mécanique lorsqu’ils sont applicables ;
9. lorsque le validateur produit ou vérifie un reçu, exécuter réellement ces opérations ;
10. réexécuter `VALIDATION_FINALE_DECKS_PERSONNAGES` sur la dernière version exacte ;
11. n’attribuer une confiance terminale `ÉLEVÉE` que si toute la chaîne applicable est effectivement fermée.

Une mention conversationnelle d’un PASS, d’un registre, d’un validateur, d’un reçu ou d’un contrôle ne constitue jamais son exécution.

## Sortie de `/fresh`

Montrer seulement une trace compacte des versions et statuts réellement obtenus.

À la fin, indiquer :

- **Version finale exacte :** `deck-vN` ;
- **Statut :** `PASS_DIRECT`, `PASS_REFACTOR` ou `FAIL_ABANDON` lorsqu’un hook multi-systèmes est concerné ;
- **Confiance terminale :** `ÉLEVÉE`, `MOYENNE` ou `FAIBLE`.

Ajouter ensuite un bloc compact **Recommandation finale** fondé uniquement sur les artefacts, deltas et conséquences déjà établis pendant ce `/fresh` :

- **Refactor appliqué :** résumer visuellement les principaux deltas matériels sous forme compacte, par exemple `carte 2 → 1 · package 11 → 7 slots`. Ne jamais inventer une cause après coup.
- **Ce que le refactor améliore :** expliquer en quelques points le bénéfice observable directement lié au défaut corrigé et aux deltas réellement produits : moins de cartes mortes ou conditionnelles, moins de conflits de ressources, meilleur accès, package plus proportionné, meilleure résilience, simplification d'une ligne, etc. Ce champ est descriptif : il ne crée aucun nouveau critère de PASS et ne peut pas attribuer une amélioration que l'autorité compétente n'a pas établie ou que le delta ne permet pas raisonnablement de constater.
- **Impact sur les combos :** indiquer uniquement les Axes, lignes ou séquences dont le pilotage, les pièces, les ratios, les restrictions ou les embranchements ont effectivement changé à cause du refactor. Donner la modification sous forme compacte `avant → après` lorsque cela aide. Si les Axes protégés restent inchangés, le dire explicitement.
- **Résultat :** conclure en une phrase sur ce qui a été conservé et ce qui a été allégé/corrigé, sans transformer ce résumé en nouveau jugement métier.
- Si le deck obtient `PASS_DIRECT`, écrire simplement **Aucune modification requise pour la viabilité** ; **Ce que le refactor améliore : non applicable** ; **Impact sur les combos : aucun**.
- Si un refactor a eu lieu mais qu’aucun combo / Axe n’a changé matériellement, écrire explicitement **Impact sur les combos : aucun Axe essentiel modifié** plutôt que d’en fabriquer un.
- Si le statut est `FAIL_ABANDON`, remplacer la logique de bénéfice par **Défaut restant** : résumer le défaut matériel qui a empêché la fermeture et, s’il existe, le dernier refactor tenté ; ne pas présenter ces changements comme ayant rendu le deck viable.

La présentation attendue reste compacte et lisible :

```text
### Recommandation finale

**Refactor appliqué**
`delta 1` · `delta 2` · `delta 3`

**Ce que le refactor améliore**
- bénéfice observable 1 ;
- bénéfice observable 2 ;
- bénéfice observable 3.

**Impact sur les combos**
Résumé compact des Axes réellement modifiés, ou mention explicite qu'aucun Axe essentiel n'a changé.

**Résultat**
Une phrase de synthèse reliant le défaut corrigé au fonctionnement conservé.
```

Ce bloc reste un **résumé de sortie** : il ne redéfinit ni la viabilité, ni la compression, ni les critères des Axes. Il reflète uniquement les deltas et conséquences déjà établis par les autorités compétentes sur la version exacte.

Puis terminer uniquement par l’une des conclusions suivantes :

**PRODUIT FINAL VIABLE**  
ou  
**REFACTOR ENCORE NÉCESSAIRE**  
ou  
**CONCEPT À ABANDONNER**

Ne pas réafficher toute la decklist sauf si l’utilisateur le demande explicitement.

## Garde-fous de juridiction

`/fresh` :

- ne redéfinit aucun critère de compression ;
- ne redéfinit aucun critère de viabilité ;
- ne redéfinit aucun PASS ;
- ne redéfinit aucune classification ;
- ne redéfinit aucune règle de progression ;
- ne calcule pas lui-même la confiance terminale ;
- ne remplace ni le registre ni le validateur ;
- ne crée pas de boucle d’optimisation autonome.

## Formule courte

**Deck déjà produit → nouveau message `/fresh` → reset en `deck-v1` → réexécution réelle des autorités et instruments → statut frais → recommandation finale = refactor matériel + bénéfice observable + impact réel sur les combos / Axes.**


---

# Extension V5 — reset des contraintes narratives matérialisées

Lors d'un `/fresh`, ignorer en plus tout ancien :

- `narrative_contract.json` ;
- `narrative_conformance.json` ;
- hash, PASS ou inventaire de mécaniques rattaché à l'ancien run.

Le nouveau run doit :

1. relire le contexte narratif courant ;
2. réexécuter `VALIDATION_PROGRESSION_NARRATIVE` ;
3. produire un nouveau contrat narratif lié au nouveau `run_id` ;
4. auditer `deck-v1` contre ce contrat avant toute viabilité ;
5. bloquer immédiatement si une mécanique future est présente.

`/fresh` ne décide aucune mécanique autorisée. Il exige seulement une nouvelle preuve issue des autorités compétentes.

**Un ancien PASS narratif ne peut jamais traverser un `/fresh`.**
