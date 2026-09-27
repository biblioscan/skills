# Outils de navigateur selon l'agent

Le skill décrit des actions génériques : ouvrir une page, lire le texte, lire les liens, cliquer, remplir un champ, envoyer des fichiers, faire une capture. Ce fichier donne leur équivalent pour les outils les plus courants. Repère la section qui correspond aux outils dont tu disposes. Si ton agent en a d'autres, fais la même correspondance.

Règles communes, quel que soit l'outil :
- **Sessions** : l'utilisateur doit être connecté à biblioscan.ai, vinted.fr et leboncoin.fr **dans le navigateur piloté**. N'entre jamais de mot de passe. Si une page de connexion s'affiche, demande-lui de se connecter lui-même dans ce navigateur, puis reprends.
- **CAPTCHA et vérifications** : l'utilisateur les résout lui-même. Mets le lot en pause et ne tente jamais de les contourner.
- **Boîtes de dialogue** (`alert`, `confirm`) : évite de les déclencher. Elles peuvent bloquer l'outil.
- **Onglets** : ferme en fin de lot ceux que tu as ouverts.

| Action | Claude in Chrome | Playwright MCP | Chrome DevTools MCP |
|---|---|---|---|
| Voir les onglets / en ouvrir un | `tabs_context_mcp`, `tabs_create_mcp` | `browser_tabs` | `list_pages`, `new_page` |
| Ouvrir une URL | `navigate` | `browser_navigate` | `navigate_page` |
| Lire le texte | `get_page_text` | `browser_snapshot` | `take_snapshot` |
| Lire les liens (`href`) | `find` puis `read_page` avec `ref_id` | `browser_snapshot` ou `browser_evaluate` | `take_snapshot` ou `evaluate_script` |
| Cliquer | `computer` (`left_click` + `ref`) | `browser_click` | `click` |
| Remplir un champ / une liste | `form_input` | `browser_type`, `browser_fill_form`, `browser_select_option` | `fill`, `fill_form` |
| Envoyer des photos | `file_upload` sur la ref de l'`input[type=file]` | cliquer sur « Ajouter des photos », puis `browser_file_upload` | `upload_file` sur l'uid de l'`input[type=file]` ou du bouton |
| Capture d'écran | `computer` (`screenshot`) | `browser_take_screenshot` | `take_screenshot` |
| Exécuter du JavaScript | `javascript_tool` | `browser_evaluate` | `evaluate_script` |

## Claude in Chrome (Claude Code)
- Les outils sont souvent « différés » : charge-les tous en un seul appel `ToolSearch`.
- Appelle `tabs_context_mcp` en premier, puis travaille dans un nouvel onglet.
- Pour les photos, **ne clique pas** sur le bouton d'upload : `file_upload` remplit directement l'input. Un clic ouvrirait le sélecteur natif, que l'agent ne peut pas piloter.
- Il se peut qu'un site n'ait pas encore été autorisé dans l'extension (« Permission denied »). Demande alors à l'utilisateur de l'autoriser.

## Playwright MCP (Codex, Cursor, autres)
- Par défaut, Playwright lance son propre profil de navigateur, différent de ton Chrome habituel. L'utilisateur doit s'y connecter une première fois aux trois sites. Le profil est conservé ensuite, sauf en mode `--isolated`.
- Envoi de photos : `browser_file_upload` répond au sélecteur de fichiers ouvert par le clic. Ici, cliquer d'abord sur le bouton d'upload est donc la bonne méthode.
- `browser_snapshot` renvoie les `ref` à utiliser pour cliquer et remplir.

## Chrome DevTools MCP
- Il peut piloter le Chrome de l'utilisateur, avec ses sessions déjà ouvertes, s'il est lancé en se connectant à ce Chrome (option `--autoConnect` ou `--browser-url`). Sinon, il utilise son propre profil : connexion initiale nécessaire, comme pour Playwright.
- `take_snapshot` renvoie les `uid` à utiliser pour `click`, `fill` et `upload_file`.
