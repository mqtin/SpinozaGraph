# SpinozaGraph

**English** · [Français](#français) · [Deutsch](#deutsch)

Spinoza's *Ethics* as an explorable graph. Each element of the text (definition, axiom, proposition, corollary, scholium…) is a node, and each reference cited in a proof is an edge. Start from a proposition, say 5p42, to see the path leading to it or everything that follows from it.

## Usage

Online: <https://treillis.qpetit.com/spinoza/>

Or open `explorer.html` in a browser. It is a single self-contained file and works offline.

The text is available in English (Elwes), French (Appuhn), German (Stern) and Latin, one language at a time.

## Rebuilding

Requires Python 3 and PyYAML (`pip install pyyaml`).

```
python outils/generate.py              # sources + corrections -> elements/
python outils/check.py                 # consistency checks
python -m unittest discover outils     # tests
python outils/build_explorer.py        # -> explorer.html
```

`DEVELOPMENT.md` (in French) documents the pipeline, element identifiers, the data model and the correction format.

## Layout

| Path | Contents |
|---|---|
| `sources/ethica/` | unmodified copy of the data from [lou/ethica](https://codeberg.org/lou/ethica) |
| `corrections.yaml` | corrections to the references, each one justified |
| `elements/` | one Markdown file per element, generated (also readable in Obsidian) |
| `outils/` | generation, checking and build scripts |
| `explorer.html` | the explorer, generated |

## Credits and licenses

Segmentation, text formatting and references come from [lou/ethica](https://codeberg.org/lou/ethica) by lou. The Latin text and its references come from the [SpinozaBase](https://github.com/BapMel/spinozabase), Baptiste Mélès' hypertext edition, itself adapted from Gilles Louise's edition. The translations are in the public domain; the digitizations are by Tom Sharpe / Project Gutenberg (Elwes), Jean-Luc Derrien / Hyperspinoza (Appuhn) and archive.org (Stern).

- Code: GPL-3.0
- Data and formatted texts: CC BY-SA 4.0
- Latin text and references derived from the SpinozaBase: GPL-3.0

Details in [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md). Please keep these notices in any redistribution.

---

## Français

L'*Éthique* de Spinoza sous forme de graphe explorable : chaque élément du texte est un nœud, et chaque renvoi d'une démonstration est une arête. On part d'une proposition, par exemple 5p42, pour voir le chemin qui y mène ou ce qui en découle.

En ligne : <https://treillis.qpetit.com/spinoza/>. Sinon, ouvrez `explorer.html` dans un navigateur : le fichier est autonome et marche sans réseau. Textes en anglais (Elwes), français (Appuhn), allemand (Stern) et latin. La documentation technique est dans `DEVELOPMENT.md`.

Découpage, mise en forme et renvois : [lou/ethica](https://codeberg.org/lou/ethica) (lou). Latin et renvois : [SpinozaBase](https://github.com/BapMel/spinozabase) de Baptiste Mélès, d'après l'édition de Gilles Louise. Code sous GPL-3.0, données sous CC BY-SA 4.0 (latin et renvois dérivés de la SpinozaBase : GPL-3.0). Voir [LICENSE](LICENSE) et [NOTICE.md](NOTICE.md).

## Deutsch

Spinozas *Ethik* als erkundbarer Graph: Jedes Element des Textes ist ein Knoten, jeder Verweis in einem Beweis eine Kante. Von einem Lehrsatz aus, etwa 5p42, sieht man den Weg dorthin oder alles, was daraus folgt.

Online: <https://treillis.qpetit.com/spinoza/>. Oder öffnen Sie `explorer.html` im Browser: Die Datei ist eigenständig und funktioniert ohne Netz. Texte auf Englisch (Elwes), Französisch (Appuhn), Deutsch (Stern) und Latein. Die technische Dokumentation steht (auf Französisch) in `DEVELOPMENT.md`.

Gliederung, Textaufbereitung und Verweise: [lou/ethica](https://codeberg.org/lou/ethica) (lou). Latein und Verweise: [SpinozaBase](https://github.com/BapMel/spinozabase) von Baptiste Mélès, nach der Ausgabe von Gilles Louise. Code unter GPL-3.0, Daten unter CC BY-SA 4.0 (lateinischer Text und Verweise aus der SpinozaBase: GPL-3.0). Siehe [LICENSE](LICENSE) und [NOTICE.md](NOTICE.md).
