# Sources, authors and notices

SpinozaGraph builds on the work of the people below. **These notices must be kept** in any redistribution of the repository, of the generated files (`elements/`) or of `explorer.html`. The explorer reproduces them on its home page ("Provenance and rights").

## lou/ethica — segmentation, formatting, references

- Author: lou — https://codeberg.org/lou/ethica (site: https://ethica.repetitions.de)
- Copy used: `sources/ethica/`, unmodified (see `sources/ethica/PROVENANCE.md`).
- Licenses stated by the author: text formatting under **CC BY-SA 4.0** insofar as it is copyrightable; website code (Lisp, not included here) under GPL-3.0.
- The author agreed to this publication in November 2026, provided that all copyright notices are kept and everyone who contributed is credited.
- Licensing section of the lou/ethica readme, verbatim:

  > The Meta data used to generate the hyperlinks between sections of the text where taken from Baptiste Mélès' Latin hypertext version of the ethics, licensed under the GNU General Public License.
  >
  > Additional Credits for translations and editions, as well as information on text provenance are provided with the corresponding versions, please refer to the respective "data/*/ethica.md" files.
  >
  > Editing of all versions into a uniform format matching the provided metadata by [lou]. Insofar as this constitutes a copyrightable work it is licensed as CC BY-SA 4.0.
  >
  > The code used to generate the web page is licensed under the GNU General Public License version 3.

## Latin text and metadata — Baptiste Mélès, Gilles Louise

- Latin text and references taken from the SpinozaBase, Baptiste Mélès' hypertext edition: http://baptiste.meles.free.fr/spinozabase/ — repository https://github.com/BapMel/spinozabase (archived revision `8b3945fc34f32b1ee7b96396b1247ec56fc16976` on Software Heritage).
- The SpinozaBase Latin edition was itself adapted, with his permission, from the edition of **Gilles Louise** (formerly http://gilles.louise.perso.sfr.fr, now offline).
- The SpinozaBase is licensed under the **GNU General Public License, version 3**. `sources/ethica/meta.json`, the Latin text files (`sources/ethica/la_spinoza/`) and everything derived from them (the references `depends_on` / `voir`, the Latin sections of `elements/`) are therefore distributed under GPL-3.0.

## Translations

| Code | Translation | Digitization and conditions |
|---|---|---|
| `en` | R. H. M. Elwes, 1883 | Project Gutenberg, digitized by Tom Sharpe — https://www.gutenberg.org/ebooks/3800 |
| `fr` | Charles Appuhn, Garnier, 1929 (after Gebhardt, 1925) | Digitized and typeset by Jean-Luc Derrien for Hyperspinoza (http://hyperspinoza.caute.lautre.net/). « Le texte de cette traduction est libre de droits. […] Merci de conserver cette mention avec toute diffusion du texte. » |
| `de` | Jakob Stern, 1887 | Scanned and OCR'd book from archive.org; no further rights known. |
| `fr_saisset` (not shown) | Émile Saisset, 1849 | Digitized by David Bosman, http://www.spinozaetnous.org. « Permission de redistribuer librement ce fichier pour un usage noncommercial et sous condition de préserver cette mention et les adresse web mentionnées. » |
| `de_auerbach` (not shown) | Berthold Auerbach, 1841, revised by Artur Buchenau | Scanned and OCR'd book from archive.org; no further rights known. |

The full notices, as provided by lou/ethica, are in `sources/ethica/<version>/ethica.md`.

**Note:** the Saisset digitization only allows **non-commercial** redistribution. It is included in `sources/` so that folder stays a faithful copy of lou/ethica, but the explorer does not use it. For commercial use, remove `sources/ethica/fr_saisset/`.

## SpinozaGraph

- Code (`outils/`): GPL-3.0.
- Corrections (`corrections.yaml`) and documentation: CC BY-SA 4.0.

### Changes made to the licensed material

`sources/ethica/` is an unmodified copy (except for our own `PROVENANCE.md`). The generated files are adaptations of it:

- `elements/`: one file per element, merging proofs and explanations into their element, decoding HTML entities, turning cited references into `[[id|text]]` links, and applying the corrections listed in `corrections.yaml` to the references.
- `explorer.html`: the same data, embedded in an interactive page.

These adaptations are shared under the same licenses (CC BY-SA 4.0 for the text formatting, GPL-3.0 for what derives from the SpinozaBase). CC BY-SA 4.0 is one-way compatible with GPL-3.0, so `explorer.html` as a whole can be distributed under GPL-3.0.
