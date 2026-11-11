# SpinozaGraph — documentation technique

L'*Éthique* de Spinoza sous forme de graphe explorable : chaque élément du texte est un nœud, et chaque renvoi d'une démonstration est une arête. On part d'une proposition (par exemple 5p42) pour voir le chemin qui y mène, ou ce qui en découle.

## Chaîne de production

```
sources/ethica/        données de lou/ethica (texte, découpage, renvois) — jamais modifiées
corrections.yaml       nos corrections des renvois, chacune justifiée
        │  outils/generate.py
        ▼
elements/<partie>/<id>.md   un fichier par élément — GÉNÉRÉS, jamais modifiés à la main
notes/*.md                  notes personnelles (facultatives, hors dépôt), jamais écrasées
        │  outils/build_explorer.py
        ▼
explorer.html          fichier autonome, sans réseau
```

Commandes :
```
python outils/generate.py              # sources + corrections -> elements/
python outils/check.py                 # contrôles (code 1 si erreur)
python -m unittest discover outils     # tests
python outils/build_explorer.py        # -> explorer.html (--watch pour régénérer en continu)
```

**Règle clé** : `elements/` est régénéré à chaque exécution. Toute intervention humaine va dans `corrections.yaml` (renvois) ou dans `notes/` (commentaires). Les notes peuvent citer les éléments par identifiant (`1p11`, `[[3p9sc]]`), et l'explorateur en fait des liens. Le dossier `notes/` est ignoré par git ; attention : `build_explorer.py` inclut les notes présentes dans `explorer.html`, il faut donc le régénérer sans `notes/` avant de publier.

## Identifiants

Ce sont ceux de lou/ethica, conservés tels quels pour pouvoir réimporter sans table de correspondance :

| exemple | sens |
|---|---|
| `1def6`, `1def6e` | définition 6 de la partie I, son explication (fusionnée dans la définition) |
| `1ax7`, `2p13ax1a` | axiome ; axiomes de l'abrégé de physique, rattachés à 2p13 |
| `1p11`, `1p11d` | proposition ; sa démonstration (fusionnée dans la proposition) |
| `1p11a1`, `1p6ca` | autre démonstration (*aliter*) |
| `1p16c1`, `1p8sc2`, `1p13csc` | corollaire, scolie, scolie du corollaire |
| `2p13l4`, `2p13def`, `2p13post3`, `3post1` | lemme, définition et postulats de l'abrégé de physique ; postulat de III |
| `3ad12`, `3agd` | définition des affects 12, définition générale des affects |
| `3pr`, `1app`, `4appc12` | préface, appendice de I, chapitre 12 de l'appendice de IV |

## Modèle (outils/ethica.py)

- **Conteneurs**, qui ne sont pas des éléments : parties, listes de définitions, d'axiomes et de postulats, et `4app`, qui n'a pas de texte propre.
- **Fusionnés** dans leur élément : démonstrations et explications.
- **Éléments** : tout le reste. Les types sont : definition, def-affect, axiome, postulat, lemme, proposition, corollaire, aliter, scolie, preface, appendice, chapitre.
- **Arêtes** :
  - `depends_on` (**appuis**) : renvois cités dans une démonstration, un *aliter* ou un corollaire ;
  - `voir` : renvois cités ailleurs (scolies, préfaces, définitions des affects, explications). Ils ne sont pas porteurs ;
  - **structurelles**, implicites et déduites de `parent` : la proposition est l'appui de son corollaire et de sa scolie ; un *aliter* est l'appui de sa proposition.
- **Repli** : dans la vue repliée de l'explorateur, corollaires, scolies et *aliter* sont rangés dans l'élément `repli` (la proposition ou le lemme qui les porte).

Remarque : une scolie peut être citée dans une démonstration. C'est alors un appui véritable.

## Langues

Les langues sont listées dans `LANGS` (`outils/ethica.py`). Actuellement, dans cet ordre : `en` (Elwes), `fr` (Appuhn), `de` (Stern), `la` (latin). L'ordre de `LANGS` est celui des icônes, et l'anglais est la langue par défaut de l'explorateur et de son interface. `fr_saisset` et `de_auerbach` sont déjà présents dans `sources/ethica` : pour ajouter une langue, il suffit d'ajouter une ligne à `LANGS` et de relancer la chaîne. Le code doit rester unique dans `LANGS` ; pour avoir deux traductions françaises, on utilisera par exemple `fr-saisset`.

L'explorateur n'affiche **qu'une langue à la fois**, choisie par les icônes en haut à droite. Ce choix s'applique au lecteur, aux libellés des nœuds, aux infobulles, à la recherche et aux noms des types. On ne fait jamais de vue côte à côte.

## Renvois cliquables dans le texte (outils/refs.py)

`generate.py` transforme les renvois du texte en liens `[[id|texte]]`, que l'explorateur et Obsidian rendent cliquables. Il y a un analyseur par langue : latin (`per propositionem 36 partis I`), Appuhn (`Prop. 36, p. I`, `Coroll. de la Prop. 9`, `Prop. préc.`) Elwes (`I. xxxvi.`, `II. ix. Coroll.`, `Def. of the Emotions, i.`) et Stern (`Lehrsatz 11, Teil 2`, `Zusatz zu Lehrsatz 9 dieses Teils`, `dem vorigen Lehrsatz`). **Un lien n'est créé que si sa cible fait partie des renvois connus de l'élément** (`depends_on` + `voir`) : on ne devine jamais. `generate.py` affiche le taux de renvois liés par langue. Une langue sans analyseur reste sans liens.

## Interface

Les textes de l'interface existent en français, en anglais et en allemand (`I18N` dans `outils/explorer_template.html`). Ils suivent les icônes de langue ; avec LA, l'interface reste dans la dernière langue choisie. Les noms de partie sont dans une marge verticale à gauche du graphe et ne doivent jamais le recouvrir.

**Favoris** : l'étoile à côté du titre d'un élément (ou la touche S) le marque. Les favoris sont gardés dans le `localStorage` du navigateur (clé `ethica-stars`, liste d'identifiants) : ils survivent aux régénérations d'`explorer.html`, mais pas à un changement de navigateur. Ils apparaissent comme une étoile sur le nœud (creuse si le favori est replié dedans), dans la liste (filtre « Favoris seulement ») et sur la page d'accueil.

## Corrections

Le format est décrit en tête de `corrections.yaml`. Chaque correction indique ce qu'elle change (`ajouter`, `retirer` ou `reclasser` un renvoi), pourquoi (`note`) et sur quelle autorité (`source` : Gebhardt, Appuhn, Curley, lecture du latin…). Les identifiants `cNNNN` ne sont jamais réutilisés. Après une correction, il faut relancer `generate.py`, puis `check.py`.

## Contrôles (outils/check.py)

Le script vérifie : 259 propositions (36, 49, 59, 73 et 42 selon la partie), aucun renvoi vers un non-élément, aucun cycle parmi les appuis et les arêtes structurelles, aucun appui vers l'avant (signalé), chaque langue présente pour chaque élément, des corrections bien formées, et un dossier `elements/` à jour.

## Mise à jour des sources

Recopier `data/` depuis un commit plus récent de https://codeberg.org/lou/ethica, mettre à jour `sources/ethica/PROVENANCE.md`, puis relancer la chaîne et relire les écarts signalés par `check.py`.

## Droits et publication

L'auteur de lou/ethica a donné son accord pour la publication (novembre 2026), à condition de conserver toutes les mentions de droits et de citer chaque contributeur. Licences : code en GPL-3.0, données en CC BY-SA 4.0, latin et renvois dérivés de la SpinozaBase (Baptiste Mélès, d'après Gilles Louise) en GPL-3.0 (voir `LICENSE` et `NOTICE.md`). L'explorateur reproduit sur sa page d'accueil la mention de chaque édition (`sources/ethica/*/ethica.md`) : ne jamais la retirer. Pour ajouter une langue à `LANGS`, il faut ajouter aussi son crédit à `NOTICE.md` et au README. Saisset n'autorise que l'usage non commercial.
