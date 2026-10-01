# Validation de la progression narrative

**Version : V6-L1 / V4 Lean**

## AUTHORITY

Seule autorité sur :

- fonctions maîtrisées / limitées / absentes ;
- potentiel et développement ;
- sophistication permise ;
- pertinence du support moderne ;
- cohérence narrative de la decklist finale ;
- matérialisation du contrat narratif et du rapport de conformité.

Exécution obligatoire **avant construction**, puis **sur chaque deck-vN matériel**.

## Principe

**La progression doit être visible dans l’architecture du deck, pas seulement dans le commentaire.**

Une faiblesse naturelle du deck n’est pas automatiquement une absence de maîtrise du personnage.

## RED — définir le stade avant la liste

Définir :

1. **2 à 4 fonctions déjà maîtrisées** ;
2. **au moins 1 fonction importante non maîtrisée ou limitée** qui doit rester réellement absente, imparfaite ou coûteuse ;
3. potentiel provisoire X/10 ;
4. niveau provisoire : rudimentaire / en développement / solide / avancé / très avancé / quasi optimal.

Formule interne obligatoire :

**« À ce stade, le personnage maîtrise [X], mais ne maîtrise pas encore [Y], et la decklist doit rendre cette limite visible. »**

Ne pas utiliser comme limite narrative :

- brick/coût naturel ;
- contrainte intrinsèque d’un archétype ;
- banlist ;
- ressource normalement disputée ;
- impossibilité de faire toutes les lignes simultanément.

## GREEN — architecture envisagée

Avant construction, vérifier :

### Compensation de la faiblesse
Le concept ou un moteur externe ne doit pas effacer indirectement la limite narrative annoncée.

### Accumulation / surcharge fonctionnelle
Une addition de fonctions individuellement plausibles peut rendre l’ensemble trop sophistiqué pour le stade.

### Support moderne
Autorisé seulement s’il respecte :
- la politique de mécaniques de STYLE ;
- les fonctions réellement maîtrisées ;
- le stade narratif.

Un expert moderne ne doit pas être artificiellement saboté : si une carte implique naturellement une fonction avancée non maîtrisée, elle doit être retirée plutôt que jouée volontairement mal.

### Boss / finisher
Date d’impression ou puissance seule ne décide pas. Juger les compétences nécessaires pour y accéder et l’exploiter.

### Potentiel démontré
Le niveau annoncé doit être soutenu par les décisions réelles du deck, pas par le texte.

Échec d’un point essentiel → simplifier/restructurer ou réévaluer le stade avant construction.

## REFACTOR

Construire sans supprimer la progression.  
Si la liste finale compense la limite, la correction doit toucher l’architecture réelle ; une justification narrative ajoutée après coup ne suffit pas.

## STOP OUTPUT — réévaluation finale aveugle

Sur la decklist finale, cacher mentalement le commentaire et reposer :

1. la limite annoncée est-elle visible dans la liste/lignes ?
2. un autre moteur la compense-t-il malgré tout ?
3. la sophistication réelle dépasse-t-elle le stade ?
4. le potentiel / niveau démontré correspondent-ils encore ?
5. la faiblesse est-elle vraiment une absence de maîtrise du personnage ?

La lecture de la liste finale a priorité sur le niveau annoncé avant construction.

Si contradiction → modifier le deck ou réévaluer le stade.  
Ne jamais conserver la contradiction et la rationaliser dans le texte.

# Contrat narratif matérialisé — sortie préconstruction

Avant exploration/construction, produire `narrative_contract.json` pour le `run_id` courant.

Données métier obligatoires :

```json
{
  "run_id": "...",
  "authority": "VALIDATION_PROGRESSION_NARRATIVE",
  "arc": "GX",
  "policy_source": "STYLE_DECKS_PERSONNAGE_LINK_EVOLUTION",
  "policy_source_sha256": "...",
  "policy_schema_version": 1,
  "mechanic_universe": ["Ritual", "Fusion", "Synchro", "Xyz", "Pendulum", "Link"],
  "allowed_mechanics": ["Ritual", "Fusion"],
  "forbidden_mechanics": ["Synchro", "Xyz", "Pendulum", "Link"],
  "mastered_functions": ["..."],
  "limited_or_absent_functions": ["..."]
}
```

Règles :

- lire la politique machine-readable de STYLE ;
- choisir l’arc correspondant au contexte ;
- partitionner **tout** `mechanic_universe` entre allowed et forbidden ;
- aucune mécanique dans les deux listes ;
- climax/potentiel élevé ne modifie jamais la chronologie ;
- les autorités aval consomment le **contrat frais du run courant**.

Le harness valide la forme, les hashes, la partition et la correspondance exacte avec STYLE ; cette autorité fournit le jugement métier.

# Rapport de conformité narrative — après chaque deck-vN

Après matérialisation du snapshot exact et **avant la viabilité multi-systèmes ou la sortie**, réexécuter cette autorité et produire `narrative_conformance.json`.

Schéma d’interface attendu par le harness :

```json
{
  "run_id": "...",
  "authority": "VALIDATION_PROGRESSION_NARRATIVE",
  "artifact": "deck-v1",
  "snapshot_sha256": "...",
  "contract_sha256": "...",
  "forbidden_mechanics_checked": ["..."],
  "card_mechanics": [
    {
      "zone": "extra_deck",
      "name": "Nom de carte",
      "qty": 1,
      "card_type": "Fusion / Effect Monster",
      "mechanics": ["Fusion"]
    }
  ],
  "axis_mechanics": ["Fusion"],
  "observed_mechanics": ["Fusion"],
  "status": "PASS"
}
```

Obligations métier :

- inventorier **toutes** les cartes Main / Extra / Side exactement une fois par zone+nom avec quantité ;
- indiquer leur type et leurs mécaniques ;
- déclarer les mécaniques réellement utilisées par les Axes ;
- contrôler toute la liste `forbidden_mechanics`.

Condition de fermeture :

`observed_mechanics ∩ forbidden_mechanics = ∅`

Sinon `FAIL`, identifier la carte/Axe fautif et renvoyer vers construction/refactor.

Une carte omise, une zone non couverte, une quantité différente, un snapshot différent ou un changement matériel rend la preuve invalide.

Toute modification matérielle de `deck-vN` rend la conformité précédente `STALE`.  
`/fresh` recrée contrat et conformité dans le nouveau run.

## OUTPUT

- jugement RED/GREEN/final ;
- potentiel/niveau réellement démontrés ;
- `narrative_contract.json` frais ;
- `narrative_conformance.json` frais sur l’artefact exact.

## DO_NOT_DECIDE

Classification, viabilité multi-systèmes, rendu, versioning, hashes ou autorisation terminale.
