# Règles de prix et d'état

## Logique

On vend sur Vinted et Leboncoin avec **un seul prix pour les deux**. Les acheteurs de ces plateformes comparent d'abord avec les autres annonces de particuliers, puis avec Amazon et les sites pros. D'où deux niveaux :

### 1. Prix de référence (plafond)
`REF = un peu sous min(prix Amazon actuel, prix le plus bas CAL)`, soit environ 8 à 10 % en dessous, et sans dépasser le **prix médian BiblioScan** de plus de 5 %.
- Si l'une des sources manque, utilise les autres.
- Si l'historique « Vendu il y a » montre une baisse récente nette (ex. 1m : 109 € contre 145 € sur 1 an), prends-la en compte et vise plutôt le bas de la fourchette.
- Arrondis à un prix « rond » : multiple de 5 € au-dessus de 20 €, euro entier en dessous.

### 2. Concurrence directe (Vinted + Leboncoin)
Soit `C` le prix le plus bas parmi les annonces **du même livre** sur Vinted et Leboncoin.

| Notre état comparé à l'offre à C | Prix |
|---|---|
| Meilleur | C + 5 % environ (au moins +3 €), arrondi |
| Équivalent / inconnu | C, ou juste en dessous (-1 à -2 €) |
| Moins bon | C − 10 % environ |

Puis `PRIX = min(ce résultat, REF)`.

Sans concurrent sur Vinted ni Leboncoin : `PRIX = REF`.

### Garde-fous (ne pas publier, noter « à vérifier »)
- Ni prix médian, ni prix Amazon, ni prix CAL : aucune base fiable.
- PRIX < 2 € : pas rentable, à signaler.
- Concurrent à moins de 30 % du médian : vérifie d'abord que c'est bien le même livre, pas un autre tome, une autre édition ou un lot. Si c'est bien le même, aligne-toi quand même, mais indique-le dans la remarque du journal.

## Exemple de référence (méthode de l'utilisateur)

ISBN 9782909698281 : *Aghora Tome 1 - Robert E. Svoboda*, relié.
- BiblioScan : médian 145 €, 4 ventes/12 mois, Amazon 153 € (8 offres). Historique : 109 € (1m), 149 € (6m), 145 € (1a).
- REF : un peu sous 148/153 → **135 €**.
- CAL : le moins cher à 148 €. Leboncoin : aucun concurrent. Vinted : 4 concurrents, le moins cher à **90 €**.
- Notre exemplaire est meilleur que celui à 90 € → 90 + 5 % ≈ **95 €**.
- 95 < 135 → **prix final 95 €** sur Vinted et sur Leboncoin.

## Grille d'état (déduite des photos)

| État | Critères visibles |
|---|---|
| Neuf | Aucune marque, dos non cassé, pages blanches, parfois encore sous film |
| Très bon | Traces minimes de manipulation, coins nets, pas d'annotation ni de tache |
| Bon | Usure normale : coins légèrement émoussés, dos un peu marqué, léger jaunissement |
| Satisfaisant | Usure marquée : taches, annotations, dos cassé, jaquette abîmée, pages cornées |

Correspondance avec les formulaires :
- Vinted : « Neuf avec étiquette » (seulement si sous film), « Neuf sans étiquette », « Très bon état », « Bon état », « Satisfaisant ».
- Leboncoin : « État neuf », « Très bon état », « Bon état », « État satisfaisant ».

En cas de doute entre deux états, choisis le moins bon.
