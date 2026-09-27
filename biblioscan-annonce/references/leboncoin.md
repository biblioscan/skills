# Publier sur Leboncoin

URL de départ : `https://www.leboncoin.fr/deposer-une-annonce`

Le parcours de dépôt se fait en plusieurs écrans. Les libellés changent parfois : cherche l'équivalent le plus proche en lisant la page. Si tu ne trouves pas d'équivalent sûr, ne publie pas et note-le dans le journal.

## Ordre de remplissage

1. **Titre** : `Titre [Tome N] - Prénom Nom`. Leboncoin propose souvent une catégorie à partir du titre : accepte **Loisirs → Livres** si c'est ce qui est proposé.
2. **Catégorie** : Livres. Si des sous-champs apparaissent (genre, ISBN…), remplis-les : genre déduit du résumé, ISBN-13.
3. **État** : voir la correspondance dans `pricing.md`.
4. **Description** : le résumé, une ligne vide, puis `ISBN : <ISBN13>`.
5. **Prix** : le prix unique calculé, le même que sur Vinted.
6. **Photos** : envoie les 4 images dans l'`input[type=file]`, dans l'ordre couverture, dos, tranche, ouvert. La première photo devient la photo principale.
7. **Livraison** : active l'envoi si c'est proposé. Choisis la tranche de poids : 250 g à 500 g pour un poche, 500 g à 1 kg pour un broché ou un relié courant, 1 à 2 kg pour un beau livre.
8. **Localisation et coordonnées** : garde les valeurs par défaut du compte. Ne les modifie jamais.
9. **Options payantes** (« remonter », « à la une », etc.) : refuse-les toujours et choisis l'option gratuite. Le skill ne dépense jamais d'argent.
10. **Publier** : valide. Relève l'URL de l'annonce, ou note « en cours de modération » si Leboncoin l'indique.

## Pièges connus

- Si l'on a peu de concurrents sur Leboncoin, la recherche par titre depuis le bouton BiblioScan ramène beaucoup de bruit : autres tomes, lots, livres sans rapport. Ne compte comme concurrents que les annonces du même livre.
- Une vérification (CAPTCHA, SMS) pendant le dépôt se traite comme pour CAL : mets en pause et laisse l'utilisateur la faire.
