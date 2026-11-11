"""Modèle de l'Éthique tiré de sources/ethica (dépôt lou/ethica) et de corrections.yaml.

Partagé par generate.py et check.py. Aucune écriture ici.

Règles (voir DEVELOPMENT.md) :
- les nœuds « conteneurs » (parties, listes de définitions, d'axiomes…) ne sont pas des éléments ;
- les démonstrations et les explications sont fusionnées dans l'élément qui les porte ;
- tous les autres nœuds sont des éléments (proposition, corollaire, scolie, aliter, lemme…) ;
- un renvoi est « logique » s'il figure dans une démonstration, un aliter ou un corollaire,
  et « voir » sinon (scolie, préface, définition, explication…).
"""
from __future__ import annotations

import html
import json
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    raise SystemExit("PyYAML est requis : pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "sources" / "ethica"
CORRECTIONS = ROOT / "corrections.yaml"

# Langues affichées : code -> dossier de sources/ethica. Ajouter une langue = ajouter une ligne.
LANGS = {"en": "en_elwes", "fr": "fr_appuhn", "de": "de_stern", "la": "la_spinoza"}

CONTAINER_TYPES = {"ethica", "pars", "definitiones", "axiomata", "postulata", "affectuum_definitiones"}
MERGED_TYPES = {"demonstratio", "explicatio"}
LOGICAL_SOURCE_TYPES = {"demonstratio", "aliter", "corollarium"}

# Type latin -> type du projet (front-matter)
TYPE_FR = {
    "definitio": "definition",
    "axioma": "axiome",
    "postulatum": "postulat",
    "propositio": "proposition",
    "lemma": "lemme",
    "corollarium": "corollaire",
    "scholium": "scolie",
    "aliter": "aliter",
    "praefatio": "preface",
    "appendix": "appendice",
    "caput": "chapitre",
    "affectuum_generalis_definitio": "def-affect",
}
# Types repliables dans leur parent (vue repliée du graphe)
FOLDABLE = {"corollaire", "scolie", "aliter"}


def norm_type(t: str) -> str:
    return t.replace(" ", "_")


def load_meta() -> dict:
    return json.loads((SRC / "meta.json").read_text(encoding="utf-8"))


def load_lang_meta() -> dict:
    out = {}
    for code, folder in LANGS.items():
        files = [p for p in (SRC / folder).glob("*.json")]
        if len(files) != 1:
            raise SystemExit(f"{folder} : un seul fichier .json attendu, trouvé {len(files)}")
        info = json.loads(files[0].read_text(encoding="utf-8"))
        info["types"] = {norm_type(k): v for k, v in info.get("types", {}).items()}
        info["folder"] = folder
        out[code] = info
    return out


def read_text(folder: str, nid: str) -> str:
    p = SRC / folder / f"{nid}.md"
    # Les sources contiennent des entités HTML (&#x2013; …) : on les décode.
    return html.unescape(p.read_text(encoding="utf-8").replace("\r\n", "\n")).strip() if p.exists() else ""


def load_corrections() -> list[dict]:
    if not CORRECTIONS.exists():
        return []
    data = yaml.safe_load(CORRECTIONS.read_text(encoding="utf-8")) or {}
    return data.get("corrections") or []


class Model:
    def __init__(self):
        self.meta = load_meta()
        self.langs = load_lang_meta()
        self.corrections = load_corrections()
        m = self.meta
        self.parent = {c: k for k, v in m.items() for c in v.get("children", [])}
        # ordre du texte (parcours préfixe depuis la racine)
        self.order: list[str] = []
        stack = ["ethica"]
        while stack:
            k = stack.pop()
            self.order.append(k)
            stack.extend(reversed(m[k].get("children", [])))
        self.pos = {k: i for i, k in enumerate(self.order)}
        self.problems: list[str] = []
        self._classify()
        self._edges()

    # --- nœuds -----------------------------------------------------------
    def is_container(self, nid: str) -> bool:
        v = self.meta[nid]
        t = norm_type(v["type"])
        if t in CONTAINER_TYPES:
            return True
        # ex. 4app : appendice sans texte propre, qui ne fait que regrouper ses chapitres
        return bool(v.get("children")) and not read_text(LANGS["la"], nid)

    def _classify(self):
        self.elements: list[str] = []
        self.owner: dict[str, str] = {}  # nœud -> élément qui le porte (lui-même s'il est élément)
        for nid in self.order:
            t = norm_type(self.meta[nid]["type"])
            if self.is_container(nid):
                continue
            if t in MERGED_TYPES and self.parent.get(nid) in self.owner:
                self.owner[nid] = self.owner[self.parent[nid]]
                continue
            if t not in TYPE_FR:
                self.problems.append(f"{nid} : type latin inconnu « {t} »")
                continue
            self.owner[nid] = nid
            self.elements.append(nid)

    def etype(self, nid: str) -> str:
        t = norm_type(self.meta[nid]["type"])
        if t == "definitio" and self.parent.get(nid) == "3ad":
            return "def-affect"
        return TYPE_FR[t]

    def element_parent(self, nid: str) -> str | None:
        """Élément de rattachement (le plus proche ancêtre qui est un élément)."""
        p = self.parent.get(nid)
        while p and p not in self.owner:
            p = self.parent.get(p)
        return self.owner.get(p) if p else None

    def fold_target(self, nid: str) -> str:
        """Élément dans lequel nid se replie (lui-même s'il n'est pas repliable)."""
        cur = nid
        while self.etype(cur) in FOLDABLE:
            p = self.element_parent(cur)
            if not p:
                break
            cur = p
        return cur

    def part(self, nid: str) -> int:
        p = nid
        while p in self.parent and self.meta[p]["type"] != "pars":
            p = self.parent[p]
        return int(self.meta[p].get("number") or 0) if self.meta[p]["type"] == "pars" else 0

    def merged_children(self, eid: str) -> list[str]:
        """Nœuds fusionnés dans eid, dans l'ordre du texte."""
        return [n for n in self.order if n != eid and self.owner.get(n) == eid]

    # --- arêtes ----------------------------------------------------------
    def _edges(self):
        logique: dict[str, list[str]] = {e: [] for e in self.elements}
        voir: dict[str, list[str]] = {e: [] for e in self.elements}
        for nid in self.order:
            refs = self.meta[nid].get("ref") or []
            if not refs:
                continue
            src = self.owner.get(nid)
            if not src:
                self.problems.append(f"{nid} : renvois portés par un conteneur, ignorés")
                continue
            kind = logique if norm_type(self.meta[nid]["type"]) in LOGICAL_SOURCE_TYPES else voir
            for r in refs:
                if r not in self.meta:
                    self.problems.append(f"{nid} : renvoi vers un id inexistant « {r} »")
                    continue
                tgt = self.owner.get(r)
                if not tgt:
                    self.problems.append(f"{nid} : renvoi vers le conteneur « {r} »")
                    continue
                if tgt != src and tgt not in kind[src]:
                    kind[src].append(tgt)
        self.applied: dict[str, list[str]] = {e: [] for e in self.elements}
        for c in self.corrections:
            self._apply(c, logique, voir)
        for e in self.elements:  # un renvoi logique l'emporte sur un renvoi « voir »
            voir[e] = [x for x in voir[e] if x not in logique[e]]
        self.logique, self.voir = logique, voir

    def _apply(self, c: dict, logique, voir):
        cid, op, de, vers = c.get("id"), c.get("op"), c.get("de"), c.get("vers")
        if de not in logique or vers not in logique:
            self.problems.append(f"correction {cid} : élément inconnu ({de} → {vers})")
            return
        target = logique if c.get("type", "logique") == "logique" else voir
        if op == "ajouter":
            if vers not in target[de]:
                target[de].append(vers)
        elif op in ("retirer", "reclasser"):
            found = False
            for d in (logique, voir):
                if vers in d[de]:
                    d[de].remove(vers)
                    found = True
            if not found:
                self.problems.append(f"correction {cid} : renvoi {de} → {vers} introuvable")
            if op == "reclasser":
                target[de].append(vers)
        else:
            self.problems.append(f"correction {cid} : opération inconnue « {op} »")
            return
        self.applied[de].append(cid)
