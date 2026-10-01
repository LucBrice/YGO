# Contexte par défaut — Decks Yu-Gi-Oh!

## Référence principale

Pour toutes les demandes concernant des :

- decks ;
- decklists ;
- combos ;
- FTK ;
- OTK ;
- loops ;
- locks ;
- moteurs ;
- archétypes ;
- cartes à exploiter ;
- stratégies broken ou expérimentales ;

le contexte par défaut est :

**Yu-Gi-Oh! Legacy of the Duelist: Link Evolution — environnement 2020.**

## Règle de contexte

Sauf indication contraire explicite de l'utilisateur :

- utiliser uniquement le **pool de cartes disponible dans Link Evolution** ;
- raisonner avec la **banlist appliquée dans Link Evolution autour de 2020** ;
- ne pas proposer spontanément de cartes sorties après le pool du jeu ;
- ne pas basculer vers le TCG moderne 2026 ;
- privilégier les interactions, moteurs, FTK, OTK, loops, locks et combos réellement réalisables dans cet environnement.

## Objectif

Le but n'est pas de reproduire le méta 2026 ni de chercher systématiquement le deck le plus compétitif actuel.

Le but est surtout de profiter de **Link Evolution comme laboratoire Yu-Gi-Oh! 2020** et d'explorer les stratégies les plus amusantes, absurdes ou cassées que le jeu permet encore :

- FTK historiques ;
- combos à rallonge ;
- moteurs de spam Extra Deck ;
- boucles de ressources ;
- négations récursives ;
- locks ;
- burn ;
- Exodia ;
- boards quasi impossibles à casser ;
- interactions qui ont ensuite conduit certaines cartes à être limitées ou interdites.

## Exception

Passer à une autre époque ou banlist uniquement si l'utilisateur le demande explicitement, par exemple :

- « en TCG 2026 » ;
- « avec la banlist actuelle » ;
- « sur Master Duel » ;
- « format Edison » ;
- « sans tenir compte de Link Evolution ».

## Résumé opérationnel

**Deck demandé sans précision = Link Evolution / 2020.**

**Priorité = fun, broken, FTK, loops et combos exploitables dans le jeu.**


## Profil de règles du jeu — routage RC16

Pour l’environnement de référence **Link Evolution / 2020**, les règles générales implicites du duel sont définies exclusivement par :

**`GAME_RULES_LINK_EVOLUTION_2020_V1`**

Le présent CONTEXTE sélectionne ce profil ; il ne redéfinit pas ses règles mécaniques.

En particulier, les règles 2020 de placement depuis l’Extra Deck, les profils Fusion / Synchro / Xyz / Pendulum / Link, les attachments Xyz et la topologie Link sont appliqués depuis cette source spécialisée lorsqu’ils deviennent matériels à une ligne.

Les textes propres aux cartes restent sous `SEMANTIC_RULING_CONTRACT_V1`.
