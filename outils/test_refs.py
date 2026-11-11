"""Tests de l'analyseur de renvois. Usage : python -m unittest discover outils"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from refs import link, roman  # noqa: E402


def ids(text, lang, part, targets, prev=()):
    return link(text, lang, part, targets, list(prev))[1]


class TestRefs(unittest.TestCase):
    def test_roman(self):
        self.assertEqual(roman("xxxvi"), 36)
        self.assertEqual(roman("IV"), 4)
        self.assertEqual(roman("lix."), 59)

    def test_latin(self):
        t = "Ergo (per axioma 7) ejus essentia; atqui hoc (per propositionem 7) est absurdum"
        self.assertEqual(ids(t, "la", 1, ["1ax7", "1p7"]), {"1ax7", "1p7"})
        self.assertEqual(ids("(per propositionem 36 partis I)", "la", 2, ["1p36"]), {"1p36"})
        self.assertEqual(ids("(per corollarium I propositionis 35 hujus)", "la", 4, ["4p35c1"]), {"4p35c1"})
        self.assertEqual(ids("(per propositiones 59 et 3 partis III)", "la", 5, ["3p59", "3p3"]), {"3p59", "3p3"})
        self.assertEqual(ids("(per definitiones 6 et 7 affectuum)", "la", 5, ["3ad6", "3ad7"]), {"3ad6", "3ad7"})
        self.assertEqual(ids("(per propositionem præcedentem)", "la", 2, ["2p10"], ["2p10", "2p9"]), {"2p10"})

    def test_francais(self):
        self.assertEqual(ids("(*Prop. 36, p. I*)", "fr", 2, ["1p36"]), {"1p36"})
        self.assertEqual(ids("(*Coroll. 1 de la Prop. 35*)", "fr", 4, ["4p35c1"]), {"4p35c1"})
        self.assertEqual(ids("(*Déf. 1 des Aff.*)", "fr", 4, ["3ad1"]), {"3ad1"})
        self.assertEqual(ids("(*Définitions 3* et *5*)", "fr", 1, ["1def3", "1def5"]), {"1def3", "1def5"})
        self.assertEqual(ids("(*Prop. préc.*)", "fr", 2, ["2p32"], ["2p32"]), {"2p32"})

    def test_anglais(self):
        self.assertEqual(ids("(II. xi.)", "en", 2, ["2p11"]), {"2p11"})
        self.assertEqual(ids("(II. ix. Coroll.)", "en", 2, ["2p9c"]), {"2p9c"})
        self.assertEqual(ids("(V. xxxvi and note)", "en", 5, ["5p36", "5p36sc"]), {"5p36", "5p36sc"})
        self.assertEqual(ids("(III. iii. lix.)", "en", 5, ["3p3", "3p59"]), {"3p3", "3p59"})
        self.assertEqual(ids("(Def. of the Emotions, i.)", "en", 4, ["3ad1"]), {"3ad1"})
        self.assertEqual(ids("(by Deff. iii. and v.)", "en", 1, ["1def3", "1def5"]), {"1def3", "1def5"})

    def test_allemand(self):
        self.assertEqual(ids("(nach Axiom VII)", "de", 1, ["1ax7"]), {"1ax7"})
        self.assertEqual(ids("(nach Lehrsatz 11, Teil 2)", "de", 4, ["2p11"]), {"2p11"})
        self.assertEqual(ids("(nach Zusatz zu Lehrsatz 9 dieses Teils)", "de", 2, ["2p9c"]), {"2p9c"})
        self.assertEqual(ids("(nach den Lehrsätzen 59 und 3, Teil 3)", "de", 5, ["3p59", "3p3"]), {"3p59", "3p3"})
        self.assertEqual(ids("(nach den Definitionen der Affekte, Ziffer I)", "de", 4, ["3ad1"]), {"3ad1"})
        self.assertEqual(ids("(nach dem vorigen Lehrsatz)", "de", 2, ["2p32"], ["2p32"]), {"2p32"})
        self.assertEqual(ids("(nach Lehrsatz 36 dieses Teils und seiner Anmerkung)", "de", 5, ["5p36", "5p36sc"]), {"5p36", "5p36sc"})

    def test_jamais_hors_des_renvois_connus(self):
        # Prop. 7 est reconnue, mais ne fait pas partie des renvois de l'élément : pas de lien
        self.assertEqual(ids("(*Prop. 7*)", "fr", 1, ["1p8"]), set())

    def test_balisage(self):
        out, _ = link("Or cela (*Proposition\n7*) est absurde", "fr", 1, ["1p7"], [])
        self.assertIn("[[1p7|Proposition 7]]", out)


if __name__ == "__main__":
    unittest.main()
