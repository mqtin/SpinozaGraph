"""Tests du modèle. Usage : python -m unittest discover outils"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check import find_cycles, run, structural_edges  # noqa: E402
from ethica import Model  # noqa: E402

M = Model()


class TestModel(unittest.TestCase):
    def test_demonstration_fusionnee(self):
        self.assertNotIn("1p11d", M.elements)
        self.assertEqual(M.owner["1p11d"], "1p11")
        self.assertEqual(M.logique["1p11"], ["1ax7", "1p7"])

    def test_aliter_et_scolie(self):
        self.assertEqual(M.etype("1p11a1"), "aliter")
        self.assertEqual(M.etype("1p11sc"), "scolie")
        self.assertEqual(M.element_parent("1p11sc"), "1p11")

    def test_repli_en_cascade(self):
        # scolie d'un corollaire -> se replie dans la proposition
        self.assertEqual(M.fold_target("1p13csc"), "1p13")
        self.assertEqual(M.fold_target("1p13"), "1p13")

    def test_types_particuliers(self):
        self.assertEqual(M.etype("3ad12"), "def-affect")
        self.assertEqual(M.etype("2p13l4"), "lemme")
        self.assertEqual(M.etype("2p13ax1a"), "axiome")
        self.assertEqual(M.etype("4appc12"), "chapitre")
        self.assertNotIn("4app", M.elements)  # conteneur sans texte
        self.assertIn("1app", M.elements)

    def test_explication_fusionnee_dans_definition(self):
        self.assertEqual(M.owner["3ad10e"], "3ad10")
        self.assertEqual(M.owner["1def6e"], "1def6")

    def test_renvois_voir(self):
        # les renvois d'une scolie ou d'une définition ne sont pas logiques
        self.assertEqual(M.logique["3ad1"], [])
        self.assertIn("3p9sc", M.voir["3ad1"])

    def test_pas_d_auto_renvoi(self):
        for e in M.elements:
            self.assertNotIn(e, M.logique[e] + M.voir[e])

    def test_parties(self):
        self.assertEqual(M.part("5p42"), 5)
        self.assertEqual(M.part("2p13l4"), 2)

    def test_cycles(self):
        self.assertEqual(find_cycles(["a", "b", "c"], [("a", "b"), ("b", "c")]), [])
        self.assertTrue(find_cycles(["a", "b"], [("a", "b"), ("b", "a")]))

    def test_structure(self):
        s = set(structural_edges(M))
        self.assertIn(("1p11", "1p11sc"), s)
        self.assertIn(("1p11a1", "1p11"), s)

    def test_controles(self):
        errors, _ = run(M)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
