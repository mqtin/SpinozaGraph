# Provenance

Copie du dossier `data/` du dépôt **lou/ethica** (auteur : lou).

- Dépôt : https://codeberg.org/lou/ethica (site associé : https://ethica.repetitions.de)
- Commit : `67c566ccb17548179e61eca28396af5f7a564fd3` (« add license note to lisp code », 11 novembre 2026)
- Copié le 11 novembre 2026, sans aucune modification.

## Contenu

- `meta.json` : structure (949 nœuds), avec pour chacun `id`, `type` (latin), `children`, `ref` (renvois) et `number`.
- Un dossier par version du texte, avec un fichier Markdown par nœud et un `types.json` :
  `la_spinoza` (latin), `fr_appuhn`, `fr_saisset`, `en_elwes`, `de_stern`, `de_auerbach`.

## Droits

Réponse de l'auteur (novembre 2026) : la publication est possible à condition de ne retirer aucune mention de droits et de citer toutes les personnes ayant contribué. Le détail est dans le README de lou/ethica et dans `NOTICE.md` à la racine.

- Traductions : domaine public. Les numérisations portent des conditions d'attribution, reproduites dans chaque `*/ethica.md` (à ne jamais retirer). Saisset : redistribution non commerciale seulement.
- Latin et `meta.json` : dérivés de la SpinozaBase de Baptiste Mélès (elle-même adaptée de l'édition de Gilles Louise), sous GPL-3.0 ; `la_spinoza/` et `meta.json` sont donc sous GPL-3.0.
- Mise en forme des textes par lou : CC BY-SA 4.0.

## Règle

Ne jamais modifier ces fichiers à la main. Pour une mise à jour, il faut recopier le dossier `data/` d'un commit plus récent, mettre à jour ce fichier, puis relancer `outils/generate.py` et `outils/check.py`. Les corrections vont dans `corrections.yaml`.
