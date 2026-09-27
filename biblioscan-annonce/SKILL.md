---
name: biblioscan-annonce
description: Transforme un ISBN ou un ASIN (ou une liste) en annonces publiées sur Vinted et Leboncoin, au bon prix. Le skill lit les stats du livre sur BiblioScan (prix médian, ventes), analyse la concurrence sur Chasse aux Livres, Vinted et Leboncoin, fixe un prix, récupère le titre et le résumé, associe les 4 photos de l'utilisateur, puis remplit et publie les annonces dans le navigateur. À utiliser dès que l'utilisateur veut mettre en vente, lister, publier, pricer ou « faire l'annonce » d'un ou plusieurs livres à partir d'ISBN, d'ASIN, de codes-barres ou d'un dossier de photos de livres, même si BiblioScan, Vinted ou Leboncoin ne sont pas cités.
license: MIT
compatibility: Tout agent capable de piloter un navigateur (Claude Code + Claude in Chrome, Codex ou autre agent avec un MCP Playwright / Chrome DevTools). L'utilisateur doit être connecté à biblioscan.ai, vinted.fr et leboncoin.fr dans ce navigateur. Python 3 pour scripts/.
---

# BiblioScan → annonce Vinted + Leboncoin

Ce skill reproduit la méthode d'un revendeur de livres d'occasion :
**ISBN/ASIN → stats BiblioScan → concurrence → prix unique → titre + résumé → photos → publication sur Vinted et Leboncoin.**

Chaque livre de la liste suit la même boucle. Il faut traiter les livres un par un et consigner le résultat de chacun dans le journal (voir « Journal »). Ainsi, un lot interrompu reprend là où il s'était arrêté, sans publier deux fois le même livre.

## 0. Préparation (une fois par lot)

1. **Entrées.** Récupère la liste des identifiants : ISBN-10, ISBN-13 ou ASIN, donnés dans le message ou dans un fichier (.txt, .csv). Récupère aussi le dossier photos. Si l'utilisateur ne l'a pas précisé, demande-le une seule fois.
2. **Photos.** Lance :
   ```bash
   python3 <skill>/scripts/prepare_photos.py <dossier_photos> <isbn1> <isbn2> ... --out <dossier_photos>/_prepared
   ```
   Le script détecte seul les trois rangements possibles : sous-dossier par ISBN, fichiers nommés avec l'ISBN, ou dossier en vrac. Il convertit les HEIC/PNG en JPEG et réduit la taille des images pour que l'upload passe. Il renvoie un JSON `{isbn: [photos triées]}` ainsi que la liste `unmatched` des photos qu'il n'a pas pu attribuer. Les photos en vrac se traitent à l'étape 4.
3. **Navigateur.** Lis `references/browser-tools.md` et repère la section qui correspond aux outils de navigateur dont tu disposes. Ouvre un onglet de travail. Vérifie que la session est ouverte sur biblioscan.ai, Vinted et Leboncoin. Si ce n'est pas le cas, demande à l'utilisateur de se connecter lui-même : n'entre jamais de mot de passe.
4. **Journal.** Lis `<dossier_photos>/biblioscan-annonces.csv` s'il existe et saute les ISBN déjà marqués `publié`.

## 1. Stats BiblioScan

Ouvre `https://biblioscan.ai/barcode/<ISBN_ou_ASIN>?db_lang=fr` et lis le texte de la page. Pour un ASIN ou un ISBN-10, cette URL fonctionne aussi. En cas d'échec, tape l'identifiant dans le champ « Entre ISBN ou ASIN ».

Relève :
- le titre BiblioScan (ex. « Aghora. La voie de la main gauche, tome 1 - Svoboda, Robert E. - Le Relié ») ; le format (Relié, Broché, Poche) sert pour la taille du colis ;
- le **prix médian de ventes**, le nombre de **ventes sur 12 mois** et l'historique « Vendu il y a… / Au prix de… » ;
- **« Actuellement vendu à X € · N offres »**, qui correspond au prix Amazon actuel ;
- l'ISBN-10 affiché (ex. `2909698289`) ;
- les liens des boutons raccourcis. Récupère leurs `href` en lisant la page (arbre d'accessibilité ou DOM), sans cliquer :
  - Chasse aux Livres : `https://cal.fr/<ISBN10>`
  - Vinted : `https://www.vinted.fr/catalog?search_text=<ISBN13>…`
  - Le Bon Coin : `https://www.leboncoin.fr/recherche?text=<titre auteur>…`
- l'URL de l'image « Couverture », qui sert à reconnaître les photos en vrac.

Si la page n'affiche aucune donnée de prix, livre inconnu compris : ne publie pas. Note `à vérifier : pas de données BiblioScan` et passe au livre suivant.

## 2. Concurrence

Ouvre les trois liens raccourcis et relève, pour chacun, **le prix le plus bas et le nombre d'offres**. Note aussi l'état annoncé du moins cher quand il est visible.

- **Chasse aux Livres** : prix le plus bas, occasion et neuf confondus.
- **Vinted** : ne garde que les annonces du **même livre**. Même titre, même tome, même édition si possible. Ignore les lots et les autres tomes.
- **Leboncoin** : la recherche se fait par titre, les résultats sont donc bruités. Même filtrage que pour Vinted.

**CAPTCHA / détection de robot.** Ne tente jamais de résoudre ou de contourner un CAPTCHA. C'est à l'utilisateur de le faire. Laisse l'onglet ouvert et préviens-le : « Chasse aux Livres demande une vérification anti-robot. Résous-la dans l'onglet ouvert puis réponds "ok". » Reprends ensuite. S'il préfère ne pas attendre, continue sans ce site : le prix CAL sera ignoré, et le titre et le résumé viendront du plan B de l'étape 3.

## 3. Prix, titre, résumé

### Prix : un seul prix pour Vinted ET Leboncoin
Suis `references/pricing.md`, qui contient les règles et l'exemple complet. En résumé : le prix de référence se place un peu sous le marché « pro » (Amazon, médian BiblioScan, CAL). La concurrence directe sur Vinted et Leboncoin l'emporte ensuite, car ces acheteurs voient les deux annonces côte à côte. On se place par rapport à l'offre la moins chère selon l'état de notre exemplaire, étape 4. Il faut donc fixer le prix **après** avoir évalué l'état.

### Titre de l'annonce
Format : `Titre [Tome N] - Prénom Nom`, par exemple `Aghora Tome 1 - Robert E. Svoboda`.
- Source principale : le titre de la page Chasse aux Livres, dont l'URL finale ressemble à `/prix/<isbn10>/<slug>`.
- Plan B : le titre BiblioScan remis en forme. Enlève le format (« Le Relié »), remets l'auteur en « Prénom Nom », garde le tome et supprime les sous-titres trop longs.
- 70 caractères au maximum.

### Description
- Source principale : le bloc **« Résumé »** de Chasse aux Livres, copié tel quel.
- Plan B, si CAL est inaccessible : `python3 <skill>/scripts/fetch_metadata.py <ISBN13>`, qui interroge Google Books puis Open Library.
- Si le script échoue (erreur réseau, limite de débit), cherche le résumé sur la fiche éditeur ou sur Babelio, dans le navigateur.
- Si aucune source n'a de résumé, écris 2 phrases neutres (titre, auteur, sujet) sans rien inventer sur le contenu.
- Termine toujours par une ligne vide suivie de `ISBN : <ISBN13>`.

## 4. Photos et état du livre

Chaque annonce a besoin de **4 photos, dans cet ordre : couverture, dos, tranche, livre ouvert**.

- Si les photos sont déjà attribuées (sous-dossier ou nom de fichier), ouvre les images pour les regarder et vérifier l'ordre. Réordonne si besoin : la couverture en premier est ce qui compte le plus, car c'est la vignette de l'annonce.
- **Photos en vrac** : télécharge la couverture BiblioScan (`curl -sL <url> -o /tmp/cover_<isbn>.jpg`) et compare-la visuellement aux photos de `unmatched`. Titre, couleurs et illustration permettent de trouver la couverture. Le dos, la tranche et l'intérieur du même livre sont en général les photos voisines : même nom séquentiel, même heure de prise de vue, même fond. Si tu hésites, ne publie pas ce livre et note `à vérifier : photos incertaines`. Mieux vaut une annonce manquante qu'une annonce avec les photos d'un autre livre.
- Moins de 4 photos : publie quand même si tu as au moins la couverture, et signale-le dans le récap. Sans couverture, ne publie pas.

**État** : déduis-le des photos avec la grille de `references/pricing.md` (Neuf / Très bon / Bon / Satisfaisant). Base-toi sur les coins, la tranche, les taches, le jaunissement, les annotations et la jaquette. En cas de doute entre deux états, choisis le moins bon : un acheteur déçu coûte plus cher que quelques euros.

## 5. Publication

L'utilisateur a choisi la **publication automatique**. Demander à traiter une liste revient à demander de publier ces annonces. Remplis et publie Vinted, puis Leboncoin, en suivant :
- `references/vinted.md`
- `references/leboncoin.md`

Pour les photos, envoie directement les fichiers du dossier `_prepared` dans le champ `<input type="file">`, avec l'outil d'upload de ton navigateur (voir `references/browser-tools.md`). Ne clique pas sur le bouton « Ajouter des photos » : il ouvre le sélecteur de fichiers du système, qu'un agent ne peut pas piloter.

Garde-fous : ne publie pas et note la raison dans le journal si
- le prix calculé est hors des bornes de `references/pricing.md` ;
- une annonce identique (même titre, même prix) existe déjà sur le compte ;
- le formulaire refuse une valeur et tu ne trouves pas d'équivalent sûr.

Après publication, récupère l'URL de l'annonce.

## Journal

Ajoute une ligne par livre à `<dossier_photos>/biblioscan-annonces.csv`. Crée le fichier avec l'en-tête s'il n'existe pas :

```
date,isbn,titre,etat,prix,median_biblioscan,amazon,cal_min,vinted_min,lbc_min,statut,url_vinted,url_lbc,remarque
```

`statut` vaut `publié`, `partiel` (une seule plateforme) ou `à vérifier`.

## Récap final

À la fin du lot, affiche un tableau court : ISBN, titre, état, prix, statut, liens. En dessous, liste les livres `à vérifier` avec la raison et ce que l'utilisateur doit faire, par exemple « ajouter une photo de couverture dans photos/978… ». Ferme les onglets que tu as ouverts.
